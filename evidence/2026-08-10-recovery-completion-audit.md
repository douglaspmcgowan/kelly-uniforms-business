# Recovery completion audit — 2026-08-10

## Outcome

The public digital estate is rebuild-ready through immutable recovery generation REC-007. The remaining recovery work is private-source work and cannot be represented as complete until value-safe authenticated access or native hosting exports are available.

## Verified public recovery boundary

- REC-007 contains 1,542 of 1,542 exact public media binaries.
- It contains 34 of 35 referenced public JavaScript/font resources. The sole missing reference is Oracle AddThis, a retired third-party service; the dead reference and retrieval history are preserved rather than replaced with invented bytes.
- The normalized SQLite database has 35 commerce tables with mandatory source-lineage fields and zero synthesized commerce rows.
- The package has 4,469 checksum entries and 512 source-manifest rows.
- SQLite integrity returned `ok`; foreign-key verification returned zero errors.
- A package-only isolated restore succeeded from the REC-007 archive using only the packaged recovery tools.
- Twelve focused recovery tests passed across package verification, runtime capture, commerce-schema upgrade, missing-media capture, and public-asset finalization.

## Live authenticated-access audit

The in-app browser was inspected without reading cookies, saved passwords, session storage, or credential values.

- The existing OpenCart administration tab resolved to the OpenCart login form. Its prior authenticated session had expired.
- A direct Ecwid control-panel check resolved to `Login | Ecwid Ecommerce` and exposed only the sign-in form.
- Browser discovery found no second connected browser family or authenticated browser session to use as a value-safe alternative.
- No login was attempted because the current browser-control path would place the credential value in agent-visible tool input. The approved unattended alternative remains the one-secret-to-one-process Bitwarden broker documented in `ACCESS.md`.

## Requirement disposition

| Requirement | Status | Evidence or blocker |
|---|---|---|
| Public storefront pages, assets, runtime references, media, public infrastructure and ownership evidence | Verified through REC-007 | Package manifest, checksums, SQLite integrity, isolated restore, focused tests |
| Normalized rebuild schema and row-level provenance | Verified, ready for ingestion | 35 commerce tables; deliberately zero private rows until native exports arrive |
| Full OpenCart database, webroot, external storage, private media, configuration, versions and logs | Blocked | Expired admin session; no value-safe broker binding; no hosting control-panel, SFTP/SSH or database-export access |
| Complete Ecwid catalog, customer, order, configuration, source-ID and media exports | Blocked | Ecwid login screen; no value-safe broker binding |
| Clover export | Excluded from current scope | Douglas ruling DEC-005 retains Clover as the external in-store POS boundary |
| Account payer, renewal, recovery and authoritative ownership records | Blocked | Requires account-side or signed ownership records |
| Encrypted offline/off-site redundant custody | Blocked | No approved public encryption recipient or securely escrowed recovery key is provisioned |

## Exact resume point

1. Provision the four value-bearing fields and machine-account access described under Path B in `ACCESS.md`; return only the non-secret project/resource IDs.
2. Restore and verify the two narrowly scoped allowlist entries.
3. Run OpenCart capture first: native database export, webroot, external storage, private media, configuration, version inventory and logs.
4. Run Ecwid capture second: all native exports, source IDs, media and account-status classification.
5. Preserve each native export immutably, hash it, ingest it into the existing 35-table schema with lineage, reconcile counts/totals, and execute the package-only restore again.
6. Add a value-safe hosting/ownership access path and an approved encryption recipient before declaring full business recovery complete.

## Completion claim boundary

REC-007 is a complete preservation of the observable public estate. It is not a full backup of the private business systems. The overall rebuild-ready recovery deliverable remains active and blocked at the authenticated/private-data boundary.
