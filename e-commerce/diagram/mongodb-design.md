---
name: E-commerce MongoDB Configuration and Event Proposal
description: Review the proposed MongoDB configuration, audit/integration events and transaction projections, together with the Redis proposal, before any collection, API or backend implementation.
status: in-review
approved_by: null
approved_at: null
---

# MongoDB Configuration and Transaction-Related Documents

## Confirmed Direction and Remaining Approval

On 2026-11-07, Ittikorn selected:

- **Transactions:** audit/integration events and transaction copies for historical search.
- **Configuration:** feature flags and general configuration, including cache/rate-limit policy.

MongoDB is therefore proposed as the source of truth for non-secret runtime configuration, and a derived document/query store for PostgreSQL transaction history. PostgreSQL remains authoritative for order/payment/refund/stock/campaign state. This records the selected responsibility split, not approval of all policies below or permission to implement code. Review with [Redis design](redis-design.md), [MongoDB research](mongodb-research.md) and [Redis research](redis-research.md).

## 1. Configuration Model and Publication

Initial scope is platform/environment configuration. Shop-specific overrides and campaign/pricing rules are outside this extension; they retain their existing PostgreSQL specifications.

| Proposed collection | Responsibility | Identity / write behavior |
| --- | --- | --- |
| `runtime_config_current` | Current validated value or configuration bundle | Unique `(environment, scopeType, scopeId, key)`; canonical non-null platform scope |
| `runtime_config_revisions` | Immutable published history and rollback provenance | Unique logical identity plus revision; retain previous published values |
| `application_audit_events` | Configuration publication/change evidence | Stable unique event ID; append-only application permissions |

Each document carries `schemaVersion`, logical key/scope, integer content `revision`, a typed validated value, publication state/effective time, actor ID and timestamps. `schemaVersion` describes document shape; it is not a policy reset number. MongoDB JSON Schema validation must reject unsupported types/ranges/keys. Validate cache TTL limits, quota capacities/refill periods and failure-policy enums before publication; configuration cannot inject arbitrary expressions, scripts or Redis commands. [MongoDB schema validation](https://www.mongodb.com/docs/manual/core/schema-validation/).

Only an authenticated, currently authorized PLATFORM_ADMIN publication workflow may change platform policy. Continue live PostgreSQL permission checks; MongoDB or Redis configuration is never an authorization grant. A conditional update matches the expected revision; a conflict cannot overwrite a newer edit. Publish the current bundle, immutable revision and its audit evidence in one MongoDB transaction when all three must succeed together. Production capability therefore requires a replica set or supported sharded deployment, not a standalone MongoDB instance. Rollback publishes a new revision pointing to an older validated value; history is not rewritten. [Atomicity](https://www.mongodb.com/docs/v8.0/core/write-operations-atomicity/), [transaction prerequisites](https://www.mongodb.com/docs/manual/core/transactions-production-consideration/).

Redis credentials/URIs, MongoDB bootstrap credentials, signing/encryption keys, tokens and other secrets remain in environment/secret management. The configuration database cannot be its own only bootstrap credential source.

## 2. Runtime Configuration Reads and Outages

Applications read a validated published configuration snapshot into a local immutable last-known-good bundle. Avoid a MongoDB lookup on every API request, and do not make Redis a prerequisite for reading the policies that govern Redis. Change streams are refresh hints, with resumable checkpoints plus periodic revision reconciliation (proposed poll interval: 30 seconds). A lost resume window triggers a full validated reload, not a claim of permanent event history. [MongoDB change streams](https://www.mongodb.com/docs/manual/changestreams/).

Proposed outage behavior for approval:

- A previously validated runtime bundle may be used for up to five minutes during MongoDB failure. Record revision/age and expose degraded configuration health.
- After that freshness allowance, unapproved/unknown feature flags are off, public metadata caching is bypassed and public reads use their approved local degraded limits. Sensitive auth/write paths whose policy cannot be established return the configured unavailable response; they do not invent a permissive policy.
- Cold start needs an explicitly supplied last-approved deployment bundle or a valid MongoDB snapshot. Public/webhook host readiness remains independent; protected functions without a valid policy remain unavailable. Secrets are still required and never bypassed.
- Signed provider webhooks and internal SQL expiry processing remain independent of MongoDB configuration availability where their existing verified contract and required credentials are intact.

General config revision and Redis bucket namespace are separate concepts. Publishing a banner/flag/TTL change must not silently reset quotas. Rate policies are activated through a controlled fleet rollout of one approved policy version; explicit counter-epoch rotation is a separate operational decision. Redis's selected failover/clock assumptions and counter-loss limits remain as documented in its proposal.

## 3. Audit, Integration Events and Transaction Copies

| Proposed collection | Purpose | Authority |
| --- | --- | --- |
| `integration_events` | Delivery/retry diagnostics and stable integration-event envelopes | Delivery evidence, not payment/order truth |
| `application_audit_events` | Administrative and selected business change evidence | Auditing/search; not a financial ledger or compliance certification |
| `transaction_status_projections` | Query-oriented current copies and source versions for historical investigation | Derived, possibly delayed copies; source PostgreSQL ID/version remains explicit |

Use stable event ID, source-store/aggregate identity, source version, event/schema type, occurrence time, correlation identity and an allowlisted minimized payload. The initial transaction projection contains status and references; adding customer PII, addresses, card data, credentials, private margins or full raw requests is not authorized. Any richer amount/detail fields need their own visibility/data-minimization review. Read access is initially restricted to platform operational/admin use, with live authorization; existing customer/shop order APIs continue to read their governed PostgreSQL source.

Unique event identity supports idempotent insertion. A current projection accepts only a newer source version and a complete approved snapshot; an old event cannot roll it back. Append-only event history can arrive out of order and is queried with stable source/version/time ordering. Raw provider retries do not invoke order/payment mutations again merely because an audit document is missing.

### Reliable Publication Across Stores

For PostgreSQL-originated events, the proposed source transaction commits the business mutation **and publication intent** in the same PostgreSQL transaction. An asynchronous outbox relay then writes MongoDB with stable IDs, acknowledges delivery after successful destination write, retries failures and exposes dead-letter/lag/reconciliation state. Source-version checks and unique IDs make replay safe. Initial operational objective for review: normal projection lag within five seconds; this is not a measured SLA.

There is no shared PostgreSQL-plus-MongoDB transaction and no exactly-once cross-store claim. If MongoDB is down after a payment/order commits, the order remains committed and publication retries later; no second charge or stock movement occurs. Reads must display source version/time and must not use the projection to settle money, check stock or authorize a refund. MongoDB transactions cover MongoDB operations only. [MongoDB transaction scope](https://www.mongodb.com/docs/manual/core/transactions/).

The outbox and relay do not exist yet. Their PostgreSQL schema, event contracts, worker ownership, backpressure/replay rules and tests are downstream design work requiring the repository's data-modeling/API workflows before implementation. This proposal creates no SQL table or collection and does not relocate business data.

MongoDB-originated configuration audit evidence is committed with its configuration change inside MongoDB's own transaction; it is not incorrectly routed through a PostgreSQL transaction that does not own the configuration.

## 4. Retention, Access and Code Seams

Initial policy: **no automatic TTL deletion** for config history, audit events or transaction projections in this design. Retention/deletion needs explicit collection-specific approval and capacity/privacy review before production; the diagrams do not imply indefinite free storage or a legal retention guarantee. When approved later, TTL is delayed background cleanup and logical expiry must be enforced on reads where required. [MongoDB TTL](https://www.mongodb.com/docs/manual/core/index-ttl/).

Keep config readers, config publishers and event/projection writers under separate least-privilege roles. Require private authenticated connectivity, TLS, suitable encryption at rest, redacted logs and capped/minimized document payloads. Configuration and operational search access cannot be inferred from a caller knowing a document ID.

Proposed source seams, not existing files:

- Application: config snapshot/provider and event/projection contracts; no MongoDB types in Domain.
- Infrastructure: `Configuration/MongoConfigurationProvider.cs`, `Documents/MongoEventProjectionStore.cs`, client/options registration and collection validation/index provisioning under approved operational ownership.
- Api: consume validated snapshots and expose separately specified administrative publication/search behavior only after contracts are approved.
- Tests/worker delivery: configuration revision conflicts, stream resume/full reload, missing/stale config, MongoDB outage, duplicate/out-of-order event delivery, reconciliation and PostgreSQL outbox atomicity.

Reuse an application-lifetime MongoClient; sessions are operation-scoped and bound to their client. A change-stream/outbox delivery worker is a proposed responsibility; hosting is not selected by this diagram task. [MongoClient](https://www.mongodb.com/docs/drivers/csharp/current/connect/mongoclient/), [.NET transaction sessions](https://www.mongodb.com/docs/drivers/csharp/current/crud/transactions/).

## 5. Approval and Verification Boundary

The owner has selected config + audit/event/projection ownership. Approval is still needed for the concrete configuration outage/freshness behavior, controlled policy activation, projection lag objective, initial restricted projection fields/access and the deliberate no-TTL-before-retention-approval policy, together with Redis quotas/isolation/failure behavior. No runtime MongoDB, cross-store, failover, load or security test has run; those remain implementation-delivery requirements.

The three diagrams identify MongoDB and Redis as **PROPOSED**, preserve PostgreSQL authority and show no new persisted order status. Reviewable diagrams are design artifacts, not a claim that any proposed adapter, collection, outbox or worker has been implemented.
