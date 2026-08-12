# Capture-ready recovery package contract v1

REC-009 is an immutable successor to REC-008. It preserves the verified public-site recovery authority and adds package-local acquisition and normalization tools needed when authenticated exports become available.

## Included interfaces

- `tools/package_capture_ready_generation.py verify <root>` verifies package checksums, database integrity, generation lineage, required tools/contracts, and fresh-package emptiness.
- `tools/capture_ecwid_api.py <store-id> <destination>` captures the Ecwid core API surface. The secret token is accepted only through the `ECWID_SECRET_TOKEN` environment variable and is never written to the capture.
- `tools/package_capture_ready_generation.py stage-import <root> <export-manifest>` validates and atomically stages a commerce bundle under `raw/private-exports/<run-id>/`, imports it with importer v2, and refreshes package checksums after success or recorded failure.

## Recovery guarantees

1. Creation accepts only a verified, empty REC-008 source and builds through a temporary sibling directory before atomic promotion.
2. All packaged tools and contracts are registered in `source_manifest` with portable paths, SHA-256 digests, and byte counts.
3. Importer v2 topologically orders category trees, rejects category cycles, and records every declared contributing artifact in `record_lineage`.
4. A fresh REC-009 contains no invented private catalog, customer, order, payment, fulfillment, return, import-run, or lineage rows.
5. Raw authenticated evidence is retained byte-for-byte before normalization, including when normalization fails.

## Remaining acquisition boundary

REC-009 contains acquisition tooling, not authenticated business exports. The current browser sessions were signed out and no approved secret broker exposed an Ecwid API token to the capture process. OpenCart native capture still requires a database dump plus webroot and external storage backup. Ecwid adjunct resources and media beyond the core profile/products/categories/customers/orders surface remain follow-on acquisition work described in the Ecwid runbook.

Never commit authenticated exports, customer records, order records, configuration secrets, or secret-bearing environment files to Git.
