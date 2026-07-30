# Sources and assets

Last updated: 2026-07-26

## Source ledger

| ID | Type | Description | Location | Received/checked | Sensitivity | Supports |
|---|---|---|---|---|---|---|
| `MSG-001` | Client intake message | Website URL, temporary notice request, cart/connection problem report, Ecwid control-panel URL, and administrative access context. Personal administrative account identifier is intentionally withheld from Git. | Current Codex task | 2026-07-26 | Internal | Client identity, digital estate, `DEL-001`–`DEL-003` |
| `MSG-002` | Douglas instruction | Create a reusable `client` skill for an AI-native digital products/solutions/consulting practice, then make the profile, deliverables file, and normal repository setup. | Current Codex task | 2026-07-26 | Internal | `DEL-004`, repository scope |
| `WEB-001` | Public website | Fetched public storefront, categories, current contact block, and absence of the requested temporary notice in returned page content. | https://www.mtuniforms.com/ | 2026-07-26 | Public | Current digital estate and storefront observations |
| `WEB-002` | Public administration page | Standard OpenCart administration login is publicly reachable and identifies itself as OpenCart Administration. No credentials were entered. | https://www.mtuniforms.com/admin/ | 2026-07-26 | Public | Live administration platform and `DEL-001` runbook |
| `WEB-003` | Official Journal documentation | Header Notice is a Special Module intended for notices at the top of the store; it supports Reset Cookie and assignment through layout Special Modules. | https://docs.journal-theme.com/docs/modules/header-notice | 2026-07-26 | Public | `DEL-001` implementation path |
| `WEB-004` | Official Journal documentation | Layouts support Special Modules on all layouts, and Journal documents Header Notice placement through that control. | https://docs.journal-theme.com/docs/layouts | 2026-07-26 | Public | Store-wide notice placement |
| `WEB-005` | Official Journal documentation | Journal Import / Export is available for backing up existing Journal settings. | https://docs.journal-theme.com/docs/system/import-export | 2026-07-26 | Public | `DEL-001` recovery preparation |
| `WEB-006` | Official Journal documentation | Module status can be limited by device, customer state, customer group, store, or Admin Only for previewing. | https://docs.journal-theme.com/docs/options/status | 2026-07-26 | Public | Preview and publication controls |
| `WEB-007` | Official Journal documentation | Device-specific module status must be tested with an actual mobile device or mobile user agent; resizing a desktop window is insufficient. | https://docs.journal-theme.com/docs/workflow/mobile-workflow | 2026-07-26 | Public | Mobile verification for `DEL-001` |
| `OBS-001` | Browser observation | Public HTML uses OpenCart routes and loads Journal 3 assets from `catalog/view/theme/journal3`; the visible admin route is OpenCart Administration. | `evidence/2026-07-26-public-site-observation.md` | 2026-07-26 | Public | Platform identification |
| `OBS-002` | Browser observation | The direct OpenCart cart route loaded an empty-cart page successfully; add-to-cart and checkout flows were not exercised. | `evidence/2026-07-26-public-site-observation.md` | 2026-07-26 | Public | Bounded cart observation and `DEL-002` |
| `FILE-001` | Client-provided image | `generic card.PNG` — MT Uniforms business/marketing card. | `PROJECT_DATA_ROOT\inputs\client-provided\2026-07-26\generic card.PNG` | 2026-07-26 | Internal | Identity, address, services, brand, ownership claims |
| `FILE-002` | Client-provided image | `5709A7A4-94C1-40E1-903E-3F393AED3C5A.PNG` — first-responder commemorative graphic. | `PROJECT_DATA_ROOT\inputs\client-provided\2026-07-26\5709A7A4-94C1-40E1-903E-3F393AED3C5A.PNG` | 2026-07-26 | Internal | Brand themes and palette |
| `FILE-003` | Client-provided image | `Screenshot 2026-06-08 at 4.32.49 PM.png` — location/service-area block. | `PROJECT_DATA_ROOT\inputs\client-provided\2026-07-26\Screenshot 2026-06-08 at 4.32.49 PM.png` | 2026-07-26 | Internal | Locations and pickup/delivery claim |
| `FILE-004` | Client-provided image | `IMG_5367.jpeg` — “One Mission. One Family.” apparel photograph. | `PROJECT_DATA_ROOT\inputs\client-provided\2026-07-26\IMG_5367.jpeg` | 2026-07-26 | Internal | Brand slogan and first-responder theme |
| `FILE-005` | Client-provided image | `Screenshot 2026-06-08 at 4.32.21 PM.png` — audience and service-benefit block. | `PROJECT_DATA_ROOT\inputs\client-provided\2026-07-26\Screenshot 2026-06-08 at 4.32.21 PM.png` | 2026-07-26 | Internal | Audiences, benefits, ownership wording |
| `FILE-006` | Client-provided image | `MT Logo.PNG` — raster Maltese-cross logo. | `PROJECT_DATA_ROOT\inputs\client-provided\2026-07-26\MT Logo.PNG` | 2026-07-26 | Internal | Identity and logo structure |
| `FILE-007` | Client-provided image | `Screenshot 2026-06-08 at 4.34.44 PM.png` — “Why choose” marketing block. | `PROJECT_DATA_ROOT\inputs\client-provided\2026-07-26\Screenshot 2026-06-08 at 4.34.44 PM.png` | 2026-07-26 | Internal | Differentiator claims |
| `DEC-001` | Douglas decision | Scope the reusable capability to a general AI-native digital products, solutions, and consulting business. | Current Codex task | 2026-07-26 | Internal | Skill design and `DEL-004` |
| `DEC-002` | Douglas decision | Use Bitwarden Secrets Manager as the credential path so an approved agent browser workflow can perform authorized administration. | Current Codex task | 2026-07-26 | Internal | `ACCESS.md`, secret manifests, `DEL-001` |

## Asset ledger

| Source ID | Filename | Stable location | Format | Size/checksum | Usage or rights note | Observations |
|---|---|---|---|---|---|---|
| `FILE-001` | `generic card.PNG` | `PROJECT_DATA_ROOT\inputs\client-provided\2026-07-26\generic card.PNG` | PNG, 1635×962 | 1,979,098 bytes; SHA-256 `9081bd49671ca44ff5329c12e5b65210ff129d5c628170732605f3699ba625e6` | Client supplied; public-web usage rights require confirmation | High-resolution composite marketing card |
| `FILE-002` | `5709A7A4-94C1-40E1-903E-3F393AED3C5A.PNG` | `PROJECT_DATA_ROOT\inputs\client-provided\2026-07-26\5709A7A4-94C1-40E1-903E-3F393AED3C5A.PNG` | PNG, 1254×1254 | 2,574,167 bytes; SHA-256 `f4b124081d82b7f60e1eec72442d5ac82a43f047d952fac58e5c3f37342f1c90` | Client supplied; generated-image/source rights require confirmation | Detailed police/fire/EMS/dispatcher commemorative composition |
| `FILE-003` | `Screenshot 2026-06-08 at 4.32.49 PM.png` | `PROJECT_DATA_ROOT\inputs\client-provided\2026-07-26\Screenshot 2026-06-08 at 4.32.49 PM.png` | PNG, 224×178 | 32,911 bytes; SHA-256 `45ec61b57f96af216519f50a1ed748b906f47bdab65d732c7cf73bed6942344d` | Client supplied; source layout ownership requires confirmation | Low-resolution location and service-area crop |
| `FILE-004` | `IMG_5367.jpeg` | `PROJECT_DATA_ROOT\inputs\client-provided\2026-07-26\IMG_5367.jpeg` | JPEG, 1736×566 | 245,117 bytes; SHA-256 `c21db797d58afeda0e768c1a8971e183fe10b6485445815a03e3eef770ae377f` | Client supplied; photo subject and artwork permissions require confirmation | Apparel photo with service-family slogan |
| `FILE-005` | `Screenshot 2026-06-08 at 4.32.21 PM.png` | `PROJECT_DATA_ROOT\inputs\client-provided\2026-07-26\Screenshot 2026-06-08 at 4.32.21 PM.png` | PNG, 306×378 | 83,258 bytes; SHA-256 `0db0db2f2fc51db6edaf85299f2ef2e39b7e8bb0e2aa832c00108262254f7da3` | Client supplied; source layout ownership requires confirmation | Low-resolution audience and benefits crop |
| `FILE-006` | `MT Logo.PNG` | `PROJECT_DATA_ROOT\inputs\client-provided\2026-07-26\MT Logo.PNG` | PNG, 1024×1024 | 1,768,871 bytes; SHA-256 `bafb60b332d51623742a69ee7c693097ea0d89f81b3aad9077c1b7a10ac70d3a` | Client supplied; trademark and vector/source rights require confirmation | High-resolution raster logo on white background |
| `FILE-007` | `Screenshot 2026-06-08 at 4.34.44 PM.png` | `PROJECT_DATA_ROOT\inputs\client-provided\2026-07-26\Screenshot 2026-06-08 at 4.34.44 PM.png` | PNG, 216×212 | 37,429 bytes; SHA-256 `c178f56f304b12672b02b04c323a82b5467c01fa14795de76bc996401b083942` | Client supplied; source layout ownership requires confirmation | Very low-resolution “Why choose” crop |

## Decisions

| ID | Date | Decision | Authority | Affected artifacts |
|---|---|---|---|---|
| `DEC-001` | 2026-07-26 | Create `client` as a general reusable repository-intake and delivery-governance skill for AI-native digital product, solution, and consulting engagements. | Douglas | `.agents/skills/client`, `skills-manifest.json`, `DEL-004` |
| `DEC-002` | 2026-07-26 | Prepare four named Bitwarden Secrets Manager values for the two platform logins and require a reviewed injection broker before agent use. | Douglas | `ACCESS.md`, `.env.example`, `secret-manifest.json`, `secret-manifest.md`, `MAP.md`, `DEL-001` |

## Provenance gaps

- The legal entity name, current ownership descriptors, decision-maker names, and approved public contact set await client confirmation.
- The visible storefront uses OpenCart routes and Journal 3 assets. The installed versions, authenticated Journal controls, and Ecwid's current operational role remain unverified.
- Production access requires four values in a dedicated Bitwarden Secrets Manager project: `MT_UNIFORMS_WEBSITE_ADMIN_USERNAME`, `MT_UNIFORMS_WEBSITE_ADMIN_PASSWORD`, `MT_UNIFORMS_ECWID_ADMIN_USERNAME`, and `MT_UNIFORMS_ECWID_ADMIN_PASSWORD`. Their values remain outside this repository. The reviewed Secrets Manager-to-browser broker is still pending.
- Original vector/logo files, source design files, fonts, and usage rights have not been supplied.
- The supplied marketing claims have not been independently validated.
- No contract, proposal, approved scope, fees, delivery dates, or future-site acceptance criteria were supplied.
