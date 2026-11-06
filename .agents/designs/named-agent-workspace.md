---
name: Named Agent Workspace Design
description: Approved repository-wide design for persistent named-agent clones, delegated PR delivery, and safe post-merge parking.
status: approved
approved_by: Ittikorn
approved_at: 2026-11-06T20:56:00+07:00
---

# Named Agent Workspace Design

## Objective

Give every enabled named agent a persistent full clone at `.workspace/<agent>` so read-only work can use the primary checkout while every file-changing assignment is isolated on a fresh task branch and delivered through a pull request.

## Decisions

- The primary checkout is the source for read-only work. Once an assignment will change files, the agent reads and writes only inside its managed clone for the rest of that assignment.
- A workspace is a full clone of the primary repository's credential-free `origin`, not a linked Git worktree and not a filesystem copy of the primary working tree.
- Agent names are stable lowercase slugs. Task branches use `<type>/<agent>-<topic>`.
- One named agent owns at most one active task or pull request at a time. A transient execution lock prevents concurrent sessions from editing the same workspace.
- Ignored local assignment metadata binds delivery authorization to the normalized task, path scopes, branch, and authorizer. Commit preflight rejects changes outside those scopes.
- Every agent may commit, push, and open its own pull request only when the assignment contains explicit delivery authorization from the user or an enabled named agent with the user-appointed `delegate-delivery` capability.
- Only the user grants or revokes `delegate-delivery`. The capability is not transitive and is effective only from the registry on `origin/main`.
- Delivery authority permits opening a pull request only. It does not grant business approval, design approval, merge authority, force-push authority, or permission to push to `main`.
- After opening a pull request, the workspace remains on the task branch for review fixes. It accepts no unrelated assignment until that pull request is merged or explicitly resolved.
- Parking requires a clean workspace and GitHub evidence that the matching pull request in the configured origin repository was merged into `main`. The lifecycle then fetches, fast-forwards local `main`, and deletes only the verified local task branch. It never deletes the remote branch.
- A closed but unmerged pull request remains intact until the user or an authorized lead chooses to resume or explicitly discard it.
- Existing `.claude/worktrees/*` and external Codex worktrees are outside this lifecycle and remain untouched.

## Safety Invariants

- `.workspace/` exists only below the primary checkout and is ignored by the primary repository. Managed workspaces are never nested.
- Remote mismatch, dirty state, divergent `main`, an open prior pull request, unsafe paths, missing authority, failed baseline verification, or ambiguous hosting state blocks mutation.
- The lifecycle never stashes, resets, cleans, overwrites, re-clones, force-pushes, merges a pull request, or deletes a workspace automatically.
- Stable identity and authority live in the tracked team registry. Branch, pull-request, lock, and working-tree state come from local Git, ignored lock metadata, and GitHub rather than tracked status files.

## Required Resources

- A global named-agent workspace rule and matching routing in `AGENTS.md` and `CLAUDE.md`.
- A canonical named-agent registry with Josh, Tommy, and Marry as the initial entries. Josh initially has `delegate-delivery`; the capability is not tied to his name or role.
- A model-invoked `agent-workspace` skill with deterministic create, status, prepare, release, and park operations.
- An updated `commit-and-pr` authorization boundary that accepts validated delegated delivery while preserving its no-merge rule.
- Isolated automated tests for authority, path safety, locking, workspace creation, branch preparation, and merged-pull-request parking.
