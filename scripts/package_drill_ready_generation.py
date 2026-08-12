#!/usr/bin/env python3
"""Build and operate REC-013 with a representative restore drill and current status."""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath

import capture_missing_media
import package_binary_ready_generation as rec012
import recovery_package


GENERATION = "REC-013"
PARENT_GENERATION = "REC-012"
READINESS = "source-acquisition-and-representative-restore-drill-ready-awaiting-authenticated-exports"
INVENTORY_PATH = "business-continuity/service-account-control-inventory.json"
PackagedAsset = rec012.PackagedAsset

INVENTORY_FIELDS = {
    "service_id",
    "category",
    "system",
    "observed_configuration",
    "authoritative_owner",
    "payer",
    "renewal_date",
    "recovery_contact",
    "export_or_recovery_path",
    "control_status",
    "evidence_refs",
    "blockers",
}
CONTROL_STATUSES = {"unverified", "partial", "verified", "deferred-by-decision"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def default_assets() -> list[PackagedAsset]:
    project = Path(__file__).resolve().parents[1]
    return [
        PackagedAsset(
            project / "scripts/package_drill_ready_generation.py",
            "tools/package_drill_ready_generation.py",
            "recovery-tool",
        ),
        PackagedAsset(
            project / "scripts/run_recovery_drill.py",
            "tools/run_recovery_drill.py",
            "recovery-tool",
        ),
        PackagedAsset(
            project / "docs/recovery/representative-restore-drill-v1.md",
            "docs/recovery/representative-restore-drill-v1.md",
            "recovery-contract",
        ),
        PackagedAsset(
            project / "evidence/2026-08-10-representative-restore-drill.md",
            "docs/recovery/representative-restore-drill-evidence.md",
            "restore-evidence",
        ),
        PackagedAsset(
            project / "docs/recovery/service-account-control-inventory-v1.json",
            INVENTORY_PATH,
            "continuity-inventory",
        ),
        PackagedAsset(
            project / "docs/recovery/drill-ready-package-v1.md",
            "docs/recovery/drill-ready-package-v1.md",
            "recovery-contract",
        ),
    ]


def validate_service_inventory(path: Path) -> dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema_version") != "mt-uniforms-service-account-control/v1":
        raise ValueError("service inventory schema_version is invalid")
    if payload.get("contains_secrets") is not False:
        raise ValueError("service inventory must explicitly declare contains_secrets false")
    services = payload.get("services")
    if not isinstance(services, list) or not services:
        raise ValueError("service inventory must contain at least one service")
    identifiers = set()
    statuses = Counter()
    for index, service in enumerate(services):
        if not isinstance(service, dict):
            raise ValueError(f"service inventory row {index} is not an object")
        missing = INVENTORY_FIELDS - set(service)
        if missing:
            raise ValueError(f"service inventory row {index} missing required fields: {sorted(missing)}")
        extra = set(service) - INVENTORY_FIELDS
        if extra:
            raise ValueError(f"service inventory row {index} has unsupported fields: {sorted(extra)}")
        identifier = service["service_id"]
        if not isinstance(identifier, str) or not identifier or identifier in identifiers:
            raise ValueError("service inventory service_id values must be unique non-empty strings")
        identifiers.add(identifier)
        for name in INVENTORY_FIELDS - {"evidence_refs", "blockers"}:
            if not isinstance(service[name], str) or not service[name].strip():
                raise ValueError(f"service inventory {identifier} field {name} must be non-empty")
        for name in ("evidence_refs", "blockers"):
            if not isinstance(service[name], list) or not all(
                isinstance(item, str) and item.strip() for item in service[name]
            ):
                raise ValueError(f"service inventory {identifier} field {name} must be a string array")
        status = service["control_status"]
        if status not in CONTROL_STATUSES:
            raise ValueError(f"service inventory {identifier} has invalid control_status")
        statuses[status] += 1
    return {
        "valid": True,
        "services": len(services),
        "control_status_counts": dict(sorted(statuses.items())),
        "contains_secrets": False,
    }


def _copy_assets(root: Path, assets: list[PackagedAsset], captured_at: str) -> dict:
    inventory_report = None
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        connection.execute("BEGIN IMMEDIATE")
        for asset in assets:
            source = Path(asset.source).resolve()
            if not source.is_file():
                raise ValueError(f"required REC-013 source asset is missing: {source.name}")
            relative = Path(asset.destination)
            if relative.is_absolute() or PureWindowsPath(asset.destination).is_absolute() or ".." in relative.parts:
                raise ValueError(f"packaged destination is not portable: {asset.destination}")
            if relative.as_posix() == INVENTORY_PATH:
                inventory_report = validate_service_inventory(source)
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
                    "recovery-tooling",
                    asset.artifact_type,
                    relative.as_posix(),
                    captured_at,
                    digest,
                    size,
                    "captured",
                    f"REC-013 packaged {asset.artifact_type}: {relative.name}",
                    f"rec013:{asset.artifact_type}:{relative.as_posix()}",
                    "deterministic-copy",
                    inventory_report["services"] if relative.as_posix() == INVENTORY_PATH else 0,
                    "internal",
                    "complete-file",
                ),
            )
        if inventory_report is None:
            raise ValueError("REC-013 assets must include the service account-control inventory")
        connection.commit()
        return inventory_report
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _recovery_status(captured_at: str, inventory: dict) -> str:
    return f"""# M&T Uniforms REC-013 recovery status

Generated: {captured_at}

REC-013 is the current verified offline recovery authority.

## Proven

- Public storefront: 528 reachable safe pages captured with zero queued uncaptured URLs.
- Public media: 1,542 / 1,542 exact referenced binaries preserved with provenance.
- Public runtime: 34 / 35 references captured; the sole remaining AddThis reference is retired and dispositioned.
- Journal: one exact supplemental theme/settings SQL export is preserved and hashed.
- Portable database: checksums, SQLite integrity, foreign keys, relative source paths, and record lineage verify.
- Representative recovery: a synthetic agency account/order drill passed through staged importer v2 with 22 normalized and 22 lineage rows in a disposable copy; the authority remained unchanged.
- Work Scope is enrolled with legacy task/history snapshots preserved.
- Service/account continuity inventory: {inventory['services']} value-free services recorded; primary control remains explicit where unverified.
- Clover authenticated export is excluded by DEC-005; Clover remains the documented external POS boundary.

## Tool-ready, awaiting authenticated source bytes

- Full OpenCart SQL database, webroot, external storage, configuration, private media, versions, and logs.
- Complete Ecwid catalog, customers, orders, settings, adjunct resources, media, and downloadable files.

## Still unproven

- Registrar, DNS, hosting, mail, payment, shipping, subscription, and licence owner/payer/renewal/recovery evidence.
- Encrypted offline immutable custody and independent offsite custody under an approved recipient/key.
- Reconciliation of real private OpenCart and Ecwid records after authenticated exports arrive.

No password, API token, session cookie, payment-card value, or plaintext authorization value is stored in this package.
"""


def _completion_audit(captured_at: str) -> str:
    return f"""# Recovery objective completion audit

Generated: {captured_at}

Status vocabulary: PROVEN, TOOL-READY, MISSING-SOURCE, EXCLUDED-BY-DECISION.

## Source preservation

- OpenCart complete database/webroot/storage/configuration: MISSING-SOURCE. Native acquisition tooling and runbook: TOOL-READY.
- Journal theme/settings supplement: PROVEN. It is explicitly supplemental and does not replace the full OpenCart export.
- Ecwid JSON/API and binary acquisition: TOOL-READY. Authenticated private exports: MISSING-SOURCE.
- Clover authenticated export: EXCLUDED-BY-DECISION under DEC-005; retained POS boundary documentation is preserved.

## Public continuity

- Reachable safe storefront graph: PROVEN at 528 pages with zero queued uncaptured URLs.
- Exact referenced public media: PROVEN at 1,542 / 1,542.
- Public runtime: PROVEN with 34 captured references and one retired AddThis disposition.
- Public business/infrastructure observations: PROVEN with record-level provenance; account control remains MISSING-SOURCE.

## Data and restore

- Portable normalized SQLite schema, checksums, source lineage, integrity, and foreign keys: PROVEN.
- Raw-first staged importer with checksum refresh on success or recorded failure: PROVEN.
- Representative agency-order drill: PROVEN with linked account, entitlement, pricing, order snapshot, customization, PO, invoice, payment/refund, fulfillment, return, production, audit, and 22 lineage rows in a disposable copy.
- Real private commerce population and cross-system reconciliation: MISSING-SOURCE.

## Ownership and custody

- Value-free service/account-control inventory with explicit owner, payer, renewal, recovery-contact, and export-path fields: PROVEN.
- Primary account-side ownership/control evidence: MISSING-SOURCE.
- Encrypted offline and independent offsite custody: MISSING-SOURCE pending an approved recipient/key and destination.

## Work Scope

- Canonical Kelly Uniforms Work Scope enrollment: PROVEN.
- Legacy task/history preservation: PROVEN through immutable project-state snapshots and guarded state migration.

## Completion ruling

The full objective remains incomplete because authenticated OpenCart/Ecwid source bytes, primary account-control evidence, and approved encrypted offsite custody are unavailable. REC-013 proves all currently closable offline acquisition, preservation, normalization, and representative-restore pathways without inventing private client records.
"""


def _register_generated_file(root: Path, relative: str, captured_at: str) -> None:
    path = root / relative
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
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
                f"REC-013 generated current status: {relative}",
                f"rec013:generated:{relative}",
                "deterministic-render",
                0,
                "internal",
                "complete-file",
            ),
        )
        connection.commit()
    finally:
        connection.close()


def stage_drill_readiness(
    root: Path, assets: list[PackagedAsset], captured_at: str | None = None
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
    inventory = _copy_assets(root, assets, now)
    connection = sqlite3.connect(database)
    try:
        connection.executemany(
            "INSERT INTO recovery_metadata(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            {
                "generation": GENERATION,
                "parent_generation": PARENT_GENERATION,
                "recovery_readiness": READINESS,
                "representative_restore_drill": "proven-synthetic-disposable-copy",
                "service_account_control_status": "inventory-present-primary-control-unverified",
            }.items(),
        )
        connection.commit()
    finally:
        connection.close()
    manifest = rec012.rec011.rec010.rec009.rec008._remove_legacy_absolute_paths(manifest)
    manifest["generation"] = GENERATION
    manifest["parent_generation"] = PARENT_GENERATION
    manifest["generated_at"] = now
    manifest["recovery_readiness"] = READINESS
    manifest["restore_drill"] = {
        "status": "proven-synthetic-disposable-copy",
        "tool": "tools/run_recovery_drill.py",
        "contract": "docs/recovery/representative-restore-drill-v1.md",
        "evidence": "docs/recovery/representative-restore-drill-evidence.md",
        "authority_population_effect": "none",
    }
    manifest["service_account_inventory"] = {
        "status": "value-free-inventory-present-primary-control-unverified",
        "path": INVENTORY_PATH,
        "services": inventory["services"],
        "control_status_counts": inventory["control_status_counts"],
        "control_status": "unverified",
        "contains_secrets": False,
    }
    manifest.setdefault("work_scope_migration", {})["status"] = (
        "enrolled-legacy-history-preserved"
    )
    manifest.setdefault("commerce_import", {})["tool"] = (
        "tools/package_drill_ready_generation.py"
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    (root / "RECOVERY-STATUS.md").write_text(
        _recovery_status(now, inventory), encoding="utf-8", newline="\n"
    )
    (root / "COMPLETION-AUDIT.md").write_text(
        _completion_audit(now), encoding="utf-8", newline="\n"
    )
    _register_generated_file(root, "RECOVERY-STATUS.md", now)
    _register_generated_file(root, "COMPLETION-AUDIT.md", now)
    return {
        "generation": GENERATION,
        "parent_generation": PARENT_GENERATION,
        "packaged_assets": len(assets),
        "readiness": READINESS,
        "inventory": inventory,
    }


def stage_and_import_bundle(root: Path, manifest_path: Path, schema_path: Path | None = None) -> dict:
    return rec012.stage_and_import_bundle(root, manifest_path, schema_path)


def create_generation(source: Path, destination: Path) -> dict:
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    if not source.is_dir():
        raise ValueError(f"source generation does not exist: {source}")
    if destination.exists():
        raise ValueError(f"destination already exists; recovery generations are immutable: {destination}")
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("source and destination generations must be distinct, non-nested paths")
    rec012.verify_generation(source, require_empty=True)
    temporary = destination.with_name(f".{destination.name}.building-{uuid.uuid4().hex}")
    try:
        shutil.copytree(source, temporary)
        stage_drill_readiness(temporary, default_assets())
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
        raise ValueError("REC-013 generation lineage is invalid")
    absolute = rec012.rec011.rec010.rec009.rec008._manifest_absolute_paths(manifest)
    if absolute:
        raise ValueError(f"package manifest contains absolute paths: {absolute[:3]}")
    drill = manifest.get("restore_drill", {})
    inventory_meta = manifest.get("service_account_inventory", {})
    required = [
        drill.get("tool"),
        drill.get("contract"),
        drill.get("evidence"),
        inventory_meta.get("path"),
        manifest.get("commerce_import", {}).get("tool"),
        "docs/recovery/drill-ready-package-v1.md",
        "RECOVERY-STATUS.md",
        "COMPLETION-AUDIT.md",
    ]
    for relative in required:
        if not relative or not (root / relative).is_file():
            raise ValueError(f"REC-013 packaged dependency is missing: {relative}")
    inventory = validate_service_inventory(root / INVENTORY_PATH)
    if inventory_meta.get("services") != inventory["services"]:
        raise ValueError("REC-013 service inventory count metadata is invalid")
    status = (root / "RECOVERY-STATUS.md").read_text(encoding="utf-8")
    audit = (root / "COMPLETION-AUDIT.md").read_text(encoding="utf-8")
    required_status = (
        "# M&T Uniforms REC-013 recovery status",
        "1,542 / 1,542",
        "Work Scope is enrolled",
        "Clover authenticated export is excluded by DEC-005",
    )
    if any(text not in status for text in required_status):
        raise ValueError("REC-013 recovery status is incomplete")
    if "Representative agency-order drill: PROVEN" not in audit:
        raise ValueError("REC-013 completion audit is missing restore-drill proof")
    stale = (
        "REC-003 recovery status",
        "Canonical Kelly Uniforms Work Scope enrollment: MISSING",
        "Binary media: PARTIAL",
    )
    if any(text in status or text in audit for text in stale):
        raise ValueError("REC-013 contains stale recovery status claims")
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        metadata = dict(connection.execute("SELECT key,value FROM recovery_metadata"))
        counts = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in rec012.rec011.rec010.rec009.rec008.EMPTY_IMPORT_TABLES
        }
        import_sources = connection.execute(
            "SELECT COUNT(*) FROM source_manifest WHERE source_ref LIKE 'import:%'"
        ).fetchone()[0]
    finally:
        connection.close()
    if metadata.get("generation") != GENERATION or metadata.get("parent_generation") != PARENT_GENERATION:
        raise ValueError("REC-013 database lineage metadata is invalid")
    if metadata.get("recovery_readiness") != READINESS:
        raise ValueError("REC-013 database recovery readiness is invalid")
    if require_empty and (sum(counts.values()) or import_sources):
        raise ValueError("fresh REC-013 contains source-backed commerce/import rows")
    return {
        "valid": True,
        "generation": GENERATION,
        "parent_generation": PARENT_GENERATION,
        "readiness": READINESS,
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
        report = verify_generation(args.root)
    else:
        report = stage_and_import_bundle(args.root, args.manifest, args.schema)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
