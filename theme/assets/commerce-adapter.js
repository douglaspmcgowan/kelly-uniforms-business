/* M.T. Uniforms commerce adapter.
 *
 * The theme never talks to a commerce platform directly. It calls MTCommerce, which picks a
 * driver at load from window.MT_COMMERCE.mode. Adding a platform means adding a driver here and
 * nothing else — no template, section, or snippet changes.
 *
 *   shopify  Shopify AJAX Cart API (/cart/*.js). Live store.
 *   ecwid    Ecwid JS API (Ecwid.Cart). Storefront embedded on the same page.
 *   local    Cart in localStorage, checkout is an emailed order ticket. Demo/preview, and the
 *            honest fallback when neither platform is wired yet.
 *
 * Every driver resolves the same shapes, so theme.js is platform-blind:
 *   add(line)   -> Promise<cart>
 *   change(key, quantity) -> Promise<cart>
 *   get()       -> Promise<cart>
 *   checkoutUrl() -> string
 *   cart = { items: [{ key, id, title, quantity, price, line_price, image, options: {} }], total }
 */
(function () {
  'use strict'

  var CONFIG = window.MT_COMMERCE || {}
  var MODE = CONFIG.mode || 'local'

  function money (cents) {
    var n = (Number(cents) || 0) / 100
    return '$' + n.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  }

  /* ---------------------------------------------------------------- local */

  var LocalDriver = {
    name: 'local',
    KEY: 'mt-cart-v1',
    /* Any stored value that is not an array of well-formed lines is discarded rather than trusted.
       `JSON.parse(...) || []` accepted anything valid-JSON — `{"items":[],"total":0}`, a bare
       string, a number — and `_shape` then called `.reduce` on it and threw SYNCHRONOUSLY, before
       any promise existed, so theme.js's `.catch` never ran and the customer saw no error at all:
       the Add to order button simply stopped working on every page until they cleared site data.
       An older cart shape or a half-written value was enough to do it. */
    _read: function () {
      var raw
      try { raw = JSON.parse(localStorage.getItem(this.KEY)) } catch (e) { return [] }
      if (!Array.isArray(raw)) return []
      return raw.filter(function (i) {
        return i && typeof i === 'object' &&
          typeof i.key === 'string' &&
          isFinite(i.price) && isFinite(i.quantity) && i.quantity > 0
      })
    },
    _write: function (items) {
      try { localStorage.setItem(this.KEY, JSON.stringify(items)) } catch (e) { /* private mode */ }
      return this._shape(items)
    },
    _shape: function (items) {
      var total = items.reduce(function (s, i) { return s + i.price * i.quantity }, 0)
      return {
        items: items.map(function (i) {
          return Object.assign({}, i, { line_price: i.price * i.quantity })
        }),
        total: total
      }
    },
    get: function () { return Promise.resolve(this._shape(this._read())) },
    add: function (line) {
      var items = this._read()
      var price = Number(line.price)
      if (!isFinite(price) || price < 0) {
        return Promise.reject(new Error('That item has no usable price. Please call us to order it.'))
      }
      var quantity = Math.max(1, Math.floor(Number(line.quantity) || 1))
      /* Key off the option values sorted by name. Keying off JSON.stringify of the raw object made
         the merge depend on property insertion order, so the same variant added from two templates
         that happened to render the groups differently produced two lines. */
      var opts = line.options || {}
      var key = line.id + ':' + JSON.stringify(Object.keys(opts).sort().map(function (k) { return [k, opts[k]] }))
      var found = items.filter(function (i) { return i.key === key })[0]
      if (found) found.quantity += quantity
      else {
        items.push({
          key: key,
          id: line.id,
          title: line.title,
          quantity: quantity,
          price: price,
          image: line.image || '',
          options: line.options || {}
        })
      }
      return Promise.resolve(this._write(items))
    },
    change: function (key, quantity) {
      /* A non-finite quantity used to fall through the `> 0` filter and silently DELETE the line —
         and the value comes from a `data-to` attribute, so any markup defect became a deletion.
         Explicitly: a bad number changes nothing, 0 removes the line, and the top is bounded. */
      var q = Number(quantity)
      if (!isFinite(q)) return Promise.resolve(this._shape(this._read()))
      q = Math.min(999, Math.max(0, Math.floor(q)))
      var items = this._read().filter(function (i) { return i.key !== key || q > 0 })
      items.forEach(function (i) { if (i.key === key) i.quantity = q })
      return Promise.resolve(this._write(items.filter(function (i) { return i.quantity > 0 })))
    },
    checkoutUrl: function () {
      // No payment rail in local mode. Hand the ticket to the store the way a phone order works.
      var self = this
      var stored = self._read()
      // An empty cart used to return a live mailto:, and theme.js set it as the href regardless —
      // aria-disabled announces a state, it does not stop an <a> from activating. Customers opened
      // their mail client on a blank order.
      if (!stored.length) return ''
      var lines = stored.map(function (i) {
        var opts = Object.keys(i.options || {}).map(function (k) { return k + ': ' + i.options[k] }).join(', ')
        return '- ' + i.quantity + ' x ' + i.title + (opts ? ' (' + opts + ')' : '') + ' — ' + money(i.price * i.quantity)
      })
      /* Outlook and the Windows shell handoff truncate a mailto: near 2,000 characters, and a
         60-line cart produced 8,634 — so a large agency order, which is this store's best customer,
         would have arrived at the shop with its tail silently missing and no server-side copy to
         reconcile against. Measured on the ENCODED url, because that is what actually gets cut, and
         a name tape full of spaces triples in encoding. Past the limit the body says so. */
      var LIMIT = 1900
      var address = CONFIG.contactEmail || 'orders@mtuniforms.com'
      var subject = '?subject=' + encodeURIComponent('Order request from the website')
      var tail = '\n\nTotal: ' + money(self._shape(stored).total) +
        '\n\nName:\nDepartment / agency:\nPhone:\nPickup or ship:\n'
      var build = function (kept, dropped) {
        return 'mailto:' + address + subject + '&body=' + encodeURIComponent(
          'I would like to place this order:\n\n' + kept.join('\n') +
          (dropped
            ? '\n\n[' + dropped + ' more lines could not fit in this email. Please call ' +
              (CONFIG.contactPhone || '(814) 536-2390') + ' and we will take the whole order over ' +
              'the phone.]'
            : '') + tail)
      }
      var url = build(lines, 0)
      for (var n = lines.length; url.length > LIMIT && n > 1; n--) {
        url = build(lines.slice(0, n - 1), lines.length - (n - 1))
      }
      return url
    }
  }

  /* -------------------------------------------------------------- shopify */

  var ShopifyDriver = {
    name: 'shopify',
    _post: function (path, payload) {
      return fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload)
      }).then(function (r) {
        if (!r.ok) return r.json().then(function (e) { throw new Error(e.description || e.message || 'Cart error') })
        return r.json()
      })
    },
    _shape: function (cart) {
      return {
        items: (cart.items || []).map(function (i) {
          return {
            key: i.key,
            id: i.variant_id || i.id,
            title: i.product_title || i.title,
            quantity: i.quantity,
            price: i.price,
            line_price: i.final_line_price != null ? i.final_line_price : i.line_price,
            image: i.image || '',
            options: i.properties || {}
          }
        }),
        total: cart.total_price || 0
      }
    },
    get: function () {
      var self = this
      return fetch('/cart.js', { headers: { Accept: 'application/json' } })
        .then(function (r) { return r.json() }).then(function (c) { return self._shape(c) })
    },
    add: function (line) {
      var self = this
      return this._post('/cart/add.js', {
        items: [{ id: line.variantId || line.id, quantity: line.quantity || 1, properties: line.options || {} }]
      }).then(function () { return self.get() })
    },
    change: function (key, quantity) {
      var self = this
      return this._post('/cart/change.js', { id: key, quantity: quantity })
        .then(function (c) { return self._shape(c) })
    },
    checkoutUrl: function () { return '/checkout' }
  }

  /* ---------------------------------------------------------------- ecwid */

  var EcwidDriver = {
    name: 'ecwid',
    _ready: function () {
      return new Promise(function (resolve, reject) {
        if (window.Ecwid && window.Ecwid.Cart) return resolve()
        var tries = 0
        var t = setInterval(function () {
          if (window.Ecwid && window.Ecwid.Cart) { clearInterval(t); resolve() }
          else if (++tries > 100) { clearInterval(t); reject(new Error('Ecwid storefront did not load')) }
        }, 100)
      })
    },
    _shape: function (cart) {
      return {
        items: (cart.items || []).map(function (i, n) {
          var opts = {}
          ;(i.selectedOptions || []).forEach(function (o) { opts[o.name] = o.valuesArray ? o.valuesArray.join(', ') : o.value })
          return {
            key: String(i.id != null ? i.id : n),
            id: i.product ? i.product.id : i.productId,
            title: i.product ? i.product.name : i.name,
            quantity: i.quantity,
            price: Math.round((i.price || 0) * 100),
            line_price: Math.round((i.price || 0) * 100) * i.quantity,
            image: (i.product && i.product.smallThumbnailUrl) || '',
            options: opts
          }
        }),
        total: Math.round((cart.total || 0) * 100)
      }
    },
    get: function () {
      var self = this
      return this._ready().then(function () {
        return new Promise(function (resolve) {
          window.Ecwid.Cart.get(function (cart) { resolve(self._shape(cart)) })
        })
      })
    },
    add: function (line) {
      var self = this
      return this._ready().then(function () {
        return new Promise(function (resolve, reject) {
          window.Ecwid.Cart.addProduct({
            id: Number(line.id),
            quantity: line.quantity || 1,
            options: line.options || {},
            callback: function (success) {
              if (!success) return reject(new Error('Ecwid rejected the item'))
              self.get().then(resolve)
            }
          })
        })
      })
    },
    change: function (key, quantity) {
      var self = this
      return this._ready().then(function () {
        return new Promise(function (resolve) {
          if (quantity > 0) window.Ecwid.Cart.setProductQuantity(Number(key), quantity)
          else window.Ecwid.Cart.removeProduct(Number(key))
          setTimeout(function () { self.get().then(resolve) }, 250)
        })
      })
    },
    checkoutUrl: function () { return '#!/~/cart' }
  }

  var DRIVERS = { local: LocalDriver, shopify: ShopifyDriver, ecwid: EcwidDriver }
  var driver = DRIVERS[MODE] || LocalDriver

  window.MTCommerce = {
    mode: driver.name,
    money: money,
    get: function () { return driver.get() },
    add: function (line) { return driver.add(line) },
    change: function (key, quantity) { return driver.change(key, quantity) },
    checkoutUrl: function () { return driver.checkoutUrl() }
  }
})()
