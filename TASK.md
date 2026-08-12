<!-- GENERATED FROM .agents/work/state.json. DO NOT EDIT DIRECTLY. -->
# Active Work


Project: kelly-uniforms-business
Initiative: mt-uniforms-replatform
Primary track: intake
Capability: intake.external
Depth: D1 (Direct)
Frontier mode: expand
Depth ceiling: D5
Breadth boundary: project
Selection strategy: dependency-first
Status: active

## Goal

Complete and verify This project is the only one still on the portable:v3 project contract, because EnsureProject refuses on a legacy VERIFY.md at D1.

## In scope

- intake.external

## Out of scope

- None

## Done when

- Every task below is closed.
- Scope-cell verification evidence is recorded.
- Generated views reconcile with canonical state.

## Tasks

- [ ] upgrade-portable-project-contract-v4: Archive legacy root project architecture and upgrade the portable project contract to v4 (status: ready; acceptance: The three legacy root files are losslessly archived with hashes, removed from the root, AGENTS.md and provenance declare portable v4, project-owned recovery verification remains routed from the archive/evidence, Manage-Harness VerifyProject passes, and Work Scope state/views remain valid without overwriting imported legacy history.)

## Declared acceptance checks

- upgrade-portable-project-contract-v4/portable-v4-project-contract: C:\Program Files\WindowsApps\Microsoft.PowerShell_7.6.4.0_x64__8wekyb3d8bbwe\pwsh.exe argv=["-NoProfile","-File","scripts/Test-PortableV4ProjectContract.ps1"]; inputs=[scripts/Test-PortableV4ProjectContract.ps1]; artifacts=[.agents/archive/task-state-migration/archive-manifest.json, .agents/harness-provenance.json, AGENTS.md, evidence/2026-08-12-portable-v4-project-contract.md]; timeout=1800s; max-output=1048576B

## Blockers and dependencies

- None

## Verification evidence

- None

## Discoveries captured

- None

## Next transition

execute_task: upgrade-portable-project-contract-v4
