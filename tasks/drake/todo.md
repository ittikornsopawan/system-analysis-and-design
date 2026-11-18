---
name: Drake Task Plan
description: Active plans and task records for Drake, Backend Developer.
---

# Drake Tasks

## Pin the backend to .NET 11 in the Showcase

- Owner: drake (accountable: ittikorn; requested by josh)
- Created at: 2026-11-18T00:00:00+07:00
- Status: In progress

- [x] Backend retarget merged: e-commerce-backend#1 (merge commit `61bedeb`)
- [ ] Update `e-commerce/REPOS.md` (purpose wording, pinned revision) and handoff line 60 (".NET 11 / C# 15")
- [ ] Run preflight and checks, open PR, send the link to Josh when CI is green

## Implement authen-and-author (10 APIs) in e-commerce-backend

- Owner: drake (accountable: ittikorn)
- Created at: 2026-11-18T00:00:00+07:00
- Started at: 2026-11-18T00:00:00+07:00
- Status: In progress
- Governing specs: `e-commerce/doc/api/authen-and-author/01..10` (each approved; re-check frontmatter before each API), `api-contract.json`, `doc/permission-scope.md`
- Code repo: `e-commerce-backend` (.NET 11 / C# 15); one task branch and PR per slice; owner approved starting here on 2026-11-18

- [x] Baseline on net11.0: build 0 warnings, 40 tests pass (backend#1)
- [x] Throw-away PostgreSQL 17 with all 54 tables loaded from `e-commerce/db/migrations/up` (no Docker daemon; same method as `run_db_tests.sh`)
- [ ] Shared foundation: response envelope and bizCodes, requestId/timestamp headers, error mapping, JWT verify, rate limit (429 E90002), transaction and lock helper, real-DB test fixture
- [x] Shared foundation merged: envelope (#2), JWT, rate limit, EF Core + ForUpdate + PostgreSQL fixture (#3), null fix (#4)
- [ ] Owner standards of 2026-11-18 apply to every slice: reusable functions placed by layer, each layer keeps its meaning, api-test-case-creator test cases automated and all passing before done
- [ ] 01 register (REPEATABLE READ, consents, address, referrer, field encryption) — with `test-cases.md` and every case automated
- [ ] 02 login (generic 401, attempts, roles/permissions claims)
- [ ] 03 reset password (request) and 04 create new password (atomic consume, revoke)
- [ ] 05 refresh token and 06 logout (rotation, replay, session revoke, JWT revoke check)
- [ ] 07/08 user profile and 09/10 user address
- [ ] Security Auditor review (auth, token, reset); remove raw reset-token log line
- [ ] Ask Josh for a `code-structure.md` update when the structure changes
- Not verified yet: SQL in specs against a running backend; every `sequence.wsd` render
