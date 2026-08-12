# REC-008 import-ready recovery package and isolated restore

Date: 2026-08-10 generation label
Parent: `REC-007`

## Result

REC-008 preserves REC-007 byte-for-byte and adds the complete, package-local path for accepting later OpenCart and Ecwid exports without inventing inaccessible business records.

- The 35-table commerce model remains empty and now includes import-run identity, record-level multi-source lineage, product/category membership, option-group and option-value fidelity, and order adjustments at schema version `1.1.0`.
- The package contains its validator, additive schema tool, low-level transactional importer, recovery-chain verifiers, JSON Schema, and both import contracts.
- `stage-import` validates an external bundle, copies its manifest and every declared artifact into immutable `raw/private-exports/<run_id>/` storage, validates the copied bytes, atomically promotes the run, invokes the importer, and rewrites package checksums even if normalization fails after source evidence is recorded.
- Legacy machine-absolute path metadata was removed from the new package manifest. SQLite lineage paths remain portable and checksum-verifiable.
- No OpenCart or Ecwid private rows were synthesized: normalized commerce rows, import runs, import lineage, and `import:*` source-manifest rows are all zero in the fresh generation.

## Verification

- Public media exact: 1,542 of 1,542 binaries (`1,111` original downloads, `430` REC-006 direct captures, `1` REC-007 embedded extraction)
- Public runtime: 34 captured of 35 references; the sole unresolved reference remains the retired Oracle AddThis dependency with its authoritative disposition
- Package checksum entries: 4,476
- Source-manifest rows: 519
- Base commerce tables: 35; import-specific structures: 5; required added option columns: 8
- Normalized commerce rows: 0; import runs: 0
- SQLite integrity: `ok`; foreign-key errors: 0
- Focused TDD: four REC-008 tests passed, including success and failure paths for raw-byte staging and post-import checksum refresh; the complete focused recovery suite passed 31 tests
- Isolated restore: the archive was extracted to `PROJECT_DATA_ROOT\backups\business-continuity\isolated-restores\rec008-20260810`; its packaged `tools\package_import_ready_generation.py verify` command passed without repository files
- Parent immutability: REC-007 manifest, SQLite database, and checksum-manifest hashes remained `6af1b266...`, `0881688e...`, and `fc854e48...`

## Immutable artifacts

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `PROJECT_DATA_ROOT\backups\business-continuity\2026-08-10-rec008\package-manifest.json` | 6,015 | `f2437353b5baa03de36112b50dfa01e47d343218873e8f8c43cec35d0b780d06` |
| `PROJECT_DATA_ROOT\backups\business-continuity\2026-08-10-rec008\mt_uniforms_recovery.sqlite` | 17,371,136 | `fc4cf95a862775667cf8cab3b7d6352c7853c6efd5206f068376a1529336d6cb` |
| `PROJECT_DATA_ROOT\backups\business-continuity\2026-08-10-rec008\SHA256SUMS.txt` | 669,838 | `ae71501c8483ed65ad2a878a28eecf76971968a7fbbc281ceca9b4e4116381a4` |
| `PROJECT_DATA_ROOT\backups\business-continuity\archives\mt-uniforms-recovery-2026-08-10-rec008.tar.gz` | 123,620,175 | `43d00045f76c1125ea9bdaea7d8183adfc55b59159526ef5e56c13b2b1c61215` |

The restricted redundant manifest, database, and archive copies have the same byte counts and SHA-256 values as their recovery-tree authorities.

## Remaining boundary

The package is ready to receive source-backed OpenCart and Ecwid bundles, but those private exports still require value-safe authenticated access or hosting exports. Primary account-control evidence and an approved encrypted offline/offsite recipient also remain unavailable. Clover authenticated export remains excluded by `DEC-005`.
