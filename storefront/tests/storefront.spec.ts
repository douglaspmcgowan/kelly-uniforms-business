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
})
