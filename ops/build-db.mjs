/* Builds the operations database from the extracted catalog.
 *
 * The database file is runtime data and lives under PROJECT_DATA_ROOT, never in Git. Catalog facts
 * come from the public extraction; inventory counts come from the authenticated admin export when
 * one is present, and are simply left at zero when it is not — an absent count is recorded as
 * absent rather than invented.
 *
 *   node ops/build-db.mjs
 *
 * Env:
 *   PROJECT_DATA_ROOT  defaults to %USERPROFILE%\Data\Projects\kelly-uniforms-business
 *   MT_EXPORT_DIR      the dated export folder; defaults to the newest under inputs/opencart-export
 */
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { DatabaseSync } from 'node:sqlite'
import { fileURLToPath } from 'node:url'

const HERE = path.dirname(fileURLToPath(import.meta.url))

// PROJECT_DATA_ROOT is the declared owner of this project's runtime data. Fall back to the
// conventional location under the home directory when it is unset or points somewhere that does
// not hold an export, so the script works on a fresh machine without a shell profile.
const CANDIDATE_ROOTS = [
  process.env.PROJECT_DATA_ROOT,
  path.join(os.homedir(), 'Data', 'Projects', 'kelly-uniforms-business')
].filter(Boolean)

function newestExport () {
  for (const root of CANDIDATE_ROOTS) {
    const base = path.join(root, 'inputs', 'opencart-export')
    if (!fs.existsSync(base)) continue
    const dirs = fs.readdirSync(base).filter(d => /^\d{4}-\d{2}-\d{2}$/.test(d)).sort()
    if (dirs.length) return path.join(base, dirs[dirs.length - 1])
  }
  return null
}

const SRC = process.env.MT_EXPORT_DIR || newestExport()
// The database belongs beside the export it was built from.
const ROOT = SRC ? path.resolve(SRC, '..', '..', '..') : CANDIDATE_ROOTS[CANDIDATE_ROOTS.length - 1]
if (!SRC || !fs.existsSync(path.join(SRC, 'products-public.json'))) {
  console.error('No catalog export found. Expected products-public.json under', SRC || '(none)')
  process.exit(1)
}

const products = JSON.parse(fs.readFileSync(path.join(SRC, 'products-public.json'), 'utf8'))

const dbDir = path.join(ROOT, 'db')
fs.mkdirSync(dbDir, { recursive: true })
const dbPath = path.join(dbDir, 'operations.sqlite')

// The previous database is set aside, not deleted — but a SQLite database is up to three files, and
// renaming only the main one left `operations.sqlite-wal` and `-shm` in place for the NEW database
// to adopt. SQLite would then replay the OLD write-ahead log over a freshly created file. Check the
// WAL back into the main file first so the archived copy is complete, then move all three together.
let archivedAs = null
if (fs.existsSync(dbPath)) {
  const stamp = new Date().toISOString().replace(/[:.]/g, '-')
  const prior = new DatabaseSync(dbPath)
  try { prior.exec('PRAGMA wal_checkpoint(TRUNCATE)') } finally { prior.close() }
  archivedAs = path.join(dbDir, `operations.${stamp}.sqlite`)
  for (const suffix of ['', '-wal', '-shm']) {
    if (fs.existsSync(dbPath + suffix)) fs.renameSync(dbPath + suffix, archivedAs + suffix)
  }
  console.log('[db] existing database kept as operations.' + stamp + '.sqlite')
}

// A failure partway through the load used to leave the transaction open, a half-written database in
// place, and the only good copy renamed away under a timestamp nobody would think to look for.
function abort (err) {
  try { db.exec('ROLLBACK') } catch {}
  try { db.close() } catch {}
  for (const suffix of ['', '-wal', '-shm']) {
    if (fs.existsSync(dbPath + suffix)) fs.rmSync(dbPath + suffix)
  }
  if (archivedAs) {
    for (const suffix of ['', '-wal', '-shm']) {
      if (fs.existsSync(archivedAs + suffix)) fs.renameSync(archivedAs + suffix, dbPath + suffix)
    }
    console.error('[db] build failed; the previous database has been restored.')
  }
  console.error(err.stack || String(err))
  process.exit(1)
}

const db = new DatabaseSync(dbPath)
db.exec(fs.readFileSync(path.join(HERE, 'schema.sql'), 'utf8'))

const cents = n => Math.round(Number(n || 0) * 100)
const slug = s => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')

const insProduct = db.prepare(`INSERT INTO product
  (source_product_id, handle, name, model, brand, weight, price_cents, image_url, description_html)
  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`)
const insCategory = db.prepare('INSERT OR IGNORE INTO category (name, handle) VALUES (?, ?)')
const getCategory = db.prepare('SELECT id FROM category WHERE handle = ?')
const insProdCat = db.prepare('INSERT OR IGNORE INTO product_category (product_id, category_id) VALUES (?, ?)')
const insOption = db.prepare(`INSERT INTO product_option
  (product_id, source_option_id, name, kind, required, position) VALUES (?, ?, ?, ?, ?, ?)`)
const insValue = db.prepare(`INSERT INTO product_option_value
  (option_id, source_value_id, label, price_delta_cents, position) VALUES (?, ?, ?, ?, ?)`)
const insInventory = db.prepare('INSERT INTO inventory (product_id, on_hand, reorder_point) VALUES (?, ?, ?)')

const KINDS = new Set(['select', 'radio', 'checkbox', 'text', 'textarea', 'date', 'file'])

db.exec('BEGIN')
let optionCount = 0
let valueCount = 0
try {
  for (const p of products) {
    if (p.price == null || !p.handle) continue
    const { lastInsertRowid: productId } = insProduct.run(
      p.productId, p.handle, p.name, p.model || '', p.brand || '', p.weight || '',
      cents(p.price), p.image || '', p.descriptionHtml || ''
    )

    for (const c of p.categories || []) {
      const h = slug(c.name)
      insCategory.run(c.name, h)
      insProdCat.run(productId, getCategory.get(h).id)
    }

    ;(p.options || []).forEach((o, i) => {
      const kind = KINDS.has(o.type) ? o.type : 'select'
      const { lastInsertRowid: optionId } = insOption.run(
        productId, o.optionId || '', o.name || 'Option', kind, o.required ? 1 : 0, i
      )
      optionCount++
      ;(o.values || []).forEach((v, j) => {
        insValue.run(optionId, v.valueId || '', v.label, cents(v.priceDelta), j)
        valueCount++
      })
    })

    // No authenticated inventory export is wired in yet, so counts start at zero and are recorded as
    // unknown rather than guessed. counted_at stays null until a real count lands.
    insInventory.run(productId, 0, 0)
  }
  db.exec('COMMIT')
} catch (err) {
  abort(err)
}

const one = sql => db.prepare(sql).get()
console.log('[db] ' + dbPath)
console.log('[db] products        ', one('SELECT COUNT(*) n FROM product').n)
console.log('[db] categories      ', one('SELECT COUNT(*) n FROM category').n)
console.log('[db] option groups   ', optionCount)
console.log('[db] option values   ', valueCount)
console.log('[db] free-text options', one('SELECT COUNT(*) n FROM v_free_text_options').n)
for (const r of db.prepare('SELECT name, option_name, kind FROM v_free_text_options').all()) {
  console.log('        - ' + r.name + ' -> ' + r.option_name + ' (' + r.kind + ')')
}
db.close()
