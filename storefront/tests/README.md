# storefront tests

`storefront.spec.ts` is the behavioural suite for the primary surface, run by
`npm test` (after `scripts/verify.mjs`) or `npm run test:e2e` on its own. It
asserts what the page *does* — catalog renders, filters narrow, search finds and
reports empty honestly, a configured fixture reaches the request drawer, the
keyboard gets a visible focus ring — plus an `@axe-core/playwright` scan that
must report no serious or critical violation. It deliberately avoids asserting
markup structure or styling, so a framework move can be proven to be a move
rather than a rewrite by running it unchanged on both sides.

`computed-style-snapshot.mjs` and `computed-style-diff.mjs` are the proof harness
for token work. The snapshot drives the running dev server through six states and
dumps every computed property of every element; the diff compares two snapshots
property by property. Use them whenever a change is claimed to be non-visual:

    npx vite --port 5311 --strictPort &
    node tests/computed-style-snapshot.mjs before.json    # on the old tree
    node tests/computed-style-snapshot.mjs after.json     # on the new tree
    node tests/computed-style-diff.mjs before.json after.json

The diff exits non-zero if a single property moved.
