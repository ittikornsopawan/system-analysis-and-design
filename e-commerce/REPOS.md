---
name: E-commerce Component Repositories
description: Declares the independently versioned e-commerce backend and its reproducible baseline; read before materializing or changing any checkout under this Project's repository directory.
repositories:
  - name: e-commerce-backend
    remote: https://github.com/ittikornsopawan/e-commerce-backend.git
    path: repository/e-commerce-backend
    default_branch: main
    revision: d8255183cba54d0c2b218607456b895a70df32f0
    release_tag: null
    required: true
    purpose: Reproducible legacy .NET 10 Authen backend baseline with source, tests and coding guides; known gaps against newer API specifications remain documented in the component code guide.
---

# E-commerce Component Repositories

This manifest is the source of truth for the Project's Component Repositories. Machine-readable identities and revisions are declared only in frontmatter.

## Setup

Use the [repository-bootstrap skill](../.agents/skills/repository-bootstrap/SKILL.md) to validate this manifest and materialize the required checkout. Follow the rule's checks for safe paths, exact stored remotes, clean working trees, remote-reachable revisions and no-clobber staging.

Bootstrap checks out the declared full commit SHA in detached HEAD state. Create a task branch in the Component Repository before changing its source. Its commits, pushes and pull requests belong to its own remote, separately from the Showcase.

## Ownership

The Showcase owns this manifest, API contracts, specifications, schema/migration files, system diagrams and shared agent resources. The Checkout Directory contains `.gitkeep` and ignored independent clones; the Showcase does not track child source code, child Git metadata or build output. No Git submodule is used.

## Baseline scope

This initial baseline preserves the existing Authen implementation and its backend-specific history. Its build and 40 existing tests passed during migration. It is not a claim that the newer Authen specifications are fully implemented; read the component's `code.md` for known differences.

Migration authority and verification are recorded in the [approved migration design](../docs/superpowers/specs/2026-11-07-e-commerce-component-migration.md).

## Troubleshooting

Stop before changing an existing component checkout when it is dirty, has a different origin, contains unsafe paths or cannot resolve the declared revision on the default branch. Preserve user content and report the failed check rather than resetting, cleaning or re-cloning over it.
