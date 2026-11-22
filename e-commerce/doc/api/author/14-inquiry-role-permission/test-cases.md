---
name: "Inquiry Role Permission API Test Cases"
description: "Documented scenarios and expected results for GET v1/author/role/permission with each grant's scopes; use for test planning and for the automated backend tests named after each case ID."
---

# Inquiry Role Permission API Test Cases

## Source baseline and scope

- Method/path: `GET v1/author/role/permission`
- Governing sources: [spec.md](spec.md), [sequence.wsd](sequence.wsd) (filters, sort, scope mapping), [11 test cases](../11-inquiry-user-role/test-cases.md) (the same query rules), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md)
- Source revision: `spec.md` and `sequence.wsd` last changed in `7180285`
- Source approval: approved (`approved_by: Josh (SA Lead, delegated by Ittikorn 2026-11-17)`, `approved_at: 2026-11-17T20:23:48+07:00`)
- Test design baseline: approved-source
- Scope and exclusions: TLS excluded; no rate limit in the spec.
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database and callers:** as in the 03 test cases; grants and grant scopes are seeded directly. Permission names start with a, b or c to fix their order.
- **Valid request (VR):** `GET v1/author/role/permission`, `authorization: Bearer <ADMIN>`, `timestamp: <now UTC>`, no body.
- **Observation:** HTTP response (five data keys; each item with its grant fields and `scopes[]` of rolePermissionScopeId, permissionScopeId, scopeId, scope, rowStatus).

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| R01 | spec Success; sequence sort and scope notes | 200 S10000 "Inquiry Role Permission Success"; grants by permission name; scopes are the non-DELETED links of any status, sorted by scope code, with the master of any status; DELETED grants never returned | [TC-RPERMQ-001](#tc-rpermq-001--by-role-sorted-with-scopes) | designed |
| R02 | spec filters; paging | roleId, permissionId, id and rowStatus combine by AND; each page carries only its own grants' scopes | [TC-RPERMQ-002](#tc-rpermq-002--filters-combine-pagination-and-scopes-per-grant) | designed |
| R03 | sequence validation note | UUID filters, page rules, rowStatus values, unknown keys, joined messages | [TC-RPERMQ-003](#tc-rpermq-003--query-validation) | designed |
| R04 | sequence order; permission rule | no body; 400 before 401; credential failures 401; only exact PLATFORM_ADMIN, else 403 "You do not have permission to read role permissions." | [TC-RPERMQ-004](#tc-rpermq-004--body-order-credentials-and-403) | designed |
| R05 | spec "No locks or writes"; timeout; page count check | a row lock does not block; a table lock times out 408; a disagreeing page is 500 | [TC-RPERMQ-005](#tc-rpermq-005--no-lock-timeout-and-a-disagreeing-page) | designed |

## Detailed test cases

### TC-RPERMQ-001 — By role, sorted, with scopes

- Source: R01. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** role R; grant of `b…` ACTIVE without links; grant of `a…` INACTIVE with links to `z_<t>` (master ACTIVE, link ACTIVE), `a_<t>` (master LOCKED, link INACTIVE) and a DELETED link; a DELETED grant of `c…`. VR `?roleId=R`. **Expected:** items `a…` (INACTIVE) then `b…`; `a…` scopes `[a_<t> INACTIVE, z_<t> ACTIVE]` with their link, definition and scope ids; `b…` scopes `[]`; totals 2/1; the DELETED grant and link absent.

### TC-RPERMQ-002 — Filters combine, pagination and scopes per grant

- Source: R02. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** role R with grants g1 (a), g2 (b, LOCKED), g3 (c, with link l3); another role with p1. **Expected:** `?roleId=R` → g1, g2, g3; `&rowStatus=LOCKED` → g2; `?permissionId=p1` → totalItems 2; `?id=g1&roleId=<other>` → empty; `?roleId=R&pageIndex=2&pageSize=2` → g3 with only l3, totals 3/2.

### TC-RPERMQ-003 — Query validation

- Source: R03. Design readiness: Ready. Execution status: Pass (automated).

| Query | Expected `bizMessage` (400 E10001) |
| --- | --- |
| `id=abc` | `Id must be a valid UUID.` |
| `roleId=abc` | `Role Id must be a valid UUID.` |
| `permissionId=` | `Permission Id must be a valid UUID.` |
| `pageSize=101` | `Page Index and Page Size must be greater than 0, Page Size must not be greater than 100.` |
| `rowStatus=DELETED` | `Row status must be one of ACTIVE, INACTIVE, LOCKED, ARCHIVED.` |
| `userId=a` | `User Id is not a known field.` |
| `roleId=x&permissionId=y` | `Role Id must be a valid UUID, Permission Id must be a valid UUID.` |

### TC-RPERMQ-004 — Body, order, credentials and 403

- Source: R04. Design readiness: Ready. Execution status: Pass (automated).

**Requests:** body `{}` → 400 "Request Body must be empty."; no token with an invalid filter → 400; no token and no roles claim → 401 E10002; callers `[]`, `["CUSTOMER"]`, `["platform_admin"]` → 403 E10009 "You do not have permission to read role permissions.".

### TC-RPERMQ-005 — No lock, timeout and a disagreeing page

- Source: R05. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** with a 1-second timeout, another session holds the grant FOR UPDATE; `?id=<G>` → 200 with it. `LOCK TABLE author.t_role_permission IN ACCESS EXCLUSIVE MODE` → 408 E90001. A test repository drops the first row of each page → 500 without bizCode.

## Revision and execution history

- 2026-11-22: first version (Drake), executed by the automated tests of e-commerce-backend on branch `feat/drake-author-08-17` (`a92391b`, `7da67cb`, PR e-commerce-backend#33): `InquiryRolePermissionApiTests` (HTTP + real PostgreSQL 17). Result: every case passes (dotnet test (full solution, branch feat/drake-author-08-17): Api 643, Application 43, Domain 73, Infrastructure 53, 0 failed). A mutation that returned DELETED grants first survived; TC-RPERMQ-001 now seeds a DELETED grant (`7da67cb`) and fails it.
