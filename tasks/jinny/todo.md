---
name: Jinny Task Plan
description: Active plans and task records of the Diagram Designer Jinny, resolved from the workspace key jinny in the agent registry.
---

# Jinny Tasks

Completed records are in `success-task.md`.

## repository: CI runs the diagram generator checks

Owner: jinny
Status: In review
Created at: 2026-11-20T21:48:23+07:00
Started at: 2026-11-20T21:48:23+07:00

Authority: Josh (SA Lead) after #276 was closed, `authorized_by: ittikorn`, delivery `open-pr`. Scope: `.github/workflows/checks.yml`, `e-commerce/diagram/domain/domain-model-verification.md`, `tasks/jinny`, `tasks/lessons.md`, `.agents/skills/commit-and-pr`.

- [x] Prepare from `main` `099f3c7` (after #283); baseline: domain and layered `--check` PASS.
- [x] Add the step "Diagram generators (--check)" to the rewritten `checks.yml`.
- [x] Re-add the verification record (cause `3c740fa`, refresh by #283) to `domain-model-verification.md`.
- [x] Record the owner's correction (hand off only a mergeable PR with green CI) in `tasks/lessons.md` and `commit-and-pr`.
- [ ] Open the PR; report it ready only when it is OPEN, MERGEABLE, CI green and `headRefOid` = local HEAD; close after merge.
