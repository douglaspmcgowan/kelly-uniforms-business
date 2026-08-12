import hashlib
import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
SCHEMA_PATH = SCRIPT_DIR.parents[0] / "schemas" / "commerce-import-bundle-v1.schema.json"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def load_module(name):
    path = SCRIPT_DIR / f"{name}.py"
    if not path.is_file():
        raise AssertionError(f"{path.name} is missing")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CommerceBundleImportTests(unittest.TestCase):
    def make_database(self, root):
        database = root / "recovery.sqlite"
        connection = sqlite3.connect(database)
        connection.execute(
            """CREATE TABLE source_manifest(
                source_id INTEGER PRIMARY KEY, system TEXT NOT NULL,
                artifact_type TEXT NOT NULL, source_path TEXT, captured_at TEXT,
                sha256 TEXT, bytes INTEGER, status TEXT NOT NULL, notes TEXT,
                source_ref TEXT, source_uri TEXT, capture_method TEXT,
                source_version TEXT, record_count INTEGER, window_start TEXT,
                window_end TEXT, sensitivity TEXT, completeness TEXT
            )"""
        )
        connection.commit()
        connection.close()
        return database

    def write_artifact(self, root, relative, artifact_type, entity, content, record_count):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return {
            "relative_path": relative,
            "artifact_type": artifact_type,
            "sha256": hashlib.sha256(content).hexdigest(),
            "bytes": len(content),
            "record_count": record_count,
            "completeness": "complete-file",
            "entity": entity,
        }

    def normalized_line(self, source_record_id, source_locator, entity, rows, raw=None):
        return (json.dumps({
            "source_record_id": source_record_id,
            "source_locator": source_locator,
            "entity": entity,
            "record": raw or {"native_id": source_record_id},
            "normalized_rows": rows,
        }, separators=(",", ":")) + "\n").encode("utf-8")

    def make_bundle(self, root, invalid_category=False, unsupported_table=False):
        sql = self.write_artifact(
            root, "opencart/database.sql", "database-sql", "products",
            b"-- immutable synthetic OpenCart export\n", 0,
        )
        category_rows = [{
            "table": "catalog_categories",
            "record_id": "opencart:category:2",
            "values": {"parent_category_ref": None, "name": "Duty Gear", "lifecycle_status": "active"},
        }]
        category_body = self.normalized_line(
            "category:2", "table:mt_category/pk:2", "categories", category_rows,
            {"category_id": 2, "name": "Duty Gear"},
        )
        category = self.write_artifact(
            root, "opencart/table-snapshots/categories.ndjson", "table-snapshot",
            "categories", category_body, 1,
        )
        target_table = "not_a_recovery_table" if unsupported_table else "catalog_products"
        product_rows = [
            {
                "table": target_table,
                "record_id": "opencart:product:7",
                "values": {
                    "category_ref": None,
                    "name": "Synthetic Duty Shirt",
                    "brand_name": "Fixture Brand",
                    "supplier_name": None,
                    "description": "Synthetic test fixture",
                    "lifecycle_status": "active",
                },
            },
            {
                "table": "catalog_product_categories",
                "record_id": "opencart:product-category:7:2",
                "values": {
                    "product_ref": "opencart:product:7",
                    "category_ref": "opencart:category:999" if invalid_category else "opencart:category:2",
                    "is_primary": 0,
                    "sort_order": 0,
                },
            },
        ]
        product_body = self.normalized_line(
            "product:7", "table:mt_product/pk:7", "products", product_rows,
            {"product_id": 7, "sku": "FIXTURE-7", "price": "49.9500"},
        )
        product = self.write_artifact(
            root, "opencart/table-snapshots/products.ndjson", "table-snapshot",
            "products", product_body, 1,
        )
        bundle = {
            "schema_version": "mt-uniforms-commerce-import/v1",
            "run_id": "fixture-opencart-import-001",
            "source_system": "opencart",
            "store_ref": "fixture-store",
            "captured_at": "2026-08-10T00:00:00Z",
            "source_version": "3.x-fixture",
            "capture_method": "native-database-export",
            "status": "reconciled",
            "scope": {"kind": "complete", "entities": ["categories", "products"]},
            "artifacts": [sql, category, product],
            "reconciliation": {
                "source_counts": {"categories": 1, "products": 1},
                "normalized_counts": {"categories": 1, "products": 1},
                "skipped_counts": {"categories": 0, "products": 0},
                "skips": [],
                "foreign_key_errors": 0,
                "unresolved_conflicts": 0,
                "money_checks": [],
            },
        }
        manifest = root / "export-manifest.json"
        manifest.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
        return manifest

    def test_schema_adds_import_fidelity_structures_without_rows(self):
        schema = load_module("extend_import_schema")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            database = self.make_database(root)
            report = schema.apply_schema(database)
            self.assertEqual(report["schema_version"], "1.1.0")
            connection = sqlite3.connect(database)
            try:
                tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                self.assertTrue({
                    "import_runs", "record_lineage", "catalog_product_categories",
                    "catalog_option_groups", "commerce_order_adjustments",
                }.issubset(tables))
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM import_runs").fetchone()[0], 0)
                option_columns = {row[1] for row in connection.execute("PRAGMA table_info(catalog_option_values)")}
                self.assertTrue({
                    "option_group_ref", "price_delta_minor", "price_prefix", "weight_delta_grams",
                    "weight_prefix", "inventory_quantity", "subtract_stock", "sku",
                }.issubset(option_columns))
            finally:
                connection.close()

    def test_imports_products_memberships_and_exact_lineage(self):
        importer = load_module("import_commerce_bundle")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            database = self.make_database(root)
            report = importer.import_bundle(database, self.make_bundle(root), SCHEMA_PATH)
            self.assertEqual(report["status"], "reconciled")
            self.assertEqual(report["normalized_rows"], 3)
            connection = sqlite3.connect(database)
            try:
                self.assertEqual(
                    connection.execute("SELECT name FROM catalog_products").fetchone()[0],
                    "Synthetic Duty Shirt",
                )
                membership = connection.execute(
                    "SELECT product_ref,category_ref,is_primary FROM catalog_product_categories"
                ).fetchone()
                self.assertEqual(membership, ("opencart:product:7", "opencart:category:2", 0))
                lineage = connection.execute(
                    "SELECT entity_table,source_record_id,source_locator FROM record_lineage ORDER BY entity_table"
                ).fetchall()
                self.assertEqual(len(lineage), 3)
                self.assertIn(("catalog_products", "product:7", "table:mt_product/pk:7"), lineage)
            finally:
                connection.close()

    def test_identical_run_is_idempotent(self):
        importer = load_module("import_commerce_bundle")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            database = self.make_database(root)
            manifest = self.make_bundle(root)
            importer.import_bundle(database, manifest, SCHEMA_PATH)
            report = importer.import_bundle(database, manifest, SCHEMA_PATH)
            self.assertTrue(report["idempotent"])
            connection = sqlite3.connect(database)
            try:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM catalog_products").fetchone()[0], 1)
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM import_runs").fetchone()[0], 1)
            finally:
                connection.close()

    def test_same_run_id_with_changed_manifest_fails(self):
        importer = load_module("import_commerce_bundle")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            database = self.make_database(root)
            manifest = self.make_bundle(root)
            importer.import_bundle(database, manifest, SCHEMA_PATH)
            bundle = json.loads(manifest.read_text(encoding="utf-8"))
            bundle["capture_method"] = "different-capture"
            manifest.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "run_id already exists with different manifest bytes"):
                importer.import_bundle(database, manifest, SCHEMA_PATH)

    def test_reconciliation_failure_rolls_back_rows_but_keeps_source_evidence(self):
        importer = load_module("import_commerce_bundle")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            database = self.make_database(root)
            manifest = self.make_bundle(root, invalid_category=True)
            with self.assertRaisesRegex(ValueError, "foreign key"):
                importer.import_bundle(database, manifest, SCHEMA_PATH)
            connection = sqlite3.connect(database)
            try:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM catalog_products").fetchone()[0], 0)
                self.assertEqual(connection.execute("SELECT status FROM import_runs").fetchone()[0], "failed")
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM source_manifest").fetchone()[0], 3)
            finally:
                connection.close()

    def test_unsupported_target_table_fails_without_partial_rows(self):
        importer = load_module("import_commerce_bundle")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            database = self.make_database(root)
            manifest = self.make_bundle(root, unsupported_table=True)
            with self.assertRaisesRegex(ValueError, "unsupported normalized target table"):
                importer.import_bundle(database, manifest, SCHEMA_PATH)
            connection = sqlite3.connect(database)
            try:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM catalog_products").fetchone()[0], 0)
                self.assertEqual(connection.execute("SELECT status FROM import_runs").fetchone()[0], "failed")
            finally:
                connection.close()


if __name__ == "__main__":
    unittest.main()
