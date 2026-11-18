---
name: Principal Architecture Review Guidelines
description: Guidelines and question checklists for boundaries and ownership, scalability and evolution, standards, compatibility and migration, reliability, security, performance, observability, developer experience and cross-team impact. Read when designing or reviewing an architecture or a cross-cutting change.
---

# Architecture review guidelines

Work through the sections that apply. For each, record findings as facts, assumptions or recommendations. Skip sections that do not apply and say so in one line.

## Contents

1. Boundaries, ownership and coupling
2. Scalability and evolution
3. Compatibility and migration
4. Reliability and resilience
5. Security and privacy
6. Performance and resources
7. Observability and operations
8. Standards, developer experience and cross-team impact

## 1. Boundaries, ownership and coupling

- Each module/service has **one reason to change** and owns its data. No other component writes its tables; reads across boundaries go through its API, an event, or an explicitly owned read model.
- Draw boundaries along **business capabilities** (ordering, payment, inventory), not technical layers (a "database service", a "validation service").
- Check **dependency direction**: domain does not depend on infrastructure or transport; shared libraries do not depend on features.
- Look for **hidden coupling**: shared database tables, shared mutable config, synchronous call chains (A→B→C must all be up), shared DTO assemblies that force lock-step releases, temporal coupling ("B must run after A").
- A distributed system is justified by a **force**: independent scaling, independent deployment by separate teams, fault isolation, regulatory isolation. Without one, a module boundary inside one deployable is cheaper.

## 2. Scalability and evolution

- Identify the **first bottleneck** at 10× current load (usually the database: connections, locks, a hot row, an unindexed query) and the cost to remove it. Design so that step is possible, do not build it now.
- Stateless application tier; state in the database or a cache with clear ownership.
- Expect requirements to change: keep the parts most likely to change (pricing rules, workflows, integrations) behind a seam that is already needed, not behind speculative plug-in frameworks.
- **Avoid premature optimization**: no sharding, caching tier, CQRS or event sourcing without a measured or credibly forecast need.

## 3. Compatibility and migration

- **APIs**: additive changes only within a version (new optional fields, new endpoints). Removing/renaming a field, changing a type or meaning, or tightening validation is breaking. Breaking changes need a new version or a deprecation window with usage telemetry.
- **Tolerant reader**: clients ignore unknown fields; servers accept old shapes during transition.
- **Database — expand / migrate / contract**: (1) add new column/table, nullable or defaulted, code writes both or reads both; (2) backfill in batches, verify; (3) switch reads; (4) remove the old one in a later release. Each step deployable and reversible on its own.
- **Zero-downtime**: old and new application versions run at the same time during a rolling deploy, so every schema change must work with both. Avoid long locks: create indexes concurrently/online, batch updates, no table rewrites at peak.
- **Rollback**: state how to roll back each step and what happens to data written by the new version. A migration that cannot be rolled back needs a feature flag or a forward-fix plan, said explicitly.
- **Events/messages**: version the schema, keep consumers tolerant, never change the meaning of an existing field.

## 4. Reliability and resilience

- Every remote call has a **timeout** (shorter than the caller's own timeout) and a cancellation path.
- **Retries** only for transient faults, with exponential backoff and jitter, a cap, and only on **idempotent** operations (or with an idempotency key). Retries multiply load — no retries at every layer.
- **Circuit breaker / bulkhead** where a slow dependency could exhaust threads or connections. In .NET, `Microsoft.Extensions.Http.Resilience` (Polly v8) provides the standard pipeline.
- **Idempotency** for any operation a client or broker may repeat: payments, order creation, message handlers. Use an idempotency key with a unique constraint, or natural idempotency (upsert, state check).
- **Consistency**: name the guarantee for each flow (strong within one DB transaction; eventual across services). Never call an external system inside a DB transaction and assume both succeed together — use the outbox pattern, or a saga with compensations.
- **Failure modes table**: for each dependency — what happens when it is slow, down, returns garbage, or succeeds twice?
- **Disaster recovery**: RPO/RTO stated, backups tested by restoring, not by existing.

## 5. Security and privacy

- **Threat model** new trust boundaries quickly with STRIDE: who can spoof, tamper, repudiate, read, deny service, escalate here?
- **Authentication** at the edge with a standard protocol (OIDC/OAuth 2.0, JWT validated for issuer, audience, lifetime, signature). Do not invent token formats or crypto.
- **Authorization** on every request at the resource level (does *this* user own *this* order?) — not just "is logged in". Prefer policy-based authorization; deny by default.
- **Input**: validate at the trust boundary; parameterize all SQL; encode output; limit sizes.
- **Secrets** in a secret store / environment, never in source or logs. **Least privilege** for service accounts and DB users.
- **Personal data**: collect the minimum, encrypt in transit and at rest where required, mask in logs, define retention and deletion.

## 6. Performance and resources

- Start from a **requirement** (p95/p99 latency, throughput, cost ceiling) and a **measurement** (profile, trace, query plan, load test). Name which resource is the bottleneck: CPU, memory/GC, database, network, lock contention.
- Database first: N+1 queries, missing indexes, `SELECT *` over wide rows, unbounded result sets, chatty round-trips, long transactions holding locks.
- .NET: blocking on async (`.Result`, `.Wait()`), per-request `HttpClient` creation (socket exhaustion — use `IHttpClientFactory`), large allocations in hot paths, EF Core change tracking on read-only queries (`AsNoTracking`), loading whole tables into memory before filtering.
- Pagination and limits on every list endpoint.
- Optimize only the measured hot path, and re-measure after.

## 7. Observability and operations

- **Structured logs** with correlation/trace IDs; log events and decisions, not secrets or full payloads with personal data.
- **Metrics**: the RED set (rate, errors, duration) per endpoint and dependency, plus saturation (pool usage, queue depth). Business metrics where they detect failure faster (orders/min).
- **Distributed tracing** via OpenTelemetry across service and queue hops.
- **Alerts on symptoms users feel** (error rate, latency SLO burn), not on every cause; each alert has a runbook.
- Health checks: liveness (process up) separate from readiness (dependencies reachable).
- Can on-call answer "what changed, what is failing, for whom" within minutes?

## 8. Standards, developer experience and cross-team impact

- Standards should remove decisions people should not have to make (logging setup, error format, auth middleware, CI pipeline) and leave room where judgment matters. A standard nobody can follow without a meeting is too complex.
- Prefer **templates, analyzers and shared building blocks** that encode the standard over documents that describe it: `.editorconfig` + analyzers (`TreatWarningsAsErrors` for new projects), a `dotnet new` template, shared CI workflow, a common `ProblemDetails` error format.
- Shared libraries are a coupling cost: keep them small, stable, versioned, and free of business logic.
- For any change: which teams, services, clients, data consumers and runbooks are affected? Who must be told, and in what order do changes ship?
