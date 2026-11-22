---
name: Drake Task Plan
description: Active plans and task records for Drake, Backend Developer.
---

# Drake Tasks

## Implement the author domain (17 APIs) in e-commerce-backend

- Owner: drake (accountable: ittikorn)
- Created at: 2026-11-20T00:00:00+07:00
- Started at: 2026-11-20T00:00:00+07:00
- Status: In progress
- Governing specs: `e-commerce/doc/api/author/01..17` (each approved; re-check frontmatter before each API)
- Code repo: `e-commerce-backend`; one task branch and PR per API; the owner starts each API

- Owner started 02..17 on 2026-11-21 ("เริ่มทำ author 01-17"), with `backend-development` and `dev-like-principal` required in every task.
- Per API: read the spec and sequence in full → readiness (raise gaps) → test-first slices → `test-cases.md` (api-test-case-creator) with every case automated → dev-like-principal quality check with measured lines → backend PR + Showcase PR.

- [x] 01 upsert role: backend#24 merged 2026-11-20, test cases in Showcase #270 merged; Api 321, Application 43, Domain 73, Infrastructure 53 passed
- [x] Spec defect found while reading 02: nine rule lines cut with "..." (cd3edbe); restore in #287, checker in #288
- [x] 02 upsert role batch (`POST v1/author/role/upsert/batch`): shared `RoleWriter`/`RoleRules` from 01, sorted target lock, `Error.At`, batch body reader; 16 cases, 34 tests pass; in review (backend PR and Showcase PR)
- [x] 03 inquiry role: backend#28 merged; test cases in #294
- [x] 04 upsert permission: backend#29 and #295 merged
- [x] 05 upsert permission batch: shared `PermissionWriter`/`PermissionRules`/`CurrentItem`; 12 cases, 28 tests; backend#30 and #296 merged
- [x] 06 inquiry permission: shared `MasterInquiryRules`/`MasterFilter`/`MasterQueryKeys`; 12 cases, 24 tests; backend#31 and #297 merged
- [x] 07 upsert scope: `MasterRules` generalised (code field, texts), `UpperCode`; 12 cases, 23 tests
- [x] 07 merged: backend#32 and Showcase #298
- [x] 08-17 in one backend PR at the owner's request on 2026-11-22 ("ทำให้ครบตั้งแต่ 08-17 แล้วทำมาเป็น pr เดียว"): e-commerce-backend#33, one commit per API and five refactor commits for the logic that gained a second caller; full run Api 643, Application 43, Domain 73, Infrastructure 53 passed; in review
  - 08 upsert scope batch (`ScopeWriter`, `ScopeRules`), 09 inquiry scope, 10 upsert user role (last-administrator rule), 11 inquiry user role, 12 me, 13 upsert role permission, 14 inquiry role permission, 15 upsert user permission, 16 inquiry user permission, 17 check permission (token claims only)
  - Test cases for 08-17, Function Book entries and lessons in the Showcase PR of branch `test/drake-author-08-17-test-cases`; in review
- [ ] After both PRs merge: advance `e-commerce/REPOS.md` to the merged backend revision and move this record to `success-task.md`
- [x] Add `no-cut-rules` to the CI document checks once #287 is merged (#287 and #288 merged; added in #289)

## Pending skill improvement

- Owner: drake (accountable: ittikorn)
- Created at: 2026-11-21T17:50:00+07:00
- Status: In review (author 04 Showcase PR)

- [x] `commit-and-pr` step 9 (both copies): write the Skills line last, from the Skill calls and reads actually made (lesson 2026-11-21)
- [x] `api-test-case-creator` `references/case-design.md` Concurrency row (both copies): the held row must be one the request locks, in a mode that conflicts only with the API's lock (lessons 2026-11-21)
- [x] `backend-development/references/verification.md` (both copies): collection assertions and lock proofs (lessons 2026-11-21)
- [x] `dev-like-principal/references/coding-guidelines.md` (both copies): `out var` in a ternary (lesson 2026-11-21)

## Security Auditor review of authen (auth, token, reset)

- Owner: drake (accountable: ittikorn)
- Created at: 2026-11-18T00:00:00+07:00
- Status: Pending
- Split from the authen implementation record (now in `success-task.md`); the raw reset-token log line it named is already removed (TC-RESET-011).

- [ ] Review login, refresh, logout, reset and create-new-password code against OWASP ASVS authentication and session rules; report findings to the owner before any fix
