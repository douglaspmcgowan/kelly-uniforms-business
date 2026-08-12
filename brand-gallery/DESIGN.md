---
name: MT Uniforms Brand Direction Gallery
description: A neutral technical specification wall for reviewing three exploratory MT Uniforms brand directions.
colors:
  graphite-ink: "#11151a"
  recommendation-navy: "#081d34"
  warm-paper: "#f3f0e9"
  bright-paper: "#fbfaf7"
  status-paper: "#e8e4db"
  muted-graphite: "#5d636a"
  technical-rule: "#c9c5bc"
  safety-orange: "#e85d0f"
  safety-orange-dark: "#a83c00"
  verified-green: "#1f6752"
typography:
  display:
    fontFamily: "Archivo Gallery, Arial Narrow, sans-serif"
    fontSize: "clamp(3.2rem, 6vw, 5.5rem)"
    fontWeight: 800
    lineHeight: 0.9
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "Archivo Gallery, Arial Narrow, sans-serif"
    fontSize: "clamp(3rem, 5.5vw, 5rem)"
    fontWeight: 800
    lineHeight: 0.9
    letterSpacing: "-0.035em"
  body:
    fontFamily: "Archivo Gallery, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Archivo Gallery, Arial Narrow, sans-serif"
    fontSize: "0.78rem"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "0.1em"
rounded:
  square: "0"
spacing:
  page-gutter: "clamp(1.1rem, 3vw, 3rem)"
  section-block: "clamp(5rem, 11vw, 10rem)"
  panel-padding: "clamp(1.5rem, 4vw, 3.5rem)"
components:
  primary-action:
    backgroundColor: "{colors.safety-orange}"
    textColor: "{colors.bright-paper}"
    rounded: "{rounded.square}"
    padding: "1.2rem"
    width: "210px"
    height: "118px"
  status-rail:
    backgroundColor: "{colors.status-paper}"
    textColor: "{colors.graphite-ink}"
    rounded: "{rounded.square}"
    padding: "clamp(2rem, 4vw, 4rem) clamp(1.3rem, 3vw, 2.5rem)"
  board-frame:
    backgroundColor: "{colors.technical-rule}"
    rounded: "{rounded.square}"
---

# Design System: MT Uniforms Brand Direction Gallery

## Overview

**Creative North Star: "The Working Specification Wall"**

The gallery is a calm, technical selection room for evaluating work. Its visual world borrows from work orders, pinned specification sheets, and production-review walls: graphite rails establish authority, warm paper keeps the room human, squared rules organize evidence, and safety orange marks decisions and active states. The density is editorial rather than app-like; large boards and decisive headings carry the reading path.

This system belongs to the gallery interface only. It is not a fourth MT Uniforms identity, and it does not adopt the logo, colors, typography, photography, or application language shown inside Quartermaster, Service Standard, or One Mission. Those boards remain three exploratory directions. Quartermaster receives stronger placement because it is the recommendation, while the frame stays visually neutral enough to judge all three.

**Key Characteristics:**

- Technical specification-wall composition with a narrow operational status rail.
- Warm paper fields bounded by graphite structure and fine rules.
- Safety orange reserved for decisions, indexing, focus, and active emphasis.
- Oversized, condensed-feeling Archivo headlines paired with plain proportional copy.
- Flat, square board frames that present concept artwork without ornamental treatment.
- Responsive editorial reordering that keeps the recommendation first on narrow screens.

## Colors

The palette behaves like a marked-up production document: warm neutral stock carries most content, graphite supplies structure, and orange appears where attention or action is required.

### Primary

- **Safety Orange** (`#e85d0f`): Marks the primary review action, active dividers, the footer disclaimer field, monogram detail, and visible keyboard focus.
- **Deep Safety Orange** (`#a83c00`): Carries direction indices and unresolved operational states on light surfaces where the brighter accent would lose text contrast.

### Secondary

- **Recommendation Navy** (`#081d34`): Identifies the featured Quartermaster sheet header and separates the recommendation from the otherwise neutral gallery frame. It supports the recommendation hierarchy without becoming the gallery's general background.
- **Verified Green** (`#1f6752`): Appears only for the verified operational state in the status rail.

### Neutral

- **Graphite Ink** (`#11151a`): Primary text, navigation rail, and the dark comparison field.
- **Warm Paper** (`#f3f0e9`): Main gallery canvas with a subtle horizontal working-paper grid.
- **Bright Paper** (`#fbfaf7`): Clear content sheets and high-contrast light surfaces.
- **Status Paper** (`#e8e4db`): Distinguishes the status rail through tonal layering.
- **Muted Graphite** (`#5d636a`): Supporting copy, labels, and lower-emphasis information.
- **Technical Rule** (`#c9c5bc`): One-pixel borders, dividers, and board boundaries.

### Named Rules

**The Neutral Frame Rule.** Gallery tokens frame the three concept boards; colors sampled from a board never migrate into the gallery interface unless the selected production identity is later approved and the gallery is deliberately redesigned.

**The Orange Means Decision Rule.** Safety orange marks action, status, indexing, focus, or a deliberate structural break. It is never ambient decoration.

## Typography

**Display Font:** Archivo Gallery (self-hosted variable Archivo, with Arial Narrow and sans-serif fallbacks)

**Body Font:** Archivo Gallery (self-hosted variable Archivo, with Segoe UI and sans-serif fallbacks)

**Character:** One proportional variable family spans compressed-feeling, work-order headlines and calm readable prose. Weight, scale, spacing, and case produce hierarchy; the gallery does not introduce a decorative display face or monospace layer.

### Hierarchy

- **Display** (weight `800`, `clamp(3.2rem, 6vw, 5.5rem)`, line-height `0.9`): Uppercase opening statement and other dominant calls to action; keep the measure tight enough to read as a specification-wall headline.
- **Headline** (weight `800`, `clamp(3rem, 5.5vw, 5rem)`, line-height `0.9`): Major section and recommendation titles.
- **Title** (heavy, responsive, line-height approximately `0.9–0.95`): Direction names and status-rail heading.
- **Body** (weight `400`, base `1rem`, line-height `1.5`): Rationale, status explanations, and comparison content. Long introductory copy stays near `63ch`.
- **Label** (weight `800`, `0.78rem`, tracking `0.1em`, uppercase): Direction numbers and compact technical labels.

### Named Rules

**The One-Family Rule.** Use the self-hosted Archivo file for every gallery role; hierarchy comes from weight, width impression, case, and scale rather than font mixing.

**The Display Is a Sign Rule.** Large headings are short, tightly led, and usually uppercase. Paragraphs remain sentence case and comfortably spaced.

## Layout

The page is a bounded editorial wall with a maximum width of `1540px` and a fluid page gutter (`clamp(1.1rem, 3vw, 3rem)`). Fine vertical rules hold the opening and decision sections together. Generous vertical intervals separate reading chapters, while content inside each sheet uses denser grids and dividers.

At wide sizes, the recommendation is a two-column work order: a narrow status rail (`minmax(240px, 0.25fr)`) beside the flexible featured sheet. The recommendation notes split into two balanced columns. Alternative directions use unequal copy-and-board grids, and the second reverses that relationship to sustain an editorial sequence without reducing the concepts to three equal cards.

At `900px` and below, multi-column regions stack, the status list becomes two columns, and the primary action expands to the full available width. At `600px` and below, navigation text is removed, the recommendation moves before the full status rail, and a compact status summary is repeated inside the recommendation header so decision context remains available. Alternatives return to source order, status rows become one column, and the footer stacks. The recommendation must remain the first concept encountered on narrow screens.

**The Unequal Evidence Rule.** Recommendation, alternatives, and operational status receive space according to decision importance. Do not flatten them into equal cards or a symmetric three-up gallery.

## Elevation & Depth

The gallery is flat by design and uses no box shadows. Depth comes from adjacent paper tones, graphite or navy fields, one-pixel rules, and the orange structural edge beneath dark rails. Board artwork sits flush within clipped rectangular frames; it should feel mounted for inspection, not floated as a product card.

**The Flat Board Rule.** Never add drop shadows, glass effects, floating panels, or soft elevation to the gallery boards. Separation comes from tonal contrast and technical borders.

## Shapes

The form language is square and mechanical (`0` corner radius). Frames, status marks, the monogram, recommendation badge, primary action, table, and section boundaries all use straight edges. Thin one-pixel rules organize information, while the featured recommendation gains a six-pixel orange lower rule. Status markers use short horizontal bars rather than dots so state is visible through both shape and color.

**The Squared Hardware Rule.** Keep every gallery control and container rectilinear. Rounded pills or soft cards would weaken the specification-wall character.

## Components

### Primary Review Action

The action is a safety-orange rectangular work-order stamp with a label and oversized direction number.

- **Shape:** Square (`0` radius), fixed at `210px` wide and at least `118px` high on wide screens.
- **Layout:** Label and direction number sit on opposite vertical ends; at medium and narrow widths the action becomes full-width and horizontal with a `90px` minimum height.
- **Hover:** Lift by `5px` and deepen the orange over `360ms` with `cubic-bezier(.22,.8,.24,1)` to signal direct interaction.
- **Focus:** Use the shared three-pixel safety-orange outline with a four-pixel offset.

### Navigation Rail

The top rail is graphite with white identity text, muted navigation links, and a four-pixel safety-orange lower rule. The bordered MT monogram is an interface identifier for this gallery and must not be mistaken for an approved production logo.

- **Default:** Compact proportional text with generous horizontal spacing.
- **Hover / Current:** Shift links to white and underline them in safety orange; the current state is synchronized to section visibility.
- **Mobile:** Hide navigation labels and the wordmark text below `600px`, retaining the compact monogram and rail.

### Status Rail

The status rail is the operational context layer: a warm-gray paper panel with a large compact heading, divided definition-list rows, and a short explanatory note.

- **Structure:** Place labels above states at wide sizes, separated by one-pixel rules.
- **State:** Pair every color with a horizontal bar and explicit word such as “Verified,” “Remain,” “Pending,” or “Separate.”
- **Responsive behavior:** The rail sits left of the recommendation on wide screens, below it on narrow screens, and yields a concise duplicate status sentence inside the featured header below `600px`.

### Board Frames

Board frames are flat, square image mounts that preserve the concept work as the dominant evidence.

- **Featured board:** Fill the available sheet width and crop to a `3 / 2` ratio where required.
- **Alternative boards:** Preserve the full responsive image and use a one-pixel technical-rule border.
- **Treatment:** No overlay, caption badge, rounded clipping, shadow, or palette reinterpretation may obscure or visually merge with the board.

### Comparison Table

The comparison is a dense, graphite field that turns qualitative differences into a sober decision aid. Header labels are subdued, direction names use orange, and horizontal rules carry scanning across rows. On narrow screens the table retains its `780px` minimum width inside a keyboard-focusable horizontal scroller.

### Motion and Accessibility Behavior

Motion communicates navigation and direct feedback only. Native smooth scrolling supports anchor navigation, the primary action lifts on hover, and the current navigation state follows the most visible observed section. When reduced motion is requested, scrolling becomes immediate and transitions or animations collapse to `0.01ms` with a single iteration.

Keyboard users receive a skip link that appears on focus, visible three-pixel orange focus outlines with four-pixel offsets, semantic landmarks, scoped headings, native links, descriptive board alt text, and a labeled focusable region for the horizontally scrollable comparison table. Operational states always combine color, a bar shape, and text.

## Do's and Don'ts

### Do:

- **Do** preserve the graphite, warm-paper, and safety-orange gallery frame when adding review content.
- **Do** keep Quartermaster visually primary while describing Service Standard and One Mission as credible alternatives.
- **Do** use full-scale board imagery, unequal editorial layouts, and technical dividers to make comparison feel consequential.
- **Do** maintain wide, medium, and narrow ordering behavior, including recommendation-first mobile flow and the compact mobile status summary.
- **Do** retain semantic structure, visible focus, non-color status cues, descriptive alt text, and reduced-motion behavior.

### Don't:

- **Don't** present the gallery interface as an approved MT Uniforms identity or treat its MT monogram as a production-ready logo.
- **Don't** import a concept board's palette, type, mark, photography, or visual motifs into the neutral gallery frame.
- **Don't** turn the three directions into equal cards; recommendation hierarchy is part of the decision experience.
- **Don't** add rounded corners, shadows, glass effects, gradients, or decorative motion to the flat specification-wall system.
- **Don't** let orange become general decoration; reserve it for action, state, indexing, focus, and deliberate structural emphasis.
