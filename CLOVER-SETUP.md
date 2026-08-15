# Clover setup

Clover is the fixed constraint in this project: the store already runs on it, it is not being
replaced, and the website has to fit around it. This brief is the setup sequence and the decisions
it depends on.

Related: `MIGRATION-RUNBOOK.md` owns the Shopify migration · `SETUP.md` owns approvals and money ·
`ACCESS.md` owns credentials · the Obsidian platform brief owns why Shopify was chosen against
this constraint.

**What is verified and what is not.** The M.T. Uniforms side of this — the catalog shape, the option
model, the stock gap — is measured from the 2026-08-14 export and is solid. The Clover side is
**not yet verified against the live merchant account**, because that needs Douglas's merchant login.
Everything below marked *verify* is a step to confirm, not a fact being asserted.

---

## The decision this all hangs on

**Who owns the product record — the website or Clover?**

This is not a technical preference and it cannot be deferred past the first sync. It is open
question 1 in `SETUP.md` and it needs a business answer.

| If Clover owns it | If Shopify owns it |
|---|---|
| The catalog is limited to what Clover's item and modifier model can express | The catalog is as rich as Shopify allows |
| One place to add a product; the counter stays the source of truth | Products are added on the website, and Clover receives them |
| Website variants must collapse into Clover items/modifiers | Clover receives sales but does not constrain the catalog |

The measured catalog makes this concrete rather than abstract: **12,098 variants across 407
products**, and one pair of trousers alone accounts for 1,020 of them. A model that has to represent
every one of those as a distinct Clover item is a different proposition from one that does not.
Answer the ownership question before writing any sync code.

---

## Stage 1 — establish what the account can actually do

**Needs Douglas — merchant login required.** This is `SETUP.md` item 5.

1. Sign in to the Clover merchant dashboard.
2. Find the merchant ID and record it in `ACCESS.md` as a name, never a value.
3. *Verify:* whether the account tier permits API access at all. Not every Clover plan does, and
   this is the step that can invalidate the whole integration design. Do it first.
4. *Verify:* which app-market integrations are already installed. The store may already have a
   sync tool nobody mentioned, which would change the build to a configuration job.
5. *Verify:* current inventory item count in Clover, against the 407 products in the export. The gap
   between those two numbers tells you whether Clover is a full catalog or a till.

## Stage 2 — get the inventory count out

This unblocks the single largest gap in the Shopify import. **Every one of the 12,098 variants
imports at stock 0**, because OpenCart holds stock per product rather than per option value and
those counts cannot be split without inventing numbers.

1. Export inventory from the Clover dashboard — item name, SKU, quantity.
2. Map Clover SKUs to the `Variant SKU` column in `products.csv`. Expect this to be partial; the
   SKUs in the import are generated from OpenCart model numbers plus option initials where no real
   SKU existed.
3. Whatever does not map is a manual count. Say so plainly rather than importing a guess.

`ops/schema.sql` already models this honestly: `inventory.counted_at` stays null until a real count
lands, and `v_reorder` excludes uncounted rows so the reorder screen shows nothing rather than
showing all 407 products as out of stock. Keep that property.

## Stage 3 — API credentials

**Never handled by an agent.** These are entered by Douglas, into Clover's own interface, and
recorded value-free.

1. Create an app in Clover's developer dashboard, or generate an API token from the merchant
   dashboard, depending on what stage 1 finds.
2. *Verify:* the current auth model and required scopes against Clover's official documentation at
   the time you do it. Do not build against remembered endpoint shapes — check the live docs.
3. Record the credential **names** in `secret-manifest.json` and safe placeholders in `.env.example`.
   Values go to the secret store, never to this repository, chat, or logs.
4. Use separate sandbox and production credentials. Clover provides a sandbox; use it for every
   test that writes.

## Stage 4 — decide the sync direction, then build the smallest thing

Do not build a bidirectional sync. It is the most expensive option and the one most likely to
produce two systems that disagree about stock on a Saturday.

| Direction | What it buys | What it costs |
|---|---|---|
| **Clover → Shopify, stock only** | The website stops selling what the shop does not have | Small, one-way, and it fails safe |
| Shopify → Clover, orders | Web orders appear at the counter | Needs order and customer mapping |
| Bidirectional catalog | One catalog everywhere | Conflict resolution, and a real answer to the ownership question first |

**Start with stock, one way, Clover to Shopify.** It is the smallest change that removes the worst
failure mode, and it does not require the ownership question to be answered first.

### The question to settle before writing any of it

What happens when the two disagree? Name the winner per field — stock, price, product name,
availability — before writing the first sync call. A sync without a stated conflict rule does not
have a bug; it has an unanswered design question that surfaces as a bug later.

---

## What is not in scope, deliberately

Per-officer clothing allowances, agency self-service portals, approval chains, and authorization
codes. `INTENT.md` holds these as a separate second phase, to be proposed only after the current
counter workflow is observed and discussed with the client. Nothing measured so far establishes
them as a requirement, and building them into the first integration would be guessing at the
business.
