<!-- agent-harness:portable:v4:start -->
## Portable operating rules

Use subagents immediately for every independent, file-disjoint workstream. This is explicit authorization to parallelize. Keep only destructive or dependent final gates serial.

Agents may create local commits for in-scope work without asking. Never push, merge, force-update, discard, delete a worktree, or remove a task workspace unless the user explicitly authorizes that action.

- Answer questions before task narration. Keep routine updates concise.
- Write durable briefs lean and self-contained: lead with the outcome, include the context needed to understand it, and link deeper evidence. When Docket is configured, `.agents/DOCKET-PROTOCOL.md` → **Brief quality** is the detailed owner.
- Never invent facts, paths, APIs, versions, source content, measurements, credential state, or passing results. Name the source checked.
- Verify inherited claims against repository, Git, runtime, or current primary evidence.
- Match commands and paths to the user's actual shell and device.
- Avoid the rhetorical "it is X, not Y" construction.
- Preserve unrelated changes. Inspect exact targets before destructive or broad operations and prefer recoverable changes.
- Before creating, replacing, renaming, or removing an artifact, search the repository and available shared harness for its existing owner, equivalents, consumers, wiring, tests, and documentation. Extend or consolidate the closest adequate owner. Record search evidence and the reason for a truly new owner in authoritative task state.
- Extract every discrete obligation from a multi-step prompt into authoritative task state. In an enrolled project, use Work Scope tasks or discoveries; otherwise use legacy `TASK.md` checkboxes.
- Read a named or clearly matching skill in full. Keep canonical workflows under `.agents\skills` and product adapters thin.
- Reproduce bugs before fixing them and add a regression test when practical. Exercise the assembled system under the condition that exposed the failure.
- **Use one build loop.** Classify the prompt into task state and project intent. Product or feature work starts from a current specification, creating or refreshing it before implementation when needed; personal systems and one-off work may proceed from project intent plus observable task acceptance. Materialize the tasks, execute test-first, verify, and update affected documentation in the same work unit. Then re-read the resulting project state against the original intent; when they diverge, re-enter the loop at the earliest stale stage.
- **Project folder and data model.** Use one resolved projects root per environment (`%USERPROFILE%\Projects` on this host, or `AGENT_PROJECTS_ROOT`) and keep one stable checkout per remote there. A writable task uses a linked or product-managed worktree as its temporary stream. Search remotes before cloning; when duplicate checkouts exist, identify their cause and file the reconciliation with the owning project rather than merging or removing either copy opportunistically. Project runtime data never lives in the vault: repositories own source and safe configuration, declared data roots own external/runtime data, and vault notes link to those owners while retaining authored knowledge.
- For browser-visible changes, run the repository browser or end-to-end verifier.
- When a correction requests permanent prevention, use the `correct` skill and implement a durable, narrowly scoped artifact.
- Treat `MEMORY.md` as a lean index. Keep behavior in instructions, skills, hooks, permissions, tests, or verifiers.
- Before claiming non-trivial work complete, run the verification recorded in authoritative task state, relevant tests, and an adversarial pass.

**This project's `skills-manifest.json` is not the catalogue.** It binds the few skills this repository requires, and it is deliberately small — most of the harness is installed on the machine and bound to no project at all, so a capability being absent from that manifest says nothing about whether it exists. The catalogue is `~/.agents/INDEX.md`, generated, listing every canonical skill and command with its purpose and per-product visibility; the design material is `~/.agents/design/LIBRARIES.md` and the `design/` tree beside it, which owns animation packages, icon kits, typefaces, design systems, the registry of committed design languages, surface-construction craft, the pre-ship matrix, and the slide and poster medium. Read the index before hand-rolling a workflow, choosing a package, or concluding a capability is missing.

When `~/.agents` does not exist — a cloud container, a fresh machine, any session with no installed harness — that material is not gone; it is in the private harness repository `pyrgos-ai/doug-harness` under `.agents/`, and pulling the file you need from there is the intended route rather than a workaround. Clone or fetch it read-only, use what you need, and never vendor a copy into this repository: a second copy drifts, and the existing-system-first rule above applies to skills and design material exactly as it applies to code.

**Read what other projects' agents filed against this one, at the start, before deciding what to work on.** An agent that finds something wrong here while working somewhere else records it and does not fix it — that is the standing rule, and the record lands in one of two places depending on this project's mode. When `.agents/work/state.json` exists, filed items are ordinary discoveries in the Work Scope queue and `Get-WorkResume.ps1` surfaces them like any other. Otherwise they are in the `agent-harness:intake:v1` managed block in this project's `BACKBURNER.md`, and **nothing surfaces that block automatically**, so reading it is yours to do. Triage what is there, promote what you take into `TASK.md`, and delete nothing to make a count look smaller; an item you reject stays with the reason.

To file one **against another project**, from wherever you are, use the one command that works in both modes rather than editing that project's files by hand:

```
pwsh -File ~/.agents/tools/Add-ProjectIntake.ps1 -Project <name-or-path> -Id <slug> \
  -Title "<what is wrong, in one line>" -From "<the project and task you were doing>" \
  -Relationship <adjacent|prerequisite|follow-up|defect|opportunity> \
  -Value <low|medium|high> -Risk <low|medium|high> \
  -Evidence "verifier=inspection; subject=<what you saw>; result=verified; reference=<path>"
```

Add `-List` to read a project's intake instead of writing to it. A bare project name resolves under the projects root, which is what the folder-name-equals-repo-name convention buys; set `AGENT_PROJECTS_ROOT` where that root differs, as it does in a container.

## Start and resume

1. Read this file, `TASK.md`, and recent `LOG.md`.
2. Run `git status --short --branch` and inspect worktrees before editing.
3. Read `MAP.md` for architecture, data, ownership, integrations, or important paths.
4. Read `DESIGN.md` for interface work and `PRODUCT.md` when present.

## Task-state authority

If the exact project path `.agents/work/state.json` exists, Work Scope is enrolled and that structured file is authoritative. Load and follow the `work-scope` skill, including its scope-guard, ownership, evidence, and handoff rules. Resolve tools from the package containing the loaded skill, then run `Test-WorkState.ps1`, `Get-WorkResume.ps1`, and `Reconcile-WorkState.ps1` with `-Root <project-root>` before changing task state. Treat `PROJECT.md`, `TRACKS.md`, `TASK.md`, `BACKBURNER.md`, and `LOG.md` as generated, read-only views. Route active-cell changes through `Update-WorkState.ps1`, executed checks through `Invoke-WorkScopeEvidence.ps1`, and pre-write ownership checks through `Test-WorkScopeGuard.ps1`. Route adjacent or deferred work through `Capture-WorkDiscovery.ps1`; use `New-WorkHandoff.ps1` for independent outcomes. A present but invalid state file fails closed and never falls back to legacy task files.

When `.agents/work/state.json` is absent, the legacy `TASK.md`, `BACKBURNER.md`, and `LOG.md` files retain their documented ownership. In either mode, durable capability state belongs in `MAP.md`, not in a task file. `STATUS.md` is retired; do not create one.

## Project files

- `TASK.md`: generated Work Scope view when enrolled; otherwise the legacy current goal, actionable queue, blockers, completed evidence, and next verifier.
- `LOG.md`: generated Work Scope view when enrolled; otherwise the legacy append-only completed-work record.
- `BACKBURNER.md`: generated Work Scope discovery view when enrolled; otherwise legacy parked ideas.
- `MAP.md`: architecture, paths, data flow, integrations, and ownership.
- `DESIGN.md`: universal interface rules plus project-specific design rules.
- `PRODUCT.md`: optional product intent for an app or product repository.
- `MEMORY.md`: lean links to durable references.
- `skills-manifest.json`: canonical baseline and project skill bindings.
- `data-manifest.yaml`: external-data authorities, adapters, restore rules, and verifiers.
- `secret-manifest.json`: value-free secret names, providers, trust boundaries, and consumers.
- `.gitignore`: carries a managed `agent-harness:project-gitignore:v1` block covering the task hooks' own runtime state. Put project-owned rules outside the markers; anything inside them is regenerated.
- `.gitattributes`: carries a managed `agent-harness:project-gitattributes:v1` block exempting vendored third-party skills from whitespace linting, since their bytes are referenced and never edited. Project-owned attributes go outside the markers.

## What is managed here, and what is yours

Everything above the closing marker is generated from the shared harness and is replaced on every project sync. Edit it in `.agents/templates/AGENTS.md` in the harness repository, not here. Everything below the marker is this project's own and is never rewritten -- put project identity, real commands, and repository-specific rules there.

The block covered only the portable operating rules until 2026-08-09. The startup procedure, the task-state authority and the project-files list sat outside it, so a correction to any of the three had to be re-applied by hand in every project and drifted the moment one was missed. Douglas ruled (`ahp-project-block-scope`) to widen it to cover all three.
<!-- agent-harness:portable:v4:end -->

# Project instructions

This file is the portable project contract for local and cloud agents.

<!-- agent-harness:portable-principles:v2:start -->
## Portable operating principles

These standing rules travel with the repository so local, cloud, and background agents receive the same core judgment.

### Communication and truth

- Address the user as Douglas.
- Answer direct and embedded questions before task narration. Repeat every unresolved question at the end of the turn.
- Never invent facts, paths, APIs, versions, source content, measurements, or passing results. Name the authoritative source checked.
- Verify claims inherited from chats, summaries, comments, or memory against repository evidence.
- For current or version-sensitive facts, consult current primary sources. Use practitioner evidence alongside primary sources for subjective workflow judgments.
- Match commands and paths to the shell and environment Douglas will actually use.
- Avoid the rhetorical â€œit is X, not Yâ€ construction in prose.
- Before drafting publishable prose, use the project voice guide when one exists.

### Safety, scope, and autonomy

- Preserve unrelated changes and keep edits surgically scoped to the requested outcome.
- Inspect exact targets before destructive or broad filesystem operations. Prefer reversible changes and backups.
- Never read, display, log, or commit credential values.
- Back up authored documents before replacement and check for unsaved/open application state before transforming them.
- Proceed through safe, in-scope implementation steps. Stop for missing authority, ambiguous irreversible changes, contradictory requirements, or credentials that require Douglas.
- Treat a request for a plan as plan-only work until Douglas gives an implementation instruction.

### Engineering judgment

- State key assumptions, surface materially different interpretations, and choose the simplest sufficient design.
- Convert work into verifiable goals. Reproduce bugs before fixing them and add a regression test when practical.
- Exercise the assembled system under the condition that exposed the bug; isolated mocks and unit tests are supporting evidence.
- Reproduce a claimed root cause before writing it to durable memory. Preserve unresolved causes as hypotheses.
- Use comments for non-obvious rationale and public interfaces; remove comments that merely restate code.
- Use code-graph or symbol navigation when available before loading large files.
- Keep bulk research and large file content out of the main conversation when targeted reads or isolated analysis can answer the question.
- Use matching repository skills when their trigger applies. Keep task workflows in skills and standing cross-tool invariants in this file.
- Delegate only independent work with one writer per file or isolated worktree.
- For browser-visible changes, run the repositoryâ€™s browser/end-to-end verifier.

### Completion and durable learning

- Run `VERIFY.md`, relevant tests, and an adversarial pass before claiming non-trivial work is complete.
- A recurring-error fix requires a durable artifact that reaches future sessions: one or more rules, skills, memories, verifiers, hooks, permissions, tests, briefs, or backlog records.
- Route corrections by evidence and scope. Use the narrowest proven scope and several enforcement mechanisms when they address different failure modes.
- Append value-free correction records to `.agents/feedback/FEEDBACK-LOG.md`; preserve history through superseding entries.
- Record failures, blockers, remaining uncertainty, created/updated file paths, and open questions plainly.
<!-- agent-harness:portable-principles:v2:end -->

## Project identity

- Name: `kelly-uniforms-business`
- Purpose: Govern and deliver AI-native digital-product, website, and consulting work for MT Uniforms LLC from a sourced client operating record.
- Default branch: `master`
- Local data root variable: `PROJECT_DATA_ROOT`

## Commands

- Setup: `C:\Users\dougl\.agents\tools\Ensure-AgentProject.cmd -Repository C:\Users\dougl\projects\kelly-uniforms-business`
- Test: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\dougl\projects\kelly-uniforms-business\.agents\skills\client\scripts\Test-ClientProject.ps1 -Repository C:\Users\dougl\projects\kelly-uniforms-business`
- Lint: Run the project-bound client validator when present; application linting is owned by each active software deliverable.
- Build: No application build is defined in the current intake phase.
- End-to-end verification: run `scripts/Test-PortableRecoveryRepository.ps1`; active Work Scope checks remain the authoritative acceptance gates.

## Safety and evidence

- Never invent facts, paths, APIs, versions, or passing results.
- Preserve unrelated user changes in a dirty worktree.
- Avoid destructive commands and broad recursive targets.
- Back up authored files before replacement.
- Never read, display, log, or commit secret values.
- Run the repository verifier before a completion claim.
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

## Project task and verification routing

- `.agents/work/state.json` is authoritative task state; `TASK.md`, `BACKBURNER.md`, `LOG.md`, `PROJECT.md`, and `TRACKS.md` are generated views.
- `MAP.md` owns durable architecture, paths, integrations, and capability state.
- `DESIGN.md` owns project design decisions and constraints.
- `MEMORY.md` is a lean index to durable references.
- `scripts/Test-PortableRecoveryRepository.ps1` is the repository-wide verification entry point.
- `.agents/archive/task-state-migration/` preserves the retired root task and verification files byte-for-byte; never restore them as active root files.

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
