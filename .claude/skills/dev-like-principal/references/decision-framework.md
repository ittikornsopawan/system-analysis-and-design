---
name: Principal Decision Framework
description: How to frame, compare and record technical decisions and technology choices, with trade-off axes, reversibility, a comparison table shape and technology-selection criteria. Read when choosing between designs or technologies, or writing an ADR.
---

# Decision framework

## 1. Frame before you compare

Write these down first; most bad decisions come from a mis-framed problem.

- **Problem** — the outcome needed, in business terms. "Checkout times out under Black Friday load", not "we need Kafka".
- **Context** — facts with sources (code, metrics, contracts), labelled assumptions, hard constraints (law, deadline, budget, existing contracts), soft preferences.
- **Drivers** — the 2–4 qualities that actually decide this case (e.g. correctness of money, time-to-market, operability by a small team). Not every "-ility" matters every time.
- **Reversibility** — one-way door (public API, schema, data format, service split, vendor) or two-way door (internal structure, a library behind an adapter you already have)?

## 2. Generate real options

- Always include **"do nothing / do less"** and **"the simplest change inside the current architecture"**. They are often the winner and they calibrate the others.
- Include the option the requester asked for, evaluated honestly.
- Do not list straw men to make the favourite look good.

## 3. Compare on the axes that matter

| Axis | Questions |
| --- | --- |
| Complexity | New moving parts, concepts and failure modes? Can a new team member understand it in a day? |
| Cost | Build effort, run cost, licence, operations and on-call load, cost of leaving later |
| Performance | Latency and throughput against the *actual* requirement, with numbers |
| Scalability | Where is the next bottleneck and at what load? Does growth need code change or config? |
| Maintainability | Coupling, testability, how many places a typical change touches |
| Reliability | Failure modes added or removed; blast radius; recovery |
| Security / privacy | New trust boundaries, data exposure, privilege |
| Compatibility | Breaking changes, migration effort for callers and data |
| Team fit | Skills the team has, hiring, ownership boundaries (Conway's law) |
| Time to value | When does the business get something useful? Can it ship incrementally? |

Present as a table: options as columns, only the decisive axes as rows, short concrete cells ("+1 broker cluster to operate", "p99 unchanged at 120 ms"), not "good/bad".

## 4. Decide and record

State the decision, the rationale tied to the drivers, and the **consequences** — including what gets worse. Name a **revisit trigger**: the signal that would make you choose differently ("revisit if order volume exceeds 200/s or a second team starts owning fulfilment").

Then state **verification**: how you will know the decision was right (a load test, an error-rate metric after rollout, a spike result).

Write an ADR (`assets/adr.md.tmpl`, or the repo's own ADR format) when the decision is a one-way door, crosses teams, or will be questioned later. Keep it to one page. An ADR is immutable once accepted: change direction with a new ADR that supersedes it.

## Technology selection

Choose for the context, not the trend. For each candidate check:

- **Problem fit** — does it solve a problem we actually have that the current stack cannot solve reasonably? If the current stack can, the new technology must clear a high bar.
- **Maturity** — production use at similar scale, release cadence, stability of APIs, security response history, licence (and licence changes).
- **Ecosystem** — client libraries for our stack (e.g. first-class .NET support), docs, community, managed offerings.
- **Operability** — who runs it, monitors it, upgrades it, restores it at 3 a.m.? Does the team have that skill?
- **Total cost** — licence, infrastructure, people, training, migration in and out.
- **Lock-in** — how hard to leave? Isolate vendor-specific APIs behind a boundary only if leaving is a realistic scenario; otherwise accept the lock-in knowingly and say so.
- **Reversibility** — can we try it behind a flag or in one bounded context first?

Say explicitly what **not** to use and why, e.g. "Not a message broker yet: a transactional outbox table polled by a background worker gives the same reliability with zero new infrastructure at our volume."

### Typical calibrations (adjust to the evidence)

- Small team, one product, moderate load → **modular monolith** with clear module boundaries beats microservices. Split a module out when it has a different scaling profile, release cadence, or owning team — not before.
- Need reliable async side effects → **transactional outbox** before a distributed transaction or "publish then commit".
- Read performance → **indexes and query shape** before caches; caches before read replicas; replicas before CQRS with separate stores.
- Relational data with integrity rules → **a relational database** (PostgreSQL / SQL Server) before NoSQL.
- ORM vs micro-ORM in .NET → follow what the project uses; EF Core for rich domain write models and migrations, Dapper for hand-tuned read paths. Mixing both is fine when the boundary is explicit.
