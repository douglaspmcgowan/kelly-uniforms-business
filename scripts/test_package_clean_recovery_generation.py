import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("package_clean_recovery_generation.py")


def load_packager():
    if not MODULE_PATH.is_file():
        raise AssertionError("package_clean_recovery_generation.py is missing")
    if str(MODULE_PATH.parent) not in sys.path:
        sys.path.insert(0, str(MODULE_PATH.parent))
    spec = importlib.util.spec_from_file_location("package_clean_recovery_generation", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CleanRecoveryGenerationTests(unittest.TestCase):
    def test_cleanup_removes_only_sqlite_verifier_sidecars(self):
        """Fails if verification leaves excluded WAL/SHM files or deletes unrelated files."""
        packager = load_packager()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            wal = root / "mt_uniforms_recovery.sqlite-wal"
            shm = root / "mt_uniforms_recovery.sqlite-shm"
            unrelated = root / "keep.bin"
            wal.write_bytes(b"wal")
            shm.write_bytes(b"shm")
            unrelated.write_bytes(b"keep")

            removed = packager.cleanup_sqlite_sidecars(root)
            self.assertEqual(removed, 2)
            self.assertFalse(wal.exists())
            self.assertFalse(shm.exists())
            self.assertTrue(unrelated.exists())

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
                    "generation": "REC-014",
                    "parent_generation": "REC-013",
                    "commerce_import": {
                        "tool": "tools/package_operational_recovery_generation.py"
                    },
                    "restore_drill": {"status": "proven-package-local-disposable-copy"},
                    "service_account_inventory": {"services": 10},
                }
            )
            + "\n",
            encoding="utf-8",
        )
        cache = root / "tools" / "__pycache__"
        cache.mkdir(parents=True)
        (cache / "inherited.pyc").write_bytes(b"inherited")
        assets = Path(temporary.name) / "assets"
        assets.mkdir()
        (assets / "v3.py").write_text("print('v3')\n", encoding="utf-8")
        (assets / "contract.md").write_text("# V3\n", encoding="utf-8")
        return temporary, root, assets

    def test_stage_removes_inherited_cache_and_routes_to_v3(self):
        """Fails if REC-015 promotes inherited cache bytes or the mutating v2 drill route."""
        packager = load_packager()
        temporary, root, assets = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        packaged = [
            packager.PackagedAsset(
                assets / "v3.py", "tools/run_recovery_drill_v3.py", "recovery-tool"
            ),
            packager.PackagedAsset(
                assets / "contract.md",
                "docs/recovery/representative-restore-drill-v3.md",
                "recovery-contract",
            ),
        ]

        report = packager.stage_clean_readiness(
            root, packaged, captured_at="2026-08-10T05:00:00Z"
        )

        manifest = json.loads((root / "package-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(report["removed_cache_artifacts"], 1)
        self.assertEqual(manifest["generation"], "REC-015")
        self.assertEqual(manifest["parent_generation"], "REC-014")
        self.assertEqual(manifest["restore_drill"]["tool"], "tools/run_recovery_drill_v3.py")
        self.assertFalse(any(root.rglob("*.pyc")))
        self.assertFalse(any(path.name == "__pycache__" for path in root.rglob("__pycache__")))
        self.assertIn(
            "Package-local v3 drill: READY",
            (root / "RECOVERY-STATUS.md").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
