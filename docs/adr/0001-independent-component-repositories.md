---
name: Use Manifest-Managed Independent Component Repositories
description: Records why Project source code is cloned as independently versioned repositories instead of being owned by the Showcase Repository or represented as Git submodules.
status: accepted
---

# Use Manifest-Managed Independent Component Repositories

Each Project declares its code repositories in `REPOS.md` and materializes them as independent Git checkouts under `repository/<repo-name>/`. This keeps specifications and showcase artifacts in the Showcase Repository while preserving the ownership, history, and delivery lifecycle of each Component Repository; full commit SHAs retain spec-to-code reproducibility.

## Considered Options

- **Manifest-managed independent clones — selected**: keeps repository ownership separate, supports multiple components, and makes setup and exact commit intent explicit.
- **Git submodules — rejected**: provide built-in commit pinning but impose submodule lifecycle and clone semantics that are not desired for this workspace.
- **Monorepo ownership — rejected**: keeps setup simple but couples source history and delivery to the Showcase Repository.
- **Unpinned independent clones — rejected**: are simple to clone but cannot reproduce the code baseline governed by approved specs.

## Consequences

- Every Project owns a `REPOS.md` manifest, including Projects with an empty repository list.
- Component Repository directories are ignored by the Showcase Repository, while their declared revisions are tracked in the manifest.
- Cross-repository delivery completes in the child repository before its remote-reachable revision is recorded in the Showcase Repository.
- Moving to Git submodules or another ownership model requires a superseding ADR.
