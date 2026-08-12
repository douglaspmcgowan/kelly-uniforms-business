#!/usr/bin/env python3
"""Import normalized commerce bundles with dependency ordering and full lineage."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

import extend_import_schema
import import_commerce_bundle
import recovery_package
import validate_import_bundle


TRANSFORM_VERSION = "mt-uniforms-normalized-payload/v2"
TABLE_ORDER = import_commerce_bundle.TABLE_ORDER
TABLE_RANK = import_commerce_bundle.TABLE_RANK


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _lineage_entries(target: dict, source_row: dict, artifact_path: str) -> list[dict]:
    declared = target.get("lineage")
    if declared is None:
        declared = [
            {
                "artifact_path": artifact_path,
                "source_record_id": str(source_row["source_record_id"]),
                "source_locator": str(source_row["source_locator"]),
                "relation_role": "primary-source",
            }
        ]
    if not isinstance(declared, list) or not declared:
        raise ValueError("normalized row lineage must be a non-empty array")
    normalized = []
    for entry in declared:
        if not isinstance(entry, dict):
            raise ValueError("normalized row lineage entry must be an object")
        required = ("artifact_path", "source_record_id", "source_locator", "relation_role")
        if any(not isinstance(entry.get(name), str) or not entry[name] for name in required):
            raise ValueError("normalized row lineage entry is incomplete")
        normalized.append({name: entry[name] for name in required})
    return normalized


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
                source_row = json.loads(line)
                targets = source_row.get("normalized_rows", [])
                if not isinstance(targets, list):
                    raise ValueError("normalized_rows must be an array")
                for target in targets:
                    if not isinstance(target, dict):
                        raise ValueError("normalized target row must be an object")
                    lineage = _lineage_entries(target, source_row, relative)
                    for entry in lineage:
                        if entry["artifact_path"] not in source_ids:
                            raise ValueError(
                                f"lineage references undeclared artifact: {entry['artifact_path']}"
                            )
                    normalized.append(
                        {
                            "table": target.get("table"),
                            "record_id": target.get("record_id"),
                            "values": target.get("values"),
                            "entity": source_row["entity"],
                            "entity_source_record_id": str(source_row["source_record_id"]),
                            "lineage": lineage,
                        }
                    )
    return _dependency_order(normalized)


def _order_categories(rows: list[dict]) -> list[dict]:
    pending = {str(row["record_id"]): row for row in rows}
    if len(pending) != len(rows):
        raise ValueError("duplicate normalized category record_id")
    ordered = []
    while pending:
        ready = [
            row
            for row in pending.values()
            if not row["values"].get("parent_category_ref")
            or row["values"].get("parent_category_ref") not in pending
        ]
        if not ready:
            raise ValueError("catalog category hierarchy contains a cycle")
        for row in sorted(ready, key=lambda item: str(item["record_id"])):
            ordered.append(row)
            del pending[str(row["record_id"])]
    return ordered


def _dependency_order(rows: list[dict]) -> list[dict]:
    by_table: dict[str, list[dict]] = {}
    for row in rows:
        by_table.setdefault(str(row["table"]), []).append(row)
    ordered = []
    all_tables = sorted(by_table, key=lambda table: (TABLE_RANK.get(table, 9999), table))
    for table in all_tables:
        table_rows = by_table[table]
        if table == "catalog_categories":
            ordered.extend(_order_categories(table_rows))
        else:
            ordered.extend(sorted(table_rows, key=lambda item: str(item["record_id"])))
    return ordered


def _insert_normalized_row(connection: sqlite3.Connection, bundle: dict, row: dict, source_ids: dict[str, int]) -> None:
    primary = row["lineage"][0]
    insert_row = {
        "table": row["table"],
        "record_id": row["record_id"],
        "values": row["values"],
        "source_id": source_ids[primary["artifact_path"]],
        "source_record_id": primary["source_record_id"],
    }
    import_commerce_bundle._validate_normalized_row(connection, insert_row)
    payload = {
        "record_id": row["record_id"],
        **row["values"],
        "source_system": bundle["source_system"],
        "source_record_id": primary["source_record_id"],
        "extracted_at": bundle["captured_at"],
        "source_id": source_ids[primary["artifact_path"]],
    }
    names = list(payload)
    connection.execute(
        f"INSERT INTO {row['table']}({','.join(names)}) VALUES({','.join('?' for _ in names)})",
        [payload[name] for name in names],
    )
    for lineage in row["lineage"]:
        connection.execute(
            """INSERT INTO record_lineage(
                entity_table,entity_record_id,source_id,source_record_id,source_locator,
                relation_role,transform_version
            ) VALUES(?,?,?,?,?,?,?)""",
            (
                row["table"],
                row["record_id"],
                source_ids[lineage["artifact_path"]],
                lineage["source_record_id"],
                lineage["source_locator"],
                lineage["relation_role"],
                TRANSFORM_VERSION,
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
                _json(reconciliation["source_counts"]),
                _json(reconciliation["normalized_counts"]), _json(reconciliation),
            ),
        )
        connection.commit()

        try:
            connection.execute("BEGIN IMMEDIATE")
            rows = _load_snapshot_rows(root, bundle["artifacts"], source_ids)
            for row in rows:
                primary = row["lineage"][0]
                import_commerce_bundle._validate_normalized_row(
                    connection,
                    {
                        "table": row["table"],
                        "record_id": row["record_id"],
                        "values": row["values"],
                        "source_id": source_ids[primary["artifact_path"]],
                        "source_record_id": primary["source_record_id"],
                    },
                )
            processed = {entity: set() for entity in bundle["scope"]["entities"]}
            for row in rows:
                _insert_normalized_row(connection, bundle, row, source_ids)
                processed[row["entity"]].add(row["entity_source_record_id"])
            expected = reconciliation["normalized_counts"]
            actual = {entity: len(processed[entity]) for entity in processed}
            if actual != expected:
                raise ValueError(
                    f"normalized source-record counts do not match reconciliation: {actual}"
                )
            foreign_keys = list(connection.execute("PRAGMA foreign_key_check"))
            if foreign_keys:
                raise ValueError(
                    f"foreign key reconciliation failed: {len(foreign_keys)} error(s)"
                )
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
        "--schema",
        type=Path,
        default=Path(__file__).parents[1] / "schemas" / "commerce-import-bundle-v1.schema.json",
    )
    args = parser.parse_args()
    print(json.dumps(import_bundle(args.database, args.manifest, args.schema), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
