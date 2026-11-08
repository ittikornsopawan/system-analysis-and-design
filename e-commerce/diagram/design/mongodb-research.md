---
name: MongoDB Architecture Research
description: Official MongoDB evidence and candidate boundaries for reviewing runtime configuration and transaction-related document storage before approving an e-commerce architecture extension.
---

# MongoDB architecture research

Researched on 2026-11-07. This is research, not an approved specification. The user's transaction categories and configuration scope remain unresolved. Candidate collections and controls below require design approval; this note creates no schema, endpoint, retention policy, or authority transfer. Sources use MongoDB's current manual and current .NET/C# driver documentation; implementation must pin compatible server and driver versions.

## Runtime configuration candidates

Candidate non-secret values include storefront announcement text, display labels, supported presentation locales, and optional UI presentation settings. Confirm which values are platform-wide, environment-specific, or shop-specific; precedence, writer permissions, publication timing, rollback, and unavailable-store behavior are product decisions. Changes affecting pricing, stock, permissions, or payment behavior need their governing business specifications reviewed separately.

Recommended document metadata is `schemaVersion`, canonical scope identity, `key`, `revision`, typed `value`, and update provenance. MongoDB validation can constrain types, required fields, and allowed values; its default rejection behavior should be deliberately selected rather than relying on flexible documents alone. `schemaVersion` identifies document shape, while `revision` identifies content changes. Readers and writers must explicitly support every retained shape. [Schema validation](https://www.mongodb.com/docs/manual/core/schema-validation/), [schema versioning](https://www.mongodb.com/docs/manual/data-modeling/design-patterns/data-versioning/schema-versioning/).

Two candidate collections keep different queries clear:

| Candidate | Identity and indexes to evaluate |
| --- | --- |
| `runtime_config_current` | Unique `(environment, scopeType, scopeId, key)` for one current value. Require canonical, non-null scope fields. |
| `runtime_config_revisions` | Unique `(environment, scopeType, scopeId, key, revision)` for retained revisions; no uniqueness on the logical key alone. |

These are recommendations using MongoDB compound uniqueness and its separate-current/history pattern, not approved collection contracts. If active and historical rows instead share a collection, a partial unique index can constrain only rows matching an explicit current-state filter; that filter must also inform reads. Sharding would require revisiting unique-index/shard-key restrictions. [Unique indexes](https://www.mongodb.com/docs/manual/core/index-unique/), [partial indexes](https://www.mongodb.com/docs/manual/core/index-partial/), [document history](https://www.mongodb.com/docs/manual/data-modeling/design-patterns/data-versioning/document-versioning/).

Use optimistic concurrency: match the logical identity and expected `revision`, set the new value, and increment `revision` in the same update. Zero matched documents requires conflict handling rather than an unconditional overwrite. A single-document update is atomic; preserving a separate revision and updating current configuration together requires an explicitly designed MongoDB transaction if both must succeed together. [Atomic updates](https://www.mongodb.com/docs/v8.0/core/write-operations-atomicity/), [transactions](https://www.mongodb.com/docs/manual/core/transactions/).

## Refresh and recovery

Change streams could notify application instances to reload configuration. They require a replica set or sharded cluster with WiredTiger and replica-set protocol version 1; a standalone development instance cannot exercise this design. Notifications represent majority-committed changes. Preserve the opaque resume token and resume using the same pipeline/options; history must still exist in the oplog. `resumeAfter` cannot cross an invalidation event, while `startAfter` can start after one. [Change streams](https://www.mongodb.com/docs/manual/changestreams/).

Recommended recovery controls are durable checkpoints after successful handling, idempotent refreshes, periodic revision reconciliation, and a tested full reload/rebuild when resumption is impossible. A stream is notification machinery, not permanent application history. Size the oplog against expected outages and monitor consumer lag. Treat `fullDocument: updateLookup` as a later document lookup, not an immutable snapshot of the original update. Approve startup bootstrap, stale-config tolerance, and recovery behavior before implementation. [Stream production guidance](https://www.mongodb.com/docs/manual/administration/change-streams-production-recommendations/), [lookup and resume semantics](https://www.mongodb.com/docs/manual/changestreams/).

## Transaction-related documents and consistency

Candidate separate collections include `integration_events`, `transaction_status_projections`, and `application_audit_events`. Their purpose could be delivery diagnostics, query-oriented status views, or change evidence. Proposed fields are stable event identity, source record identity/version, event type, occurrence time, correlation identity, and a minimized payload. Unique event identity can support deduplication; source-version checks can prevent stale projection updates. These are design recommendations based on unique keys and conditional atomic updates, not approval to move order, payment, settlement, refund, stock, or financial truth. [Unique indexes](https://www.mongodb.com/docs/manual/core/index-unique/), [atomic updates](https://www.mongodb.com/docs/v8.0/core/write-operations-atomicity/).

MongoDB supports atomic operations within one document and transactions across MongoDB documents, collections, databases, and shards. Multi-document transactions require replica-set/sharded deployment and introduce operational cost. Their documented boundary does not provide an atomic PostgreSQL-plus-MongoDB commit; do not draw one shared transaction around both stores. This cross-store conclusion is an architectural inference from the documented MongoDB transaction/session boundary. [Transaction scope](https://www.mongodb.com/docs/manual/core/transactions/), [deployment prerequisites](https://www.mongodb.com/docs/manual/core/transactions-production-consideration/), [.NET sessions](https://www.mongodb.com/docs/drivers/csharp/current/crud/transactions/).

If an approved source of truth remains PostgreSQL and MongoDB holds projections, recommend a transactional-outbox design: commit source mutation and publication intent in the same source transaction, then asynchronously deliver with retries. Require stable event IDs, idempotent application, per-source ordering/version checks, observable lag/failures, replay, and reconciliation. Acknowledge delivery only after the destination write succeeds. This recommendation addresses the inferred cross-store boundary; it is not a claim that MongoDB supplies a PostgreSQL outbox or exactly-once delivery, and authorizes no new tables.

## Retention, security, and .NET seams

TTL is suitable only after collection-specific retention is approved. It uses a separate single-field date index; missing/non-date expiry fields do not expire. Deletion runs in the background and may be delayed beyond the monitoring interval. Queries needing immediate logical expiry must filter it themselves. Do not infer audit, financial, or legal retention from TTL capability. [TTL behavior and restrictions](https://www.mongodb.com/docs/manual/core/index-ttl/).

Recommend excluding credentials, signing/encryption keys, connection-string secrets, tokens, and unnecessary customer/payment payloads from runtime configuration and projections. Bootstrap connection credentials outside the configuration collection. Apply least privilege, authenticated access, TLS, and suitable encryption at rest; separate configuration writers from application readers and projection writers. These are proposed controls, with MongoDB's documented security mechanisms as evidence. [Security checklist](https://www.mongodb.com/docs/manual/administration/security-checklist/).

Reuse `MongoClient` with a singleton lifetime and register it through dependency injection. Recommended application seams are configuration-reader/publisher and projection-writer interfaces with MongoDB implementations behind them. Keep sessions operation-scoped and tied to their creating client; the .NET driver does not support parallel operations inside one transaction. Reuse the client for multiple sessions. [Client lifetime](https://www.mongodb.com/docs/drivers/csharp/current/connect/mongoclient/), [official DI example](https://www.mongodb.com/docs/drivers/csharp/current/integrations/odata/), [transaction sessions](https://www.mongodb.com/docs/drivers/csharp/current/crud/transactions/).

## Decisions still required

- Identify each transaction category, its authoritative store, and its acceptable projection delay.
- Confirm configuration scopes, precedence, authorized writers, publication/rollback, and outage behavior.
- Select server/driver versions, deployment topology, recovery objectives, and retention per collection.
- Approve consistency and security contracts before schema, API, or backend implementation.

## Source ledger

All sources are official MongoDB documentation, accessed 2026-11-07. Inline links identify the supporting page for each finding; recommendations and inferences are labeled above.

| Source | Evidence used |
| --- | --- |
| [Schema validation](https://www.mongodb.com/docs/manual/core/schema-validation/) | Required structure, types, rejection behavior |
| [Schema versioning](https://www.mongodb.com/docs/manual/data-modeling/design-patterns/data-versioning/schema-versioning/) | Explicit shape versions and reader/writer handling |
| [Document history](https://www.mongodb.com/docs/manual/data-modeling/design-patterns/data-versioning/document-versioning/) | Separate current and revision collections |
| [Unique indexes](https://www.mongodb.com/docs/manual/core/index-unique/) / [partial indexes](https://www.mongodb.com/docs/manual/core/index-partial/) | Compound identity, filtered uniqueness, sharding constraints |
| [Atomicity](https://www.mongodb.com/docs/v8.0/core/write-operations-atomicity/) | Conditional single-document updates |
| [Change streams](https://www.mongodb.com/docs/manual/changestreams/) / [production guidance](https://www.mongodb.com/docs/manual/administration/change-streams-production-recommendations/) | Prerequisites, resume tokens, oplog limits, lookup semantics |
| [Transactions](https://www.mongodb.com/docs/manual/core/transactions/) / [production considerations](https://www.mongodb.com/docs/manual/core/transactions-production-consideration/) | MongoDB transaction scope and deployment requirements |
| [TTL indexes](https://www.mongodb.com/docs/manual/core/index-ttl/) | Delayed background deletion and date/index restrictions |
| [Security](https://www.mongodb.com/docs/manual/administration/security-checklist/) | Authentication, least privilege, TLS, encryption |
| [.NET client](https://www.mongodb.com/docs/drivers/csharp/current/connect/mongoclient/) / [DI](https://www.mongodb.com/docs/drivers/csharp/current/integrations/odata/) / [transactions](https://www.mongodb.com/docs/drivers/csharp/current/crud/transactions/) | Singleton reuse, DI, client-bound sessions, sequential transaction operations |
