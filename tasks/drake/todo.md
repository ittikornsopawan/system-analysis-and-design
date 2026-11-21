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
- [ ] 03 inquiry role
- [ ] 04 upsert permission
- [ ] 05 upsert permission batch
- [ ] 06 inquiry permission
- [ ] 07 upsert scope
- [ ] 08 upsert scope batch
- [ ] 09 inquiry scope
- [ ] 10 upsert user role
- [ ] 11 inquiry user role
- [ ] 12 me
- [ ] 13 upsert role permission
- [ ] 14 inquiry role permission
- [ ] 15 upsert user permission
- [ ] 16 inquiry user permission
- [ ] 17 check permission
- [x] Add `no-cut-rules` to the CI document checks once #287 is merged (#287 and #288 merged; added in #289)

## Register reads the applicable consents from the consent view

- Owner: drake (accountable: ittikorn)
- Created at: 2026-11-21T15:00:00+07:00
- Started at: 2026-11-21T15:00:00+07:00
- Status: In review
- Governing spec: `e-commerce/doc/api/authen-and-author/01-register` (approved; already names `consent.v_applicable_consent` and its LINQ since Showcase #279)

- [x] `GetApplicableConsentsAsync` reads `db.ApplicableConsents` (keyless view mapping); the `m_consent_type` query and the unused table records removed
- [x] All tests pass (Api 321, Application 43, Domain 73, Infrastructure 53); `dotnet format` clean; mutation: no expiry filter fails TC_REG_017
- [ ] backend#26 reviewed and merged by the owner

## Mandatory skill reading and recheck of backend#26

- Owner: drake (accountable: ittikorn)
- Created at: 2026-11-21T16:00:00+07:00
- Started at: 2026-11-21T16:00:00+07:00
- Status: In review
- Owner order 2026-11-21: every later task must use `backend-development` and `dev-like-principal`.

- [x] Read both `SKILL.md` files, `code-quality-standards.md`, `e-commerce-dotnet.md` and `verification.md` in full
- [x] Rechecked backend#26: no code defect; Function Book has no entry to add; measured methods 7 and 10 lines; `code-structure.md` row "EF Core model" now names views
- [x] Role, commit-and-pr and verification reference changed; two lessons recorded; PR descriptions of backend#26 and #285 corrected
- [ ] Josh confirms the one-phrase change to the approved `code-structure.md`; the owner merges

## Security Auditor review of authen (auth, token, reset)

- Owner: drake (accountable: ittikorn)
- Created at: 2026-11-18T00:00:00+07:00
- Status: Pending
- Split from the authen implementation record (now in `success-task.md`); the raw reset-token log line it named is already removed (TC-RESET-011).

- [ ] Review login, refresh, logout, reset and create-new-password code against OWASP ASVS authentication and session rules; report findings to the owner before any fix
