# Ecwid binary capture contract v1

This stage consumes a completed `mt-uniforms-ecwid-api-capture/v2` directory and preserves the catalog binaries that raw JSON references.

## Captured binaries

- Product and variation images, thumbnails, gallery images, media images, and video-cover images discovered from documented image-bearing JSON fields.
- Category images and thumbnails.
- Downloadable product files reconstructed as `GET /{storeId}/products/{productId}/files/{fileId}` from captured IDs.

Public catalog media is downloaded without an Authorization header. The Bearer token is sent only to the reconstructed Ecwid API product-file endpoint. Token-bearing `adminUrl` values are ignored, and neither token values nor credential-bearing query strings are written to the inventory.

## Command

```powershell
$env:ECWID_SECRET_TOKEN = '<injected by approved secret process>'
py tools\capture_ecwid_binaries.py `
  --capture 'C:\path\to\ecwid-v2-capture' `
  --destination 'C:\path\outside-git\ecwid-binaries'
Remove-Item Env:ECWID_SECRET_TOKEN
```

The destination must not exist. The tool builds through a temporary sibling directory and removes it on any failed download, byte-count mismatch, malformed source page, or missing stable product/file ID.

## Inventory invariants

- Downloads are deduplicated by safe public URL or product/file identity.
- Every stored binary records portable path, SHA-256, byte count, MIME type, capture status, authentication mode, and all JSON provenance locators.
- Product-file byte counts reconcile to the API-declared size when present.
- `binary-manifest.json` hashes `inventory/binaries.ndjson` and records catalog-media/product-file totals.

The binary capture remains restricted and outside Git. Order-option uploads, order download links, and feature-specific video binaries require separate documented endpoints and are not claimed here.

Primary references:

- https://docs.ecwid.com/api-reference/rest-api/products/search-products
- https://docs.ecwid.com/api-reference/rest-api/categories/search-categories
- https://docs.ecwid.com/api-reference/rest-api/products/product-files/download-product-file
