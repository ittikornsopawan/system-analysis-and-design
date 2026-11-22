---
name: "Me API Test Cases"
description: "Documented scenarios and expected results for GET v1/author/me, the caller's own token roles; use for test planning and for the automated backend tests named after each case ID."
---

# Me API Test Cases

## Source baseline and scope

- Method/path: `GET v1/author/me`
- Governing sources: [spec.md](spec.md), [sequence.wsd](sequence.wsd) (the token snapshot, the credential read)
- Source revision: `spec.md` and `sequence.wsd` last changed in `ed42887`
- Source approval: approved (`approved_by: Josh (SA Lead, delegated by Ittikorn 2026-11-17)`, `approved_at: 2026-11-20T15:26:03+07:00`)
- Test design baseline: approved-source
- Scope and exclusions: TLS excluded; no rate limit in the spec. The generic 500 branch has no case of its own; it is the shared exception path tested by the other author APIs.
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Callers:** each case registers its own user with an ACTIVE stored access token whose JWT carries the `roles` claim it needs.
- **Valid request (VR):** `GET v1/author/me`, `authorization: Bearer <JWT>`, `timestamp: <now UTC>`, no query, no body.
- **Observation:** HTTP response (`data` exactly userId, isPlatformAdmin, roles).

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| R01 | spec Success | 200 S10000; the caller's id and the token's roles in token order | [TC-ME-001](#tc-me-001--the-callers-token-roles) | designed |
| R02 | spec isPlatformAdmin rule | exact, case-sensitive PLATFORM_ADMIN; `[]` is valid | [TC-ME-002](#tc-me-002--platform-administrator-and-empty-roles) | designed |
| R03 | spec "token snapshot" | a role assigned after issuance is not in the answer | [TC-ME-003](#tc-me-003--the-token-roles-not-the-assignments) | designed |
| R04 | spec "no target user" | no query key, no body | [TC-ME-004](#tc-me-004--no-target-user-query-or-body) | designed |
| R05 | sequence credential note | missing/invalid JWT, missing or malformed roles, revoked or expired token, user not ACTIVE → 401 E10002 | [TC-ME-005](#tc-me-005--credential-failures) | designed |
| R06 | spec "no locks"; timeout | a row lock does not block; a held credential table times out 408 | [TC-ME-006](#tc-me-006--a-held-table-lock-times-out-and-no-row-lock-blocks) | designed |

## Detailed test cases

### TC-ME-001 — The caller's token roles

- Source: R01. Design readiness: Ready. Execution status: Pass (automated).

**Request:** a caller with `["SHOP_SUPPORT","CATALOG_MANAGER"]`. **Expected:** 200; userId = the caller; isPlatformAdmin false; roles in that order.

### TC-ME-002 — Platform administrator and empty roles

- Source: R02. Design readiness: Ready. Execution status: Pass (automated).

**Expected:** `["CUSTOMER","PLATFORM_ADMIN"]` → isPlatformAdmin true and both roles; `["platform_admin"]` → false; `[]` → false with roles `[]`.

### TC-ME-003 — The token roles, not the assignments

- Source: R03. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a CUSTOMER caller is assigned PLATFORM_ADMIN in the database after the token was issued. **Expected:** isPlatformAdmin false, one role.

### TC-ME-004 — No target user, query or body

- Source: R04. Design readiness: Ready. Execution status: Pass (automated).

**Expected:** `?userId=<id>` → 400 "User Id is not a known field."; body `{}` → "Request Body must be empty."; `?x=1` with no token → 400 "X is not a known field." (not 401).

### TC-ME-005 — Credential failures

- Source: R05. Design readiness: Ready. Execution status: Pass (automated).

**Requests:** no token; `not-a-jwt`; no roles claim; roles as a string; stored token INACTIVE; user LOCKED; stored token expired. **Expected:** each 401 E10002 "Invalid or expired access token.".

### TC-ME-006 — A held table lock times out, and no row lock blocks

- Source: R06. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** with a 1-second timeout, another session holds the caller's `m_user` row FOR UPDATE → 200. Another session holds `LOCK TABLE authen.t_user_access_token IN ACCESS EXCLUSIVE MODE` → 408 E90001.

## Revision and execution history

- 2026-11-22: first version (Drake), executed by the automated tests of e-commerce-backend on branch `feat/drake-author-08-17` (`635e4a9`, PR e-commerce-backend#33): `MeApiTests` (HTTP + real PostgreSQL 17). Result: every case passes (dotnet test (full solution, branch feat/drake-author-08-17): Api 643, Application 43, Domain 73, Infrastructure 53, 0 failed). The first run of TC-ME-002 compared a list inside a tuple by reference; the assertion was split before this run. Mutation checks were run while implementing; their individual results were not recorded, so none are listed here.
