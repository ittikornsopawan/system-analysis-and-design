---
name: "Inquiry User Address API Test Cases"
description: "Documented scenarios and expected results for GET v1/user/address; use for test planning and for the automated backend tests named after each case ID."
---

# Inquiry User Address API Test Cases

## Source baseline and scope

- Method/path: `GET v1/user/address`
- Governing sources: [spec.md](spec.md) (query parameters, response examples, Database Relations), [sequence.wsd](sequence.wsd) (validation, credential, count/page and mapping notes), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md)
- Source revision: Showcase `main` at the commit that adds this file; `spec.md` and `sequence.wsd` last changed in `8023e47`
- Source approval: approved (`approved_by: Ittikorn`, `approved_at: 2026-11-16T09:24:57+07:00`)
- Test design baseline: approved-source, except gap G1 (message choices, pending the lead's review)
- Scope and exclusions: the caller's own addresses only; TLS excluded. The spec has no rate limit for this API. READ ONLY is not testable through EF Core (see the 08 limitation); the snapshot is REPEATABLE READ.
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database:** throw-away PostgreSQL 17 with every Showcase migration (backend `PostgresFixture`), sessions in UTC.
- **Caller:** `U_OK` ACTIVE with an ACTIVE stored access token A (its JWT presented) and addresses inserted directly with known `created_at`: `Home` (ACTIVE, default), `Office` (ACTIVE), `Old flat` (INACTIVE), `Gone` (DELETED). `U_OTHER` has its own ACTIVE address `Home`.
- **Valid request (VR):** `authorization: Bearer <A>`, `timestamp: <now UTC>`, no body, query as each case says.
- **Observation:** HTTP response; the five `data` keys and each item's nine keys; the address rows (decrypted with the test key).

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| A01 | spec Success; sequence mapping note | 200 S10000 "Inquiry User Address Success"; data has exactly items/pageIndex/pageSize/totalItems/totalPages; each item exactly the nine fields, five decrypted; no userId, token or audit field | [TC-ADDRESSQ-001](#tc-addressq-001--the-own-list-in-order) | designed |
| A02 | spec Database Relations ORDER BY | default first, then created_at DESC, then id | [TC-ADDRESSQ-001](#tc-addressq-001--the-own-list-in-order) | designed |
| A03 | spec id parameter; sequence note | id filters within the caller's non-DELETED rows, still paginated and combined with search/status; another user's, DELETED or missing id → empty list, never 404 | [TC-ADDRESSQ-002](#tc-addressq-002--by-id) | designed |
| A04 | spec rowStatus parameter; sequence note | omitted → every non-DELETED status; ACTIVE or INACTIVE filters; DELETED never returned | [TC-ADDRESSQ-003](#tc-addressq-003--status-visibility) | designed |
| A05 | spec search; sequence search note | title only, case-insensitive ILIKE of percent + search + percent with the client's % and _ kept; empty search is valid and matches all | [TC-ADDRESSQ-004](#tc-addressq-004--search-by-title) | designed |
| A06 | spec pageIndex/pageSize; sequence totals note | defaults 1/10 when omitted; totalPages = ceiling(totalItems / pageSize), 0 when none; a page beyond range → items [] with positive totals | [TC-ADDRESSQ-005](#tc-addressq-005--pagination-and-totals) | designed |
| A07 | spec Fail - Bad Request examples; sequence validation note | pageIndex/pageSize positive signed 64-bit integers, pageSize ≤ 100, explicit empty or invalid never defaulted, offset fits BIGINT; rowStatus ACTIVE/INACTIVE; id a UUID | [TC-ADDRESSQ-006](#tc-addressq-006--query-validation) | designed; overflow and id messages G1 |
| A08 | sequence validation note | unknown or repeated query keys and a non-empty body → 400 E10001; all validation before the JWT (400 not 401) | [TC-ADDRESSQ-007](#tc-addressq-007--request-shape-before-the-credential) | designed; messages G1 |
| A09 | spec rule; sequence credential note | missing/invalid JWT, stored token missing, INACTIVE or expired, user not ACTIVE → 401 E10002 "Invalid or expired access token." | [TC-ADDRESSQ-008](#tc-addressq-008--credential-failures) | designed |
| A10 | sequence "No user/address locks or write SQL run" | the read waits for no row lock and changes nothing | [TC-ADDRESSQ-009](#tc-addressq-009--the-read-takes-no-lock) | designed |
| A11 | sequence failure branches | timeout before COMMIT → 408 E90001 | [TC-ADDRESSQ-010](#tc-addressq-010--timeout) | designed |
| A12 | spec "Count and page share the same repeatable-read snapshot" | a row committed by another transaction between the count and the page is not seen by either | [TC-ADDRESSQ-011](#tc-addressq-011--one-snapshot-for-count-and-page) | designed |
| A13 | sequence row-count and failure notes | a page row count other than min(pageSize, max(0, totalItems − offset)), or an unexpected SQL/decryption failure → 500 without bizCode, no partial list | [TC-ADDRESSQ-012](#tc-addressq-012--unexpected-failure) | designed |

## Detailed test cases

### TC-ADDRESSQ-001 — The own list in order

- Source: A01, A02. Design readiness: Ready. Execution status: Pass (automated).

**Request:** VR with no query. **Expected:** 200, "Ok", S10000 "Inquiry User Address Success"; data keys exactly items, pageIndex 1, pageSize 10, totalItems 3, totalPages 1; items `Home` (default), then `Office` and `Old flat` by created_at DESC, with equal created_at ordered by id; each item has exactly userAddressId, title, isDefault, address, city, state, postalCode, country, rowStatus with the decrypted values; `Gone` and U_OTHER's address absent.

### TC-ADDRESSQ-002 — By id

- Source: A03. Design readiness: Ready. Execution status: Pass (automated).

**Request:** `?id=<Office id>` → one item, totals 1/1. `?id=<U_OTHER's id>`, `?id=<Gone id>`, `?id=<random UUID>` → 200 with items [], totalItems 0, totalPages 0. `?id=<Office id>&search=home` and `?id=<Office id>&rowStatus=INACTIVE` → empty. `?id=<Office id>&pageIndex=2` → items [], totalItems 1, totalPages 1.

### TC-ADDRESSQ-003 — Status visibility

- Source: A04. Design readiness: Ready. Execution status: Pass (automated).

**Request:** no rowStatus → ACTIVE and INACTIVE rows (3); `rowStatus=ACTIVE` → `Home`, `Office`; `rowStatus=INACTIVE` → `Old flat`. **Expected:** `Gone` never appears.

### TC-ADDRESSQ-004 — Search by title

- Source: A05. Design readiness: Ready. Execution status: Pass (automated).

**Request:** `search=OFF` → `Office`; `search=` (empty) → all 3; `search=o_d` → `Old flat` (underscore matches one character); `search=%25` (a literal %) → all 3; `search=Road` (a word only in the encrypted address) → empty.

### TC-ADDRESSQ-005 — Pagination and totals

- Source: A06. Design readiness: Ready. Execution status: Pass (automated).

**Request:** `pageSize=2` → 2 items, totalItems 3, totalPages 2; `pageIndex=2&pageSize=2` → the third item; `pageIndex=3&pageSize=2` → items [], totalItems 3, totalPages 2, pageIndex 3 echoed; `pageSize=100` accepted; a caller with no address → items [], totalItems 0, totalPages 0, pageIndex 1, pageSize 10.

### TC-ADDRESSQ-006 — Query validation

- Source: A07. Design readiness: Ready (messages per G1). Execution status: Pass (automated).

**Request (each 400 E10001, no data):** pageIndex `0`, `-1`, `abc`, `` (empty), `1.5`, `+1`, `9223372036854775808`; pageSize `0`, `101`, `` → "Page Index and Page Size must be greater than 0, Page Size must not be greater than 100."; `pageIndex=9223372036854775807&pageSize=2` → "Page Index is too large for Page Size."; rowStatus `DELETED`, `active`, `` → "Row status must be one of ACTIVE, INACTIVE."; id `abc` and `` → "Id must be a valid UUID."; `id=abc&rowStatus=DELETED` → both messages combined in that order.

### TC-ADDRESSQ-007 — Request shape before the credential

- Source: A08. Design readiness: Ready (messages per G1). Execution status: Pass (automated).

**Request:** `?userId=<U_OTHER id>` → "User Id is not a known field."; `?pageIndex=1&pageIndex=2` → "Page Index must not be duplicated."; a JSON body `{}` → "Request Body must be empty."; each again with no authorization header, and `pageSize=0` with no authorization → still 400 E10001 (not 401); without `timestamp` → "Timestamp is a required header.".

### TC-ADDRESSQ-008 — Credential failures

- Source: A09. Design readiness: Ready. Execution status: Pass (automated).

**Request:** VR with: no authorization; a JWT signed with another key; a valid JWT with no stored row; the stored row expired; the stored row INACTIVE; the user LOCKED. **Expected:** 401 E10002 "Invalid or expired access token.", no data.

### TC-ADDRESSQ-009 — The read takes no lock

- Source: A10. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a second connection holds U_OK's user row and every address row `FOR UPDATE`; VR with a 1-second command timeout. **Expected:** 200 with the 3 items; the rows unchanged (no updated_at change).

### TC-ADDRESSQ-010 — Timeout

- Source: A11. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a second connection holds `LOCK TABLE authen.t_user_address IN ACCESS EXCLUSIVE MODE`; VR with a 1-second command timeout. **Expected:** 408 E90001 "The server timed out waiting for the request.", no data. After release → 200.

### TC-ADDRESSQ-011 — One snapshot for count and page

- Source: A12. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a test-only wrapper commits a new ACTIVE address for U_OK from another connection right after the count. **Expected:** 200 with totalItems 3 and the same 3 items (the new row is in neither); the next request sees 4.

### TC-ADDRESSQ-012 — Unexpected failure

- Source: A13. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a test-only wrapper (a) throws on the page query; (b) returns one row fewer than the page holds. **Expected:** 500 "An unexpected error occurred.", no bizCode, no data, each time.

## Open gaps and decisions

| Gap ID | Conflicting/missing sources | Affected obligations/cases | Missing decision or prerequisite | Status / decision reference |
| --- | --- | --- | --- | --- |
| G1 | the spec gives examples only for the pagination range and the row status; api-conventions has no message for an offset overflow, an unknown or repeated query key or a body on a GET | A07, A08 | the messages | implementation choice, pending the lead's review: "Page Index is too large for Page Size.", "Id must be a valid UUID.", "<Field> is not a known field.", "<Field> must not be duplicated.", "Request Body must be empty."; every pagination range failure (non-numeric, empty, zero, over 100) uses the spec example |

## Document verification and limitations

- Every obligation A01–A13 maps to a case, and every case cites its obligation.
- Every case runs automatically; see the execution history.

## Revision and execution history

- 2026-11-19: first version (Drake), Not run.
- 2026-11-19: executed by the automated tests of e-commerce-backend on branch `feat/drake-10-inquiry-user-address` (stacked on 09): `InquiryUserAddressApiTests` (HTTP + real PostgreSQL 17, 28 tests including the 17 validation rows), `PageRequestTests` (21). Result: every case passes (`dotnet test`: Api 277, Application 42, Domain 79, Infrastructure 46, 0 failed). Mutation checks: READ COMMITTED instead of REPEATABLE READ fails TC-ADDRESSQ-011; removing the row-count check fails TC-ADDRESSQ-012; removing the ACTIVE-user join fails TC-ADDRESSQ-008; removing the created_at order fails TC-ADDRESSQ-001; removing the DELETED filter fails eight cases; dropping the % wrap of search fails TC-ADDRESSQ-004.
