import hashlib
import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("package_operational_recovery_generation.py")


def load_packager():
    if not MODULE_PATH.is_file():
        raise AssertionError("package_operational_recovery_generation.py is missing")
    if str(MODULE_PATH.parent) not in sys.path:
        sys.path.insert(0, str(MODULE_PATH.parent))
    spec = importlib.util.spec_from_file_location(
        "package_operational_recovery_generation", MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OperationalRecoveryGenerationTests(unittest.TestCase):
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
        for name in ("RECOVERY-STATUS.md", "COMPLETION-AUDIT.md"):
            path = root / name
            path.write_text(f"stale {name}\n", encoding="utf-8")
            connection.execute(
                """INSERT INTO source_manifest(
                    system,artifact_type,source_path,captured_at,sha256,bytes,status,notes,
                    source_ref,capture_method,record_count,sensitivity,completeness
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    "recovery-tooling",
                    "recovery-status",
                    name,
                    "2026-08-10T00:00:00Z",
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                    path.stat().st_size,
                    "captured",
                    "stale",
                    f"rec013:generated:{name}",
                    "deterministic-render",
                    0,
                    "internal",
                    "complete-file",
                ),
            )
        connection.commit()
        connection.close()
        (root / "package-manifest.json").write_text(
            json.dumps(
                {
                    "generation": "REC-013",
                    "parent_generation": "REC-012",
                    "commerce_import": {
                        "tool": "tools/package_drill_ready_generation.py"
                    },
                    "restore_drill": {"status": "package-local-v1-failed"},
                    "service_account_inventory": {"services": 10},
                }
            )
            + "\n",
            encoding="utf-8",
        )
        assets = Path(temporary.name) / "assets"
        assets.mkdir()
        (assets / "drill-v2.py").write_text("print('v2')\n", encoding="utf-8")
        (assets / "contract.md").write_text("# V2\n", encoding="utf-8")
        return temporary, root, assets

    def test_stage_points_to_v2_and_updates_status_lineage_without_duplicates(self):
        """Fails if REC-014 keeps the broken v1 route or stale status hashes."""
        packager = load_packager()
        temporary, root, assets = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        packaged = [
            packager.PackagedAsset(
                assets / "drill-v2.py", "tools/run_recovery_drill_v2.py", "recovery-tool"
            ),
            packager.PackagedAsset(
                assets / "contract.md",
                "docs/recovery/representative-restore-drill-v2.md",
                "recovery-contract",
            ),
        ]

        report = packager.stage_operational_readiness(
            root, packaged, captured_at="2026-08-10T04:00:00Z"
        )

        manifest = json.loads((root / "package-manifest.json").read_text(encoding="utf-8"))
        status = (root / "RECOVERY-STATUS.md").read_text(encoding="utf-8")
        self.assertEqual(report["generation"], "REC-014")
        self.assertEqual(manifest["parent_generation"], "REC-013")
        self.assertEqual(manifest["restore_drill"]["status"], "ready-awaiting-self-test")
        self.assertEqual(
            manifest["restore_drill"]["tool"], "tools/run_recovery_drill_v2.py"
        )
        self.assertIn("# M&T Uniforms REC-014 recovery status", status)
        self.assertIn("Package-local v2 drill: READY", status)
        connection = sqlite3.connect(root / "mt_uniforms_recovery.sqlite")
        try:
            rows = connection.execute(
                "SELECT source_path,sha256,bytes FROM source_manifest "
                "WHERE source_path IN ('RECOVERY-STATUS.md','COMPLETION-AUDIT.md') "
                "ORDER BY source_path"
            ).fetchall()
        finally:
            connection.close()
        self.assertEqual(len(rows), 2)
        for source_path, digest, size in rows:
            path = root / source_path
            self.assertEqual(digest, hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(size, path.stat().st_size)

    def test_proof_marker_requires_successful_unchanged_authority_drill(self):
        """Fails if REC-014 can claim drill proof from an incomplete or failed report."""
        packager = load_packager()
        temporary, root, assets = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        packaged = [
            packager.PackagedAsset(
                assets / "drill-v2.py", "tools/run_recovery_drill_v2.py", "recovery-tool"
            ),
            packager.PackagedAsset(
                assets / "contract.md",
                "docs/recovery/representative-restore-drill-v2.md",
                "recovery-contract",
            ),
        ]
        packager.stage_operational_readiness(
            root, packaged, captured_at="2026-08-10T04:00:00Z"
        )

        with self.assertRaisesRegex(ValueError, "successful package-local drill"):
            packager.mark_drill_proven(
                root,
                {
                    "valid": True,
                    "authority_unchanged": False,
                    "import": {"status": "reconciled"},
                    "reconstruction": {"valid": True},
                },
                captured_at="2026-08-10T04:05:00Z",
            )


if __name__ == "__main__":
    unittest.main()
