import hashlib
import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("package_capture_ready_generation.py")


def load_packager():
    if not MODULE_PATH.is_file():
        raise AssertionError("package_capture_ready_generation.py is missing")
    if str(MODULE_PATH.parent) not in sys.path:
        sys.path.insert(0, str(MODULE_PATH.parent))
    spec = importlib.util.spec_from_file_location("package_capture_ready_generation", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CaptureReadyGenerationTests(unittest.TestCase):
    def make_rec008_fixture(self):
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
        connection.executemany(
            "INSERT INTO recovery_metadata(key,value) VALUES(?,?)",
            [("generation", "REC-008"), ("parent_generation", "REC-007")],
        )
        connection.commit()
        connection.close()
        (root / "package-manifest.json").write_text(
            json.dumps(
                {
                    "generation": "REC-008",
                    "parent_generation": "REC-007",
                    "commerce_import": {
                        "schema_version": "1.1.0",
                        "readiness": "ready-awaiting-authenticated-exports",
                        "population_status": "empty-awaiting-authenticated-exports",
                    },
                }
            ),
            encoding="utf-8",
        )
        tooling = Path(temporary.name) / "tooling"
        tooling.mkdir()
        for name in ("capture.py", "importer.py", "contract.md"):
            (tooling / name).write_text(f"{name}\n", encoding="utf-8")
        return temporary, root, tooling

    def test_stage_adds_capture_tools_and_promotes_generation_metadata(self):
        packager = load_packager()
        temporary, root, tooling = self.make_rec008_fixture()
        self.addCleanup(temporary.cleanup)
        assets = [
            packager.PackagedAsset(tooling / "capture.py", "tools/capture.py", "capture-tool"),
            packager.PackagedAsset(tooling / "importer.py", "tools/importer.py", "recovery-tool"),
            packager.PackagedAsset(tooling / "contract.md", "docs/contract.md", "capture-contract"),
        ]

        report = packager.stage_capture_readiness(
            root, assets, captured_at="2026-08-10T01:00:00Z"
        )

        manifest = json.loads((root / "package-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["generation"], "REC-009")
        self.assertEqual(manifest["parent_generation"], "REC-008")
        self.assertEqual(
            manifest["source_capture"]["readiness"],
            "tools-packaged-awaiting-authenticated-exports",
        )
        self.assertEqual(
            manifest["commerce_import"]["tool"],
            "tools/package_capture_ready_generation.py",
        )
        self.assertEqual(
            manifest["commerce_import"]["payload_contract"],
            "docs/recovery/commerce-normalization-payload-v2.md",
        )
        self.assertEqual(report["packaged_assets"], 3)
        connection = sqlite3.connect(root / "mt_uniforms_recovery.sqlite")
        try:
            metadata = dict(connection.execute("SELECT key,value FROM recovery_metadata"))
            rows = connection.execute(
                "SELECT source_path,sha256,bytes FROM source_manifest ORDER BY source_path"
            ).fetchall()
        finally:
            connection.close()
        self.assertEqual(metadata["generation"], "REC-009")
        self.assertEqual(metadata["parent_generation"], "REC-008")
        self.assertEqual(
            metadata["source_capture_readiness"],
            "tools-packaged-awaiting-authenticated-exports",
        )
        self.assertEqual(len(rows), 3)
        for source_path, digest, size in rows:
            packaged = root / source_path
            self.assertEqual(digest, hashlib.sha256(packaged.read_bytes()).hexdigest())
            self.assertEqual(size, packaged.stat().st_size)

    def test_default_assets_package_ecwid_capture_and_importer_v2(self):
        packager = load_packager()

        destinations = {asset.destination for asset in packager.default_assets()}

        self.assertIn("tools/capture_ecwid_api.py", destinations)
        self.assertIn("tools/import_commerce_bundle_v2.py", destinations)
        self.assertIn("docs/recovery/ecwid-api-capture-runbook.md", destinations)
        self.assertIn("docs/recovery/commerce-normalization-payload-v2.md", destinations)

    def test_stage_refuses_to_replace_non_replaceable_asset(self):
        packager = load_packager()
        temporary, root, tooling = self.make_rec008_fixture()
        self.addCleanup(temporary.cleanup)
        destination = root / "docs" / "contract.md"
        destination.parent.mkdir()
        destination.write_text("existing\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "already exists"):
            packager.stage_capture_readiness(
                root,
                [
                    packager.PackagedAsset(
                        tooling / "contract.md", "docs/contract.md", "capture-contract"
                    )
                ],
                captured_at="2026-08-10T01:00:00Z",
            )


if __name__ == "__main__":
    unittest.main()
