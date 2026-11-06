---
name: E-commerce Project Knowledge
description: Project index agents load when the active project is e-commerce to locate its authoritative specs, architecture, code, and templates.
---

# E-commerce Project Knowledge

## Scope

Load this document only when the active project is `e-commerce`. It is an index, not a copy of project facts that can be read from their authoritative files.

## Source Map

| Concern | Source of truth |
| --- | --- |
| API specifications | `e-commerce/doc/api/` |
| Schema specifications | `e-commerce/doc/schema/` |
| API contract | `e-commerce/api/api-contract.json` |
| Diagrams | `e-commerce/diagram/` and project-specific diagram directories |
| Database migrations | `e-commerce/db/migrations/up/` and `e-commerce/db/migrations/down/` |
| Database tests | `e-commerce/db/tests/` |
| C# backend | `e-commerce/repository/` |
| Backend architecture and feature conventions | `e-commerce/repository/project-structure.md` |
| Backend build configuration and target framework | `e-commerce/repository/Directory.Build.props` and `e-commerce/repository/Ecommerce.sln` |
| Backend tests | `e-commerce/repository/tests/` |

## Templates

- Use `e-commerce/doc/api/template.md` for e-commerce API specs.
- Use `e-commerce/doc/schema/template.md` for e-commerce schema specs.
- These project templates override `.agents/templates/api-spec.md` and `.agents/templates/schema.md`.

## Working Boundary

- Keep e-commerce changes inside `e-commerce/` unless the approved task explicitly changes shared agent resources.
- Read `e-commerce/repository/project-structure.md` before modifying backend code.
- Inspect project files directly for changing facts such as framework versions, current endpoints, commands, and directory contents.
