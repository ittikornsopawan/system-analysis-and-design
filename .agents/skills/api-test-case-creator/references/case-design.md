---
name: API Test-Case Design
description: Scenario selection, observable expectations and a self-contained worked case for documented API testing. Read before deriving cases from an API spec.
---

# Design cases from obligations

Use each explicit rule, response requirement and acceptance criterion as an obligation. Map both rule-to-case and case-to-rule: an unmapped rule is a coverage gap, and an assertion without a source may be an invented requirement. Split compound rules into testable parts; success status coverage does not prove response shape, grant resolution or durable state.

## Select scenarios that reach the branch

| Spec feature | Case design |
| --- | --- |
| Required/optional inputs | Distinguish omitted, null, empty, malformed and valid values according to the spec. Keep other inputs valid when testing one validation failure. |
| Bounds, precision, time windows | Exercise just below, exactly at and just above each meaningful bound using the declared units/precision. State the clock/time zone and fixtures; preserve inclusive/exclusive predicates. |
| Authentication/authorization | Use the actual required credential/permission state. Cover relevant inactive, expired, revoked, missing, wrong-owner and permission-specific scope states. A deliberately absent permission cannot exercise an authorized business-conflict branch. |
| Business state and SQL predicates | Choose fixtures that separately satisfy/fail each material predicate, including NULL, inactive/deleted rows and matching/mismatching ownership or assignment where specified. Read actual schema/constraints before proposing impossible data. |
| Batch | Cover the specified size/duplicate/index rules, first and later failing items, result correspondence and whole-batch/partial effects. Fixture existence must survive earlier steps or be reset. |
| Inquiry/paging | Check specified filters, sort keys/tie breakers, empty results, boundaries, visibility and totals. Missing ordering or page semantics become gaps rather than invented assertions. |
| Transactions and external effects | State the expected durable effects for each branch. An error response can retain an audit write. Place failure injection at a specified point relative to commit, and separate committed effects from uncommitted writes. |
| Concurrency/idempotency | Specify actors, initial state, synchronization and observable aggregate outcomes. Identify the approved invariant and allowed response combinations without assuming a winning actor or inventing an idempotency rule. |
| Error precedence | Isolate each error with otherwise valid inputs. Add simultaneous-failure cases only where precedence is specified or needs clarification. |

Use equivalence partitions to avoid redundant cases, with a reason when one case represents several equivalent values. Different rules, result codes, data effects or failure phases need distinct expectations. Avoid an exhaustive Cartesian product unless rule interactions justify it. A category that has no governing rule can be excluded with a reason; uncertainty remains a gap, not N/A.

## Make observations executable later

Write complete method/path, required headers, principal and body/query/path values, or reference a fully defined shared fixture. Synthetic secrets/tokens are fixture labels with issuance requirements, not claims that illustrative strings authenticate. For generated IDs/tokens/timestamps, assert source-defined shape, relationships and time calculations rather than hard-coded random values. Missing response fields and explicit null values are distinct.

State HTTP status separately from status/body fields. Preserve exact specified bizCodes, field names and absence rules; label illustrative example wording separately from an exact contractual message. If the source leaves a required outcome unknown, identify that gap rather than borrowing a neighboring endpoint's code. Never infer rollback from HTTP status alone.

For DB/external effects, list relevant before/after state and the observation boundary: an approved inquiry API, authorized read-only DB inspection or an existing test adapter/trace. HTTP alone cannot prove lack of SQL, lock ordering or atomicity. An undefined observation method stays a named verification prerequisite/gap; internal assertions are not presented as already observable.

Describe setup, failure injection and cleanup without executing them during document creation. Copy SQL only when necessary, exactly from its authoritative spec with a source link; keep illustrative inspection/setup proposals labeled as proposals and outside the contract SQL. Secrets and real personal data stay outside fixtures.

## Self-contained worked example

This mini-spec and its case are teaching material, not an approved production API. An actual endpoint supplies its own rules, data model and status codes.

Mini-spec revision `example-v1`, `POST /sessions`, no authentication required:

- **R1 — Input:** body requires non-empty string `username` and `password`. Invalid input returns HTTP 400 with `status.bizCode = E_INPUT` before database work.
- **R2 — Unknown user:** valid input whose username has no account returns HTTP 401 with `status.bizCode = E_AUTH`, no `data` field and generic `status.bizMessage = Invalid credentials`. It commits exactly one attempt row with that username's identifier hash, `user_id = NULL` and `result = FAILED`; no session row is created.
- **R3 — Success:** a unique active account with a matching password returns HTTP 200 with `status.bizCode = S_SESSION` and a newly generated `data.sessionId`. Exactly one session and one SUCCESS attempt for that user commit together. A pre-commit write failure rolls back both and returns HTTP 500 with `status.bizCode` absent.

The matrix for a full suite must include separate invalid-input partitions from R1, the R2 rejection, and R3 success/atomic-failure cases. The following fully worked case covers only R2; it is not a complete suite for the mini-spec.

### TC-SESSIONS-002 — Retain the rejected attempt for an unknown username

- **Source:** mini-spec `example-v1`, R2. **Design:** Ready (illustrative source). **Execution:** Not run.
- **Purpose:** Verify the generic rejection and the durable FAILED attempt together.
- **Preconditions/data:** Isolated database; no account for `missing.case@example.test`; no session/attempt rows for this fixture. Other requests do not use this identifier. The future test environment supplies the specified identifier-hash calculation and authorized read-only DB observation. Reset this fixture before each execution.
- **Request:** no authorization header required; `Content-Type: application/json`.

```http
POST /sessions
Content-Type: application/json

{"username":"missing.case@example.test","password":"Synthetic-Password-123!"}
```

1. Verify the initial account/session/attempt state and capture the attempt count for the fixture hash.
2. Send the request once and record the HTTP response.
3. After the response, read the committed attempt/session state through the authorized observation method.

**Expected:** HTTP 401; body `status.bizCode = E_AUTH` and `status.bizMessage = Invalid credentials`; `data` is absent. The attempt count for that identifier increases from 0 to 1, with `user_id = NULL` and `result = FAILED`. Session count remains 0. The audit insert persists despite the rejection. No SQL ordering assertion is inferred from that HTTP result.

**Cleanup:** Remove only this case's attempt rows through the future authorized fixture teardown, restoring the initial state. **Actual result/evidence:** none; Not run.

### Ambiguity example

Suppose a later mini-spec paragraph instead says every HTTP error rolls back all writes. R2 and that paragraph conflict. Keep TC-SESSIONS-002's HTTP expectation linked to the unambiguous rule and mark the durable-outcome decision blocked. Do not silently choose either SQL or prose.

Use the skill's four-part question contract, for example an English topic `Retain rejected-login audit records?` with Thai explanations identifying R2 versus the rollback paragraph, their effect on persisted data, the proposed branch-specific correction and future transaction-test implications. Continue unaffected cases while waiting. The illustrative conflict is deliberate evaluation input; it does not itself prove a defect in a live project.
