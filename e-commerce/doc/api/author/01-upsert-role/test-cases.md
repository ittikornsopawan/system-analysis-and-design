---
name: "Upsert Role API Test Cases"
description: "Documented scenarios and expected results for POST v1/author/role/upsert; use for test planning and for the automated backend tests named after each case ID."
---

# Upsert Role API Test Cases

## Source baseline and scope

- Method/path: `POST v1/author/role/upsert`
- Governing sources: [spec.md](spec.md) (body, rules, response examples, Database Relations), [sequence.wsd](sequence.wsd) (execution order, lock order, system-role and in-use notes), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md)
- Source revision: Showcase `main` at the commit that adds this file; `spec.md` and `sequence.wsd` last changed in `b533d83`
- Source approval: approved (`approved_by: Ittikorn`, `approved_at: 2026-11-16T09:24:57+07:00`); owner-confirmed API review Q2/Q4/Q7/Q10/Q13/Q15
- Test design baseline: approved-source, except gap G1 (message forms by convention, accepted by Josh 2026-11-20)
- Scope and exclusions: one role per request (the batch is spec 02); TLS excluded; no rate limit in the spec.
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database:** throw-away PostgreSQL 17 with every Showcase migration (backend `PostgresFixture`), sessions in UTC. The shared database holds the seeded `PLATFORM_ADMIN` role once (added by the test when missing); every other role has a unique generated code.
- **Callers:** each case registers its own user with an ACTIVE stored access token whose JWT carries the `roles` claim it needs: `["PLATFORM_ADMIN"]` (ADMIN), `[]`, `["CUSTOMER"]`, `["platform_admin"]`, or a missing/malformed claim.
- **Valid request (VR):** `authorization: Bearer <ADMIN>`, `content-type: application/json`, `timestamp: <now UTC>`, body `{"name": <unique code>, "description": "A role"}`.
- **Observation:** HTTP response; the `author.m_role` row (name, description, row_status, created_by, updated_by).

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| R01 | spec Success - Insert; sequence data note | no id → insert, 201 S10000 "Insert Role Success", data exactly `roleId`; created_by = caller UUID, status ACTIVE by default; insert-ARCHIVED is an insert | [TC-ROLE-001](#tc-role-001--insert) | designed |
| R02 | spec Success - Update; "INACTIVE, LOCKED and ARCHIVED are reversible" | id → 200 "Update Role Success"; updated_by = caller; created_by unchanged; ACTIVE reopens | [TC-ROLE-002](#tc-role-002--update-and-reopen) | designed |
| R03 | spec Archive / Delete; "DELETED is final" | ARCHIVED → 200 "Archive Role Success"; DELETED → 204 no body; a DELETED id is 404; its name can be used again | [TC-ROLE-003](#tc-role-003--archive-delete-and-reuse-the-name) | designed |
| R04 | sequence validation note; Fail - Bad Request examples | name/description required and non-blank (also for delete/archive); role code `^[A-Z][A-Z0-9_]{0,63}$`, never trimmed; description ≤ 256; id a UUID (null refused); rowStatus one of five; insert-DELETED; JSON kinds; unknown, repeated and query keys | [TC-ROLE-004](#tc-role-004--input-validation) | designed; forms G1 |
| R05 | sequence order | every 400 before the JWT check (401) | [TC-ROLE-005](#tc-role-005--validation-before-the-credential) | designed |
| R06 | sequence JWT and credential notes | missing/invalid JWT, missing or malformed `roles` claim (not an array, duplicates, empty name), unstored, revoked token or non-ACTIVE user → 401 E10002 | [TC-ROLE-006](#tc-role-006--credential-failures) | designed |
| R07 | spec Permission; sequence "after the existence check and before conflicts" | only exact `PLATFORM_ADMIN` in the token → otherwise 403 E10009; for an id, 404 comes first | [TC-ROLE-007](#tc-role-007--only-a-platform-administrator) | designed |
| R08 | spec Not Found | an unknown or DELETED id → 404 E10004, nothing changed | [TC-ROLE-008](#tc-role-008--unknown-or-deleted-id) | designed |
| R09 | spec system role rule | any request naming `PLATFORM_ADMIN` by id → 409 E10006, row unchanged; a new role named `PLATFORM_ADMIN` → 409 E10003 | [TC-ROLE-009](#tc-role-009--the-system-role) | designed |
| R10 | spec uniqueness | another non-DELETED role (any status) with the name → 409 E10003; a role may keep its own name | [TC-ROLE-010](#tc-role-010--duplicate-name) | designed |
| R11 | spec in-use rule | DELETED/ARCHIVED refused (409 E10006) while a non-DELETED user or permission binding exists, of any status; INACTIVE/LOCKED allowed | [TC-ROLE-011](#tc-role-011--in-use-blocks-archive-and-delete) | designed |
| R12 | sequence 23505 note | concurrent inserts of one name → one 201, the rest 409 E10003 from `uq_m_role_name` | [TC-ROLE-012](#tc-role-012--concurrent-inserts-of-one-name) | designed |
| R13 | sequence lock order; failure branches | caller user locked, then the target role FOR UPDATE before 404/403; timeout → 408 E90001 | [TC-ROLE-013](#tc-role-013--the-caller-and-target-locks) | designed |
| R14 | sequence failure branches | an unexpected failure after a write → 500 without bizCode, nothing kept | [TC-ROLE-014](#tc-role-014--an-unexpected-failure-rolls-back) | designed |

## Detailed test cases

### TC-ROLE-001 — Insert

- Source: R01. Design readiness: Ready. Execution status: Pass (automated).

**Request:** VR with description "Manages the catalogue"; then VR with `rowStatus: "ARCHIVED"`. **Expected:** 201, "Created", S10000 "Insert Role Success", `data` exactly `{roleId}`; the row has the name and description as sent, row_status ACTIVE, created_by = the caller's UUID, updated_by NULL; the second row is ARCHIVED.

### TC-ROLE-002 — Update and reopen

- Source: R02. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a seeded role; VR with its id, a new name, "New text" and `LOCKED`; then the same without rowStatus. **Expected:** 200 "Update Role Success" with the same roleId; name, description and LOCKED stored, created_by still "seed", updated_by = caller; the second request makes it ACTIVE.

### TC-ROLE-003 — Archive, delete and reuse the name

- Source: R03. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a seeded role; `ARCHIVED` → 200 "Archive Role Success"; `DELETED` → 204 with an empty body; the same id again → 404 "Role not found."; an insert with the deleted role's name → 201.

### TC-ROLE-004 — Input validation

- Source: R04. Design readiness: Ready (forms per G1). Execution status: Pass (automated).

**Request (each 400 E10001, no data):** name missing → "Name is a required field."; `{"name":" ","description":null}` and `{}` → "Name and Description are required fields."; name `catalog_manager`, `1ROLE`, `" ROLE"`, `ROLE-A`, 65 characters → "Role name must be capital letters, digits and _, starting with a letter, at most 64 characters."; insert with `DELETED` → "Row status must not be DELETED when inserting a role."; rowStatus `active` → "Row Status must be ACTIVE, INACTIVE, DELETED, LOCKED or ARCHIVED."; id `abc` or `null` → "Id must be a valid UUID."; name `1` (a number) → "Name must be a string."; key `isAdmin` → "Is Admin is not a known field."; `name` given twice → "Name must not be duplicated."; `[]` → "Request Body must be an object."; description 257 characters → "Description must be at most 256 characters." (256 accepted); query `?userId=x` → "User Id is not a known field."; id `abc` with name `bad` → "Id must be a valid UUID, Role name must be capital letters, digits and _, starting with a letter, at most 64 characters." (field order).

### TC-ROLE-005 — Validation before the credential

- Source: R05. Design readiness: Ready. Execution status: Pass (automated).

**Request:** `{}` with no authorization; an invalid name with a JWT that has no roles claim. **Expected:** 400 E10001 each time, not 401.

### TC-ROLE-006 — Credential failures

- Source: R06. Design readiness: Ready. Execution status: Pass (automated).

**Request:** VR with: no authorization; a JWT signed with another key; a valid JWT with no stored row; roles claim missing, `"PLATFORM_ADMIN"` (a string), `["PLATFORM_ADMIN","PLATFORM_ADMIN"]`, `[""]`; the caller LOCKED; the stored token INACTIVE. **Expected:** 401 E10002 "Invalid or expired access token."; no row written.

### TC-ROLE-007 — Only a platform administrator

- Source: R07. Design readiness: Ready. Execution status: Pass (automated).

**Request:** with roles `[]`, `["CUSTOMER"]` and `["platform_admin"]`: an insert, an update of an existing role, an update of an unknown id. **Expected:** 403 E10009 "You do not have permission to manage roles." for the first two; 404 "Role not found." for the unknown id (existence is checked first).

### TC-ROLE-008 — Unknown or deleted id

- Source: R08. Design readiness: Ready. Execution status: Pass (automated).

**Request:** VR with a random id; with the id of a DELETED role. **Expected:** 404 E10004 "Role not found."; the DELETED row stays DELETED.

### TC-ROLE-009 — The system role

- Source: R09. Design readiness: Ready. Execution status: Pass (automated).

**Request:** the `PLATFORM_ADMIN` id with its own name and each status ACTIVE, INACTIVE, LOCKED, ARCHIVED, DELETED; the same id with a new name; an insert named `PLATFORM_ADMIN`. **Expected:** 409 E10006 "System role cannot be changed." for every id request, the row unchanged; 409 E10003 "Role name already exists." for the insert.

### TC-ROLE-010 — Duplicate name

- Source: R10. Design readiness: Ready. Execution status: Pass (automated).

**Request:** for a role with status ACTIVE, INACTIVE, LOCKED and ARCHIVED: an insert with its name, and an update of another role to its name; then an update that keeps a role's own name. **Expected:** 409 E10003 "Role name already exists." for each conflict; 200 for keeping the own name.

### TC-ROLE-011 — In use blocks archive and delete

- Source: R11. Design readiness: Ready. Execution status: Pass (automated).

**Preconditions:** role A has an INACTIVE `t_user_role` row; role B has an ACTIVE `t_role_permission` row. **Request:** ARCHIVED and DELETED for each; INACTIVE for each; DELETED for A after its binding becomes DELETED. **Expected:** 409 E10006 "Role is assigned to users or has permissions." for ARCHIVED and DELETED; 200 for INACTIVE; 204 after the binding is DELETED.

### TC-ROLE-012 — Concurrent inserts of one name

- Source: R12. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** four different administrators insert the same new name at once (different callers, so the caller lock does not queue them). **Expected:** exactly one 201; the others 409 E10003 "Role name already exists."; one row with that name.

### TC-ROLE-013 — The caller and target locks

- Source: R13. Design readiness: Ready. Execution status: Pass (automated).

**Steps (1-second command timeout):** another connection holds the target role FOR UPDATE, then the caller's user row FOR UPDATE, while the administrator updates the role; then it holds the role FOR SHARE while a `["CUSTOMER"]` caller updates it. **Expected:** 408 E90001 each time and the role unchanged; after release the customer gets 403 (the target lock is taken before the permission check).

### TC-ROLE-014 — An unexpected failure rolls back

- Source: R14. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a test-only repository throws right after inserting the role. **Expected:** 500 "An unexpected error occurred.", no bizCode; no role with that name.

## Open gaps and decisions

| Gap ID | Conflicting/missing sources | Affected obligations/cases | Missing decision or prerequisite | Status / decision reference |
| --- | --- | --- | --- | --- |
| G1 | the spec gives examples for the required fields, the role code and insert-DELETED only | R04 | messages for an invalid id, rowStatus, JSON kind, unknown, repeated and query keys, a long description and several failures | convention forms of api-conventions and of 07–10 (accepted by Josh 2026-11-20): "Id must be a valid UUID.", "Row Status must be ... or ARCHIVED.", "<Field> must be a string.", "<Field> is not a known field.", "<Field> must not be duplicated.", "Description must be at most 256 characters.", several failures joined in field order |

## Document verification and limitations

- Every obligation R01–R14 maps to a case, and every case cites its obligation.
- The "Check system role" query of the spec is answered from the locked target row's stored name (same row, same transaction); the guarded UPDATE also excludes `PLATFORM_ADMIN`.

## Revision and execution history

- 2026-11-20: first version (Drake), executed by the automated tests of e-commerce-backend on branch `feat/drake-author-01-upsert-role`: `UpsertRoleApiTests` (HTTP + real PostgreSQL 17, 31 tests including the 17 validation rows) and `JwtVerificationTests` (roles claim shape). Result: every case passes (`dotnet test`: Api 321, Application 43, Domain 73, Infrastructure 53, 0 failed). Mutation checks: removing the target `ForUpdate()` fails TC-ROLE-013; removing the system-role check fails TC-ROLE-009; removing the in-use check, or only its permission-binding half, fails TC-ROLE-011; removing the `uq_m_role_name` mapping fails TC-ROLE-012; accepting a malformed roles claim fails TC-ROLE-006; accepting repeated keys fails TC-ROLE-004. The first versions of TC-ROLE-012 and 013 let the 23505 and lock mutations survive (one caller queued the race; the UPDATE blocked anyway) and were strengthened before this run.
