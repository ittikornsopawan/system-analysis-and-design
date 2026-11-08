---
name: Supporting Payment Sequence Research
description: Evidence and review questions for drawing checkout, Stripe webhook and refund recovery sequences without changing the current payment contracts.
---

# Supporting payment sequence research

Researched 2026-11-07 against the local project specifications and current official Stripe documentation. **SPEC** below means current written behavior, not verified implementation or approval: the referenced legacy API files lack the required approval frontmatter. **PROPOSED** means recovery design requiring subsequent specification approval. This note changes no API, SQL, persisted status or provider integration.

## Current SPEC boundaries

Checkout preview reads current prices, availability and campaign budgets without reserving anything. Create-order revalidates, creates one `WAIT_PAYMENT` order per shop, snapshots address/prices, conditionally takes lot stock and campaign budget, records `RESERVE`, and removes selected cart lines in one PostgreSQL transaction. A shortage rolls back every shop order. The specified payment window is 30 minutes. [Checkout preview](../doc/api/sales/01-inquiry-checkout/spec.md), [create order](../doc/api/sales/02-create-order/spec.md).

Start-payment locks the order, checks ownership/status/expiry, calculates shipping and THB amount server-side, and creates or reuses a PaymentIntent. The new payment UUID is the provider idempotency key; metadata includes `paymentId` and `orderId`. One live payment is enforced by a partial unique index. Stripe.js receives the client secret; browser success does not confirm the order. Stripe timeout/refusal currently returns 408 with local rollback. [Start payment](../doc/api/payment/01-start-payment/spec.md), [payment schema](../doc/schema/payment/t_payment.md).

The webhook verifies the raw-body signature and delivery timestamp, resolves the PaymentIntent, locks the order first and applies status guards. Success confirms an order still `WAIT_PAYMENT`, even past expiry while stock remains held. A previously cancelled order triggers a full late-payment refund without restoring stock twice. Unknown payments currently return 200 `IGNORED`. Cancellation/expiry skips `PROCESSING` payments; stock and reserved campaign budget are restored together. [Webhook](../doc/api/payment/02-stripe-webhook/spec.md), [cancellation](../doc/api/sales/05-cancel-order/spec.md).

Refund requires an authorized shop ADMIN/STAFF or PLATFORM_ADMIN, `COMPLETED` payment and `PAYMENT_CONFIRMED` order. SPEC requests a full refund including shipping with key `refund-<paymentId>`, then marks payment/order `REFUNDED`, restores lots and releases campaign budget in one local transaction. A following webhook is a no-op. [Refund](../doc/api/payment/05-refund-payment/spec.md).

## Provider evidence and correctness gaps

Stripe network failure leaves execution uncertain; a 500 can also have side effects. Its guidance is to preserve operation identity, retrieve provider objects and reconcile with webhooks rather than start a new operation. **Inference:** PostgreSQL rollback cannot undo Stripe success. If creation succeeds but the SQL commit fails, the generated payment UUID/provider mapping can disappear; the next request can use a different key. The existing unknown-payment 200 path then discards the orphan’s webhook. [Stripe error handling](https://docs.stripe.com/error-low-level).

For API v1, the same key replays the original response, including 500, and requires matching parameters. Keys may be removed after at least 24 hours. A key therefore prevents repeated provider execution only within its supported lifetime; it is not permanent business deduplication. [Stripe idempotency](https://docs.stripe.com/api/idempotent_requests).

Stripe events can repeat or arrive out of order. Event IDs identify repeated deliveries; object ID plus event type can identify separately generated duplicates. Event `created` is not a reliable ordering key. Verify the raw payload/signature; delivery retries receive fresh signatures, so signature age differs from event age. Live automatic retries last up to three days. These guarantees do not establish exactly-once processing. [Stripe webhooks](https://docs.stripe.com/webhooks).

Refund creation does not guarantee final settlement: refund status can be `pending`, `requires_action`, `succeeded`, `failed` or `canceled`. PromptPay can require customer refund instructions, another missing recovery path. Also, `charge.refunded` includes **partial** refunds. SPEC currently treats that event as a full refund/restock and does not model pending/failed refund outcomes. Diagrams must flag this contract gap instead of presenting it as safe provider behavior. [Refund object](https://docs.stripe.com/api/refunds/object), [refund events](https://docs.stripe.com/refunds#refund-events).

## PROPOSED recovery behavior for review

Persist a durable operation identity, immutable parameters and reconciliation evidence before the external mutation; serialize conflicting operations for the same order. Keep operation progress distinct from approved order/payment statuses. The existing payment schema cannot represent every recovery step: its required provider ID and refund constraints mean this needs a separately approved data design, not invented columns in these diagrams. [Current schema](../doc/schema/payment/t_payment.md).

After timeout or provider success followed by local failure, retain an unresolved operation and prevent an unrelated replacement. Retry the same operation/key/parameters only within Stripe’s documented retry window; after 24 hours, stop POST retries and reconcile through provider retrieval, request inspection and verified events, escalating unresolved cases. Metadata aids correlation but is not authorization or permission to recreate an order. [Stripe recovery guidance](https://docs.stripe.com/error-low-level#post-requests).

Propose a durable verified-event inbox plus idempotent consumer, atomically recording SQL business effects and completion evidence. Acknowledge only after durable acceptance; failed acceptance receives non-2xx. This replaces the current synchronous/unknown-payment behavior only after approval. Quarantine unmatched events for reconciliation; verify amount, currency, provider account/mode and local association. Guards must also prevent duplicate stock/budget release. Reconcile full refund amount and final provider outcome before financial completion; pending, failed and dashboard partial refunds require an explicit approved policy.

Redis remains admission/cache infrastructure, never payment deduplication or stock authority. Signed webhooks bypass Redis admission. MongoDB remains derived audit/projection storage; a source SQL outbox and asynchronous relay are proposed, and MongoDB failure after SQL commit cannot trigger another charge/refund. No transaction spans PostgreSQL, Stripe and MongoDB. [Redis proposal](redis-design.md), [MongoDB proposal](mongodb-design.md).

## Three high-level sequence recommendations

Use solid **SPEC** messages and a separately labelled **PROPOSED recovery** panel. Count every request/response arrow; use notes for validations and transaction contents, not hidden extra calls.

| Diagram | Lifelines and message budget | Question and required content |
| --- | --- | --- |
| Checkout and payment start | Customer, API, Redis, PostgreSQL, Stripe; at most 12 messages | Preview is non-reserving; create-order is atomic; rate admission precedes mutation; start-payment locks/reuses or creates; client secret follows local commit. Mark provider-success/SQL-failure as unresolved, never “provider rolled back.” Show browser confirmation only as a note. |
| Signed webhook and projection | Stripe, API, PostgreSQL, Relay, MongoDB; at most 12 messages | Signature validation precedes effects; current guarded SQL commit precedes 200. Duplicate event has no extra business effect. Proposed inbox/outbox and asynchronous publication are visibly separate; MongoDB outage retries publication only. |
| Refund and reconciliation | Shop, API, PostgreSQL, Stripe, Reconciler; at most 12 messages | Permission/order guards precede refund. Show provider success plus SQL failure, stable-key recovery/retrieval, then one guarded SQL finalization. Pending/partial refunds are a review gap. Late-payment compensation restores neither stock nor budget again. |

## Acceptance cases for later specification

- Concurrent checkout shortage: all shop orders roll back; no partial reservation.
- Duplicate payment start: one logical operation/PaymentIntent across process restart.
- Provider success then SQL failure: no false “nothing happened”; recover association without a second charge.
- Duplicate/out-of-order webhook: no final-state regression or repeated stock/budget release; unknown association is investigated.
- Refund timeout or commit failure: stable identity survives; no replacement refund; unresolved requests beyond 24 hours stop POST retry.
- Pending/failed/partial refund: no unsupported full-refund completion or automatic restock.
- Cancellation racing late success: retained stock confirms once, or cancelled order compensates once.
- Redis/MongoDB outage: verified payment truth remains in PostgreSQL/provider reconciliation; projection retry never repeats money movement.

These are proposed review cases, not executed tests. Runtime behavior, recovery storage and revised error contracts remain unverified and unapproved.
