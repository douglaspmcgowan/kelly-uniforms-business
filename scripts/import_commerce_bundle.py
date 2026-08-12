#!/usr/bin/env python3
"""Transactionally import a validated normalized payload into the recovery database."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

import extend_import_schema
import recovery_package
import upgrade_commerce_schema
import validate_import_bundle


TRANSFORM_VERSION = "mt-uniforms-normalized-payload/v1"
TABLE_ORDER = [
    "catalog_categories", "catalog_products", "catalog_product_categories",
    "catalog_variants", "catalog_option_groups", "catalog_option_values",
    "catalog_variant_options", "catalog_media", "inventory_locations", "inventory_levels",
    "business_accounts", "account_members", "account_addresses", "tax_exemptions",
    "entitlements", "allowance_ledger", "price_lists", "price_list_entries", "promotions",
    "commerce_orders", "commerce_order_lines", "line_customizations", "purchase_orders",
    "invoices", "payments", "refunds", "fulfillments", "fulfillment_lines", "returns",
    "return_lines", "production_artwork", "production_proofs", "production_work_orders",
    "production_operations", "commerce_order_adjustments", "integration_mappings", "audit_events",
]
TABLE_RANK = {table: index for index, table in enumerate(TABLE_ORDER)}
ALLOWED_TABLES = set(upgrade_commerce_schema.DEFINITIONS) | set(extend_import_schema.NORMALIZED_DEFINITIONS)


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _load_snapshot_rows(root: Path, artifacts: list[dict], source_ids: dict[str, int]) -> list[dict]:
    normalized = []
    for artifact in artifacts:
        if artifact["artifact_type"] != "table-snapshot":
            continue
        relative = artifact["relative_path"]
        with (root / relative).open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                rows = row.get("normalized_rows", [])
                if not isinstance(rows, list):
                    raise ValueError("normalized_rows must be an array")
                for target in rows:
                    if not isinstance(target, dict):
                        raise ValueError("normalized target row must be an object")
                    normalized.append({
                        "table": target.get("table"),
                        "record_id": target.get("record_id"),
                        "values": target.get("values"),
                        "entity": row["entity"],
                        "source_id": source_ids[relative],
                        "source_record_id": str(row["source_record_id"]),
                        "source_locator": str(row["source_locator"]),
                    })
    return sorted(normalized, key=lambda row: (TABLE_RANK.get(str(row["table"]), 9999), str(row["record_id"])))


def _validate_normalized_row(connection: sqlite3.Connection, row: dict) -> None:
    table = row["table"]
    if table not in ALLOWED_TABLES:
        raise ValueError(f"unsupported normalized target table: {table}")
    if not isinstance(row["record_id"], str) or not row["record_id"]:
        raise ValueError("normalized record_id must be non-empty")
    values = row["values"]
    if not isinstance(values, dict):
        raise ValueError("normalized values must be an object")
    validate_import_bundle._reject_sensitive_keys(values, "normalized_values")
    columns = {item[1] for item in connection.execute(f"PRAGMA table_info({table})")}
    reserved = {"record_id", "source_system", "source_record_id", "extracted_at", "source_id"}
    unknown = set(values) - (columns - reserved)
    if unknown:
        raise ValueError(f"unsupported normalized columns for {table}: {sorted(unknown)}")


def _insert_normalized_row(connection: sqlite3.Connection, bundle: dict, row: dict) -> None:
    _validate_normalized_row(connection, row)
    table = row["table"]
    values = row["values"]
    payload = {
        "record_id": row["record_id"],
        **values,
        "source_system": bundle["source_system"],
        "source_record_id": row["source_record_id"],
        "extracted_at": bundle["captured_at"],
        "source_id": row["source_id"],
    }
    names = list(payload)
    placeholders = ",".join("?" for _ in names)
    connection.execute(
        f"INSERT INTO {table}({','.join(names)}) VALUES({placeholders})",
        [payload[name] for name in names],
    )
    connection.execute(
        """INSERT INTO record_lineage(
            entity_table,entity_record_id,source_id,source_record_id,source_locator,
            relation_role,transform_version
        ) VALUES(?,?,?,?,?,?,?)""",
        (
            table, row["record_id"], row["source_id"], row["source_record_id"],
            row["source_locator"], "primary-source", TRANSFORM_VERSION,
        ),
    )


def import_bundle(database: Path, manifest_path: Path, schema_path: Path) -> dict:
    database = Path(database).resolve()
    manifest_path = Path(manifest_path).resolve()
    validation = validate_import_bundle.validate_bundle(manifest_path, schema_path)
    bundle = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_sha256 = recovery_package.sha256_file(manifest_path)
    extend_import_schema.apply_schema(database)
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        existing = connection.execute(
            "SELECT manifest_sha256,status,normalized_row_counts_json FROM import_runs WHERE run_id=?",
            (bundle["run_id"],),
        ).fetchone()
        if existing:
            if existing["manifest_sha256"] != manifest_sha256:
                raise ValueError("run_id already exists with different manifest bytes")
            return {
                "valid": True,
                "run_id": bundle["run_id"],
                "status": existing["status"],
                "idempotent": True,
                "normalized_rows": sum(json.loads(existing["normalized_row_counts_json"]).values()),
            }

        root = manifest_path.parent
        connection.execute("BEGIN IMMEDIATE")
        source_ids = {}
        for artifact in bundle["artifacts"]:
            relative = artifact["relative_path"]
            packaged_path = f"raw/private-exports/{bundle['run_id']}/{relative}"
            cursor = connection.execute(
                """INSERT INTO source_manifest(
                    system,artifact_type,source_path,captured_at,sha256,bytes,status,notes,
                    source_ref,capture_method,source_version,record_count,sensitivity,completeness
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    bundle["source_system"], artifact["artifact_type"], packaged_path,
                    bundle["captured_at"], artifact["sha256"], artifact["bytes"], "staged",
                    f"Commerce import run {bundle['run_id']}",
                    f"import:{bundle['run_id']}:{relative}", bundle["capture_method"],
                    bundle["source_version"], artifact["record_count"], "restricted",
                    artifact["completeness"],
                ),
            )
            source_ids[relative] = int(cursor.lastrowid)
        reconciliation = bundle["reconciliation"]
        connection.execute(
            """INSERT INTO import_runs(
                run_id,source_system,store_ref,captured_at,source_version,transform_version,
                manifest_sha256,scope_json,status,source_row_counts_json,
                normalized_row_counts_json,reconciliation_json,error_text
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,NULL)""",
            (
                bundle["run_id"], bundle["source_system"], bundle["store_ref"],
                bundle["captured_at"], bundle["source_version"], TRANSFORM_VERSION,
                manifest_sha256, _json(bundle["scope"]), "staged",
                _json(reconciliation["source_counts"]), _json(reconciliation["normalized_counts"]),
                _json(reconciliation),
            ),
        )
        connection.commit()

        try:
            connection.execute("BEGIN IMMEDIATE")
            rows = _load_snapshot_rows(root, bundle["artifacts"], source_ids)
            for row in rows:
                _validate_normalized_row(connection, row)
            processed = {entity: set() for entity in bundle["scope"]["entities"]}
            for row in rows:
                _insert_normalized_row(connection, bundle, row)
                processed[row["entity"]].add(row["source_record_id"])
            expected = reconciliation["normalized_counts"]
            actual = {entity: len(processed[entity]) for entity in processed}
            if actual != expected:
                raise ValueError(f"normalized source-record counts do not match reconciliation: {actual}")
            foreign_keys = list(connection.execute("PRAGMA foreign_key_check"))
            if foreign_keys:
                raise ValueError(f"foreign key reconciliation failed: {len(foreign_keys)} error(s)")
            connection.execute(
                "UPDATE source_manifest SET status='captured' WHERE source_ref LIKE ?",
                (f"import:{bundle['run_id']}:%",),
            )
            connection.execute(
                "UPDATE import_runs SET status='reconciled',error_text=NULL WHERE run_id=?",
                (bundle["run_id"],),
            )
            connection.commit()
        except Exception as exc:
            connection.rollback()
            connection.execute(
                "UPDATE import_runs SET status='failed',error_text=? WHERE run_id=?",
                (f"{type(exc).__name__}: normalization or reconciliation failed", bundle["run_id"]),
            )
            connection.commit()
            if isinstance(exc, sqlite3.IntegrityError) and "FOREIGN KEY" in str(exc).upper():
                raise ValueError("foreign key reconciliation failed") from exc
            if isinstance(exc, ValueError):
                raise
            raise ValueError("normalization or reconciliation failed") from exc
        return {
            "valid": validation["valid"],
            "run_id": bundle["run_id"],
            "status": "reconciled",
            "idempotent": False,
            "normalized_rows": len(rows),
            "source_manifest_rows": len(source_ids),
        }
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "--schema", type=Path,
        default=Path(__file__).parents[1] / "schemas" / "commerce-import-bundle-v1.schema.json",
    )
    args = parser.parse_args()
    print(json.dumps(import_bundle(args.database, args.manifest, args.schema), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
