---
name: "Inquiry User Profile API Test Cases"
description: "Documented scenarios and expected results for GET v1/user/profile; use for test planning and for the automated backend tests named after each case ID."
---

# Inquiry User Profile API Test Cases

## Source baseline and scope

- Method/path: `GET v1/user/profile`
- Governing sources: [spec.md](spec.md) (rules, Data Object, response examples, Database Relations), [sequence.wsd](sequence.wsd), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md)
- Source revision: Showcase `main` at the commit that adds this file; `spec.md` and `sequence.wsd` last changed in `8023e47`
- Source approval: approved (`approved_by: Ittikorn`, `approved_at: 2026-11-16T09:24:57+07:00`)
- Test design baseline: approved-source, except gap G1 (implementation choice, pending the lead's review)
- Scope and exclusions: the caller's own profile only; TLS excluded. The spec has no rate limit for this API.
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database:** throw-away PostgreSQL 17 with every Showcase migration (backend `PostgresFixture`), sessions in UTC.
- **Caller:** `U_OK` ACTIVE with every profile field set and an ACTIVE stored access token A; variant `U_BARE` with no optional field and no information row.
- **Valid request (VR):** `GET`, `authorization: Bearer <A>`, `timestamp: <now UTC>`, no query and no body.

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| I01 | spec Success; Data Object | 200 S10000 "Inquiry User Profile Success"; data has exactly the ten fields, decrypted, dateOfBirth `YYYY-MM-DD` | [TC-PROFILEQ-001](#tc-profileq-001--the-full-profile) | designed |
| I02 | Data Object "null when not set" | every unset field, and every information field when there is no information row, is present as null; an empty gender is null | [TC-PROFILEQ-002](#tc-profileq-002--unset-fields-are-null) | designed |
| I03 | spec rule | the profile is the caller's: userId only from the JWT sub | [TC-PROFILEQ-001](#tc-profileq-001--the-full-profile) | designed |
| I04 | spec Fail - Bad Request | a query parameter or a body → 400; missing or invalid timestamp → 400; all before the credential | [TC-PROFILEQ-003](#tc-profileq-003--no-query-and-no-body) | designed; message G1 |
| I05 | spec rule; Fail - Unauthorized | bad JWT, stored token missing, INACTIVE or expired, user not ACTIVE → 401 "Invalid or expired access token." | [TC-PROFILEQ-004](#tc-profileq-004--credential-failures) | designed |
| I06 | spec "Read user and information from the same repeatable-read snapshot" | one REPEATABLE READ snapshot; no lock, so a held user-row lock does not block the read | [TC-PROFILEQ-005](#tc-profileq-005--no-lock-one-snapshot) | designed |
| I07 | sequence failure branches | unexpected failure → 500 without bizCode | [TC-PROFILEQ-006](#tc-profileq-006--unexpected-failure) | designed |

## Detailed test cases

### TC-PROFILEQ-001 — The full profile

- Source: I01, I03. Design readiness: Ready. Execution status: Pass (automated).

**Request:** VR. **Expected:** 200, "Ok", S10000 "Inquiry User Profile Success"; `data` has exactly `userId` (U_OK id), `emailAddress`, `firstName`, `lastName`, `displayName`, `profilePicturePath`, `phoneNumber`, `address`, `dateOfBirth` (`1990-01-31`), `gender` (`MALE`), with the stored values decrypted.

### TC-PROFILEQ-002 — Unset fields are null

- Source: I02. Design readiness: Ready. Execution status: Pass (automated).

**Preconditions:** `U_BARE`; then a variant with an information row whose gender is `''`. **Expected:** 200; `firstName`, `lastName`, `displayName`, `profilePicturePath`, `phoneNumber`, `address`, `dateOfBirth`, `gender` are present with JSON null; `userId` and `emailAddress` set.

### TC-PROFILEQ-003 — No query and no body

- Source: I04. Design readiness: Ready (message per G1). Execution status: Pass (automated).

**Request:** VR with `?userId=<another id>`; VR with a JSON body; both also without authorization; VR without `timestamp`. **Expected:** 400 E10001 "Timestamp must be valid UTC and this endpoint accepts no query parameters or body." for the query and body cases, "Timestamp is a required header." for the missing header; never 401.

### TC-PROFILEQ-004 — Credential failures

- Source: I05. Design readiness: Ready. Execution status: Pass (automated).

**Request:** no authorization; a JWT signed with another key; a valid JWT with no stored row; the stored row INACTIVE; the stored row expired; the user LOCKED. **Expected:** 401 E10002 "Invalid or expired access token.".

### TC-PROFILEQ-005 — No lock, one snapshot

- Source: I06. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a second connection holds U_OK's row `FOR UPDATE`; VR with a 1-second command timeout. **Expected:** 200 (the read takes no lock). The single-snapshot property is a code property (one REPEATABLE READ transaction around both queries), covered by a handler test of the isolation level.

### TC-PROFILEQ-006 — Unexpected failure

- Source: I07. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a test-only wrapper throws on the information query. **Expected:** 500 "An unexpected error occurred.", no bizCode, no `data`.

## Open gaps and decisions

| Gap ID | Conflicting/missing sources | Affected obligations/cases | Missing decision or prerequisite | Status / decision reference |
| --- | --- | --- | --- | --- |
| G1 | the spec example "Timestamp must be valid UTC and this endpoint accepts no query parameters or body." covers several checks in one sentence; api-conventions has separate header messages | I04 | which message each 400 gets | implementation choice, pending the lead's review: header failures use the shared header messages; a query parameter or a body uses the spec example text |

## Document verification and limitations

- Every obligation I01–I07 maps to a case, and every case cites its obligation.
- The spec asks for a READ ONLY transaction; the backend opens REPEATABLE READ and issues no write (EF Core has no read-only transaction option); recorded as a limitation, not a behavior difference.
- Every case runs automatically; see the execution history.

## Revision and execution history

- 2026-11-19: first version (Drake), Not run.
- 2026-11-19: executed by the automated tests of e-commerce-backend on branch `feat/drake-08-inquiry-user-profile` (stacked on 07): `GetUserProfileApiTests` (HTTP + real PostgreSQL 17, 6 tests), `GetUserProfileQueryHandlerTests` (2). Result: every case passes (`dotnet test`: Api 202, Application 42, Domain 69, Infrastructure 46, 0 failed). Mutation checks: removing the token status and expiry filters fails TC-PROFILEQ-004; keeping an empty gender fails TC-PROFILEQ-002.
