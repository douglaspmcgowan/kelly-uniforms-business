<!-- agent-harness:universal-design:v1:start -->
## Universal interface rules

- Never use IBM Plex Mono.
- Use a proportional body face for prose, navigation, labels, dates, names, and human-readable metadata.
- Reserve monospace for code, commands, identifiers, timestamps, and genuinely tabular numeric data.
- Define explicit body, display, and monospace roles. Use tabular numerals on the proportional face for aligned quantities.
- Establish hierarchy through size, weight, spacing, and placement before decoration.
- Give each screen a clear primary action or reading path. Use spacing and alignment to show relationships.
- Reuse existing tokens and components before adding variants.
- Cover relevant default, hover, focus, active, disabled, loading, empty, error, and success states.
- Use semantic structure and native controls, visible keyboard focus, logical tab order, accessible names, sufficient contrast, and non-color state cues.
- Support narrow, medium, and wide layouts, zoom, text resizing, touch targets, and reduced motion.
- Inspect the existing design system, screenshots, and implementation before proposing a new rule or component.
- Verify browser-visible work with browser or end-to-end tests across responsive, keyboard, loading, empty, and error behavior.
<!-- agent-harness:universal-design:v1:end -->

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
