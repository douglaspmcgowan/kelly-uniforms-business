# Prior Codex session — reconciliation and discrepancies

Source: `CDX-001`, `MSG-004`. Reviewed 2026-07-31.

Session file:
`C:\Users\dougl\.codex\sessions\2026\07\30\rollout-2026-07-30T23-28-20-019fb637-3846-7523-9d63-74cbb75b3841.jsonl`

Two client screenshots supplied to that session are preserved at its attachment
path outside this repository.

---

## 1. SECURITY — act on this first

**The OpenCart administrator password was pasted in cleartext into that session
and is stored unencrypted on this disk.** It is also in the originating chat
history. The username appears alongside it.

Required actions, in order:

1. Change the OpenCart administrator password at
   <https://www.mtuniforms.com/admin/>.
2. Store the new value only in Bitwarden.
3. Treat the old value as compromised. Do not reuse it anywhere.

`secret-manifest.json` records `MT_UNIFORMS_WEBSITE_ADMIN_PASSWORD` with status
`rotation-required` for this reason. The Ecwid credential was withheld by
Douglas in the first message and re-sent only in part; treat it as
possibly-exposed and rotate it too.

Deleting the session file does not undo the exposure — rotation is the only
remediation.

---

## 2. The banner discrepancy — the client has been told something that is not true

In the message thread, Douglas told the client: *"I added the announcement you
wanted as a banner."*

**The notice is not visible on the live public site.** The 2026-07-31
unauthenticated check found no notice on the home, category, contact, cart, or
checkout routes.

The two facts reconcile: the public page source registers Journal Header Notice
module **56** (`headerNotice: [{m:56, c:"266c89c7"}]`), but no
`module-header_notice-56` markup renders. A Header Notice module was almost
certainly created during that Codex session and is disabled, unassigned to a
layout, or filtered out by its status conditions.

Most likely cause, given section 4 below: the module was created and verified
against one host while the public site was viewed on the other, or it was left
in **Admin Only** status.

**This is the single most urgent open item.** The client believes their
customers are seeing an ordering notice during a period when their cart is
broken. They are not.

Resolution: authenticate, open module 56, record its status and layout
assignment, and either enable it or replace it per
`WEBSITE-UPDATE-RUNBOOK.md`.

---

## 3. New client facts established

From the screenshots (`MSG-004`), now folded into `CLIENT.md`:

| Fact | Client's words | Consequence |
|---|---|---|
| Clover is the POS | "We use clover. As our pos" | Explains the Ecwid account. Drives the whole platform decision. |
| They asked about OpenCart + Clover | "Would you recommend keeping open cart. Can it work with clover ?" | A direct question that needs a direct answer. |
| No design attachment | "Nothing I want to keep" | Full redesign freedom on `DEL-003`. |
| Previous owner pays for the platform | "The old platform is from the previous owner and I think he stops paying for it" | Continuity risk. Ownership of domain, DNS, hosting, and the Journal licence is now the top unknown. |
| They want online payment | "modernize it and allow customers to be able to pay online instead of it coming as an invoice" | Reframes `DEL-003` as a payments change, not a cosmetic refresh. |
| Two owners | Kelly Huntington and David; David "does a lot more of the ordering and might have a better idea about the website" | David is the better technical/operational contact. |

---

## 4. Why the Ecwid account exists — resolved

Previously recorded as an open question. The answer follows directly from
`MSG-004`.

Ecwid ("Ecwid by Lightspeed") is the **officially Clover-integrated online
store**. The Clover app is first-party, built by Lightspeed, and installs from
the Clover Web Dashboard or a Clover Station. It syncs Clover products,
inventory, and online orders.

So: somebody — the previous owner, or the client after adopting Clover — signed
up for Ecwid because it is what Clover points merchants at for an online store.
It was never launched as the public storefront, and `mtuniforms.com` continued
to run OpenCart.

**Ecwid does not overlap with OpenCart in any live capacity.** They are two
independent commerce platforms; only OpenCart serves the public site. Ecwid
overlaps with the *future* platform decision, where it is a live candidate
precisely because of the Clover integration.

Remaining unknown: whether the Ecwid account holds a populated Clover-synced
catalog (which would be a migration asset) or is empty. One authenticated look
answers it.

---

## 5. Independent corroboration of the cart diagnosis

The Codex session independently reached the same www/non-www conclusion this
session reached from HTTP evidence. Two separate analyses converging raised
confidence before external confirmation arrived.

That confirmation has now landed from primary sources:

- **OpenCart issue #2992**, titled "www and non-www add to cart", documents the
  exact failure: add-to-cart fails with
  `No 'Access-Control-Allow-Origin' header is present on the requested resource`
  when a visitor arrives on the host variant that does not match the configured
  one. <https://github.com/opencart/opencart/issues/2992>
- **Journal's own support KB article 20**, "Icons not showing or Add to Cart
  button not working", states the cause is the store being reached from a URL
  format other than the one used at install, notes it is not Journal-specific,
  and recommends configuring a server redirect for the other variants.
  <https://support.journal-theme.com/knowledgebase.php?article=20>

The mechanism is worse than a split cart. Because the `www` page declares
`<base href="https://mtuniforms.com/">`, the add-to-cart XHR resolves to a
different origin and the **browser blocks it outright via CORS** before OpenCart
ever receives it. The host-only `OCSESSID` splits the cart as well, but the CORS
block is the primary failure.

**The fix is one nginx 301 from `www` to the non-www canonical host** — matching
the host the site already declares in its `<base>` and canonical tags. Low risk,
reversible with a config reload, and it consolidates SEO signals rather than
moving them. Prerequisite: confirm the TLS certificate covers
`www.mtuniforms.com` so the redirect is reachable over HTTPS.

This moves `DEL-002` from "unreproduced client report" to "diagnosed, with a
one-line remediation pending access."
