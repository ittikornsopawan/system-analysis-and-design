---
name: Backend Verification and Test-First Workflow
description: Select observable test seams and real DB/API evidence for backend changes, with test-first cycles and a self-contained worked example. Read when planning tests, implementing a slice or deciding whether a backend change is verified.
---

# Test the claim at its observable boundary

Derive expected outcomes from the approved spec, a worked example or an independent fixture, not by copying the implementation's calculation into the assertion. Before writing tests, list the public seams under test and what they catch/miss; require owner confirmation when that boundary is not already agreed in the approved spec/test plan. Use the four-part question format from the spec/clarification reference for unresolved choices.

| Changed guarantee | Required evidence | What a fake/unit test alone cannot establish |
| --- | --- | --- |
| Pure business decision, value invariant or state transition | Behavior tests through its public operation with independently derived expected values | Database persistence, cross-request atomicity or HTTP mapping |
| Use-case orchestration and boundary failure handling | Public use-case tests; controlled substitutes only at system boundaries such as email, time or provider APIs | Real SQL, cryptography or framework security behavior |
| SQL predicates/mappings, constraints or affected-row outcomes | Integration tests against the actual configured database engine/dialect and relevant schema | Query validity and persisted outcomes from an in-memory repository |
| Commit/rollback and retained effects | Real DB tests covering the approved durable outcome of each changed success/error branch | A fake UnitOfWork invoking a delegate or a returned Result type |
| Locking, single-use or stock/uniqueness races | Independent connections/transactions exercising competing requests and observing the approved persisted result | Parallel callbacks over one connection or repeated mutation of one in-memory object |
| HTTP serialization, validation, status/bizCode, auth/authz | Requests through the relevant real framework pipeline, in-process where appropriate, with representative valid/invalid principals and required adapter evidence | Direct handler/controller calls bypassing middleware or fake token strings |
| Cryptography, session invalidation or external integration | Tests of the actual affected adapter/configuration and required endpoint behavior; controlled provider sandbox when applicable | Fake hash/token generators or asserting an internal method was called |

Use the project's existing test tools first. Discover DB/runtime/test commands and prerequisites from its configuration; do not substitute SQLite for a PostgreSQL guarantee or install a new test framework/dependency outside approved scope. Use isolated test databases, deterministic fixtures, independent connections where required and cleanup owned by the test. Do not use production data or shared environments to manufacture evidence.

Prefer observable interfaces to private methods, call-count assertions or unapproved side channels. If persistence itself is the agreed seam, integration assertions may inspect that adapter's declared read/write outcomes; say explicitly what is being verified. Time/randomness/provider boundaries may be controlled without claiming to have tested the real provider. Do not invent a coverage percentage, benchmark target or load-test requirement.

## One red-to-green slice

1. Select one affected criterion and its agreed seam; name the example and expected outcome.
2. Write the smallest relevant test and run it against the pre-fix/pre-feature behavior. Record the expected behavioral failure. A missing SDK, syntax error or unavailable database is an environment/build failure, not the behavioral red evidence.
3. Implement only enough of that behavior to make the test pass while preserving the approved contract and architecture.
4. Rerun that test and the related regression tests. Add the next independent edge/failure case as the next slice.
5. Keep requested behavior-preserving refactors outside feature/fix red-green cycles: prove the existing baseline, change structure, then prove the same observables. Do not bulk-write every test before learning from any implementation.

For bug fixes, the reproducer must fail before the fix and pass after it. For SQL/HTTP guarantees, red/green evidence belongs at the real relevant boundary, not only in a mocked handler test.

## Self-contained worked example

These fixture requirements illustrate evidence design; they do not approve a new production endpoint:

- A stock store starts with 5 available units. Reserving a positive quantity of 3 succeeds and leaves 2.
- Reserving 6 is rejected and leaves 5.
- Two competing reservations of 4 against the same initial stock produce one success and one rejection, leaving 1.
- A transaction interrupted before its required commit leaves the approved pre-transaction state; if a different branch explicitly retains an audit write on rejection, test that retained effect separately.

Proposed seams: the business operation validates allowed quantities; the public use case exposes success/rejection; the persistence adapter's agreed reserve/read interface proves actual atomic stock changes. Confirm undecided seams before writing tests. Expected values above are fixed from the fixture requirements.

| Slice | Initial behavioral test | Minimal implementation direction | Additional evidence |
| --- | --- | --- | --- |
| Positive reservation | Reserve 3 from 5; expect success and 2 available | Coordinate the approved rule and persistence operation | Verify real SQL/result mapping if storage changes |
| Insufficient stock | Reserve 6 from 5; expect rejection and unchanged stock | Handle the conditional-write no-row outcome | Real persisted state via the agreed read boundary |
| Concurrency | Two independent requests reserve 4 from 5; expect exactly one winner and final stock 1 | Use the approved atomic condition/lock and inspect affected rows | Real competing DB transactions, not in-memory tasks |
| Interrupted write | Interrupt the approved transaction before commit; expect the specified durable state | Preserve correct transaction lifetime and cancellation/error handling | Actual DB rollback/retained-effect assertions |

An illustrative conditional update could bind `quantity` and `id` as parameters and require `available >= quantity` in the write. A preceding application count alone cannot establish the concurrent guarantee. Follow the real project's approved SQL and transaction design; the skill introduces no table, isolation level or new UnitOfWork API.

## Required result record

Record the relevant baseline and each claimed red/green or before/after result, commands, environment and exact remaining gaps. Run configured build/type/lint/static checks and the tests implied by the final scope, not just the one happy-path test. A tool that cannot start has not validated the artifact; identify equivalent-check coverage and what remains unverified. Required DB/API evidence unavailable means that guarantee remains unverified and its completion gate stays open.

Preserve examples of failures that exposed a skill gap, fix the guidance and replay the scenario. Report genuine regressions separately from pre-existing unrelated failures; neither is a reason to silently weaken the approved requirement.
