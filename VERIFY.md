# Verification

This file preserves the useful verification owner found in `origin/master` while updating it for the repository's current Work Scope state and brand-gallery deliverable. The retired `CURRENT-TASK.md`, `WORK_QUEUE.md`, and `STATUS.md` files from that history are intentionally not restored.

## Project and task state

```powershell
pwsh -NoProfile -File C:\Users\dougl\.agents\tools\Test-WorkState.ps1 -Root C:\Users\dougl\Projects\kelly-uniforms-business
pwsh -NoProfile -File C:\Users\dougl\.agents\tools\Reconcile-WorkState.ps1 -Root C:\Users\dougl\Projects\kelly-uniforms-business
pwsh -NoProfile -File C:\Users\dougl\.agents\tools\Test-TaskStateFormat.ps1 -Root C:\Users\dougl\Projects\kelly-uniforms-business
```

## Brand gallery

```powershell
Set-Location C:\Users\dougl\Projects\kelly-uniforms-business\brand-gallery
npm test
```

After a production deployment, verify the canonical URL returns HTTP 200, includes the `Quartermaster` recommendation, serves all three full-size direction boards and the self-hosted font, and contains no credential values or private recovery mechanics.

## Recovery packages

Run each acceptance command recorded in `.agents/work/state.json` through `Invoke-WorkScopeEvidence.ps1`. Do not substitute an ad hoc command for a recorded evidence gate.

## Secret and source scan

```powershell
C:\Users\dougl\Tools\gitleaks\gitleaks.exe dir --no-banner --redact C:\Users\dougl\Projects\kelly-uniforms-business
```

## Manual evidence

- Trace every `Confirmed` and `Observed` claim in `CLIENT.md` to `SOURCES.md`.
- Confirm every supplied request appears once in `DELIVERABLES.md`.
- Confirm active, verified, and delivered items define acceptance evidence.
- Confirm every data-root asset checksum matches `data-manifest.yaml`.
- Confirm administrative account identifiers and credential values remain outside tracked files.
- For browser-visible work, preserve desktop and mobile evidence and verify the published result.

## Storefront theme, preview, and operations database (added 2026-08-14)

Run from the repository root.

| What | Command | Passing looks like |
|---|---|---|
| Operations schema | `node ops/verify-db.mjs` | `8 checks passed` |
| Catalog data file | `MT_EXPORT_DIR=<dated export> node preview/make-catalog.mjs` | `[catalog] 321 products, 5 pages` |
| Theme renders | `cd preview && node build.mjs` | `321 products · 51 collections · 5 pages` |
| Deployed prototype | `curl -o /dev/null -w '%{http_code}' https://mt-uniforms-storefront-prototype.vercel.app/` | `200` |

Manual checks that the commands cannot make for you:

1. Open a product with required options, submit without choosing, and confirm one consistent error
   appears for both dropdown options and chip options. Native browser validation is switched off on
   purpose so these do not behave differently.
2. Add a decorated line to the cart and confirm the chosen options and the name-tape text both
   appear on the cart line.
3. Confirm the reorder screen in `ops/admin.mjs` distinguishes *never counted* from *out of stock*.
   Showing all 321 products as needing reorder is a regression, not a full shelf.

## OpenCart export and Shopify import — added 2026-08-14

```bash
node ops/build-shopify-import.mjs
```

Passing looks like: 407 products, 12,409 CSV rows (12,098 variant rows plus 311 image-only rows), 0 oversized, 0 without a handle, **0 duplicate
SKUs**. A changed product count means the export under
`%PROJECT_DATA_ROOT%\inputs\opencart-export\` was replaced; confirm that was intended before
trusting the output. Both build scripts print the export folder they resolved — check it is the one
you meant, since `exportDir()` takes the newest dated folder unless `MT_EXPORT_DIR` says otherwise.

```bash
node ops/build-shopify-data.mjs
```

Passing looks like: 2,212 customers, 1,154 orders with 347 abandoned excluded, 568 redirects, 6
reviews of which 5 are five-star, and 8 testimonials **excluded**. The testimonial count being
non-zero and excluded is the check, not a warning — those rows are Journal 3 Lorem Ipsum under
invented names and putting them on a real store would be fabricated praise.

**Two numbers that must never quietly grow.** `redirects` was 873 while the parser was reading both
storefronts out of `oc_seo_url`; only `store_id = 0` is live. If it returns to the 800s, the
store-id filter has been lost. `duplicateSkus` was 3 while product-level SKUs were copied onto every
variant row; any non-zero value means inventory can no longer tell two garments apart.

Manual checks, none of which a script can stand in for:

1. **The CSV parses as CSV.** Descriptions contain newlines, which are legal inside quoted fields
   and which a naive line-splitting check will report as thousands of malformed rows. Parse the
   whole file, not line by line. Expect 31 columns on every row.
2. **Descriptions are real HTML, not escaped text.** `Body (HTML)` should start with `<p>`, not
   `&lt;p&gt;`. OpenCart stores them entity-encoded and the parser decodes them.
3. **Demotions are still sensible.** Read `report.json`. Waist, length, and colour should be
   variants; braid, hat bands, and hardware finish should be properties. If a size or colour group
   has been demoted, the `STOCK_BEARING` pattern in `ops/build-shopify-import.mjs` needs a term.
4. **Nothing from the export is inside the repository.** `find . -name '*.sql'` should return only
   `ops/schema.sql`.

## Storefront regression checks — added 2026-08-14

Both were found by testing the built site rather than reading the source, and both would pass a
source review.

1. **Option surcharge labels must match what the cart charges.** On a product with a priced option
   (Elbeco Tek3 Trousers, braid `+$8.00`), confirm the label reads `+$8.00` and the resulting cart
   line is `6699` cents against a `5899` base. A label reading `+$0.08` means `price_delta` reached
   the money filter in dollars: every price the theme touches is cents, in `preview/build.mjs` and
   in `theme/assets/theme.js` alike.
2. **Every internal link must resolve, accounting for `cleanUrls`.** Crawl `preview/dist`, resolve
   each internal href against the file, `file + .html`, and `file/index.html`, and require zero
   unresolvable. Expect 51 collections. If it drops to 39, the shelf threshold in `build.mjs` has
   been applied to page generation again rather than to the shelf, and product breadcrumbs will
   point at pages that do not exist.

3. **The reviews band shows real reviews, and only real ones.** The homepage must render
   `section.reviews` with four cards, each linking to a product page that exists. Nothing in the
   storefront may read `oc_testimonial`: those eight rows are Journal 3 Lorem Ipsum under invented
   names, and a review card whose body reads like filler copy is the symptom. Grep the built site
   for a testimonial author name and expect zero hits.

   The count is 4 here and 5 in `reviews.csv` on purpose. The fifth is on a product outside the
   321-product public slice the preview carries; the full 407-product Shopify import includes it.

Re-verified 2026-08-15 against a fresh `preview/dist`: 381 pages, **9,926 internal `href`s, 0 unresolvable** (counting root-relative hrefs only, resolving each against the file, `file.html`, and `file/index.html`). Two documents used to give 10,684 and 10,689 for this, neither reproducible from a stated method; the method is stated here so the number can be checked. Validation, option
pricing, line merging, quantity, removal, empty state, and the mailto checkout all pass.

## Storefront regression checks — added 2026-08-15, from five review passes

Each of these is a defect that shipped and was caught by driving the built site. Each has a number
to check, because "looks fine" is what let them through the first time.

4. **No horizontal scroll at 375px, on every page type.** Measure `documentElement.scrollWidth`
   against `clientWidth` on home, collection, product, search, and an info page; they must be equal.
   They read 452 against 375 for a while, and the piece pushed off-screen was the **cart button —
   the only route to the cart on a phone**. Two independent causes, both the `min-width: auto`
   default on a grid or flex child: the search input, and the nav row.
5. **`.workbench` does not size itself to the category shelf.** At 1440 the document was 2733px
   wide and the product grid sprawled to ten columns with a dead gutter. `.shelf` has
   `overflow-x: auto` and it could not engage, because the `1fr` grid track would not shrink below
   its content. Expect `scrollWidth == clientWidth` and a four-column grid at 1440.
6. **`visually-hidden` must be defined in `theme.css`.** Three templates use it. When it is missing,
   the screen-reader label "Search the catalog" renders as visible body text in the header of every
   page — a grep for the class in the stylesheet is the whole check.
7. **Every option group a customer selects must reach the cart.** On
   `w-alboum-cushion-air-8-point-uniform-cap-ht8p`, select all seven groups and expect **seven**
   stored options. Two of its groups are both labelled "Option" (cap device, and band style), and
   keying the payload by legend text meant the second silently overwrote the first — the officer
   picked the police button, the price was right, and the shop received an order that never
   mentioned it. Six of seven is the failure signature.
8. **A malformed stored cart must not brick the button.** Set `mt-cart-v1` to
   `{"items":[],"total":0}` and confirm `get()` and `add()` resolve. This threw synchronously, ahead
   of any promise, so the `.catch` never fired and the customer saw no error at all — Add to order
   simply stopped working on every page until they cleared site data.
9. **The checkout link is inert on an empty cart, and never exceeds ~1,900 characters.**
   `checkoutUrl()` returns `''` when empty and the href is removed, because `aria-disabled` does not
   stop an `<a>` from activating. With 60 lines the URL must stay under the limit and say in the
   body how many lines did not fit, rather than being truncated by the mail client in silence.
10. **Search returns results.** `/search?q=hemming` must find the tailoring page; `?q=elbeco
    trousers` must return product cards. The prototype's search was dead end to end: the form's
    query was dropped by the `.html` → clean-URL redirect, and the generated `search-index.json` had
    no reader at all. This is preview-only scaffolding — on Shopify the page is server-rendered —
    so check it against the built preview, never as evidence about the real store.
