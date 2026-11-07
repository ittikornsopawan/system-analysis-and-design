---
name: E-commerce Project Knowledge
description: Project index agents load when the active project is e-commerce to locate its authoritative specs, architecture, code, and templates.
---

# E-commerce Project Knowledge

## Scope

Load this document only when the active project is `e-commerce`. It is an index, not a copy of project facts that can be read from their authoritative files.

## Component Repositories

Status: `manifest-managed`

- Read `e-commerce/REPOS.md` for the authoritative repository identities, remotes and pinned revisions before accessing component code.
- Use `repository-bootstrap` to validate the manifest and materialize declared repositories. Each checkout has its own Git metadata, remote and delivery lifecycle; it is ignored by the Showcase Repository.
- The approved ownership migration and verification are recorded in `docs/superpowers/specs/2026-11-07-e-commerce-component-migration.md`. This migration preserves the legacy Authen baseline and does not close its known API-specification gaps.

## Source Map

| Concern                                          | Source of truth                                                                         |
| ------------------------------------------------ | --------------------------------------------------------------------------------------- |
| API specifications                               | `e-commerce/doc/api/`                                                                   |
| Schema specifications                            | `e-commerce/doc/schema/`                                                                |
| API contract                                     | `e-commerce/api/api-contract.json`                                                      |
| Diagrams                                         | `e-commerce/diagram/` and project-specific diagram directories                          |
| Database migrations                              | `e-commerce/db/migrations/up/` and `e-commerce/db/migrations/down/`                     |
| Database tests                                   | `e-commerce/db/tests/`                                                                  |
| Repository Manifest                             | `e-commerce/REPOS.md`                                                                    |
| C# backend                                       | `e-commerce/repository/e-commerce-backend/`                                                                |
| Backend architecture and feature conventions     | `e-commerce/repository/e-commerce-backend/project-structure.md`                                            |
| Backend build configuration and target framework | `e-commerce/repository/e-commerce-backend/Directory.Build.props` and `e-commerce/repository/e-commerce-backend/Ecommerce.sln` |
| Backend tests                                    | `e-commerce/repository/e-commerce-backend/tests/`                                                          |

## Templates

- Use `e-commerce/doc/api/template.md` for e-commerce API specs.
- Use `e-commerce/doc/schema/template.md` for e-commerce schema specs.
- These project templates override `.agents/templates/api-spec.md` and `.agents/templates/schema.md`.

## Working Boundary

- Keep e-commerce changes inside `e-commerce/` unless the approved task explicitly changes shared agent resources.
- Read `e-commerce/repository/e-commerce-backend/project-structure.md` before modifying backend code.
- Backend changes belong to the declared Component Repository; commit and open its pull requests against its own remote. Deliver and verify a component commit before updating the Showcase manifest revision.
- Inspect project files directly for changing facts such as framework versions, current endpoints, commands, and directory contents.
