---
name: Claude Instructions
description: Shared bootstrap instructions for Claude and Codex working in this repository.
---

# Repository Agent Bootstrap

## Project Overview

This repository is a multi-project System Analysis and Design showcase created for portfolio reviewers, developers, and AI agents. Each independent project demonstrates how business needs become approved requirements, system specifications, API contracts, data models, diagrams, database migrations, automated tests, and a working C#/.NET backend. The showcase reflects the perspective of a System Analyst with 7+ years of experience and a prior background as a .NET Developer; C#/.NET connects analysis and design artifacts to implementation in the author's primary engineering stack.

Work follows Spec-Driven Development (SDD): behavior is designed, reviewed, and approved in specifications before implementation begins. Specifications are the source of truth, and code and tests remain traceable to the requirements, contracts, and models that govern them. Each top-level project is an independent case study with its own specifications, architecture, and implementation details.

## Project Structure

```text
/
├── AGENTS.md              # Codex entry point
├── CLAUDE.md              # Claude entry point
├── GLOSSARY.md            # Canonical repository terminology
├── .claude/               # Claude-specific configuration and commands
├── .codex/                # Codex-specific configuration
├── .agents/               # Shared agents, skills, rules, workflows, templates, and knowledge
├── docs/                  # Repository-wide documentation and handoffs
├── tasks/
│   ├── todo.md            # Checkable plans grouped by active task
│   └── lessons.md         # Corrections and reusable lessons
└── <project>/             # Independent System Analysis and Design case study
    ├── REPOS.md           # Machine-readable manifest of Component Repositories
    ├── api/               # Machine-readable API contracts
    ├── db/                # Database migrations and database tests
    ├── diagram/           # System and architecture diagrams
    ├── doc/
    │   ├── api/           # Human-readable API specifications
    │   └── schema/        # Human-readable data schema specifications
    └── repository/        # Checkout Directory; child repositories are ignored by the Showcase Repository
        ├── .gitkeep
        └── <github-repository-name>/
            ├── .git/      # Independent Git history and remote
            └── ...
```

Use the `repository-bootstrap` skill to validate `REPOS.md` and materialize declared Component Repositories. Do not clone directly into a Checkout Directory or operate on a migration-pending Project.

For a named agent, resolve `.agents/team/agents.yaml` and load `.agents/rules/named-agent-workspaces.md` before delegation. Read-only assignments use the primary checkout; any assignment that changes files must use the agent's managed `.workspace/<agent>` clone through `agent-workspace`.

Each top-level project is self-contained. Before changing files, identify the active scope and, when it is project-specific, use that project's local specifications, templates, architecture, and conventions. Project-specific resources may refine shared defaults but must not weaken global rules.

## Workflow Orchestration

### Resource Discovery

1. Determine the active scope:
   - Use the project explicitly named by the user.
   - Otherwise, infer the project from referenced paths or the current working directory.
   - Use `repository-wide` for root files, `.agents/`, or cross-project work.
   - Ask the user when multiple project candidates remain.
2. Read `.agents/README.md` to discover available resources and their status.
3. Load every applicable rule, including all global rules.
4. Load project knowledge when the scope is a specific project.
5. Select the governing workflow and any applicable ready agent, skill, or template.
6. Treat resources marked `placeholder` as unavailable.

### Workflow Strategy

#### 1. Plan Mode Default

- Enter planning for any non-trivial task: three or more steps, a cross-layer change, or a change to behavior, API, data, or architecture.
- Ground the plan in the approved spec when one exists. When creating or changing a spec, use approved requirements and current evidence, then stop at the approval gate before implementation.
- Treat an existing spec as approved only when its frontmatter has `status: approved` with populated `approved_by` and `approved_at`; active-task approval must be persisted before implementation.
- Stop and re-plan when evidence, scope, or constraints invalidate the current direction.

#### 2. Subagent Strategy

- Use subagents only when the runtime supports them and the task contains independent research or focused execution streams.
- Give each subagent one bounded objective, the minimum required context, and an explicit expected output.
- The primary agent owns product decisions, integration, verification, and the final handoff.
- Until an agent role is ready, the primary agent performs its SDD phase directly and uses the role name only as an analytical perspective.

#### 3. Self-Improvement Loop

- Review `tasks/lessons.md` at the start of each task for lessons relevant to the active scope.
- After every user correction, record the mistake, root cause, and corrected behavior in `tasks/lessons.md`.
- Re-evaluate the affected work before continuing and correct every artifact influenced by the mistake.
- Distinguish reusable lessons from one-off task preferences before promoting guidance into `.agents/`.

#### 4. Skill First

- After resource discovery, select a ready skill that matches the task before inventing an ad hoc workflow.
- Read the selected `SKILL.md` completely and follow its instructions, required inputs, outputs, and completion criteria.
- Use the minimum set of skills that fully covers the task and state the execution order when multiple skills apply.
- Treat skills marked `placeholder` as unavailable and continue with the governing workflow and rules.

#### 5. Verification Before Done

- Completion requires evidence such as builds, tests, static analysis, contract comparison, logs, or diffs.
- Verify code and tests against the approved spec, not only against successful command execution.
- Report every skipped or failed verification and the exact result that remains uncertain.

#### 6. Demand Elegance — Balanced

- Prefer the simplest complete solution that satisfies the approved spec and existing architecture.
- Improve an approach that is fragile, duplicated, or inconsistent when the task scope justifies the change.
- Avoid speculative abstraction and large redesigns for small, isolated changes.

#### 7. Autonomous Bug Fixing

- For an explicit bug-fix task, reproduce the failure, trace the evidence, isolate the root cause, implement the fix, and prove the result.
- Resolve discoverable technical facts independently before requesting user input.
- Escalate only product decisions, conflicting instructions, missing access, destructive actions, or behavior-changing ambiguity.

### Task Management

#### 8. Plan First

- Load `.agents/rules/task-management.md` and resolve the task folder before planning: use `tasks/owner/` for work directly owned by the repository owner, or `tasks/<workspace_key>/` for a named-agent assignment resolved from `.agents/team/agents.yaml`.
- Write every non-trivial plan to the accountable owner's `todo.md` as ordered, checkable tasks before implementation begins.
- Include spec updates, implementation, tests, verification, and documentation when they are part of the scope.
- Keep the task owner's `todo.md` aligned with the approved approach as scope or evidence changes. Do not add new tasks to the legacy root `tasks/todo.md`.
- Let assignments already started in the legacy root file finish there. Do not migrate legacy entries until all unresolved items have evidence-based completion or owner-approved closure.

#### 9. Verify the Plan and Track Progress

- Confirm the active scope, governing spec when applicable, applicable rules, dependencies, task owner, and approval state before executing the task plan.
- Check in with the user before implementation when the plan or governing spec requires approval.
- Record task status and required timestamps in the owner's `todo.md`; for blocked work, record when it was blocked, why, what it is waiting on, and the next action.
- Mark an item complete only when its completion criterion and required verification are satisfied.

#### 10. Explain Changes and Document Results

- Provide concise progress updates at meaningful milestones for long-running work.
- Explain what changed, why it changed, and which approved requirement or spec governs the change.
- Move verified completed records to the task owner's `success-task.md`; move cancelled or superseded records to `archive.md` with a closure time and reason.
- End with a handoff covering changed files, verification results, remaining risks, and follow-up work.

#### 11. Capture Lessons

- After every user correction, update `tasks/lessons.md` before closing the task.
- Promote reusable project-specific lessons into project knowledge and repository-wide behavior into the relevant rule, workflow, agent, skill, or template.
- Register new resources in `.agents/README.md` and avoid duplicating the same lesson across files.

### Core Principles

#### 12. Simplicity First

- Make the smallest change that completely satisfies the approved requirement.
- Reuse existing project patterns and abstractions when they remain correct.
- Prefer code and specifications that another engineer can understand without reconstructing hidden reasoning.

#### 13. No Shortcuts

- Find the root cause before choosing a fix.
- Deliver complete implementation and verification for the agreed scope.
- Use placeholders, TODOs, skipped tests, or temporary workarounds only when explicitly approved and clearly documented.

#### 14. Minimal Impact

- Change only the files and behavior required by the active task.
- Preserve existing user changes and avoid unrelated refactoring, formatting, renaming, or dependency updates.
- Keep public contracts and architecture stable unless an approved spec explicitly changes them.

