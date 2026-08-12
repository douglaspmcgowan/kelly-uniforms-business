# REC-006 complete public media retry and isolated restore

Date: 2026-08-10 generation label
Parent: `REC-005`

## Result

REC-006 immutably preserves REC-005 and retries every public image URL that REC-005 classified as `referenced-only` or `direct-network-blocked`.

- Attempted unresolved URLs: 430
- Captured exact binaries: 430
- Failed retries: 0
- Total exact external image binaries: 1,541 of 1,541 URL-backed assets
- Inline embedded placeholder: one, preserved in the inventory as `inline-or-unsupported`
- Package checksum entries: 4,466
- Source-manifest rows: 509
- SQLite integrity: `ok`
- Foreign-key errors: 0
- Inherited runtime: 34 of 35 JavaScript/font URLs captured; the sole AddThis DNS failure remains explicit
- Inherited commerce model: 35 provenance-constrained tables, zero synthesized commerce rows

Each newly captured image retains its exact URL, capture timestamp, content type, byte count, SHA-256, portable path, acquisition method, media ID, and a `source_manifest` lineage row. The normalized `media_assets` table was updated to match the inventory.

## Restore proof

The final archive was extracted into `PROJECT_DATA_ROOT\backups\business-continuity\isolated-restores\rec006-20260810`. Its own packaged `tools\capture_missing_media.py` verifier passed package checksums, source lineage, media binary hashes, media inventory/database reconciliation, runtime checks, commerce-schema checks, SQLite integrity, and foreign keys.

## Immutable artifacts

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `PROJECT_DATA_ROOT\backups\business-continuity\2026-08-10-rec006\package-manifest.json` | 5,291 | `eccd5eeba1e00c4845a44d720442cd2d7f091506f23e0c063d78a22c64a8d9eb` |
| `PROJECT_DATA_ROOT\backups\business-continuity\2026-08-10-rec006\mt_uniforms_recovery.sqlite` | 17,309,696 | `c20a61b779473d7e2beb9df2a80493d0acafa5353c2f094d7207611931c29960` |
| `PROJECT_DATA_ROOT\backups\business-continuity\archives\mt-uniforms-recovery-2026-08-10-rec006.tar.gz` | 123,596,195 | `3b599d31561d0dd9cb8e9023f38f113b17a7f2bf08627df70d078f0d70294ece` |

## Remaining boundary

The public page, public image, public runtime, public infrastructure, and normalized-schema work is now exhausted for the current evidence set. Completion still requires private OpenCart/Ecwid and hosting exports, primary account-control records, population/reconciliation of the commerce schema, representative private-business restore scenarios, and encrypted offline/offsite custody. Clover authenticated export remains excluded by client decision.
