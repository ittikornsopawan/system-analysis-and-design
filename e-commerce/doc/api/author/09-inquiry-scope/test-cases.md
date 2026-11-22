---
name: "Inquiry Scope API Test Cases"
description: "Documented scenarios and expected results for GET v1/author/scope; use for test planning and for the automated backend tests named after each case ID."
---

# Inquiry Scope API Test Cases

## Source baseline and scope

- Method/path: `GET v1/author/scope`
- Governing sources: [spec.md](spec.md), [sequence.wsd](sequence.wsd), [03 test cases](../03-inquiry-role/test-cases.md) (the same query rules), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md)
- Source revision: `spec.md` and `sequence.wsd` last changed in `b533d83`
- Source approval: approved (`approved_by: Ittikorn`, `approved_at: 2026-11-16T09:24:57+07:00`)
- Test design baseline: approved-source
- Scope and exclusions: TLS excluded; no rate limit in the spec. The `id` tiebreak of the sort is not observable (`uq_m_scope_scope` keeps codes unique).
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database and callers:** as in the 03 test cases. Each case seeds its own scopes with a unique code prefix and the name `Name <code>`, description "seeded".
- **Valid request (VR):** `GET v1/author/scope`, `authorization: Bearer <ADMIN>`, `timestamp: <now UTC>`, no body.
- **Observation:** HTTP response (`data` exactly items, pageIndex, pageSize, totalItems, totalPages; each item exactly scopeId, scope, name, description, rowStatus); the `author.m_scope` row after the call.

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| R01 | spec Success | 200 S10000 "Inquiry Scope Success"; exact keys; sorted by code; DELETED never returned | [TC-SCOPEQ-001](#tc-scopeq-001--filters-sort-and-exclude-deleted) | designed |
| R02 | spec query id, search, rowStatus | id combines with the filters; a missing or DELETED id is an empty 200; search on code or description, case-insensitive, `_` keeps its ILIKE meaning; each status filters | [TC-SCOPEQ-002](#tc-scopeq-002--by-id-search-and-row-status) | designed |
| R03 | sequence paging note | page 2 of 3, beyond range empty with totals kept | [TC-SCOPEQ-003](#tc-scopeq-003--pagination) | designed |
| R04 | sequence validation note | the twelve query rows of TC-ROLEQ-006 | [TC-SCOPEQ-004](#tc-scopeq-004--query-validation) | designed (reuses the 03 rows) |
| R05 | sequence order; permission rule | no body; 400 before 401; credential failures 401; only exact PLATFORM_ADMIN, else 403 for existing and unknown ids | [TC-SCOPEQ-005](#tc-scopeq-005--body-validation-order-credentials-and-403) | designed |
| R06 | spec "No locks or writes"; timeout; page count check | a row lock does not block; a table lock times out 408; a page that disagrees with its count is 500 | [TC-SCOPEQ-006](#tc-scopeq-006--no-lock-timeout-and-a-disagreeing-page) | designed |

## Detailed test cases

### TC-SCOPEQ-001 — Filters, sort and exclude DELETED

- Source: R01. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** `<P>_B` ACTIVE, `<P>_A` LOCKED, `<P>_C` DELETED; VR `?search=<P>`. **Expected:** 200 S10000; items `<P>_A` (LOCKED) then `<P>_B` (ACTIVE), each with name `Name <code>` and description "seeded"; pageIndex 1, pageSize 10, totals 2/1.

### TC-SCOPEQ-002 — By id, search and row status

- Source: R02. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** one scope per status, DELETED included. **Expected:** `?id=<LOCKED>` → that scope; `?id=<LOCKED>&rowStatus=ACTIVE`, `?id=<DELETED>`, `?id=<random>` → empty, totals 0/0; `?search=<P>&rowStatus=<s>` → only that status's scope for each of the four; `?search=<P lower case>` → totalItems 4; a scope whose description is `<tag>_9` → `?search=<tag>_9` returns only it.

### TC-SCOPEQ-003 — Pagination

- Source: R03. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** three scopes `<P>_0..2`. **Expected:** `?search=<P>&pageIndex=2&pageSize=2` → only `<P>_2`, pageIndex 2, pageSize 2, totals 3/2; `pageIndex=9` → items `[]`, totals 3/2.

### TC-SCOPEQ-004 — Query validation

- Source: R04. Design readiness: Ready. Execution status: Pass (automated).

**Rows:** the twelve rows of [TC-ROLEQ-006](../03-inquiry-role/test-cases.md#tc-roleq-006--query-validation); the test reuses them. **Expected:** each 400 E10001 with its message.

### TC-SCOPEQ-005 — Body, validation order, credentials and 403

- Source: R05. Design readiness: Ready. Execution status: Pass (automated).

**Requests:** a JSON body `{}` → `Request Body must be empty.`; no token with `?pageSize=0` → 400 page message; no token and a JWT without roles → 401 E10002; callers `[]`, `["CUSTOMER"]`, `["platform_admin"]` with an existing and a random id → 403 E10009 "You do not have permission to read scopes.".

### TC-SCOPEQ-006 — No lock, timeout and a disagreeing page

- Source: R06. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** with a 1-second timeout, another session holds the scope FOR UPDATE; VR `?id=<S>` → 200 with the scope. Another session holds `LOCK TABLE author.m_scope IN ACCESS EXCLUSIVE MODE` → 408 E90001. A test repository drops the first row of each page → 500 "An unexpected error occurred." without bizCode.

## Revision and execution history

- 2026-11-22: first version (Drake), executed by the automated tests of e-commerce-backend on branch `feat/drake-author-08-17` (`6000ad0`, PR e-commerce-backend#33): `InquiryScopeApiTests` (HTTP + real PostgreSQL 17). Result: every case passes (dotnet test (full solution, branch feat/drake-author-08-17): Api 643, Application 43, Domain 73, Infrastructure 53, 0 failed). Mutation checks were run while implementing; their individual results were not recorded, so none are listed here.
