---
name: "Upsert Role Batch API Test Cases"
description: "Documented scenarios and expected results for POST v1/author/role/upsert/batch; use for test planning and for the automated backend tests named after each case ID."
---

# Upsert Role Batch API Test Cases

## Source baseline and scope

- Method/path: `POST v1/author/role/upsert/batch`
- Governing sources: [spec.md](spec.md) (body, rules, response examples, Database Relations), [sequence.wsd](sequence.wsd) (execution order, lock order, request-order notes), [01 test cases](../01-upsert-role/test-cases.md) for the single-role rules, [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md) (Batch, validation messages)
- Source revision: Showcase `main` at the commit that adds this file; `spec.md` and `sequence.wsd` last changed in `b533d83`. Three rule lines of `spec.md` were cut with "..." (restored in #287); the full rules are read from `sequence.wsd`, which already holds them.
- Source approval: approved (`approved_by: Ittikorn`, `approved_at: 2026-11-16T09:24:57+07:00`); owner-confirmed API review Q2/Q4/Q7/Q10/Q13/Q15
- Test design baseline: approved-source, except gap G1 (message of a non-object item, by convention)
- Scope and exclusions: TLS excluded; no rate limit in the spec. The guarded UPDATE's zero-row 404 is not reachable from HTTP while the target is locked by this transaction; it stays a defensive branch (see R17).
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database:** throw-away PostgreSQL 17 with every Showcase migration (backend `PostgresFixture`), sessions in UTC. The shared database holds the seeded `PLATFORM_ADMIN` role once (added by the test when missing); every other role has a unique generated code.
- **Callers:** each case registers its own user with an ACTIVE stored access token whose JWT carries the `roles` claim it needs: `["PLATFORM_ADMIN"]` (ADMIN), `[]`, `["CUSTOMER"]`, `["platform_admin"]`, or a missing/malformed claim.
- **Item(name, description = "A role", id?, rowStatus?)**; **Batch(items...)** = `{"roles": [items]}`.
- **Valid request (VR):** `authorization: Bearer <ADMIN>`, `content-type: application/json`, `timestamp: <now UTC>`, body Batch(Item(<unique code>)).
- **Observation:** HTTP response (`data.roles[]` with exactly `index`, `roleId`, `action`); the `author.m_role` rows (name, description, row_status, created_by, updated_by) and their count by name.

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| R01 | spec Success; sequence result note | 200 S10000 "Batch Upsert Role Success" for any mix; `data` exactly `roles`; each result exactly index/roleId/action in request order; DELETE results stay in data; audit columns | [TC-RBATCH-001](#tc-rbatch-001--insert-update-delete-and-archive-in-one-batch) | designed |
| R02 | sequence action rule | insert-ARCHIVED is INSERT; ACTIVE/INACTIVE/LOCKED are UPDATE; omitted rowStatus is ACTIVE | [TC-RBATCH-002](#tc-rbatch-002--insert-archived-and-status-changes) | designed |
| R03 | spec validation rule; api-conventions Batch/Limits | only `roles`; no query key; roles required, an array, 1..100 items (100 accepted, 0 and 101 refused); repeated key; not an object | [TC-RBATCH-003](#tc-rbatch-003--request-level-validation) | designed |
| R04 | spec validation rule; 01 rules; Bad Request examples | each item an object of the four keys, no repeated key, string values; single-role rules; messages start with `roles[i]`, several joined in order | [TC-RBATCH-004](#tc-rbatch-004--item-validation) | designed; G1 |
| R05 | spec Duplicate Id/Name examples; sequence duplicate note | duplicated id compared as UUIDs; duplicated name among non-DELETED items; a DELETED item does not reserve its name | [TC-RBATCH-005](#tc-rbatch-005--duplicated-ids-and-names-in-the-request) | designed |
| R06 | sequence order | every 400 before the JWT check | [TC-RBATCH-006](#tc-rbatch-006--validation-before-the-credential) | designed |
| R07 | sequence JWT and credential notes | missing/invalid JWT, missing or malformed roles claim, revoked token → 401 E10002, nothing written | [TC-RBATCH-007](#tc-rbatch-007--credential-failures) | designed |
| R08 | sequence lock-then-existence note | first missing or DELETED target in request order → 404 E10004 `roles[i]`; before 403; nothing written | [TC-RBATCH-008](#tc-rbatch-008--first-missing-target-in-request-order) | designed |
| R09 | spec Permission; sequence 403 note | only exact `PLATFORM_ADMIN` in the token; otherwise one 403 E10009 with no position, before any conflict | [TC-RBATCH-009](#tc-rbatch-009--only-a-platform-administrator) | designed |
| R10 | spec system role rule | an item naming `PLATFORM_ADMIN` by id → 409 E10006 `roles[i]` for any status; a new role named `PLATFORM_ADMIN` → 409 E10003 | [TC-RBATCH-010](#tc-rbatch-010--the-system-role) | designed |
| R11 | sequence request-order note | conflict reads see the earlier items; no final-state rename plan; a role keeps its own name | [TC-RBATCH-011](#tc-rbatch-011--duplicate-names-follow-the-request-order) | designed |
| R12 | spec in-use rule | DELETED/ARCHIVED refused (409 E10006 `roles[i]`) while a non-DELETED user or permission binding of any status exists; INACTIVE allowed | [TC-RBATCH-012](#tc-rbatch-012--in-use-blocks-archive-and-delete) | designed |
| R13 | spec "If any role fails then no role is changed" | a failure at a later item keeps no earlier insert or update | [TC-RBATCH-013](#tc-rbatch-013--a-later-failure-keeps-no-earlier-item) | designed |
| R14 | sequence 23505 note | concurrent batches with one name → one 200, the rest 409 E10003 at the writing item's index | [TC-RBATCH-014](#tc-rbatch-014--concurrent-batches-with-one-name) | designed |
| R15 | sequence lock order; timeout branch | caller user and target roles locked; a held lock → 408 E90001; targets locked in id order so crossed batches finish | [TC-RBATCH-015](#tc-rbatch-015--locks-and-their-order) | designed; id order not observable (see the case) |
| R16 | sequence unexpected-failure branch | an unexpected failure at a later item → 500 without bizCode, nothing kept | [TC-RBATCH-016](#tc-rbatch-016--an-unexpected-failure-rolls-back-every-item) | designed |
| R17 | sequence guarded UPDATE zero rows → 404 | defensive: the row is locked by this transaction, so no HTTP fixture reaches it | — | excluded (unreachable while locked) |

## Gaps

- **G1:** the spec has no example for an item that is not an object. The message follows api-conventions "`<Field> must be an object.`" with the position first: `roles[0]: Role must be an object.`

## Detailed test cases

### TC-RBATCH-001 — Insert, update, delete and archive in one batch

- Source: R01. Design readiness: Ready. Execution status: Pass (automated).

**Request:** VR with Batch(Item(new, "New role"), Item(new name, "Renamed", A, INACTIVE), Item(B's name, "Gone", B, DELETED), Item(C's name, "Kept", C, ARCHIVED)). **Expected:** 200 "Ok", S10000 "Batch Upsert Role Success"; `data` has only `roles`; indexes 0..3, actions INSERT, UPDATE, DELETE, ARCHIVE, roleIds of A, B, C for items 1..3. The new row is ACTIVE with created_by = caller and no updated_by; A is renamed, INACTIVE, created_by "seed", updated_by = caller; B DELETED; C ARCHIVED.

### TC-RBATCH-002 — Insert-ARCHIVED and status changes

- Source: R02. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** Batch(Item(new, ARCHIVED), Item(INACTIVE role, LOCKED)); then Batch(Item(same role, no rowStatus)). **Expected:** actions INSERT and UPDATE; the new row is ARCHIVED, the role LOCKED; the second batch answers UPDATE and the role is ACTIVE.

### TC-RBATCH-003 — Request-level validation

- Source: R03. Design readiness: Ready. Execution status: Pass (automated).

| Body | Expected `bizMessage` (400 E10001) |
| --- | --- |
| `[]` | `Request Body must be an object.` |
| roles plus `"extra": 1` | `Extra is not a known field.` |
| `roles` twice | `Roles must not be duplicated.` |
| `{}` / `{"roles": null}` | `Roles is a required field.` |
| `{"roles": "A"}` | `Roles must be an array.` |
| `{"roles": []}` / 101 items | `Roles must contain 1 to 100 items.` (nothing written) |
| query `?dryRun=true` | `Dry Run is not a known field.` |

**Also:** 100 items → 200 with indexes 0..99.

### TC-RBATCH-004 — Item validation

- Source: R04. Design readiness: Ready (G1). Execution status: Pass (automated).

| Item(s) | Expected `bizMessage` (400 E10001) |
| --- | --- |
| `null` | `roles[0]: Role must be an object.` |
| extra key `code` | `roles[0]: Code is not a known field.` |
| `name` twice | `roles[0]: Name must not be duplicated.` |
| item 1 `"name": 1` | `roles[1]: Name must be a string.` |
| item 1 without name | `roles[1]: Name is a required field.` |
| `" "` and `""` | `roles[0]: Name and Description are required fields.` |
| item 1 `catalog` | `roles[1]: Role name must be capital letters, digits and _, starting with a letter, at most 64 characters.` |
| insert with DELETED | `roles[0]: Row status must not be DELETED when inserting a role.` |
| `"id": null` | `roles[0]: Id must be a valid UUID.` |
| rowStatus `GONE` | `roles[0]: Row Status must be ACTIVE, INACTIVE, DELETED, LOCKED or ARCHIVED.` |
| item 0 `a b`/`""`, item 1 no description | `roles[0]: Description is a required field, Role name must be capital letters, digits and _, starting with a letter, at most 64 characters, roles[1]: Description is a required field.` |
| description of 257 | `roles[0]: Description must be at most 256 characters.` |
| delete by id without name and description | `roles[0]: Name and Description are required fields.`; the role stays ACTIVE |

**Also:** a description of exactly 256 is accepted.

### TC-RBATCH-005 — Duplicated ids and names in the request

- Source: R05. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** Batch(new, Item(A by id), Item(A's id in upper case)) → 400 `roles[2]: Id is duplicated with roles[1].`; Batch(Item(N), Item(B by id), Item(N)) → 400 `roles[2]: Name is duplicated with roles[0].`; Batch(Item(A's name, A, DELETED), Item(A's name)) → 200 DELETE then INSERT, and the new row holds A's name.

### TC-RBATCH-006 — Validation before the credential

- Source: R06. Design readiness: Ready. Execution status: Pass (automated).

**Request:** no authorization, Batch(Item("bad name")) and `{"roles": []}`. **Expected:** 400 E10001 with the item and the count message, not 401.

### TC-RBATCH-007 — Credential failures

- Source: R07. Design readiness: Ready. Execution status: Pass (automated).

**Requests:** VR with no token, `not-a-jwt`, a JWT without the roles claim, a roles claim that is a string, and an ADMIN whose stored token is INACTIVE. **Expected:** each 401 E10002 "Invalid or expired access token."; no row with the name.

### TC-RBATCH-008 — First missing target in request order

- Source: R08. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** Batch(Item(new), Item(unknown id), Item(kept role, "Changed"), Item(id `00000000-0000-4000-8000-000000000001`, also unknown and sorting first)) → 404 `roles[1]: Role not found.`; Batch(Item(new), Item(DELETED role)) → 404 `roles[1]: Role not found.`; a CUSTOMER with Batch(Item(DELETED role)) → 404 `roles[0]: Role not found.` (before 403). **Expected:** no new row; the kept role unchanged.

### TC-RBATCH-009 — Only a platform administrator

- Source: R09. Design readiness: Ready. Execution status: Pass (automated).

**Request:** callers with `[]`, `["CUSTOMER"]`, `["platform_admin"]` send Batch(Item(new), Item("PLATFORM_ADMIN" by the system role's id), Item(existing role)). **Expected:** 403 E10009 "You do not have permission to manage roles." with no position (not the system-role 409); nothing changed.

### TC-RBATCH-010 — The system role

- Source: R10, R13. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** Batch(Item(new N), Item("PLATFORM_ADMIN", "Renamed", system id, status)) for no status, INACTIVE, DELETED, ARCHIVED → 409 E10006 `roles[1]: System role cannot be changed.`; Batch(Item(N), Item("PLATFORM_ADMIN")) → 409 E10003 `roles[1]: Role name already exists.` **Expected:** no row named N; the system role still ACTIVE.

### TC-RBATCH-011 — Duplicate names follow the request order

- Source: R11. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** A ACTIVE, B LOCKED. Batch(Item(B's name), Item(B's name, B, DELETED)) → 409 E10003 `roles[0]: Role name already exists.`; Batch(Item(B's name, A), Item(new name, B)) → 409 `roles[0]: Role name already exists.`; Batch(Item(A's name, "Own name", A)) → 200. **Expected:** A keeps its name, B stays LOCKED after the refused batches.

### TC-RBATCH-012 — In use blocks archive and delete

- Source: R12, R13. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a role with a LOCKED user binding and one with a permission binding; for each, Batch(Item(new N), Item(role, ARCHIVED or DELETED)) → 409 E10006 `roles[1]: Role is assigned to users or has permissions.`; Batch(Item(role, INACTIVE)) → 200. **Expected:** no row named N.

### TC-RBATCH-013 — A later failure keeps no earlier item

- Source: R13. Design readiness: Ready. Execution status: Pass (automated).

**Request:** Batch(Item(new N), Item(role U, "Changed"), Item(a name already taken)). **Expected:** 409 E10003 `roles[2]: Role name already exists.`; no row named N; U still has description "seeded" and no updated_by.

### TC-RBATCH-014 — Concurrent batches with one name

- Source: R14. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** four administrators (so the caller lock does not queue them) send Batch(Item(own new name), Item(shared N)) at once. **Expected:** exactly one 200; every other answer 409 E10003 `roles[1]: Role name already exists.` (from the name check or `uq_m_role_name`); exactly one row named N.

### TC-RBATCH-015 — Locks and their order

- Source: R15. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** with a 1-second command timeout, another session holds the caller's `m_user` row, then the target role, FOR UPDATE; Batch(Item(role A by id)). Then two administrators send Batch(A, B) and Batch(B, A) at once, five rounds. **Expected:** 408 E90001 "The server timed out waiting for the request." for both holds; every crossed batch answers 200 (no deadlock). **Limit:** PostgreSQL locks the rows of one statement in its scan order, the same for both batches, so removing `ORDER BY id` is not observable here; the order follows the spec SQL.

### TC-RBATCH-016 — An unexpected failure rolls back every item

- Source: R16. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a test repository throws after the second insert; Batch(Item(N1), Item(N2)). **Expected:** 500 "An unexpected error occurred." without bizCode; no row named N1 or N2.

## Revision and execution history

- 2026-11-21: first version (Drake), executed by the automated tests of e-commerce-backend on branch `feat/drake-author-02-upsert-role-batch` (`c703882`): `UpsertRoleBatchApiTests` (HTTP + real PostgreSQL 17, 34 tests including the 7 request-level and 11 item validation rows). Result: every case passes (`dotnet test`: Api 355, Application 43, Domain 73, Infrastructure 53, 0 failed). Mutation checks: no 403 fails TC-RBATCH-009; no 404 check fails TC-RBATCH-008; a DELETED item reserving its name or no duplicate-id check fails TC-RBATCH-005; no `uq_m_role_name` mapping or no current-item tracking fails TC-RBATCH-014; no target `ForUpdate()` fails TC-RBATCH-015. Removing `ORDER BY id` from the target lock survives (see TC-RBATCH-015). The first run of TC-RBATCH-015 held a role the batch did not target; the test was corrected before this run.
