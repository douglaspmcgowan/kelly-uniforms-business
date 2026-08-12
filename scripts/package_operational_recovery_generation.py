#!/usr/bin/env python3
"""Build REC-014 and prove its package-local recovery drill before promotion."""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath

import capture_missing_media
import package_drill_ready_generation as rec013
import recovery_package
import run_recovery_drill_v2


GENERATION = "REC-014"
PARENT_GENERATION = "REC-013"
READINESS = "operational-recovery-self-test-proven-awaiting-authenticated-exports"
PackagedAsset = rec013.PackagedAsset


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def default_assets() -> list[PackagedAsset]:
    project = Path(__file__).resolve().parents[1]
    return [
        PackagedAsset(
            project / "scripts/package_operational_recovery_generation.py",
            "tools/package_operational_recovery_generation.py",
            "recovery-tool",
        ),
        PackagedAsset(
            project / "scripts/run_recovery_drill_v2.py",
            "tools/run_recovery_drill_v2.py",
            "recovery-tool",
        ),
        PackagedAsset(
            project / "docs/recovery/representative-restore-drill-v2.md",
            "docs/recovery/representative-restore-drill-v2.md",
            "recovery-contract",
        ),
        PackagedAsset(
            project / "docs/recovery/operational-recovery-package-v1.md",
            "docs/recovery/operational-recovery-package-v1.md",
            "recovery-contract",
        ),
    ]


def _copy_assets(root: Path, assets: list[PackagedAsset], captured_at: str) -> None:
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        connection.execute("BEGIN IMMEDIATE")
        for asset in assets:
            source = Path(asset.source).resolve()
            if not source.is_file():
                raise ValueError(f"required REC-014 source asset is missing: {source.name}")
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
                    f"REC-014 packaged {asset.artifact_type}: {relative.name}",
                    f"rec014:{asset.artifact_type}:{relative.as_posix()}",
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
    drill_state = "PROVEN" if proven else "READY"
    detail = (
        "The package-local v2 drill completed against the REC-014 build before promotion; "
        "22 normalized and 22 lineage rows were verified in a disposable copy and the authority remained unchanged."
        if proven
        else "The generation-aware v2 drill is packaged and awaiting the mandatory pre-promotion self-test."
    )
    return f"""# M&T Uniforms REC-014 recovery status

Generated: {captured_at}

REC-014 is the corrected operational recovery successor. REC-013 is preserved as a failed drill checkpoint and is not current.

## Proven offline recovery

- Public storefront: 528 reachable safe pages with zero queued uncaptured URLs.
- Public media: 1,542 / 1,542 exact referenced binaries.
- Runtime: 34 / 35 references captured; the sole AddThis reference is retired and dispositioned.
- Journal: exact supplemental theme/settings SQL export preserved and hashed.
- Package checksums, SQLite integrity, foreign keys, source paths, and lineage verify.
- Work Scope is enrolled with legacy task/history snapshots preserved.
- Value-free continuity inventory covers 10 services with unknown control fields explicit.
- Package-local v2 drill: {drill_state}. {detail}
- Clover authenticated export is excluded by DEC-005.

## Awaiting source access

- Full OpenCart database, webroot, storage, configuration, private media, versions, and logs.
- Complete Ecwid catalog, customers, orders, configuration, adjunct resources, media, and downloadable files.
- Primary registrar/DNS/hosting/mail/payment/shipping/subscription/licence owner, payer, renewal, and recovery evidence.
- Approved encrypted offline and independent offsite custody.

Fresh private commerce and import rows in this authority remain zero.
"""


def _audit(captured_at: str, proven: bool) -> str:
    drill = "PROVEN" if proven else "READY-AWAITING-SELF-TEST"
    return f"""# Recovery objective completion audit

Generated: {captured_at}

- OpenCart native acquisition: TOOL-READY; authenticated database/webroot/storage/configuration bytes MISSING-SOURCE.
- Journal supplemental export: PROVEN.
- Ecwid JSON and binary acquisition: TOOL-READY; authenticated source bytes MISSING-SOURCE.
- Clover authenticated export: EXCLUDED-BY-DECISION under DEC-005.
- Reachable public storefront graph: PROVEN at 528 pages.
- Exact referenced public media: PROVEN at 1,542 / 1,542.
- Portable database/checksums/provenance/import staging: PROVEN.
- Representative agency-order reconstruction: PROVEN against REC-012.
- Generation-aware package-local REC-014 drill: {drill}.
- Value-free service/account continuity inventory: PROVEN for 10 services; primary account control MISSING-SOURCE.
- Work Scope enrollment and legacy history preservation: PROVEN.
- Encrypted offline and independent offsite custody: MISSING-SOURCE pending approved recipient/key and destination.

The full objective remains incomplete until authenticated OpenCart/Ecwid source bytes, primary account-control evidence, and approved encrypted offsite custody are obtained and reconciled. No private client records are invented to satisfy those gaps.
"""


def _upsert_generated_file(root: Path, relative: str, captured_at: str) -> None:
    path = root / relative
    values = (
        captured_at,
        recovery_package.sha256_file(path),
        path.stat().st_size,
        f"REC-014 generated current status: {relative}",
        f"rec014:generated:{relative}",
        relative,
    )
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
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
                    f"REC-014 generated current status: {relative}",
                    f"rec014:generated:{relative}",
                    "deterministic-render",
                    0,
                    "internal",
                    "complete-file",
                ),
            )
        connection.commit()
    finally:
        connection.close()


def _write_current_docs(root: Path, captured_at: str, proven: bool) -> None:
    (root / "RECOVERY-STATUS.md").write_text(
        _status(captured_at, proven), encoding="utf-8", newline="\n"
    )
    (root / "COMPLETION-AUDIT.md").write_text(
        _audit(captured_at, proven), encoding="utf-8", newline="\n"
    )
    _upsert_generated_file(root, "RECOVERY-STATUS.md", captured_at)
    _upsert_generated_file(root, "COMPLETION-AUDIT.md", captured_at)


def stage_operational_readiness(
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
    _copy_assets(root, assets, now)
    connection = sqlite3.connect(database)
    try:
        connection.executemany(
            "INSERT INTO recovery_metadata(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            {
                "generation": GENERATION,
                "parent_generation": PARENT_GENERATION,
                "recovery_readiness": "operational-recovery-self-test-pending",
                "representative_restore_drill": "ready-awaiting-self-test",
            }.items(),
        )
        connection.commit()
    finally:
        connection.close()
    manifest = rec013.rec012.rec011.rec010.rec009.rec008._remove_legacy_absolute_paths(manifest)
    manifest["generation"] = GENERATION
    manifest["parent_generation"] = PARENT_GENERATION
    manifest["generated_at"] = now
    manifest["recovery_readiness"] = "operational-recovery-self-test-pending"
    manifest["restore_drill"] = {
        "status": "ready-awaiting-self-test",
        "tool": "tools/run_recovery_drill_v2.py",
        "contract": "docs/recovery/representative-restore-drill-v2.md",
        "authority_population_effect": "none",
        "self_test": None,
    }
    manifest.setdefault("commerce_import", {})["tool"] = (
        "tools/package_operational_recovery_generation.py"
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    _write_current_docs(root, now, proven=False)
    return {
        "generation": GENERATION,
        "parent_generation": PARENT_GENERATION,
        "readiness": "operational-recovery-self-test-pending",
        "packaged_assets": len(assets),
    }


def mark_drill_proven(
    root: Path, drill_report: dict, captured_at: str | None = None
) -> dict:
    valid = (
        drill_report.get("valid") is True
        and drill_report.get("authority_unchanged") is True
        and drill_report.get("import", {}).get("status") == "reconciled"
        and drill_report.get("reconstruction", {}).get("valid") is True
        and drill_report.get("reconstruction", {}).get("foreign_key_errors") == 0
        and drill_report.get("reconstruction", {}).get("lineage_rows") == 22
    )
    if not valid:
        raise ValueError("REC-014 proof requires a successful package-local drill with unchanged authority")
    root = Path(root).resolve()
    now = captured_at or utc_now()
    manifest_path = root / "package-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("generation") != GENERATION:
        raise ValueError("drill proof can only be recorded on REC-014")
    manifest["generated_at"] = now
    manifest["recovery_readiness"] = READINESS
    manifest["restore_drill"]["status"] = "proven-package-local-disposable-copy"
    manifest["restore_drill"]["self_test"] = {
        "drill_version": drill_report.get("drill_version"),
        "authority_unchanged": True,
        "normalized_rows": drill_report["import"].get("normalized_rows"),
        "lineage_rows": drill_report["reconstruction"].get("lineage_rows"),
        "foreign_key_errors": 0,
        "classification": drill_report.get("classification"),
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
                "representative_restore_drill": "proven-package-local-disposable-copy",
            }.items(),
        )
        connection.commit()
    finally:
        connection.close()
    _write_current_docs(root, now, proven=True)
    return manifest["restore_drill"]["self_test"]


def stage_and_import_bundle(root: Path, manifest_path: Path, schema_path: Path | None = None) -> dict:
    return rec013.stage_and_import_bundle(root, manifest_path, schema_path)


def create_generation(source: Path, destination: Path) -> dict:
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    if not source.is_dir():
        raise ValueError(f"source generation does not exist: {source}")
    if destination.exists():
        raise ValueError(f"destination already exists; recovery generations are immutable: {destination}")
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("source and destination generations must be distinct, non-nested paths")
    rec013.verify_generation(source, require_empty=True)
    temporary = destination.with_name(f".{destination.name}.building-{uuid.uuid4().hex}")
    drill_output = destination.with_name(f".{destination.name}.self-test-{uuid.uuid4().hex}")
    try:
        shutil.copytree(source, temporary)
        stage_operational_readiness(temporary, default_assets())
        recovery_package.write_checksums(temporary)
        verify_generation(temporary, require_empty=True, require_drill_proof=False)
        drill_report = run_recovery_drill_v2.run_drill(temporary, drill_output)
        mark_drill_proven(temporary, drill_report)
        recovery_package.write_checksums(temporary)
        report = verify_generation(temporary, require_empty=True, require_drill_proof=True)
        temporary.rename(destination)
        return report
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    finally:
        shutil.rmtree(drill_output, ignore_errors=True)


def verify_generation(
    root: Path, require_empty: bool = False, require_drill_proof: bool = False
) -> dict:
    root = Path(root).resolve()
    package = capture_missing_media.verify_generation(root, expected_generation=GENERATION)
    manifest = json.loads((root / "package-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("generation") != GENERATION or manifest.get("parent_generation") != PARENT_GENERATION:
        raise ValueError("REC-014 generation lineage is invalid")
    absolute = rec013.rec012.rec011.rec010.rec009.rec008._manifest_absolute_paths(manifest)
    if absolute:
        raise ValueError(f"package manifest contains absolute paths: {absolute[:3]}")
    drill = manifest.get("restore_drill", {})
    required = [
        drill.get("tool"),
        drill.get("contract"),
        manifest.get("commerce_import", {}).get("tool"),
        "docs/recovery/operational-recovery-package-v1.md",
        rec013.INVENTORY_PATH,
        "RECOVERY-STATUS.md",
        "COMPLETION-AUDIT.md",
    ]
    for relative in required:
        if not relative or not (root / relative).is_file():
            raise ValueError(f"REC-014 packaged dependency is missing: {relative}")
    inventory = rec013.validate_service_inventory(root / rec013.INVENTORY_PATH)
    if inventory["services"] != 10:
        raise ValueError("REC-014 service continuity inventory is incomplete")
    status = (root / "RECOVERY-STATUS.md").read_text(encoding="utf-8")
    audit = (root / "COMPLETION-AUDIT.md").read_text(encoding="utf-8")
    if "# M&T Uniforms REC-014 recovery status" not in status or "1,542 / 1,542" not in status:
        raise ValueError("REC-014 recovery status is incomplete")
    if require_drill_proof:
        if drill.get("status") != "proven-package-local-disposable-copy":
            raise ValueError("REC-014 package-local drill proof is missing")
        self_test = drill.get("self_test") or {}
        if not self_test.get("authority_unchanged") or self_test.get("lineage_rows") != 22:
            raise ValueError("REC-014 package-local drill proof is invalid")
        if "Package-local v2 drill: PROVEN" not in status or "REC-014 drill: PROVEN" not in audit:
            raise ValueError("REC-014 current documents do not record drill proof")
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        metadata = dict(connection.execute("SELECT key,value FROM recovery_metadata"))
        counts = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in rec013.rec012.rec011.rec010.rec009.rec008.EMPTY_IMPORT_TABLES
        }
        import_sources = connection.execute(
            "SELECT COUNT(*) FROM source_manifest WHERE source_ref LIKE 'import:%'"
        ).fetchone()[0]
    finally:
        connection.close()
    if metadata.get("generation") != GENERATION or metadata.get("parent_generation") != PARENT_GENERATION:
        raise ValueError("REC-014 database lineage metadata is invalid")
    if require_drill_proof and metadata.get("recovery_readiness") != READINESS:
        raise ValueError("REC-014 database drill proof metadata is invalid")
    if require_empty and (sum(counts.values()) or import_sources):
        raise ValueError("fresh REC-014 contains source-backed commerce/import rows")
    return {
        "valid": True,
        "generation": GENERATION,
        "parent_generation": PARENT_GENERATION,
        "readiness": manifest.get("recovery_readiness"),
        "drill_status": drill.get("status"),
        "normalized_rows": sum(counts.values()),
        "inventory_services": inventory["services"],
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
