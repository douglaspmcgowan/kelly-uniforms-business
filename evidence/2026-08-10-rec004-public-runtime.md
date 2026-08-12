# REC-004 public runtime capture and isolated restore

Date: 2026-08-09 EDT / 2026-08-10 generation label
Scope: public, unauthenticated JavaScript and font assets already enumerated by REC-003
Parent: `REC-003` at `PROJECT_DATA_ROOT\backups\business-continuity\2026-08-09-rec003`

## Result

REC-004 immutably preserves REC-003 and adds direct HTTP capture for the 31 JavaScript references and four failed font references in its runtime inventory.

- Attempted URLs: 35
- Captured binaries: 34
- Explicit failures: 1
- Remaining failure: the legacy AddThis script referenced by the hidden badge-wallet page; DNS lookup for `s7.addthis.com` failed during the bounded retry window
- Package checksum entries: 4,034
- SQLite source-manifest rows: 75
- SQLite integrity: `ok`
- Foreign-key errors: 0
- Schema: 1.1.0; application ID 1297372498; user version 2
- Public ownership facts retained: one business entity, 11 business facts, three infrastructure assets, and 26 infrastructure observations

Every captured runtime record stores its source URL, source page set, asset kind, capture timestamp, content type, byte count, SHA-256, portable packaged path, and a corresponding SQLite lineage record. The runtime verifier independently recomputes each binary hash and checks the inventory-to-database count.

## Immutable artifacts

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `PROJECT_DATA_ROOT\backups\business-continuity\2026-08-10-rec004\package-manifest.json` | 4,035 | `9ccb42311cf233ff70d75b3fa404e87d1627017a37c598a10cf844dd8db86ab1` |
| `PROJECT_DATA_ROOT\backups\business-continuity\2026-08-10-rec004\mt_uniforms_recovery.sqlite` | 16,580,608 | `ccca1a0b8132d31b823f934a6bb2d11d915d3496d19a11c02412c7654295319f` |
| `PROJECT_DATA_ROOT\backups\business-continuity\archives\mt-uniforms-recovery-2026-08-10-rec004.tar.gz` | 117,901,796 | `34f73c71e490e9118d08a7a889588abfc1924f882dd2e2fc262f111607c9944a` |

The first archive produced before scope reconciliation was retained, rather than overwritten, as `mt-uniforms-recovery-2026-08-10-rec004-pre-scope-reconcile.tar.gz`. It is historical evidence and is not the current REC-004 authority.

## Restore proof

The final archive was extracted into a fresh directory at `PROJECT_DATA_ROOT\backups\business-continuity\isolated-restores\rec004-final-20260810`. Running `scripts\capture_public_runtime.py verify` against the extracted generation passed all package checksums, SQLite integrity and foreign-key checks, source-lineage checks, runtime binary hashes, byte counts, and runtime inventory/database reconciliation.

Focused tests also passed two scenarios: real local HTTP capture with an intentional 404, and deliberate post-capture binary tampering detected as a checksum mismatch.

## Remaining boundary

REC-004 is the current public recovery authority. It does not claim private commerce completeness. The remaining required evidence is:

- full OpenCart database, webroot, external storage, private media, configuration, versions, and logs;
- complete Ecwid UI/API exports and media;
- primary account-control evidence for domain, DNS, hosting, email, payment, shipping, subscriptions, and licences; and
- encrypted offline and offsite custody.

Clover authenticated export remains excluded by client decision. OpenCart and Ecwid private work remains blocked on the approved Path B credential broker or an attended authenticated session; hosting recovery separately requires hosting/SFTP/SSH/database access.
