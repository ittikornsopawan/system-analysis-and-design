---
name: "Upsert User Profile API Test Cases"
description: "Documented scenarios and expected results for POST v1/user/profile/upsert; use for test planning and for the automated backend tests named after each case ID."
---

# Upsert User Profile API Test Cases

## Source baseline and scope

- Method/path: `POST v1/user/profile/upsert`
- Governing sources: [spec.md](spec.md) (body fields, rules, response examples, Database Relations), [sequence.wsd](sequence.wsd) (validation, presence flags, lock and credential notes), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md)
- Source revision: Showcase `main` at the commit that adds this file; `spec.md` and `sequence.wsd` last changed in `8023e47`
- Source approval: approved (`approved_by: Ittikorn`, `approved_at: 2026-11-16T09:24:57+07:00`)
- Test design baseline: approved-source, except gap G1 (message choices, approved by Josh 2026-11-20)
- Scope and exclusions: the own profile only; TLS excluded. The spec has no rate limit for this API.
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database:** throw-away PostgreSQL 17 with every Showcase migration (backend `PostgresFixture`), sessions in UTC.
- **Caller:** `U_OK` ACTIVE with an ACTIVE stored access token A (its JWT presented). Variant `U_NEW` with no information row; variant with only a DELETED information row.
- **Valid request (VR):** `authorization: Bearer <A>`, `content-type: application/json`, `timestamp: <now UTC>`, body as each case says.
- **Observation:** HTTP response; `authen.m_user` and `authen.m_user_information` rows of the caller (sensitive columns decrypted with the test key; `updated_at` before and after).

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| U01 | spec Success | 200 S10000 "Upsert User Profile Success" with data.userId only | [TC-PROFILE-001](#tc-profile-001--update-both-tables) | designed |
| U02 | sequence presence note | an omitted field keeps its value; explicit null clears it; flags come from key presence | [TC-PROFILE-003](#tc-profile-003--omit-keeps-null-clears) | designed |
| U03 | spec sensitive rule | firstName, lastName, phoneNumber, address stored encrypted; displayName and profilePicturePath plain; dateOfBirth and gender typed | [TC-PROFILE-001](#tc-profile-001--update-both-tables) | designed |
| U04 | sequence information note | no non-DELETED information row → insert one with omitted columns NULL; a DELETED row alone does not count | [TC-PROFILE-002](#tc-profile-002--first-information-row) | designed |
| U05 | sequence skip note | no user field → no m_user update (updated_at unchanged); no information field → no information lookup or row; body {} → 200 with no writes | [TC-PROFILE-004](#tc-profile-004--an-empty-body-writes-nothing), [TC-PROFILE-005](#tc-profile-005--one-group-only) | designed |
| U06 | sequence validation note; Fail - Bad Request | lengths (first/last 100, display 128), phone `^\+?[0-9]{8,15}$`, dateOfBirth real and not after today UTC, gender MALE/FEMALE/OTHER, string types; null allowed | [TC-PROFILE-006](#tc-profile-006--field-validation) | designed; messages G1 |
| U07 | Fail - Bad Request Fixed Field | username, emailAddress or password present, even null → 400 "Username, Email Address and Password cannot be changed here." | [TC-PROFILE-007](#tc-profile-007--fixed-fields) | designed |
| U08 | sequence "Reject request userId/id, unknown body keys" | userId, id or any unknown key → 400; a body that is not a JSON object → 400 | [TC-PROFILE-008](#tc-profile-008--unknown-keys-and-shape) | designed; message G1 |
| U09 | sequence order | validation (400) before the JWT (401) | [TC-PROFILE-009](#tc-profile-009--validation-before-the-credential) | designed |
| U10 | sequence credential note | bad JWT, user not ACTIVE, stored token revoked or expired → 401 "Invalid or expired access token.", no writes | [TC-PROFILE-010](#tc-profile-010--credential-failures) | designed |
| U11 | sequence lock note | the user row is locked FOR UPDATE before the credential check and writes | [TC-PROFILE-011](#tc-profile-011--the-user-row-lock) | designed |
| U12 | sequence failure branches | timeout → 408 E90001; a failure after the user update → 500 without bizCode and nothing saved | [TC-PROFILE-011](#tc-profile-011--the-user-row-lock), [TC-PROFILE-012](#tc-profile-012--unexpected-failure) | designed |

## Detailed test cases

### TC-PROFILE-001 — Update both tables

- Source: U01, U03. Design readiness: Ready. Execution status: Pass (automated).

**Request:** all eight fields: `firstName John`, `lastName Doe`, `displayName John Doe`, `profilePicturePath /p.png`, `phoneNumber +66812345678`, `address 1 Road`, `dateOfBirth 1990-01-31`, `gender MALE`. **Expected:** 200, "Ok", S10000 "Upsert User Profile Success", `data` exactly `{userId: U_OK id}`; m_user first/last name decrypt to the input, display_name and profile_picture_path plain, updated_by = U_OK id; information phone and address decrypt to the input, date and gender typed, updated_by = U_OK id.

### TC-PROFILE-002 — First information row

- Source: U04. Design readiness: Ready. Execution status: Pass (automated).

**Preconditions:** `U_NEW` has no information row (then a variant with only a DELETED row). **Request:** `{"gender": "OTHER"}`. **Expected:** 200; one new non-DELETED information row with gender OTHER, phone, address and date NULL, created_by = U_NEW id; the DELETED row unchanged.

### TC-PROFILE-003 — Omit keeps, null clears

- Source: U02. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** set all fields (TC-PROFILE-001); then send `{"firstName": null, "phoneNumber": null}`. **Expected:** first_name and phone_number NULL; last_name, display_name, address, date and gender unchanged.

### TC-PROFILE-004 — An empty body writes nothing

- Source: U05. Design readiness: Ready. Execution status: Pass (automated).

**Request:** `{}`. **Expected:** 200 with data.userId; m_user and information `updated_at` unchanged; no information row created for `U_NEW`.

### TC-PROFILE-005 — One group only

- Source: U05. Design readiness: Ready. Execution status: Pass (automated).

**Request:** `{"displayName": "Jo"}` for `U_NEW`; then `{"address": "2 Road"}` for `U_OK`. **Expected:** first: m_user updated, still no information row; second: information updated, m_user `updated_at` unchanged.

### TC-PROFILE-006 — Field validation

- Source: U06. Design readiness: Ready (messages per G1). Execution status: Pass (automated).

**Request (each a 400 E10001 with no writes):** firstName 101 characters → "First Name must be at most 100 characters."; lastName 101; displayName 129 → "Display Name must be at most 128 characters."; phoneNumber `1234567` and `+1234567890123456` and `08-1234` → "Phone Number must be 8 to 15 digits with an optional leading +."; dateOfBirth `1990-02-30`, `31-01-1990` and tomorrow UTC → "Date of birth must be a real date on or before today's UTC date (YYYY-MM-DD)."; gender `male` → "Gender must be MALE, FEMALE or OTHER."; firstName `123` (a number) → "First Name must be a string.". **Accepted:** every field null; firstName 100 characters; phone `12345678` and `+123456789012345`; dateOfBirth today UTC.

### TC-PROFILE-007 — Fixed fields

- Source: U07. Design readiness: Ready. Execution status: Pass (automated).

**Request:** `{"username": "x"}`, `{"emailAddress": null}`, `{"password": "Passw0rd"}` (each with a valid firstName too). **Expected:** 400 E10001 "Username, Email Address and Password cannot be changed here."; no writes.

### TC-PROFILE-008 — Unknown keys and shape

- Source: U08. Design readiness: Ready (message per G1). Execution status: Pass (automated).

**Request:** `{"userId": "<another id>"}`, `{"id": "x"}`, `{"nickname": "x"}` → 400 E10001 "<Field> is not a known field." (for example "User Id is not a known field."); `[]` and `"text"` → "Request Body must be an object."; no writes.

### TC-PROFILE-009 — Validation before the credential

- Source: U09. Design readiness: Ready. Execution status: Pass (automated).

**Request:** an invalid gender with no authorization header; then without `timestamp` and no authorization. **Expected:** 400 E10001 each time, not 401.

### TC-PROFILE-010 — Credential failures

- Source: U10. Design readiness: Ready. Execution status: Pass (automated).

**Request:** valid body with: no authorization; a JWT signed with another key; a valid JWT with no stored row; the stored row INACTIVE (after logout); the user LOCKED. **Expected:** 401 E10002 "Invalid or expired access token."; no writes.

### TC-PROFILE-011 — The user row lock

- Source: U11, U12. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a second connection holds U_OK's row `FOR UPDATE`; VR `{"firstName": "Lock"}` with a 1-second command timeout. **Expected:** 408 E90001; first_name unchanged. After release → 200.

### TC-PROFILE-012 — Unexpected failure

- Source: U12. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a test-only wrapper throws after the m_user update, before the information write. **Expected:** 500 "An unexpected error occurred.", no bizCode; m_user unchanged (rollback).

## Open gaps and decisions

| Gap ID | Conflicting/missing sources | Affected obligations/cases | Missing decision or prerequisite | Status / decision reference |
| --- | --- | --- | --- | --- |
| G1 | the spec and api-conventions give no message for an invalid phone number or an unknown key | U06, U08 | the two messages | implementation choice, approved by Josh 2026-11-20: "Phone Number must be 8 to 15 digits with an optional leading +." and "<Field> is not a known field."; every other message comes from the spec example or the convention forms |

## Document verification and limitations

- Every obligation U01–U12 maps to a case, and every case cites its obligation.
- Every case runs automatically; see the execution history.

## Revision and execution history

- 2026-11-19: first version (Drake), Not run.
- 2026-11-19: executed by the automated tests of e-commerce-backend on branch `feat/drake-07-upsert-user-profile` (stacked on 06): `UpsertUserProfileApiTests` (HTTP + real PostgreSQL 17, 22 tests), `UpsertUserProfileCommandHandlerTests` (4), `UserProfileRepositoryTests` (2) and `CallerCredentialRepositoryTests` (1, real database), `ProfileFieldRulesTests` (11). Result: every case passes (`dotnet test`: Api 196, Application 40, Domain 69, Infrastructure 46, 0 failed). Mutation checks: making any of firstName, lastName, profilePicturePath, phoneNumber or gender always written fails TC-PROFILE-003 or 005 (an assertion was added to TC-PROFILE-005 after the firstName mutation first survived); writing the information group always fails TC-PROFILE-004 and 005; removing `ForUpdate()` fails the credential repository test.
- 2026-11-20: Josh (SA Lead) approved every gap choice above as written; the status column now says so.
