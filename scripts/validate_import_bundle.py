#!/usr/bin/env python3
"""Fail-closed validator for staged OpenCart and Ecwid recovery bundles."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path, PurePosixPath, PureWindowsPath


SCHEMA_VERSION = "mt-uniforms-commerce-import/v1"
SYSTEMS = {"opencart", "ecwid"}
ARTIFACT_TYPES = {
    "database-sql", "table-snapshot", "ui-csv", "api-page", "media", "configuration", "log"
}
COMPLETENESS = {"complete-file", "complete-window", "partial-documented"}
SENSITIVE_NORMALIZED_FIELDS = {
    "password", "salt", "token", "authorization", "cookie", "session", "cvv", "cvc",
    "pan", "card_number", "full_card_number", "ip", "cart", "wishlist", "code",
}
RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,127}$")
SHA256 = re.compile(r"^[a-f0-9]{64}$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _portable_path(value: object) -> PurePosixPath:
    _require(isinstance(value, str) and value.strip() == value and value, "artifact path must be non-empty")
    _require("\\" not in value, f"artifact path is not a portable relative path: {value}")
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    _require(
        not posix.is_absolute() and not windows.is_absolute() and not windows.drive
        and ".." not in posix.parts and "." not in posix.parts,
        f"artifact path is not a portable relative path: {value}",
    )
    return posix


def _is_nonnegative_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _reject_sensitive_keys(value: object, locator: str = "record") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            if normalized in SENSITIVE_NORMALIZED_FIELDS:
                raise ValueError(f"sensitive field is forbidden in normalization snapshot: {locator}/{key}")
            _reject_sensitive_keys(child, f"{locator}/{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_sensitive_keys(child, f"{locator}/{index}")


def validate_ecwid_pages(pages: list[dict], entity: str) -> dict:
    _require(bool(pages), f"Ecwid {entity} API page set is empty")
    ordered = sorted(pages, key=lambda page: page.get("offset", -1))
    expected_offset = 0
    expected_total = None
    seen_ids = set()
    observed = 0
    for page in ordered:
        for name in ("offset", "limit", "count", "total"):
            _require(_is_nonnegative_int(page.get(name)), f"Ecwid {entity} page {name} must be a non-negative integer")
        items = page.get("items")
        _require(isinstance(items, list), f"Ecwid {entity} page items must be an array")
        _require(page["offset"] == expected_offset, f"Ecwid {entity} pages are not contiguous at offset {page['offset']}")
        _require(page["count"] == len(items), f"Ecwid {entity} page count does not match items")
        if expected_total is None:
            expected_total = page["total"]
        _require(page["total"] == expected_total, f"Ecwid {entity} page total drifted")
        for item in items:
            _require(isinstance(item, dict) and "id" in item, f"Ecwid {entity} item lacks stable id")
            item_id = str(item["id"])
            _require(item_id not in seen_ids, f"Ecwid {entity} duplicate item id: {item_id}")
            seen_ids.add(item_id)
        observed += len(items)
        expected_offset += page["limit"]
    _require(observed == expected_total, f"Ecwid {entity} cumulative items do not equal total")
    return {"entity": entity, "pages": len(ordered), "items": observed}


def _validate_snapshot(path: Path, artifact: dict, seen_source_ids: set[str]) -> int:
    rows = 0
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid NDJSON at {artifact['relative_path']}:{line_number}: {exc.msg}") from exc
            _require(isinstance(row, dict), "table-snapshot row must be an object")
            for key in ("source_record_id", "source_locator", "entity", "record"):
                _require(key in row, f"table-snapshot row missing {key}")
            source_record_id = str(row["source_record_id"])
            _require(source_record_id not in seen_source_ids, f"duplicate source_record_id: {source_record_id}")
            seen_source_ids.add(source_record_id)
            _require(row["entity"] == artifact["entity"], "snapshot entity does not match artifact entity")
            _reject_sensitive_keys(row["record"])
            rows += 1
    _require(rows == artifact["record_count"], f"snapshot record_count mismatch: {artifact['relative_path']}")
    return rows


def _validate_money_checks(checks: object) -> None:
    _require(isinstance(checks, list), "money_checks must be an array")
    for check in checks:
        _require(isinstance(check, dict), "money check must be an object")
        required = ("order_ref", "source_total_minor", "normalized_total_minor", "rounding_quantum_minor")
        for name in required:
            _require(name in check, f"money check missing {name}")
        for name in required[1:]:
            _require(_is_nonnegative_int(check[name]), "money checks must use integer minor units")
        delta = abs(check["source_total_minor"] - check["normalized_total_minor"])
        _require(delta <= check["rounding_quantum_minor"], f"money reconciliation failed for {check['order_ref']}")


def validate_bundle(manifest_path: Path, schema_path: Path) -> dict:
    manifest_path = Path(manifest_path).resolve()
    root = manifest_path.parent
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    bundle = json.loads(manifest_path.read_text(encoding="utf-8"))
    _require(schema.get("properties", {}).get("schema_version", {}).get("const") == SCHEMA_VERSION,
             "validator schema is unsupported")
    _require(isinstance(bundle, dict), "bundle manifest must be an object")
    required = {
        "schema_version", "run_id", "source_system", "store_ref", "captured_at", "source_version",
        "capture_method", "status", "scope", "artifacts", "reconciliation",
    }
    _require(required.issubset(bundle), f"bundle manifest missing fields: {sorted(required - set(bundle))}")
    _require(bundle["schema_version"] == SCHEMA_VERSION, "bundle schema_version is unsupported")
    _require(isinstance(bundle["run_id"], str) and RUN_ID.fullmatch(bundle["run_id"]) is not None,
             "run_id is invalid")
    _require(bundle["source_system"] in SYSTEMS, "source_system must be opencart or ecwid")
    _require(isinstance(bundle["store_ref"], str) and bundle["store_ref"], "store_ref is required")
    _require(isinstance(bundle["source_version"], str) and bundle["source_version"], "source_version is required")
    _require(isinstance(bundle["capture_method"], str) and bundle["capture_method"], "capture_method is required")
    _require(bundle["status"] == "reconciled", "only reconciled bundles can be accepted")
    try:
        datetime.fromisoformat(str(bundle["captured_at"]).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("captured_at must be an RFC 3339 timestamp") from exc

    scope = bundle["scope"]
    _require(isinstance(scope, dict) and scope.get("kind") in {"complete", "partial"}, "scope kind is invalid")
    entities = scope.get("entities")
    _require(isinstance(entities, list) and entities and len(entities) == len(set(entities)),
             "scope entities must be a non-empty unique array")

    artifacts = bundle["artifacts"]
    _require(isinstance(artifacts, list) and artifacts, "artifacts must be a non-empty array")
    seen_paths = set()
    seen_source_ids: set[str] = set()
    artifact_types = set()
    ecwid_pages: dict[str, list[dict]] = {}
    snapshot_rows = 0
    for artifact in artifacts:
        _require(isinstance(artifact, dict), "artifact must be an object")
        for name in ("relative_path", "artifact_type", "sha256", "bytes", "record_count", "completeness", "entity"):
            _require(name in artifact, f"artifact missing {name}")
        relative = _portable_path(artifact["relative_path"])
        _require(relative.as_posix() not in seen_paths, f"duplicate artifact path: {relative}")
        seen_paths.add(relative.as_posix())
        _require(artifact["artifact_type"] in ARTIFACT_TYPES, "artifact_type is unsupported")
        _require(artifact["completeness"] in COMPLETENESS, "artifact completeness is unsupported")
        _require(artifact["entity"] in entities, "artifact entity is outside declared scope")
        _require(isinstance(artifact["sha256"], str) and SHA256.fullmatch(artifact["sha256"]) is not None,
                 "artifact sha256 is invalid")
        _require(_is_nonnegative_int(artifact["bytes"]) and _is_nonnegative_int(artifact["record_count"]),
                 "artifact bytes and record_count must be non-negative integers")
        path = (root / Path(*relative.parts)).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"artifact path is not a portable relative path: {relative}") from exc
        _require(path.is_file(), f"artifact is missing: {relative}")
        _require(path.stat().st_size == artifact["bytes"], f"artifact size mismatch: {relative}")
        _require(sha256_file(path) == artifact["sha256"], f"artifact checksum mismatch: {relative}")
        artifact_types.add(artifact["artifact_type"])
        if artifact["artifact_type"] == "table-snapshot":
            snapshot_rows += _validate_snapshot(path, artifact, seen_source_ids)
        elif artifact["artifact_type"] == "api-page":
            page = json.loads(path.read_text(encoding="utf-8"))
            ecwid_pages.setdefault(artifact["entity"], []).append(page)

    if bundle["source_system"] == "opencart":
        _require("database-sql" in artifact_types, "OpenCart bundle requires a database-sql artifact")
        _require("table-snapshot" in artifact_types, "reconciled OpenCart bundle requires table-snapshot artifacts")
    else:
        _require(bool(artifact_types & {"ui-csv", "api-page"}), "Ecwid bundle requires ui-csv or api-page artifacts")
        for entity, pages in ecwid_pages.items():
            validate_ecwid_pages(pages, entity)

    reconciliation = bundle["reconciliation"]
    required_reconciliation = {
        "source_counts", "normalized_counts", "skipped_counts", "skips",
        "foreign_key_errors", "unresolved_conflicts", "money_checks",
    }
    _require(isinstance(reconciliation, dict) and required_reconciliation.issubset(reconciliation),
             "reconciliation is incomplete")
    _require(reconciliation["foreign_key_errors"] == 0, "foreign key errors remain")
    _require(reconciliation["unresolved_conflicts"] == 0, "unresolved conflicts remain")
    count_maps = [reconciliation[name] for name in ("source_counts", "normalized_counts", "skipped_counts")]
    for counts in count_maps:
        _require(isinstance(counts, dict) and set(counts) == set(entities), "reconciliation count keys must match scope entities")
        _require(all(_is_nonnegative_int(value) for value in counts.values()), "reconciliation counts must be non-negative integers")
    for entity in entities:
        source = reconciliation["source_counts"][entity]
        imported = reconciliation["normalized_counts"][entity]
        skipped = reconciliation["skipped_counts"][entity]
        _require(source == imported + skipped, f"{entity}: source rows must equal imported plus skipped")
    skips = reconciliation["skips"]
    _require(isinstance(skips, list) and len(skips) == sum(reconciliation["skipped_counts"].values()),
             "each skipped row requires one reason")
    _validate_money_checks(reconciliation["money_checks"])
    return {
        "valid": True,
        "schema_version": SCHEMA_VERSION,
        "run_id": bundle["run_id"],
        "source_system": bundle["source_system"],
        "artifact_count": len(artifacts),
        "source_records": sum(reconciliation["source_counts"].values()),
        "snapshot_rows": snapshot_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--schema", type=Path, default=Path(__file__).parents[1] / "schemas" / "commerce-import-bundle-v1.schema.json")
    args = parser.parse_args()
    print(json.dumps(validate_bundle(args.manifest, args.schema), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
