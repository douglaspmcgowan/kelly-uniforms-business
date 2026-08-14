/* Builds preview/data/catalog.json from the extracted public catalog.
 *
 * Only public storefront facts travel into the repository: names, models, brands, list prices,
 * images, categories, options, and marketing copy. Inventory counts, costs, orders, and any
 * customer record stay under PROJECT_DATA_ROOT and are never committed.
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const SRC = process.env.MT_EXPORT_DIR
if (!SRC) { console.error('MT_EXPORT_DIR required (the dated export folder under PROJECT_DATA_ROOT)'); process.exit(1) }

const raw = JSON.parse(fs.readFileSync(path.join(SRC, 'products-public.json'), 'utf8'))

const products = raw
  .filter(p => p.price != null && p.handle)
  .map(p => ({
    productId: p.productId,
    handle: p.handle,
    name: p.name,
    model: p.model,
    brand: p.brand,
    weight: p.weight,
    price: p.price,
    image: p.image,
    categories: p.categories,
    options: p.options,
    descriptionHtml: p.descriptionHtml
  }))

const pages = [
  {
    handle: 'departments',
    title: 'Department and agency accounts',
    content: `
<p>Most of what we do is not a one-off sale. It is a department that needs twenty officers in the
same shirt, with the same patch, cut to twenty different inseams — and a business office that needs
one invoice at the end of it.</p>
<h2>How an account works</h2>
<ul>
  <li><strong>Purchase orders.</strong> Send the PO number with the order and we bill the agency directly.</li>
  <li><strong>Allowances.</strong> If your contract gives each officer a yearly dollar amount, we can track it
      against the roster so nobody has to keep receipts in a drawer.</li>
  <li><strong>Standing specifications.</strong> We keep your patch placement, badge, name tape format, and
      approved colors on file, so a replacement in March matches the one issued in September.</li>
  <li><strong>Fittings.</strong> Walk in, or we come to you and size a whole shift at once.</li>
</ul>
<p>To open an account, call <a href="tel:+18145362390">(814) 536-2390</a> or
<a href="mailto:orders@mtuniforms.com">email us</a> with your agency name and who handles purchasing.</p>`
  },
  {
    handle: 'tailoring',
    title: 'Tailoring and decoration',
    content: `
<p>Alterations and decoration happen in our own shop. Nothing gets shipped out and nothing waits on
a vendor's queue.</p>
<h2>What we do</h2>
<ul>
  <li>Hemming and tapering, including trousers cut to a boot</li>
  <li>Patch and emblem sewing, positioned to your department's standard</li>
  <li>Name tapes and embroidery, on the garment or on a separate tape</li>
  <li>Badge tabs, hash marks, service stripes, and rank insignia</li>
  <li>Vest carrier fitting and adjustment</li>
</ul>
<h2>What it costs</h2>
<p>Decoration is quoted on the order ticket rather than priced on the website, because the honest
answer depends on the garment, the placement, and how many you need. Add what you want in the notes
when you order and we confirm the price before anything is charged.</p>`
  },
  {
    handle: 'sizing',
    title: 'Sizing guide',
    content: `
<p>Uniform sizing is not street sizing, and it is not consistent between manufacturers. The numbers
below get you close; a fitting gets you right.</p>
<h2>Shirts</h2>
<p>Ordered by neck and sleeve, not by S/M/L. Measure the neck where the collar sits, and the sleeve
from the center back of the neck, over the shoulder, to the wrist bone with the arm slightly bent.</p>
<h2>Trousers</h2>
<p>Ordered by waist and inseam. Measure the waist where the duty belt rides, not at the natural
waist — this is the single most common sizing mistake we see. Unhemmed lengths are normal; we cut
them to you.</p>
<h2>Body armor and carriers</h2>
<p>Not sized from a chart. Armor is fitted in person, every time.</p>
<p>If you are between sizes, call <a href="tel:+18145362390">(814) 536-2390</a> before you order.</p>`
  },
  {
    handle: 'returns',
    title: 'Returns',
    content: `
<p>Unworn, undecorated stock items can be returned within 30 days for exchange or refund, with the
tags on and the original receipt.</p>
<h2>What we cannot take back</h2>
<ul>
  <li>Anything decorated, hemmed, or altered — once your name is on it, it is yours</li>
  <li>Special orders brought in specifically for you</li>
  <li>Worn footwear, and any restraint or duty item that has left our custody</li>
</ul>
<p>Sizing exchanges on undecorated garments are routine and we do not make them difficult. Call
before shipping anything back so we can tell you what is in stock to swap into.</p>`
  },
  {
    handle: 'contact',
    title: 'Contact',
    content: `
<p><strong>M.T. Uniforms LLC</strong><br>Johnstown, Pennsylvania</p>
<p>Phone: <a href="tel:+18145362390">(814) 536-2390</a><br>
Email: <a href="mailto:orders@mtuniforms.com">orders@mtuniforms.com</a></p>
<h2>Hours</h2>
<p>Monday–Friday 9:00–5:00<br>Saturday by appointment</p>
<h2>Fittings</h2>
<p>Walk in any weekday for a fitting. For a whole shift or a new class, call ahead and we will
schedule time — or bring the fitting to your station.</p>`
  }
]

const out = {
  generatedFrom: path.basename(SRC),
  notice: 'Prototype for review. Prices and stock come from the current mtuniforms.com catalog; ordering is not live.',
  roles: ['Police', 'Fire-EMS', 'Corrections', 'Security', 'PA Constable', 'Postal Letter Carrier', 'Postal Police'],
  pages,
  products
}

fs.mkdirSync(path.join(HERE, 'data'), { recursive: true })
fs.writeFileSync(path.join(HERE, 'data', 'catalog.json'), JSON.stringify(out, null, 1))
console.log(`[catalog] ${products.length} products, ${pages.length} pages`)
