---
name: "Inquiry User Role API Test Cases"
description: "Documented scenarios and expected results for GET v1/author/user/role; use for test planning and for the automated backend tests named after each case ID."
---

# Inquiry User Role API Test Cases

## Source baseline and scope

- Method/path: `GET v1/author/user/role`
- Governing sources: [spec.md](spec.md), [sequence.wsd](sequence.wsd) (filters, sort, mapping), [03 test cases](../03-inquiry-role/test-cases.md) (the paging rules), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md)
- Source revision: `spec.md` and `sequence.wsd` last changed in `b533d83`
- Source approval: approved (`approved_by: Ittikorn`, `approved_at: 2026-11-16T09:24:57+07:00`)
- Test design baseline: approved-source
- Scope and exclusions: TLS excluded; no rate limit in the spec. Each case isolates its rows with `userId`, `roleId` or `id` filters.
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database and callers:** as in the 03 test cases; each case seeds its own users (display names set in `authen.m_user`), roles and assignments.
- **Valid request (VR):** `GET v1/author/user/role`, `authorization: Bearer <ADMIN>`, `timestamp: <now UTC>`, no body.
- **Observation:** HTTP response (`data` exactly items, pageIndex, pageSize, totalItems, totalPages; each item exactly userRoleId, userId, userDisplayName, roleId, roleName, rowStatus).

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| R01 | spec Success; sequence sort and mapping | 200 S10000 "Inquiry User Role Success"; exact keys; role name, then display name (null last), then id; DELETED never returned | [TC-UROLEQ-001](#tc-uroleq-001--by-role-sorted-by-display-name-deleted-excluded) | designed |
| R02 | spec filters; paging | id, userId, roleId and rowStatus combine by AND; page 2 and beyond range | [TC-UROLEQ-002](#tc-uroleq-002--filters-combine-and-pagination) | designed |
| R03 | sequence validation note | UUID filters, page rules, rowStatus values, unknown and repeated keys, joined messages | [TC-UROLEQ-003](#tc-uroleq-003--query-validation) | designed |
| R04 | sequence order; permission rule | no body; 400 before 401; credential failures 401; only exact PLATFORM_ADMIN, else 403 | [TC-UROLEQ-004](#tc-uroleq-004--body-order-credentials-and-403) | designed |
| R05 | spec "No locks or writes"; timeout; page count check | a row lock does not block; a table lock times out 408; a disagreeing page is 500 | [TC-UROLEQ-005](#tc-uroleq-005--no-lock-timeout-and-a-disagreeing-page) | designed |

## Detailed test cases

### TC-UROLEQ-001 — By role, sorted by display name, DELETED excluded

- Source: R01. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** role R; users "Bob", "Amy", one without a display name, and one more; assignments Bob ACTIVE, Amy LOCKED, the unnamed user ACTIVE, the last DELETED. VR `?roleId=R`. **Expected:** 200; items Amy (LOCKED), Bob (ACTIVE), the unnamed user (`userDisplayName` null), each with R's name; totals 3/1; the DELETED assignment absent.

### TC-UROLEQ-002 — Filters combine, and pagination

- Source: R02. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** user U with roles A_, B_ (INACTIVE), C_; another user with A_. **Expected:** `?userId=U` → the three in role-name order; `&rowStatus=INACTIVE` → B_ only; `&roleId=A_` → A_ only; `?id=<C_ assignment>` → it; `?id=<C_>&userId=<other>` → empty; `?userId=U&pageIndex=2&pageSize=2` → C_, totals 3/2; `pageIndex=9` → empty, totalItems 3.

### TC-UROLEQ-003 — Query validation

- Source: R03. Design readiness: Ready. Execution status: Pass (automated).

| Query | Expected `bizMessage` (400 E10001) |
| --- | --- |
| `id=abc` | `Id must be a valid UUID.` |
| `userId=abc` | `User Id must be a valid UUID.` |
| `roleId=` | `Role Id must be a valid UUID.` |
| `pageSize=101` | `Page Index and Page Size must be greater than 0, Page Size must not be greater than 100.` |
| `pageIndex=9223372036854775807&pageSize=100` | `Page Index is too large for Page Size.` |
| `rowStatus=DELETED` | `Row status must be one of ACTIVE, INACTIVE, LOCKED, ARCHIVED.` |
| `search=a` | `Search is not a known field.` |
| `userId=a&userId=b` | `User Id must not be duplicated.` |
| `id=x&roleId=y&pageIndex=0` | `Id must be a valid UUID, Role Id must be a valid UUID, Page Index and Page Size must be greater than 0, Page Size must not be greater than 100.` |

### TC-UROLEQ-004 — Body, order, credentials and 403

- Source: R04. Design readiness: Ready. Execution status: Pass (automated).

**Requests:** body `{}` → `Request Body must be empty.`; no token with `?userId=x` → 400; no token and a JWT without roles → 401 E10002; callers `[]`, `["CUSTOMER"]`, `["platform_admin"]` → 403 E10009 "You do not have permission to read user roles.".

### TC-UROLEQ-005 — No lock, timeout and a disagreeing page

- Source: R05. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** with a 1-second timeout, another session holds the assignment FOR UPDATE; `?id=<A>` → 200 with it. `LOCK TABLE author.t_user_role IN ACCESS EXCLUSIVE MODE` → 408 E90001. A test repository drops the first row of each page → 500 without bizCode.

## Revision and execution history

- 2026-11-22: first version (Drake), executed by the automated tests of e-commerce-backend on branch `feat/drake-author-08-17` (`662e3b3`, PR e-commerce-backend#33): `InquiryUserRoleApiTests` (HTTP + real PostgreSQL 17). Result: every case passes (dotnet test (full solution, branch feat/drake-author-08-17): Api 643, Application 43, Domain 73, Infrastructure 53, 0 failed). The first run failed with 500: EF Core cannot ORDER BY members of a record constructor projection; the repository now sorts a member-init row and maps it afterwards. Mutation checks were run while implementing; their individual results were not recorded, so none are listed here.
