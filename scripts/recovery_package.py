#!/usr/bin/env python3
"""Upgrade and verify the portable M&T Uniforms recovery package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath


SCHEMA_VERSION = "1.1.0"
DATABASE_USER_VERSION = 2
APPLICATION_ID = 0x4D545552  # ASCII MTUR
CHECKSUM_FILE = "SHA256SUMS.txt"
DATABASE_FILE = "mt_uniforms_recovery.sqlite"

SOURCE_MANIFEST_COLUMNS = {
    "source_ref": "TEXT",
    "source_uri": "TEXT",
    "capture_method": "TEXT",
    "source_version": "TEXT",
    "record_count": "INTEGER",
    "window_start": "TEXT",
    "window_end": "TEXT",
    "sensitivity": "TEXT",
    "completeness": "TEXT",
}


def ensure_provenance_schema(connection: sqlite3.Connection) -> None:
    existing = {row[1] for row in connection.execute("PRAGMA table_info(source_manifest)")}
    for name, declaration in SOURCE_MANIFEST_COLUMNS.items():
        if name not in existing:
            connection.execute(f"ALTER TABLE source_manifest ADD COLUMN {name} {declaration}")
    statements = [
        """CREATE TABLE IF NOT EXISTS business_entities(
            entity_id TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL,
            canonical_name TEXT NOT NULL,
            jurisdiction TEXT,
            registration_identifier TEXT,
            lifecycle_status TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS business_facts(
            fact_id INTEGER PRIMARY KEY,
            entity_id TEXT NOT NULL REFERENCES business_entities(entity_id),
            fact_type TEXT NOT NULL,
            value_text TEXT NOT NULL,
            normalized_value TEXT,
            observed_at TEXT NOT NULL,
            valid_from TEXT,
            valid_to TEXT,
            verification_status TEXT NOT NULL CHECK(verification_status IN
                ('publicly-observed','client-claimed','primary-record-verified','contradicted','unknown')),
            confidence TEXT NOT NULL,
            source_id INTEGER NOT NULL REFERENCES source_manifest(source_id)
        )""",
        """CREATE TABLE IF NOT EXISTS infrastructure_assets(
            asset_id TEXT PRIMARY KEY,
            asset_type TEXT NOT NULL,
            canonical_identifier TEXT NOT NULL UNIQUE,
            purpose TEXT,
            parent_asset_id TEXT REFERENCES infrastructure_assets(asset_id),
            lifecycle_status TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS infrastructure_observations(
            observation_id INTEGER PRIMARY KEY,
            asset_id TEXT NOT NULL REFERENCES infrastructure_assets(asset_id),
            observation_type TEXT NOT NULL,
            observed_value_json TEXT NOT NULL CHECK(json_valid(observed_value_json)),
            observed_at TEXT NOT NULL,
            expires_at TEXT,
            verification_status TEXT NOT NULL CHECK(verification_status IN
                ('publicly-observed','client-claimed','primary-record-verified','contradicted','unknown')),
            source_id INTEGER NOT NULL REFERENCES source_manifest(source_id)
        )""",
        """CREATE TABLE IF NOT EXISTS asset_control_claims(
            claim_id INTEGER PRIMARY KEY,
            asset_id TEXT NOT NULL REFERENCES infrastructure_assets(asset_id),
            entity_id TEXT REFERENCES business_entities(entity_id),
            control_role TEXT NOT NULL,
            claim_status TEXT NOT NULL CHECK(claim_status IN
                ('publicly-observed','client-claimed','primary-record-verified','contradicted','unknown')),
            observed_at TEXT NOT NULL,
            effective_from TEXT,
            effective_to TEXT,
            renewal_at TEXT,
            recovery_contact_ref TEXT,
            recovery_path TEXT,
            source_id INTEGER NOT NULL REFERENCES source_manifest(source_id),
            notes TEXT
        )""",
    ]
    for statement in statements:
        connection.execute(statement)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_files(root: Path) -> list[Path]:
    excluded = {CHECKSUM_FILE, f"{DATABASE_FILE}-wal", f"{DATABASE_FILE}-shm"}
    return sorted(
        (
            path
            for path in root.rglob("*")
            if path.is_file()
            and path.name not in excluded
            and not path.name.endswith((".tmp", ".pyc"))
            and "__pycache__" not in path.parts
        ),
        key=lambda path: path.relative_to(root).as_posix(),
    )


def write_checksums(root: Path) -> Path:
    root = Path(root).resolve()
    lines = [
        f"{sha256_file(path)}  {path.relative_to(root).as_posix()}"
        for path in package_files(root)
    ]
    destination = root / CHECKSUM_FILE
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return destination


def _is_absolute_any_platform(value: str) -> bool:
    return Path(value).is_absolute() or PureWindowsPath(value).is_absolute()


def _portable_source_path(value: str, old_root: str | None) -> str:
    if not _is_absolute_any_platform(value):
        return value.replace("\\", "/")
    if not old_root:
        raise ValueError(f"cannot relativize absolute source path without prior root: {value}")
    source = PureWindowsPath(value)
    base = PureWindowsPath(old_root)
    try:
        return source.relative_to(base).as_posix()
    except ValueError as exc:
        raise ValueError(f"absolute source path is outside the prior package root: {value}") from exc


def upgrade_package(root: Path) -> dict:
    root = Path(root).resolve()
    manifest_path = root / "package-manifest.json"
    database_path = root / DATABASE_FILE
    if not manifest_path.is_file() or not database_path.is_file():
        raise ValueError("package-manifest.json and mt_uniforms_recovery.sqlite are required")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    old_root = manifest.get("root")
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    connection = sqlite3.connect(database_path)
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "CREATE TABLE IF NOT EXISTS recovery_metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        ensure_provenance_schema(connection)
        rows = connection.execute(
            "SELECT source_id, source_path FROM source_manifest WHERE source_path IS NOT NULL"
        ).fetchall()
        for source_id, source_path in rows:
            portable = _portable_source_path(source_path, old_root)
            connection.execute(
                "UPDATE source_manifest SET source_path=? WHERE source_id=?",
                (portable, source_id),
            )
        metadata = {
            "schema_version": SCHEMA_VERSION,
            "package_id": str(manifest.get("package", "mt-uniforms-recovery")),
            "package_root": ".",
            "upgraded_at": now,
        }
        connection.executemany(
            "INSERT INTO recovery_metadata(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            metadata.items(),
        )
        connection.execute(f"PRAGMA application_id={APPLICATION_ID}")
        connection.execute(f"PRAGMA user_version={DATABASE_USER_VERSION}")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    manifest["schema_version"] = SCHEMA_VERSION
    manifest["root"] = "."
    manifest["database"] = {
        "path": DATABASE_FILE,
        "application_id": APPLICATION_ID,
        "user_version": DATABASE_USER_VERSION,
        "metadata_table": "recovery_metadata",
        "lineage_table": "source_manifest",
    }
    manifest["portability"] = {
        "status": "portable-relative-paths",
        "upgraded_at": now,
        "checksum_manifest": CHECKSUM_FILE,
    }
    work_scope = manifest.setdefault("work_scope_migration", {})
    work_scope["status"] = "legacy-source-snapshots-preserved"
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    write_checksums(root)
    return verify_package(root)


def verify_package(root: Path) -> dict:
    root = Path(root).resolve()
    manifest_path = root / "package-manifest.json"
    database_path = root / DATABASE_FILE
    checksums_path = root / CHECKSUM_FILE
    for required in (manifest_path, database_path, checksums_path):
        if not required.is_file():
            raise ValueError(f"missing required package file: {required.name}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("package manifest schema_version is missing or unsupported")
    if manifest.get("root") != ".":
        raise ValueError("package manifest root must be the portable relative path '.'")

    expected_files = {
        path.relative_to(root).as_posix(): sha256_file(path) for path in package_files(root)
    }
    recorded: dict[str, str] = {}
    for line_number, line in enumerate(checksums_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line:
            continue
        try:
            digest, relative = line.split("  ", 1)
        except ValueError as exc:
            raise ValueError(f"malformed checksum line {line_number}") from exc
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise ValueError(f"malformed checksum digest on line {line_number}")
        if relative in recorded:
            raise ValueError(f"duplicate checksum path: {relative}")
        recorded[relative] = digest
    if recorded.keys() != expected_files.keys():
        missing = sorted(expected_files.keys() - recorded.keys())
        extra = sorted(recorded.keys() - expected_files.keys())
        raise ValueError(f"checksum inventory mismatch; missing={missing}; extra={extra}")
    mismatched = sorted(path for path, digest in recorded.items() if expected_files[path] != digest)
    if mismatched:
        raise ValueError(f"checksum mismatch: {mismatched[0]}")

    connection = sqlite3.connect(f"file:{database_path.as_posix()}?mode=ro", uri=True)
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        foreign_key_errors = connection.execute("PRAGMA foreign_key_check").fetchall()
        user_version = connection.execute("PRAGMA user_version").fetchone()[0]
        application_id = connection.execute("PRAGMA application_id").fetchone()[0]
        metadata = dict(connection.execute("SELECT key, value FROM recovery_metadata"))
        source_rows = connection.execute(
            "SELECT source_id, source_path, sha256, bytes FROM source_manifest "
            "WHERE source_path IS NOT NULL"
        ).fetchall()
        table_names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        provenance_tables = (
            "business_entities",
            "business_facts",
            "infrastructure_assets",
            "infrastructure_observations",
            "asset_control_claims",
        )
        record_counts = {
            name: connection.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
            for name in provenance_tables
            if name in table_names
        }
        rec003_source_rows = connection.execute(
            "SELECT COUNT(*) FROM source_manifest WHERE source_ref='REC-003'"
        ).fetchone()[0] if "source_ref" in {
            row[1] for row in connection.execute("PRAGMA table_info(source_manifest)")
        } else 0
    finally:
        connection.close()

    if integrity != "ok":
        raise ValueError(f"SQLite integrity_check failed: {integrity}")
    if foreign_key_errors:
        raise ValueError(f"SQLite foreign_key_check found {len(foreign_key_errors)} error(s)")
    if user_version != DATABASE_USER_VERSION or application_id != APPLICATION_ID:
        raise ValueError("SQLite schema identity does not match the recovery package contract")
    if metadata.get("schema_version") != SCHEMA_VERSION or metadata.get("package_root") != ".":
        raise ValueError("recovery_metadata is incomplete or incompatible")
    required_tables = {
        "business_entities",
        "business_facts",
        "infrastructure_assets",
        "infrastructure_observations",
        "asset_control_claims",
    }
    if not required_tables.issubset(table_names):
        raise ValueError("record-level provenance schema is incomplete")
    public_ownership = manifest.get("public_ownership")
    if public_ownership:
        observed_total = (
            record_counts["business_facts"]
            + record_counts["infrastructure_observations"]
            + record_counts["asset_control_claims"]
        )
        if observed_total != int(public_ownership.get("observation_count", -1)):
            raise ValueError("public ownership observation count does not match SQLite")
        if rec003_source_rows != int(public_ownership.get("artifact_count", -1)):
            raise ValueError("public ownership artifact count does not match source_manifest")

    absolute_paths = [path for _, path, _, _ in source_rows if _is_absolute_any_platform(path)]
    if absolute_paths:
        raise ValueError("source_manifest contains absolute paths")
    missing_sources = []
    lineage_mismatches = []
    for source_id, source_path, source_sha256, source_bytes in source_rows:
        resolved = root / Path(source_path)
        if not resolved.exists():
            missing_sources.append(source_path)
            continue
        if resolved.is_file() and source_sha256:
            if sha256_file(resolved) != str(source_sha256).lower():
                lineage_mismatches.append(f"source_id={source_id}:sha256")
            if source_bytes is not None and resolved.stat().st_size != int(source_bytes):
                lineage_mismatches.append(f"source_id={source_id}:bytes")
    if missing_sources:
        raise ValueError(f"source_manifest paths are missing: {missing_sources[:3]}")
    if lineage_mismatches:
        raise ValueError(f"source_manifest lineage mismatch: {lineage_mismatches[:3]}")

    return {
        "valid": True,
        "schema_version": SCHEMA_VERSION,
        "database_user_version": user_version,
        "database_application_id": application_id,
        "checksummed_files": len(recorded),
        "source_manifest_rows": len(source_rows),
        "integrity": integrity,
        "foreign_key_errors": len(foreign_key_errors),
        "record_counts": record_counts,
        "rec003_source_rows": rec003_source_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("upgrade", "verify"))
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    report = upgrade_package(args.root) if args.command == "upgrade" else verify_package(args.root)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
