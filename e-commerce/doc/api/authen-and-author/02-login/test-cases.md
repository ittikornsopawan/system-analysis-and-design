---
name: "Login API Test Cases"
description: "Documented scenarios and expected results for POST v1/auth/login; use for test planning and for the automated backend tests named after each case ID."
---

# Login API Test Cases

## Source baseline and scope

- Method/path: `POST v1/auth/login`
- Governing sources: [spec.md](spec.md) (rules, response examples, JWT payload, Database Relations), [sequence.wsd](sequence.wsd) (execution order, lock order, claim resolution notes), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md) (Error codes, Validation messages, Limits and rate limiting)
- Source revision: Showcase `main` at the commit that adds this file; `spec.md` and `sequence.wsd` last changed in `8023e47`
- Source approval: approved (`approved_by: Ittikorn`, `approved_at: 2026-11-16T09:24:57+07:00`)
- Test design baseline: approved-source
- Implementation decision: the "QUERY - Serialize identifier" advisory lock runs through one Infrastructure helper with a fixed, parameterized statement (owner decision 2026-11-18; every other query is EF Core LINQ).
- Scope and exclusions: the login endpoint only. Excluded: response-time equality of the dummy password verification (the spec requires the dummy work, not a timing bound; covered by a call-count check); the 30-day attempt clean-up job (separate system job); TLS.
- Execution summary: Not run — automated tests in e-commerce-backend will carry the case ID in their names.

## Shared fixtures and observation prerequisites

- **Database:** throw-away PostgreSQL 17 with every Showcase migration (backend `PostgresFixture`), sessions in UTC.
- **Users (created per case with unique identifiers):** `U_OK` ACTIVE with an ACTIVE PASSWORD row for `Passw0rd-Example`; variants with row_status INACTIVE, LOCKED and DELETED; `U_NOPW` ACTIVE with no ACTIVE PASSWORD row.
- **Authorization fixtures:** roles, permissions, scopes, permission-scope definitions and their assignments created per case with unique names.
- **Valid request (VR):** headers `content-type: application/json`, `timestamp: <now UTC>`, `requestId: req-<case>`; body `{"username": <U_OK username>, "password": "Passw0rd-Example"}`.
- **Observation:** HTTP response through the real pipeline; the access token decoded with the test signing key; committed rows of `authen.t_user_access_token`, `authen.t_user_refresh_token` and `authen.l_user_login_attempt` read by test queries. `identifier_hash` is SHA-256 of the exact UTF-8 username sent.
- **Failure injection:** a second connection holding the user row lock with a short command timeout (timeout), and a test-only repository wrapper that throws after the writes (unexpected failure).

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| L01 | spec Success; Data Object | 200 S10000 "Logged-in Success"; data has exactly tokenType Bearer, accessToken, refreshAccessToken, expiresIn 900 | [TC-LOGIN-001](#tc-login-001--successful-login) | designed |
| L02 | spec Example JWT Payload; sequence "Session" note | HS256 JWT with iss, sub, aud, jti, iat, exp (exp - iat = 900), user {id, username, displayName, email}, roles, permissions, scopes; no credentials | [TC-LOGIN-001](#tc-login-001--successful-login) | designed |
| L03 | sequence "Session" note; INSERT access/refresh token | one new session_id per login; one access row and one refresh row with that session; token columns hold SHA-256 hashes; access expiry now + 15 min, refresh now + 14 days; refresh token is 32 random bytes in base64url | [TC-LOGIN-001](#tc-login-001--successful-login), [TC-LOGIN-018](#tc-login-018--each-login-is-a-new-session) | designed |
| L04 | spec Fail - Bad Request; sequence validation note; Validation messages | username and password required; username ≤ 254, password ≤ 128; missing both → "Username and Password are required fields." | [TC-LOGIN-002](#tc-login-002--missing-fields), [TC-LOGIN-003](#tc-login-003--length-limits) | designed |
| L05 | sequence validation note | the registration password rule is not applied to login | [TC-LOGIN-004](#tc-login-004--no-password-complexity-at-login) | designed |
| L06 | sequence "A missing/malformed request (400) is not an authentication attempt" | a 400 writes no attempt row | [TC-LOGIN-002](#tc-login-002--missing-fields) | designed |
| L07 | spec "One answer for every failure" | unknown, ambiguous, wrong password, no ACTIVE PASSWORD row, user not ACTIVE, refused → 401 E10002 "Invalid username or password." | [TC-LOGIN-005](#tc-login-005--unknown-username) .. [TC-LOGIN-010](#tc-login-010--ambiguous-identifier), [TC-LOGIN-013](#tc-login-013--five-failures-refuse-the-sixth) | designed |
| L08 | spec Brute force; INSERT - Record attempt | every valid attempt writes one row: identifier_hash, result, user_id (NULL when unknown, ambiguous or REFUSED), created_by `system`, created_at = now after the lock | [TC-LOGIN-001](#tc-login-001--successful-login), [TC-LOGIN-005](#tc-login-005--unknown-username), [TC-LOGIN-006](#tc-login-006--wrong-password) | designed |
| L09 | sequence note "FAILED and REFUSED rows are committed although the answer is 401" | 401 still commits the attempt and writes no token row | [TC-LOGIN-006](#tc-login-006--wrong-password), [TC-LOGIN-013](#tc-login-013--five-failures-refuse-the-sixth) | designed |
| L10 | sequence validation note | identifier compared exactly (no case change, no trim); login by email works | [TC-LOGIN-011](#tc-login-011--identifier-is-compared-exactly), [TC-LOGIN-012](#tc-login-012--login-by-email-address) | designed |
| L11 | sequence "Only FAILED rows are counted" | 5 FAILED in the window → REFUSED without user lookup or password check, even with the right password; REFUSED is not counted | [TC-LOGIN-013](#tc-login-013--five-failures-refuse-the-sixth) | designed |
| L12 | sequence same note | failures older than 15 minutes do not count | [TC-LOGIN-014](#tc-login-014--old-failures-do-not-count) | designed |
| L13 | sequence advisory note | the counter is per supplied identifier (username and email are separate) | [TC-LOGIN-015](#tc-login-015--the-counter-is-per-supplied-identifier) | designed |
| L14 | sequence advisory note | concurrent attempts for one identifier are serialized: never more than 5 FAILED before refusal | [TC-LOGIN-016](#tc-login-016--concurrent-attempts-cannot-pass-a-stale-count) | designed |
| L15 | sequence claim notes 1–6 | roles: ACTIVE assignments of ACTIVE roles; permissions from ACTIVE role grants and direct grants of ACTIVE permissions; scoped grants need the exact matching ACTIVE definition and ACTIVE scope; unscoped grant only for a permission with no non-DELETED definition; names mapped (last `.` → `:`, scope `<lower code>:*`); deduplicated and sorted; empty arrays allowed | [TC-LOGIN-017](#tc-login-017--authorization-claims) | designed |
| L16 | sequence lock order note | login locks the matching user row FOR UPDATE before reading the password | [TC-LOGIN-019](#tc-login-019--login-waits-for-the-user-row-lock) | designed |
| L17 | sequence "Timeout before COMMIT" | timeout → 408 E90001; no token and no attempt row | [TC-LOGIN-019](#tc-login-019--login-waits-for-the-user-row-lock) | designed |
| L18 | sequence "Unexpected failure before COMMIT" | 500 without bizCode; nothing committed | [TC-LOGIN-020](#tc-login-020--unexpected-failure) | designed |
| L19 | spec Rate limit | 11th request in a minute from one IP → 429 E90002 with Retry-After | [TC-LOGIN-021](#tc-login-021--rate-limit) | designed |
| L20 | sequence dummy verification note | an unknown or ambiguous user or a missing password row still costs one password verification | [TC-LOGIN-005](#tc-login-005--unknown-username), [TC-LOGIN-009](#tc-login-009--no-active-password-row) | designed (call count, not timing) |

## Detailed test cases

### TC-LOGIN-001 — Successful login

- Source: L01, L02, L03, L08. Design readiness: Ready. Execution status: Not run.

**Preconditions:** `U_OK` with display name `John Doe`, one ACTIVE role `CATALOG_MANAGER` granting ACTIVE permission `catalog.manage` (unscoped). **Request:** VR with `requestId: req-TC-LOGIN-001`.

| Observation | Expected | Source |
| --- | --- | --- |
| HTTP / bizCode | 200; S10000 "Logged-in Success", message "Ok", status SUCCESS, requestId echoed | Success example |
| data | exactly `tokenType` "Bearer", `accessToken`, `refreshAccessToken`, `expiresIn` 900 | Data Object |
| JWT | HS256; `sub` = `user.id` = U_OK id; `exp - iat` = 900; `jti` a UUID; `user.username` and `user.email` as registered, `user.displayName` "John Doe"; `roles` ["CATALOG_MANAGER"], `permissions` ["catalog:manage"], `scopes` []; no password, hash or salt claim | JWT payload; claim note 6 |
| token rows | 1 access row and 1 refresh row for U_OK with the same new session_id; `token` = SHA-256 of the returned token; access `expired_at` ≈ now + 15 min, refresh ≈ now + 14 days; created_by = U_OK id | INSERT access/refresh token |
| refresh token | base64url of 32 bytes | Session note |
| attempt | 1 row: identifier_hash = SHA-256(username), user_id = U_OK id, result SUCCESS, created_by `system` | INSERT - Record attempt |

### TC-LOGIN-002 — Missing fields

- Source: L04, L06. Design readiness: Ready. Execution status: Not run.

**Request:** VR without `username` → "Username is a required field."; without `password` → "Password is a required field."; with neither → "Username and Password are required fields."; `username ""` → "Username is a required field.". **Expected:** 400 E10001, no `data`, no attempt row and no token row.

### TC-LOGIN-003 — Length limits

- Source: L04. Design readiness: Ready. Execution status: Not run.

**Request:** `username` of 255 characters → "Username must be at most 254 characters."; `password` of 129 → "Password must be at most 128 characters."; each 400 E10001 with no attempt row. `username` of 254 (unknown) → 401 (it is a valid attempt).

### TC-LOGIN-004 — No password complexity at login

- Source: L05. Design readiness: Ready. Execution status: Not run.

**Request:** VR with `password "abc"`. **Expected:** 401 E10002 (not 400); one FAILED attempt row.

### TC-LOGIN-005 — Unknown username

- Source: L07, L08, L20. Design readiness: Ready. Execution status: Not run.

**Request:** VR with a username no user has. **Expected:** 401 E10002 "Invalid username or password.", no `data`; one attempt FAILED with user_id NULL; no token row; the password hasher was called once (dummy verification).

### TC-LOGIN-006 — Wrong password

- Source: L07, L08, L09. Design readiness: Ready. Execution status: Not run.

**Request:** VR with `password "Wrong-Passw0rd"`. **Expected:** 401 E10002; one FAILED attempt with user_id = U_OK id, committed; no token row.

### TC-LOGIN-007 — User not ACTIVE

- Source: L07. Design readiness: Ready. Execution status: Not run.

**Preconditions:** a user with the right password and row_status INACTIVE, then LOCKED, then DELETED. **Expected:** 401 E10002 each time; FAILED with user_id NULL (the lock query only matches ACTIVE users); no token row.

### TC-LOGIN-008 — The answer never says which failure it is

- Source: L07. Design readiness: Ready. Execution status: Not run.

**Steps:** compare the bodies of TC-LOGIN-005, 006, 007, 009, 010 and 013. **Expected:** identical except `requestId` and `timestamp`.

### TC-LOGIN-009 — No ACTIVE PASSWORD row

- Source: L07, L20. Design readiness: Ready. Execution status: Not run.

**Preconditions:** `U_NOPW`. **Expected:** 401 E10002; FAILED with user_id = U_NOPW id; hasher called once.

### TC-LOGIN-010 — Ambiguous identifier

- Source: L07, L08. Design readiness: Ready. Execution status: Not run.

**Preconditions:** ACTIVE user A with username `x@example.test` and ACTIVE user B with email `x@example.test` (both with the password). **Request:** username `x@example.test`. **Expected:** 401 E10002; FAILED with user_id NULL; no token row for A or B.

### TC-LOGIN-011 — Identifier is compared exactly

- Source: L10. Design readiness: Ready. Execution status: Not run.

**Request:** VR with the username upper-cased, then with a trailing space. **Expected:** 401 E10002 each time (no match), FAILED with user_id NULL.

### TC-LOGIN-012 — Login by email address

- Source: L10. Design readiness: Ready. Execution status: Not run.

**Request:** VR with U_OK's email as `username`. **Expected:** 200 S10000; the attempt identifier_hash is SHA-256 of the email.

### TC-LOGIN-013 — Five failures refuse the sixth

- Source: L07, L09, L11. Design readiness: Ready. Execution status: Not run.

**Steps:** 5 wrong-password requests, then the right password, then the right password again.

| Observation | Expected | Source |
| --- | --- | --- |
| 1st–5th | 401, FAILED with user_id | L07 |
| 6th and 7th (right password) | 401 E10002 (same body), REFUSED with user_id NULL, no token row, hasher not called | L11 |
| count | REFUSED rows do not count: still 5 FAILED | L11 |

### TC-LOGIN-014 — Old failures do not count

- Source: L12. Design readiness: Ready. Execution status: Not run.

**Preconditions:** 5 FAILED rows for the identifier with created_at = now − 16 minutes, and 4 with now − 14 minutes in a second variant. **Expected:** the right password → 200 in both variants (5 old do not count; 4 recent are below 5).

### TC-LOGIN-015 — The counter is per supplied identifier

- Source: L13. Design readiness: Ready. Execution status: Not run.

**Preconditions:** 5 recent FAILED rows for U_OK's username. **Request:** U_OK's email with the right password. **Expected:** 200 (the email has no failures), while the username is refused.

### TC-LOGIN-016 — Concurrent attempts cannot pass a stale count

- Source: L14. Design readiness: Ready. Execution status: Not run.

**Preconditions:** 4 recent FAILED rows for the identifier. **Steps:** send 5 wrong-password requests at once. **Expected:** all 401; exactly 1 new FAILED and 4 REFUSED rows (each request saw the count after the previous one committed).

### TC-LOGIN-017 — Authorization claims

- Source: L15. Design readiness: Ready. Execution status: Not run.

**Preconditions (one user):**

- Roles: `B_ROLE` and `A_ROLE` ACTIVE and assigned ACTIVE; `X_ROLE` ACTIVE but its assignment INACTIVE; `Y_ROLE` assigned but the role INACTIVE.
- Permissions: `catalog.manage` (no scope definition) via A_ROLE; `shop.product.manage` with definitions for scopes `OWN` and `ALL`, granted via B_ROLE with a scope link to its `OWN` definition; `order.view` granted directly with no scope (no definition); `report.view` with a definition for `ALL`, granted via A_ROLE with no scope link (must be omitted); `audit.view` INACTIVE, granted directly (must be omitted); `catalog.manage` also granted directly (deduplicated); a permission granted only via X_ROLE or Y_ROLE (must be omitted).

**Expected JWT:** `roles` ["A_ROLE", "B_ROLE"]; `permissions` ["catalog:manage", "order:view", "shop.product:manage"]; `scopes` ["own:*"]. A user with no grants → 200 with `roles`, `permissions` and `scopes` as empty arrays.

### TC-LOGIN-018 — Each login is a new session

- Source: L03. Design readiness: Ready. Execution status: Not run.

**Steps:** log in twice. **Expected:** two different session_ids, each with one access and one refresh row; different jti.

### TC-LOGIN-019 — Login waits for the user row lock

- Source: L16, L17. Design readiness: Ready. Execution status: Not run.

**Steps:** a second connection holds `SELECT ... FOR UPDATE` on U_OK's row; login runs with a 1-second command timeout. **Expected:** 408 E90001 "The server timed out waiting for the request."; no token row and no attempt row (rolled back). After the lock is released, login → 200.

### TC-LOGIN-020 — Unexpected failure

- Source: L18. Design readiness: Ready. Execution status: Not run.

**Steps:** a test-only wrapper throws after the token inserts. **Expected:** 500, bizMessage "An unexpected error occurred.", no bizCode, no `data`; no token row and no attempt row.

### TC-LOGIN-021 — Rate limit

- Source: L19. Design readiness: Ready. Execution status: Not run.

**Steps:** with the limit at 10, send 11 requests from one IP. **Expected:** the 11th is 429 E90002 "Too many requests. Try again later." with `Retry-After` 1–60, and writes no attempt row.

## Open gaps and decisions

| Gap ID | Conflicting/missing sources | Affected obligations/cases | Missing decision or prerequisite | Status / decision reference |
| --- | --- | --- | --- | --- |
| None | — | — | — | The advisory-lock implementation question was decided by the owner on 2026-11-18 (Infrastructure helper). |

## Document verification and limitations

- Every obligation L01–L20 maps to a case, and every case cites its obligation. Codes and messages come from the spec examples and api-conventions.
- Not covered: timing equality of the dummy verification (only its call), the 30-day clean-up job.
- No case has run yet.

## Revision and execution history

- 2026-11-18: first version (Drake), Not run.
