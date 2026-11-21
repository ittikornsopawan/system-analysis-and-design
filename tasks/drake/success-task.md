---
name: Drake Completed Tasks
description: Verified completed task records of Drake, moved from todo.md.
---

# Drake Completed Tasks

## Pin the backend to .NET 11 in the Showcase

- Owner: drake (accountable: ittikorn; requested by josh)
- Created at: 2026-11-18T00:00:00+07:00
- Completed at: 2026-11-18T02:03:00+07:00
- Status: Complete

- [x] Backend retarget merged: e-commerce-backend#1 (merge commit `61bedeb`)
- [x] `e-commerce/REPOS.md` and the handoff say .NET 11 / C# 15. Evidence: Showcase #233 merged 2026-11-18; the pin was later moved by Josh in #266.

## Implement authen-and-author (10 APIs) in e-commerce-backend

- Owner: drake (accountable: ittikorn)
- Created at: 2026-11-18T00:00:00+07:00
- Started at: 2026-11-18T00:00:00+07:00
- Completed at: 2026-11-20T23:59:00+07:00
- Status: Complete
- Governing specs: `e-commerce/doc/api/authen-and-author/01..10` (approved)

- [x] Shared foundation: envelope (#2), JWT, rate limit, EF Core + ForUpdate + PostgreSQL fixture (#3), null fix (#4)
- [x] 01 register (#5, #6), 02 login (#7), 03 reset (#8), 04 create new password (#9), 05 refresh (#10), 06 logout (#11)
- [x] 07/08 profile (#12, #13), 09/10 address (#14, #15)
- [x] Owner standards applied: quality catch-up of 01-08 (#16), strict email rule (#17), legacy /me removed and READ ONLY for 08/10 (#18), dead code and docs (#20, #22)
- [x] Every case of each `test-cases.md` automated and passing; raw reset-token log line removed (TC-RESET-011)
- [x] `code-structure.md` rewritten and approved (Showcase #259, #262, #265); LINQ beside SQL for 01-10 (#264)
- Evidence: every PR above merged in e-commerce-backend; last run Api 321, Application 43, Domain 73, Infrastructure 53 passed.
- The Security Auditor review moved to its own record in `todo.md`.
