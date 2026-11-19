---
name: "Logout API Test Cases"
description: "Documented scenarios and expected results for POST v1/auth/logout; use for test planning and for the automated backend tests named after each case ID."
---

# Logout API Test Cases

## Source baseline and scope

- Method/path: `POST v1/auth/logout`
- Governing sources: [spec.md](spec.md) (rules, response examples, Database Relations), [sequence.wsd](sequence.wsd) (validation order, lock, session revocation notes), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md)
- Source revision: Showcase `main` at the commit that adds this file; `spec.md` and `sequence.wsd` last changed in `8023e47`
- Source approval: approved (`approved_by: Ittikorn`, `approved_at: 2026-11-16T09:24:57+07:00`)
- Test design baseline: approved-source, except gap G1 (implementation choice recorded, pending the lead's review)
- Scope and exclusions: logout only; TLS excluded. Logout has no rate limit in its spec.
- Execution summary: Not run — automated tests in e-commerce-backend will carry the case ID in their names.

## Shared fixtures and observation prerequisites

- **Database:** throw-away PostgreSQL 17 with every Showcase migration (backend `PostgresFixture`), sessions in UTC.
- **Session S1:** `U_OK` logs in twice in S1's history: access A1 (expired but ACTIVE), access A2 (current, presented), refresh R1 (INACTIVE, rotated) and R2 (ACTIVE). **Session S2:** another device of U_OK with one ACTIVE access and refresh row. `U_OTHER` reuses session id S1 in legacy data with ACTIVE rows.
- **Valid request (VR):** `authorization: Bearer <A2 JWT>`, `timestamp: <now UTC>`, no body.
- **Observation:** HTTP response; rows of `t_user_access_token` and `t_user_refresh_token` by user and session.

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| O01 | spec Success | 200 S10000 "Logout Success", status only, no data | [TC-LOGOUT-001](#tc-logout-001--the-session-is-closed) | designed |
| O02 | spec rule; sequence revocation note | every ACTIVE access and refresh row of the presented token's session becomes INACTIVE (updated_by = user id), expired ACTIVE rows included; other sessions and other users unchanged | [TC-LOGOUT-001](#tc-logout-001--the-session-is-closed) | designed |
| O03 | sequence validation note; Fail - Bad Request | missing or invalid UTC timestamp or a non-empty body → 400 E10001 before the JWT check and before SQL | [TC-LOGOUT-002](#tc-logout-002--validation-comes-first) | designed; body message G1 |
| O04 | sequence JWT note; Fail - Unauthorized | missing, malformed or invalid JWT (signature, issuer, audience, expiry, UUID sub) → 401 E10002 "Invalid or expired access token." before a transaction | [TC-LOGOUT-003](#tc-logout-003--a-bad-jwt) | designed |
| O05 | spec rule | user not ACTIVE, stored access row missing, INACTIVE, expired or of another user → the same 401, nothing changed | [TC-LOGOUT-004](#tc-logout-004--a-revoked-or-unknown-access-token), [TC-LOGOUT-005](#tc-logout-005--user-not-active) | designed |
| O06 | sequence "Calling logout again likewise answers 401" | a second logout with the same token → 401 | [TC-LOGOUT-004](#tc-logout-004--a-revoked-or-unknown-access-token) | designed |
| O07 | sequence lock note | the user row is locked FOR UPDATE; concurrent logouts → one 200, one 401 | [TC-LOGOUT-006](#tc-logout-006--concurrent-logouts), [TC-LOGOUT-007](#tc-logout-007--the-user-row-lock) | designed |
| O08 | sequence failure branches | timeout → 408 E90001; unexpected failure → 500 without bizCode; rollback, no partial revocation | [TC-LOGOUT-007](#tc-logout-007--the-user-row-lock), [TC-LOGOUT-008](#tc-logout-008--unexpected-failure) | designed |
| O09 | spec "Derive userId only from verified JWT sub" | the user and session never come from the request; the JWT claims of roles do not matter | [TC-LOGOUT-001](#tc-logout-001--the-session-is-closed) | designed |

## Detailed test cases

### TC-LOGOUT-001 — The session is closed

- Source: O01, O02, O09. Design readiness: Ready. Execution status: Not run.

**Request:** VR. **Expected:** 200, "Ok", S10000 "Logout Success", no `data`; A1, A2 and R2 INACTIVE with updated_by = U_OK id; S2 rows still ACTIVE; U_OTHER's rows in S1 still ACTIVE; no new token row.

### TC-LOGOUT-002 — Validation comes first

- Source: O03. Design readiness: Ready (body message per G1). Execution status: Not run.

**Request:** VR without `timestamp` → "Timestamp is a required header."; with `timestamp "yesterday"` → "Timestamp must be a valid UTC timestamp."; with a JSON body `{}` → "Timestamp must be a valid UTC timestamp and the request body must be empty."; the same three without any authorization header still answer 400 (not 401). **Expected:** 400 E10001; nothing changed.

### TC-LOGOUT-003 — A bad JWT

- Source: O04. Design readiness: Ready. Execution status: Not run.

**Request:** no authorization header; `Bearer not-a-jwt`; a JWT signed with another key; an expired JWT; a JWT with `sub` "abc". **Expected:** 401 E10002 "Invalid or expired access token."; nothing changed.

### TC-LOGOUT-004 — A revoked or unknown access token

- Source: O05, O06. Design readiness: Ready. Execution status: Not run.

**Steps:** a valid JWT that has no stored row; a valid JWT whose stored row is INACTIVE; a stored row of another user with the same hash is not possible (hash is unique), so a JWT whose `sub` is another user than the row owner; VR twice. **Expected:** 401 each time (the second VR included); nothing changed by those calls.

### TC-LOGOUT-005 — User not ACTIVE

- Source: O05. Design readiness: Ready. Execution status: Not run.

**Preconditions:** U_OK LOCKED. **Expected:** 401; S1 rows still ACTIVE.

### TC-LOGOUT-006 — Concurrent logouts

- Source: O07. Design readiness: Ready. Execution status: Not run.

**Steps:** send VR twice at once. **Expected:** one 200 and one 401; S1 closed once.

### TC-LOGOUT-007 — The user row lock

- Source: O07, O08. Design readiness: Ready. Execution status: Not run.

**Steps:** a second connection holds U_OK's row `FOR UPDATE`; VR with a 1-second command timeout. **Expected:** 408 E90001; S1 rows still ACTIVE. After release → 200.

### TC-LOGOUT-008 — Unexpected failure

- Source: O08. Design readiness: Ready. Execution status: Not run.

**Steps:** a test-only wrapper throws after the access-token update. **Expected:** 500 "An unexpected error occurred.", no bizCode; every S1 row still ACTIVE (no partial revocation).

## Open gaps and decisions

| Gap ID | Conflicting/missing sources | Affected obligations/cases | Missing decision or prerequisite | Status / decision reference |
| --- | --- | --- | --- | --- |
| G1 | the spec example "Timestamp must be a valid UTC timestamp and the request body must be empty." covers both checks in one sentence; api-conventions has separate header messages | O03, TC-LOGOUT-002 | which message a non-empty body gets | implementation choice, pending the lead's review: header failures use the shared header messages; a non-empty body uses the spec example text |

## Document verification and limitations

- Every obligation O01–O09 maps to a case, and every case cites its obligation.
- No case has run yet.

## Revision and execution history

- 2026-11-19: first version (Drake), Not run.
