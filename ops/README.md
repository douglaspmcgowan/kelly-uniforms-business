# Operations database

Catalog, agencies, orders, decoration work, and stock for M.T. Uniforms. SQLite, no dependencies —
`node:sqlite` ships with Node 22+.

The database file is runtime data. It lives under `PROJECT_DATA_ROOT`
(`~/Data/Projects/kelly-uniforms-business/db/operations.sqlite`) and is never committed.

## Commands

```bash
node ops/verify-db.mjs     # 8 checks against a throwaway in-memory database
node ops/build-db.mjs      # build from the newest catalog export
node ops/seed-demo.mjs     # add four clearly-fictional orders so the console has content
node ops/admin.mjs         # local console at http://127.0.0.1:8930
```

`build-db.mjs` renames any existing database to `operations.<timestamp>.sqlite` rather than
overwriting it.

## What it models, and what it deliberately does not

Modelled: products with option groups and values, categories, agencies, customers, orders, order
lines, the options chosen on each line, decoration jobs, and stock movements.

**Not modelled, on purpose:** per-officer clothing allowance ledgers, agency self-service portals,
approval chains, and authorization codes. `INTENT.md` holds these as a separate second phase to be
proposed only after the current workflow is observed and discussed with the client. A
`purchase_order_number` column exists on orders because agency POs are already how these orders get
paid — that is a field, not an approval system.

## Two design decisions worth knowing

**Order lines are denormalised.** `name_at_sale`, `model_at_sale`, and `unit_price_cents` are copied
onto the line. An order is a record of what was sold on the day and must not change because someone
renamed or repriced the product afterwards. `verify-db.mjs` asserts this.

**An unknown stock count is not a count of zero.** `inventory.counted_at` is null until a real count
lands, and `v_reorder` excludes those rows. Without that, all 321 products would appear to need
reordering — which is what the first version did. `v_uncounted` shows the gap honestly instead.

## The console

`admin.mjs` binds to `127.0.0.1` only and has no authentication, because it is a local tool on a
trusted machine and a half-built login is worse than an honest local-only bind. **Do not expose it
to a network without putting real authentication in front of it first.**

Screens: dashboard, orders, order detail with status changes, decoration queue with completion,
catalog search, and reorder.
