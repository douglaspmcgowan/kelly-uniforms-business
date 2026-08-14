# Setup — what only Douglas can do

Everything an agent cannot do for itself: approvals, purchases, sign-ups, and the handful of manual
steps that gate the next phase of work. Credentials and login mechanics stay in `ACCESS.md`; this
file owns decisions, money, and physical actions.

Written 2026-08-14 at the end of the overnight build run.

---

## 1. Do this first — the password you pasted is burned

You pasted the OpenCart admin password into chat. It is now in the session transcript on disk, so
it must be treated as compromised regardless of it being temporary.

**Action:** change the `AdminB` password at <https://www.mtuniforms.com/admin/>, and do not send the
new one anywhere. Nothing in the build depends on that account staying as it was — the catalog
extraction is finished and used the authenticated session you were already signed into, then
completed against the public storefront.

`ACCESS.md` already carries a "CREDENTIAL ROTATION REQUIRED" section from an identical earlier
incident. This is the second occurrence; the standing rule is that credential values never enter
chat, the repository, terminal output, or logs.

---

## 2. Approvals needed before further work

Numbered so you can reply with just the numbers you approve.

| # | What | Why it is blocked | Cost |
|---|---|---|---|
| 1 | Pick the platform: **Shopify**, **Ecwid**, or **custom** | Everything downstream — theme wiring, POS sync design, migration order — forks here. The brief in Obsidian lays out the tradeoffs. | Decision only |
| 2 | Open a **Shopify** trial and give the agent store access | Cannot test the theme against a real Shopify store, real money format, or the AJAX cart without one. | Free for the trial; $39–$105/mo after |
| 3 | Or: install **Ecwid via the Clover App Market**, not via ecwid.com | Same integration, materially different price — see the note below. | $29/mo via Clover vs $119–149/mo direct |
| 4 | Buy/confirm the **domain and DNS control** for the new storefront | Cannot cut over without it, and cannot test the checkout domain. | Existing domain, no new cost |
| 5 | Confirm the **Clover merchant account** can grant API access | The middleware design is unverifiable until we know what the account is allowed to do. | Free, but needs your merchant login |
| 6 | Decide whether the client sees the **prototype URL** tomorrow | It is live now and reads as a real store. It should not reach the client's customers by accident. | Decision only |

**On item 3 — the Ecwid pricing gap is real and worth checking before paying.** The same Ecwid
storefront with the same Clover integration is listed at roughly $29/month through the Clover App
Market and roughly $119–149/month through ecwid.com directly. Verify current pricing on both
surfaces before subscribing to either; do not sign up on ecwid.com first.

---

## 3. Purchases — nothing has been bought

No money has been spent. Nothing below is committed until you say so.

| Item | When it is needed | Rough cost |
|---|---|---|
| Shopify plan | Only if item 1 lands on Shopify | $39/mo Basic, $105/mo Grow |
| Ecwid plan (via Clover) | Only if item 1 lands on Ecwid | ~$29/mo |
| Vercel | Already on the free tier and sufficient for the prototype | $0 |
| Domain | Already owned | $0 |
| Theme/app purchases | None planned; the theme is ours | $0 |

---

## 4. Manual steps you will have to do by hand

1. **Stock counts.** The database has all 321 products but zero real inventory counts, because the
   public catalog does not publish them. Until a count lands, the reorder screen deliberately shows
   nothing rather than showing all 321 products as out of stock. Either export inventory from the
   OpenCart admin, or pull it from Clover, and tell the agent which.
2. **Orders and customers were not extracted.** 1,154 orders and 2,212 customer records are in the
   old system. They are real personal data, they were not touched, and moving them needs a
   deliberate decision about where they live and who may read them.
3. **Product photography.** 321 products have exactly one image each and no gallery. Several
   categories reuse the same photo across different items.
4. **Disabled products.** The admin holds 407 products; 321 are publicly visible. The other 86 are
   switched off. Someone who knows the business has to say whether they are dead or seasonal.

---

## 5. Open questions

Answers change what gets built next; none of them block the demo.

1. **Who owns the product record — the website or Clover?** This is the single decisive question
   for the whole architecture and it is not a technical preference. If Clover owns it, the catalog
   is limited to what Clover's option model can express. If the website owns it, Clover receives
   sales but does not constrain the catalog.
2. **How does decoration get priced today?** The site cannot express it at all, so hemming, name
   tapes, and patch work happen off-catalog. Is there a price list, or is it quoted per job?
3. **Do agencies actually need self-service, or does the counter want a better ticket?** Per-officer
   allowances and agency portals keep coming up. `INTENT.md` holds them as a deliberate second
   phase, and nothing observed so far establishes them as a requirement.
4. **What is the deadline that actually matters** — the client demo, a season, or the point where
   the current site stops being maintainable?
5. **Is there an eBay channel in use?** The old database carries `oc_ebay_*` tables, which means an
   eBay sales-channel extension was installed at some point. It is documented nowhere in this
   project and nobody has mentioned it.

---

## 6. A goal command for the next run

Once you have answered item 1 above, this is a run that can go unattended:

```
/goal Platform is <shopify|ecwid>. Wire the theme in theme/ to it for real: create the store,
import the 321 products from the extracted catalog with their option groups intact, verify a real
add-to-cart and a real checkout end to end, and report anything the platform cannot express.
Then map the Clover sync: what syncs, in which direction, and what breaks when the two disagree.
Do not migrate orders or customers. Put anything needing my approval or money in SETUP.md.
[allow-push]
```

---

## 7. What is already done and needs nothing from you

- **Live prototype:** <https://mt-uniforms-storefront-prototype.vercel.app/> — 321 real products,
  39 categories, working cart, working option selection. Cart is browser-local and checkout hands
  the order to the store by email, because no payment rail is wired and pretending otherwise would
  be worse than saying so.
- **Portable theme** in `theme/` — real Shopify Liquid, and the same files render the prototype.
  Switching platform is one setting, not a rebuild.
- **Operations database** in `ops/` — catalog, agencies, orders, decoration queue, stock movements;
  8 schema checks passing.
- **Catalog extraction** under `PROJECT_DATA_ROOT` — 321 products, 0 errors, no credentials used.
