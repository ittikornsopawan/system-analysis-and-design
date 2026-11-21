---
name: "Upsert Permission API Test Cases"
description: "Documented scenarios and expected results for POST v1/author/permission/upsert with its scope links; use for test planning and for the automated backend tests named after each case ID."
---

# Upsert Permission API Test Cases

## Source baseline and scope

- Method/path: `POST v1/author/permission/upsert`
- Governing sources: [spec.md](spec.md) (body, rules, response examples, Database Relations), [sequence.wsd](sequence.wsd) (execution order, lock order, Q22/Q23/Q24 notes), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md) (validation messages)
- Source revision: Showcase `main` at the commit that adds this file; `spec.md` and `sequence.wsd` last changed in `b533d83`
- Source approval: approved (`approved_by: Ittikorn`, `approved_at: 2026-11-16T09:24:57+07:00`); owner-confirmed API review Q22/Q23/Q24
- Test design baseline: approved-source, except gaps G1 and G2 (link message forms by convention)
- Scope and exclusions: TLS excluded; no rate limit in the spec. The guarded parent and link UPDATEs' zero-row 404s are not reachable from HTTP while this transaction holds the row locks; they stay defensive branches (R18).
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database:** throw-away PostgreSQL 17 with every Showcase migration (backend `PostgresFixture`), sessions in UTC. Each case seeds its own permissions (unique code `p<hex>.manage`), scope masters, links and grants.
- **Callers:** each case registers its own user with an ACTIVE stored access token whose JWT carries the `roles` claim it needs: `["PLATFORM_ADMIN"]` (ADMIN), `[]`, `["CUSTOMER"]`, `["platform_admin"]`, or a missing/malformed claim.
- **Body(name, description = "A permission", id?, rowStatus?, scopes...)**; **Scope(scopeId, id?, rowStatus?)**.
- **Grants:** a role grant (`t_role_permission`, optionally with a `t_role_permission_scope` on one link) and a direct-user grant (`t_user_permission`, INACTIVE, optionally on one link).
- **Observation:** HTTP response (`data` exactly `permissionId`); the `author.m_permission` row (name, row_status, created_by, updated_by, description) and the `author.t_permission_scope` rows (row_status, count of non-DELETED links).

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| R01 | spec Success - Insert | no id → 201 "Insert Permission Success", data exactly `permissionId`; created_by = caller; ACTIVE by default; links inserted | [TC-PERM-001](#tc-perm-001--insert-with-scopes) | designed |
| R02 | spec Update/Archive/Delete; "DELETED is final" | update 200, archive 200 "Archive Permission Success", ACTIVE reopens, delete 204; a DELETED id is 404 and its name is free; insert-ARCHIVED is 201 | [TC-PERM-002](#tc-perm-002--update-archive-reopen-and-delete) | designed |
| R03 | sequence validation notes; Bad Request examples | object of five known keys, no repeated key; required non-blank name/description; permission code; ≤ 64/256; parent status; insert-DELETED; `scopes` an array (null refused) of objects with id/scopeId/rowStatus; link id and scopeId UUIDs; link status ACTIVE/DELETED; link insert-DELETED; repeated link id; repeated scope among non-DELETED links; no query key | [TC-PERM-003](#tc-perm-003--input-validation) | designed; G1, G2 |
| R04 | sequence order; JWT and credential notes | every 400 before 401; missing/invalid JWT, missing roles claim, revoked token → 401 E10002, nothing written | [TC-PERM-004](#tc-perm-004--validation-before-the-credential-and-credential-failures) | designed |
| R05 | spec Permission; sequence "after parent existence and before scope/conflict work" | only exact PLATFORM_ADMIN; 403 E10009 "You do not have permission to manage permissions."; 404 for the permission first; 403 before the scope check | [TC-PERM-005](#tc-perm-005--only-a-platform-administrator-after-the-permission-lookup) | designed |
| R06 | spec scopeId rule; Q23 | an ACTIVE link needs an ACTIVE master (404 E10005 "Scope not found."); removing an existing link may name a closed master | [TC-PERM-006](#tc-perm-006--scope-masters-and-q23) | designed |
| R07 | spec link id rule; sequence child checks | a link id must be a non-DELETED link of this permission (404 E10004 "Permission scope not found."), also for a link id on an insert; its stored scope cannot change (400 E10001 "Scope Id cannot be changed.") | [TC-PERM-007](#tc-perm-007--link-ids-belong-to-the-permission-and-keep-their-scope) | designed |
| R08 | spec name uniqueness | another non-DELETED permission of any status with the name → 409 E10003; own name kept; a DELETED permission's name is free | [TC-PERM-008](#tc-perm-008--duplicate-name) | designed |
| R09 | spec in-use rule | DELETED/ARCHIVED refused (409 E10006 "Permission is used by roles or users.") while a non-DELETED role or direct-user grant of any status exists; INACTIVE allowed | [TC-PERM-009](#tc-perm-009--grants-block-delete-and-archive) | designed |
| R10 | sequence duplicate-link precheck | an existing non-DELETED link to the same scope → 409 E10003 "Scope already exists in the permission."; delete and re-add in one request also 409; a link may be sent unchanged | [TC-PERM-010](#tc-perm-010--duplicate-link) | designed |
| R11 | spec link in-use rule | removing a link referenced by a role-scope or direct-user grant → 409 E10006 "Scope is used by roles or users."; an unused link is removed | [TC-PERM-011](#tc-perm-011--a-used-link-cannot-be-removed) | designed |
| R12 | Q24 | delete with remaining links → 409 E10006 "Permission cannot be deleted while scope definitions remain."; ARCHIVED may keep links; removing every link and deleting in one request → 204 | [TC-PERM-012](#tc-perm-012--q24-delete-needs-zero-links) | designed |
| R13 | Q22 | removing the last link of a granted permission → 409 E10006 "Permission cannot become unscoped while assigned to roles or users." with everything rolled back; replacing it is allowed; an already unscoped permission keeps its grants | [TC-PERM-013](#tc-perm-013--q22-a-granted-permission-keeps-a-link) | designed |
| R14 | sequence 23505 note | concurrent inserts of one name → one 201, the rest 409 E10003 | [TC-PERM-014](#tc-perm-014--concurrent-inserts-of-one-name) | designed |
| R15 | sequence lock order | concurrent requests adding the same link to one permission → one 200, the rest 409 "Scope already exists in the permission." | [TC-PERM-015](#tc-perm-015--concurrent-links-of-one-scope) | designed |
| R16 | sequence lock order; timeout branch | caller user, permission and scope master locked (FOR UPDATE) before the checks; a held lock → 408 E90001, nothing written | [TC-PERM-016](#tc-perm-016--locks-time-out) | designed |
| R17 | sequence unexpected-failure branch | a failure after the link insert → 500 without bizCode; parent and links rolled back | [TC-PERM-017](#tc-perm-017--an-unexpected-failure-rolls-back-the-parent-and-links) | designed |
| R18 | guarded UPDATE zero rows → 404 | defensive: the rows are locked by this transaction | — | excluded (unreachable while locked) |

## Gaps

- **G1:** the spec has no message for a link sent with insert-DELETED. The case uses `scopes[i]: Row status must not be DELETED when inserting a scope.`, the form of the parent's message.
- **G2:** the spec has no message for a repeated link id or scope. The cases use the api-conventions batch form `scopes[i]: Id is duplicated with scopes[k].` and `scopes[i]: Scope Id is duplicated with scopes[k].` (the same form as author 02).

## Detailed test cases

### TC-PERM-001 — Insert with scopes

- Source: R01. Design readiness: Ready. Execution status: Pass (automated).

**Request:** Body(new code, "Reads reports", scopes: two ACTIVE scopes). **Expected:** 201 S10000 "Insert Permission Success", data exactly `permissionId`; the row has the name, ACTIVE, created_by = caller; two non-DELETED links.

### TC-PERM-002 — Update, archive, reopen and delete

- Source: R02. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** rename with LOCKED → 200 "Update Permission Success", same id, updated_by = caller; ARCHIVED → 200 "Archive Permission Success"; no rowStatus → ACTIVE; DELETED → 204 with no body; the same id again → 404 E10004 "Permission not found."; a new permission with the freed name → 201; a new permission with ARCHIVED → 201 and stored ARCHIVED.

### TC-PERM-003 — Input validation

- Source: R03. Design readiness: Ready (G1, G2). Execution status: Pass (automated).

| Body | Expected `bizMessage` (400 E10001) |
| --- | --- |
| `[]` | `Request Body must be an object.` |
| extra key `code` / `name` twice | `Code is not a known field.` / `Name must not be duplicated.` |
| `" "` and `""` | `Name and Description are required fields.` |
| `catalog`, `Catalog.manage`, `a.` + 63 × `b` | `Permission name must be lower-case letters, digits, _ and ., with at least two parts separated by a dot, at most 64 characters.` |
| insert with DELETED | `Row status must not be DELETED when inserting a permission.` |
| `"id": null` | `Id must be a valid UUID.` |
| `"scopes": null` | `Scopes must be an array.` |
| `scopes: [null]` / extra key / `{}` / `scopeId: "x"` | `scopes[0]: Scope must be an object.` / `scopes[0]: Extra is not a known field.` / `scopes[0]: Scope Id is a required field.` / `scopes[0]: Scope Id must be a valid UUID.` |
| link rowStatus INACTIVE / link insert with DELETED | `scopes[0]: Row Status must be ACTIVE or DELETED.` / `scopes[0]: Row status must not be DELETED when inserting a scope.` |
| the same scopeId twice (lower and upper case) / the same link id twice | `scopes[1]: Scope Id is duplicated with scopes[0].` / `scopes[1]: Id is duplicated with scopes[0].` |
| several failures | `Description is a required field, Permission name must be ..., scopes[0]: Scope Id must be a valid UUID.` |
| description of 257 / query `?x=1` | `Description must be at most 256 characters.` / `X is not a known field.` |

**Also:** a DELETED link and an ACTIVE link may name the same scope (no 400; this request ends 404 on its unknown permission id); a name of exactly 64 and a description of 256 are accepted (201).

### TC-PERM-004 — Validation before the credential and credential failures

- Source: R04. Design readiness: Ready. Execution status: Pass (automated).

**Requests:** no token with an invalid name → 400 (not 401); then a valid body with no token, `not-a-jwt`, a JWT without the roles claim, an ADMIN whose stored token is INACTIVE. **Expected:** each 401 E10002 "Invalid or expired access token."; no permission with the name.

### TC-PERM-005 — Only a platform administrator, after the permission lookup

- Source: R05. Design readiness: Ready. Execution status: Pass (automated).

**Request:** callers with `[]`, `["CUSTOMER"]`, `["platform_admin"]`: a new permission → 403; a DELETED permission id → 404 E10004 (before 403); an existing permission with an INACTIVE scope → 403 (before 404 E10005).

### TC-PERM-006 — Scope masters and Q23

- Source: R06. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a new permission linking an INACTIVE, a DELETED or an unknown scope → 404 E10005 "Scope not found." and nothing written. A permission with two links; one master is then LOCKED: keeping that link ACTIVE → 404 E10005; removing it (DELETED) → 200; the other link stays ACTIVE.

### TC-PERM-007 — Link ids belong to the permission and keep their scope

- Source: R07. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** permissions A and B with links. A with B's link id, with an unknown link id, a new permission with A's link id, A with a DELETED link of A → each 404 E10004 "Permission scope not found."; A's link with another scope → 400 E10001 "Scope Id cannot be changed.".

### TC-PERM-008 — Duplicate name

- Source: R08. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** an ARCHIVED permission holds N: insert N → 409 E10003 "Permission name already exists."; renaming another to N → 409; that permission keeping its own name → 200; a DELETED permission's name → 201.

### TC-PERM-009 — Grants block delete and archive

- Source: R09. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** one permission with a LOCKED role grant, one with an INACTIVE direct-user grant. For each: ARCHIVED and DELETED → 409 E10006 "Permission is used by roles or users."; INACTIVE → 200.

### TC-PERM-010 — Duplicate link

- Source: R10. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a permission with a link to S. Adding S again → 409 E10003 "Scope already exists in the permission."; removing the link and adding S in one request → 409 and the link stays ACTIVE; sending the link unchanged → 200.

### TC-PERM-011 — A used link cannot be removed

- Source: R11. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** three links: one used by a role-scope grant, one by a direct-user grant, one unused. Removing either used link → 409 E10006 "Scope is used by roles or users."; removing the unused one → 200. **Expected:** the used links stay ACTIVE, the unused one is DELETED.

### TC-PERM-012 — Q24: delete needs zero links

- Source: R12. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a permission with one link. DELETED → 409 E10006 "Permission cannot be deleted while scope definitions remain." and still ACTIVE; ARCHIVED → 200; DELETED with that link removed in the same request → 204, both rows DELETED.

### TC-PERM-013 — Q22: a granted permission keeps a link

- Source: R13. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a granted permission with one link. Removing it (with a new description) → 409 E10006 "Permission cannot become unscoped while assigned to roles or users."; the link is ACTIVE and the description still "seeded". Removing it and adding another scope → 200. A granted permission with no link updated → 200.

### TC-PERM-014 — Concurrent inserts of one name

- Source: R14. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** four administrators insert the same new code at once. **Expected:** one 201, the others 409 E10003 "Permission name already exists."; one row with the name.

### TC-PERM-015 — Concurrent links of one scope

- Source: R15. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** four administrators add the same scope to one permission at once. **Expected:** one 200, the others 409 E10003 "Scope already exists in the permission."; one link.

### TC-PERM-016 — Locks time out

- Source: R16. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** with a 1-second command timeout, another session holds FOR UPDATE on the caller's `m_user` row, then the permission, then the scope master; each time the admin updates the permission adding that scope → 408 E90001 and no link written. Then another session holds the permission FOR SHARE and a CUSTOMER sends an update → 408 (403 once released); another session holds the scope FOR SHARE and the admin inserts a taken name with that scope → 408 (409 once released). The FOR SHARE steps fail without this API's FOR UPDATE, which the FOR UPDATE steps alone cannot show.

### TC-PERM-017 — An unexpected failure rolls back the parent and links

- Source: R17. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a test repository throws after the link insert; insert a new permission with one scope. **Expected:** 500 "An unexpected error occurred." without bizCode; no permission with the name.

## Revision and execution history

- 2026-11-21: first version (Drake), executed by the automated tests of e-commerce-backend on branch `feat/drake-author-04-upsert-permission` (`6a1c93e`, after merging spec 03): `UpsertPermissionApiTests` (HTTP + real PostgreSQL 17, 35 tests including 18 validation rows). Result: every case passes (`dotnet test`: Api 414, Application 43, Domain 73, Infrastructure 53, 0 failed). Mutation checks, each failing its case: no 403 (005), no master check and no Q23 exception (006), scope change allowed and foreign link allowed (007), no grant check (009), no link precheck (010), no link in-use (011), no Q24 (012), no Q22 (013), no `uq_m_permission_name` mapping (014), a DELETED link reserving its scope (003), no scope lock and no permission lock (016). The first TC-PERM-016 held rows FOR UPDATE only, so removing either lock survived; the FOR SHARE steps were added before this run.
