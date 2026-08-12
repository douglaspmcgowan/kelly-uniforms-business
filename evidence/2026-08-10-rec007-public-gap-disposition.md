# REC-007 final public-asset disposition and isolated restore

Date: 2026-08-10 generation label
Parent: `REC-006`

## Result

REC-007 exhausts the final public-only recovery gaps found in REC-006.

- The single embedded `data:image/png;base64,...` storefront asset was decoded to its exact PNG bytes and recorded with MIME type, byte count, SHA-256, portable path, media ID, source-URI hash, capture time, and SQLite lineage.
- Public media coverage is now 1,542 of 1,542 exact binaries: 1,541 URL-backed files plus one embedded binary.
- The remaining runtime reference is Oracle AddThis. Its live host does not resolve, and two bounded Internet Archive CDX attempts returned no bytes before timeout.
- Oracle terminated all AddThis services effective 2023-05-31. REC-007 preserves the exact dead reference, source page, live failure, authoritative retirement URL, archive-attempt result, and rebuild guidance. It does not substitute unrelated or unverifiable JavaScript.

Authoritative retirement source: <https://community.oracle.com/customerconnect/discussion/673943/oracle-has-made-the-business-decision-to-terminate-all-addthis-services-effective-as-of-may-31-2023>

## Verification

- Package checksum entries: 4,469
- Source-manifest rows: 512
- SQLite integrity: `ok`
- Foreign-key errors: 0
- Embedded binaries captured: 1
- Public media exact: 1,542 of 1,542
- Commerce tables retained: 35; synthesized commerce rows: 0

The final archive was extracted into `PROJECT_DATA_ROOT\backups\business-continuity\isolated-restores\rec007-20260810`. Its packaged `tools\finalize_public_assets.py` verifier passed package checksums, source lineage, embedded-media hashes, inventory/database reconciliation, the AddThis disposition, public-media retry checks, runtime checks, commerce-schema checks, SQLite integrity, and foreign keys.

## Immutable artifacts

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `PROJECT_DATA_ROOT\backups\business-continuity\2026-08-10-rec007\package-manifest.json` | 5,617 | `6af1b266ffdcdb5e7b908c1d42335e08d2c67668f1dae8de7c0a5fb54ee1513b` |
| `PROJECT_DATA_ROOT\backups\business-continuity\2026-08-10-rec007\mt_uniforms_recovery.sqlite` | 17,309,696 | `0881688e29dedb5698f7786623f725181c9c192e308a1c3cc8e1885bdd939b63` |
| `PROJECT_DATA_ROOT\backups\business-continuity\archives\mt-uniforms-recovery-2026-08-10-rec007.tar.gz` | 123,602,696 | `ff867c3884ecaabee3e2282be9cfe174ac5bdbdfab4da5c2124009ea12502c66` |

## Remaining boundary

No known unauthenticated storefront, media, runtime, public-infrastructure, or schema task remains. Further recovery depends on unavailable authenticated OpenCart/Ecwid or hosting access, primary account-control records, and an approved encryption recipient/key for offline and offsite custody. Clover authenticated export remains excluded by client decision.
