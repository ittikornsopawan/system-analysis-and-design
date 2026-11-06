---
name: <project-name> Component Repositories
description: Declares the independently versioned Git repositories required by this Project and tells humans and agents how to materialize them.
repositories:
  - name: <github-repository-name>
    remote: https://github.com/<owner>/<github-repository-name>.git
    path: repository/<github-repository-name>
    default_branch: main
    revision: <full-commit-sha>
    release_tag: null
    required: true
    purpose: <repository-purpose>
---

# Component Repositories

This manifest is the source of truth for Component Repositories in this Project. Keep repository declarations in frontmatter; do not duplicate their values in the document body.

## Setup

Use the `repository-bootstrap` skill to validate this manifest and materialize the declared repositories. Required repositories are included in the default setup. Optional repositories are included only when the user or active task needs them.

## Working State

Bootstrap checks out the full commit SHA declared by `revision` as a reproducible baseline. `release_tag: null` means no release tag is declared; a non-null tag is optional human context and never replaces the commit SHA. Create a task branch from the revision before changing code. Each Component Repository owns its commits, pushes, pull requests, and verification.

## Troubleshooting

Bootstrap stops instead of changing an existing checkout when its working tree is dirty, its remote differs from the manifest, its revision cannot be resolved, or credentials or network access are unavailable.
