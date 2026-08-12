# mtuniforms.com architecture scope — 2026-07-31

Method: unauthenticated HTTPS GETs from this workstation plus one non-persisting
`checkout/cart/add` probe. No credentials were entered. No order, customer,
inventory, catalog, or configuration state was created or changed. Source ID:
`OBS-004`.

## 1. Stack

| Layer | Observed value | Evidence |
|---|---|---|
| Web server | `nginx/1.31.1` | `Server` response header on every route |
| Application | OpenCart | `OCSESSID` cookie, `index.php?route=` URL scheme, `/admin/` login page titled `Administration`, footer `OpenCart © 2009-2026` |
| Admin UI generation | OpenCart 2.x/3.x family | admin loads Bootstrap 3, Font Awesome, `jquery-2.1.1.min.js`, `bootstrap-datetimepicker`. Exact release requires an authenticated dashboard read. |
| Theme | Journal 3 | all storefront assets under `catalog/view/theme/journal3/`; admin also loads `view/javascript/journal3/assets/menu.css`, so the Journal admin extension is installed |
| Proxy cache | present but off | `X-Proxy-Cache: DISABLED` on every route |
| TLS/security headers | HSTS (duplicated), `X-Frame-Options: SAMEORIGIN`, `X-Content-Type-Options: nosniff` (duplicated), `X-XSS-Protection` | response headers; duplicate values indicate the header is set in two places (nginx and app/`.htaccess`-equivalent) |

Front-end libraries loaded on the storefront: jQuery 2.1.1, Bootstrap 3,
Modernizr, MasterSlider, Swiper, anime.js, hoverIntent, typeahead,
vanilla-lazyload, jquery.countdown, Journal's `cjs.js`.

## 2. What is NOT there

- **No Ecwid.** No Ecwid script, asset, iframe, or storefront URL on the home,
  category, contact, cart, or checkout routes. The Ecwid account is not
  rendering any part of the public site.
- **No analytics or tag manager.** No Google Analytics, GA4, GTM, Meta pixel, or
  any other measurement script. The business currently has zero web analytics.
- **No payment provider JavaScript** on public pages (PayPal, Stripe, Square,
  Authorize.net are all absent from the pages fetched). Payment method
  configuration is server-side and requires an authenticated read.
- **No consent management platform.** The cookie bar is Journal's own
  Notification module, not a GDPR/CCPA consent tool.

Third-party hosts referenced: `fonts.googleapis.com`, `fonts.gstatic.com`
(Montserrat, Roboto), `maps.google.com` (contact page), and Google reCAPTCHA
(contact form only).

## 3. Journal module inventory exposed publicly

Journal publishes its client-side config as `window['Journal']` in the page
source (76 keys). Relevant registrations:

- `headerNotice: [{ m: 56, c: "266c89c7" }]` — **a Header Notice module with ID
  56 already exists in this installation.** No `module-header_notice-56` markup
  rendered on the home page during this check, so module 56 is present but not
  currently displaying (disabled, unassigned, or filtered by status).
- `notification: [{ m: 137, c: "4f0f9264" }]` — the bottom cookie bar
  ("We use cookies and other similar technologies…", green **OK** button).
- `layoutNotice` — supported by the theme, none registered.
- Header: `headerType: classic`, `headerHeight: 100`, `headerTopBarHeight: 35`,
  mobile header engages at tablet width, mobile sticky header on.

Other module IDs visible in generated CSS: menus 3/13/14/72/75/76/77/240/291,
blocks 288/289/290, banners 259, products 27.

**This materially changes the runbook.** The existing plan says "create a new
Header Notice module." Module 56 must be inspected first — editing it or adding
a second one are different actions with different rollback paths.

## 4. Existing custom CSS in the theme

Journal's Custom CSS field is already in use. Live rules include:

- the mobile logo is replaced by a CSS background image
  (`image/catalog/logo/mtlogo-lg.png`) with the real `<img>` hidden;
- `module-banners-259` and `module-products-27` are hidden in specific grid slots;
- a mobile product-carousel width override at ≤480px.

Any Journal export/restore must preserve these.

## 5. Site structure

Catalog taxonomy (top level → children): Police, Fire-EMS, PA Constable,
Corrections, Security, Closeouts, Other Items, Postal (Vendor # 22973), Badges,
Equipment, Footwear, Headwear, Outerwear, Pants/Trousers, Rainwear, Shirts,
Gloves, Hi-Visibility Garments, Body Armor, Duty Gear, and related accessory
groups.

Information pages: About Us, Delivery, Privacy Policy, Terms & Conditions,
Contact, Returns, Site Map, Brands, Gift Voucher, Specials.

SEO: SEO-friendly URLs are on (`/6-boots`, `/about-us`). `robots.txt` dates from
2019-11-27 and disallows `/admin`, search, checkout, account, and all
sort/order/limit/page/filter parameters. `sitemap.xml` returns
`Content-Type: text/html` rather than XML. Organization JSON-LD is present.

## 6. Contact details currently published

- Contact page: `M.T. Uniforms, 525 Franklin St, Johnstown PA 15901`,
  telephone `814-536-2390`.
- No `mailto:` or `tel:` links anywhere on the home page; the phone is plain
  text, so it is not tappable on a phone.
- `800-535-0134` and `sales@mtuniforms.com` did **not** appear on the home or
  contact pages during this check. `CLIENT.md` records both from the 2026-07-26
  pass; that claim needs re-sourcing or retiring.
- Footer copyright reads `© Copyright 2011-2026 MT Uniforms`.

## 7. Cart behavior — probe result and leading hypothesis

The add-to-cart endpoint itself works. `POST index.php?route=checkout/cart/add`
with `product_id=142` and `product_id=637` each returned HTTP 200 with valid
JSON and correct server-side option validation:

```json
{"error":{"option":{"334":"Shoe Size required!","335":"Shoe Width required!"}},
 "redirect":"https://mtuniforms.com/rocky-tmc-5019-waterproof-boot",
 "options_popup":true}
```

Nothing was added to any cart; both probes stopped at validation.

### Host-split hypothesis (high confidence, not yet proven end-to-end)

1. `https://www.mtuniforms.com/` returns **200 and does not redirect** to the
   canonical host.
2. `https://mtuniforms.com/` also returns 200 independently.
3. Only the HTTP→HTTPS redirects exist (`http://…` → `https://…`, same host).
4. The page served at **www** declares `<base href="https://mtuniforms.com/">`
   and `<link rel="canonical" href="https://mtuniforms.com">` — both **non-www**.
5. `OCSESSID` is set **host-only** (`path=/; secure; SameSite=None`, no `Domain`
   attribute), so `www.mtuniforms.com` and `mtuniforms.com` hold **separate
   sessions and therefore separate carts**.
6. The `cart/add` JSON `redirect` target is the **non-www** host, so the options
   popup a customer must complete for footwear and most uniform items is fetched
   from the host their cart is *not* on.

A customer who arrives at `www` (the address on printed material, and what most
browsers autocomplete) gets a session on `www`, then has the theme resolve links
and the required-options popup against `mtuniforms.com`. Cart contents split
across the two hosts and the header cart counter disagrees with the cart page.
That reproduces the client's reported "cart link broken / connections failing"
symptom precisely.

Also observed: a single www home-page response returned **two different
`OCSESSID` Set-Cookie values** (`748217d5…` and `3405b53f…`), indicating session
regeneration or duplicated session handling per request.

The fix is a server/OpenCart configuration change — force one canonical host with
a 301 — not a theme edit. It belongs to `DEL-002`, not `DEL-001`.

### Not yet exercised

Completing an option-bearing add, a multi-item cart, a logged-in customer cart,
guest checkout, shipping/payment method selection, and any order placement.
Confirming the host-split end to end needs one option-complete add on `www`
followed by a cart read on both hosts.

## 8. Other issues found while scoping

- **Journal demo content is live in the main menu.** The mega menu renders
  "Create 0 Unlimited Menus", "More Menus", and "The Best Menu Options You Will
  Ever Find In a Theme" — unedited Journal placeholder copy visible to every
  customer.
- `sitemap.xml` serves `text/html`, so search engines are unlikely to parse it.
- `robots.txt` has not been touched since 2019.
- No analytics means no data on where ordering actually fails for real users.
- jQuery 2.1.1 (2014) and Bootstrap 3 are both end-of-life.

## 9. Open questions requiring authenticated access

1. Exact OpenCart and Journal versions, and their patch status.
2. What Header Notice module 56 currently contains and why it is not displaying.
3. Whether the website-admin account can modify Journal modules and layouts.
4. Configured store URL(s) and whether an SEO/canonical-host extension exists.
5. Configured payment and shipping methods, and whether any are failing.
6. Whether recent orders exist, and error-log contents.
7. Ecwid's actual role: standalone/abandoned, back-office catalog, or a channel.
