# Deliverables

Last updated: 2026-07-26

## Delivery rules

- A client request enters as `Requested`.
- Commercial commitment requires an authoritative approval source.
- Completion requires recorded acceptance evidence.
- Scope changes receive a dated change record.
- Live-system changes require a reversible path and browser verification.

## Register

| ID | Priority | Deliverable | Desired outcome | Scope status | State | Owner | Dependencies | Acceptance evidence | Source | Next action |
|---|---|---|---|---|---|---|---|---|---|---|
| `DEL-001` | P0 | Publish temporary website ordering notice | Preserve order continuity during cart/connectivity failures | Client-requested; candidate OpenCart/Journal 3 path documented; authenticated controls pending | Requested | Unassigned pending delivery authorization | Populate website-admin Secrets Manager values, verify the broker for agent operation or use an authorized manual login, confirm mailbox and phone readiness, verify Journal controls, export Journal settings | Notice appears at the top on desktop/mobile and core routes; exact approved text and links render; ordering contacts work; existing page remains usable | `MSG-001`, `DEC-002`, `WEB-002`–`WEB-007`, `OBS-001` | Follow `WEBSITE-UPDATE-RUNBOOK.md`; verify the authenticated Journal controls before editing |
| `DEL-002` | P1 | Diagnose cart and connection failures | Restore reliable online ordering or identify a bounded repair path | Mentioned problem; repair scope open | Proposed | Unassigned | Reproduction steps, platform ownership, integrations, logs, test order authority | Each failure reproduced; root cause evidenced; repair verifier agreed before changes | `MSG-001` | Capture exact failing flows after access is established |
| `DEL-003` | P2 | Define and deliver the future website | Replace the aging/unreliable storefront with an approved client experience | Future intent; commercial and product scope open | Proposed | Unassigned | Discovery, content/product inventory, platform decision, domain/DNS ownership, budget, timeline, compliance, migration plan | Acceptance criteria require client discovery and written approval | `MSG-001` | Run outcome-first discovery after continuity work is stable |
| `DEL-004` | Internal | Initialize governed client repository and reusable `client` skill | Give the consulting practice a durable operating record for this and future clients | Douglas-approved internal scope | Verified | Codex | Shared harness, skill portability contract, supplied context and assets | Skill validator passes; profile, delivery ledger, sources, manifests, state, and repository verifier pass | `MSG-002`, `DEC-001` | Use the skill on the next client intake and revise only from observed failure evidence |

## Detail

### DEL-001 — Temporary website ordering notice

- Desired outcome: Keep prospective customers ordering while unreliable commerce functions are visible.
- Requested artifact/change: Add a prominent top-of-site notice using the client’s supplied wording: “New Website Coming! For all orders email orders@mtuniforms.com or call us directly at (814) 536-2390.”
- In scope: Reversible notice implementation after the live platform and contact readiness are confirmed.
- Exclusions: Cart repair, platform migration, future-site design, DNS changes, and checkout replacement remain separately scoped.
- Dependencies and client inputs: Website-admin username and password in Bitwarden Secrets Manager; active mailbox; confirmed phone routing; approval for punctuation/capitalization and clickable email/phone links.
- Acceptance evidence: Desktop and mobile screenshots, DOM/text check, `mailto:` and `tel:` link checks if used, and regression check of primary navigation/catalog access.
- Risk and recovery: A theme/header edit can affect every page. Back up/export the current configuration or record the exact prior value before mutation, then restore it if layout or navigation regresses.
- Owner: Unassigned pending delivery authorization.
- State: Requested.
- Source: `MSG-001`.
- Next action: Follow `WEBSITE-UPDATE-RUNBOOK.md` in OpenCart and preview the Journal Header Notice in Admin Only mode.

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

## Change record

| Date | Deliverable | Change | Source | Impact |
|---|---|---|---|---|
| 2026-07-26 | `DEL-001`–`DEL-004` | Initial delivery register created from the client intake and Douglas’s repository/skill request | `MSG-001`, `MSG-002`, `DEC-001` | Establishes request states and prevents future-site intent from silently becoming approved build scope |
| 2026-07-26 | `DEL-001` | Selected Bitwarden Secrets Manager names and documented the pending browser-broker boundary | `DEC-002` | Makes the credential-entry path explicit without placing values in the repository |
| 2026-07-26 | `DEL-001` | Verified public OpenCart/Journal 3 signals and documented a conditional Header Notice workflow | `WEB-002`–`WEB-006`, `OBS-001` | Gives Douglas a likely reversible path with an authenticated verification gate |
