import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.test_capture_ecwid_api import ApiFixture


MODULE_PATH = Path(__file__).with_name("capture_ecwid_api_v2.py")


def load_capture():
    if not MODULE_PATH.is_file():
        raise AssertionError("capture_ecwid_api_v2.py is missing")
    if str(MODULE_PATH.parent) not in sys.path:
        sys.path.insert(0, str(MODULE_PATH.parent))
    spec = importlib.util.spec_from_file_location("capture_ecwid_api_v2", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EcwidCompleteCaptureTests(unittest.TestCase):
    def make_pages(self, carts=None):
        empty = {"total": 0, "count": 0, "offset": 0, "limit": 100, "items": []}
        pages = {
            ("/api/v3/42/profile", 0): {"generalInfo": {"storeId": 42}},
            ("/api/v3/42/products", 0): empty,
            ("/api/v3/42/categories", 0): empty,
            ("/api/v3/42/customers", 0): empty,
            ("/api/v3/42/orders", 0): empty,
            ("/api/v3/42/classes", 0): [{"id": 0, "name": "General"}],
            ("/api/v3/42/customer_groups", 0): {
                "total": 1,
                "count": 1,
                "offset": 0,
                "limit": 100,
                "items": [{"id": 0, "name": "General"}],
            },
            ("/api/v3/42/store_extrafields/customers", 0): {
                "items": [{"key": "field-1", "title": "PO number"}]
            },
            ("/api/v3/42/staff", 0): {
                "staffList": [{"id": "staff-1", "name": "Owner"}]
            },
            ("/api/v3/42/discount_coupons", 0): {
                "total": 1,
                "count": 1,
                "offset": 0,
                "limit": 100,
                "items": [{"id": 3, "code": "SAVE"}],
            },
            ("/api/v3/42/promotions", 0): {
                "total": 1,
                "count": 1,
                "offset": 0,
                "limit": 100,
                "items": [{"id": 4, "name": "Sale"}],
            },
        }
        pages.update(
            carts
            or {
                ("/api/v3/42/carts", 0): {
                    "total": 1,
                    "count": 1,
                    "offset": 0,
                    "limit": 100,
                    "items": [
                        {
                            "cartId": "cart-1",
                            "adminUrl": "https://secret.invalid/?token=do-not-store",
                        }
                    ],
                }
            }
        )
        return pages

    def test_complete_capture_includes_core_and_all_documented_adjunct_resources(self):
        capture = load_capture()
        fixture = ApiFixture(self.make_pages())
        self.addCleanup(fixture.close)
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "capture"

            report = capture.capture_store_complete(
                "42",
                "fixture-secret",
                destination,
                base_url=fixture.base_url,
                min_interval_seconds=0,
                captured_at="2026-08-10T04:00:00Z",
            )

            expected = {
                "profile", "products", "categories", "customers", "orders",
                "product_types", "customer_groups", "customer_extra_fields",
                "abandoned_carts", "staff", "discount_coupons", "promotions",
            }
            self.assertEqual(set(report["entities"]), expected)
            self.assertEqual(report["entities"]["product_types"]["records"], 1)
            self.assertEqual(report["entities"]["abandoned_carts"]["records"], 1)
            cart_request = next(r for r in fixture.requests if r["path"].endswith("/carts"))
            self.assertEqual(cart_request["query"]["showHidden"], ["true"])
            self.assertEqual(cart_request["authorization"], "Bearer fixture-secret")
            all_bytes = b"".join(path.read_bytes() for path in destination.rglob("*") if path.is_file())
            self.assertNotIn(b"fixture-secret", all_bytes)
            self.assertNotIn(b"do-not-store", all_bytes)
            self.assertIn(b'"code": "SAVE"', all_bytes)
            manifest = json.loads((destination / "capture-manifest.json").read_text(encoding="utf-8"))
            self.assertIn("read_promotion", manifest["required_scopes"])
            self.assertIn("read_staff", manifest["required_scopes"])

    def test_duplicate_cart_ids_fail_closed(self):
        capture = load_capture()
        carts = {
            ("/api/v3/42/carts", 0): {
                "total": 2, "count": 1, "offset": 0, "limit": 100,
                "items": [{"cartId": "same"}],
            },
            ("/api/v3/42/carts", 1): {
                "total": 2, "count": 1, "offset": 1, "limit": 100,
                "items": [{"cartId": "same"}],
            },
        }
        fixture = ApiFixture(self.make_pages(carts))
        self.addCleanup(fixture.close)
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "capture"

            with self.assertRaisesRegex(ValueError, "duplicate abandoned_carts cartId"):
                capture.capture_store_complete(
                    "42", "fixture-secret", destination,
                    base_url=fixture.base_url, min_interval_seconds=0,
                )

            self.assertFalse(destination.exists())

    def test_cli_has_no_token_argument(self):
        capture = load_capture()
        parsed = capture.build_parser().parse_args(
            ["--store-id", "42", "--destination", "capture"]
        )
        self.assertFalse(hasattr(parsed, "token"))


if __name__ == "__main__":
    unittest.main()
