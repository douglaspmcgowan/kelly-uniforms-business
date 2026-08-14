// Builds a Shopify product-import CSV from the OpenCart export.
//
// Run:  node ops/build-shopify-import.mjs
// Out:  PROJECT_DATA_ROOT/outputs/shopify-import/<date>/  (products.csv, properties.json, report.json)
//
// The output goes to PROJECT_DATA_ROOT rather than the repository. It carries no customer data, but
// it is a large generated artifact derived from a private export, and the repository owns source
// rather than generated bulk.
//
// ── The limit that shapes this whole file ────────────────────────────────────────────────────────
// Shopify allows a product THREE option groups. OpenCart allows any number, and M.T. Uniforms uses
// up to seven. Ten products exceed three groups and thirty-one exceed a sane variant count, with a
// worst case of 6,120 combinations on one pair of trousers (Braid x Color x Waist x Length).
//
// Rather than drop data or silently truncate, every option group that cannot be a Shopify variant
// is demoted to a LINE-ITEM PROPERTY. Shopify carries properties onto the order line natively, and
// theme/ already posts them as `properties[...]`, so the storefront needs no change. The customer
// still chooses; the difference is that a property does not carry its own SKU or stock.
//
// Demotion is deliberate and ordered, never arbitrary:
//   1. Groups that are genuinely stock-bearing keep variant status — size, colour, length, width.
//   2. Everything else is demoted first, largest-cardinality first, until the product fits.
//   3. Free-text groups (OpenCart `textarea`) are ALWAYS properties. A name tape is not a variant.
// report.json names every demotion so the decision is reviewable rather than buried.

import fs from 'node:fs'
import path from 'node:path'
import { loadCatalog, exportDir } from './parse-opencart.mjs'

const MAX_OPTION_GROUPS = 3
const MAX_VARIANTS = 2000

// Option names that describe a stock-bearing physical dimension. Matched case-insensitively as
// whole words so "Hat Size" and "Waist Size" match but "Hat Band" does not.
const STOCK_BEARING = /\b(size|color|colour|length|width|waist|inseam|neck|sleeve)\b/i

function planOptions (product) {
  const selectable = product.options.filter(o => o.values.length > 0)
  const freeText = product.options.filter(o => o.values.length === 0)

  // Free text can never be a variant.
  const properties = [...freeText]
  let variants = [...selectable]

  const combos = () => variants.reduce((a, o) => a * o.values.length, 1)
  const demote = () => {
    // Prefer demoting a non-stock-bearing group; among equals, demote the largest.
    const pool = variants.filter(o => !STOCK_BEARING.test(o.name))
    const from = pool.length ? pool : variants
    const victim = from.slice().sort((a, b) => b.values.length - a.values.length)[0]
    variants = variants.filter(o => o !== victim)
    properties.push(victim)
    return victim
  }

  const demoted = []
  while (variants.length > MAX_OPTION_GROUPS) demoted.push(demote())
  while (combos() > MAX_VARIANTS && variants.length > 1) demoted.push(demote())

  return { variants, properties, demoted }
}

function cartesian (groups) {
  return groups.reduce((acc, g) => acc.flatMap(row => g.values.map(v => [...row, v])), [[]])
}

const csvCell = (v) => {
  const s = String(v ?? '')
  return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s
}

const HEADERS = [
  'Handle', 'Title', 'Body (HTML)', 'Vendor', 'Product Category', 'Type', 'Tags', 'Published',
  'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value',
  'Variant SKU', 'Variant Grams', 'Variant Inventory Tracker', 'Variant Inventory Qty',
  'Variant Inventory Policy', 'Variant Fulfillment Service', 'Variant Price', 'Variant Compare At Price',
  'Variant Requires Shipping', 'Variant Taxable', 'Image Src', 'Image Position', 'Image Alt Text',
  'Gift Card', 'SEO Title', 'SEO Description', 'Status',
]

// OpenCart weights are in the store's weight class; class 1 is pounds on this install.
const toGrams = (lb) => Math.round(Number(lb || 0) * 453.592)

function optionPrice (base, v) {
  const delta = Number(v.price || 0)
  if (!delta) return base
  return v.pricePrefix === '-' ? base - delta : base + delta
}

const imageUrl = (p) => (p ? 'https://mtuniforms.com/image/' + p.split('/').map(encodeURIComponent).join('/') : '')

function build () {
  const catalog = loadCatalog()
  const rows = []
  const propertyMap = {}
  const report = { generated: new Date().toISOString().slice(0, 10), products: catalog.length, demotions: [], oversized: [], noHandle: [] }

  for (const p of catalog) {
    if (!p.handle) { report.noHandle.push(p.name); continue }
    const { variants, properties, demoted } = planOptions(p)

    if (demoted.length) {
      report.demotions.push({
        handle: p.handle,
        product: p.name,
        keptAsVariants: variants.map(o => o.name),
        demotedToProperties: demoted.map(o => `${o.name} (${o.values.length} values)`),
      })
    }
    if (properties.length) {
      propertyMap[p.handle] = properties.map(o => ({
        name: o.name,
        required: o.required,
        type: o.values.length ? 'select' : (o.type === 'textarea' ? 'text' : o.type),
        values: o.values.map(v => ({ label: v.name, priceDelta: (v.pricePrefix === '-' ? -1 : 1) * Number(v.price || 0) })),
      }))
    }

    const combos = variants.length ? cartesian(variants) : [[]]
    if (combos.length > MAX_VARIANTS) report.oversized.push({ handle: p.handle, variants: combos.length })

    const tags = [...new Set([...p.categories, p.brand].filter(Boolean))].join(', ')
    const images = [p.image, ...p.extraImages].filter(Boolean)

    combos.forEach((combo, i) => {
      const first = i === 0
      const price = combo.reduce((acc, v) => optionPrice(acc, v), p.price)
      const row = {
        Handle: p.handle,
        Title: first ? p.name : '',
        'Body (HTML)': first ? p.description : '',
        Vendor: first ? p.brand : '',
        'Product Category': '',
        Type: first ? (p.categories[0] || '') : '',
        Tags: first ? tags : '',
        Published: first ? (p.status ? 'TRUE' : 'FALSE') : '',
        'Variant SKU': p.sku || `${p.model}${combo.length ? '-' + combo.map(v => v.name.replace(/[^A-Za-z0-9]/g, '').slice(0, 6)).join('-') : ''}`,
        'Variant Grams': toGrams(p.weight),
        'Variant Inventory Tracker': 'shopify',
        // OpenCart stores stock at product level, not per option value, so the count cannot be
        // split across variants without inventing numbers. Every variant starts at 0 and is set by
        // the first real count. See SETUP.md — stock is a manual step.
        'Variant Inventory Qty': 0,
        'Variant Inventory Policy': 'continue',
        'Variant Fulfillment Service': 'manual',
        'Variant Price': price.toFixed(2),
        'Variant Compare At Price': '',
        'Variant Requires Shipping': 'TRUE',
        'Variant Taxable': 'TRUE',
        'Image Src': first ? imageUrl(p.image) : '',
        'Image Position': first && p.image ? 1 : '',
        'Image Alt Text': first ? p.name : '',
        'Gift Card': first ? 'FALSE' : '',
        'SEO Title': first ? (p.metaTitle || p.name) : '',
        'SEO Description': first ? p.metaDescription : '',
        Status: first ? (p.status ? 'active' : 'draft') : '',
      }
      variants.forEach((g, gi) => {
        row[`Option${gi + 1} Name`] = first ? g.name : ''
        row[`Option${gi + 1} Value`] = combo[gi]?.name || ''
      })
      rows.push(row)
    })

    // Extra gallery images ride on their own handle-only rows, which is how Shopify's CSV works.
    images.slice(1).forEach((img, n) => {
      rows.push({ Handle: p.handle, 'Image Src': imageUrl(img), 'Image Position': n + 2 })
    })
  }

  const outRoot = path.join(exportDir().replace(/inputs[\\/]opencart-export[\\/].*/, ''), 'outputs', 'shopify-import', report.generated)
  fs.mkdirSync(outRoot, { recursive: true })

  const csv = [HEADERS.join(',')]
    .concat(rows.map(r => HEADERS.map(h => csvCell(r[h])).join(',')))
    .join('\n')
  fs.writeFileSync(path.join(outRoot, 'products.csv'), csv, 'utf8')
  fs.writeFileSync(path.join(outRoot, 'line-item-properties.json'), JSON.stringify(propertyMap, null, 1))

  report.csvRows = rows.length
  report.productsWritten = new Set(rows.map(r => r.Handle)).size
  report.propertyProducts = Object.keys(propertyMap).length
  fs.writeFileSync(path.join(outRoot, 'report.json'), JSON.stringify(report, null, 1))

  console.log(JSON.stringify({
    out: outRoot,
    products: report.productsWritten,
    csvRows: report.csvRows,
    demotions: report.demotions.length,
    propertyProducts: report.propertyProducts,
    oversized: report.oversized.length,
    noHandle: report.noHandle.length,
  }, null, 1))
}

build()
