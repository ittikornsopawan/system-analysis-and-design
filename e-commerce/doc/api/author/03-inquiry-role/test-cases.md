---
name: "Inquiry Role API Test Cases"
description: "Documented scenarios and expected results for GET v1/author/role; use for test planning and for the automated backend tests named after each case ID."
---

# Inquiry Role API Test Cases

## Source baseline and scope

- Method/path: `GET v1/author/role`
- Governing sources: [spec.md](spec.md) (query table, response examples, Database Relations), [sequence.wsd](sequence.wsd) (execution order, search pattern, paging and mapping notes), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md) (validation messages, unknown and repeated query keys)
- Source revision: Showcase `main` at the commit that adds this file; `spec.md` and `sequence.wsd` last changed in `b533d83`
- Source approval: approved (`approved_by: Ittikorn`, `approved_at: 2026-11-16T09:24:57+07:00`); owner-confirmed API review Q2/Q4/Q10/Q13
- Test design baseline: approved-source
- Scope and exclusions: TLS excluded; no rate limit in the spec. The `ORDER BY r.name, r.id` tiebreak is not observable: `uq_m_role_name` keeps names unique among the roles this API returns (see R05).
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database:** throw-away PostgreSQL 17 with every Showcase migration (backend `PostgresFixture`), sessions in UTC. Each case seeds its own roles with a unique name prefix and isolates them with `search=<prefix>`.
- **Callers:** each case registers its own user with an ACTIVE stored access token whose JWT carries the `roles` claim it needs: `["PLATFORM_ADMIN"]` (ADMIN), `[]`, `["CUSTOMER"]`, `["platform_admin"]`, or a missing/malformed claim.
- **Valid request (VR):** `GET v1/author/role`, `authorization: Bearer <ADMIN>`, `timestamp: <now UTC>`, no body.
- **Observation:** HTTP response (`data` exactly items, pageIndex, pageSize, totalItems, totalPages; each item exactly roleId, name, description, rowStatus); the `author.m_role` row after the call.

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| R01 | spec Success; sequence mapping note | 200 S10000 "Inquiry Role Success"; exactly five data keys and four item keys; DELETED roles never returned | [TC-ROLEQ-001](#tc-roleq-001--filters-sort-and-exclude-deleted) | designed |
| R02 | spec query `id`; Success - By Id; sequence "id is still filtered/paginated" | id combines with the other filters; a missing or DELETED id is an empty 200 with totals 0/0 | [TC-ROLEQ-002](#tc-roleq-002--by-id-combines-with-the-other-filters) | designed |
| R03 | spec search rule; sequence search note | name OR description, case-insensitive ILIKE; `%search%` keeps % and _; an empty search matches all | [TC-ROLEQ-003](#tc-roleq-003--search) | designed |
| R04 | spec query `rowStatus` | each of ACTIVE/INACTIVE/LOCKED/ARCHIVED filters; omitted means all non-DELETED | [TC-ROLEQ-004](#tc-roleq-004--row-status-filter) | designed |
| R05 | sequence paging note; Success - Page Beyond Range | defaults 1/10; pageSize up to 100; sorted by name; a page beyond range is empty with totals kept, no 404; a large in-range offset works | [TC-ROLEQ-001](#tc-roleq-001--filters-sort-and-exclude-deleted), [TC-ROLEQ-005](#tc-roleq-005--pagination) | designed; id tiebreak not observable |
| R06 | sequence validation note; Bad Request examples; api-conventions | id a UUID (empty refused); positive 64-bit pages, pageSize ≤ 100, no default for an explicit empty value; offset overflow; rowStatus one of four exact values; unknown and repeated keys; no body; several messages joined | [TC-ROLEQ-006](#tc-roleq-006--query-validation) | designed |
| R07 | sequence order | every 400 before the JWT check | [TC-ROLEQ-007](#tc-roleq-007--validation-before-the-credential) | designed |
| R08 | sequence JWT and credential notes | missing/invalid JWT, missing or malformed roles claim, non-ACTIVE user → 401 E10002 | [TC-ROLEQ-008](#tc-roleq-008--credential-failures) | designed |
| R09 | spec permission rule; sequence 403 note | only exact `PLATFORM_ADMIN`; otherwise 403 E10009 "You do not have permission to read roles." before any role read, the same for existing and unknown ids | [TC-ROLEQ-009](#tc-roleq-009--only-a-platform-administrator) | designed |
| R10 | spec "No locks or writes" | rows locked by another session do not block the read; nothing is written | [TC-ROLEQ-010](#tc-roleq-010--no-lock-and-no-write) | designed |
| R11 | sequence timeout branch | a read that cannot finish → 408 E90001 | [TC-ROLEQ-011](#tc-roleq-011--a-held-table-lock-times-out) | designed |
| R12 | sequence "page row count = min(...); mismatch is internal failure" | a page that disagrees with its count → 500 without bizCode | [TC-ROLEQ-012](#tc-roleq-012--a-page-that-disagrees-with-the-count) | designed |

## Detailed test cases

### TC-ROLEQ-001 — Filters, sort and exclude DELETED

- Source: R01, R05. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** seed `<P>_B` ACTIVE, `<P>_A` LOCKED, `<P>_C` DELETED; VR `?search=<P>`. **Expected:** 200, S10000 "Inquiry Role Success"; items `<P>_A` then `<P>_B` (name order) with description "seeded" and their statuses; pageIndex 1, pageSize 10, totalItems 2, totalPages 1; `<P>_C` absent.

### TC-ROLEQ-002 — By id combines with the other filters

- Source: R02. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** an INACTIVE role R; `?id=R` → one item, totals 1/1. Then `?id=R&rowStatus=ACTIVE`, `?id=R&search=NO_SUCH_<name>`, `?id=<DELETED role>`, `?id=<random UUID>`. **Expected:** each 200 with items `[]`, pageIndex 1, pageSize 10, totalItems 0, totalPages 0.

### TC-ROLEQ-003 — Search

- Source: R03. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a tag T; roles with T (upper case) in the name, "Manages T items" as description, and "T_9" as description. **Expected:** `?search=<T upper>&pageSize=100` returns all three; `?search=T_9` returns only the third (`_` is one character); `?search=T%25` (T%) returns 3; `?search=` returns the same total as no search.

### TC-ROLEQ-004 — Row status filter

- Source: R04. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** one role per status, DELETED included. **Expected:** each of ACTIVE, INACTIVE, LOCKED, ARCHIVED returns only its role; without rowStatus totalItems is 4.

### TC-ROLEQ-005 — Pagination

- Source: R05. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** three roles `<P>_0..2`. **Expected:** `?pageIndex=2&pageSize=2` → only `<P>_2`, pageIndex 2, pageSize 2, totalItems 3, totalPages 2; `?pageIndex=9&pageSize=2` → items `[]`, totals 3/2, no 404; `?pageIndex=92233720368547758&pageSize=100` (offset inside BIGINT) → items `[]`, totalItems 3; `?pageSize=100` → pageSize 100.

### TC-ROLEQ-006 — Query validation

- Source: R06. Design readiness: Ready. Execution status: Pass (automated).

| Query | Expected `bizMessage` (400 E10001) |
| --- | --- |
| `id=abc` / `id=` | `Id must be a valid UUID.` |
| `pageIndex=0` / `pageSize=101` / `pageIndex=` / `pageIndex=1.5` | `Page Index and Page Size must be greater than 0, Page Size must not be greater than 100.` |
| `pageIndex=9223372036854775807&pageSize=100` | `Page Index is too large for Page Size.` |
| `rowStatus=DELETED` / `rowStatus=active` | `Row status must be one of ACTIVE, INACTIVE, LOCKED, ARCHIVED.` |
| `name=A` | `Name is not a known field.` |
| `search=a&search=b` | `Search must not be duplicated.` |
| `id=abc&pageSize=0&rowStatus=GONE` | `Id must be a valid UUID, Page Index and Page Size must be greater than 0, Page Size must not be greater than 100, Row status must be one of ACTIVE, INACTIVE, LOCKED, ARCHIVED.` |
| a JSON body `{}` | `Request Body must be empty.` |

### TC-ROLEQ-007 — Validation before the credential

- Source: R07. Design readiness: Ready. Execution status: Pass (automated).

**Request:** no authorization, `?pageSize=0`. **Expected:** 400 E10001 with the page message, not 401.

### TC-ROLEQ-008 — Credential failures

- Source: R08. Design readiness: Ready. Execution status: Pass (automated).

**Requests:** VR with no token, `not-a-jwt`, a JWT without the roles claim, a roles claim with a repeated name, and an ADMIN whose user is INACTIVE. **Expected:** each 401 E10002 "Invalid or expired access token.".

### TC-ROLEQ-009 — Only a platform administrator

- Source: R09. Design readiness: Ready. Execution status: Pass (automated).

**Request:** callers with `[]`, `["CUSTOMER"]`, `["platform_admin"]` send `?id=<existing role>` and `?id=<random UUID>`. **Expected:** every answer 403 E10009 "You do not have permission to read roles.", the same for both ids.

### TC-ROLEQ-010 — No lock and no write

- Source: R10. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** with a 1-second command timeout, another session holds the role FOR UPDATE, then the caller's `m_user` row FOR UPDATE; VR `?id=<role>` each time. **Expected:** 200 with the role both times (no wait, no 408); the role row unchanged (updated_by NULL).

### TC-ROLEQ-011 — A held table lock times out

- Source: R11. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** another session holds `LOCK TABLE author.m_role IN ACCESS EXCLUSIVE MODE`; VR with a 1-second command timeout. **Expected:** 408 E90001 "The server timed out waiting for the request.".

### TC-ROLEQ-012 — A page that disagrees with the count

- Source: R12. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a test repository drops the first row of every page; VR. **Expected:** 500 "An unexpected error occurred." without bizCode.

## Revision and execution history

- 2026-11-21: first version (Drake), executed by the automated tests of e-commerce-backend on branch `feat/drake-author-03-inquiry-role` (`cad38c5`): `InquiryRoleApiTests` (HTTP + real PostgreSQL 17, 24 tests including the 12 validation rows). Result: every case passes (`dotnet test`: Api 379, Application 43, Domain 73, Infrastructure 53, 0 failed). Mutation checks: no 403 fails TC-ROLEQ-009; returning DELETED rows fails TC-ROLEQ-001; searching the name only or dropping the `%` wrap fails TC-ROLEQ-003; a wrong sort fails TC-ROLEQ-001; no row-count check fails TC-ROLEQ-012; no credential check fails TC-ROLEQ-008. Removing the `id` tiebreak survives (names are unique among returned roles). The first run of TC-ROLEQ-005 compared a list inside a tuple by reference; the assertion was corrected before this run.
