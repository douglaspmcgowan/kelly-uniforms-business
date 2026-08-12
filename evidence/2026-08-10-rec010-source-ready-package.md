# REC-010 OpenCart-and-Ecwid source-ready recovery package

Date: 2026-08-10
Generation: `REC-010`
Parent: `REC-009`

## Result

Created the current self-contained recovery authority with package-local acquisition paths for both Ecwid API exports and OpenCart native database/webroot/storage/config exports. The importer-v2 staging and normalization chain remains packaged and preserves raw source evidence before normalization.

Fresh REC-010 has no authenticated private exports, normalized private commerce rows, import runs, or lineage rows. Its readiness is `opencart-and-ecwid-tools-packaged-awaiting-authenticated-exports`.

## Verification

- TDD red: both focused tests failed because `package_source_ready_generation.py` did not exist.
- Focused green: `py -m unittest scripts.test_package_source_ready_generation` passed 2 tests.
- Real creation returned `valid: true`, generation `REC-010`, parent `REC-009`, and `normalized_rows: 0`.
- Package inventory: 4,486 checksummed files plus `SHA256SUMS.txt`; 529 `source_manifest` rows; SQLite integrity `ok`; zero foreign-key errors.
- Inherited authority: 35 commerce tables remain empty, 430 missing-media captures remain exact, 34 of 35 runtime dependencies remain captured, and the one retired AddThis dependency remains the known disposition.
- Isolated restore: extracted the archive outside the repository and ran `tools\package_source_ready_generation.py verify` from `C:\Windows\Temp`; it returned `valid: true` using only package-local files.
- Redundancy: primary and restricted copies match for manifest, database, checksum inventory, and archive.

## Authority paths

- Primary generation: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\2026-08-10-rec010`
- Primary archive: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\archives\mt-uniforms-recovery-2026-08-10-rec010.tar.gz`
- Restricted redundant generation: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\private\business-continuity\2026-08-10-rec010`
- Restricted redundant archive: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\private\business-continuity\mt-uniforms-recovery-2026-08-10-rec010.tar.gz`
- Isolated restore: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\isolated-restores\rec010-20260810\2026-08-10-rec010`

## SHA-256 evidence

- `package-manifest.json`: `cb716048b5541f0d7c93cf315f947629192e9a44503fd5fde972ef0ee97e8134`
- `mt_uniforms_recovery.sqlite`: `d8c9885cf387126e394ee11633353c06b1a6b3a7689013ac6d7cc4abc1ce8285`
- `SHA256SUMS.txt`: `402357cd86d649dac7914215fbffcfde88998cdb1958f565873522f24c77dbf0`
- Archive: `957fe412a61e7c619ec116f15f6769a1e5775c5bddd23e50b7447a8f55c8f7fd` (123,630,715 bytes)

## Remaining boundary

Private records still require authenticated access: Ecwid API/store authorization and OpenCart hosting/database export access. The current visible admin sessions were signed out, and no approved secret-bearing process was available. Clover capture remains deferred by the client decision and is outside this generation.
