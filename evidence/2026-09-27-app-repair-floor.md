# App-repair floor: before and after

Date: 2026-09-27. Branch: `agent/kelly-uniforms-business-repair`. Verdict from the
program specification: `CONVERGE`.

The program brief asks for these rows to be pasted into `LOG.md`. They are here
instead, because Work Scope is enrolled in this repository (`.agents/work/state.json`
exists) and `LOG.md` therefore carries `GENERATED FROM .agents/work/events.jsonl. DO
NOT EDIT DIRECTLY.` at line 1. The shared-harness rule against hand-editing a
generated view wins over the brief's choice of file; `evidence/` is this project's
authored home for dated verification records, and `VERIFY.md` points here.

## The scan

Appendix A `m4`, reproduced verbatim: `git ls-files`, `.css` and `.html` together,
excluding `/.next`, `/dist/`, `/out/`, `/.agents/`, `*.min.css`, `/coverage/` and
`/.tmp-`. Five files in both runs:

    brand-gallery/index.html
    brand-gallery/styles.css
    storefront/index.html
    storefront/src/styles.css
    theme/assets/theme.css

## The rows

| column | baseline (stage 1, `0c1ff80`) | after | direction |
|---|---|---|---|
| style files | 5 | 5 | — |
| KB | 64 | 80 | **up** — see note 1 |
| unique hex | 72 | 111 | **up** — see note 1 |
| distinct font sizes | 55 | 51 | better |
| custom properties | 24 | 126 | better |
| `transition` | 6 | 17 | better |
| `@keyframes` | 0 | 0 | — |
| `!important` | 9 | 6 | better |
| `:focus-visible` | 7 | 10 | better |
| `prefers-color-scheme` | 1 | 3 | better |
| `@container` | 0 | 0 | — |
| `clamp(` | 31 | 32 | better |
| `prefers-reduced-motion` | 3 | 3 | — |

Compact form, in the roster's own order:

    BASELINE  5 / 64KB / 72 / 55 / 24 / 6 / 0 / 9 / 7 / 1 / 0 / 31 / 3
    AFTER     5 / 80KB / 111 / 51 / 126 / 17 / 0 / 6 / 10 / 3 / 0 / 32 / 3

### Note 1: the two columns that went up, and why the app is still better

Both increases are the arithmetic consequence of two items the brief itself ranks
third and seventh, and neither is a quality regression:

- **Extracting a token layer** moves each literal from its use site into `:root`. The
  literal is still in the file, so `unique hex` cannot fall; the added token names and
  comments make the file bigger, so `KB` cannot fall.
- **Adding a `prefers-color-scheme: dark` block** introduces a second palette. Thirty-nine
  new hex values entered the repository for it, all of them inside a `:root` block.

`unique hex` measured across a whole file cannot distinguish a controlled palette from
an uncontrolled one. The metric that can is *unique hex still hard-coded outside a
token-defining block* — the colour that is not yet under a single name. Measured with
the same five files on both sides:

| | baseline (`0c1ff80`) | after |
|---|---|---|
| unique hex, total | 72 | 111 |
| unique hex outside `:root` / `[data-theme]` | **50** | **1** |

The one survivor is `#0b1d34` in `storefront/index.html`'s `<meta name="theme-color">`,
which cannot take a CSS custom property.

## Proof that the token work changed no pixel

`storefront/tests/computed-style-snapshot.mjs` drives the running dev server through six
states — initial, configurator open, options chosen, drawer with an item, size-guide
modal, first keyboard focus — and dumps every computed property of every element.
`storefront/tests/computed-style-diff.mjs` compares two snapshots property by property.

Run across this stage's change to `src/styles.css` and `src/App.tsx`:

    S1_initial        270 elements  146,070 properties compared    270 different
    S2_configurator   270 elements  146,070 properties compared    270 different
    S3_optionschosen  271 elements  146,611 properties compared    271 different
    S4_drawer         305 elements  165,005 properties compared    305 different
    S5_sizeguide      289 elements  156,349 properties compared    289 different
    S6_firstfocus     289 elements  156,349 properties compared    289 different
    TOTAL                           916,454 properties compared  1,694 different

Grouped by property name, the entire difference is:

    color-scheme x1694

That is exactly one per element per state, and it is the dark-mode declaration itself
(`normal` → `light dark`). **No painted value moved**: not a colour, a font size, a
radius, a spacing, a border, a shadow or a transition. The light appearance is
byte-identical.

For `theme/assets/theme.css` and `brand-gallery/styles.css` — a Shopify Liquid asset and
a static page, neither of which the storefront harness can drive — value preservation was
proved a second way: every `var(--x)` was expanded back to its `:root` literal and the
resulting declaration list compared to the previous revision's.

    brand-gallery/styles.css   320 declarations both sides,   0 differing
    theme/assets/theme.css     405 -> 406 declarations, one change only:
                               border-color: #b8440c !important  (removed)
                               border-color: #b8440c             (x2, the unforced rule
                                                                 plus a higher-specificity
                                                                 replacement for it)

## The one change that is deliberately perceptible

Every colour hover and selected state on all three stylesheets snapped, because the
hover rules were added at some point without a `transition` beside them. `theme/assets/
theme.css` had seven hover rules and two pressed rules against zero real transitions.
~/.agents/DESIGN.md section Motion: "An instant state change with no transition, and a
default `linear` or `ease-in-out` curve, both read as unfinished — real easing carries
mass." Eleven transitions were added on `.chip`, `.card`, `.btn`, `.icon-button`,
`.product-card`, `.button`, `.role-rail > button`, `.category-tabs button`,
`.choice-grid button`, `.product-card__media img` and brand-gallery's `nav a`, all on
the repository's own existing easing curve.

This *is* perceptible — it is motion where there was none — so it is reported rather
than buried. What the harness proves is that it changed nothing else. Same six states,
same 916,454 properties, this time with only the transition work in between:

    differing properties: transition-behavior x170, transition-delay x170,
                          transition-duration x170, transition-property x170,
                          transition-timing-function x170

Five sub-properties of `transition` on 170 element-states, and nothing else. No colour,
size, radius, spacing, border or shadow drifted while the transitions went in. Paint
properties only are animated; nothing here animates geometry, per this file's
§ Performance rule against animating `top`, `left`, `width` or `height`.

## Proving commands

    storefront/   npm run typecheck   -> exit 0  (tsc --noEmit && tsc -p tsconfig.node.json --noEmit)
    storefront/   npm run build       -> exit 0  (4557 modules; dist/index.html 1.15 kB,
                                                 index-uiHR7MJT.css 21.56 kB,
                                                 index-BAUQvVWt.js 211.56 kB; 32.90s)
    storefront/   npm test            -> exit 0  ({"passed":true,"products":7,
                                                 "asset_hashes":8,"production_contract":true}
                                                 then 6/6 Playwright specs passed)
    brand-gallery/ npm test          -> exit 0  (tsc --noEmit, then 4 pass / 0 fail)
    preview/       node build.mjs     -> exit 0  (321 products, 51 collections, 5 pages)
    repository     git diff --check   -> exit 0
