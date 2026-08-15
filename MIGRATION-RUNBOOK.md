# Migration runbook — OpenCart to Shopify

The decision is **Shopify, Basic plan.** This is the sequence from the current OpenCart 3 store to a
live Shopify store, with the data offload already done and the parts that need Douglas marked.

Related: `SETUP.md` owns approvals and money · `CLOVER-SETUP.md` owns the POS side ·
`ACCESS.md` owns credentials · `theme/README.md` owns the storefront ·
`PLATFORM-RECOMMENDATION.md` and the Obsidian platform brief own why Shopify.

---

## Stage 0 — the offload, which is finished

Done on 2026-08-14. Nothing here needs repeating. The conversion below was last regenerated 2026-08-15.

| | |
|---|---|
| Database | 210 of 212 tables, 121,957 rows, ~37 MB |
| Images | 518 files, ~30 MB |
| Location | `%PROJECT_DATA_ROOT%\inputs\opencart-export\2026-08-14\` |
| Manifest | `README.md` in that folder, with SHA-256 checksums |

**How it was taken, in case it must be repeated.** OpenCart's own
`System → Maintenance → Backup / Restore` endpoint (`route=tool/backup/export`), driven from an
already-authenticated admin session, **one table per request**. A whole-database request returns
after seven tables and stops — that failure is preserved as `mt-00-partial-*.sql`. No credential was
entered, read, or stored.

Images are not in the database; it stores paths only. They were pulled separately from the public
`https://mtuniforms.com/image/<path>` route using the paths in `oc_product_image`, `oc_product`,
`oc_category`, and `oc_manufacturer`.

**Two tables did not export** — `oc_seo_analysis` and `oc_session`, both HTTP 500. Both are derived
or transient. Neither is needed.

**Ten image references are dead** — the database points at files that are not on the server. They
are already broken on the live site. Listed in the export README.

### If you need to re-run it

```bash
node ops/build-shopify-import.mjs
```

`ops/parse-opencart.mjs` reads the SQL dump directly rather than reconstructing a MySQL schema, so
re-running needs no database server and no credentials.

---

## Stage 1 — provision the store

1. Open the Shopify **Basic** plan. **Needs Douglas** — see `SETUP.md` item 2.
2. Set the store's country, currency (USD), weight unit (lb), and address.
3. Set the tax configuration to match `oc_tax_rate` and `oc_tax_rule` from the export — there are
   3 tax rates and 5 rules on the current store, and PA charges no sales tax on most apparel, which
   is a real distinction for a uniform retailer and must not be assumed away.
4. Upload `theme/` as a custom theme, or run it through the Shopify CLI.
5. Set `commerce_mode` to `shopify` in theme settings. It is already the committed default.

## Stage 2 — import the catalog

The generated import is at `%PROJECT_DATA_ROOT%\outputs\shopify-import\2026-08-15\`.

| File | What it is | How it gets in |
|---|---|---|
| `products.csv` | 407 products, 12,409 rows — 12,098 variants plus 311 image-only rows | **Native** — Products › Import |
| `redirects.csv` | 568 rows | **Native** — Navigation › URL Redirects |
| `customers.csv` | 2,212 rows | **Native** — Customers › Import, but see stage 3 |
| `reviews.csv` | 6 reviews, 5 of them five-star | A review app (Judge.me) |
| `orders.jsonl` | 1,154 real orders; 347 abandoned checkouts excluded | **No native route.** Admin API or a migration app |
| `line-item-properties.json` | The option groups that could not be variants, per product | Consumed by the theme |
| `report.json` | Every demotion decision, plus the defect lists below | Read it before importing |

Regenerate both halves with:

```bash
node ops/build-shopify-import.mjs
```

```bash
node ops/build-shopify-data.mjs
```

### Read `report.json` before you import

Four lists in it are the reason to open the file rather than trust the summary line:

- **`pricedDemotions` — 12 entries, and this one costs money.** A Shopify line-item property carries
  no price. Where a demoted option group had a surcharge, the customer picks it and is charged
  **nothing**: Hat Visor up to **$56.99**, Hat Band $18.99, Braid $10.00, and a group named "Option"
  at $16.00. Eight products are affected. Decide how each is priced before the catalog goes live —
  fold it into the base price, keep it as a variant at the cost of another group, or quote it at the
  counter. This is a business decision and no code change makes it go away.
- **`blankOptionValues` — 4 entries.** Four Elbeco shirts have a "Sleeve Length" value whose
  description row is missing from the export, so the label is empty. Shopify rejects a blank option
  value on import. Supply the four labels by hand.
- **`duplicateOptionLabels` — 2 entries.** Two boots list the same size twice, which Shopify reads
  as a duplicate variant. Remove the repeat.
- **`duplicateSkus` — must be 0.** Anything else means two physically different garments share a
  SKU and inventory cannot tell them apart.

**Weights are converted through the store's own `oc_weight_class` table**, not assumed. This catalog
mixes units — 265 products in pounds, 142 in ounces — and converting everything as pounds shipped
those 142 at 16× their real weight, which mispriced carrier-calculated shipping on every order
containing one. An unrecognised weight class now fails the build rather than guessing.

1. **Import `products.csv`** through Products → Import. Images pull from the live
   `mtuniforms.com` URLs, so **do not take the old site down until the import has finished.** That
   ordering constraint is easy to get wrong and expensive to undo.
2. Verify the count: 407 products, 327 active and 80 draft.
3. Spot-check the three worst products for variant correctness — Elbeco Tek3 Trousers, Elbeco
   Tex-Trop2 Trousers, and the W. Alboum Cushion Air 8-Point Cap.

### The limit that shapes the import

**Shopify allows three option groups per product. This catalog uses up to seven.** One pair of
trousers generates 6,120 combinations across Braid × Color × Waist × Length.

Nothing was truncated. Option groups that cannot be variants are demoted to **line-item
properties**, which Shopify carries onto the order line natively and which `theme/` already posts.
Ten products were demoted. The rule: groups that bear stock — size, colour, length, waist — stay
variants; braid, hat bands, hardware finish, and visors become properties.

**What you lose by demotion:** a property has no SKU, no stock count of its own, **and no price**.
The first two are fine for braid and hat bands, which are made to order anyway. The third is not
fine anywhere and is the thing to look at — `report.json` lists the 12 money-bearing demotions under
`pricedDemotions`. Review it and overrule anything that looks wrong before importing.

## Stage 3 — the things the import cannot carry

1. **Stock is all zeros.** OpenCart holds stock per *product*, not per option value, so 407 counts
   cannot be split across 12,098 variants without inventing numbers. Every variant imports at 0 with
   inventory policy `continue`, so nothing blocks a sale. The first real count comes from Clover or
   a manual export — see `CLOVER-SETUP.md`.
2. **Customers and orders are not migrated, and should not be by default.** 2,212 customers and
   1,154 real orders are personal data. Shopify can import customers, but that puts personal records
   into a new system and starts a new retention clock. Treat it as a separate decision with a
   business reason, not a default step of the migration.
3. **Decoration is not in the catalog at all.** Hemming, name tapes, patches, and embroidery are
   quoted at the counter and appear nowhere in the product data. This is the single biggest gap
   between what the store sells and what the website can express, and it is a design question before
   it is a migration one.

## Stage 4 — SEO, which is where migrations quietly fail

The export carries **1,099 SEO URLs**, 538 URL aliases, and 24 existing 301 redirects.

**Only half of those SEO URLs are the live site's.** This install runs a second storefront
(`store_id = 2`) which carries its own keyword for all 407 products, and **402 of the 407 differ**
from the live one — product 99 is `usps-baseball-cap-summer-pbcs` live and
`usps-letter-carrier-mailman-postal-baseball-cap-summer` on store 2. (This document said "26
products" until 2026-08-15, which was wrong by an order of magnitude and made the store-0 filter
look like a nicety rather than the thing the whole handle set depends on.) `redirects.csv` filters
to `store_id = 0`, which is why it holds 568 rows and not the 873 an unfiltered read produces. The
extra 305 would have been redirects from paths that were never live on mtuniforms.com.

The 568 breaks down as 407 products, 99 categories, 32 manufacturers, 6 information pages, and the
24 existing 301s. Categories were **silently dropped until 2026-08-15**: the builder branched on a
`path=` query kind that this export never emits — OpenCart 3 files category URLs under
`category_id=` — so `/police`, `/boots`, `/corrections` and 96 others were absent from a map whose
whole purpose is that they survive. The arithmetic was the tell: the old total of 469 is exactly
24 + 407 + 32 + 6, with the category branch contributing nothing.

1. Build a redirect map from `oc_seo_url` to the new Shopify handles. The handles in `products.csv`
   are taken from `oc_seo_url`, so **most products keep their exact URL path** — the map is mostly
   identity, and the exceptions are what matter.
2. Carry the 24 existing 301s forward.
3. `oc_seo_404_pages` holds **43,400 rows** of URLs that already 404 on the current site. Do not
   import that as redirects; mine it for the handful of high-traffic dead URLs worth catching.
4. Keep the 6 information pages (`oc_information`) — they are authored content.

## Stage 5 — cutover

1. Point DNS at Shopify. **Needs Douglas** — see `SETUP.md` item 4.
2. Keep the OpenCart install running, read-only, for at least 90 days. It is the only copy of order
   history that is not a SQL file, and `oc_offline_cc_data` must be dealt with before it is
   decommissioned rather than after.
3. Verify a real end-to-end purchase with a real card before announcing.

---

## Do this before any of it

`oc_offline_cc_data` holds **39 rows**. That is OpenCart's offline credit-card module, which stores
card details submitted through the storefront in the site's own database. The contents were not
read. This is a live cardholder-data exposure on the current site and it outranks the migration.
`SETUP.md` carries it as an approval item.
