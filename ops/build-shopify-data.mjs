// Converts everything else in the OpenCart export into Shopify-ready form.
//
// Run:  node ops/build-shopify-data.mjs
// Out:  PROJECT_DATA_ROOT/outputs/shopify-import/<date>/
//
// `build-shopify-import.mjs` owns the product catalog. This owns the rest: customers, orders,
// redirects, and reviews. They are separate files because Shopify ingests them through four
// different doors, not because they are separate concerns.
//
// ── What Shopify will and will not accept ────────────────────────────────────────────────────────
//
//   customers.csv   Native import, Customers > Import. Ready to use as-is.
//   redirects.csv   Native import, Navigation > URL Redirects. Ready to use as-is.
//   reviews.csv     Judge.me / Shopify Product Reviews import shape. App-dependent, so the columns
//                   are the common denominator those apps accept.
//   orders.jsonl    NOT natively importable. Shopify has no order CSV import at any plan level;
//                   historical orders go through the Admin API or a migration app. This file is
//                   shaped for that, one order per line, and is deliberately not called a CSV so
//                   nobody tries to upload it and wonders why it fails.
//
// ── The privacy line ────────────────────────────────────────────────────────────────────────────
//
// customers.csv and orders.jsonl are real personal data — names, emails, phone numbers, addresses.
// They are written under PROJECT_DATA_ROOT and must never enter Git. Whether they are imported at
// all is a business decision recorded in SETUP.md, not a default step of the migration: importing
// them starts a fresh retention clock in a new system.
//
// Passwords are not exported. `parse-opencart.mjs` names the fields it keeps rather than deleting
// the ones it does not, so a sensitive column cannot arrive by default. Shopify cannot accept
// OpenCart password hashes anyway; imported customers set a new password on first login.

import fs from 'node:fs'
import path from 'node:path'
import { loadCustomers, loadOrders, loadReviews, loadUrls, loadCatalog, loadTestimonials, exportDir, localDate } from './parse-opencart.mjs'

const csvCell = (v) => {
  const s = String(v ?? '')
  return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s
}
const toCsv = (headers, rows) =>
  [headers.join(',')].concat(rows.map(r => headers.map(h => csvCell(r[h])).join(','))).join('\n')

/* ── customers ─────────────────────────────────────────────────────────────────────────────────── */

const CUSTOMER_HEADERS = [
  'First Name', 'Last Name', 'Email', 'Company', 'Address1', 'Address2', 'City', 'Province',
  'Province Code', 'Country', 'Country Code', 'Zip', 'Phone', 'Accepts Email Marketing',
  'Tags', 'Note', 'Tax Exempt',
]

function buildCustomers (customers) {
  const rows = customers
    .filter(c => c.email)
    .map(c => ({
      'First Name': c.firstName,
      'Last Name': c.lastName,
      Email: c.email,
      Company: c.company,
      Address1: c.address1,
      Address2: c.address2,
      City: c.city,
      Province: c.province,
      'Province Code': c.provinceCode,
      Country: c.country || 'United States',
      'Country Code': c.countryCode || 'US',
      Zip: c.zip,
      Phone: c.phone,
      // Shopify treats this as consent. OpenCart's newsletter flag is the only consent record that
      // exists, so anything else would be inventing permission the customer never gave.
      'Accepts Email Marketing': c.acceptsMarketing ? 'yes' : 'no',
      Tags: ['imported-from-opencart', c.active ? '' : 'inactive-in-opencart'].filter(Boolean).join(', '),
      Note: `OpenCart customer ${c.customerId}, joined ${String(c.createdAt).slice(0, 10)}`,
      'Tax Exempt': 'no',
    }))
  return { csv: toCsv(CUSTOMER_HEADERS, rows), count: rows.length }
}

/* ── orders ────────────────────────────────────────────────────────────────────────────────────── */

// OpenCart status -> what Shopify actually models. Shopify has no single "status" field: it has a
// financial status and a fulfillment status, and they are independent.
const STATUS_MAP = {
  Delivered: { financial: 'paid', fulfillment: 'fulfilled' },
  Shipped: { financial: 'paid', fulfillment: 'fulfilled' },
  Processing: { financial: 'paid', fulfillment: null },
  Complete: { financial: 'paid', fulfillment: 'fulfilled' },
  Canceled: { financial: 'voided', fulfillment: null },
  'Canceled Reversal': { financial: 'voided', fulfillment: null },
  Denied: { financial: 'voided', fulfillment: null },
  Failed: { financial: 'voided', fulfillment: null },
  Refunded: { financial: 'refunded', fulfillment: null },
  Returned: { financial: 'refunded', fulfillment: 'restocked' },
  Voided: { financial: 'voided', fulfillment: null },
  'Pending': { financial: 'pending', fulfillment: null },
  'Expired': { financial: 'voided', fulfillment: null },
}

function buildOrders (orders, catalog) {
  const handleByProductId = {}
  for (const p of catalog) handleByProductId[p.productId] = p.handle

  // Abandoned checkouts are excluded. OpenCart status 0 means the customer never completed the
  // order, so importing them would invent 347 sales that never happened.
  const real = orders.filter(o => !o.incomplete)

  const lines = real.map(o => {
    const mapped = STATUS_MAP[o.status] || { financial: 'pending', fulfillment: null }
    const findTotal = (code) => o.totals.find(t => t.code === code)?.value ?? 0
    return JSON.stringify({
      name: '#' + o.number,
      legacy_opencart_id: o.orderId,
      email: o.email,
      phone: o.phone,
      created_at: o.createdAt,
      updated_at: o.updatedAt,
      currency: o.currency,
      financial_status: mapped.financial,
      fulfillment_status: mapped.fulfillment,
      opencart_status: o.status,
      note: o.comment,
      tags: ['imported-from-opencart', `opencart-${o.status.toLowerCase().replace(/\s+/g, '-')}`],
      customer: { first_name: o.firstName, last_name: o.lastName, email: o.email },
      shipping_address: {
        first_name: o.firstName,
        last_name: o.lastName,
        company: o.shipping.company,
        address1: o.shipping.address1,
        address2: o.shipping.address2,
        city: o.shipping.city,
        province: o.shipping.province,
        zip: o.shipping.zip,
        country: o.shipping.country,
      },
      line_items: o.lines.map(l => ({
        title: l.name,
        sku: l.model,
        quantity: l.quantity,
        price: l.price.toFixed(2),
        product_handle: handleByProductId[l.productId] || null,
        // Order-line options become Shopify line-item properties, which is exactly what they are:
        // a record of what the customer chose, attached to the line rather than to the product.
        properties: l.options.map(op => ({ name: op.name, value: op.value })),
      })),
      shipping_lines: [{ title: o.shippingMethod, price: findTotal('shipping').toFixed(2) }],
      total_tax: findTotal('tax').toFixed(2),
      subtotal_price: findTotal('sub_total').toFixed(2),
      total_price: o.total.toFixed(2),
      payment_gateway_names: [o.paymentMethod],
    })
  })

  return { jsonl: lines.join('\n'), count: real.length, excluded: orders.length - real.length }
}

/* ── redirects ─────────────────────────────────────────────────────────────────────────────────── */

function buildRedirects (urls, catalog) {
  const handles = new Set(catalog.map(p => p.handle).filter(Boolean))
  const rows = []
  const seen = new Set()
  const add = (from, to) => {
    const f = '/' + String(from).replace(/^\/+/, '')
    if (seen.has(f) || f === '/') return
    seen.add(f)
    rows.push({ Redirect: f, Target: to })
  }

  // The existing 301s carry forward as-is; they already encode decisions someone made.
  for (const r of urls.redirects) add(r.from, '/' + String(r.to).replace(/^\/+/, ''))

  // OpenCart serves products at a bare keyword (/some-product). Shopify serves them at
  // /products/<handle>. Where the handle matches the old keyword the path still changes, so every
  // product needs a redirect even though the slug is identical — this is the step migrations skip
  // and then wonder where their search traffic went.
  for (const s of urls.seo) {
    if (!s.query || !s.keyword) continue
    const [kind, id] = s.query.split('=')
    if (kind === 'product_id') {
      const p = catalog.find(x => x.productId === id)
      if (p && handles.has(p.handle)) add(s.keyword, `/products/${p.handle}`)
    } else if (kind === 'path') {
      add(s.keyword, `/collections/${s.keyword.split('/').pop()}`)
    } else if (kind === 'information_id') {
      add(s.keyword, `/pages/${s.keyword}`)
    } else if (kind === 'manufacturer_id') {
      add(s.keyword, `/collections/${s.keyword}`)
    }
  }

  return { csv: toCsv(['Redirect', 'Target'], rows), count: rows.length }
}

/* ── reviews ───────────────────────────────────────────────────────────────────────────────────── */

const REVIEW_HEADERS = [
  'product_handle', 'rating', 'title', 'author', 'email', 'body', 'created_at', 'published',
]

function buildReviews (reviews) {
  const usable = reviews.filter(r => r.approved && r.productHandle)
  const rows = usable.map(r => ({
    product_handle: r.productHandle,
    rating: r.rating,
    title: '',
    author: r.author,
    // No email is exported. The review table stores a customer_id, not an address, and inventing
    // one would attach a real person's identity to a public review they did not consent to publish
    // under it. Review apps accept a blank email.
    email: '',
    body: r.body,
    created_at: r.createdAt,
    published: 'true',
  }))
  return {
    csv: toCsv(REVIEW_HEADERS, rows),
    count: rows.length,
    fiveStar: rows.filter(r => Number(r.rating) === 5).length,
  }
}

/* ── run ───────────────────────────────────────────────────────────────────────────────────────── */

function main () {
  const stamp = localDate()
  const dataRoot = exportDir().replace(/inputs[\\/]opencart-export[\\/].*/, '')
  const out = path.join(dataRoot, 'outputs', 'shopify-import', stamp)
  fs.mkdirSync(out, { recursive: true })

  const catalog = loadCatalog()
  const customers = buildCustomers(loadCustomers())
  const orders = buildOrders(loadOrders(), catalog)
  const redirects = buildRedirects(loadUrls(), catalog)
  const reviews = buildReviews(loadReviews())
  const testimonials = loadTestimonials()

  fs.writeFileSync(path.join(out, 'customers.csv'), customers.csv, 'utf8')
  fs.writeFileSync(path.join(out, 'orders.jsonl'), orders.jsonl, 'utf8')
  fs.writeFileSync(path.join(out, 'redirects.csv'), redirects.csv, 'utf8')
  fs.writeFileSync(path.join(out, 'reviews.csv'), reviews.csv, 'utf8')

  const summary = {
    generated: stamp,
    out,
    customers: { rows: customers.count, importVia: 'Shopify Customers > Import (native CSV)' },
    orders: {
      rows: orders.count,
      excludedAbandoned: orders.excluded,
      importVia: 'Admin API or migration app — Shopify has NO native order CSV import',
    },
    redirects: { rows: redirects.count, importVia: 'Shopify Navigation > URL Redirects (native CSV)' },
    reviews: { rows: reviews.count, fiveStar: reviews.fiveStar, importVia: 'Judge.me / Product Reviews app' },
    testimonialsDeliberatelyExcluded: {
      rows: testimonials.length,
      reason: 'Journal 3 demo placeholders under invented names, not real customer words',
    },
  }
  fs.writeFileSync(path.join(out, 'data-report.json'), JSON.stringify(summary, null, 1))
  console.log(JSON.stringify(summary, null, 1))
}

main()
