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
card details submitted through the storefront in the site's own database. The contents were not
read and will not be.

This outranks everything else on this page, including the migration.

**Action:** establish what is in those rows and for how long it has been there, then purge them and
disable the offline credit-card module. If real card numbers are stored, this is a PCI matter and
the card processor's disclosure requirements apply — that is a conversation with the merchant
services provider, not a code change.

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
| 1 | ~~Pick the platform~~ | **Ruled 2026-08-14: Shopify, Basic plan.** | — |
| 2 | Open the **Shopify Basic** plan and grant store access | Nothing can be imported, and no real cart or checkout can be tested, without a store | $39/mo |
| 3 | Confirm **DNS control** for the cutover | Cannot cut over or test the checkout domain without it | Existing domain, $0 |
| 4 | Confirm the **Clover merchant account** permits API access | The whole integration design is unverifiable until the account's tier is known. See `CLOVER-SETUP.md` stage 1. | Free, needs your merchant login |
| 5 | Decide whether the client sees the **prototype URL** | It is live and reads as a real store. It should not reach the client's customers by accident. | Decision only |
| 6 | **Push the branch.** Send `[allow-push]` or run the command below | Committed locally through `fc8df6d` on `codex/mt-uniforms-storefront`; Gitleaks clean. The tag expires with the turn it was sent in. | Free |
| 7 | Decide whether **customers and orders** migrate at all | 2,212 customers and 1,501 orders are real personal data. Moving them starts a new retention clock in a new system and needs a business reason, not a default. | Decision only |

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

1. **Stock counts.** Every one of the 12,409 Shopify variants imports at 0, because OpenCart holds
   stock per product and those 407 counts cannot be split across variants without inventing
   numbers. Export inventory from Clover, or count by hand, and say which. `CLOVER-SETUP.md` stage 2.
2. **Product photography.** 407 products have one image each and no gallery, and several categories
   reuse the same photo across different items. 10 image references are already dead on the live
   site.
3. **The 80 disabled products.** The admin holds 407; 327 are active. Someone who knows the business
   has to say whether the other 80 are dead or seasonal. They import as drafts, which is safe either
   way.
4. **Decoration pricing.** Hemming, name tapes, patches, and embroidery appear nowhere in the
   product data and are quoted at the counter. This is the largest gap between what the store sells
   and what any website can express.

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
- **Shopify import**, generated — 407 products, 12,409 rows, validated.
  `%PROJECT_DATA_ROOT%\outputs\shopify-import\2026-08-14\`.
- **Live prototype:** <https://mt-uniforms-storefront-prototype.vercel.app/> — working cart and
  option selection. Checkout hands the order to the store by email, because no payment rail is
  wired and pretending otherwise would be worse than saying so.
- **Portable theme** in `theme/` — real Shopify Liquid, already set to `commerce_mode: shopify`.
- **Operations database** in `ops/` — catalog, agencies, orders, decoration queue, stock movements.
