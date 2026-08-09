# Project instructions

This file is the portable project contract for local and cloud agents.

<!-- agent-harness:portable:v3:start -->
## Portable operating rules

Use subagents immediately for every independent, file-disjoint workstream. This is explicit authorization to parallelize. Keep only destructive or dependent final gates serial.

Agents may create local commits for in-scope work without asking. Never push, merge, force-update, discard, delete a worktree, or remove a task workspace unless the user explicitly authorizes that action.

- Answer questions before task narration. Keep routine updates concise.
- Never invent facts, paths, APIs, versions, source content, measurements, credential state, or passing results. Name the source checked.
- Verify inherited claims against repository, Git, runtime, or current primary evidence.
- Match commands and paths to the user's actual shell and device.
- Avoid the rhetorical "it is X, not Y" construction.
- Preserve unrelated changes. Inspect exact targets before destructive or broad operations and prefer recoverable changes.
- Before creating, replacing, renaming, or removing an artifact, search the repository and available shared harness for its existing owner, equivalents, consumers, wiring, tests, and documentation. Extend or consolidate the closest adequate owner. Record search evidence and the reason for a truly new owner in authoritative task state.
- Extract every discrete obligation from a multi-step prompt into authoritative task state. In an enrolled project, use Work Scope tasks or discoveries; otherwise use legacy `TASK.md` checkboxes.
- Read a named or clearly matching skill in full. Keep canonical workflows under `.agents\skills` and product adapters thin.
- Reproduce bugs before fixing them and add a regression test when practical. Exercise the assembled system under the condition that exposed the failure.
- For browser-visible changes, run the repository browser or end-to-end verifier.
- When a correction requests permanent prevention, use the `correct` skill and implement a durable, narrowly scoped artifact.
- Treat `MEMORY.md` as a lean index. Keep behavior in instructions, skills, hooks, permissions, tests, or verifiers.
- Before claiming non-trivial work complete, run the verification recorded in authoritative task state, relevant tests, and an adversarial pass.

**This project's `skills-manifest.json` is not the catalogue.** It binds the few skills this repository requires, and it is deliberately small — most of the harness is installed on the machine and bound to no project at all, so a capability being absent from that manifest says nothing about whether it exists. The catalogue is `~/.agents/INDEX.md`, generated, listing every canonical skill and command with its purpose and per-product visibility; the design material is `~/.agents/design/LIBRARIES.md` and the `design/` tree beside it, which owns animation packages, icon kits, typefaces, design systems, the registry of committed design languages, surface-construction craft, the pre-ship matrix, and the slide and poster medium. Read the index before hand-rolling a workflow, choosing a package, or concluding a capability is missing.

When `~/.agents` does not exist — a cloud container, a fresh machine, any session with no installed harness — that material is not gone; it is in the private harness repository `pyrgos-ai/doug-harness` under `.agents/`, and pulling the file you need from there is the intended route rather than a workaround. Clone or fetch it read-only, use what you need, and never vendor a copy into this repository: a second copy drifts, and the existing-system-first rule above applies to skills and design material exactly as it applies to code.
<!-- agent-harness:portable:v3:end -->

## Project identity

- Name: `kelly-uniforms-business`
- Purpose: Govern and deliver AI-native digital-product, website, and consulting work for MT Uniforms LLC from a sourced client operating record.
- Default branch: `master`
- Local data root variable: `PROJECT_DATA_ROOT`

## Start and resume

1. Read this file.
2. Read `TASK.md` and the last 5Ã¢â‚¬â€œ10 entries in `LOG.md`.
3. Read `BACKBURNER.md` for parked work.
4. Run `git status --short --branch` and `git worktree list --porcelain`.
5. Reconcile stale chat claims against files and Git before editing.
6. Run the repository state verifier when the local shared harness is available.

## Commands

- Setup: `C:\Users\dougl\.agents\tools\Ensure-AgentProject.cmd -Repository C:\Users\dougl\projects\kelly-uniforms-business`
- Test: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\dougl\projects\kelly-uniforms-business\.agents\skills\client\scripts\Test-ClientProject.ps1 -Repository C:\Users\dougl\projects\kelly-uniforms-business`
- Lint: Run the client skill validator listed in `VERIFY.md`; application linting begins when a software deliverable becomes active.
- Build: No application build is defined in the current intake phase.
- End-to-end verification: Run both project-state and client-project commands in `VERIFY.md`, then complete its manual evidence checks.

## Safety and evidence

- Never invent facts, paths, APIs, versions, or passing results.
- Preserve unrelated user changes in a dirty worktree.
- Avoid destructive commands and broad recursive targets.
- Back up authored files before replacement.
- Never read, display, log, or commit secret values.
- Use the repository-wide verifier when the changed files affect repository-wide invariants or the active task explicitly requires it. Record unrelated verifier failures separately without expanding the task.
- Record failures and remaining uncertainty plainly.

## Data boundary

- Read `data-manifest.yaml` before accessing external data.
- Keep small safe fixtures under `data\fixtures`.
- Keep disposable cache under ignored `.local`.
- Receive local application data through `PROJECT_DATA_ROOT`.
- Cloud sessions use committed fixtures or explicitly provisioned data.
- Keep runtime databases, private records, and generated outputs outside Git.
- Use plain files for documents, media, immutable inputs, portable exports, and append-only logs.
- Use SQLite for transactions, relationships, integrity constraints, indexed queries, or coordinated multi-record updates.

## Worktree boundary

- One writable task gets one branch, one worktree, and one owner.
- Detect existing isolation before creating a worktree.
- Use distinct ports, test databases, deployment targets, and mutable resources for parallel work.
- Record worktree path, branch, owner, goal, shared resources, and verifier in task state.
- Merge only after required verification passes and the source worktree has no unexplained changes.

## Task and knowledge files

- `LOG.md`: append-only work log.
- `BACKBURNER.md`: parked backlog.
- `VERIFY.md`: required proof before completion.
- `MAP.md`: architecture, data, ownership, and file navigation.
- `DESIGN.md`: current design decisions and constraints.
- `MEMORY.md`: lean index to durable reference files.

Use session-keyed active task files when concurrent sessions share one folder. Shared files remain `LOG.md` and `BACKBURNER.md`.

### Update triggers

- Start or resume: read `TASK.md` and recent `LOG.md`.
- Multi-step request: seed the queue in `TASK.md` before implementation and update it as evidence lands.
- Active goal, completed step, next command, or verifier changes: update `TASK.md`.
- Durable capability or project-state change: update `MAP.md`. `STATUS.md` is retired; do not create one.
- Meaningful completed work: append one dated line to `LOG.md`.
- Parked idea or deferred task: update `BACKBURNER.md`.
- Architecture, data flow, ownership, integration, or important path changes: update `MAP.md`.
- Product or architecture decision changes: update `DESIGN.md`.
- Verification command or required evidence changes: update `VERIFY.md`.
- Reusable fact gains a durable reference: add one linked line to `MEMORY.md`.
- Douglas corrects recurring behavior: record evidence, choose path/project/shared/platform/provider scope, implement the narrowest reliable rule or enforcement artifact, and add verification.
- Before handoff or stopping: reconcile the queue, task narrative, durable status, log, and Git state.

`TASK.md` owns the active goal, the actionable queue, blockers, completed evidence, and the exact next verifier. Keep queue entries short. `CURRENT-TASK.md` and `WORK_QUEUE.md` are retired: do not create either, and note that project setup fails while one is present.

## Secret handling

- `secret-manifest.json` is the canonical value-free inventory.
- `secret-manifest.md` is generated from it.
- `.env.example` contains names and safe placeholders.
- `.env`, credential exports, session keys, recovery keys, and real values stay outside Git.
- Inject secrets only into an approved trusted process for the shortest practical lifetime.
- Use separate development, preview, and production trust boundaries.
- Run Gitleaks before commits and in CI.
- Revoke or rotate a confirmed exposed credential before history cleanup.

## Skills

- `skills-manifest.json` declares project skill bindings.
- Project-specific portable skills live under `.agents\skills`.
- Product adapters stay thin and point to the canonical workflow.
- Add a skill only when repository evidence shows a recurring, fragile, or cloud-required workflow.

## Product adapters

- Claude loads `CLAUDE.md`, which imports this file.
- Codex loads this `AGENTS.md`.
- Cursor loads `.cursor\rules\00-project-contract.mdc`, which requires this file.

## Local shared supplement

When present, read:

- `C:\Users\dougl\.agents\HARNESS-MAP.md`
- `C:\Users\dougl\.agents\CROSS-AGENT-CONTRACT.md`
- `C:\Users\dougl\.agents\FEEDBACK-ROUTER.md` when Douglas corrects behavior or asks for a durable prevention
- `C:\Users\dougl\.agents\WORKTREE-PROTOCOL.md` for parallel or isolated work

Cloud sessions continue with this repository contract when those machine-local files are absent.
