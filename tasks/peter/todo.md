---
name: Peter Task Plan
description: Active plans and task records of the System Analyst Peter, resolved from the workspace key peter in the agent registry.
---

# Peter Tasks

## e-commerce: WP5b author permission assignment (specs 13–17)

Owner: peter
Status: In progress
Created at: 2026-11-06T00:00:00+07:00
Started at: 2026-11-17T09:27:31+07:00

- Moved from `tasks/owner/todo.md` at 2026-11-17T09:27:31+07:00 (owner order of 2026-11-17: "Start WP5b now"). Earlier blocker (2026-11-06, small scope) is lifted by that order.
- Governing: `docs/superpowers/specs/2026-11-06-author-design.md` (5b, A2, A8, A10, A12, A13, A17), `docs/superpowers/specs/2026-11-07-api-review-design.md` (JWT claims, Q12, Q22–Q24), `e-commerce/doc/api/template.md`, shape of author 01–12. Schema of the WP5a migration used as is.
- New specs start `status: in-review`, `approved_by: null`; the owner approves.

- [x] Send the open business questions (check source/input/output, PLATFORM_ADMIN exemption, grants to PLATFORM_ADMIN, scoped role grant without scope, request shape) to Josh as one batch — sent 2026-11-17.
- [ ] PR 1: `13-upsert-role-permission` and `14-inquiry-role-permission` (spec, `sequence.wsd`, SQL parity, `check_docs.py` needles, deliberate-fault test of the needles).
- [ ] PR 2: `15-upsert-user-permission` and `16-inquiry-user-permission` (same set).
- [ ] PR 3: `17` check (same set, after Josh answers Q1–Q3).
- [ ] Each PR: every `check_docs.py` sub-command, `audit_all.py` 0 findings, `test_sequence_skeleton.py`, `test_agent_workspace.py`, preflight; `run_db_tests.sh` only if SQL tests or a migration change; link sent to Josh when CI is green.

Verification: not started
