#!/usr/bin/env python3
"""Retry every unresolved public media URL and create immutable REC-006."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import capture_public_runtime
import recovery_package
import upgrade_commerce_schema


INVENTORY_PATH = Path("public-site/media-inventory.json")
RETRY_STATUSES = {"referenced-only", "direct-network-blocked"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _extension(url: str, content_type: str | None) -> str:
    suffix = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if suffix and len(suffix) <= 10:
        return suffix
    return ".bin"


def _capture_one(asset: dict, root: Path, timeout: int) -> dict:
    captured_at = utc_now()
    try:
        payload, content_type = capture_public_runtime._fetch(asset["url"], retries=1, timeout=timeout)
        digest = hashlib.sha256(payload).hexdigest()
        url_digest = hashlib.sha256(asset["url"].encode("utf-8")).hexdigest()
        relative = Path("public-site/media") / f"{url_digest}{_extension(asset['url'], content_type)}"
        (root / relative).parent.mkdir(parents=True, exist_ok=True)
        (root / relative).write_bytes(payload)
        return {
            "ok": True,
            "media_id": asset["media_id"],
            "captured_at": captured_at,
            "content_type": content_type,
            "bytes": len(payload),
            "sha256": digest,
            "downloaded_path": relative.as_posix(),
        }
    except Exception as exc:
        return {
            "ok": False,
            "media_id": asset["media_id"],
            "captured_at": captured_at,
            "reason": str(exc),
        }


def retry_media(inventory: dict, root: Path, workers: int = 12, timeout: int = 15) -> dict:
    root = Path(root)
    targets = [asset for asset in inventory.get("assets", []) if asset.get("download_status") in RETRY_STATUSES]
    by_id = {asset["media_id"]: asset for asset in targets}
    captured = 0
    failed = 0
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_capture_one, asset, root, timeout): asset for asset in targets}
        for future in as_completed(futures):
            result = future.result()
            asset = by_id[result["media_id"]]
            if result["ok"]:
                asset.update({key: value for key, value in result.items() if key not in {"ok", "media_id"}})
                asset["download_status"] = "downloaded-direct-rec006"
                asset["acquisition"] = "direct-http-rec006"
                asset.pop("capture_failure", None)
                captured += 1
            else:
                asset["download_status"] = "failed-direct-rec006"
                asset["capture_attempted_at"] = result["captured_at"]
                asset["capture_failure"] = result["reason"]
                failed += 1
    summary = {"attempted": len(targets), "captured": captured, "failed": failed}
    inventory["rec006_direct_capture"] = summary | {"completed_at": utc_now()}
    inventory["downloaded_exact_binaries"] = sum(
        1 for asset in inventory.get("assets", []) if str(asset.get("download_status", "")).startswith("downloaded")
    )
    inventory["direct_network_blocked"] = sum(
        1 for asset in inventory.get("assets", []) if asset.get("download_status") == "failed-direct-rec006"
    )
    return summary


def _update_database(root: Path, inventory: dict) -> None:
    inventory_file = root / INVENTORY_PATH
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("BEGIN IMMEDIATE")
        for asset in inventory["assets"]:
            if asset.get("download_status") == "downloaded-direct-rec006":
                connection.execute(
                    """UPDATE media_assets SET download_status=?, downloaded_path=?, content_type=?, sha256=?
                       WHERE media_id=?""",
                    (
                        asset["download_status"], asset["downloaded_path"], asset.get("content_type"),
                        asset["sha256"], asset["media_id"],
                    ),
                )
                packaged = root / asset["downloaded_path"]
                connection.execute(
                    """INSERT INTO source_manifest(
                        system, artifact_type, source_path, captured_at, sha256, bytes, status,
                        notes, source_ref, source_uri, capture_method, record_count, sensitivity, completeness
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        "public-storefront", "media-binary", asset["downloaded_path"], asset["captured_at"],
                        asset["sha256"], packaged.stat().st_size, "captured",
                        "REC-006 exact public media retry", f"media:{asset['media_id']}", asset["url"],
                        "direct-http", 1, "public", "complete-binary",
                    ),
                )
            elif asset.get("download_status") == "failed-direct-rec006":
                connection.execute(
                    "UPDATE media_assets SET download_status=? WHERE media_id=?",
                    (asset["download_status"], asset["media_id"]),
                )
        connection.execute(
            """UPDATE source_manifest SET sha256=?, bytes=?, captured_at=?, status='captured', notes=?
               WHERE source_path=?""",
            (
                recovery_package.sha256_file(inventory_file), inventory_file.stat().st_size, utc_now(),
                "REC-006 media inventory after retrying all unresolved public URLs", INVENTORY_PATH.as_posix(),
            ),
        )
        connection.executemany(
            "INSERT INTO recovery_metadata(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            {
                "generation": "REC-006",
                "parent_generation": "REC-005",
                "public_media_rec006_captured": str(inventory["rec006_direct_capture"]["captured"]),
                "public_media_rec006_failed": str(inventory["rec006_direct_capture"]["failed"]),
            }.items(),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _package_tools(root: Path) -> None:
    tools = root / "tools"
    tools.mkdir(exist_ok=True)
    sources = [
        Path(__file__), Path(capture_public_runtime.__file__), Path(recovery_package.__file__),
        Path(upgrade_commerce_schema.__file__),
    ]
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        connection.execute("BEGIN IMMEDIATE")
        for source in sources:
            packaged = tools / source.name
            shutil.copy2(source, packaged)
            relative = packaged.relative_to(root).as_posix()
            digest = recovery_package.sha256_file(packaged)
            updated = connection.execute(
                "UPDATE source_manifest SET captured_at=?,sha256=?,bytes=?,notes=? WHERE source_path=?",
                (utc_now(), digest, packaged.stat().st_size, f"REC-006 packaged tool: {source.name}", relative),
            ).rowcount
            if not updated:
                connection.execute(
                    """INSERT INTO source_manifest(system,artifact_type,source_path,captured_at,sha256,bytes,
                    status,notes,source_ref,capture_method,record_count,sensitivity,completeness)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    ("recovery-tooling", "recovery-tool", relative, utc_now(), digest, packaged.stat().st_size,
                     "captured", f"REC-006 packaged tool: {source.name}", f"recovery-tool:{source.name}",
                     "deterministic-copy", 0, "internal", "complete-file"),
                )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def create_generation(source: Path, destination: Path, workers: int = 12, timeout: int = 15) -> dict:
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError(f"destination already exists; recovery generations are immutable: {destination}")
    shutil.copytree(source, destination)
    inventory_file = destination / INVENTORY_PATH
    inventory = json.loads(inventory_file.read_text(encoding="utf-8"))
    summary = retry_media(inventory, destination, workers=workers, timeout=timeout)
    inventory_file.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8", newline="\n")
    _update_database(destination, inventory)
    manifest_file = destination / "package-manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    manifest["generation"] = "REC-006"
    manifest["parent_generation"] = "REC-005"
    manifest["generated_at"] = utc_now()
    manifest["public_media_retry"] = summary | {"inventory": INVENTORY_PATH.as_posix()}
    manifest_file.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    _package_tools(destination)
    recovery_package.write_checksums(destination)
    return verify_generation(destination)


def verify_generation(root: Path, expected_generation: str = "REC-006") -> dict:
    root = Path(root).resolve()
    inherited = upgrade_commerce_schema.verify_generation(root, expected_generation=expected_generation)
    inventory = json.loads((root / INVENTORY_PATH).read_text(encoding="utf-8"))
    summary = inventory.get("rec006_direct_capture")
    if not summary:
        raise ValueError("REC-006 media capture summary is missing")
    captured = [a for a in inventory["assets"] if a.get("download_status") == "downloaded-direct-rec006"]
    for asset in captured:
        path = root / asset["downloaded_path"]
        if not path.is_file() or recovery_package.sha256_file(path) != asset["sha256"]:
            raise ValueError(f"REC-006 media checksum mismatch: {asset['downloaded_path']}")
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        db_count = connection.execute(
            "SELECT COUNT(*) FROM media_assets WHERE download_status='downloaded-direct-rec006'"
        ).fetchone()[0]
    finally:
        connection.close()
    if db_count != len(captured):
        raise ValueError(f"REC-006 media database mismatch: database={db_count}; inventory={len(captured)}")
    return {"valid": True, "generation": expected_generation, **{k: summary[k] for k in ("attempted", "captured", "failed")}, "inherited": inherited}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create")
    create.add_argument("source", type=Path)
    create.add_argument("destination", type=Path)
    create.add_argument("--workers", type=int, default=12)
    create.add_argument("--timeout", type=int, default=15)
    verify = sub.add_parser("verify")
    verify.add_argument("root", type=Path)
    args = parser.parse_args()
    report = create_generation(args.source, args.destination, args.workers, args.timeout) if args.command == "create" else verify_generation(args.root)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
