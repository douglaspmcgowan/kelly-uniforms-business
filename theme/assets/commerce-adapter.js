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
    _read: function () {
      try { return JSON.parse(localStorage.getItem(this.KEY)) || [] } catch (e) { return [] }
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
      var key = line.id + ':' + JSON.stringify(line.options || {})
      var found = items.filter(function (i) { return i.key === key })[0]
      if (found) found.quantity += line.quantity || 1
      else {
        items.push({
          key: key,
          id: line.id,
          title: line.title,
          quantity: line.quantity || 1,
          price: line.price,
          image: line.image || '',
          options: line.options || {}
        })
      }
      return Promise.resolve(this._write(items))
    },
    change: function (key, quantity) {
      var items = this._read().filter(function (i) { return i.key !== key || quantity > 0 })
      items.forEach(function (i) { if (i.key === key) i.quantity = quantity })
      return Promise.resolve(this._write(items.filter(function (i) { return i.quantity > 0 })))
    },
    checkoutUrl: function () {
      // No payment rail in local mode. Hand the ticket to the store the way a phone order works.
      var self = this
      var lines = self._read().map(function (i) {
        var opts = Object.keys(i.options || {}).map(function (k) { return k + ': ' + i.options[k] }).join(', ')
        return '- ' + i.quantity + ' x ' + i.title + (opts ? ' (' + opts + ')' : '') + ' — ' + money(i.price * i.quantity)
      }).join('\n')
      var body = 'I would like to place this order:\n\n' + lines +
        '\n\nTotal: ' + money(self._shape(self._read()).total) +
        '\n\nName:\nDepartment / agency:\nPhone:\nPickup or ship:\n'
      return 'mailto:' + (CONFIG.contactEmail || 'orders@mtuniforms.com') +
        '?subject=' + encodeURIComponent('Order request from the website') +
        '&body=' + encodeURIComponent(body)
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
