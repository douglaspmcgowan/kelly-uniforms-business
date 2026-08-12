# Ecwid core API capture adapter

Date: 2026-08-10

## Result

Added a value-safe, atomic Ecwid API capture adapter for the five authoritative core endpoint families: extended store profile, products, categories, customers, and orders.

The adapter:

- accepts the numeric store ID as a non-secret argument and reads the secret token only from `ECWID_SECRET_TOKEN`;
- sends the token only in the Bearer authorization header;
- never persists headers or credential values;
- strips token-bearing administrative/customer download URLs and secret query parameters from persisted JSON;
- captures unfiltered API objects without `responseFields`;
- requests hidden categories and product membership IDs;
- records deterministic JSON pages with SHA-256, bytes, entity, and record counts;
- advances pagination from observed records and fails on offset/count mismatch, total drift, missing IDs, duplicate IDs, empty nonterminal pages, or unreconciled totals;
- builds in a temporary sibling and atomically promotes only a complete capture.

## Verification

Three local integration tests used a real loopback HTTP server rather than mocked request assertions. They proved:

1. multi-page capture advances from offset 0 to offset 2, preserves three unique product records, sends the Bearer header, requests hidden category membership, hashes every artifact, and writes no supplied token or token-bearing URL;
2. a duplicate native ID fails closed and leaves no final capture directory;
3. the CLI exposes no token argument.

Command: `py -m unittest scripts.test_capture_ecwid_api`
Result: 3 tests passed.

## Live-source boundary

The connected Ecwid tab still shows the sign-in form, the OpenCart tab also resolves to its login form, the available email surface is signed out, and no second browser family is connected. No live token was available, so no client-private Ecwid records were acquired in this unit.

The adapter currently covers the core five endpoint families. Media/downloadable files, staff, customer groups/extra fields, carts, discounts/promotions, product adjunct resources, order adjunct resources, and corroborating CSV exports remain required before a live Ecwid capture can be called complete.
