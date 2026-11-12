---
name: Named Agent Workspace Rules
description: Mandatory identity, authority, isolation, lifecycle, and safety rules for named agents that read from the primary checkout or change files in managed workspaces.
---

# Named Agent Workspace Rules

## Scope

Apply this rule whenever an assignment names an agent registered in `.agents/team/agents.yaml`, delegates work to that agent, changes its authority, or reads or changes its managed workspace.

The **primary checkout** is the repository checkout that owns the root `.workspace/` directory. A **managed workspace** is the persistent full clone at `.workspace/<agent>`. A workspace is **parked** only when it is clean, on `main`, and fast-forwarded to `origin/main`.

## Identity and Authority

- Resolve the named agent from `.agents/team/agents.yaml` on `origin/main` before loading its generic role file or accepting delegated delivery authority.
- Use only enabled agents whose lowercase slug, role, scope, and workspace key pass registry validation.
- Only the authorized user grants or revokes `delegate-delivery`. An agent cannot grant the capability to itself or another agent, and the capability is never transitive.
- Registry changes affect authority only after merge into `origin/main`. Never trust authority read from a task branch or managed workspace.
- `delegate-delivery` authorizes another agent to commit, integrate the latest base into its task branch, push that branch, and open its own pull request when the assignment explicitly says `delivery: open-pr`. It does not authorize business or design approval, merging a PR or task branch into `main`, auto-merge, force pushing, hook bypass, or pushing to `main`.
- Every named agent may open only its own task pull request and only under explicit user or validated delegated authorization. No agent merges a pull request.

## Assignment Contract

Before a file-changing assignment starts, establish all of:

- `agent`: the enabled registry name.
- `role`: the registry role; a temporary perspective may supplement but never replace it.
- `task`: one bounded outcome.
- `scope`: the repository or project paths the task owns.
- `delivery`: `open-pr` or `none`.
- `authorized_by`: the authorized user or an enabled agent with `delegate-delivery` on `origin/main` when `delivery` is `open-pr`.

An incomplete or contradictory contract blocks file changes. A named agent may hold only one active task at a time. By the order of the owner on 2026-11-11 ("a worker who finishes starts the next task without waiting for the merge"), a named agent may have several open pull requests when the assignment of each one is **suspended** (see the lifecycle). An assignment without `delivery: open-pr` stops before commit or push.

Persist the normalized contract as ignored local assignment metadata when the task branch is created. Every review-resume and delivery preflight must match that metadata, and every changed path must remain inside its recorded scope. Remove the metadata only after verified post-merge parking or an explicitly approved discard.

## Read and Write Routing

- Perform read-only assignments from the primary checkout.
- Before the first file change, prepare the named agent's managed workspace and perform every remaining read and write for that assignment inside it.
- Clone from the primary checkout's credential-free `origin`; never copy the primary working tree or clone from its filesystem path.
- Require each managed workspace to own its `.git` directory and identity markers; a linked worktree or unmarked clone cannot impersonate a managed workspace.
- Create managed workspaces only below the primary checkout's `.workspace/`. Resolve the primary checkout even when invoked from an existing managed workspace; never create nested `.workspace/` directories.
- Keep Component Repository setup under `repository-bootstrap`. This rule does not materialize, migrate, or replace repositories governed by a Project's `REPOS.md`.

## Lifecycle

1. **Parked**: the workspace is clean, on `main`, synchronized by fast-forward with `origin/main`, and has no active pull request.
2. **Prepared**: acquire a transient execution lock, run the repository-declared baseline verification when one exists, and create `<type>/<agent>-<topic>` from the synchronized `main`.
3. **Working**: keep the assignment inside its declared scope and preserve the execution lock for the editing session.
4. **PR open**: use `commit-and-pr` only when delivery is authorized. Release the execution lock when the session ends, but keep the workspace on the task branch for review fixes.
5. **Review**: a later session may reacquire the lock and resume only the same task and pull request.
6. **Parked again**: after GitHub proves the matching pull request in the workspace's configured origin repository merged into `main`, require a clean workspace and matching local PR head, fetch and fast-forward `main`, delete only the verified local task branch, remove its assignment metadata, and release the lock.

**Suspended**: after delivery, `suspend` moves the assignment of a task whose pull request is open to the record `.workspace/.state/<agent>-prs/<branch-slug>.json`, returns the workspace to `main` and releases the lock, so the agent can start the next task. It requires a clean task branch, a pushed `HEAD` and an open GitHub pull request of the same branch with the same head. `prepare` accepts open pull requests only when every one of them is suspended, and the agent still has one active task. `prepare --resume-pr` restores a suspended record for review fixes (no other active task allowed; a pure fast-forward of the branch is accepted) and `park --pr` closes it after the merge is verified.

Before assigning new work, reconcile the previous pull request. A closed but unmerged pull request remains on its branch until the user or an authorized lead chooses `resume` or explicitly approves destructive discard.

## Safety Gates

- Block on an unsafe or symlinked path, invalid registry, disabled agent, remote mismatch, nested workspace, dirty state, divergent `main`, branch collision, concurrent lock, unauthorized delivery, baseline failure, missing GitHub evidence, mismatched pull-request base or head, or local commits that are not the verified PR head.
- Never stash, reset, clean, overwrite, re-clone, force push, bypass hooks, merge a PR or task branch into `main`, enable auto-merge, delete a remote branch, or delete a workspace automatically. Base-to-task integration for authorized PR delivery follows `commit-and-pr` and must preserve unrelated work and the protected base branch.
- Treat stale locks as evidence to inspect, not permission to remove them. Only the user or an authorized lead may approve lock recovery after proving no session is active.
- Existing `.claude/worktrees/*`, external Codex worktrees, and unrelated dirty worktrees remain untouched.
