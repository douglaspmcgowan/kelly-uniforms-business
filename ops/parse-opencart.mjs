// Parses the OpenCart backup SQL into plain JS objects.
//
// The export is TRUNCATE + INSERT statements with no CREATE TABLE, so the column names come from
// each INSERT's own column list rather than from a schema. That is the whole reason this file
// exists instead of a MySQL load: no server, no credentials, no schema reconstruction.
//
// It reads from PROJECT_DATA_ROOT and never from the repository. The export holds real customer
// names, addresses, and payment records and must not be copied into Git.

import fs from 'node:fs'
import path from 'node:path'

const CANDIDATE_ROOTS = [
  process.env.PROJECT_DATA_ROOT,
  'C:/Users/dougl/Data/Projects/kelly-uniforms-business',
  path.join(process.env.USERPROFILE || process.env.HOME || '.', 'Data/Projects/kelly-uniforms-business'),
].filter(Boolean)

export function exportDir (stamp = '2026-08-14') {
  for (const root of CANDIDATE_ROOTS) {
    const dir = path.join(root, 'inputs/opencart-export', stamp)
    if (fs.existsSync(dir)) return dir
  }
  throw new Error('OpenCart export not found. Set PROJECT_DATA_ROOT to the data root.')
}

// A single INSERT's VALUES list, split on commas that are not inside a quoted string.
// OpenCart escapes with backslashes, so a quote preceded by an odd run of backslashes is literal.
function splitValues (body) {
  const out = []
  let cur = ''
  let inStr = false
  for (let i = 0; i < body.length; i++) {
    const c = body[i]
    if (inStr) {
      if (c === '\\') { cur += c + (body[++i] ?? ''); continue }
      if (c === "'") { inStr = false; continue }
      cur += c
    } else if (c === "'") {
      inStr = true
    } else if (c === ',') {
      out.push(cur.trim()); cur = ''
    } else {
      cur += c
    }
  }
  out.push(cur.trim())
  return out.map(v => (v === 'NULL' ? null : unescapeSql(v)))
}

function unescapeSql (v) {
  return v
    .replace(/\\n/g, '\n').replace(/\\r/g, '\r').replace(/\\t/g, '\t')
    .replace(/\\'/g, "'").replace(/\\"/g, '"').replace(/\\\\/g, '\\')
}

/** Read every row of one table across all chunk files. */
export function readTable (tableName, files) {
  const dir = exportDir()
  const rows = []
  const re = new RegExp('^INSERT INTO `' + tableName + '` \\(([^)]*)\\) VALUES \\((.*)\\);\\s*$')
  for (const file of files) {
    const full = path.join(dir, file)
    if (!fs.existsSync(full)) continue
    for (const line of fs.readFileSync(full, 'utf8').split('\n')) {
      const m = re.exec(line)
      if (!m) continue
      const cols = m[1].split(',').map(c => c.trim().replace(/`/g, ''))
      const vals = splitValues(m[2])
      const row = {}
      cols.forEach((c, i) => { row[c] = vals[i] })
      rows.push(row)
    }
  }
  return rows
}

export const CATALOG = ['mt-03-catalog.sql']
export const ORDERS = ['mt-01-orders.sql']
export const CUSTOMERS = ['mt-02-customers.sql']
export const CONTENT = ['mt-04-content-seo.sql']

/** The full catalog, joined: products with descriptions, categories, options, and images. */
export function loadCatalog () {
  const products = readTable('oc_product', CATALOG)
  const descs = index(readTable('oc_product_description', CATALOG), 'product_id')
  const cats = index(readTable('oc_category_description', CATALOG), 'category_id')
  const p2c = readTable('oc_product_to_category', CATALOG)
  const mans = index(readTable('oc_manufacturer', CATALOG), 'manufacturer_id')
  const opts = index(readTable('oc_option_description', CATALOG), 'option_id')
  // `type` (select/radio/checkbox/text/textarea) lives on oc_option, not oc_product_option.
  const optTypes = index(readTable('oc_option', CATALOG), 'option_id')
  const optVals = index(readTable('oc_option_value_description', CATALOG), 'option_value_id')
  const pOpts = readTable('oc_product_option', CATALOG)
  const pOptVals = readTable('oc_product_option_value', CATALOG)
  const images = readTable('oc_product_image', CATALOG)
  const seo = readTable('oc_seo_url', CONTENT).filter(r => (r.query || '').startsWith('product_id='))

  const catByProduct = groupBy(p2c, 'product_id')
  const optByProduct = groupBy(pOpts, 'product_id')
  const valByProductOption = groupBy(pOptVals, 'product_option_id')
  const imgByProduct = groupBy(images, 'product_id')
  const seoByProduct = {}
  for (const s of seo) seoByProduct[s.query.split('=')[1]] = s.keyword

  return products.map(p => {
    const d = descs[p.product_id] || {}
    return {
      productId: p.product_id,
      model: p.model,
      sku: p.sku || '',
      handle: seoByProduct[p.product_id] || '',
      name: decodeEntities(d.name || ''),
      // OpenCart stores the description entity-encoded (`&lt;p&gt;`) and decodes it on output.
      // Shopify's Body (HTML) expects real HTML, so it is decoded here rather than shipped as
      // literal escaped text the customer would read as markup.
      description: decodeEntities(d.description || ''),
      metaTitle: decodeEntities(d.meta_title || ''),
      metaDescription: decodeEntities(d.meta_description || ''),
      price: Number(p.price || 0),
      quantity: Number(p.quantity || 0),
      status: p.status === '1',
      weight: Number(p.weight || 0),
      weightClassId: p.weight_class_id,
      image: p.image || '',
      dateAvailable: p.date_available,
      brand: mans[p.manufacturer_id]?.name || '',
      // Deduplicated: a product is commonly filed under several category ids that share one display
      // name, because the tree repeats a name at more than one level.
      categories: [...new Set((catByProduct[p.product_id] || [])
        .map(r => decodeEntities(cats[r.category_id]?.name || ''))
        .filter(Boolean))],
      extraImages: (imgByProduct[p.product_id] || [])
        .sort((a, b) => Number(a.sort_order) - Number(b.sort_order))
        .map(r => r.image).filter(Boolean),
      options: (optByProduct[p.product_id] || []).map(po => ({
        productOptionId: po.product_option_id,
        name: decodeEntities(opts[po.option_id]?.name || ''),
        type: optTypes[po.option_id]?.type || 'select',
        required: po.required === '1',
        // A free-text option carries its default in `value` and has no value rows.
        defaultValue: po.value || '',
        values: (valByProductOption[po.product_option_id] || [])
          .sort((a, b) => Number(a.sort_order) - Number(b.sort_order))
          .map(pv => ({
            name: decodeEntities(optVals[pv.option_value_id]?.name || ''),
            quantity: Number(pv.quantity || 0),
            price: Number(pv.price || 0),
            pricePrefix: pv.price_prefix,
          })),
      })),
    }
  })
}

function index (rows, key) {
  const out = {}
  for (const r of rows) out[r[key]] = r
  return out
}

function groupBy (rows, key) {
  const out = {}
  for (const r of rows) (out[r[key]] ||= []).push(r)
  return out
}

function decodeEntities (s) {
  return String(s)
    .replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#039;/g, "'")
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&nbsp;/g, ' ')
}
