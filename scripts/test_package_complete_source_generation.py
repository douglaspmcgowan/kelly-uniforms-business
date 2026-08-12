import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("package_complete_source_generation.py")


def load_packager():
    if not MODULE_PATH.is_file():
        raise AssertionError("package_complete_source_generation.py is missing")
    if str(MODULE_PATH.parent) not in sys.path:
        sys.path.insert(0, str(MODULE_PATH.parent))
    spec = importlib.util.spec_from_file_location("package_complete_source_generation", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CompleteSourceGenerationTests(unittest.TestCase):
    def make_fixture(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name) / "generation"
        root.mkdir()
        connection = sqlite3.connect(root / "mt_uniforms_recovery.sqlite")
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
        connection.execute("CREATE TABLE recovery_metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        connection.commit()
        connection.close()
        (root / "package-manifest.json").write_text(
            json.dumps(
                {
                    "generation": "REC-010",
                    "parent_generation": "REC-009",
                    "source_capture": {
                        "readiness": "opencart-and-ecwid-tools-packaged-awaiting-authenticated-exports",
                        "ecwid_tool": "tools/capture_ecwid_api.py",
                        "opencart_tool": "tools/capture_opencart_native_export.py",
                    },
                    "commerce_import": {"population_status": "empty-awaiting-authenticated-exports"},
                }
            ),
            encoding="utf-8",
        )
        tooling = Path(temporary.name) / "tooling"
        tooling.mkdir()
        (tooling / "ecwid-v2.py").write_text("print('v2')\n", encoding="utf-8")
        return temporary, root, tooling

    def test_stage_promotes_complete_ecwid_tool_and_generation_metadata(self):
        packager = load_packager()
        temporary, root, tooling = self.make_fixture()
        self.addCleanup(temporary.cleanup)

        report = packager.stage_complete_source_readiness(
            root,
            [packager.PackagedAsset(tooling / "ecwid-v2.py", "tools/ecwid-v2.py", "capture-tool")],
            captured_at="2026-08-10T05:00:00Z",
        )

        manifest = json.loads((root / "package-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["generation"], "REC-011")
        self.assertEqual(manifest["parent_generation"], "REC-010")
        self.assertEqual(
            manifest["source_capture"]["ecwid_tool"], "tools/capture_ecwid_api_v2.py"
        )
        self.assertEqual(
            manifest["source_capture"]["readiness"],
            "opencart-and-complete-ecwid-tools-packaged-awaiting-authenticated-exports",
        )
        self.assertEqual(
            manifest["commerce_import"]["tool"],
            "tools/package_complete_source_generation.py",
        )
        self.assertEqual(report["packaged_assets"], 1)
        connection = sqlite3.connect(root / "mt_uniforms_recovery.sqlite")
        try:
            metadata = dict(connection.execute("SELECT key,value FROM recovery_metadata"))
        finally:
            connection.close()
        self.assertEqual(metadata["generation"], "REC-011")
        self.assertEqual(metadata["parent_generation"], "REC-010")

    def test_default_assets_include_complete_ecwid_capture_and_contract(self):
        packager = load_packager()
        destinations = {asset.destination for asset in packager.default_assets()}
        self.assertIn("tools/capture_ecwid_api_v2.py", destinations)
        self.assertIn("docs/recovery/ecwid-api-complete-capture-v2.md", destinations)
        self.assertIn("tools/package_complete_source_generation.py", destinations)


if __name__ == "__main__":
    unittest.main()
