# Storefront prototype evidence — 2026-08-12

## Outcome

The first client-first modernization slice is built and published at <https://mt-uniforms-storefront-prototype.vercel.app/>. It uses the provisional Quartermaster Order Ticket design language and preserves the current human ordering workflow: customers find and configure products, review a complete request, then draft an email or call the store. It deliberately does not accept payment.

## Source boundary

- Recovery authority: `%PROJECT_DATA_ROOT%\backups\business-continuity\2026-08-10-rec015`.
- Public recovery available: 528 pages and 1,542 of 1,542 exact referenced media assets.
- Prototype fixtures: seven public product records and exact recovered images, each recorded in `storefront/ASSET-PROVENANCE.md`.
- Authenticated OpenCart and Ecwid exports remain absent. Prices, details, and availability are labeled public snapshots and are not treated as authoritative live commerce data.
- No secret value, private customer/order row, payment collection, authentication, or Clover connection is present in the prototype.

## Verification

- `npm test`: passed; production build, seven source-backed fixtures, eight exact asset hashes, exact continuity copy, contact actions, no-payment boundary, request-review completeness, dialog keyboard implementation, reduced-motion behavior, responsive rules, contrast token, and production seed contract.
- Work Scope receipt: `4b677ac5-7ca9-47e5-9f6a-6a6ad9f63cc6` passed and closed `storefront-modernization/customer-storefront@D3`.
- `npm audit --json`: zero vulnerabilities after moving the build toolchain to Vite 8.2.1 and current compatible packages.
- Design detector: zero findings on the initial finished UI pass.
- Independent visual review: no blocking issue; eight material findings were applied in one pass, including a single desktop scroll context, request notice and notes, contact recovery, required-field prevention, dialog focus/Escape handling, reduced-motion scrolling, and a compliant darker action orange.
- Live production browser: title resolved; incomplete Add was disabled; no-results Email and Call were visible; configured Add became enabled; the final review displayed the exact notice and personalization note; the draft action produced a `mailto:orders@mtuniforms.com` URL; zero console warnings or errors.
- Responsive proof: `storefront/evidence/desktop.png`, `storefront/evidence/mobile.png`, and `storefront/evidence/mobile-request.png`.

## Deployment

- Vercel project: `douglas-mcgowans-projects/mt-uniforms-storefront-prototype`.
- Production alias: <https://mt-uniforms-storefront-prototype.vercel.app/>.
- Verified deployment ID: `dpl_McWWniCjKGJvRejfySUo4pVAATZN`.

## Remaining boundary

This prototype can become a Shopify theme or headless frontend after platform selection by replacing the seven fixtures with authoritative products, variants, inventory, pricing, and checkout APIs. That migration should begin only after the OpenCart and Ecwid private exports are captured through the approved Bitwarden Secrets Manager broker and reconciled into the recovery package.
