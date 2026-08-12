# What the MT Uniforms online store has to be able to do

Last updated: 2026-07-31. Status: **draft for client confirmation.**

This is the requirements specification the platform decision (`DEL-003`) gets
judged against. Anything marked **must** is a disqualifier if a platform cannot
do it. Items marked **[CONFIRM]** are assumptions I have made from evidence and
that Kelly or David needs to accept or correct before a platform is chosen.

Sources: `MSG-001`, `MSG-004`, `OBS-004`, and the live catalog.

---

## 0. The three facts that drive everything

1. **Clover is the in-store POS** and the client asked whether the website can
   work with it. Any recommendation must answer that explicitly. Source: `MSG-004`.
2. **They want customers to pay online instead of being invoiced.** This is a
   payments change, not a redesign. Source: `MSG-004`.
3. **The previous owner is believed to be paying for the current platform and may
   stop.** Source: `MSG-004`. Until domain, hosting, and licence ownership are
   established, every plan has an unpriced continuity risk under it.

---

## 1. Product catalog — the hardest requirement

Uniform retail breaks most e-commerce platforms on option complexity. This is
the first filter to apply, before design, price, or anything else.

| # | Requirement | Priority | Why |
|---|---|---|---|
| 1.1 | Multi-axis variants: **size × width × inseam × color × gender cut** — four to five independent axes on a single product | **must** | A duty trouser is 12 waists × 3 inseams × 4 colors × 2 cuts = 288 combinations. Platforms with a 3-option cap or a 250-combination cap cannot hold this. |
| 1.2 | Per-variant SKU, price, stock level, weight, and image | **must** | Sizes carry different costs; stock is tracked per exact SKU. |
| 1.3 | Free-text input per line item with an optional surcharge — **name, rank, badge number, department** for embroidery | **must** | Highest-margin service. The text must stay bound to the garment line, not float as a separate cart item. |
| 1.4 | Dropdown/選択 customization options that adjust price — hemming, patch placement, thread color, DTF placement | **must** | |
| 1.5 | File upload per line item for artwork | should | Needed for custom logo work; a workaround by email is tolerable at launch. |
| 1.6 | Catalog scale of roughly 500–2,000 products with variants | **must** | Live catalog spans police, fire/EMS, constable, corrections, security, postal, badges, footwear, headwear, outerwear, duty gear. |
| 1.7 | Supplier catalog feeds (Elbeco, Rocky, Reebok, Hatch, 5.11 and similar) | should | Manual entry of a 2,000-SKU catalog is the single largest migration cost. |
| 1.8 | Restricted-item handling: badges, insignia, and duty gear that only verified agency personnel may buy | **[CONFIRM]** | The catalog sells badges and body armor. Whether they gate these today is unknown and materially changes the build. |

## 2. Ordering, payment, and checkout

| # | Requirement | Priority | Why |
|---|---|---|---|
| 2.1 | Online card payment at checkout | **must** | The client's stated goal. Source: `MSG-004`. |
| 2.2 | Coexistence with the Clover merchant account, or a costed decision to leave it | **must** | Clover binds hardware and processing to Fiserv. Exit has contractual cost. |
| 2.3 | Purchase-order checkout — buyer enters a PO number, order proceeds unpaid | **must** | Departments buy on POs. This is how agency business actually transacts. |
| 2.4 | Net-terms invoicing (Net 30/60/90) | **must** | |
| 2.5 | Per-agency pricing / contract price lists | **must** | Departments negotiate rates. |
| 2.6 | Tax exemption per account | **must** | Municipal and government buyers are exempt. |
| 2.7 | Local pickup and local delivery as fulfilment options | **must** | Advertised in supplied marketing. |
| 2.8 | Quote request → quote → order flow | should | Large department orders start as quotes. |
| 2.9 | Partial payment or deposit on large orders | **[CONFIRM]** | Common in uniform contracts; on some platforms this forces the top pricing tier. |

## 3. Agency and department accounts

This is the section that decides between a mainstream platform and a
uniform-industry vertical platform.

| # | Requirement | Priority | Why |
|---|---|---|---|
| 3.1 | Company/agency accounts with multiple individual buyers under them | **must** | |
| 3.2 | Per-officer order history and one-click reorder | **must** | Officers reorder the same shirt for years. |
| 3.3 | Approved-item lists per department | should | Departments mandate exact permitted items. |
| 3.4 | **Per-officer uniform allowance with balance tracking, partial spend, and annual reset** | **[CONFIRM] — likely must** | This is the hardest requirement in the whole document and the clearest reason to consider a vertical platform. Mainstream platforms do not do it natively. **Kelly or David must confirm whether any current agency runs an allowance program.** |
| 3.5 | Authorization codes for agency purchases | **[CONFIRM]** | No researched platform documents this natively; assume custom work if required. |
| 3.6 | Supervisor approval routing before an order is placed | nice to have | |

## 4. Operations and back office

| # | Requirement | Priority |
|---|---|---|
| 4.1 | Inventory sync with Clover so the counter and the website do not oversell | **must** |
| 4.2 | Production routing — embroidery/DTF orders reach the shop floor with the name, rank, and placement attached | **must** |
| 4.3 | Artwork proofing and customer approval before production | should |
| 4.4 | Order status notifications to the customer | **must** |
| 4.5 | Shipping rates and label printing | **must** |
| 4.6 | Returns and exchanges — sizing returns are frequent in uniform retail | **must** |
| 4.7 | Reporting: sales by category, by agency, by product | should |

## 5. Storefront quality

| # | Requirement | Priority | Why |
|---|---|---|---|
| 5.1 | Mobile-first; usable one-handed on a phone | **must** | Officers order from patrol vehicles and station houses. |
| 5.2 | **WCAG 2.1 AA accessibility, with a vendor VPAT available** | **must — now dated** | See the deadline box below. |
| 5.3 | Working search and faceted filtering by size, color, brand, agency type | **must** | 2,000 SKUs are unusable without it. |
| 5.4 | Clear size guides and fit information | **must** | Directly reduces return rate. |
| 5.5 | Fast page loads on the mobile networks their customers use | should | |
| 5.6 | No design carry-over required | — | Client said "Nothing I want to keep." Full redesign freedom. Source: `MSG-004`. |

### The accessibility deadline is real and dated

DOJ's 2024 final rule adopts **WCAG 2.1 Level AA** for state and local government
web content and mobile apps. <https://www.ada.gov/resources/2024-03-08-web-rule/>

| Entity | Compliance deadline |
|---|---|
| Serving **50,000 or more** people | **2027-04-26** |
| Serving **fewer than 50,000** | **2028-04-28** |
| **Special district governments** (any size — most fire districts) | **2028-04-28** |

The rule binds the government entity, not its uniform vendor, and a retailer
running its own catalog is not automatically captured. **But the procurement
consequence arrives well before the deadline.** Departments facing April 2027
will write WCAG 2.1 AA into solicitations and vendor onboarding during 2026 —
now. And where a department directs its officers to a vendor ordering portal as
part of uniform issue, that portal starts to resemble third-party web content
made available by arrangement.

Losing a bid requires no DOJ action. An inaccessible storefront is simply a
disqualifying line on a checklist. **Ask every finalist platform for a VPAT in
writing.** Several major platforms could not produce a locatable one during
research.

## 6. Migration and continuity

| # | Requirement | Priority |
|---|---|---|
| 6.1 | Migrate the catalog including product options, not just flat products | **must** |
| 6.2 | Migrate customers and order history, or an agreed decision not to | **must** |
| 6.3 | 301 redirect map from existing SEO URLs so search rankings survive | **must** |
| 6.4 | **Establish who owns and pays for the domain, DNS, hosting, and theme licence** | **must — do this first** |
| 6.5 | Rollback plan if the new platform fails at launch | **must** |
| 6.6 | Preserve each OpenCart, Journal, Ecwid, hosting, and infrastructure export byte-for-byte before transformation, with source account reference, method, time window, version, size, SHA-256, and record counts | **must** |
| 6.7 | Preserve immutable external IDs and a trace from every normalized record to its source artifact and extraction run | **must** |
| 6.8 | Reconcile catalog, variants, options, media, customers, inventory by location, orders by status, discounts, tax, shipping, tenders, refunds, and net sales before cutover. Clover settlement reconciliation is outside the current recovery scope unless separately authorized | **must** |
| 6.9 | Keep historical order-line name, SKU, description, price, tax, option, personalization, and address snapshots independent of later catalog edits | **must** |
| 6.10 | Maintain encrypted working, immutable offline, and independent offsite copies; exclude credential values, session cookies, PAN/CVV data, and authentication codes | **must** |
| 6.11 | Restore on a clean isolated host without vendor access and reconstruct a representative agency order, fulfillment, return/refund, and cross-system reconciliation | **must** |
| 6.12 | Publish an explicit completeness matrix (`PROVEN`, `PARTIAL`, `MISSING`, or `BLOCKED BY ACCESS`) and never label a public crawl or theme export as a complete business backup | **must** |

## 7. Cost and maintainability

| # | Requirement | Priority |
|---|---|---|
| 7.1 | Manageable by a non-developer for routine catalog and content work | **must** |
| 7.2 | Total monthly cost visible and predictable, including apps and transaction fees | **must** |
| 7.3 | No dependence on a single third-party middleware vendor with no fallback | should |
| 7.4 | Douglas can hand it over and the business can run it | **must** |

---

## The one question that decides the platform

**Does any current agency customer run a per-officer uniform allowance, or
require authorization codes?**

- **If no** — a mainstream platform works. Shopify's native B2B moved onto the
  non-Plus plans in April 2026, which brings company accounts, PO checkout, net
  terms, tax exemption, and per-agency catalogs within reach at normal small-
  business pricing.
- **If yes** — mainstream platforms do not handle per-officer allowance balances
  natively, and a uniform-industry vertical platform enters serious contention
  despite its lock-in and thin review base.

Everything else in this document has a known answer. This one does not, and it
is worth a direct phone call to David before any platform is recommended.

---

## The acceptance test every finalist must pass

Do not choose a platform from a feature matrix. Run this one scenario in a trial
account, end to end, before any money is committed:

> **A 12-officer department order: 12 garments, 12 distinct name and badge-number
> values, each drawn against that officer's individual annual allowance balance,
> the whole order invoiced to the department on net 30, tax exempt, with the
> embroidery details reaching the shop floor on the packing slip.**

That single scenario exercises every requirement this project has found to be
fragile: multi-axis variants, per-line-item priced free text, per-officer
allowance balances, department-level invoicing, tax exemption, and production
routing. Across every platform researched, **at least one leg of it fails**.

Note the bar the competition sets. Galls runs agency portals where **allotment
balances update live while the officer shops**. That is not licensable software —
it is Galls' own moat, built in-house. But it is what departments will compare
MT Uniforms against.
