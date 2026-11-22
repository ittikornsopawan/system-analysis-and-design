---
name: "Upsert User Role API Test Cases"
description: "Documented scenarios and expected results for POST v1/author/user/role/upsert, including the last-administrator rule; use for test planning and for the automated backend tests named after each case ID."
---

# Upsert User Role API Test Cases

## Source baseline and scope

- Method/path: `POST v1/author/user/role/upsert`
- Governing sources: [spec.md](spec.md), [sequence.wsd](sequence.wsd) (check order, locks, the last-administrator count), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md)
- Source revision: `spec.md` and `sequence.wsd` last changed in `aa82b4a`
- Source approval: approved (`approved_by: Ittikorn`, `approved_at: 2026-11-16T09:24:57+07:00`)
- Test design baseline: approved-source
- Scope and exclusions: TLS excluded; no rate limit in the spec. The duplicate precheck is not separately observable: `uq_t_user_role_user_id_role_id` answers the same 409 when the precheck is removed.
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database and callers:** as in the 03 test cases. `AnchorAdministratorAsync` keeps one ACTIVE PLATFORM_ADMIN assignment of an ACTIVE user so other cases never trip the last-administrator rule. Each case seeds its own users and roles.
- **Valid request (VR):** `POST v1/author/user/role/upsert`, `authorization: Bearer <ADMIN>`, `timestamp: <now UTC>`, body `{"id"?, "userId", "roleId", "rowStatus"?}`.
- **Observation:** HTTP response (`data.userRoleId`; 204 has no body); the `author.t_user_role` row after the call.

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| R01 | spec Success | insert 201 "Insert User Role Success", ACTIVE, created_by the caller | [TC-UROLE-001](#tc-urole-001--insert) | designed |
| R02 | spec Success | update 200, archive 200 "Archive User Role Success", reopen, delete 204; a deleted row is 404 and the role can be given again as a new row | [TC-UROLE-002](#tc-urole-002--update-archive-reopen-and-delete) | designed |
| R03 | spec body rules | shape, unknown and repeated fields, required, UUIDs, insert not DELETED, row status values | [TC-UROLE-003](#tc-urole-003--input-validation) | designed |
| R04 | sequence order | 400 before 401; credential failures 401 with no write | [TC-UROLE-004](#tc-urole-004--validation-before-the-credential-and-credential-failures) | designed |
| R05 | spec target and ACTIVE rules | a missing target user 404 E10005 "User not found." before 403; giving (insert or reopen) needs an ACTIVE user and role (404 E10005); taking away or keeping ACTIVE does not | [TC-UROLE-005](#tc-urole-005--the-target-user-must-exist-and-the-request-must-give-to-active-rows) | designed |
| R06 | spec id rules | a missing or DELETED id 404 E10004; user and role fixed (400) | [TC-UROLE-006](#tc-urole-006--the-assignment-id-and-its-fixed-user-and-role) | designed |
| R07 | spec permission rule | only exact PLATFORM_ADMIN; 403 E10009 before the duplicate check | [TC-UROLE-007](#tc-urole-007--only-a-platform-administrator-before-the-duplicate-check) | designed |
| R08 | spec duplicate rule | a non-DELETED pair of any status is 409 E10003 | [TC-UROLE-008](#tc-urole-008--duplicate-assignment) | designed |
| R09 | spec last-administrator rule | removing the last ACTIVE administrator (ACTIVE assignment of an ACTIVE user) is 409 E10006 for every non-ACTIVE status; with a second one it is allowed | [TC-UROLE-009](#tc-urole-009--the-platform-keeps-at-least-one-administrator) | designed |
| R10 | sequence unique guard | concurrent inserts of one pair: one 201, others 409 | [TC-UROLE-010](#tc-urole-010--concurrent-assignments-of-one-role) | designed |
| R11 | sequence locks | the target user and the role are locked FOR UPDATE before the 403 | [TC-UROLE-011](#tc-urole-011--user-and-role-locks) | designed (FOR SHARE holder, so only this API's lock conflicts) |
| R12 | sequence failure branch | an unexpected failure is 500 without bizCode and nothing is kept | [TC-UROLE-012](#tc-urole-012--an-unexpected-failure-rolls-back) | designed (failure injected through a test repository) |

## Detailed test cases

### TC-UROLE-001 — Insert

- Source: R01. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** an ACTIVE user U and role R; VR `{"userId":U,"roleId":R}`. **Expected:** 201 S10000 "Insert User Role Success"; the row has U, R, ACTIVE and created_by = the caller.

### TC-UROLE-002 — Update, archive, reopen and delete

- Source: R02. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a seeded assignment A of U and R. **Expected:** LOCKED → 200 "Update User Role Success" with the same id, updated_by = the caller, created_by "seed"; ARCHIVED → 200 "Archive User Role Success"; no rowStatus → 200 and ACTIVE again; DELETED → 204; A again → 404 E10004 "User role not found."; a new insert of U and R → 201 with a new id.

### TC-UROLE-003 — Input validation

- Source: R03. Design readiness: Ready. Execution status: Pass (automated).

| Body | Expected `bizMessage` (400 E10001) |
| --- | --- |
| `[]` | `Request Body must be an object.` |
| with `"extra":1` | `Extra is not a known field.` |
| `userId` twice | `User Id must not be duplicated.` |
| `{"userId":null,"roleId":""}` | `User Id and Role Id are required fields.` |
| `userId` "x" | `User Id must be a valid UUID.` |
| `id` "x" and `roleId` "y" | `Id must be a valid UUID, Role Id must be a valid UUID.` |
| insert with rowStatus DELETED | `Row status must not be DELETED when inserting a user role.` |
| rowStatus GONE | `Row Status must be ACTIVE, INACTIVE, DELETED, LOCKED or ARCHIVED.` |

### TC-UROLE-004 — Validation before the credential and credential failures

- Source: R04. Design readiness: Ready. Execution status: Pass (automated).

**Requests:** no token with invalid UUIDs → 400 with both messages; no token, a JWT without roles, an ADMIN whose stored token is INACTIVE → each 401 E10002. **Expected:** no assignment stored.

### TC-UROLE-005 — The target user must exist and the request must give to ACTIVE rows

- Source: R05. Design readiness: Ready. Execution status: Pass (automated).

**Steps and expected:** a random userId → 404 E10005 "User not found."; a CUSTOMER deleting a random id of a random user → the same 404 (before 403). A LOCKED user, an INACTIVE role or a random roleId on insert → 404 E10005 "User or role not found or not ACTIVE."; reopening an INACTIVE assignment of the LOCKED user → the same 404; deleting it → 204. An ACTIVE assignment whose role was LOCKED afterwards, updated to ACTIVE → 200.

### TC-UROLE-006 — The assignment id and its fixed user and role

- Source: R06. Design readiness: Ready. Execution status: Pass (automated).

**Expected:** a random id → 404 E10004 "User role not found."; a DELETED assignment's id → the same; another user or another role with an existing id → 400 E10001 "User Id and Role Id cannot be changed.".

### TC-UROLE-007 — Only a platform administrator, before the duplicate check

- Source: R07. Design readiness: Ready. Execution status: Pass (automated).

**Request:** callers `[]`, `["CUSTOMER"]`, `["platform_admin"]` insert an existing pair, and insert the PLATFORM_ADMIN role for a new user. **Expected:** every answer 403 E10009 "You do not have permission to assign roles.".

### TC-UROLE-008 — Duplicate assignment

- Source: R08. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** an ARCHIVED assignment of U and R; insert U and R. **Expected:** 409 E10003 "The user already has this role."; still one non-DELETED row.

### TC-UROLE-009 — The platform keeps at least one administrator

- Source: R09. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** every other ACTIVE PLATFORM_ADMIN assignment is set INACTIVE for the case (restored afterwards), and an ACTIVE assignment of a LOCKED user is added. **Expected:** the anchor assignment set to INACTIVE, LOCKED, ARCHIVED or DELETED → each 409 E10006 "The platform must keep at least one administrator." and the anchor stays ACTIVE; a second administrator is inserted (201) and then deleted (204).

### TC-UROLE-010 — Concurrent assignments of one role

- Source: R10. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** four ADMIN callers insert U and R at once. **Expected:** one 201; the others 409 E10003 "The user already has this role."; one row.

### TC-UROLE-011 — User and role locks

- Source: R11. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** with a 1-second timeout, another session holds the target user FOR SHARE, then the role FOR SHARE; a CUSTOMER inserts U and R each time → 408 E90001. Released → 403 E10009.

### TC-UROLE-012 — An unexpected failure rolls back

- Source: R12. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a test repository throws after the insert. **Expected:** 500 "An unexpected error occurred." without bizCode; no assignment of U and R.

## Revision and execution history

- 2026-11-22: first version (Drake), executed by the automated tests of e-commerce-backend on branch `feat/drake-author-08-17` (`9da4517`, `0878964`, PR e-commerce-backend#33): `UpsertUserRoleApiTests` (HTTP + real PostgreSQL 17). Result: every case passes (dotnet test (full solution, branch feat/drake-author-08-17): Api 643, Application 43, Domain 73, Infrastructure 53, 0 failed). A mutation that counted an ACTIVE assignment of a user who is not ACTIVE as an administrator first survived; TC-UROLE-009 was extended (`0878964`) and now fails it. The duplicate precheck survives its mutation (the unique index gives the same 409).
