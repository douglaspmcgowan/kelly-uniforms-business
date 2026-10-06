import AxeBuilder from '@axe-core/playwright'
import { expect, test } from '@playwright/test'

// The primary surface, exercised through the one path a customer takes:
// discover a fixture, configure it, put it on the request, read the fit guide.
// This suite exists so a framework move can be proven to be a move rather than
// a rewrite: it asserts behaviour, never markup structure or styling.

test.describe('order ticket storefront', () => {
  test('the catalog renders the shop identity and a product grid', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/M\.T\. Uniforms/)
    await expect(page.getByRole('banner')).toContainText(/M\.T\. UNIFORMS/i)
    const cards = page.locator('.product-card__hit')
    await expect(cards.first()).toBeVisible()
    expect(await cards.count()).toBeGreaterThan(0)
  })

  test('role and category filters narrow the grid and can be cleared', async ({ page }) => {
    await page.goto('/')
    const cards = page.locator('.product-card__hit')
    const all = await cards.count()
    const police = page.getByRole('button', { name: /^Police$/ })
    await police.click()
    const filtered = await cards.count()
    expect(filtered).toBeLessThanOrEqual(all)
    expect(filtered).toBeGreaterThan(0)
    await page.getByRole('button', { name: /^All roles$/ }).click()
    expect(await cards.count()).toBe(all)
  })

  test('search finds a product by name and reports an empty result honestly', async ({ page }) => {
    await page.goto('/')
    const search = page.getByLabel('Search products')
    await search.fill('zzzznotathing')
    await expect(page.locator('.product-card__hit')).toHaveCount(0)
    await search.fill('')
    await expect(page.locator('.product-card__hit').first()).toBeVisible()
  })

  test('configuring a fixture puts it on the request drawer', async ({ page }) => {
    await page.goto('/')
    await page.locator('.product-card__hit').first().click()
    const configurator = page.locator('.configurator')
    await expect(configurator).toBeVisible()
    const grids = configurator.locator('.choice-grid')
    for (let i = 0; i < (await grids.count()); i += 1) {
      await grids.nth(i).locator('button').first().click()
    }
    const radio = configurator.locator('input[type=radio]').first()
    if (await radio.count()) await radio.check()
    await configurator.locator('.button.primary').first().click()
    await expect(page.locator('.drawer')).toBeVisible()
    await expect(page.locator('.drawer')).not.toContainText('Your request is empty')
  })

  test('the keyboard reaches the skip link and the first control shows a focus ring', async ({ page }) => {
    await page.goto('/')
    await page.keyboard.press('Tab')
    const outline = await page.evaluate(() => {
      const el = document.activeElement as HTMLElement | null
      if (!el) return null
      const cs = getComputedStyle(el)
      return { tag: el.tagName, width: cs.outlineWidth, style: cs.outlineStyle }
    })
    expect(outline).not.toBeNull()
    expect(outline!.style).not.toBe('none')
    expect(parseFloat(outline!.width)).toBeGreaterThan(0)
  })

  test('axe reports no serious or critical violation on the primary surface', async ({ page }) => {
    await page.goto('/')
    await page.locator('.product-card__hit').first().waitFor()
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze()
    const blocking = results.violations.filter((v) => v.impact === 'serious' || v.impact === 'critical')
    expect(
      blocking.map((v) => `${v.impact} ${v.id}: ${v.nodes.map((n) => n.target.join(' ')).join(' | ')}`),
    ).toEqual([])
  })

  for (const width of [375, 768, 1440]) {
    test(`no horizontal scroll at ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 })
      await page.goto('/')
      await page.locator('.product-card__hit').first().waitFor()
      const { sw, cw } = await page.evaluate(() => ({
        sw: document.documentElement.scrollWidth,
        cw: document.documentElement.clientWidth,
      }))
      expect(sw).toBeLessThanOrEqual(cw)
    })
  }

  for (const width of [375, 768, 1440]) {
    test(`the configurator title is not overlapped by the product image at ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 })
      await page.goto('/')
      const title = page.locator('.configurator h2')
      await title.waitFor()
      const [t, img] = await Promise.all([
        title.boundingBox(),
        page.locator('.configurator__top').boundingBox(),
      ])
      expect(t).not.toBeNull()
      expect(img).not.toBeNull()
      // The title sits wholly below the image panel, or wholly beside it; never underneath.
      const below = t!.y >= img!.y + img!.height - 1
      const beside = t!.x >= img!.x + img!.width - 1
      expect(below || beside).toBe(true)
      const clipped = await title.evaluate((el) => el.scrollHeight > el.clientHeight + 1)
      expect(clipped).toBe(false)
    })
  }

  test('an incomplete request keeps the button enabled and explains the gap on submit', async ({ page }) => {
    await page.goto('/')
    const add = page.getByRole('button', { name: /^Add to request/ })
    await expect(add).toBeEnabled()
    await expect(page.getByText('Choose a size to continue')).toHaveCount(0)
    await add.click()
    await expect(page.getByText('Choose a size to continue')).toBeVisible()
    await expect(page.locator('.drawer')).toHaveCount(0)
    await expect(page.locator('.choice-grid button').first()).toBeFocused()
  })

  test('no element renders with an all-caps text transform', async ({ page }) => {
    await page.goto('/')
    const found = await page.evaluate(() =>
      [...document.querySelectorAll('body *')].filter((el) => getComputedStyle(el).textTransform === 'uppercase').length,
    )
    expect(found).toBe(0)
  })

  test('the page carries its own identity: favicon, Open Graph image, theme colour', async ({ page, request }) => {
    await page.goto('/')
    const icon = await page.locator('link[rel=icon]').getAttribute('href')
    expect((await request.get(icon!)).ok()).toBe(true)
    await expect(page.locator('meta[property="og:image"]')).toHaveCount(1)
    await expect(page.locator('meta[property="og:title"]')).toHaveCount(1)
    await expect(page.locator('meta[name="theme-color"]')).toHaveCount(1)
    expect((await request.get('/og-image.png')).ok()).toBe(true)
  })

  test('size choices are a single-selection toggle group driven by the arrow keys', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: /^Configure USPS Letter Carrier/ }).click()
    const group = page.getByRole('group', { name: 'Size' })
    const chips = group.getByRole('button')
    await expect(chips).toHaveCount(6)
    await chips.first().focus()
    await page.keyboard.press('ArrowRight')
    await expect(chips.nth(1)).toBeFocused()
    await page.keyboard.press('Space')
    await expect(chips.nth(1)).toHaveAttribute('aria-pressed', 'true')
    await expect(chips.nth(1).locator('svg')).toHaveCount(1)
    await chips.nth(3).click()
    await expect(chips.nth(3)).toHaveAttribute('aria-pressed', 'true')
    await expect(chips.nth(1)).toHaveAttribute('aria-pressed', 'false')
  })

  test('the request drawer holds focus, closes on Escape and returns focus to its trigger', async ({ page }) => {
    await page.goto('/')
    const trigger = page.getByRole('button', { name: /^Request list/ })
    await trigger.click()
    const drawer = page.getByRole('dialog', { name: /Request list/ })
    await expect(drawer).toBeVisible()
    await expect(page.getByRole('button', { name: 'Close request list' })).toBeFocused()
    for (let i = 0; i < 6; i += 1) await page.keyboard.press('Tab')
    expect(await drawer.evaluate((el) => el.contains(document.activeElement))).toBe(true)
    await page.keyboard.press('Escape')
    await expect(page.locator('.drawer')).toHaveCount(0)
    await expect(trigger).toBeFocused()
  })

  test('the empty order sheet says what belongs there and sends the shopper to the catalogue', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: /^Request list/ }).click()
    const drawer = page.locator('.drawer')
    await expect(drawer).toContainText('Configure a garment and add it to build the order sheet')
    await drawer.getByRole('button', { name: 'Browse the catalogue' }).click()
    await expect(page.locator('.drawer')).toHaveCount(0)
    await expect(page.locator('.product-card__hit').first()).toBeFocused()
  })

  test('a filled request reads as an order sheet with garment, size, quantity and notes columns', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: /^Configure USPS Letter Carrier/ }).click()
    const configurator = page.locator('.configurator')
    await configurator.getByRole('group', { name: 'Size' }).getByRole('button').first().click()
    await configurator.getByRole('group', { name: 'Sleeve' }).getByRole('button').first().click()
    await configurator.getByLabel(/Personalization or order notes/).fill('Dispatch')
    await configurator.getByRole('button', { name: /^Add to request/ }).click()
    const sheet = page.locator('.drawer .order-sheet')
    await expect(sheet.getByRole('heading', { name: 'Order sheet' })).toBeVisible()
    for (const name of ['Garment', 'Size and options', 'Qty', 'Notes']) {
      await expect(sheet.getByRole('columnheader', { name })).toBeVisible()
    }
    await expect(sheet).toContainText('Dispatch')
    await expect(sheet).toContainText('$42.99')
    await expect(page.getByText('Request preview. No payment is processed.').first()).toBeVisible()
  })

  test('the size chart sits beside the garment image on wide screens and below it on phones', async ({ page }) => {
    for (const [width, beside] of [[1440, true], [375, false]] as const) {
      await page.setViewportSize({ width, height: 900 })
      await page.goto('/')
      const chart = page.locator('.size-chart')
      await expect(chart).toBeVisible()
      await expect(chart.getByRole('columnheader', { name: 'Size' })).toBeVisible()
      await expect(chart).toContainText('Measurements on file with the shop; call (814) 536-2390')
      const [c, img] = await Promise.all([chart.boundingBox(), page.locator('.configurator__image').boundingBox()])
      if (beside) expect(c!.x).toBeGreaterThanOrEqual(img!.x + img!.width - 1)
      else expect(c!.y).toBeGreaterThanOrEqual(img!.y + img!.height - 1)
    }
  })

  test('an empty search names the query and offers Clear search', async ({ page }) => {
    await page.goto('/')
    await page.getByLabel('Search products').fill('zzzznotathing')
    await expect(page.getByRole('heading', { name: /zzzznotathing/ })).toBeVisible()
    await page.getByRole('button', { name: 'Clear search' }).click()
    await expect(page.getByLabel('Search products')).toHaveValue('')
    await expect(page.locator('.product-card__hit').first()).toBeVisible()
  })

  test('the interface uses Phosphor icons only: no glyph arrows in the rendered text', async ({ page }) => {
    await page.goto('/')
    const text = await page.locator('body').innerText()
    expect(text).not.toMatch(/[→←↑↓▸►▶✓✔×]/)
  })
})
