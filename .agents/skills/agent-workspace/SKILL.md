---
name: agent-workspace
description: Prepare and manage persistent full-clone workspaces for enabled named agents during file-changing assignments, review fixes, and verified post-merge parking. Use for named-agent mutations or PR reconciliation; keep read-only work in the primary checkout and use repository-bootstrap for manifest-managed Component Repositories.
---

# Agent Workspace

Keep one named agent's task isolated from the primary checkout and from every other agent, while deriving volatile state from Git and GitHub rather than tracked status files.

## Preconditions

1. Read `.agents/rules/named-agent-workspaces.md` completely.
2. Establish the assignment contract: `agent`, registry `role`, bounded `task`, owned `scope`, `delivery`, and `authorized_by`.
3. Resolve the primary checkout. Read-only work stops here and uses that checkout; file-changing work continues in the managed clone.
4. Treat `.agents/team/agents.yaml` on `origin/main` as the authority source. The working branch cannot grant capabilities.

## Lifecycle

Run the helper from the primary checkout or any managed workspace:

```bash
python3 .agents/skills/agent-workspace/scripts/agent_workspace.py status --agent <name>
```

For a missing workspace, create the full clone from the primary checkout's `origin`:

```bash
python3 .agents/skills/agent-workspace/scripts/agent_workspace.py create --agent <name>
```

Before editing, prepare a fresh branch. Pass each verification command declared by the applicable repository or workflow; omit the option only when no baseline command is declared, and report that absence:

```bash
python3 .agents/skills/agent-workspace/scripts/agent_workspace.py prepare \
  --agent <name> \
  --type <type> \
  --topic <short-kebab-topic> \
  --task '<bounded outcome>' \
  --scope <repository-relative-path> \
  --delivery <open-pr|none> \
  --authorized-by <user-or-agent> \
  --baseline-command '<argv-style command>'
```

Repeat `--scope` when the assignment owns several path prefixes (`--scope a --scope b`); never join paths with commas in one `--scope`, `prepare` blocks a value that has a comma. `prepare` records the task, normalized scopes, delivery mode, authorizer, and branch in ignored local metadata, and blocks when that agent already has assignment metadata or an open PR.

`prepare` prints a lock token. Keep it private to the active session, work only in the returned workspace, and release it whenever that editing session ends:

```bash
python3 .agents/skills/agent-workspace/scripts/agent_workspace.py release \
  --agent <name> --token <lock-token>
```

When resuming review fixes, use `prepare --resume-pr <number-or-url>` with the original assignment fields. It must prove the recorded assignment and origin repository match the open pull request, current task branch, and `main` before returning the workspace.

When `delivery: open-pr`, run `commit-and-pr` from the managed workspace. Its preflight invokes `agent-workspace delivery-check` to prove the durable authorization and reject every changed path outside the recorded assignment scope. Opening the pull request ends delivery; it never authorizes merging or starting unrelated work.

To start the next task while the pull request is still open, suspend the delivered task (the order of the owner on 2026-11-11). Hold the lock, have a clean task branch, a pushed `HEAD` and an open pull request of the branch with the same head:

```bash
python3 .agents/skills/agent-workspace/scripts/agent_workspace.py suspend \
  --agent <name> --token <lock-token>
```

`suspend` moves the assignment to `.workspace/.state/<name>-prs/<branch-slug>.json`, switches to `main` and releases the lock; `status` lists the suspended records. `prepare` then accepts the open pull request because it is suspended. To fix a review, run `prepare --resume-pr <number-or-url>` with the original assignment fields while no other task is active. `park --pr` also closes a suspended record, after the merge is verified.

After the user or an authorized lead reports that the pull request merged, verify and park it:

```bash
python3 .agents/skills/agent-workspace/scripts/agent_workspace.py park \
  --agent <name> --pr <number-or-url>
```

`park` succeeds only when GitHub reports the matching PR merged into `main`, the workspace is clean, and local `HEAD` equals the PR head. It then fast-forwards local `main` and deletes only the verified local task branch. It never deletes the remote branch or the workspace.

## Blocked States

Stop and report the exact evidence when the helper blocks. Preserve dirty files, divergent branches, closed-but-unmerged pull requests, stale locks, mismatched remotes, and legacy worktrees. Destructive recovery is a separate user-authorized task.

## Done When

- Read-only work stayed in the primary checkout, or mutation work stayed entirely inside the correct managed clone.
- The assignment authority, baseline result, branch, lock, and pull-request state were proven.
- An open PR remains available for review fixes, or a merged PR has returned the clean workspace to synchronized `main`.
- No pull request was merged and no unrelated workspace or branch was changed.
