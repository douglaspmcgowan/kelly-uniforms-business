import hashlib
import importlib.util
import json
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


MODULE_PATH = Path(__file__).with_name("capture_ecwid_api.py")


def load_capture():
    if not MODULE_PATH.is_file():
        raise AssertionError("capture_ecwid_api.py is missing")
    if str(MODULE_PATH.parent) not in sys.path:
        sys.path.insert(0, str(MODULE_PATH.parent))
    spec = importlib.util.spec_from_file_location("capture_ecwid_api", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ApiFixture:
    def __init__(self, pages):
        self.pages = pages
        self.requests = []

        fixture = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urlparse(self.path)
                query = parse_qs(parsed.query)
                fixture.requests.append(
                    {"path": parsed.path, "query": query, "authorization": self.headers.get("Authorization")}
                )
                key = (parsed.path, int(query.get("offset", [0])[0]))
                payload = fixture.pages.get(key)
                if payload is None:
                    self.send_response(404)
                    self.end_headers()
                    return
                body = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format, *args):
                return

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    @property
    def base_url(self):
        return f"http://127.0.0.1:{self.server.server_port}/api/v3"

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


class EcwidCaptureTests(unittest.TestCase):
    def make_fixture(self, product_pages=None):
        pages = {
            ("/api/v3/42/profile", 0): {"generalInfo": {"storeId": 42}, "account": {"accountName": "Fixture"}},
            ("/api/v3/42/categories", 0): {"total": 0, "count": 0, "offset": 0, "limit": 100, "items": []},
            ("/api/v3/42/customers", 0): {"total": 0, "count": 0, "offset": 0, "limit": 100, "items": []},
            ("/api/v3/42/orders", 0): {"total": 0, "count": 0, "offset": 0, "limit": 100, "items": []},
        }
        pages.update(
            product_pages
            or {
                ("/api/v3/42/products", 0): {
                    "total": 3,
                    "count": 2,
                    "offset": 0,
                    "limit": 100,
                    "items": [
                        {"id": 1, "name": "A", "adminUrl": "https://secret.invalid/?token=do-not-store"},
                        {"id": 2, "name": "B"},
                    ],
                },
                ("/api/v3/42/products", 2): {
                    "total": 3,
                    "count": 1,
                    "offset": 2,
                    "limit": 100,
                    "items": [{"id": 3, "name": "C"}],
                },
            }
        )
        fixture = ApiFixture(pages)
        self.addCleanup(fixture.close)
        return fixture

    def test_capture_preserves_complete_pages_without_secret_urls(self):
        capture = load_capture()
        fixture = self.make_fixture()
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "capture"
            report = capture.capture_store(
                store_id="42",
                token="fixture-secret",
                destination=destination,
                base_url=fixture.base_url,
                endpoint_specs=capture.CORE_ENDPOINTS,
                min_interval_seconds=0,
                captured_at="2026-08-10T12:00:00Z",
            )

            self.assertEqual(report["entities"]["products"]["records"], 3)
            self.assertEqual(report["entities"]["products"]["pages"], 2)
            second_request = next(
                request for request in fixture.requests
                if request["path"].endswith("/products") and request["query"].get("offset") == ["2"]
            )
            self.assertEqual(second_request["authorization"], "Bearer fixture-secret")
            category_request = next(request for request in fixture.requests if request["path"].endswith("/categories"))
            self.assertEqual(category_request["query"]["hidden_categories"], ["true"])
            self.assertEqual(category_request["query"]["productIds"], ["true"])

            first_page = (destination / "api/products/offset-000000.json").read_text(encoding="utf-8")
            all_bytes = b"".join(path.read_bytes() for path in destination.rglob("*") if path.is_file())
            self.assertNotIn("adminUrl", first_page)
            self.assertNotIn(b"fixture-secret", all_bytes)
            self.assertNotIn(b"do-not-store", all_bytes)
            manifest = json.loads((destination / "capture-manifest.json").read_text(encoding="utf-8"))
            for artifact in manifest["artifacts"]:
                path = destination / artifact["relative_path"]
                self.assertEqual(artifact["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
                self.assertEqual(artifact["bytes"], path.stat().st_size)

    def test_capture_fails_closed_on_duplicate_ids_without_final_directory(self):
        capture = load_capture()
        fixture = self.make_fixture(
            {
                ("/api/v3/42/products", 0): {
                    "total": 2,
                    "count": 1,
                    "offset": 0,
                    "limit": 100,
                    "items": [{"id": 7}],
                },
                ("/api/v3/42/products", 1): {
                    "total": 2,
                    "count": 1,
                    "offset": 1,
                    "limit": 100,
                    "items": [{"id": 7}],
                },
            }
        )
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "capture"
            with self.assertRaisesRegex(ValueError, "duplicate products id"):
                capture.capture_store(
                    store_id="42",
                    token="fixture-secret",
                    destination=destination,
                    base_url=fixture.base_url,
                    endpoint_specs=capture.CORE_ENDPOINTS,
                    min_interval_seconds=0,
                )
            self.assertFalse(destination.exists())

    def test_cli_requires_token_from_environment_not_arguments(self):
        capture = load_capture()
        parser = capture.build_parser()
        parsed = parser.parse_args(["--store-id", "42", "--destination", "capture"])
        self.assertFalse(hasattr(parsed, "token"))


if __name__ == "__main__":
    unittest.main()
