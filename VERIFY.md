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
| Theme renders | `cd preview && node build.mjs` | `321 products · 39 collections · 5 pages` |
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

Passing looks like: 407 products, 12,409 CSV rows, 0 oversized, 0 without a handle. A changed
product count means the export under `%PROJECT_DATA_ROOT%\inputs\opencart-export\2026-08-14\` was
replaced; confirm that was intended before trusting the output.

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

Verified 2026-08-14 against production: 10,684 internal links, 0 unresolvable; validation, option
pricing, line merging, quantity, removal, empty state, and the mailto checkout all pass.
