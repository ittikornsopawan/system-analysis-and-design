---
name: Owner Task Plan
description: Active plans and task records directly owned by the repository owner.
---

# Owner Tasks

## Register Drake as Backend Developer

- Owner: ittikorn (accountable); executed by Drake
- Created at: 2026-11-18T00:00:00+07:00
- Status: In progress

- [x] Add `drake` to `.agents/team/agents.yaml` (role `backend-developer.md`, reports to ittikorn, no capabilities) and to the registry test
- [x] `python3 -m unittest discover -s .agents/skills/agent-workspace/tests` passes (27 tests)
- [ ] Owner approves and merges the registry PR; authority applies only after merge into `origin/main`
- [ ] Then prepare `.workspace/drake` and start the handoff work (`docs/handoff/2026-11-17-dev-handoff.md`)

## Create the `dev-like-principal` skill

- Owner: ittikorn
- Created at: 2026-11-18T14:04:00+07:00
- Started at: 2026-11-18T14:04:00+07:00
- Status: In review (awaiting owner feedback)

- [x] Write `.agents/skills/dev-like-principal/SKILL.md` and its references/assets (decision framework, architecture review, .NET coding guidelines, review checklist, anti-patterns, verification, worked examples, ADR template)
- [x] Register the skill in `.agents/README.md`
- [x] Validate structure (frontmatter, links, line counts) with the skill-creator validator
- [x] Run three eval cases (feature development, architecture design, code review) with and without the skill and grade them
- [x] Write the test report in `docs/handoff/` with sample outputs
- [ ] Owner reviews the skill and the test report; iterate if feedback is given

Evidence: `quick_validate` → "Skill is valid!"; 8/8 referenced files exist; eval with skill 22/22, without 19/22 (`docs/handoff/2026-11-18-dev-like-principal-test-report.md`).

## Add code quality standards and the Function Book to `dev-like-principal`

- Owner: ittikorn
- Created at: 2026-11-18T19:30:00+07:00
- Started at: 2026-11-18T19:30:00+07:00
- Status: In review (awaiting owner feedback)

- [x] Write `references/code-quality-standards.md` (Function Book reuse, formatting, short functions, comments, class/domain separation, before-coding steps, before-delivery check) and `assets/function-book.md.tmpl`
- [x] Seed `e-commerce/doc/function-book.md` from component revision `648226c`
- [x] Make `dev-like-principal` the code gate: `SKILL.md`, review checklist, coding guidelines
- [x] Route every code-writing skill through it: backend-development, data-modeling, api-contract-design, diagram-creator; plus `rules/global.md`, backend-developer and code-reviewer roles, e-commerce knowledge, `.agents/README.md`
- [x] Eval `code-gate-newsletter-subscription`: current backend-development (with gate) vs the HEAD snapshot (without)
- [x] Update the test report
- [x] Owner decided the email rule (2026-11-18): the `EmailAddress` rule governs, with the dot required in the domain; validity only, no trimming or lower-casing. Recorded in api-conventions "Email address", spec 01-register (approval metadata updated), register TC-REG-006 and reset TC-RESET-002 (new inputs Not run), and the Function Book
- [ ] Drake (after his current create-new-password PR): make `EmailAddressFormat.IsValid` the single rule as written in api-conventions (one `@`, non-empty local part, `.` in the domain, ≤ 254, plain address with no spaces/display name/angle brackets); have `EmailAddress.Create` call it; test-first with the new TC-REG-006 and TC-RESET-002 inputs; then remove the pending note from the Function Book
- [ ] Owner reviews; nothing committed yet

Evidence: `quick_validate` → "Skill is valid!"; 10/10 referenced files exist; code-gate eval: old_skill 5/8, with gate 7/8 (iteration 2), 8/8 after the length-rule fix (iteration 3); report section 6 of `docs/handoff/2026-11-18-dev-like-principal-test-report.md`; lesson in `tasks/lessons.md`.
