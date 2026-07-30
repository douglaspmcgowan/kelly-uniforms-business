# Verification

## Commands

Setup and shared repository state:

```powershell
C:\Users\dougl\.agents\tools\Test-AgentProjectState.cmd -Repository C:\Users\dougl\projects\kelly-uniforms-business
```

Client operating record:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\dougl\projects\kelly-uniforms-business\.agents\skills\client\scripts\Test-ClientProject.ps1 -Repository C:\Users\dougl\projects\kelly-uniforms-business
```

Client skill structure:

```powershell
$env:PYTHONPATH = "C:\Users\dougl\projects\kelly-uniforms-business\.validator-deps"
C:\Users\dougl\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B -X utf8 C:\Users\dougl\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\dougl\projects\kelly-uniforms-business\.agents\skills\client
```

Secret and source scan:

```powershell
C:\Users\dougl\Tools\gitleaks\gitleaks.exe dir --no-banner --redact C:\Users\dougl\projects\kelly-uniforms-business
```

## Manual evidence

- Trace every `Confirmed` and `Observed` claim in `CLIENT.md` to `SOURCES.md`.
- Confirm every supplied request appears once in `DELIVERABLES.md`.
- Confirm active, verified, and delivered items define acceptance evidence.
- Confirm the seven data-root asset checksums match `data-manifest.yaml`.
- Confirm the administrative account identifier and credential value remain outside tracked files.
- For future live-site work, capture desktop/mobile evidence and a recovery record.

## Current build status

The repository is in intake and delivery-governance mode. Application lint, build, and browser test commands will be added when a software deliverable becomes active.
