# Public site observation — 2026-07-26

Scope: read-only public inspection. No credentials were entered, no cart item was added, and no customer, inventory, or order state was changed.

## Storefront

- URL: `https://www.mtuniforms.com/`
- Page title: `Serving Police, Fire, EMS, Security, and USPS Customers`
- Requested temporary notice: absent from the visible DOM snapshot.
- Customer routes use OpenCart patterns, including `index.php?route=checkout/cart`, `index.php?route=account/wishlist`, and `index.php?route=information/contact`.
- Public script assets include:
  - `catalog/view/theme/journal3/lib/modernizr/modernizr-custom.js`
  - `catalog/view/theme/journal3/lib/jquery/jquery-2.1.1.min.js`
  - `catalog/view/javascript/common.js`
  - `catalog/view/theme/journal3/js/common.js`
  - `catalog/view/theme/journal3/js/journal.js`
- Public stylesheet assets include:
  - `catalog/view/theme/journal3/icons/style.minimal.css`
  - `catalog/view/theme/journal3/stylesheet/style.css`

These observations establish OpenCart routes and Journal 3 storefront assets. They do not establish the installed OpenCart or Journal version, enabled administration modules, user permissions, or Ecwid's back-office role.

## Administration route

- URL: `https://www.mtuniforms.com/admin/`
- Page title: `Administration`
- Visible heading: `Please enter your login details.`
- Visible fields: `Username`, `Password`
- Visible brand/link: `OpenCart`
- No credentials were entered.

## Cart route

- URL: `https://www.mtuniforms.com/index.php?route=checkout/cart`
- Page title: `Shopping Cart`
- Visible state: `Your shopping cart is empty!`

This confirms only that the empty-cart destination loaded. It does not exercise add-to-cart, checkout, payment, session persistence, or the client's exact failure path.

## Official implementation references

- Journal Header Notice: `https://docs.journal-theme.com/docs/modules/header-notice`
- Journal Layouts: `https://docs.journal-theme.com/docs/layouts`
- Journal Status controls: `https://docs.journal-theme.com/docs/options/status`
- Journal Mobile Workflow: `https://docs.journal-theme.com/docs/workflow/mobile-workflow`
- Journal Import / Export: `https://docs.journal-theme.com/docs/system/import-export`
