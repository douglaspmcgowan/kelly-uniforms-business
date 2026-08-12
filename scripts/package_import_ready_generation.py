#!/usr/bin/env python3
"""Build and operate the self-contained REC-008 commerce-import generation."""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from typing import NamedTuple

import capture_missing_media
import extend_import_schema
import finalize_public_assets
import import_commerce_bundle
import recovery_package
import upgrade_commerce_schema
import validate_import_bundle


GENERATION = "REC-008"
PARENT_GENERATION = "REC-007"
READINESS = "ready-awaiting-authenticated-exports"
MEDIA_INVENTORY = Path("public-site/media-inventory.json")
ADDDTHIS_EVIDENCE = Path("public-evidence/addthis-service-disposition.json")


class PackagedAsset(NamedTuple):
    source: Path
    destination: str
    artifact_type: str
    replace_existing: bool = False


EMPTY_IMPORT_TABLES = tuple(
    sorted(
        set(upgrade_commerce_schema.REQUIRED_TABLES)
        | set(extend_import_schema.NORMALIZED_DEFINITIONS)
        | {"import_runs", "record_lineage"}
    )
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def default_assets() -> list[PackagedAsset]:
    project = Path(__file__).resolve().parents[1]
    scripts = project / "scripts"
    return [
        PackagedAsset(scripts / name, f"tools/{name}", "recovery-tool", True)
        for name in (
            "package_import_ready_generation.py",
            "extend_import_schema.py",
            "import_commerce_bundle.py",
            "validate_import_bundle.py",
            "recovery_package.py",
            "upgrade_commerce_schema.py",
            "capture_public_runtime.py",
            "capture_missing_media.py",
            "finalize_public_assets.py",
        )
    ] + [
        PackagedAsset(
            project / "schemas/commerce-import-bundle-v1.schema.json",
            "schemas/commerce-import-bundle-v1.schema.json",
            "import-schema",
        ),
        PackagedAsset(
            project / "docs/recovery/opencart-ecwid-import-reconcile-contract.md",
            "docs/recovery/opencart-ecwid-import-reconcile-contract.md",
            "import-contract",
        ),
        PackagedAsset(
            project / "docs/recovery/commerce-normalization-payload-v1.md",
            "docs/recovery/commerce-normalization-payload-v1.md",
            "import-contract",
        ),
    ]


def _is_absolute_path(value: str) -> bool:
    return Path(value).is_absolute() or PureWindowsPath(value).is_absolute()


def _remove_legacy_absolute_paths(value: object) -> object:
    if isinstance(value, list):
        return [_remove_legacy_absolute_paths(item) for item in value]
    if not isinstance(value, dict):
        return value
    cleaned = {}
    for key, child in value.items():
        if key == "path" and isinstance(child, str) and _is_absolute_path(child):
            continue
        cleaned[key] = _remove_legacy_absolute_paths(child)
    return cleaned


def _manifest_absolute_paths(value: object, locator: str = "manifest") -> list[str]:
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            found.extend(_manifest_absolute_paths(child, f"{locator}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_manifest_absolute_paths(child, f"{locator}[{index}]"))
    elif isinstance(value, str) and _is_absolute_path(value):
        found.append(locator)
    return found


def _copy_packaged_assets(root: Path, assets: list[PackagedAsset], captured_at: str) -> None:
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        connection.execute("BEGIN IMMEDIATE")
        for asset in assets:
            source = Path(asset.source).resolve()
            if not source.is_file():
                raise ValueError(f"required REC-008 source asset is missing: {source.name}")
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
            values = (
                captured_at,
                digest,
                size,
                "captured",
                f"REC-008 packaged {asset.artifact_type}: {relative.name}",
                relative.as_posix(),
            )
            updated = connection.execute(
                """UPDATE source_manifest SET captured_at=?,sha256=?,bytes=?,status=?,notes=?
                   WHERE source_path=?""",
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
                        asset.artifact_type,
                        relative.as_posix(),
                        captured_at,
                        digest,
                        size,
                        "captured",
                        f"REC-008 packaged {asset.artifact_type}: {relative.name}",
                        f"rec008:{asset.artifact_type}:{relative.as_posix()}",
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


def stage_import_readiness(
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
    schema_report = extend_import_schema.apply_schema(database)
    _copy_packaged_assets(root, assets, now)
    connection = sqlite3.connect(database)
    try:
        connection.executemany(
            "INSERT INTO recovery_metadata(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            {
                "generation": GENERATION,
                "parent_generation": PARENT_GENERATION,
                "commerce_import_schema_version": extend_import_schema.IMPORT_SCHEMA_VERSION,
                "commerce_import_readiness": READINESS,
            }.items(),
        )
        connection.commit()
        populated = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in EMPTY_IMPORT_TABLES
        }
    finally:
        connection.close()
    if sum(populated.values()):
        raise ValueError("REC-008 source generation contains commerce/import rows")
    manifest = _remove_legacy_absolute_paths(
        json.loads(manifest_path.read_text(encoding="utf-8"))
    )
    manifest["generation"] = GENERATION
    manifest["parent_generation"] = PARENT_GENERATION
    manifest["generated_at"] = now
    manifest["commerce_import"] = {
        "schema_version": extend_import_schema.IMPORT_SCHEMA_VERSION,
        "readiness": READINESS,
        "population_status": "empty-awaiting-authenticated-exports",
        "source_priority": ["opencart", "ecwid"],
        "tool": "tools/package_import_ready_generation.py",
        "bundle_schema": "schemas/commerce-import-bundle-v1.schema.json",
        "contracts": [
            "docs/recovery/opencart-ecwid-import-reconcile-contract.md",
            "docs/recovery/commerce-normalization-payload-v1.md",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    return {
        "generation": GENERATION,
        "schema_version": schema_report["schema_version"],
        "packaged_assets": len(assets),
        "commerce_rows": sum(populated.values()),
    }


def _copy_validated_bundle(manifest_path: Path, destination: Path, schema_path: Path) -> Path:
    validation = validate_import_bundle.validate_bundle(manifest_path, schema_path)
    bundle = json.loads(manifest_path.read_text(encoding="utf-8"))
    final = destination / validation["run_id"]
    if final.exists():
        staged_manifest = final / "export-manifest.json"
        validate_import_bundle.validate_bundle(staged_manifest, schema_path)
        if recovery_package.sha256_file(staged_manifest) != recovery_package.sha256_file(manifest_path):
            raise ValueError("staged run already exists with different manifest bytes")
        return staged_manifest
    temporary = destination / f".{validation['run_id']}.building-{uuid.uuid4().hex}"
    temporary.mkdir(parents=True, exist_ok=False)
    try:
        shutil.copy2(manifest_path, temporary / "export-manifest.json")
        for artifact in bundle["artifacts"]:
            source = manifest_path.parent / artifact["relative_path"]
            target = temporary / artifact["relative_path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        staged_manifest = temporary / "export-manifest.json"
        validate_import_bundle.validate_bundle(staged_manifest, schema_path)
        final.parent.mkdir(parents=True, exist_ok=True)
        temporary.rename(final)
        return final / "export-manifest.json"
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def stage_and_import_bundle(root: Path, manifest_path: Path, schema_path: Path | None = None) -> dict:
    root = Path(root).resolve()
    schema = Path(schema_path or root / "schemas/commerce-import-bundle-v1.schema.json").resolve()
    staged_manifest = _copy_validated_bundle(
        Path(manifest_path).resolve(), root / "raw/private-exports", schema
    )
    manifest_file = root / "package-manifest.json"
    try:
        report = import_commerce_bundle.import_bundle(
            root / recovery_package.DATABASE_FILE, staged_manifest, schema
        )
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        if "commerce_import" in manifest:
            manifest["commerce_import"]["population_status"] = "source-backed-imports-present"
            manifest_file.write_text(
                json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
            )
        return report
    finally:
        recovery_package.write_checksums(root)


def create_generation(source: Path, destination: Path) -> dict:
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    if not source.is_dir():
        raise ValueError(f"source generation does not exist: {source}")
    if destination.exists():
        raise ValueError(f"destination already exists; recovery generations are immutable: {destination}")
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("source and destination generations must be distinct, non-nested paths")
    source_manifest = json.loads((source / "package-manifest.json").read_text(encoding="utf-8"))
    if source_manifest.get("generation") != PARENT_GENERATION:
        raise ValueError(f"source generation must be {PARENT_GENERATION}")
    finalize_public_assets.verify_generation(source)
    temporary = destination.with_name(f".{destination.name}.building-{uuid.uuid4().hex}")
    try:
        shutil.copytree(source, temporary)
        stage_import_readiness(temporary, default_assets())
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
        raise ValueError("REC-008 generation lineage is invalid")
    absolute = _manifest_absolute_paths(manifest)
    if absolute:
        raise ValueError(f"package manifest contains absolute paths: {absolute[:3]}")
    commerce = manifest.get("commerce_import", {})
    if commerce.get("schema_version") != extend_import_schema.IMPORT_SCHEMA_VERSION:
        raise ValueError("REC-008 import schema metadata is invalid")
    for relative in [commerce.get("tool"), commerce.get("bundle_schema"), *commerce.get("contracts", [])]:
        if not relative or not (root / relative).is_file():
            raise ValueError(f"REC-008 packaged import dependency is missing: {relative}")
    media = json.loads((root / MEDIA_INVENTORY).read_text(encoding="utf-8"))
    statuses = {}
    for asset in media["assets"]:
        status = asset.get("download_status")
        statuses[status] = statuses.get(status, 0) + 1
        path = root / asset["downloaded_path"]
        if not path.is_file() or recovery_package.sha256_file(path) != asset["sha256"]:
            raise ValueError(f"public media lineage mismatch: {asset.get('downloaded_path')}")
        if asset.get("bytes") is not None and path.stat().st_size != int(asset["bytes"]):
            raise ValueError(f"public media byte count mismatch: {asset.get('downloaded_path')}")
    expected_statuses = {"downloaded": 1111, "downloaded-direct-rec006": 430, "embedded-extracted-rec007": 1}
    if statuses != expected_statuses:
        raise ValueError(f"public media status counts drifted: {statuses}")
    disposition = json.loads((root / ADDDTHIS_EVIDENCE).read_text(encoding="utf-8"))
    if disposition.get("status") != "retired-external-dependency-no-current-binary":
        raise ValueError("AddThis retirement disposition is missing")
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        tables = {
            row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        missing = set(EMPTY_IMPORT_TABLES) - tables
        if missing:
            raise ValueError(f"REC-008 import tables are missing: {sorted(missing)}")
        option_columns = {row[1] for row in connection.execute("PRAGMA table_info(catalog_option_values)")}
        missing_columns = set(extend_import_schema.OPTION_VALUE_COLUMNS) - option_columns
        if missing_columns:
            raise ValueError(f"REC-008 option columns are missing: {sorted(missing_columns)}")
        metadata = dict(connection.execute("SELECT key,value FROM recovery_metadata"))
        if metadata.get("commerce_import_schema_version") != extend_import_schema.IMPORT_SCHEMA_VERSION:
            raise ValueError("REC-008 database import schema metadata is invalid")
        counts = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in EMPTY_IMPORT_TABLES
        }
        media_rows = connection.execute("SELECT COUNT(*) FROM media_assets").fetchone()[0]
        import_sources = connection.execute(
            "SELECT COUNT(*) FROM source_manifest WHERE source_ref LIKE 'import:%'"
        ).fetchone()[0]
    finally:
        connection.close()
    if media_rows != 1542:
        raise ValueError(f"public media database count drifted: {media_rows}")
    if require_empty and (sum(counts.values()) or import_sources):
        raise ValueError("fresh REC-008 contains source-backed commerce/import rows")
    return {
        "valid": True,
        "generation": GENERATION,
        "parent_generation": PARENT_GENERATION,
        "public_media_exact": sum(statuses.values()),
        "commerce_tables": len(upgrade_commerce_schema.REQUIRED_TABLES),
        "import_schema_version": extend_import_schema.IMPORT_SCHEMA_VERSION,
        "normalized_rows": sum(counts[table] for table in upgrade_commerce_schema.REQUIRED_TABLES),
        "import_runs": counts["import_runs"],
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
