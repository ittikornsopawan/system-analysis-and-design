---
name: "Refresh Token API Test Cases"
description: "Documented scenarios and expected results for POST v1/auth/refresh-token; use for test planning and for the automated backend tests named after each case ID."
---

# Refresh Token API Test Cases

## Source baseline and scope

- Method/path: `POST v1/auth/refresh-token`
- Governing sources: [spec.md](spec.md) (rules, response examples, Database Relations), [sequence.wsd](sequence.wsd) (lock order, rotation, reuse and grace notes), [02-login/sequence.wsd](../02-login/sequence.wsd) (claim resolution reused by refresh), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md)
- Source revision: Showcase `main` at the commit that adds this file; `spec.md` and `sequence.wsd` last changed in `8023e47`
- Source approval: approved (`approved_by: Ittikorn`, `approved_at: 2026-11-16T09:24:57+07:00`)
- Test design baseline: approved-source
- Scope and exclusions: refresh only. The claim resolution rules themselves are covered by [02-login TC-LOGIN-017](../02-login/test-cases.md#tc-login-017--authorization-claims); here one case proves refresh resolves current grants instead of copying old ones.
- Execution summary: Not run — automated tests in e-commerce-backend will carry the case ID in their names.

## Shared fixtures and observation prerequisites

- **Database:** throw-away PostgreSQL 17 with every Showcase migration (backend `PostgresFixture`), sessions in UTC.
- **Session S1:** `U_OK` ACTIVE logs in through `POST v1/auth/login`, giving access token A1 and refresh token R1 in session S1. A second session S2 of the same user exists.
- **Valid request (VR):** headers `content-type: application/json`, `timestamp: <now UTC>`; body `{"refreshAccessToken": R1}`.
- **Observation:** HTTP response; decoded JWT; rows of `t_user_refresh_token` and `t_user_access_token` by session; `updated_at` of the consumed row can be moved back by a test query to simulate time.

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| F01 | spec Success; sequence rotation note | 200 S10000 "Refresh Token Success" with tokenType Bearer, accessToken, refreshAccessToken, expiresIn 900 | [TC-REFRESH-001](#tc-refresh-001--rotation) | designed |
| F02 | spec Rotation; sequence rotation note | the presented row becomes INACTIVE (updated_by user, updated_at now); one new access and one new refresh row in the **same** session; new hashes differ from the presented one; old access tokens stay ACTIVE | [TC-REFRESH-001](#tc-refresh-001--rotation) | designed |
| F03 | spec Fresh authorization claims | the new JWT has the current user snapshot, roles, permissions and scopes, not the old token's | [TC-REFRESH-002](#tc-refresh-002--claims-are-resolved-again) | designed |
| F04 | spec Fail - Bad Request; sequence validation note | refreshAccessToken required, non-empty string → 400 "Refresh Access Token is a required field." before SQL | [TC-REFRESH-003](#tc-refresh-003--missing-token) | designed |
| F05 | spec Fail - Unauthorized | unknown, expired token, or user not ACTIVE → 401 E10002 "Invalid or expired refresh token.", nothing changed | [TC-REFRESH-004](#tc-refresh-004--unknown-or-expired-token), [TC-REFRESH-005](#tc-refresh-005--user-not-active) | designed |
| F06 | sequence reuse note | INACTIVE row used again within 10 seconds → 401, rollback, the rotated session stays | [TC-REFRESH-006](#tc-refresh-006--replay-inside-the-grace-window) | designed |
| F07 | sequence reuse note | INACTIVE row used again at 10 seconds or later (or with NULL updated_at) → every ACTIVE refresh and access row of that session INACTIVE and committed, answer 401; other sessions untouched | [TC-REFRESH-007](#tc-refresh-007--replay-after-the-grace-window-closes-the-session) | designed |
| F08 | sequence lock note | concurrent refreshes with the same token: one 200, the other 401 inside grace, and the rotated session stays ACTIVE | [TC-REFRESH-008](#tc-refresh-008--concurrent-refreshes) | designed |
| F09 | sequence lock note | the user row is locked FOR UPDATE before the reread | [TC-REFRESH-009](#tc-refresh-009--the-user-row-lock) | designed |
| F10 | sequence failure branches | timeout → 408 E90001 with rollback; unexpected failure → 500 without bizCode | [TC-REFRESH-009](#tc-refresh-009--the-user-row-lock), [TC-REFRESH-010](#tc-refresh-010--unexpected-failure) | designed |
| F11 | spec Rate limit | more than 60 requests per minute per IP → 429 E90002 + Retry-After | [TC-REFRESH-011](#tc-refresh-011--rate-limit) | designed |
| F12 | spec "No authorization header is required" | refresh works without an access token, even when A1 has expired | [TC-REFRESH-001](#tc-refresh-001--rotation) | designed |

## Detailed test cases

### TC-REFRESH-001 — Rotation

- Source: F01, F02, F12. Design readiness: Ready. Execution status: Not run.

**Request:** VR without an authorization header. **Expected:** 200, "Ok", S10000 "Refresh Token Success"; data has exactly tokenType "Bearer", accessToken, refreshAccessToken (≠ R1), expiresIn 900; R1's row INACTIVE with updated_by = U_OK id; session S1 now has 2 access rows (A1 still ACTIVE) and 2 refresh rows (the new one ACTIVE, hash = SHA-256 of the returned token); S2 untouched; the new JWT `sub` = U_OK id.

### TC-REFRESH-002 — Claims are resolved again

- Source: F03. Design readiness: Ready. Execution status: Not run.

**Steps:** log in with role `R_A` granting `catalog.manage`; then remove the role assignment (INACTIVE) and grant role `R_B` with `order.view`; refresh. **Expected:** the new JWT `roles` = ["R_B"], `permissions` = ["order:view"]; `user` matches the current row.

### TC-REFRESH-003 — Missing token

- Source: F04. Design readiness: Ready. Execution status: Not run.

**Request:** body without `refreshAccessToken`, then `""`. **Expected:** 400 E10001 "Refresh Access Token is a required field."; nothing changed.

### TC-REFRESH-004 — Unknown or expired token

- Source: F05. Design readiness: Ready. Execution status: Not run.

**Request:** an unknown token; then R1 after its `expired_at` is set one second in the past. **Expected:** 401 E10002 "Invalid or expired refresh token."; no row changed.

### TC-REFRESH-005 — User not ACTIVE

- Source: F05. Design readiness: Ready. Execution status: Not run.

**Preconditions:** U_OK is LOCKED. **Expected:** the same 401; R1 stays ACTIVE (not consumed).

### TC-REFRESH-006 — Replay inside the grace window

- Source: F06. Design readiness: Ready. Execution status: Not run.

**Steps:** refresh with R1 (200, gives R2); immediately refresh with R1 again. **Expected:** the second is the same 401; R2 and the new access row stay ACTIVE.

### TC-REFRESH-007 — Replay after the grace window closes the session

- Source: F07. Design readiness: Ready. Execution status: Not run.

**Steps:** refresh with R1 (gives R2); move R1's `updated_at` 10 seconds back; refresh with R1 again. Variant: R1 INACTIVE with `updated_at` NULL. **Expected:** 401; every refresh and access row of S1 INACTIVE (R2 and A1 included) and committed; S2 rows still ACTIVE; R2 then fails with 401.

### TC-REFRESH-008 — Concurrent refreshes

- Source: F08. Design readiness: Ready. Execution status: Not run.

**Steps:** send 3 VRs with R1 at once. **Expected:** exactly one 200 and two 401; exactly one new ACTIVE refresh row in S1 and it stays ACTIVE.

### TC-REFRESH-009 — The user row lock

- Source: F09, F10. Design readiness: Ready. Execution status: Not run.

**Steps:** a second connection holds U_OK's row `FOR UPDATE`; VR runs with a 1-second command timeout. **Expected:** 408 E90001; R1 still ACTIVE; no new row. After release, VR → 200.

### TC-REFRESH-010 — Unexpected failure

- Source: F10. Design readiness: Ready. Execution status: Not run.

**Steps:** a test-only wrapper throws after the new token inserts. **Expected:** 500, "An unexpected error occurred.", no bizCode; R1 still ACTIVE; no new row.

### TC-REFRESH-011 — Rate limit

- Source: F11. Design readiness: Ready. Execution status: Not run.

**Steps:** with the standard limit at 60, send 61 requests from one IP. **Expected:** the 61st is 429 E90002 "Too many requests. Try again later." with `Retry-After` 1–60.

## Open gaps and decisions

| Gap ID | Conflicting/missing sources | Affected obligations/cases | Missing decision or prerequisite | Status / decision reference |
| --- | --- | --- | --- | --- |
| None | — | — | — | — |

## Document verification and limitations

- Every obligation F01–F12 maps to a case, and every case cites its obligation.
- Codes and messages come from the spec examples.
- No case has run yet.

## Revision and execution history

- 2026-11-18: first version (Drake), Not run.
