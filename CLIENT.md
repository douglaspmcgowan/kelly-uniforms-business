# Client profile

Last updated: 2026-08-09
Profile status: Draft

## Public contact information

These values are published on the client's own live website and are safe to
reuse in public-facing deliverables. Verified against the live site on
2026-07-31. Source: `OBS-004`, `WEB-001`.

| Channel | Public value | Where it appears |
|---|---|---|
| Business name | M.T. Uniforms (storefront) / MT Uniforms LLC (marketing) | contact page, footer |
| Address | 525 Franklin St, Johnstown, PA 15901 | contact page |
| Telephone | 814-536-2390 | contact page (plain text, not a `tel:` link) |
| Website | <https://www.mtuniforms.com/> | — |
| Order email | `orders@mtuniforms.com` | client-requested for the notice; not yet published on the site |

Not found on the live home or contact pages during the 2026-07-31 check:
`800-535-0134` and `sales@mtuniforms.com`. Both were recorded on 2026-07-26 and
need re-sourcing or retiring.

**Private contact information is deliberately excluded from this repository.**
Owner personal email addresses, personal mobile numbers, and all administrative
account identifiers stay out of Git, chat, and screenshots. They live in
Bitwarden and in Douglas's own message history. See `ACCESS.md`.

## Identity

- Trading name: MT Uniforms LLC. Source: `MSG-001`, `FILE-001`, `FILE-006`.
- Business type: Uniform, apparel, equipment, and custom-product retailer/service provider. Source: `FILE-001`, `WEB-001`.
- Confirmed public website: https://www.mtuniforms.com/. Source: `MSG-001`, `WEB-001`.
- Johnstown location shown in supplied materials: 525 Franklin St, Johnstown, PA 15901. Source: `FILE-001`, `FILE-003`.
- State College and surrounding areas are named as a service area in supplied materials. Source: `FILE-003`.
- Ownership descriptors remain client-confirmation items. Supplied materials use “women owned,” “firefighter owned,” and “woman owned & firefighter managed.” Source: `FILE-001`, `FILE-005`.

## Business

### Products and services

- The public storefront currently presents police, fire/EMS, PA constable, corrections, security, postal, badges, footwear, apparel, equipment, and related accessories. Source: `WEB-001`.
- Supplied marketing materials present custom apparel, DTF printing, glass etching, hats/headwear, accessories, shirts, hoodies, and custom equipment. Source: `FILE-001`.
- Supplied materials also present local pickup and delivery. Source: `FILE-003`, `FILE-005`.

### Customers, users, and buyers

- The public site title and category structure identify police, fire, EMS, security, corrections, constables, and USPS/postal customers. Source: `WEB-001`.
- Supplied materials also name schools, businesses, teams, and organizations. Source: `FILE-005`.

### Desired outcomes

- Preserve order continuity while the existing cart and other connections are unreliable. Source: `MSG-001`.
- Direct customers to email or phone ordering through a prominent temporary website notice. Source: `MSG-001`.
- **Modernize the site and let customers pay online instead of receiving an invoice.** Kelly's own words. This reframes the future-site work from a cosmetic refresh to a payments-and-checkout change. Source: `MSG-004`.
- **Keep Clover as the point of sale.** The client confirmed "We use clover. As our pos" and asked directly whether OpenCart can work with Clover. Any platform recommendation must answer that question. Source: `MSG-004`.
- **No attachment to the current design.** Asked what aesthetic they wanted to keep, the reply was "Nothing I want to keep." A full redesign is in scope for `DEL-003`. Source: `MSG-004`.

### Differentiators and proof

- Supplied materials claim no minimum orders, fast turnaround, local ownership, custom work, quality, and small-business service. These are observed marketing claims awaiting current operational confirmation. Source: `FILE-001`, `FILE-005`, `FILE-007`.
- “One Mission. One Family.” and service/protection themes recur across supplied artwork. Source: `FILE-002`, `FILE-004`, `FILE-005`.

## Stakeholders and decisions

| Person or role | Organization | Interest | Influence | Decision authority | Communication | Source |
|---|---|---|---|---|---|---|
| Kelly Huntington — co-owner | MT Uniforms LLC | Website continuity, modernization, and moving customers from invoicing to online payment | High | Co-owner; states the business direction | Primary contact in Douglas's message thread; personal address withheld from Git | `MSG-004` |
| David — co-owner | MT Uniforms LLC | Day-to-day ordering and the operational reality of the website | High | Co-owner; described by Kelly as handling more of the ordering and better informed on the website | Reachable in the same thread; personal number withheld from Git | `MSG-004` |
| Previous owner | Former proprietor | Currently believed to be paying for the existing platform | Passive but load-bearing | None over this project; controls a billing relationship the business depends on | No direct contact established | `MSG-004` |
| Douglas | Consulting practice | Client intake, delivery governance, and implementation | Influence unknown | Repository and consulting-work decisions | Codex task | `MSG-002`, `DEC-001` |
| MT Uniforms customers | Public buyers and organizations | Needs require discovery | Impact unknown | No project decision authority identified | Public website, phone, and email | `MSG-001`, `WEB-001` |

## Current digital estate

| System | Purpose | Owner | Current condition | Access required | Source |
|---|---|---|---|---|---|
| `mtuniforms.com` | Public OpenCart catalog/storefront loading Journal 3 assets | MT Uniforms LLC | Live; the cart failure was reproduced on 2026-08-12 as a www/bare-host session split; the temporary notice is present in the current public capture | `MT_UNIFORMS_WEBSITE_ADMIN_USERNAME` and `MT_UNIFORMS_WEBSITE_ADMIN_PASSWORD` through the approved access path | `MSG-001`, `WEB-001`, `WEB-002`, `OBS-001`–`OBS-004`, `OBS-006`, `DEC-002` |
| OpenCart administration | Production storefront administration | MT Uniforms LLC | Standard administration login remained live at `https://www.mtuniforms.com/admin/` on 2026-07-30; no credentials entered | Same website-admin secret pair; required Journal access/modify permissions must be confirmed after login | `WEB-002`, `OBS-001`, `OBS-003`, `DEC-002` |
| Ecwid control panel | Hosted commerce platform ("Ecwid by Lightspeed"); the officially Clover-integrated online store | MT Uniforms LLC | Renders no part of the public site as of 2026-07-31. **Most likely explanation: it was signed up for as the Clover-connected online store and never launched or was abandoned.** Ecwid's Clover app is first-party (built by Lightspeed) and syncs Clover products, inventory, and orders | `MT_UNIFORMS_ECWID_ADMIN_USERNAME` and `MT_UNIFORMS_ECWID_ADMIN_PASSWORD` through the approved access path | `MSG-001`, `MSG-004`, `OBS-001`, `OBS-003`, `OBS-004`, `DEC-002` |
| Clover POS | In-store point of sale, inventory, and card processing | MT Uniforms LLC | Confirmed in use by the client. Clover binds the merchant to Fiserv processing and to device-locked hardware, so switching processors has contractual and hardware cost. Contract terms, ISO, term length, early-termination fee, lease status, and whether surcharging is enabled are all unknown and materially affect the platform decision | Not required for the current deliverables; contract terms needed from the client | `MSG-004` |
| Email ordering | Order-continuity channel | MT Uniforms LLC | Client requests `orders@mtuniforms.com` in the temporary notice | Mailbox readiness should be confirmed before publication | `MSG-001` |
| Phone ordering | Order-continuity channel | MT Uniforms LLC | Client requests `(814) 536-2390` in the temporary notice | Call handling readiness should be confirmed before publication | `MSG-001` |
| Business-continuity recovery | Portable public-site evidence, normalized data, media, Journal settings, public business/infrastructure observations, checksums, and restore records | Custody: Douglas; business/account control remains source-specific and unverified where no primary account evidence exists | REC-003 is schema-versioned, relative-path portable, self-verifying, and isolated-restore tested under `PROJECT_DATA_ROOT\backups\business-continuity`; full private OpenCart, Ecwid, and account-control captures remain missing. Clover remains the retained POS and is not an authenticated export target for this work | Value-safe OpenCart/Ecwid or hosting access for remaining exports | `REC-001`, `REC-002`, `REC-003`, `MSG-005`, `MSG-006`, `DEC-005` |

## Brand

### Supplied assets

Seven client-provided raster assets are recorded under `PROJECT_DATA_ROOT\inputs\client-provided\2026-07-26`. Their exact filenames, dimensions, sizes, and SHA-256 checksums are recorded in `SOURCES.md` and `data-manifest.yaml`. The 1024×1024 `MT Logo.PNG` was confirmed locally accessible on 2026-07-30; the public site also exposed its existing 299×82 cached header logo. Sources: `FILE-001` through `FILE-007`, `OBS-003`.

### Observed visual and verbal patterns

- Dominant palette: black, white/silver, and red, with blue and gold used for police/EMS and commemorative details. Source: `FILE-001`, `FILE-002`, `FILE-004`, `FILE-005`, `FILE-006`.
- Recurring forms: Maltese-cross badge, police shield, Star of Life, firefighting tools, American flag imagery, and first-responder scenes. Source: `FILE-001`, `FILE-002`, `FILE-006`.
- Typography in supplied art uses condensed uppercase display lettering, distressed textures, and high-contrast service-oriented slogans. Source: `FILE-001`, `FILE-002`, `FILE-004`, `FILE-005`, `FILE-007`.
- The recovered storefront and client-supplied patch use two unrelated identities: a dated blue eagle/value header and a dense photoreal Maltese-cross patch. The patch connects well to embroidery and signals the category, but it is too complex for navigation, favicon, one-color printing, invoices, and consistent cross-channel use. Sources: `REC-001`, `FILE-006`.
- Three concept routes are preserved for selection: Service Standard (modern heraldic), Quartermaster (recommended modern outfitter), and One Mission (community service). They are decision aids, not production trademarks. Sources: `BRAND-001`–`BRAND-003`.

### Accessibility, licensing, and usage constraints

- The client supplied the assets. Ownership, trademark clearance, source/vector availability, reproduction rights, and permission for public reuse remain open. Sources: `FILE-001` through `FILE-007`.
- Several screenshots are low resolution and unsuitable as primary production assets without replacement or careful limited use. Source: `FILE-003`, `FILE-005`, `FILE-007`.
- The current public page needs a browser-visible accessibility review when implementation begins. Source: `WEB-001`.

## Constraints and risks

### Operational

- **The previous owner is believed to be paying for the current platform and may stop.** Kelly: "The old platform is from the previous owner and I think he stops paying for it." If that billing lapses, hosting, the domain, the Journal 3 licence, or all three could be cut off with little notice, taking the storefront offline. Establishing who actually controls and pays for the domain, hosting, and licences is now the highest-priority unknown in the engagement — it is a continuity risk that outranks the cosmetic work. Source: `MSG-004`.
- Ordering continuity is urgent because the client reports a broken cart link and other connection failures. Source: `MSG-001`.
- Orders currently arrive as invoices rather than paid online transactions, which the client wants to change. Source: `MSG-004`.
- The requested phone and email differ from the contact details currently fetched from the public site and should be intentionally reconciled during implementation. Source: `MSG-001`, `WEB-001`.

### Technical

- The visible storefront uses OpenCart routes and Journal 3 assets, and the standard OpenCart login route is active. Installed versions, authenticated Journal controls, and Ecwid's present role remain open. Sources: `MSG-001`, `WEB-001`, `WEB-002`, `OBS-001`.
- A live change requires authenticated administrative access, a reversible edit path, and post-change browser verification.
- A fresh live audit on 2026-08-09 found OpenCart, Ecwid, and Clover at their login screens; no authenticated vendor session was available. Only OpenCart and Ecwid authenticated exports remain gated on a signed-in handoff or the value-safe credential broker; Clover login is outside current scope. Source: `OBS-005`, `MSG-005`, `MSG-006`, `DEC-005`.

### Data, privacy, security, and compliance

- Administrative account identifiers and credential values stay outside Git.
- Product/customer/order data has not been provided and should be treated as private if later accessed.
- Public-safety organization names, marks, and uniform requirements may introduce trademark, policy, or vendor constraints that require client confirmation.

## AI context

- Intended use: The sources inventoried through 2026-07-26 contain no request for an AI-enabled client product or automation. Sources: `MSG-001`, `MSG-002`.
- Affected people: Unknown until an AI deliverable is proposed.
- Data classes: The sources inventoried through 2026-07-26 contain no client operational dataset. Sources: `MSG-001`, `MSG-002`, `data-manifest.yaml`.
- Human oversight: Approval authority for any future AI-enabled work is unknown and requires an explicit decision source.
- Cost of failure: Unknown; assess per future deliverable.
- Evaluation evidence: Define before any AI feature enters active scope.
- Monitoring: Define before deployment.
- Shutdown or rollback authority: Client owner and Douglas roles require explicit assignment per future deliverable.

## Evidence status

### Confirmed

- Client requested a temporary top-of-site notice with exact contact directions. Source: `MSG-001`.
- Client identified `mtuniforms.com` and supplied an Ecwid control-panel URL. Source: `MSG-001`.
- Douglas requested a reusable client skill plus this project profile, deliverables file, and repository setup. Source: `MSG-002`, `DEC-001`.

### Observed

- The public site was live and lacked the requested temporary notice during the 2026-07-30 live browser recheck. Sources: `WEB-001`, `OBS-003`.
- Current public-site categories and contact details are recorded from the fetched page. Source: `WEB-001`.
- Brand and marketing observations come from the seven supplied images. Source: `FILE-001` through `FILE-007`.

### Inferred

- The future website will likely need a commerce-platform decision and content migration; the client has not defined either.
- The documented Journal Header Notice is a likely reversible implementation, pending authenticated confirmation that this installation exposes the expected controls.

### Open questions and contradictions

- Which OpenCart and Journal versions are installed, and does the website-admin account expose the documented Header Notice and All Layouts controls?
- Is `orders@mtuniforms.com` active, monitored, and ready to publish?
- Should `(814) 536-2390` replace the current public-site phone `800-535-0134`, or appear alongside it?
- Should `sales@mtuniforms.com` remain public?
- Which ownership wording is current and approved: women-owned, woman-owned, firefighter-owned, or firefighter-managed?
- Which supplied marks and images have confirmed public-web usage rights and vector/source files?
- What is the approved scope, budget, timeline, and acceptance process for the future website?
