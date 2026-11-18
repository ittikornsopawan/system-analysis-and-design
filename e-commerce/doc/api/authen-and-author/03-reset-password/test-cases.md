---
name: "Reset Password Request API Test Cases"
description: "Documented scenarios and expected results for POST v1/auth/reset-password; use for test planning and for the automated backend tests named after each case ID."
---

# Reset Password Request API Test Cases

## Source baseline and scope

- Method/path: `POST v1/auth/reset-password`
- Governing sources: [spec.md](spec.md) (rules, response examples, Database Relations), [sequence.wsd](sequence.wsd) (order, lock, throttle and email notes), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md) (Error codes, Validation messages, Limits and rate limiting)
- Source revision: Showcase `main` at the commit that adds this file; `spec.md` and `sequence.wsd` last changed in `8023e47`
- Source approval: approved (`approved_by: Ittikorn`, `approved_at: 2026-11-16T09:24:57+07:00`)
- Test design baseline: approved-source, except gaps G1 and G2 below (implementation choices recorded, waiting for the lead's review)
- Scope and exclusions: the reset request only (create-new-password is 04). Excluded: real email delivery (outside the spec); response-time equality (the spec says runtime verification is needed; covered by "the same preparation runs for every valid request").
- Execution summary: Not run — automated tests in e-commerce-backend will carry the case ID in their names.

## Shared fixtures and observation prerequisites

- **Database:** throw-away PostgreSQL 17 with every Showcase migration (backend `PostgresFixture`), sessions in UTC.
- **Users:** `U_OK` ACTIVE with a unique email; variants INACTIVE, LOCKED and DELETED.
- **Valid request (VR):** headers `content-type: application/json`, `timestamp: <now UTC>`, `requestId: req-<case>`; body `{"emailAddress": <U_OK email>}`.
- **Generic answer (GA):** 200, message "Ok", bizCode S10000, bizMessage "If the email address is registered, a reset link has been sent.", status SUCCESS, no `data`.
- **Observation:** HTTP response; rows of `authen.t_user_reset_password` for the user; a test email sender that records each hand-off (recipient and link); the configured reset URL `https://reset.test/reset-password?token=`.

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| P01 | spec "The answer is always 200 with the same message"; Success example | unknown email, non-ACTIVE user, refusal and issuance all answer GA | [TC-RESET-001](#tc-reset-001--issuance-for-an-active-user), [TC-RESET-004](#tc-reset-004--unknown-email), [TC-RESET-005](#tc-reset-005--user-not-active), [TC-RESET-006](#tc-reset-006--three-per-hour-then-refused) | designed |
| P02 | sequence validation note; Fail - Bad Request | emailAddress required, valid, ≤ 254 → 400 E10001; validation before SQL | [TC-RESET-002](#tc-reset-002--invalid-email-address) | designed; message choice G1 |
| P03 | sequence INSERT note | one new row: created_by = user id, created_at = post-lock now, reset_token = SHA-256 of the raw token, expired_at = now + 30 min, ACTIVE | [TC-RESET-001](#tc-reset-001--issuance-for-an-active-user) | designed |
| P04 | sequence token note | raw token = 32 random bytes, unpadded base64url; never returned, stored or logged raw | [TC-RESET-001](#tc-reset-001--issuance-for-an-active-user), [TC-RESET-011](#tc-reset-011--the-raw-token-is-never-logged) | designed |
| P05 | sequence UPDATE note | earlier ACTIVE rows of the user become INACTIVE (updated_by, updated_at = now) before the insert; other users and non-ACTIVE history untouched; at most one ACTIVE row | [TC-RESET-003](#tc-reset-003--a-new-issuance-replaces-the-active-one) | designed |
| P06 | spec Throttle; sequence count note | at most 3 issuance rows per rolling hour per user, whatever their status; the 4th answers GA with no change and no email; equality at windowStart is outside | [TC-RESET-006](#tc-reset-006--three-per-hour-then-refused), [TC-RESET-007](#tc-reset-007--the-rolling-window) | designed |
| P07 | sequence email note | email hand-off only after COMMIT, only to the registered address, link = configured reset URL + raw token; none for unknown, inactive or refused | [TC-RESET-001](#tc-reset-001--issuance-for-an-active-user), [TC-RESET-004](#tc-reset-004--unknown-email), [TC-RESET-006](#tc-reset-006--three-per-hour-then-refused) | designed |
| P08 | sequence lock note | the user row is locked FOR UPDATE and rechecked (ACTIVE and same email); concurrent requests reread the count after the lock | [TC-RESET-008](#tc-reset-008--concurrent-requests-respect-the-limit), [TC-RESET-009](#tc-reset-009--the-user-row-lock) | designed |
| P09 | sequence lookup note | the email is compared exactly (same encryption as register/login, no trim or case change) | [TC-RESET-004](#tc-reset-004--unknown-email) | designed |
| P10 | sequence failure branches | pre-commit timeout → 408 E90001, rollback, no email; unexpected failure → 500 without bizCode, rollback, no email | [TC-RESET-009](#tc-reset-009--the-user-row-lock), [TC-RESET-010](#tc-reset-010--unexpected-failure) | designed |
| P11 | sequence note "Do not change password, access/refresh tokens ..." | a reset request changes nothing else | [TC-RESET-001](#tc-reset-001--issuance-for-an-active-user) | designed |
| P12 | spec Rate limit | 11th request in a minute from one IP → 429 E90002 + Retry-After | [TC-RESET-012](#tc-reset-012--rate-limit) | designed |
| P13 | sequence "apply the same configured response-latency policy" | every 200 business outcome follows the same latency policy | — | gap G2 |

## Detailed test cases

### TC-RESET-001 — Issuance for an active user

- Source: P01, P03, P04, P07, P11. Design readiness: Ready. Execution status: Not run.

**Request:** VR. **Expected:** GA; one ACTIVE reset row: created_by = U_OK id, created_at within the request, expired_at = created_at + 30 min, reset_token = SHA-256 of the token in the handed-off link; exactly one email hand-off to U_OK's address with link `https://reset.test/reset-password?token=<raw>`, where `<raw>` decodes from unpadded base64url to 32 bytes; U_OK's password row and token rows unchanged.

### TC-RESET-002 — Invalid email address

- Source: P02. Design readiness: Ready (message per G1). Execution status: Not run.

**Request:** `emailAddress` omitted, `""`, `"abc"`, `"a@b@c"` → 400 E10001 "Email Address is required and must be a valid email address."; 255 characters → 400 E10001 "Email Address must be at most 254 characters."; no reset row and no email.

### TC-RESET-003 — A new issuance replaces the ACTIVE one

- Source: P05. Design readiness: Ready. Execution status: Not run.

**Steps:** request twice for U_OK; another user has an ACTIVE row. **Expected:** both GA; U_OK has 2 rows: the first INACTIVE with updated_by = U_OK id and updated_at = the second request's now, the second ACTIVE; the other user's row is still ACTIVE.

### TC-RESET-004 — Unknown email

- Source: P01, P07, P09. Design readiness: Ready. Execution status: Not run.

**Request:** an email no user has; then U_OK's email upper-cased. **Expected:** GA each time; no row; no email.

### TC-RESET-005 — User not ACTIVE

- Source: P01. Design readiness: Ready. Execution status: Not run.

**Preconditions:** the user is INACTIVE, LOCKED, then DELETED. **Expected:** GA; no row; no email.

### TC-RESET-006 — Three per hour, then refused

- Source: P01, P06, P07. Design readiness: Ready. Execution status: Not run.

**Steps:** 4 requests for U_OK. **Expected:** all GA; 3 rows (2 INACTIVE, 1 ACTIVE); 3 emails; the 4th changes nothing and sends nothing.

### TC-RESET-007 — The rolling window

- Source: P06. Design readiness: Ready. Execution status: Not run.

**Preconditions:** 3 rows with created_at = now − 61 minutes (any status). **Expected:** a request issues (GA, 4th row, email). Variant: 3 rows at now − 59 minutes → refused (no new row, no email).

### TC-RESET-008 — Concurrent requests respect the limit

- Source: P08. Design readiness: Ready. Execution status: Not run.

**Steps:** 5 requests for U_OK at once. **Expected:** all GA; exactly 3 rows, exactly one ACTIVE; exactly 3 emails.

### TC-RESET-009 — The user row lock

- Source: P08, P10. Design readiness: Ready. Execution status: Not run.

**Steps:** a second connection holds U_OK's row `FOR UPDATE`; the request runs with a 1-second command timeout. **Expected:** 408 E90001 "The server timed out waiting for the request."; no row; no email. After the lock is released → GA and one row.

### TC-RESET-010 — Unexpected failure

- Source: P10. Design readiness: Ready. Execution status: Not run.

**Steps:** a test-only wrapper throws after the insert. **Expected:** 500, "An unexpected error occurred.", no bizCode, no `data`; the earlier ACTIVE row is still ACTIVE (rollback); no email.

### TC-RESET-011 — The raw token is never logged

- Source: P04. Design readiness: Ready. Execution status: Not run.

**Steps:** run TC-RESET-001 with the development email sender and capture its log output. **Expected:** no log line contains the raw token or the reset link.

### TC-RESET-012 — Rate limit

- Source: P12. Design readiness: Ready. Execution status: Not run.

**Steps:** with the limit at 10, send 11 requests from one IP. **Expected:** the 11th is 429 E90002 "Too many requests. Try again later." with `Retry-After` 1–60.

## Open gaps and decisions

| Gap ID | Conflicting/missing sources | Affected obligations/cases | Missing decision or prerequisite | Status / decision reference |
| --- | --- | --- | --- | --- |
| G1 | spec example "Email Address is required and must be a valid email address." vs api-conventions forms ("is a required field." / "must be a valid email address.") | P02, TC-RESET-002 | which message a missing, invalid or too long email gets | implementation choice, pending the lead's review: a spec example keeps its text (api-conventions "A spec example that already shows a message keeps it"), so missing and invalid share the example message; too long uses the convention form |
| G2 | "apply the same configured response-latency policy" names no setting or value | P13 | the latency policy (minimum duration) | implementation choice, pending the lead's review: no extra delay is configured; every valid request does the same encryption and token/hash preparation before the lookup; timing is not measured |

## Document verification and limitations

- Every obligation P01–P12 maps to a case; P13 is gap G2.
- Codes and messages come from the spec examples and api-conventions.
- No case has run yet.

## Revision and execution history

- 2026-11-18: first version (Drake), Not run.
