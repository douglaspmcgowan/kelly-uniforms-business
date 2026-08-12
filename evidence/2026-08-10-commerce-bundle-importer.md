# Commerce bundle importer evidence — 2026-08-10

## Outcome

The recovery repository now has an executable, transactional path from a validated OpenCart/Ecwid bundle into the provenance-constrained SQLite landing model. Synthetic fixtures prove the behavior without inserting any invented MT Uniforms business records into REC-007.

## New database fidelity structures

- `import_runs`: immutable run ID, source/store/version, transform version, manifest hash, scope, counts, reconciliation and value-free failure status.
- `record_lineage`: target table/record plus every exact source artifact, native record ID, source locator, role and transform version.
- `catalog_product_categories`: faithful many-to-many category membership without inventing a primary category.
- `catalog_option_groups` plus modifier columns on `catalog_option_values`: type, required state, price/weight modifiers, inventory, subtract-stock and SKU.
- `commerce_order_adjustments`: exact shipping, tax, discount, coupon, fee and other order-total components.

The extension is additive and leaves the prior 35-table landing schema and REC-007 bytes untouched.

## Import behavior

- Runs the immutable bundle validator before any database write.
- Registers each exact source artifact in `source_manifest` with digest, byte count, native system/version, capture method, completeness and restricted sensitivity.
- Accepts only allowlisted target tables and real columns; common provenance is injected by the importer and cannot be overridden by payload data.
- Inserts target rows in dependency order and writes one `record_lineage` record per target row.
- Reconciles normalized source-record counts and SQLite foreign keys before commit.
- Treats an identical run as idempotent and rejects changed manifest bytes under the same run ID.
- On normalization failure, rolls back every target row while preserving the staged source-manifest rows and a value-free failed `import_runs` record.

## Test-first evidence

Six tests were written before either implementation module existed. The red run failed all six because `extend_import_schema.py` and `import_commerce_bundle.py` were absent. The implementation then passed:

1. additive schema creation with zero fabricated rows;
2. product/category membership and exact lineage;
3. identical-run idempotency;
4. changed bytes under one run ID fail closed;
5. foreign-key failure rolls back target rows while preserving source evidence;
6. unsupported target tables fail before partial insertion.

Work Scope evidence:

- Task: `commerce-bundle-importer-v2`
- Check: `commerce-bundle-importer-verify-v2`
- Receipt: `321e01c1-d421-44d7-8cfe-5f18a1286445`
- Result: pass, exit code 0
- Focused importer tests: 6 passed
- Full focused recovery suite after integration: 27 passed

The first task declaration was retired before evidence because its command assumed the `scripts` working directory while Work Scope correctly executes from the project root. The replacement check uses the real root-level invocation.

## Remaining boundary

The next truthful recovery generation needs real native OpenCart/Ecwid artifacts. The importer is ready; it cannot create private products, customers, orders, configuration or ownership evidence that has not been exported. REC-007 stays the current immutable checkpoint until those source bytes arrive or a tooling-only successor is intentionally packaged and isolated-restore verified.
