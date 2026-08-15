/* Local operations console for M.T. Uniforms.
 *
 * Runs on the shop's own machine against the SQLite database under PROJECT_DATA_ROOT. It binds to
 * 127.0.0.1 only and has no authentication, because it is a local tool on a trusted machine and a
 * half-built login is worse than an honest local-only bind. Do not expose it to a network without
 * putting real authentication in front of it first.
 *
 *   node ops/admin.mjs          then open http://127.0.0.1:8930
 */
import crypto from 'node:crypto'
import fs from 'node:fs'
import os from 'node:os'
import http from 'node:http'
import path from 'node:path'
import { DatabaseSync } from 'node:sqlite'

const PORT = Number(process.env.MT_ADMIN_PORT || 8930)
const ROOTS = [process.env.PROJECT_DATA_ROOT, path.join(os.homedir(), 'Data', 'Projects', 'kelly-uniforms-business')].filter(Boolean)
const dbPath = ROOTS.map(r => path.join(r, 'db', 'operations.sqlite')).find(p => fs.existsSync(p))
if (!dbPath) { console.error('No operations.sqlite found. Run: node ops/build-db.mjs'); process.exit(1) }

const db = new DatabaseSync(dbPath)
db.exec('PRAGMA foreign_keys = ON')
const all = (sql, ...a) => db.prepare(sql).all(...a)
const get = (sql, ...a) => db.prepare(sql).get(...a)
const run = (sql, ...a) => db.prepare(sql).run(...a)

/* Binding to 127.0.0.1 keeps the NETWORK out; it does nothing about the browser already running on
   this machine. Any page the shop's browser visits can POST to http://127.0.0.1:8930/... and change
   an order status, and DNS rebinding can point an attacker's hostname at this port. So: every
   state-changing POST carries a token minted for this process, the Origin must be one of our own,
   and the Host header must name the loopback address rather than an attacker's domain. */
const CSRF_TOKEN = crypto.randomBytes(24).toString('hex')
const MAX_BODY_BYTES = 64 * 1024

const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c])
const money = c => '$' + ((Number(c) || 0) / 100).toFixed(2)
const csrfField = () => `<input type="hidden" name="_token" value="${CSRF_TOKEN}">`

/* `%` and `_` are wildcards inside LIKE, so a search for "50_" matched "501" and "50%" matched
   everything. Escaped with a backslash, declared to SQLite with ESCAPE at each call site. */
const likeTerm = s => '%' + String(s).replace(/[\\%_]/g, c => '\\' + c) + '%'

const CSS = `
:root{--navy:#0b1d34;--paper:#f3f2ee;--white:#fbfaf7;--steel:#6d7780;--hairline:#c8c8c2;--orange:#b8440c;--ink:#12181f}
*{box-sizing:border-box}body{margin:0;font:16px/1.5 Archivo,system-ui,sans-serif;background:var(--paper);color:var(--ink)}
header{background:var(--navy);color:#fff;padding:.75rem 1.25rem;display:flex;gap:1.25rem;align-items:center}
header a{color:#cdd7e2;text-decoration:none}header a:hover,header a.on{color:#fff;text-decoration:underline}
main{padding:1.25rem;max-width:1180px;margin:0 auto}
h1{font-size:1.25rem;margin:0 0 1rem}h2{font-size:1rem;margin:1.5rem 0 .5rem}
table{width:100%;border-collapse:collapse;background:var(--white);border:1px solid var(--hairline);border-radius:10px;overflow:hidden}
th,td{text-align:left;padding:.55rem .75rem;border-bottom:1px solid var(--hairline);font-size:.9375rem}
th{background:#eceae4;font-size:.75rem;text-transform:uppercase;letter-spacing:.06em;color:var(--steel)}
tr:last-child td{border-bottom:0}
.tag{display:inline-block;padding:.125rem .5rem;border-radius:99px;font-size:.75rem;font-weight:600;border:1px solid var(--hairline)}
.tag.warn{background:#fdf0e6;border-color:#e8b78e;color:#8a3308}
.tag.ok{background:#e9f2ea;border-color:#a8c8ab;color:#245c2b}
.empty{color:var(--steel)}
form.inline{display:inline}
button{font:inherit;font-size:.8125rem;border:1px solid var(--navy);background:var(--navy);color:#fff;border-radius:6px;padding:.3rem .6rem;cursor:pointer}
button.ghost{background:transparent;color:var(--ink);border-color:var(--hairline)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:.75rem;margin-bottom:1rem}
.stat{background:var(--white);border:1px solid var(--hairline);border-radius:10px;padding:.75rem .9rem}
.stat b{display:block;font-size:1.5rem}
.stat span{color:var(--steel);font-size:.8125rem}
`

const page = (title, nav, body) => `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)} · M.T. Uniforms ops</title>
<style>${CSS}</style></head><body>
<header><strong>M.T. Uniforms — operations</strong>
${['', 'orders', 'decoration', 'catalog', 'reorder'].map(p =>
  `<a class="${nav === (p || 'dashboard') ? 'on' : ''}" href="/${p}">${p ? p[0].toUpperCase() + p.slice(1) : 'Dashboard'}</a>`).join('')}
</header><main><h1>${esc(title)}</h1>${body}</main></body></html>`

const table = (cols, rows, cells) => rows.length
  ? `<table><thead><tr>${cols.map(c => `<th>${esc(c)}</th>`).join('')}</tr></thead>
     <tbody>${rows.map(r => `<tr>${cells(r).map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table>`
  : '<p class="empty">Nothing here yet.</p>'

/* ------------------------------------------------------------------ views */

function dashboard () {
  const s = {
    products: get('SELECT COUNT(*) n FROM product WHERE active = 1').n,
    open: get(`SELECT COUNT(*) n FROM "order" WHERE status NOT IN ('collected','shipped','cancelled')`).n,
    decoration: get(`SELECT COUNT(*) n FROM decoration_job WHERE status IN ('queued','in-progress')`).n,
    reorder: get('SELECT COUNT(*) n FROM v_reorder').n,
    uncounted: get('SELECT COUNT(*) n FROM v_uncounted').n,
    freeText: get('SELECT COUNT(*) n FROM v_free_text_options').n
  }
  return page('Dashboard', 'dashboard', `
    <div class="grid">
      <div class="stat"><b>${s.products}</b><span>active products</span></div>
      <div class="stat"><b>${s.open}</b><span>open orders</span></div>
      <div class="stat"><b>${s.decoration}</b><span>decoration jobs waiting</span></div>
      <div class="stat"><b>${s.reorder}</b><span>at or below reorder point</span></div>
      <div class="stat"><b>${s.uncounted}</b><span>never stock-counted</span></div>
    </div>
    <h2>Recent orders</h2>
    ${table(['Ref', 'Customer', 'Status', 'Decoration', 'Total'],
      all('SELECT * FROM v_order_summary ORDER BY created_at DESC LIMIT 10'),
      r => [`<a href="/orders/${r.id}">${esc(r.reference)}</a>`, esc(r.customer),
        `<span class="tag">${esc(r.status)}</span>`,
        r.open_decoration ? `<span class="tag warn">${r.open_decoration} open</span>` : '<span class="tag ok">clear</span>',
        money(r.total_cents)])}
    <h2>Free-text options</h2>
    <p class="empty">${s.freeText} product option${s.freeText === 1 ? '' : 's'} require typed input rather than a
       pick from a list. This is the set a pick-list-only point-of-sale option model cannot carry.</p>
    ${table(['Product', 'Option', 'Kind'], all('SELECT * FROM v_free_text_options'),
      r => [esc(r.name), esc(r.option_name), esc(r.kind)])}`)
}

function orders () {
  return page('Orders', 'orders', table(
    ['Ref', 'Customer', 'Channel', 'Status', 'Payment', 'PO', 'Lines', 'Total', 'Promised'],
    all('SELECT * FROM v_order_summary ORDER BY created_at DESC'),
    r => [`<a href="/orders/${r.id}">${esc(r.reference)}</a>`, esc(r.customer), esc(r.channel),
      `<span class="tag">${esc(r.status)}</span>`, esc(r.payment_status), esc(r.purchase_order_number) || '—',
      r.lines, money(r.total_cents), esc(r.promised_at) || '—']))
}

const STATUSES = ['draft', 'placed', 'awaiting-stock', 'in-decoration', 'ready', 'collected', 'shipped', 'cancelled']

function order (id) {
  const o = get('SELECT * FROM v_order_summary WHERE id = ?', id)
  if (!o) return null
  const lines = all('SELECT * FROM order_line WHERE order_id = ?', id)
  // v_order_summary carries only total_cents, which the schema defines as subtotal + decoration +
  // tax. It was shown labelled "Goods", so a $313.96 order with $74 of decoration read as $313.96
  // of garments. The four figures come off the order row and are each labelled for what they are.
  const t = get('SELECT subtotal_cents, decoration_cents, tax_cents, total_cents FROM "order" WHERE id = ?', id)
  return page('Order ' + o.reference, 'orders', `
    <p><b>${esc(o.customer)}</b> · ${esc(o.channel)} · ${esc(o.payment_status)}
       ${o.purchase_order_number ? '· PO ' + esc(o.purchase_order_number) : ''}</p>
    <form method="post" action="/orders/${id}/status" class="inline">
      ${csrfField()}
      <label>Status
        <select name="status">${STATUSES.map(s => `<option ${s === o.status ? 'selected' : ''}>${s}</option>`).join('')}</select>
      </label>
      <button type="submit">Update</button>
    </form>
    <h2>Lines</h2>
    ${lines.map(l => {
      const opts = all('SELECT * FROM order_line_option WHERE order_line_id = ?', l.id)
      const jobs = all('SELECT * FROM decoration_job WHERE order_line_id = ?', l.id)
      return `<div class="stat" style="margin-bottom:.75rem">
        <b style="font-size:1rem">${l.quantity} × ${esc(l.name_at_sale)}</b>
        <span>${esc(l.model_at_sale)} · ${money(l.unit_price_cents)} each · ${money(l.line_total_cents)}</span>
        ${opts.length ? '<p style="margin:.4rem 0 0">' + opts.map(o2 => esc(o2.option_name) + ': <b>' + esc(o2.value_label) + '</b>').join(' · ') + '</p>' : ''}
        ${jobs.length ? '<p style="margin:.4rem 0 0">' + jobs.map(j =>
          `<span class="tag ${j.status === 'done' ? 'ok' : 'warn'}">${esc(j.kind)}: ${esc(j.status)}</span> ${esc(j.instructions)}`).join('<br>') + '</p>' : ''}
      </div>`
    }).join('') || '<p class="empty">No lines.</p>'}
    <h2>Totals</h2>
    <p>Goods ${money(t.subtotal_cents)} · Decoration ${money(t.decoration_cents)}
       · Tax ${money(t.tax_cents)} · <b>Total ${money(t.total_cents)}</b></p>`)
}

function decoration () {
  const rows = all(`SELECT d.*, l.name_at_sale, o.reference, o.id AS order_id,
                           COALESCE(a.name, c.name, 'Walk-in') AS customer
                      FROM decoration_job d
                      JOIN order_line l ON l.id = d.order_line_id
                      JOIN "order" o ON o.id = l.order_id
                      LEFT JOIN agency a ON a.id = o.agency_id
                      LEFT JOIN customer c ON c.id = o.customer_id
                     WHERE d.status IN ('queued','in-progress')
                     ORDER BY o.promised_at IS NULL, o.promised_at, d.created_at`)
  return page('Decoration queue', 'decoration', table(
    ['Order', 'Customer', 'Garment', 'Work', 'Instructions', 'Status', ''],
    rows,
    r => [`<a href="/orders/${r.order_id}">${esc(r.reference)}</a>`, esc(r.customer), esc(r.name_at_sale),
      `<span class="tag">${esc(r.kind)}</span>`, esc(r.instructions), esc(r.status),
      `<form class="inline" method="post" action="/decoration/${r.id}/done">${csrfField()}<button>Mark done</button></form>`]))
}

function catalog (q) {
  const rows = q
    ? all(`SELECT p.*, (SELECT COUNT(*) FROM product_option o WHERE o.product_id = p.id) opts
             FROM product p WHERE p.name LIKE ? ESCAPE '\\' OR p.model LIKE ? ESCAPE '\\'
                               OR p.brand LIKE ? ESCAPE '\\'
            ORDER BY p.name LIMIT 300`, likeTerm(q), likeTerm(q), likeTerm(q))
    : all(`SELECT p.*, (SELECT COUNT(*) FROM product_option o WHERE o.product_id = p.id) opts
             FROM product p ORDER BY p.name LIMIT 300`)
  return page('Catalog', 'catalog', `
    <form method="get"><input name="q" value="${esc(q || '')}" placeholder="Search name, model, brand"
      style="padding:.45rem .6rem;border:1px solid var(--hairline);border-radius:6px;font:inherit"> <button>Search</button></form>
    <p class="empty">${rows.length} shown${rows.length === 300 ? ' (capped at 300)' : ''}.</p>
    ${table(['Name', 'Model', 'Brand', 'Price', 'Options', 'On hand'], rows, r => [
      esc(r.name), esc(r.model), esc(r.brand), money(r.price_cents), r.opts,
      (get('SELECT on_hand FROM inventory WHERE product_id = ?', r.id) || {}).on_hand ?? '—'])}`)
}

function reorder () {
  const uncounted = all('SELECT * FROM v_uncounted')
  return page('Reorder', 'reorder', `
    <p class="empty">Only products with a real stock count appear here. ${uncounted.length} product${uncounted.length === 1 ? ' has' : 's have'}
       never been counted, so an empty list below means <b>not yet known</b> rather than <b>nothing to order</b>.</p>
    ${table(['Product', 'Model', 'Brand', 'On hand', 'Reorder point', 'Counted'], all('SELECT * FROM v_reorder'),
      r => [esc(r.name), esc(r.model), esc(r.brand), r.on_hand, r.reorder_point, esc(r.counted_at)])}
    <h2>Never counted (${uncounted.length})</h2>
    ${table(['Product', 'Model', 'Brand'], uncounted.slice(0, 50),
      r => [esc(r.name), esc(r.model), esc(r.brand)])}
    ${uncounted.length > 50 ? `<p class="empty">Showing the first 50 of ${uncounted.length}.</p>` : ''}`)
}

/* ----------------------------------------------------------------- server */

const LOCAL_HOSTS = new Set([`127.0.0.1:${PORT}`, `localhost:${PORT}`])
const LOCAL_ORIGINS = new Set([`http://127.0.0.1:${PORT}`, `http://localhost:${PORT}`])

/** The reason to refuse a state-changing POST, or null when it is one of ours. */
function refuseUnsafePost (req) {
  // A rebinding attack reaches this port with the ATTACKER's hostname in Host, which is how it gets
  // the browser to treat our responses as same-origin. Anything not naming loopback is not us.
  if (!LOCAL_HOSTS.has(String(req.headers.host || '').toLowerCase())) {
    return 'Unexpected Host header. This console only answers to 127.0.0.1 or localhost.'
  }
  // Browsers send Origin on cross-site form POSTs, so an absent Origin is a non-browser client and
  // a foreign one is exactly the attack. Both are refused rather than trusted.
  const origin = req.headers.origin
  if (origin && !LOCAL_ORIGINS.has(origin)) return 'Cross-origin request refused.'
  return null
}

/** The form body, or null when the client sent more than we will hold in memory. */
function readBody (req) {
  return new Promise((resolve, reject) => {
    let size = 0
    const chunks = []
    req.on('data', c => {
      size += c.length
      // Capped and hung up on, because an unbounded accumulator is a one-request memory exhaustion.
      if (size > MAX_BODY_BYTES) { req.destroy(); resolve(null); return }
      chunks.push(c)
    })
    req.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')))
    // Without these the promise never settled on a dropped or aborted connection and the handler
    // waited forever, holding the request open.
    req.on('aborted', () => resolve(null))
    req.on('error', reject)
  })
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://127.0.0.1')
  const send = (code, html) => { res.writeHead(code, { 'content-type': 'text/html; charset=utf-8' }); res.end(html) }
  const back = to => { res.writeHead(303, { location: to }); res.end() }

  try {
    if (req.method === 'POST') {
      const refused = refuseUnsafePost(req)
      if (refused) return send(403, page('Refused', '', `<p>${esc(refused)}</p>`))
      const body = await readBody(req)
      if (body === null) return send(413, page('Too large', '', '<p>Request body too large.</p>'))
      const form = new URLSearchParams(body)
      // Constant-time so a wrong token cannot be discovered a character at a time.
      const supplied = Buffer.from(form.get('_token') || '')
      const expected = Buffer.from(CSRF_TOKEN)
      if (supplied.length !== expected.length || !crypto.timingSafeEqual(supplied, expected)) {
        return send(403, page('Refused', '', '<p>Missing or stale form token. Reload the page and try again.</p>'))
      }
      let m
      if ((m = url.pathname.match(/^\/orders\/(\d+)\/status$/))) {
        const status = form.get('status')
        if (!STATUSES.includes(status)) return send(400, page('Bad status', 'orders', '<p>Unknown status.</p>'))
        run('UPDATE "order" SET status = ?, updated_at = datetime(\'now\') WHERE id = ?', status, Number(m[1]))
        return back('/orders/' + m[1])
      }
      if ((m = url.pathname.match(/^\/decoration\/(\d+)\/done$/))) {
        run(`UPDATE decoration_job SET status = 'done', completed_at = datetime('now') WHERE id = ?`, Number(m[1]))
        return back('/decoration')
      }
      return send(404, page('Not found', '', '<p>No such action.</p>'))
    }

    if (url.pathname === '/') return send(200, dashboard())
    if (url.pathname === '/orders') return send(200, orders())
    const om = url.pathname.match(/^\/orders\/(\d+)$/)
    if (om) {
      const html = order(Number(om[1]))
      return html ? send(200, html) : send(404, page('Not found', 'orders', '<p>No such order.</p>'))
    }
    if (url.pathname === '/decoration') return send(200, decoration())
    if (url.pathname === '/catalog') return send(200, catalog(url.searchParams.get('q')))
    if (url.pathname === '/reorder') return send(200, reorder())
    return send(404, page('Not found', '', '<p>No such page.</p>'))
  } catch (e) {
    send(500, page('Error', '', `<pre>${esc(e.message)}</pre>`))
  }
})

server.listen(PORT, '127.0.0.1', () => {
  console.log(`[ops] ${dbPath}`)
  console.log(`[ops] http://127.0.0.1:${PORT}  (local only, no authentication — do not expose)`)
})
