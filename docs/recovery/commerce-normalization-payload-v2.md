# Commerce normalization payload v2

Version: `mt-uniforms-normalized-payload/v2`

This successor preserves the v1 bundle envelope and target tables while repairing two source-fidelity failures found during the OpenCart native-export audit.

## Dependency-aware category insertion

`catalog_categories.parent_category_ref` is an immediate self-foreign key. Source IDs and normalized IDs do not guarantee that parents sort before children, so lexical insertion can reject a valid category tree.

The v2 importer topologically orders every category batch:

- root categories and categories whose parent already exists are ready first;
- parents present in the same batch are inserted before their children;
- a cycle fails before normalized writes commit;
- a missing external parent still fails the database foreign-key gate.

Other tables retain the declared dependency order and deterministic record-ID ordering within each table.

## Multi-artifact lineage

A normalized target row may declare a non-empty `lineage` array:

```json
{
  "table": "catalog_product_categories",
  "record_id": "opencart:product-category:7:2",
  "values": {
    "product_ref": "opencart:product:7",
    "category_ref": "opencart:category:2",
    "is_primary": 0,
    "sort_order": 0
  },
  "lineage": [
    {
      "artifact_path": "snapshots/products.ndjson",
      "source_record_id": "product:7",
      "source_locator": "table:product/pk:7",
      "relation_role": "product-source"
    },
    {
      "artifact_path": "snapshots/categories.ndjson",
      "source_record_id": "category:2",
      "source_locator": "table:category/pk:2",
      "relation_role": "category-source"
    }
  ]
}
```

Every entry must reference an artifact declared in the same immutable bundle and must provide a source record ID, source locator, and relation role. The first entry supplies the target table's required common provenance columns; every entry is written to `record_lineage` with transform version v2.

When `lineage` is absent, the importer generates the v1-compatible single `primary-source` entry from the enclosing snapshot row.

Reconciliation continues to count unique enclosing source records that produced at least one normalized row. Contributing joined rows do not inflate the normalized count for the enclosing entity.

## Operational boundary

The importer remains insert-only. Run each complete vendor capture against a new immutable recovery generation. Reusing the same run ID with identical manifest bytes is idempotent; changed bytes under the same run ID are rejected.

Raw SQL, webroot, configuration, Journal data, unsupported OpenCart tables/fields, and original API envelopes remain the fidelity authority. The normalized database is a rebuild model with exact lineage, not a substitute for immutable native exports.
