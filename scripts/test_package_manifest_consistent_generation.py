import copy
import importlib.util
import sys
import tempfile
import unittest
import subprocess
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).with_name("package_manifest_consistent_generation.py")


def load_packager():
    if str(MODULE_PATH.parent) not in sys.path:
        sys.path.insert(0, str(MODULE_PATH.parent))
    spec = importlib.util.spec_from_file_location(
        "package_manifest_consistent_generation", MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parent_manifest():
    return {
        "generation": "REC-015",
        "parent_generation": "REC-014",
        "missing_required": [
            "full OpenCart database",
            "domain/DNS/hosting/email/payment/shipping ownership inventory",
            "encrypted offline and offsite copies",
        ],
        "public_media": {
            "status": "reference-inventory-complete-binary-mirror-partial",
            "unique_image_urls": 1542,
            "total_occurrences": 8026,
            "downloaded_exact_binaries": 1111,
            "exact_binary_coverage_percent": 72.05,
            "direct_network_blocked_urls": 26,
            "referenced_only_urls": 404,
            "public_render_sweep_status": "saturated-for-currently-rendered-pages",
            "json": "public-site/media-inventory.json",
            "csv": "public-site/media-inventory.csv",
            "alternate_json": "public-site/browser-observed-media.json",
            "binaries": "public-site/media/",
        },
        "public_media_completion": {
            "url_backed_exact": 1541,
            "embedded_exact": 1,
            "total_exact": 1542,
        },
        "service_account_inventory": {
            "status": "value-free-inventory-present-primary-control-unverified",
            "services": 10,
            "contains_secrets": False,
        },
        "source_capture": {"captured_private_exports": False},
        "commerce_import": {"tool": "tools/package_clean_recovery_generation.py"},
    }


class ManifestConsistentGenerationTests(unittest.TestCase):
    def test_reconciles_current_claims_without_mutating_parent(self):
        packager = load_packager()
        source = parent_manifest()
        before = copy.deepcopy(source)

        result = packager.reconcile_manifest(
            source,
            "2026-08-12T12:00:00Z",
            dict(packager.MEDIA_STATUS_COUNTS),
        )

        self.assertEqual(source, before)
        self.assertEqual(result["generation"], "REC-016")
        self.assertEqual(result["parent_generation"], "REC-015")
        self.assertEqual(result["public_media"]["status"], "exact-binary-mirror-complete")
        self.assertEqual(result["public_media"]["exact_binaries"], 1542)
        self.assertEqual(result["public_media"]["exact_binary_coverage_percent"], 100.0)
        self.assertEqual(result["public_media"]["unresolved_referenced_urls"], 0)
        self.assertNotIn("downloaded_exact_binaries", result["public_media"])
        self.assertNotIn("referenced_only_urls", result["public_media"])
        self.assertNotIn(
            "domain/DNS/hosting/email/payment/shipping ownership inventory",
            result["missing_required"],
        )
        self.assertIn(
            "primary account-control evidence for domain/DNS/hosting/email/payment/shipping services",
            result["missing_required"],
        )
        self.assertFalse(result["source_capture"]["captured_private_exports"])
        self.assertEqual(
            result["commerce_import"]["tool"],
            "tools/package_manifest_consistent_generation.py",
        )

    def test_rejects_unproven_media_completion(self):
        packager = load_packager()
        source = parent_manifest()
        source["public_media_completion"]["total_exact"] = 1541

        with self.assertRaisesRegex(ValueError, "completion proof"):
            packager.reconcile_manifest(
                source,
                "2026-08-12T12:00:00Z",
                dict(packager.MEDIA_STATUS_COUNTS),
            )

    def test_rejects_non_value_free_service_inventory(self):
        packager = load_packager()
        source = parent_manifest()
        source["service_account_inventory"]["contains_secrets"] = True

        with self.assertRaisesRegex(ValueError, "value-free"):
            packager.reconcile_manifest(
                source,
                "2026-08-12T12:00:00Z",
                dict(packager.MEDIA_STATUS_COUNTS),
            )

    def test_status_names_only_remaining_boundaries(self):
        packager = load_packager()
        status = packager._status("2026-08-12T12:00:00Z", proven=True)

        self.assertIn("1,542 / 1,542 exact referenced binaries", status)
        self.assertIn("primary control evidence remains unverified", status)
        self.assertIn("Package-local v3 drill: PROVEN", status)
        self.assertIn("Fresh private commerce/import rows: 0", status)

    def test_create_refuses_existing_destination_before_parent_verification(self):
        packager = load_packager()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            destination = root / "destination"
            source.mkdir()
            destination.mkdir()

            with self.assertRaisesRegex(ValueError, "immutable"):
                packager.create_generation(source, destination)

    def test_verify_rejects_sqlite_sidecars_without_deleting_them(self):
        packager = load_packager()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sidecar = root / "mt_uniforms_recovery.sqlite-wal"
            sidecar.write_bytes(b"uncheckpointed-state")

            with self.assertRaisesRegex(ValueError, "SQLite sidecar"):
                packager.verify_generation(root)

            self.assertEqual(sidecar.read_bytes(), b"uncheckpointed-state")

    def test_failed_release_verification_removes_all_final_targets(self):
        packager = load_packager()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            destination = root / "REC-016"
            archive = root / "archives" / "REC-016.tar.gz"
            isolated = root / "restores" / "REC-016"
            source.mkdir()

            def fake_create_generation(_source, build_root):
                build_root.mkdir()
                (build_root / "package-manifest.json").write_text(
                    '{"generation":"REC-016"}', encoding="utf-8"
                )
                return {"valid": True}

            failure = subprocess.CalledProcessError(1, ["verify"])
            with mock.patch.object(
                packager, "create_generation", side_effect=fake_create_generation
            ), mock.patch.object(packager.subprocess, "run", side_effect=failure):
                with self.assertRaises(subprocess.CalledProcessError):
                    packager.create_release(source, destination, archive, isolated)

            self.assertFalse(destination.exists())
            self.assertFalse(archive.exists())
            self.assertFalse(isolated.exists())


if __name__ == "__main__":
    unittest.main()
