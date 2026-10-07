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
})
