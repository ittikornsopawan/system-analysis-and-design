---
name: "Check Permission API Test Cases"
description: "Documented scenarios and expected results for GET v1/author/check, answered only from the caller's token claims; use for test planning and for the automated backend tests named after each case ID."
---

# Check Permission API Test Cases

## Source baseline and scope

- Method/path: `GET v1/author/check`
- Governing sources: [spec.md](spec.md) (claim source, Q1–Q3), [sequence.wsd](sequence.wsd) (validation patterns, claim checks, credential read), [login claim payload](../../authen-and-author/02-login/spec.md#example-jwt-payload)
- Source revision: `spec.md` and `sequence.wsd` last changed in `7180285`
- Source approval: approved (`approved_by: Josh (SA Lead, delegated by Ittikorn 2026-11-17)`, `approved_at: 2026-11-17T20:23:48+07:00`)
- Test design baseline: approved-source
- Scope and exclusions: TLS excluded; no rate limit in the spec. The generic 500 branch has no case of its own; it is the shared exception path tested by the other author APIs.
- Execution summary: every case automated in e-commerce-backend (test names start with the case ID) and passing; see [Revision and execution history](#revision-and-execution-history).

## Shared fixtures and observation prerequisites

- **Callers:** each case registers its own user with an ACTIVE stored access token whose JWT carries the `roles`, `permissions` and `scopes` claims it needs (any of them may be omitted or malformed on purpose).
- **Valid request (VR):** `GET v1/author/check?permission=<p>[&scope=<s>]`, `authorization: Bearer <JWT>`, `timestamp: <now UTC>`, no body.
- **Observation:** HTTP response (`data` exactly permission, scope, allowed; scope null when not asked).

## Coverage matrix

| Obligation ID | Source rule/section | Required behavior or boundary | Case IDs | Design coverage / gap |
| --- | --- | --- | --- | --- |
| R01 | spec Success | 200 S10000 "Check Permission Success"; allowed true with a held permission and scope; scope null when not asked | [TC-CHECK-001](#tc-check-001--allowed-with-and-without-a-scope) | designed |
| R02 | spec "always 200"; exact match | not held is allowed false, still 200; either claim missing makes it false; case-sensitive | [TC-CHECK-002](#tc-check-002--not-allowed-is-still-200) | designed |
| R03 | spec Q3, Q2 | PLATFORM_ADMIN adds nothing; the claims are flat, so a scope granted with another permission answers true | [TC-CHECK-003](#tc-check-003--platform-administrator-has-no-implicit-permission-and-claims-are-flat) | designed |
| R04 | spec Q1 | a direct grant in the database after issuance does not change the answer | [TC-CHECK-004](#tc-check-004--the-token-not-the-grant-tables) | designed |
| R05 | sequence validation note | permission mandatory, claim pattern, at most 64; scope optional, `<code>:*`, at most 64; empty values, unknown and repeated keys; joined messages | [TC-CHECK-005](#tc-check-005--query-validation) | designed |
| R06 | sequence validation note and order | 64-character boundaries accepted; no body; 400 before 401 | [TC-CHECK-006](#tc-check-006--boundaries-body-and-validation-before-the-credential) | designed |
| R07 | sequence JWT and credential notes | roles, permissions and scopes must each be an array of unique non-empty strings; a revoked or expired token or a user not ACTIVE → 401 E10002 | [TC-CHECK-007](#tc-check-007--credential-and-claim-failures) | designed |
| R08 | spec Q1; sequence timeout | locked grant tables and a locked user row do not block; a held credential table times out 408 | [TC-CHECK-008](#tc-check-008--no-grant-table-or-row-lock-blocks-and-a-held-credential-table-times-out) | designed |

## Detailed test cases

### TC-CHECK-001 — Allowed with and without a scope

- Source: R01. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** permissions `["catalog:manage","shop.product:manage"]`, scopes `["all:*","shop:*"]`. **Expected:** `?permission=catalog:manage&scope=all:*` → (catalog:manage, all:*, true); `?permission=shop.product:manage` → (shop.product:manage, null, true).

### TC-CHECK-002 — Not allowed is still 200

- Source: R02. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** permissions `["catalog:manage","CATALOG:READ"]`, scopes `["all:*"]`. **Expected (each 200):** payment:refund with shop:* → false; payment:refund → false; catalog:manage with shop:* → false; payment:refund with all:* → false; catalog:read → false (the token's upper-case claim is not this one).

### TC-CHECK-003 — Platform administrator has no implicit permission, and claims are flat

- Source: R03. Design readiness: Ready. Execution status: Pass (automated).

**Expected:** roles `["PLATFORM_ADMIN"]` with empty permissions and scopes → catalog:manage false. Permissions `["catalog:manage","shop.product:manage"]`, scopes `["shop:*"]` → catalog:manage with shop:* → true.

### TC-CHECK-004 — The token, not the grant tables

- Source: R04. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** a caller with empty claims gets a direct ACTIVE grant of permission P in the database; VR with P's claim form. **Expected:** allowed false.

### TC-CHECK-005 — Query validation

- Source: R05. Design readiness: Ready. Execution status: Pass (automated).

| Query | Expected `bizMessage` (400 E10001) |
| --- | --- |
| none / `permission=` / `catalog.manage` / `Catalog:manage` / `catalog:manage:all` / `catalog:manage%0A` / 65 characters | `Permission is required and must be a permission claim such as catalog:manage.` |
| `scope=` / `shop` / `SHOP:*` / 65 characters | `Scope must be a scope claim such as shop:*.` |
| `scope=shop` alone | `Permission is required and must be a permission claim such as catalog:manage, Scope must be a scope claim such as shop:*.` |
| `permission` twice | `Permission must not be duplicated.` |
| `userId=x` | `User Id is not a known field.` |

### TC-CHECK-006 — Boundaries, body, and validation before the credential

- Source: R06. Design readiness: Ready. Execution status: Pass (automated).

**Expected:** a 64-character permission and a 64-character scope held by the token → allowed true; body `{}` → 400 "Request Body must be empty."; no token with `?permission=bad` → 400 (not 401).

### TC-CHECK-007 — Credential and claim failures

- Source: R07. Design readiness: Ready. Execution status: Pass (automated).

**Requests (each 401 E10002 "Invalid or expired access token."):** no token; `not-a-jwt`; no roles claim; no permissions claim; no scopes claim; a repeated permission; permissions as a string; an empty scope name; a revoked stored token; a LOCKED user; an expired stored token.

### TC-CHECK-008 — No grant table or row lock blocks, and a held credential table times out

- Source: R08. Design readiness: Ready. Execution status: Pass (automated).

**Steps:** with a 1-second timeout: another session holds the caller's `m_user` row FOR UPDATE → 200; `LOCK TABLE ... IN ACCESS EXCLUSIVE MODE` on `author.t_user_permission`, `author.t_role_permission` and `author.t_user_role` in turn → 200 with allowed true each time; on `authen.t_user_access_token` → 408 E90001.

## Revision and execution history

- 2026-11-22: first version (Drake), executed by the automated tests of e-commerce-backend on branch `feat/drake-author-08-17` (`384d1d2`, PR e-commerce-backend#33): `CheckPermissionApiTests` (HTTP + real PostgreSQL 17, 21 tests including the 14 validation rows). Result: every case passes (dotnet test (full solution, branch feat/drake-author-08-17): Api 643, Application 43, Domain 73, Infrastructure 53, 0 failed). Mutation checks (each applied after the commit, then undone); each made at least one test fail: scope not checked (002), case-insensitive match (002), implicit PLATFORM_ADMIN (003), no credential check (007), each of the roles, permissions and scopes claims not required (007), no scope validation (005), `$` instead of `\z` (005), no 64-character limit on either claim (005), the limit off by one (006).
