---
name: "Inquiry Permission API Test Cases"
description: "Documented scenarios and expected results for GET v1/author/permission with each permission's scopes; use for test planning and for the automated backend tests named after each case ID."
---

# Inquiry Permission API Test Cases

## Source baseline and scope

- Method/path: `GET v1/author/permission`
- Governing sources: [spec.md](spec.md) (query table, response examples, Database Relations), [sequence.wsd](sequence.wsd) (execution order, scope mapping and ordering notes), [03 test cases](../03-inquiry-role/test-cases.md) (the same query rules), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md)
- Source revision: Showcase `main` at the commit that adds this file; `spec.md` and `sequence.wsd` last changed in `b533d83`
- Source approval: approved (`approved_by: Ittikorn`, `approved_at: 2026-11-16T09:24:57+07:00`)
- Test design baseline: approved-source
- Scope and exclusions: TLS excluded; no rate limit in the spec. The `ORDER BY p.name, p.id` tiebreak is not observable (`uq_m_permission_name` keeps returned names unique). A link whose master is missing cannot exist under the foreign key; it is exercised with a test repository (R12).
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database and callers:** as in the 03 test cases. Each case seeds its own permissions with a unique lower-case prefix (`q<hex>.<part>`) and isolates them with `search=<prefix>`; scope masters get a chosen code and the name `Name <code>`.
- **Valid request (VR):** `GET v1/author/permission`, `authorization: Bearer <ADMIN>`, `timestamp: <now UTC>`, no body.
- **Observation:** HTTP response (`data` exactly items, pageIndex, pageSize, totalItems, totalPages; each item exactly permissionId, name, description, scopes, rowStatus; each scope exactly permissionScopeId, scopeId, scope, scopeName, rowStatus); the `author.m_permission` row after the call.

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| R01 | spec Success; sequence mapping note | 200 S10000 "Inquiry Permission Success"; exact data, item and scope keys; DELETED permissions never returned; sorted by name | [TC-PERMQ-001](#tc-permq-001--items-with-their-scopes-sorted-and-deleted-excluded) | designed |
| R02 | sequence scope notes | scopes are the non-DELETED links of any link status; scope and scopeName from the master of any status; rowStatus is the link's; sorted by the master's code then id; `[]` when none | [TC-PERMQ-001](#tc-permq-001--items-with-their-scopes-sorted-and-deleted-excluded) | designed |
| R03 | spec query `id` | id combines with the other filters; a missing or DELETED id is an empty 200 with totals 0/0 | [TC-PERMQ-002](#tc-permq-002--by-id-combines-with-the-other-filters) | designed |
| R04 | spec search rule | name OR description, case-insensitive ILIKE; `%search%` keeps % and _; an empty search matches all | [TC-PERMQ-003](#tc-permq-003--search) | designed |
| R05 | spec query `rowStatus` | each of ACTIVE/INACTIVE/LOCKED/ARCHIVED filters; omitted means all non-DELETED | [TC-PERMQ-004](#tc-permq-004--row-status-filter) | designed |
| R06 | sequence paging note | page sizes and indexes; beyond range empty with totals kept; each page carries only its own permissions' scopes | [TC-PERMQ-005](#tc-permq-005--pagination-keeps-each-permissions-scopes) | designed |
| R07 | sequence validation note | the 03 query rules and messages; no body; every 400 before 401 | [TC-PERMQ-006](#tc-permq-006--query-validation) | designed |
| R08 | sequence JWT and credential notes | credential failures → 401 E10002 | [TC-PERMQ-007](#tc-permq-007--credential-failures) | designed |
| R09 | spec permission rule | only exact PLATFORM_ADMIN; 403 E10009 "You do not have permission to read permissions." the same for existing and unknown ids | [TC-PERMQ-008](#tc-permq-008--only-a-platform-administrator) | designed |
| R10 | spec "No locks or writes" | rows locked by another session (permission, link, master, caller) do not block; nothing written | [TC-PERMQ-009](#tc-permq-009--no-lock-and-no-write) | designed |
| R11 | sequence timeout branch | a read that cannot finish → 408 E90001 | [TC-PERMQ-010](#tc-permq-010--a-held-table-lock-times-out) | designed |
| R12 | sequence "page row count" and "one exact master" checks | a page that disagrees with its count, or a link whose master is not returned → 500 without bizCode | [TC-PERMQ-011](#tc-permq-011--a-page-or-master-that-disagrees-is-an-error) | designed; the explicit missing-master check is not separately observable (the lookup would throw the same 500) |
| R13 | sequence "skip master query" | a page without links runs no master query | [TC-PERMQ-012](#tc-permq-012--no-master-query-without-links) | designed (counted through a test repository) |

## Detailed test cases

### TC-PERMQ-001 — Items with their scopes, sorted, DELETED excluded

- Source: R01, R02. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** `<P>.b` ACTIVE, `<P>.a` LOCKED, `<P>.c` DELETED. `<P>.a` has an INACTIVE link to master `z_<t>` (ACTIVE), then an ACTIVE link to master `a_<t>` (LOCKED), and a DELETED link. VR `?search=<P>`. **Expected:** 200 S10000; items `<P>.a`, `<P>.b`; `<P>.a` description "seeded", LOCKED, scopes `[a_<t> (Name a_<t>, ACTIVE), z_<t> (Name z_<t>, INACTIVE)]` with their link and scope ids; `<P>.b` scopes `[]`; totals 2/1; `<P>.c` and the DELETED link absent.

### TC-PERMQ-002 — By id combines with the other filters

- Source: R03. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** an INACTIVE permission P: `?id=P` → one item, totals 1/1; `?id=P&rowStatus=ACTIVE`, `?id=P&search=no_such_<name>`, `?id=<DELETED>`, `?id=<random>` → each 200 with items `[]`, pageIndex 1, pageSize 10, totals 0/0.

### TC-PERMQ-003 — Search

- Source: R04. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a tag T in one permission's name, another's description (upper case), and a third's description as `T_9`. **Expected:** `?search=<T upper>&pageSize=100` returns all three; `?search=T_9` only the third; `?search=` the same total as no search.

### TC-PERMQ-004 — Row status filter

- Source: R05. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** one permission per status, DELETED included. **Expected:** each visible status returns only its permission; without rowStatus totalItems is 4.

### TC-PERMQ-005 — Pagination keeps each permission's scopes

- Source: R06. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** three permissions, each with its own link. **Expected:** `?pageIndex=2&pageSize=2` → only the third with only its link, totals 3/2; `?pageSize=2` → the first two, each with only its own link; `?pageIndex=9&pageSize=2` → items `[]`, totals kept; `?pageSize=100` → pageSize 100.

### TC-PERMQ-006 — Query validation

- Source: R07. Design readiness: Ready. Execution status: Pass (automated).

**Rows:** the twelve rows of TC-ROLEQ-006 (the same rules and messages; the test reuses them). **Also:** a JSON body `{}` → `Request Body must be empty.`; no token with `?pageSize=0` → 400, not 401.

### TC-PERMQ-007 — Credential failures

- Source: R08. Design readiness: Ready. Execution status: Pass (automated).

**Requests:** no token, `not-a-jwt`, a JWT without the roles claim, an ADMIN whose user is INACTIVE. **Expected:** each 401 E10002.

### TC-PERMQ-008 — Only a platform administrator

- Source: R09. Design readiness: Ready. Execution status: Pass (automated).

**Request:** callers with `[]`, `["CUSTOMER"]`, `["platform_admin"]`, with an existing and a random id. **Expected:** every answer 403 E10009 "You do not have permission to read permissions.".

### TC-PERMQ-009 — No lock and no write

- Source: R10. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** with a 1-second command timeout, another session holds FOR UPDATE on the permission, then its link, then the scope master, then the caller's `m_user` row; VR `?id=<P>` each time. **Expected:** 200 with the permission and its one scope every time; the permission's updated_by stays NULL.

### TC-PERMQ-010 — A held table lock times out

- Source: R11. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** another session holds `LOCK TABLE author.m_permission IN ACCESS EXCLUSIVE MODE`; VR with a 1-second timeout. **Expected:** 408 E90001.

### TC-PERMQ-011 — A page or master that disagrees is an error

- Source: R12. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a test repository drops the first row of each page; VR → 500. A test repository drops the first returned master; `?id=<P with one link>` → 500. **Expected:** both 500 "An unexpected error occurred." without bizCode.

### TC-PERMQ-012 — No master query without links

- Source: R13. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a permission without links; `?id=<P>` through a test repository that counts master queries. **Expected:** 200 with scopes `[]`; the count is unchanged.

## Revision and execution history

- 2026-11-21: first version (Drake), executed by the automated tests of e-commerce-backend on branch `feat/drake-author-06-inquiry-permission` (`d85ea76`): `InquiryPermissionApiTests` (HTTP + real PostgreSQL 17, 24 tests including the 12 reused validation rows). Result: every case passes (`dotnet test`: Api 466, Application 43, Domain 73, Infrastructure 53, 0 failed). Mutation checks, each failing its case: no 403 (008), no credential check (007), scopes unsorted (001), scopes not split by permission (005), the master query run without links (012), DELETED links shown (001), DELETED permissions shown (001), name-only search (003), closed masters dropped (001). The explicit missing-master check survives its mutation (the lookup throws the same 500).
