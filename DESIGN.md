# Design record

## Goals

- Keep client facts traceable to supplied or verified sources.
- Distinguish client requests, approved scope, active work, and delivered evidence.
- Preserve business continuity work ahead of larger transformation work.
- Give future local and cloud agents the same client and delivery context.

## Constraints

- The current public website has client-reported cart and connection failures.
- The live administration platform remains unverified.
- Administrative identifiers and credential values stay outside Git.
- The client’s seven supplied assets have uncertain public-web rights and several are low resolution.
- Future-site scope, budget, timeline, and acceptance criteria remain open.

## Decisions

- Use `CLIENT.md`, `DELIVERABLES.md`, and `SOURCES.md` as the client operating record.
- Assign stable source and delivery IDs so claims and work can be traced across files.
- Store source media under `PROJECT_DATA_ROOT` and keep checksums in the repository.
- Keep the temporary order-continuity notice as the top-priority client request.
- Keep diagnostics and the future website in proposed state until Douglas activates them.
- Bind the reusable project-local `client` skill for Claude, Codex, Cursor, and cloud sessions.
