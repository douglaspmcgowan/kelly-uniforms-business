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

/**
 * The dated export folder every loader reads from.
 *
 * Resolution order: an explicit `MT_EXPORT_DIR`, then a caller-named stamp, then the newest dated
 * folder found. The stamp used to be a hardcoded default, which meant the next export silently
 * left every consumer building from the previous snapshot — two artifacts from two different days
 * with nothing saying so. `MT_EXPORT_DIR` is the same variable `preview/make-catalog.mjs` already
 * honoured, so both halves of the pipeline now pin to one export the same way.
 */
export function exportDir (stamp = process.env.MT_EXPORT_STAMP || null) {
  if (process.env.MT_EXPORT_DIR) return process.env.MT_EXPORT_DIR
  for (const root of CANDIDATE_ROOTS) {
    const base = path.join(root, 'inputs/opencart-export')
    if (!fs.existsSync(base)) continue
    if (stamp) {
      const dir = path.join(base, stamp)
      if (fs.existsSync(dir)) return dir
      continue
    }
    const dated = fs.readdirSync(base)
      .filter(d => /^\d{4}-\d{2}-\d{2}$/.test(d) && fs.statSync(path.join(base, d)).isDirectory())
      .sort()
    if (dated.length) return path.join(base, dated[dated.length - 1])
  }
  throw new Error('OpenCart export not found. Set PROJECT_DATA_ROOT or MT_EXPORT_DIR.')
}

/**
 * Today's date in the operator's own timezone, `YYYY-MM-DD`.
 *
 * `toISOString()` is UTC, so a run after 8pm Eastern stamps the output folder with tomorrow's date
 * — two runs on one working evening land in two folders, and the one that looks newest is not the
 * one just produced. Both build scripts name their output folder from this.
 */
export function localDate (d = new Date()) {
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
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
export const SYSTEM = ['mt-07-system-config.sql']

/**
 * The live store is `store_id = 0`. This install carries a second storefront (`store_id = 2`) with
 * its own keyword for every product, and the two disagree on 26 of them — product 99 is
 * `usps-baseball-cap-summer-pbcs` live and `usps-letter-carrier-mailman-postal-baseball-cap-summer`
 * on store 2. Taking whichever row the file happened to list last picked the wrong URL for 35
 * products, which would have pointed the redirect map at paths that were never the live ones.
 */
const LIVE_STORE_ID = '0'

function productSeo () {
  return readTable('oc_seo_url', CONTENT)
    .filter(r => (r.query || '').startsWith('product_id=') && r.store_id === LIVE_STORE_ID)
}

/**
 * Weight classes, as grams per unit. OpenCart stores `value` as units-per-kilogram — 2.2046 for
 * pounds, 35.274 for ounces — so the conversion is derived from the store's own table rather than
 * assumed. It used to be a flat pounds multiplier, which shipped 142 ounce-weighted products at
 * 16x their real weight and mispriced carrier-calculated shipping on every one of them.
 */
export function loadWeightClasses () {
  const out = {}
  for (const w of readTable('oc_weight_class', SYSTEM)) {
    const perKg = Number(w.value || 0)
    if (perKg > 0) out[w.weight_class_id] = 1000 / perKg
  }
  return out
}

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
  const seo = productSeo()

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
            // `rowId` is unique per row by construction, `valueId` is the shared value it points at.
            // Two rows on one product can carry the same label — a boot listed at "10.5" twice —
            // so anything that must be unique (a SKU, a variant key) uses rowId, never the label.
            rowId: pv.product_option_value_id,
            valueId: pv.option_value_id,
            // An empty name means the join found no description row for this value id. It is left
            // empty rather than invented; `build-shopify-import.mjs` reports it, because a blank
            // Option Value is a Shopify import error and an unlabeled choice on the storefront.
            name: decodeEntities(optVals[pv.option_value_id]?.name || ''),
            quantity: Number(pv.quantity || 0),
            price: Number(pv.price || 0),
            pricePrefix: pv.price_prefix,
          })),
      })),
    }
  })
}

/* ── The rest of the store, beyond the catalog ────────────────────────────────────────────────── */

/** Real customer reviews. `oc_testimonial` is NOT here on purpose — see loadTestimonials. */
export function loadReviews () {
  const products = index(readTable('oc_product_description', CATALOG), 'product_id')
  const seo = {}
  for (const s of productSeo()) seo[s.query.split('=')[1]] = s.keyword
  return readTable('oc_review', CONTENT).map(r => ({
    reviewId: r.review_id,
    productId: r.product_id,
    productName: decodeEntities(products[r.product_id]?.name || ''),
    productHandle: seo[r.product_id] || '',
    author: decodeEntities(r.author || ''),
    body: decodeEntities(r.text || ''),
    rating: Number(r.rating || 0),
    approved: r.status === '1',
    createdAt: r.date_added,
  }))
}

/**
 * Journal 3's demo testimonials. Exported so callers can SEE they are placeholders, never to ship.
 * Every row is Lorem Ipsum under an invented name ("Rebecka Filson", "Nathanael Jaworski"), pointing
 * at one shared stock image that is itself a dead reference. Showing these to a customer would put
 * fabricated praise on a real store, so nothing in the storefront may read this.
 */
export function loadTestimonials () {
  return readTable('oc_testimonial_description', CONTENT).map(t => ({
    id: t.testimonial_id,
    name: t.customer_name,
    isLoremIpsum: /lorem ipsum|consectetur adipiscing|proin gravida/i.test(t.content || ''),
  }))
}

/** Customers, with credentials structurally excluded rather than filtered downstream. */
export function loadCustomers () {
  const addrs = groupBy(readTable('oc_address', CUSTOMERS), 'customer_id')
  const zones = index(readTable('oc_zone', ['mt-07-system-config.sql']), 'zone_id')
  const countries = index(readTable('oc_country', ['mt-07-system-config.sql']), 'country_id')
  return readTable('oc_customer', CUSTOMERS).map(c => {
    // `password` and `salt` are never read off the row. Naming the fields we keep, rather than
    // deleting the ones we do not, means a new sensitive column cannot leak in by default.
    const primary = (addrs[c.customer_id] || []).find(a => a.address_id === c.address_id)
      || (addrs[c.customer_id] || [])[0] || {}
    return {
      customerId: c.customer_id,
      firstName: decodeEntities(c.firstname || ''),
      lastName: decodeEntities(c.lastname || ''),
      email: c.email || '',
      phone: c.telephone || '',
      acceptsMarketing: c.newsletter === '1',
      createdAt: c.date_added,
      active: c.status === '1',
      company: decodeEntities(primary.company || ''),
      address1: decodeEntities(primary.address_1 || ''),
      address2: decodeEntities(primary.address_2 || ''),
      city: decodeEntities(primary.city || ''),
      zip: primary.postcode || '',
      province: zones[primary.zone_id]?.name || '',
      provinceCode: zones[primary.zone_id]?.code || '',
      country: countries[primary.country_id]?.name || '',
      countryCode: countries[primary.country_id]?.iso_code_2 || '',
      addressCount: (addrs[c.customer_id] || []).length,
    }
  })
}

/** Orders with their lines, the options chosen on each line, and their totals. */
export function loadOrders () {
  const statuses = index(readTable('oc_order_status', ORDERS), 'order_status_id')
  const lines = groupBy(readTable('oc_order_product', ORDERS), 'order_id')
  const opts = groupBy(readTable('oc_order_option', ORDERS), 'order_product_id')
  const totals = groupBy(readTable('oc_order_total', ORDERS), 'order_id')

  return readTable('oc_order', ORDERS).map(o => ({
    orderId: o.order_id,
    number: (o.invoice_prefix || '') + (o.invoice_no && o.invoice_no !== '0' ? o.invoice_no : o.order_id),
    email: o.email || '',
    phone: o.telephone || '',
    firstName: decodeEntities(o.firstname || ''),
    lastName: decodeEntities(o.lastname || ''),
    createdAt: o.date_added,
    updatedAt: o.date_modified,
    statusId: o.order_status_id,
    status: statuses[o.order_status_id]?.name || '',
    // order_status_id 0 is OpenCart's "incomplete" — an abandoned checkout, never a sale.
    incomplete: o.order_status_id === '0',
    total: Number(o.total || 0),
    currency: o.currency_code || 'USD',
    paymentMethod: decodeEntities(o.payment_method || ''),
    shippingMethod: decodeEntities(o.shipping_method || ''),
    comment: decodeEntities(o.comment || ''),
    shipping: {
      company: decodeEntities(o.shipping_company || ''),
      address1: decodeEntities(o.shipping_address_1 || ''),
      address2: decodeEntities(o.shipping_address_2 || ''),
      city: decodeEntities(o.shipping_city || ''),
      zip: o.shipping_postcode || '',
      province: o.shipping_zone || '',
      country: o.shipping_country || '',
    },
    totals: (totals[o.order_id] || [])
      .sort((a, b) => Number(a.sort_order) - Number(b.sort_order))
      .map(t => ({ code: t.code, title: decodeEntities(t.title || ''), value: Number(t.value || 0) })),
    lines: (lines[o.order_id] || []).map(l => ({
      productId: l.product_id,
      name: decodeEntities(l.name || ''),
      model: l.model,
      quantity: Number(l.quantity || 0),
      price: Number(l.price || 0),
      total: Number(l.total || 0),
      options: (opts[l.order_product_id] || []).map(op => ({
        name: decodeEntities(op.name || ''),
        value: decodeEntities(op.value || ''),
        type: op.type,
      })),
    })),
  }))
}

/** Existing SEO paths and 301s, for the redirect map a migration lives or dies by. */
export function loadUrls () {
  return {
    // Live store only. Store 2's keywords are real paths on a storefront that is not this one, and
    // redirecting them onto Shopify handles would invent traffic history the live site never had.
    seo: readTable('oc_seo_url', CONTENT)
      .filter(s => s.store_id === LIVE_STORE_ID)
      .map(s => ({ query: s.query, keyword: s.keyword })),
    redirects: readTable('oc_301redirect', CONTENT).map(r => ({ from: r.url_from, to: r.url_to })),
  }
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
