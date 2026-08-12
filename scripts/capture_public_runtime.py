#!/usr/bin/env python3
"""Create and verify an immutable recovery generation with public runtime binaries."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import shutil
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import recovery_package


INVENTORY_PATH = Path("public-site/runtime-assets/inventory.json")
DIRECT_ASSET_DIR = Path("public-site/runtime-assets/direct")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _kind(entry: dict) -> str:
    if entry.get("kind"):
        return str(entry["kind"])
    path = urllib.parse.urlparse(entry["url"]).path.lower()
    return "script" if path.endswith(".js") else "font" if ".woff" in path else "runtime"


def _extension(url: str, content_type: str | None, kind: str) -> str:
    suffix = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if suffix and len(suffix) <= 10:
        return suffix
    guessed = mimetypes.guess_extension((content_type or "").split(";", 1)[0].strip())
    return guessed or (".js" if kind == "script" else ".bin")


def _targets(inventory: dict) -> list[dict]:
    ordered: dict[str, dict] = {}
    for entry in inventory.get("script_references", []):
        ordered.setdefault(
            entry["url"],
            {"url": entry["url"], "kind": "script", "pages": entry.get("pages", [])},
        )
    for entry in inventory.get("failed_assets", []):
        ordered.setdefault(
            entry["url"],
            {"url": entry["url"], "kind": _kind(entry), "pages": entry.get("pages", [])},
        )
    return list(ordered.values())


def _fetch(url: str, retries: int, timeout: int) -> tuple[bytes, str | None]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 MT-Uniforms-Recovery/1.0", "Accept": "*/*"},
    )
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read(), response.headers.get_content_type()
        except Exception as exc:  # recorded as evidence; retry transient and HTTP failures alike
            if last_error is not None and hasattr(last_error, "close"):
                last_error.close()
            last_error = exc
            if attempt < retries:
                time.sleep(min(2 ** attempt, 4))
    if isinstance(last_error, urllib.error.HTTPError):
        code, reason = last_error.code, last_error.reason
        last_error.close()
        raise RuntimeError(f"HTTP {code}: {reason}") from last_error
    raise RuntimeError(f"{type(last_error).__name__}: {last_error}") from last_error


def _ensure_runtime_tables(connection: sqlite3.Connection) -> None:
    connection.execute(
        """CREATE TABLE IF NOT EXISTS runtime_assets(
            asset_id INTEGER PRIMARY KEY, url TEXT NOT NULL, kind TEXT NOT NULL,
            source_page TEXT, downloaded_path TEXT NOT NULL, content_type TEXT,
            bytes INTEGER, sha256 TEXT NOT NULL, status TEXT NOT NULL
        )"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS runtime_asset_failures(
            failure_id INTEGER PRIMARY KEY, url TEXT NOT NULL, kind TEXT,
            content_type TEXT, reason TEXT, pages_json TEXT NOT NULL
        )"""
    )


def _update_database(root: Path, captured: list[dict], failures: list[dict], captured_at: str) -> None:
    database = root / recovery_package.DATABASE_FILE
    connection = sqlite3.connect(database)
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("BEGIN IMMEDIATE")
        _ensure_runtime_tables(connection)
        connection.execute(
            "CREATE TABLE IF NOT EXISTS recovery_metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        for item in captured:
            connection.execute(
                """INSERT INTO runtime_assets(
                    url, kind, source_page, downloaded_path, content_type, bytes, sha256, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    item["url"], item["kind"], (item.get("pages") or [None])[0],
                    item["packaged_path"], item["content_type"], item["bytes"],
                    item["sha256"], "captured-direct-rec004",
                ),
            )
            connection.execute(
                """INSERT INTO source_manifest(
                    system, artifact_type, source_path, captured_at, sha256, bytes, status,
                    notes, source_ref, source_uri, capture_method, record_count,
                    sensitivity, completeness
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    "public-storefront", "runtime-binary", item["packaged_path"], captured_at,
                    item["sha256"], item["bytes"], "captured",
                    f"REC-004 direct public capture ({item['kind']})",
                    f"runtime:{hashlib.sha256(item['url'].encode()).hexdigest()}",
                    item["url"], "direct-http", 1, "public", "complete-binary",
                ),
            )
        for item in failures:
            connection.execute(
                """INSERT INTO runtime_asset_failures(
                    url, kind, content_type, reason, pages_json
                ) VALUES (?, ?, ?, ?, ?)""",
                (item["url"], item["kind"], None, item["reason"], json.dumps(item["pages"])),
            )
        connection.executemany(
            "INSERT INTO recovery_metadata(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            {
                "generation": "REC-004",
                "public_runtime_captured_at": captured_at,
                "public_runtime_captured_count": str(len(captured)),
                "public_runtime_failed_count": str(len(failures)),
            }.items(),
        )
        inventory = root / INVENTORY_PATH
        connection.execute(
            """UPDATE source_manifest SET sha256=?, bytes=?, captured_at=?,
                status='captured', notes=? WHERE source_path=?""",
            (
                recovery_package.sha256_file(inventory), inventory.stat().st_size, captured_at,
                "REC-004 runtime inventory after direct public capture",
                INVENTORY_PATH.as_posix(),
            ),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _reconcile_manifest_scope(root: Path, captured_at: str, summary: dict) -> None:
    manifest_path = root / "package-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    missing = manifest.get("missing_required", [])
    manifest["missing_required"] = [
        item for item in missing
        if "clover" not in str(item).lower() and str(item) != "isolated restore evidence"
    ]
    manifest["generation"] = "REC-004"
    manifest["generated_at"] = captured_at
    manifest["parent_generation"] = "REC-003"
    manifest["clover_authenticated_scope"] = "excluded-per-client-decision"
    manifest["public_runtime"] = summary | {
        "inventory": INVENTORY_PATH.as_posix(),
        "capture_method": "direct-http",
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )


def capture_generation(source: Path, destination: Path, retries: int = 2, timeout: int = 30) -> dict:
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    if not source.is_dir():
        raise ValueError(f"source recovery generation does not exist: {source}")
    if destination.exists():
        raise ValueError(f"destination already exists; recovery generations are immutable: {destination}")
    inventory_path = source / INVENTORY_PATH
    if not inventory_path.is_file():
        raise ValueError(f"runtime inventory is missing: {inventory_path}")

    shutil.copytree(source, destination)
    captured_at = utc_now()
    inventory_file = destination / INVENTORY_PATH
    inventory = json.loads(inventory_file.read_text(encoding="utf-8"))
    captured: list[dict] = []
    failures: list[dict] = []
    binary_dir = destination / DIRECT_ASSET_DIR
    binary_dir.mkdir(parents=True, exist_ok=True)

    for target in _targets(inventory):
        url = target["url"]
        try:
            payload, content_type = _fetch(url, retries=retries, timeout=timeout)
            url_digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
            relative = DIRECT_ASSET_DIR / f"{url_digest}{_extension(url, content_type, target['kind'])}"
            output = destination / relative
            output.write_bytes(payload)
            captured.append(
                {
                    "url": url,
                    "kind": target["kind"],
                    "pages": target.get("pages", []),
                    "captured_at": captured_at,
                    "content_type": content_type,
                    "bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "packaged_path": relative.as_posix(),
                    "status": "captured-direct",
                }
            )
        except Exception as exc:
            failures.append(
                {
                    "url": url,
                    "kind": target["kind"],
                    "pages": target.get("pages", []),
                    "captured_at": captured_at,
                    "reason": str(exc),
                    "status": "failed-direct",
                }
            )

    inventory["direct_capture_generated_at"] = captured_at
    inventory["direct_capture_assets"] = captured
    inventory["direct_capture_failures"] = failures
    inventory["direct_capture_summary"] = {
        "attempted": len(captured) + len(failures),
        "captured": len(captured),
        "failed": len(failures),
    }
    inventory_file.write_text(
        json.dumps(inventory, indent=2) + "\n", encoding="utf-8", newline="\n"
    )

    _reconcile_manifest_scope(destination, captured_at, inventory["direct_capture_summary"])

    _update_database(destination, captured, failures, captured_at)
    tools_dir = destination / "tools"
    tools_dir.mkdir(exist_ok=True)
    shutil.copy2(Path(__file__), tools_dir / Path(__file__).name)
    shutil.copy2(Path(recovery_package.__file__), tools_dir / Path(recovery_package.__file__).name)
    recovery_package.write_checksums(destination)
    return verify_generation(destination)


def finalize_generation(root: Path) -> dict:
    """Repair generation metadata after an interrupted post-capture verification."""
    root = Path(root).resolve()
    inventory_file = root / INVENTORY_PATH
    inventory = json.loads(inventory_file.read_text(encoding="utf-8"))
    captured = inventory.get("direct_capture_assets", [])
    failures = inventory.get("direct_capture_failures", [])
    captured_at = inventory.get("direct_capture_generated_at") or utc_now()
    _reconcile_manifest_scope(
        root,
        captured_at,
        {"attempted": len(captured) + len(failures), "captured": len(captured), "failed": len(failures)},
    )
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        connection.execute(
            """UPDATE source_manifest SET sha256=?, bytes=?, captured_at=?,
                status='captured', notes=? WHERE source_path=?""",
            (
                recovery_package.sha256_file(inventory_file), inventory_file.stat().st_size,
                captured_at, "REC-004 runtime inventory after direct public capture",
                INVENTORY_PATH.as_posix(),
            ),
        )
        connection.commit()
    finally:
        connection.close()
    recovery_package.write_checksums(root)
    return verify_generation(root)


def verify_generation(root: Path, expected_generation: str = "REC-004") -> dict:
    root = Path(root).resolve()
    package_report = recovery_package.verify_package(root)
    manifest = json.loads((root / "package-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("generation") != expected_generation:
        raise ValueError(f"package generation is not {expected_generation}")
    inventory = json.loads((root / INVENTORY_PATH).read_text(encoding="utf-8"))
    captured = inventory.get("direct_capture_assets", [])
    failures = inventory.get("direct_capture_failures", [])
    for item in captured:
        path = root / item["packaged_path"]
        if not path.is_file():
            raise ValueError(f"captured runtime binary is missing: {item['packaged_path']}")
        if recovery_package.sha256_file(path) != item["sha256"]:
            raise ValueError(f"captured runtime checksum mismatch: {item['packaged_path']}")
        if path.stat().st_size != item["bytes"]:
            raise ValueError(f"captured runtime byte count mismatch: {item['packaged_path']}")
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        database_count = connection.execute(
            "SELECT COUNT(*) FROM runtime_assets WHERE status='captured-direct-rec004'"
        ).fetchone()[0]
    finally:
        connection.close()
    if database_count != len(captured):
        raise ValueError(
            f"runtime SQLite provenance mismatch: database={database_count}; inventory={len(captured)}"
        )
    return {
        "valid": True,
        "generation": expected_generation,
        "attempted": len(captured) + len(failures),
        "captured": len(captured),
        "failed": len(failures),
        "package": package_report,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    capture = subparsers.add_parser("capture")
    capture.add_argument("source", type=Path)
    capture.add_argument("destination", type=Path)
    capture.add_argument("--retries", type=int, default=2)
    capture.add_argument("--timeout", type=int, default=30)
    verify = subparsers.add_parser("verify")
    verify.add_argument("root", type=Path)
    finalize = subparsers.add_parser("finalize")
    finalize.add_argument("root", type=Path)
    args = parser.parse_args()
    if args.command == "capture":
        report = capture_generation(args.source, args.destination, args.retries, args.timeout)
    elif args.command == "finalize":
        report = finalize_generation(args.root)
    else:
        report = verify_generation(args.root)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
