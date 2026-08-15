/* Search, for the static preview only.

   This file is NOT part of `theme/` and never reaches Shopify. On a real store the search page is
   server-rendered: `search.terms` and `search.results` arrive populated and `main-search.liquid`
   renders them, including its no-results branch. A static build has no server, so the prototype's
   search box submitted a query that nothing answered — every term, matching or not, produced the
   same idle page. The index was already being generated and had no reader.

   Kept deliberately small and dependency-free. It reads the query, scores against the index the
   build writes, and fills in the same markup `main-search.liquid` produces, so the two runtimes
   look alike without the preview pretending to be Shopify. */
(function () {
  var params = new URLSearchParams(location.search)
  var q = (params.get('q') || '').trim()
  var main = document.querySelector('main') || document.body
  var shell = main.querySelector('.shell')
  if (!shell) return

  var input = document.getElementById('site-search')
  if (input && q) input.value = q

  var hint = shell.querySelector('.hint')
  var results = document.createElement('div')
  shell.appendChild(results)

  if (!q) return

  fetch('/search-index.json').then(function (r) { return r.json() }).then(function (index) {
    var terms = q.toLowerCase().split(/\s+/).filter(Boolean)
    var matchAll = function (hay) {
      hay = hay.toLowerCase()
      return terms.every(function (t) { return hay.indexOf(t) !== -1 })
    }

    var products = (index.products || []).filter(function (p) {
      return matchAll([p.t, p.v, p.m, p.o].join(' '))
    })
    var pages = (index.pages || []).filter(function (p) { return matchAll(p.t + ' ' + p.x) })

    var esc = function (s) {
      return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
        return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]
      })
    }
    var money = function (cents) {
      return '$' + (Number(cents) / 100).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
    }

    var total = products.length + pages.length
    if (hint) hint.textContent = total + (total === 1 ? ' result' : ' results') + ' for “' + q + '”'

    var html = ''

    /* Pages first when they match: someone typing "hemming" or "name tape" wants the tailoring
       page that explains it, and no product in this catalog carries either word. */
    if (pages.length) {
      html += '<ul class="search-pages" role="list">' + pages.map(function (p) {
        return '<li><a href="' + esc(p.u) + '">' + esc(p.t) + '</a></li>'
      }).join('') + '</ul>'
    }

    if (products.length) {
      html += '<div class="grid">' + products.map(function (p) {
        return '<article class="card">' +
          '<a class="card__media" href="' + esc(p.u) + '">' +
            (p.i ? '<img src="' + esc(p.i) + '" alt="" loading="lazy">' : '') +
          '</a>' +
          '<div class="card__body">' +
            (p.v ? '<p class="card__eyebrow">' + esc(p.v) + '</p>' : '') +
            '<a class="card__title" href="' + esc(p.u) + '">' + esc(p.t) + '</a>' +
            '<p class="card__price">' + money(p.p) + '</p>' +
          '</div>' +
        '</article>'
      }).join('') + '</div>'
    }

    if (!total) {
      html = '<p>Nothing matched that. Try a shorter term, or ' +
        '<a href="/pages/contact.html">ask us</a> — a lot of what we sell is ordered in.</p>'
    }

    results.innerHTML = html
  }).catch(function () {
    if (hint) hint.textContent = 'Search is unavailable right now. Please call (814) 536-2390.'
  })
})()
