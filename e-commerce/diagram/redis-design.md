---
name: E-commerce Redis Architecture Proposal
description: Review the proposed Redis cache, distributed rate policies, failure semantics and diagram impact before approving any Redis implementation or API contract changes.
status: in-review
approved_by: null
approved_at: null
---

# Redis Cache and Distributed Admission Proposal

## Request, Baseline and Approval Boundary

Ittikorn requested Redis for caching, rate limiting and appropriate related uses on 2026-11-07. That establishes the requested direction. The concrete policies below are **proposed initial settings for approval**, not measured production limits or an already implemented feature.

The current .NET 10 backend has custom CQRS, inner interfaces and Dapper/Npgsql adapters. `Program.cs` and `DependencyInjection.cs` contain no Redis service, distributed cache or rate limiter. The existing Authen design excluded infrastructure/IP rate limiting; this proposal is a separate extension, and retains its SQL-backed account lock/session rules. Those rules describe the specified design; the current Authen subset is not claimed to implement all of them. See [research](redis-research.md), [current architecture](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/project-structure.md), [Authen design](../../docs/superpowers/specs/2026-11-06-authen-design.md), and the [diagram source map](README.md).

This in-review document governs **proposed diagrams only**. Approval here is requested for the cache scope, freshness, quota settings, isolation and outage policy. Endpoint error-body contracts, actual dependencies, Redis deployment configuration and backend implementation require the subsequent approved specifications and verification. No package, service, API, migration or application code is changed by this proposal.

## 1. Responsibilities and Resource Isolation

Use two separately provisioned Redis processes/services in the production design:

| Role | Stored data | Memory behavior | Authority |
| --- | --- | --- | --- |
| Redis read cache | Allowlisted public metadata projections and their cache generations | Bounded memory, `allkeys-lfu`, every data entry has a hard TTL | Rebuildable from PostgreSQL; never decides access or money |
| Redis rate store | Short-lived shared token-bucket state | Independent bounded memory, `noeviction`, idle TTL on every bucket | Admission protection only; not durable business state |

Prefixes and logical database numbers are namespaces, not independent eviction/resource budgets. Separate credentials and configuration are required for the two roles. The diagram shows logical services; no cloud vendor, capacity, cluster topology or deployment platform is selected. A single shared instance is not the proposed production default because cache pressure could otherwise reset quota state or reject admission writes. [Redis eviction](https://redis.io/docs/latest/develop/reference/eviction/), [SELECT](https://redis.io/docs/latest/commands/select/).

PostgreSQL remains the authority for stock, lot selection, checkout prices, order totals, campaign reservations, payment/refund state, account lockout, token/session revocation, permissions and consent. Keep database transactions, locks, constraints and provider idempotency. Redis is not a stock lock, payment deduplication database, session authority or workflow engine.

## 2. Cache Scope and Freshness

Cache **internal, explicitly public projection DTOs**, not whole controller responses, domain objects, authenticated inquiry results or raw database rows.

| Proposed projection | Allowed examples | Hard TTL / jitter | Always checked live |
| --- | --- | --- | --- |
| Product public descriptors | Public name, description, slug, display labels and allowed image references | Random 48–60 seconds; never above 60 seconds | Shop/product/listing/SKU visibility, current referenced child IDs and order, price and stock |
| Public taxonomy labels | Names/labels of currently selected brand/category/type IDs | Random 240–300 seconds; never above 300 seconds | Which IDs may be returned, visibility and endpoint permission |

The initial proposal does **not** cache complete storefront pages, lists, search ordering, price filters, availability, `maxOrderQuantity`, carts, orders, user profiles, addresses, review author data, credentials, access tokens or permission decisions. Storefront APIs combine public text with live lot prices/quantities and ACTIVE rules; caching their entire payload would silently change those rules. Relevant sources: [shop/04](../doc/api/shop/04-inquiry-storefront-product/spec.md), [shop/14](../doc/api/shop/14-inquiry-storefront-shop-product/spec.md), [sales/02](../doc/api/sales/02-create-order/spec.md).

On a hit, PostgreSQL still selects currently eligible IDs and dynamic values; the cached object supplies only approved display fields. If a currently referenced field/child ID is absent from the projection, read it from PostgreSQL and refill. A failed visibility/permission check never falls back to cached content. The ordinary concurrent-request database snapshot behavior remains; Redis must not extend an inactive entity's visibility window.

Display text/image-label updates may remain stale within their approved freshness target after a failed invalidation. This is a deliberate decision requiring owner approval. The TTL values are operational targets under bounded, synchronized clocks, not unconditional elapsed-time guarantees during clock steps/failover. Include source-read UTC time, projection version, generation and freshness budget in the internal cache envelope; compare age against a monitored API/source clock envelope (initial candidate: 250ms skew allowance), and bypass cache when clock health is unknown, skew exceeds that allowance or the timestamp is unexpectedly in the future. Real-time age can differ by the accepted skew budget. On Redis failover/reconnection, bypass restored cache values for the longest configured metadata lifetime and refill only from PostgreSQL; generation guards alone do not prevent a replica from restoring older generations. No stale-while-revalidate response is enabled initially. Request IDs, timestamps, authorization headers and response envelopes are constructed fresh and are never cached.

### Keys, Cache-Aside and Invalidation

Use environment and DTO-version prefixes, bounded canonical identifiers and public scope. Example key shapes:

```text
ec:<env>:c:v1:{pc:<productId>}:g
ec:<env>:c:v1:{pc:<productId>}:d:<generation>:<shapeHash>
ec:<env>:rl:v1:<activePolicyVersion>:<policyId>:<subjectHmac>
```

The first two share the explicit Redis Cluster hash tag `{pc:<productId>}`. No raw email, username, token or IP appears in a key. Limit cached values to 64 KiB, bound supported projection shapes, validate inputs before key creation, and skip cache writes for oversized values. The initial stage caches no errors or negative authorization results.

1. Read/create a cryptographically random generation token for the projection group. Missing/evicted generation keys get a **new random value**, never a resettable zero counter, so old generation data cannot become reachable again.
2. An atomic read script verifies the expected generation before returning its data key. A mismatch is a miss/retry, not a stale hit.
3. On a miss, read eligible public fields from PostgreSQL. A fill script compares the same generation and writes only if it still matches; it cannot overwrite a newer generation. Pass all script keys explicitly and keep them in the same hash slot.
4. A mutating request commits PostgreSQL first, then replaces the affected generation token. Old generation values expire naturally; do not use broad `KEYS`/`SCAN` invalidation in the request path.
5. Cache TTL starts at the metadata read's start: subtract elapsed read time before filling, and skip a fill whose remaining TTL is nonpositive. This bounds stale refill age rather than granting a slow reader a fresh full lifetime.
6. An invalidation failure does not roll back a committed order or retry a provider charge. Record it and rely on the hard freshness limit plus live visibility gates. This is bounded eventual metadata consistency, not an atomic PostgreSQL/Redis commit guarantee.

Invalidate affected public descriptor/label groups after relevant product, image, option, category/type/brand or public shop-display updates. Stock/price/order/payment changes do not need to invalidate stock/prices because those values are never cached in this stage. They still run existing authoritative SQL. A future full storefront cache requires a separate dependency/invalidation design.

Extras included in this proposal: TTL jitter, per-key in-process miss coalescing, bounded refill concurrency (initial candidate: eight database fills per API process), cache-generation guards and observability. Same-key coalescing is **not** a fleet-wide lock. Cache distributed locking, Redis Pub/Sub as reliable invalidation, output caching, review aggregates and warm-up jobs are deferred until evidence justifies them. [Cache-aside](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside), [HybridCache scope](https://learn.microsoft.com/en-us/aspnet/core/performance/caching/hybrid?view=aspnetcore-10.0).

## 3. Distributed Rate Policies

Built-in ASP.NET limiting, including GlobalLimiter, is per process. Use a custom shared-store admission operation so requests reaching different API instances consume the same logical bucket. Retain a separate local concurrency guard to protect each process. [Microsoft rate limiting](https://learn.microsoft.com/en-us/aspnet/core/performance/rate-limit?view=aspnetcore-10.0#rate-limiting-with-multiple-app-instances).

The following token-bucket settings are candidates, not hard rolling-window counts. Each row refills the stated number of tokens over the interval and permits an initial burst equal to capacity. Every request costs one token; no queue is used. Business failure does not refund an admission token.

| Policy | Partition | Refill | Capacity | Redis unavailable |
| --- | --- | --- | --- | --- |
| Public storefront reads | Trusted client IP + public-read group | 60 tokens / 60 seconds | 20 | Same policy locally per instance; log degraded scope |
| Authenticated reads | Validated user ID + read group | 300 / 60 seconds | 50 | Local per-user fallback; log degraded scope |
| Login | Trusted client IP + login route | 20 / 300 seconds | 5 | 503, Retry-After 5 seconds |
| Register | Trusted client IP + register route | 4 / 900 seconds | 2 | 503, Retry-After 5 seconds |
| Password-reset request | Trusted client IP + reset-request route | 3 / 900 seconds | 1 | 503, Retry-After 5 seconds |
| Password-reset confirmation | Trusted client IP + reset-confirm route | 20 / 300 seconds | 5 | 503, Retry-After 5 seconds |
| Order/payment mutations | Validated user ID + commerce-write group | 30 / 60 seconds | 5 | 503, Retry-After 5 seconds |
| Administrative mutations | Validated user ID + admin-write group | 60 / 60 seconds | 10 | 503, Retry-After 5 seconds |

These limits are not account lockout. The existing SQL-backed failed-login counter, REFUSED distinction and account lock rules remain unchanged. Do not create Redis quota partitions from unverified email/username values: password-reset behavior stays independent of account existence.

Public/IP policy runs before expensive work; user partitioning runs only after authentication has validated the principal. Trust forwarded client IP only from explicitly configured proxies/networks; do not accept arbitrary `X-Forwarded-For` or unsigned JWT claims. Use HMAC-SHA256 of canonical subject identity with a protected environment-specific key; retain bucket state only until idle expiry.

One bounded Lua operation uses Redis server TIME, computes nonnegative elapsed time, refills up to capacity, admits or rejects, deducts only an admitted request and updates idle expiry. Use fixed-precision arithmetic and tested rounding. Clamp backward-clock elapsed time to zero and preserve the later stored timestamp. Define `futureLead = max(0, storedTimestamp - serverNow)`; idle expiry must be at least `futureLead + capacity/refillRate + 1 second`. Deleting a depleted bucket before that natural full-refill time would grant an early burst. For a rejection, the next-token delay is `futureLead + (1 - availableTokens)/refillRate`, not just the token deficit. Monitor backward-clock lead and test clock steps. Failover/forward clock changes can still relax admission, bounded by bucket capacity; this is not a strict durable entitlement.

Quota rejection is 429 with `Retry-After = ceil(time until a token is available)`, minimum one second, including any backward-clock timestamp lead. Store timeout/OOM is **not** quota rejection: follow the outage column. Proposed initial operation budgets: 100ms for an admission attempt and 50ms for best-effort cache access; no automatic write retry after an ambiguous timeout, because the first token deduction may have succeeded. A definitive NOSCRIPT result permits reloading the script; it is different from an ambiguous write timeout. Tune through load testing before production.

The local fallback is explicitly per process; it does not preserve a fleet-wide quota during a Redis outage. Fail-closed sensitive policies protect admission while making those routes unavailable. Both trade-offs require owner approval. Replication can lose acknowledged bucket updates on failover; Redis limiting is abuse protection, not a strict financial entitlement or durable quota ledger. Never claim fail-closed disconnection handling eliminates post-failover undercount. [Atomic scripts](https://redis.io/docs/latest/develop/programmability/eval-intro/), [TIME](https://redis.io/docs/latest/commands/time/), [replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/).

Stripe webhooks bypass these user/IP Redis policies. Keep raw-body signature/replay validation, guarded SQL transitions and database idempotency authoritative. Redis unavailability must not prevent a valid provider event from reaching that path. Host/body/concurrency protection remains separate. Existing provider idempotency keys are not moved into disposable Redis state.

The scheduled expiry responsibility also runs internal cancellation rules without a user/IP quota partition. Redis TTL/keyspace events never cancel an order or release stock: PostgreSQL expiry selection and transaction guards remain required. IP-based limits can affect many legitimate clients behind NAT; the candidate values require traffic/load review before rollout.

## 4. Code Seams, Security and Operations

- **Api, proposed:** endpoint policy mapping and Redis-backed admission middleware before handlers; validated user partitions after authentication; distinct 429/503 handling. Preserve auth validation and raw webhook-body processing.
- **Application, proposed:** `ICacheStore` and `IRateLimitStore` ports with public-projection/decision contracts. Domain remains Redis-free. Existing source references need no direction change.
- **Infrastructure, proposed:** `Caching/RedisCacheStore.cs`, `RateLimiting/RedisRateLimitStore.cs`, Redis options and client registration. Reuse an application-lifetime `ConnectionMultiplexer` per Redis role/configuration; do not connect per request. These paths do not yet exist. [StackExchange.Redis lifetime](https://stackexchange.github.io/StackExchange.Redis/Basics.html).
- Private connectivity, TLS, separate least-privilege ACLs/key patterns, connection secrets through environment/secret management, no secret values in diagrams or source. Operations accounts own monitoring; request adapters get no administrative flush/configuration access. [Redis security](https://redis.io/docs/latest/operate/oss_and_stack/management/security/).
- Redis disconnection must not block HTTP host startup or make all API routes unready: publish per-role health and preserve the signed-webhook/database path while affected endpoints follow their own outage policies. Redis readiness must not be an unconditional dependency of the entire host's readiness probe. Invalid security configuration remains an operator error, not permission to bypass credentials or TLS.
- Monitor hit/miss/refill latency, cache bypasses, invalidation failures, generation mismatches, rate allows/denies/store failures, local degraded fallback, memory/key cardinality, evictions/OOM, script latency and reconnection. Never log raw identifiers, cache payloads or credentials.
- Bound admission resource use before bucket creation: require a deployment-approved maximum Redis memory/key-cardinality budget derived from measured bucket size, longest idle TTL and maximum API instance/rollout count. Apply an aggregate host/ingress admission guard independent of per-subject Redis keys and bound new-subject creation. Refuse new allocations and follow the store-unavailable policy when that budget is exhausted; do not rely on HMAC or monitoring to constrain cardinality, and do not claim a racy key-count check is an atomic fleet-wide cap. The final cap/reservation mechanism and numerical sizing are an explicit production-readiness requirement, not a validated property of these diagrams. Address churn can still deny sensitive routes under the selected fail-closed policy; that residual availability trade-off requires approval.
- Keep scripts bounded: fixed operation count, bounded key/argument lengths and at most 64 KiB cache payloads; no key scans, dynamic user scripts or unbounded loops. Application deadlines do not cancel server-side execution. Disable disconnected-command backlog, bound client in-flight admission work and use a per-role circuit breaker (candidate: five consecutive failures opens for one second, one half-open probe). BUSY follows store-unavailable handling; request handlers never kill scripts or restart Redis. Operators investigate slow scripts. Numerical client concurrency and new-subject budgets must be load-tested with the instance count before production. A timed-out deduction may finish later; it must not cause an automatic duplicate execution.
- Keep one approved active policy version consistent across replicas during rollout; changing policy/key versions resets buckets and must be treated as an explicit controlled reset, not an unnoticed rolling-deployment side effect.

The owner subsequently selected MongoDB for feature flags/general configuration including cache/rate policies. Its validated snapshot publication, local last-known-good behavior and controlled activation are defined in [MongoDB design](mongodb-design.md). Requests do not require a Redis cache hit to obtain Redis policies. A MongoDB config revision is not automatically a new bucket epoch, and a missing/stale policy follows the configuration outage rules rather than silently selecting permissive limits.

## 5. Acceptance Evidence Required Before Implementation Delivery

1. Two API instances share bucket capacity under concurrent traffic; expiry/rejection/clock rounding and restart/failover behavior match the selected policy.
2. Forged headers/JWTs cannot choose another quota subject; reset responses do not differ by account existence. Raw identifiers never enter keys/logs.
3. Simulated cache pressure cannot evict limiter counters because resource domains are isolated; noeviction/OOM follows outage policy.
4. Cache values contain only the approved public fields. Disabled shop/product/SKU/child visibility and fresh price/stock checks still come from PostgreSQL on every eligible request.
5. A paused stale reader cannot fill a superseded generation. Generation eviction cannot revive an old namespace. Failed invalidation, clock anomalies and restored generations follow the freshness/skew and bypass policy; no unconditional wall-clock-independent ceiling is claimed.
6. Cache/limiter outages and timeouts produce the selected fallback/503 behavior, with no duplicate order, provider charge, stock or budget effect. Valid signed webhooks continue without Redis.
7. Cold-cache load demonstrates bounded refill concurrency, payload/cardinality limits and tolerable PostgreSQL load across the expected instance count.
8. Updated endpoint specifications explicitly define 429/503 envelopes/business codes and headers before API implementation/publication; no new business code is invented by this architecture proposal.

No runtime Redis tests, load tests, security exploit tests or backend builds have been performed for this documentation-only draft. Source review and diagram checks cannot establish those operational properties.

## 6. Diagram Changes and Decision Requested

- Architecture: two **PROPOSED** Redis roles with separate eviction domains, Infrastructure access, cache fallback and distributed-limit behavior. Expiry/completion responsibilities remain explicit in notes; the revised logical view uses native layer/child decomposition rather than flattening responsibilities to meet the earlier nine-node budget.
- Repository: proposed middleware/ports/adapters/tests are identified as proposed paths within existing layers; current source/project references remain factual.
- System: Redis is an admission/cache boundary around the existing order lifecycle. It adds no order state, does not join PostgreSQL transactions, and invalidation happens after commit.

**Approve or revise the two-role isolation, projection/freshness scope, rate table and fail-open/fail-closed choices above.** In particular, sensitive routes return 503 during limiter-store failure, while read routes use explicitly local degraded limits and signed webhooks bypass Redis. Approval must be recorded in this document before downstream implementation. The existing diagram task retains delivery none; no commit, push or PR is implied.
