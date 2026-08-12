# Ecwid complete API capture adapter v2

Date: 2026-08-10

## Result

Added a successor Ecwid adapter that captures the frozen v1 core resources plus product types, customer groups, customer extra-field definitions, hidden abandoned carts, staff, discount coupons, and promotions in one atomic run.

The implementation uses the resource-specific response envelopes and stable IDs documented by Ecwid, declares required read scopes, retains environment-only Bearer-token handling, removes secret-bearing URLs/keys, and preserves coupon codes as business evidence.

## Verification

- TDD red: 3 tests failed because `capture_ecwid_api_v2.py` did not exist.
- Focused green: `py -m unittest scripts.test_capture_ecwid_api_v2` passed 3 tests against a real loopback HTTP server.
- The test exercises all 12 core/adjunct resources, confirms `showHidden=true`, verifies the Authorization header reaches the server but neither token nor token-bearing URL reaches disk, preserves a coupon code, validates scope declarations, and proves duplicate `cartId` values fail closed without a final directory.

## Current boundary

No live Ecwid capture was performed. The available browser session is signed out and no approved secret-bearing process supplied an API token. Separate product binaries/downloadable files and other feature-dependent adjunct endpoints remain explicitly outside this v2 claim.
