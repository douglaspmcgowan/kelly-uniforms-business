import hashlib
import importlib.util
import json
import sqlite3
import tempfile
import threading
import unittest
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("capture_public_runtime.py")
SPEC = importlib.util.spec_from_file_location("capture_public_runtime", MODULE_PATH)
capture_public_runtime = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(capture_public_runtime)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


class PublicRuntimeCaptureTests(unittest.TestCase):
    def make_source_package(self, base_url):
        temporary = tempfile.TemporaryDirectory()
        source = Path(temporary.name) / "rec003"
        runtime = source / "public-site" / "runtime-assets"
        runtime.mkdir(parents=True)
        payload = source / "raw" / "source.txt"
        payload.parent.mkdir()
        payload.write_text("preserved source\n", encoding="utf-8")

        inventory = {
            "generated_at": "2026-08-09T00:00:00Z",
            "downloaded_assets": [],
            "script_references": [
                {"script_id": 1, "url": f"{base_url}/app.js", "pages": ["https://example.test/"]}
            ],
            "failed_assets": [
                {
                    "failure_id": 1,
                    "url": f"{base_url}/font.woff2",
                    "kind": "font",
                    "pages": ["https://example.test/"],
                    "reason": "prior browser capture failed",
                },
                {
                    "failure_id": 2,
                    "url": f"{base_url}/missing.woff2",
                    "kind": "font",
                    "pages": ["https://example.test/"],
                    "reason": "prior browser capture failed",
                },
            ],
        }
        (runtime / "inventory.json").write_text(json.dumps(inventory), encoding="utf-8")

        database = source / "mt_uniforms_recovery.sqlite"
        connection = sqlite3.connect(database)
        connection.execute(
            """CREATE TABLE source_manifest(
                source_id INTEGER PRIMARY KEY, system TEXT NOT NULL,
                artifact_type TEXT NOT NULL, source_path TEXT, captured_at TEXT,
                sha256 TEXT, bytes INTEGER, status TEXT NOT NULL, notes TEXT
            )"""
        )
        inventory_file = runtime / "inventory.json"
        connection.execute(
            """INSERT INTO source_manifest(
                system, artifact_type, source_path, captured_at, sha256, bytes, status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "fixture", "runtime inventory", "public-site/runtime-assets/inventory.json",
                "2026-08-09T00:00:00Z", hashlib.sha256(inventory_file.read_bytes()).hexdigest(),
                inventory_file.stat().st_size, "captured", "tracked mutable inventory",
            ),
        )
        connection.execute(
            """INSERT INTO source_manifest(
                system, artifact_type, source_path, captured_at, sha256, bytes, status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "fixture", "source", "raw/source.txt", "2026-08-09T00:00:00Z",
                hashlib.sha256(payload.read_bytes()).hexdigest(), payload.stat().st_size,
                "captured", "test fixture",
            ),
        )
        connection.commit()
        connection.close()
        (source / "package-manifest.json").write_text(
            json.dumps(
                {
                    "package": "mt-uniforms-recovery",
                    "generation": "REC-003",
                    "generated_at": "2026-08-09T00:00:00Z",
                    "root": ".",
                    "missing_required": [
                        "complete Clover exports and reconciliation",
                        "complete Clover exports and mappings",
                        "isolated restore evidence",
                        "authenticated OpenCart export",
                    ],
                }
            ),
            encoding="utf-8",
        )
        capture_public_runtime.recovery_package.upgrade_package(source)
        return temporary, source

    def test_capture_is_immutable_provenanced_and_verifiable(self):
        with tempfile.TemporaryDirectory() as served:
            served_root = Path(served)
            (served_root / "app.js").write_text("window.fixture = true;\n", encoding="utf-8")
            (served_root / "font.woff2").write_bytes(b"fixture-font")
            handler = lambda *args, **kwargs: QuietHandler(
                *args, directory=str(served_root), **kwargs
            )
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            self.addCleanup(server.server_close)
            self.addCleanup(server.shutdown)

            package_tmp, source = self.make_source_package(
                f"http://127.0.0.1:{server.server_port}"
            )
            self.addCleanup(package_tmp.cleanup)
            source_inventory_before = (
                source / "public-site" / "runtime-assets" / "inventory.json"
            ).read_bytes()
            destination = source.parent / "rec004"

            report = capture_public_runtime.capture_generation(source, destination, retries=0)

            self.assertEqual(source_inventory_before, (
                source / "public-site" / "runtime-assets" / "inventory.json"
            ).read_bytes())
            self.assertEqual(report["attempted"], 3)
            self.assertEqual(report["captured"], 2)
            self.assertEqual(report["failed"], 1)

            inventory = json.loads((
                destination / "public-site" / "runtime-assets" / "inventory.json"
            ).read_text(encoding="utf-8"))
            captured = inventory["direct_capture_assets"]
            self.assertEqual({item["kind"] for item in captured}, {"script", "font"})
            for item in captured:
                packaged = destination / item["packaged_path"]
                self.assertTrue(packaged.is_file())
                self.assertEqual(item["sha256"], hashlib.sha256(packaged.read_bytes()).hexdigest())
                self.assertGreater(item["bytes"], 0)
                self.assertIn("captured_at", item)
                self.assertIn("content_type", item)
            self.assertEqual(len(inventory["direct_capture_failures"]), 1)
            self.assertIn("HTTP 404", inventory["direct_capture_failures"][0]["reason"])

            manifest = json.loads((destination / "package-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["generation"], "REC-004")
            self.assertNotIn("complete Clover exports and reconciliation", manifest["missing_required"])
            self.assertNotIn("complete Clover exports and mappings", manifest["missing_required"])
            self.assertNotIn("isolated restore evidence", manifest["missing_required"])
            self.assertIn("authenticated OpenCart export", manifest["missing_required"])
            self.assertEqual(manifest["clover_authenticated_scope"], "excluded-per-client-decision")

            verified = capture_public_runtime.verify_generation(destination)
            self.assertTrue(verified["valid"])
            self.assertEqual(verified["captured"], 2)
            connection = sqlite3.connect(destination / "mt_uniforms_recovery.sqlite")
            try:
                lineage = connection.execute(
                    "SELECT sha256, bytes FROM source_manifest WHERE source_path=?",
                    ("public-site/runtime-assets/inventory.json",),
                ).fetchone()
            finally:
                connection.close()
            inventory_file = destination / "public-site" / "runtime-assets" / "inventory.json"
            self.assertEqual(lineage[0], hashlib.sha256(inventory_file.read_bytes()).hexdigest())
            self.assertEqual(lineage[1], inventory_file.stat().st_size)

    def test_verifier_detects_runtime_binary_tampering(self):
        with tempfile.TemporaryDirectory() as served:
            served_root = Path(served)
            (served_root / "app.js").write_text("window.fixture = true;\n", encoding="utf-8")
            (served_root / "font.woff2").write_bytes(b"fixture-font")
            handler = lambda *args, **kwargs: QuietHandler(
                *args, directory=str(served_root), **kwargs
            )
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            self.addCleanup(server.server_close)
            self.addCleanup(server.shutdown)
            package_tmp, source = self.make_source_package(
                f"http://127.0.0.1:{server.server_port}"
            )
            self.addCleanup(package_tmp.cleanup)
            destination = source.parent / "rec004"
            capture_public_runtime.capture_generation(source, destination, retries=0)
            inventory = json.loads((
                destination / "public-site" / "runtime-assets" / "inventory.json"
            ).read_text(encoding="utf-8"))
            binary = destination / inventory["direct_capture_assets"][0]["packaged_path"]
            binary.write_bytes(b"tampered")

            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                capture_public_runtime.verify_generation(destination)


if __name__ == "__main__":
    unittest.main()
