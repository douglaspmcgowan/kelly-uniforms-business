<!-- agent-harness:universal-design:v1:start -->
## Universal interface rules

The authority is `~/.agents/DESIGN.md`, and it is fuller than this. What follows is
carried here rather than only linked because a cloud or container session has no
`~/.agents` to reach — so the rules that actually change what gets built have to survive
in the repository itself.

### Anti-default discipline

Quoted verbatim from the authority rather than paraphrased, because this is the section an
agent most needs and a paraphrase is a second copy that drifts.

The model's house style is recognizable, and reaching for it reads as machine-made. Never
default to: purple-blue gradients, a centered hero over a dark mesh background, three equal
feature cards, ubiquitous glassmorphism, or Inter with slate everywhere. The
beige-brass-espresso "premium consumer" palette is the same tell; rotate off it.

- Lock one accent color page-wide, and one gray family per project.
- Lock one corner-radius system per page. Mix radii only under a rule you can state.
- Keep one theme per page. Sections do not invert light and dark mid-scroll except as a single deliberate composition device.
- A section layout family appears at most once per page. At most two consecutive image-text zigzag splits. At most one small uppercase eyebrow label per three sections.
- Where a brief reads as an established design system, use that system's official package rather than approximating it. One system per project.
- The brief wins. Honor a pinned aesthetic even when it is not the choice you would make; redirecting a clear brief toward your own taste is failure, not judgment.

### Everything else

- Never use IBM Plex Mono.
- Default to a sans display face. Use serif only with an articulated reason; `Fraunces` and `Instrument Serif` are banned as defaults specifically because they are the common machine-made choice.
- Hero discipline: the hero fits the first viewport, the headline runs at most two lines, subtext stays under roughly twenty words, and no more than four text elements sit inside it. Trust marks and logo walls go below the hero, never in it.
- A grid has exactly as many cells as there is content for. Reshape the grid rather than pasting in a blank tile.
- Every animation names what it communicates — hierarchy, sequence, feedback, or state change. An animation that names nothing gets cut.
- Reread every visible string before shipping. Never invent a precise-sounding number.
- Use a proportional body face for prose, navigation, labels, dates, names, and human-readable metadata.
- Reserve monospace for code, commands, identifiers, timestamps, and genuinely tabular numeric data.
- Define explicit body, display, and monospace roles. Use tabular numerals on the proportional face for aligned quantities.
- Establish hierarchy through size, weight, spacing, and placement before decoration.
- Give each screen a clear primary action or reading path. Use spacing and alignment to show relationships.
- Reuse existing tokens and components before adding variants.
- Cover relevant default, hover, focus, active, disabled, loading, empty, error, and success states.
- Use semantic structure and native controls, visible keyboard focus, logical tab order, accessible names, sufficient contrast, and non-color state cues.
- Support narrow, medium, and wide layouts, zoom, text resizing, touch targets, and reduced motion.
- A design skill's silence on accessibility is not an exemption. Seven of the sixteen design-adjacent skill packages carry no accessibility content at all, so the two bullets above are the floor whichever skill is driving.
- A visual world is chosen, not accumulated. Template packs, style presets, and named aesthetics contradict each other by construction — `retro-windows` bans every rounded corner where `capsule` requires a 9999px radius. Commit to one, take its taste entire, and treat the others as unread. The rules here apply to all of them.
- Inspect the existing design system, screenshots, and implementation before proposing a new rule or component.
- Verify browser-visible work with browser or end-to-end tests across responsive, keyboard, loading, empty, and error behavior.

### Design libraries

Concrete things to reach for — animation packages and working skeletons, icon kits, typeface pools, design-system install commands and canonical documentation. Read the leaf you need; each one loads on its own.

- **Index** `~/.agents/design/LIBRARIES.md`
- **Motion** `~/.agents/design/animation/` — `libraries.md`, `sticky-stack.md`, `horizontal-pan.md`, `scroll-reveal.md`, `liquid-glass.md` (frosted glass), `forbidden.md`
- **Icons** `~/.agents/design/icons/libraries.md`
- **Type** `~/.agents/design/type/families.md`
- **Design systems** `~/.agents/design/systems/install.md` and `sources.md`
- **Design languages** `~/.agents/design/languages/registry.md` — read it before committing a visual world or generating a new design language, and register the world committed for this project there in the same work unit
- **Surface craft** `~/.agents/design/craft/` — `high-end.md` (surface construction), `from-reference.md` (building faithfully from a reference image), `from-code.md` (reading a design system out of a live product's own CSS), `device-mockups.md`
- **Fundamentals** `~/.agents/design/fundamentals.md` — the arithmetic under a decision: palette construction (60-30-10, one accent, warm neutrals, the colourblind-safe sets and the grayscale test), type-scale ratios with a worked scale and measure, and grid selection. Read it when the palette or scale is not already decided
- **Slides and posters** `~/.agents/design/slides-and-posters.md` — the only leaf addressing a non-web medium: deck frameworks, PowerPoint craft, HTML deck frameworks, and the academic poster including A0 sizing and the ≥24pt body floor
- **Pre-ship matrix** `~/.agents/design/preflight.md` — the mechanical finish check for landing, marketing and portfolio surfaces; not dashboards, not product UI
- **Dashboards and data-dense product UI** `~/.agents/design/dashboards.md` — the full system for the surface this tree used to leave uncovered: the three dashboard kinds and why building one while thinking of another causes most of the mistakes, information architecture and the three reading distances, density targets set against marketing spacing, typography and colour for data (sequential, diverging, categorical and semantic scales), chart selection ordered by the Cleveland-McGill perceptual ranking, chart and table craft, the six states every data region has, filters and URL state, interaction, real-time cadence, renderer choice by point count, the charting-library table, the anti-patterns, and a §18 pre-ship matrix that is the entry above's equivalent for this medium. This line used to say the tree did not own dashboards and pointed at the `/design-review` rubric, which critiques a running app rather than generating one; that gap closed on 2026-08-09

The full universal rules are `~/.agents/DESIGN.md`. Where a library entry and a rule disagree, the rule wins.

**This list is enumerated because it has to be.** A cloud or container session has no `~/.agents` to walk, so this block is the only routing it gets — which also means a leaf missing here is a leaf that session cannot reach at all. `craft/` and `preflight.md` were absent until 2026-08-07 and every project copy inherited the gap. `Test-DesignLibraryIndex.ps1` now fails the build when this list falls behind the tree.
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
- Treat vendor-native exports as immutable source evidence. Normalize only after raw capture, retain source-system IDs and artifact/run lineage, keep money in integer minor units, and preserve historical order-line snapshots rather than joining them to mutable catalog rows.
- Keep restricted recovery data outside Git under `PROJECT_DATA_ROOT\backups\business-continuity`; pair every working package with per-file checksums, an immutable archive, a detached restore record, and later encrypted offline/offsite copies.
- Classify the 2026-08-08 recovery as a verified public-storefront checkpoint and Journal-settings supplement. Do not call it a complete business-system backup until OpenCart, Ecwid, Clover, infrastructure ownership, private operational data, reconciliation, and isolated private restore are proven.
- Use the three 2026-08-08 brand boards as concept directions only. No replacement-store identity is committed yet. The published decision surface has its own committed neutral specification-wall UI documented in `brand-gallery/DESIGN.md`; that gallery frame does not select the future storefront's brand language.
- Recommend the Quartermaster direction for the ecommerce system because it serves the broadest customer base and makes products, fit, customization, and fulfillment legible. Borrow One Mission's documentary warmth and local-service storytelling; use a heraldic seal only as a secondary application if client research supports it.
- Replace the two current unrelated identities with one simple master mark and wordmark. Avoid departmental clip art, faux metal, distress, glow, and any master symbol that privileges fire, police, or EMS over the broader market.
- Superseded 2026-10-06 by the Varsity Catalogue system below: commit the first storefront prototype to the provisional Quartermaster Order Ticket visual world: deep navy, warm ivory, safety orange, Archivo, compact role/category rails, product-first imagery, and a persistent configuration/request surface. The stable surface contract is `storefront/DESIGN.md`; client approval and final identity work remain open.
- Modernize the existing workflow before adding agency allowances, authorization-code gates, portals, live inventory, or payment. The prototype therefore ends at a complete email/phone request with an explicit no-payment boundary and uses recovered public prices only as labeled snapshots.
- Both shipped surfaces follow the universal design rules through their own token sets: `storefront/DESIGN.md` (section "Tokens and formats") and `brand-gallery/DESIGN.md` (section "Compliance record"). Spacing scale 4-64, a three-size type scale, sentence case, no kickers, named easing, hairline-or-shadow elevation, and dark mode as token redefinition apply to both. Remaining exceptions are recorded in those two files.

## Design system: Varsity Catalogue

Ruled for the storefront and the brand gallery on 2026-10-06 under design-audit-20261003. Decision: **replace** the provisional Quartermaster Order Ticket world. The storefront keeps every control and behaviour; only the visual system changes.

### Direction and source

- **Character.** A uniform shop's printed catalogue: condensed headings, garment plates on plain paper grounds, and a size chart that sits beside the garment instead of behind a tab. Kelly green marks the two things a buyer does: add to the request and select.
- **Pulled from.** The catalogue spec pattern in the saved-posts reference set, through two harness references: `doug-harness/.agents/design/slides/bold-template-pack/selection-index.json` slug `stencil-tablet` (condensed metadata chrome, colour blocks as layout, plates on a bone ground) and `design-lab/data/library/stack-catalogue.json` entries `base-ui` (headless primitives, https://base-ui.com) and `phosphor` (icons, https://phosphoricons.com). Stencil & Tablet's all-caps headlines, pure black and 22–26px tablet radii are not adopted: the universal rules ban uppercase headings and pure black, and the craft floor holds card radii to 12–16px.
- **Audience check.** The direction is wrong if the storefront targets fashion buyers. It does not: it serves agencies, departments and staff buying duty uniforms. The allocation's "order sheet by school or team" reads here as **order sheet by department**.

### Colour tokens

One accent, one gray family (cool navy-gray, derived from the shipped ink). Surface levels are named; status tokens are separate from the accent. Eight literal colours per scheme; raised and border are mixes of ink into the page so they cannot drift.

| Token | Light | Dark | Use |
|---|---|---|---|
| `--surface-page` | `#f3f2ee` paper | `#111820` | page ground |
| `--surface-card` | `#fbfaf7` | `#18212b` | garment plates, configurator |
| `--surface-raised` | `color-mix(--ink 6%, --surface-page)` | same mix | rails, chart rows, hover fills |
| `--border` | `color-mix(--ink 20%, --surface-page)` | same mix | input edges, table rules only |
| `--ink` | `#0b1d34` | `#eeede8` | text, filled header |
| `--ink-muted` | `#4f5a63` | `#a9b3bc` | secondary text |
| `--accent` | `#46bc24` kelly | `#46bc24` | add-to-request fill, selection fill (ink text on it, 6.84:1) |
| `--accent-ink` | `#1f6b12` | `#6fd64c` | accent as text or 2px rule on paper (5.91:1) |
| `--status-error` | `#a52819` | `#ff8a78` | error text and icon |
| `--status-success` | `#175b31` | `#7fd39b` | confirmations |
| `--status-info` | `var(--ink)` | `var(--ink)` | snapshot notices; words and an icon carry the meaning |
| `--on-accent` | `#0b1d34` | `#0b1d34` | text on kelly fills; not redefined in dark, so it holds 6.84:1 |

Dark mode is the same tokens redefined under `prefers-color-scheme: dark`; `body` carries `background: var(--surface-page)`.

### Type

- **Faces.** Display: Archivo Narrow (`@fontsource-variable/archivo-narrow`, OFL-1.1, self-hosted through the bundle). Body: Archivo (the shipped local variable font, `storefront/public/assets/fonts/archivo-variable.woff2`). No monospace role: the surfaces render no code. Both declare `font-display: swap` with an Arial Narrow / Arial metric fallback.
- **Scale.** Ratio 1.333 (perfect fourth) from a 16px body: `--fs-small` 12px, `--fs-body` 16px, `--fs-lead` 21px, `--fs-title` clamp(24px, 2.2vw + 14px, 28px), `--fs-display` clamp(38px, 5vw + 12px, 67px). Display is Archivo Narrow 700; titles Archivo Narrow 600; body Archivo 400/600. Sentence case everywhere; tracking -0.02em on display only.
- **Numerals.** Prices, sizes and quantities use `font-variant-numeric: tabular-nums` on the proportional face.

### Spacing, radii, elevation

- **Spacing.** `--space-1` 4, `--space-2` 8, `--space-3` 12, `--space-4` 16, `--space-5` 24, `--space-6` 32, `--space-7` 48, `--space-8` 64 (px). Section padding uses `clamp(var(--space-6), 5vw, var(--space-8))`.
- **Radii.** `--radius-control` 6px (inputs, size chips, buttons), `--radius-card` 12px (plates, configurator, drawer edge), `--radius-pill` 999px (count badges only). Rule: the radius follows the object's size class.
- **Elevation.** Declared once per surface, as a shadow tinted toward navy, never with a border:
  - `--elev-1` `0 1px 2px rgb(11 29 52 / .06), 0 4px 16px rgb(11 29 52 / .06)`: a plate the pointer is on, or the selected plate.
  - `--elev-2` `0 12px 40px rgb(11 29 52 / .14)`: the request drawer and the size-chart dialog, which sit above the page.
  - Dark mode redefines both toward black at higher opacity.

### Motion

- **Easing.** `--ease-out` `cubic-bezier(0.22, 1, 0.36, 1)` (exponential out); `--ease-in` `cubic-bezier(0.55, 0, 1, 0.45)` for exits.
- **Duration.** `--dur-fast` 120ms (hover, press, focus), `--dur-base` 200ms (drawer, selection), `--dur-slow` 320ms (order count bump).
- **Inventory.** Each names what it communicates:
  - Control hover and press: colour and 1px lift on `--dur-fast`. Feedback: the control is live.
  - Size chip selection: fill to kelly on `--dur-base`. State change: this size is chosen.
  - Request drawer: slide in from the right with `transform` on 200ms `--ease-out`. Hierarchy: the request is a layer above the catalogue.
  - Request count badge: one scale pulse when an item is added. Feedback: the add landed.
  - `prefers-reduced-motion: reduce` makes all of them instant.

### Icons

Phosphor (`@phosphor-icons/react` 2.1.10), regular weight in body, bold in the header; no emoji, no Unicode glyph icons.

### Components and states

Every interactive component has default, hover, focus-visible, active and disabled; data regions also have loading, empty and error.

- **Garment plate** (product card): image on a plain `--surface-card` ground, condensed title, model and price row in tabular numerals, Configure action. Container query switches the plate from stacked to side-by-side when its own width passes 420px. Selected: `--elev-1` plus a 2px `--accent-ink` outline.
- **Size chip group** (Base UI `ToggleGroup`): single selection, keyboard arrows, selected chip filled kelly with ink text and a check icon, so state is not carried by colour alone.
- **Size chart beside the plate**: the configurator shows the size table next to the garment, never behind a tab; the size-guide dialog remains as the full reference.
- **Request drawer** (Base UI `Dialog`): focus moves in, wraps, Escape closes, focus returns to the trigger. Empty state says what belongs there and offers Browse the catalogue.
- **Order sheet by department**: the drawer lists lines as rows of garment, size, quantity and notes, the shape a department's order sheet takes.
- **Search**: label above the field, empty-result message names the query and offers Clear search.
- **Continuity notice bar**: the exact client notice with Email orders and Call now; stays first.
- **Buttons**: primary filled kelly (Add to request), secondary tonal `--surface-raised` (Draft email request, Call), tertiary text with an underline (Clear request, View source). One outlined tier: none.

### Layout grid

- **1440.** 12-column grid, 24px gutters, max content 1320px: role rail 2 columns, catalogue 6, configurator with size chart 4.
- **768.** 8 columns: role rail becomes a horizontal chip row above the catalogue; configurator moves below the catalogue full width with the size chart beside the image.
- **375.** 4 columns, 16px side gutter: single column; chips scroll horizontally inside their own row with no page scroll; the drawer fills the viewport.

### Formats

- Prices: US dollars, `$159.98`, two decimals, tabular numerals.
- Dates: `Oct 6, 2026` (month abbreviation, day, year).
- Sizes: the garment maker's own labels (X-Large, 32 x 30); quantities as plain integers.

### Recorded exceptions

- The `<meta name="theme-color">` carries a literal hex because the attribute cannot take a custom property.
- The brand gallery keeps one dark band ("What each route prioritizes") as its single deliberate composition device.

### Recommendations

- **In this build:** Archivo Narrow display face with Archivo body; the kelly accent and the token set above; garment plates with a container query; size chart beside the garment in the configurator; Base UI `ToggleGroup` for size choice and `Dialog` for the request drawer; request lines laid out as an order sheet by department; the request-count pulse and drawer motion above; brand-gallery directions recut as swatch cards carrying colour code, fabric and care line where the record supplies them.
- **Proposed for later:** a department order sheet with one row per staff member (name, size, quantity), once the client confirms agencies order that way; a printable catalogue view (`@media print`) of the plate grid; fabric and care fields in `src/data.ts` once the client supplies verified garment specs; a measured fit finder that recommends a size from chest and waist, after real size charts are on file; the client's final mark replacing the provisional M/T monogram.
