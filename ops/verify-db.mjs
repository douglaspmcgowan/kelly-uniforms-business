/* Exercises the operations schema end to end against a throwaway in-memory database.
 *
 * This is the proof that the schema works, not just that it parses: it walks a real counter
 * workflow — an agency orders trousers with options, the shop hems them, stock moves, the order
 * closes — and asserts the constraints and views behave. It never touches the live database.
 *
 *   node ops/verify-db.mjs
 */
import fs from 'node:fs'
import path from 'node:path'
import assert from 'node:assert/strict'
import { DatabaseSync } from 'node:sqlite'
import { fileURLToPath } from 'node:url'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const db = new DatabaseSync(':memory:')
db.exec(fs.readFileSync(path.join(HERE, 'schema.sql'), 'utf8').replace(/PRAGMA journal_mode = WAL;/, ''))

const run = (sql, ...a) => db.prepare(sql).run(...a)
const get = (sql, ...a) => db.prepare(sql).get(...a)
const all = (sql, ...a) => db.prepare(sql).all(...a)

let passed = 0
function check (name, fn) {
  fn()
  passed++
  console.log('  ok  ' + name)
}

/* --------------------------------------------------------------- fixtures */

const product = run(
  `INSERT INTO product (source_product_id, handle, name, model, brand, price_cents)
   VALUES ('662', 'elbeco-adu-ripstop-trousers-tradu', 'Elbeco ADU Ripstop Trousers', 'TRADU', 'Elbeco', 6299)`
).lastInsertRowid
const optWaist = run(
  `INSERT INTO product_option (product_id, name, kind, required) VALUES (?, 'Waist Size', 'select', 1)`, product
).lastInsertRowid
run(`INSERT INTO product_option_value (option_id, label) VALUES (?, '34')`, optWaist)
run(`INSERT INTO inventory (product_id, on_hand, reorder_point) VALUES (?, 10, 4)`, product)

const agency = run(
  `INSERT INTO agency (name, kind, spec_notes) VALUES ('Richland Township PD', 'police', 'Shoulder patch both sleeves, 1in below seam.')`
).lastInsertRowid
const officer = run(
  `INSERT INTO customer (name, agency_id, size_notes) VALUES ('R. Kelly', ?, 'Waist 34, inseam 30 unhemmed')`, agency
).lastInsertRowid

/* ------------------------------------------------------------------ tests */

console.log('operations schema')

check('an order line preserves the name and price it was sold at', () => {
  const order = run(
    `INSERT INTO "order" (reference, customer_id, agency_id, channel, status, purchase_order_number)
     VALUES ('MT-1001', ?, ?, 'counter', 'placed', 'PO-88213')`, officer, agency
  ).lastInsertRowid
  const line = run(
    `INSERT INTO order_line (order_id, product_id, name_at_sale, model_at_sale, unit_price_cents, quantity, line_total_cents)
     VALUES (?, ?, 'Elbeco ADU Ripstop Trousers', 'TRADU', 6299, 2, 12598)`, order, product
  ).lastInsertRowid
  run(`INSERT INTO order_line_option (order_line_id, option_name, value_label) VALUES (?, 'Waist Size', '34')`, line)

  // Renaming and repricing the product must not rewrite history.
  run(`UPDATE product SET name = 'Elbeco ADU RipStop Trouser (2027)', price_cents = 6999 WHERE id = ?`, product)
  const row = get('SELECT name_at_sale, unit_price_cents FROM order_line WHERE id = ?', line)
  assert.equal(row.name_at_sale, 'Elbeco ADU Ripstop Trousers')
  assert.equal(row.unit_price_cents, 6299)
})

check('decoration work is tracked separately from the sale', () => {
  const line = get('SELECT id FROM order_line LIMIT 1').id
  run(`INSERT INTO decoration_job (order_line_id, kind, instructions, price_cents)
       VALUES (?, 'hem', 'Hem to 30in finished, boot cut.', 1200)`, line)
  run(`INSERT INTO decoration_job (order_line_id, kind, instructions, price_cents)
       VALUES (?, 'name-tape', 'KELLY, silver on navy.', 900)`, line)

  const summary = get('SELECT * FROM v_order_summary WHERE reference = ?', 'MT-1001')
  assert.equal(summary.open_decoration, 2, 'both jobs should be open')
  assert.equal(summary.customer, 'Richland Township PD')
  assert.equal(summary.purchase_order_number, 'PO-88213')

  run(`UPDATE decoration_job SET status = 'done', completed_at = datetime('now') WHERE kind = 'hem'`)
  assert.equal(get('SELECT * FROM v_order_summary WHERE reference = ?', 'MT-1001').open_decoration, 1)
})

check('stock movements are recorded, not just applied', () => {
  const order = get('SELECT id FROM "order" LIMIT 1').id
  run(`INSERT INTO inventory_movement (product_id, delta, reason, order_id) VALUES (?, -2, 'sold', ?)`, product, order)
  run(`UPDATE inventory SET on_hand = on_hand - 2 WHERE product_id = ?`, product)

  const moved = get('SELECT SUM(delta) d FROM inventory_movement WHERE product_id = ?', product).d
  const onHand = get('SELECT on_hand FROM inventory WHERE product_id = ?', product).on_hand
  assert.equal(moved, -2)
  assert.equal(onHand, 8)
})

check('the reorder view fires only at or below the reorder point', () => {
  run(`UPDATE inventory SET counted_at = datetime('now') WHERE product_id = ?`, product)
  assert.equal(all('SELECT * FROM v_reorder').length, 0, '8 on hand against a point of 4 is fine')
  run(`UPDATE inventory SET on_hand = 4 WHERE product_id = ?`, product)
  assert.equal(all('SELECT * FROM v_reorder').length, 1, '4 against 4 should surface')
})

check('a product that has never been counted is not treated as out of stock', () => {
  run(`INSERT INTO product (handle, name, price_cents) VALUES ('never-counted', 'Never Counted', 100)`)
  const p2 = get(`SELECT id FROM product WHERE handle = 'never-counted'`).id
  run('INSERT INTO inventory (product_id, on_hand, reorder_point) VALUES (?, 0, 0)', p2)

  assert.equal(all('SELECT * FROM v_reorder').filter(r => r.id === p2).length, 0,
    'zero-on-hand with no count must not appear as needing reorder')
  assert.equal(all('SELECT * FROM v_uncounted').filter(r => r.id === p2).length, 1,
    'it should appear as uncounted instead')
})

check('free-text options are identifiable as a set', () => {
  run(`INSERT INTO product (handle, name, price_cents) VALUES ('nametag-nt08', 'Nametag', 2699)`)
  const nametag = get(`SELECT id FROM product WHERE handle = 'nametag-nt08'`).id
  run(`INSERT INTO product_option (product_id, name, kind, required) VALUES (?, 'Engraving', 'textarea', 1)`, nametag)
  const rows = all('SELECT * FROM v_free_text_options')
  assert.equal(rows.length, 1)
  assert.equal(rows[0].option_name, 'Engraving')
})

check('invalid states are rejected rather than stored', () => {
  assert.throws(() => run(`UPDATE "order" SET status = 'almost-ready' WHERE reference = 'MT-1001'`), /CHECK/i)
  assert.throws(() => run(`INSERT INTO order_line (order_id, name_at_sale, unit_price_cents, quantity, line_total_cents)
                           VALUES (1, 'x', 100, 0, 0)`), /CHECK/i)
  assert.throws(() => run(`INSERT INTO "order" (reference) VALUES ('MT-1001')`), /UNIQUE/i)
})

check('deleting an order takes its lines, options, and decoration with it', () => {
  run(`DELETE FROM "order" WHERE reference = 'MT-1001'`)
  assert.equal(get('SELECT COUNT(*) n FROM order_line').n, 0)
  assert.equal(get('SELECT COUNT(*) n FROM order_line_option').n, 0)
  assert.equal(get('SELECT COUNT(*) n FROM decoration_job').n, 0)
  // The stock movement survives on purpose: the goods still left the shelf.
  assert.equal(get('SELECT COUNT(*) n FROM inventory_movement').n, 1)
  assert.equal(get('SELECT order_id FROM inventory_movement').order_id, null)
})

console.log(`\n${passed} checks passed`)
db.close()
