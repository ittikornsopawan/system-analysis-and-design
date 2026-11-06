---
name: Component Repository Rules
description: Mandatory ownership, manifest, checkout, revision, and safety rules for independently versioned Git repositories inside a Project.
---

# Component Repository Rules

## Scope

Apply this rule whenever a task reads, creates, clones, verifies, changes, or references content under `<project>/repository/`, or creates or changes `<project>/REPOS.md`.

## Project Contract

- Every Project contains a `REPOS.md` Repository Manifest. A Project without component code declares `repositories: []`.
- `repository/` is a Checkout Directory, not source owned by the Showcase Repository.
- Each direct child at `repository/<repo-name>/` is an independent Component Repository with its own `.git` metadata, remote, branches, commits, and delivery lifecycle.
- Do not use Git submodules. Changing this decision requires a superseding ADR.
- Do not place or clone an undeclared repository in the Checkout Directory.

## Manifest Invariants

Every repository entry declares `name`, `remote`, `path`, `default_branch`, `revision`, `required`, and `purpose`. It may declare `release_tag` for human context.

- `name` equals the Git remote repository slug.
- `path` equals `repository/<name>` and resolves inside the active Project.
- `remote` is an exact credential-free GitHub HTTPS or SSH URL: `https://github.com/<owner>/<name>.git` or `git@github.com:<owner>/<name>.git`. Never store a token, password, or embedded credential.
- `default_branch` names the branch used for development.
- `revision` is the full commit SHA used as the reproducible baseline. A branch or tag is not a valid revision.
- `release_tag`, when non-null, is an informational valid Git tag name and must resolve to the same commit as `revision`.
- `required` is a boolean. Required repositories are part of the Project's default setup; optional repositories are materialized only when the user or task needs them.

## Git Ownership Boundary

- The Showcase Repository tracks `REPOS.md` and may track `repository/.gitkeep`.
- The Showcase Repository ignores each declared Component Repository using an explicit root `.gitignore` entry: `/<project>/repository/<repo-name>/`.
- The root `.gitignore` also ignores bootstrap staging directories with `/*/repository/.bootstrap-*/`.
- Do not stage or commit Component Repository files, Git metadata, build output, or working-tree state in the Showcase Repository.
- Preserve dirty Component Repository worktrees. Never switch, reset, clean, overwrite, or re-clone them.

## Revision Gate

Update `revision` only when the selected full commit SHA:

1. Exists on the declared remote.
2. Passed the Component Repository's applicable verification.
3. Is the intended baseline for the Project's approved specs.
4. Has completed its child-repository delivery before the Showcase Repository records it.

Never record an uncommitted state, branch name, tag name, abbreviated SHA, or local-only commit as `revision`.

## Migration Boundary

A legacy Project without `REPOS.md` is migration-pending. Report that state and stop repository bootstrap. Do not move, delete, overwrite, clone into, or create nested Git metadata in its existing `repository/` directory outside an explicitly approved migration task.
