---
name: MT Uniforms Brand Direction Gallery
description: A Varsity Catalogue selection room for reviewing three exploratory MT Uniforms brand directions.
colors:
  surface-page: "#f3f2ee"
  surface-card: "#fbfaf7"
  ink: "#0b1d34"
  ink-muted: "#4f5a63"
  accent: "#46bc24"
  accent-ink: "#1f6b12"
  status-error: "#a52819"
  status-success: "#175b31"
  surface-page-dark: "#111820"
  surface-card-dark: "#18212b"
  ink-dark: "#eeede8"
  ink-muted-dark: "#a9b3bc"
  accent-ink-dark: "#6fd64c"
  status-error-dark: "#ff8a78"
  status-success-dark: "#7fd39b"
typography:
  display:
    fontFamily: "Archivo Narrow Gallery, Arial Narrow, sans-serif"
    fontSize: "clamp(2.375rem, 5vw + 0.75rem, 4.1875rem)"
    fontWeight: 700
    lineHeight: 0.95
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Archivo Narrow Gallery, Arial Narrow, sans-serif"
    fontSize: "clamp(1.5rem, 2.2vw + 0.875rem, 1.75rem)"
    fontWeight: 600
    lineHeight: 1.1
  body:
    fontFamily: "Archivo Gallery, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
rounded:
  control: "6px"
  card: "12px"
spacing:
  scale: "4, 8, 12, 16, 24, 32, 48, 64"
  page-gutter: "clamp(1rem, 3vw, 3rem)"
components:
  primary-action:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
  swatch-card:
    backgroundColor: "{colors.surface-card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
---

# Design system: MT Uniforms Brand Direction Gallery

The gallery follows the root `DESIGN.md` section "Design system: Varsity Catalogue", which owns every token value (colour, type, spacing, radius, elevation, motion). This file records only how the gallery applies it. History: until 2026-10-06 the gallery used a graphite and safety-orange specification wall; the Varsity Catalogue recut replaced it (design-audit-20261003, packet 3).

## Overview

A calm selection room for three exploratory directions: Service Standard, Quartermaster (recommended) and One Mission. It is not a fourth identity. The frame stays neutral so the boards can be judged: ink and paper, kelly green only on the primary action and the status marker accent, Archivo Narrow headings over Archivo body, sentence case, no eyebrow labels.

## Colour

Eight literal colours per scheme (light and dark), defined as custom properties on `:root` and redefined under `prefers-color-scheme: dark` and `[data-theme="dark"]`. Raised surface and border are mixes of ink into the page. Kelly (`--accent`) fills the review action and the closing disclaimer field with ink text; `--accent-ink` carries accent as text or a rule. Status colours are separate from the accent and always pair with a bar and a word. Colours sampled from a board never enter the gallery frame.

## Typography

Display and titles: Archivo Narrow Gallery (self-hosted `assets/fonts/archivo-narrow-variable.woff2`, OFL-1.1), weight 700 for display and 600 for titles, tracking -0.02em on display only. Body: Archivo Gallery (self-hosted `assets/fonts/archivo-variable.woff2`), 400 and 600. Both declare `font-display: swap` with Arial Narrow and Arial fallbacks. Scale tokens: `--fs-small`, `--fs-body`, `--fs-lead`, `--fs-title`, `--fs-display`.

## Layout

A bounded wall, `--max` 1540px, with a fluid gutter (`--pad`). The recommendation is a two-column work order: a status rail beside the featured Quartermaster sheet. Below it, the swatch cards sit in an auto-fit grid of three. Alternatives use unequal copy-and-board pairs, not equal cards. At 900px and below regions stack; at 600px and below navigation text is removed, the recommendation moves first and a compact status sentence repeats in its header.

## Components

- **Swatch card.** One per direction: name in Archivo Narrow, direction number below in muted text, palette chips, and a link to the board. Radius 12px (`--radius-card`), plain card surface, `--elev-1` once, on hover. The recommended card carries a 2px `--accent-ink` outline.
- **Palette chips.** Radius 6px, raised surface. They carry the palette names printed on each board (Charcoal and Signal red; Deep navy; Civic blue and Clay). The record holds no colour codes, fabric or care lines for any direction, so none are shown; colour codes and a fabric and care line are proposed for later, once the client supplies verified garment and palette specs.
- **Primary action.** Kelly fill, ink text, 6px radius; hover lifts 4px and shows `--elev-1`.
- **Board frames.** 12px radius, flush mounts for the concept art; no overlay, caption badge or palette reinterpretation.
- **Status rail.** Raised surface, divided definition rows; each state pairs a horizontal bar, a colour and a word (Verified, Remain, Pending, Separate).
- **Comparison table.** The page's single deliberate dark band; `--inverse` ground with a keyboard-focusable horizontal scroller below 780px.

## Motion and accessibility

Tokens `--ease-out`, `--dur-fast` 120ms, `--dur-base` 200ms. Motion marks feedback only: link and action hover, swatch-card shadow, native smooth anchor scrolling. Reduced motion zeroes the durations without `!important`. Skip link, landmarks, descriptive board alt text, visible 3px focus rings, a labelled scrollable table region.

## Do's and don'ts

- Do keep Quartermaster primary and present the other two as credible alternatives, not equal cards.
- Do keep the recommendation-first mobile order and the compact mobile status line.
- Don't present the monogram as an approved logo; it is a gallery identifier.
- Don't import a board's palette, type or marks into the frame.
- Don't add uppercase text, eyebrow labels, extra dark bands, or a second elevation on a surface.

## Compliance record

- **Colours:** the root system's tokens, light and dark; the dark comparison band and header use `--inverse`.
- **Spacing scale:** 4 to 64 (`--space-1` to `--space-8`); chapter breaks use `--space-section`.
- **Radii and elevation:** `--radius-control` 6px, `--radius-card` 12px; `--elev-1` on the primary action and swatch cards on hover.
- **Container query:** the fact lists answer to their own container (`@container facts`).
- **Formats:** no prices, dates or measured units appear; direction numbers are `Direction 01` to `Direction 03`.
- **The one deliberate inversion:** the comparison band "What each route prioritizes". The ink header and the recommendation sheet header are chrome and a card header.
- **Identity:** favicon `assets/favicon.svg`, Open Graph image `assets/og-image.png` (relative path; no deployed origin recorded), `theme-color` `#0b1d34` (a literal hex because the attribute cannot take a custom property).
