# Binary-ready recovery package contract v1

REC-012 is the current offline recovery authority. It preserves the verified storefront, public media, database schema, provenance, raw-import staging, and importer-v2 chain while packaging:

- OpenCart native database/webroot/storage/config acquisition
- Ecwid core and adjunct JSON acquisition
- Ecwid catalog-media and downloadable-product-file acquisition

## Package-local commands

```powershell
py tools\package_binary_ready_generation.py verify <recovery-root>
py tools\capture_opencart_native_export.py <source-export> <capture-destination>
py tools\capture_ecwid_api_v2.py --store-id <digits> --destination <json-capture>
py tools\capture_ecwid_binaries.py --capture <json-capture> --destination <binary-capture>
py tools\package_binary_ready_generation.py stage-import <recovery-root> <export-manifest>
```

Both Ecwid stages receive their token only through `ECWID_SECRET_TOKEN`. Public media requests carry no Authorization header; authenticated product-file requests use reconstructed API paths. All private captures remain restricted and outside Git.

Readiness `opencart-and-ecwid-json-binary-tools-packaged-awaiting-authenticated-exports` proves the toolchain and package are self-contained. It does not claim private source records or binaries have been obtained; fresh private commerce/import rows remain empty until authenticated acquisition succeeds.
