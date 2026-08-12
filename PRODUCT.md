# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

delegated: Vite + React + TypeScript static prototype for the D3 storefront slice, with a future commerce adapter reserved for a separately approved implementation. No authenticated commerce connection is present in this phase.

## Users

The primary users are public M.T. Uniforms customers: first responders, law-enforcement and security staff, postal and corrections staff, organizations, and local buyers who need to find a uniform, footwear, apparel, or equipment item and understand its fit or customization choices. They may be on a phone at a station or in the field, or on a desktop while arranging an order.

M.T. Uniforms staff are the secondary users. They receive an order request or a phone call, clarify details, and complete the transaction through the business's approved process. Douglas and the owners are evaluators of the prototype's clarity and fidelity to sourced public evidence.

## Product Purpose

This is a web replacement storefront prototype for M.T. Uniforms / MT Uniforms LLC. It modernizes the public product-discovery and inquiry experience around the business's real workflow: customers should be able to find a relevant item, understand the choices needed to order it, and reach a human when online checkout is unavailable.

The first slice protects order continuity while making the future storefront concrete. It uses a small, verified public fixture catalog and media, supports role/category/search discovery, explains fit and options, demonstrates a request/cart path, and keeps the temporary order notice visible. The prototype is successful when a visitor can move from a role or search term to a complete product request without guessing what is required, while the boundary between a demonstration and a real paid order remains unmistakable.

## Positioning

Working positioning (ASSUMED, pending client discovery): a local uniform outfitter's clear, fit-first catalog with human ordering always within reach. The product treats fit, personalization, and fulfillment context as part of the item a customer is requesting, while preserving a practical fallback to M.T. Uniforms staff.

## Operating Context

- The current public storefront has client-reported cart and connection failures. REC-015's current public recovery shows the requested continuity notice on the reachable storefront pages; the 2026-07-30 absence is historical evidence of the earlier state. The public catalog and category taxonomy are evidence for this prototype; the installed administration, private catalog data, and account ownership are not verified.
- Clover remains the client's in-store point of sale. The prototype documents that boundary and does not claim an inventory, payment, or order synchronization.
- The temporary continuity copy is exact: “New Website Coming! For all orders email orders@mtuniforms.com or call us directly at (814) 536-2390.” The email and phone are the fallback ordering path for this slice.
- Public contact evidence includes M.T. Uniforms, 525 Franklin St, Johnstown, PA 15901, and 814-536-2390. Contact copy must remain attributable to the public/client record.
- The prototype is evaluated on narrow, medium, and wide screens with keyboard and touch interaction. It is a separate demonstrative surface; it does not mutate the live storefront, brand gallery, or recovery generations.

## Capabilities and Constraints

- Discover products through customer role, category, and search, with an understandable no-results state.
- Render these seven verified public fixture products and media from REC-015's public page evidence: Spiewak Visguard Two Tone Hi-Vis Waterproof Safety Parka; Elbeco Tek2 Cargo Pocket Trousers; USPS Letter Carrier Performance Knit Shirt; W. Alboum Cushion Air Pershing Style Uniform Cap; Adjustable High Visibility Break Away Safety Vest; 5.11 Tactical Wingman Nylon Equipment Bag; and Embroidered Sergeant Chevrons. Retain a source/provenance reference for each fixture. Product options and fit guidance must reflect only what the corresponding public evidence supports.
- Show product media, fit guidance, required options, optional personalization, and any request-specific notes beside the item they describe.
- Build a demonstrative cart/request summary that preserves product, options, personalization, quantity, and contact preference. The flow must say when a request is only a demonstration.
- Keep the exact temporary notice and actionable email/phone controls available from the storefront's primary ordering path.
- Meet a WCAG-oriented floor: semantic structure, keyboard completion, visible focus, logical tab order, accessible names, text alternatives for media, non-color state cues, touch-sized controls, responsive reflow, text resizing/zoom, and reduced-motion tolerance.
- The future commerce adapter is a seam for later approved work, not a launch feature. No real payment checkout, customer authentication, live inventory, order submission, agency account, or private integration is implied by this prototype.
- Authenticated OpenCart, Ecwid, Clover, customer, order, and private catalog data is not present in this repository. Public recovery evidence is useful for fixtures and media; it is not a complete business-data export.
- Supplied logos and campaign images have unresolved public-web rights and may be low resolution. No supplied asset is a production identity approval.

## Brand Commitments

- Use the public business names M.T. Uniforms (storefront) and MT Uniforms LLC (marketing) as sourced.
- Preserve a plain, practical, local-service voice. Do not invent testimonials, ownership claims, customer counts, prices, inventory promises, turnaround promises, or agency capabilities.
- The owners stated that there is no current design they need to keep. The three brand directions in the gallery are concept directions; Quartermaster is a recommendation for exploration, not a client-approved replacement identity. This storefront must not claim approval of a new mark, wordmark, palette, or visual identity.
- Use source-backed public media with provenance. Treat the seven client-supplied raster assets as rights-uncertain until the client confirms public use and production suitability.

## Evidence on Hand

- `CLIENT.md` records the public business identity, audience, contact details, current digital estate, stakeholder context, and evidence boundaries.
- `STORE-REQUIREMENTS.md` records the broader commerce questions and marks agency allowances, authorization codes, and related capabilities as confirmation-dependent.
- `PLATFORM-RECOMMENDATION.md` recommends stabilizing continuity first and deferring platform or custom-workflow decisions until the business workflow is observed.
- `evidence/2026-07-31-site-architecture-scope.md` records the public taxonomy and the earlier cart-option validation evidence; it is historical context for the fixture rules.
- `evidence/2026-07-30-public-site-recheck.md` records the public M.T. Uniforms logo and the historical absence of the requested notice during that check.
- REC-015 is the current recovery authority: 528 reachable public pages, 1,542/1,542 exact public media binaries, and zero private normalized/import rows. Its public page and public JSON-LD snapshot evidence is the source for the seven fixture products and their media; that snapshot is not authoritative inventory or pricing.
- Authenticated OpenCart and Ecwid private data is not present in this prototype. No private products, customers, orders, prices, or payment records may be fabricated; REC-015's public evidence does not stand in for those exports.

## Product Principles

1. Preserve ordering continuity before adding conversion ambition.
2. Put fit and personalization decisions beside the product they affect.
3. Prefer source-backed facts and media; label every assumption.
4. Keep human help visible and actionable at the moment a customer needs it.
5. Leave room for a future commerce adapter without pretending that one exists.

## Accessibility & Inclusion

The prototype targets a WCAG 2.1 AA-oriented experience for public browsing and request preparation. It must work with keyboard-only navigation, visible focus, semantic/native controls, screen-reader names and text alternatives, sufficient contrast, non-color state cues, touch-sized targets, narrow and wide layouts, text resizing and zoom, and reduced motion. Plain language and role/category labels should support mixed familiarity with uniform retail; no essential state may depend on color, hover, or a private account.
