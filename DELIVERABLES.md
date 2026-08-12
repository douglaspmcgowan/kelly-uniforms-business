# Deliverables

Last updated: 2026-08-09

## Delivery rules

- A client request enters as `Requested`.
- Commercial commitment requires an authoritative approval source.
- Completion requires recorded acceptance evidence.
- Scope changes receive a dated change record.
- Live-system changes require a reversible path and browser verification.

## Register

| ID | Priority | Deliverable | Desired outcome | Scope status | State | Owner | Dependencies | Acceptance evidence | Source | Next action |
|---|---|---|---|---|---|---|---|---|---|---|
| `DEL-001` | P0 | Publish temporary website ordering notice | Preserve order continuity during cart/connectivity failures | Client-requested and Douglas-authorized; candidate OpenCart/Journal 3 path documented; authenticated controls pending | Active, blocked by access | Codex after value-safe login | Fresh signed-in handoff or completed broker, mailbox and phone readiness, verified Journal controls, current settings export | Notice appears at the top on desktop/mobile and core routes; exact approved text and links render; ordering contacts work; existing page remains usable | `MSG-001`, `MSG-003`, `MSG-005`, `DEC-002`, `DEC-003`, `WEB-002`–`WEB-007`, `OBS-001`, `OBS-003` | Resume from `TASK.md`; follow `WEBSITE-UPDATE-RUNBOOK.md` after value-safe authentication |
| `DEL-002` | P1 | Diagnose cart and connection failures | Restore reliable online ordering or identify a bounded repair path | Mentioned problem; repair scope open; leading root-cause hypothesis recorded | Proposed | Unassigned | Reproduction steps, platform ownership, integrations, logs, test order authority | Each failure reproduced; root cause evidenced; repair verifier agreed before changes | `MSG-001`, `OBS-004` | Prove or disprove the www/non-www session-split hypothesis with one option-complete add-to-cart on `www` followed by cart reads on both hosts |
| `DEL-003` | P2 | Define and deliver the future website | Replace the aging/unreliable storefront with an approved client experience | Future intent; commercial and product scope open | Proposed | Unassigned | Discovery, content/product inventory, platform decision, domain/DNS ownership, budget, timeline, compliance, migration plan | Acceptance criteria require client discovery and written approval | `MSG-001` | Run outcome-first discovery after continuity work is stable |
| `DEL-004` | Internal | Initialize governed client repository and reusable `client` skill | Give the consulting practice a durable operating record for this and future clients | Douglas-approved internal scope | Verified | Codex | Shared harness, skill portability contract, supplied context and assets | Skill validator passes; profile, delivery ledger, sources, manifests, state, and repository verifier pass | `MSG-002`, `DEC-001` | Use the skill on the next client intake and revise only from observed failure evidence |
| `DEL-005` | P0 | Preserve the digital estate and business data | Retain rebuild-ready raw exports, normalized data, provenance, and restore evidence if current web systems disappear | Douglas-authorized; REC-008 is public-complete and package-local import-ready; live-session audit confirmed both OpenCart and Ecwid are signed out; Clover authentication excluded | Active, blocked at private-source access | Codex | Value-safe OpenCart/Ecwid access, hosting and ownership access, encrypted backup destinations | Native exports hash and reconcile; SQLite integrity/FKs pass; isolated restore reconstructs representative catalog, B2B, order, fulfillment, and return scenarios | `MSG-005`, `MSG-006`, `REC-001`–`REC-008`, `DEC-005` | Provision Path B resource bindings or a fresh signed-in handoff; then stage OpenCart first and Ecwid second through the packaged REC-008 command |
| `DEL-006` | P2 | Frame the future brand and visual direction | Give the client clear modern identities to select before website design | Douglas-authorized concept and gallery scope; client selection pending | Published for selection | Codex | Sourced client intent, preserved assets, rights and trademark review | Three distinct boards and rationale exist in a verified public gallery; selected route later passes vector, small-size, one-color, embroidery, accessibility, and rights checks | `MSG-005`, `MSG-007`, `FILE-001`–`FILE-007`, `BRAND-001`–`BRAND-003`, `WEB-008` | Share the gallery and collect a direction decision; recommendation is Quartermaster with One Mission's documentary warmth |

## Detail

### DEL-001 — Temporary website ordering notice

- Desired outcome: Keep prospective customers ordering while unreliable commerce functions are visible.
- Requested artifact/change: Add a prominent top-of-site notice using the client’s supplied wording: “New Website Coming! For all orders email orders@mtuniforms.com or call us directly at (814) 536-2390.”
- In scope: Reversible notice implementation after the live platform and contact readiness are confirmed.
- Exclusions: Cart repair, platform migration, future-site design, DNS changes, and checkout replacement remain separately scoped.
- Dependencies and client inputs: website-admin values delivered through the selected Bitwarden Secrets Manager broker. Douglas confirmed the mailbox and phone are ready and authorized publication on 2026-08-09.
- Acceptance evidence: Desktop and mobile screenshots, DOM/text check, `mailto:` and `tel:` link checks if used, and regression check of primary navigation/catalog access.
- Risk and recovery: A theme/header edit can affect every page. Back up/export the current configuration or record the exact prior value before mutation, then restore it if layout or navigation regresses.
- Owner: Codex after value-safe login.
- State: Active, blocked by access.
- Source: `MSG-001`, `MSG-007`, `DEC-007`, `DEC-011`.
- Next action: Finish Path B provisioning, run the approved broker, then follow `WEBSITE-UPDATE-RUNBOOK.md` and preview the Journal Header Notice in Admin Only mode.

### DEL-002 — Cart and integration diagnosis

- Desired outcome: Establish the real failure boundary and a safe repair plan.
- Requested artifact/change: Reproduce the client-reported broken cart link and unspecified connection failures.
- In scope: Diagnostic proposal only until Douglas activates the work.
- Exclusions: Production repair and test purchases lack current authority.
- Dependencies and client inputs: Exact reproduction paths, platform/admin access, integration inventory, expected behavior, and permission for any test order.
- Acceptance evidence: Reproduced failures with URLs/steps and recorded observed behavior; root-cause evidence tied to the relevant system.
- Risk and recovery: Avoid live orders, inventory changes, customer notifications, or payment actions during diagnosis without explicit approval.
- Owner: Unassigned.
- State: Proposed.
- Source: `MSG-001`.
- Next action: Collect exact failing paths once access is available.

### DEL-003 — Future website

- Desired outcome: Create a reliable, maintainable ordering and inquiry experience aligned with MT Uniforms’ current business.
- Requested artifact/change: Scope remains open; the temporary notice announces future intent.
- In scope: Discovery and option framing after approval.
- Exclusions: Platform, feature set, catalog migration, design direction, schedule, and fees remain open.
- Dependencies and client inputs: Desired business outcome, customer research, product/catalog source of truth, order workflow, current systems, brand rights, accessibility target, stakeholder/approver map, budget, and launch constraints.
- Acceptance evidence: Define through discovery before build authorization.
- Risk and recovery: Preserve the current domain, catalog, order history, customer data, SEO value, and a tested rollback path.
- Owner: Unassigned.
- State: Proposed.
- Source: `MSG-001`.
- Next action: Schedule discovery after `DEL-001` and the diagnostic decision.

### DEL-004 — Client operating repository and reusable skill

- Desired outcome: Make every client project legible, sourced, verifiable, and ready for governed delivery.
- Requested artifact/change: Reusable `client` skill, client profile, deliverables file, source/asset ledger, and normal repository harness.
- In scope: Local repository and project-bound skill; global canonical installation follows validation.
- Exclusions: Live website mutation.
- Dependencies and client inputs: Supplied context and assets.
- Acceptance evidence: Official skill validator, client-project validator, repository harness verifier, source trace, and adversarial review.
- Risk and recovery: All work remains local and uncommitted; source assets remain preserved.
- Owner: Codex.
- State: Verified.
- Source: `MSG-002`, `DEC-001`.
- Next action: Use the skill on the next client intake and revise only from observed failure evidence.

### DEL-005 — Digital-estate and business-data preservation

- Desired outcome: Rebuild the storefront and non-POS operating record without depending on OpenCart, Journal, Ecwid, or the current host; Clover remains the retained external in-store POS.
- Requested artifact/change: Native raw exports, a portable normalized SQLite model with lineage, media and configuration files, checksums, encrypted redundant copies, and tested restore procedures.
- In scope: Public-site recovery, authenticated OpenCart/Ecwid exports, source IDs and mappings, infrastructure ownership, business operational data, reconciliation, and documentation of Clover as the retained POS boundary.
- Exclusions: Credential values, session cookies, PAN/CVV data, and an unsupported claim that a public crawl is a complete backup.
- Dependencies and client inputs: Value-safe authenticated access or hosting exports; ownership records; retention and privacy decisions for restricted and customer data.
- Acceptance evidence: Work Scope execution receipts, package checksums, native source counts, row-level lineage, financial reconciliation, and an isolated representative business restore.
- Risk and recovery: Keep raw exports immutable; normalize only after capture; encrypt restricted copies; retain source-specific restore paths and rollback evidence.
- Owner: Codex for the recovery system; account owners for access-only exports.
- State: Active, blocked at private-source access. REC-008 preserves all 1,542 exact public media binaries and the retired AddThis disposition, while packaging the versioned validator, source-fidelity schema extension, transactional importer, contracts, and a package-level raw staging/checksum command. The fresh database remains deliberately empty of private business rows. A 2026-08-10 live-session audit confirmed that the preserved OpenCart tab and Ecwid control panel both resolve to login forms and that no alternate connected browser session is available. Private OpenCart/Ecwid, hosting, account-control, and encrypted redundant custody remain incomplete. Clover authentication is outside current scope.
- Source: `MSG-005`, `MSG-006`, `REC-001`–`REC-008`, `DEC-005`.
- Next action: Complete the non-secret Path B project/resource bindings (or provide a fresh signed-in handoff), then acquire the full OpenCart database, webroot, external storage, versions, and logs before Ecwid ingestion.

### DEL-006 — Brand and visual-direction framing

- Desired outcome: Replace the dated, inconsistent identities with a coherent system suited to a broad uniform, customization, and equipment business.
- Requested artifact/change: Three premium identity and website-aesthetic direction boards plus a documented recommendation.
- In scope: Service Standard, Quartermaster, and One Mission concept routes; logo-system diagnosis; site-aesthetic implications.
- Exclusions: Final trademark, production vector logo, public launch, and unconfirmed slogan or image rights.
- Dependencies and client inputs: Client selection, rights confirmation, approved naming/slogan, and authentic photography for the community-led route.
- Acceptance evidence: Three hashed PNG boards and rationale under `PROJECT_DATA_ROOT\outputs\brand-directions\2026-08-08`; tested production gallery at <https://mt-uniforms-brand-directions.vercel.app/>; independent visual-review disposition `ship`.
- Risk and recovery: Treat generated boards as decision aids; redraw the selected mark deterministically and verify physical/digital applications before production.
- Owner: Codex for concept framing; client for selection.
- State: Published for client selection. The public gallery includes current non-sensitive project status and excludes credentials and private recovery mechanics.
- Source: `MSG-005`, `MSG-007`, `FILE-001`–`FILE-007`, `BRAND-001`–`BRAND-003`, `WEB-008`, `DEC-012`.
- Next action: Share the gallery and select one direction or a deliberate hybrid; current recommendation is Quartermaster plus One Mission's photography and warmth.

## Change record

| Date | Deliverable | Change | Source | Impact |
|---|---|---|---|---|
| 2026-07-26 | `DEL-001`–`DEL-004` | Initial delivery register created from the client intake and Douglas’s repository/skill request | `MSG-001`, `MSG-002`, `DEC-001` | Establishes request states and prevents future-site intent from silently becoming approved build scope |
| 2026-07-26 | `DEL-001` | Selected Bitwarden Secrets Manager names and documented the pending browser-broker boundary | `DEC-002` | Makes the credential-entry path explicit without placing values in the repository |
| 2026-07-26 | `DEL-001` | Verified public OpenCart/Journal 3 signals and documented a conditional Header Notice workflow | `WEB-002`–`WEB-006`, `OBS-001` | Gives Douglas a likely reversible path with an authenticated verification gate |
| 2026-07-31 | `DEL-001` | Persisted the complete plan, current live recheck, logo access, decision gates, execution order, verification, and rollback path for Claude resumption | `MSG-003`, `DEC-003`, `OBS-003` | Makes the repository the durable cross-agent handoff without authorizing or performing a production change |
| 2026-07-31 | `DEL-001`, `DEC-002` | Corrected the runbook for the pre-existing Header Notice module 56, recorded existing Journal Custom CSS, separated the two logins by purpose, and replaced the incorrect "bws installed" access claim with the four concrete broker prerequisites | `OBS-004` | Prevents a duplicate stacked banner, prevents Custom CSS loss on restore, and makes the access decision actionable |
| 2026-07-31 | `DEL-002` | Recorded the www/non-www session-split hypothesis and a single falsifying test | `OBS-004` | Moves cart diagnosis from "no reproduction" to one bounded experiment; also relocates the fix from theme to server/OpenCart configuration |
| 2026-08-08 | `DEL-005` | Created and durably placed a verified public-storefront recovery checkpoint with normalized SQLite data, media, provenance, checksums, archive, and restore evidence | `MSG-005`, `REC-001` | Converts the public digital estate from a vendor-dependent site into a portable continuity checkpoint while exposing the remaining private-data gaps |
| 2026-08-09 | `DEL-005` | Preserved REC-001 and created REC-002 with relative lineage paths, explicit SQLite schema/application identity, a packaged verifier, immutable private mirrors, and a fresh isolated archive restore | `REC-002` | Removes machine-local paths and makes the public checkpoint independently verifiable after extraction |
| 2026-08-09 | `DEL-005` | Preserved REC-002 and created REC-003 with current public DNS, RDAP, TLS, HTTP, legal/trade-name, retail-licence, contact, operational-workflow, and dealer evidence normalized through record-level provenance | `REC-003` | Adds rebuild-critical public ownership and operational context while explicitly retaining private account-control gaps |
| 2026-08-10 | `DEL-005` | Preserved REC-003 and created REC-004 with 34 directly captured public JavaScript/font binaries, refreshed scope metadata, SQLite lineage, fresh checksums, and a successful isolated archive restore | `REC-004` | Closes the reachable public-runtime gap while retaining one explicit third-party DNS failure and every private-data boundary |
| 2026-08-10 | `DEL-005` | Preserved REC-004 and created REC-005 with 35 normalized commerce tables, mandatory source lineage, zero synthesized business rows, fresh checksums, and a successful isolated archive restore | `REC-005` | Makes later OpenCart/Ecwid ingestion structurally ready without misrepresenting inaccessible private data as recovered |
| 2026-08-10 | `DEL-005` | Preserved REC-005 and created REC-006 by retrying all 430 unresolved public image URLs; every one was captured with exact binary provenance, then package-only restore verified | `REC-006` | Exhausts the current public-media gap while preserving private-data boundaries |
| 2026-08-10 | `DEL-005` | Preserved REC-006 and created REC-007 by extracting the final embedded PNG and recording the retired AddThis dependency with authoritative shutdown evidence and failed retrieval history | `REC-007` | Completes exact public-media preservation and distinguishes a dead vendor dependency from a recoverable missing file |
| 2026-08-10 | `DEL-005` | Audited the live in-app browser without inspecting credential/session stores; both OpenCart and Ecwid resolve to login forms and no alternate connected browser exists | `evidence/2026-08-10-recovery-completion-audit.md` | Establishes that every remaining private-source requirement depends on value-safe authentication, hosting/ownership access, or an encryption recipient |
| 2026-08-10 | `DEL-005` | Added and executed the versioned OpenCart/Ecwid import-bundle contract and fail-closed validator; nine focused tests passed on Work Scope receipt `35d39aa8-0551-4199-b103-6b3eb4933f94` | `evidence/2026-08-10-commerce-import-contract.md` | Makes future authenticated exports deterministically acceptable or rejectable without synthesizing inaccessible private records |
| 2026-08-10 | `DEL-005` | Added the source-fidelity schema extension and transactional normalized-bundle importer; six importer tests and 27 total focused recovery tests passed on receipt `321e01c1-d421-44d7-8cfe-5f18a1286445` | `evidence/2026-08-10-commerce-bundle-importer.md` | Makes accepted source bundles ingestible with exact lineage, idempotency and rollback while keeping REC-007 immutable |
| 2026-08-10 | `DEL-005` | Preserved REC-007 and created REC-008 with package-local validation, raw-byte staging, normalized import, checksum refresh, restricted redundant copies, and a successful package-only isolated restore | `REC-008` | Makes future authenticated OpenCart/Ecwid exports safely ingestible without repository dependencies or invented private rows |
| 2026-08-08 | `DEL-006` | Audited both existing identities and produced three sourced visual directions with a recommended route | `MSG-005`, `BRAND-001`–`BRAND-003` | Gives the future website a concrete client decision before UI implementation begins |
| 2026-08-09 | `DEL-006` | Built, independently reviewed, tested, and published the stakeholder gallery with public project status and three brand directions | `MSG-007`, `WEB-008`, `DEC-012` | Gives the client a stable decision URL while keeping credentials and private recovery mechanics off the public surface |
