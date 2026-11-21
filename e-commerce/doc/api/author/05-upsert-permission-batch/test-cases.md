---
name: "Upsert Permission Batch API Test Cases"
description: "Documented scenarios and expected results for POST v1/author/permission/upsert/batch; use for test planning and for the automated backend tests named after each case ID."
---

# Upsert Permission Batch API Test Cases

## Source baseline and scope

- Method/path: `POST v1/author/permission/upsert/batch`
- Governing sources: [spec.md](spec.md) (body, rules, response examples, Database Relations), [sequence.wsd](sequence.wsd) (execution order, lock order, request-order and Q22/Q23/Q24 notes), [04 test cases](../04-upsert-permission/test-cases.md) for the single-permission rules, [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md) (Batch, validation messages)
- Source revision: Showcase `main` at the commit that adds this file; `spec.md` and `sequence.wsd` last changed in `aa82b4a`
- Source approval: approved (`approved_by: Ittikorn`, `approved_at: 2026-11-16T09:24:57+07:00`); owner-confirmed API review Q22/Q23/Q24
- Test design baseline: approved-source; link message forms G1/G2 as in the 04 test cases
- Scope and exclusions: TLS excluded; no rate limit in the spec. Every single-permission rule runs through the same `PermissionWriter` as spec 04 and is tested there; these cases cover what the batch adds (positions, whole-batch rollback, request order, global locks). The guarded UPDATEs' zero-row 404s stay defensive branches (R14).
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database, callers, permission and link builders:** as in the 04 test cases (`Body`, `Scope` are shared with them).
- **Batch(items...)** = `{"permissions": [items]}`.
- **Valid request (VR):** `authorization: Bearer <ADMIN>`, `content-type: application/json`, `timestamp: <now UTC>`, body Batch(Body(<unique code>)).
- **Observation:** HTTP response (`data.permissions[]` with exactly `index`, `permissionId`, `action`); `author.m_permission` rows and their count by name; non-DELETED link counts.

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| R01 | spec Success; sequence mapping note | 200 S10000 "Batch Upsert Permission Success" for any mix; `data` exactly `permissions`; results exactly index/permissionId/action in request order, DELETE included; links written; audit | [TC-PBATCH-001](#tc-pbatch-001--insert-update-delete-and-archive-in-one-batch) | designed |
| R02 | spec validation rule; api-conventions Batch | only `permissions`; required array of 1..100 (100 accepted, 0 and 101 refused); repeated key; not an object; no query key | [TC-PBATCH-002](#tc-pbatch-002--request-level-validation) | designed |
| R03 | sequence validation note; Bad Request examples | each item a permission object, its links shaped; item rules of 04 with `permissions[i]`, link shapes with `permissions[i]: scopes[j]`; duplicated ids as UUIDs; duplicated names among non-DELETED items; a DELETED item does not reserve its name | [TC-PBATCH-003](#tc-pbatch-003--item-validation-and-duplicates) | designed |
| R04 | sequence order; JWT and credential notes | every 400 before 401; credential failures → 401 E10002, nothing written | [TC-PBATCH-004](#tc-pbatch-004--validation-before-the-credential-and-credential-failures) | designed |
| R05 | sequence lock-then-existence note | first missing or DELETED target in request order → 404 `permissions[i]: Permission not found.`; before 403; nothing written | [TC-PBATCH-005](#tc-pbatch-005--first-missing-target-in-request-order) | designed |
| R06 | spec Permission; sequence 403 note | one 403 E10009 with no position, before any scope check | [TC-PBATCH-006](#tc-pbatch-006--only-a-platform-administrator-once) | designed |
| R07 | sequence per-item checks; Fail examples | every item error after BEGIN starts with `permissions[i]` and keeps no earlier item: scope 404 E10005, link 404 E10004 (also a link of another permission in the same batch), changed scope 400, name 409 E10003, link duplicate 409 E10003, grants 409 E10006, Q24 409 E10006 | [TC-PBATCH-007](#tc-pbatch-007--every-item-error-names-its-position-and-rolls-back-the-batch) | designed |
| R08 | sequence per-item checks | link in use 409 E10006 and Q22 409 E10006 at a later item; nothing kept | [TC-PBATCH-008](#tc-pbatch-008--link-in-use-and-q22-at-a-later-item) | designed |
| R09 | sequence request-order note | an item sees the writes before it; a delete frees a name for a later insert; the reverse order and a rename onto a name released later are 409; no final-state plan | [TC-PBATCH-009](#tc-pbatch-009--items-see-the-writes-before-them) | designed |
| R10 | sequence 23505 note | concurrent batches with one name → one 200, the rest 409 at the writing item's index | [TC-PBATCH-010](#tc-pbatch-010--concurrent-batches-with-one-name) | designed |
| R11 | sequence lock order; timeout branch | caller, target permissions and scope masters locked; a held lock → 408; crossed batches finish without a deadlock | [TC-PBATCH-011](#tc-pbatch-011--locks-and-their-order) | designed; id order not observable |
| R12 | sequence unexpected-failure branch | a failure at a later item → 500 without bizCode, nothing kept | [TC-PBATCH-012](#tc-pbatch-012--an-unexpected-failure-rolls-back-every-item) | designed |
| R13 | 04 rules per item | single-permission rules (Q23 removal of a closed master, Q24 complete withdrawal, ARCHIVED keeps links) | [04 test cases](../04-upsert-permission/test-cases.md) | covered through the shared writer |
| R14 | guarded UPDATE zero rows → 404 | defensive: the rows are locked by this transaction | — | excluded (unreachable while locked) |

## Detailed test cases

### TC-PBATCH-001 — Insert, update, delete and archive in one batch

- Source: R01. Design readiness: Ready. Execution status: Pass (automated).

**Request:** Batch(Body(new, "New", scopes: one ACTIVE scope), Body(new name, "Renamed", A, INACTIVE), Body(B, "Gone", B, DELETED), Body(C, "Kept", C, ARCHIVED)). **Expected:** 200 "Ok", S10000 "Batch Upsert Permission Success"; indexes 0..3, actions INSERT, UPDATE, DELETE, ARCHIVE, the ids of A, B, C for items 1..3; the new permission ACTIVE with one link and created_by = caller; A renamed and INACTIVE; B DELETED; C ARCHIVED.

### TC-PBATCH-002 — Request-level validation

- Source: R02. Design readiness: Ready. Execution status: Pass (automated).

| Body | Expected `bizMessage` (400 E10001) |
| --- | --- |
| `[]` | `Request Body must be an object.` |
| permissions plus `"extra": 1` | `Extra is not a known field.` |
| `permissions` twice | `Permissions must not be duplicated.` |
| `{}` / `{"permissions": null}` | `Permissions is a required field.` |
| `{"permissions": "a"}` | `Permissions must be an array.` |
| `{"permissions": []}` / 101 items | `Permissions must contain 1 to 100 items.` (nothing written) |
| query `?dryRun=1` | `Dry Run is not a known field.` |

**Also:** 100 items → 200 with indexes 0..99.

### TC-PBATCH-003 — Item validation and duplicates

- Source: R03. Design readiness: Ready. Execution status: Pass (automated).

| Item(s) | Expected `bizMessage` (400 E10001) |
| --- | --- |
| `null` | `permissions[0]: Permission must be an object.` |
| extra key `code` | `permissions[0]: Code is not a known field.` |
| item 1 `"scopes": null` | `permissions[1]: Scopes must be an array.` |
| item 1 link with an extra key | `permissions[1]: scopes[0]: Extra is not a known field.` |
| item 1 link `scopeId: "x"` | `permissions[1]: scopes[0]: Scope Id must be a valid UUID.` |
| `name: "x"`, `description: ""` | `permissions[0]: Description is a required field, Permission name must be lower-case letters, digits, _ and ., with at least two parts separated by a dot, at most 64 characters.` |
| item 1 insert with DELETED | `permissions[1]: Row status must not be DELETED when inserting a permission.` |
| link insert with DELETED | `permissions[0]: scopes[0]: Row status must not be DELETED when inserting a scope.` |
| item 0 no name, item 1 no description | `permissions[0]: Name is a required field, permissions[1]: Description is a required field.` |

**Duplicates:** Batch(new, Body(A by id), A's id in upper case) → `permissions[2]: Id is duplicated with permissions[1].`; Batch(Body(N), Body(B by id), Body(N)) → `permissions[2]: Name is duplicated with permissions[0].`; Batch(Body(A's name, A, DELETED), Body(A's name)) → 200 DELETE then INSERT, the new permission holding A's name.

### TC-PBATCH-004 — Validation before the credential and credential failures

- Source: R04. Design readiness: Ready. Execution status: Pass (automated).

**Requests:** no token with an invalid name → 400 `permissions[0]: Permission name must be ...` (not 401); then a valid batch with no token, `not-a-jwt`, a JWT without the roles claim, an ADMIN whose stored token is INACTIVE → each 401 E10002; no permission with the name.

### TC-PBATCH-005 — First missing target in request order

- Source: R05. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** Batch(Body(new), Body(unknown id), Body(kept, "Changed"), Body(id `00000000-0000-4000-8000-000000000001`, also unknown and sorting first)) → 404 E10004 `permissions[1]: Permission not found.`; Batch(new, a DELETED permission) → `permissions[1]: ...`; a CUSTOMER with Batch(a DELETED permission) → `permissions[0]: ...` (before 403). **Expected:** no new permission; the kept one unchanged.

### TC-PBATCH-006 — Only a platform administrator, once

- Source: R06. Design readiness: Ready. Execution status: Pass (automated).

**Request:** callers with `[]`, `["CUSTOMER"]`, `["platform_admin"]` send Batch(Body(new), Body(existing, scopes: an INACTIVE scope)). **Expected:** 403 E10009 "You do not have permission to manage permissions." with no position (not the scope 404 of index 1).

### TC-PBATCH-007 — Every item error names its position and rolls back the batch

- Source: R07. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** each batch starts with a valid insert N at index 0; the item at index 1 fails:

| Item 1 | Expected |
| --- | --- |
| a new permission linking an INACTIVE scope | 404 E10005 `permissions[1]: Scope not found.` |
| W with the link id of a permission outside the batch | 404 E10004 `permissions[1]: Permission scope not found.` |
| W's link with another scope | 400 E10001 `permissions[1]: Scope Id cannot be changed.` |
| a new permission with W's name | 409 E10003 `permissions[1]: Permission name already exists.` |
| W adding the scope it already links | 409 E10003 `permissions[1]: Scope already exists in the permission.` |
| a granted permission ARCHIVED | 409 E10006 `permissions[1]: Permission is used by roles or users.` |
| W DELETED with its link remaining | 409 E10006 `permissions[1]: Permission cannot be deleted while scope definitions remain.` |

Then Batch(N, Body(O, id: O), Body(a taken name, id: W, scopes: O's link)) → 404 E10004 `permissions[2]: Permission scope not found.` (O's link is locked as part of the batch, but it is not W's; the ownership check answers before the name check). **Expected:** no permission named N; W still ACTIVE with one link.

### TC-PBATCH-008 — Link in use and Q22 at a later item

- Source: R08. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** P has two links, one used by a direct-user grant. Batch(N, Body(P, remove the used link)) → 409 E10006 `permissions[1]: Scope is used by roles or users.`. The grant is then moved to P itself (no link); Batch(N, Body(P, remove both links)) → 409 E10006 `permissions[1]: Permission cannot become unscoped while assigned to roles or users.`. **Expected:** no permission named N; P keeps two links.

### TC-PBATCH-009 — Items see the writes before them

- Source: R09. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** A ACTIVE, B LOCKED. Batch(Body(B's name), Body(B, DELETED)) → 409 E10003 `permissions[0]: Permission name already exists.`; Batch(Body(B's name, id: A), Body(new name, id: B)) → 409 `permissions[0]: ...`; A keeps its name and B stays LOCKED. Batch(Body(B, DELETED), Body(B's name)) → 200 DELETE then INSERT.

### TC-PBATCH-010 — Concurrent batches with one name

- Source: R10. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** four administrators send Batch(Body(own new name), Body(shared N)) at once. **Expected:** one 200; the others 409 E10003 `permissions[1]: Permission name already exists.`; one permission named N.

### TC-PBATCH-011 — Locks and their order

- Source: R11. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** with a 1-second command timeout: another session holds the caller's `m_user` row FOR UPDATE → 408 E90001. Another session holds B FOR SHARE and a CUSTOMER sends Batch(A, B) → 408 (403 once released). Another session holds a scope FOR SHARE and the admin sends Batch(Body(A's name), Body(new, scopes: that scope)) → 408 (409 at index 0 once released). Then two administrators send Batch(A, B) and Batch(B, A) at once, five rounds → every answer 200 (no deadlock). **Limit:** PostgreSQL locks one statement's rows in the same scan order for both batches, so the id order itself is not observable; it follows the spec SQL.

### TC-PBATCH-012 — An unexpected failure rolls back every item

- Source: R12. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a test repository throws after the second permission insert; Batch(Body(N1, scopes: one), Body(N2)). **Expected:** 500 "An unexpected error occurred." without bizCode; no permission named N1 or N2.

## Revision and execution history

- 2026-11-21: first version (Drake), executed by the automated tests of e-commerce-backend on branch `feat/drake-author-05-upsert-permission-batch` (`12eb6e8`): `UpsertPermissionBatchApiTests` (HTTP + real PostgreSQL 17, 28 tests including 7 request-level and 9 item validation rows). Result: every case passes (`dotnet test`: Api 442, Application 43, Domain 73, Infrastructure 53, 0 failed). Mutation checks, each failing its case: no 403 (006), no 404 check (005), current item not tracked and 23505 without position (010), a DELETED item reserving its name and no duplicate-id check (003), no ownership compare (007), no target lock (011), no Q22 in the shared writer (008). A reversed target lock order survives (not observable). The first TC-PBATCH-007 sent a foreign link without a name conflict, so the ownership mutation survived (the guarded link UPDATE gives the same 404); the taken name was added before this run.
