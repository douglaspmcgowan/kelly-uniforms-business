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
      var url = window.MTCommerce.checkoutUrl()
      /* Remove the href outright when there is nothing to send. `aria-disabled` announces a state to
         assistive technology; it does not stop an <a> from activating, so an empty cart used to open
         the customer's mail client on a blank order. */
      if (cart.items.length && url) checkout.href = url
      else checkout.removeAttribute('href')
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
      /* The chip's own data-label, never its text: the text has the surcharge appended, so
         reading it put "(+$5.00)" inside the size on the order ticket the shop works from. */
      input.setAttribute('data-label', chip.getAttribute('data-label') || chip.textContent.trim())
      input.setAttribute('data-price-delta', chip.getAttribute('data-price-delta') || '0')
    }
    group.removeAttribute('aria-invalid')
    clearFormError(chip.closest('form'))
    updatePrice(chip.closest('form'))
  })

  document.addEventListener('change', function (e) {
    if (!e.target.matches('select[data-option-input]')) return
    var sel = e.target.selectedOptions[0]
    e.target.setAttribute('data-price-delta', sel ? (sel.getAttribute('data-price-delta') || '0') : '0')
    e.target.setAttribute('data-label', sel ? (sel.getAttribute('data-label') || sel.textContent.trim()) : '')
    // Mirror the chip handler: a select-backed group used to keep aria-invalid and leave the error
    // message on screen after the customer had fixed it, until the next submit.
    var group = e.target.closest('[data-option]')
    if (group && e.target.value) group.removeAttribute('aria-invalid')
    clearFormError(e.target.closest('form'))
    updatePrice(e.target.closest('form'))
  })

  function clearFormError (form) {
    if (!form) return
    // Only once every required group is satisfied — clearing on the first fix would hide a message
    // that still applies to another group.
    if (firstMissing(form)) return
    var err = $('[data-form-error]', form)
    if (err) err.hidden = true
  }

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
      /* Twenty-two groups in this catalog are labelled literally "Option", and the W. Alboum caps
         carry TWO of them — cap device (P Button / FD Button) and band style. Keying purely by
         legend text meant the second silently overwrote the first, so an officer could pick the
         police button, see the right price, and have the shop receive an order that never mentioned
         it. The option id disambiguates; the label stays first so the order ticket still reads in
         the shop's own words. Renaming the groups in the catalog is the real fix (SETUP.md manual
         step 7); this makes the data survive in the meantime instead of vanishing. */
      if (Object.prototype.hasOwnProperty.call(out, name)) {
        name = name + ' (' + (group.getAttribute('data-option-id') || input.name) + ')'
      }
      out[name] = input.getAttribute('data-label') || input.value
    })
    $$('input[name^="properties["], textarea[name^="properties["]', form).forEach(function (el) {
      if (!el.value.trim()) return
      out[el.name.replace(/^properties\[|\]$/g, '')] = el.value.trim()
    })
    return out
  }

  /* The selected values of the variant-defining groups, in the order Shopify lists the options —
     which is DOM order, because main-product.liquid renders them from product.options_with_values. */
  function selectedOptionValues (form) {
    return $$('[data-option]', form).map(function (group) {
      var input = $('[data-option-input]', group) || $('input[type=text], textarea', group)
      return input ? (input.getAttribute('data-label') || input.value) : ''
    })
  }

  function variantMap (form) {
    var el = $('script[data-variant-map]', form)
    if (!el) return []
    try { return JSON.parse(el.textContent) || [] } catch (e) { return [] }
  }

  /* Resolve the chosen combination to a variant id. Empty in the preview, which has no variants —
     the caller falls back to the product id there, which is what the local driver expects. */
  function resolveVariant (form) {
    var chosen = selectedOptionValues(form)
    if (!chosen.length) return null
    var wanted = chosen.join(' / ')
    return variantMap(form).filter(function (v) {
      return (v.options || []).join(' / ') === wanted
    })[0] || null
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
    var variant = resolveVariant(form)
    var opts = collectOptions(form)

    /* When a real variant carries the choice, do not also send it as a line-item property: Shopify
       already prints the variant's options on the order line, and sending both put every size and
       colour on the ticket twice. The demoted groups and the decoration fields stay properties,
       which is the whole point of the demotion. */
    if (variant) {
      $$('[data-option]', form).forEach(function (group) {
        var legend = $('legend', group)
        if (legend) delete opts[legend.textContent.replace('*', '').trim()]
      })
    }

    window.MTCommerce.add({
      id: form.getAttribute('data-product-id'),
      variantId: (variant && variant.id) || form.getAttribute('data-variant-id') || form.getAttribute('data-product-id'),
      title: form.getAttribute('data-title'),
      price: unitPrice(form),
      image: form.getAttribute('data-image'),
      quantity: Math.max(1, Number(qtyEl && qtyEl.value) || 1),
      options: opts,
      variantOptions: variant ? selectedOptionValues(form) : null
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
