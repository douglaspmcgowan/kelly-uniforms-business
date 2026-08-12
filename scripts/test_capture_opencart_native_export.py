import hashlib
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("capture_opencart_native_export.py")


def load_capture():
    if not MODULE_PATH.is_file():
        raise AssertionError("capture_opencart_native_export.py is missing")
    spec = importlib.util.spec_from_file_location("capture_opencart_native_export", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OpenCartNativeExportCaptureTests(unittest.TestCase):
    def make_source(self):
        temporary = tempfile.TemporaryDirectory()
        source = Path(temporary.name) / "source"
        source.mkdir()
        (source / "database.sql").write_bytes(b"-- OpenCart dump\nCREATE TABLE x(id int);\n")
        webroot = source / "webroot"
        (webroot / "image" / "catalog").mkdir(parents=True)
        (webroot / "image" / "catalog" / "shirt.jpg").write_bytes(b"jpeg-bytes")
        (webroot / "index.php").write_text("<?php echo 'store';\n", encoding="utf-8")
        storage = source / "storage" / "modification"
        storage.mkdir(parents=True)
        (storage / "compiled.php").write_text("<?php // modified\n", encoding="utf-8")
        config = source / "config"
        config.mkdir()
        (config / "config.php").write_text(
            "<?php define('DB_PASSWORD', 'do-not-copy-into-manifest');\n",
            encoding="utf-8",
        )
        return temporary, source

    def test_capture_copies_exact_bytes_and_writes_value_safe_inventory(self):
        capture = load_capture()
        temporary, source = self.make_source()
        self.addCleanup(temporary.cleanup)
        destination = Path(temporary.name) / "capture"

        report = capture.capture_export(
            source, destination, captured_at="2026-08-10T02:00:00Z"
        )

        manifest_text = (destination / "capture-manifest.json").read_text(encoding="utf-8")
        manifest = json.loads(manifest_text)
        inventory_text = (destination / "inventory" / "files.ndjson").read_text(
            encoding="utf-8"
        )
        inventory = [json.loads(line) for line in inventory_text.splitlines()]
        self.assertEqual(manifest["format"], "mt-uniforms-opencart-native-capture/v1")
        self.assertEqual(manifest["status"], "captured")
        self.assertEqual(manifest["required_roots"], ["database.sql", "webroot"])
        self.assertEqual(report["source_files"], 5)
        self.assertEqual(len(inventory), 5)
        self.assertNotIn("do-not-copy-into-manifest", manifest_text)
        self.assertNotIn("do-not-copy-into-manifest", inventory_text)
        for row in inventory:
            source_file = source / row["source_path"]
            copied_file = destination / row["captured_path"]
            self.assertEqual(copied_file.read_bytes(), source_file.read_bytes())
            self.assertEqual(row["sha256"], hashlib.sha256(copied_file.read_bytes()).hexdigest())
            self.assertEqual(row["bytes"], copied_file.stat().st_size)
            self.assertEqual(row["sensitivity"], "restricted")

    def test_capture_requires_database_and_webroot_and_leaves_no_final_directory(self):
        capture = load_capture()
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            source.mkdir()
            (source / "database.sql").write_bytes(b"-- dump\n")
            destination = Path(temporary) / "capture"

            with self.assertRaisesRegex(ValueError, "webroot"):
                capture.capture_export(source, destination)

            self.assertFalse(destination.exists())

    def test_capture_rejects_existing_destination(self):
        capture = load_capture()
        temporary, source = self.make_source()
        self.addCleanup(temporary.cleanup)
        destination = Path(temporary.name) / "capture"
        destination.mkdir()

        with self.assertRaisesRegex(ValueError, "already exists"):
            capture.capture_export(source, destination)

    def test_capture_rejects_symlinks_when_platform_allows_fixture(self):
        capture = load_capture()
        temporary, source = self.make_source()
        self.addCleanup(temporary.cleanup)
        link = source / "webroot" / "linked-config.php"
        try:
            os.symlink(source / "config" / "config.php", link)
        except OSError:
            self.skipTest("symlink creation is unavailable for this test user")
        destination = Path(temporary.name) / "capture"

        with self.assertRaisesRegex(ValueError, "symbolic link"):
            capture.capture_export(source, destination)

        self.assertFalse(destination.exists())

    def test_capture_rejects_windows_directory_junctions(self):
        if os.name != "nt":
            self.skipTest("Windows junction test")
        capture = load_capture()
        temporary, source = self.make_source()
        self.addCleanup(temporary.cleanup)
        outside = Path(temporary.name) / "outside"
        outside.mkdir()
        (outside / "secret.txt").write_text("outside-tree", encoding="utf-8")
        link = source / "webroot" / "linked-directory"
        created = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(outside)],
            capture_output=True,
            text=True,
            check=False,
        )
        if created.returncode:
            self.skipTest("junction creation is unavailable for this test user")
        destination = Path(temporary.name) / "capture"

        with self.assertRaisesRegex(ValueError, "symbolic link|reparse point"):
            capture.capture_export(source, destination)

        self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
