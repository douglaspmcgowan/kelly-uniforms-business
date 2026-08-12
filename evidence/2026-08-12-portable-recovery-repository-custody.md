# Portable recovery repository custody evidence

Generated: 2026-08-12

## Purpose

Put the complete value-safe M&T Uniforms recovery system under remote Git custody so another machine can rebuild, verify, and resume the project without relying on this workstation's uncommitted files. Restricted recovery bytes remain outside Git under `PROJECT_DATA_ROOT`.

## Scoped repository contents

- OpenCart, Journal, Ecwid, public-site, media, ownership, normalization, staged-import, recovery-generation, and restore-drill tooling;
- schemas, contracts, runbooks, tests, and generation evidence through REC-016;
- the value-free data adapter and secret manifests;
- Work Scope schema, canonical state, event chain, evidence receipts, and immutable legacy TASK/BACKBURNER/LOG imports;
- generated project views and current REC-016 routing;
- the brand-direction gallery and already-merged storefront validation surfaces.

Runtime locks, Python bytecode/cache directories, dependency directories, Vercel metadata, credential values, and external recovery packages are excluded.

## Pre-publication verification

`scripts/Test-PortableRecoveryRepository.ps1` passed against the staged project tree:

- Python recovery suite: 80 tests passed, 1 skipped;
- external-data adapter tests: passed;
- brand-gallery tests: 4 passed;
- storefront contract: 7 products, 8 asset hashes, production contract passed;
- storefront TypeScript/Vite production build: passed;
- Work Scope validation and generated-view reconciliation: passed with no drift;
- Gitleaks redacted working-tree scan: no leaks found;
- staged and unstaged whitespace checks: passed;
- tracked runtime-lock/bytecode check: zero forbidden files.

Pre-merge review also proved that REC-016 is represented by value-free manifest entries, verification rejects SQLite WAL/SHM sidecars without mutating them, and failed release verification removes all temporary or partially promoted outputs. Focused regression tests cover both release-safety cases.

The final Work Scope verifier additionally requires the local Git tree to equal `origin/master` after integration. Its receipt is recorded in `.agents/work/state.json` and the hash-chained event log.

## External recovery authority

REC-016 remains the current immutable offline authority at:

`C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\2026-08-12-rec016`

Its archive and isolated restore are documented in `evidence/2026-08-12-rec016-manifest-consistency-successor.md`. They are intentionally absent from Git.
