import { readFileSync } from 'node:fs';
const A = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const B = JSON.parse(readFileSync(process.argv[3], 'utf8'));
let totalProps = 0, totalDiff = 0;
const lines = [];
for (const state of Object.keys(A)) {
  const a = A[state], b = B[state] || [];
  const bm = new Map(b.map(e => [e.key, e.props]));
  let diffs = 0, props = 0, missing = 0;
  for (const e of a) {
    const bp = bm.get(e.key);
    if (!bp) { missing++; continue; }
    for (const [k, v] of Object.entries(e.props)) {
      props++;
      if (bp[k] !== v) { diffs++; if (lines.length < 40) lines.push(`${state} ${e.key} ${k}: ${v} -> ${bp[k]}`); }
    }
  }
  totalProps += props; totalDiff += diffs;
  console.log(`${state}: elementsA=${a.length} elementsB=${b.length} missingInB=${missing} propsCompared=${props} propsDifferent=${diffs}`);
}
console.log(`TOTAL propsCompared=${totalProps} propsDifferent=${totalDiff}`);
if (lines.length) { console.log('--- first differences ---'); lines.forEach(l => console.log(l)); }
process.exit(totalDiff === 0 ? 0 : 1);
