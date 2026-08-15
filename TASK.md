<!-- GENERATED FROM .agents/work/state.json. DO NOT EDIT DIRECTLY. -->
# Active Work


Project: kelly-uniforms-business
Initiative: mt-uniforms-replatform
Primary track: business-continuity
Capability: portable-recovery-repository-custody
Cell: portable-recovery-repository-custody@D3
Depth: D3 (Hardened)
Frontier mode: expand
Depth ceiling: D5
Breadth boundary: project
Selection strategy: dependency-first
Status: active

## Goal

Complete and verify Commit and push the verified portable recovery system and Work Scope authority to the remote repository at D3.

## In scope

- portable-recovery-repository-custody

## Out of scope

- None

## Done when

- Every task below is closed.
- Scope-cell verification evidence is recorded.
- Generated views reconcile with canonical state.

## Tasks

- [ ] publish-portable-recovery-system: Commit and push the portable recovery system and Work Scope authority (status: ready; acceptance: The remote master tree contains the complete value-safe recovery toolchain, contracts, schemas, tests, evidence, data adapter, brand gallery, generated Work Scope views, canonical state/event/import history, and current REC-016 routing; runtime locks and bytecode are excluded; Gitleaks finds no secrets; all 78 recovery tests, adapter tests, frontend tests/builds, and Work Scope gates pass; the final verifier proves the local tree equals origin/master.)

## Declared acceptance checks

- publish-portable-recovery-system/portable-recovery-repository-custody: C:\Program Files\WindowsApps\Microsoft.PowerShell_7.6.4.0_x64__8wekyb3d8bbwe\pwsh.exe argv=["-NoProfile","-File","scripts/Test-PortableRecoveryRepository.ps1","-RequireRemoteTree"]; inputs=[scripts/Test-PortableRecoveryRepository.ps1]; artifacts=[evidence/2026-08-12-portable-recovery-repository-custody.md, MAP.md, scripts/Test-PortableRecoveryRepository.ps1, SOURCES.md, VERIFY.md]; timeout=3600s; max-output=1048576B

## Blockers and dependencies

- None

## Verification evidence

- None

## Discoveries captured

- shopify-basic-store-provisioning
- shopify-catalog-import
- opencart-data-offload-runbook
- clover-integration-setup
- shopify-conversion-workstream-has-no-workscope-cell-20260815
- confirm-physical-business-facts-with-the-client
- align-storefront-with-google-business-profile
- april-2026-ownership-change-reframes-the-data-migration
- agency-order-path-cannot-carry-a-twenty-officer-order
- six-products-advertise-an-unbuildable-price
- department-collections-are-nearly-empty-and-fire-ems-is-missing
- twenty-two-option-groups-are-named-literally-option
- reviews-band-provenance-is-not-defensible
- storefront-ships-an-undesigned-dark-mode

## Next transition

execute_task: publish-portable-recovery-system
