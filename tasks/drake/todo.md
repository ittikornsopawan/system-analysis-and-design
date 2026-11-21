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

- [x] 01 upsert role: backend#24 merged 2026-11-20, test cases in Showcase #270 merged; Api 321, Application 43, Domain 73, Infrastructure 53 passed
- [ ] 02..17 (16 APIs): waiting for the owner to start 02

## Register reads the applicable consents from the consent view

- Owner: drake (accountable: ittikorn)
- Created at: 2026-11-21T15:00:00+07:00
- Started at: 2026-11-21T15:00:00+07:00
- Status: In review
- Governing spec: `e-commerce/doc/api/authen-and-author/01-register` (approved; already names `consent.v_applicable_consent` and its LINQ since Showcase #279)

- [x] `GetApplicableConsentsAsync` reads `db.ApplicableConsents` (keyless view mapping); the `m_consent_type` query and the unused table records removed
- [x] All tests pass (Api 321, Application 43, Domain 73, Infrastructure 53); `dotnet format` clean; mutation: no expiry filter fails TC_REG_017
- [ ] backend#26 reviewed and merged by the owner

## Security Auditor review of authen (auth, token, reset)

- Owner: drake (accountable: ittikorn)
- Created at: 2026-11-18T00:00:00+07:00
- Status: Pending
- Split from the authen implementation record (now in `success-task.md`); the raw reset-token log line it named is already removed (TC-RESET-011).

- [ ] Review login, refresh, logout, reset and create-new-password code against OWASP ASVS authentication and session rules; report findings to the owner before any fix
