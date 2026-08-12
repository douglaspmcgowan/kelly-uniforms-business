<!-- GENERATED FROM .agents/work/state.json. DO NOT EDIT DIRECTLY. -->
# Active Work


Project: kelly-uniforms-business
Initiative: mt-uniforms-replatform
Primary track: business-continuity
Capability: public-cart-session-diagnosis
Depth: D1 (Direct)
Frontier mode: expand
Depth ceiling: D5
Breadth boundary: project
Selection strategy: dependency-first
Status: closed

## Goal

Complete and verify Reproduce and record the public www/non-www OpenCart cart-session split without authenticated access at D1.

## In scope

- public-cart-session-diagnosis

## Out of scope

- None

## Done when

- Every task below is closed.
- Scope-cell verification evidence is recorded.
- Generated views reconcile with canonical state.

## Tasks

- [x] prove-public-cart-host-session-split: Prove the public OpenCart www/non-www cart-session split with an option-complete add (status: closed; acceptance: A disposable unauthenticated option-complete add succeeds on www, its generated cart link uses the bare host, the product is present only in the www cart, cookie domains prove separate sessions without recording values, and the source ledger and client runbook record the confirmed root cause and hosting repair boundary.)

## Declared acceptance checks

- prove-public-cart-host-session-split/public-cart-host-session-split-live: C:\Program Files\WindowsApps\Microsoft.PowerShell_7.6.4.0_x64__8wekyb3d8bbwe\pwsh.exe argv=["-NoProfile","-File","scripts/Test-PublicCartHostSessionSplit.ps1","-OutputPath","evidence/2026-08-12-public-cart-host-session-split.json"]; inputs=[scripts/Test-PublicCartHostSessionSplit.ps1]; artifacts=[CLIENT.md, evidence/2026-08-12-public-cart-host-session-split.json, evidence/2026-08-12-public-cart-host-session-split.md, scripts/Test-PublicCartHostSessionSplit.ps1, SOURCES.md, WEBSITE-UPDATE-RUNBOOK.md]; timeout=300s; max-output=1048576B

## Blockers and dependencies

- None

## Verification evidence

- [test/pass] prove-public-cart-host-session-split | .agents/work/evidence/b9b95b57-a941-4fe6-8851-540df6a52034.json | sha256:0f84e9af20a7 | receipt:b9b95b57-a941-4fe6-8851-540df6a52034

## Discoveries captured

- None

## Next transition

frontier_transition
