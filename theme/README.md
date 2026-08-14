# M.T. Uniforms theme

A Shopify Liquid theme that does not assume Shopify.

## The portability contract

The theme never calls a commerce platform directly. Every cart action goes through
`assets/commerce-adapter.js`, which picks a driver at load time from `settings.commerce_mode`:

| Mode | Cart and checkout | Use it for |
|---|---|---|
| `shopify` | Shopify AJAX Cart API (`/cart/*.js`) | A live Shopify store |
| `ecwid` | `Ecwid.Cart` JS API | Ecwid embedded on the page |
| `local` | `localStorage`, checkout composes an order email | Previews, and any period before a platform is wired |

All three resolve the same cart shape, so `assets/theme.js` and every template are
platform-blind. Adding a platform means adding a driver and changing nothing else.

**The rule that keeps this true:** no template, section, or snippet may call a platform API. If you
find yourself reaching for one, it belongs in the adapter.

## Layout

```
layout/theme.liquid          Document shell; publishes window.MT_COMMERCE
sections/                    announcement-bar, header, home-hero, main-collection,
                             main-product, main-search, service-band, footer
snippets/                    product-card, product-options, cart-drawer
templates/                   index, collection, product, search, page, 404
assets/theme.css             Design tokens and the whole design system
assets/commerce-adapter.js   Platform drivers
assets/theme.js              Drawer, option choosing, validation, add-to-cart
config/settings_schema.json  Theme settings, including commerce_mode
```

## Two runtimes, one set of files

`../preview/build.mjs` renders these exact files with liquidjs, shimming the handful of Shopify
objects and filters the theme uses. That is deliberate: the client-facing prototype and the Shopify
theme are the same code, so they cannot drift apart while the platform decision is open.

```bash
cd ../preview && npm install && node build.mjs
```

## Design

Tokens mirror `../DESIGN.md` — navy `#0b1d34`, paper `#f3f2ee`, orange `#b8440c`, Archivo, 14px
radius, no gradients or decorative shadows. Light and dark are both defined; the palette lives on
bare `:root` and is redefined for dark, never the other way round.

## Notes for whoever wires this to a real platform

- The product form is `novalidate` on purpose. Chip-style options post through a hidden input, which
  browsers never validate, so leaving native validation on would give dropdowns one error style and
  chips another. `theme.js` validates every option group the same way instead.
- `money_with_sign` is used for option price deltas and is not a stock Shopify filter — it is
  provided by the preview renderer and must be defined on Shopify before launch.
- Decoration fields post as `properties[...]`, which Shopify carries onto the order line natively.
  Ecwid has no equivalent; under Ecwid they must be modelled as product options or captured
  elsewhere. This is the same gap the platform brief identifies.
