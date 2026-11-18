---
name: Principal Verification Guidelines
description: What evidence each kind of technical claim needs (behavior, data, concurrency, compatibility, performance, security, design) and how to report verified versus unverified results. Read before claiming a change, design or review conclusion is correct.
---

# Verification guidelines

A claim is only as strong as the evidence produced for it. Match the evidence to the claim, run it, and report the actual result.

## Evidence by claim

| Claim | Minimum evidence |
| --- | --- |
| Code compiles / no new warnings | `dotnet build` (warnings as errors where the project uses it) and analyzers |
| Business rule works | Unit test that fails without the rule and passes with it |
| SQL, constraint, transaction, locking behaves | Integration test against the real database engine (e.g. Testcontainers), not an in-memory provider |
| HTTP contract, auth, status codes | Integration test through the real pipeline (`WebApplicationFactory`) or a contract test against the published spec |
| Concurrency/idempotency safe | Test that issues concurrent or duplicate requests and asserts a single effect; plus the constraint that enforces it |
| Bug fixed | Regression test that failed before the fix (capture the red run) and passes after |
| Backward compatible | Old clients/contract tests still pass; schema diff shows only additive changes; migration runs with the old code version |
| Faster / scales | Before-and-after measurement under a stated load: benchmark (BenchmarkDotNet), query plan (`EXPLAIN ANALYZE`), or load test with p95/p99 |
| Secure | The specific threat tested (unauthorized user gets 403/404 on another user's resource; injection payload is inert); dependency scan for new packages |
| Design decision right | A verification plan with a measurable signal after rollout, a spike result, or a prototype answering the riskiest question |
| Refactor preserved behavior | Same tests green before and after; no test modified to fit the new code |

## Rules

- Run the checks the project already has (build, tests, linters, contract checkers) before adding new ones.
- A test that has never failed has not been shown to test anything; for new tests of new behavior, see it fail first or mutate the code to confirm it can fail.
- Do not weaken or skip a test to make it pass. A failing test is a code bug or a spec question.
- Fakes prove orchestration and decisions; they do not prove database or HTTP guarantees.
- For designs and reviews that produce no code, verification means: claims traced to the code/spec lines that support them, numbers sourced, and assumptions listed for confirmation.

## Reporting

Report, in this order:

1. What was run (exact commands) and the result (pass counts, timings, measured numbers).
2. What was not run or could not run, and why.
3. What therefore remains unverified, stated as a risk, not hidden.

"Should work" and "looks fine" are not results.
