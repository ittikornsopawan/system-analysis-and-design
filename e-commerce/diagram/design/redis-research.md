---
name: Redis Architecture Research
description: Evidence and design recommendations to consult when reviewing the proposed e-commerce Redis cache and distributed rate-limiting diagrams before implementation.
---

# Redis architecture research

Research date: 2026-11-07. This note supports the proposed diagram revision; it does not approve backend implementation, quotas, expiry periods, or failure policies. Recommendations and deductions below are explicitly distinguished from documented behavior.

## Fit with the current backend

The inspected [backend architecture](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/project-structure.md) uses controllers, a custom CQRS dispatcher, inner interfaces and Infrastructure adapters; [shared build settings](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/Directory.Build.props) target .NET 10. **Recommendation:** retain those boundaries: admission middleware calls a limiter adapter; eligible query handlers use an application cache port implemented in Infrastructure. PostgreSQL remains authoritative. Label Redis components **proposed** rather than implying existing implementation.

## Shared admission control

ASP.NET Core's built-in limiter stores counters in each app instance. Even its global limiter is global only within that instance. Microsoft identifies a shared gateway or a custom limiter with shared counters as alternatives for one limit across replicas. Adding `IDistributedCache` alone does not replace those counters. **Recommendation:** depict API replicas calling the same Redis admission operation, with any local concurrency limiter shown separately. [Microsoft rate limiting](https://learn.microsoft.com/en-us/aspnet/core/performance/rate-limit?view=aspnetcore-10.0#rate-limiting-with-multiple-app-instances)

Redis documents token buckets for bounded bursts and average admission rates. Its .NET example reads and updates a hash atomically through Lua, but its primary token-bucket sample accepts application time and omits expiry. **Recommendation:** treat that sample as an algorithm reference, not a complete production contract. Specify partition identity, capacity, refill rate, request cost, retry metadata and cleanup before implementation; do not copy illustrative quotas. [Redis .NET limiter](https://redis.io/docs/latest/develop/use-cases/rate-limiter/dotnet/)

**Proposed operation:** one short Lua script reads server `TIME`, reads bucket state, refills up to capacity, decides admission, deducts only an admitted request, updates state and sets idle expiry. Redis guarantees script execution without interleaving, while blocking other server activity during execution; keep work bounded and handle missing script caches after restart/failover. `TIME` supplies server time, avoiding dependence on disagreeing application clocks. [Lua execution](https://redis.io/docs/latest/develop/programmability/eval-intro/), [TIME](https://redis.io/docs/latest/commands/time/)

**Deduction:** removing a depleted bucket early recreates full capacity and admits an unintended burst. Set idle cleanup no earlier than the time when that bucket would naturally be full, using the selected refill algorithm; verify boundary rounding and clock movement. `EXPIRE` deletes a key when its timeout elapses. **Recommendation:** bound identity cardinality and normalize trusted partition inputs; test rejected traffic, expiry, backward clocks and many unique callers. [EXPIRE](https://redis.io/docs/latest/commands/expire/), [token-bucket initialization/refill](https://redis.io/docs/latest/develop/use-cases/rate-limiter/dotnet/)

## Safe caching and freshness

Cache-aside checks Redis, reads PostgreSQL on a miss, then fills Redis. Microsoft recommends updating the data store before invalidating cached data and notes that cache-aside does not guarantee consistency. **Recommendation:** cache only allowlisted public read DTOs such as category/brand labels or public product descriptions. Exclude authoritative stock, checkout prices, permission decisions, credentials/tokens, sessions and PII from this proposal. Each eligible DTO needs an explicit staleness allowance. [Microsoft cache-aside](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside)

**Race deduction:** reader A misses and reads an old database snapshot; writer B commits a change and invalidates the key; A subsequently fills the old value. Commit-then-delete alone therefore does not prevent stale refill. A failed invalidation after commit is another stale-data path. **Recommendation:** bounded TTL is a freshness backstop, not immediate consistency. If stronger freshness is required, design version-guarded refill and reliable invalidation together, or bypass caching for that DTO. Single-flight alone cannot fix this race. This deduction follows the documented read/fill and update/invalidate steps. [Cache-aside operations and consistency](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside)

Keys must identify all response dimensions, including shop/tenant, language, filters, sorting, pagination and DTO version where relevant. Microsoft warns about untrusted cache-key inputs. **Recommendation:** canonicalize and bound key space, payload size and TTL; use expiry jitter and bounded database refill concurrency to spread misses. `HybridCache` offers same-key single-flight within one instance, but coordination does not extend to other instances sharing Redis. Do not depict it as a fleet-wide lock. [HybridCache keys and coordination](https://learn.microsoft.com/en-us/aspnet/core/performance/caching/hybrid?view=aspnetcore-10.0)

## Isolation, failures and connections

Redis eviction is controlled by `maxmemory` and its policy. `allkeys-*` can remove any key; `volatile-*` can remove expiring limiter keys too. `noeviction` rejects memory-growing writes rather than guaranteeing availability. **Recommendation:** isolate disposable cache and limiter workloads in separately provisioned Redis processes/services with independent memory, eviction and credentials. [Eviction policies](https://redis.io/docs/latest/develop/reference/eviction/)

Logical database numbers are namespacing, share persistence, and Redis Cluster supports only database zero. **Deduction:** neither prefixes nor `SELECT` database numbers create independent process memory or eviction budgets. Distinguish these logical namespaces from separately provisioned managed-service databases when drawing deployment boundaries. Leave operational memory headroom and monitor evictions, rejected writes and limiter key growth. [SELECT](https://redis.io/docs/latest/commands/select/), [memory and eviction](https://redis.io/docs/latest/develop/reference/eviction/)

**Proposed failure policy for review:** disposable cache reads/writes fail through to PostgreSQL under short time budgets, with bounded fallback concurrency. For sensitive throttles, failing closed preserves admission protection while denying legitimate traffic during Redis outages; failing open preserves access while weakening protection. These are business/security choices requiring explicit endpoint policy, not Redis guarantees. A limiter-store failure must be distinguishable from an actual quota rejection. [Cache resilience considerations](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside), [limiter policy context](https://learn.microsoft.com/en-us/aspnet/core/performance/rate-limit?view=aspnetcore-10.0)

Replication is asynchronous; even `WAIT` does not make Redis strongly consistent or eliminate acknowledged-write loss on failover. **Deduction:** a promoted replica can lose recent token deductions and admit additional traffic; cache invalidations can also be lost. Fail-closed handling during disconnection cannot alone prevent post-failover undercount. Test the chosen topology and document its accepted admission/freshness envelope. [Redis replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)

StackExchange.Redis's `ConnectionMultiplexer` is thread-safe and intended for reuse rather than creation per operation. **Recommendation:** use an application-lifetime connection owner per distinct Redis service/configuration; expose ports rather than clients to inner layers. Keep services private, require TLS and least-privilege ACLs, and exclude raw identifiers or credentials from keys/logs. [Client lifetime](https://stackexchange.github.io/StackExchange.Redis/Basics.html), [Redis security](https://redis.io/docs/latest/operate/oss_and_stack/management/security/)

## Extras and explicit deferrals

**Optional later extensions:** shared output caching for reviewed anonymous read endpoints, and best-effort public cache invalidation hints. ASP.NET output caching defaults exclude authenticated and cookie-setting responses; configure it deliberately rather than caching every controller result. Pub/Sub is at-most-once and loses messages during subscriber disconnection, so hints need TTL/refetch backstops. [Output caching](https://learn.microsoft.com/en-us/aspnet/core/performance/caching/output?view=aspnetcore-10.0), [Pub/Sub delivery](https://redis.io/docs/latest/develop/pubsub/#delivery-semantics)

**Defer:** Redis business locks, authoritative session/revocation state, durable idempotency truth and order/payment workflow ownership. Redis's lock documentation explains why asynchronous replica promotion can break mutual exclusion. Keep existing database transactions and constraints authoritative; any future responsibility transfer needs separate failure/recovery design and approval. [Distributed-lock failure model](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)

## Source ledger

All external sources were consulted on the research date; links above are the claim-level references.

| Owner | Primary sources | Used for |
| --- | --- | --- |
| Microsoft Learn | [Rate limiting](https://learn.microsoft.com/en-us/aspnet/core/performance/rate-limit?view=aspnetcore-10.0); [Cache-Aside](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside) | Instance scope, shared-store alternative, cache flow and consistency |
| Microsoft Learn | [HybridCache](https://learn.microsoft.com/en-us/aspnet/core/performance/caching/hybrid?view=aspnetcore-10.0); [Output caching](https://learn.microsoft.com/en-us/aspnet/core/performance/caching/output?view=aspnetcore-10.0) | Single-flight boundary, key design, public-response guardrails |
| Redis | [.NET limiter](https://redis.io/docs/latest/develop/use-cases/rate-limiter/dotnet/); [Lua](https://redis.io/docs/latest/develop/programmability/eval-intro/); [TIME](https://redis.io/docs/latest/commands/time/); [EXPIRE](https://redis.io/docs/latest/commands/expire/) | Token-bucket model, atomicity, server clock, cleanup |
| Redis | [Eviction](https://redis.io/docs/latest/develop/reference/eviction/); [SELECT](https://redis.io/docs/latest/commands/select/) | Memory policies versus logical namespacing |
| Redis | [Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/); [Distributed locks](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/) | Failover write-loss and mutual-exclusion limits |
| Redis | [Security](https://redis.io/docs/latest/operate/oss_and_stack/management/security/); [Pub/Sub](https://redis.io/docs/latest/develop/pubsub/) | Private access, ACL/TLS, at-most-once invalidation hints |
| StackExchange.Redis | [Basic Usage](https://stackexchange.github.io/StackExchange.Redis/Basics.html) | Multiplexer reuse and thread safety |

## Review risks and next decisions

Approve eligible DTOs and freshness budgets; partition identity and abuse cases; cache/limiter resource isolation; endpoint-specific failure semantics; and failover tolerance before implementation. Verification should cover concurrent admission, stale refill, invalidation failure, cold-cache load, memory exhaustion and Redis failover. No backend build or runtime Redis test was run: this is documentation research, not implementation verification.
