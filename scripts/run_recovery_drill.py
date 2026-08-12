#!/usr/bin/env python3
"""Exercise the recovery model with synthetic agency-order data in a disposable copy."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import uuid
from pathlib import Path

import package_binary_ready_generation
import package_import_ready_generation
import recovery_package


RUN_ID = "synthetic-restore-drill-v1"
CAPTURED_AT = "2026-08-10T00:00:00Z"
TABLES = (
    "account_members",
    "business_accounts",
    "catalog_products",
    "catalog_variants",
    "commerce_order_lines",
    "commerce_orders",
    "entitlements",
    "fulfillment_lines",
    "fulfillments",
    "invoices",
    "line_customizations",
    "payments",
    "price_list_entries",
    "price_lists",
    "production_operations",
    "production_work_orders",
    "purchase_orders",
    "refunds",
    "return_lines",
    "returns",
    "tax_exemptions",
    "audit_events",
)


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _target(table: str, record_id: str, **values: object) -> dict:
    return {"table": table, "record_id": record_id, "values": values}


def _source_row(source_record_id: str, locator: str, entity: str, rows: list[dict]) -> dict:
    return {
        "source_record_id": source_record_id,
        "source_locator": locator,
        "entity": entity,
        "record": {
            "synthetic": True,
            "fixture_version": "representative-agency-order-v1",
            "native_reference": source_record_id,
        },
        "normalized_rows": rows,
    }


def _fixture_rows() -> list[dict]:
    account = "opencart:drill:account:1"
    member = "opencart:drill:member:1"
    product = "opencart:drill:product:1"
    variant = "opencart:drill:variant:1"
    price_list = "opencart:drill:price-list:1"
    order = "opencart:drill:order:1001"
    line = "opencart:drill:order-line:1001:1"
    invoice = "opencart:drill:invoice:1001"
    payment = "opencart:drill:payment:1001"
    refund = "opencart:drill:refund:1001:1"
    fulfillment = "opencart:drill:fulfillment:1001"
    returned = "opencart:drill:return:1001:1"
    work_order = "opencart:drill:work-order:1001:1"

    return [
        _source_row(
            "customer:synthetic-1",
            "table:customer/pk:synthetic-1",
            "customers",
            [
                _target(
                    "business_accounts",
                    account,
                    account_type="agency",
                    name="Synthetic Public Safety Agency",
                    tax_exempt=1,
                    payment_terms_days=30,
                    lifecycle_status="active",
                ),
                _target(
                    "account_members",
                    member,
                    account_ref=account,
                    display_name="Synthetic Uniform Officer",
                    email="synthetic.invalid@example.invalid",
                    role_name="buyer",
                    lifecycle_status="active",
                ),
                _target(
                    "tax_exemptions",
                    "opencart:drill:tax-exemption:1",
                    account_ref=account,
                    jurisdiction="PA",
                    certificate_ref="synthetic-reference",
                    valid_from="2026-01-01",
                    valid_to=None,
                    status="active",
                ),
                _target(
                    "entitlements",
                    "opencart:drill:entitlement:1",
                    account_ref=account,
                    member_ref=member,
                    entitlement_type="restricted-item-approval",
                    rule_json=_json({"approval_reference_required": True}),
                    status="active",
                ),
            ],
        ),
        _source_row(
            "product:synthetic-1",
            "table:product/pk:synthetic-1",
            "products",
            [
                _target(
                    "catalog_products",
                    product,
                    category_ref=None,
                    name="Synthetic Duty Shirt",
                    brand_name="Synthetic Brand",
                    supplier_name="Synthetic Supplier",
                    description="Synthetic drill fixture; never client data.",
                    lifecycle_status="active",
                ),
                _target(
                    "catalog_variants",
                    variant,
                    product_ref=product,
                    sku="SYNTH-DRILL-001",
                    name="Synthetic Duty Shirt / Large",
                    price_minor=6000,
                    currency="USD",
                    weight_grams=500,
                    lifecycle_status="active",
                ),
            ],
        ),
        _source_row(
            "price-list:synthetic-1",
            "table:product_discount/pk:synthetic-1",
            "price_lists",
            [
                _target(
                    "price_lists",
                    price_list,
                    account_ref=account,
                    name="Synthetic Agency Contract Pricing",
                    currency="USD",
                    valid_from="2026-01-01",
                    valid_to=None,
                    lifecycle_status="active",
                ),
                _target(
                    "price_list_entries",
                    "opencart:drill:price-list-entry:1",
                    price_list_ref=price_list,
                    product_ref=product,
                    variant_ref=variant,
                    price_minor=6000,
                    minimum_quantity=1,
                ),
            ],
        ),
        _source_row(
            "order:synthetic-1001",
            "table:order/pk:synthetic-1001",
            "orders",
            [
                _target(
                    "commerce_orders",
                    order,
                    account_ref=account,
                    member_ref=member,
                    order_number="SYNTHETIC-1001",
                    status="complete",
                    currency="USD",
                    subtotal_minor=12000,
                    tax_minor=0,
                    shipping_minor=500,
                    discount_minor=0,
                    total_minor=12500,
                    placed_at="2026-08-10T00:00:00Z",
                    billing_address_json=_json({"synthetic": True, "region": "PA"}),
                    shipping_address_json=_json({"synthetic": True, "region": "PA"}),
                ),
                _target(
                    "commerce_order_lines",
                    line,
                    order_ref=order,
                    product_ref=product,
                    variant_ref=variant,
                    line_number=1,
                    quantity=2,
                    snapshot_name="Synthetic Duty Shirt / Large",
                    snapshot_sku="SYNTH-DRILL-001",
                    snapshot_description="Synthetic drill fixture",
                    snapshot_options_json=_json({"size": "Large"}),
                    unit_price_minor=6000,
                    tax_minor=0,
                    discount_minor=0,
                    line_total_minor=12000,
                ),
                _target(
                    "line_customizations",
                    "opencart:drill:customization:1001:1",
                    order_line_ref=line,
                    customization_type="embroidery",
                    label="Synthetic name strip",
                    value_text="SYNTHETIC",
                    portable_file_path=None,
                    surcharge_minor=0,
                    production_status="complete",
                ),
                _target(
                    "purchase_orders",
                    "opencart:drill:purchase-order:1001",
                    order_ref=order,
                    account_ref=account,
                    po_number="SYNTHETIC-PO-1001",
                    amount_minor=12500,
                    currency="USD",
                    status="accepted",
                    issued_at="2026-08-10T00:00:00Z",
                ),
                _target(
                    "invoices",
                    invoice,
                    order_ref=order,
                    account_ref=account,
                    invoice_number="SYNTHETIC-INV-1001",
                    status="paid",
                    currency="USD",
                    total_minor=12500,
                    due_at="2026-09-09T00:00:00Z",
                    issued_at="2026-08-10T00:00:00Z",
                ),
                _target(
                    "payments",
                    payment,
                    order_ref=order,
                    invoice_ref=invoice,
                    provider="synthetic-provider",
                    provider_reference="synthetic-payment-reference",
                    tender_type="invoice-settlement",
                    amount_minor=12500,
                    currency="USD",
                    status="settled",
                    occurred_at="2026-08-15T00:00:00Z",
                ),
                _target(
                    "refunds",
                    refund,
                    payment_ref=payment,
                    order_ref=order,
                    provider_reference="synthetic-refund-reference",
                    amount_minor=2500,
                    currency="USD",
                    reason="Synthetic partial return",
                    status="settled",
                    occurred_at="2026-08-20T00:00:00Z",
                ),
                _target(
                    "fulfillments",
                    fulfillment,
                    order_ref=order,
                    method="pickup",
                    carrier=None,
                    tracking_number=None,
                    status="complete",
                    shipped_at="2026-08-16T00:00:00Z",
                    delivered_at="2026-08-16T00:00:00Z",
                ),
                _target(
                    "fulfillment_lines",
                    "opencart:drill:fulfillment-line:1001:1",
                    fulfillment_ref=fulfillment,
                    order_line_ref=line,
                    quantity=2,
                ),
                _target(
                    "returns",
                    returned,
                    order_ref=order,
                    return_number="SYNTHETIC-RET-1001",
                    status="complete",
                    reason="Synthetic fit return",
                    requested_at="2026-08-18T00:00:00Z",
                    received_at="2026-08-20T00:00:00Z",
                ),
                _target(
                    "return_lines",
                    "opencart:drill:return-line:1001:1",
                    return_ref=returned,
                    order_line_ref=line,
                    quantity=1,
                    resolution="partial-refund",
                    refund_ref=refund,
                ),
                _target(
                    "production_work_orders",
                    work_order,
                    order_ref=order,
                    order_line_ref=line,
                    due_at="2026-08-16T00:00:00Z",
                    status="complete",
                    instructions="Synthetic embroidery drill",
                ),
                _target(
                    "production_operations",
                    "opencart:drill:production-operation:1001:1",
                    work_order_ref=work_order,
                    operation_type="embroidery",
                    sequence_number=1,
                    status="complete",
                    completed_at="2026-08-15T00:00:00Z",
                    qc_result="pass",
                ),
                _target(
                    "audit_events",
                    "opencart:drill:audit-event:1001:1",
                    entity_table="commerce_orders",
                    entity_record_id=order,
                    event_type="representative-restore-verified",
                    occurred_at="2026-08-10T00:00:00Z",
                    actor_ref="synthetic-drill",
                    event_json=_json({"synthetic": True, "purpose": "recovery-drill"}),
                ),
            ],
        ),
    ]


def _artifact(path: Path, artifact_type: str, entity: str, record_count: int) -> dict:
    payload = path.read_bytes()
    return {
        "relative_path": path.name,
        "artifact_type": artifact_type,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "record_count": record_count,
        "completeness": "complete-file",
        "entity": entity,
    }


def build_fixture_bundle(destination: Path) -> Path:
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError(f"fixture destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.building-{uuid.uuid4().hex}")
    try:
        temporary.mkdir()
        database = temporary / "database.sql"
        database.write_bytes(b"-- synthetic recovery drill; contains no client data\n")
        rows = _fixture_rows()
        source_counts = {"customers": 1, "orders": 1, "price_lists": 1, "products": 1}
        snapshots = []
        for entity in source_counts:
            entity_rows = [row for row in rows if row["entity"] == entity]
            snapshot = temporary / f"{entity}.ndjson"
            snapshot.write_text(
                "".join(_json(row) + "\n" for row in entity_rows),
                encoding="utf-8",
                newline="\n",
            )
            snapshots.append(
                _artifact(snapshot, "table-snapshot", entity, len(entity_rows))
            )
        manifest = {
            "schema_version": "mt-uniforms-commerce-import/v1",
            "run_id": RUN_ID,
            "source_system": "opencart",
            "store_ref": "synthetic-drill-never-client-data",
            "captured_at": CAPTURED_AT,
            "source_version": "synthetic-fixture-v1",
            "capture_method": "synthetic-recovery-drill",
            "status": "reconciled",
            "scope": {"kind": "partial", "entities": sorted(source_counts)},
            "artifacts": [
                _artifact(database, "database-sql", "orders", 0),
                *snapshots,
            ],
            "reconciliation": {
                "source_counts": source_counts,
                "normalized_counts": source_counts,
                "skipped_counts": {entity: 0 for entity in source_counts},
                "skips": [],
                "foreign_key_errors": 0,
                "unresolved_conflicts": 0,
                "money_checks": [
                    {
                        "order_ref": "opencart:drill:order:1001",
                        "source_total_minor": 12500,
                        "normalized_total_minor": 12500,
                        "rounding_quantum_minor": 0,
                    }
                ],
            },
        }
        manifest_path = temporary / "export-manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        temporary.rename(destination)
        return destination / "export-manifest.json"
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def verify_reconstruction(database: Path) -> dict:
    database = Path(database).resolve()
    connection = sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True)
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
        table_counts = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in TABLES
        }
        order_total = connection.execute(
            "SELECT total_minor FROM commerce_orders WHERE record_id='opencart:drill:order:1001'"
        ).fetchone()
        payment = connection.execute(
            "SELECT amount_minor FROM payments WHERE record_id='opencart:drill:payment:1001'"
        ).fetchone()
        refund = connection.execute(
            "SELECT amount_minor FROM refunds WHERE record_id='opencart:drill:refund:1001:1'"
        ).fetchone()
        fulfilled = connection.execute(
            "SELECT quantity FROM fulfillment_lines WHERE record_id='opencart:drill:fulfillment-line:1001:1'"
        ).fetchone()
        returned = connection.execute(
            "SELECT quantity FROM return_lines WHERE record_id='opencart:drill:return-line:1001:1'"
        ).fetchone()
        lineage_rows = connection.execute(
            "SELECT COUNT(*) FROM record_lineage WHERE entity_record_id LIKE 'opencart:drill:%'"
        ).fetchone()[0]
        import_status = connection.execute(
            "SELECT status FROM import_runs WHERE run_id=?", (RUN_ID,)
        ).fetchone()
    finally:
        connection.close()

    expected_counts = {table: 1 for table in TABLES}
    if integrity != "ok":
        raise ValueError(f"drill database integrity failed: {integrity}")
    if foreign_keys:
        raise ValueError(f"drill database has {len(foreign_keys)} foreign-key error(s)")
    if table_counts != expected_counts:
        raise ValueError(f"drill table counts do not match: {table_counts}")
    if not import_status or import_status[0] != "reconciled":
        raise ValueError("drill import run is not reconciled")
    scalar_rows = (order_total, payment, refund, fulfilled, returned)
    if any(row is None for row in scalar_rows):
        raise ValueError("drill reconstruction is missing required linked records")
    if lineage_rows != len(TABLES):
        raise ValueError(f"drill lineage coverage is incomplete: {lineage_rows}/{len(TABLES)}")
    return {
        "valid": True,
        "classification": "synthetic-drill-never-client-data",
        "integrity": integrity,
        "foreign_key_errors": len(foreign_keys),
        "table_counts": table_counts,
        "order_total_minor": order_total[0],
        "payment_minor": payment[0],
        "refund_minor": refund[0],
        "fulfilled_quantity": fulfilled[0],
        "returned_quantity": returned[0],
        "lineage_rows": lineage_rows,
    }


def _authority_hashes(root: Path) -> dict[str, str]:
    return {
        name: recovery_package.sha256_file(root / name)
        for name in ("package-manifest.json", recovery_package.DATABASE_FILE, recovery_package.CHECKSUM_FILE)
    }


def run_drill(authority: Path, destination: Path, schema: Path | None = None) -> dict:
    authority = Path(authority).resolve()
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError(f"drill destination already exists: {destination}")
    if not authority.is_dir():
        raise ValueError(f"authority package does not exist: {authority}")
    if authority == destination or authority in destination.parents or destination in authority.parents:
        raise ValueError("authority and drill destination must be distinct and non-nested")
    schema = Path(schema).resolve() if schema else Path(__file__).parents[1] / "schemas" / "commerce-import-bundle-v1.schema.json"
    package_binary_ready_generation.verify_generation(authority)
    authority_before = _authority_hashes(authority)
    temporary = destination.with_name(f".{destination.name}.building-{uuid.uuid4().hex}")
    fixture = destination.with_name(f".{destination.name}.fixture-{uuid.uuid4().hex}")
    try:
        shutil.copytree(authority, temporary)
        marker = {
            "classification": "synthetic-drill-never-client-data",
            "authority": authority.name,
            "run_id": RUN_ID,
            "promotable": False,
        }
        (temporary / "DRILL-ONLY.json").write_text(
            json.dumps(marker, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        manifest = build_fixture_bundle(fixture)
        import_report = package_import_ready_generation.stage_and_import_bundle(
            temporary, manifest, schema
        )
        package_report = recovery_package.verify_package(temporary)
        reconstruction = verify_reconstruction(temporary / recovery_package.DATABASE_FILE)
        package_binary_ready_generation.verify_generation(authority)
        authority_after = _authority_hashes(authority)
        if authority_before != authority_after:
            raise ValueError("authority package changed during the recovery drill")
        temporary.rename(destination)
        return {
            "valid": True,
            "classification": "synthetic-drill-never-client-data",
            "authority_unchanged": True,
            "destination": str(destination),
            "import": import_report,
            "package": package_report,
            "reconstruction": reconstruction,
        }
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    finally:
        shutil.rmtree(fixture, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build-fixture")
    build.add_argument("destination", type=Path)
    verify = sub.add_parser("verify")
    verify.add_argument("database", type=Path)
    run = sub.add_parser("run")
    run.add_argument("authority", type=Path)
    run.add_argument("destination", type=Path)
    run.add_argument("--schema", type=Path)
    args = parser.parse_args()
    if args.command == "build-fixture":
        report = {"manifest": str(build_fixture_bundle(args.destination))}
    elif args.command == "verify":
        report = verify_reconstruction(args.database)
    else:
        report = run_drill(args.authority, args.destination, args.schema)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
