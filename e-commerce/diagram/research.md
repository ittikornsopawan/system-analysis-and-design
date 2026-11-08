---
name: E-commerce Diagram Redesign Research
description: Primary-source findings and evidence-based design recommendations; read before redesigning the three e-commerce overview diagrams.
---

# E-commerce Diagram Redesign Research

Researched on 2026-11-07. This note informs presentation choices; it does not approve or introduce architecture or business behavior. Repository facts below come from the primary checkout. The current diagram README was inspected in Jinny's managed workspace.

## Finding: use three different questions and grammars

The current README assigns code dependencies to `architecture-design`, a request pipeline to `repository-architecture`, and nine capability boxes to `system-design`. All three use the same architecture layout and frame. The redesign should instead separate runtime boundaries, source organization, and business behavior. Increase useful detail through containment, relationships, guards, and transaction scope, rather than repeating the same domain boxes.

C4 defines context, container, component, and code as different zoom levels and explicitly says teams need only the views that add value. **These levels do not prescribe this repository's filename meanings.** Mapping the three filenames below is an editorial choice, not a C4 requirement. [C4 diagrams](https://c4model.com/diagrams)

## 1. Architecture: nested runtime boundaries and integration spokes

A context view identifies the system, directly connected people, and external systems. A container view adds applications, data stores, responsibilities, technologies, and communication. Neither requires inventing hosting topology; C4 places environment-specific deployment details in deployment views. [Context](https://c4model.com/diagrams/system-context), [containers](https://c4model.com/diagrams/container)

**Recommendation for `architecture-design.drawio.png`:** use an explicitly titled runtime/integration view with a large system boundary, a nested backend application, a database region, actors outside, and Stripe outside the boundary. This is a deliberate context/container hybrid, not a strict single-level C4 diagram.

- Place customer, shop member, and platform administrator on the perimeter. Distinguish their specified capabilities without implying three implemented frontends.
- Inside the backend, separate HTTP entry/security, CQRS use cases, domain rules, and infrastructure adapters. Show controller → dispatcher/validator → handler and handler → interface → adapter as runtime collaboration, not separate deployed services.
- Show PostgreSQL through Dapper/Npgsql and the implemented Authen persistence path. Group broader schema capabilities as specification scope; do not imply all have runtime implementations.
- Draw the specified payment API → Stripe PaymentIntent call, client/Stripe.js → Stripe card-data path, and Stripe → signature-verified webhook as distinct labeled interactions. Browser completion is not the source of payment truth.
- Keep the implemented `LoggingEmailSender` inside the development boundary as a logging stub. Shipping information is entered by shop users; do not draw a carrier API.

Use solid/dashed styling plus words to distinguish implemented and specified elements. The evidence is [`Program.cs`](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Api/Program.cs), [`DependencyInjection.cs`](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Infrastructure/DependencyInjection.cs), [`payment/01`](../doc/api/payment/01-start-payment/spec.md), [`payment/02`](../doc/api/payment/02-stripe-webhook/spec.md), and [`shipping/03`](../doc/api/shipping/03-upsert-shipping-stop/spec.md). No deployment platform, gateway, broker, or independently hosted commerce service is established by these sources.

## 2. Repository: directory tree with dependency overlay and test rail

Microsoft distinguishes compile-time dependencies from runtime collaboration and explains that infrastructure implements core interfaces, wired through dependency injection. Several projects can run as one application. This supports showing project references separately from the runtime view. [Microsoft web application architecture](https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures)

**Recommendation for `repository-architecture.drawio.png`:** use a source tree rooted at `e-commerce/`, expanding `repository/` into solution/build settings, `src/`, and `tests/`. Place five project cards within `src/`; add a narrow dependency matrix or routed overlay beside the tree and a test rail below it.

Each project needs representative contents: Api controllers/contracts/composition root; Application abstractions and Authen use cases; Domain entities/value objects/repository interfaces; Infrastructure persistence/security/email; Shared results and CQRS primitives. Keep `api/`, `doc/`, `db/`, and `diagram/` as sibling evidence artifacts rather than runtime modules. Source: [`project-structure.md`](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/project-structure.md).

Reproduce all nine direct source references from `.csproj` files: Api → Application, Infrastructure, Shared; Application → Domain, Shared; Domain → Shared; Infrastructure → Application, Domain, Shared. Shared references no source project. The two test projects add five direct references: Domain.Tests → Domain, Shared; Application.Tests → Application, Domain, Shared. Show actual test files as examples, not invented API/infrastructure integration suites. Label arrows **project reference** and give directory containment a different visual treatment.

The current framework is `net10.0` in [`Directory.Build.props`](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/Directory.Build.props). CQRS here separates commands and queries through shared dispatching; it does not establish messaging infrastructure. Microsoft documents basic CQRS using one underlying database, while event sourcing is an additional combination. Consequently, no queue, event store, replica, or separate query database follows merely from the CQRS label. [Microsoft CQRS](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs)

## 3. System: lifecycle swimlanes with transaction callouts

C4 dynamic views show runtime collaboration for a particular use case, using numbered interactions and either collaboration or sequence arrangements. W3C SCXML independently makes events, guards, target states, and transition actions explicit. These support an editorial lifecycle/swimlane hybrid that explains behavior rather than only listing capabilities. [C4 dynamic](https://c4model.com/diagrams/dynamic), [SCXML transitions](https://www.w3.org/TR/scxml/#transition)

**Recommendation for `system-design.drawio.png`:** use horizontal lifecycle phases with customer, commerce transaction, payment/Stripe, and shop/fulfilment lanes. Separate order states from payment and parcel states; identically named statuses are different entities.

Include these concrete branches and side effects:

1. Checkout validates cart/availability, creates one order per shop, snapshots prices/address, reserves lots and campaign budget, writes ledger `RESERVE`, and removes purchased cart lines in one transaction. Stock/budget races roll back the whole request. New orders are `WAIT_PAYMENT`, with a configured payment window. [Sales create](../doc/api/sales/02-create-order/spec.md)
2. Start payment locks the order, checks expiry/ownership/live payment, calculates shipping and total, and creates or reuses a PaymentIntent. A signed webhook moves the order to `PAYMENT_CONFIRMED`; duplicate/stale events are guarded. Late money is refunded without releasing stock twice. [Payment start](../doc/api/payment/01-start-payment/spec.md), [webhook](../doc/api/payment/02-stripe-webhook/spec.md)
3. Cancellation/expiry releases stock and campaign budget with `RELEASE` evidence; a processing payment blocks cancellation and makes expiry processing wait. [Sales cancel](../doc/api/sales/05-cancel-order/spec.md)
4. Shop creates partial parcels, moving the order to `PROCESSING`; parcel states include `PENDING`, `SHIPPED`, `DELIVERED`, `CANCELLED`, and `RETURNED`. Show the guarded route back to `PAYMENT_CONFIRMED` when no live/delivered parcel remains, and refund as its own branch. [Shipping create](../doc/api/shipping/01-create-shipping/spec.md), [status](../doc/api/shipping/02-update-shipping-status/spec.md)
5. The customer confirms receipt, or the system confirms eligible parcels after seven days under the merged WP3b rules. Complete only when delivered quantities cover every item; partial/unshipped orders never qualify. [Delivery confirmation](../doc/api/shipping/06-confirm-delivery/spec.md)

Annotate atomic operations and lock order locally. A scheduled expiry responsibility is specified, but its hosting is unresolved. Keep detailed SQL in API sequence diagrams, with source pointers here.

## Source ledger and review criteria

The official C4 pages above govern view intent; [component](https://c4model.com/diagrams/component) and [code](https://c4model.com/diagrams/code) clarify optional implementation zoom. Microsoft governs the dependency/CQRS comparisons; W3C supplies transition semantics. Local linked code/specs govern all project-specific details. None grants approval for new behavior.

Review each output for a distinct silhouette and question, legible relationship labels, explicit implementation status, traceable states/guards, and absence of unsupported infrastructure. Use a larger canvas when the evidence requires it; retain a shared palette and typography without forcing identical layouts or arbitrary small node budgets.

## Applied editorial choices

The final revision uses Architecture for runtime boundaries, Tree for physical source ownership, and the diagram-design Lifecycle phase map/State Machine for order behavior. The repository lists direct references inside project leaves instead of adding a second arrow grammar. The lifecycle uses state bands rather than actor swimlanes so it preserves one subject and one dominant grammar. All three use an A3 landscape canvas and richer local detail. These are presentation decisions grounded in the sources above, not new system requirements or a claim of strict C4/SCXML conformance.
