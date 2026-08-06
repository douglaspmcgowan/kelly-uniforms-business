# Task

## Goal

Publish the requested temporary ordering notice on mtuniforms.com through an
authorized, reversible production edit, while running client-intake/delivery
governance for MT Uniforms (David) under the `client` skill.

## Active

Mode: handoff complete; production execution remains pending explicit
Douglas authorization. Resume by reading `AGENTS.md`, `STATUS.md`, this file,
and `WEBSITE-UPDATE-RUNBOOK.md` (the single detailed execution procedure).
Keep credential values and administrative identifiers out of repository
files, chat, logs, screenshots, and tool output. Preserve the current public
site; use the documented preview, backup, verification, and rollback gates.

**Requested notice:**

> **New Website Coming!** For all orders email orders@mtuniforms.com or call us
> directly at (814) 536-2390.

The runbook makes the email/phone clickable (`mailto:`/`tel:`). Default scope
is banner-only; footer contact details stay unchanged unless Douglas expands
scope.

### 2026-07-31 architecture-scope findings (full detail: `evidence/2026-07-31-site-architecture-scope.md`, `OBS-004`)

1. A Header Notice module already exists (module 56, registered, rendered nothing on home page) — inspect module 56 first, decide edit vs. add.
2. Leading root cause of the reported cart failure: a www/non-www host split (`www.mtuniforms.com` serves 200 without redirecting; page declares canonical non-www; `OCSESSID` is host-only so www/non-www hold separate carts). Server/OpenCart config fix, belongs to `DEL-002`.
3. Ecwid renders no part of the public site; role still unverified but off the critical path.
4. No analytics installed anywhere (no GA/GA4/GTM/pixel).
5. Journal demo placeholder copy is live in the main menu, visible to every customer.
6. Journal Custom CSS already in use (mobile logo replacement, two hidden modules) — any export/restore must preserve it.
7. Published phone `814-536-2390` matches the requested notice but is not tappable anywhere (no `tel:`/`mailto:` links exist). `800-535-0134` and `sales@mtuniforms.com` from `CLIENT.md` were not found live and need re-sourcing or retiring.

### Verified current state (2026-07-30, read-only; evidence: `evidence/2026-07-30-public-site-recheck.md`)

Live storefront rechecked; requested notice absent; OpenCart/Journal 3 assets visible; `www.mtuniforms.com/admin/` is a live OpenCart admin login; no rendered Ecwid asset URL observed; client-supplied logo + 6 raster assets available locally under the project data root; existing 299x82 header logo accessible. No credentials entered, no live state changed.

## Blocked

- [!] **Rotate the OpenCart administrator password** — exposed in cleartext in a prior session transcript. Rotate the Ecwid credential too.
- [!] Path B (unattended Bitwarden-brokered login) blocked on Douglas: create the four `mtuniforms.*` secrets in the `Agent Runtime` Bitwarden project, grant the machine account read access + run `Set-BwsMachineToken.ps1`, and return the non-secret project ID + four resource IDs to fill the allowlist placeholders. (`bws.exe` 2.1.0 installed + checksum-verified; broker Playwright self-tested; pipeline confirmed to fail only at credential retrieval.)
- [!] Apply nginx 301 www → non-www, after confirming the TLS cert covers `www.mtuniforms.com`.

## Needs decision

- [?] Confirm `orders@mtuniforms.com` is monitored and ready for order intake.
- [?] Confirm `(814) 536-2390` reaches the intended order-taking line.
- [?] Confirm banner-only scope, or explicitly authorize footer contact changes.
- [?] Choose the access path: **Path A** — Douglas signs in at the admin URL in the Browser pane and hands off the authenticated session (available immediately); or **Path B** — the blocked broker above.
- [?] Give explicit authorization for the production edit after the above resolve.
- [?] Ask David whether any agency runs a per-officer uniform allowance or requires authorization codes (decides platform).
- [?] Obtain the Clover merchant agreement terms (ISO, term length, early-termination fee, lease status, surcharging).
- [?] Get written confirmation from Shopify sales on whether customer-specific catalogs work on non-Plus plans (sources contradict; primary recommendation depends on it).
- [?] Who owns/pays for the domain, DNS, hosting, and the Journal 3 licence.

## Queue

- [ ] Authenticate read-only and verify production-store identity, installed OpenCart/Journal versions, Header Notice control, All-layouts control, and modify permission.
- [ ] Inspect existing Header Notice module 56 (name, status, content, layout assignment) before creating or editing any notice module.
- [ ] Prove/disprove the www/non-www session-split hypothesis with one option-complete add-to-cart on `www` followed by cart reads on both hosts.
- [ ] Export current Journal settings and record any existing Header Notice state.
- [ ] Create `MT Temporary Ordering Notice` in Admin Only state; assign via Special Modules → All layouts.
- [ ] Preview and verify exact copy, links, layout, cookie-bar coexistence, and core navigation on desktop and phone/mobile-user-agent views.
- [ ] Publish globally, verify in a private browser, capture desktop/mobile acceptance evidence.
- [ ] Roll back immediately if the notice disrupts header, navigation, search, login, cart, or readability.
- [ ] After continuity is stable and separately authorized: reproduce the reported cart/connection failures via the systematic-debugging workflow.
- [ ] After continuity is stable and separately authorized: determine Ecwid's current operational role.
- [ ] Run outcome-first discovery before defining or building the future website.
- [ ] Run the 12-officer acceptance test in a trial account for each finalist platform before any commitment.
- [ ] Request a VPAT in writing from every finalist platform ahead of the 2027/2028 DOJ WCAG 2.1 AA deadlines.
- [ ] Book demos with UniformMarket and qUniform if David confirms an allowance program exists.

## Completed

- [x] Researched client-intake/discovery/delivery mechanisms; installed the reusable `client` skill with deterministic templates/scripts; validated and adversarially forward-tested it.
- [x] Ran the skill for MT Uniforms: sourced client profile + deliverables register.
- [x] Finished repo contract, data/asset map, project state, access documentation, verification evidence.
- [x] Verified live storefront platform, admin route, reversible notice mechanism; documented the Journal 3 Header Notice workflow (`DEL-001`).
- [x] Rechecked live storefront/admin/Journal signals/notice state/logo access without credentials or mutations.
- [x] Scoped live site architecture, stack, modules, integrations, cart mechanics without credentials (`evidence/2026-07-31-site-architecture-scope.md`).
- [x] Documented both logins and exact unblock steps for each access path in `ACCESS.md`.
- [x] Wrote `scripts\New-MtUniformsCredentialPlaceholders.ps1` for Douglas to fill in.
- [x] Located prior Codex session findings and reconciled into the repo (`evidence/2026-07-31-codex-session-reconciliation.md`).
- [x] Wrote two headless Bitwarden-brokered login scripts; registered value-safe allowlist entries.
- [x] Updated `secret-manifest.json` to the harness `Agent Runtime` prefixed-key convention.
- [x] Recorded public vs. private client contact info in `CLIENT.md`.
- [x] Wrote `STORE-REQUIREMENTS.md` and ran/synthesized parallel platform recon (`PLATFORM-RECOMMENDATION.md`).
- [x] Documented in-app-browser vs. Claude-in-Chrome vs. Playwright tradeoffs in `ACCESS.md`.
- [x] Installed `bws.exe` 2.1.0 at the broker's pinned path (checksum-verified) and Playwright in `scripts\broker\`; self-tested headless Chromium against the live login form.
- [x] Verified the assembled broker pipeline fails at credential retrieval rather than any dependency check.
- [x] Gitignored `node_modules/` and `package-lock.json` for the broker install.

## Verification

- Setup and shared repository state: `C:\Users\dougl\.agents\tools\Test-AgentProjectState.cmd -Repository C:\Users\dougl\projects\kelly-uniforms-business`
- Client operating record: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\dougl\projects\kelly-uniforms-business\.agents\skills\client\scripts\Test-ClientProject.ps1 -Repository C:\Users\dougl\projects\kelly-uniforms-business`
- Client skill structure: `$env:PYTHONPATH = "C:\Users\dougl\projects\kelly-uniforms-business\.validator-deps"` then run `quick_validate.py` against `.agents\skills\client` (see prior VERIFY.md for the exact Codex-runtime python path)
- Secret/source scan: `C:\Users\dougl\Tools\gitleaks\gitleaks.exe dir --no-banner --redact C:\Users\dougl\projects\kelly-uniforms-business`
- Manual evidence: trace every `Confirmed`/`Observed` claim in `CLIENT.md` to `SOURCES.md`; confirm every supplied request appears once in `DELIVERABLES.md`; confirm active/verified/delivered items define acceptance evidence; confirm the seven data-root asset checksums match `data-manifest.yaml`; confirm the administrative account identifier and credential value remain outside tracked files; for future live-site work, capture desktop/mobile evidence and a recovery record.
- Current build status: repository is in intake and delivery-governance mode; application lint/build/browser-test commands will be added when a software deliverable becomes active.

## Next verifier

After Douglas resolves the "Needs decision" items above, authenticate read-only and verify the production store identity plus the installed Journal controls before any production mutation.
