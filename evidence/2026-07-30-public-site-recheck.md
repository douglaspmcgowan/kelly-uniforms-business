# Public site recheck — 2026-07-30

Scope: live, read-only browser inspection performed while preparing the
temporary-notice plan. No credentials were entered, no cart item was added, and
no customer, inventory, order, configuration, or website state was changed.

## Storefront

- URL: `https://www.mtuniforms.com/`
- Page title: `Serving Police, Fire, EMS, Security, and USPS Customers`
- Requested text `New Website Coming!`: absent from the rendered page.
- The header displayed a public `M.T. Uniforms` logo loaded from
  `https://mtuniforms.com/image/cache/catalog/logo/mtlogo-299x82.png`; the
  rendered asset reported 299×82 pixels.
- Public assets continued to load from `catalog/view/theme/journal3`.
- Customer links continued to expose OpenCart route patterns, including
  `index.php?route=checkout/cart`, account, contact, sitemap, and product routes.
- No asset URL containing `ecwid` appeared among the rendered page's scripts,
  stylesheets, or iframes.

The missing Ecwid asset signal establishes only that Ecwid was not observed
rendering this storefront during this check. It does not determine whether Ecwid
has a back-office, synchronization, historical, or otherwise indirect role.

## Administration route

- URL: `https://www.mtuniforms.com/admin/`
- Page title: `Administration`
- Visible heading: `Please enter your login details.`
- Visible fields: `Username`, `Password`
- Visible platform link/brand: `OpenCart`
- No credentials were entered.

## Local logo and supplied assets

- The seven client-supplied raster assets remained present under
  `C:\Users\dougl\Data\Projects\kelly-uniforms-business\inputs\client-provided\2026-07-26`.
- `MT Logo.PNG` was opened successfully and is the 1024×1024 raster
  Maltese-cross logo recorded as `FILE-006`.
- Trademark clearance, public-reuse rights, and a vector/source logo remain
  unconfirmed.

## Official implementation references rechecked

- Journal Header Notice:
  `https://docs.journal-theme.com/docs/modules/header-notice`
- Journal Layouts and All layouts:
  `https://docs.journal-theme.com/docs/layouts`
- Journal Status and Admin Only:
  `https://docs.journal-theme.com/docs/options/status`
- Journal Import / Export:
  `https://docs.journal-theme.com/docs/system/import-export`

These references continued to support the conditional runbook. Authenticated
inspection must still verify that the installed Journal version exposes the
documented controls before any production edit.
