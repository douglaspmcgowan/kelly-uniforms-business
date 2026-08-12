import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
MODULE_PATH = SCRIPT_DIR / "run_recovery_drill.py"
SCHEMA_PATH = SCRIPT_DIR.parents[0] / "schemas" / "commerce-import-bundle-v1.schema.json"


def load_drill():
    if not MODULE_PATH.is_file():
        raise AssertionError("run_recovery_drill.py is missing")
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location("run_recovery_drill", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_database(root: Path) -> Path:
    database = root / "mt_uniforms_recovery.sqlite"
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
    (root / "package-manifest.json").write_text(
        json.dumps({"generation": "TEST", "commerce_import": {}}) + "\n",
        encoding="utf-8",
    )
    return database


class RepresentativeRecoveryDrillTests(unittest.TestCase):
    def test_fixture_reconstructs_complete_agency_order_with_lineage(self):
        """Fails if any required agency-order relationship or amount is omitted or mislinked."""
        drill = load_drill()
        import package_import_ready_generation

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = root / "package"
            package.mkdir()
            database = make_database(package)
            bundle = drill.build_fixture_bundle(root / "bundle")

            import_report = package_import_ready_generation.stage_and_import_bundle(
                package, bundle, SCHEMA_PATH
            )
            report = drill.verify_reconstruction(database)

        self.assertEqual(import_report["status"], "reconciled")
        self.assertEqual(report["integrity"], "ok")
        self.assertEqual(report["foreign_key_errors"], 0)
        self.assertEqual(report["order_total_minor"], 12500)
        self.assertEqual(report["payment_minor"], 12500)
        self.assertEqual(report["refund_minor"], 2500)
        self.assertEqual(report["fulfilled_quantity"], 2)
        self.assertEqual(report["returned_quantity"], 1)
        self.assertEqual(report["lineage_rows"], 22)
        self.assertEqual(
            report["table_counts"],
            {
                "account_members": 1,
                "business_accounts": 1,
                "catalog_products": 1,
                "catalog_variants": 1,
                "commerce_order_lines": 1,
                "commerce_orders": 1,
                "entitlements": 1,
                "fulfillment_lines": 1,
                "fulfillments": 1,
                "invoices": 1,
                "line_customizations": 1,
                "payments": 1,
                "price_list_entries": 1,
                "price_lists": 1,
                "production_operations": 1,
                "production_work_orders": 1,
                "purchase_orders": 1,
                "refunds": 1,
                "return_lines": 1,
                "returns": 1,
                "tax_exemptions": 1,
                "audit_events": 1,
            },
        )

    def test_fixture_is_explicitly_synthetic_and_reconciles_source_counts(self):
        """Fails if drill evidence could be mistaken for client data or counts drift from rows."""
        drill = load_drill()

        with tempfile.TemporaryDirectory() as temporary:
            manifest_path = drill.build_fixture_bundle(Path(temporary) / "bundle")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(manifest["run_id"], "synthetic-restore-drill-v1")
        self.assertEqual(manifest["store_ref"], "synthetic-drill-never-client-data")
        self.assertEqual(manifest["scope"]["kind"], "partial")
        self.assertEqual(
            manifest["reconciliation"]["source_counts"],
            {"customers": 1, "orders": 1, "price_lists": 1, "products": 1},
        )
        self.assertEqual(
            manifest["reconciliation"]["normalized_counts"],
            manifest["reconciliation"]["source_counts"],
        )


if __name__ == "__main__":
    unittest.main()
