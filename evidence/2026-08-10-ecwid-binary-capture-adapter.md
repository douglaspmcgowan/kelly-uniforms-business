# Ecwid binary capture adapter

Date: 2026-08-10

## Result

Added an atomic binary-acquisition stage for Ecwid v2 captures. It deduplicates catalog image references while retaining every JSON locator, downloads public media without credentials, reconstructs authenticated product-file endpoints from IDs, reconciles declared file sizes, and writes portable SHA-256/MIME/byte inventories without credential-bearing URLs.

## Verification

- Initial TDD red: 3 tests failed because `capture_ecwid_binaries.py` did not exist.
- First green exercised exact public media downloads, duplicate-URL collapsing, two-locator provenance, authenticated reconstructed product-file download, token non-persistence, and failed-download cleanup.
- Adversarial red reproduced an unclosed `HTTPError` response as a `ResourceWarning`; the adapter now closes error responses before raising.
- Timestamp red reproduced a null default capture time; the adapter now records an explicit UTC timestamp.
- Final focused command: `py -m unittest scripts.test_capture_ecwid_binaries`.
- Final focused result: 4 tests passed against real loopback HTTP responses with no warnings.

## Current boundary

No live Ecwid binaries were captured because no authorized API token is provisioned. The adapter is ready to run immediately after the v2 JSON capture completes.
