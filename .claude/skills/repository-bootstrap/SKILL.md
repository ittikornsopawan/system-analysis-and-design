---
name: repository-bootstrap
description: Validate and materialize Component Repositories declared in a Project's REPOS.md. Use when setting up or cloning a Project, when a required checkout is missing, or when asked to verify or restore declared repository baselines. Do not use to migrate a legacy Project without a manifest, or to commit, push, or open pull requests.
---

# Repository Bootstrap

Materialize only repositories declared by the active Project. Preserve every existing working tree and stop when safe, reproducible setup cannot be proven.

## Preconditions

1. Read `.agents/rules/component-repositories.md` completely.
2. Resolve the active Project and locate `<project>/REPOS.md`.
3. If the manifest is missing, report `migration-pending` and stop. Do not create Git metadata or move existing files.
4. Parse the YAML frontmatter with a safe loader that rejects duplicate keys, aliases, and object deserialization. Validate every repository entry before running Git commands.

## Validate the Manifest

For each entry, prove that:

- All required fields exist: `name`, `remote`, `path`, `default_branch`, `revision`, `required`, and `purpose`.
- `remote` exactly matches `https://github.com/<owner>/<name>.git` or `git@github.com:<owner>/<name>.git`, with no embedded credentials.
- Strip the final `.git` only when extracting the remote repository slug; that slug equals `name`.
- `path` is the exact relative path `repository/<name>`, contains no `.` or `..` segments, and is not absolute.
- Resolve every existing path ancestor and reject symlinks or any escape from the active Project before constructing a missing leaf.
- `revision` is a full 40- or 64-character hexadecimal commit SHA, not a branch, tag, or abbreviated SHA.
- `release_tag` is either null or a non-empty string accepted by `git check-ref-format refs/tags/<release_tag>`; a non-null tag is informational and resolves to the same commit as `revision`.
- The Showcase Repository root `.gitignore` contains both `/<project>/repository/<name>/` and `/*/repository/.bootstrap-*/`.

Stop before cloning if any entry is invalid.

## Select Repositories

- Select every entry with `required: true`.
- Add an optional entry only when the user names it or the active task requires it.
- Never materialize an undeclared repository.

## Materialize Each Repository

### Missing Checkout

1. Confirm the Checkout Directory is safe, then create a unique staging parent named `.bootstrap-<name>-<nonce>` inside it.
2. Clone the declared `default_branch` from `remote` into `<staging-parent>/checkout`.
3. Fetch the declared default branch and remote tags without pruning.
4. Verify `revision^{commit}` exists and `revision` is an ancestor of `origin/<default_branch>`.
5. When `release_tag` is non-null, verify its peeled remote commit equals `revision`.
6. Checkout the exact revision in detached HEAD state.
7. Publish `<staging-parent>/checkout` with a no-clobber filesystem operation that fails when the declared target exists. Do not use ordinary move-to-directory semantics. Use an exclusive bootstrap lock and recheck the target immediately before publication when the runtime lacks a native no-replace rename.
8. Before publication failure, remove only the staging parent created by this run, leave the declared target absent, and report `blocked`.
9. After successful publication, remove the now-empty staging parent. If cleanup fails, keep the valid target, report `cloned` with a cleanup warning, and identify the staging path.

### Existing Checkout

1. Confirm the path is a Git working tree with the expected repository root.
2. Inspect tracked changes and all non-ignored untracked files before any fetch or checkout.
3. If tracked or non-ignored untracked changes exist, report `blocked` and leave the checkout untouched.
4. Read the stored value with `git config --get remote.origin.url` and require an exact manifest match. Do not use a URL-expanded command for identity comparison. A mismatch is `blocked`.
5. Fetch the declared default branch and remote tags without pruning or deleting local refs.
6. Verify `revision^{commit}` exists and `revision` is an ancestor of `origin/<default_branch>`.
7. When `release_tag` is non-null, verify its peeled remote commit equals `revision`.
8. List ignored files and compare them with paths tracked by the target revision. If any path collides, report `blocked` before checkout; otherwise preserve ignored files in place.
9. Checkout the exact revision in detached HEAD state.

Before modifying code, hand off to the applicable development workflow and create a task branch from the declared revision. This skill does not create the task branch unless the active task explicitly includes that action.

## Safety Boundaries

- Follow runtime approval requirements for network access and credential use.
- Never reset, clean, stash, overwrite, delete existing user content, commit, push, or open a pull request.
- Deletion is permitted only for the unique staging directory created by the current run.
- Never print credentials or credential-bearing URLs.
- Stop on authentication failure, network failure, remote mismatch, missing revision, dirty state, unsafe path, or ambiguous manifest data.

## Report

Report one status per selected repository:

- `cloned`: created and checked out at the declared revision.
- `verified`: existing clean checkout already matches or was safely moved to the declared revision.
- `skipped`: optional repository not required by the user or task.
- `blocked`: setup could not complete. For a missing checkout, the declared target remains absent; report whether a temporary staging directory required cleanup. For an existing clean checkout, also report any fetched refs before the block.

For each status, include the repository name, relative path, short revision, and any required user action. Completion requires every selected repository to be `cloned` or `verified`, with all non-selected optional repositories reported as `skipped`.
