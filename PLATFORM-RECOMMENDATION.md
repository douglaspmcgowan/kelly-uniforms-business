# M&T Uniforms — platform decision brief

**Status:** current decision brief. Recheck vendor pricing and plan limits during
the pilot; they change too often to be a durable recommendation.

## Recommendation

Do **not** change platforms to fix the broken cart. First restore the existing
OpenCart storefront, preserve the business data, and learn how the business
actually takes agency orders today. Then run a small real-product pilot.

For a normal modern retail site, **Shopify is the leading default**: it is
managed, has a mature app/API ecosystem, and now has first-party agent-facing
commerce interfaces. Keep Clover at the counter unless the pilot proves a clean
inventory and payment workflow requires replacing it.

Only choose a uniform-specific platform or a custom build if M&T Uniforms
actually needs to automate per-officer allowances, controlled agency ordering,
or other workflows that staff currently handle outside the site.

## What the business appears to do today

### The public website does

- Publish a large uniform catalog organized by customer type and product type.
- Collect normal product choices such as shoe size and width; public cart
  validation confirms required options exist.
- Offer a standard OpenCart cart, customer registration/login, wishlist, and
  order-history surface.

### The business appears to do outside the website

- Take in-store payments through Clover.
- Handle at least some agency orders through staff and invoices. The client said
  they want customers to pay online rather than have orders "come as an invoice."
- Likely manage custom decoration, contract pricing, restricted-product checks,
  and department relationships through staff, phone, email, and back-office
  records. Those workflows are not proven from public evidence.

### Not established

There is no public evidence that the present store has per-officer allowances,
authorization codes, protected agency portals, PO checkout, net terms,
approvals, or department-specific price lists. An authenticated OpenCart export
and a short conversation with the owners are needed to rule out private
extensions or manual practices.

## What needs a platform change, and what does not

| Goal | Needs a new platform? | Practical answer |
|---|---:|---|
| Fix the cart | No | Force one canonical domain (`www` → non-`www`) in hosting/OpenCart configuration. |
| Keep selling at the counter | No | Keep Clover. |
| Build a cleaner online catalog and take ordinary card orders | Probably | Shopify is the low-operations default; a repaired OpenCart can also buy time. |
| Keep Clover and sell online | Not automatically | Use a proven connector or a defined manual reconciliation process. Test it with real stock and returns. |
| Track one annual balance per officer and deduct it over multiple orders | Yes, if they want it automated | Use a vertical platform/add-on or custom service only after proving this is a real client workflow. |
| Require an agency code before an officer can buy | Yes, if they want it automated | Use agency accounts/roles first; add codes only when they are actually part of the client’s process. |

## Clover, plainly

Clover is the existing **point-of-sale system**: the counter hardware/software
that takes payments and tracks sales, items, staff activity, and reports. It can
support structured products and variants ("matrix" items) for counter sales.

That does not mean M&T Uniforms must move away from Clover. The open question is
which system owns the catalog and inventory:

- **Clover as master** is reasonable for a small, simple catalog.
- **The website as master** is safer for a large apparel catalog with photos,
  descriptions, custom embroidery input, and complex variants.
- **Two systems** can work only if one real product survives the full loop:
  website order → Clover stock → pickup/shipment → return/refund → correct stock
  and order history in both places.

Do not buy a connector or replace Clover before that test.

## The only questions to answer before selecting software

1. Do any departments give each officer a personal yearly dollar or item
   allotment that must be tracked over multiple orders?
2. Do officers need agency-issued authorization codes, or will normal agency
   accounts and staff approval work?
3. How are agency orders handled today: email, phone, counter sale, invoice,
   purchase order, or an undiscovered private OpenCart extension?
4. Does the business need live inventory synchronization between online orders
   and Clover, or is a controlled manual process acceptable during the first
   phase?
5. Who owns the domain, hosting, OpenCart data, Clover merchant agreement, and
   any current payment account?

## Pilot before purchase

Use a trial store and one real Clover test account/product set. Do not sign a
contract until it passes all five cases:

1. A normal retail order with a size/color product.
2. A personalized garment with a name or badge number attached to the exact
   line item and visible to production staff.
3. A department order using the way M&T Uniforms actually bills today.
4. A stock adjustment and return/refund across website and Clover.
5. A staff member adding a product, changing a price, and finding the order
   without developer help.

If the owners confirm individual allowances or authorization codes are truly
required, add a sixth test: twelve officers making partial purchases against
twelve distinct balances. Until then, do not make that scenario a platform
requirement.

## Evidence and useful references

- Current public-site architecture and cart diagnosis:
  [`evidence/2026-07-31-site-architecture-scope.md`](evidence/2026-07-31-site-architecture-scope.md)
- Current capability/recovery inventory:
  [`STORE-REQUIREMENTS.md`](STORE-REQUIREMENTS.md)
- OpenCart cart issue: <https://github.com/opencart/opencart/issues/2992>
- Clover item/inventory APIs: <https://docs.clover.com/dev/docs/working-with-inventory>
- Shopify agentic commerce: <https://shopify.dev/docs/agents>
- Shopify Storefront MCP: <https://shopify.dev/docs/apps/build/storefront-mcp/index>

## Copy/paste prompt for an independent review

> I am rebuilding a small-to-mid-sized ecommerce business. Compare Shopify,
> WooCommerce, OpenCart, Medusa, Saleor, and any better option for a modern
> store that an AI coding agent can extend safely. Separate the recommendation
> for ordinary retail from one that must automate per-employee allowances,
> authorization codes, purchase orders, net terms, approvals, custom
> personalization, and a physical Clover POS. Explain operational burden, data
> export, APIs, accessibility, current pricing, and a 90-day pilot plan. Cite
> current primary sources and clearly label assumptions.
