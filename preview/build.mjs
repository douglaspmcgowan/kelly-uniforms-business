/* Static renderer for the M.T. Uniforms theme.
 *
 * This is deliberately not a second storefront. It renders the SAME files in ../theme that a
 * Shopify store would render, through liquidjs plus the small set of Shopify objects and filters
 * the theme actually uses. What you see in the preview is what the theme does on Shopify; the
 * only difference is that commerce_mode is 'local', so the cart lives in the browser and checkout
 * hands the order to the store by email.
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { Liquid } from 'liquidjs'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const THEME = path.join(HERE, '..', 'theme')
const OUT = path.join(HERE, 'dist')
const CATALOG = JSON.parse(fs.readFileSync(path.join(HERE, 'data', 'catalog.json'), 'utf8'))

const engine = new Liquid({
  root: [path.join(THEME, 'sections'), path.join(THEME, 'snippets'), path.join(THEME, 'templates'), THEME],
  extname: '.liquid',
  jekyllInclude: false,
  strictFilters: false,
  strictVariables: false
})

/* ------------------------------------------------------------- Shopify shims */

const money = c => '$' + ((Number(c) || 0) / 100).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')

engine.registerFilter('money', money)
engine.registerFilter('money_with_sign', c => (Number(c) < 0 ? '-' : '+') + money(Math.abs(Number(c) || 0)))
engine.registerFilter('image_url', (src) => src || '')
engine.registerFilter('asset_url', a => '/assets/' + a)
engine.registerFilter('stylesheet_tag', href => `<link rel="stylesheet" href="${href}">`)
engine.registerFilter('script_tag', src => `<script src="${src}"></script>`)
engine.registerFilter('handleize', s => slug(String(s ?? '')))
engine.registerFilter('strip_html', s => String(s ?? '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim())

/* `{% section 'x' %}` renders sections/x.liquid with a `section` scope carrying schema defaults. */
engine.registerTag('section', {
  parse (token) { this.name = token.args.trim().replace(/^['"]|['"]$/g, '') },
  async render (ctx) {
    const file = path.join(THEME, 'sections', this.name + '.liquid')
    if (!fs.existsSync(file)) return ''
    const raw = fs.readFileSync(file, 'utf8')
    const body = raw.replace(/{%-?\s*schema\s*-?%}[\s\S]*?{%-?\s*endschema\s*-?%}/g, '')
    const schema = parseSchema(raw)
    const scope = ctx.getAll()
    // `blocks` is reserved in an override: everything else is a settings value, but blocks are a
    // separate part of the section object on Shopify and a section may not read them as settings.
    const { blocks = [], ...settingOverrides } = (scope.section_overrides || {})[this.name] || {}
    scope.section = {
      id: this.name,
      settings: Object.assign(defaults(schema.settings), settingOverrides),
      blocks: blocks.map((b, i) => Object.assign(
        { id: `${this.name}-${i}`, type: b.type || 'block', shopify_attributes: '' },
        b,
        { settings: Object.assign(defaults((schema.blocks || []).find(s => s.type === b.type)?.settings), b.settings) }
      )),
      shopify_attributes: ''
    }
    return engine.parseAndRender(body, scope)
  }
})

function parseSchema (raw) {
  const m = raw.match(/{%-?\s*schema\s*-?%}([\s\S]*?){%-?\s*endschema\s*-?%}/)
  if (!m) return { settings: [] }
  try { return JSON.parse(m[1]) } catch { return { settings: [] } }
}
const defaults = (settings = []) =>
  Object.fromEntries(settings.filter(s => s.id).map(s => [s.id, s.default ?? '']))

/* ------------------------------------------------------------------ catalog */

const slug = s => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')

const SETTINGS = Object.assign(
  JSON.parse(fs.readFileSync(path.join(THEME, 'config', 'settings_data.json'), 'utf8')).current,
  { commerce_mode: 'local', prototype_banner: CATALOG.notice }
)

const products = CATALOG.products.map(p => ({
  id: p.productId,
  handle: p.handle,
  title: p.name,
  vendor: p.brand,
  model: p.model,
  weight: p.weight,
  url: `/products/${p.handle}.html`,
  price: Math.round(p.price * 100),
  compare_at_price: null,
  featured_image: p.image,
  description: p.descriptionHtml,
  has_options: p.options.length > 0,
  first_available_variant: { id: p.productId },
  breadcrumbs: p.categories.map(c => ({ title: c.name, url: `/collections/${slug(c.name)}.html` })),
  options_with_values: p.options.map(o => ({
    id: o.optionId,
    name: o.name,
    type: o.type,
    required: o.required,
    // Cents, like `price` above. The catalog carries dollars; every price the theme touches is
    // cents, because Shopify's money filters divide by 100. Leaving this in dollars rendered an
    // $8.00 braid surcharge as "+$0.08" while the cart correctly charged $8.00.
    values: o.values.map(v => ({ id: v.valueId, label: v.label, price_delta: Math.round(v.priceDelta * 100) }))
  })),
  _categories: p.categories.map(c => c.name)
}))

const byCategory = new Map()
for (const p of products) {
  for (const name of p._categories) {
    if (!byCategory.has(name)) byCategory.set(name, [])
    byCategory.get(name).push(p)
  }
}
/* Every category a product claims gets a page. The threshold below decides what is worth putting
   on the shelf, not what exists: products carry breadcrumbs to all of their categories, so
   filtering here instead left 18 breadcrumb links pointing at pages that were never generated. */
const collections = [...byCategory.entries()]
  .map(([title, items]) => ({ title, handle: slug(title), url: `/collections/${slug(title)}.html`, products: items }))
  .sort((a, b) => b.products.length - a.products.length)

const SHELF_MINIMUM = 3
const shelvable = collections.filter(c => c.products.length >= SHELF_MINIMUM)
const ROLES = shelvable.filter(c => CATALOG.roles.includes(c.title))
const SHELF = shelvable.filter(c => !CATALOG.roles.includes(c.title)).slice(0, 18)
const ALL = { title: 'Full catalog', handle: 'all', url: '/collections/all.html', products, description: '' }

/* Real five-star reviews, as the section's own block shape. `make-catalog.mjs` already filtered to
   approved five-star reviews whose product still exists; this only translates them, and links each
   one to the product page it was written about so the claim is checkable rather than decorative. */
const productByHandle = new Map(products.map(p => [p.handle, p]))
const REVIEW_BLOCKS = (CATALOG.reviews || []).map(r => ({
  type: 'review',
  settings: {
    body: r.body,
    author: r.author,
    product: r.productName,
    product_url: productByHandle.get(r.productHandle)?.url || '',
    date: r.date
  }
}))

/* ------------------------------------------------------------------- render */

const routes = {
  root_url: '/',
  search_url: '/search.html',
  all_products_collection_url: '/collections/all.html'
}

const base = () => ({
  shop: { name: 'M.T. Uniforms', money_format: '${{amount}}' },
  settings: SETTINGS,
  routes,
  linklists: {
    'main-menu': {
      links: [
        { title: 'Catalog', url: '/collections/all.html' },
        { title: 'Departments', url: '/pages/departments.html' },
        { title: 'Contact', url: '/pages/contact.html' }
      ]
    }
  },
  request: { locale: { iso_code: 'en' } },
  current_tags: null,
  page_description: '',
  canonical_url: '',
  section_overrides: {
    'main-collection': { roles: ROLES, shelf: SHELF },
    'reviews-band': { blocks: REVIEW_BLOCKS }
  }
})

async function page (template, scope, outPath, title) {
  const layout = fs.readFileSync(path.join(THEME, 'layout', 'theme.liquid'), 'utf8')
  const ctx = Object.assign(base(), scope, {
    page_title: title,
    template,
    content_for_header: '',
    content_for_layout: await engine.renderFile(template, Object.assign(base(), scope, { page_title: title, template }))
  })
  const html = await engine.parseAndRender(layout, ctx)
  const dest = path.join(OUT, outPath)
  fs.mkdirSync(path.dirname(dest), { recursive: true })
  fs.writeFileSync(dest, html)
}

// Clear the contents rather than the directory itself: on Windows a running static server holds
// a handle on dist/ and removing the root fails with EPERM mid-rebuild.
fs.mkdirSync(OUT, { recursive: true })
for (const entry of fs.readdirSync(OUT)) {
  fs.rmSync(path.join(OUT, entry), { recursive: true, force: true, maxRetries: 5, retryDelay: 150 })
}
fs.cpSync(path.join(THEME, 'assets'), path.join(OUT, 'assets'), { recursive: true })

await page('index', { collection: Object.assign({}, ALL, { title: 'Stocked now', products: products.slice(0, 12) }) },
  'index.html', 'Uniforms and duty gear for western Pennsylvania')

await page('collection', { collection: ALL }, 'collections/all.html', ALL.title)
for (const c of collections) {
  await page('collection', { collection: c }, `collections/${c.handle}.html`, c.title)
}
for (const p of products) {
  await page('product', { product: p }, `products/${p.handle}.html`, p.title)
}
await page('search', { search: { terms: '', results: [], results_count: 0 } }, 'search.html', 'Search')
await page('404', {}, '404.html', 'Not found')

for (const pg of CATALOG.pages) {
  await page('page', { page: pg }, `pages/${pg.handle}.html`, pg.title)
}

// The client-side search index. Small enough to ship whole; no server needed.
fs.writeFileSync(path.join(OUT, 'search-index.json'), JSON.stringify(
  products.map(p => ({ t: p.title, v: p.vendor, m: p.model, u: p.url, i: p.featured_image, p: p.price }))
))

console.log(`[preview] ${products.length} products · ${collections.length} collections · ${CATALOG.pages.length} pages -> ${OUT}`)
