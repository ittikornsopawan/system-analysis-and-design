---
name: Owner Task Plan
description: Active plans and task records directly owned by the repository owner.
---

# Owner Tasks

## repository-wide: Define per-agent task tracking

Owner: owner
Status: In progress
Created at: 2026-11-14T12:16:51+07:00
Started at: 2026-11-14T12:16:51+07:00

- [x] Confirm the requested layout, one accountable owner per task, timestamp format, blocker details, and the legacy migration gate with the owner.
- [x] Audit active task-path instructions and the legacy root backlog without modifying other agents' assignments.
- [x] Add the task-management rule and update non-overlapping repository instructions and skills to resolve the correct task folder.
- [x] Verify the rule and non-overlapping references: all nine changed Markdown files have required frontmatter and no trailing whitespace, `AGENTS.md` and `CLAUDE.md` task sections match, and `tasks/todo.md` remains unchanged.
- [ ] Verify the resource registry and diagram role after Jinny's active scope is released.

Verification: `git diff --check` passed; the targeted Markdown frontmatter/whitespace check passed for nine files; the two root task sections match; the legacy root backlog remains unchanged at 40 open items.

Progress (2026-11-14T12:34:25+07:00): Closed 25 legacy checklist items in `tasks/todo.md` where merged-PR or recorded verification evidence supported completion. Examples include delivery/reconciliation work for PRs #27, #29–#31, #40, #42, #46, #48, #49, #54, #58–#64, #92, #97, #99, #104, #107, #110, #114, #119, #120 and #125, plus completed checker/template verification. The legacy backlog now has 15 unchecked items. No agent workspace was edited; Peter's active assignment and lock remain in place.

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
