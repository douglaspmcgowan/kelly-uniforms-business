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
MODULE_PATH = SCRIPT_DIR / "import_commerce_bundle_v2.py"


def load_importer():
    if not MODULE_PATH.is_file():
        raise AssertionError("import_commerce_bundle_v2.py is missing")
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location("import_commerce_bundle_v2", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CommerceBundleImporterV2Tests(unittest.TestCase):
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

    def write_artifact(self, root, relative, artifact_type, entity, payload, count):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        return {
            "relative_path": relative,
            "artifact_type": artifact_type,
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
            "record_count": count,
            "completeness": "complete-file",
            "entity": entity,
        }

    def row(self, source_id, locator, entity, normalized_rows):
        return (
            json.dumps(
                {
                    "source_record_id": source_id,
                    "source_locator": locator,
                    "entity": entity,
                    "record": {"native_id": source_id},
                    "normalized_rows": normalized_rows,
                },
                separators=(",", ":"),
            )
            + "\n"
        ).encode("utf-8")

    def write_manifest(self, root, artifacts, entities, source_counts, normalized_counts):
        manifest = {
            "schema_version": "mt-uniforms-commerce-import/v1",
            "run_id": "fixture-v2-import-001",
            "source_system": "opencart",
            "store_ref": "fixture-store",
            "captured_at": "2026-08-10T00:00:00Z",
            "source_version": "3.x-fixture",
            "capture_method": "native-database-export",
            "status": "reconciled",
            "scope": {"kind": "complete", "entities": entities},
            "artifacts": artifacts,
            "reconciliation": {
                "source_counts": source_counts,
                "normalized_counts": normalized_counts,
                "skipped_counts": {entity: 0 for entity in entities},
                "skips": [],
                "foreign_key_errors": 0,
                "unresolved_conflicts": 0,
                "money_checks": [],
            },
        }
        path = root / "export-manifest.json"
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return path

    def test_parent_category_is_inserted_before_lexically_earlier_child(self):
        importer = load_importer()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            database = self.make_database(root)
            sql = self.write_artifact(root, "database.sql", "database-sql", "categories", b"-- fixture\n", 0)
            child = self.row(
                "category:10",
                "table:category/pk:10",
                "categories",
                [{
                    "table": "catalog_categories",
                    "record_id": "opencart:category:a-child",
                    "values": {
                        "parent_category_ref": "opencart:category:z-parent",
                        "name": "Child",
                        "lifecycle_status": "active",
                    },
                }],
            )
            parent = self.row(
                "category:20",
                "table:category/pk:20",
                "categories",
                [{
                    "table": "catalog_categories",
                    "record_id": "opencart:category:z-parent",
                    "values": {
                        "parent_category_ref": None,
                        "name": "Parent",
                        "lifecycle_status": "active",
                    },
                }],
            )
            categories = self.write_artifact(
                root, "categories.ndjson", "table-snapshot", "categories", child + parent, 2
            )
            manifest = self.write_manifest(
                root, [sql, categories], ["categories"], {"categories": 2}, {"categories": 2}
            )

            report = importer.import_bundle(database, manifest, SCHEMA_PATH)

            self.assertEqual(report["status"], "reconciled")
            connection = sqlite3.connect(database)
            try:
                self.assertEqual(
                    connection.execute(
                        "SELECT parent_category_ref FROM catalog_categories WHERE record_id=?",
                        ("opencart:category:a-child",),
                    ).fetchone()[0],
                    "opencart:category:z-parent",
                )
            finally:
                connection.close()

    def test_joined_row_records_every_declared_source_lineage(self):
        importer = load_importer()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            database = self.make_database(root)
            sql = self.write_artifact(root, "database.sql", "database-sql", "categories", b"-- fixture\n", 0)
            category_body = self.row(
                "category:2",
                "table:category/pk:2",
                "categories",
                [{
                    "table": "catalog_categories",
                    "record_id": "opencart:category:2",
                    "values": {"parent_category_ref": None, "name": "Duty Gear", "lifecycle_status": "active"},
                }],
            )
            category = self.write_artifact(
                root, "categories.ndjson", "table-snapshot", "categories", category_body, 1
            )
            product_body = self.row(
                "product:7",
                "table:product/pk:7",
                "products",
                [
                    {
                        "table": "catalog_products",
                        "record_id": "opencart:product:7",
                        "values": {
                            "category_ref": None,
                            "name": "Duty Shirt",
                            "brand_name": None,
                            "supplier_name": None,
                            "description": None,
                            "lifecycle_status": "active",
                        },
                    },
                    {
                        "table": "catalog_product_categories",
                        "record_id": "opencart:product-category:7:2",
                        "values": {
                            "product_ref": "opencart:product:7",
                            "category_ref": "opencart:category:2",
                            "is_primary": 0,
                            "sort_order": 0,
                        },
                        "lineage": [
                            {
                                "artifact_path": "products.ndjson",
                                "source_record_id": "product:7",
                                "source_locator": "table:product/pk:7",
                                "relation_role": "product-source",
                            },
                            {
                                "artifact_path": "categories.ndjson",
                                "source_record_id": "category:2",
                                "source_locator": "table:category/pk:2",
                                "relation_role": "category-source",
                            },
                        ],
                    },
                ],
            )
            product = self.write_artifact(
                root, "products.ndjson", "table-snapshot", "products", product_body, 1
            )
            manifest = self.write_manifest(
                root,
                [sql, category, product],
                ["categories", "products"],
                {"categories": 1, "products": 1},
                {"categories": 1, "products": 1},
            )

            importer.import_bundle(database, manifest, SCHEMA_PATH)

            connection = sqlite3.connect(database)
            try:
                lineage = connection.execute(
                    """SELECT source_record_id,source_locator,relation_role
                       FROM record_lineage WHERE entity_record_id=? ORDER BY relation_role""",
                    ("opencart:product-category:7:2",),
                ).fetchall()
            finally:
                connection.close()
            self.assertEqual(
                lineage,
                [
                    ("category:2", "table:category/pk:2", "category-source"),
                    ("product:7", "table:product/pk:7", "product-source"),
                ],
            )


if __name__ == "__main__":
    unittest.main()
