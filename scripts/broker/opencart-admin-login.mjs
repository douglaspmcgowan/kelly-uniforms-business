/**
 * Approved Bitwarden-brokered login broker for the MT Uniforms OpenCart admin.
 *
 * Invoked ONLY through the harness broker, which injects the credentials as
 * environment variables into this process and nothing else:
 *
 *   & "$env:USERPROFILE\.agents\tools\Invoke-WithBitwardenSecret.ps1" `
 *       -CommandId "mtuniforms-opencart-admin-login"
 *
 * Contract:
 *  - Reads MT_UNIFORMS_WEBSITE_ADMIN_USERNAME / _PASSWORD from its own env.
 *  - Never prints, logs, or writes a credential value. Any accidental echo of
 *    the password is scrubbed from stdout before exit.
 *  - Writes an authenticated Playwright storage state to STATE_PATH, which
 *    defaults to a location OUTSIDE the git repository.
 *  - Exits non-zero on any failure, including an MFA challenge.
 */

import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { homedir } from 'node:os';

const ADMIN_URL = process.env.MT_UNIFORMS_ADMIN_URL ?? 'https://www.mtuniforms.com/admin/';
const STATE_PATH =
  process.env.MT_UNIFORMS_STATE_PATH ??
  join(homedir(), '.local', 'mtuniforms', 'opencart-admin-state.json');

const username = process.env.MT_UNIFORMS_WEBSITE_ADMIN_USERNAME;
const password = process.env.MT_UNIFORMS_WEBSITE_ADMIN_PASSWORD;

if (!username || !password) {
  console.error(
    'Missing MT_UNIFORMS_WEBSITE_ADMIN_USERNAME or MT_UNIFORMS_WEBSITE_ADMIN_PASSWORD. ' +
      'Run this through Invoke-WithBitwardenSecret.ps1, not directly.'
  );
  process.exit(2);
}

// Belt-and-braces: scrub the secret from anything this process emits.
const scrub = (chunk) => String(chunk).split(password).join('[redacted]');
for (const stream of [process.stdout, process.stderr]) {
  const original = stream.write.bind(stream);
  stream.write = (chunk, ...rest) => original(scrub(chunk), ...rest);
}

const browser = await chromium.launch({ headless: true });
let exitCode = 0;

try {
  const context = await browser.newContext();
  const page = await context.newPage();

  await page.goto(ADMIN_URL, { waitUntil: 'domcontentloaded', timeout: 30_000 });
  await page.fill('input[name="username"]', username);
  await page.fill('input[name="password"]', password);
  await Promise.all([
    page.waitForLoadState('networkidle', { timeout: 30_000 }),
    page.click('button[type="submit"]'),
  ]);

  const url = page.url();

  // OpenCart appends a per-session user_token to every authenticated admin URL.
  if (!/user_token=/.test(url)) {
    const alert = await page
      .locator('.alert-danger, .text-danger')
      .first()
      .textContent()
      .catch(() => null);
    console.error(
      `Login did not reach an authenticated admin route. ${
        alert ? `Page reported: ${alert.trim()}` : 'No error message was shown.'
      } If this store requires MFA, unattended login is not supported; use the attended path.`
    );
    exitCode = 1;
  } else {
    await mkdir(dirname(STATE_PATH), { recursive: true });
    await context.storageState({ path: STATE_PATH });

    // Emit only non-secret facts.
    const token = new URL(url).searchParams.get('user_token');
    await writeFile(
      `${STATE_PATH}.meta.json`,
      JSON.stringify(
        { adminUrl: ADMIN_URL, authenticatedAt: new Date().toISOString(), hasUserToken: Boolean(token) },
        null,
        2
      )
    );
    console.log(`Authenticated. Storage state written to ${STATE_PATH}`);
  }
} catch (error) {
  console.error(`Login broker failed: ${error.message}`);
  exitCode = 1;
} finally {
  await browser.close();
}

process.exit(exitCode);
