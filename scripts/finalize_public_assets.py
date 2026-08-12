#!/usr/bin/env python3
"""Extract embedded media and disposition the retired AddThis dependency in REC-007."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import capture_missing_media
import capture_public_runtime
import recovery_package
import upgrade_commerce_schema


MEDIA_INVENTORY = Path("public-site/media-inventory.json")
RUNTIME_INVENTORY = Path("public-site/runtime-assets/inventory.json")
ADDDTHIS_EVIDENCE = Path("public-evidence/addthis-service-disposition.json")
ORACLE_RETIREMENT_URL = "https://community.oracle.com/customerconnect/discussion/673943/oracle-has-made-the-business-decision-to-terminate-all-addthis-services-effective-as-of-may-31-2023"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def extract_inline_asset(asset: dict, root: Path) -> dict:
    uri = str(asset.get("url", ""))
    if not uri.startswith("data:") or "," not in uri:
        raise ValueError("asset is not a data URI")
    header, encoded = uri.split(",", 1)
    metadata = header[5:].split(";")
    content_type = metadata[0] or "application/octet-stream"
    if "base64" not in metadata[1:]:
        raise ValueError("data URI is not base64 encoded")
    payload = base64.b64decode(encoded, validate=True)
    extension = {"image/png": ".png", "image/jpeg": ".jpg", "image/gif": ".gif"}.get(content_type, ".bin")
    url_digest = hashlib.sha256(uri.encode("utf-8")).hexdigest()
    relative = Path("public-site/media") / f"{url_digest}{extension}"
    output = Path(root) / relative
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(payload)
    return {
        "download_status": "embedded-extracted-rec007",
        "downloaded_path": relative.as_posix(),
        "content_type": content_type,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "acquisition": "embedded-data-uri",
        "captured_at": utc_now(),
    }


def _package_tools(root: Path) -> None:
    sources = [
        Path(__file__), Path(capture_missing_media.__file__), Path(capture_public_runtime.__file__),
        Path(recovery_package.__file__), Path(upgrade_commerce_schema.__file__),
    ]
    tools = root / "tools"
    tools.mkdir(exist_ok=True)
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
                (utc_now(), digest, packaged.stat().st_size, f"REC-007 packaged tool: {source.name}", relative),
            ).rowcount
            if not updated:
                connection.execute(
                    """INSERT INTO source_manifest(system,artifact_type,source_path,captured_at,sha256,bytes,
                    status,notes,source_ref,capture_method,record_count,sensitivity,completeness)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    ("recovery-tooling", "recovery-tool", relative, utc_now(), digest, packaged.stat().st_size,
                     "captured", f"REC-007 packaged tool: {source.name}", f"recovery-tool:{source.name}",
                     "deterministic-copy", 0, "internal", "complete-file"),
                )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def create_generation(source: Path, destination: Path) -> dict:
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError(f"destination already exists; recovery generations are immutable: {destination}")
    shutil.copytree(source, destination)
    media_path = destination / MEDIA_INVENTORY
    media = json.loads(media_path.read_text(encoding="utf-8"))
    inline = [asset for asset in media["assets"] if asset.get("download_status") == "inline-or-unsupported"]
    for asset in inline:
        asset.update(extract_inline_asset(asset, destination))
    media["inline_extracted_binaries"] = len(inline)
    media["complete_public_media_status"] = "all-url-and-embedded-binaries-preserved"
    media_path.write_text(json.dumps(media, indent=2) + "\n", encoding="utf-8", newline="\n")

    runtime = json.loads((destination / RUNTIME_INVENTORY).read_text(encoding="utf-8"))
    failures = runtime.get("direct_capture_failures", [])
    addthis = next((item for item in failures if "s7.addthis.com/js/300/addthis_widget.js" in item.get("url", "")), None)
    if addthis is None:
        raise ValueError("expected discontinued AddThis reference is missing")
    disposition = {
        "captured_at": utc_now(),
        "referenced_url": addthis["url"],
        "source_pages": addthis.get("pages", []),
        "direct_capture_result": addthis.get("reason"),
        "status": "retired-external-dependency-no-current-binary",
        "vendor": "Oracle AddThis",
        "vendor_termination_effective": "2023-05-31",
        "authoritative_source": ORACLE_RETIREMENT_URL,
        "archive_lookup": "bounded Internet Archive CDX requests timed out without response on 2026-08-10",
        "rebuild_guidance": "Remove the dead reference; do not fabricate or re-enable discontinued tracking code.",
    }
    evidence_path = destination / ADDDTHIS_EVIDENCE
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(disposition, indent=2) + "\n", encoding="utf-8", newline="\n")

    connection = sqlite3.connect(destination / recovery_package.DATABASE_FILE)
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("BEGIN IMMEDIATE")
        for asset in inline:
            connection.execute(
                """UPDATE media_assets SET download_status=?,downloaded_path=?,content_type=?,sha256=?
                   WHERE media_id=?""",
                (asset["download_status"], asset["downloaded_path"], asset["content_type"], asset["sha256"], asset["media_id"]),
            )
            connection.execute(
                """INSERT INTO source_manifest(system,artifact_type,source_path,captured_at,sha256,bytes,status,
                notes,source_ref,source_uri,capture_method,record_count,sensitivity,completeness)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                ("public-storefront", "embedded-media-binary", asset["downloaded_path"], asset["captured_at"],
                 asset["sha256"], asset["bytes"], "captured", "REC-007 extracted embedded data URI",
                 f"media:{asset['media_id']}", "data-uri:sha256:" + hashlib.sha256(asset["url"].encode()).hexdigest(),
                 "base64-decode", 1, "public", "complete-binary"),
            )
        for relative, artifact_type, source_uri in [
            (MEDIA_INVENTORY.as_posix(), "media-inventory", None),
            (ADDDTHIS_EVIDENCE.as_posix(), "dependency-disposition", ORACLE_RETIREMENT_URL),
        ]:
            path = destination / relative
            digest = recovery_package.sha256_file(path)
            updated = connection.execute(
                "UPDATE source_manifest SET captured_at=?,sha256=?,bytes=?,notes=? WHERE source_path=?",
                (utc_now(), digest, path.stat().st_size, f"REC-007 {artifact_type}", relative),
            ).rowcount
            if not updated:
                connection.execute(
                    """INSERT INTO source_manifest(system,artifact_type,source_path,captured_at,sha256,bytes,status,
                    notes,source_ref,source_uri,capture_method,record_count,sensitivity,completeness)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    ("public-storefront", artifact_type, relative, utc_now(), digest, path.stat().st_size, "captured",
                     f"REC-007 {artifact_type}", f"rec007:{artifact_type}", source_uri, "documented-observation", 1,
                     "public", "complete-artifact"),
                )
        connection.executemany(
            "INSERT INTO recovery_metadata(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            {"generation": "REC-007", "parent_generation": "REC-006", "inline_media_extracted": str(len(inline)),
             "addthis_dependency_status": disposition["status"]}.items(),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    manifest_path = destination / "package-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["generation"] = "REC-007"
    manifest["parent_generation"] = "REC-006"
    manifest["generated_at"] = utc_now()
    manifest["public_media_completion"] = {"url_backed_exact": 1541, "embedded_exact": len(inline), "total_exact": 1541 + len(inline)}
    manifest["retired_dependencies"] = [{"name": "Oracle AddThis", "status": disposition["status"], "evidence": ADDDTHIS_EVIDENCE.as_posix()}]
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    _package_tools(destination)
    recovery_package.write_checksums(destination)
    return verify_generation(destination)


def verify_generation(root: Path) -> dict:
    root = Path(root).resolve()
    inherited = capture_missing_media.verify_generation(root, expected_generation="REC-007")
    media = json.loads((root / MEDIA_INVENTORY).read_text(encoding="utf-8"))
    extracted = [asset for asset in media["assets"] if asset.get("download_status") == "embedded-extracted-rec007"]
    for asset in extracted:
        path = root / asset["downloaded_path"]
        if not path.is_file() or recovery_package.sha256_file(path) != asset["sha256"]:
            raise ValueError(f"REC-007 embedded media checksum mismatch: {asset['downloaded_path']}")
    disposition = json.loads((root / ADDDTHIS_EVIDENCE).read_text(encoding="utf-8"))
    if disposition.get("status") != "retired-external-dependency-no-current-binary":
        raise ValueError("AddThis retirement disposition is missing")
    connection = sqlite3.connect(root / recovery_package.DATABASE_FILE)
    try:
        db_count = connection.execute(
            "SELECT COUNT(*) FROM media_assets WHERE download_status='embedded-extracted-rec007'"
        ).fetchone()[0]
    finally:
        connection.close()
    if db_count != len(extracted):
        raise ValueError(f"embedded media database mismatch: database={db_count}; inventory={len(extracted)}")
    return {"valid": True, "generation": "REC-007", "embedded_captured": len(extracted),
            "addthis_status": disposition["status"], "inherited": inherited}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create")
    create.add_argument("source", type=Path)
    create.add_argument("destination", type=Path)
    verify = sub.add_parser("verify")
    verify.add_argument("root", type=Path)
    args = parser.parse_args()
    report = create_generation(args.source, args.destination) if args.command == "create" else verify_generation(args.root)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
