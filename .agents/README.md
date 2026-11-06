---
name: Agent Resource Registry
description: Registry Claude and Codex read to discover applicable rules, workflows, roles, skills, templates, and project knowledge.
---

# Agent Resource Registry

This directory is the source of truth for repository-specific agent resources. Read this registry after identifying the active scope and, when applicable, the active project.

## Status

- `ready`: The resource has actionable content and may be used.
- `placeholder`: The resource is reserved for later design and must not be treated as instructions.

## Loading Order

1. Determine whether the active scope is a specific project or `repository-wide`.
2. Load every rule whose scope applies. Global rules always apply.
3. Load the active project's knowledge document when available.
4. Load the workflow that matches the task.
5. Load the relevant ready agent role.
6. Load only ready skills and templates needed by the selected workflow.
7. Prefer project-specific resources over global defaults without weakening global rules.

## Rules

| Resource | Status | Load when |
| --- | --- | --- |
| `rules/global.md` | ready | Every task |
| `rules/markdown.md` | ready | Creating or modifying an authored Markdown file |
| `rules/component-repositories.md` | ready | Reading, creating, cloning, verifying, or changing a Project's `REPOS.md` or `repository/` content |

## Workflows

| Resource | Status | Load when |
| --- | --- | --- |
| `workflows/spec-driven-development.md` | ready | Designing or changing behavior, APIs, data models, architecture, or backend code |

## Agent Roles

| Resource | Status | Intended phase |
| --- | --- | --- |
| `agents/product-owner.md` | placeholder | Product goals, value, priority, and acceptance outcomes |
| `agents/business-analyst.md` | placeholder | Stakeholder needs, processes, business rules, and requirements |
| `agents/system-analyst.md` | placeholder | System specifications and functional or non-functional requirements |
| `agents/solution-architect.md` | placeholder | Architecture, boundaries, dependencies, and technical decisions |
| `agents/backend-developer.md` | placeholder | C# backend implementation and automated tests |
| `agents/code-reviewer.md` | placeholder | Spec compliance and code quality review |

## Skills

Skills marked `placeholder` are unavailable until designed. Design each `SKILL.md` before adding it to a workflow.

| Resource | Status | Load when |
| --- | --- | --- |
| `skills/data-modeling/SKILL.md` | ready | Adding or changing a table, column, constraint, index, migration, schema doc, or ER diagram |
| `skills/api-contract-design/SKILL.md` | ready | Writing, reviewing, or changing an API spec, its examples, error codes, or its checker |
| `skills/commit-and-pr/SKILL.md` | ready | The user asks to commit, push, open or update a pull request, or hands work over for review |
| `skills/repository-bootstrap/SKILL.md` | ready | Setting up, cloning, verifying, or restoring Component Repositories declared by a Project |
| `skills/requirement-analysis/SKILL.md` | placeholder | Reserved |
| `skills/spec-authoring/SKILL.md` | placeholder | Reserved |
| `skills/system-modeling/SKILL.md` | placeholder | Reserved |
| `skills/dotnet-backend-development/SKILL.md` | placeholder | Reserved |
| `skills/test-design/SKILL.md` | placeholder | Reserved |
| `skills/code-review/SKILL.md` | placeholder | Reserved |
| `skills/diagram-creator/SKILL.md` | placeholder | Reserved |

The ready skills carry their own `references/`, `assets/` (templates ending in `.tmpl`), and `scripts/`; load those files only when the skill's procedure points to them.

## Templates

| Resource | Status | Use when |
| --- | --- | --- |
| `templates/api-spec.md` | ready | A project has no project-specific API template |
| `templates/schema.md` | ready | A project has no project-specific schema template |
| `templates/repository-manifest.md` | ready | Creating the required `REPOS.md` for a new or migrating Project |
| `templates/requirement-spec.md` | placeholder | Reserved for requirement specifications |
| `templates/system-spec.md` | placeholder | Reserved for system specifications |
| `templates/architecture-decision.md` | placeholder | Reserved for architecture decisions |
| `templates/code-review-report.md` | placeholder | Reserved for code review reports |
| `templates/handoff-report.md` | placeholder | Reserved for task handoffs |

## Task Artifacts

These paths are relative to the repository root.

| Resource | Status | Use when |
| --- | --- | --- |
| `tasks/todo.md` | ready | Planning and tracking every non-trivial task |
| `tasks/lessons.md` | ready | Reviewing and recording user corrections and reusable lessons |

## Repository Language

This path is relative to the repository root.

| Resource | Status | Use when |
| --- | --- | --- |
| `GLOSSARY.md` | ready | Interpreting canonical workflow, scope, and specification terms |

## Project Knowledge

| Resource | Status | Load when |
| --- | --- | --- |
| `knowledge/projects/e-commerce.md` | ready | The active project is `e-commerce` |

## Registration Rule

Register every new resource here with its status and loading trigger. A file's frontmatter describes the resource itself; this registry describes how it participates in repository work.
