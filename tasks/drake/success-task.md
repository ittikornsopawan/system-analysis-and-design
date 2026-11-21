---
name: Drake Completed Tasks
description: Verified completed task records of Drake, moved from todo.md.
---

# Drake Completed Tasks

## Copy the ready skills into .claude/skills

- Owner: drake (accountable: ittikorn)
- Created at: 2026-11-21T17:30:00+07:00
- Started at: 2026-11-21T17:30:00+07:00
- Status: Complete
- Completed at: 2026-11-21T16:28:44+07:00
- Owner request 2026-11-21: the Skill tool lists only `.claude/skills/`, so repo skills could not be loaded.

- [x] Copy the nine `ready` skills (tracked files only, 114 files); placeholders not copied
- [x] CI step: each copy equals `.agents/skills/<name>`, and every ready skill has a copy (drift and missing copy both caught locally)
- [x] `.agents/README.md`: edit in `.agents/skills/`, copy in the same change
- [x] CI fix: the first run failed (eval copies lacked frontmatter, exempted only under `.agents/skills/`; CI's `__pycache__` broke `diff -r`); `evals/` not copied, the diff skips `evals` and `__pycache__`; every CI step rerun locally
- [x] #291 merged (`7807c5c`, CI green)
- [x] Follow-up PR: lesson and commit-and-pr change (run every CI step locally before a PR that adds files outside the spec folders), both copies of the skill
- [x] After merge, a new session confirms the Skill tool lists the skills

Evidence: #291 merged (2026-11-21T16:28:44+07:00) and #292 (follow-up rule); on 2026-11-21 a new session listed the repo skills and the Skill tool loaded `backend-development` and `dev-like-principal` from `.claude/skills/`.

## Mandatory skill reading and recheck of backend#26

- Owner: drake (accountable: ittikorn)
- Created at: 2026-11-21T16:00:00+07:00
- Started at: 2026-11-21T16:00:00+07:00
- Status: Complete
- Completed at: 2026-11-21T15:51:10+07:00
- Owner order 2026-11-21: every later task must use `backend-development` and `dev-like-principal`.

- [x] Read both `SKILL.md` files, `code-quality-standards.md`, `e-commerce-dotnet.md` and `verification.md` in full
- [x] Rechecked backend#26: no code defect; Function Book has no entry to add; measured methods 7 and 10 lines; `code-structure.md` row "EF Core model" now names views
- [x] Role, commit-and-pr and verification reference changed; two lessons recorded; PR descriptions of backend#26 and #285 corrected
- [x] Josh confirms the one-phrase change to the approved `code-structure.md`; the owner merges

Evidence: #286 merged (2026-11-21T15:51:10+07:00), including the `code-structure.md` wording.

## Register reads the applicable consents from the consent view

- Owner: drake (accountable: ittikorn)
- Created at: 2026-11-21T15:00:00+07:00
- Started at: 2026-11-21T15:00:00+07:00
- Status: Complete
- Completed at: 2026-11-21T15:19:57+07:00
- Governing spec: `e-commerce/doc/api/authen-and-author/01-register` (approved; already names `consent.v_applicable_consent` and its LINQ since Showcase #279)

- [x] `GetApplicableConsentsAsync` reads `db.ApplicableConsents` (keyless view mapping); the `m_consent_type` query and the unused table records removed
- [x] All tests pass (Api 321, Application 43, Domain 73, Infrastructure 53); `dotnet format` clean; mutation: no expiry filter fails TC_REG_017
- [x] backend#26 reviewed and merged by the owner

Evidence: e-commerce-backend#26 merged (2026-11-21T15:19:57+07:00).

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
