# Verification

This file preserves the useful verification owner found in `origin/master` while updating it for the repository's current Work Scope state and brand-gallery deliverable. The retired `CURRENT-TASK.md`, `WORK_QUEUE.md`, and `STATUS.md` files from that history are intentionally not restored.

## Project and task state

```powershell
pwsh -NoProfile -File C:\Users\dougl\.agents\tools\Test-WorkState.ps1 -Root C:\Users\dougl\Projects\kelly-uniforms-business
pwsh -NoProfile -File C:\Users\dougl\.agents\tools\Reconcile-WorkState.ps1 -Root C:\Users\dougl\Projects\kelly-uniforms-business
pwsh -NoProfile -File C:\Users\dougl\.agents\tools\Test-TaskStateFormat.ps1 -Root C:\Users\dougl\Projects\kelly-uniforms-business
```

## Brand gallery

```powershell
Set-Location C:\Users\dougl\Projects\kelly-uniforms-business\brand-gallery
npm test
```

After a production deployment, verify the canonical URL returns HTTP 200, includes the `Quartermaster` recommendation, serves all three full-size direction boards and the self-hosted font, and contains no credential values or private recovery mechanics.

## Recovery packages

Run each acceptance command recorded in `.agents/work/state.json` through `Invoke-WorkScopeEvidence.ps1`. Do not substitute an ad hoc command for a recorded evidence gate.

## Secret and source scan

```powershell
C:\Users\dougl\Tools\gitleaks\gitleaks.exe dir --no-banner --redact C:\Users\dougl\Projects\kelly-uniforms-business
```

## Manual evidence

- Trace every `Confirmed` and `Observed` claim in `CLIENT.md` to `SOURCES.md`.
- Confirm every supplied request appears once in `DELIVERABLES.md`.
- Confirm active, verified, and delivered items define acceptance evidence.
- Confirm every data-root asset checksum matches `data-manifest.yaml`.
- Confirm administrative account identifiers and credential values remain outside tracked files.
- For browser-visible work, preserve desktop and mobile evidence and verify the published result.
