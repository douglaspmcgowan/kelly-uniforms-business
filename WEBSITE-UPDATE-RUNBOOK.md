# MT Uniforms temporary website notice

Last verified: 2026-07-30

## What controls the live site

The public storefront is OpenCart with the Journal 3 theme. Public page assets load from `catalog/view/theme/journal3`, customer routes use OpenCart route patterns, and the standard OpenCart administration login is live at:

<https://www.mtuniforms.com/admin/>

The likely notice control is in the OpenCart Journal 3 administration area. The supplied Ecwid account remains a separate system whose current operational role is unverified. No public evidence in this pass showed Ecwid rendering the visible storefront.

Sources: `WEB-001`, `WEB-002`, `WEB-003`, `OBS-001`.

The 2026-07-30 live, read-only recheck confirmed that the requested notice
remained absent, the public site continued to expose OpenCart routes and Journal
3 assets, and the OpenCart Administration login remained live. No rendered
Ecwid asset URL was observed. This does not rule out an indirect or back-office
Ecwid role. See `evidence/2026-07-30-public-site-recheck.md`.

## Resumption and authority

This runbook is the single detailed execution owner for `DEL-001`. Cross-agent
resumption starts from `.agents/work/state.json` through `Get-WorkResume.ps1`;
the generated `TASK.md` view exposes evidence-backed state for human readers.

Persisting this plan does not authorize a live website change. Before execution,
Douglas must:

1. confirm the order mailbox and phone line are ready;
2. confirm banner-only scope or explicitly expand the contact-change scope;
3. choose manual sign-in or the reviewed agent broker path; and
4. explicitly authorize the production edit.

The fastest safe one-time path is manual sign-in by Douglas or the client,
followed by execution through this runbook. Keep passwords out of chat,
repository files, screenshots, and logs.

## Recommended implementation to verify after login

Use Journal 3's built-in **Header Notice** module if authenticated inspection confirms that this installation exposes it. Journal documents this module as a top-of-store notice and allows it to be assigned as a Special Module across all layouts.

This approach:

- places the message above the existing header;
- avoids editing theme files, PHP, Twig, JavaScript, or CSS;
- can be previewed for administrators before public release;
- can be disabled quickly for rollback;
- is designed to avoid catalog and navigation edits; the preview checks below must verify that outcome on this installation.

Sources: `WEB-003`, `WEB-004`.

## Before editing

1. Confirm that `orders@mtuniforms.com` receives mail.
2. Confirm that `(814) 536-2390` reaches the intended order-taking line.
3. Open <https://www.mtuniforms.com/admin/>.
4. Choose the authorized login path:

   - **Manual update:** Douglas or the client signs in with the website/OpenCart administrator credentials.
   - **Agent-operated update:** use the reviewed Secrets Manager-to-browser broker after it is installed and verified. Keep credential values out of chat, repository files, and logs.

5. After login, verify all of the following before changing anything:

   - the dashboard identifies this as the production `mtuniforms.com` store;
   - a **Journal** menu is present;
   - **Journal → Modules → Header Notice** is available;
   - **Journal → Layouts** exposes **Special Modules** and **All Layouts**;
   - the signed-in user can modify those controls.

6. If any control differs, stop and record the installed OpenCart version, Journal version, visible menu path, and permission message. Revise this runbook from that authenticated evidence.
7. If the controls match, go to **Journal → System → Import / Export** and export the current Journal settings. Save the downloaded file with the date and time. Journal documents this export as a backup mechanism.
8. Record the active notice module name and its current status if an existing Header Notice will be edited.

Source: `WEB-005`.

## Create the notice

> **2026-07-31 correction.** A Header Notice module **already exists** in this
> installation. The public page source registers
> `headerNotice: [{m: 56, c: "266c89c7"}]`, though no `module-header_notice-56`
> markup rendered on the home page — so module 56 exists but is disabled,
> unassigned, or filtered by its status conditions. **Open module 56 first** and
> record its name, status, content, and layout assignment. Then decide whether to
> repurpose it or add a second module; a second visible Header Notice would stack
> two banners above the header. The same page source registers Notification
> module 137 (the bottom cookie bar) and shows existing Journal Custom CSS that
> any export/restore must preserve. Source: `OBS-004`.

1. Go to **Journal → Modules → Header Notice**.
2. Inspect module 56, then create a new module or edit 56 per the decision above.
   Keep any existing notice intact unless deliberately repurposing it.
3. Set **Module Name** to `MT Temporary Ordering Notice`.
4. Set **Status** to **Admin Only** for the preview.
5. Leave scheduling blank unless the client supplies explicit start and end times.
6. In the notice text field, enter:

   **New Website Coming! For all orders email orders@mtuniforms.com or call us directly at (814) 536-2390.**

7. Use the editor's link control to make:

   - `orders@mtuniforms.com` link to `mailto:orders@mtuniforms.com`
   - `(814) 536-2390` link to `tel:+18145362390`

   If the editor exposes an HTML/source mode, this is the equivalent minimal markup:

   ```html
   <strong>New Website Coming!</strong>
   For all orders email
   <a href="mailto:orders@mtuniforms.com">orders@mtuniforms.com</a>
   or call us directly at
   <a href="tel:+18145362390">(814) 536-2390</a>.
   ```

8. Use an existing high-contrast Journal style. Center the text, keep it readable on a phone, and avoid custom code.
9. Disable the close link if the module exposes that setting, so the continuity message remains visible while online ordering is unreliable.
10. Save the module.

Journal's documented Status control supports an **Admin Only** state for previews and separate device, customer, customer-group, and store conditions. Confirm that this installation exposes those controls. Source: `WEB-006`.

## Place it across the store

1. Go to **Journal → Layouts → Home**.
2. Open **Special Modules** in the upper-right area of the layout editor.
3. Under **All Layouts**, add `MT Temporary Ordering Notice` as a **Header Notice**.
4. Save the layout.

Using **All Layouts** is important: it carries the notice onto the home page, category pages, product pages, cart, and other storefront routes. Source: `WEB-003`, `WEB-004`.

## Preview

While the module is **Admin Only**:

1. Remain signed in to OpenCart administration.
2. Open the public storefront in another tab.
3. Verify the notice on:

   - <https://www.mtuniforms.com/>
   - one category page;
   - one product page;
   - <https://www.mtuniforms.com/index.php?route=checkout/cart>

4. Check desktop width and use an actual phone or browser mobile emulation with a mobile user agent. Journal warns that resizing a desktop window alone does not test device-specific module status.
5. Confirm the notice is the first customer-facing content above the normal header.
6. Confirm the email link opens a draft addressed to `orders@mtuniforms.com`.
7. Confirm the telephone link targets `+18145362390`.
8. Confirm navigation, search, login, and cart links remain usable.

## Publish

1. Return to **Journal → Modules → Header Notice**.
2. Open `MT Temporary Ordering Notice`.
3. Change **Status** from **Admin Only** to enabled globally.
4. Confirm it is enabled for:

   - desktop, tablet, and phone;
   - guests and signed-in customers;
   - the production MT Uniforms store.

5. Save.
6. If the module was previously closed during testing, use its **Reset Cookie** control so it appears again.
7. Open a private browsing window and repeat the desktop check plus the actual-phone or mobile-user-agent check.

Header Notice is cookie-based and Journal provides a Reset Cookie control. Source: `WEB-003`.

## Rollback

If the notice disrupts the header or navigation:

1. Go to **Journal → Modules → Header Notice**.
2. Disable `MT Temporary Ordering Notice`.
3. Save.
4. Verify the public home, category, product, and cart pages again.

If disabling the module does not remove it, remove its assignment from **Journal → Layouts → Home → Special Modules → All Layouts**, save, and verify again.

Keep the exported Journal settings as a supplemental configuration snapshot. Confirm that the download is non-empty and preserve it securely. Do not import that snapshot into production as a rollback step until its contents and restore behavior have been tested separately.

## Current cart observation

The direct cart route loaded successfully with an empty-cart message during the 2026-07-26 public check. This does not reproduce the client's reported failure, which may occur after adding a product, during checkout, on a particular device, or through another link. No cart state, customer data, inventory, or order was changed during this check.

Source: `OBS-002`.

The 2026-07-31 scope went further. `POST index.php?route=checkout/cart/add` works
and returns correct server-side option validation, so the endpoint itself is not
broken. The leading root-cause hypothesis was a **www/non-www host split**:
`https://www.mtuniforms.com/` serves 200 without redirecting, yet declares
`<base href="https://mtuniforms.com/">` and a non-www canonical, while `OCSESSID`
is set host-only — so the two hosts hold separate carts, and the required-options
popup is fetched from the host the customer's cart is not on.

The option-complete 2026-08-12 reproduction confirmed it. A successful add on
`www` generated a bare-host cart link; the product remained in the `www` cart
and was absent from the bare-host cart, with separate host-scoped `OCSESSID`
cookies. No cookie values were retained. That is a
server/OpenCart configuration fix, not a theme edit, and it belongs to `DEL-002`,
not this runbook. Source: `OBS-004`,
`OBS-006`, `evidence/2026-07-31-site-architecture-scope.md`, and
`evidence/2026-08-12-public-cart-host-session-split.md`.

## Logo and asset boundary

The notice does not require a logo change. The following assets are available
for later, separately authorized work:

- client-supplied `MT Logo.PNG`, a 1024×1024 raster logo under the declared
  project data root;
- six additional client-supplied raster marketing/image assets; and
- the current public header's cached 299×82 logo asset.

Trademark clearance, public-reuse rights, and vector/source originals remain
unconfirmed. Do not replace the live logo or publish supplied assets as part of
`DEL-001`.

## Source links

- Journal 3 Header Notice: <https://docs.journal-theme.com/docs/modules/header-notice>
- Journal 3 Layouts: <https://docs.journal-theme.com/docs/layouts>
- Journal 3 module status controls: <https://docs.journal-theme.com/docs/options/status>
- Journal 3 mobile workflow: <https://docs.journal-theme.com/docs/workflow/mobile-workflow>
- Journal 3 import/export backup: <https://docs.journal-theme.com/docs/system/import-export>
- OpenCart documentation: <https://docs.opencart.com/>
