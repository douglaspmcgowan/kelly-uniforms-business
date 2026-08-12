#!/usr/bin/env python3
"""Build and operate REC-012 with Ecwid JSON and binary acquisition."""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath

import capture_missing_media
import package_complete_source_generation as rec011
import recovery_package


GENERATION = "REC-012"
PARENT_GENERATION = "REC-011"
READINESS = "opencart-and-ecwid-json-binary-tools-packaged-awaiting-authenticated-exports"
PackagedAsset = rec011.PackagedAsset


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def default_assets() -> list[PackagedAsset]:
    project = Path(__file__).resolve().parents[1]
    return [
        PackagedAsset(
            project / "scripts/package_binary_ready_generation.py",
            "tools/package_binary_ready_generation.py",
            "recovery-tool",
        ),
        PackagedAsset(
            project / "scripts/capture_ecwid_binaries.py",
            "tools/capture_ecwid_binaries.py",
            "capture-tool",
        ),
        PackagedAsset(
            project / "docs/recovery/ecwid-binary-capture-v1.md",
            "docs/recovery/ecwid-binary-capture-v1.md",
            "capture-contract",
        ),
        PackagedAsset(
            project / "docs/recovery/binary-ready-package-v1.md",
            "docs/recovery/binary-ready-package-v1.md",
            "capture-contract",
        ),
    ]


def _copy_assets(root: Path, assets: list[PackagedAsset], captured_at: str) -> None:
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        connection.execute("BEGIN IMMEDIATE")
        for asset in assets:
            source = Path(asset.source).resolve()
            if not source.is_file():
                raise ValueError(f"required REC-012 source asset is missing: {source.name}")
            relative = Path(asset.destination)
            if relative.is_absolute() or PureWindowsPath(asset.destination).is_absolute() or ".." in relative.parts:
                raise ValueError(f"packaged destination is not portable: {asset.destination}")
            destination = root / relative
            if destination.exists() and not asset.replace_existing:
                raise ValueError(f"packaged asset already exists: {asset.destination}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            digest = recovery_package.sha256_file(destination)
            size = destination.stat().st_size
            connection.execute(
                """INSERT INTO source_manifest(
                    system,artifact_type,source_path,captured_at,sha256,bytes,status,notes,
                    source_ref,capture_method,record_count,sensitivity,completeness
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    "recovery-tooling", asset.artifact_type, relative.as_posix(), captured_at,
                    digest, size, "captured",
                    f"REC-012 packaged {asset.artifact_type}: {relative.name}",
                    f"rec012:{asset.artifact_type}:{relative.as_posix()}",
                    "deterministic-copy", 0, "internal", "complete-file",
                ),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def stage_binary_readiness(
    root: Path,
    assets: list[PackagedAsset],
    captured_at: str | None = None,
) -> dict:
    root = Path(root).resolve()
    now = captured_at or utc_now()
    database = root / recovery_package.DATABASE_FILE
    manifest_path = root / "package-manifest.json"
    if not database.is_file() or not manifest_path.is_file():
        raise ValueError("recovery database and package manifest are required")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("generation") != PARENT_GENERATION:
        raise ValueError(f"source generation must be {PARENT_GENERATION}")
    _copy_assets(root, assets, now)
    connection = sqlite3.connect(database)
    try:
        connection.executemany(
            "INSERT INTO recovery_metadata(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            {
                "generation": GENERATION,
                "parent_generation": PARENT_GENERATION,
                "source_capture_readiness": READINESS,
            }.items(),
        )
        connection.commit()
    finally:
        connection.close()
    manifest = rec011.rec010.rec009.rec008._remove_legacy_absolute_paths(manifest)
    manifest["generation"] = GENERATION
    manifest["parent_generation"] = PARENT_GENERATION
    manifest["generated_at"] = now
    source_capture = manifest.setdefault("source_capture", {})
    source_capture.update(
        {
            "readiness": READINESS,
            "ecwid_binary_tool": "tools/capture_ecwid_binaries.py",
            "ecwid_binary_contract": "docs/recovery/ecwid-binary-capture-v1.md",
            "captured_private_exports": False,
        }
    )
    manifest.setdefault("commerce_import", {})["tool"] = "tools/package_binary_ready_generation.py"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    return {
        "generation": GENERATION,
        "parent_generation": PARENT_GENERATION,
        "packaged_assets": len(assets),
        "readiness": READINESS,
    }


def stage_and_import_bundle(root: Path, manifest_path: Path, schema_path: Path | None = None) -> dict:
    return rec011.stage_and_import_bundle(root, manifest_path, schema_path)


def create_generation(source: Path, destination: Path) -> dict:
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    if not source.is_dir():
        raise ValueError(f"source generation does not exist: {source}")
    if destination.exists():
        raise ValueError(f"destination already exists; recovery generations are immutable: {destination}")
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("source and destination generations must be distinct, non-nested paths")
    rec011.verify_generation(source, require_empty=True)
    temporary = destination.with_name(f".{destination.name}.building-{uuid.uuid4().hex}")
    try:
        shutil.copytree(source, temporary)
        stage_binary_readiness(temporary, default_assets())
        recovery_package.write_checksums(temporary)
        report = verify_generation(temporary, require_empty=True)
        temporary.rename(destination)
        return report
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def verify_generation(root: Path, require_empty: bool = False) -> dict:
    root = Path(root).resolve()
    package = capture_missing_media.verify_generation(root, expected_generation=GENERATION)
    manifest = json.loads((root / "package-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("generation") != GENERATION or manifest.get("parent_generation") != PARENT_GENERATION:
        raise ValueError("REC-012 generation lineage is invalid")
    absolute = rec011.rec010.rec009.rec008._manifest_absolute_paths(manifest)
    if absolute:
        raise ValueError(f"package manifest contains absolute paths: {absolute[:3]}")
    capture = manifest.get("source_capture", {})
    commerce = manifest.get("commerce_import", {})
    if capture.get("readiness") != READINESS:
        raise ValueError("REC-012 source-capture readiness metadata is invalid")
    required = [
        capture.get("ecwid_tool"), capture.get("ecwid_contract"),
        capture.get("ecwid_binary_tool"), capture.get("ecwid_binary_contract"),
        capture.get("opencart_tool"), capture.get("opencart_runbook"),
        commerce.get("tool"), commerce.get("importer"), commerce.get("payload_contract"),
    ]
    for relative in required:
        if not relative or not (root / relative).is_file():
            raise ValueError(f"REC-012 packaged dependency is missing: {relative}")
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        metadata = dict(connection.execute("SELECT key,value FROM recovery_metadata"))
        counts = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in rec011.rec010.rec009.rec008.EMPTY_IMPORT_TABLES
        }
        import_sources = connection.execute(
            "SELECT COUNT(*) FROM source_manifest WHERE source_ref LIKE 'import:%'"
        ).fetchone()[0]
    finally:
        connection.close()
    if metadata.get("generation") != GENERATION or metadata.get("parent_generation") != PARENT_GENERATION:
        raise ValueError("REC-012 database lineage metadata is invalid")
    if metadata.get("source_capture_readiness") != READINESS:
        raise ValueError("REC-012 database source-capture readiness is invalid")
    if require_empty and (sum(counts.values()) or import_sources):
        raise ValueError("fresh REC-012 contains source-backed commerce/import rows")
    return {
        "valid": True,
        "generation": GENERATION,
        "parent_generation": PARENT_GENERATION,
        "readiness": READINESS,
        "normalized_rows": sum(counts.values()),
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
        report = verify_generation(args.root)
    else:
        report = stage_and_import_bundle(args.root, args.manifest, args.schema)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
