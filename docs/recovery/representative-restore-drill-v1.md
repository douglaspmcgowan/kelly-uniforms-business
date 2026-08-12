# Representative restore drill v1

This drill proves that the recovery package can reconstruct a representative M&T Uniforms agency transaction through the same staged importer intended for authenticated OpenCart and Ecwid exports.

The fixture is explicitly synthetic. It contains no client record, cannot be promoted as an authority, and is written only into a new disposable copy of a verified recovery generation.

## Coverage

The drill reconstructs and links:

- agency account, buyer, tax exemption, and restricted-item entitlement;
- product, variant, and agency price list;
- immutable order and line snapshot with customization;
- purchase order, invoice, payment, and partial refund;
- fulfillment, partial return, production work order, operation, and audit event;
- record-level source lineage for every normalized row;
- integer-minor-unit order-total reconciliation.

## Command

```powershell
py tools\run_recovery_drill.py run <verified-authority> <new-disposable-destination>
```

The command verifies the authority before work begins, hashes its manifest/database/checksum authorities, copies it to a sibling build directory, stages the fixture through importer v2, verifies package checksums and SQLite integrity, confirms all expected relationships and values, re-verifies the unchanged authority, and atomically promotes only the disposable drill output.

The output contains `DRILL-ONLY.json` with classification `synthetic-drill-never-client-data` and `promotable: false`.

## Success criteria

- staged import status is `reconciled`;
- exactly 22 representative normalized rows and 22 lineage rows exist;
- SQLite integrity is `ok` and foreign-key errors are zero;
- order total is 12,500 minor units, payment is 12,500, refund is 2,500;
- fulfilled quantity is 2 and returned quantity is 1;
- the authority's package manifest, SQLite database, and checksum manifest hashes are unchanged.

This drill proves the normalized recovery pathway. It does not substitute synthetic values for missing authenticated client exports.
