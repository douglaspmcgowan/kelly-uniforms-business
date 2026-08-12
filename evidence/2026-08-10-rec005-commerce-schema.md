# REC-005 normalized commerce schema and isolated restore

Date: 2026-08-10 generation label
Parent: `REC-004`
Purpose: provide a source-backed landing model for future OpenCart, Ecwid, hosting, and client-supplied exports without fabricating private business records.

## Result

REC-005 immutably preserves REC-004 and adds 35 normalized commerce tables covering:

- catalog categories, products, variants, multi-axis option values/mappings, and media;
- inventory locations, balances, and movements;
- agency/business accounts, members, addresses, tax exemptions, entitlements, allowance ledger, price lists, and promotions;
- orders with immutable line snapshots, per-line customizations, purchase orders, invoices, payments, and refunds;
- fulfillment, tracking, returns, and return lines;
- production artwork, proofs, work orders, operations, and QC; and
- cross-system mappings and audit events.

Every table requires `source_system`, immutable `source_record_id`, `extracted_at`, and a foreign key to `source_manifest`. The new tables contain zero rows because no authenticated export was available; the package records `empty-awaiting-authenticated-exports` instead of inventing data.

## Verification

- Focused schema tests: 2 passed, including idempotent migration and rejection of missing/invalid source lineage.
- Commerce schema version: 1.0.0
- Commerce tables: 35
- Commerce rows: 0
- Package checksum entries: 4,035
- Source-manifest rows: 78
- SQLite integrity: `ok`
- Foreign-key errors: 0
- Public runtime retained: 34 captured of 35 attempted; one explicit AddThis DNS failure

The final archive was extracted into `PROJECT_DATA_ROOT\backups\business-continuity\isolated-restores\rec005-final2-20260810`. The verifier was run from the extracted package's own `tools\upgrade_commerce_schema.py`, and passed package checksums, source lineage, runtime inventory/database reconciliation, required commerce tables, schema metadata, and foreign keys. Generated Python bytecode is intentionally excluded from the immutable payload inventory; a regression test proves that importing the packaged verifier cannot invalidate its package.

## Immutable artifacts

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `PROJECT_DATA_ROOT\backups\business-continuity\2026-08-10-rec005\package-manifest.json` | 5,148 | `998f6adb39e33d23f49a740a3b5a668b41dc6f46b65f6a5c6be1b45baa9228f7` |
| `PROJECT_DATA_ROOT\backups\business-continuity\2026-08-10-rec005\mt_uniforms_recovery.sqlite` | 17,035,264 | `51fe2dc39eb5ff523d1604fa1a575a94f46cc4be3875d4389214514cb949fdc3` |
| `PROJECT_DATA_ROOT\backups\business-continuity\archives\mt-uniforms-recovery-2026-08-10-rec005.tar.gz` | 117,918,714 | `7dadc33e6c0d49b3a3ffda8b6110fab8d87e4c105004598bd80488f094e102ff` |

## Remaining boundary

REC-005 is structurally rebuild-ready and publicly populated; it is not a complete private business backup. Population and reconciliation still require the full OpenCart database/webroot/storage and complete Ecwid exports, while account-control records require primary hosting/domain/mail/payment/shipping evidence. Encrypted offline and independent offsite custody also remains open. Clover authenticated export is excluded by client decision.
