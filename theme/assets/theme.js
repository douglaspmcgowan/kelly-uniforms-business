/* Theme behaviour. Platform-blind: every commerce call goes through window.MTCommerce. */
(function () {
  'use strict'

  var $ = function (sel, root) { return (root || document).querySelector(sel) }
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)) }

  /* ---------------------------------------------------------- cart drawer */

  var drawer = $('#cart-drawer')
  var scrim = $('#drawer-scrim')
  var lastFocus = null

  function openDrawer () {
    if (!drawer) return
    lastFocus = document.activeElement
    drawer.hidden = false
    if (scrim) scrim.hidden = false
    var close = $('[data-cart-close]', drawer)
    if (close) close.focus()
    document.addEventListener('keydown', onKeydown)
  }

  function closeDrawer () {
    if (!drawer) return
    drawer.hidden = true
    if (scrim) scrim.hidden = true
    document.removeEventListener('keydown', onKeydown)
    if (lastFocus && lastFocus.focus) lastFocus.focus()
  }

  function onKeydown (e) {
    if (e.key === 'Escape') return closeDrawer()
    if (e.key !== 'Tab' || !drawer) return
    var focusable = $$('button, [href], input, select, textarea', drawer)
      .filter(function (el) { return !el.disabled && el.offsetParent !== null })
    if (!focusable.length) return
    var first = focusable[0]
    var last = focusable[focusable.length - 1]
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus() }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus() }
  }

  document.addEventListener('click', function (e) {
    if (e.target.closest('[data-cart-open]')) { e.preventDefault(); openDrawer() }
    if (e.target.closest('[data-cart-close]') || e.target === scrim) { e.preventDefault(); closeDrawer() }
  })

  /* ------------------------------------------------------------ rendering */

  function renderCart (cart) {
    var count = cart.items.reduce(function (s, i) { return s + i.quantity }, 0)
    $$('[data-cart-open]').forEach(function (b) { b.setAttribute('data-count', String(count)) })

    var empty = $('[data-cart-empty]')
    var lines = $('[data-cart-lines]')
    var total = $('[data-cart-total]')
    if (total) total.textContent = window.MTCommerce.money(cart.total)
    if (empty) empty.hidden = cart.items.length > 0
    if (!lines) return

    lines.innerHTML = cart.items.map(function (i) {
      var opts = Object.keys(i.options || {})
        .filter(function (k) { return i.options[k] })
        .map(function (k) { return escapeHtml(k) + ': ' + escapeHtml(i.options[k]) }).join(' · ')
      return '<div class="line-item">' +
        (i.image ? '<img src="' + escapeAttr(i.image) + '" alt="" width="56" height="56">' : '<div></div>') +
        '<div><strong>' + escapeHtml(i.title) + '</strong>' +
        (opts ? '<div class="line-item__opts">' + opts + '</div>' : '') +
        '<div class="line-item__opts">' +
        '<button class="chip" type="button" data-qty data-key="' + escapeAttr(i.key) + '" data-to="' + (i.quantity - 1) + '" aria-label="Decrease quantity">−</button> ' +
        i.quantity +
        ' <button class="chip" type="button" data-qty data-key="' + escapeAttr(i.key) + '" data-to="' + (i.quantity + 1) + '" aria-label="Increase quantity">+</button>' +
        '</div></div>' +
        '<div>' + window.MTCommerce.money(i.line_price) + '</div>' +
        '</div>'
    }).join('')

    var checkout = $('[data-cart-checkout]')
    if (checkout) {
      checkout.href = window.MTCommerce.checkoutUrl()
      checkout.textContent = window.MTCommerce.mode === 'local' ? 'Send this order to the store' : 'Continue to checkout'
      checkout.setAttribute('aria-disabled', cart.items.length ? 'false' : 'true')
    }
  }

  function escapeHtml (s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]
    })
  }
  var escapeAttr = escapeHtml

  document.addEventListener('click', function (e) {
    var q = e.target.closest('[data-qty]')
    if (!q) return
    e.preventDefault()
    window.MTCommerce.change(q.getAttribute('data-key'), Number(q.getAttribute('data-to'))).then(renderCart)
  })

  /* ------------------------------------------------------- option choosing */

  document.addEventListener('click', function (e) {
    var chip = e.target.closest('[data-option-chip]')
    if (!chip) return
    e.preventDefault()
    var group = chip.closest('[data-option]')
    $$('[data-option-chip]', group).forEach(function (c) { c.setAttribute('aria-pressed', String(c === chip)) })
    var input = $('[data-option-input]', group)
    if (input) {
      input.value = chip.getAttribute('data-value-id')
      input.setAttribute('data-label', chip.textContent.trim())
      input.setAttribute('data-price-delta', chip.getAttribute('data-price-delta') || '0')
    }
    group.removeAttribute('aria-invalid')
    updatePrice(chip.closest('form'))
  })

  document.addEventListener('change', function (e) {
    if (!e.target.matches('select[data-option-input]')) return
    var sel = e.target.selectedOptions[0]
    e.target.setAttribute('data-price-delta', sel ? (sel.getAttribute('data-price-delta') || '0') : '0')
    e.target.setAttribute('data-label', sel ? sel.textContent.trim() : '')
    updatePrice(e.target.closest('form'))
  })

  /* Every price here is in cents, base and deltas alike, because that is what Shopify's money
     filters expect. Do not reintroduce a conversion in this function: the delta arrives as cents
     already, and multiplying it here is what made the label and the charge disagree. */
  function unitPrice (form) {
    var base = Number(form.getAttribute('data-base-price')) || 0
    return $$('[data-option-input]', form).reduce(function (sum, el) {
      return sum + (Number(el.getAttribute('data-price-delta')) || 0)
    }, base)
  }

  function updatePrice (form) {
    if (!form) return
    var out = $('.product__price')
    if (out) out.textContent = window.MTCommerce.money(unitPrice(form))
  }

  /* ------------------------------------------------------------ add to cart */

  function collectOptions (form) {
    var out = {}
    $$('[data-option]', form).forEach(function (group) {
      var input = $('[data-option-input]', group) || $('input[type=text], textarea', group)
      if (!input || !input.value) return
      var legend = $('legend', group)
      var name = legend ? legend.textContent.replace('*', '').trim() : input.name
      out[name] = input.getAttribute('data-label') || input.value
    })
    $$('input[name^="properties["], textarea[name^="properties["]', form).forEach(function (el) {
      if (!el.value.trim()) return
      out[el.name.replace(/^properties\[|\]$/g, '')] = el.value.trim()
    })
    return out
  }

  function firstMissing (form) {
    return $$('[data-option][data-required="true"]', form).filter(function (group) {
      var input = $('[data-option-input]', group) || $('input[type=text], textarea', group)
      return !input || !input.value
    })[0]
  }

  document.addEventListener('submit', function (e) {
    var form = e.target.closest('[data-product-form]')
    if (!form) return
    e.preventDefault()

    var err = $('[data-form-error]', form)
    var missing = firstMissing(form)
    if (missing) {
      missing.setAttribute('aria-invalid', 'true')
      if (err) {
        var legend = $('legend', missing)
        err.textContent = 'Choose ' + (legend ? legend.textContent.replace('*', '').trim().toLowerCase() : 'the required options') + ' first.'
        err.hidden = false
      }
      missing.scrollIntoView({ block: 'center', behavior: 'smooth' })
      return
    }
    if (err) err.hidden = true

    var qtyEl = $('input[name=quantity]', form)
    window.MTCommerce.add({
      id: form.getAttribute('data-product-id'),
      variantId: form.getAttribute('data-variant-id') || form.getAttribute('data-product-id'),
      title: form.getAttribute('data-title'),
      price: unitPrice(form),
      image: form.getAttribute('data-image'),
      quantity: Math.max(1, Number(qtyEl && qtyEl.value) || 1),
      options: collectOptions(form)
    }).then(function (cart) {
      renderCart(cart)
      openDrawer()
    }).catch(function (e2) {
      if (err) { err.textContent = e2.message; err.hidden = false }
    })
  })

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-add-to-cart]')
    if (!btn) return
    e.preventDefault()
    btn.disabled = true
    window.MTCommerce.add({
      id: btn.getAttribute('data-product-id'),
      variantId: btn.getAttribute('data-variant-id') || btn.getAttribute('data-product-id'),
      title: btn.getAttribute('data-title'),
      price: Number(btn.getAttribute('data-price')) || 0,
      image: btn.getAttribute('data-image'),
      quantity: 1,
      options: {}
    }).then(function (cart) {
      renderCart(cart)
      openDrawer()
    }).finally(function () { btn.disabled = false })
  })

  /* ---------------------------------------------------------------- start */

  if (window.MTCommerce) window.MTCommerce.get().then(renderCart).catch(function () {})
})()
