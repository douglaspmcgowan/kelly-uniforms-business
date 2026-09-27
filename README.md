# kelly-uniforms-business

Client work for M.T. Uniforms, a Johnstown, Pennsylvania workwear and public-safety uniform shop: a
replacement storefront prototype, the brand-direction boards that chose its visual language, a static
renderer for the Shopify theme, and the migration records behind all three.

Everything here is built from recovered public evidence. No surface holds authenticated OpenCart or
Ecwid data, and none of them processes a payment.

## Start it

```powershell
cd storefront; npm install; npm run dev
```

That serves the customer-facing storefront prototype — the primary surface — at the URL Vite prints
(http://localhost:5173 by default).

## The surfaces

| Path | What it is | Start | Verify |
|---|---|---|---|
| `storefront/` | React order-ticket storefront prototype. Discovery, fit and options, request preparation, human ordering fallback. Deployed to Vercel | `npm install; npm run dev` | `npm test` |
| `brand-gallery/` | Static stakeholder page holding the brand-direction boards | `npx serve .` | `npm test` |
| `preview/` | Static renderer for the Liquid theme in `theme/`, for reviewing catalog pages before publishing | `npm install; npm run build; npx serve dist` | build exit code |
| `theme/` | The Shopify Liquid theme itself. Consumed by `preview/`, published through Shopify | — | `theme/README.md` |
| `scripts/`, `ops/` | Migration, catalog conversion, and operations tooling | — | — |

Node 24 and npm 11 are what these were last built and tested against.

## Where the records live

`SPEC.md` holds the requirements, `DESIGN.md` the visual language, `MAP.md` the architecture and file
navigation, `TASK.md` the active queue, and `LOG.md` the append-only work log. `CLIENT.md`,
`STORE-REQUIREMENTS.md` and `SOURCES.md` hold the client-facing requirements and the evidence they came
from. `AGENTS.md` is the contract every agent reads before changing anything here.
