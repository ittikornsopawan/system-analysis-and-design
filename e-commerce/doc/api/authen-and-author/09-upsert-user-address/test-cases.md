---
name: "Upsert User Address API Test Cases"
description: "Documented scenarios and expected results for POST v1/user/address/upsert; use for test planning and for the automated backend tests named after each case ID."
---

# Upsert User Address API Test Cases

## Source baseline and scope

- Method/path: `POST v1/user/address/upsert`
- Governing sources: [spec.md](spec.md) (body, rules, response examples, Database Relations), [sequence.wsd](sequence.wsd) (validation, Q21, default and quota notes), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md)
- Source revision: Showcase `main` at the commit that adds this file; `spec.md` and `sequence.wsd` last changed in `8023e47`
- Source approval: approved (`approved_by: Ittikorn`, `approved_at: 2026-11-16T09:24:57+07:00`); Q21 approved by the product owner on 2026-11-08
- Test design baseline: approved-source, except gap G1 (message choices, pending the lead's review)
- Scope and exclusions: the caller's own addresses; no batch and no archive (per spec); TLS excluded. No rate limit in the spec.
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database:** throw-away PostgreSQL 17 with every Showcase migration (backend `PostgresFixture`), sessions in UTC.
- **Caller:** `U_OK` ACTIVE with an ACTIVE stored access token A and no address (each case adds what it needs); `U_OTHER` owns one address.
- **Valid request (VR):** `authorization: Bearer <A>`, `content-type: application/json`, `timestamp: <now UTC>`, body `{"title": "Home", "address": "1 Road", "city": "Watthana", "state": "Bangkok", "postalCode": "10110", "country": "Thailand"}` plus the fields of each case.
- **Observation:** HTTP response; `authen.t_user_address` rows of the caller (decrypted), `is_default`, `row_status`, `updated_at`.

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| A01 | spec Success - Insert | no id → insert, 201 S10000 "Insert User Address Success", data.userAddressId only | [TC-ADDRESS-001](#tc-address-001--insert-the-first-address) | designed |
| A02 | spec Success - Update | id with ACTIVE or INACTIVE → 200 S10000 "Update User Address Success" | [TC-ADDRESS-004](#tc-address-004--update) | designed |
| A03 | sequence delete note | id with DELETED → soft delete (row kept, DELETED), 204 with no body; DELETED is final | [TC-ADDRESS-005](#tc-address-005--soft-delete) | designed |
| A04 | spec sensitive rule | address, city, state, postalCode, country encrypted; title plain | [TC-ADDRESS-001](#tc-address-001--insert-the-first-address) | designed |
| A05 | sequence default note | the first ACTIVE address is default whatever isDefault says; a new INACTIVE address is never default | [TC-ADDRESS-001](#tc-address-001--insert-the-first-address), [TC-ADDRESS-002](#tc-address-002--default-rules-on-insert) | designed |
| A06 | spec Default address | explicit true makes this the only default (old default cleared); false or omitted keeps the stored flag; at most one default | [TC-ADDRESS-002](#tc-address-002--default-rules-on-insert), [TC-ADDRESS-003](#tc-address-003--choosing-a-new-default) | designed |
| A07 | sequence promotion note | deleting or deactivating the default promotes the ACTIVE address with the latest COALESCE(updated_at, created_at), then lowest id; none when no ACTIVE address remains | [TC-ADDRESS-006](#tc-address-006--promotion-after-the-default-leaves) | designed |
| A08 | spec Fail - Bad Request Default (Q21) | isDefault true with INACTIVE or DELETED → 400 "A default address must be ACTIVE." before SQL, even for an unknown id | [TC-ADDRESS-007](#tc-address-007--q21-default-must-be-active) | designed |
| A09 | spec Fail - Bad Request Row Status | insert with DELETED → 400 "Row status must not be DELETED when inserting a user address." | [TC-ADDRESS-008](#tc-address-008--validation) | designed |
| A10 | spec Fail - Bad Request; sequence validation note | title, address, city, state, postalCode, country mandatory non-blank (also for update and delete); title ≤ 128; id a UUID; rowStatus ACTIVE/INACTIVE/DELETED (not null); isDefault a boolean (not null); unknown keys and userId rejected | [TC-ADDRESS-008](#tc-address-008--validation) | designed; messages G1 |
| A11 | spec Fail - Bad Request Limit | an insert at 10 non-DELETED addresses → 400 "A user can have at most 10 addresses."; update and delete still allowed; DELETED rows do not count | [TC-ADDRESS-009](#tc-address-009--at-most-10-addresses) | designed |
| A12 | spec Fail - Not Found | id of another user, a DELETED address or an unknown id → 404 E10004 "User address not found." | [TC-ADDRESS-010](#tc-address-010--not-found) | designed |
| A13 | sequence order and credential note | validation (400) before the JWT (401); bad JWT, revoked token or user not ACTIVE → 401 | [TC-ADDRESS-011](#tc-address-011--validation-before-the-credential-and-credential-failures) | designed |
| A14 | sequence quota note | concurrent inserts cannot both take the tenth slot (user lock) | [TC-ADDRESS-012](#tc-address-012--concurrent-inserts-at-the-limit) | designed |
| A15 | sequence failure branches | timeout → 408 E90001; unexpected failure → 500 without bizCode; no old default is lost | [TC-ADDRESS-013](#tc-address-013--timeout-and-unexpected-failure) | designed |

## Detailed test cases

### TC-ADDRESS-001 — Insert the first address

- Source: A01, A04, A05. Design readiness: Ready. Execution status: Pass (automated).

**Request:** VR with `isDefault: false`. **Expected:** 201, "Created", S10000 "Insert User Address Success", `data` exactly `{userAddressId}`; one row ACTIVE, is_default TRUE (first ACTIVE address), title plain, other fields decrypt to the input, created_by = U_OK id.

### TC-ADDRESS-002 — Default rules on insert

- Source: A05, A06. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** insert A1 (default); insert A2 with isDefault omitted → A2 not default. For a fresh user: insert B1 with `rowStatus: INACTIVE` → not default; then insert B2 ACTIVE → B2 is default (first ACTIVE address, not the first row).

### TC-ADDRESS-003 — Choosing a new default

- Source: A06. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** A1 default, A2 not; insert A3 with `isDefault: true` → A3 default, A1 not; update A1 with `isDefault: false` → A1 still not default, A3 still default; update A3 with `isDefault` omitted → A3 stays default. **Expected:** exactly one default at every step.

### TC-ADDRESS-004 — Update

- Source: A02. Design readiness: Ready. Execution status: Pass (automated).

**Request:** id of A1 with a new title and `rowStatus: INACTIVE` (A1 not default). **Expected:** 200, "Ok", S10000 "Update User Address Success", data.userAddressId = A1; the row has the new title and INACTIVE, is_default FALSE, updated_by = U_OK id.

### TC-ADDRESS-005 — Soft delete

- Source: A03. Design readiness: Ready. Execution status: Pass (automated).

**Request:** id of A2 with `rowStatus: DELETED` and `isDefault: false`. **Expected:** 204 with no body; the row still exists with DELETED and is_default FALSE; a second delete of A2 → 404.

### TC-ADDRESS-006 — Promotion after the default leaves

- Source: A07. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** A1 default, A2 and A3 ACTIVE with A3 the most recently updated; delete A1 → A3 becomes default; deactivate A3 (`INACTIVE`) → A2 becomes default; delete A2 → no ACTIVE address left, no default.

### TC-ADDRESS-007 — Q21: default must be ACTIVE

- Source: A08. Design readiness: Ready. Execution status: Pass (automated).

**Request:** `isDefault: true` with `rowStatus: INACTIVE`; with `rowStatus: DELETED` and an id that does not exist. **Expected:** 400 E10001 "A default address must be ACTIVE." (not 404); nothing changed.

### TC-ADDRESS-008 — Validation

- Source: A09, A10. Design readiness: Ready (messages per G1). Execution status: Pass (automated).

**Request (each 400 E10001, nothing changed):** every mandatory field missing → "Title, Address, City, State, Postal Code and Country are required fields."; `city` missing → "City is a required field."; `postalCode: "  "` → "Postal Code is a required field."; title 129 characters → "Title must be at most 128 characters."; `id: "x"` and `id: null` → "Id must be a valid UUID."; `rowStatus: "ARCHIVED"` and `null` → "Row Status must be ACTIVE, INACTIVE or DELETED."; `isDefault: "yes"` and `null` → "Is Default must be a boolean."; `userId: <any>` → "User Id is not a known field."; insert with `rowStatus: DELETED` → "Row status must not be DELETED when inserting a user address."; a mandatory field missing on a delete → still 400.

### TC-ADDRESS-009 — At most 10 addresses

- Source: A11. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** 10 addresses (mixed ACTIVE and INACTIVE); insert one more → 400 "A user can have at most 10 addresses." and nothing changed; update one of them → 200; delete one → 204; insert again → 201 (the DELETED row does not count).

### TC-ADDRESS-010 — Not found

- Source: A12. Design readiness: Ready. Execution status: Pass (automated).

**Request:** id of U_OTHER's address; id of a DELETED address of U_OK; a random UUID. **Expected:** 404 E10004 "User address not found."; U_OTHER's row unchanged.

### TC-ADDRESS-011 — Validation before the credential, and credential failures

- Source: A13. Design readiness: Ready. Execution status: Pass (automated).

**Request:** an invalid body without authorization → 400; a valid body with: no authorization, another key, no stored token row, the token INACTIVE, the user LOCKED → 401 E10002 "Invalid or expired access token."; nothing changed.

### TC-ADDRESS-012 — Concurrent inserts at the limit

- Source: A14. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** 9 addresses; send 3 inserts at once. **Expected:** exactly one 201 and two 400 "A user can have at most 10 addresses."; 10 non-DELETED rows; exactly one default.

### TC-ADDRESS-013 — Timeout and unexpected failure

- Source: A15. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** (a) a second connection holds U_OK's row `FOR UPDATE`; insert with a 1-second command timeout → 408 E90001, no row. (b) a test-only wrapper throws after the old default was cleared, during an insert with `isDefault: true` → 500 without bizCode; the old default is still the default.

## Open gaps and decisions

| Gap ID | Conflicting/missing sources | Affected obligations/cases | Missing decision or prerequisite | Status / decision reference |
| --- | --- | --- | --- | --- |
| G1 | no message in the spec or the conventions for a null id, an invalid or null rowStatus, a null isDefault and an unknown key | A10 | the messages | implementation choice, pending the lead's review: "Id must be a valid UUID.", "Row Status must be ACTIVE, INACTIVE or DELETED.", "Is Default must be a boolean.", "<Field> is not a known field." (the convention forms) |

## Document verification and limitations

- Every obligation A01–A15 maps to a case, and every case cites its obligation.
- Every case runs automatically; see the execution history.

## Revision and execution history

- 2026-11-19: first version (Drake), Not run.
- 2026-11-19: executed by the automated tests of e-commerce-backend on branch `feat/drake-09-upsert-user-address` (stacked on 08): `UpsertUserAddressApiTests` (HTTP + real PostgreSQL 17, 26 tests including the 12 validation rows), `AddressDefaultPolicyTests` (10). Result: every case passes (`dotnet test`: Api 228, Application 42, Domain 79, Infrastructure 46, 0 failed). Mutation checks: removing the promotion fails TC-ADDRESS-006; removing the default clear on insert fails TC-ADDRESS-003; removing the user lock fails TC-ADDRESS-012.
