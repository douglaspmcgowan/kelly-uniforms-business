<!-- GENERATED FROM .agents/work/state.json. DO NOT EDIT DIRECTLY. -->
# Project

- Project: kelly-uniforms-business
- Kind: client
- Initiative: mt-uniforms-replatform
- Root: C:\Users\dougl\Projects\kelly-uniforms-business
- Remote: github.com/douglaspmcgowan/kelly-uniforms-business
- Breadth boundary: project

## Intent

M.T. Uniforms LLC is a real uniform shop at 525 Franklin Street in Johnstown, Pennsylvania, serving police, fire, EMS, corrections, constables, and postal carriers across western Pennsylvania. It fits people in person, hems and decorates what it sells, and quotes that work at the counter. This project exists to serve that business, not to produce a website artifact.

This is a client business project, not an internal workstream. Every deliverable is judged by whether it helps the shop take, fit, decorate, and bill an order better than it does today, and by whether what it publishes about the business is true. A storefront that renders correctly while stating the wrong hours, the wrong address, or a founding year nobody can source is a failure of this project even if every test passes.

Three things follow from that framing and govern the work. The counter is the source of truth about the business, so any fact the site publishes about hours, location, history, or services is confirmed with the client before it ships rather than inferred from the old site or a directory listing. Decoration and agency billing are the real business and are almost entirely absent from the existing product data, so the gap between what the shop sells and what any website can express is the central design problem rather than an edge case. And the customer and order records inherited from the previous site are other people personal data, held by a business that changed hands in April 2026, so moving them anywhere is a decision with a reason attached and never a default step of a migration.

## Specs

- [ ] `published-business-facts-are-client-confirmed` Every fact the storefront publishes about the physical business — street address, ZIP, phone, hours, founding year, and services offered — traces to a client confirmation recorded in SOURCES.md. No such fact is carried forward from the previous owner's site or from a third-party directory listing without that confirmation. The storefront currently claims 'since 1985' with no source, and publishes Monday-Friday 9:00-5:00 hours that no external listing corroborates.
- [ ] `storefront-matches-the-google-business-profile` The address, phone, and hours on the storefront match the business's Google Business Profile exactly, and the storefront gives a street address and a map link on its contact page. A customer who finds the shop on Google and a customer who finds it on the website are told the same thing about where it is and when it is open.
- [ ] `inherited-personal-data-moves-only-on-a-recorded-decision` The 2,212 customer records and 1,154 order records extracted from the previous site are not loaded into any new system until a dated decision recording the business reason appears in the project's Open Decisions document. Absent that decision, the generated customers.csv and orders.jsonl stay under PROJECT_DATA_ROOT and outside Git. The business changed hands in April 2026, which makes this a transfer between owners rather than an internal migration.
- [ ] `the-counter-can-take-an-agency-order` A quartermaster ordering for twenty officers can complete that order through whatever the project ships, carrying a PO number and per-officer sizes, and receives one invoice. Today this is impossible: there is no quantity-by-size grid, no PO field, and the checkout is a mailto: that cannot hold a twenty-line order.
- [ ] `decoration-is-expressible` Hemming, name tapes, patches, and embroidery can be requested, priced or explicitly quoted, and routed to the person who does the work. This is the highest-margin service the shop sells and it appears nowhere in the 407-product catalog extracted from the old site.
- [ ] `no-unbuildable-price-is-advertised` No product displays a price that no valid configuration can reach. Six products currently do, because a required option group has no zero-cost choice: a cap listed at 59.99 US dollars cannot be built below 116.98.

## Global definition of done

- All active-cell tasks are closed with evidence.
- Generated views reconcile with canonical state.
