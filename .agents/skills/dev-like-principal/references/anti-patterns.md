---
name: Principal Anti-patterns
description: Catalogue of over-engineering, under-engineering, architecture, process and communication anti-patterns with the signal that reveals each and the better move. Read when judging whether a design or change is over- or under-built, or during a review.
---

# Anti-patterns

Both directions fail. Over-engineering spends today's time on imaginary futures; under-engineering ships today's failure modes to production. Each entry: **signal → better move**.

## Over-engineering

- **Microservices for a small team** — 3 developers, one product, services deployed together → a modular monolith with enforced module boundaries; extract later along a proven seam.
- **Interface for every class** — `IOrderService` with one implementation and no test using a substitute → use the concrete class; extract an interface when a second implementation or a real seam appears.
- **Repository over EF Core that re-exposes `IQueryable`** — a generic `IRepository<T>` wrapping `DbSet<T>` adds nothing → use `DbContext` directly or a repository with intention-revealing methods per aggregate.
- **Mediator/CQRS/event sourcing by default** — pipeline ceremony for CRUD → plain handlers or services; adopt CQRS read models when read and write needs measurably diverge.
- **Speculative configurability** — options, plug-ins, strategy registries nobody asked for → hard-code the one behavior; make it easy to change later.
- **Premature caching / sharding / queues** — no measurement of the problem they solve → measure first; fix query shape and indexes first.
- **Shared "Common" library holding business logic** — every service must upgrade in lock-step → keep shared libraries technical, small and versioned.
- **Rewrite instead of refactor** — "the old code is bad" without a list of concrete failures → strangler-fig: replace one slice at a time behind the existing interface.

## Under-engineering

- **Happy-path only** — no timeouts, no handling of duplicates, partial failure or invalid input.
- **External call inside a DB transaction** — locks held during network I/O; inconsistent state when one side fails → outbox or saga.
- **Check-then-insert without a constraint** — race creates duplicates → unique constraint plus handling of the violation.
- **Breaking change shipped in place** — renamed field, tightened validation, migration that drops a column the old version still reads → expand/migrate/contract with versioning.
- **Swallowed exceptions / log-and-continue** in money or data paths.
- **Floating-point money, local time storage, culture-dependent parsing.**
- **No observability** — a new integration with no metrics, no correlation ID, no alert.
- **Security by obscurity** — hidden endpoints, client-side authorization, custom crypto or token formats.

## Architecture

- **Distributed monolith** — services that share a database or must deploy together.
- **Chatty synchronous chains** — a request fans through 4 services in series; availability is the product of all of them.
- **Data ownership blur** — two services write the same table.
- **Technology chosen for the CV** — new database or framework with no problem the current stack cannot solve.
- **Vendor abstraction for a vendor you will never leave** — or the reverse, deep lock-in to a vendor you are likely to leave, unexamined.

## Process and communication

- **Solution before problem** — proposing Kafka before knowing message volume or consistency needs.
- **Opinion stated as fact** — no labelled assumptions, no evidence.
- **"Works on my machine" claims** — "should work", "tested" without the command and result.
- **Nit-heavy reviews** — twenty style comments hide the one data-loss bug.
- **Silent scope creep** — refactoring unrelated code inside a feature change.
- **Undocumented one-way decisions** — the next team cannot tell why the schema looks like this.
