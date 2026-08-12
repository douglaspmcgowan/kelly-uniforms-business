#!/usr/bin/env python3
"""Atomically capture value-safe, paginated Ecwid API evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


CAPTURE_SCHEMA_VERSION = "mt-uniforms-ecwid-api-capture/v1"
DEFAULT_BASE_URL = "https://app.ecwid.com/api/v3"
TOKEN_ENV = "ECWID_SECRET_TOKEN"
SECRET_KEYS = {
    "adminurl", "customerurl", "authorization", "accesstoken", "access_token",
    "secret", "secret_token", "password", "cookie", "session",
}
SECRET_QUERY_KEYS = {"token", "access_token", "authorization", "secret"}


class EndpointSpec(NamedTuple):
    entity: str
    path: str
    mode: str
    query: tuple[tuple[str, str], ...] = ()


CORE_ENDPOINTS = (
    EndpointSpec(
        "profile",
        "profile",
        "singleton",
        (
            ("showExtendedInfo", "true"),
            ("getReportAvailabilityStatus", "true"),
            ("getStoreVertical", "true"),
            ("getFeaturesByPlans", "true"),
        ),
    ),
    EndpointSpec("products", "products", "paginated"),
    EndpointSpec(
        "categories",
        "categories",
        "paginated",
        (("hidden_categories", "true"), ("productIds", "true")),
    ),
    EndpointSpec("customers", "customers", "paginated"),
    EndpointSpec("orders", "orders", "paginated"),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _scrub_url(value: str) -> str:
    try:
        split = urlsplit(value)
    except ValueError:
        return value
    if not split.scheme or not split.netloc or not split.query:
        return value
    safe_query = [
        (key, item)
        for key, item in parse_qsl(split.query, keep_blank_values=True)
        if key.lower() not in SECRET_QUERY_KEYS
    ]
    return urlunsplit((split.scheme, split.netloc, split.path, urlencode(safe_query), split.fragment))


def scrub_secrets(value: object) -> object:
    if isinstance(value, list):
        return [scrub_secrets(item) for item in value]
    if isinstance(value, dict):
        cleaned = {}
        for key, child in value.items():
            if str(key).replace("-", "_").lower() in SECRET_KEYS:
                continue
            cleaned[key] = scrub_secrets(child)
        return cleaned
    if isinstance(value, str):
        return _scrub_url(value)
    return value


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _request_json(url: str, token: str, retries: int = 4) -> object:
    for attempt in range(retries + 1):
        request = Request(
            url,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        )
        try:
            with urlopen(request, timeout=60) as response:
                if response.status != 200:
                    raise ValueError(f"Ecwid API returned HTTP {response.status}")
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code == 429 and attempt < retries:
                retry_after = float(exc.headers.get("Retry-After", "1"))
                time.sleep(max(retry_after, 0))
                continue
            raise ValueError(f"Ecwid API request failed with HTTP {exc.code}") from exc
        except (URLError, TimeoutError) as exc:
            raise ValueError("Ecwid API request failed before a complete response") from exc
    raise ValueError("Ecwid API retry budget exhausted")


def _artifact(root: Path, path: Path, entity: str, records: int) -> dict:
    return {
        "relative_path": path.relative_to(root).as_posix(),
        "entity": entity,
        "records": records,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "sensitivity": "restricted-value-safe",
    }


def _capture_singleton(
    root: Path,
    store_root: str,
    token: str,
    spec: EndpointSpec,
) -> tuple[dict, list[dict]]:
    url = f"{store_root}/{spec.path}"
    if spec.query:
        url += "?" + urlencode(spec.query)
    payload = _request_json(url, token)
    if not isinstance(payload, dict):
        raise ValueError(f"{spec.entity} response must be a JSON object")
    path = root / f"api/{spec.entity}/singleton.json"
    _write_json(path, scrub_secrets(payload))
    return {"records": 1, "pages": 1}, [_artifact(root, path, spec.entity, 1)]


def _capture_paginated(
    root: Path,
    store_root: str,
    token: str,
    spec: EndpointSpec,
    min_interval_seconds: float,
) -> tuple[dict, list[dict]]:
    expected_offset = 0
    expected_total = None
    seen_ids = set()
    artifacts = []
    pages = 0
    while True:
        query = [*spec.query, ("limit", "100"), ("offset", str(expected_offset))]
        payload = _request_json(f"{store_root}/{spec.path}?{urlencode(query)}", token)
        if not isinstance(payload, dict):
            raise ValueError(f"{spec.entity} page must be a JSON object")
        items = payload.get("items")
        if not isinstance(items, list):
            raise ValueError(f"{spec.entity} page items must be an array")
        for field in ("total", "count", "offset", "limit"):
            if not isinstance(payload.get(field), int) or isinstance(payload.get(field), bool):
                raise ValueError(f"{spec.entity} page {field} must be an integer")
        if payload["offset"] != expected_offset or payload["count"] != len(items):
            raise ValueError(f"{spec.entity} page envelope does not match requested offset/count")
        if expected_total is None:
            expected_total = payload["total"]
        elif payload["total"] != expected_total:
            raise ValueError(f"{spec.entity} total changed during capture")
        for item in items:
            if not isinstance(item, dict) or "id" not in item:
                raise ValueError(f"{spec.entity} item lacks a stable id")
            item_id = str(item["id"])
            if item_id in seen_ids:
                raise ValueError(f"duplicate {spec.entity} id: {item_id}")
            seen_ids.add(item_id)
        path = root / f"api/{spec.entity}/offset-{expected_offset:06d}.json"
        _write_json(path, scrub_secrets(payload))
        artifacts.append(_artifact(root, path, spec.entity, len(items)))
        pages += 1
        if expected_offset + len(items) >= expected_total:
            break
        if not items:
            raise ValueError(f"{spec.entity} returned an empty page before total")
        expected_offset += len(items)
        if min_interval_seconds:
            time.sleep(min_interval_seconds)
    if len(seen_ids) != expected_total:
        raise ValueError(f"{spec.entity} unique records do not reconcile to total")
    return {"records": len(seen_ids), "pages": pages}, artifacts


def capture_store(
    store_id: str,
    token: str,
    destination: Path,
    base_url: str = DEFAULT_BASE_URL,
    endpoint_specs: tuple[EndpointSpec, ...] = CORE_ENDPOINTS,
    min_interval_seconds: float = 0.12,
    captured_at: str | None = None,
) -> dict:
    if not str(store_id).isdigit():
        raise ValueError("Ecwid store ID must contain digits only")
    if not token:
        raise ValueError(f"Ecwid secret token is required through {TOKEN_ENV}")
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError(f"capture destination already exists: {destination}")
    temporary = destination.with_name(f".{destination.name}.building-{uuid.uuid4().hex}")
    temporary.mkdir(parents=True, exist_ok=False)
    try:
        entities = {}
        artifacts = []
        store_root = f"{base_url.rstrip('/')}/{store_id}"
        for spec in endpoint_specs:
            if spec.mode == "singleton":
                report, captured = _capture_singleton(temporary, store_root, token, spec)
            elif spec.mode == "paginated":
                report, captured = _capture_paginated(
                    temporary, store_root, token, spec, min_interval_seconds
                )
            else:
                raise ValueError(f"unsupported endpoint mode: {spec.mode}")
            entities[spec.entity] = report
            artifacts.extend(captured)
            if min_interval_seconds:
                time.sleep(min_interval_seconds)
        manifest = {
            "schema_version": CAPTURE_SCHEMA_VERSION,
            "source_system": "ecwid",
            "store_ref": str(store_id),
            "captured_at": captured_at or utc_now(),
            "base_url": DEFAULT_BASE_URL,
            "credential_policy": "bearer-token-environment-only-never-persisted",
            "entities": entities,
            "artifacts": artifacts,
        }
        _write_json(temporary / "capture-manifest.json", manifest)
        temporary.rename(destination)
        return manifest
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--store-id", required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    token = os.environ.get(TOKEN_ENV, "")
    report = capture_store(args.store_id, token, args.destination, args.base_url)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
