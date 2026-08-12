import { chromium } from './broker/node_modules/playwright/index.mjs';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const outputArg = process.argv.indexOf('--output');
const outputDir = resolve(outputArg >= 0 ? process.argv[outputArg + 1] : 'evidence/public-ordering-notice-20260812');
const exactNotice = 'New Website Coming! For all orders email orders@mtuniforms.com or call us directly at (814) 536-2390.';

const routes = [
  { id: 'home', url: 'https://www.mtuniforms.com/' },
  { id: 'category', url: 'https://www.mtuniforms.com/police-uniforms-equipment' },
  { id: 'product', url: 'https://www.mtuniforms.com/elbeco-tek2-cargo-pocket-trousers-trttcpo' },
  { id: 'cart', url: 'https://www.mtuniforms.com/index.php?route=checkout/cart' },
];

const viewports = [
  { id: 'desktop', width: 1440, height: 1000, isMobile: false },
  { id: 'mobile', width: 390, height: 844, isMobile: true },
];

const normalize = (value) => value.replace(/\s+/g, ' ').trim();
const browser = await chromium.launch({ headless: true });
const observations = [];

try {
  await mkdir(outputDir, { recursive: true });
  for (const viewport of viewports) {
    const context = await browser.newContext({
      viewport: { width: viewport.width, height: viewport.height },
      isMobile: viewport.isMobile,
      hasTouch: viewport.isMobile,
      locale: 'en-US',
    });

    for (const route of routes) {
      const page = await context.newPage();
      const response = await page.goto(route.url, { waitUntil: 'domcontentloaded', timeout: 60_000 });
      await page.waitForSelector('.module-header_notice', { state: 'visible', timeout: 30_000 });

      const result = await page.evaluate((expected) => {
        const notice = document.querySelector('.module-header_notice');
        const header = document.querySelector('header');
        const email = notice?.querySelector('a[href="mailto:orders@mtuniforms.com"]');
        const phone = notice?.querySelector('a[href^="tel:"]');
        const noticeRect = notice?.getBoundingClientRect();
        const headerRect = header?.getBoundingClientRect();
        const text = notice?.textContent?.replace(/\s+/g, ' ').trim() ?? '';
        return {
          title: document.title,
          final_url: location.href,
          exact_copy: text.includes(expected),
          visible: Boolean(noticeRect && noticeRect.width > 0 && noticeRect.height > 0),
          above_header: Boolean(noticeRect && headerRect && noticeRect.top <= headerRect.top),
          within_viewport_width: Boolean(noticeRect && noticeRect.left >= -1 && noticeRect.right <= innerWidth + 1),
          email_link: email?.getAttribute('href') ?? null,
          phone_link: phone?.getAttribute('href') ?? null,
          close_button_present: Boolean(notice?.querySelector('.hn-close')),
          header_visible: Boolean(headerRect && headerRect.width > 0 && headerRect.height > 0),
        };
      }, exactNotice);

      const screenshot = `${viewport.id}-${route.id}.png`;
      await page.screenshot({ path: resolve(outputDir, screenshot), fullPage: false });
      observations.push({
        viewport: viewport.id,
        viewport_size: { width: viewport.width, height: viewport.height },
        route: route.id,
        requested_url: route.url,
        http_status: response?.status() ?? null,
        screenshot,
        ...result,
      });
      await page.close();
    }
    await context.close();
  }
} finally {
  await browser.close();
}

const failures = observations.flatMap((item) => {
  const problems = [];
  if (item.http_status !== 200) problems.push('http-status');
  if (!item.exact_copy) problems.push('exact-copy');
  if (!item.visible) problems.push('notice-visible');
  if (!item.above_header) problems.push('notice-above-header');
  if (!item.within_viewport_width) problems.push('viewport-overflow');
  if (item.email_link !== 'mailto:orders@mtuniforms.com') problems.push('email-link');
  if (!item.header_visible) problems.push('header-visible');
  return problems.map((problem) => `${item.viewport}/${item.route}:${problem}`);
});

const report = {
  schema_version: 1,
  captured_at_utc: new Date().toISOString(),
  exact_notice: exactNotice,
  result: failures.length === 0 ? 'pass' : 'fail',
  checks: observations.length,
  failures,
  limitations: [
    'The phone number is rendered as plain text rather than a tel link.',
    'The notice exposes a close button, so a returning browser may retain a dismissal cookie.',
    'This public verification does not prove the authenticated admin module state or rollback configuration.',
  ],
  observations,
};

await writeFile(resolve(outputDir, 'report.json'), `${JSON.stringify(report, null, 2)}\n`, 'utf8');
process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
if (failures.length > 0) process.exitCode = 1;
