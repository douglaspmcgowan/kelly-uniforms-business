import hashlib
import importlib.util
import tempfile
import threading
import unittest
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("capture_missing_media.py")
SPEC = importlib.util.spec_from_file_location("capture_missing_media", MODULE_PATH)
media = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(media)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


class MissingMediaCaptureTests(unittest.TestCase):
    def test_retries_only_missing_assets_and_records_exact_results(self):
        with tempfile.TemporaryDirectory() as served, tempfile.TemporaryDirectory() as package:
            served_root = Path(served)
            (served_root / "available.jpg").write_bytes(b"exact-image")
            handler = lambda *args, **kwargs: QuietHandler(
                *args, directory=str(served_root), **kwargs
            )
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            self.addCleanup(server.server_close)
            self.addCleanup(server.shutdown)
            base = f"http://127.0.0.1:{server.server_port}"
            inventory = {
                "assets": [
                    {"media_id": 1, "url": f"{base}/available.jpg", "download_status": "referenced-only"},
                    {"media_id": 2, "url": f"{base}/missing.jpg", "download_status": "direct-network-blocked"},
                    {"media_id": 3, "url": f"{base}/old.jpg", "download_status": "downloaded", "sha256": "old"},
                ]
            }

            report = media.retry_media(inventory, Path(package), workers=2, timeout=5)

            self.assertEqual(report["attempted"], 2)
            self.assertEqual(report["captured"], 1)
            self.assertEqual(report["failed"], 1)
            captured = inventory["assets"][0]
            self.assertEqual(captured["download_status"], "downloaded-direct-rec006")
            binary = Path(package) / captured["downloaded_path"]
            self.assertEqual(binary.read_bytes(), b"exact-image")
            self.assertEqual(captured["sha256"], hashlib.sha256(b"exact-image").hexdigest())
            self.assertEqual(inventory["assets"][2]["sha256"], "old")
            self.assertEqual(inventory["assets"][1]["download_status"], "failed-direct-rec006")
            self.assertIn("HTTP 404", inventory["assets"][1]["capture_failure"])


if __name__ == "__main__":
    unittest.main()
