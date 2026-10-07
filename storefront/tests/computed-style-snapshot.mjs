// Computed-style snapshot of the storefront across five interaction states.
// Dumps every computed property of every element so a before/after diff is total.
import { chromium } from '@playwright/test';
import { writeFileSync } from 'node:fs';

const out = process.argv[2];
const url = process.argv[3] || 'http://localhost:5311/';

const grab = () => {
  const path = (el) => {
    const parts = [];
    while (el && el.nodeType === 1 && el !== document.documentElement) {
      const p = el.parentNode; let i = 0, n = 0;
      if (p) for (let c = p.firstElementChild; c; c = c.nextElementSibling) { n++; if (c === el) i = n; }
      parts.unshift(el.tagName.toLowerCase() + '[' + i + ']');
      el = p;
    }
    parts.unshift('html');
    return parts.join('>');
  };
  const els = [...document.querySelectorAll('*')];
  return els.map((el, k) => {
    const cs = getComputedStyle(el);
    const o = {};
    for (let j = 0; j < cs.length; j++) o[cs[j]] = cs.getPropertyValue(cs[j]);
    return { key: path(el) + '#' + k, props: o };
  });
};

const browser = await chromium.launch();
const page = await browser.newPage({ colorScheme: 'light', viewport: { width: 1440, height: 950 } });
await page.goto(url, { waitUntil: 'networkidle' });
await page.waitForSelector('.product-card__hit');
await page.mouse.move(2, 2);
const states = {};
const snap = async (n) => { await page.mouse.move(2, 2); await page.waitForTimeout(700); states[n] = await page.evaluate(grab); };

await snap('S1_initial');
await page.locator('.product-card__hit').first().click();
await page.waitForTimeout(700);
await snap('S2_configurator');
const chips = page.locator('.options .choice-grid');
for (let i = 0; i < await chips.count(); i++) await chips.nth(i).locator('button').first().click();
const rad = page.locator('fieldset.fulfillment input[type=radio]').first();
if (await rad.count()) await rad.check();
await page.waitForTimeout(700);
await snap('S3_optionschosen');
await page.locator('.configurator .button.primary.full').first().click();
await page.waitForTimeout(700);
if (!(await page.locator('.drawer.is-open').count())) {
  await page.locator('.request-button').first().click();
}
await page.waitForTimeout(700);
await snap('S4_drawer');
await page.locator('.drawer .icon-button').first().click();
await page.waitForTimeout(700);
await page.locator('.fit-callout').first().click();
await page.waitForTimeout(700);
await snap('S5_sizeguide');
// keyboard focus, so the focus ring is a measured value rather than an assumed one
await page.keyboard.press('Tab');
await page.waitForTimeout(700);
await snap('S6_firstfocus');

await browser.close();
writeFileSync(out, JSON.stringify(states));
console.log('wrote', out, Object.entries(states).map(([k, v]) => k + '=' + v.length).join(' '));
