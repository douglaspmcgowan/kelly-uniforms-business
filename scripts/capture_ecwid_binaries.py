#!/usr/bin/env python3
"""Capture Ecwid catalog media and downloadable product files from a v2 API snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


FORMAT = "mt-uniforms-ecwid-binary-capture/v1"
SOURCE_FORMAT = "mt-uniforms-ecwid-api-capture/v2"
DEFAULT_API_BASE = "https://app.ecwid.com/api/v3"
TOKEN_ENV = "ECWID_SECRET_TOKEN"
SECRET_QUERY_KEYS = {"token", "access_token", "authorization", "secret"}
MEDIA_HINTS = ("image", "thumbnail", "gallery", "media", "cover")
MIME_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
    "application/pdf": ".pdf",
    "application/zip": ".zip",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_url(value: str) -> str:
    split = urlsplit(value)
    query = [
        (key, item)
        for key, item in parse_qsl(split.query, keep_blank_values=True)
        if key.lower() not in SECRET_QUERY_KEYS
    ]
    return urlunsplit((split.scheme, split.netloc, split.path, urlencode(query), ""))


def _is_media_locator(locator: str, key: str) -> bool:
    lowered = f"{locator}.{key}".lower()
    return any(hint in lowered for hint in MEDIA_HINTS)


def _collect_media(value: object, locator: str, found: dict[str, dict]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_locator = f"{locator}.{key}"
            if (
                isinstance(child, str)
                and child.startswith(("http://", "https://"))
                and _is_media_locator(locator, str(key))
            ):
                safe = _safe_url(child)
                entry = found.setdefault(
                    safe,
                    {"kind": "catalog-media", "request_url": child, "safe_url": safe, "locators": []},
                )
                entry["locators"].append(child_locator)
            else:
                _collect_media(child, child_locator, found)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _collect_media(child, f"{locator}[{index}]", found)


def _read_pages(capture: Path, entity: str) -> list[tuple[Path, dict]]:
    pages = []
    for path in sorted((capture / "api" / entity).glob("offset-*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
            raise ValueError(f"invalid {entity} capture page: {path.name}")
        pages.append((path, payload))
    if not pages:
        raise ValueError(f"Ecwid capture has no {entity} pages")
    return pages


def _download(url: str, token: str | None) -> tuple[bytes, str]:
    headers = {"Accept": "*/*"}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=90) as response:
            if response.status != 200:
                raise ValueError(f"binary download returned HTTP {response.status}")
            mime = response.headers.get_content_type().lower()
            payload = response.read()
    except HTTPError as exc:
        code = exc.code
        exc.close()
        raise ValueError(f"binary download returned HTTP {code}") from exc
    except (URLError, TimeoutError) as exc:
        raise ValueError("binary download failed before a complete response") from exc
    return payload, mime


def _extension(mime: str, url: str) -> str:
    if mime in MIME_EXTENSIONS:
        return MIME_EXTENSIONS[mime]
    suffix = Path(urlsplit(url).path).suffix.lower()
    if suffix and len(suffix) <= 10 and suffix.replace(".", "").isalnum():
        return suffix
    return ".bin"


def capture_binaries(
    capture: Path,
    token: str,
    destination: Path,
    api_base_url: str = DEFAULT_API_BASE,
    captured_at: str | None = None,
) -> dict:
    capture = Path(capture).resolve()
    destination = Path(destination).resolve()
    if not token:
        raise ValueError(f"Ecwid secret token is required through {TOKEN_ENV}")
    if destination.exists():
        raise ValueError("binary capture destination already exists")
    if capture == destination or capture in destination.parents or destination in capture.parents:
        raise ValueError("source capture and destination must be distinct, non-nested paths")
    manifest_path = capture / "capture-manifest.json"
    if not manifest_path.is_file():
        raise ValueError("Ecwid capture manifest is missing")
    source_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        source_manifest.get("schema_version") != SOURCE_FORMAT
        or source_manifest.get("source_system") != "ecwid"
        or not str(source_manifest.get("store_ref", "")).isdigit()
    ):
        raise ValueError("source is not a valid Ecwid v2 capture")
    store_id = str(source_manifest["store_ref"])
    jobs: dict[str, dict] = {}
    for entity in ("products", "categories"):
        for path, page in _read_pages(capture, entity):
            relative = path.relative_to(capture).as_posix()
            for index, item in enumerate(page["items"]):
                _collect_media(item, f"{relative}:items[{index}]", jobs)
                if entity != "products" or not isinstance(item, dict):
                    continue
                product_id = item.get("id")
                files = item.get("files", [])
                if not isinstance(product_id, int) or isinstance(product_id, bool) or not isinstance(files, list):
                    continue
                for file_index, descriptor in enumerate(files):
                    if not isinstance(descriptor, dict):
                        continue
                    file_id = descriptor.get("id")
                    if not isinstance(file_id, int) or isinstance(file_id, bool):
                        raise ValueError(f"product {product_id} file lacks a stable id")
                    identity = f"product-file:{product_id}:{file_id}"
                    jobs[identity] = {
                        "kind": "product-file",
                        "request_url": (
                            f"{api_base_url.rstrip('/')}/{store_id}/products/{product_id}/files/{file_id}"
                        ),
                        "safe_url": (
                            f"{DEFAULT_API_BASE}/{store_id}/products/{product_id}/files/{file_id}"
                        ),
                        "locators": [f"{relative}:items[{index}].files[{file_index}]"],
                        "product_id": product_id,
                        "file_id": file_id,
                        "declared_bytes": descriptor.get("size"),
                        "declared_name": descriptor.get("name"),
                    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.building-{uuid.uuid4().hex}")
    temporary.mkdir(parents=True, exist_ok=False)
    try:
        inventory = []
        for identity, job in sorted(jobs.items()):
            authenticated = job["kind"] == "product-file"
            payload, mime = _download(job["request_url"], token if authenticated else None)
            if job.get("declared_bytes") is not None and int(job["declared_bytes"]) != len(payload):
                raise ValueError(f"product file byte count mismatch: {identity}")
            digest = sha256_bytes(payload)
            suffix = _extension(mime, job["safe_url"])
            if authenticated:
                relative = Path("media/product-files") / str(job["product_id"]) / f"{job['file_id']}{suffix}"
            else:
                relative = Path("media/catalog") / f"{hashlib.sha256(identity.encode()).hexdigest()}{suffix}"
            target = temporary / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            row = {
                "identity": identity,
                "kind": job["kind"],
                "captured_path": relative.as_posix(),
                "sha256": digest,
                "bytes": len(payload),
                "mime_type": mime,
                "status": "captured",
                "locators": sorted(set(job["locators"])),
                "source_url": job["safe_url"],
                "authenticated_request": authenticated,
            }
            if authenticated:
                row.update(
                    {
                        "product_id": job["product_id"],
                        "file_id": job["file_id"],
                        "declared_name": job.get("declared_name"),
                    }
                )
            inventory.append(row)
        inventory_path = temporary / "inventory/binaries.ndjson"
        inventory_path.parent.mkdir(parents=True, exist_ok=True)
        inventory_path.write_text(
            "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in inventory),
            encoding="utf-8",
            newline="\n",
        )
        result = {
            "format": FORMAT,
            "source_capture_schema": SOURCE_FORMAT,
            "source_system": "ecwid",
            "store_ref": store_id,
            "captured_at": captured_at or utc_now(),
            "credential_policy": "bearer-token-environment-only-never-persisted",
            "unique_binaries": len(inventory),
            "catalog_media": sum(row["kind"] == "catalog-media" for row in inventory),
            "product_files": sum(row["kind"] == "product-file" for row in inventory),
            "inventory": {
                "path": "inventory/binaries.ndjson",
                "sha256": sha256_file(inventory_path),
                "bytes": inventory_path.stat().st_size,
            },
        }
        (temporary / "binary-manifest.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        temporary.rename(destination)
        return result
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--api-base-url", default=DEFAULT_API_BASE)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    token = os.environ.get(TOKEN_ENV, "")
    report = capture_binaries(
        args.capture, token, args.destination, api_base_url=args.api_base_url
    )
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
