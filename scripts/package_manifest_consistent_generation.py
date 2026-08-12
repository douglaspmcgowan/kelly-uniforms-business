#!/usr/bin/env python3
"""Build and verify the immutable REC-016 manifest-consistency successor."""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import tarfile
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath

import capture_missing_media
import package_clean_recovery_generation as rec015
import recovery_package
import run_recovery_drill_v3


GENERATION = "REC-016"
PARENT_GENERATION = "REC-015"
READINESS = (
    "manifest-consistent-cache-free-operational-recovery-self-test-proven-"
    "awaiting-authenticated-exports"
)
MEDIA_STATUS_COUNTS = {
    "downloaded": 1111,
    "downloaded-direct-rec006": 430,
    "embedded-extracted-rec007": 1,
}
MEDIA_TOTAL = sum(MEDIA_STATUS_COUNTS.values())
PackagedAsset = rec015.PackagedAsset


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def authority_hashes(root: Path) -> dict[str, str]:
    root = Path(root).resolve()
    return {
        path.relative_to(root).as_posix(): recovery_package.sha256_file(path)
        for path in sorted(
            (candidate for candidate in root.rglob("*") if candidate.is_file()),
            key=lambda candidate: candidate.relative_to(root).as_posix(),
        )
    }


def default_assets() -> list[PackagedAsset]:
    project = Path(__file__).resolve().parents[1]
    return [
        PackagedAsset(
            project / "scripts/package_manifest_consistent_generation.py",
            "tools/package_manifest_consistent_generation.py",
            "recovery-tool",
        )
    ]


def _portable_relative(value: str) -> Path:
    posix = PurePosixPath(value)
    if posix.is_absolute() or PureWindowsPath(value).is_absolute() or ".." in posix.parts:
        raise ValueError(f"packaged destination is not portable: {value}")
    return Path(*posix.parts)


def _copy_assets(root: Path, assets: list[PackagedAsset], captured_at: str) -> None:
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        connection.execute("BEGIN IMMEDIATE")
        for asset in assets:
            source = Path(asset.source).resolve()
            if not source.is_file():
                raise ValueError(f"required REC-016 source asset is missing: {source.name}")
            relative = _portable_relative(asset.destination)
            destination = root / relative
            if destination.exists() and not asset.replace_existing:
                raise ValueError(f"packaged asset already exists: {asset.destination}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            portable = relative.as_posix()
            connection.execute(
                """INSERT INTO source_manifest(
                    system,artifact_type,source_path,captured_at,sha256,bytes,status,notes,
                    source_ref,capture_method,record_count,sensitivity,completeness
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    "recovery-tooling",
                    asset.artifact_type,
                    portable,
                    captured_at,
                    recovery_package.sha256_file(destination),
                    destination.stat().st_size,
                    "captured",
                    f"REC-016 packaged {asset.artifact_type}: {relative.name}",
                    f"rec016:{asset.artifact_type}:{portable}",
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


def _media_status_counts(root: Path) -> dict[str, int]:
    inventory = json.loads(
        (root / rec015.rec014.rec013.rec012.rec011.rec010.rec009.rec008.MEDIA_INVENTORY)
        .read_text(encoding="utf-8")
    )
    counts: dict[str, int] = {}
    for asset in inventory["assets"]:
        status = asset.get("download_status")
        counts[status] = counts.get(status, 0) + 1
    if counts != MEDIA_STATUS_COUNTS:
        raise ValueError(f"public media status counts drifted: {counts}")
    return counts


def reconcile_manifest(
    manifest: dict, captured_at: str, media_status_counts: dict[str, int]
) -> dict:
    if manifest.get("generation") != PARENT_GENERATION:
        raise ValueError(f"source generation must be {PARENT_GENERATION}")
    public_media = manifest.get("public_media") or {}
    completion = manifest.get("public_media_completion") or {}
    if public_media.get("unique_image_urls") != MEDIA_TOTAL:
        raise ValueError("REC-015 unique public-media count is not 1,542")
    if completion.get("total_exact") != MEDIA_TOTAL:
        raise ValueError("REC-015 exact public-media completion proof is not 1,542")
    if media_status_counts != MEDIA_STATUS_COUNTS:
        raise ValueError("REC-015 media status proof does not reconcile to 1,542")
    inventory = manifest.get("service_account_inventory") or {}
    if inventory.get("services") != 10 or inventory.get("contains_secrets") is not False:
        raise ValueError("REC-015 value-free service/account inventory proof is invalid")

    reconciled = json.loads(json.dumps(manifest))
    reconciled["generation"] = GENERATION
    reconciled["parent_generation"] = PARENT_GENERATION
    reconciled["generated_at"] = captured_at
    reconciled["recovery_readiness"] = "manifest-consistency-self-test-pending"
    reconciled["public_media"] = {
        "status": "exact-binary-mirror-complete",
        "unique_image_urls": MEDIA_TOTAL,
        "total_occurrences": public_media.get("total_occurrences"),
        "exact_binaries": MEDIA_TOTAL,
        "exact_binary_coverage_percent": 100.0,
        "capture_status_counts": dict(media_status_counts),
        "unresolved_referenced_urls": 0,
        "public_render_sweep_status": public_media.get("public_render_sweep_status"),
        "json": public_media.get("json"),
        "csv": public_media.get("csv"),
        "alternate_json": public_media.get("alternate_json"),
        "binaries": public_media.get("binaries"),
    }
    missing = [
        item
        for item in reconciled.get("missing_required", [])
        if item != "domain/DNS/hosting/email/payment/shipping ownership inventory"
    ]
    account_evidence = (
        "primary account-control evidence for domain/DNS/hosting/email/payment/"
        "shipping services"
    )
    if account_evidence not in missing:
        missing.append(account_evidence)
    reconciled["missing_required"] = missing
    reconciled["manifest_consistency"] = {
        "status": "reconciled-from-package-evidence",
        "public_media_claim": "1542-of-1542-exact",
        "service_inventory_claim": "present-value-free-primary-control-unverified",
        "private_source_claim": "not-captured",
    }
    reconciled["restore_drill"] = {
        "status": "ready-awaiting-self-test",
        "tool": "tools/run_recovery_drill_v3.py",
        "contract": "docs/recovery/representative-restore-drill-v3.md",
        "authority_population_effect": "none",
        "self_test": None,
    }
    reconciled.setdefault("commerce_import", {})["tool"] = (
        "tools/package_manifest_consistent_generation.py"
    )
    return reconciled


def _status(captured_at: str, proven: bool) -> str:
    drill = "PROVEN" if proven else "READY"
    detail = (
        "The package-local v3 drill passed with 22 normalized and 22 lineage rows, "
        "zero foreign-key errors, unchanged authority hashes, and zero Python cache artifacts."
        if proven
        else "The package-local v3 drill is packaged and awaiting mandatory pre-promotion execution."
    )
    return f"""# M&T Uniforms REC-016 recovery status

Generated: {captured_at}

REC-016 is the current manifest-consistent operational recovery successor. REC-015 remains preserved and unchanged.

- Public storefront: 528 reachable safe pages; zero queued uncaptured URLs.
- Public media: 1,542 / 1,542 exact referenced binaries (100% exact coverage).
- Runtime: 34 / 35 references captured; retired AddThis is dispositioned.
- Journal supplemental theme/settings export: preserved and hashed.
- Checksums, SQLite integrity, foreign keys, relative provenance, and full physical-file reconciliation: verified.
- Work Scope enrollment and legacy history preservation: verified.
- Value-free service/account inventory: 10 services; primary control evidence remains unverified.
- Package-local v3 drill: {drill}. {detail}
- Python cache artifacts in authority: 0.
- Fresh private commerce/import rows: 0.
- Clover authenticated export is excluded by DEC-005.

Still awaiting authenticated OpenCart/Ecwid source bytes, primary account-control evidence, and approved encrypted offline/offsite custody.
"""


def _audit(captured_at: str, proven: bool) -> str:
    drill = "PROVEN" if proven else "READY-AWAITING-SELF-TEST"
    return f"""# Recovery objective completion audit

Generated: {captured_at}

- OpenCart full native source: TOOL-READY, MISSING-SOURCE.
- Journal supplement: PROVEN.
- Ecwid complete JSON/binary source: TOOL-READY, MISSING-SOURCE.
- Clover authentication: EXCLUDED-BY-DECISION under DEC-005.
- Public storefront/media/runtime/business infrastructure: PROVEN for the reachable safe graph, including 1,542 / 1,542 exact media binaries.
- Portable database, checksums, provenance, staged importer, and representative reconstruction: PROVEN.
- Cache-free package-local REC-016 drill: {drill}.
- Service/account continuity inventory: PROVEN and value-free; primary control evidence MISSING-SOURCE.
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
            f"REC-016 generated current status: {relative}",
            f"rec016:generated:{relative}",
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
                    f"REC-016 generated current status: {relative}",
                    f"rec016:generated:{relative}",
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


def stage_consistency_readiness(
    root: Path, assets: list[PackagedAsset], captured_at: str | None = None
) -> dict:
    root = Path(root).resolve()
    now = captured_at or utc_now()
    manifest_path = root / "package-manifest.json"
    database = root / recovery_package.DATABASE_FILE
    if not manifest_path.is_file() or not database.is_file():
        raise ValueError("recovery database and package manifest are required")
    counts = _media_status_counts(root)
    manifest = reconcile_manifest(
        json.loads(manifest_path.read_text(encoding="utf-8")), now, counts
    )
    _copy_assets(root, assets, now)
    connection = sqlite3.connect(database)
    try:
        connection.executemany(
            "INSERT INTO recovery_metadata(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            {
                "generation": GENERATION,
                "parent_generation": PARENT_GENERATION,
                "recovery_readiness": "manifest-consistency-self-test-pending",
                "representative_restore_drill": "ready-awaiting-cache-free-self-test",
                "manifest_consistency": "public-media-and-account-inventory-reconciled",
                "python_cache_artifacts": "0",
            }.items(),
        )
        connection.commit()
    finally:
        connection.close()
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    _write_docs(root, now, proven=False)
    return {
        "generation": GENERATION,
        "parent_generation": PARENT_GENERATION,
        "readiness": "manifest-consistency-self-test-pending",
        "public_media_exact": MEDIA_TOTAL,
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
        raise ValueError("REC-016 proof requires a successful cache-free package-local drill")
    root = Path(root).resolve()
    run_recovery_drill_v3.assert_no_cache_artifacts(root)
    now = captured_at or utc_now()
    manifest_path = root / "package-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("generation") != GENERATION:
        raise ValueError("drill proof can only be recorded on REC-016")
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
                "manifest_consistency": "public-media-and-account-inventory-reconciled",
                "python_cache_artifacts": "0",
            }.items(),
        )
        connection.commit()
    finally:
        connection.close()
    _write_docs(root, now, proven=True)
    return manifest["restore_drill"]["self_test"]


def stage_and_import_bundle(
    root: Path, manifest_path: Path, schema_path: Path | None = None
) -> dict:
    return rec015.stage_and_import_bundle(root, manifest_path, schema_path)


def verify_generation(
    root: Path, require_empty: bool = False, require_drill_proof: bool = False
) -> dict:
    root = Path(root).resolve()
    sqlite_sidecars = [
        root / f"{recovery_package.DATABASE_FILE}{suffix}"
        for suffix in ("-wal", "-shm")
        if (root / f"{recovery_package.DATABASE_FILE}{suffix}").exists()
    ]
    if sqlite_sidecars:
        names = ", ".join(path.name for path in sqlite_sidecars)
        raise ValueError(
            f"REC-016 SQLite sidecar files require checkpoint/rebuild before verification: {names}"
        )
    run_recovery_drill_v3.assert_no_cache_artifacts(root)
    package = capture_missing_media.verify_generation(root, expected_generation=GENERATION)
    base = recovery_package.verify_package(root)
    run_recovery_drill_v3.assert_no_cache_artifacts(root)
    physical_files = sum(1 for path in root.rglob("*") if path.is_file())
    if physical_files != base["checksummed_files"] + 1:
        raise ValueError(
            f"REC-016 physical/checksum inventory mismatch: {physical_files} != "
            f"{base['checksummed_files']} + SHA256SUMS"
        )
    manifest = json.loads((root / "package-manifest.json").read_text(encoding="utf-8"))
    if (
        manifest.get("generation") != GENERATION
        or manifest.get("parent_generation") != PARENT_GENERATION
    ):
        raise ValueError("REC-016 generation lineage is invalid")
    if manifest.get("python_cache_artifacts") != 0:
        raise ValueError("REC-016 cache metadata is invalid")
    absolute = rec015.rec014.rec013.rec012.rec011.rec010.rec009.rec008._manifest_absolute_paths(
        manifest
    )
    if absolute:
        raise ValueError(f"package manifest contains absolute paths: {absolute[:3]}")
    media = manifest.get("public_media") or {}
    if (
        media.get("status") != "exact-binary-mirror-complete"
        or media.get("exact_binaries") != MEDIA_TOTAL
        or media.get("exact_binary_coverage_percent") != 100.0
        or media.get("unresolved_referenced_urls") != 0
        or media.get("capture_status_counts") != MEDIA_STATUS_COUNTS
    ):
        raise ValueError("REC-016 public-media manifest claims are not reconciled")
    if "domain/DNS/hosting/email/payment/shipping ownership inventory" in manifest.get(
        "missing_required", []
    ):
        raise ValueError("REC-016 still claims the value-free service inventory is missing")
    account_evidence = (
        "primary account-control evidence for domain/DNS/hosting/email/payment/"
        "shipping services"
    )
    if account_evidence not in manifest.get("missing_required", []):
        raise ValueError("REC-016 does not preserve the missing primary-control boundary")
    if manifest.get("source_capture", {}).get("captured_private_exports") is not False:
        raise ValueError("REC-016 private-source boundary is invalid")
    if manifest.get("manifest_consistency", {}).get("status") != (
        "reconciled-from-package-evidence"
    ):
        raise ValueError("REC-016 consistency evidence is missing")
    drill = manifest.get("restore_drill", {})
    required = [
        drill.get("tool"),
        drill.get("contract"),
        manifest.get("commerce_import", {}).get("tool"),
        "docs/recovery/cache-free-operational-recovery-package-v1.md",
        rec015.rec014.rec013.INVENTORY_PATH,
        "RECOVERY-STATUS.md",
        "COMPLETION-AUDIT.md",
    ]
    for relative in required:
        if not relative or not (root / relative).is_file():
            raise ValueError(f"REC-016 packaged dependency is missing: {relative}")
    inventory = rec015.rec014.rec013.validate_service_inventory(
        root / rec015.rec014.rec013.INVENTORY_PATH
    )
    _media_status_counts(root)
    status = (root / "RECOVERY-STATUS.md").read_text(encoding="utf-8")
    if (
        "# M&T Uniforms REC-016 recovery status" not in status
        or "Public media: 1,542 / 1,542 exact" not in status
        or "Python cache artifacts in authority: 0" not in status
    ):
        raise ValueError("REC-016 recovery status is incomplete")
    if require_drill_proof:
        proof = drill.get("self_test") or {}
        if drill.get("status") != "proven-cache-free-package-local-copy":
            raise ValueError("REC-016 package-local drill proof is missing")
        if proof.get("authority_cache_artifacts") != 0 or proof.get("lineage_rows") != 22:
            raise ValueError("REC-016 package-local drill proof is invalid")
        if "Package-local v3 drill: PROVEN" not in status:
            raise ValueError("REC-016 status does not record package-local drill proof")
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        metadata = dict(connection.execute("SELECT key,value FROM recovery_metadata"))
        counts = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in rec015.rec014.rec013.rec012.rec011.rec010.rec009.rec008.EMPTY_IMPORT_TABLES
        }
        import_sources = connection.execute(
            "SELECT COUNT(*) FROM source_manifest WHERE source_ref LIKE 'import:%'"
        ).fetchone()[0]
    finally:
        connection.close()
    if (
        metadata.get("generation") != GENERATION
        or metadata.get("parent_generation") != PARENT_GENERATION
    ):
        raise ValueError("REC-016 database lineage metadata is invalid")
    if metadata.get("manifest_consistency") != (
        "public-media-and-account-inventory-reconciled"
    ):
        raise ValueError("REC-016 database consistency metadata is invalid")
    if metadata.get("python_cache_artifacts") != "0":
        raise ValueError("REC-016 database cache metadata is invalid")
    if require_empty and (sum(counts.values()) or import_sources):
        raise ValueError("fresh REC-016 contains source-backed commerce/import rows")
    return {
        "valid": True,
        "generation": GENERATION,
        "parent_generation": PARENT_GENERATION,
        "readiness": manifest.get("recovery_readiness"),
        "drill_status": drill.get("status"),
        "normalized_rows": sum(counts.values()),
        "public_media_exact": MEDIA_TOTAL,
        "inventory_services": inventory["services"],
        "python_cache_artifacts": 0,
        "physical_files": physical_files,
        "checksummed_files": base["checksummed_files"],
        "package": package,
    }


def create_generation(source: Path, destination: Path) -> dict:
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    if not source.is_dir():
        raise ValueError(f"source generation does not exist: {source}")
    if destination.exists():
        raise ValueError(
            f"destination already exists; recovery generations are immutable: {destination}"
        )
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("source and destination generations must be distinct, non-nested paths")
    rec015.verify_generation(source, require_empty=True, require_drill_proof=True)
    source_before = authority_hashes(source)
    temporary = destination.with_name(f".{destination.name}.building-{uuid.uuid4().hex}")
    drill_output = destination.with_name(f".{destination.name}.self-test-{uuid.uuid4().hex}")
    try:
        shutil.copytree(source, temporary)
        stage_consistency_readiness(temporary, default_assets())
        recovery_package.write_checksums(temporary)
        verify_generation(temporary, require_empty=True, require_drill_proof=False)
        report = run_recovery_drill_v3.run_drill(temporary, drill_output)
        mark_drill_proven(temporary, report)
        recovery_package.write_checksums(temporary)
        final = verify_generation(temporary, require_empty=True, require_drill_proof=True)
        source_after = authority_hashes(source)
        if source_before != source_after:
            raise ValueError("REC-015 authority changed while building REC-016")
        temporary.rename(destination)
        return {**final, "source_authority_unchanged": True}
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    finally:
        shutil.rmtree(drill_output, ignore_errors=True)


def _safe_extract(archive: Path, destination: Path) -> None:
    destination = Path(destination).resolve()
    with tarfile.open(archive, "r:gz") as handle:
        for member in handle.getmembers():
            relative = PurePosixPath(member.name)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError(f"unsafe archive member: {member.name}")
        handle.extractall(destination, filter="data")


def create_release(
    source: Path,
    destination: Path,
    archive: Path,
    isolated_restore: Path,
) -> dict:
    destination = Path(destination).resolve()
    archive = Path(archive).resolve()
    isolated_restore = Path(isolated_restore).resolve()
    for target, label in (
        (destination, "destination"),
        (archive, "archive"),
        (isolated_restore, "isolated restore"),
    ):
        if target.exists():
            raise ValueError(f"{label} already exists: {target}")
    build_generation = destination.with_name(
        f".{destination.name}.release-building-{uuid.uuid4().hex}"
    )
    archive.parent.mkdir(parents=True, exist_ok=True)
    temporary_archive = archive.with_name(f".{archive.name}.building-{uuid.uuid4().hex}")
    restore_wrapper = isolated_restore.with_name(
        f".{isolated_restore.name}.building-{uuid.uuid4().hex}"
    )
    promoted: list[Path] = []
    try:
        report = create_generation(source, build_generation)
        with tarfile.open(temporary_archive, "w:gz") as handle:
            handle.add(build_generation, arcname=destination.name)
        restore_wrapper.mkdir(parents=True)
        _safe_extract(temporary_archive, restore_wrapper)
        extracted = restore_wrapper / destination.name
        if not extracted.is_dir():
            raise ValueError("archive does not contain the REC-016 package root")
        tool = extracted / "tools/package_manifest_consistent_generation.py"
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, "-B", str(tool), "verify", str(extracted)],
            cwd=extracted,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        isolated_report = json.loads(completed.stdout)
        if isolated_report.get("valid") is not True:
            raise ValueError("isolated package-only REC-016 verification failed")
        build_generation.rename(destination)
        promoted.append(destination)
        temporary_archive.replace(archive)
        promoted.append(archive)
        extracted.rename(isolated_restore)
        promoted.append(isolated_restore)
        restore_wrapper.rmdir()
        return {
            **report,
            "archive": str(archive),
            "archive_sha256": recovery_package.sha256_file(archive),
            "archive_bytes": archive.stat().st_size,
            "isolated_restore": str(isolated_restore),
            "isolated_package_only_verify": True,
        }
    except Exception:
        for promoted_target in reversed(promoted):
            if promoted_target.is_dir():
                shutil.rmtree(promoted_target, ignore_errors=True)
            elif promoted_target.exists():
                promoted_target.unlink()
        shutil.rmtree(build_generation, ignore_errors=True)
        if temporary_archive.exists():
            temporary_archive.unlink()
        shutil.rmtree(restore_wrapper, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create")
    create.add_argument("source", type=Path)
    create.add_argument("destination", type=Path)
    release = sub.add_parser("release")
    release.add_argument("source", type=Path)
    release.add_argument("destination", type=Path)
    release.add_argument("archive", type=Path)
    release.add_argument("isolated_restore", type=Path)
    verify = sub.add_parser("verify")
    verify.add_argument("root", type=Path)
    ingest = sub.add_parser("stage-import")
    ingest.add_argument("root", type=Path)
    ingest.add_argument("manifest", type=Path)
    ingest.add_argument("--schema", type=Path)
    args = parser.parse_args()
    if args.command == "create":
        report = create_generation(args.source, args.destination)
    elif args.command == "release":
        report = create_release(
            args.source, args.destination, args.archive, args.isolated_restore
        )
    elif args.command == "verify":
        report = verify_generation(
            args.root, require_empty=True, require_drill_proof=True
        )
    else:
        report = stage_and_import_bundle(args.root, args.manifest, args.schema)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
