# M.T. Uniforms storefront design

## Surface contract

- **Visual world:** Varsity Catalogue, recorded in the root `DESIGN.md` section "Design system: Varsity Catalogue" (it supersedes the provisional Quartermaster Order Ticket; surface seed `734cebaa` is kept as an identifier). The experience reads as one practical supply-counter ticket: choose a role, find a public fixture, resolve fit, and prepare a human request.
- **Status:** Provisional prototype direction. The M.T. Uniforms wordmark treatment and CSS M/T monogram are exploratory; this document does not record client approval, a final identity, or trademark clearance.
- **Continuity bar:** The first action band carries the exact notice, `New Website Coming! For all orders email orders@mtuniforms.com or call us directly at (814) 536-2390.`, with real email and phone links.
- **Visual language:** the root system record owns every colour, type, spacing, radius, elevation and motion value: ink `#0b1d34` on paper `#f3f2ee`, kelly `#46bc24` as the add-to-request and selection fill with ink text, Archivo Narrow display over Archivo body, Phosphor icons. No gradients, glass, hard shadows, or faux-metal treatment. This file records only how the storefront applies it.

## Layout and components

- A sticky ink header holds the provisional M.T. Uniforms mark, search, Shop/Help/Contact anchors, and request-list count. The intro leads with “Find the right uniform. Get the fit right.” and a public-snapshot confirmation note.
- The workbench is three coordinated regions: a role rail, category shelf/catalog, and selected-product configurator. The catalog renders the seven REC-015 public JSON-LD fixtures defined in `src/data.ts` (parka, trousers, USPS knit shirt, cap, safety vest, equipment bag, and sergeant chevrons).
- Product cards keep category, model, price snapshot, image, and Configure action together. The configurator uses fieldsets, pressed option buttons, fit guidance, quantity, personalization notes, fulfillment choice, and an enabled Add to request button that, when a required option is missing, shows the error below that option and moves focus to it on submit. A service band and footer keep phone/email help visible.
- The request list is a right-side off-canvas drawer on wide screens and a full-width panel on phones. It repeats the continuity notice, preserves product/options/quantity/notes/fulfillment, and offers Draft email request, Call, and Clear request actions. A size-guide dialog provides fit context and a call-for-help route.

## Data and commerce boundary

- Fixture names, public source URLs, recovered source-image URLs, and option labels are owned by `src/data.ts`; the seven exact public image binaries and SHA-256 checks are documented in `ASSET-PROVENANCE.md`.
- Prices and details are labeled as a recovered public snapshot. They are migration/reference evidence and do not promise current inventory, availability, price, image rights, or fit. Authenticated OpenCart/Ecwid data, private customers/orders, and live catalog state are absent.
- The flow stops at a demonstrative request preview and human handoff through `mailto:` or `tel:`. There is no payment, checkout, order submission, authorization gate, agency portal, or inventory integration. M.T. Uniforms confirms final fit and availability with the requester.

## Responsive and accessible behavior

- Desktop keeps the role rail, catalog, and configurator visible together. At `max-width: 1150px`, the configurator continues full width with image/body treatment; at `max-width: 800px`, the page becomes one stacked reading path, the role rail/category shelf can scroll horizontally, and the request drawer fills the viewport; at `max-width: 480px`, product cards become one column and the brand lockup compacts. Primary surfaces avoid horizontal page scrolling.
- A skip link targets the catalog. Native buttons, links, labels, fieldsets/legends, `aria-pressed`, `aria-invalid`/descriptions, descriptive image alt text, visible `:focus-visible` outlines, and touch-sized controls carry the interaction without color-only state.
- Drawer and size-guide dialogs expose `role="dialog"`, `aria-modal`, and labelled titles. `useDialogFocus` moves focus into the open panel, wraps Tab, closes on Escape, and restores the trigger; scrims provide an explicit close control. Reduced-motion preferences disable drawer/image transitions and use instant programmatic scrolling.

## Verification routes

- From `storefront/`, run `npm test`; it invokes `scripts/verify.mjs`, which checks the exact notice, seven source-backed fixtures, request/no-payment and handoff boundaries, required-option/no-results/notes behavior, keyboard and reduced-motion contracts, responsive CSS, seed `734cebaa`, credential-like literals, asset hashes, and the production build/dist contract.
- From the repository root, the equivalent route is `node storefront/scripts/verify.mjs`. Visual review artifacts are `storefront/evidence/desktop.png`, `storefront/evidence/mobile.png`, and `storefront/evidence/mobile-request.png`.

## Tokens and formats

All values live as custom properties on `:root` in `src/styles.css`; dark mode redefines the same names under `prefers-color-scheme: dark` and `[data-theme="dark"]`. Components never override colours.

- **Colour:** `--surface-page`, `--surface-card`, `--surface-raised`, `--border`, `--ink`, `--ink-muted`, `--accent` (kelly fill, `--on-accent` ink text), `--accent-ink` (accent as text), `--status-error`, `--status-success`, `--status-info`; values and dark redefinitions are in the root record. Kelly fills the primary button, selected states and the request count badge. The continuity notice and header use `--inverse` with `--on-inverse`.
- **Spacing scale:** 4 to 64 as `--space-1` to `--space-8`; the page gutter is `clamp(var(--space-4), 4vw, var(--space-8))`.
- **Type scale:** `--fs-small`, `--fs-body`, `--fs-lead`, `--fs-title`, `--fs-display`; display Archivo Narrow 700 (`@fontsource-variable/archivo-narrow` 5.3.0), titles Archivo Narrow 600, body Archivo 400/600. At most three sizes and three weights per screen.
- **Radii:** `--radius-control` 6px, `--radius-card` 12px, `--radius-pill` for count badges only.
- **Elevation:** `--elev-1` (plate under the pointer or selected), `--elev-2` (request drawer and dialog); resting plates separate by surface tone.
- **Motion:** `--ease-out`, `--ease-in`, `--dur-fast` 120ms, `--dur-base` 200ms, `--dur-slow` 320ms. Reduced motion zeroes the durations.
- **Focus:** a 3px `:focus-visible` ring in `--focus`, which flips to `--on-inverse` on the header, notice and service band.
- **Containers:** `.product-card` is a size container; its layout answers to its own width (`@container product`).
- **Formats:** prices are US dollars with two decimals and a leading `$` (`$159.98`), tabular numerals; quantities are `Qty 2`; there are no dates; inline lists use commas, never a middle dot.
- **Case and punctuation:** sentence case everywhere, including the wordmark (`M.T. Uniforms`) and the role rail heading; no kicker labels above headings; no terminal period on a title or label.

### Recorded exceptions

- The continuity notice keeps its client-supplied wording and the trailing exclamation mark (`New Website Coming!`), because the exact string is a verified requirement.
- The M/T monogram is stacked capitals inside a square; it is a mark, not a label.
- The category tab strip and role rail scroll horizontally inside their own boxes on narrow screens by design.
