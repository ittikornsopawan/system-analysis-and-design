---
name: Markdown Frontmatter Rules
description: Frontmatter contract for authored Markdown files and the trigger for applying it when Markdown is created or modified.
---

# Markdown Frontmatter Rules

## Scope

Apply this rule to every human-authored `*.md` file in the repository, including existing and future files. Generated, third-party, and vendor Markdown files are exempt.

## Contract

Every in-scope Markdown file starts with valid YAML frontmatter containing at least:

```yaml
---
name: Human-readable document name
description: The document's purpose and when an agent should read or use it.
---
```

- `name` must identify the document and agree with its content.
- `description` must state both the document's purpose and its loading or usage trigger.
- Additional frontmatter fields may be added when a later resource contract requires them.

## Specification Approval Metadata

Every Markdown specification also contains:

```yaml
status: draft
approved_by: null
approved_at: null
```

- `status` must be one of `draft`, `in-review`, `approved`, or `superseded`.
- Set `status: approved` only after explicit user approval.
- When approved, set `approved_by` to the approver and `approved_at` to an ISO-8601 timestamp.
- Keep `approved_by` and `approved_at` as `null` while the spec is not approved.
- A user approval in the active task is valid evidence, but record it in the spec before implementation begins.

## Change Boundary

- Make every Markdown file created or modified by the current task comply with this contract.
- Do not retrofit unrelated files while completing another task.
- Treat repository-wide remediation of existing Markdown as a separate migration task.
