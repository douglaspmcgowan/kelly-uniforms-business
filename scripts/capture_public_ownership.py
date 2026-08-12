#!/usr/bin/env python3
"""Capture public infrastructure evidence and import it into a recovery package."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import socket
import ssl
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import recovery_package


DNS_TYPES = ("A", "AAAA", "CNAME", "MX", "NS", "SOA", "TXT", "CAA")
SAFE_RESPONSE_HEADERS = {
    "cache-control",
    "content-length",
    "content-type",
    "date",
    "location",
    "server",
    "strict-transport-security",
    "x-powered-by",
}
USER_AGENT = "MT-Uniforms-Recovery/1.0 (public continuity capture)"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sanitize_headers(headers) -> dict[str, str]:
    items = headers.items() if hasattr(headers, "items") else headers
    return {
        str(name).lower(): str(value)
        for name, value in items
        if str(name).lower() in SAFE_RESPONSE_HEADERS
    }


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read())


def fetch_http_evidence(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
            return {
                "requested_url": url,
                "final_url": response.geturl(),
                "status": response.status,
                "headers": sanitize_headers(response.headers),
                "body_bytes": len(body),
                "body_sha256": sha256_bytes(body),
            }
    except urllib.error.HTTPError as error:
        body = error.read()
        return {
            "requested_url": url,
            "final_url": error.geturl(),
            "status": error.code,
            "headers": sanitize_headers(error.headers),
            "body_bytes": len(body),
            "body_sha256": sha256_bytes(body),
        }


def capture_tls(hostname: str) -> dict:
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443), timeout=30) as raw_socket:
        with context.wrap_socket(raw_socket, server_hostname=hostname) as tls_socket:
            certificate = tls_socket.getpeercert()
            der = tls_socket.getpeercert(binary_form=True)
            return {
                "hostname": hostname,
                "protocol": tls_socket.version(),
                "cipher": list(tls_socket.cipher() or ()),
                "subject": certificate.get("subject"),
                "issuer": certificate.get("issuer"),
                "serialNumber": certificate.get("serialNumber"),
                "notBefore": certificate.get("notBefore"),
                "notAfter": certificate.get("notAfter"),
                "subjectAltName": certificate.get("subjectAltName"),
                "certificate_der_sha256": sha256_bytes(der),
            }


def dns_query(name: str, record_type: str) -> dict:
    query = urllib.parse.urlencode({"name": name, "type": record_type})
    return fetch_json(f"https://dns.google/resolve?{query}")


def normalize_dns_observations(
    subject: str, record_type: str, response: dict, source_key: str
) -> list[dict]:
    observations = []
    for answer in response.get("Answer", []):
        observations.append(
            {
                "source_key": source_key,
                "subject": subject,
                "record_type": record_type,
                "name": answer.get("name"),
                "value": answer.get("data"),
                "ttl": answer.get("TTL"),
                "confidence": "resolver-observed",
                "inference": 0,
            }
        )
    return observations


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_capture_bundle(
    root: Path,
    domain: str,
    captured_at: str,
    artifacts: dict[str, object],
    observations: list[dict],
) -> Path:
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    artifact_rows = []
    for relative, payload in sorted(artifacts.items()):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = _json_bytes(payload)
        path.write_bytes(raw)
        artifact_rows.append(
            {
                "path": relative.replace("\\", "/"),
                "bytes": len(raw),
                "sha256": sha256_bytes(raw),
            }
        )
    manifest = {
        "schema_version": "1.0.0",
        "domain": domain,
        "captured_at": captured_at,
        "classification": "public-business-continuity-evidence",
        "artifacts": artifact_rows,
        "observations": observations,
        "limits": [
            "Public configuration evidence does not prove account, billing, or legal control.",
            "Response headers are allowlisted so cookies and authorization material are never stored.",
        ],
    }
    destination = root / "capture-manifest.json"
    destination.write_bytes(_json_bytes(manifest))
    return destination


def append_business_facts(root: Path, facts: list[dict]) -> Path:
    root = Path(root).resolve()
    manifest_path = root / "capture-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    relative = "business/business-footprint.json"
    payload = {
        "captured_at": manifest["captured_at"],
        "entity": {
            "entity_id": "mt-uniforms-llc",
            "entity_type": "limited-liability-company",
            "canonical_name": "MT UNIFORMS LLC",
            "jurisdiction": "US-PA",
            "lifecycle_status": "publicly-observed-active",
        },
        "facts": facts,
    }
    raw = _json_bytes(payload)
    destination = root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(raw)
    manifest["artifacts"] = [
        item for item in manifest["artifacts"] if item["path"] != relative
    ]
    manifest["artifacts"].append(
        {"path": relative, "bytes": len(raw), "sha256": sha256_bytes(raw)}
    )
    manifest["artifacts"].sort(key=lambda item: item["path"])
    manifest["observations"] = [
        item
        for item in manifest["observations"]
        if not (
            item.get("record_type") == "BUSINESS_FACT"
            and item.get("source_key") == relative
        )
    ]
    for fact in facts:
        manifest["observations"].append(
            {
                "source_key": relative,
                "subject": "mt-uniforms-llc",
                "record_type": "BUSINESS_FACT",
                "fact_type": fact["fact_type"],
                "value": fact["value"],
                "normalized_value": fact.get("normalized_value"),
                "source_uri": fact["source_uri"],
                "verification_status": fact["verification_status"],
                "confidence": fact["confidence"],
            }
        )
    manifest_path.write_bytes(_json_bytes(manifest))
    return manifest_path


def capture(root: Path, domain: str) -> Path:
    captured_at = utc_now()
    artifacts: dict[str, object] = {}
    observations: list[dict] = []
    rdap_url = f"https://rdap.verisign.com/com/v1/domain/{domain.upper()}"
    rdap = fetch_json(rdap_url)
    artifacts[f"rdap/{domain}.json"] = {
        "source_uri": rdap_url,
        "captured_at": captured_at,
        "response": rdap,
    }
    observations.append(
        {
            "source_key": f"rdap/{domain}.json",
            "subject": domain,
            "record_type": "RDAP",
            "name": rdap.get("ldhName", domain),
            "value": {
                "status": rdap.get("status", []),
                "events": rdap.get("events", []),
                "nameservers": [item.get("ldhName") for item in rdap.get("nameservers", [])],
            },
            "confidence": "registry-observed",
            "inference": 0,
        }
    )

    dns_responses = []
    for host in (domain, f"www.{domain}"):
        for record_type in DNS_TYPES:
            response = dns_query(host, record_type)
            source_key = f"dns/{host}-{record_type.lower()}.json"
            payload = {
                "source_uri": f"https://dns.google/resolve?{urllib.parse.urlencode({'name': host, 'type': record_type})}",
                "captured_at": captured_at,
                "response": response,
            }
            artifacts[source_key] = payload
            dns_responses.append(payload)
            observations.extend(
                normalize_dns_observations(host, record_type, response, source_key)
            )
    artifacts["dns/summary.json"] = {"captured_at": captured_at, "queries": dns_responses}

    tls = capture_tls(domain)
    artifacts[f"tls/{domain}.json"] = {
        "source_uri": f"tls://{domain}:443",
        "captured_at": captured_at,
        "response": tls,
    }
    observations.append(
        {
            "source_key": f"tls/{domain}.json",
            "subject": domain,
            "record_type": "TLS",
            "name": domain,
            "value": tls,
            "confidence": "endpoint-observed",
            "inference": 0,
        }
    )

    for url in (
        f"http://{domain}/",
        f"https://{domain}/",
        f"http://www.{domain}/",
        f"https://www.{domain}/",
    ):
        evidence = fetch_http_evidence(url)
        key = "http/" + urllib.parse.urlsplit(url).netloc + "-" + urllib.parse.urlsplit(url).scheme + ".json"
        artifacts[key] = {
            "source_uri": url,
            "captured_at": captured_at,
            "response": evidence,
        }
        observations.append(
            {
                "source_key": key,
                "subject": urllib.parse.urlsplit(url).netloc,
                "record_type": "HTTP",
                "name": url,
                "value": evidence,
                "confidence": "endpoint-observed",
                "inference": 0,
            }
        )
    return write_capture_bundle(root, domain, captured_at, artifacts, observations)


def import_capture(package_root: Path, capture_root: Path) -> dict:
    package_root = Path(package_root).resolve()
    capture_root = Path(capture_root).resolve()
    manifest = json.loads((capture_root / "capture-manifest.json").read_text(encoding="utf-8"))
    destination = package_root / "raw" / "public-ownership"
    if destination.exists():
        raise ValueError("public ownership evidence already exists in this immutable generation")
    shutil.copytree(capture_root, destination)
    database = package_root / recovery_package.DATABASE_FILE
    connection = sqlite3.connect(database)
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("BEGIN IMMEDIATE")
        recovery_package.ensure_provenance_schema(connection)
        source_ids: dict[str, int] = {}
        for artifact in manifest["artifacts"]:
            relative = f"raw/public-ownership/{artifact['path']}"
            payload = json.loads((package_root / relative).read_text(encoding="utf-8"))
            cursor = connection.execute(
                """INSERT INTO source_manifest(
                    system, artifact_type, source_path, captured_at, sha256, bytes, status, notes,
                    source_ref, source_uri, capture_method, record_count, sensitivity, completeness
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    "public-infrastructure",
                    "public-observation-json",
                    relative,
                    manifest["captured_at"],
                    artifact["sha256"],
                    artifact["bytes"],
                    "captured",
                    "Public evidence; proves observed configuration only, not account control.",
                    "REC-003",
                    payload.get("source_uri"),
                    "stdlib HTTPS/TLS plus Google Public DNS resolver",
                    1,
                    "public",
                    "complete-for-recorded-query",
                ),
            )
            source_ids[artifact["path"]] = cursor.lastrowid
        domain = manifest["domain"]
        for asset_id, asset_type, identifier, purpose in (
            ("domain-apex", "domain", domain, "public website and domain mail"),
            ("hostname-www", "hostname", f"www.{domain}", "public storefront hostname"),
            ("tls-apex", "tls-certificate", f"{domain}:443", "HTTPS identity"),
        ):
            connection.execute(
                "INSERT OR IGNORE INTO infrastructure_assets VALUES(?,?,?,?,?,?)",
                (asset_id, asset_type, identifier, purpose, None, "observed-active"),
            )
        for observation in manifest["observations"]:
            if observation["record_type"] == "BUSINESS_FACT":
                continue
            subject = observation["subject"]
            asset_id = "hostname-www" if subject.startswith("www.") else "domain-apex"
            if observation["record_type"] == "TLS":
                asset_id = "tls-apex"
            source_id = source_ids[observation["source_key"]]
            connection.execute(
                """INSERT INTO infrastructure_observations(
                    asset_id, observation_type, observed_value_json, observed_at,
                    verification_status, source_id
                ) VALUES(?,?,?,?,?,?)""",
                (
                    asset_id,
                    observation["record_type"],
                    json.dumps(observation, sort_keys=True),
                    manifest["captured_at"],
                    "publicly-observed",
                    source_id,
                ),
            )
        business_observations = [
            item for item in manifest["observations"] if item["record_type"] == "BUSINESS_FACT"
        ]
        if business_observations:
            business_payload = json.loads(
                (destination / "business" / "business-footprint.json").read_text(encoding="utf-8")
            )
            entity = business_payload["entity"]
            connection.execute(
                "INSERT OR REPLACE INTO business_entities VALUES(?,?,?,?,?,?)",
                (
                    entity["entity_id"],
                    entity["entity_type"],
                    entity["canonical_name"],
                    entity.get("jurisdiction"),
                    entity.get("registration_identifier"),
                    entity["lifecycle_status"],
                ),
            )
            for observation in business_observations:
                connection.execute(
                    """INSERT INTO business_facts(
                        entity_id, fact_type, value_text, normalized_value, observed_at,
                        verification_status, confidence, source_id
                    ) VALUES(?,?,?,?,?,?,?,?)""",
                    (
                        observation["subject"],
                        observation["fact_type"],
                        observation["value"],
                        observation.get("normalized_value"),
                        manifest["captured_at"],
                        observation["verification_status"],
                        observation["confidence"],
                        source_ids[observation["source_key"]],
                    ),
                )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    package_manifest_path = package_root / "package-manifest.json"
    package_manifest = json.loads(package_manifest_path.read_text(encoding="utf-8"))
    package_manifest["public_ownership"] = {
        "status": "public-infrastructure-evidence-captured",
        "captured_at": manifest["captured_at"],
        "domain": manifest["domain"],
        "artifact_count": len(manifest["artifacts"]),
        "observation_count": len(manifest["observations"]),
        "account_control_status": "unverified",
    }
    package_manifest_path.write_text(
        json.dumps(package_manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    recovery_package.write_checksums(package_root)
    return recovery_package.verify_package(package_root)


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    capture_parser = subparsers.add_parser("capture")
    capture_parser.add_argument("output", type=Path)
    capture_parser.add_argument("--domain", default="mtuniforms.com")
    import_parser = subparsers.add_parser("import")
    import_parser.add_argument("package", type=Path)
    import_parser.add_argument("capture", type=Path)
    business_parser = subparsers.add_parser("append-business")
    business_parser.add_argument("capture", type=Path)
    business_parser.add_argument("facts", type=Path)
    args = parser.parse_args()
    if args.command == "capture":
        print(capture(args.output, args.domain))
    elif args.command == "append-business":
        facts = json.loads(args.facts.read_text(encoding="utf-8"))
        print(append_business_facts(args.capture, facts))
    else:
        print(json.dumps(import_capture(args.package, args.capture), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
