---
name: Global Agent Rules
description: Mandatory repository-wide rules Claude and Codex must load and follow for every task.
---

# Global Agent Rules

## Scope and Discovery

- Apply this rule to every task in the repository.
- Determine the active scope before editing: use the project named by the user, then referenced paths, then the current working directory; use `repository-wide` for root, `.agents/`, or cross-project work; ask when multiple project candidates remain.
- Read `.agents/README.md` before loading resources, then load every global and scoped rule that applies to the project, path, role, or task type.
- Treat resources marked `placeholder` as unavailable.
- Keep changes inside the active project or repository-wide task scope unless the user explicitly expands it.

## Evidence and Decisions

- Inspect relevant specs, code, tests, configuration, and local conventions before proposing or making changes.
- Ask the user about ambiguity that affects behavior, API contracts, data models, architecture, priority, or acceptance outcomes.
- Follow `.agents/workflows/spec-driven-development.md` for behavior, API, data model, architecture, and backend changes.
- Treat an existing spec as approved only when its frontmatter has `status: approved` with populated `approved_by` and `approved_at`; persist active-task approval in the spec before implementation.
- If a spec and implementation conflict, report the conflict and resolve it with the user before proceeding.
- If instructions or applicable rules conflict, stop, identify the conflicting statements, and ask the user which direction governs the task.

## Change Safety

- Preserve existing user changes and unrelated worktree state.
- Add a dependency, change architecture, or change a public contract only after the change is represented in an approved spec.
- Keep secrets, credentials, tokens, and sensitive data out of source control.

## Verification and Handoff

- Run verification proportionate to the change, such as build, tests, or static analysis.
- When verification cannot run, report the reason and the exact result that remains unverified.
- In the handoff, identify changed files, the governing spec, verification results, remaining risks, and follow-up work.
