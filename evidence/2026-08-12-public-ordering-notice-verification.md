# Public ordering notice verification

## Outcome

The temporary ordering notice is publicly published and visible across representative OpenCart layouts on desktop and mobile.

The 2026-08-12 Playwright pass exercised four live routes at 1440×1000 and 390×844:

| Layout | Desktop | Mobile |
| --- | --- | --- |
| Home | Pass | Pass |
| Police category | Pass | Pass |
| Product with required options | Pass | Pass |
| Cart | Pass | Pass |

All eight checks returned HTTP 200, rendered the exact requested copy, placed the notice visibly above the header, stayed within the viewport width, retained the order-email `mailto:` link, and left the site header visible. Desktop and mobile screenshots were inspected directly after capture.

## Evidence

- Machine report: `evidence/public-ordering-notice-20260812/report.json`
- Desktop screenshots: `desktop-home.png`, `desktop-category.png`, `desktop-product.png`, `desktop-cart.png`
- Mobile screenshots: `mobile-home.png`, `mobile-category.png`, `mobile-product.png`, `mobile-cart.png`
- Reproducible verifier: `scripts/verify-public-ordering-notice.mjs`

The check runs in a fresh browser context without customer authentication. It does not retain cookies or credentials.

## Remaining quality gaps

1. The email address is linked correctly, but the phone number is plain text rather than `tel:+18145362390`.
2. The Journal Header Notice includes a close button. Dismissal-cookie behavior means a returning customer can hide the continuity notice.
3. Public observation proves publication and layout behavior. It cannot prove the module's authenticated Admin Only history, rollback configuration, or Journal export state.

The first two items should be corrected when authenticated OpenCart/Journal access is available. Until then, the notice is readable and publicly serving its continuity purpose.
