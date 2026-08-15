# Setup — what only Douglas can do

Everything an agent cannot do for itself: approvals, purchases, sign-ups, and the manual steps that
gate the next phase. Credentials and login mechanics stay in `ACCESS.md`; this file owns decisions,
money, and physical actions.

The procedures live next door and this file does not repeat them:

- **`MIGRATION-RUNBOOK.md`** — OpenCart to Shopify, stage by stage. The data offload is done.
- **`CLOVER-SETUP.md`** — the POS side, and the ownership question the whole integration hangs on.
- **`ACCESS.md`** — credentials, value-free.
- **`theme/README.md`** — the storefront and its portability contract.
- **`ops/README.md`** — the operations database.

Updated 2026-08-14, after the full OpenCart export.

---

## 1. Cardholder data is sitting in the current site's database

`oc_offline_cc_data` holds **39 rows**. That is OpenCart's offline credit-card module, which stores
card details submitted through the storefront in the site's own database.

**No value in that table was read.** Everything below comes from column names and value *shapes* —
lengths, uniqueness, and character classes — which answer the question without exposing anything.

### What is actually in there

| Field | Finding | Reading |
|---|---|---|
| `cc_number` | 39 values, uniform 45 characters, only 14% digits | **Encrypted or encoded, not a plaintext card number.** A plaintext PAN would be 15–16 characters and ~100% digits. |
| `cc_cvv` | **One distinct value across all 39 rows** | **CVV is not retained.** A constant is a placeholder, not 39 security codes. This is the single most important finding. |
| `cc_name` | 30 distinct values, plain text | Cardholder names, in the clear. |
| `cc_exp` | 24 distinct values, `MM/YY` shaped | Expiry dates, in the clear. |
| `cc_postcode` | 25 distinct values, mostly digits | Billing postcodes, in the clear. |

### How old, and why that matters

The 39 rows reference order IDs **1836–2906**. The surviving `oc_order` table starts at ID **3844**,
dated **2021-07-24**. Not one of those 39 orders still exists.

**These are orphaned records.** The orders were deleted years ago and the card data was left behind
— it has outlived the transactions it belonged to by at least five years, which is the part that
makes it a retention problem rather than an operational one.

### What this means

It is **materially better than the worst case**: no CVV retention and no plaintext card numbers.
It is still a real problem: personal data with no business purpose, retained indefinitely, and the
encryption is OpenCart's own with the key in `config.php` on the same server — so anyone who can
read the database can very likely also read the key.

**Action, in order:**

1. **Purge the 39 rows.** They belong to orders that no longer exist. Nothing references them.
2. **Disable the offline credit-card payment module** so no more accumulate.
3. **Confirm the module is not still live on the storefront** before the Shopify cutover.

A disclosure conversation with the merchant services provider is the cautious call given cardholder
names and expiry dates were stored in the clear, but the absence of CVV and plaintext PANs means
this is very likely a retention and hygiene finding rather than a reportable breach. **Neither I nor
this document is the right authority on that** — if the answer matters, it is a question for the
processor or a QSA, not an inference from column shapes.

## 2. The OpenCart admin password you pasted is still burned

You pasted it into chat on a prior session. It is in a transcript on disk and must be treated as
compromised regardless of it being temporary.

**Action:** change the `AdminB` password at <https://www.mtuniforms.com/admin/> and do not send the
new one anywhere. Nothing depends on that account staying as it was — the export is finished.

`ACCESS.md` carries a "CREDENTIAL ROTATION REQUIRED" section from an identical earlier incident.
This is the second occurrence.

---

## 3. Approvals needed

Numbered so you can reply with just the numbers you approve.

| # | What | Why it is blocked | Cost |
|---|---|---|---|
| 0a | **Purge the 39 `oc_offline_cc_data` rows** | Section 1. Cardholder names, expiry dates and billing postcodes are stored in the clear on the live site, orphaned from orders deleted years ago. This is the highest-severity item in the project and it outranks the migration. | Free, needs your admin login |
| 0b | **Disable the offline credit-card module, then confirm it is not still live on the storefront** | Without this the table refills. The confirmation is a separate step from the disable and must happen before cutover. | Free |
| 1 | ~~Pick the platform~~ | **Ruled 2026-08-14: Shopify, Basic plan.** | — |
| 2 | Open the **Shopify Basic** plan and grant store access | Nothing can be imported, and no real cart or checkout can be tested, without a store | $39/mo |
| 3 | Confirm **DNS control** for the cutover | Cannot cut over or test the checkout domain without it | Existing domain, $0 |
| 4 | Confirm the **Clover merchant account** permits API access | The whole integration design is unverifiable until the account's tier is known. See `CLOVER-SETUP.md` stage 1. | Free, needs your merchant login |
| 5 | Decide whether the client sees the **prototype URL** | It is live and reads as a real store. It should not reach the client's customers by accident. | Decision only |
| 6 | **Push the branch.** Send `[allow-push]` or run the command below | Committed locally through `fc8df6d` on `codex/mt-uniforms-storefront`; Gitleaks clean. The tag expires with the turn it was sent in. | Free |
| 7 | Decide whether **customers and orders** migrate at all | 2,212 customers and 1,154 real orders are personal data. Moving them starts a new retention clock in a new system and needs a business reason, not a default. | Decision only |
| 8a | Decide whether the **prototype may publish real customers' names** | The reviews band republishes Richard Kidd's and Shane Fryer's names and words under a Vercel domain. They are already public on mtuniforms.com, so this is not an exposure — but republishing named individuals on a different domain is a fresh processing decision the client never made, and it is now in Git history. Relates to item 5. | Decision only |
| 8b | Decide how **12 priced option groups** get charged | Shopify's line-item properties carry no price. Twelve demoted groups across nine products have surcharges — Hat Visor up to **$56.99**, Hat Band $18.99, Braid $10.00. As imported, the customer picks them and is charged $0. See below. | Decision only, but it is revenue |
| 9 | Decide what happens to the **reviews band** | All four reviews are from **two people on one day, 2014-07-08**, and every one is about a patch or a tie bar rather than duty gear — under a heading claiming they are from "the people who wear this gear to work". Five separate review passes independently flagged it as reading manufactured. Three ways out: widen the set from the real export, date it honestly ("Reviews from mtuniforms.com, 2014–present"), or pull the band until there are current reviews. | Decision only |
| 10 | Decide whether the storefront keeps its **dark mode** | A `prefers-color-scheme: dark` block ships that no design document owns, and it is half-done: product photography keeps white backgrounds and floats as bright squares, the announcement bar stays full-brightness orange, and orange on dark paper measures **3.35:1** — a contrast failure for the stars, error text, and focus outline. Roughly half of visitors on default OS settings see this rather than the approved light world. My recommendation is to delete it; designing it properly is real work. | Decision only |
| 11 | Decide whether the order form collects a **PO number** | `/pages/departments` promises "send the PO number with the order and we bill the agency directly", and the order the site generates has no field for one. It is the single field a quartermaster's business office requires. Either add it, or stop promising it. | Decision only |
| 12 | Decide the fate of the **`mailto:` checkout** | Every review pass reached the same wall: there is no order page, no confirmation, no reference number, and the message lands in the *customer's* outbox — the store gets nothing unless they press send. A 60-line agency order does not fit in a `mailto:` at all; it is now capped and says so, which is honest rather than good. The 20-officers-one-invoice job cannot be done on this site. A posting form with a confirmation page is the fix and it is scope. | Decision, and it is the biggest one |

```bash
git -C C:/Users/dougl/Projects/kelly-uniforms-business push origin codex/mt-uniforms-storefront
```

---

## 4. Purchases

No money has been spent. Nothing below is committed until you say so.

| Item | When it is needed | Cost |
|---|---|---|
| Shopify Basic | To import the catalog and test a real checkout | $39/mo |
| Vercel | Free tier, sufficient for the prototype | $0 |
| Domain | Already owned | $0 |
| Theme or app purchases | None planned; the theme is ours | $0 |

The Ecwid-via-Clover pricing note that used to sit here is retired — Shopify is the decision.

---

## 5. Manual steps

1. **Stock counts.** Every one of the 12,098 Shopify variants imports at 0, because OpenCart holds
   stock per product and those 407 counts cannot be split across variants without inventing
   numbers. Export inventory from Clover, or count by hand, and say which. `CLOVER-SETUP.md` stage 2.
2. **Product photography.** Every product has a primary image; **236 of the 407 also have a gallery**
   (316 additional images in `oc_product_image`), so 171 products have a single photo and nothing
   else. Several categories reuse the same photo across different items, and 10 image references are
   already dead on the live site. This item read "407 products have one image each and no gallery"
   until 2026-08-15, which was wrong — over half the catalog has more photography than that claimed.
3. **The 80 disabled products.** The admin holds 407; 327 are active. Someone who knows the business
   has to say whether the other 80 are dead or seasonal. They import as drafts, which is safe either
   way.
4. **Decoration pricing.** Hemming, name tapes, patches, and embroidery appear nowhere in the
   product data and are quoted at the counter. This is the largest gap between what the store sells
   and what any website can express.
5. **The twelve priced option groups (approval item 8).** Shopify allows three option groups per
   product; this catalog uses up to seven, and the surplus is demoted to line-item properties, which
   carry the customer's choice onto the order but carry **no money**. Twelve demoted groups have a
   real surcharge:

   | Product | Option | Up to |
   |---|---|---|
   | W. Alboum Cushion Air 8-Point / Round Top / Pershing caps | Hat Visor | **$56.99** |
   | The same three caps | Hat Band | $18.99 |
   | Elbeco dress coats (3) | "Option" | $16.00 |
   | Elbeco Tek3 and Tex-Trop2 trousers | Braid | $10.00 |

   Three ways out, and it is your call which: fold the surcharge into the base price, keep the group
   as a variant and demote something else instead, or leave it as a property and quote it at the
   counter the way decoration already is. Doing nothing means selling a $56.99 visor for $0.
   `report.json` lists all twelve under `pricedDemotions`.
6. **192 of 321 product descriptions carry Microsoft Word paste markup** — `mso-` styles, `<o:p>`
   tags, Windows font stacks. It renders acceptably today and imports fine, so this is cleanup
   rather than a blocker. One of them (`usps-retail-clerk-unisex-eagle-logo-cardigan-sweater-pswcc`)
   embeds a `file:///C:\DOCUME~1\...` image path from whoever's desktop wrote it — that image is
   broken on the live site right now and will be broken on Shopify. It is the only unresolvable
   link in the prototype, across 9,926 internal links on 381 pages.
7. **Four blank option labels and two duplicated sizes.** Four Elbeco shirts have a "Sleeve Length"
   value whose description row is missing from the export; two boots list the same size twice.
   Shopify rejects both on import. They need four labels typed in and two duplicates removed.
8. **Twenty-two option groups are labelled literally "Option".** Two of them sit on the same
   W. Alboum cap — one is *P Button / FD Button*, the police-versus-fire cap device, and the other
   is band style. The customer is told a choice is required without being told what it is about, and
   the validation message reads "Choose option first." on a page with seven groups. The code no
   longer loses the second one, but only the person who knows the business can name them.
9. **Six products advertise a price no configuration can reach**, because a required group has no
   zero-cost choice. The W. Alboum Round Top cap shows **$59.99** and cannot be built below
   **$116.98** — a forced $56.99 visor. Also the Pershing cap, the Fire Dept. Bell Crown cap, the
   Elbeco Double Breasted Dress Coat, the Pro Style Public Safety Vest, and the Mini Mag Holder.
   Either add a zero-cost default to those groups or display "from $116.98"; a quartermaster
   budgeting twenty caps off the listed price is $1,140 short.
10. **The department collections are nearly empty, and Fire/EMS is missing entirely.** Police holds
    4 items, Corrections 3, Security 7, out of 321 — the Elbeco cargo trousers an officer would
    actually buy are in none of them. A `fire-ems` collection exists with **1 item** and is linked
    from nowhere, while the homepage headline promises "police, fire, EMS, corrections, constables,
    and postal carriers". Products need tagging to departments, or the rail should be dropped.
11. **Two content gaps the client has to fill.** `/pages/contact` gives no street address for a shop
    whose pitch is walking in for a fitting, and `/pages/sizing` says "the numbers below get you
    close" above no numbers at all — there is no size table on the page.

---

## 6. Open questions

1. **Who owns the product record — the website or Clover?** The single decisive question for the
   architecture, and a business one rather than a technical preference. `CLOVER-SETUP.md` opens with it.
2. **How is decoration priced today?** A price list, or quoted per job?
3. **Do agencies need self-service, or does the counter want a better ticket?** `INTENT.md` holds
   the agency portal as a deliberate second phase; nothing observed establishes it as a requirement.
4. **What deadline actually matters** — the client demo, a season, or the point where the current
   site stops being maintainable?
5. ~~Is there an eBay channel in use?~~ **Answered 2026-08-14: no.** All 19 `oc_ebay_*` tables are
   empty. The extension was installed and never used.

New, from the export: **17,526 real customer search queries** sit in `oc_customer_search` and
nothing has looked at them. That is the best available evidence of what people come to this site
looking for, and it should inform the category structure before the Shopify store is built out.

---

## 7. What is done and needs nothing from you

- **Full OpenCart export**, 2026-08-14 — 210 of 212 tables, 121,957 rows, plus 518 images.
  ~67 MB under `%PROJECT_DATA_ROOT%\inputs\opencart-export\2026-08-14\`, with a manifest and
  checksums. Outside Git, because it holds real customer PII and admin password hashes.
- **The whole Shopify conversion**, generated and validated 2026-08-15, at
  `%PROJECT_DATA_ROOT%\outputs\shopify-import\2026-08-15\` — 407 products across 12,409 CSV rows (12,098 variants plus 311 image-only rows), 2,212
  customers, 1,154 orders, 568 redirects, and 6 reviews. Three defects found and fixed in the same
  pass: ounce-weighted products were converting at 16× their real weight, product handles were being
  taken from a second storefront that is not the live one, and one product-level SKU was repeating
  across every variant of that product.
- **A five-star review showcase on the storefront** — real, approved reviews from the current site,
  built as theme-editor blocks so it works identically on Shopify and in the preview. Journal 3's
  eight demo testimonials are excluded by construction and verified absent from the built site.
- **Live prototype:** <https://mt-uniforms-storefront-prototype.vercel.app/> — working cart and
  option selection. Checkout hands the order to the store by email, because no payment rail is
  wired and pretending otherwise would be worse than saying so.
- **Portable theme** in `theme/` — real Shopify Liquid, already set to `commerce_mode: shopify`.
- **Operations database** in `ops/` — catalog, agencies, orders, decoration queue, stock movements.
