/* Puts a handful of illustrative orders into the operations database so the console has something
 * to show. Every record here is invented for demonstration and is marked as such: references start
 * at MT-D and the agency names are fictional. No real customer, order, or agency data is used.
 *
 *   node ops/seed-demo.mjs
 */
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { DatabaseSync } from 'node:sqlite'

const ROOTS = [process.env.PROJECT_DATA_ROOT, path.join(os.homedir(), 'Data', 'Projects', 'kelly-uniforms-business')].filter(Boolean)
const dbPath = ROOTS.map(r => path.join(r, 'db', 'operations.sqlite')).find(p => fs.existsSync(p))
if (!dbPath) { console.error('Run ops/build-db.mjs first.'); process.exit(1) }

const db = new DatabaseSync(dbPath)
db.exec('PRAGMA foreign_keys = ON')
const run = (sql, ...a) => db.prepare(sql).run(...a)
const get = (sql, ...a) => db.prepare(sql).get(...a)

if (get(`SELECT COUNT(*) n FROM "order" WHERE reference LIKE 'MT-D%'`).n) {
  console.log('[seed] demo orders already present; leaving them alone.')
  process.exit(0)
}

const AGENCIES = [
  ['Laurel Ridge Township PD', 'police', 'Shoulder patch both sleeves, 1in below shoulder seam. Silver hardware.'],
  ['Conemaugh Valley Fire Co.', 'fire-ems', 'Maltese cross left chest. Bugles by rank on collar.'],
  ['Cambria County Constables', 'constable', 'Keystone patch left sleeve only.']
]
const agencyIds = AGENCIES.map(([name, kind, spec]) =>
  run('INSERT INTO agency (name, kind, spec_notes) VALUES (?, ?, ?)', name, kind, spec).lastInsertRowid)

const PEOPLE = [
  ['R. Kelly', 0, 'Waist 34, inseam 30 unhemmed, shirt 16-34'],
  ['D. Mowrey', 0, 'Waist 38, inseam 32, shirt 17-35'],
  ['A. Shaffer', 1, 'Shirt L, trousers 34x30'],
  ['J. Puskar', 2, 'Shirt XL']
]
const personIds = PEOPLE.map(([name, ai, sizes]) =>
  run('INSERT INTO customer (name, agency_id, size_notes) VALUES (?, ?, ?)', name, agencyIds[ai], sizes).lastInsertRowid)

const pick = handle => get('SELECT * FROM product WHERE handle LIKE ? LIMIT 1', `%${handle}%`)

const ORDERS = [
  {
    ref: 'MT-D1001', person: 0, agency: 0, channel: 'counter', status: 'in-decoration', pay: 'invoiced', po: 'PO-88213',
    promised: '+3 days',
    lines: [
      { handle: 'elbeco-adu-ripstop-trousers', qty: 2, opts: [['Waist Size', '34'], ['Length', '30'], ['Color', 'Dark Navy']],
        jobs: [['hem', 'Hem to 30in finished, boot cut.', 1200], ['name-tape', 'KELLY — silver on navy.', 900]] },
      { handle: 'elbeco-tek3-uniform-shirt-l-s', qty: 2, opts: [['Shirt Size', '16'], ['Sleeve Length', '34']],
        jobs: [['patch', 'Township patch both sleeves per agency spec.', 1600]] }
    ]
  },
  {
    ref: 'MT-D1002', person: 2, agency: 1, channel: 'phone', status: 'awaiting-stock', pay: 'unpaid', po: '',
    promised: '+10 days',
    lines: [
      { handle: 'bugle-collar-brass-2', qty: 4, opts: [['Hardware Finish', 'Gold']], jobs: [] }
    ]
  },
  {
    ref: 'MT-D1003', person: 3, agency: 2, channel: 'web', status: 'ready', pay: 'paid', po: '',
    promised: '-1 days',
    lines: [
      { handle: 'pa-state-constable-ball-cap', qty: 1, opts: [], jobs: [] },
      { handle: 'pa-constable-cloth-badge', qty: 2, opts: [], jobs: [] }
    ]
  },
  {
    ref: 'MT-D1004', person: 1, agency: 0, channel: 'on-site-fitting', status: 'placed', pay: 'invoiced', po: 'PO-88240',
    promised: '+7 days',
    lines: [
      { handle: 'elbeco-shield-duty-jacket', qty: 1, opts: [['Alpha Size', 'XL']],
        jobs: [['patch', 'Township patch both sleeves.', 1600], ['name-tape', 'MOWREY.', 900]] }
    ]
  }
]

let made = 0
for (const o of ORDERS) {
  const lines = o.lines.map(l => ({ ...l, product: pick(l.handle) })).filter(l => l.product)
  if (!lines.length) { console.log('[seed] skipped ' + o.ref + ' — no matching products in catalog'); continue }

  const orderId = run(
    `INSERT INTO "order" (reference, customer_id, agency_id, channel, status, payment_status,
                          purchase_order_number, promised_at)
     VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now', ?))`,
    o.ref, personIds[o.person], agencyIds[o.agency], o.channel, o.status, o.pay, o.po, o.promised
  ).lastInsertRowid

  let subtotal = 0
  let decoration = 0
  for (const l of lines) {
    const unit = l.product.price_cents
    const lineTotal = unit * l.qty
    subtotal += lineTotal
    const lineId = run(
      `INSERT INTO order_line (order_id, product_id, name_at_sale, model_at_sale, unit_price_cents, quantity, line_total_cents)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      orderId, l.product.id, l.product.name, l.product.model, unit, l.qty, lineTotal
    ).lastInsertRowid

    for (const [name, value] of l.opts) {
      run('INSERT INTO order_line_option (order_line_id, option_name, value_label) VALUES (?, ?, ?)', lineId, name, value)
    }
    for (const [kind, instructions, price] of l.jobs) {
      decoration += price * l.qty
      run(`INSERT INTO decoration_job (order_line_id, kind, instructions, price_cents, status)
           VALUES (?, ?, ?, ?, ?)`, lineId, kind, instructions, price,
      o.status === 'ready' || o.status === 'collected' ? 'done' : 'queued')
    }

    if (['in-decoration', 'ready', 'collected', 'shipped'].includes(o.status)) {
      run(`INSERT INTO inventory_movement (product_id, delta, reason, order_id, note)
           VALUES (?, ?, 'sold', ?, 'demo seed')`, l.product.id, -l.qty, orderId)
    }
  }

  const tax = Math.round((subtotal + decoration) * 0.06)
  run(`UPDATE "order" SET subtotal_cents = ?, decoration_cents = ?, tax_cents = ?, total_cents = ? WHERE id = ?`,
    subtotal, decoration, tax, subtotal + decoration + tax, orderId)
  made++
}

console.log(`[seed] ${made} demonstration orders, ${AGENCIES.length} agencies, ${PEOPLE.length} people`)
db.close()
