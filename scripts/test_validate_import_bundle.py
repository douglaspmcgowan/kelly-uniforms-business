import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("validate_import_bundle.py")
SCHEMA_PATH = Path(__file__).parents[1] / "schemas" / "commerce-import-bundle-v1.schema.json"


def load_validator():
    if not MODULE_PATH.is_file():
        raise AssertionError("validate_import_bundle.py is missing")
    spec = importlib.util.spec_from_file_location("validate_import_bundle", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ImportBundleContractTests(unittest.TestCase):
    def write_artifact(self, root, relative, content):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return {
            "relative_path": relative,
            "artifact_type": "database-sql" if relative.endswith(".sql") else "table-snapshot",
            "sha256": hashlib.sha256(content).hexdigest(),
            "bytes": len(content),
            "record_count": 1,
            "completeness": "complete-file",
            "entity": "products",
        }

    def valid_opencart_bundle(self, root):
        sql = self.write_artifact(root, "opencart/database.sql", b"-- immutable test export\n")
        snapshot_body = (
            json.dumps({
                "source_record_id": "product:7",
                "source_locator": "table:mt_product/pk:7",
                "entity": "products",
                "record": {"product_id": 7, "sku": "FIXTURE-7"},
            }, separators=(",", ":")) + "\n"
        ).encode("utf-8")
        snapshot = self.write_artifact(root, "opencart/table-snapshots/products.ndjson", snapshot_body)
        return {
            "schema_version": "mt-uniforms-commerce-import/v1",
            "run_id": "fixture-opencart-001",
            "source_system": "opencart",
            "store_ref": "fixture-store",
            "captured_at": "2026-08-10T00:00:00Z",
            "source_version": "3.x-fixture",
            "capture_method": "native-database-export",
            "status": "reconciled",
            "scope": {"kind": "complete", "entities": ["products"]},
            "artifacts": [sql, snapshot],
            "reconciliation": {
                "source_counts": {"products": 1},
                "normalized_counts": {"products": 1},
                "skipped_counts": {"products": 0},
                "skips": [],
                "foreign_key_errors": 0,
                "unresolved_conflicts": 0,
                "money_checks": [],
            },
        }

    def write_manifest(self, root, bundle):
        path = root / "export-manifest.json"
        path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
        return path

    def validate(self, root, bundle):
        validator = load_validator()
        return validator.validate_bundle(self.write_manifest(root, bundle), SCHEMA_PATH)

    def test_accepts_hash_verified_reconciled_opencart_bundle(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            report = self.validate(root, self.valid_opencart_bundle(root))
            self.assertTrue(report["valid"])
            self.assertEqual(report["artifact_count"], 2)
            self.assertEqual(report["source_records"], 1)

    def test_rejects_path_traversal_before_reading_artifact(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = self.valid_opencart_bundle(root)
            bundle["artifacts"][0]["relative_path"] = "../database.sql"
            with self.assertRaisesRegex(ValueError, "portable relative path"):
                self.validate(root, bundle)

    def test_rejects_artifact_checksum_mismatch(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = self.valid_opencart_bundle(root)
            bundle["artifacts"][0]["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                self.validate(root, bundle)

    def test_rejects_opencart_bundle_without_native_database_export(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = self.valid_opencart_bundle(root)
            bundle["artifacts"] = [a for a in bundle["artifacts"] if a["artifact_type"] != "database-sql"]
            with self.assertRaisesRegex(ValueError, "database-sql"):
                self.validate(root, bundle)

    def test_rejects_unaccounted_source_rows(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = self.valid_opencart_bundle(root)
            bundle["reconciliation"]["source_counts"]["products"] = 2
            with self.assertRaisesRegex(ValueError, "imported plus skipped"):
                self.validate(root, bundle)

    def test_rejects_sensitive_fields_in_normalization_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = self.valid_opencart_bundle(root)
            artifact = next(a for a in bundle["artifacts"] if a["artifact_type"] == "table-snapshot")
            body = (
                json.dumps({
                    "source_record_id": "customer:9",
                    "source_locator": "table:mt_customer/pk:9",
                    "entity": "customers",
                    "record": {"customer_id": 9, "password": "must-not-normalize"},
                }) + "\n"
            ).encode("utf-8")
            path = root / artifact["relative_path"]
            path.write_bytes(body)
            artifact["sha256"] = hashlib.sha256(body).hexdigest()
            artifact["bytes"] = len(body)
            artifact["entity"] = "customers"
            for source_artifact in bundle["artifacts"]:
                source_artifact["entity"] = "customers"
            bundle["scope"]["entities"] = ["customers"]
            bundle["reconciliation"]["source_counts"] = {"customers": 1}
            bundle["reconciliation"]["normalized_counts"] = {"customers": 1}
            bundle["reconciliation"]["skipped_counts"] = {"customers": 0}
            with self.assertRaisesRegex(ValueError, "sensitive field"):
                self.validate(root, bundle)

    def test_rejects_duplicate_source_record_ids(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = self.valid_opencart_bundle(root)
            artifact = next(a for a in bundle["artifacts"] if a["artifact_type"] == "table-snapshot")
            path = root / artifact["relative_path"]
            row = path.read_bytes()
            path.write_bytes(row + row)
            artifact["sha256"] = hashlib.sha256(row + row).hexdigest()
            artifact["bytes"] = len(row + row)
            artifact["record_count"] = 2
            bundle["reconciliation"]["source_counts"]["products"] = 2
            bundle["reconciliation"]["normalized_counts"]["products"] = 2
            with self.assertRaisesRegex(ValueError, "duplicate source_record_id"):
                self.validate(root, bundle)

    def test_rejects_ecwid_page_gap(self):
        validator = load_validator()
        pages = [
            {"offset": 0, "limit": 100, "count": 1, "total": 2, "items": [{"id": 1}]},
            {"offset": 2, "limit": 100, "count": 1, "total": 2, "items": [{"id": 2}]},
        ]
        with self.assertRaisesRegex(ValueError, "contiguous"):
            validator.validate_ecwid_pages(pages, "products")

    def test_rejects_binary_float_money_checks(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = self.valid_opencart_bundle(root)
            bundle["reconciliation"]["money_checks"] = [{
                "order_ref": "order:1", "source_total_minor": 10.5,
                "normalized_total_minor": 10, "rounding_quantum_minor": 1,
            }]
            with self.assertRaisesRegex(ValueError, "integer minor units"):
                self.validate(root, bundle)


if __name__ == "__main__":
    unittest.main()
