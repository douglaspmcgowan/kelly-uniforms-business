# Commerce normalization payload v1

This payload is the deterministic bridge between restored vendor-native records and the provenance-constrained recovery database. It extends each `table-snapshot` NDJSON row accepted by `mt-uniforms-commerce-import/v1`; it does not replace or rewrite the immutable raw record.

```json
{
  "source_record_id": "product:7",
  "source_locator": "table:mt_product/pk:7",
  "entity": "products",
  "record": {"product_id": 7, "sku": "SOURCE-SKU"},
  "normalized_rows": [
    {
      "table": "catalog_products",
      "record_id": "opencart:product:7",
      "values": {
        "category_ref": null,
        "name": "Source product name",
        "brand_name": null,
        "supplier_name": null,
        "description": "Source description",
        "lifecycle_status": "active"
      }
    }
  ]
}
```

Rules:

- `source_record_id` is the immutable native ID or compound child path. It is never a SKU, email, name, or phone number.
- `source_locator` points to the exact restored table/primary key, CSV row, or JSON pointer that supplied the record.
- `record` preserves the non-sensitive extraction snapshot used by the transform. Credential, session, IP, cart, wishlist and payment-card fields are excluded.
- `normalized_rows` is an ordered list of explicit target rows. Target tables and columns are allowlisted from the recovery schema; arbitrary table or column names fail closed.
- `record_id` is deterministically namespaced by source, entity and native ID.
- Common provenance columns are injected by the importer from the bundle and exact source artifact. Payload authors cannot override them.
- Each target row receives a `record_lineage` entry with the source artifact, source record ID, source locator and transform version.
- Rows are inserted in dependency order inside one transaction. Any unsupported table/column, duplicate, count drift, constraint failure or foreign-key error rolls back every normalized row.
- Source artifacts and the `import_runs` failure state survive a failed normalization transaction. Error text is value-free.
- Re-running an identical accepted `run_id` is idempotent. Reusing that ID with different manifest bytes is fatal.

The first implemented transform boundary is intentionally generic. Source-specific OpenCart and Ecwid extraction adapters must produce these rows from the immutable artifacts according to `opencart-ecwid-import-reconcile-contract.md`; they must never guess relationships, variants, payments, deletions, or cross-system matches.
