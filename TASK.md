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
Status: closed

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

- [ ] upgrade-portable-project-contract-v4: Archive legacy root project architecture and upgrade the portable project contract to v4 (status: retired; acceptance: The three legacy root files are losslessly archived with hashes, removed from the root, AGENTS.md and provenance declare portable v4, project-owned recovery verification remains routed from the archive/evidence, Manage-Harness VerifyProject passes, and Work Scope state/views remain valid without overwriting imported legacy history.)
- [x] verify-portable-project-contract-v4: Verify the generated portable-v4 project contract and lossless task-state archive (status: closed; acceptance: The three legacy root files are losslessly archived with hashes and absent from root; AGENTS carries only the v4 marked block; provenance matches the generator-supported authority; Manage-Harness VerifyProject passes; Work Scope remains valid and reconciled.)

## Declared acceptance checks

- upgrade-portable-project-contract-v4/portable-v4-project-contract: C:\Program Files\WindowsApps\Microsoft.PowerShell_7.6.4.0_x64__8wekyb3d8bbwe\pwsh.exe argv=["-NoProfile","-File","scripts/Test-PortableV4ProjectContract.ps1"]; inputs=[scripts/Test-PortableV4ProjectContract.ps1]; artifacts=[.agents/archive/task-state-migration/archive-manifest.json, .agents/harness-provenance.json, AGENTS.md, evidence/2026-08-12-portable-v4-project-contract.md]; timeout=1800s; max-output=1048576B
- verify-portable-project-contract-v4/portable-v4-project-contract-corrected: C:\Program Files\WindowsApps\Microsoft.PowerShell_7.6.4.0_x64__8wekyb3d8bbwe\pwsh.exe argv=["-NoProfile","-File","scripts/Test-PortableV4ProjectContract.ps1"]; inputs=[scripts/Test-PortableV4ProjectContract.ps1]; artifacts=[.agents/archive/task-state-migration/archive-manifest.json, .agents/harness-provenance.json, AGENTS.md, evidence/2026-08-12-portable-v4-project-contract.md]; timeout=1800s; max-output=1048576B

## Blockers and dependencies

- None

## Verification evidence

- [test/pass] verify-portable-project-contract-v4 | .agents/work/evidence/53a3f255-7f28-403c-8b24-1e42a84ff4a9.json | sha256:2990d5c47003 | receipt:53a3f255-7f28-403c-8b24-1e42a84ff4a9

## Discoveries captured

- None

## Next transition

frontier_transition
