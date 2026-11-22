---
name: "Upsert Role Permission API Test Cases"
description: "Documented scenarios and expected results for POST v1/author/role/permission/upsert with its scope items; use for test planning and for the automated backend tests named after each case ID."
---

# Upsert Role Permission API Test Cases

## Source baseline and scope

- Method/path: `POST v1/author/role/permission/upsert`
- Governing sources: [spec.md](spec.md), [sequence.wsd](sequence.wsd) (check order, scope items, locks), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md)
- Source revision: `spec.md` and `sequence.wsd` last changed in `7180285`
- Source approval: approved (`approved_by: Josh (SA Lead, delegated by Ittikorn 2026-11-17)`, `approved_at: 2026-11-17T20:23:48+07:00`)
- Test design baseline: approved-source
- Scope and exclusions: TLS excluded; no rate limit in the spec.
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database and callers:** as in the 03 test cases. `ScopedAsync` seeds a role, a permission, a scope and one ACTIVE scope definition of the permission; grants and grant scopes are seeded directly with created_by "seed".
- **Valid request (VR):** `POST v1/author/role/permission/upsert`, `authorization: Bearer <ADMIN>`, `timestamp: <now UTC>`, body `{"id"?, "roleId", "permissionId", "rowStatus"?, "scopes"?: [{"id"?, "scopeId", "rowStatus"?}]}`.
- **Observation:** HTTP response (`data.rolePermissionId`; 204 has no body); the `author.t_role_permission` and `author.t_role_permission_scope` rows.

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| R01 | spec Success | insert 201 with a scope link | [TC-RPERM-001](#tc-rperm-001--insert-with-a-scope) | designed |
| R02 | spec Success | update, archive, reopen; delete 204 deletes its links; a deleted grant is 404; the pair can be granted again | [TC-RPERM-002](#tc-rperm-002--update-archive-reopen-and-delete-with-its-scopes) | designed |
| R03 | spec body rules | shape, required, UUIDs, insert not DELETED, scopes an array, scope item rules and duplicates | [TC-RPERM-003](#tc-rperm-003--input-validation) | designed |
| R04 | sequence order | 400 before 401; credential failures 401 | [TC-RPERM-004](#tc-rperm-004--validation-before-the-credential-and-credential-failures) | designed |
| R05 | spec id, fixed keys, ACTIVE rules | missing id 404; role/permission fixed 400; giving needs ACTIVE role and permission (404 E10005); taking away does not | [TC-RPERM-005](#tc-rperm-005--the-grant-id-its-fixed-keys-and-active-rows-to-give) | designed |
| R06 | spec scope item rules | link not found 404; scope fixed 400; not a scope of the permission 400; a new link needs an ACTIVE definition and master (404 E10005); keeping one does not | [TC-RPERM-006](#tc-rperm-006--scope-items) | designed |
| R07 | spec permission rule | only exact PLATFORM_ADMIN; 403 before the duplicate check | [TC-RPERM-007](#tc-rperm-007--only-a-platform-administrator-before-the-duplicate-check) | designed |
| R08 | spec duplicate rules | duplicate grant 409; duplicate scope of a grant 409 at its position; delete-and-re-add in one request allowed | [TC-RPERM-008](#tc-rperm-008--duplicate-grant-and-scope) | designed |
| R09 | spec scoped-permission rule | an ACTIVE grant of a scoped permission needs an ACTIVE scope | [TC-RPERM-009](#tc-rperm-009--an-active-grant-of-a-scoped-permission-keeps-a-scope) | designed |
| R10 | sequence unique guard | concurrent inserts of one pair: one 201 | [TC-RPERM-010](#tc-rperm-010--concurrent-grants-of-one-pair) | designed |
| R11 | sequence locks | role and permission locked before the 403 | [TC-RPERM-011](#tc-rperm-011--role-and-permission-locks) | designed (FOR SHARE holder) |
| R12 | sequence failure branch | 500 without bizCode; the grant and its scopes rolled back | [TC-RPERM-012](#tc-rperm-012--an-unexpected-failure-rolls-back-the-grant-and-its-scopes) | designed (failure injected through a test repository) |

## Detailed test cases

### TC-RPERM-001 — Insert with a scope

- Source: R01. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** VR with role R, permission P and `scopes:[{scopeId:S}]` (S a scope of P). **Expected:** 201 "Insert Role Permission Success"; grant ACTIVE, created_by the caller, one ACTIVE scope link.

### TC-RPERM-002 — Update, archive, reopen and delete with its scopes

- Source: R02. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a seeded grant G with one link L. **Expected:** LOCKED → 200 "Update Role Permission Success", updated_by the caller; ARCHIVED → 200 "Archive Role Permission Success"; ACTIVE → 200; DELETED → 204 and both G and L DELETED; G again → 404 E10004 "Role permission not found."; a new insert of R and P with S → 201 with a new id.

### TC-RPERM-003 — Input validation

- Source: R03. Design readiness: Ready. Execution status: Pass (automated).

| Body | Expected `bizMessage` (400 E10001) |
| --- | --- |
| `[]` | `Request Body must be an object.` |
| with `"extra":1` | `Extra is not a known field.` |
| `{"roleId":null}` | `Role Id and Permission Id are required fields.` |
| roleId "x" | `Role Id must be a valid UUID.` |
| insert with rowStatus DELETED | `Row status must not be DELETED when inserting a role permission.` |
| `"scopes":null` | `Scopes must be an array.` |
| a scope item with scopeId "x" | `scopes[0]: Scope Id must be a valid UUID.` |
| two items with one scopeId | `scopes[1]: Scope Id is duplicated with scopes[0].` |
| a new scope item with rowStatus DELETED | `scopes[0]: Row status must not be DELETED when inserting a scope.` |

### TC-RPERM-004 — Validation before the credential and credential failures

- Source: R04. Design readiness: Ready. Execution status: Pass (automated).

**Requests:** no token with invalid UUIDs → 400 with both messages; no token, no roles claim, a revoked stored token → each 401 E10002.

### TC-RPERM-005 — The grant id, its fixed keys and ACTIVE rows to give

- Source: R05. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** an INACTIVE grant G of R and P with a link. **Expected:** a random id → 404 E10004; another role with G → 400 "Role Id and Permission Id cannot be changed."; after R is LOCKED, reopening G → 404 E10005 "Role or permission not found or not ACTIVE."; an INACTIVE permission or a random permission on insert → the same 404; archiving G → 200 "Archive Role Permission Success".

### TC-RPERM-006 — Scope items

- Source: R06. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** an ACTIVE grant G of P with link L to S; P also has scope O. **Expected:** an item with a random link id → 404 E10004 `scopes[0]: Role permission scope not found.`; L with scopeId O → 400 `scopes[0]: Scope Id cannot be changed.`; a scope that is not P's → 400 `scopes[0]: Scope is not a scope of the permission.`; L used under another role's new grant → 404 at `scopes[0]`; O LOCKED, a new link to O → 404 E10005 `scopes[0]: Scope not found or not ACTIVE.`; S's definition INACTIVE, keeping L → 200.

### TC-RPERM-007 — Only a platform administrator, before the duplicate check

- Source: R07. Design readiness: Ready. Execution status: Pass (automated).

**Request:** callers `[]`, `["CUSTOMER"]`, `["platform_admin"]` insert an existing pair. **Expected:** each 403 E10009 "You do not have permission to assign permissions.".

### TC-RPERM-008 — Duplicate grant and scope

- Source: R08. Design readiness: Ready. Execution status: Pass (automated).

**Expected:** an ARCHIVED grant of R and P, then insert R and P → 409 E10003 "The role already has this permission."; a grant with link L to S, then a new item S → 409 E10003 `scopes[0]: The role already has this scope for the permission.`; [L DELETED, new S] → 200, L DELETED and one ACTIVE link.

### TC-RPERM-009 — An ACTIVE grant of a scoped permission keeps a scope

- Source: R09. Design readiness: Ready. Execution status: Pass (automated).

**Expected:** inserting R and a scoped P without scopes → 400 "An ACTIVE grant of a scoped permission needs at least one ACTIVE scope."; deleting the only link of an ACTIVE grant → the same 400 and the link stays ACTIVE; the same with the grant INACTIVE → 200; inserting a permission without scopes → 201.

### TC-RPERM-010 — Concurrent grants of one pair

- Source: R10. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** four ADMIN callers insert R and P at once. **Expected:** one 201; others 409 E10003 "The role already has this permission.".

### TC-RPERM-011 — Role and permission locks

- Source: R11. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** with a 1-second timeout, another session holds the role FOR SHARE, then the permission FOR SHARE; a CUSTOMER inserts R and P → 408 E90001 each time; released → 403 E10009.

### TC-RPERM-012 — An unexpected failure rolls back the grant and its scopes

- Source: R12. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a test repository throws after the scope insert; VR with one scope. **Expected:** 500 without bizCode; no grant for R.

## Revision and execution history

- 2026-11-22: first version (Drake), executed by the automated tests of e-commerce-backend on branch `feat/drake-author-08-17` (`805f1d5`, PR e-commerce-backend#33): `UpsertRolePermissionApiTests` (HTTP + real PostgreSQL 17). Result: every case passes (dotnet test (full solution, branch feat/drake-author-08-17): Api 643, Application 43, Domain 73, Infrastructure 53, 0 failed). Mutation checks were run while implementing; their individual results were not recorded, so none are listed here.
