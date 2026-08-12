STATUS: superseded — implemented by `storefront/`; the shipped behavior and visual contract are owned by `storefront/DESIGN.md`, with durable architecture and data boundaries in `MAP.md`.

# M&T Uniforms replacement storefront prototype

This document defines the product behavior and proof bar for the first client-first storefront slice. It is the technology-agnostic WHAT; implementation choices belong in the build plan and surface documentation.

## Product

### Root problem

Customers need a dependable way to identify the right uniform or equipment item and reach M.T. Uniforms while the existing online ordering path is unreliable. The central failure is uncertainty: product discovery, fit and customization choices, and the human fallback are not presented as one understandable path.

### Users and context

Public buyers include first responders, law-enforcement and security staff, postal and corrections staff, organizations, and local customers. They may be on a phone at a station or in the field, or on a desktop while arranging an order. M.T. Uniforms staff receive the resulting request and complete the approved business process. Project stakeholders evaluate fidelity to sourced public evidence, clarity, and accessibility.

### Jobs to be done (ranked)

1. Find a relevant item by role, category, or plain-language search.
2. Understand the item's evidence-backed media, fit guidance, and required choices.
3. Preserve the selected item and choices while preparing a request.
4. Reach a human by email or phone when the visitor is ready to order.
5. Understand which parts of the flow are demonstrative and which are a future commerce decision.

### Success criteria

- **SC-001:** During the launch validation session, in a moderated task with the seven fixture products available, at least 4 of 5 representative visitors reach a product detail view from a role, category, or search entry without using browser backtracking.
- **SC-002:** During the launch validation session, at least 4 of 5 visitors identify every required choice shown for the selected fixture before adding it to the request.
- **SC-003:** During the launch validation session, at least 4 of 5 visitors can produce a request summary containing the intended fixture, selected options, quantity, and personalization (when supplied) and can identify the email/phone fallback within two minutes.
- **SC-004:** Keyboard and narrow-screen checks produce zero blocked primary paths for discovery, product choice, request review, and contact fallback; evidence is recorded by manual inspection and automated assertions where available.

### Non-goals

- Real payment, paid checkout, tax calculation, shipping calculation, order submission, inventory reservation, or customer account creation.
- Authenticated OpenCart, Ecwid, Clover, customer, order, private catalog, or private pricing integrations. Authenticated OpenCart/Ecwid private data is not present.
- Per-officer allowances, authorization codes, agency portals, private agency price lists, approval routing, or other unverified B2B workflows.
- A migration of the complete catalog, customers, order history, URLs, or media rights.
- A production identity decision, trademark clearance, final logo, or claim that the client approved a new visual identity.

### Constraints and assumptions

- **ASSUMED:** The seven public fixture products are the exact launch set: Spiewak Visguard Two Tone Hi-Vis Waterproof Safety Parka; Elbeco Tek2 Cargo Pocket Trousers; USPS Letter Carrier Performance Knit Shirt; W. Alboum Cushion Air Pershing Style Uniform Cap; Adjustable High Visibility Break Away Safety Vest; 5.11 Tactical Wingman Nylon Equipment Bag; and Embroidered Sergeant Chevrons.
- **ASSUMED:** The public JSON-LD/page snapshot in REC-015 is suitable evidence for names, categories, descriptions, and media references. It is not authoritative inventory, price, availability, or private commerce data.
- **ASSUMED:** The exact continuity copy is “New Website Coming! For all orders email orders@mtuniforms.com or call us directly at (814) 536-2390.” The email and phone are the request fallback for this slice.
- **ASSUMED:** Pickup and human contact are represented as request preferences or instructions; no live fulfillment or order confirmation is implied.
- **ASSUMED:** The storefront can be evaluated online at narrow, medium, and wide viewport sizes with keyboard, touch, and reduced-motion settings.

## Evidence and boundaries

REC-015 is the current public recovery authority: 528 reachable public pages, 1,542/1,542 exact public media binaries, and zero private normalized/import rows. Its public page and JSON-LD snapshot supply the seven fixture products and media. The current public evidence includes the exact continuity notice; the 2026-07-30 record of its absence is historical. Public evidence does not establish authenticated catalog, customer, order, inventory, payment, agency, or account-control data.

## Functional

### Prioritized user stories

#### P1 — Discover, understand, and request a product

As a public customer, I want to find a relevant fixture, understand its choices, and prepare a request, so that I can move toward an order without guessing or relying on a broken cart.

**Why this priority:** It is the smallest complete value path for continuity and modernization.

**Independent test:** Starting from the storefront entry, use a role/category route or a search term to open one of the seven fixtures, select its required choices, add optional personalization, review the request, and reach the contact fallback.

#### P2 — Use the storefront across devices and access needs

As a customer using a phone, keyboard, zoom, or assistive technology, I want the same discovery and request path to remain understandable, so that device or access method does not block ordering help.

**Why this priority:** Public buyers may be mobile and the request path must be usable before any commerce decision.

**Independent test:** Repeat the P1 path at narrow, medium, and wide viewports with keyboard-only navigation, text resizing/zoom, visible focus, and reduced-motion settings.

### Functional requirements

- **FR-001 (ubiquitous):** The system MUST provide discoverable entry paths for customer role, product category, and free-text search.
- **FR-002 (event-driven):** WHEN a visitor selects a role, category, or search result, the system MUST show matching fixture products with name, category, media, and a public-evidence/source label that does not imply live inventory.
- **FR-003 (state-driven):** WHILE a visitor views a product, the system MUST show the product's fit guidance and every required choice supported by its public evidence before the item can be added to a request.
- **FR-004 (event-driven):** WHEN a visitor adds a configured item, the system MUST preserve the item identity, chosen options, personalization text, and quantity in the request summary.
- **FR-005 (event-driven):** WHEN a visitor reviews a request, the system MUST expose pickup/contact preferences and the exact email-and-phone fallback copy without implying that a paid order was submitted.
- **FR-006 (unwanted-behavior):** IF a required choice is missing or invalid, THEN the system MUST prevent that item from entering the request and identify the missing correction in text.
- **FR-007 (unwanted-behavior):** IF a role, category, or search query has no matching fixture, THEN the system MUST show an explicit no-results state with a way to broaden discovery or contact M.T. Uniforms.
- **FR-008 (ubiquitous):** The system MUST make the primary discovery, product-choice, request-review, and contact controls operable by keyboard with visible focus and accessible names.
- **FR-009 (state-driven):** WHILE the viewport or text scale changes, the system MUST preserve readable hierarchy, content order, touch-sized controls, and access to the P1 path without horizontal scrolling.
- **FR-010 (unwanted-behavior):** IF a fixture image cannot be displayed, THEN the system MUST retain an informative text alternative and the product's request path.
- **FR-011 (ubiquitous):** The system MUST label the request flow as demonstrative and MUST avoid presenting payment, inventory, account, agency, or order-confirmation claims as completed actions.

### Key entities

- **Fixture product:** A public-evidence-backed product record used for demonstration; it has a name, role/category labels, media references, supported choices, and provenance.
- **Product choice:** A required or optional fit/customization value attached to one fixture line.
- **Request line:** A selected fixture plus quantity, choices, and optional personalization.
- **Request summary:** A collection of request lines and contact/pickup preferences prepared for human follow-up.
- **Continuity notice:** The exact temporary ordering message with actionable email and phone destinations.

## Acceptance

```yaml
acceptance:
  - id: AC-001
    story: P1
    fr: [FR-001, FR-002]
    verification: Demonstration
    given: "the storefront entry and the role labels Police, Fire/EMS, Postal, and Security are available"
    when: "a visitor selects Postal"
    then: "the result view contains at least one of the seven public fixture products and preserves a path to its detail view"
    grader:
      type: code
      weight: 1.0
      config:
        assertions:
          - "selected_role == 'Postal'"
          - "result_products.length >= 1"
          - "result_products.every(product => product.provenance.source == 'REC-015 public page/JSON-LD snapshot')"

  - id: AC-002
    story: P1
    fr: [FR-001, FR-002]
    verification: Test
    given: "the seven public fixture products are available"
    when: "a visitor searches for 'rain'"
    then: "the results contain the Spiewak Visguard Two Tone Hi-Vis Waterproof Safety Parka and show its category and media"
    grader:
      type: code
      weight: 1.0
      config:
        assertions:
          - "search_results.some(product => product.name == 'Spiewak Visguard Two Tone Hi-Vis Waterproof Safety Parka')"
          - "search_results.find(product => product.name == 'Spiewak Visguard Two Tone Hi-Vis Waterproof Safety Parka').media.length >= 1"

  - id: AC-003
    story: P1
    fr: [FR-002]
    verification: Inspection
    given: "the public REC-015 page/JSON-LD snapshot is the fixture authority"
    when: "the catalog fixture set is inspected"
    then: "exactly seven products are present and all seven names match the launch set"
    grader:
      type: code
      weight: 1.0
      config:
        assertions:
          - "fixture_products.length == 7"
          - "fixture_products.map(product => product.name).sort() == ['5.11 Tactical Wingman Nylon Equipment Bag', 'Adjustable High Visibility Break Away Safety Vest', 'Elbeco Tek2 Cargo Pocket Trousers', 'Embroidered Sergeant Chevrons', 'Spiewak Visguard Two Tone Hi-Vis Waterproof Safety Parka', 'USPS Letter Carrier Performance Knit Shirt', 'W. Alboum Cushion Air Pershing Style Uniform Cap'].sort()"
          - "fixture_products.every(product => product.provenance.source == 'REC-015 public page/JSON-LD snapshot')"

  - id: AC-004
    story: P1
    fr: [FR-003]
    verification: Demonstration
    given: "a visitor opens Elbeco Tek2 Cargo Pocket Trousers"
    when: "the visitor inspects fit and options"
    then: "the product view exposes supported fit guidance and labels required choices before the request action"
    grader:
      type: code
      weight: 1.0
      config:
        assertions:
          - "product_detail.name == 'Elbeco Tek2 Cargo Pocket Trousers'"
          - "product_detail.fit_help != null"
          - "product_detail.required_choices.length >= 1"
          - "request_action.disabled == true until required_choices.valid == true"

  - id: AC-005
    story: P1
    fr: [FR-004]
    verification: Test
    given: "the visitor selected USPS Letter Carrier Performance Knit Shirt, quantity 2, and personalization 'J. Rivera'"
    when: "the visitor adds it to the request and opens the request summary"
    then: "one request line retains that exact product, quantity, selected options, and personalization"
    grader:
      type: code
      weight: 1.0
      config:
        assertions:
          - "request.lines.length == 1"
          - "request.lines[0].product_name == 'USPS Letter Carrier Performance Knit Shirt'"
          - "request.lines[0].quantity == 2"
          - "request.lines[0].personalization == 'J. Rivera'"
          - "request.lines[0].options == selected_options"

  - id: AC-006
    story: P1
    fr: [FR-005]
    verification: Demonstration
    given: "a request summary contains one configured fixture line"
    when: "the visitor opens the contact/pickup fallback"
    then: "the exact continuity notice is visible, pickup/contact preferences remain available, and email and phone controls target orders@mtuniforms.com and (814) 536-2390"
    grader:
      type: code
      weight: 1.0
      config:
        assertions:
          - "continuity_notice == 'New Website Coming! For all orders email orders@mtuniforms.com or call us directly at (814) 536-2390.'"
          - "contact_fallback.email == 'orders@mtuniforms.com'"
          - "contact_fallback.phone == '(814) 536-2390'"
          - "request_fallback.pickup_option != null"

  - id: AC-007
    story: P1
    fr: [FR-006]
    verification: Test
    given: "a visitor opens Adjustable High Visibility Break Away Safety Vest and leaves a required choice empty"
    when: "the visitor activates the request action"
    then: "no request line is created and the missing choice is identified in text adjacent to the control"
    grader:
      type: code
      weight: 1.0
      config:
        assertions:
          - "request.lines.length == 0"
          - "validation_messages.length >= 1"
          - "validation_messages.some(message => message.field == missing_choice.field)"

  - id: AC-008
    story: P1
    fr: [FR-007]
    verification: Demonstration
    given: "no fixture matches the search query 'ceremonial scuba helmet'"
    when: "the visitor submits that query"
    then: "the page states that no products match and offers a broaden-search action plus the M.T. Uniforms contact fallback"
    grader:
      type: code
      weight: 1.0
      config:
        assertions:
          - "results.length == 0"
          - "empty_state.has_broaden_search == true"
          - "empty_state.has_contact_fallback == true"

  - id: AC-009
    story: P1
    fr: [FR-005, FR-011]
    verification: Inspection
    given: "a visitor reaches the final request step"
    when: "the visitor looks for a payment or order-confirmation action"
    then: "the flow identifies itself as demonstrative and provides no completed-payment, inventory, account, or order-confirmation claim"
    grader:
      type: code
      weight: 1.0
      config:
        assertions:
          - "request_flow.is_demonstrative == true"
          - "request_flow.payment_action == null"
          - "request_flow.order_confirmation == null"
          - "request_flow.inventory_claim == null"

  - id: AC-010
    story: P2
    fr: [FR-008]
    verification: Test
    given: "a visitor uses only a keyboard"
    when: "the visitor tabs from discovery through product choices, request review, and contact fallback"
    then: "every primary control receives visible focus, has an accessible name, and can be activated without a pointer"
    grader:
      type: code
      weight: 1.0
      config:
        assertions:
          - "keyboard_trace.blocked_controls.length == 0"
          - "keyboard_trace.unlabelled_controls.length == 0"
          - "keyboard_trace.focus_visible == true"

  - id: AC-011
    story: P2
    fr: [FR-009]
    verification: Analysis
    measure:
      metric: "blocked_primary_paths"
      threshold: 0
      op: "=="
      condition: "narrow, medium, and wide viewport checks with text resizing or zoom"
    grader:
      type: code
      weight: 1.0
      config:
        assertions:
          - "responsive_checks.blocked_primary_paths == 0"
          - "responsive_checks.horizontal_scroll == false"

  - id: AC-012
    story: P2
    fr: [FR-010]
    verification: Test
    given: "one fixture image is unavailable"
    when: "the product card or detail view renders"
    then: "the product name and informative text alternative remain available and the request path remains usable"
    grader:
      type: code
      weight: 1.0
      config:
        assertions:
          - "media_failure.product_name_visible == true"
          - "media_failure.informative_alt_text == true"
          - "media_failure.request_path_available == true"

  - id: AC-013
    story: P2
    fr: [FR-008, FR-009]
    verification: Inspection
    given: "the storefront is viewed with reduced motion enabled"
    when: "the visitor completes discovery and request review"
    then: "no essential content or state depends on motion, hover, color alone, or a disappearing transition"
    grader:
      type: prompt
      weight: 0.5
      config:
        rubric: "Pass only when a reviewer can complete the P1 path with reduced motion and every state is communicated through text, structure, or an independent visual cue."
```

### Traceability check

Every P1 functional requirement (FR-001 through FR-007 and FR-011) is covered by at least one acceptance criterion. P1 includes positive discovery, configured-request, and contact-fallback scenarios plus missing-choice, no-results, and no-payment negative paths. P2 requirements are covered by keyboard, responsive, media-failure, and reduced-motion criteria.

### Assumption register

The seven fixture names, REC-015 public JSON-LD/page snapshot as source, and exact continuity notice are explicit assumptions pending any client or source correction. Authenticated OpenCart/Ecwid private data remains unavailable and outside this prototype's evidence boundary.
