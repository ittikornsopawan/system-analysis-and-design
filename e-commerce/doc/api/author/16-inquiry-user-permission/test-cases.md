---
name: "Inquiry User Permission API Test Cases"
description: "Documented scenarios and expected results for GET v1/author/user/permission, the permissions given directly to users with their scope; use for test planning and for the automated backend tests named after each case ID."
---

# Inquiry User Permission API Test Cases

## Source baseline and scope

- Method/path: `GET v1/author/user/permission`
- Governing sources: [spec.md](spec.md), [sequence.wsd](sequence.wsd) (filters, sort, mapping), [11 test cases](../11-inquiry-user-role/test-cases.md) (the same query rules), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md)
- Source revision: `spec.md` and `sequence.wsd` last changed in `7180285`
- Source approval: approved (`approved_by: Josh (SA Lead, delegated by Ittikorn 2026-11-17)`, `approved_at: 2026-11-17T20:23:48+07:00`)
- Test design baseline: approved-source
- Scope and exclusions: TLS excluded; no rate limit in the spec. A grant without a scope next to a scoped grant of the same user and permission cannot be made through API 15; it is seeded directly to observe "no scope last".
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database and callers:** as in the 03 test cases; users get display names in `authen.m_user`; grants are seeded directly.
- **Valid request (VR):** `GET v1/author/user/permission`, `authorization: Bearer <ADMIN>`, `timestamp: <now UTC>`, no body.
- **Observation:** HTTP response (five data keys; each item exactly userPermissionId, userId, userDisplayName, permissionId, permissionName, permissionScopeId, scopeId, scope, rowStatus); the grant row after the call.

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| R01 | spec Success; sequence sort and mapping | 200 S10000 "Inquiry User Permission Success"; exact keys; permission name, then display name (null last), then scope code (no scope last), then id; scope fields null without a scope; closed masters still shown; DELETED never returned | [TC-UPERMQ-001](#tc-upermq-001--items-sorted-with-their-scope-deleted-excluded) | designed |
| R02 | spec filters; paging | userId, permissionId, rowStatus and id combine by AND; a missing or DELETED id is an empty 200 with totals 0/0; page 2 and beyond range | [TC-UPERMQ-002](#tc-upermq-002--filters-combine-and-pagination) | designed |
| R03 | sequence validation note | UUID filters, page rules, rowStatus values, unknown and repeated keys, joined messages | [TC-UPERMQ-003](#tc-upermq-003--query-validation) | designed |
| R04 | sequence order; permission rule | no body; 400 before 401; credential failures (incl. user not ACTIVE) 401; only exact PLATFORM_ADMIN, else 403 | [TC-UPERMQ-004](#tc-upermq-004--body-order-credentials-and-403) | designed |
| R05 | spec "No locks or writes"; timeout; page count check | row locks on the grant, user, permission, definition and scope do not block; nothing written; a table lock times out 408; a disagreeing page is 500 | [TC-UPERMQ-005](#tc-upermq-005--no-lock-timeout-and-a-disagreeing-page) | designed |

## Detailed test cases

### TC-UPERMQ-001 — Items sorted with their scope, DELETED excluded

- Source: R01. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** users "Amy", "Bob" and one without a display name; permission `a<t>.manage` with scopes `a_<t>` (ACTIVE, definition ACTIVE) and `z_<t>` (master LOCKED, definition INACTIVE); permission `b<t>.manage` LOCKED without scopes. Grants: Bob z; Amy z (LOCKED); Amy a; unnamed a; Amy without a scope; Bob on `b…` ARCHIVED; Amy on `b…` DELETED. **Expected:** `?permissionId=<a…>` → Amy a, Amy z (LOCKED), Amy no scope (three scope fields null), Bob z, unnamed a, each with its definition, scope id and code; `?permissionId=<b…>` → only Bob's ARCHIVED grant with null scope fields.

### TC-UPERMQ-002 — Filters combine and pagination

- Source: R02. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** user U with grants g1 (a…), g2 (b…, INACTIVE), g3 (c…); another user with a… and a DELETED b… grant. **Expected:** `?userId=U` → g1, g2, g3; `&rowStatus=INACTIVE` → g2; `&permissionId=<a…>` → g1; `?id=g3` → g3; `?id=g3&userId=<other>` → empty; `?id=<DELETED>` and `?id=<random>` → empty, totals 0/0; `?userId=U&pageIndex=2&pageSize=2` → g3, totals 3/2; `pageIndex=9` → empty, totals 3/2.

### TC-UPERMQ-003 — Query validation

- Source: R03. Design readiness: Ready. Execution status: Pass (automated).

| Query | Expected `bizMessage` (400 E10001) |
| --- | --- |
| `id=abc` | `Id must be a valid UUID.` |
| `userId=abc` | `User Id must be a valid UUID.` |
| `permissionId=` | `Permission Id must be a valid UUID.` |
| `pageSize=101` | `Page Index and Page Size must be greater than 0, Page Size must not be greater than 100.` |
| `pageIndex=9223372036854775807&pageSize=100` | `Page Index is too large for Page Size.` |
| `rowStatus=DELETED` | `Row status must be one of ACTIVE, INACTIVE, LOCKED, ARCHIVED.` |
| `roleId=a` | `Role Id is not a known field.` |
| `permissionId=a&permissionId=b` | `Permission Id must not be duplicated.` |
| `id=x&permissionId=y&pageIndex=0` | `Id must be a valid UUID, Permission Id must be a valid UUID, Page Index and Page Size must be greater than 0, Page Size must not be greater than 100.` |

### TC-UPERMQ-004 — Body, order, credentials and 403

- Source: R04. Design readiness: Ready. Execution status: Pass (automated).

**Requests:** body `{}` → 400 "Request Body must be empty."; no token with `?permissionId=x` → 400; no token, no roles claim, and an ADMIN whose user is INACTIVE → each 401 E10002; callers `[]`, `["CUSTOMER"]`, `["platform_admin"]` → 403 E10009 "You do not have permission to read user permissions.".

### TC-UPERMQ-005 — No lock, timeout and a disagreeing page

- Source: R05. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** with a 1-second timeout, another session holds FOR UPDATE on the grant, then the user, the permission, the definition and the scope; `?id=<G>` → 200 with G each time; G's updated_by stays NULL. `LOCK TABLE author.t_user_permission IN ACCESS EXCLUSIVE MODE` → 408 E90001. A test repository drops the first row of each page → 500 without bizCode.

## Revision and execution history

- 2026-11-22: first version (Drake), executed by the automated tests of e-commerce-backend on branch `feat/drake-author-08-17` (`22d24cd`, PR e-commerce-backend#33): `InquiryUserPermissionApiTests` (HTTP + real PostgreSQL 17, 13 tests including the 9 validation rows). Result: every case passes (dotnet test (full solution, branch feat/drake-author-08-17): Api 643, Application 43, Domain 73, Infrastructure 53, 0 failed). Mutation checks (each applied after the commit, then undone); each made at least one test fail: DELETED rows shown (001, 002), no display-name sort (001), no scope sort (001), scope sorted descending (001), each of the four filters dropped (001, 002), the 403 message of another API (004).
