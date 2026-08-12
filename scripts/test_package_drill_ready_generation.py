import hashlib
import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("package_drill_ready_generation.py")


def load_packager():
    if not MODULE_PATH.is_file():
        raise AssertionError("package_drill_ready_generation.py is missing")
    if str(MODULE_PATH.parent) not in sys.path:
        sys.path.insert(0, str(MODULE_PATH.parent))
    spec = importlib.util.spec_from_file_location("package_drill_ready_generation", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DrillReadyGenerationTests(unittest.TestCase):
    def make_fixture(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name) / "generation"
        root.mkdir()
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
        connection.execute(
            "CREATE TABLE recovery_metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        connection.commit()
        connection.close()
        (root / "package-manifest.json").write_text(
            json.dumps(
                {
                    "generation": "REC-012",
                    "parent_generation": "REC-011",
                    "public_media_completion": {
                        "url_backed_exact": 1541,
                        "embedded_exact": 1,
                        "total_exact": 1542,
                    },
                    "source_capture": {"captured_private_exports": False},
                    "clover_authenticated_scope": "excluded-per-client-decision",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        assets = Path(temporary.name) / "assets"
        assets.mkdir()
        (assets / "tool.py").write_text("print('drill')\n", encoding="utf-8")
        (assets / "contract.md").write_text("# Drill contract\n", encoding="utf-8")
        inventory = {
            "schema_version": "mt-uniforms-service-account-control/v1",
            "generated_from": "public-and-client-evidence-only",
            "contains_secrets": False,
            "services": [
                {
                    "service_id": "domain-registration",
                    "category": "domain",
                    "system": "mtuniforms.com",
                    "observed_configuration": "Public RDAP and DNS evidence captured",
                    "authoritative_owner": "UNKNOWN",
                    "payer": "UNKNOWN",
                    "renewal_date": "UNKNOWN",
                    "recovery_contact": "UNKNOWN",
                    "export_or_recovery_path": "Registrar account export or transfer procedure",
                    "control_status": "unverified",
                    "evidence_refs": ["raw/public-ownership/"],
                    "blockers": ["Primary registrar account evidence unavailable"],
                }
            ],
        }
        (assets / "inventory.json").write_text(
            json.dumps(inventory, indent=2) + "\n", encoding="utf-8"
        )
        return temporary, root, assets

    def test_stage_replaces_stale_status_and_packages_value_free_inventory(self):
        """Fails if REC-013 retains historical REC-003/REC-008 status or omits continuity fields."""
        packager = load_packager()
        temporary, root, assets = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        packaged = [
            packager.PackagedAsset(assets / "tool.py", "tools/tool.py", "recovery-tool"),
            packager.PackagedAsset(
                assets / "contract.md", "docs/recovery/contract.md", "recovery-contract"
            ),
            packager.PackagedAsset(
                assets / "inventory.json",
                "business-continuity/service-account-control-inventory.json",
                "continuity-inventory",
            ),
        ]

        report = packager.stage_drill_readiness(
            root, packaged, captured_at="2026-08-10T03:00:00Z"
        )

        manifest = json.loads((root / "package-manifest.json").read_text(encoding="utf-8"))
        status = (root / "RECOVERY-STATUS.md").read_text(encoding="utf-8")
        audit = (root / "COMPLETION-AUDIT.md").read_text(encoding="utf-8")
        self.assertEqual(report["generation"], "REC-013")
        self.assertEqual(manifest["generation"], "REC-013")
        self.assertEqual(manifest["parent_generation"], "REC-012")
        self.assertEqual(
            manifest["service_account_inventory"]["path"],
            "business-continuity/service-account-control-inventory.json",
        )
        self.assertEqual(manifest["service_account_inventory"]["control_status"], "unverified")
        self.assertIn("# M&T Uniforms REC-013 recovery status", status)
        self.assertIn("1,542 / 1,542", status)
        self.assertIn("Work Scope is enrolled", status)
        self.assertIn("Clover authenticated export is excluded by DEC-005", status)
        self.assertIn("Representative agency-order drill: PROVEN", audit)
        self.assertNotIn("REC-003 recovery status", status)
        self.assertNotIn("Canonical Kelly Uniforms Work Scope enrollment: MISSING", audit)
        connection = sqlite3.connect(root / "mt_uniforms_recovery.sqlite")
        try:
            row = connection.execute(
                "SELECT sha256,bytes FROM source_manifest WHERE source_path=?",
                ("business-continuity/service-account-control-inventory.json",),
            ).fetchone()
            metadata = dict(connection.execute("SELECT key,value FROM recovery_metadata"))
        finally:
            connection.close()
        inventory_path = root / "business-continuity/service-account-control-inventory.json"
        self.assertEqual(row[0], hashlib.sha256(inventory_path.read_bytes()).hexdigest())
        self.assertEqual(row[1], inventory_path.stat().st_size)
        self.assertEqual(metadata["generation"], "REC-013")
        self.assertEqual(metadata["parent_generation"], "REC-012")

    def test_inventory_rejects_missing_account_control_field(self):
        """Fails if an inventory can hide an unknown owner, payer, renewal, recovery, or export path."""
        packager = load_packager()
        temporary, _, assets = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        inventory_path = assets / "inventory.json"
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        del inventory["services"][0]["payer"]
        inventory_path.write_text(json.dumps(inventory), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "missing required fields"):
            packager.validate_service_inventory(inventory_path)


if __name__ == "__main__":
    unittest.main()
