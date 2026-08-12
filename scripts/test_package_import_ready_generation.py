import hashlib
import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("package_import_ready_generation.py")


def load_packager():
    if not MODULE_PATH.is_file():
        raise AssertionError("package_import_ready_generation.py is missing")
    if str(MODULE_PATH.parent) not in sys.path:
        sys.path.insert(0, str(MODULE_PATH.parent))
    spec = importlib.util.spec_from_file_location("package_import_ready_generation", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ImportReadyGenerationTests(unittest.TestCase):
    def make_fixture(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name) / "generation"
        root.mkdir()
        database = root / "mt_uniforms_recovery.sqlite"
        connection = sqlite3.connect(database)
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
        connection.execute(
            "CREATE TABLE recovery_metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        connection.commit()
        connection.close()
        (root / "package-manifest.json").write_text(
            json.dumps({"generation": "REC-007", "parent_generation": "REC-006"}),
            encoding="utf-8",
        )
        tooling = Path(temporary.name) / "tooling"
        tooling.mkdir()
        (tooling / "importer.py").write_text("print('import')\n", encoding="utf-8")
        (tooling / "contract.json").write_text('{"version": 1}\n', encoding="utf-8")
        return temporary, root, tooling

    def write_import_bundle(self, root, invalid_parent=False):
        artifact_root = root / "external"
        artifact_root.mkdir()
        sql = artifact_root / "database.sql"
        sql.write_bytes(b"-- synthetic export\n")
        snapshot = artifact_root / "categories.ndjson"
        snapshot.write_text(
            json.dumps(
                {
                    "source_record_id": "category:2",
                    "source_locator": "table:category/pk:2",
                    "entity": "categories",
                    "record": {"category_id": 2, "name": "Duty Gear"},
                    "normalized_rows": [
                        {
                            "table": "catalog_categories",
                            "record_id": "opencart:category:2",
                            "values": {
                                "parent_category_ref": "opencart:category:999" if invalid_parent else None,
                                "name": "Duty Gear",
                                "lifecycle_status": "active",
                            },
                        }
                    ],
                },
                separators=(",", ":"),
            )
            + "\n",
            encoding="utf-8",
        )
        artifacts = []
        for path, artifact_type, count in (
            (sql, "database-sql", 0),
            (snapshot, "table-snapshot", 1),
        ):
            payload = path.read_bytes()
            artifacts.append(
                {
                    "relative_path": path.name,
                    "artifact_type": artifact_type,
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "bytes": len(payload),
                    "record_count": count,
                    "completeness": "complete-file",
                    "entity": "categories",
                }
            )
        manifest = {
            "schema_version": "mt-uniforms-commerce-import/v1",
            "run_id": "fixture-import-001",
            "source_system": "opencart",
            "store_ref": "fixture-store",
            "captured_at": "2026-08-10T00:00:00Z",
            "source_version": "fixture",
            "capture_method": "native-database-export",
            "status": "reconciled",
            "scope": {"kind": "complete", "entities": ["categories"]},
            "artifacts": artifacts,
            "reconciliation": {
                "source_counts": {"categories": 1},
                "normalized_counts": {"categories": 1},
                "skipped_counts": {"categories": 0},
                "skips": [],
                "foreign_key_errors": 0,
                "unresolved_conflicts": 0,
                "money_checks": [],
            },
        }
        manifest_path = artifact_root / "export-manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return manifest_path

    def test_stage_adds_import_schema_tool_lineage_and_zero_business_rows(self):
        packager = load_packager()
        temporary, root, tooling = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        assets = [
            packager.PackagedAsset(tooling / "importer.py", "tools/importer.py", "recovery-tool"),
            packager.PackagedAsset(tooling / "contract.json", "contracts/contract.json", "import-contract"),
        ]

        report = packager.stage_import_readiness(root, assets, captured_at="2026-08-10T12:00:00Z")

        manifest = json.loads((root / "package-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["generation"], "REC-008")
        self.assertEqual(manifest["parent_generation"], "REC-007")
        self.assertEqual(
            manifest["commerce_import"]["population_status"],
            "empty-awaiting-authenticated-exports",
        )
        self.assertEqual(report["packaged_assets"], 2)
        connection = sqlite3.connect(root / "mt_uniforms_recovery.sqlite")
        try:
            metadata = dict(connection.execute("SELECT key,value FROM recovery_metadata"))
            self.assertEqual(metadata["generation"], "REC-008")
            self.assertEqual(metadata["parent_generation"], "REC-007")
            self.assertEqual(metadata["commerce_import_schema_version"], "1.1.0")
            self.assertEqual(
                metadata["commerce_import_readiness"],
                "ready-awaiting-authenticated-exports",
            )
            for table in packager.EMPTY_IMPORT_TABLES:
                self.assertEqual(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0], 0)
            rows = connection.execute(
                "SELECT source_path,sha256,bytes FROM source_manifest ORDER BY source_path"
            ).fetchall()
        finally:
            connection.close()
        self.assertEqual([row[0] for row in rows], ["contracts/contract.json", "tools/importer.py"])
        for source_path, digest, size in rows:
            packaged = root / source_path
            self.assertEqual(digest, hashlib.sha256(packaged.read_bytes()).hexdigest())
            self.assertEqual(size, packaged.stat().st_size)

    def test_stage_refuses_to_replace_a_packaged_asset(self):
        packager = load_packager()
        temporary, root, tooling = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        destination = root / "tools" / "importer.py"
        destination.parent.mkdir()
        destination.write_text("existing\n", encoding="utf-8")
        asset = packager.PackagedAsset(tooling / "importer.py", "tools/importer.py", "recovery-tool")

        with self.assertRaisesRegex(ValueError, "already exists"):
            packager.stage_import_readiness(root, [asset], captured_at="2026-08-10T12:00:00Z")

    def test_import_command_stages_raw_bytes_and_refreshes_checksums(self):
        packager = load_packager()
        temporary, root, _ = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        manifest = self.write_import_bundle(Path(temporary.name))
        schema = Path(__file__).parents[1] / "schemas" / "commerce-import-bundle-v1.schema.json"

        report = packager.stage_and_import_bundle(root, manifest, schema)

        staged = root / "raw" / "private-exports" / "fixture-import-001"
        self.assertEqual(report["status"], "reconciled")
        self.assertTrue((staged / "export-manifest.json").is_file())
        self.assertEqual((staged / "database.sql").read_bytes(), b"-- synthetic export\n")
        checksum_text = (root / "SHA256SUMS.txt").read_text(encoding="utf-8")
        self.assertIn("mt_uniforms_recovery.sqlite", checksum_text)
        self.assertIn("raw/private-exports/fixture-import-001/database.sql", checksum_text)
        connection = sqlite3.connect(root / "mt_uniforms_recovery.sqlite")
        try:
            source_paths = {
                row[0] for row in connection.execute(
                    "SELECT source_path FROM source_manifest WHERE source_ref LIKE 'import:%'"
                )
            }
        finally:
            connection.close()
        self.assertEqual(
            source_paths,
            {
                "raw/private-exports/fixture-import-001/database.sql",
                "raw/private-exports/fixture-import-001/categories.ndjson",
            },
        )

    def test_failed_import_retains_raw_evidence_and_refreshes_checksums(self):
        packager = load_packager()
        temporary, root, _ = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        manifest = self.write_import_bundle(Path(temporary.name), invalid_parent=True)
        schema = Path(__file__).parents[1] / "schemas" / "commerce-import-bundle-v1.schema.json"

        with self.assertRaisesRegex(ValueError, "foreign key"):
            packager.stage_and_import_bundle(root, manifest, schema)

        staged = root / "raw" / "private-exports" / "fixture-import-001"
        self.assertTrue((staged / "export-manifest.json").is_file())
        checksum_text = (root / "SHA256SUMS.txt").read_text(encoding="utf-8")
        self.assertIn("mt_uniforms_recovery.sqlite", checksum_text)
        self.assertIn("raw/private-exports/fixture-import-001/categories.ndjson", checksum_text)
        connection = sqlite3.connect(root / "mt_uniforms_recovery.sqlite")
        try:
            self.assertEqual(connection.execute("SELECT status FROM import_runs").fetchone()[0], "failed")
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM catalog_categories").fetchone()[0], 0)
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
