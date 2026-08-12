# Task

## Goal

Preserve enough of M&T Uniforms' digital estate to rebuild the business if the
current OpenCart, Journal, Ecwid, or Clover systems disappear; keep the
temporary ordering notice as the urgent production-continuity change; and give
the client a sourced set of modern brand directions before the future website
is designed.

## Active

Mode: business-continuity recovery and brand-direction handoff. Douglas has
authorized the data exports and the previously requested banner, but the
OpenCart session expired and the in-app browser has no saved autofill. Ecwid
and Clover also opened at login screens. Continue authenticated work only
through an existing signed-in session or the approved value-safe credential
broker; never retrieve credential values from email, vault notes, repository
files, chat, logs, screenshots, or tool output.

The public recovery checkpoint is now durably placed under
`PROJECT_DATA_ROOT\backups\business-continuity`. It is a verified public-site
continuity checkpoint and Journal-settings supplement; it is not yet a full
business-system backup. The three brand directions and selection rationale are
under `PROJECT_DATA_ROOT\outputs\brand-directions\2026-08-08`.

### Search record and touch list (2026-08-08)

- Searched the repository, project data root, recovery package, harness Work
  Scope tools, current browser tabs, and sourced client assets before adding an
  owner. Existing owners retained: `data-manifest.yaml` for external artifacts,
  `MAP.md` for architecture and paths, `DESIGN.md` for decisions,
  `SOURCES.md` for provenance, `DELIVERABLES.md` for client scope, and this file
  for active state.
- The established off-Git `backups` owner was extended for restricted recovery
  data. `outputs\brand-directions` was added because no existing owner held
  generated client decision aids.
- Touch list: `TASK.md`, `DELIVERABLES.md`, `MAP.md`, `DESIGN.md`, `CLIENT.md`,
  `SOURCES.md`, `STORE-REQUIREMENTS.md`, `data-manifest.yaml`, and `LOG.md`,
  plus the external continuity and brand-direction indexes. The retired
  `VERIFY.md` was consolidated into this file and archived outside Git.
- Work Scope enrollment remains unsafe: `Initialize-WorkScope.ps1` regenerates
  legacy `TASK.md`, `BACKBURNER.md`, and `LOG.md` before the importer can preserve
  them. The immutable migration snapshot and discovery payload are preserved in
  the recovery package; keep legacy task state authoritative until the harness
  migration-order defect is resolved and dry-run recovery proves no history loss.

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

- [!] **Rotate the OpenCart administrator password** — owner: Douglas; decision id: `mtu-opencart-credential-rotation-20260730`. The credential was exposed in a prior session transcript; rotate the Ecwid credential too.
- [!] Authenticated export and banner work — owner: Douglas; decision id: `mtu-production-access-path-20260806`. The preserved OpenCart tab and the Ecwid/Clover tabs resolve to login screens with no saved autofill. Resume through a fresh signed-in handoff or the approved broker; never copy a plaintext password into agent-visible input.
- [!] Path B (unattended Bitwarden-brokered login) — blocked on: Douglas. Create the four `mtuniforms.*` secrets in the `Agent Runtime` Bitwarden project, grant the machine account read access, run `Set-BwsMachineToken.ps1`, and return the non-secret project ID plus four resource IDs. (`bws.exe` 2.1.0 is checksum-verified; broker Playwright self-test passed; the pipeline stops at credential retrieval.)
- [!] Apply nginx 301 www → non-www — blocked on: hosting access and confirmation that the TLS certificate covers `www.mtuniforms.com`.

## Needs decision

- [?] Confirm `orders@mtuniforms.com` is monitored and ready for order intake — owner: Kelly or David; decision id: `mtu-orders-mailbox-readiness-20260808`.
- [?] Confirm `(814) 536-2390` reaches the intended order-taking line — owner: Kelly or David; decision id: `mtu-order-phone-readiness-20260808`.
- [?] Choose the production access path — owner: Douglas; decision id: `mtu-production-access-path-20260806`.
- [?] Ask David whether any agency runs a per-officer uniform allowance or requires authorization codes — owner: David; decision id: `mtu-agency-uniform-allowance-20260806`.
- [?] Get written Shopify confirmation on non-Plus customer-specific catalogs — owner: Douglas; decision id: `mtu-shopify-nonplus-catalogs-20260806`.

## Queue

- [ ] Export and hash the full OpenCart database, webroot, external storage, private media, configuration, versions, and logs after value-safe authentication or hosting access becomes available; done when: raw artifacts, hashes, source counts, and restore evidence are indexed outside Git.
- [ ] Export and hash complete Ecwid catalog, customer, order, configuration, source-ID, and media data; done when: every available export is preserved with hashes and the account is classified active or abandoned.
- [ ] Export and reconcile Clover inventory, customer, order, payment-reference, refund, settlement, configuration, and cross-system mapping data; done when: exports are hashed and record counts/totals reconcile or discrepancies are documented.
- [ ] Establish domain, DNS, TLS, hosting, mail, payment, shipping, subscription, and licence ownership; done when: every service has an owner, payer, renewal date, recovery contact, and export/recovery path in the restricted continuity inventory.
- [ ] Obtain the Clover merchant agreement terms: ISO, term length, early-termination fee, lease status, and surcharging; done when: the sourced terms are recorded without account secrets in `PLATFORM-RECOMMENDATION.md`.
- [ ] Add encrypted offline and independent offsite copies, then run a full private-data isolated restore; done when: two independent encrypted copies exist, the adapter can publish an encrypted artifact without its `private/` safety refusal, and a fresh restore passes the Business-continuity package gates below.
- [ ] Have the client select a brand direction; done when: Direction 1, 2, 3, or a documented hybrid is recorded in `DESIGN.md`. Current recommendation is Direction 2 (Quartermaster) with Direction 3's documentary warmth.
- [ ] Authenticate read-only and verify production-store identity, installed OpenCart/Journal versions, Header Notice control, All-layouts control, and modify permission; done when: value-free screenshots or notes record all six checks.
- [ ] Inspect existing Header Notice module 56 before creating or editing any notice module; done when: its name, status, content, and layout assignment are captured in the recovery record.
- [ ] Prove or disprove the www/non-www session-split hypothesis with one option-complete add-to-cart on `www` followed by cart reads on both hosts; done when: both host outcomes and cookie-domain evidence are recorded.
- [ ] Export current Journal settings and record any existing Header Notice state; done when: the export is hashed and its restore route is documented.
- [ ] Create `MT Temporary Ordering Notice` in Admin Only state and assign it through Special Modules to All layouts; done when: the unpublished module is visible in admin with the exact requested copy.
- [ ] Preview and verify exact copy, links, layout, cookie-bar coexistence, and core navigation on desktop and phone/mobile-user-agent views; done when: every Browser-visible production gate below passes.
- [ ] Publish globally and verify in a private browser; done when: desktop and mobile acceptance evidence shows the notice on all representative layouts.
- [ ] Roll back immediately if the notice disrupts header, navigation, search, login, cart, or readability; done when: either the published notice passes all gates or rollback evidence confirms the prior state was restored.
- [ ] After continuity is stable and separately authorized, reproduce the reported cart/connection failures through the systematic-debugging workflow; done when: a minimal reproduction and evidence-backed root cause are recorded.
- [ ] After continuity is stable and separately authorized, determine Ecwid's current operational role; done when: account status, catalog/order ownership, and replacement dependency are documented.
- [ ] Run outcome-first discovery before defining or building the future website; done when: client-approved outcomes, audiences, workflows, constraints, and acceptance criteria are recorded.
- [ ] Run the 12-officer acceptance test in a trial account for each finalist platform before any commitment; done when: the scored results are attached to `PLATFORM-RECOMMENDATION.md`.
- [ ] Request a VPAT in writing from every finalist platform ahead of the 2027/2028 DOJ WCAG 2.1 AA deadlines; done when: each response or non-response is recorded with date and source.
- [ ] Book demos with UniformMarket and qUniform if David confirms an allowance program exists; done when: both demos are completed or a documented reason excludes a vendor.

## Completed

- [x] Built and durably placed the public-storefront recovery checkpoint: 3,973 files, 260,428,953 bytes, 3,972 checksum entries with zero failures, byte-identical archive, SQLite integrity `ok`, and zero foreign-key errors.
- [x] Preserved 528 public pages, 1,542 normalized media assets, 524 browser-observed media variants, partial runtime assets, Journal settings, provenance, checksums, restore evidence, and a project-state snapshot.
- [x] Audited the recovered and client-supplied identities, recorded the design diagnosis, and generated three selection boards: Service Standard, Quartermaster, and One Mission.
- [x] Searched Kelly Huntington's email metadata for the sourced correspondence and verified that the seven non-secret client attachments were already preserved under `PROJECT_DATA_ROOT`; no credential values were read or copied.
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
- Data manifest: `C:\Users\dougl\.agents\tools\Test-DataManifest.ps1 -ManifestPath C:\Users\dougl\Projects\kelly-uniforms-business\data-manifest.yaml -ProjectAdapterRoot C:\Users\dougl\Projects\kelly-uniforms-business\.agents\data`
- Data adapter regression: `C:\Users\dougl\Projects\kelly-uniforms-business\.agents\data\Sync-MtUniformsData.test.ps1`
- Manual evidence: trace every `Confirmed`/`Observed` claim in `CLIENT.md` to `SOURCES.md`; confirm every supplied request appears once in `DELIVERABLES.md`; confirm active/verified/delivered items define acceptance evidence; confirm the seven data-root asset checksums match `data-manifest.yaml`; confirm the administrative account identifier and credential value remain outside tracked files; for future live-site work, capture desktop/mobile evidence and a recovery record.
- Current build status: repository is in intake and delivery-governance mode; application lint/build/browser-test commands will be added when a software deliverable becomes active.

### Business-continuity package gates

1. Every entry in `PROJECT_DATA_ROOT\backups\business-continuity\2026-08-08\SHA256SUMS.txt` exists and matches. Expected: 3,972 checked, zero failures.
2. The unpacked package contains 3,973 files and 260,428,953 bytes.
3. The archive SHA-256 is `8c20986500f4cd3d9bae193195924999a5d12931162daac4b5d8d1663714f0be`.
4. SQLite `PRAGMA integrity_check` returns `ok`, `PRAGMA foreign_key_check` returns zero rows, and row counts are 528 `public_pages`, 1,542 `media_assets`, and 524 `browser_observed_media`.
5. The copied archive matches the detached restore-verification record.
6. Do not call the package a complete business-system backup while the continuity README lists missing OpenCart, Ecwid, Clover, infrastructure, or private operational domains.

### Brand-direction gates

For concept-board changes, open all three PNGs, confirm legible text and visibly distinct directions, verify their manifest hashes, and confirm the adjacent README labels them decision aids rather than production trademarks. Before production use, require deterministic vector artwork, small-size and one-color tests, embroidery/print proofs, trademark clearance, confirmed slogan rights, and browser-visible accessibility checks.

### Browser-visible production gates

Follow `WEBSITE-UPDATE-RUNBOOK.md`. Capture desktop and mobile evidence, verify exact copy and `mailto:`/`tel:` behavior, exercise primary navigation and catalog access, and retain the rollback record. Live publication remains separately authorized but requires a signed-in or brokered session.

## Next verifier

Run the package, data-manifest, adapter, client-record, and secret-scan checks
above; then resume the highest-value missing capture through a value-safe
authenticated session. OpenCart is first because it owns the live storefront,
orders, customers, theme, and configuration.
