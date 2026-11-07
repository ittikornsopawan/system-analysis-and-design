---
name: E-commerce Architecture Diagrams
description: Explains the three researched diagram views, project evidence, editable sources, fidelity decisions, reproduction and verification; read when reviewing or updating the diagrams.
---

# E-commerce Architecture Diagrams

The three files answer different questions. The 2026-11-07 revision adds concrete project detail and replaces the earlier uniform component-card treatment. They distinguish existing code, specified commerce behavior and the owner-requested Redis/MongoDB architecture proposal. Proposed policies remain in review; no backend, API contract or database implementation is changed.

| File | Question and visual grammar | Added detail |
| --- | --- | --- |
| [architecture-design.drawio.png](architecture-design.drawio.png) | **What collaborates at runtime?** Architecture with nested system/application boundaries and integration paths. | Client roles, one HTTP/CQRS host, core interfaces, infrastructure, authoritative PostgreSQL, Stripe paths and proposed MongoDB plus isolated Redis cache/rate stores. Nine functional nodes and eleven connectors. Config ownership, asynchronous transaction copies, cache invalidation and quota outage behavior are explicit. |
| [repository-architecture.drawio.png](repository-architecture.drawio.png) | **Where does each responsibility live?** A three-level source Tree. | Solution/build settings, source/test folders, five production projects, representative filenames, core-owned interfaces, exact nine production and five test references, two existing xUnit suites, adjacent specification/database artefacts and proposed cache/rate/config/projection ports and adapters. Nine nodes and eight containment connectors. |
| [system-design.drawio.png](system-design.drawio.png) | **How does an order progress or recover?** State Machine using the Lifecycle phase map pattern. | Four primary order phases, two alternate terminal outcomes, payment retry, guarded return from fulfilment, actor ownership, cancellation/expiry guards, split parcels, full refunds, stock/budget reservation and release, transaction scope, lock order, late-event behavior and proposed Redis admission/cache plus PostgreSQL-outbox-to-MongoDB publication. Six persisted order states, an initial marker and eight transitions. |

Open any PNG directly in draw.io to edit it. Matching `.drawio` sources are also supplied. Matching `.html` files contain accessible inline SVG and support local horizontal scrolling at narrow widths.

## Detailed Thai Explanations

Read each companion document beside its matching image. These explanations record the existing diagram decisions and their rationale; they do not approve proposed policies or change the source specifications.

| Explanation | Coverage |
| --- | --- |
| [architecture-design.md](architecture-design.md) | All 9 runtime components and 11 relationships; CODE/SPEC/PROPOSED labels; PostgreSQL/Redis/MongoDB authority; cache, quota, config and outbox flows; rationale, trade-offs and operational limits. |
| [repository-architecture.md](repository-architecture.md) | All 9 tree nodes/8 containment relationships; five production projects, nine production and five test references; responsibility placement, dependency inversion, proposed adapters and test boundaries. |
| [system-design.md](system-design.md) | All 6 persisted order states and 8 transitions; actors/guards/actions, payment/parcel separation, stock/budget invariants, late payment/refund/recovery examples and Redis/MongoDB failure boundaries. |

## Research and Presentation Decisions

[research.md](research.md) records official sources and project evidence. C4 separates runtime context/container/component/code perspectives; it does not prescribe these filenames. Microsoft distinguishes compile references from runtime dependency injection and documents CQRS without requiring separate databases or a broker. W3C describes transitions with events, guards and actions. These inform the editorial choices here. [C4 containers](https://c4model.com/diagrams/container), [Microsoft architecture](https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures), [Microsoft CQRS](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs), [W3C transitions](https://www.w3.org/TR/scxml/#transition).

The architecture view is an explicitly scoped runtime/context hybrid rather than a strict single-level C4 rendering. Its API, domain and adapter boxes are parts of one backend application. The outer dashed region scopes backend/primary data; the separate MongoDB and Redis boxes express data-service responsibilities without asserting deployment ownership or replica topology. Solid code-backed components and explicit SPEC labels separate implemented Authen from broader specified commerce behavior. The actor grouping represents client responsibilities, not three implemented frontends. No gateway, cloud platform, broker, carrier API or deployment topology is invented.

The repository view uses containment arrows only. `REF` lines reproduce direct `.csproj` references; they are not runtime arrows. This prevents the old request pipeline from being mistaken for repository structure. The two test projects use existing entities/value-object tests and handler tests with in-memory fakes; no C# database integration suite is claimed.

The system view uses one dominant State Machine grammar rather than mixing actor lifelines into the lifecycle. The primary rail is `WAIT_PAYMENT → PAYMENT_CONFIRMED → PROCESSING → COMPLETED`. `CANCELLED` and `REFUNDED` are separate alternate terminal outcomes. Payment and parcel statuses are explicitly different entities. Detailed SQL remains in API specs and their sequence files.

## Evidence and Fidelity Ledger

- Runtime evidence: `../repository/src/Ecommerce.Api/Program.cs`, `Controllers/AuthenController.cs`, `../repository/src/Ecommerce.Shared/Cqrs/Dispatcher.cs`, `../repository/src/Ecommerce.Application/Features/Authen/`, `../repository/src/Ecommerce.Infrastructure/DependencyInjection.cs`, and `Persistence/Authen/`. Email remains `LoggingEmailSender`, an in-process development stub.
- Repository evidence: `../repository/project-structure.md`, `../repository/Directory.Build.props`, every `src/*/*.csproj` and `tests/*/*.csproj`, and the representative source/test filenames. The Component Repository migration is still pending; this task does not move code or create nested Git metadata.
- Lifecycle evidence: `../doc/api/sales/02-create-order/spec.md`, `sales/05-cancel-order/spec.md`, `payment/01-start-payment/spec.md`, `payment/02-stripe-webhook/spec.md`, `payment/05-refund-payment/spec.md`, `shipping/01-create-shipping/spec.md`, `shipping/02-update-shipping-status/spec.md`, `shipping/06-confirm-delivery/spec.md`, campaign rules C2–C9, and the current migrations/schema documents.
- The original architecture and system PNGs were empty. The initial repository PNG contained an Authen request pipeline. That pipeline's responsibilities now live inside the runtime architecture view, with validation order and interface ownership retained. The repository file is replaced by the source/dependency tree.
- The previous compact code-reference picture is expanded into the source tree; no production reference is omitted. The old nine-capability system map is replaced by the order lifecycle. Catalog taxonomy, campaign configuration and individual table structures remain in their specifications rather than being misrepresented as order states.
- Success, failure, retry, cancellation, late payment, partial parcels, guarded seven-day completion and refund effects are summarised at lifecycle level. Payloads, exact SQL, exhaustive HTTP errors and full provider event tables remain in the linked API specifications.
- The HTTP pipeline and CQRS use cases are merged into one runtime host to keep the nine-node budget; their actual five-project split remains explicit in the repository view. Expiry and guarded seven-day automatic completion are specified responsibilities; their worker implementation/hosting is unresolved. Shipping stops remain shop-entered data. A payment failure does not create a new order failure state, and a late refund does not release cancelled stock twice.

## Style, Sources and Reproduction

The owner approved the diagram-design default light style: paper `#f5f5f5`, ink `#2d3142`, accent `#bf4520`. Each view uses `print-a3-landscape` 1584 × 1120, the print type ramp, one focal node, orthogonal rounded routing and a bottom legend. Rich detail rows keep technical paths/types in mono and explanatory prose in sans.

`diagram_content.py` owns the semantic content and explicit geometry. `generate_diagrams.py` produces the HTML and editable draw.io sources, checks code evidence and geometry, and finalises PNG metadata. Run from the repository root containing this directory:

```sh
python3 -B e-commerce/diagram/generate_diagrams.py

for name in architecture-design repository-architecture system-design; do
  /Applications/draw.io.app/Contents/MacOS/draw.io \
    -x -f png --embed-diagram --size page -s 1.5 --theme light \
    --disable-update --timeout 45 \
    -o "e-commerce/diagram/$name.drawio.png" \
    "e-commerce/diagram/$name.drawio"
done

python3 -B e-commerce/diagram/generate_diagrams.py --finalize-pngs
```

draw.io Desktop 32.6.10 includes a one-pixel page frame before scaling. The PR exports use scale 1.5, producing 2378 × 1682 PNGs without cropping or post-export raster resampling. Matching HTML/draw.io sources retain the full 1584 × 1120 vector canvas. Compressed compatibility metadata keeps every final PNG below the repository limit of 1 MiB. PR delivery was directly authorized by the owner on 2026-11-07.

The native PNG key is `mxGraphModel` in a compressed `zTXt` chunk. The installed skill extractor recognises the older `mxfile` key. Finalisation verifies the native model is exactly the `.drawio` source, retains that native metadata and adds the compatible key as a compressed `zTXt` chunk with the same decoded content. PNG CRCs are checked, and every `IDAT` image-data byte is preserved.

The skill's Python PNG helper remains unavailable because Python has no Playwright; the installed draw.io renderer is used instead. The skill's SVG export helper was exercised in a temporary QA location. No dependencies or fonts were installed. HTML retains the default web-font stacks; reviewed native output uses supplied Georgia, Arial and Courier New fallbacks when Instrument Serif, Geist and Geist Mono are unavailable.

## Proposed Redis and MongoDB Responsibilities

The owner selected MongoDB for non-secret feature flags/general configuration (including cache/rate policies), audit/integration events and transaction copies for historical search. PostgreSQL retains authoritative order/payment/refund/stock/campaign and account/permission state.

- [Redis design](redis-design.md) and [research](redis-research.md): cache only public metadata, check live visibility/prices/stock in PostgreSQL, invalidate after commit, guard stale fills and separate rebuildable cache eviction from shared token-bucket memory. True quota denial is proposed as 429; protected-route store outages as 503; signed webhooks and SQL expiry must remain independent of Redis readiness. TTLs, quotas and fallback settings are candidates for approval.
- [MongoDB design](mongodb-design.md) and [research](mongodb-research.md): validated, versioned configuration with local snapshots; configuration publication and its audit evidence use MongoDB-local consistency. PostgreSQL business updates and outbox intent commit together, then a proposed relay delivers idempotent audit/integration events and versioned transaction projections. There is no shared PostgreSQL/MongoDB transaction. MongoDB failure must not repeat a payment or business write. Automatic retention/TTL is not selected.
- [Redis design review](redis-review.md): records independent source-based findings and clearly separated primary-agent remediation. Clock/failover conditions, cardinality budgets, script execution bounds and outage handling still require implementation and operational proof. MongoDB projection lag, retention/capacity and configuration activation also require downstream approval and validation.

Both design documents remain `in-review` with no implementation approval. Proposed middleware, interfaces, adapters, outbox, collections and tests are diagram/design content only. This task creates none of those backend files or database structures.

## Verification of the Combined Data-Service Revision

- Source evidence: all nine production references, all five test references and all six displayed persisted order states match current files. Runtime now has 9 nodes/11 connectors, repository 9/8, and lifecycle 6 persisted states plus initial marker/8 transitions.
- Geometry: node budgets/grid, readable row capacity, perimeter ports, orthogonal paths with 6–8px corner radii, 6–10px label gaps, label/node separation, no stacked/crossing connectors, no transit through unrelated boxes and no connector passing through an annotation.
- Skill: all three `self_check.py` runs pass; accessible title/description IDs, complete HTML, embedded-content safety and viewBox bounds are checked. The installed package lacks its separate repository-only `verify-geometry.py`; explicit model checks and render review cover geometry here.
- Browser: all three final Redis/MongoDB HTML previews at 390px retain a local scroller, a 1584px minimum SVG width, no page overflow and no node text overflow. Print CSS releases the minimum width for paper output.
- Visual: all three final Redis/MongoDB PNGs were inspected, including data-store ownership, the webhook path and lifecycle annotations clear of transition routes. Their silhouettes and content responsibilities were compared across the set.
- Editability: each PNG produces the same extracted model as its `.drawio` source, excluding the input filename. Each final PNG was opened directly by draw.io and exported again at scale 1.5, preserving identical `IDAT` data.
- `git diff --check` passes. Backend builds, API/database tests and real Stripe/carrier calls were not run because this revision changes diagrams and documentation only. The diagrams do not imply that specification-only behavior has been implemented.

## PR Baseline Reconciliation

Before delivery, the branch was compared with current `origin/main`. Merged WP3b adds guarded seven-day system completion in `shipping/06`; the lifecycle diagram, runtime worker note, research and Thai explanation now include it. Candidate scanning filters complete eligibility, each order is rechecked under its lock, partial/unshipped orders do not qualify, and system confirmation does not release campaign budget. Hosting remains unresolved. This is specification alignment, not a new backend job implementation. The additional overview/sequence/data/operations diagrams requested later have not started and are outside this PR.
