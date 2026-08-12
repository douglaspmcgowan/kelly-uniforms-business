#!/usr/bin/env python3
"""Capture Ecwid core and adjunct business resources atomically."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import time
import uuid
from pathlib import Path
from typing import NamedTuple
from urllib.parse import urlencode

import capture_ecwid_api as v1


CAPTURE_SCHEMA_VERSION = "mt-uniforms-ecwid-api-capture/v2"
DEFAULT_BASE_URL = v1.DEFAULT_BASE_URL
TOKEN_ENV = v1.TOKEN_ENV
REQUIRED_SCOPES = (
    "read_store_profile",
    "read_store_profile_extended",
    "read_store_limits",
    "read_catalog",
    "read_customers",
    "read_customers_extrafields",
    "read_orders",
    "read_staff",
    "read_discount_coupons",
    "read_promotion",
)


class AdjunctSpec(NamedTuple):
    entity: str
    path: str
    mode: str
    id_field: str
    collection_key: str | None = None
    query: tuple[tuple[str, str], ...] = ()


ADJUNCT_ENDPOINTS = (
    AdjunctSpec("product_types", "classes", "array", "id"),
    AdjunctSpec("customer_groups", "customer_groups", "paginated", "id"),
    AdjunctSpec(
        "customer_extra_fields",
        "store_extrafields/customers",
        "collection",
        "key",
        "items",
    ),
    AdjunctSpec(
        "abandoned_carts", "carts", "paginated", "cartId", query=(("showHidden", "true"),)
    ),
    AdjunctSpec("staff", "staff", "collection", "id", "staffList"),
    AdjunctSpec("discount_coupons", "discount_coupons", "paginated", "id"),
    AdjunctSpec("promotions", "promotions", "paginated", "id"),
)


def _validate_unique(items: object, spec: AdjunctSpec) -> set[str]:
    if not isinstance(items, list):
        raise ValueError(f"{spec.entity} collection must be an array")
    seen = set()
    for item in items:
        if not isinstance(item, dict) or spec.id_field not in item:
            raise ValueError(f"{spec.entity} item lacks stable {spec.id_field}")
        item_id = str(item[spec.id_field])
        if item_id in seen:
            raise ValueError(f"duplicate {spec.entity} {spec.id_field}: {item_id}")
        seen.add(item_id)
    return seen


def _capture_collection(
    root: Path,
    store_root: str,
    token: str,
    spec: AdjunctSpec,
) -> tuple[dict, list[dict]]:
    url = f"{store_root}/{spec.path}"
    if spec.query:
        url += "?" + urlencode(spec.query)
    payload = v1._request_json(url, token)
    if spec.mode == "array":
        items = payload
    else:
        if not isinstance(payload, dict) or spec.collection_key not in payload:
            raise ValueError(f"{spec.entity} response lacks {spec.collection_key}")
        items = payload[spec.collection_key]
    seen = _validate_unique(items, spec)
    path = root / f"api/{spec.entity}/collection.json"
    v1._write_json(path, v1.scrub_secrets(payload))
    return {"records": len(seen), "pages": 1}, [v1._artifact(root, path, spec.entity, len(seen))]


def _capture_paginated(
    root: Path,
    store_root: str,
    token: str,
    spec: AdjunctSpec,
    min_interval_seconds: float,
) -> tuple[dict, list[dict]]:
    expected_offset = 0
    expected_total = None
    seen = set()
    artifacts = []
    pages = 0
    while True:
        query = [*spec.query, ("limit", "100"), ("offset", str(expected_offset))]
        payload = v1._request_json(f"{store_root}/{spec.path}?{urlencode(query)}", token)
        if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
            raise ValueError(f"{spec.entity} page must contain an items array")
        for field in ("total", "count", "offset", "limit"):
            if not isinstance(payload.get(field), int) or isinstance(payload.get(field), bool):
                raise ValueError(f"{spec.entity} page {field} must be an integer")
        items = payload["items"]
        if payload["offset"] != expected_offset or payload["count"] != len(items):
            raise ValueError(f"{spec.entity} page envelope does not match requested offset/count")
        if expected_total is None:
            expected_total = payload["total"]
        elif payload["total"] != expected_total:
            raise ValueError(f"{spec.entity} total changed during capture")
        page_ids = _validate_unique(items, spec)
        duplicate = seen.intersection(page_ids)
        if duplicate:
            raise ValueError(
                f"duplicate {spec.entity} {spec.id_field}: {sorted(duplicate)[0]}"
            )
        seen.update(page_ids)
        path = root / f"api/{spec.entity}/offset-{expected_offset:06d}.json"
        v1._write_json(path, v1.scrub_secrets(payload))
        artifacts.append(v1._artifact(root, path, spec.entity, len(items)))
        pages += 1
        if expected_offset + len(items) >= expected_total:
            break
        if not items:
            raise ValueError(f"{spec.entity} returned an empty page before total")
        expected_offset += len(items)
        if min_interval_seconds:
            time.sleep(min_interval_seconds)
    if len(seen) != expected_total:
        raise ValueError(f"{spec.entity} unique records do not reconcile to total")
    return {"records": len(seen), "pages": pages}, artifacts


def capture_store_complete(
    store_id: str,
    token: str,
    destination: Path,
    base_url: str = DEFAULT_BASE_URL,
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
        for spec in v1.CORE_ENDPOINTS:
            if spec.mode == "singleton":
                report, captured = v1._capture_singleton(temporary, store_root, token, spec)
            else:
                report, captured = v1._capture_paginated(
                    temporary, store_root, token, spec, min_interval_seconds
                )
            entities[spec.entity] = report
            artifacts.extend(captured)
            if min_interval_seconds:
                time.sleep(min_interval_seconds)
        for spec in ADJUNCT_ENDPOINTS:
            if spec.mode == "paginated":
                report, captured = _capture_paginated(
                    temporary, store_root, token, spec, min_interval_seconds
                )
            else:
                report, captured = _capture_collection(temporary, store_root, token, spec)
            entities[spec.entity] = report
            artifacts.extend(captured)
            if min_interval_seconds:
                time.sleep(min_interval_seconds)
        manifest = {
            "schema_version": CAPTURE_SCHEMA_VERSION,
            "source_system": "ecwid",
            "store_ref": str(store_id),
            "captured_at": captured_at or v1.utc_now(),
            "base_url": DEFAULT_BASE_URL,
            "credential_policy": "bearer-token-environment-only-never-persisted",
            "required_scopes": list(REQUIRED_SCOPES),
            "entities": entities,
            "artifacts": artifacts,
        }
        v1._write_json(temporary / "capture-manifest.json", manifest)
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
    report = capture_store_complete(
        args.store_id, token, args.destination, base_url=args.base_url
    )
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
