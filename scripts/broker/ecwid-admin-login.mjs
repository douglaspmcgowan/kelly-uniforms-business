/**
 * Approved Bitwarden-brokered login broker for the MT Uniforms Ecwid control panel.
 *
 * Invoked ONLY through the harness broker:
 *
 *   & "$env:USERPROFILE\.agents\tools\Invoke-WithBitwardenSecret.ps1" `
 *       -CommandId "mtuniforms-ecwid-admin-login"
 *
 * Purpose is diagnostic: establish what the Ecwid account is actually doing
 * (abandoned, Clover-synced catalog, or an active sales channel). It performs
 * no configuration change.
 *
 * Same contract as the OpenCart broker: credentials arrive as environment
 * variables, are never printed or written, and the process exits non-zero on
 * failure including any MFA challenge.
 */

import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { homedir } from 'node:os';

const LOGIN_URL = process.env.MT_UNIFORMS_ECWID_URL ?? 'https://my.ecwid.com/cp/';
const STATE_PATH =
  process.env.MT_UNIFORMS_ECWID_STATE_PATH ??
  join(homedir(), '.local', 'mtuniforms', 'ecwid-admin-state.json');

const username = process.env.MT_UNIFORMS_ECWID_ADMIN_USERNAME;
const password = process.env.MT_UNIFORMS_ECWID_ADMIN_PASSWORD;

if (!username || !password) {
  console.error(
    'Missing MT_UNIFORMS_ECWID_ADMIN_USERNAME or MT_UNIFORMS_ECWID_ADMIN_PASSWORD. ' +
      'Run this through Invoke-WithBitwardenSecret.ps1, not directly.'
  );
  process.exit(2);
}

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

  await page.goto(LOGIN_URL, { waitUntil: 'domcontentloaded', timeout: 30_000 });
  await page.fill('input[type="email"], input[name="email"]', username);
  await page.fill('input[type="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForLoadState('networkidle', { timeout: 45_000 });

  if (/\/cp\//.test(page.url()) && !/login|signin/i.test(page.url())) {
    await mkdir(dirname(STATE_PATH), { recursive: true });
    await context.storageState({ path: STATE_PATH });
    console.log(`Authenticated. Storage state written to ${STATE_PATH}`);
  } else {
    console.error(
      'Login did not reach the Ecwid control panel. If the account requires MFA or a ' +
        'device confirmation email, unattended login is not supported; use the attended path.'
    );
    exitCode = 1;
  }
} catch (error) {
  console.error(`Login broker failed: ${error.message}`);
  exitCode = 1;
} finally {
  await browser.close();
}

process.exit(exitCode);
