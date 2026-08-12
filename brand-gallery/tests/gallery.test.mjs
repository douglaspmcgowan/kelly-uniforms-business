import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join, normalize } from 'node:path';
import test from 'node:test';

const root = new URL('../', import.meta.url).pathname.replace(/^\/(.:\/)/, '$1');
const types = { '.css': 'text/css', '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png' };

let server;
let baseUrl;

test.before(async () => {
  server = createServer(async (request, response) => {
    const requested = request.url === '/' ? 'index.html' : request.url.slice(1);
    const file = normalize(join(root, requested));
    if (!file.startsWith(normalize(root))) {
      response.writeHead(403).end();
      return;
    }
    try {
      const body = await readFile(file);
      response.writeHead(200, { 'content-type': types[extname(file)] ?? 'application/octet-stream' });
      response.end(body);
    } catch {
      response.writeHead(404).end();
    }
  });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});

test.after(() => new Promise((resolve) => server.close(resolve)));

test('serves a stakeholder decision page with the verified public status', async () => {
  const response = await fetch(`${baseUrl}/`);
  assert.equal(response.status, 200, 'the gallery home page must resolve');
  const html = await response.text();

  for (const phrase of ['Service Standard', 'Quartermaster', 'One Mission', 'Recovery groundwork verified']) {
    assert.match(html, new RegExp(phrase), `missing public gallery copy: ${phrase}`);
  }

  assert.match(html, /Private platform exports[\s\S]{0,120}>Remain</);
  assert.match(html, /Temporary ordering notice[\s\S]{0,120}>Pending</);
  assert.match(html, /Platform selection[\s\S]{0,120}>Separate</);

  assert.match(html, /Recommended direction/i);
  assert.match(html, /exploratory concepts/i);
  assert.match(html, /not final production trademarks/i);
});

test('keeps credentials and private recovery mechanics outside the published page', async () => {
  const html = await (await fetch(`${baseUrl}/`)).text();
  const forbidden = [
    /password\s*[:=]/i,
    /Davidkelly/i,
    /Bitwarden/i,
    /C:\\Users\\/i,
    /sha-?256/i,
    /customer records/i,
    /credential broker/i,
  ];
  for (const pattern of forbidden) {
    assert.doesNotMatch(html, pattern, `published page leaked forbidden material: ${pattern}`);
  }
});

test('serves every brand-direction board as an image', async () => {
  const assets = [
    'assets/brand-directions/01-service-standard.png',
    'assets/brand-directions/02-quartermaster.png',
    'assets/brand-directions/03-one-mission.png',
  ];
  for (const asset of assets) {
    const response = await fetch(`${baseUrl}/${asset}`);
    assert.equal(response.status, 200, `${asset} must resolve`);
    assert.equal(response.headers.get('content-type'), 'image/png');
    assert.ok((await response.arrayBuffer()).byteLength > 1_000_000, `${asset} must be the full board`);
  }
});

test('ships the responsive focal fix and a self-hosted display face', async () => {
  const html = await (await fetch(`${baseUrl}/`)).text();
  const css = await (await fetch(`${baseUrl}/styles.css`)).text();
  const font = await fetch(`${baseUrl}/assets/fonts/archivo-variable.woff2`);

  assert.match(html, /class="mobile-status"/);
  assert.match(css, /@font-face[\s\S]*Archivo Gallery/);
  assert.match(css, /\.sheet-header h2 \{[^}]*overflow-wrap: anywhere/);
  assert.doesNotMatch(css, /Bahnschrift|Aptos/);
  assert.equal(font.status, 200);
  assert.ok((await font.arrayBuffer()).byteLength > 50_000);
});
