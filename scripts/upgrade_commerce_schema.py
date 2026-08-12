#!/usr/bin/env python3
"""Add the provenance-constrained MT Uniforms commerce model to a recovery generation."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import capture_public_runtime
import recovery_package


COMMERCE_SCHEMA_VERSION = "1.0.0"

DEFINITIONS = {
    "catalog_categories": "parent_category_ref TEXT REFERENCES catalog_categories(record_id), name TEXT NOT NULL, lifecycle_status TEXT NOT NULL",
    "catalog_products": "category_ref TEXT REFERENCES catalog_categories(record_id), name TEXT NOT NULL, brand_name TEXT, supplier_name TEXT, description TEXT, lifecycle_status TEXT NOT NULL",
    "catalog_variants": "product_ref TEXT NOT NULL REFERENCES catalog_products(record_id), sku TEXT, name TEXT, price_minor INTEGER, currency TEXT, weight_grams INTEGER, lifecycle_status TEXT NOT NULL",
    "catalog_option_values": "product_ref TEXT NOT NULL REFERENCES catalog_products(record_id), option_group TEXT NOT NULL, option_value TEXT NOT NULL, sort_order INTEGER",
    "catalog_variant_options": "variant_ref TEXT NOT NULL REFERENCES catalog_variants(record_id), option_value_ref TEXT NOT NULL REFERENCES catalog_option_values(record_id)",
    "catalog_media": "product_ref TEXT REFERENCES catalog_products(record_id), variant_ref TEXT REFERENCES catalog_variants(record_id), media_role TEXT NOT NULL, portable_path TEXT, source_url TEXT, sha256 TEXT",
    "inventory_locations": "name TEXT NOT NULL, location_type TEXT NOT NULL, lifecycle_status TEXT NOT NULL",
    "inventory_levels": "variant_ref TEXT NOT NULL REFERENCES catalog_variants(record_id), location_ref TEXT NOT NULL REFERENCES inventory_locations(record_id), on_hand INTEGER NOT NULL, reserved INTEGER NOT NULL DEFAULT 0, observed_at TEXT NOT NULL",
    "inventory_movements": "variant_ref TEXT NOT NULL REFERENCES catalog_variants(record_id), location_ref TEXT NOT NULL REFERENCES inventory_locations(record_id), quantity_delta INTEGER NOT NULL, movement_type TEXT NOT NULL, occurred_at TEXT NOT NULL",
    "business_accounts": "account_type TEXT NOT NULL, name TEXT NOT NULL, tax_exempt INTEGER NOT NULL DEFAULT 0 CHECK(tax_exempt IN (0,1)), payment_terms_days INTEGER, lifecycle_status TEXT NOT NULL",
    "account_members": "account_ref TEXT NOT NULL REFERENCES business_accounts(record_id), display_name TEXT NOT NULL, email TEXT, role_name TEXT, lifecycle_status TEXT NOT NULL",
    "account_addresses": "account_ref TEXT NOT NULL REFERENCES business_accounts(record_id), address_role TEXT NOT NULL, address_json TEXT NOT NULL CHECK(json_valid(address_json))",
    "tax_exemptions": "account_ref TEXT NOT NULL REFERENCES business_accounts(record_id), jurisdiction TEXT, certificate_ref TEXT, valid_from TEXT, valid_to TEXT, status TEXT NOT NULL",
    "entitlements": "account_ref TEXT NOT NULL REFERENCES business_accounts(record_id), member_ref TEXT REFERENCES account_members(record_id), entitlement_type TEXT NOT NULL, rule_json TEXT NOT NULL CHECK(json_valid(rule_json)), status TEXT NOT NULL",
    "allowance_ledger": "account_ref TEXT NOT NULL REFERENCES business_accounts(record_id), member_ref TEXT NOT NULL REFERENCES account_members(record_id), amount_minor INTEGER NOT NULL, currency TEXT NOT NULL, entry_type TEXT NOT NULL, occurred_at TEXT NOT NULL, reset_period TEXT",
    "price_lists": "account_ref TEXT REFERENCES business_accounts(record_id), name TEXT NOT NULL, currency TEXT NOT NULL, valid_from TEXT, valid_to TEXT, lifecycle_status TEXT NOT NULL",
    "price_list_entries": "price_list_ref TEXT NOT NULL REFERENCES price_lists(record_id), product_ref TEXT REFERENCES catalog_products(record_id), variant_ref TEXT REFERENCES catalog_variants(record_id), price_minor INTEGER NOT NULL, minimum_quantity INTEGER NOT NULL DEFAULT 1",
    "promotions": "name TEXT NOT NULL, rule_json TEXT NOT NULL CHECK(json_valid(rule_json)), valid_from TEXT, valid_to TEXT, lifecycle_status TEXT NOT NULL",
    "commerce_orders": "account_ref TEXT REFERENCES business_accounts(record_id), member_ref TEXT REFERENCES account_members(record_id), order_number TEXT, status TEXT NOT NULL, currency TEXT NOT NULL, subtotal_minor INTEGER, tax_minor INTEGER, shipping_minor INTEGER, discount_minor INTEGER, total_minor INTEGER, placed_at TEXT, billing_address_json TEXT CHECK(billing_address_json IS NULL OR json_valid(billing_address_json)), shipping_address_json TEXT CHECK(shipping_address_json IS NULL OR json_valid(shipping_address_json))",
    "commerce_order_lines": "order_ref TEXT NOT NULL REFERENCES commerce_orders(record_id), product_ref TEXT REFERENCES catalog_products(record_id), variant_ref TEXT REFERENCES catalog_variants(record_id), line_number INTEGER NOT NULL, quantity INTEGER NOT NULL, snapshot_name TEXT NOT NULL, snapshot_sku TEXT, snapshot_description TEXT, snapshot_options_json TEXT CHECK(snapshot_options_json IS NULL OR json_valid(snapshot_options_json)), unit_price_minor INTEGER NOT NULL, tax_minor INTEGER, discount_minor INTEGER, line_total_minor INTEGER NOT NULL",
    "line_customizations": "order_line_ref TEXT NOT NULL REFERENCES commerce_order_lines(record_id), customization_type TEXT NOT NULL, label TEXT, value_text TEXT, portable_file_path TEXT, surcharge_minor INTEGER, production_status TEXT",
    "purchase_orders": "order_ref TEXT REFERENCES commerce_orders(record_id), account_ref TEXT REFERENCES business_accounts(record_id), po_number TEXT NOT NULL, amount_minor INTEGER, currency TEXT, status TEXT NOT NULL, issued_at TEXT",
    "invoices": "order_ref TEXT REFERENCES commerce_orders(record_id), account_ref TEXT REFERENCES business_accounts(record_id), invoice_number TEXT, status TEXT NOT NULL, currency TEXT NOT NULL, total_minor INTEGER NOT NULL, due_at TEXT, issued_at TEXT",
    "payments": "order_ref TEXT REFERENCES commerce_orders(record_id), invoice_ref TEXT REFERENCES invoices(record_id), provider TEXT, provider_reference TEXT, tender_type TEXT, amount_minor INTEGER NOT NULL, currency TEXT NOT NULL, status TEXT NOT NULL, occurred_at TEXT NOT NULL",
    "refunds": "payment_ref TEXT REFERENCES payments(record_id), order_ref TEXT REFERENCES commerce_orders(record_id), provider_reference TEXT, amount_minor INTEGER NOT NULL, currency TEXT NOT NULL, reason TEXT, status TEXT NOT NULL, occurred_at TEXT NOT NULL",
    "fulfillments": "order_ref TEXT NOT NULL REFERENCES commerce_orders(record_id), method TEXT NOT NULL, carrier TEXT, tracking_number TEXT, status TEXT NOT NULL, shipped_at TEXT, delivered_at TEXT",
    "fulfillment_lines": "fulfillment_ref TEXT NOT NULL REFERENCES fulfillments(record_id), order_line_ref TEXT NOT NULL REFERENCES commerce_order_lines(record_id), quantity INTEGER NOT NULL",
    "returns": "order_ref TEXT NOT NULL REFERENCES commerce_orders(record_id), return_number TEXT, status TEXT NOT NULL, reason TEXT, requested_at TEXT, received_at TEXT",
    "return_lines": "return_ref TEXT NOT NULL REFERENCES returns(record_id), order_line_ref TEXT NOT NULL REFERENCES commerce_order_lines(record_id), quantity INTEGER NOT NULL, resolution TEXT, refund_ref TEXT REFERENCES refunds(record_id)",
    "production_artwork": "account_ref TEXT REFERENCES business_accounts(record_id), name TEXT, portable_path TEXT, sha256 TEXT, lifecycle_status TEXT NOT NULL",
    "production_proofs": "artwork_ref TEXT REFERENCES production_artwork(record_id), order_line_ref TEXT REFERENCES commerce_order_lines(record_id), portable_path TEXT, sha256 TEXT, status TEXT NOT NULL, approved_at TEXT",
    "production_work_orders": "order_ref TEXT REFERENCES commerce_orders(record_id), order_line_ref TEXT REFERENCES commerce_order_lines(record_id), due_at TEXT, status TEXT NOT NULL, instructions TEXT",
    "production_operations": "work_order_ref TEXT NOT NULL REFERENCES production_work_orders(record_id), operation_type TEXT NOT NULL, sequence_number INTEGER NOT NULL, status TEXT NOT NULL, completed_at TEXT, qc_result TEXT",
    "integration_mappings": "left_system TEXT NOT NULL, left_type TEXT NOT NULL, left_id TEXT NOT NULL, right_system TEXT NOT NULL, right_type TEXT NOT NULL, right_id TEXT NOT NULL, mapping_status TEXT NOT NULL, observed_at TEXT NOT NULL",
    "audit_events": "entity_table TEXT NOT NULL, entity_record_id TEXT NOT NULL, event_type TEXT NOT NULL, occurred_at TEXT NOT NULL, actor_ref TEXT, event_json TEXT NOT NULL CHECK(json_valid(event_json))",
}
REQUIRED_TABLES = set(DEFINITIONS)

COMMON_PROVENANCE = """source_system TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    extracted_at TEXT NOT NULL,
    source_id INTEGER NOT NULL REFERENCES source_manifest(source_id),
    UNIQUE(source_system, source_record_id)"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def apply_schema(database: Path) -> dict:
    database = Path(database)
    connection = sqlite3.connect(database)
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "CREATE TABLE IF NOT EXISTS recovery_metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        for table, fields in DEFINITIONS.items():
            connection.execute(
                f"CREATE TABLE IF NOT EXISTS {table}(record_id TEXT PRIMARY KEY, {fields}, {COMMON_PROVENANCE})"
            )
        connection.executemany(
            "INSERT INTO recovery_metadata(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            {
                "commerce_schema_version": COMMERCE_SCHEMA_VERSION,
                "commerce_schema_applied_at": utc_now(),
                "commerce_schema_policy": "empty-until-source-backed",
            }.items(),
        )
        connection.commit()
        tables = {row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        errors = list(connection.execute("PRAGMA foreign_key_check"))
        return {
            "schema_version": COMMERCE_SCHEMA_VERSION,
            "table_count": len(REQUIRED_TABLES),
            "missing_tables": sorted(REQUIRED_TABLES - tables),
            "foreign_key_errors": len(errors),
        }
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _package_tools_and_lineage(root: Path, captured_at: str) -> None:
    tools = root / "tools"
    tools.mkdir(exist_ok=True)
    tool_sources = [
        Path(__file__),
        Path(capture_public_runtime.__file__),
        Path(recovery_package.__file__),
    ]
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        connection.execute("BEGIN IMMEDIATE")
        for source in tool_sources:
            packaged = tools / source.name
            shutil.copy2(source, packaged)
            relative = packaged.relative_to(root).as_posix()
            digest = recovery_package.sha256_file(packaged)
            values = (
                captured_at, digest, packaged.stat().st_size,
                f"REC-005 packaged recovery tool: {source.name}", relative,
            )
            updated = connection.execute(
                """UPDATE source_manifest SET captured_at=?, sha256=?, bytes=?, status='captured',
                    notes=? WHERE source_path=?""",
                values,
            ).rowcount
            if not updated:
                connection.execute(
                    """INSERT INTO source_manifest(
                        system, artifact_type, source_path, captured_at, sha256, bytes, status,
                        notes, source_ref, capture_method, record_count, sensitivity, completeness
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        "recovery-tooling", "recovery-tool", relative, captured_at, digest,
                        packaged.stat().st_size, "captured",
                        f"REC-005 packaged recovery tool: {source.name}",
                        f"recovery-tool:{source.name}", "deterministic-copy", 0,
                        "internal", "complete-file",
                    ),
                )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def create_generation(source: Path, destination: Path) -> dict:
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    if not source.is_dir():
        raise ValueError(f"source generation does not exist: {source}")
    if destination.exists():
        raise ValueError(f"destination already exists; recovery generations are immutable: {destination}")
    shutil.copytree(source, destination)
    apply_schema(destination / recovery_package.DATABASE_FILE)
    now = utc_now()
    connection = sqlite3.connect(destination / recovery_package.DATABASE_FILE)
    try:
        connection.executemany(
            "INSERT INTO recovery_metadata(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            {"generation": "REC-005", "parent_generation": "REC-004"}.items(),
        )
        connection.commit()
    finally:
        connection.close()
    manifest_path = destination / "package-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["generation"] = "REC-005"
    manifest["parent_generation"] = "REC-004"
    manifest["generated_at"] = now
    manifest["normalized_commerce_schema"] = {
        "version": COMMERCE_SCHEMA_VERSION,
        "tables": sorted(REQUIRED_TABLES),
        "population_status": "empty-awaiting-authenticated-exports",
        "provenance_policy": "every-row-requires-source-manifest-reference",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    _package_tools_and_lineage(destination, now)
    recovery_package.write_checksums(destination)
    return verify_generation(destination)


def finalize_generation(root: Path) -> dict:
    root = Path(root).resolve()
    manifest = json.loads((root / "package-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("generation") != "REC-005":
        raise ValueError("package generation is not REC-005")
    _package_tools_and_lineage(root, utc_now())
    recovery_package.write_checksums(root)
    return verify_generation(root)


def verify_generation(root: Path, expected_generation: str = "REC-005") -> dict:
    root = Path(root).resolve()
    package = capture_public_runtime.verify_generation(root, expected_generation=expected_generation)
    manifest = json.loads((root / "package-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("generation") != expected_generation:
        raise ValueError(f"package generation is not {expected_generation}")
    database = root / recovery_package.DATABASE_FILE
    connection = sqlite3.connect(database)
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        tables = {row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        missing = REQUIRED_TABLES - tables
        if missing:
            raise ValueError(f"commerce schema tables are missing: {sorted(missing)}")
        version = connection.execute(
            "SELECT value FROM recovery_metadata WHERE key='commerce_schema_version'"
        ).fetchone()
        if not version or version[0] != COMMERCE_SCHEMA_VERSION:
            raise ValueError("commerce schema version metadata is missing or unsupported")
        errors = list(connection.execute("PRAGMA foreign_key_check"))
        if errors:
            raise ValueError(f"commerce schema foreign-key errors: {errors[:3]}")
        populated = {table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                     for table in sorted(REQUIRED_TABLES)}
    finally:
        connection.close()
    return {
        "valid": True,
        "generation": expected_generation,
        "commerce_schema_version": COMMERCE_SCHEMA_VERSION,
        "commerce_tables": len(REQUIRED_TABLES),
        "populated_rows": sum(populated.values()),
        "runtime": package,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create")
    create.add_argument("source", type=Path)
    create.add_argument("destination", type=Path)
    verify = sub.add_parser("verify")
    verify.add_argument("root", type=Path)
    finalize = sub.add_parser("finalize")
    finalize.add_argument("root", type=Path)
    args = parser.parse_args()
    if args.command == "create":
        report = create_generation(args.source, args.destination)
    elif args.command == "finalize":
        report = finalize_generation(args.root)
    else:
        report = verify_generation(args.root)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
