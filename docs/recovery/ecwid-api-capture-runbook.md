# Ecwid API capture runbook

Version: `mt-uniforms-ecwid-api-capture/v1`

This is the value-safe acquisition boundary for the Ecwid portion of the recovery. The current adapter captures the complete unfiltered store profile, products, categories, customers, and orders collections into a new immutable directory. It never accepts a token on the command line, never writes request headers, and removes token-bearing administrative download URLs from persisted JSON.

## Prerequisites

Create or use a private/custom Ecwid app for the store and grant these read scopes:

- `read_store_profile`
- `read_store_profile_extended`
- `read_store_limits`
- `read_catalog`
- `read_customers`
- `read_orders`

Keep the secret token in the approved one-secret-to-one-process broker. Ecwid requires a Bearer token in the `Authorization` header and the numeric store ID in the API path. A public token is insufficient for private recovery data.

Official references:

- [Authentication quickstart](https://docs.ecwid.com/get-started/make-your-first-api-request)
- [REST API overview and rate limits](https://docs.ecwid.com/api-reference)
- [Store profile](https://docs.ecwid.com/api-reference/rest-api/store-profile/get-store-profile)
- [Products](https://docs.ecwid.com/api-reference/rest-api/products/search-products)
- [Categories](https://docs.ecwid.com/api-reference/rest-api/categories/search-categories)
- [Customers](https://docs.ecwid.com/api-reference/rest-api/customers/search-customers)
- [Orders](https://docs.ecwid.com/api-reference/rest-api/orders/search-orders)

## Capture command

Inject the token into the process environment without echoing or logging it, then run:

```powershell
py scripts\capture_ecwid_api.py `
  --store-id <numeric-store-id> `
  --destination <new-private-capture-directory>
```

The adapter reads the token only from `ECWID_SECRET_TOKEN`. It refuses an existing destination, builds in a temporary sibling, validates every page, and atomically promotes the directory after all five endpoint families reconcile.

## Pagination and completeness gates

- Every paginated request explicitly sets `limit=100` and a numeric offset.
- The requested and returned offsets must match.
- `count` must equal the number of returned items.
- `total` must remain stable across pages.
- Every item must have a stable unique ID.
- Unique records must equal the final total.
- An empty page before the total, a repeated ID, or total drift fails the entire capture and leaves no final directory.
- Categories explicitly include hidden categories and product membership IDs.
- No `responseFields` filter is used, so Ecwid does not remove unspecified fields.

Each JSON artifact is registered with a portable path, record count, byte count, SHA-256 digest, and value-safe sensitivity label. `capture-manifest.json` records the source, store reference, timestamp, entity counts, and credential policy.

## Required follow-on capture

The current adapter covers the five authoritative core endpoint families. A complete live Ecwid run must also preserve, where enabled and permitted:

- product types/attributes, brands, reviews, size charts, downloadable product files, and product/category media;
- customer groups and customer extra-field definitions;
- hidden/abandoned carts;
- staff and ownership records;
- discount coupons and promotions;
- order invoices, statuses, extra-field definitions, subscriptions, and configuration-specific resources;
- corroborating admin CSV exports.

Those resources remain explicit follow-on work; the core adapter does not claim they have been captured. After the expanded raw acquisition is complete, transform it into the existing `mt-uniforms-commerce-import/v1` bundle, validate it, and use REC-008's packaged `stage-import` command.

## Current access status

The live Ecwid control panel still displays the sign-in form. No token or authenticated session was available during adapter verification, so only deterministic local API fixtures were exercised. A live capture requires the approved broker or an already-authenticated handoff.
