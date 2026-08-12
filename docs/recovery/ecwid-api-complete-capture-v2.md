# Ecwid complete API capture contract v2

This successor preserves the v1 core capture and adds the documented adjunct resources needed to reconstruct store operations more faithfully.

## Captured resources

Core resources:

- extended store profile
- products
- categories including hidden categories and ordered product membership
- customers
- orders

Adjunct resources:

- product types and attribute definitions: `GET /classes`
- customer groups: `GET /customer_groups`
- customer extra-field definitions: `GET /store_extrafields/customers`
- abandoned carts including hidden carts: `GET /carts?showHidden=true`
- staff and ownership evidence: `GET /staff`
- discount coupons: `GET /discount_coupons`
- promotions: `GET /promotions`

Each paginated endpoint is requested with `limit=100`, advances by the returned item count, rejects changing totals, empty nonterminal pages, duplicate stable IDs, and envelope mismatches, and reconciles unique IDs to `total`. Resource-specific stable identifiers are used: `id`, `cartId`, or extra-field `key` as documented.

## Required scopes

The capture manifest declares the expected scope set: `read_store_profile`, `read_store_profile_extended`, `read_store_limits`, `read_catalog`, `read_customers`, `read_customers_extrafields`, `read_orders`, `read_staff`, `read_discount_coupons`, and `read_promotion`.

The token is accepted only through `ECWID_SECRET_TOKEN`. Authorization headers are never persisted. Secret-bearing URL fields and token-like query parameters are removed recursively before responses are written. Coupon `code` remains intact because it is business state, not an API credential.

## Command

```powershell
$env:ECWID_SECRET_TOKEN = '<injected by approved secret process>'
py tools\capture_ecwid_api_v2.py `
  --store-id '<digits only>' `
  --destination 'C:\path\outside-git\ecwid-capture'
Remove-Item Env:ECWID_SECRET_TOKEN
```

The destination must not exist. All endpoints are captured into a temporary sibling and promoted only after every resource reconciles; any failure removes the temporary capture.

## Current remaining API surface

Separate product binaries/downloadable files, product brands/reviews, order invoices/status dictionaries/extra-field definitions/subscriptions, and other feature-dependent resources are not claimed by v2. Preserve raw v2 JSON as the authority and add further successor endpoints only after confirming the store features and current official endpoint contracts.

Primary endpoint references:

- https://docs.ecwid.com/api-reference/rest-api/products/product-types-and-attributes/search-product-types
- https://docs.ecwid.com/api-reference/rest-api/customers/customer-groups/search-customer-groups
- https://docs.ecwid.com/api-reference/rest-api/customers/customer-extra-fields/search-customer-extra-fields
- https://docs.ecwid.com/api-reference/rest-api/orders/abandonned-carts/search-abandoned-carts
- https://docs.ecwid.com/api-reference/rest-api/staff-accounts/search-staff-accounts
- https://docs.ecwid.com/api-reference/rest-api/discounts/discount-coupons/search-discount-coupons
- https://docs.ecwid.com/api-reference/rest-api/discounts/promotions/search-promotions
