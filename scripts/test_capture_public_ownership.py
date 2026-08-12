import hashlib
import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("capture_public_ownership.py")
SPEC = importlib.util.spec_from_file_location("capture_public_ownership", MODULE_PATH)
capture_public_ownership = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(capture_public_ownership)


class PublicOwnershipCaptureTests(unittest.TestCase):
    def test_sanitize_headers_drops_session_material(self):
        sanitized = capture_public_ownership.sanitize_headers(
            {
                "Server": "nginx",
                "Content-Type": "text/html",
                "Set-Cookie": "OCSESSID=secret-value; HttpOnly",
                "Authorization": "Bearer secret-value",
                "X-Powered-By": "PHP",
            }
        )

        self.assertEqual(
            sanitized,
            {
                "content-type": "text/html",
                "server": "nginx",
                "x-powered-by": "PHP",
            },
        )

    def test_dns_observations_preserve_fact_and_source(self):
        response = {
            "Status": 0,
            "Question": [{"name": "mtuniforms.com.", "type": 1}],
            "Answer": [
                {"name": "mtuniforms.com.", "type": 1, "TTL": 300, "data": "203.0.113.9"}
            ],
        }

        observations = capture_public_ownership.normalize_dns_observations(
            "mtuniforms.com", "A", response, "dns-a"
        )

        self.assertEqual(
            observations,
            [
                {
                    "source_key": "dns-a",
                    "subject": "mtuniforms.com",
                    "record_type": "A",
                    "name": "mtuniforms.com.",
                    "value": "203.0.113.9",
                    "ttl": 300,
                    "confidence": "resolver-observed",
                    "inference": 0,
                }
            ],
        )

    def test_write_bundle_hashes_every_raw_artifact(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        artifacts = {
            "rdap/mtuniforms.com.json": {"ldhName": "MTUNIFORMS.COM"},
            "dns/records.json": {"queries": []},
        }

        manifest_path = capture_public_ownership.write_capture_bundle(
            root,
            "mtuniforms.com",
            "2026-08-09T00:00:00Z",
            artifacts,
            [],
        )

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["domain"], "mtuniforms.com")
        self.assertEqual(len(manifest["artifacts"]), 2)
        for item in manifest["artifacts"]:
            artifact = root / item["path"]
            self.assertEqual(item["bytes"], artifact.stat().st_size)
            self.assertEqual(item["sha256"], hashlib.sha256(artifact.read_bytes()).hexdigest())

    def test_append_business_facts_adds_provenanced_observations(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        capture_public_ownership.write_capture_bundle(
            root, "mtuniforms.com", "2026-08-09T00:00:00Z", {}, []
        )
        facts = [
            {
                "fact_type": "legal-name",
                "value": "MT UNIFORMS LLC",
                "source_uri": "https://data.pa.gov/example",
                "verification_status": "primary-record-verified",
                "confidence": "high",
            }
        ]

        capture_public_ownership.append_business_facts(root, facts)

        manifest = json.loads((root / "capture-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["artifacts"][0]["path"], "business/business-footprint.json")
        self.assertEqual(manifest["observations"][0]["record_type"], "BUSINESS_FACT")
        self.assertEqual(manifest["observations"][0]["source_key"], "business/business-footprint.json")


if __name__ == "__main__":
    unittest.main()
