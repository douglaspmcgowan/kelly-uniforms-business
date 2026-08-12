# Public cart host/session split

## Outcome

The reported OpenCart cart-link failure is reproduced and the www/non-www session-split hypothesis is confirmed.

On 2026-08-12, a disposable unauthenticated session submitted one option-complete add-to-cart request for public product ID 814 on `www.mtuniforms.com`. The server returned HTTP 200 and a success response, but the success markup generated its cart link on the bare `mtuniforms.com` host.

The same client session then read the cart on both hosts:

| Cart host | HTTP status | Added product present |
| --- | ---: | --- |
| `www.mtuniforms.com` | 200 | Yes |
| `mtuniforms.com` | 200 | No |

The www request received an `OCSESSID` scoped to `www.mtuniforms.com`. Visiting the bare host created a separate `OCSESSID` scoped to `mtuniforms.com`. No cookie values were recorded. This proves that a customer can add successfully on www and then follow the generated bare-host cart link into a different empty session.

## Reproduction

- Script: `scripts/Test-PublicCartHostSessionSplit.ps1`
- Sanitized machine result: `evidence/2026-08-12-public-cart-host-session-split.json`
- Public product: Elbeco Tek2 Cargo Pocket Trousers, product ID 814
- Valid option value IDs used: 4824, 4839, 4854
- Customer, account, inventory, payment, and order records were not created or changed. The disposable cart session expired with the process.

## Root cause and repair boundary

Both hosts serve the storefront without a canonical redirect, while the storefront generates bare-host links and OpenCart session cookies remain host-scoped. The immediate repair is to choose one canonical host and issue a permanent redirect from the other host before PHP/OpenCart handles the request. The OpenCart `config.php`/`admin/config.php` HTTP and HTTPS constants, Journal base/canonical configuration, and TLS coverage must agree with that host.

The existing recommendation remains to redirect `www` to the current bare-host canonical, contingent on confirming the TLS certificate covers `www.mtuniforms.com` and obtaining hosting/nginx access. The temporary ordering notice remains appropriate until the redirect and full cart/checkout regression pass are complete.

## Safety

The capture contains public identifiers, hostnames, HTTP outcomes, cookie names/domains, and boolean assertions only. It excludes cookie values, credentials, customer data, and payment data.
