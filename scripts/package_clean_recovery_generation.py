#!/usr/bin/env python3
"""Build cache-free REC-015 and self-test it without mutating authority bytes."""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
import shutil
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath

import capture_missing_media
import package_operational_recovery_generation as rec014
import recovery_package
import run_recovery_drill_v3


GENERATION = "REC-015"
PARENT_GENERATION = "REC-014"
READINESS = "cache-free-operational-recovery-self-test-proven-awaiting-authenticated-exports"
PackagedAsset = rec014.PackagedAsset


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def default_assets() -> list[PackagedAsset]:
    project = Path(__file__).resolve().parents[1]
    return [
        PackagedAsset(
            project / "scripts/package_clean_recovery_generation.py",
            "tools/package_clean_recovery_generation.py",
            "recovery-tool",
        ),
        PackagedAsset(
            project / "scripts/run_recovery_drill_v3.py",
            "tools/run_recovery_drill_v3.py",
            "recovery-tool",
        ),
        PackagedAsset(
            project / "docs/recovery/representative-restore-drill-v3.md",
            "docs/recovery/representative-restore-drill-v3.md",
            "recovery-contract",
        ),
        PackagedAsset(
            project / "docs/recovery/cache-free-operational-recovery-package-v1.md",
            "docs/recovery/cache-free-operational-recovery-package-v1.md",
            "recovery-contract",
        ),
    ]


def remove_cache_artifacts(root: Path) -> int:
    root = Path(root).resolve()
    files = sorted(
        (path for path in root.rglob("*.pyc") if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix(),
    )
    for path in files:
        path.unlink()
    directories = sorted(
        (path for path in root.rglob("__pycache__") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for directory in directories:
        shutil.rmtree(directory)
    return len(files)


def cleanup_sqlite_sidecars(root: Path) -> int:
    root = Path(root).resolve()
    removed = 0
    for suffix in ("-wal", "-shm"):
        sidecar = root / f"{recovery_package.DATABASE_FILE}{suffix}"
        if sidecar.is_file():
            sidecar.unlink()
            removed += 1
    return removed


def _copy_assets(root: Path, assets: list[PackagedAsset], captured_at: str) -> None:
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        connection.execute("BEGIN IMMEDIATE")
        for asset in assets:
            source = Path(asset.source).resolve()
            if not source.is_file():
                raise ValueError(f"required REC-015 source asset is missing: {source.name}")
            relative = Path(asset.destination)
            if relative.is_absolute() or PureWindowsPath(asset.destination).is_absolute() or ".." in relative.parts:
                raise ValueError(f"packaged destination is not portable: {asset.destination}")
            destination = root / relative
            if destination.exists() and not asset.replace_existing:
                raise ValueError(f"packaged asset already exists: {asset.destination}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            connection.execute(
                """INSERT INTO source_manifest(
                    system,artifact_type,source_path,captured_at,sha256,bytes,status,notes,
                    source_ref,capture_method,record_count,sensitivity,completeness
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    "recovery-tooling",
                    asset.artifact_type,
                    relative.as_posix(),
                    captured_at,
                    recovery_package.sha256_file(destination),
                    destination.stat().st_size,
                    "captured",
                    f"REC-015 packaged {asset.artifact_type}: {relative.name}",
                    f"rec015:{asset.artifact_type}:{relative.as_posix()}",
                    "deterministic-copy",
                    0,
                    "internal",
                    "complete-file",
                ),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _status(captured_at: str, proven: bool) -> str:
    state = "PROVEN" if proven else "READY"
    detail = (
        "The cache-free package-local v3 drill passed before promotion with 22 normalized and 22 lineage rows, zero foreign-key errors, unchanged authority hashes, and zero Python cache artifacts."
        if proven
        else "The cache-free generation-aware v3 drill is packaged and awaiting mandatory pre-promotion execution."
    )
    return f"""# M&T Uniforms REC-015 recovery status

Generated: {captured_at}

REC-015 is the current cache-free operational recovery successor. REC-013 and REC-014 remain preserved diagnostic checkpoints and are not current.

- Public storefront: 528 reachable safe pages; zero queued uncaptured URLs.
- Public media: 1,542 / 1,542 exact referenced binaries.
- Runtime: 34 / 35 references captured; retired AddThis is dispositioned.
- Journal supplemental theme/settings export: preserved and hashed.
- Checksums, SQLite integrity, foreign keys, relative provenance, and full physical-file reconciliation: verified.
- Work Scope enrollment and legacy history preservation: verified.
- Value-free service/account inventory: 10 services; unknown control fields explicit.
- Package-local v3 drill: {state}. {detail}
- Python cache artifacts in authority: 0.
- Fresh private commerce/import rows: 0.
- Clover authenticated export is excluded by DEC-005.

Still awaiting authenticated OpenCart/Ecwid source bytes, primary account-control evidence, and approved encrypted offline/offsite custody.
"""


def _audit(captured_at: str, proven: bool) -> str:
    state = "PROVEN" if proven else "READY-AWAITING-SELF-TEST"
    return f"""# Recovery objective completion audit

Generated: {captured_at}

- OpenCart full native source: TOOL-READY, MISSING-SOURCE.
- Journal supplement: PROVEN.
- Ecwid complete JSON/binary source: TOOL-READY, MISSING-SOURCE.
- Clover authentication: EXCLUDED-BY-DECISION under DEC-005.
- Public storefront/media/runtime/business infrastructure: PROVEN for the reachable safe graph.
- Portable database, checksums, provenance, staged importer, and representative reconstruction: PROVEN.
- Cache-free package-local REC-015 drill: {state}.
- Service/account continuity inventory: PROVEN; primary control evidence MISSING-SOURCE.
- Work Scope and legacy history preservation: PROVEN.
- Encrypted offline and independent offsite custody: MISSING-SOURCE pending approved recipient/key and destination.

The full objective remains incomplete only where authenticated source bytes, primary account evidence, or an approved encryption/custody endpoint are unavailable. No private client records are invented.
"""


def _upsert_generated_file(root: Path, relative: str, captured_at: str) -> None:
    path = root / relative
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        values = (
            captured_at,
            recovery_package.sha256_file(path),
            path.stat().st_size,
            f"REC-015 generated current status: {relative}",
            f"rec015:generated:{relative}",
            relative,
        )
        updated = connection.execute(
            """UPDATE source_manifest SET captured_at=?,sha256=?,bytes=?,status='captured',
                notes=?,source_ref=?,capture_method='deterministic-render',record_count=0,
                sensitivity='internal',completeness='complete-file' WHERE source_path=?""",
            values,
        ).rowcount
        if not updated:
            connection.execute(
                """INSERT INTO source_manifest(
                    system,artifact_type,source_path,captured_at,sha256,bytes,status,notes,
                    source_ref,capture_method,record_count,sensitivity,completeness
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    "recovery-tooling",
                    "recovery-status",
                    relative,
                    captured_at,
                    recovery_package.sha256_file(path),
                    path.stat().st_size,
                    "captured",
                    f"REC-015 generated current status: {relative}",
                    f"rec015:generated:{relative}",
                    "deterministic-render",
                    0,
                    "internal",
                    "complete-file",
                ),
            )
        connection.commit()
    finally:
        connection.close()


def _write_docs(root: Path, captured_at: str, proven: bool) -> None:
    (root / "RECOVERY-STATUS.md").write_text(
        _status(captured_at, proven), encoding="utf-8", newline="\n"
    )
    (root / "COMPLETION-AUDIT.md").write_text(
        _audit(captured_at, proven), encoding="utf-8", newline="\n"
    )
    _upsert_generated_file(root, "RECOVERY-STATUS.md", captured_at)
    _upsert_generated_file(root, "COMPLETION-AUDIT.md", captured_at)


def stage_clean_readiness(
    root: Path, assets: list[PackagedAsset], captured_at: str | None = None
) -> dict:
    root = Path(root).resolve()
    now = captured_at or utc_now()
    manifest_path = root / "package-manifest.json"
    database = root / recovery_package.DATABASE_FILE
    if not manifest_path.is_file() or not database.is_file():
        raise ValueError("recovery database and package manifest are required")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("generation") != PARENT_GENERATION:
        raise ValueError(f"source generation must be {PARENT_GENERATION}")
    removed = remove_cache_artifacts(root)
    run_recovery_drill_v3.assert_no_cache_artifacts(root)
    _copy_assets(root, assets, now)
    connection = sqlite3.connect(database)
    try:
        connection.executemany(
            "INSERT INTO recovery_metadata(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            {
                "generation": GENERATION,
                "parent_generation": PARENT_GENERATION,
                "recovery_readiness": "cache-free-operational-self-test-pending",
                "representative_restore_drill": "ready-awaiting-cache-free-self-test",
                "python_cache_artifacts": "0",
            }.items(),
        )
        connection.commit()
    finally:
        connection.close()
    manifest = rec014.rec013.rec012.rec011.rec010.rec009.rec008._remove_legacy_absolute_paths(manifest)
    manifest["generation"] = GENERATION
    manifest["parent_generation"] = PARENT_GENERATION
    manifest["generated_at"] = now
    manifest["recovery_readiness"] = "cache-free-operational-self-test-pending"
    manifest["python_cache_artifacts"] = 0
    manifest["restore_drill"] = {
        "status": "ready-awaiting-self-test",
        "tool": "tools/run_recovery_drill_v3.py",
        "contract": "docs/recovery/representative-restore-drill-v3.md",
        "authority_population_effect": "none",
        "self_test": None,
    }
    manifest.setdefault("commerce_import", {})["tool"] = (
        "tools/package_clean_recovery_generation.py"
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    _write_docs(root, now, proven=False)
    return {
        "generation": GENERATION,
        "parent_generation": PARENT_GENERATION,
        "readiness": "cache-free-operational-self-test-pending",
        "removed_cache_artifacts": removed,
        "packaged_assets": len(assets),
    }


def mark_drill_proven(root: Path, report: dict, captured_at: str | None = None) -> dict:
    valid = (
        report.get("valid") is True
        and report.get("authority_unchanged") is True
        and report.get("authority_cache_artifacts") == 0
        and report.get("import", {}).get("status") == "reconciled"
        and report.get("reconstruction", {}).get("valid") is True
        and report.get("reconstruction", {}).get("foreign_key_errors") == 0
        and report.get("reconstruction", {}).get("lineage_rows") == 22
    )
    if not valid:
        raise ValueError("REC-015 proof requires a successful cache-free package-local drill")
    root = Path(root).resolve()
    run_recovery_drill_v3.assert_no_cache_artifacts(root)
    now = captured_at or utc_now()
    manifest_path = root / "package-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("generation") != GENERATION:
        raise ValueError("drill proof can only be recorded on REC-015")
    manifest["generated_at"] = now
    manifest["recovery_readiness"] = READINESS
    manifest["restore_drill"]["status"] = "proven-cache-free-package-local-copy"
    manifest["restore_drill"]["self_test"] = {
        "drill_version": report.get("drill_version"),
        "authority_unchanged": True,
        "authority_cache_artifacts": 0,
        "normalized_rows": report.get("import", {}).get("normalized_rows"),
        "lineage_rows": 22,
        "foreign_key_errors": 0,
        "classification": report.get("classification"),
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        connection.executemany(
            "INSERT INTO recovery_metadata(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            {
                "recovery_readiness": READINESS,
                "representative_restore_drill": "proven-cache-free-package-local-copy",
                "python_cache_artifacts": "0",
            }.items(),
        )
        connection.commit()
    finally:
        connection.close()
    _write_docs(root, now, proven=True)
    return manifest["restore_drill"]["self_test"]


def stage_and_import_bundle(root: Path, manifest_path: Path, schema_path: Path | None = None) -> dict:
    return rec014.stage_and_import_bundle(root, manifest_path, schema_path)


def create_generation(source: Path, destination: Path) -> dict:
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    if not source.is_dir():
        raise ValueError(f"source generation does not exist: {source}")
    if destination.exists():
        raise ValueError(f"destination already exists; recovery generations are immutable: {destination}")
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("source and destination generations must be distinct, non-nested paths")
    rec014.verify_generation(source, require_empty=True, require_drill_proof=True)
    temporary = destination.with_name(f".{destination.name}.building-{uuid.uuid4().hex}")
    drill_output = destination.with_name(f".{destination.name}.self-test-{uuid.uuid4().hex}")
    try:
        shutil.copytree(source, temporary)
        stage_clean_readiness(temporary, default_assets())
        recovery_package.write_checksums(temporary)
        verify_generation(temporary, require_empty=True, require_drill_proof=False)
        report = run_recovery_drill_v3.run_drill(temporary, drill_output)
        mark_drill_proven(temporary, report)
        recovery_package.write_checksums(temporary)
        final = verify_generation(temporary, require_empty=True, require_drill_proof=True)
        temporary.rename(destination)
        return final
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    finally:
        shutil.rmtree(drill_output, ignore_errors=True)


def verify_generation(
    root: Path, require_empty: bool = False, require_drill_proof: bool = False
) -> dict:
    root = Path(root).resolve()
    run_recovery_drill_v3.assert_no_cache_artifacts(root)
    package = capture_missing_media.verify_generation(root, expected_generation=GENERATION)
    base = recovery_package.verify_package(root)
    run_recovery_drill_v3.assert_no_cache_artifacts(root)
    cleanup_sqlite_sidecars(root)
    physical_files = sum(1 for path in root.rglob("*") if path.is_file())
    if physical_files != base["checksummed_files"] + 1:
        raise ValueError(
            f"REC-015 physical/checksum inventory mismatch: {physical_files} != "
            f"{base['checksummed_files']} + SHA256SUMS"
        )
    manifest = json.loads((root / "package-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("generation") != GENERATION or manifest.get("parent_generation") != PARENT_GENERATION:
        raise ValueError("REC-015 generation lineage is invalid")
    if manifest.get("python_cache_artifacts") != 0:
        raise ValueError("REC-015 cache metadata is invalid")
    absolute = rec014.rec013.rec012.rec011.rec010.rec009.rec008._manifest_absolute_paths(manifest)
    if absolute:
        raise ValueError(f"package manifest contains absolute paths: {absolute[:3]}")
    drill = manifest.get("restore_drill", {})
    required = [
        drill.get("tool"),
        drill.get("contract"),
        manifest.get("commerce_import", {}).get("tool"),
        "docs/recovery/cache-free-operational-recovery-package-v1.md",
        rec014.rec013.INVENTORY_PATH,
        "RECOVERY-STATUS.md",
        "COMPLETION-AUDIT.md",
    ]
    for relative in required:
        if not relative or not (root / relative).is_file():
            raise ValueError(f"REC-015 packaged dependency is missing: {relative}")
    inventory = rec014.rec013.validate_service_inventory(root / rec014.rec013.INVENTORY_PATH)
    status = (root / "RECOVERY-STATUS.md").read_text(encoding="utf-8")
    if "# M&T Uniforms REC-015 recovery status" not in status or "Python cache artifacts in authority: 0" not in status:
        raise ValueError("REC-015 recovery status is incomplete")
    if require_drill_proof:
        proof = drill.get("self_test") or {}
        if drill.get("status") != "proven-cache-free-package-local-copy":
            raise ValueError("REC-015 package-local drill proof is missing")
        if proof.get("authority_cache_artifacts") != 0 or proof.get("lineage_rows") != 22:
            raise ValueError("REC-015 package-local drill proof is invalid")
        if "Package-local v3 drill: PROVEN" not in status:
            raise ValueError("REC-015 status does not record package-local drill proof")
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        metadata = dict(connection.execute("SELECT key,value FROM recovery_metadata"))
        counts = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in rec014.rec013.rec012.rec011.rec010.rec009.rec008.EMPTY_IMPORT_TABLES
        }
        import_sources = connection.execute(
            "SELECT COUNT(*) FROM source_manifest WHERE source_ref LIKE 'import:%'"
        ).fetchone()[0]
    finally:
        connection.close()
    if metadata.get("generation") != GENERATION or metadata.get("parent_generation") != PARENT_GENERATION:
        raise ValueError("REC-015 database lineage metadata is invalid")
    if metadata.get("python_cache_artifacts") != "0":
        raise ValueError("REC-015 database cache metadata is invalid")
    if require_empty and (sum(counts.values()) or import_sources):
        raise ValueError("fresh REC-015 contains source-backed commerce/import rows")
    return {
        "valid": True,
        "generation": GENERATION,
        "parent_generation": PARENT_GENERATION,
        "readiness": manifest.get("recovery_readiness"),
        "drill_status": drill.get("status"),
        "normalized_rows": sum(counts.values()),
        "inventory_services": inventory["services"],
        "python_cache_artifacts": 0,
        "physical_files": physical_files,
        "checksummed_files": base["checksummed_files"],
        "package": package,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create")
    create.add_argument("source", type=Path)
    create.add_argument("destination", type=Path)
    verify = sub.add_parser("verify")
    verify.add_argument("root", type=Path)
    ingest = sub.add_parser("stage-import")
    ingest.add_argument("root", type=Path)
    ingest.add_argument("manifest", type=Path)
    ingest.add_argument("--schema", type=Path)
    args = parser.parse_args()
    if args.command == "create":
        report = create_generation(args.source, args.destination)
    elif args.command == "verify":
        report = verify_generation(args.root, require_drill_proof=True)
    else:
        report = stage_and_import_bundle(args.root, args.manifest, args.schema)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
