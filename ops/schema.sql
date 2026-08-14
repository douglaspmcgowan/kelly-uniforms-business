-- M.T. Uniforms operations database
--
-- Scope discipline. INTENT.md is explicit that unverified ecommerce features must not become
-- requirements, and that per-officer allowances, authorization codes, and agency portals are a
-- separate second phase to be proposed only after the current workflow is observed and discussed
-- with the client. This schema therefore models only what the extracted catalog and the observable
-- counter workflow actually establish:
--
--   * a catalog of products with option groups and option values, which is what the current site has
--   * customers, which may be a walk-in person or an agency
--   * orders, order lines, and the chosen options on each line
--   * decoration and alteration work, because that is the part of the job the current site cannot
--     express at all and the part the counter tracks on paper
--   * inventory counts held per product, matching how the current admin holds them
--
-- Deliberately absent, and not to be added without the client conversation:
--   * per-officer clothing allowance ledgers
--   * agency self-service portals and approval chains
--   * authorization codes
-- A purchase_order_number column exists on orders because agency POs are already how these orders
-- get paid; that is a field on an order, not an approval system.
--
-- Money is stored in integer cents. Times are ISO-8601 UTC strings.

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------------ catalog

CREATE TABLE IF NOT EXISTS product (
  id                INTEGER PRIMARY KEY,
  source_product_id TEXT UNIQUE,            -- id in the OpenCart catalog it was imported from
  handle            TEXT NOT NULL UNIQUE,
  name              TEXT NOT NULL,
  model             TEXT NOT NULL DEFAULT '',
  brand             TEXT NOT NULL DEFAULT '',
  weight            TEXT NOT NULL DEFAULT '',
  price_cents       INTEGER NOT NULL CHECK (price_cents >= 0),
  image_url         TEXT NOT NULL DEFAULT '',
  description_html  TEXT NOT NULL DEFAULT '',
  active            INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
  created_at        TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS category (
  id     INTEGER PRIMARY KEY,
  name   TEXT NOT NULL,
  handle TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS product_category (
  product_id  INTEGER NOT NULL REFERENCES product(id) ON DELETE CASCADE,
  category_id INTEGER NOT NULL REFERENCES category(id) ON DELETE CASCADE,
  PRIMARY KEY (product_id, category_id)
);

-- An option group on a product: "Waist Size", "Color", "Engraving".
CREATE TABLE IF NOT EXISTS product_option (
  id               INTEGER PRIMARY KEY,
  product_id       INTEGER NOT NULL REFERENCES product(id) ON DELETE CASCADE,
  source_option_id TEXT NOT NULL DEFAULT '',
  name             TEXT NOT NULL,
  -- 'select' and 'radio' are pickable lists; 'text' and 'textarea' are free entry, which matters
  -- because a POS whose option model is pick-lists only cannot represent the free-entry kinds.
  kind             TEXT NOT NULL CHECK (kind IN ('select', 'radio', 'checkbox', 'text', 'textarea', 'date', 'file')),
  required         INTEGER NOT NULL DEFAULT 0 CHECK (required IN (0, 1)),
  position         INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_product_option_product ON product_option(product_id);

CREATE TABLE IF NOT EXISTS product_option_value (
  id                INTEGER PRIMARY KEY,
  option_id         INTEGER NOT NULL REFERENCES product_option(id) ON DELETE CASCADE,
  source_value_id   TEXT NOT NULL DEFAULT '',
  label             TEXT NOT NULL,
  price_delta_cents INTEGER NOT NULL DEFAULT 0,
  position          INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_option_value_option ON product_option_value(option_id);

-- ---------------------------------------------------------------- inventory

CREATE TABLE IF NOT EXISTS inventory (
  product_id    INTEGER PRIMARY KEY REFERENCES product(id) ON DELETE CASCADE,
  on_hand       INTEGER NOT NULL DEFAULT 0,
  reorder_point INTEGER NOT NULL DEFAULT 0,
  counted_at    TEXT
);

-- Every change to on_hand leaves a row here, so a discrepancy can be traced instead of argued.
CREATE TABLE IF NOT EXISTS inventory_movement (
  id         INTEGER PRIMARY KEY,
  product_id INTEGER NOT NULL REFERENCES product(id) ON DELETE CASCADE,
  delta      INTEGER NOT NULL,
  reason     TEXT NOT NULL CHECK (reason IN ('received', 'sold', 'returned', 'count-adjustment', 'damaged', 'transferred')),
  order_id   INTEGER REFERENCES "order"(id) ON DELETE SET NULL,
  note       TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_movement_product ON inventory_movement(product_id, created_at);

-- --------------------------------------------------------------- customers

CREATE TABLE IF NOT EXISTS agency (
  id             INTEGER PRIMARY KEY,
  name           TEXT NOT NULL UNIQUE,
  kind           TEXT NOT NULL DEFAULT 'other'
                   CHECK (kind IN ('police', 'fire-ems', 'corrections', 'security', 'constable', 'postal', 'other')),
  billing_email  TEXT NOT NULL DEFAULT '',
  billing_phone  TEXT NOT NULL DEFAULT '',
  billing_address TEXT NOT NULL DEFAULT '',
  -- Standing decoration specification: patch placement, badge, name-tape format, approved colors.
  -- Free text on purpose; this is a note the counter reads, not a rules engine.
  spec_notes     TEXT NOT NULL DEFAULT '',
  active         INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
  created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS customer (
  id         INTEGER PRIMARY KEY,
  name       TEXT NOT NULL,
  email      TEXT NOT NULL DEFAULT '',
  phone      TEXT NOT NULL DEFAULT '',
  agency_id  INTEGER REFERENCES agency(id) ON DELETE SET NULL,
  -- Sizes kept on file so a repeat order does not need a fitting. Free text per field because
  -- uniform sizing is not consistent between manufacturers.
  size_notes TEXT NOT NULL DEFAULT '',
  notes      TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_customer_agency ON customer(agency_id);
CREATE INDEX IF NOT EXISTS idx_customer_name ON customer(name);

-- ------------------------------------------------------------------ orders

CREATE TABLE IF NOT EXISTS "order" (
  id                   INTEGER PRIMARY KEY,
  reference            TEXT NOT NULL UNIQUE,
  customer_id          INTEGER REFERENCES customer(id) ON DELETE SET NULL,
  agency_id            INTEGER REFERENCES agency(id) ON DELETE SET NULL,
  channel              TEXT NOT NULL DEFAULT 'counter'
                         CHECK (channel IN ('counter', 'phone', 'web', 'on-site-fitting')),
  status               TEXT NOT NULL DEFAULT 'draft'
                         CHECK (status IN ('draft', 'placed', 'awaiting-stock', 'in-decoration', 'ready', 'collected', 'shipped', 'cancelled')),
  purchase_order_number TEXT NOT NULL DEFAULT '',
  payment_status       TEXT NOT NULL DEFAULT 'unpaid'
                         CHECK (payment_status IN ('unpaid', 'invoiced', 'paid', 'refunded')),
  -- Set when the sale is rung through the POS, so the two systems can be reconciled by reference
  -- rather than by memory. Null means it has not been rung yet.
  pos_reference        TEXT,
  subtotal_cents       INTEGER NOT NULL DEFAULT 0,
  decoration_cents     INTEGER NOT NULL DEFAULT 0,
  tax_cents            INTEGER NOT NULL DEFAULT 0,
  total_cents          INTEGER NOT NULL DEFAULT 0,
  notes                TEXT NOT NULL DEFAULT '',
  promised_at          TEXT,
  created_at           TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at           TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_order_status ON "order"(status, created_at);
CREATE INDEX IF NOT EXISTS idx_order_agency ON "order"(agency_id);

CREATE TABLE IF NOT EXISTS order_line (
  id              INTEGER PRIMARY KEY,
  order_id        INTEGER NOT NULL REFERENCES "order"(id) ON DELETE CASCADE,
  product_id      INTEGER REFERENCES product(id) ON DELETE SET NULL,
  -- Denormalised on purpose: an order is a record of what was sold on the day, and it must not
  -- change because someone renamed or repriced the product afterwards.
  name_at_sale    TEXT NOT NULL,
  model_at_sale   TEXT NOT NULL DEFAULT '',
  unit_price_cents INTEGER NOT NULL CHECK (unit_price_cents >= 0),
  quantity        INTEGER NOT NULL CHECK (quantity > 0),
  line_total_cents INTEGER NOT NULL,
  created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_line_order ON order_line(order_id);

CREATE TABLE IF NOT EXISTS order_line_option (
  id            INTEGER PRIMARY KEY,
  order_line_id INTEGER NOT NULL REFERENCES order_line(id) ON DELETE CASCADE,
  option_name   TEXT NOT NULL,
  value_label   TEXT NOT NULL,
  price_delta_cents INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_line_option_line ON order_line_option(order_line_id);

-- ------------------------------------------------------- decoration and alterations

-- The work the shop does to a garment after it is picked. This is the part of the business the
-- current website cannot express, and the reason an order is not finished when it is paid for.
CREATE TABLE IF NOT EXISTS decoration_job (
  id            INTEGER PRIMARY KEY,
  order_line_id INTEGER NOT NULL REFERENCES order_line(id) ON DELETE CASCADE,
  kind          TEXT NOT NULL CHECK (kind IN ('hem', 'taper', 'name-tape', 'embroidery', 'patch', 'badge-tab', 'hash-marks', 'other')),
  instructions  TEXT NOT NULL DEFAULT '',
  price_cents   INTEGER NOT NULL DEFAULT 0,
  status        TEXT NOT NULL DEFAULT 'queued'
                  CHECK (status IN ('queued', 'in-progress', 'done', 'cancelled')),
  assigned_to   TEXT NOT NULL DEFAULT '',
  completed_at  TEXT,
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_decoration_status ON decoration_job(status, created_at);

-- ------------------------------------------------------------------- views

CREATE VIEW IF NOT EXISTS v_order_summary AS
SELECT o.id, o.reference, o.status, o.payment_status, o.channel,
       COALESCE(a.name, c.name, 'Walk-in') AS customer,
       o.purchase_order_number,
       (SELECT COUNT(*) FROM order_line l WHERE l.order_id = o.id) AS lines,
       (SELECT COUNT(*) FROM decoration_job d
          JOIN order_line l ON l.id = d.order_line_id
         WHERE l.order_id = o.id AND d.status IN ('queued', 'in-progress')) AS open_decoration,
       o.total_cents, o.promised_at, o.created_at
  FROM "order" o
  LEFT JOIN agency a ON a.id = o.agency_id
  LEFT JOIN customer c ON c.id = o.customer_id;

-- counted_at IS NOT NULL is load-bearing: a product that has never been counted has on_hand 0,
-- which would otherwise read as "out of stock, reorder now" for the entire catalog. An unknown
-- count is not a count of zero.
CREATE VIEW IF NOT EXISTS v_reorder AS
SELECT p.id, p.name, p.model, p.brand, i.on_hand, i.reorder_point, i.counted_at
  FROM product p
  JOIN inventory i ON i.product_id = p.id
 WHERE p.active = 1
   AND i.counted_at IS NOT NULL
   AND i.on_hand <= i.reorder_point
 ORDER BY (i.reorder_point - i.on_hand) DESC;

-- The counterpart: what the shop does not know yet. Surfacing this is the honest way to show that
-- the reorder list is short because counts are missing, not because stock is healthy.
CREATE VIEW IF NOT EXISTS v_uncounted AS
SELECT p.id, p.name, p.model, p.brand
  FROM product p
  JOIN inventory i ON i.product_id = p.id
 WHERE p.active = 1 AND i.counted_at IS NULL;

-- Products the shop sells that need free-text entry from the buyer. This view exists because it is
-- the exact set that a pick-list-only option model cannot represent, which is a live platform
-- question rather than a hypothetical one.
CREATE VIEW IF NOT EXISTS v_free_text_options AS
SELECT p.id, p.name, p.model, o.name AS option_name, o.kind, o.required
  FROM product p
  JOIN product_option o ON o.product_id = p.id
 WHERE o.kind IN ('text', 'textarea')
 ORDER BY p.name;
