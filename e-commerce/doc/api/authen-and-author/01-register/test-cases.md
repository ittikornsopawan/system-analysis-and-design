---
name: "Register API Test Cases"
description: "Documented scenarios and expected results for POST v1/auth/register; use for test planning and for the automated backend tests named after each case ID."
---

# Register API Test Cases

## Source baseline and scope

- Method/path: `POST v1/auth/register`
- Governing sources: [spec.md](spec.md) (request, response examples, Database Relations), [sequence.wsd](sequence.wsd) (check order, transaction notes), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md) (Error codes; Limits and rate limiting)
- Source revision: Showcase `main` at the commit that adds this file; `spec.md` and `sequence.wsd` last changed in `8023e47`
- Source approval: approved (`approved_by: Josh (SA Lead, delegated by Ittikorn 2026-11-17)`, `approved_at: 2026-11-18T13:18:23+07:00`), with the Validation messages of api-conventions.md from Showcase PR #237
- Test design baseline: approved-source; gaps G1–G3 resolved by Josh on 2026-11-18 (PR #237)
- Scope and exclusions: the register endpoint only. Excluded: the gateway TLS layer (infrastructure); load testing. The 429 limit is covered once here because the spec states it as a rule line.
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing at backend commit `5dc828a`; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database:** a throw-away PostgreSQL 17 with every Showcase migration applied (backend `PostgresFixture`). Each case uses its own random username and email, so cases do not share rows.
- **Clock:** UTC; `now` is captured by the handler. Consent fixtures use `effective_at = now - 1 day` unless a case says otherwise.
- **Consent fixtures** (`consent.m_consent_type`, `consent.t_consent`):
  - `TYPE_A` ACTIVE type; `C_REQ` ACTIVE, `is_required = true`, version `1.0.0`, effective, no expiry.
  - `C_OPT` ACTIVE, `is_required = false`, version `1.0.0`, type `TYPE_A`.
  - `C_FUTURE` ACTIVE, required, `effective_at = now + 1 day`. `C_EXPIRED` ACTIVE, required, `expired_at = now - 1 minute`. `C_INACTIVE` row_status `INACTIVE`, required. `C_TYPE_OFF` ACTIVE, required, type `TYPE_B` with row_status `INACTIVE`.
  - Cases that need "no applicable required consent" run with only `C_OPT`, `C_FUTURE`, `C_EXPIRED`, `C_INACTIVE` and `C_TYPE_OFF` present.
- **Referrer:** `U_REF`, an existing user (any status).
- **Valid request (VR):** headers `content-type: application/json`, `timestamp: <now ISO-8601 UTC>`, `requestId: req-<case>`; body `username`, `emailAddress`, `password = Passw0rd-Example` (unique per case), and `consents = [{consentId: C_REQ, consentVersion: "1.0.0", result: true}]`. Each case lists only its overrides.
- **Observation:** HTTP response through the real ASP.NET pipeline; committed rows read by authorized read-only queries on the test database. The field key of the test configuration decrypts byte columns.
- **Failure injection:** a test-only interceptor or connection that fails one insert, a held lock for timeout, and two concurrent requests for duplicates. These exist only in the test project.

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| R01 | spec Body; sequence "Validate ..."; api-conventions Validation messages | username, emailAddress, password are mandatory; the missing ones are named: one → "<Field> is a required field.", all three → "Username, Email Address and Password are required fields." | [TC-REG-002](#tc-reg-002--missing-mandatory-field), [TC-REG-003](#tc-reg-003--empty-or-blank-mandatory-field) | designed |
| R02 | spec Body row 3; "Fail - Bad Request Password" | password 8–128 with upper, lower, digit → else 400 E10001 with the password message | [TC-REG-004](#tc-reg-004--password-policy-boundaries) | designed |
| R03 | spec Body rows 1, 2, 4, 5, 6 | length limits: username 128, emailAddress 254, firstName 100, lastName 100, displayName 128 | [TC-REG-005](#tc-reg-005--length-limits) | designed |
| R04 | spec Body rows 10, 11, 12 | dateOfBirth `YYYY-MM-DD`; gender MALE, FEMALE, OTHER; referrerId UUID | [TC-REG-006](#tc-reg-006--format-of-optional-scalars) | designed |
| R05 | spec Address Object; sequence note | address object fields mandatory non-empty strings, title ≤ 128, isDefault boolean; `addresses` is one object, never an array | [TC-REG-007](#tc-reg-007--address-object-validation) | designed |
| R06 | spec Consent Object; sequence note | consentId UUID, consentVersion non-empty ≤ 8, result boolean if present; duplicate consentIds → 400 | [TC-REG-008](#tc-reg-008--consent-item-validation), [TC-REG-009](#tc-reg-009--duplicate-consentid) | designed |
| R07 | spec Header Parameters | content-type and timestamp mandatory; requestId optional and echoed or generated | [TC-REG-010](#tc-reg-010--headers), [TC-REG-001](#tc-reg-001--full-registration-succeeds) | designed |
| R08 | sequence "Invalid input" | validation failures do no database work | [TC-REG-002](#tc-reg-002--missing-mandatory-field) | designed |
| R09 | sequence "Existing username or email" | username or email existing in any lifecycle state → 409 E10003 "Username or email address already exists." | [TC-REG-011](#tc-reg-011--duplicate-username-or-email) | designed |
| R10 | sequence "m_user identifier UNIQUE violation" | a concurrent duplicate (23505) → whole rollback, same 409 | [TC-REG-012](#tc-reg-012--concurrent-duplicate) | designed |
| R11 | sequence "Check referrer"; spec rule | referrerId of a missing user → 404 E10005 "Consent or referrer not found."; any lifecycle status is valid | [TC-REG-013](#tc-reg-013--referrer), [TC-REG-001](#tc-reg-001--full-registration-succeeds) | designed |
| R12 | sequence "Missing/hidden consent" | a submitted consentId that is not effective, inactive, inactive type or unknown → 404 E10005 | [TC-REG-014](#tc-reg-014--submitted-consent-not-applicable) | designed |
| R13 | sequence "consentVersion differs" | displayed version ≠ current → 400 E10001 "Consent version is no longer current." | [TC-REG-015](#tc-reg-015--stale-consent-version) | designed |
| R14 | sequence "Required consent missing or result is not explicit true" | each applicable required consent needs result = true → else 400 E10001 "All current required consents must be accepted." | [TC-REG-016](#tc-reg-016--required-consent-not-accepted) | designed |
| R15 | sequence note "Read all currently effective ACTIVE consents ..." | only effective, ACTIVE consents of ACTIVE types are applicable; `t_consent.is_required` decides | [TC-REG-017](#tc-reg-017--only-applicable-consents-are-required) | designed |
| R16 | spec rule "consents may be omitted/empty only when ..." | no applicable required consent → omitted or empty consents succeed | [TC-REG-018](#tc-reg-018--no-required-consent-and-no-consents) | designed |
| R17 | sequence "Insert user consent" note (Q16) | each supplied consent → one row, is_read = true, read_at = now, result = explicit value or false; omitted optional consent → no row; rows in consentId order | [TC-REG-019](#tc-reg-019--consent-evidence-rows) | designed |
| R18 | sequence "Create user" .. "Create user information" | one m_user, one PASSWORD row (salted PBKDF2), one information row; createdBy = `auth-register` | [TC-REG-001](#tc-reg-001--full-registration-succeeds), [TC-REG-020](#tc-reg-020--minimal-registration) | designed |
| R19 | spec Body "encrypts it before it is stored" | username, emailAddress, firstName, lastName, phoneNumber, address and address fields except title stored encrypted; displayName and title plain | [TC-REG-001](#tc-reg-001--full-registration-succeeds) | designed |
| R20 | sequence "Create user address" | optional address → one row with is_default = TRUE whatever isDefault says; omitted → no row | [TC-REG-021](#tc-reg-021--address-is-always-default), [TC-REG-020](#tc-reg-020--minimal-registration) | designed |
| R21 | sequence "Create user referral" | referrerId → one l_user_referral row; omitted → none | [TC-REG-001](#tc-reg-001--full-registration-succeeds), [TC-REG-020](#tc-reg-020--minimal-registration) | designed |
| R22 | sequence "COMMIT"; "Success" example | 201 S10000 "Register Success", data.userId = new user id only | [TC-REG-001](#tc-reg-001--full-registration-succeeds) | designed |
| R23 | sequence "Failure of ... insertion rolls back" | a failing child insert rolls back user and every child; 500 without bizCode | [TC-REG-022](#tc-reg-022--child-insert-failure-rolls-back-everything) | designed |
| R24 | sequence "Referenced row deleted concurrently" | FK violation → rollback, 404 E10005 | [TC-REG-023](#tc-reg-023--referenced-row-deleted-concurrently) | designed |
| R25 | sequence "Timeout before COMMIT" | timeout → rollback, 408 E90001 | [TC-REG-024](#tc-reg-024--timeout-before-commit) | designed |
| R26 | sequence "Serialization conflict" | retry the whole transaction with a new snapshot; no partial writes | [TC-REG-025](#tc-reg-025--serialization-conflict-is-retried-whole) | designed |
| R27 | spec rule "Rate limit" | more than 10 requests per minute per IP → 429 E90002 + Retry-After, before the handler | [TC-REG-026](#tc-reg-026--rate-limit) | designed |
| R28 | sequence "preserve input identifier representation" | username and email are stored as sent (no lower-casing or trimming) | [TC-REG-027](#tc-reg-027--identifier-stored-as-sent) | designed |
| R29 | sequence note | register never grants PLATFORM_ADMIN | [TC-REG-001](#tc-reg-001--full-registration-succeeds) | designed (no author rows written) |

## Detailed test cases

### TC-REG-001 — Full registration succeeds

- Source: R07, R11, R18, R19, R21, R22, R29
- Purpose: every optional part is written in one commit and only the user id is returned.
- Design readiness: Ready
- Execution status: Pass (automated)

**Preconditions and test data:** consent fixtures; `U_REF` exists.

**Request/input:** VR plus `firstName John`, `lastName Doe`, `displayName John Doe`, `profilePicturePath /profiles/a.png`, `phoneNumber 0812345678`, `address 123 Road`, `dateOfBirth 1990-01-31`, `gender MALE`, `referrerId U_REF`, `addresses {title Home, isDefault false, address 1 Road, city Watthana, state Bangkok, postalCode 10110, country Thailand}`, `consents [C_REQ true, C_OPT false]`.

**Steps:** 1. Confirm no user with the username or email. 2. Send the request. 3. Read the rows of the new user id.

**Expected results**

| Observation | Expected value or predicate | Source / evidence needed |
| --- | --- | --- |
| HTTP status | 201 | Success example |
| bizCode | S10000, bizMessage "Register Success", status "SUCCESS", message "Created", requestId `req-TC-REG-001` | Success example |
| Response | `data` has exactly `userId`, a UUID equal to the new `m_user.id` | Data Object |
| Durable effects | 1 m_user (created_by `auth-register`, username/email/first/last encrypted and decrypting to the input, display_name plain); 1 m_user_password row_type PASSWORD, 16-byte salt, hash verifies with PBKDF2-HMAC-SHA256 600,000; 1 m_user_information (phone and address encrypted, date 1990-01-31, gender MALE); 1 t_user_address is_default TRUE, title plain, other fields encrypted; 2 t_user_consent; 1 l_user_referral to `U_REF`; no author.t_user_role row | sequence inserts; DB read |

**Cleanup:** none needed (unique identifiers). **Actual result and evidence:** Pass — see [Revision and execution history](#revision-and-execution-history).

### TC-REG-002 — Missing mandatory field

- Source: R01, R08. Design readiness: Ready. Execution status: Pass (automated).

**Request/input:** VR with `username` omitted; repeat with `emailAddress` omitted and `password` omitted; then a body with all three omitted.

**Steps:** send each variant; count `authen.m_user` rows before and after.

| Observation | Expected value or predicate | Source |
| --- | --- | --- |
| HTTP status | 400 | Fail - Bad Request |
| bizCode | E10001; bizMessage "Username is a required field." / "Email Address is a required field." / "Password is a required field."; all three missing: "Username, Email Address and Password are required fields."; no `data` | example; Validation messages |
| Durable effects | no row written; no SQL needed (validation precedes BEGIN) | sequence "Invalid input" |

**Actual result and evidence:** Pass — see [Revision and execution history](#revision-and-execution-history).

### TC-REG-003 — Empty or blank mandatory field

- Source: R01. Design readiness: Ready. Execution status: Pass (automated).

**Request/input:** VR with `username ""`, then `"   "`; same for `emailAddress` and `password ""`.

| Observation | Expected | Source |
| --- | --- | --- |
| HTTP status / bizCode | 400 / E10001 "Email Address is a required field." (and the same form for the other two) | R01 |
| Durable effects | none | R08 |

### TC-REG-004 — Password policy boundaries

- Source: R02. Design readiness: Ready. Execution status: Pass (automated).

**Request/input:** VR with password of 7 characters `Passw0r` (400), 8 `Passw0rd` (201), 128 characters with upper/lower/digit (201), 129 (400), `password1` no upper (400), `PASSWORD1` no lower (400), `Password` no digit (400).

| Observation | Expected | Source |
| --- | --- | --- |
| 400 variants | E10001, bizMessage "Password must be 8 to 128 characters and contain an upper-case letter, a lower-case letter and a digit." | Fail - Bad Request Password |
| 201 variants | as TC-REG-001 for the minimal body | R22 |

### TC-REG-005 — Length limits

- Source: R03. Design readiness: Ready. Execution status: Pass (automated).

**Request/input:** for each field the maximum (201) and maximum + 1 (400): username 128/129, emailAddress 254/255, firstName 100/101, lastName 100/101, displayName 128/129.

| Observation | Expected | Source |
| --- | --- | --- |
| over limit | 400 E10001 "<Field> must be at most <n> characters." (Username 128, Email Address 254, First Name 100, Last Name 100, Display Name 128) | spec Body; Validation messages |
| at limit | 201 | spec Body |

### TC-REG-006 — Format of optional scalars

- Source: R04, G3. Design readiness: Ready. Execution status: Pass (automated).

**Request/input:** `dateOfBirth "1990-13-01"`, `"31-01-1990"` → "Date Of Birth must be a valid date (YYYY-MM-DD)."; `gender "male"`, `"X"` → "Gender must be MALE, FEMALE or OTHER."; `referrerId "abc"` → "Referrer Id must be a valid UUID."; `emailAddress "abc"`, `"a@b@c"` → "Email Address must be a valid email address."; added 2026-11-18 for the owner's stricter rule: `"a.b@c"` (no dot in the domain), `"a b@shop.co"`, `"A <a@shop.co>"` → the same message, and `" a.b@shop.co"` (leading space); each 400 E10001 with no rows. `gender "X"` with `referrerId "abc"` → "Gender must be MALE, FEMALE or OTHER, Referrer Id must be a valid UUID." (field order). `gender "OTHER"` and `dateOfBirth "2000-02-29"` → 201.

### TC-REG-007 — Address object validation

- Source: R05. Design readiness: Ready. Execution status: Pass (automated).

**Request/input:** `addresses` as an array → "Addresses must be an object."; `city` missing → "addresses: City is a required field."; `postalCode ""` → "addresses: Postal Code is a required field."; `title` of 129 characters → "addresses: Title must be at most 128 characters."; `isDefault "yes"` → "addresses: Is Default must be a boolean." (G4); each 400 E10001 and no rows. `title` of 128 → 201. A body that is not valid JSON (`not json`), an array (`[]`) or a string (`"text"`) → "Request Body must be an object." alone, before any field rule (G4).

### TC-REG-008 — Consent item validation

- Source: R06. Design readiness: Ready. Execution status: Pass (automated).

**Request/input:** second consent with `consentId "x"` → "consents[1]: Consent Id must be a valid UUID."; `consentVersion ""` → "consents[0]: Consent Version is a required field."; `consentVersion "1.0.0.123"` (9 characters) → "consents[0]: Consent Version must be at most 8 characters."; `result "true"` (string) → "consents[0]: Result must be a boolean." (G4); each 400 E10001 and no rows. `consentVersion` of 8 characters that does not match the current version → TC-REG-015 path, not this one.

### TC-REG-009 — Duplicate consentId

- Source: R06. Design readiness: Ready. Execution status: Pass (automated).

**Request/input:** `consents [C_REQ true, C_REQ false]`. **Expected:** 400 E10001 "consents[1]: Consent Id must not be duplicated." before SQL; no rows.

### TC-REG-010 — Headers

- Source: R07, G2. Design readiness: Ready. Execution status: Pass (automated).

**Request/input:** VR without `timestamp`; with `timestamp "yesterday"`; with `timestamp "2026-11-18T12:00:00+07:00"` (not UTC); with `content-type: text/plain`; VR without `requestId`.

| Observation | Expected | Source |
| --- | --- | --- |
| missing timestamp | 400 E10001 "Timestamp is a required header."; no rows | Validation messages (headers) |
| invalid or non-UTC timestamp | 400 E10001 "Timestamp must be a valid UTC timestamp." | Validation messages (headers) |
| wrong content-type | 400 E10001 "Content-Type must be application/json." (never 415) | Validation messages (headers) |
| no requestId | 201; `status.requestId` is a generated non-empty string starting `req-` | sequence "generate requestId if omitted" |

### TC-REG-011 — Duplicate username or email

- Source: R09. Design readiness: Ready. Execution status: Pass (automated).

**Preconditions:** `U_DUP` registered with username `dup.user` and email `dup@example.test`; variants with `U_DUP.row_status` ACTIVE, INACTIVE and DELETED.

**Request/input:** VR with username `dup.user` (new email); VR with email `dup@example.test` (new username).

| Observation | Expected | Source |
| --- | --- | --- |
| HTTP / bizCode | 409 / E10003 "Username or email address already exists." for every lifecycle state | sequence |
| Durable effects | no new rows (transaction rolled back) | sequence ROLLBACK |

### TC-REG-012 — Concurrent duplicate

- Source: R10. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** two requests with the same username and different emails start together (both pass the check before either inserts).

| Observation | Expected | Source |
| --- | --- | --- |
| responses | exactly one 201 and one 409 E10003 | sequence 23505 branch |
| Durable effects | one user with that username; the loser left no child rows | sequence |

### TC-REG-013 — Referrer

- Source: R11. Design readiness: Ready. Execution status: Pass (automated).

**Request/input:** `referrerId` = a random UUID with no user → 404 E10005 "Consent or referrer not found.", no rows. `referrerId` = a user with row_status DELETED → 201 with one referral row.

### TC-REG-014 — Submitted consent not applicable

- Source: R12. Design readiness: Ready. Execution status: Pass (automated).

**Request/input:** VR plus one more consent, in turn: unknown UUID, `C_FUTURE`, `C_EXPIRED`, `C_INACTIVE`, `C_TYPE_OFF` (each with version `1.0.0`, result true). **Expected:** 404 E10005 "Consent or referrer not found."; no rows.

### TC-REG-015 — Stale consent version

- Source: R13. Design readiness: Ready. Execution status: Pass (automated).

**Request/input:** VR with `C_REQ` version `0.9.0`. **Expected:** 400 E10001 "Consent version is no longer current."; no rows. The version is never defaulted: omitting `consentVersion` is TC-REG-008.

### TC-REG-016 — Required consent not accepted

- Source: R14. Design readiness: Ready. Execution status: Pass (automated).

**Request/input:** `consents` omitted; `consents []`; `C_REQ` with `result false`; `C_REQ` with `result` omitted. **Expected:** 400 E10001 "All current required consents must be accepted."; no rows.

### TC-REG-017 — Only applicable consents are required

- Source: R15. Design readiness: Ready. Execution status: Pass (automated).

**Preconditions:** all consent fixtures. **Request/input:** VR (accepts only `C_REQ`). **Expected:** 201: `C_FUTURE`, `C_EXPIRED`, `C_INACTIVE` and `C_TYPE_OFF` are required in their rows but not applicable, so they are not demanded. Add `TYPE_A` with type-level `is_required` true and `C_OPT` still optional → still 201.

### TC-REG-018 — No required consent and no consents

- Source: R16. Design readiness: Ready. Execution status: Pass (automated).

**Preconditions:** only non-applicable or optional consents exist (see fixtures). **Request/input:** VR with `consents` omitted, then `[]`. **Expected:** 201; zero t_user_consent rows.

### TC-REG-019 — Consent evidence rows

- Source: R17. Design readiness: Ready. Execution status: Pass (automated).

**Request/input:** `consents [C_OPT (result omitted), C_REQ true]` (C_OPT listed first).

| Observation | Expected | Source |
| --- | --- | --- |
| HTTP | 201 | R22 |
| rows | 2 rows; `C_OPT` result false, `C_REQ` result true; both consent_version `1.0.0`, is_read true, read_at = handler now (same value), created_by `auth-register` | sequence consent note |
| order | inserted in consentId order (observable by row creation order or id comparison in a trace; if not observable, recorded as unverified) | sequence loop |
| optional not sent | another optional consent not in the request has no row | Q16 |

### TC-REG-020 — Minimal registration

- Source: R18, R20, R21. Design readiness: Ready. Execution status: Pass (automated).

**Request/input:** VR only. **Expected:** 201; 1 m_user (first_name, last_name, profile_picture_path NULL; display_name NULL), 1 PASSWORD row, 1 information row with all nullable columns SQL NULL (not the string `null`), 0 address rows, 0 referral rows.

### TC-REG-021 — Address is always default

- Source: R20. Design readiness: Ready. Execution status: Pass (automated).

**Request/input:** VR with an address with `isDefault false`; then with `isDefault` omitted. **Expected:** 201; one address row with is_default TRUE each time.

### TC-REG-022 — Child insert failure rolls back everything

- Source: R23. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a test-only interceptor fails the `t_user_address` insert (then separately the consent insert) for this request.

| Observation | Expected | Source |
| --- | --- | --- |
| HTTP / bizCode | 500, bizMessage "An unexpected error occurred.", no bizCode | Fail - Internal Server Error |
| Durable effects | no m_user, password, information, address, consent or referral row for the username | sequence rollback |

### TC-REG-023 — Referenced row deleted concurrently

- Source: R24. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** the referrer passes the check, then is deleted (hard delete by a test connection) before the referral insert; FK violation follows. **Expected:** 404 E10005; no rows for the new user.

### TC-REG-024 — Timeout before commit

- Source: R25. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a test connection holds a lock the register transaction needs, or the test sets the request timeout below the time of one insert. **Expected:** 408 E90001 "The server timed out waiting for the request."; no rows.

### TC-REG-025 — Serialization conflict is retried whole

- Source: R26. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a test-only interceptor raises SQLSTATE 40001 on the first commit attempt only. **Expected:** 201; exactly one user and one of each child row (the retry repeated every read and write, nothing partial from the first attempt).

### TC-REG-026 — Rate limit

- Source: R27. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** with the limit configured to 10, send 11 requests from one IP within a minute. **Expected:** the 11th is 429, bizCode E90002, bizMessage "Too many requests. Try again later.", header `Retry-After` 1–60 seconds; it does not reach the handler.

### TC-REG-027 — Identifier stored as sent

- Source: R28. Design readiness: Ready. Execution status: Pass (automated).

**Request/input:** username `John.Doe`, email `John.Doe@Example.test`. **Expected:** 201; decrypted username and email equal the input exactly. A second registration with `john.doe` and `john.doe@example.test` is not a duplicate (201), because comparison is on the stored bytes.

## Open gaps and decisions

| Gap ID | Conflicting/missing sources | Affected obligations/cases | Missing decision or prerequisite | Status / decision reference |
| --- | --- | --- | --- | --- |
| G1 | spec examples give bizMessage only for required fields, password and consent | R01, R03–R06 | exact bizMessage text | resolved — Josh, 2026-11-18, api-conventions "Validation messages" (PR #237) |
| G2 | no example for a header failure; content-type could be a framework 415 | R07 | status and message for headers | resolved — 400 E10001, header messages (PR #237) |
| G3 | emailAddress had only a length | R03 | email format rule | resolved — exactly one @ with non-empty parts, "Email Address must be a valid email address." (PR #237); superseded 2026-11-18 by the owner: the `EmailAddress` rule with a dot required in the domain (api-conventions "Email address") |
| G4 | no form for a JSON value of the wrong type or a body that is not an object | TC-REG-007, TC-REG-008 | message forms | resolved — Josh, 2026-11-18 (PR #238): "<Field> must be a string. / a number. / a boolean. / an array."; "Request Body must be an object." alone |

## Document verification and limitations

- Every obligation R01–R29 maps to at least one case, and every case cites its obligation. Error codes and messages were copied from the spec examples.
- Error precedence follows `sequence.wsd`: 409 (duplicate) is checked before 404 (consent/referrer) and the consent 400s, which differs from the generic order in api-conventions; the sequence governs this endpoint.
- Not covered: TLS, load, and SQL lock order (this endpoint takes no FOR UPDATE lock per its sequence note).
- No case has run; runtime evidence comes from the automated backend tests.

## Revision and execution history

- 2026-11-18: first version (Drake), Not run.
- 2026-11-18: G1–G3 resolved (PR #237); messages added to TC-REG-002, 003, 005–010; G4 opened.
- 2026-11-18: executed by the automated tests of e-commerce-backend at commit `5dc828a` (branch `feat/drake-01-register`): `RegisterApiTests` (HTTP + real PostgreSQL 17, 48 tests), `RegisterCommandHandlerTests` (6), `RegistrationRepositoryTests` (12), `RegistrationConsentPolicyTests` (9). Result: every case passes (`dotnet test`: Api 90, Application 12, Domain 39, Infrastructure 17, 0 failed). TC-REG-012, 022, 023, 024 and 025 are proven at the repository and handler level (real-database exceptions and their HTTP mapping) because the race or failure cannot be timed through HTTP alone; TC-REG-019 consentId insert order is enforced in code but not observable in the stored rows.
- 2026-11-18: G4 resolved (PR #238); three body cases added to TC-REG-007 and passing at backend commit `353075c` (Api 93, Application 12, Domain 39, Infrastructure 17, 0 failed).
- 2026-11-20: the strict email rule (owner decision 2026-11-18) is applied by e-commerce-backend commit `07cccc1` (branch `fix/drake-strict-email-rule`): `EmailAddressFormat` is the one rule. The four TC-REG-006 email rows `"a.b@c"`, `"a b@shop.co"`, `"A <a@shop.co>"` and `" a.b@shop.co"` are automated and pass (`dotnet test`: Api 278, Application 42, Domain 96, Infrastructure 46, 0 failed). Mutation check: accepting a dot anywhere instead of in the domain fails the `"a.b@c"` row.
