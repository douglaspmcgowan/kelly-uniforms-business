import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("upgrade_commerce_schema.py")
SPEC = importlib.util.spec_from_file_location("upgrade_commerce_schema", MODULE_PATH)
schema = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(schema)


class CommerceSchemaTests(unittest.TestCase):
    def make_database(self):
        temporary = tempfile.TemporaryDirectory()
        database = Path(temporary.name) / "recovery.sqlite"
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
            "INSERT INTO source_manifest(system, artifact_type, status) VALUES('fixture','export','captured')"
        )
        connection.commit()
        connection.close()
        return temporary, database

    def test_schema_covers_required_business_families_without_inventing_rows(self):
        temporary, database = self.make_database()
        self.addCleanup(temporary.cleanup)
        report = schema.apply_schema(database)
        self.assertEqual(report["schema_version"], schema.COMMERCE_SCHEMA_VERSION)
        self.assertEqual(set(report["missing_tables"]), set())

        connection = sqlite3.connect(database)
        connection.execute("PRAGMA foreign_keys=ON")
        try:
            tables = {row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )}
            self.assertTrue(schema.REQUIRED_TABLES.issubset(tables))
            for table in schema.REQUIRED_TABLES:
                self.assertEqual(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0], 0)
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO catalog_products(record_id, name, lifecycle_status) VALUES('p1','Test','active')"
                )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    """INSERT INTO catalog_products(
                        record_id, name, lifecycle_status, source_system, source_record_id,
                        extracted_at, source_id
                    ) VALUES('p1','Test','active','fixture','p1','2026-08-10T00:00:00Z',999)"""
                )
        finally:
            connection.close()

    def test_schema_application_is_idempotent(self):
        temporary, database = self.make_database()
        self.addCleanup(temporary.cleanup)
        first = schema.apply_schema(database)
        second = schema.apply_schema(database)
        self.assertEqual(first["table_count"], second["table_count"])
        self.assertEqual(second["foreign_key_errors"], 0)


if __name__ == "__main__":
    unittest.main()
