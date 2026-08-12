# Portable v4 project contract

## Outcome

The M&T Uniforms repository was upgraded from the portable v3 project contract to portable v4 without overwriting its enrolled Work Scope history. The retired root task architecture is preserved byte-for-byte under `.agents/archive/task-state-migration/`, while `.agents/work/state.json` remains the authoritative task owner.

## Search record

Before writing, the existing owners and supported migration routes were inspected:

- `C:\Users\dougl\.agents\tools\Manage-Harness.ps1` owns project contract generation and verification.
- `C:\Users\dougl\.agents\tools\Migrate-TaskState.ps1` owns pre-enrollment legacy task migration, but its normal mode is not valid for this already-enrolled repository because `TASK.md` is a generated Work Scope view.
- `.agents/work/state.json` owns current task state and imported legacy history.
- `scripts/Test-PortableRecoveryRepository.ps1` owns repository-wide recovery verification.

The safe route was therefore a lossless archive of the three superseded root files, followed by `Manage-Harness.ps1 -Action EnsureProject`. No second task-state owner was created.

## Lossless archive

| Retired root file | SHA-256 | Bytes |
| --- | --- | ---: |
| `CURRENT-TASK.md` | `41bb44498fa428b7897df928cfd93cc11808fc47630782d2d47090b2d194d1b8` | 1,424 |
| `WORK_QUEUE.md` | `19cffafe12a4bc10b02035d9f2eafb30b5c16208f5d34ac42d5b6c9fb849d784` | 941 |
| `VERIFY.md` | `32ec282e081c495f316d57dde622ae4c7651376fa0a763462cebf1fe488b2dce` | 2,017 |

The hashes and sizes are machine-recorded in `.agents/archive/task-state-migration/archive-manifest.json`. The three names no longer exist at repository root.

## Touch list

- `AGENTS.md`, `.agents/harness-provenance.json`, `skills-manifest.json`, `.gitattributes`, and `.gitignore`: generated portable-v4 contract and project harness metadata.
- `.agents/work/state.json`, `.agents/work/events.jsonl`, `TASK.md`, `TRACKS.md`, `BACKBURNER.md`, and `LOG.md`: guarded Work Scope selection, task materialization, and generated views.
- `MAP.md` and `WEBSITE-UPDATE-RUNBOOK.md`: task and verification routing corrected to Work Scope and the repository verifier.
- `DESIGN.md`: managed design contract refreshed by `EnsureProject`.
- `data-manifest.yaml`: REC-016 destinations normalized to supported private/versioned data classes.
- `.agents/archive/task-state-migration/`: exact retired files plus their value-free byte manifest.
- `scripts/Test-PortableV4ProjectContract.ps1`: bounded verifier for the migration invariants.

## External-data custody correction

The current REC-016 manifest, SQLite database, and immutable archive were copied into their declared restricted data-root destinations. Their verified hashes remain:

- package manifest: `cfe34f6fdc1d2642419314247aa9259e3d433c7fbc271932eb94a7a68d28f428`
- SQLite database: `8ede2bd1023a9229907e8bca3889da568877e06e1b41aa75ef0f638e74cd3aa2`
- recovery archive: `1afc9330940949f487c0dda46eebe5a34ea9a472279454b66ff44b612dfd1d68`

These private recovery bytes remain outside Git. The repository contains only value-free routes, hashes, contracts, and safe public evidence.

## Verification contract

`scripts/Test-PortableV4ProjectContract.ps1` fails closed unless:

1. the retired root files are absent and their archived bytes match the manifest;
2. `AGENTS.md` contains portable v4 and no portable v3 marker;
3. harness provenance declares portable project contract v4;
4. `Manage-Harness.ps1 -Action VerifyProject` passes;
5. Work Scope state validates and all generated views reconcile.

The final bound receipt must be generated from a real worktree whose folder basename is `kelly-uniforms-business`, because the shared project validator intentionally rejects a checkout whose directory name does not match the project identity. A filesystem junction was tested and rejected by the validator, so no verifier or custody rule was weakened.

