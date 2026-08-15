// Builds a Shopify product-import CSV from the OpenCart export.
//
// Run:  node ops/build-shopify-import.mjs
// Out:  PROJECT_DATA_ROOT/outputs/shopify-import/<date>/  (products.csv, line-item-properties.json, report.json)
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
import { loadCatalog, exportDir, localDate, loadWeightClasses } from './parse-opencart.mjs'

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

// Grams, converted through the store's OWN weight-class table rather than an assumed unit. This
// catalog mixes classes: 265 products are pounds and 142 are ounces. Converting everything as
// pounds shipped those 142 at 16x their real weight, which mispriced carrier-calculated shipping
// on every order containing one. An unrecognised class is a hard failure, never a silent guess.
const WEIGHT_CLASSES = loadWeightClasses()
function toGrams (weight, classId) {
  const gramsPerUnit = WEIGHT_CLASSES[classId]
  if (!gramsPerUnit) throw new Error(`Unknown weight_class_id ${classId} — refusing to guess a unit.`)
  return Math.round(Number(weight || 0) * gramsPerUnit)
}

const skuBase = (p) => (p.sku || p.model || `oc-${p.productId}`).trim()

/* Unique across the whole import, not merely within a product. Two distinct products can share a
   model number — three do here — so a base that collides is disambiguated with the OpenCart product
   id, which is unique by definition. `used` is passed in so the check is the same object that
   decides, rather than a report written after the fact. */
function skuFor (p, combo, used) {
  const base = combo.length ? `${skuBase(p)}-${combo.map(v => v.rowId).join('-')}` : skuBase(p)
  const sku = used.has(base) ? `${base}-${p.productId}` : base
  used.add(sku)
  return sku
}

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
  const usedSkus = new Set()
  const report = { generated: localDate(), products: catalog.length, demotions: [], pricedDemotions: [], oversized: [], noHandle: [], blankOptionValues: [], duplicateOptionLabels: [], duplicateSkus: [] }

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
      // A line-item property carries no money. Where a demoted group had a surcharge, the customer
      // picks the option and Shopify charges nothing for it — a $56.99 hat visor sold at $0. This
      // is the real cost of demotion and it is named here rather than left to be discovered on an
      // order. MIGRATION-RUNBOOK.md stage 2 carries the same warning.
      for (const o of demoted) {
        const max = Math.max(0, ...o.values.map(v => Number(v.price || 0)))
        if (max > 0) report.pricedDemotions.push({ handle: p.handle, option: o.name, maxSurcharge: max })
      }
    }
    for (const o of p.options) {
      for (const v of o.values) {
        if (!v.name) report.blankOptionValues.push({ handle: p.handle, option: o.name, valueId: v.valueId })
      }
      const labels = o.values.map(v => v.name)
      if (new Set(labels).size !== labels.length) {
        report.duplicateOptionLabels.push({ handle: p.handle, option: o.name })
      }
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
        // Unique per variant, always. The product-level `sku` used to be copied onto every row,
        // so all 1,020 rows of one product carried one SKU and inventory could not tell a 32x30
        // from a 44x36. The option-value row ids are unique by construction, which the truncated
        // labels were not — "Brushed Silver W/Polished Edge" and "Brushed Gold W/Polished Edge"
        // both collapsed to `Brushe`.
        'Variant SKU': skuFor(p, combo, usedSkus),
        'Variant Grams': toGrams(p.weight, p.weightClassId),
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

  const skus = rows.map(r => r['Variant SKU']).filter(Boolean)
  const skuSeen = new Set()
  for (const sku of skus) {
    if (skuSeen.has(sku)) report.duplicateSkus.push(sku)
    skuSeen.add(sku)
  }

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
    pricedDemotions: report.pricedDemotions.length,
    blankOptionValues: report.blankOptionValues.length,
    duplicateOptionLabels: report.duplicateOptionLabels.length,
    duplicateSkus: report.duplicateSkus.length,
  }, null, 1))
}

build()
