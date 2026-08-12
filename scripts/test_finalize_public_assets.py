import base64
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("finalize_public_assets.py")
SPEC = importlib.util.spec_from_file_location("finalize_public_assets", MODULE_PATH)
finalizer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(finalizer)


class FinalPublicAssetTests(unittest.TestCase):
    def test_extracts_base64_data_uri_with_exact_provenance(self):
        payload = b"embedded-png"
        asset = {
            "media_id": 1,
            "url": "data:image/png;base64," + base64.b64encode(payload).decode("ascii"),
            "download_status": "inline-or-unsupported",
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = finalizer.extract_inline_asset(asset, root)
            binary = root / result["downloaded_path"]
            self.assertEqual(binary.read_bytes(), payload)
            self.assertEqual(result["content_type"], "image/png")
            self.assertEqual(result["bytes"], len(payload))
            self.assertEqual(result["sha256"], hashlib.sha256(payload).hexdigest())
            self.assertEqual(result["download_status"], "embedded-extracted-rec007")

    def test_rejects_non_data_uri(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "not a data URI"):
                finalizer.extract_inline_asset(
                    {"media_id": 1, "url": "https://example.test/image.png"}, Path(temporary)
                )


if __name__ == "__main__":
    unittest.main()
