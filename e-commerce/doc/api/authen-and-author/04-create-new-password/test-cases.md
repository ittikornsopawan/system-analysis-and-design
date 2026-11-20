---
name: "Create New Password API Test Cases"
description: "Documented scenarios and expected results for POST v1/auth/create-new-password; use for test planning and for the automated backend tests named after each case ID."
---

# Create New Password API Test Cases

## Source baseline and scope

- Method/path: `POST v1/auth/create-new-password`
- Governing sources: [spec.md](spec.md) (rules, response examples, Database Relations), [sequence.wsd](sequence.wsd) (lock order, guarded consumption, password and revocation notes), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md) (Error codes, Validation messages, Limits and rate limiting)
- Source revision: Showcase `main` at the commit that adds this file; `spec.md` and `sequence.wsd` last changed in `8023e47`
- Source approval: approved (`approved_by: Ittikorn`, `approved_at: 2026-11-16T09:24:57+07:00`)
- Test design baseline: approved-source
- Scope and exclusions: create-new-password only. Excluded: TLS; timing of the constant-time comparison (the comparison method is a code property, not an HTTP observation).
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database:** throw-away PostgreSQL 17 with every Showcase migration (backend `PostgresFixture`), sessions in UTC.
- **User:** `U_OK` ACTIVE with an ACTIVE PASSWORD row for `Passw0rd-Example`, 2 ACTIVE access and 2 ACTIVE refresh rows in two sessions (one expired but still ACTIVE), and one INACTIVE access row.
- **Reset token:** `T_OK` raw token whose SHA-256 is stored in an ACTIVE `t_user_reset_password` row of U_OK, expiring in 30 minutes.
- **Valid request (VR):** headers `content-type: application/json`, `timestamp: <now UTC>`; body `{"resetToken": T_OK, "newPassword": "NewSecret1x"}`. Since 2026-11-20 VR also carries the headers `encryptionKeyId` and `encryptedKey`, and its sensitive body fields are sent encrypted (api-conventions "Encrypted sensitive fields"); the test client does this for every request.
- **Observation:** HTTP response; rows of `t_user_reset_password`, `m_user_password`, `t_user_access_token`, `t_user_refresh_token` of U_OK and of another user `U_OTHER`; the new password verified with PBKDF2 against the stored row.

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| N01 | spec Success; sequence COMMIT | 200 S10000 "Create New Password Success", status only, no data; no login, no new token | [TC-NEWPW-001](#tc-newpw-001--the-password-is-replaced-and-every-session-is-closed) | designed |
| N02 | sequence consumption note | the reset row becomes INACTIVE (updated_by user id, updated_at now) | [TC-NEWPW-001](#tc-newpw-001--the-password-is-replaced-and-every-session-is-closed) | designed |
| N03 | sequence password note | old PASSWORD row INACTIVE (kept as history), one new ACTIVE PASSWORD row with a fresh 16-byte salt and PBKDF2 hash of the new password; created_by and updated_by = user id | [TC-NEWPW-001](#tc-newpw-001--the-password-is-replaced-and-every-session-is-closed) | designed |
| N04 | sequence revocation note | every ACTIVE access and refresh row of the user becomes INACTIVE, including expired ACTIVE rows and every session; other users and INACTIVE history unchanged | [TC-NEWPW-001](#tc-newpw-001--the-password-is-replaced-and-every-session-is-closed) | designed |
| N05 | spec Fail - Bad Request | resetToken and newPassword required; both missing → "Reset Token and New Password are required fields." | [TC-NEWPW-002](#tc-newpw-002--missing-fields) | designed |
| N06 | spec password policy; Fail - Bad Request Password Policy | the policy is checked before any lookup | [TC-NEWPW-003](#tc-newpw-003--password-policy-before-any-lookup) | designed |
| N07 | spec "one answer" rule; Fail - Bad Request Reset Token | unknown, INACTIVE (used or replaced), expired token, or a user not ACTIVE → 400 "Reset token is invalid or expired.", nothing changed | [TC-NEWPW-004](#tc-newpw-004--an-unknown-token), [TC-NEWPW-005](#tc-newpw-005--a-used-or-replaced-token), [TC-NEWPW-006](#tc-newpw-006--an-expired-token), [TC-NEWPW-007](#tc-newpw-007--a-user-that-is-not-active) | designed |
| N08 | spec "must differ"; Fail - Bad Request Same Password; sequence rollback note | the same password → 400 "New password must be different from the current password.", rollback, the token stays usable | [TC-NEWPW-008](#tc-newpw-008--the-same-password-is-refused-and-the-token-stays-usable) | designed |
| N09 | sequence guarded consumption | the token is used once: a second request with it → the generic 400 | [TC-NEWPW-005](#tc-newpw-005--a-used-or-replaced-token), [TC-NEWPW-009](#tc-newpw-009--concurrent-requests-consume-the-token-once) | designed |
| N10 | sequence lock note | concurrent requests serialize on the user row; only the first consumes | [TC-NEWPW-009](#tc-newpw-009--concurrent-requests-consume-the-token-once), [TC-NEWPW-010](#tc-newpw-010--the-user-row-lock) | designed |
| N11 | sequence "A missing current password is an internal consistency failure" | no ACTIVE PASSWORD row → 500 without bizCode, rollback | [TC-NEWPW-011](#tc-newpw-011--missing-current-password) | designed |
| N12 | sequence failure branches | timeout → 408 E90001, rollback | [TC-NEWPW-010](#tc-newpw-010--the-user-row-lock) | designed |
| N13 | sequence "never log or return either secret" | the response never contains the token or a password | [TC-NEWPW-001](#tc-newpw-001--the-password-is-replaced-and-every-session-is-closed) | designed |
| N14 | spec Rate limit | 11th request in a minute → 429 E90002 + Retry-After | [TC-NEWPW-012](#tc-newpw-012--rate-limit) | designed |
| N15 | sequence expiry note | expiry is strict `expired_at > now` | [TC-NEWPW-006](#tc-newpw-006--an-expired-token) | designed |
| N16 | api-conventions "Encrypted sensitive fields"; spec Headers | `encryptionKeyId` and `encryptedKey` are mandatory; a missing or empty one → 400 E10001 `Encryption Key Id is a required header.` / `Encrypted Key is a required header.` before the body is read | [TC-NEWPW-013](#tc-newpw-013--missing-encryption-headers) | designed |
| N17 | api-conventions "Encrypted sensitive fields"; spec Fail - Bad Request Encryption | unknown key id, key not base64, key of the wrong size, field under another key, plain text in an encrypted field, wrong JSON path, short value and wrong tag all answer one 400 E10001 `Encrypted fields could not be decrypted.` with the same body | [TC-NEWPW-014](#tc-newpw-014--every-decrypt-failure-is-the-same-400) | designed |
| N18 | api-conventions "Encrypted sensitive fields" "Order" | fields are decrypted before validation: a valid ciphertext reaches the spec validation; the same plain value unencrypted is the decrypt 400 | [TC-NEWPW-015](#tc-newpw-015--decrypt-comes-before-validation) | designed |

## Detailed test cases

### TC-NEWPW-001 — The password is replaced and every session is closed

- Source: N01–N04, N13. Design readiness: Ready. Execution status: Pass (automated).

**Request:** VR. **Expected:** 200, message "Ok", S10000 "Create New Password Success", no `data`, body without the token or a password; the reset row INACTIVE with updated_by = U_OK id; old PASSWORD row INACTIVE (updated_by = U_OK id), one new ACTIVE PASSWORD row (created_by = U_OK id, 16-byte salt) that verifies `NewSecret1x` and not the old password; all 4 ACTIVE token rows of U_OK INACTIVE (including the expired one); U_OTHER's rows unchanged; no new token row.

### TC-NEWPW-002 — Missing fields

- Source: N05. Design readiness: Ready. Execution status: Pass (automated).

**Request:** without `resetToken` → "Reset Token is a required field."; without `newPassword` → "New Password is a required field."; with neither → "Reset Token and New Password are required fields."; each 400 E10001, nothing changed.

### TC-NEWPW-003 — Password policy before any lookup

- Source: N06. Design readiness: Ready. Execution status: Pass (automated).

**Request:** VR with `newPassword` `Short1`, `nouppercase1`, `NOLOWERCASE1`, `NoDigitsHere`, 129 characters; and with an unknown `resetToken` plus `Short1`. **Expected:** 400 E10001 "Password must be 8 to 128 characters and contain an upper-case letter, a lower-case letter and a digit." each time (the policy answers before the token lookup); nothing changed; T_OK still usable.

### TC-NEWPW-004 — An unknown token

- Source: N07. Design readiness: Ready. Execution status: Pass (automated).

**Request:** VR with a token that has no row. **Expected:** 400 E10001 "Reset token is invalid or expired."; nothing changed.

### TC-NEWPW-005 — A used or replaced token

- Source: N07, N09. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** use T_OK successfully, then send it again with another new password; and a token whose row is INACTIVE because a newer reset replaced it. **Expected:** the generic 400 each time; nothing changed by the second call.

### TC-NEWPW-006 — An expired token

- Source: N07, N15. Design readiness: Ready. Execution status: Pass (automated).

**Preconditions:** the reset row expired one second ago (and a variant with `expired_at` equal to the lookup time, which counts as expired). **Expected:** the generic 400; nothing changed.

### TC-NEWPW-007 — A user that is not ACTIVE

- Source: N07. Design readiness: Ready. Execution status: Pass (automated).

**Preconditions:** U_OK is LOCKED (then INACTIVE). **Expected:** the generic 400; the reset row stays ACTIVE (rollback); nothing changed.

### TC-NEWPW-008 — The same password is refused and the token stays usable

- Source: N08. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** VR with `newPassword` = `Passw0rd-Example` (the current password); then VR with `NewSecret1x`. **Expected:** first 400 E10001 "New password must be different from the current password." with the reset row still ACTIVE and no password or token change; then 200 as TC-NEWPW-001.

### TC-NEWPW-009 — Concurrent requests consume the token once

- Source: N09, N10. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** send 3 VRs with different new passwords at once. **Expected:** exactly one 200 and two generic 400; exactly one new ACTIVE PASSWORD row.

### TC-NEWPW-010 — The user row lock

- Source: N10, N12. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a second connection holds U_OK's row `FOR UPDATE`; VR runs with a 1-second command timeout. **Expected:** 408 E90001 "The server timed out waiting for the request."; nothing changed. After the lock is released, VR → 200.

### TC-NEWPW-011 — Missing current password

- Source: N11. Design readiness: Ready. Execution status: Pass (automated).

**Preconditions:** U_OK's PASSWORD row is INACTIVE. **Expected:** 500, "An unexpected error occurred.", no bizCode, no `data`; the reset row stays ACTIVE; no token row changed.

### TC-NEWPW-012 — Rate limit

- Source: N14. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** with the limit at 10, send 11 requests from one IP. **Expected:** the 11th is 429 E90002 "Too many requests. Try again later." with `Retry-After` 1–60.

### TC-NEWPW-013 — Missing encryption headers

- Source: N16. Design readiness: Ready. Execution status: Pass (automated).

**Request:** VR with `encryptionKeyId` removed; then `encryptedKey` removed; then both removed; then `encryptionKeyId` empty. **Expected:** 400 E10001 with bizMessage `Encryption Key Id is a required header.`, then `Encrypted Key is a required header.`, then `Encryption Key Id is a required header, Encrypted Key is a required header.`, then `Encryption Key Id is a required header.`; the body is not decrypted and nothing is written.

### TC-NEWPW-014 — Every decrypt failure is the same 400

- Source: N17. Design readiness: Ready. Execution status: Pass (automated).

**Request:** VR with the encryption headers changed in eight ways: (1) unknown `encryptionKeyId`; (2) `encryptedKey` that is not base64; (3) `encryptedKey` wrapping a 16-byte key; (4) fields encrypted under a key other than the wrapped one; (5) plain text in the encrypted fields; (6) fields encrypted with another JSON path as additional authenticated data; (7) a value shorter than IV plus tag (`AAAA`); (8) a value whose last tag byte is changed. **Expected:** every request answers 400 E10001 `Encrypted fields could not be decrypted.`; the eight bodies are identical except `requestId` and `timestamp`; the body never contains a plain value; nothing is written.

### TC-NEWPW-015 — Decrypt comes before validation

- Source: N18. Design readiness: Ready. Execution status: Pass (automated).

**Request:** VR with `newPassword` set to `short`: first sent as plain text, then encrypted correctly. **Expected:** the plain-text request is 400 E10001 `Encrypted fields could not be decrypted.`; the encrypted request is 400 E10001 `Password must be 8 to 128 characters and contain an upper-case letter, a lower-case letter and a digit.` (validation sees the plain value).

## Open gaps and decisions

| Gap ID | Conflicting/missing sources | Affected obligations/cases | Missing decision or prerequisite | Status / decision reference |
| --- | --- | --- | --- | --- |
| None | — | — | — | Single-field missing messages follow api-conventions "Validation messages" (`<Field> is a required field.`). |

## Document verification and limitations

- Every obligation N01–N15 maps to a case, and every case cites its obligation.
- Codes and messages come from the spec examples and api-conventions.
- Every case runs automatically; see the execution history.

## Revision and execution history

- 2026-11-18: first version (Drake), Not run.
- 2026-11-18: executed by the automated tests of e-commerce-backend on branch `feat/drake-04-create-new-password` (stacked on 03): `CreateNewPasswordApiTests` (HTTP + real PostgreSQL 17, 16 tests), `CreateNewPasswordCommandHandlerTests` (6), `CreateNewPasswordRepositoryTests` (4, real database). Result: every case passes (`dotnet test`: Api 150, Application 25, Domain 48, Infrastructure 37, 0 failed). Mutation checks: removing the single-use guard fails TC-NEWPW-005, 006 and 009; removing `ForUpdate()` fails the repository TC-NEWPW-010 (the guarded consumption alone already keeps TC-NEWPW-009 correct).
- 2026-11-20: field-transport cases TC-NEWPW-013, TC-NEWPW-014, TC-NEWPW-015 added (Janny) and every existing request now sent encrypted; automated by `FieldTransportApiTests`, `FieldTransportTests` and the encrypted `Send` of the endpoint tests, on e-commerce-backend branch `feat/janny-field-transport` at `338f74c` (Api 289, Application 43, Domain 96, Infrastructure 51, 0 failed). Not yet merged into `main` (e-commerce-backend#21).
