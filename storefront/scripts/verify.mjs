import { createHash } from "node:crypto";
import { readFile, stat } from "node:fs/promises";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

const root = new URL("..", import.meta.url).pathname.replace(/^\/(.:)/, "$1");
const text = async (path) => readFile(join(root, path), "utf8");
const failures = [];
const assert = (condition, message) => {
  if (!condition) failures.push(message);
};

const notice =
  "New Website Coming! For all orders email orders@mtuniforms.com or call us directly at (814) 536-2390.";
const [app, data, css, sourceHtml] = await Promise.all(
  ["src/App.tsx", "src/data.ts", "src/styles.css", "index.html"].map(text),
);
assert(data.includes(notice), "exact continuity notice is missing");
assert(
  (data.match(/sourceUrl: 'https:\/\//g) || []).length === 7,
  "fixture catalog must contain exactly seven source-backed products",
);
assert(
  app.includes("Request preview. No payment is processed."),
  "no-payment boundary is missing",
);
assert(
  app.includes("drawer-notice") && app.includes("{NOTICE}"),
  "request review must repeat the exact continuity notice",
);
assert(
  app.includes("mailto:") && app.includes("tel:+18145362390"),
  "email and telephone fallback actions are missing",
);
assert(
  app.includes("no-results-actions") &&
    app.includes("No products match those filters"),
  "no-results contact recovery is missing",
);
assert(
  app.includes("request-note") && app.includes("item.note"),
  "request review must expose personalization notes",
);
assert(
  app.includes("disabled={!isComplete}") &&
    app.includes("aria-invalid={option.required && !selections[option.id]}"),
  "required choices must prevent incomplete requests and identify missing fields",
);
assert(
  app.includes("useDialogFocus") && app.includes('event.key === "Escape"'),
  "drawer and dialog keyboard behavior is missing",
);
assert(
  app.includes("matchMedia") && app.includes("(prefers-reduced-motion: reduce)"),
  "programmatic scrolling must respect reduced motion",
);
assert(
  css.includes("@media (max-width: 800px)") &&
    css.includes("prefers-reduced-motion"),
  "responsive or reduced-motion rules are missing",
);
assert(
  css.includes("--orange: #b8440c"),
  "action orange does not meet the chosen white-text contrast floor",
);
assert(
  !css.includes("max-height: calc(100dvh - 78px)"),
  "desktop configurator must not create a second page scroll context",
);
assert(
  sourceHtml.includes("SEED 734cebaa"),
  "direction contract did not survive in source",
);
assert(
  !`${app}\n${data}\n${css}`.match(/Davidkelly|khuntington79|AdminB/i),
  "credential-like literal detected",
);

const hashes = new Map([
  [
    "public/assets/1d8171ec58d145a783246357566377929b0020bdc09fbaef5ec8f9c5e0807663.jpg",
    "51a7098fd889c2488759957e7beb30d01dde8dbaab224e230a0aef77ae9f8758",
  ],
  [
    "public/assets/23b8c837cdb88630c233f10e48d9cbf9877a13a7d06a78946add0f1a2905fefb.jpg",
    "eeca37448284d12da60f4d5e7d2105e30bc2c84ce545c4ee2e6332f02c2e8463",
  ],
  [
    "public/assets/606ddfa707c44874da1ed1c8edf2d58653bded851ec79b0f4bb7f8482ea45afd.jpg",
    "d89e4dd3dea910e788e40a7871313a7629abe08156e301ad29cfbcb8f7d5c0aa",
  ],
  [
    "public/assets/74d50994de2984e114e378f4dd8c92f57fff021e3739fac6abc0307609527640.jpg",
    "9998b671bc5d5ff90d98bc8c32887233eaec476fb923fca3e550b5447cde6fcb",
  ],
  [
    "public/assets/9f7bf62d0dab56c43af0c4dfc17ca7600932284eba7fac15df849c47d16da635.jpg",
    "c70601e7acfcf3e603202440e093c0f56ce7c22af197043004f632fe13bae25f",
  ],
  [
    "public/assets/d269c3c8148366cd9a50cb138bb58fec229080eeccde08ebe0a68ded94a56baa.jpg",
    "9de0690431caf87c427349e882ed78559353afd1f5b6918a2b3812747c956625",
  ],
  [
    "public/assets/f3bb10376c9a347e90d7a60e4357b9e66b98b91479c04706be28a47dfe15104f.jpg",
    "4248bdcc4fe00f893b11bfe6d3e2242da0bd2bc2390d711b47ce7b54ba71d064",
  ],
  [
    "public/assets/fonts/archivo-variable.woff2",
    "e3a28eade21a900c7155a247757f4b2834c07bb7ef07ad7efa55cebaac1e8f5e",
  ],
]);
for (const [path, expected] of hashes) {
  const bytes = await readFile(join(root, path)).catch(() => null);
  assert(
    bytes && createHash("sha256").update(bytes).digest("hex") === expected,
    `asset hash mismatch: ${path}`,
  );
}

const typecheck = spawnSync(
  process.execPath,
  [join(root, "node_modules/typescript/bin/tsc"), "--noEmit"],
  { cwd: root, encoding: "utf8" },
);
const bundle =
  typecheck.status === 0
    ? spawnSync(process.execPath, [join(root, "node_modules/vite/bin/vite.js"), "build"], {
        cwd: root,
        encoding: "utf8",
      })
    : null;
assert(
  typecheck.status === 0 && bundle?.status === 0,
  `production build failed: ${typecheck.error?.message || typecheck.stderr || typecheck.stdout || bundle?.error?.message || bundle?.stderr || bundle?.stdout}`,
);
const distHtml = await text("dist/index.html").catch(() => "");
assert(
  distHtml.includes("SEED 734cebaa"),
  "direction contract was stripped from production output",
);
assert(
  (await stat(join(root, "dist/index.html")).catch(() => null))?.size > 500,
  "production entry is missing or empty",
);

if (failures.length) {
  console.error(JSON.stringify({ passed: false, failures }, null, 2));
  process.exit(1);
}
console.log(
  JSON.stringify(
    {
      passed: true,
      products: 7,
      asset_hashes: hashes.size,
      production_contract: true,
    },
    null,
    2,
  ),
);
