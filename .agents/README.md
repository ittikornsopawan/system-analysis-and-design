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
4. Resolve the named-agent registry and workspace rule when an assignment names, delegates to, or changes authority for a named agent.
5. Load the workflow that matches the task.
6. Load the relevant ready agent role.
7. Load only ready skills and templates needed by the selected workflow.
8. Prefer project-specific resources over global defaults without weakening global rules.

## Rules

| Resource | Status | Load when |
| --- | --- | --- |
| `rules/global.md` | ready | Every task |
| `rules/markdown.md` | ready | Creating or modifying an authored Markdown file |
| `rules/component-repositories.md` | ready | Reading, creating, cloning, verifying, or changing a Project's `REPOS.md` or `repository/` content |
| `rules/named-agent-workspaces.md` | ready | Naming or delegating to an agent, changing delivery authority, or reading or changing `.workspace/` content |

## Workflows

| Resource | Status | Load when |
| --- | --- | --- |
| `workflows/spec-driven-development.md` | ready | Designing or changing behavior, APIs, data models, architecture, or backend code |

## Agent Roles

| Resource | Status | Intended phase |
| --- | --- | --- |
| `agents/product-owner.md` | ready | Product goals, value, priority, scope, and acceptance outcomes |
| `agents/business-analyst.md` | ready | Stakeholder needs, processes, business rules, and Requirements |
| `agents/system-analyst.md` | ready | Specification completeness, system behavior, SQL analysis, traceability, and approval readiness |
| `agents/solution-architect.md` | ready | Architecture, boundaries, dependencies, integrations, and technical decisions |
| `agents/diagram-designer.md` | ready | Jinny's system diagram creation, source traceability, editable artifacts, and rendered visual review |
| `agents/api-documenter.md` | ready | Pre-implementation OpenAPI 3.1 publication and validation from Approved API Specs |
| `agents/backend-developer.md` | ready | Version-aware C# and .NET implementation with traceable automated tests |
| `agents/code-reviewer.md` | ready | Independent Spec compliance and engineering-quality review |
| `agents/security-auditor.md` | ready | Optional security review for identity, cryptography, tokens, payments, sensitive data, and trust boundaries |

## Skills

Skills marked `placeholder` are unavailable until designed. Design each `SKILL.md` before adding it to a workflow.

| Resource | Status | Load when |
| --- | --- | --- |
| `skills/data-modeling/SKILL.md` | ready | Adding or changing a table, column, constraint, index, migration, schema doc, or ER diagram |
| `skills/api-contract-design/SKILL.md` | ready | Writing, reviewing, or changing an API spec, its examples, error codes, or its checker |
| `skills/commit-and-pr/SKILL.md` | ready | The user directly authorizes delivery or a named-agent assignment carries validated delegated delivery authorization |
| `skills/repository-bootstrap/SKILL.md` | ready | Setting up, cloning, verifying, or restoring Component Repositories declared by a Project |
| `skills/agent-workspace/SKILL.md` | ready | An enabled named agent will change files, resume review fixes, or reconcile a merged pull request |
| `skills/requirement-analysis/SKILL.md` | placeholder | Reserved |
| `skills/spec-authoring/SKILL.md` | placeholder | Reserved |
| `skills/system-modeling/SKILL.md` | placeholder | Reserved |
| `skills/backend-development/SKILL.md` | ready | Implementing approved backend features, fixing implementation bugs or refactoring in any stack with spec-first clarification and meaningful test-first DB/API evidence |
| `skills/test-design/SKILL.md` | placeholder | Reserved |
| `skills/code-review/SKILL.md` | placeholder | Reserved |
| `skills/diagram-creator/SKILL.md` | ready | Creating, updating or reviewing system diagrams from specs, code or DB evidence, with editable artifacts and rendered review |

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

## Team Registry

| Resource | Status | Load when |
| --- | --- | --- |
| `.agents/team/agents.yaml` | ready | Resolving a named agent's role, scope, reporting line, workspace key, enabled state, or delivery-delegation capability |

## Approved Designs

| Resource | Status | Load when |
| --- | --- | --- |
| `designs/named-agent-workspace.md` | ready | Changing named-agent identity, delegated delivery authority, workspace lifecycle, or post-merge parking behavior |

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
