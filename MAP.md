# Project map

## Core documents

| File | Audience | Loaded or read when | Owns |
|---|---|---|---|
| `AGENTS.md` | Agents and humans | Every repository session | Portable project contract |
| `CLAUDE.md` | Claude adapter | Every Claude repository session | Imports `AGENTS.md` |
| `.cursor/rules/00-project-contract.mdc` | Cursor adapter | Every Cursor repository session | Requires `AGENTS.md` |
| `CURRENT-TASK.md` | Agents and humans | Start, resume, handoff | Active goal, progress, exact next verifier |
| `WORK_QUEUE.md` | Agents and harness | Multi-step work | Actionable checkbox state |
| `STATUS.md` | Agents and humans | Start, resume, milestone | Durable project state |
| `LOG.md` | Agents and humans | Recent history, handoff | Append-only work record |
| `BACKBURNER.md` | Humans and agents | Planning | Parked backlog |
| `VERIFY.md` | Agents and CI | Before completion | Required evidence and commands |
| `MAP.md` | Agents and humans | Orientation | This document graph and project navigation |
| `DESIGN.md` | Agents and humans | Feature and architecture work | Goals, constraints, decisions |
| `MEMORY.md` | Agents | Recall | Lean links to durable topic notes |
| `data-manifest.yaml` | Agents and applications | Data access | Value-free data locations and classifications |
| `secret-manifest.json` | Agents and automation | Credential-dependent setup | Value-free credential inventory |
| `skills-manifest.json` | Agents and cloud setup | Skill selection and export | Project skill bindings |
| `CLIENT.md` | Douglas and delivery agents | Every client task | Sourced client identity, business, systems, brand, constraints, and open questions |
| `DELIVERABLES.md` | Douglas and delivery agents | Planning and execution | Scope state, dependencies, acceptance evidence, and next actions |
| `SOURCES.md` | Agents and reviewers | Intake, refresh, and verification | Message, web, file, asset, and decision provenance |

## Architecture

| Component | Purpose | Entry point | Owner |
|---|---|---|---|
| Client operating record | Keep facts, requests, sources, and delivery state aligned | `CLIENT.md`, `DELIVERABLES.md`, `SOURCES.md` | Douglas |
| Client skill | Initialize and refresh governed client repositories | `.agents\skills\client\SKILL.md` | Douglas |
| Project harness | Provide portable instructions, task state, manifests, adapters, and verification | `AGENTS.md` | Shared agent harness |
| Client source assets | Preserve supplied media outside Git with checksums | `%PROJECT_DATA_ROOT%\inputs\client-provided\2026-07-26` | Douglas + client |
| Website update runbook | Provide the reversible Journal 3 path for the temporary ordering notice | `WEBSITE-UPDATE-RUNBOOK.md` | Douglas + client site owner |

## Important paths

| Path | Purpose | Generated | Committed |
|---|---|---|---|
| `C:\Users\dougl\projects\kelly-uniforms-business` | Stable client repository | No | Repository content is uncommitted pending Douglas’s direction |
| `C:\Users\dougl\Data\Projects\kelly-uniforms-business` | Stable client inputs and outputs | No | No |
| `.agents\skills\client` | Project-bound reusable intake skill | No | Pending commit |
| `.validator-deps` | Disposable PyYAML dependency for the official skill validator | Yes | No |

## Data flow

Client messages, public pages, and supplied assets enter the source ledger first. Supported facts flow into `CLIENT.md`; work requests flow into `DELIVERABLES.md`; durable source media is copied to the declared project data root. Authenticated administration crosses into the client-production trust boundary only during a separately authorized live deliverable.

## Integrations

| System | Direction | Authentication name | Failure behavior |
|---|---|---|---|
| MT Uniforms OpenCart / Journal 3 website | Inbound observation; outbound changes require separate authority | `MT_UNIFORMS_WEBSITE_ADMIN_USERNAME` and `MT_UNIFORMS_WEBSITE_ADMIN_PASSWORD` in Bitwarden Secrets Manager | Use the standard OpenCart admin route and the `WEBSITE-UPDATE-RUNBOOK.md`; preserve current state and use the Header Notice rollback |
| Ecwid control panel | Both during separately authorized administration | `MT_UNIFORMS_ECWID_ADMIN_USERNAME` and `MT_UNIFORMS_ECWID_ADMIN_PASSWORD` in Bitwarden Secrets Manager | Treat as a secondary or legacy system until its operational role is confirmed; keep credential values outside repository files, logs, and chat |
| Project data root | Both | `PROJECT_DATA_ROOT` | Stop asset moves when the stable root is unavailable; preserve original source paths |

## Ownership and concurrency

Douglas owns repository and delivery decisions. Client representatives own production website approval and account access. The production website is a shared mutable resource. Each live change requires one owner, a reversible edit path, and browser verification. No application port, test database, or deployment target exists yet.

## Update rule

Update this file whenever a core document, component boundary, data flow, owner, integration, or important path changes.
