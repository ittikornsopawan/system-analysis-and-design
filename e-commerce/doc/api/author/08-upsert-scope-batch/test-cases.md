---
name: "Upsert Scope Batch API Test Cases"
description: "Documented scenarios and expected results for POST v1/author/scope/upsert/batch; use for test planning and for the automated backend tests named after each case ID."
---

# Upsert Scope Batch API Test Cases

## Source baseline and scope

- Method/path: `POST v1/author/scope/upsert/batch`
- Governing sources: [spec.md](spec.md), [sequence.wsd](sequence.wsd) (item order, lock order, rollback), [07 test cases](../07-upsert-scope/test-cases.md) (the per-item rules), [api-conventions.md](../../../../../.agents/skills/api-contract-design/references/api-conventions.md)
- Source revision: `spec.md` and `sequence.wsd` last changed in `aa82b4a`
- Source approval: approved (`approved_by: Josh (SA Lead, delegated by Ittikorn 2026-11-17)`, `approved_at: 2026-11-20T15:26:03+07:00`)
- Test design baseline: approved-source
- Scope and exclusions: TLS excluded; no rate limit in the spec. The per-item field rules are those of spec 07; this file checks that each one names its position and rolls the whole batch back.
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Database and callers:** throw-away PostgreSQL 17 with every Showcase migration (backend `PostgresFixture`); each case registers its own callers with an ACTIVE stored access token: ADMIN (`["PLATFORM_ADMIN"]`), `[]`, `["CUSTOMER"]`, `["platform_admin"]`, or no roles claim. Scope codes are unique per case (`NewCode()`).
- **Valid request (VR):** `POST v1/author/scope/upsert/batch`, `authorization: Bearer <ADMIN>`, `timestamp: <now UTC>`, body `{"scopes":[<item>...]}` where an item is the spec 07 body.
- **Observation:** HTTP response (`data.scopes[]` exactly index, scopeId, action); the `author.m_scope` rows after the call.

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| R01 | spec Success | 200 S10000 "Batch Upsert Scope Success"; one result per item in request order with INSERT/UPDATE/DELETE/ARCHIVE | [TC-SBATCH-001](#tc-sbatch-001--insert-update-delete-and-archive-in-one-batch) | designed |
| R02 | spec body rules; api-conventions | body shape, 1 to 100 items, item rules prefixed with `scopes[i]`, duplicated id (case-insensitive) or code in one batch, unknown query keys | [TC-SBATCH-002](#tc-sbatch-002--request-and-item-validation) | designed |
| R03 | sequence order | every 400 before the JWT; credential failures 401 with no write | [TC-SBATCH-003](#tc-sbatch-003--validation-before-the-credential-and-credential-failures) | designed |
| R04 | sequence target and permission checks | the first missing or DELETED target is 404 E10004 with its position, before one 403 E10009 for the whole batch | [TC-SBATCH-004](#tc-sbatch-004--first-missing-target-then-one-403) | designed |
| R05 | spec conflicts | duplicate code 409 E10003 and in-use 409 E10006 name their position; the code check answers first; nothing is kept | [TC-SBATCH-005](#tc-sbatch-005--item-errors-name-their-position-and-roll-back) | designed |
| R06 | sequence "each item sees the writes before it" | a later item sees an earlier delete or rename | [TC-SBATCH-006](#tc-sbatch-006--items-see-the-writes-before-them) | designed |
| R07 | sequence unique guard | concurrent batches with one code: one 200, others 409 at that position | [TC-SBATCH-007](#tc-sbatch-007--concurrent-batches-with-one-code) | designed |
| R08 | sequence locks | the caller lock and the scope locks are held; locks are taken in id order so opposite batches do not deadlock | [TC-SBATCH-008](#tc-sbatch-008--locks-and-their-order) | designed |
| R09 | sequence failure branch | an unexpected failure is 500 without bizCode and rolls back every item | [TC-SBATCH-009](#tc-sbatch-009--an-unexpected-failure-rolls-back-every-item) | designed (failure injected through a test repository) |

## Detailed test cases

### TC-SBATCH-001 — Insert, update, delete and archive in one batch

- Source: R01. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** three ACTIVE scopes U, D, A; VR with items [insert N; U renamed, INACTIVE; D DELETED; A ARCHIVED]. **Expected:** 200 S10000; results index 0..3 with actions INSERT, UPDATE, DELETE, ARCHIVE and the ids of U, D, A; N stored ACTIVE with created_by = the caller; U renamed and INACTIVE; D DELETED; A ARCHIVED.

### TC-SBATCH-002 — Request and item validation

- Source: R02. Design readiness: Ready. Execution status: Pass (automated; two test methods carry this ID).

| Body or request | Expected `bizMessage` (400 E10001) |
| --- | --- |
| `[]` | `Request Body must be an object.` |
| `{"scopes":[],"extra":1}` | `Extra is not a known field.` |
| `{}` | `Scopes is a required field.` |
| `{"scopes":"a"}` | `Scopes must be an array.` |
| `{"scopes":[]}` / 101 items | `Scopes must contain 1 to 100 items.` |
| `{"scopes":[null]}` | `scopes[0]: Scope must be an object.` |
| an item with `"x":1` | `scopes[0]: X is not a known field.` |
| second item with empty name and code `a` | `scopes[1]: Name is a required field, Scope code must be capital letters, digits and _, starting with a letter, at most 64 characters.` |
| an insert item with rowStatus DELETED | `scopes[0]: Row status must not be DELETED when inserting a scope.` |
| `?x=1` | `X is not a known field.` |
| items 1 and 2 with one id (item 2 upper case) | `scopes[2]: Id is duplicated with scopes[1].` |
| items 0 and 2 with one code | `scopes[2]: Scope is duplicated with scopes[0].` |

**Also:** 100 items → 200 with indexes 0..99; [delete A; insert A's code] → 200 DELETE, INSERT (a DELETED item does not hold its code).

### TC-SBATCH-003 — Validation before the credential and credential failures

- Source: R03. Design readiness: Ready. Execution status: Pass (automated).

**Requests:** no token with an invalid code → 400 with the `scopes[0]` code message; no token, a JWT without roles, an ADMIN whose stored token is INACTIVE → each 401 E10002. **Expected:** the code is not stored.

### TC-SBATCH-004 — First missing target, then one 403

- Source: R04. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** ADMIN sends [insert; random id; a valid update; another random id] → 404 E10004 `scopes[1]: Scope not found.`; [insert; DELETED scope] → the same at `scopes[1]`. Callers `[]`, `["CUSTOMER"]`, `["platform_admin"]`: a DELETED target → 404 at `scopes[0]`; an insert and a valid update → 403 E10009 "You do not have permission to manage scopes.". **Expected:** nothing inserted; the kept scope's description stays "seeded".

### TC-SBATCH-005 — Item errors name their position and roll back

- Source: R05. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** T ARCHIVED; S ACTIVE and linked to a permission. [insert F; insert T's code] → 409 E10003 `scopes[1]: Scope code already exists.`; [insert F; S ARCHIVED] → 409 E10006 `scopes[1]: Scope is used by permissions.`; [insert F; S renamed to T's code and DELETED] → 409 E10003 (code first). **Expected:** F never stored; S stays ACTIVE.

### TC-SBATCH-006 — Items see the writes before them

- Source: R06. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** A ACTIVE, B LOCKED. [insert B's code; delete B] → 409 at `scopes[0]`; [A renamed to B's code; B renamed] → 409 at `scopes[0]`. **Expected:** A's code and B's status unchanged; then [delete B; insert B's code] → 200 DELETE, INSERT.

### TC-SBATCH-007 — Concurrent batches with one code

- Source: R07. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** four ADMIN callers send at once [insert a fresh code; insert C]. **Expected:** exactly one 200; the others 409 E10003 `scopes[1]: Scope code already exists.`; one row with code C.

### TC-SBATCH-008 — Locks and their order

- Source: R08. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** with a 1-second command timeout: another session holds the caller's `m_user` row FOR UPDATE → 408 E90001; holds scope B FOR SHARE while a CUSTOMER sends [A; B] → 408 (the scope lock is taken before the 403); released → 403 E10009. Two ADMIN callers send [A, B] and [B, A] five times at once. **Expected:** every one of those ten answers 200 (no deadlock).

### TC-SBATCH-009 — An unexpected failure rolls back every item

- Source: R09. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a test repository throws after the second insert; VR [insert X; insert Y]. **Expected:** 500 "An unexpected error occurred." without bizCode; neither X nor Y stored.

## Revision and execution history

- 2026-11-22: first version (Drake), executed by the automated tests of e-commerce-backend on branch `feat/drake-author-08-17` (`146d20b`, PR e-commerce-backend#33): `UpsertScopeBatchApiTests` (HTTP + real PostgreSQL 17). Result: every case passes (dotnet test (full solution, branch feat/drake-author-08-17): Api 643, Application 43, Domain 73, Infrastructure 53, 0 failed). Mutation checks were run while implementing; their individual results were not recorded, so none are listed here.
