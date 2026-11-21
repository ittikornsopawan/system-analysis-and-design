---
name: "Upsert Scope API Test Cases"
description: "Documented scenarios and expected results for POST v1/author/scope/upsert; use for test planning and for the automated backend tests named after each case ID."
---

# Upsert Scope API Test Cases

## Source baseline and scope

- Method/path: `POST v1/author/scope/upsert`
- Governing sources: [spec.md](spec.md) (body, rules, response examples, Database Relations), [sequence.wsd](sequence.wsd) (execution order, lock order, validation and usage notes), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md)
- Source revision: Showcase `main` at the commit that adds this file; `spec.md` and `sequence.wsd` last changed in `ed42887`
- Source approval: approved (`approved_by: Josh (SA Lead, delegated by Ittikorn 2026-11-17)`, `approved_at: 2026-11-20T15:26:03+07:00`); owner-confirmed API review Q2/Q4/Q7/Q10/Q13/Q15
- Test design baseline: approved-source
- Scope and exclusions: TLS excluded; no rate limit in the spec; no reserved or seeded code is protected (the sequence says none is added). The guarded UPDATE's zero-row 404 is not reachable while the scope is locked by this transaction (R12). The insert-path code precheck is not observable on its own (nothing runs between it and the INSERT, whose unique index gives the same 409).
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database and callers:** as in the 01 test cases. Each case seeds its own scope masters with a unique code `S_<HEX>`.
- **Body(scope, name = "A scope", description = "Scope description", id?, rowStatus?)**.
- **Observation:** HTTP response (`data` exactly `scopeId`); the `author.m_scope` row (scope, name, description, row_status, created_by, updated_by) and the count by code.

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| R01 | spec Success - Insert | no id → 201 "Insert Scope Success", data exactly `scopeId`; ACTIVE by default; created_by = caller | [TC-SCOPE-001](#tc-scope-001--insert) | designed |
| R02 | spec Update/Archive/Delete; "DELETED is final" | update 200, archive 200 "Archive Scope Success", ACTIVE reopens, delete 204; a DELETED id is 404 and its code free; insert-ARCHIVED is 201 | [TC-SCOPE-002](#tc-scope-002--update-archive-reopen-and-delete) | designed |
| R03 | sequence validation note; Bad Request examples | object of five known keys, no repeated key, string values; scope/name/description required and non-blank; code `^[A-Z][A-Z0-9_]{0,63}$` never trimmed; name ≤ 64, description ≤ 256; status; insert-DELETED; id a UUID; no query key; several messages joined | [TC-SCOPE-003](#tc-scope-003--input-validation) | designed |
| R04 | sequence order; credential notes | every 400 before 401; credential failures → 401 E10002, nothing written | [TC-SCOPE-004](#tc-scope-004--validation-before-the-credential-and-credential-failures) | designed |
| R05 | spec Permission; sequence order | only exact PLATFORM_ADMIN; 403 E10009 "You do not have permission to manage scopes."; for an id the 404 comes first | [TC-SCOPE-005](#tc-scope-005--only-a-platform-administrator-after-the-scope-lookup) | designed |
| R06 | spec uniqueness | another non-DELETED scope of any status with the code → 409 E10003 "Scope code already exists."; own code kept; a DELETED scope's code free; the code check comes before the in-use check | [TC-SCOPE-006](#tc-scope-006--duplicate-code) | designed |
| R07 | spec in-use rule | DELETED/ARCHIVED refused (409 E10006 "Scope is used by permissions.") while a non-DELETED link of any status uses it; INACTIVE allowed; a DELETED link does not count | [TC-SCOPE-007](#tc-scope-007--in-use-blocks-archive-and-delete) | designed |
| R08 | sequence 23505 note | concurrent inserts of one code → one 201, the rest 409 | [TC-SCOPE-008](#tc-scope-008--concurrent-inserts-of-one-code) | designed |
| R09 | sequence lock order; timeout branch | caller user locked; the target scope FOR UPDATE before the 403; a held lock → 408 | [TC-SCOPE-009](#tc-scope-009--the-caller-and-target-locks) | designed |
| R10 | sequence unexpected-failure branch | a failure after the insert → 500 without bizCode, nothing kept | [TC-SCOPE-010](#tc-scope-010--an-unexpected-failure-rolls-back) | designed |
| R11 | 404 code of a scope | the target's "Scope not found." is E10004 (spec 04's referenced master is E10005) | [TC-SCOPE-002](#tc-scope-002--update-archive-reopen-and-delete), [TC-SCOPE-005](#tc-scope-005--only-a-platform-administrator-after-the-scope-lookup) | designed |
| R12 | guarded UPDATE zero rows → 404 | defensive: the row is locked by this transaction | — | excluded (unreachable while locked) |

## Detailed test cases

### TC-SCOPE-001 — Insert

- Source: R01. Design readiness: Ready. Execution status: Pass (automated).

**Request:** Body(new code, "Region", "The shops of one region"). **Expected:** 201 S10000 "Insert Scope Success", data exactly `scopeId`; the row has the code, name and description as sent, ACTIVE, created_by = caller.

### TC-SCOPE-002 — Update, archive, reopen and delete

- Source: R02, R11. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a seeded scope: new code, "Renamed", "Changed", LOCKED → 200 "Update Scope Success", same id, every field stored, updated_by = caller, created_by still "seed"; ARCHIVED → 200 "Archive Scope Success"; no rowStatus → ACTIVE; DELETED → 204 with no body; the same id again → 404 E10004 "Scope not found."; a new scope with the freed code → 201; a new scope requested ARCHIVED → 201 and stored ARCHIVED.

### TC-SCOPE-003 — Input validation

- Source: R03. Design readiness: Ready. Execution status: Pass (automated).

| Body | Expected `bizMessage` (400 E10001) |
| --- | --- |
| `[]` | `Request Body must be an object.` |
| extra key `code` / `scope` twice / `"name": 1` | `Code is not a known field.` / `Scope must not be duplicated.` / `Name must be a string.` |
| `" "`, `""`, `null` | `Scope, Name and Description are required fields.` |
| name omitted | `Name is a required field.` |
| `region`, `1A`, `" A"`, `A` + 64 × `B` | `Scope code must be capital letters, digits and _, starting with a letter, at most 64 characters.` |
| insert with DELETED / rowStatus `GONE` | `Row status must not be DELETED when inserting a scope.` / `Row Status must be ACTIVE, INACTIVE, DELETED, LOCKED or ARCHIVED.` |
| `"id": null` | `Id must be a valid UUID.` |
| `id: "x"`, `scope: "a"`, `name: ""` | `Id must be a valid UUID, Name is a required field, Scope code must be ...` |
| name of 65 / description of 257 / query `?x=1` | `Name must be at most 64 characters.` / `Description must be at most 256 characters.` / `X is not a known field.` |

**Also:** a 64-character code, a 64-character name and a 256-character description are accepted (201).

### TC-SCOPE-004 — Validation before the credential and credential failures

- Source: R04. Design readiness: Ready. Execution status: Pass (automated).

**Requests:** no token with an invalid code → 400 (not 401); then no token, `not-a-jwt`, a JWT without the roles claim, an ADMIN whose stored token is INACTIVE → each 401 E10002; no scope with the code.

### TC-SCOPE-005 — Only a platform administrator, after the scope lookup

- Source: R05, R11. Design readiness: Ready. Execution status: Pass (automated).

**Request:** callers with `[]`, `["CUSTOMER"]`, `["platform_admin"]`: an insert → 403; an update of an existing scope → 403; an update of a DELETED scope → 404 E10004 (before 403). **Expected:** the existing scope unchanged.

### TC-SCOPE-006 — Duplicate code

- Source: R06. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** for a scope of each status ACTIVE, INACTIVE, LOCKED, ARCHIVED holding a code: inserting it and renaming another scope to it → 409 E10003 "Scope code already exists."; a scope keeping its own code → 200; a DELETED scope's code → 201; a scope used by a link, archived under a taken code → 409 E10003 (the code check answers before the in-use check).

### TC-SCOPE-007 — In use blocks archive and delete

- Source: R07. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a scope with a LOCKED link: ARCHIVED and DELETED → 409 E10006 "Scope is used by permissions."; INACTIVE → 200. After the link is DELETED: DELETED → 204.

### TC-SCOPE-008 — Concurrent inserts of one code

- Source: R08. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** four administrators insert the same new code at once. **Expected:** one 201, the others 409 E10003; one scope with the code.

### TC-SCOPE-009 — The caller and target locks

- Source: R09. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** with a 1-second command timeout: another session holds the caller's `m_user` row FOR UPDATE → 408 E90001. Another session holds the scope FOR SHARE and a CUSTOMER sends an update → 408 (403 once released); the scope's description stays "seeded".

### TC-SCOPE-010 — An unexpected failure rolls back

- Source: R10. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a test repository throws after the insert. **Expected:** 500 "An unexpected error occurred." without bizCode; no scope with the code.

## Revision and execution history

- 2026-11-21: first version (Drake), executed by the automated tests of e-commerce-backend on branch `feat/drake-author-07-upsert-scope` (`3b532da`): `UpsertScopeApiTests` (HTTP + real PostgreSQL 17, 23 tests including 13 validation rows). Result: every case passes (`dotnet test`: Api 489, Application 43, Domain 73, Infrastructure 53, 0 failed). Mutation checks, each failing its case: no 403 (005), no 404 (005, 002), no code precheck (006, paired with the in-use check), no in-use check (007), only ACTIVE links counted (007), no `uq_m_scope_scope` mapping (008), no target lock (009).
