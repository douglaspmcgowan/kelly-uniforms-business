# Project map

## State

- The repository is a business-continuity, client-delivery, and storefront-modernization system. The production commerce platform remains unselected.
- **Storefront, as of 2026-08-14.** `theme` holds a real Shopify Liquid theme whose commerce calls all route through `theme/assets/commerce-adapter.js`, which selects a Shopify, Ecwid, or local driver at runtime; switching platform is one theme setting rather than a rebuild. `preview` renders those same theme files to static HTML with liquidjs and is what is deployed, so the prototype and the Shopify theme cannot drift apart. The earlier fixture-backed React prototype under `storefront` is superseded by this and is no longer the deployed artifact.
- **Catalog, as of 2026-08-14.** The full public catalog was extracted from mtuniforms.com — 321 live products, 0 errors, with option groups, categories, prices, images, and descriptions. The authenticated admin holds 407 products, so 86 are switched off. Public catalog facts live in `preview/data/catalog.json` (committed); the raw export lives under `PROJECT_DATA_ROOT`. Inventory counts, orders, and customer records were not extracted and are recorded as absent rather than as zero.
- **Operations, as of 2026-08-14.** `ops` holds a SQLite schema for catalog, agencies, customers, orders, order-line options, decoration jobs, and stock movements, with a local-only console at `ops/admin.mjs`. Per `INTENT.md`, per-officer allowances, agency portals, and authorization codes are deliberately absent from the schema pending client confirmation.
- The requested ordering notice is present in the recovered public homepage and in the replacement prototype. OpenCart and Ecwid authenticated exports still require the value-safe broker documented in `ACCESS.md`; Clover is the retained POS and its login/export is outside the current recovery scope.
- The broker, Playwright login flows, and Bitwarden allowlist structure are built and tested. They remain blocked on the Douglas-owned secret setup and non-secret resource IDs recorded in `TASK.md`.
- Work Scope closed `storefront-modernization/customer-storefront@D3` after the client-first prototype passed its recorded verifier and production browser check. `business-continuity/recovery-package-maintenance@D2` owns the REC-016 consistency successor; the separate `business-continuity/rebuild-ready-recovery@D5` capability remains blocked on authenticated OpenCart and Ecwid sources.
- REC-016 is the current verified recovery checkpoint: 528 reachable public pages, 1,542 of 1,542 exact referenced media assets with reconciled 100% coverage, 34 of 35 runtime references with the retired AddThis disposition, a present value-free ten-service account inventory, and zero private commerce/import rows. Its cache-free package and package-only isolated restore drill passed, and REC-015 remained byte-for-byte unchanged. Authenticated OpenCart/Ecwid bytes, primary account-control evidence, and encrypted redundant custody remain incomplete. Clover authentication is excluded by `DEC-005`.
- The v2 `data-manifest.yaml` and project-local adapter own thirteen portable assets and recovery outputs. The adapter uses SHA-256 comparison, rejects traversal/reparse paths, refuses divergent overwrites, and will not publish `private/` assets offsite until an encrypted artifact exists.
- Three brand directions are published for client selection at <https://mt-uniforms-brand-directions.vercel.app/>. The storefront prototype implements a provisional Quartermaster Order Ticket direction, borrowing Direction 3's documentary warmth; it does not imply client approval of a final identity.
- Platform position: stabilize ordering first and choose the replacement separately. Agency allowance research is deferred; written Shopify catalog confirmation remains an open execution item.
- `.agents/work/state.json` is authoritative Work Scope state. The lossless 2026-08-09 enrollment imported 51 legacy task records and preserves exact pre-migration `TASK.md`, `BACKBURNER.md`, and `LOG.md` snapshots under `.agents/work/imports` and the external project-state backup; `TASK.md`, `BACKBURNER.md`, `LOG.md`, `PROJECT.md`, and `TRACKS.md` are generated views.

## Core documents

| File | Audience | Loaded or read when | Owns |
|---|---|---|---|
| `AGENTS.md` | Agents and humans | Every repository session | Portable project contract |
| `CLAUDE.md` | Claude adapter | Every Claude repository session | Imports `AGENTS.md` |
| `.cursor/rules/00-project-contract.mdc` | Cursor adapter | Every Cursor repository session | Requires `AGENTS.md` |
| `.agents/work/state.json` | Agents and guarded tools | Start, resume, handoff | Authoritative active cell, queue, blockers, ownership, evidence, and frontier |
| `.agents/work/events.jsonl` | Agents and guarded tools | Audit and reconciliation | Hash-chained Work Scope event history |
| `TASK.md`, `BACKBURNER.md`, `LOG.md`, `PROJECT.md`, `TRACKS.md` | Humans and agents | Read-only orientation | Generated views of authoritative Work Scope state and events |
| `.agents/work/imports` | Agents and auditors | Migration provenance | Immutable SHA-256-named legacy task, backlog, and log snapshots |
| `MAP.md` | Agents and humans | Orientation | This document graph and project navigation |
| `DESIGN.md` | Agents and humans | Feature and architecture work | Goals, constraints, decisions |
| `MEMORY.md` | Agents | Recall | Lean links to durable topic notes |
| `data-manifest.yaml` | Agents and applications | Data access | Value-free data locations and classifications |
| `secret-manifest.json` | Agents and automation | Credential-dependent setup | Value-free credential inventory |
| `skills-manifest.json` | Agents and cloud setup | Skill selection and export | Project skill bindings |
| `CLIENT.md` | Douglas and delivery agents | Every client task | Sourced client identity, business, systems, brand, constraints, and open questions |
| `DELIVERABLES.md` | Douglas and delivery agents | Planning and execution | Scope state, dependencies, acceptance evidence, and next actions |
| `SOURCES.md` | Agents and reviewers | Intake, refresh, and verification | Message, web, file, asset, and decision provenance |
| `SETUP.md` | Douglas | Start of any run that needs money, an account, or a ruling | Approvals, purchases, manual steps, open questions, and the next goal command |
| `ACCESS.md` | Douglas and delivery agents | Credential-dependent work | Login inventory and the value-safe access routes |

## Architecture

| Component | Purpose | Entry point | Owner |
|---|---|---|---|
| Client operating record | Keep facts, requests, sources, and delivery state aligned | `CLIENT.md`, `DELIVERABLES.md`, `SOURCES.md` | Douglas |
| Portable storefront theme | One theme that runs on Shopify, Ecwid, or neither | `theme/layout/theme.liquid`, `theme/assets/commerce-adapter.js` | Delivery agents |
| Static theme renderer | Render the same theme files for the client-facing prototype | `preview/build.mjs` | Delivery agents |
| Catalog extraction | Turn the public storefront into structured product data | `preview/make-catalog.mjs` | Delivery agents |
| Operations database | Model orders, decoration work, agencies, and stock | `ops/schema.sql`, `ops/build-db.mjs`, `ops/verify-db.mjs` | Delivery agents |
| Operations console | Local-only screen for orders, decoration queue, catalog, reorder | `ops/admin.mjs` | Douglas |
| Client skill | Initialize and refresh governed client repositories | `.agents\skills\client\SKILL.md` | Douglas |
| Project harness | Provide portable instructions, task state, manifests, adapters, and verification | `AGENTS.md` | Shared agent harness |
| Client source assets | Preserve supplied media outside Git with checksums | `%PROJECT_DATA_ROOT%\inputs\client-provided\2026-07-26` | Douglas + client |
| Website update runbook | Provide the reversible Journal 3 path for the temporary ordering notice | `WEBSITE-UPDATE-RUNBOOK.md` | Douglas + client site owner |
| Business-continuity recovery | Preserve immutable raw artifacts, a queryable portable recovery database, checksums, archive, self-contained verifier, and restore evidence outside Git | Current: `%PROJECT_DATA_ROOT%\backups\business-continuity\2026-08-12-rec016`; archive under `%PROJECT_DATA_ROOT%\backups\business-continuity\archives`; isolated restores under `%PROJECT_DATA_ROOT%\backups\business-continuity\isolated-restores` | Douglas + recovery operator |
| Commerce import contract | Reject incomplete, unsafe, contradictory or unreconciled OpenCart/Ecwid captures before normalized ingestion | `docs\recovery\opencart-ecwid-import-reconcile-contract.md`; `schemas\commerce-import-bundle-v1.schema.json`; `scripts\validate_import_bundle.py` | Recovery operator |
| Commerce bundle importer | Add source-fidelity structures and transactionally write allowlisted normalized rows with exact lineage, reconciliation, idempotency and rollback | `docs\recovery\commerce-normalization-payload-v1.md`; `scripts\extend_import_schema.py`; `scripts\import_commerce_bundle.py` | Recovery operator |
| Import-ready recovery packager | Preserve REC-007, package every importer dependency, atomically stage authenticated raw bundles, refresh package checksums, and verify REC-008 from an isolated extraction | `scripts\package_import_ready_generation.py`; `scripts\test_package_import_ready_generation.py`; `evidence\2026-08-10-rec008-import-ready-package.md` | Recovery operator |
| External-data adapter | Publish, restore, and compare immutable project data without overwriting divergent generations | `.agents\data\Sync-MtUniformsData.ps1`, `data-manifest.yaml` | Project agents |
| Brand-direction handoff | Preserve generated selection boards and the sourced recommendation outside Git | `%PROJECT_DATA_ROOT%\outputs\brand-directions\2026-08-08\README.md` | Douglas + client approver |
| Brand-direction gallery | Present the three directions and public project status as a stakeholder decision surface | `brand-gallery\index.html`; production at <https://mt-uniforms-brand-directions.vercel.app/> | Douglas + client approver |
| Storefront prototype | Demonstrate role/category/search discovery, recovered public products, fit-aware configuration, and an email/phone request fallback without processing payment | `storefront\src\App.tsx`; behavior in `SPEC.md`; visual contract in `storefront\DESIGN.md` | Douglas + storefront implementer |

## Important paths

| Path | Purpose | Generated | Committed |
|---|---|---|---|
| `C:\Users\dougl\projects\kelly-uniforms-business` | Stable client repository | No | Recovery system and storefront are under Git custody; external recovery bytes remain under `PROJECT_DATA_ROOT` |
| `C:\Users\dougl\Data\Projects\kelly-uniforms-business` | Stable client inputs and outputs | No | No |
| `%PROJECT_DATA_ROOT%\backups\business-continuity\2026-08-08` | Preserved REC-001 recovery generation | Yes | No |
| `%PROJECT_DATA_ROOT%\backups\business-continuity\2026-08-09` | Preserved REC-002 portable recovery generation, SQLite database, and packaged verifier | Yes | No |
| `%PROJECT_DATA_ROOT%\backups\business-continuity\2026-08-09-rec003` | Current REC-003 generation with public business, DNS, RDAP, TLS, HTTP, and provenance records | Yes | No |
| `%PROJECT_DATA_ROOT%\backups\business-continuity\2026-08-10-rec004` | Current REC-004 generation preserving REC-003 and adding directly captured public JavaScript/font binaries with runtime provenance | Yes | No |
| `%PROJECT_DATA_ROOT%\backups\business-continuity\2026-08-10-rec005` | Current REC-005 generation preserving REC-004 and adding the source-constrained normalized commerce schema | Yes | No |
| `%PROJECT_DATA_ROOT%\backups\business-continuity\2026-08-10-rec006` | Current REC-006 generation preserving REC-005 and capturing all 430 previously unresolved public image URLs | Yes | No |
| `%PROJECT_DATA_ROOT%\backups\business-continuity\2026-08-10-rec007` | Immutable parent generation with complete public media and retired AddThis disposition | Yes | No |
| `%PROJECT_DATA_ROOT%\backups\business-continuity\2026-08-10-rec008` | Current import-ready generation with packaged validation, staging, normalization, and restore tooling | Yes | No |
| `%PROJECT_DATA_ROOT%\backups\business-continuity\2026-08-10-rec015` | Preserved cache-free REC-016 parent authority | Yes | No |
| `%PROJECT_DATA_ROOT%\backups\business-continuity\2026-08-12-rec016` | Current manifest-consistent operational recovery authority; 1,542 exact media, zero private rows, archive, and package-only isolated restore proven | Yes | No |
| `%PROJECT_DATA_ROOT%\backups\project-state\2026-08-09\pre-work-scope` | Exact pre-enrollment task, backlog, and log backup with hash manifest | Yes | No |
| `%PROJECT_DATA_ROOT%\backups\business-continuity\archives` | Immutable archive, checksum sidecar, and detached restore record | Yes | No |
| `%PROJECT_DATA_ROOT%\outputs\brand-directions\2026-08-08` | Three visual direction boards and selection rationale | Yes | No |
| `brand-gallery` | Static, tested Vercel gallery with copied public boards and a scoped `DESIGN.md` | No | Yes |
| `storefront` | Vite/React storefront prototype, exact public fixture media, request-flow verifier, and responsive screenshots | No | Yes |
| `VERIFY.md` | Current repository verification owner | No | Yes |
| `.agents\skills\client` | Project-bound reusable intake skill | No | Yes |
| `.validator-deps` | Disposable PyYAML dependency for the official skill validator | Yes | No |

## Data flow

Client messages, public pages, and supplied assets enter the source ledger first. Supported facts flow into `CLIENT.md`; work requests flow into `DELIVERABLES.md`; durable source media is copied to the declared project data root. Recovery exports follow a raw-first path: immutable vendor-native files and hashes are captured under the restricted data root, then normalized into SQLite with source-system IDs and lineage, then reconciled and restore-tested. The prototype consumes seven explicitly provenance-tracked public fixtures and treats prices and availability as snapshots pending authenticated migration. Generated brand concepts live under `outputs` and remain decision aids until client selection and deterministic redraw. Authenticated administration crosses into the client-production trust boundary only through an existing signed-in session or the approved value-safe credential broker.

## Integrations

| System | Direction | Authentication name | Failure behavior |
|---|---|---|---|
| MT Uniforms OpenCart / Journal 3 website | Inbound observation; outbound changes require separate authority | `MT_UNIFORMS_WEBSITE_ADMIN_USERNAME` and `MT_UNIFORMS_WEBSITE_ADMIN_PASSWORD` in Bitwarden Secrets Manager | Use the standard OpenCart admin route and the `WEBSITE-UPDATE-RUNBOOK.md`; preserve current state and use the Header Notice rollback |
| Ecwid control panel | Both during separately authorized administration | `MT_UNIFORMS_ECWID_ADMIN_USERNAME` and `MT_UNIFORMS_ECWID_ADMIN_PASSWORD` in Bitwarden Secrets Manager | Treat as a secondary or legacy system until its operational role is confirmed; keep credential values outside repository files, logs, and chat |
| Clover POS | Retained external in-store POS; authenticated export is outside current recovery scope | Client-supplied non-secret documents or a separately authorized future export | Preserve documented integration requirements and any later-supplied Clover IDs/mappings; do not store PAN/CVV data |
| Project data root | Both | `PROJECT_DATA_ROOT` | Stop asset moves when the stable root is unavailable; preserve original source paths |

## Ownership and concurrency

Douglas owns repository and delivery decisions. Client representatives own production website approval and account access. The production website is a shared mutable resource. Each live change requires one owner, a reversible edit path, and browser verification. Recovery raw exports are append-only and restricted; one operator owns each extraction run. Work Scope is enrolled and location-bound; all state changes go through the guarded tools, with generated root views treated as read-only.

## Update rule

Update this file whenever a core document, component boundary, data flow, owner, integration, or important path changes.
