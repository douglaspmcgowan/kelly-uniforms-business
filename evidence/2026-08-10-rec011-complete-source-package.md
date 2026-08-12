# REC-011 complete-source recovery package

Date: 2026-08-10
Generation: `REC-011`
Parent: `REC-010`

## Result

Created the current offline recovery authority with package-local OpenCart native acquisition, Ecwid complete API acquisition, importer v2, raw evidence staging, schemas, contracts, and verification chain.

Readiness is `opencart-and-complete-ecwid-tools-packaged-awaiting-authenticated-exports`. Fresh private commerce tables, import runs, lineage rows, and import-backed source rows remain empty.

## Verification

- TDD red: both focused tests failed because `package_complete_source_generation.py` did not exist.
- Focused green: `py -m unittest scripts.test_package_complete_source_generation` passed 2 tests.
- Real creation returned `valid: true`, generation `REC-011`, parent `REC-010`, and `normalized_rows: 0`.
- Package inventory: 4,490 checksummed files plus `SHA256SUMS.txt`; 533 `source_manifest` rows; SQLite integrity `ok`; zero foreign-key errors.
- Inherited authority: 35 empty commerce tables, 430 exact missing-media captures, 34 of 35 runtime dependencies, and the known retired AddThis disposition.
- Isolated restore: the archive was extracted outside the repository and `tools\package_complete_source_generation.py verify` returned `valid: true` using package-local files only.
- Primary and restricted copies match for the manifest, database, checksum inventory, and archive.

## Authority paths

- Primary generation: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\2026-08-10-rec011`
- Primary archive: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\archives\mt-uniforms-recovery-2026-08-10-rec011.tar.gz`
- Restricted redundant generation: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\private\business-continuity\2026-08-10-rec011`
- Restricted redundant archive: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\private\business-continuity\mt-uniforms-recovery-2026-08-10-rec011.tar.gz`
- Isolated restore: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\isolated-restores\rec011-20260810\2026-08-10-rec011`

## SHA-256 evidence

- `package-manifest.json`: `95f06b17691245c3c032399ee555ce4417824429971960b24a1bffa9c72e73b9`
- `mt_uniforms_recovery.sqlite`: `f2ebe17c0b0fa90339ee579050d79611e37bda74ea6c500679f0842cce92b2f2`
- `SHA256SUMS.txt`: `a746633fd7c8e31fe34e8aad2a2640e4964153a808ba4d14cc0a6ccc81b800d9`
- Archive: `01be92388cbd6a94ffaf377c4e80b0ecf1ec1942a233e388fb6b0bfc2669c898` (123,634,795 bytes)

## Remaining boundary

Authenticated source acquisition is the remaining prerequisite: an Ecwid token with the declared read scopes and OpenCart hosting/database export access. The visible admin sessions are signed out and no approved secret-bearing process is available. Clover remains deferred by the client decision.
