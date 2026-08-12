import importlib.util
import gc
import json
import sys
import tempfile
import threading
import unittest
import warnings
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


MODULE_PATH = Path(__file__).with_name("capture_ecwid_binaries.py")


def load_capture():
    if not MODULE_PATH.is_file():
        raise AssertionError("capture_ecwid_binaries.py is missing")
    if str(MODULE_PATH.parent) not in sys.path:
        sys.path.insert(0, str(MODULE_PATH.parent))
    spec = importlib.util.spec_from_file_location("capture_ecwid_binaries", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BinaryFixture:
    def __init__(self, fail_product_file=False):
        self.requests = []
        fixture = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                path = urlparse(self.path).path
                fixture.requests.append(
                    {"path": path, "authorization": self.headers.get("Authorization")}
                )
                if path == "/media/product.jpg":
                    status, mime, body = 200, "image/jpeg", b"product-image"
                elif path == "/media/category.png":
                    status, mime, body = 200, "image/png", b"category-image"
                elif path == "/api/v3/42/products/10/files/5" and not fail_product_file:
                    status, mime, body = 200, "application/pdf", b"pdf-bytes"
                else:
                    status, mime, body = 404, "text/plain", b"missing"
                self.send_response(status)
                self.send_header("Content-Type", mime)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format, *args):
                return

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    @property
    def origin(self):
        return f"http://127.0.0.1:{self.server.server_port}"

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


class EcwidBinaryCaptureTests(unittest.TestCase):
    def make_capture(self, root: Path, fixture: BinaryFixture):
        root.mkdir()
        (root / "api/products").mkdir(parents=True)
        (root / "api/categories").mkdir(parents=True)
        (root / "capture-manifest.json").write_text(
            json.dumps(
                {
                    "schema_version": "mt-uniforms-ecwid-api-capture/v2",
                    "source_system": "ecwid",
                    "store_ref": "42",
                }
            ),
            encoding="utf-8",
        )
        (root / "api/products/offset-000000.json").write_text(
            json.dumps(
                {
                    "items": [
                        {
                            "id": 10,
                            "imageUrl": fixture.origin + "/media/product.jpg",
                            "originalImage": {"url": fixture.origin + "/media/product.jpg"},
                            "files": [
                                {
                                    "id": 5,
                                    "name": "manual.pdf",
                                    "size": 9,
                                    "adminUrl": "https://secret.invalid/?token=do-not-store",
                                }
                            ],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        (root / "api/categories/offset-000000.json").write_text(
            json.dumps(
                {
                    "items": [
                        {"id": 20, "imageUrl": fixture.origin + "/media/category.png"}
                    ]
                }
            ),
            encoding="utf-8",
        )

    def test_capture_downloads_deduplicated_media_and_reconstructed_product_files(self):
        capture = load_capture()
        fixture = BinaryFixture()
        self.addCleanup(fixture.close)
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            destination = Path(temporary) / "binaries"
            self.make_capture(source, fixture)

            report = capture.capture_binaries(
                source,
                "fixture-secret",
                destination,
                api_base_url=fixture.origin + "/api/v3",
                captured_at="2026-08-10T06:00:00Z",
            )

            self.assertEqual(report["unique_binaries"], 3)
            product_media_requests = [r for r in fixture.requests if r["path"] == "/media/product.jpg"]
            self.assertEqual(len(product_media_requests), 1)
            self.assertIsNone(product_media_requests[0]["authorization"])
            file_request = next(r for r in fixture.requests if "/products/10/files/5" in r["path"])
            self.assertEqual(file_request["authorization"], "Bearer fixture-secret")
            all_bytes = b"".join(path.read_bytes() for path in destination.rglob("*") if path.is_file())
            self.assertNotIn(b"fixture-secret", all_bytes)
            self.assertNotIn(b"do-not-store", all_bytes)
            inventory = [
                json.loads(line)
                for line in (destination / "inventory/binaries.ndjson").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(len(inventory), 3)
            product_image = next(row for row in inventory if row["kind"] == "catalog-media" and len(row["locators"]) == 2)
            self.assertEqual(len(product_image["locators"]), 2)
            for row in inventory:
                self.assertTrue((destination / row["captured_path"]).is_file())

    def test_failed_download_removes_final_destination(self):
        capture = load_capture()
        fixture = BinaryFixture(fail_product_file=True)
        self.addCleanup(fixture.close)
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            destination = Path(temporary) / "binaries"
            self.make_capture(source, fixture)

            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always", ResourceWarning)
                with self.assertRaisesRegex(ValueError, "HTTP 404"):
                    capture.capture_binaries(
                        source,
                        "fixture-secret",
                        destination,
                        api_base_url=fixture.origin + "/api/v3",
                    )
                gc.collect()

            self.assertFalse(
                [warning for warning in caught if issubclass(warning.category, ResourceWarning)]
            )

            self.assertFalse(destination.exists())

    def test_cli_has_no_token_argument(self):
        capture = load_capture()
        parsed = capture.build_parser().parse_args(
            ["--capture", "source", "--destination", "binaries"]
        )
        self.assertFalse(hasattr(parsed, "token"))

    def test_default_capture_timestamp_is_utc(self):
        capture = load_capture()
        fixture = BinaryFixture()
        self.addCleanup(fixture.close)
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            destination = Path(temporary) / "binaries"
            self.make_capture(source, fixture)

            report = capture.capture_binaries(
                source,
                "fixture-secret",
                destination,
                api_base_url=fixture.origin + "/api/v3",
            )

            self.assertIsInstance(report["captured_at"], str)
            self.assertTrue(report["captured_at"].endswith("Z"))


if __name__ == "__main__":
    unittest.main()
