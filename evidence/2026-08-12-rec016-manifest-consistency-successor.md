# REC-016 manifest-consistency successor evidence

Generated: 2026-08-12

## Outcome

REC-016 is the immutable successor to REC-015. It corrects two stale current-state claims in the inherited package manifest while preserving the source generation unchanged:

- public media now records 1,542 of 1,542 exact binaries, 100% exact coverage, and zero unresolved referenced URLs;
- the value-free ten-service account inventory is recorded as present, while primary account-control evidence remains explicitly missing.

No authenticated OpenCart or Ecwid source bytes were invented. Fresh private commerce/import rows remain zero. Clover authentication remains excluded by DEC-005.

## Search record and touch list

The existing generation owner was `scripts/package_clean_recovery_generation.py`, which is evidence-bound to REC-015 and cannot safely be retargeted. REC-016 therefore adds the adjacent generation-specific owner `scripts/package_manifest_consistent_generation.py`, packages that verifier inside the successor, and keeps every REC-015 file immutable.

Current-authority routing is updated in `MAP.md`. Recovery provenance is added to `SOURCES.md`. Historical REC-015 evidence and generation-specific recovery contracts remain unchanged because they describe their own checkpoints.

## Authority and release artifacts

- Source authority: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\2026-08-10-rec015`
- REC-016 authority: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\2026-08-12-rec016`
- Archive: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\archives\mt-uniforms-recovery-2026-08-12-rec016.tar.gz`
- Isolated restore: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\isolated-restores\rec016-20260812\2026-08-12-rec016`

## Integrity evidence

- generation / parent: `REC-016` / `REC-015`
- readiness: `manifest-consistent-cache-free-operational-recovery-self-test-proven-awaiting-authenticated-exports`
- physical files: 4,510
- checksummed files: 4,509 plus `SHA256SUMS.txt`
- source-manifest rows: 554
- public media: 1,542 exact; capture statuses 1,111 inherited downloads + 430 REC-006 direct recoveries + 1 REC-007 embedded extraction
- public pages: 528
- runtime: 34 captured of 35; sole retired AddThis dependency remains dispositioned
- commerce schema: 35 tables; fresh normalized/private rows 0
- package-local reconstruction: 22 normalized rows and 22 lineage rows in a disposable synthetic drill, zero foreign-key errors
- SQLite integrity: `ok`; foreign-key errors: 0
- Python cache artifacts: 0
- REC-015 authority hashes before/after release: unchanged
- isolated package-only verifier: passed

Hashes:

- package manifest: `cfe34f6fdc1d2642419314247aa9259e3d433c7fbc271932eb94a7a68d28f428`
- SQLite database: `8ede2bd1023a9229907e8bca3889da568877e06e1b41aa75ef0f638e74cd3aa2`
- checksum manifest: `6616eef90fb223a91b4ddd608bb72b847f462477733494901a1db56101aad6e8`
- packaged REC-016 verifier: `8eaaa360a77b39dde73bc4c7e84677988e580a5476acdcce147a988473a8f933`
- archive: `1afc9330940949f487c0dda46eebe5a34ea9a472279454b66ff44b612dfd1d68` (123,563,898 bytes)
- isolated manifest: `cfe34f6fdc1d2642419314247aa9259e3d433c7fbc271932eb94a7a68d28f428`

## Verification commands

```powershell
py -m unittest scripts.test_package_manifest_consistent_generation
py -B scripts\package_manifest_consistent_generation.py verify C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\2026-08-12-rec016
py -B C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\isolated-restores\rec016-20260812\2026-08-12-rec016\tools\package_manifest_consistent_generation.py verify C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\isolated-restores\rec016-20260812\2026-08-12-rec016
```

## Remaining objective boundary

The complete rebuild-ready objective still requires authenticated OpenCart database/webroot/storage bytes, complete Ecwid JSON/binary exports, primary control evidence for the named services, and an approved encrypted offline/offsite custody endpoint. Those are missing-source boundaries, not package defects.
