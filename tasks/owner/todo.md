---
name: Owner Task Plan
description: Active plans and task records directly owned by the repository owner.
---

# Owner Tasks

## repository-wide: Update the agent resource registry and diagram role

Owner: owner
Status: Blocked
Created at: 2026-11-14T12:16:51+07:00

Blocker:
- Blocked at: 2026-11-14T12:21:34+07:00
- Reason: Jinny's active assignment includes `.agents/README.md` and `.agents/agents/diagram-designer.md`.
- Waiting on: Jinny to finish the assignment and release those paths.
- Next action: Recheck the assignment and current main after the paths are released, then register the new rule and update the diagram role.

Verification: Not run; edits to both paths are deferred to avoid interfering with the active assignment.

## repository-wide: Migrate the legacy root backlog

Owner: owner
Status: Blocked
Created at: 2026-11-14T12:16:51+07:00

Blocker:
- Blocked at: 2026-11-14T12:21:34+07:00
- Reason: `tasks/todo.md` contained 40 unresolved `[ ]` items, including work associated with active or suspended named-agent assignments.
- Waiting on: Completion or owner-approved disposition of every legacy task, with active agents retaining control of their assignments.
- Next action: Re-audit the remaining 15 items; close each only with evidence or owner-approved cancellation/supersession, then migrate.
- Progress at: 2026-11-14T12:34:25+07:00 — 25 items closed with evidence; 15 remain unresolved.

- [ ] Resolve every legacy root task with evidence or owner-approved closure before migrating any record.
- [ ] Migrate closed legacy records to the correct owner folders and replace the root task file with an index.

Verification: 25 checklist items were closed with existing merged-PR or checker evidence; `rg -c '^\s*[-*] \[ \]' tasks/todo.md` reports 15 unresolved items. `git diff --check -- tasks/todo.md` passes. Migration remains blocked, and no active agent workspace was changed.
