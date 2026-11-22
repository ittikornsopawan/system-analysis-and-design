---
name: "Upsert User Permission API Test Cases"
description: "Documented scenarios and expected results for POST v1/author/user/permission/upsert, one direct grant per permission and scope; use for test planning and for the automated backend tests named after each case ID."
---

# Upsert User Permission API Test Cases

## Source baseline and scope

- Method/path: `POST v1/author/user/permission/upsert`
- Governing sources: [spec.md](spec.md), [sequence.wsd](sequence.wsd) (check order, the scope rule, locks), [10 test cases](../10-upsert-user-role/test-cases.md) (the same target-user rules), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md)
- Source revision: `spec.md` and `sequence.wsd` last changed in `7180285`
- Source approval: approved (`approved_by: Josh (SA Lead, delegated by Ittikorn 2026-11-17)`, `approved_at: 2026-11-17T20:23:48+07:00`)
- Test design baseline: approved-source
- Scope and exclusions: TLS excluded; no rate limit in the spec. The duplicate precheck is not separately observable: the two partial unique indexes (`uq_t_user_permission_*`, with and without a scope) answer the same 409 when it is removed.
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database and callers:** as in the 03 test cases; grants are seeded directly with created_by "seed" (`UserPermissionAsync`).
- **Valid request (VR):** `POST v1/author/user/permission/upsert`, `authorization: Bearer <ADMIN>`, `timestamp: <now UTC>`, body `{"id"?, "userId", "permissionId", "scopeId"?, "rowStatus"?}`.
- **Observation:** HTTP response (`data.userPermissionId`; 204 has no body); the `author.t_user_permission` row.

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| R01 | spec Success | insert 201 with and without a scope; the stored permission_scope_id is the definition of that scope | [TC-UPERM-001](#tc-uperm-001--insert-scoped-and-unscoped) | designed |
| R02 | spec Success | update, archive, reopen, delete 204; a deleted grant is 404 | [TC-UPERM-002](#tc-uperm-002--update-archive-reopen-and-delete) | designed |
| R03 | spec body rules | shape, unknown fields, required, UUIDs (scopeId null is not a UUID), insert not DELETED, joined messages | [TC-UPERM-003](#tc-uperm-003--input-validation) | designed |
| R04 | sequence order | 400 before 401; credential failures 401; a missing target user 404 E10005 "User not found." before 403; a missing id 404 E10004 | [TC-UPERM-004](#tc-uperm-004--validation-before-the-credential-credentials-and-the-target-user) | designed |
| R05 | spec scope rule; fixed keys | a scoped permission needs one of its scopes; an unscoped one takes none; user, permission and scope fixed (400) | [TC-UPERM-005](#tc-uperm-005--the-scope-rule-and-fixed-keys) | designed |
| R06 | spec ACTIVE rule | giving (insert or reopen) needs an ACTIVE user, permission, definition and scope (404 E10005); taking away does not | [TC-UPERM-006](#tc-uperm-006--active-rows-to-give) | designed |
| R07 | spec permission rule | only exact PLATFORM_ADMIN; 403 E10009 before the duplicate check | [TC-UPERM-007](#tc-uperm-007--only-a-platform-administrator-before-the-duplicate-check) | designed |
| R08 | spec duplicate rule | one grant per user, permission and scope (a non-DELETED row of any status); a second scope is a second grant | [TC-UPERM-008](#tc-uperm-008--duplicates-per-scope) | designed |
| R09 | sequence unique guard | concurrent inserts of one grant: one 201 | [TC-UPERM-009](#tc-uperm-009--concurrent-grants-of-one-scope) | designed |
| R10 | sequence locks | the target user and the permission locked before the 403 | [TC-UPERM-010](#tc-uperm-010--user-and-permission-locks) | designed (FOR SHARE holder) |
| R11 | sequence failure branch | 500 without bizCode; nothing kept | [TC-UPERM-011](#tc-uperm-011--an-unexpected-failure-rolls-back) | designed (failure injected through a test repository) |

## Detailed test cases

### TC-UPERM-001 — Insert, scoped and unscoped

- Source: R01. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a permission with scope S (definition D) and a permission without scopes. **Expected:** both inserts 201 "Insert User Permission Success"; the scoped row stores D, the unscoped row NULL; ACTIVE; created_by the caller.

### TC-UPERM-002 — Update, archive, reopen and delete

- Source: R02. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a seeded unscoped grant G. **Expected:** LOCKED → 200 "Update User Permission Success" with the same id, updated_by the caller; ARCHIVED → 200 "Archive User Permission Success"; ACTIVE → 200 "Update User Permission Success"; DELETED → 204; G again → 404 E10004 "User permission not found.".

### TC-UPERM-003 — Input validation

- Source: R03. Design readiness: Ready. Execution status: Pass (automated).

| Body | Expected `bizMessage` (400 E10001) |
| --- | --- |
| `[]` | `Request Body must be an object.` |
| with `"extra":1` | `Extra is not a known field.` |
| `{"userId":null}` | `User Id and Permission Id are required fields.` |
| `"scopeId":null` | `Scope Id must be a valid UUID.` |
| permissionId "y", scopeId "z" | `Permission Id must be a valid UUID, Scope Id must be a valid UUID.` |
| insert with rowStatus DELETED | `Row status must not be DELETED when inserting a user permission.` |

### TC-UPERM-004 — Validation before the credential, credentials and the target user

- Source: R04. Design readiness: Ready. Execution status: Pass (automated).

**Expected:** no token with invalid UUIDs → 400 with both messages; no token and no roles claim → 401 E10002; ADMIN with a random userId → 404 E10005 "User not found."; a CUSTOMER deleting a random id of a random user → the same 404 (before 403); ADMIN with a random id → 404 E10004 "User permission not found.".

### TC-UPERM-005 — The scope rule and fixed keys

- Source: R05. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** permission P with scope S (and later O); permission Q without scopes. **Expected:** P without scopeId → 400 "Scope Id is required for a permission that has scopes."; P with a scope that is not P's → 400 "Scope is not a scope of the permission."; Q with S → the same 400; a grant of P in S updated with scope O → 400 "User Id, Permission Id and Scope Id cannot be changed."; the same grant with another user → the same 400.

### TC-UPERM-006 — ACTIVE rows to give

- Source: R06. Design readiness: Ready. Execution status: Pass (automated).

**Expected:** each 404 E10005 "User, permission or scope not found or not ACTIVE.": a LOCKED user; an INACTIVE permission; a random permission; the scope master LOCKED. Reopening an INACTIVE grant whose scope is LOCKED → the same 404; deleting it → 204.

### TC-UPERM-007 — Only a platform administrator, before the duplicate check

- Source: R07. Design readiness: Ready. Execution status: Pass (automated).

**Request:** callers `[]`, `["CUSTOMER"]`, `["platform_admin"]` insert an existing grant. **Expected:** each 403 E10009 "You do not have permission to assign permissions.".

### TC-UPERM-008 — Duplicates per scope

- Source: R08. Design readiness: Ready. Execution status: Pass (automated).

**Expected:** an ARCHIVED unscoped grant, then the same insert → 409 E10003 "The user already has this permission in this scope."; a grant of P in S1, then P in S1 → the same 409; P in S2 → 201.

### TC-UPERM-009 — Concurrent grants of one scope

- Source: R09. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** four ADMIN callers insert one unscoped grant at once. **Expected:** one 201; others 409 E10003.

### TC-UPERM-010 — User and permission locks

- Source: R10. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** with a 1-second timeout, another session holds the target user FOR SHARE, then the permission FOR SHARE; a CUSTOMER inserts → 408 E90001 each time; released → 403 E10009.

### TC-UPERM-011 — An unexpected failure rolls back

- Source: R11. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a test repository throws after the insert. **Expected:** 500 "An unexpected error occurred." without bizCode; no grant for the user.

## Revision and execution history

- 2026-11-22: first version (Drake), executed by the automated tests of e-commerce-backend on branch `feat/drake-author-08-17` (`b1fd365`, PR e-commerce-backend#33): `UpsertUserPermissionApiTests` (HTTP + real PostgreSQL 17, 16 tests including the 6 validation rows). Result: every case passes (dotnet test (full solution, branch feat/drake-author-08-17): Api 643, Application 43, Domain 73, Infrastructure 53, 0 failed). Mutation checks (each applied after the commit, then undone); each made at least one test fail: no 403 (007), scopeId not required (005), a foreign scope accepted (005), no ACTIVE check (006), scope not ACTIVE accepted (006), user not ACTIVE accepted (006), scope or user change accepted (005), no target-user lock (004, 010), no permission lock (010), reopening not treated as giving (006). The duplicate precheck survives its mutation (the unique indexes give the same 409).
