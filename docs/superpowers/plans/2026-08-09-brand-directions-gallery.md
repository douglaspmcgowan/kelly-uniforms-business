# Brand Directions Gallery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a client-safe Vercel gallery containing the three existing MT Uniforms brand directions and a current, sourced project-status snapshot.

**Architecture:** A dependency-free static site under `brand-gallery/` owns the presentation layer. Versioned copies of the approved concept boards sit under `assets/brand-directions/`; Node's built-in test runner starts a local HTTP server and verifies the public boundary, content, and assets before deployment.

**Tech Stack:** Semantic HTML, modern CSS, small vanilla JavaScript module, Node.js built-in test runner, Vercel static hosting.

## Global Constraints

- Never publish credentials, customer data, internal filesystem paths, access mechanics, or recovery hashes.
- Label all three boards as exploratory concepts rather than final trademarks.
- Present Quartermaster as the recommendation with One Mission's documentary warmth.
- Show only status confirmed by `.agents/work/state.json`, `MAP.md`, and the brand-direction README.
- Preserve reduced-motion behavior, keyboard navigation, and responsive layouts.

---

### Task 1: Public gallery contract

**Files:**
- Create: `brand-gallery/tests/gallery.test.mjs`
- Create: `brand-gallery/package.json`

**Interfaces:**
- Consumes: HTTP files served from the gallery root.
- Produces: `npm test`, which rejects missing pages/assets, missing public status, broken recommendation labeling, and credential-like leakage.

- [ ] **Step 1: Write the failing integration test**

Create a Node test that serves the folder, fetches `/`, asserts status 200, checks for all three direction names, verifies the concept disclaimer and current status, rejects password/secret patterns, and fetches each board asset.

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test`
Expected: FAIL because `index.html` and the board assets do not exist.

- [ ] **Step 3: Add the minimal test command**

Create `package.json` with `"test": "node --test tests/gallery.test.mjs"` and no runtime dependencies.

### Task 2: Gallery implementation

**Files:**
- Create: `brand-gallery/index.html`
- Create: `brand-gallery/styles.css`
- Create: `brand-gallery/script.js`
- Create: `brand-gallery/assets/brand-directions/01-service-standard.png`
- Create: `brand-gallery/assets/brand-directions/02-quartermaster.png`
- Create: `brand-gallery/assets/brand-directions/03-one-mission.png`

**Interfaces:**
- Consumes: the three verified 1536x1024 concept boards and public status facts.
- Produces: a static selection-room experience at `/`.

- [ ] **Step 1: Copy the verified boards without modifying the source package**

Copy all three PNG files from the authoritative 2026-08-08 output folder into the gallery assets folder and compare SHA-256 values.

- [ ] **Step 2: Implement semantic gallery markup**

Build one opening status composition, one recommended-direction feature, two alternate direction studies, a comparison table, and a closing decision prompt. Put the required five-block design contract as the first child of `<body>`.

- [ ] **Step 3: Implement the visual system and responsive collapse**

Use a restrained graphite, paper, and signal-orange frame; large sans display type; asymmetrical editorial composition; full-width board imagery; one-line navigation; visible focus states; and reduced-motion fallbacks.

- [ ] **Step 4: Add minimal interaction**

Implement direction navigation and active section state with `IntersectionObserver`; leave all content visible when scripting is unavailable.

- [ ] **Step 5: Run tests to verify green**

Run: `npm test`
Expected: PASS with all HTTP, content-boundary, and asset checks green.

### Task 3: Browser verification and publication

**Files:**
- Modify: `DESIGN.md`
- Modify: `MAP.md`
- Modify: `.agents/work/state.json` through guarded Work Scope tools only.

**Interfaces:**
- Consumes: the tested static build.
- Produces: desktop/mobile screenshots, design review verdict, durable project documentation, and a production Vercel URL.

- [ ] **Step 1: Inspect desktop and mobile**

Serve locally, capture 1440x1000 and 390x844 screenshots, check keyboard focus, overflow, image loading, and reduced motion, then fix material gaps in one batch.

- [ ] **Step 2: Run mechanical checks**

Run the Impeccable detector on `brand-gallery/index.html`, `brand-gallery/styles.css`, and `brand-gallery/script.js`, then run `npm test` again.

- [ ] **Step 3: Complete independent finish review**

Send the request, design contract, artifact paths, screenshots, detector findings, and craft-floor reference to a fresh finish reviewer; apply its material fixes and obtain a verdict.

- [ ] **Step 4: Deploy and verify production**

Create/link the Vercel project `mt-uniforms-brand-directions`, deploy with `vercel deploy --prod --yes`, then fetch the production URL and verify the three boards and public copy.

- [ ] **Step 5: Reconcile durable state**

Record the gallery URL and current status in `MAP.md`, document the built surface in `DESIGN.md`, and reconcile Work Scope generated views and evidence.

## Self-review

- Coverage: brand comparison, recommendation, status, public-data boundary, accessibility, verification, deployment, and documentation are all assigned.
- Placeholder scan: no deferred code or unspecified implementation step remains.
- Interface consistency: the same gallery root, asset names, test command, and Vercel project name are used throughout.
