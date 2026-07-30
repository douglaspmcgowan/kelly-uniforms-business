# Client profile

Last updated: 2026-07-26  
Profile status: Draft

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
- Prepare for a future website, with scope and timing still open. Source: `MSG-001`.

### Differentiators and proof

- Supplied materials claim no minimum orders, fast turnaround, local ownership, custom work, quality, and small-business service. These are observed marketing claims awaiting current operational confirmation. Source: `FILE-001`, `FILE-005`, `FILE-007`.
- “One Mission. One Family.” and service/protection themes recur across supplied artwork. Source: `FILE-002`, `FILE-004`, `FILE-005`.

## Stakeholders and decisions

| Person or role | Organization | Interest | Influence | Decision authority | Communication | Source |
|---|---|---|---|---|---|---|
| Client contact | MT Uniforms LLC | Website continuity and future replacement | Influence unknown | Website content and account access authority require confirmation | Client supplied email context; personal account identifier withheld from Git | `MSG-001` |
| Douglas | Consulting practice | Client intake, delivery governance, and implementation | Influence unknown | Repository and consulting-work decisions | Codex task | `MSG-002`, `DEC-001` |
| MT Uniforms customers | Public buyers and organizations | Needs require discovery | Impact unknown | No project decision authority identified | Public website, phone, and email | `MSG-001`, `WEB-001` |

## Current digital estate

| System | Purpose | Owner | Current condition | Access required | Source |
|---|---|---|---|---|---|
| `mtuniforms.com` | Public OpenCart catalog/storefront loading Journal 3 assets | MT Uniforms LLC | Live on 2026-07-26; cart and connection failures are client-reported; temporary notice absent; direct empty-cart route loads | `MT_UNIFORMS_WEBSITE_ADMIN_USERNAME` and `MT_UNIFORMS_WEBSITE_ADMIN_PASSWORD` through the approved access path | `MSG-001`, `WEB-001`, `WEB-002`, `OBS-001`, `OBS-002`, `DEC-002` |
| OpenCart administration | Production storefront administration | MT Uniforms LLC | Standard administration login is live at `https://www.mtuniforms.com/admin/`; no credentials entered | Same website-admin secret pair; required Journal access/modify permissions must be confirmed after login | `WEB-002`, `OBS-001`, `DEC-002` |
| Ecwid control panel | Client-named commerce administration with an unknown current role | MT Uniforms LLC | No public evidence in this pass showed Ecwid rendering the visible storefront; integrations, synchronization, checkout, and back-office roles remain open | `MT_UNIFORMS_ECWID_ADMIN_USERNAME` and `MT_UNIFORMS_ECWID_ADMIN_PASSWORD` through the approved access path | `MSG-001`, `OBS-001`, `DEC-002` |
| Email ordering | Order-continuity channel | MT Uniforms LLC | Client requests `orders@mtuniforms.com` in the temporary notice | Mailbox readiness should be confirmed before publication | `MSG-001` |
| Phone ordering | Order-continuity channel | MT Uniforms LLC | Client requests `(814) 536-2390` in the temporary notice | Call handling readiness should be confirmed before publication | `MSG-001` |

## Brand

### Supplied assets

Seven client-provided raster assets are recorded under `PROJECT_DATA_ROOT\inputs\client-provided\2026-07-26`. Their exact filenames, dimensions, sizes, and SHA-256 checksums are recorded in `SOURCES.md` and `data-manifest.yaml`. Source: `FILE-001` through `FILE-007`.

### Observed visual and verbal patterns

- Dominant palette: black, white/silver, and red, with blue and gold used for police/EMS and commemorative details. Source: `FILE-001`, `FILE-002`, `FILE-004`, `FILE-005`, `FILE-006`.
- Recurring forms: Maltese-cross badge, police shield, Star of Life, firefighting tools, American flag imagery, and first-responder scenes. Source: `FILE-001`, `FILE-002`, `FILE-006`.
- Typography in supplied art uses condensed uppercase display lettering, distressed textures, and high-contrast service-oriented slogans. Source: `FILE-001`, `FILE-002`, `FILE-004`, `FILE-005`, `FILE-007`.

### Accessibility, licensing, and usage constraints

- The client supplied the assets. Ownership, trademark clearance, source/vector availability, reproduction rights, and permission for public reuse remain open. Sources: `FILE-001` through `FILE-007`.
- Several screenshots are low resolution and unsuitable as primary production assets without replacement or careful limited use. Source: `FILE-003`, `FILE-005`, `FILE-007`.
- The current public page needs a browser-visible accessibility review when implementation begins. Source: `WEB-001`.

## Constraints and risks

### Operational

- Ordering continuity is urgent because the client reports a broken cart link and other connection failures. Source: `MSG-001`.
- The requested phone and email differ from the contact details currently fetched from the public site and should be intentionally reconciled during implementation. Source: `MSG-001`, `WEB-001`.

### Technical

- The visible storefront uses OpenCart routes and Journal 3 assets, and the standard OpenCart login route is active. Installed versions, authenticated Journal controls, and Ecwid's present role remain open. Sources: `MSG-001`, `WEB-001`, `WEB-002`, `OBS-001`.
- A live change requires authenticated administrative access, a reversible edit path, and post-change browser verification.

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

- The public site was live and lacked the requested temporary notice in the fetched page on 2026-07-26. Source: `WEB-001`.
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
