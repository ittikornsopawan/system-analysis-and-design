---
name: Principal Technical Review Checklist
description: Severity-ordered checklist and finding format for reviewing code, pull requests and designs beyond syntax and style — correctness, compatibility, reliability, security, performance, operability, design fit and tests. Read when reviewing code, a PR or a design.
---

# Technical review checklist

## How to review

1. **Understand intent first.** Read the ticket/spec and the PR description. What is this change supposed to do, and what must it not change?
2. **Read the connected code**, not only the diff: callers, the transaction around it, configuration, migrations, tests.
3. **Hunt for failures, not style.** For each finding, write the concrete scenario that breaks ("two requests with the same key at the same time both insert"), not a vague concern.
4. **Rank by severity** and keep nits clearly separate so they do not drown blockers.
5. **Acknowledge what is good** in one or two lines, so the author knows what to keep.
6. **State what you did not check** (e.g. "did not run the tests", "load not measured").

## Severity

| Severity | Meaning |
| --- | --- |
| Blocker | Data loss or corruption, security hole, money error, breaking a public contract, production outage risk. Must fix before merge. |
| Major | Incorrect behavior in a realistic case, missing failure handling, serious performance issue, untestable or misplaced design that will spread. Should fix before merge. |
| Minor | Maintainability or clarity issue with a cheap fix; low-risk edge case. |
| Nit | Style or preference. Optional. Prefer letting analyzers/formatters handle these. |

## Finding format

```text
[Severity] file:line — one-sentence problem
Scenario: concrete inputs/state → wrong outcome
Fix: the smallest change that removes it (code sketch if useful)
```

## Checklist

### Correctness

- [ ] Does it do what the spec says, including the error branches?
- [ ] Null/empty/boundary values, time zones (UTC), rounding and currency (`decimal`, never `double` for money)
- [ ] Concurrency: check-then-act races, lost updates, missing unique constraints or row versions
- [ ] Transactions: correct scope; nothing external (HTTP, email, message publish) inside; partial failure handled
- [ ] Idempotency for retried operations (payments, webhooks, message handlers)

### Compatibility

- [ ] Public API: removed/renamed fields, changed types, stricter validation, changed status codes or semantics?
- [ ] Database migration safe with old and new code running together; reversible or flagged; no long locks
- [ ] Message/event schema changes tolerated by existing consumers

### Reliability

- [ ] Timeouts and cancellation on every I/O; retries only where idempotent; no retry storms
- [ ] Resource lifetimes: `HttpClient` via factory, `DbContext` scoped, disposables disposed
- [ ] Errors: no swallowed exceptions; expected failures mapped; unexpected logged once with context

### Security

- [ ] Authorization at resource level (ownership/tenant), not only authentication
- [ ] Parameterized queries; validated, size-limited input; encoded output
- [ ] No secrets or personal data in code, logs, URLs or error responses
- [ ] Least privilege for new credentials, scopes, roles

### Performance

- [ ] N+1 queries, missing indexes for new filters/joins, unbounded lists, `ToList()` before filtering
- [ ] Sync-over-async, large allocations in hot paths, chatty remote calls in loops
- [ ] Claims of "faster" backed by a measurement

### Operability

- [ ] Logs/metrics/traces sufficient to diagnose this change in production
- [ ] Feature flag or rollback path for risky behavior changes
- [ ] Config added with validation and documented defaults

### Design fit

- [ ] Follows the project's layering and conventions; logic in the layer that owns it
- [ ] No speculative abstraction, unused extension points or patterns without a present need
- [ ] No duplication of an existing helper/service (checked against the project's Function Book and code); no new dependency for a few lines
- [ ] New or changed shared functions are recorded in the Function Book in the same change
- [ ] Code quality standards met (`code-quality-standards.md`): visible formatting, short single-purpose functions, intent-explaining comments, one domain responsibility per class
- [ ] Naming reflects the domain

### Tests

- [ ] Tests prove the behavior and the main failure cases at the right level (real DB for SQL/constraints)
- [ ] A bug fix has a regression test that failed before the fix
- [ ] Tests are deterministic (no real clock, random, network or ordering dependencies)

## Design review additions

For a design document instead of code, also check: the problem and constraints are stated with numbers; at least two options were considered; trade-offs and consequences are explicit; failure modes, migration and rollback are planned; ownership and cross-team impact are named; there is a verification plan.
