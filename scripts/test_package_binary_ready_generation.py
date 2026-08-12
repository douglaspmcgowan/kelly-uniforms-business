import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("package_binary_ready_generation.py")


def load_packager():
    if not MODULE_PATH.is_file():
        raise AssertionError("package_binary_ready_generation.py is missing")
    if str(MODULE_PATH.parent) not in sys.path:
        sys.path.insert(0, str(MODULE_PATH.parent))
    spec = importlib.util.spec_from_file_location("package_binary_ready_generation", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BinaryReadyGenerationTests(unittest.TestCase):
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
                    "generation": "REC-011",
                    "parent_generation": "REC-010",
                    "source_capture": {
                        "readiness": "opencart-and-complete-ecwid-tools-packaged-awaiting-authenticated-exports",
                        "ecwid_tool": "tools/capture_ecwid_api_v2.py",
                    },
                    "commerce_import": {"population_status": "empty-awaiting-authenticated-exports"},
                }
            ),
            encoding="utf-8",
        )
        tooling = Path(temporary.name) / "tooling"
        tooling.mkdir()
        (tooling / "binaries.py").write_text("print('binary')\n", encoding="utf-8")
        return temporary, root, tooling

    def test_stage_adds_binary_capture_and_promotes_generation(self):
        packager = load_packager()
        temporary, root, tooling = self.make_fixture()
        self.addCleanup(temporary.cleanup)

        report = packager.stage_binary_readiness(
            root,
            [packager.PackagedAsset(tooling / "binaries.py", "tools/binaries.py", "capture-tool")],
            captured_at="2026-08-10T07:00:00Z",
        )

        manifest = json.loads((root / "package-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["generation"], "REC-012")
        self.assertEqual(manifest["parent_generation"], "REC-011")
        self.assertEqual(
            manifest["source_capture"]["ecwid_binary_tool"],
            "tools/capture_ecwid_binaries.py",
        )
        self.assertEqual(
            manifest["source_capture"]["readiness"],
            "opencart-and-ecwid-json-binary-tools-packaged-awaiting-authenticated-exports",
        )
        self.assertEqual(
            manifest["commerce_import"]["tool"],
            "tools/package_binary_ready_generation.py",
        )
        self.assertEqual(report["packaged_assets"], 1)
        connection = sqlite3.connect(root / "mt_uniforms_recovery.sqlite")
        try:
            metadata = dict(connection.execute("SELECT key,value FROM recovery_metadata"))
        finally:
            connection.close()
        self.assertEqual(metadata["generation"], "REC-012")
        self.assertEqual(metadata["parent_generation"], "REC-011")

    def test_default_assets_include_binary_capture_tool_and_contract(self):
        packager = load_packager()
        destinations = {asset.destination for asset in packager.default_assets()}
        self.assertIn("tools/capture_ecwid_binaries.py", destinations)
        self.assertIn("docs/recovery/ecwid-binary-capture-v1.md", destinations)
        self.assertIn("tools/package_binary_ready_generation.py", destinations)


if __name__ == "__main__":
    unittest.main()
