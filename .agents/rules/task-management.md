---
name: Agent Task Management Rules
description: Mandatory rules for assigning, tracking, closing, archiving, and migrating repository tasks by owner and registered agent.
---

# Agent Task Management

## Resolve the task folder

- For work assigned to a named agent, read `.agents/team/agents.yaml` and use `tasks/<workspace_key>/`. Do not derive the folder from the agent's display name or role.
- For work directly owned by the repository owner, use `tasks/owner/`.
- For work spanning agents, keep one canonical task record under the accountable owner's folder and name the collaborators there. Do not copy the same task into multiple folders.
- Resolve and record the accountable owner before creating the task. If ownership is unclear, leave the task unassigned and ask the owner rather than guessing.

## Task files and format

- Keep the existing task-entry format: a scoped heading, status, ordered checkable items, and verification evidence. Add `Owner`, `Created at`, and `Status` to every task record.
- Use `todo.md` for pending, in-progress, or blocked work. Create `success-task.md` and `archive.md` in a task folder when the first completed or archived record is needed; do not create empty files just to populate every agent folder.
- When work starts, add `Started at`. When it is complete, add `Completed at`, mark the task `Complete`, and include the actual verification evidence before moving the complete record from `todo.md` to `success-task.md`.
- Use `archive.md` only for work the accountable owner has cancelled, superseded, or confirmed is no longer relevant. Record the final status, `Closed at`, and the reason; do not archive work merely because it is old, blocked, or inconvenient.
- Use ISO-8601 date-times with an explicit timezone offset for all timestamps, for example `2026-11-14T12:16:51+07:00`. Record the actual time of each event, not an estimated date.
- Keep the existing checklist style. Mark an item complete only when its stated acceptance criterion is met and the required evidence is recorded. Do not mark work complete based only on a merged pull request or an earlier plan.

## Blocked work

- Keep blocked work in `todo.md` with `Status: Blocked`; do not move it to `success-task.md` or `archive.md`.
- For every block, record `Blocked at`, the reason, who or what it is waiting on, and the next action. When unblocked, record `Unblocked at`, preserve the blocker history, and update the status. Record each later block as a separate event.
- A task may contain a blocked checklist item while other authorized work continues. Do not begin work explicitly held for owner approval or instruction.

## Legacy root backlog and migration

- `tasks/todo.md` is the legacy task file. Do not add new tasks there. Assignments that began before this rule may continue updating their existing root entries until complete; do not move, reorder, or rewrite their records while they are active.
- Do not migrate any legacy entries while `tasks/todo.md` contains unresolved `[ ]` items, including pending, active, blocked, deferred, or owner-waiting work. Resolve each item with evidence or record an owner-approved cancellation/supersession before migration.
- During migration, assign each legacy record to exactly one accountable owner folder. Move completed records to that folder's `success-task.md`, and cancelled, superseded, or obsolete records to `archive.md`, preserving their dates, status, rationale, and verification. If the owner cannot be established, stop and ask rather than assigning by inference.
- After all legacy records have been migrated and reconciled, replace the contents of `tasks/todo.md` with an index linking the per-owner and per-agent task files. Keep `tasks/lessons.md` at the repository root.
- Existing agent assignments and workspace state remain governed by `.agents/rules/named-agent-workspaces.md`; task-file migration does not authorize changing another agent's files or workspace.

## Completion check

Before handing off a task, verify that it is stored under the correct owner folder, has the required timestamps and status, includes blocker details when applicable, and has evidence for every completed item. For a legacy migration, reconcile every source record to exactly one destination and confirm no unresolved root item was moved.
