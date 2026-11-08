---
name: Redis Architecture Independent Security Review
description: Consult this source-based review when revising the Redis diagram proposal or approving its policy decisions before implementation.
status: draft
approved_by: null
approved_at: null
---

# Redis architecture review

Reviewed 2026-11-07: [design](redis-design.md), [research](redis-research.md), repository/global/Markdown rules and the security-auditor role. This is a documentation assessment, not implementation verification, policy approval or security certification. Findings below are design gaps or deductions, not demonstrated runtime vulnerabilities.

## Concrete design gaps

1. **Addressed at design level; originally medium, high confidence — bucket expiry under backward clocks (§3).** The revised draft now includes `futureLead = max(0, storedTimestamp-serverNow)` in both idle expiry and rejected-request delay. This fixes the documented early-burst scenario: with capacity five, one token/second, empty timestamp 100 and server time 90, a six-second TTL would recreate capacity before refill starts. The revised minimum is sixteen seconds. Checked the revised formulas and preserved later timestamp; no runtime proof is available. Redis expiry remains wall-clock dependent. [Redis EXPIRE](https://redis.io/docs/latest/commands/expire/)

2. **Medium; high confidence — freshness ceiling needs clock assumptions (§2).** Starting TTL at database-read start prevents slow-fill extension under stable clocks, but Redis TTL alone does not establish an unconditional 60/300-second elapsed-time ceiling. A backward clock step after filling can prolong retention. **Smallest fix:** explicitly condition the ceiling on a bounded clock-skew/time-synchronization envelope, specify skew monitoring and cache bypass during detected time anomalies, and test the selected failover topology. Random generation replacement and compare-before-read/fill correctly address ordinary invalidation races; they do not provide clock independence. [Redis expiration clock behavior](https://redis.io/docs/latest/commands/expire/)

3. **Medium; medium confidence — key-cardinality availability exposure (§§3–4).** HMAC conceals identity but does not bound distinct identities. Rotating addresses can create many buckets; `noeviction` then turns memory pressure into sensitive-route 503s under the proposed policy. Monitoring detects pressure without defining prevention. **Smallest fix:** specify a measured cardinality/memory budget, upstream aggregate request protection and an overload response; load-test address churn without weakening authoritative account rules. This is a threat-model gap, not a claim that the candidate quotas are insufficient.

4. **Low; high confidence — operation deadlines are not script cancellation (§3).** The proposed 100ms attempt budget can stop application waiting while a script continues blocking Redis. **Smallest fix:** define bounded script commands/input sizes, backlog/circuit behavior, and operator handling for BUSY/NOSCRIPT. The revision now permits reload after definite NOSCRIPT and retains the ban on blind retry after ambiguous execution; backlog/circuit handling remains unspecified. Redis scripts block other clients; a script that has written cannot be interrupted with SCRIPT KILL. [Redis scripting](https://redis.io/docs/latest/develop/programmability/eval-intro/)

## Recommendations and accepted boundaries

- **Defense in depth; medium confidence:** make canonical identities a versioned typed tuple; normalize IPv4-mapped addresses, configure the actual trusted proxy chain/hop limit, and run forwarded-header processing before IP admission. The draft already rejects arbitrary forwarded headers and unvalidated principals. [Microsoft proxy guidance](https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/proxy-load-balancer?view=aspnetcore-10.0)
- Bind webhook exemption to the exact endpoint, preserving raw-body signature validation and independent body/concurrency limits; exemptions must never depend on caller-supplied identity. The revised host-startup/readiness independence closes the indirect Redis outage dependency at design level. PostgreSQL idempotency and visibility/price/stock gates remain appropriate authorities.
- Acknowledged-write loss, per-process fallback scope and separate eviction domains are accurately qualified. A promoted replica can also restore an older cache generation; generation guards alone do not prevent that. [Redis replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)

## Decisions and unperformed checks

Owner approval remains necessary for quotas/bursts, NAT impact, clock/failover tolerance, freshness allowances, local fallback and sensitive-route unavailability. These settings are proposals, not facts established by external sources. No Lua execution, proxy configuration inspection, failover/clock simulation, memory exhaustion, webhook exploit test, backend build or load test was performed. Those checks remain required before implementation delivery.

## Primary-Agent Remediation Note After Independent Review

Added by the primary designer on 2026-11-07; this is not a second independent review. The proposal now conditions freshness on clock health, adds source-time checks and cache bypass during clock anomalies and failover/reconnect windows. It explicitly separates client waiting deadlines from server execution, bounds Lua operations/inputs and specifies backlog, circuit, BUSY and definite-NOSCRIPT handling. Cardinality/memory sizing and upstream aggregate protection are explicit production-readiness requirements; no numeric global budget or address-churn availability proof is claimed. Residual sensitive-route 503 exposure under exhaustion remains documented. These changes address documentation gaps; runtime clock, failover, timeout and load verification remains unperformed. MongoDB now owns validated policy snapshots per [MongoDB design](mongodb-design.md); policy revision alone must not reset Redis buckets.
