# Commerce import contract evidence — 2026-08-10

## Outcome

The recovery project now has a versioned, executable acceptance boundary for future OpenCart and Ecwid exports. It does not populate REC-007 with invented data. It proves whether a later authenticated capture is immutable, source-identifiable, complete for its declared scope, safe to normalize, and reconciled before ingestion.

## Existing-owner search and touch list

- `STORE-REQUIREMENTS.md` owns the business capabilities that must survive migration.
- `DELIVERABLES.md` `DEL-005` owns recovery delivery state.
- `evidence/2026-08-10-rec005-commerce-schema.md` owns the rationale for the empty 35-table landing schema.
- No executable OpenCart/Ecwid import-and-reconcile contract existed, so the new owner is `docs/recovery/opencart-ecwid-import-reconcile-contract.md`, paired with the versioned JSON schema and validator.
- Touch list for this change: the contract, schema, validator, focused test, this evidence note, `MAP.md`, `DELIVERABLES.md`, and generated Work Scope views/state.

## Contract coverage

- Raw OpenCart SQL remains the authority and must be restored into a disposable compatible database before read-only table snapshots are produced.
- Ecwid UI CSVs and native paginated API envelopes remain untouched source artifacts.
- Artifact paths are portable and traversal-free; sizes and SHA-256 hashes must match exact bytes.
- Every run, store, source version, capture method, entity scope, artifact, source count, normalized count, skip and reconciliation result is explicit.
- Normalization snapshots reject credential/session/payment-card fields, duplicate native identifiers and unexplained count deltas.
- Ecwid pages must be contiguous, non-overlapping, total-stable and collectively complete.
- Money checks use integer minor units with an explicit rounding quantum; binary floats fail closed.
- The prose contract records deterministic IDs, source locators, non-merge rules, historical-order fidelity, rollback, schema additions and isolated-restore gates.

## Test-first evidence

The nine focused tests were written before `scripts/validate_import_bundle.py` existed. The required red run failed nine of nine tests with `validate_import_bundle.py is missing`. After implementation, one fixture-precondition failure was corrected so the test reached the intended sensitive-field branch. The final test run passed all nine tests.

Work Scope evidence:

- Task: `opencart-ecwid-import-contract-v2`
- Check: `opencart-ecwid-import-contract-verify-v2`
- Receipt: `35d39aa8-0551-4199-b103-6b3eb4933f94`
- Result: pass, exit code 0
- Tests: 9 passed

The first immutable task declaration was retired because its test-input hash correctly became stale when the fixture was corrected. Closing the replacement exposed a harness edge case in which dependency resolution revived retired tasks. Discovery `retired-task-status-resolver-resurrects-20260810` records the defect in the `agent-harness` queue. The already-existing isolated `fix-retired-task` worktree preserves retired status and was used to close only this task; no shared harness file was edited or merged here.

## Remaining boundary

This contract makes future private data ingestion deterministic and testable. Full OpenCart, Journal, Ecwid, hosting, ownership and encrypted-custody recovery still requires the authenticated exports and hosting access listed in `ACCESS.md`. D5 and the overall recovery capability remain active.
