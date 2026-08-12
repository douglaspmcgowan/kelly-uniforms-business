# Complete-source recovery package contract v1

REC-011 is the current offline recovery authority. It preserves the verified public storefront, media, database schema, provenance, raw-import staging, and importer-v2 chain, and packages both source-acquisition paths:

- OpenCart native SQL dump, webroot, external storage, and configuration capture
- Ecwid core plus adjunct API capture for profile, catalog, customers, orders, product types, customer groups/extra fields, hidden carts, staff, coupons, and promotions

## Package-local entry points

```powershell
py tools\package_complete_source_generation.py verify <recovery-root>
py tools\capture_opencart_native_export.py <source-export> <capture-destination>
py tools\capture_ecwid_api_v2.py --store-id <digits> --destination <capture-destination>
py tools\package_complete_source_generation.py stage-import <recovery-root> <export-manifest>
```

The Ecwid token must be injected only through `ECWID_SECRET_TOKEN`. All source captures and imported private records remain restricted and outside Git.

## Meaning of readiness

`opencart-and-complete-ecwid-tools-packaged-awaiting-authenticated-exports` confirms the local recovery toolchain is self-contained and verified. It explicitly does not claim authenticated exports have been obtained. A fresh REC-011 therefore keeps all private commerce/import tables empty and carries `captured_private_exports: false`.

When access becomes available, capture raw evidence first, retain it byte-for-byte, transform it into the commerce bundle with explicit unsupported-field reporting, and create a new immutable generation after import.
