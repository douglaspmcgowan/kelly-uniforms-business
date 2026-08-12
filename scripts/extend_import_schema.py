#!/usr/bin/env python3
"""Extend the REC-007 commerce landing model for source-faithful imports."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

import upgrade_commerce_schema


IMPORT_SCHEMA_VERSION = "1.1.0"

NORMALIZED_DEFINITIONS = {
    "catalog_product_categories": (
        "product_ref TEXT NOT NULL REFERENCES catalog_products(record_id), "
        "category_ref TEXT NOT NULL REFERENCES catalog_categories(record_id), "
        "is_primary INTEGER NOT NULL CHECK(is_primary IN (0,1)), sort_order INTEGER"
    ),
    "catalog_option_groups": (
        "product_ref TEXT NOT NULL REFERENCES catalog_products(record_id), name TEXT NOT NULL, "
        "option_type TEXT NOT NULL, required INTEGER NOT NULL CHECK(required IN (0,1)), sort_order INTEGER"
    ),
    "commerce_order_adjustments": (
        "order_ref TEXT NOT NULL REFERENCES commerce_orders(record_id), "
        "order_line_ref TEXT REFERENCES commerce_order_lines(record_id), adjustment_type TEXT NOT NULL, "
        "name TEXT NOT NULL, amount_minor INTEGER NOT NULL, tax_minor INTEGER, "
        "metadata_json TEXT CHECK(metadata_json IS NULL OR json_valid(metadata_json))"
    ),
}

OPTION_VALUE_COLUMNS = {
    "option_group_ref": "TEXT REFERENCES catalog_option_groups(record_id)",
    "price_delta_minor": "INTEGER",
    "price_prefix": "TEXT",
    "weight_delta_grams": "INTEGER",
    "weight_prefix": "TEXT",
    "inventory_quantity": "INTEGER",
    "subtract_stock": "INTEGER CHECK(subtract_stock IN (0,1))",
    "sku": "TEXT",
}


def apply_schema(database: Path) -> dict:
    database = Path(database)
    upgrade_commerce_schema.apply_schema(database)
    connection = sqlite3.connect(database)
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            """CREATE TABLE IF NOT EXISTS import_runs(
                run_id TEXT PRIMARY KEY,
                source_system TEXT NOT NULL CHECK(source_system IN ('opencart','ecwid')),
                store_ref TEXT NOT NULL,
                captured_at TEXT NOT NULL,
                source_version TEXT NOT NULL,
                transform_version TEXT NOT NULL,
                manifest_sha256 TEXT NOT NULL,
                scope_json TEXT NOT NULL CHECK(json_valid(scope_json)),
                status TEXT NOT NULL CHECK(status IN ('staged','reconciled','failed')),
                source_row_counts_json TEXT NOT NULL CHECK(json_valid(source_row_counts_json)),
                normalized_row_counts_json TEXT NOT NULL CHECK(json_valid(normalized_row_counts_json)),
                reconciliation_json TEXT NOT NULL CHECK(json_valid(reconciliation_json)),
                error_text TEXT
            )"""
        )
        connection.execute(
            """CREATE TABLE IF NOT EXISTS record_lineage(
                entity_table TEXT NOT NULL,
                entity_record_id TEXT NOT NULL,
                source_id INTEGER NOT NULL REFERENCES source_manifest(source_id),
                source_record_id TEXT NOT NULL,
                source_locator TEXT NOT NULL,
                relation_role TEXT NOT NULL,
                transform_version TEXT NOT NULL,
                PRIMARY KEY(entity_table,entity_record_id,source_id,source_record_id,relation_role)
            )"""
        )
        for table, fields in NORMALIZED_DEFINITIONS.items():
            connection.execute(
                f"CREATE TABLE IF NOT EXISTS {table}(record_id TEXT PRIMARY KEY, {fields}, "
                f"{upgrade_commerce_schema.COMMON_PROVENANCE})"
            )
        existing_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(catalog_option_values)")
        }
        for name, declaration in OPTION_VALUE_COLUMNS.items():
            if name not in existing_columns:
                connection.execute(f"ALTER TABLE catalog_option_values ADD COLUMN {name} {declaration}")
        connection.executemany(
            "INSERT INTO recovery_metadata(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            {
                "commerce_import_schema_version": IMPORT_SCHEMA_VERSION,
                "commerce_import_policy": "raw-first-fail-closed",
            }.items(),
        )
        connection.commit()
        tables = {
            row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        option_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(catalog_option_values)")
        }
        foreign_key_errors = list(connection.execute("PRAGMA foreign_key_check"))
        required_tables = set(NORMALIZED_DEFINITIONS) | {"import_runs", "record_lineage"}
        return {
            "schema_version": IMPORT_SCHEMA_VERSION,
            "missing_tables": sorted(required_tables - tables),
            "missing_option_columns": sorted(set(OPTION_VALUE_COLUMNS) - option_columns),
            "foreign_key_errors": len(foreign_key_errors),
        }
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    args = parser.parse_args()
    print(json.dumps(apply_schema(args.database), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
