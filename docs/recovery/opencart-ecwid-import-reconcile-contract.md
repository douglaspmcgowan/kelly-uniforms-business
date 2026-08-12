# OpenCart and Ecwid import-and-reconcile contract

Version: `mt-uniforms-commerce-import/v1`

This contract is the boundary between immutable vendor exports and the normalized recovery database. A bundle is accepted only after its raw artifacts, source counts, normalized counts, skipped records, conflicts, foreign keys, and money checks reconcile. The executable authority is `scripts/validate_import_bundle.py`; the structural contract is `schemas/commerce-import-bundle-v1.schema.json`.

## Capture order and immutability

1. Capture OpenCart first: database SQL, webroot, external storage, configuration, versions, logs, and private media.
2. Restore the SQL into a disposable compatible database. Never parse arbitrary SQL text with regular expressions.
3. Produce read-only NDJSON table snapshots from that restored database. Preserve the SQL and snapshots together.
4. Capture Ecwid second: untouched UI CSV exports, raw paginated API envelopes, configuration evidence, and locally mirrored media/downloadable files.
5. Put each capture in a new immutable run directory. A changed byte requires a new `run_id`; never rewrite an accepted run.

Every artifact has a portable relative path, byte length, SHA-256 digest, source record count, entity, and completeness classification. Credential values, cookies, authorization headers, MFA material, payment-card PAN/CVV, and browser storage never enter a bundle. A raw database may contain vendor-managed authentication fields; those bytes remain restricted and immutable, while normalization snapshots must exclude them.

## Required lineage

Every normalized row retains:

- `source_system`: exactly `opencart` or `ecwid`;
- an immutable native `source_record_id` or compound source path;
- `extracted_at`: the capture timestamp, never the later import timestamp;
- `source_id`: the exact `source_manifest` artifact containing the record;
- a source locator: OpenCart table plus primary key, CSV row, or RFC 6901 JSON pointer;
- the transform version and import run ID.

Normalized IDs are namespaced (`opencart:<entity>:<id>` and `ecwid:<entity>:<id>`). SKU, email, name, and phone are never identity keys. Cross-system similarities create candidate `integration_mappings`; only explicit connector IDs or a recorded human ruling may confirm a merge.

## Mapping rules

### OpenCart

- Discover the table prefix and installed version/extensions from the restored schema; never assume `oc_`.
- Join categories and default-language descriptions; preserve `product_to_category` as many-to-many membership. Do not invent a primary category.
- Create one base variant from the product record. Core OpenCart option choices are modifiers, not Cartesian SKU combinations. Populate combination links only when an installed extension supplies an explicit variant/combination ID.
- Preserve option type, required status, sort order, price/weight prefixes and deltas, SKU, quantity, and subtract-stock behavior.
- Preserve product and gallery media as exact binaries with hashes.
- Build order lines exclusively from historical order snapshots. Current catalog names, SKUs, prices, addresses, and options must never overwrite order history.
- Map `order_total` components into order adjustments so subtotal, shipping, tax, coupon/discount, fee, and total can be reconciled.
- Exclude password, salt, token, code, IP, session, cart, and wishlist fields from normalized snapshots and reports.

### Ecwid

- Preserve each native API envelope with `total`, `count`, `offset`, `limit`, and `items`. Pages must be contiguous, non-overlapping, total-stable, and collectively complete.
- Preserve all category memberships; set a primary category only from `defaultCategoryId`.
- Map actual combination IDs as variants and their selected options as explicit links. Products without combinations receive one deterministic base variant.
- Treat UI CSVs as supplemental and header-driven because selected export columns vary. Normalization requires stable product/category/order/customer identifiers; absent identifiers produce a documented skip, never a guessed match.
- Preserve order display ID and internal ID in lineage. Create payment rows only when a real transaction/provider reference exists; paid status alone is not a payment record.
- Absence from a partial export never means deletion. Deletion requires an explicit tombstone/webhook or a complete same-scope snapshot comparison.

## Schema additions required before populated imports

REC-007's 35 commerce tables remain the landing model. A populated generation must add:

- `import_runs` for source scope, transform version, counts, status, and reconciliation;
- `record_lineage` for joined and derived rows with every contributing source locator;
- `catalog_product_categories` for many-to-many category membership;
- `catalog_option_groups` and modifier columns on option values;
- `commerce_order_adjustments` for exact order-total reconstruction.

Unsupported source fields stay in immutable raw artifacts and appear in the reconciliation report. They are never silently discarded or mapped by guesswork.

## Reconciliation and failure behavior

- Artifact paths must remain relative and traversal-free; recorded sizes and SHA-256 hashes must match exact bytes.
- Required source tables/columns, identifiers, versions, prefixes, CSV dialects, and API page envelopes must be recorded and validated.
- For every declared entity: `source_count = normalized_count + skipped_count`. Every skipped row has one source locator and reason.
- Monetary transforms use decimal parsing and integer minor units. Binary floating point is forbidden. Source totals and normalized totals may differ only by the recorded currency rounding quantum.
- SQLite integrity and foreign-key checks must be clean; unresolved mapping conflicts must be zero before acceptance.
- The same run is idempotent. Reusing a run ID with different bytes is fatal.
- Any failed validation or reconciliation rolls back normalized writes. Raw artifacts and failure evidence remain immutable in the new generation.
- Completion requires a package-only isolated restore followed by this validator, package checksums, SQLite integrity, foreign keys, per-table lineage coverage, and representative catalog/order reconstruction.

Authenticated OpenCart/Ecwid exports and hosting files are prerequisites for population. This contract makes their later ingestion deterministic; it does not claim that inaccessible private rows have already been recovered.
