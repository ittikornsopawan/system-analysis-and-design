---
name: Spec-Driven Development Workflow
description: Required workflow for designing or changing behavior, APIs, data models, architecture, or C# backend code from an approved specification.
---

# Spec-Driven Development

Spec-Driven Development (SDD) means every feature begins with a clear, approved spec before code is written. The approved spec is the source of truth for API behavior, data models, business rules, implementation, and tests. When behavior changes, update and approve the spec first, then bring code and tests into agreement.

## Role Sequence

The default sequence is:

`Product Owner → Business Analyst → System Analyst → Solution Architect → API Documenter → Backend Developer → Code Reviewer`

A phase may omit a role that has no relevant responsibility, but the handoff must state why it was omitted. Agent role files marked `placeholder` describe planned roles only and must not be treated as executable instructions.

Until a role file is ready, the primary agent performs that phase directly and uses the role name as an analytical perspective rather than an executable subagent.

The System Analyst is the central completeness gate for Specifications and traceability across the sequence. This authority may stop an incomplete handoff but does not transfer product, business, architecture, implementation, approval, or independent-review decisions from their owning roles.

Security Auditor is an optional specialist, not a mandatory phase. The Solution Architect or Code Reviewer invokes it when the scope affects authentication, authorization, cryptography, key management, tokens or sessions, payments or webhooks, sensitive personal data, consent or privacy, compliance, or a material trust boundary.

## Approval Evidence

- An existing spec is approved only when its frontmatter contains `status: approved` with `approved_by` and `approved_at`, or when the user explicitly approves it in the active task.
- Record active-task approval in the spec frontmatter before implementation begins.
- A draft, in-review, superseded, missing, or ambiguous approval state does not authorize implementation.

## 1. Discover

- Identify the active scope, requested outcome, and task boundary; identify the active project only for project-specific work.
- Read `.agents/README.md` and load applicable rules and project knowledge.
- Select ready resources only.

Complete when the project, scope, applicable rules, and source documents are explicitly known.

## 2. Inspect

- Read existing requirements, specs, API contracts, schemas, diagrams, code, tests, and local conventions relevant to the task.
- Record conflicts, missing information, and existing user changes that must be preserved.

Complete when every artifact that can constrain the requested behavior has been examined or identified as unavailable.

## 3. Clarify

- Separate discoverable facts from product or design decisions.
- Ask the user about ambiguity that changes behavior, data, APIs, architecture, priority, or acceptance outcomes.

Complete when no unresolved decision prevents an unambiguous spec.

## 4. Design

- Create or update the required specification artifacts.
- Set new or changed Markdown specifications to `status: draft` or `status: in-review` until approved.
- Make business rules, inputs, outputs, validation, errors, data impact, dependencies, acceptance criteria, and verification expectations explicit where applicable.
- Maintain traceability from requirements to the proposed system behavior.

Complete when the spec is internally consistent, testable, and detailed enough to implement without inventing behavior.

## 5. Approve

- Present every new or changed spec to the user for approval before implementation.
- Record requested revisions in the spec and repeat this phase until approved.
- After explicit approval, set the spec to `status: approved` and record `approved_by` and `approved_at`.
- If the user requests implementation from an unchanged spec with durable approval metadata, use that approval without asking again.

Complete only when the governing spec is approved.

## 6. Publish API Contract

- For an API change, use the API Documenter to publish the Approved API Specs into the Active Project's machine-readable OpenAPI 3.1 contract.
- Represent every approved path, operation, parameter, request, response, status code, business code, example, and security requirement in scope.
- Preserve unrelated contract content and return every behavioral conflict or omission to Design rather than inventing a contract.
- Parse the contract and run every available OpenAPI validator; report semantic validation as unverified when no validator is configured.
- Maintain traceability from each changed OpenAPI operation to its source Approved API Spec.

Complete when every approved API operation in scope is represented faithfully, JSON and available OpenAPI validation pass, and no unresolved contract conflict remains. Omit this phase for work that has no API impact and state why in the handoff.

## 7. Implement

- For a manifest-managed Project, implement the approved spec in the Component Repository declared by `<project>/REPOS.md` at `<project>/repository/<repo-name>/`.
- For a migration-pending Project, follow its project knowledge and do not relocate or create nested Git metadata outside an explicitly approved migration task.
- For an API change, implement against both the Approved API Specs and the published OpenAPI contract.
- Add or update automated tests that trace to the acceptance criteria and business rules.
- Keep implementation changes within the approved scope.

Complete when code and tests account for every applicable requirement in the approved spec.

## 8. Verify

- Build the affected solution and run relevant tests or static analysis.
- Compare implementation behavior, the published OpenAPI contract, public contracts, data access, and tests against the approved spec.
- Run the optional Security Auditor review when the security trigger applies.
- Send spec gaps back to Design; send implementation gaps back to Implement.

Complete when every spec requirement is verified or explicitly reported as unverified with a reason.

## 9. Handoff

- Summarize changed specs, OpenAPI operations, and code.
- Link the implementation to its governing spec and acceptance criteria.
- Report verification commands and results, applicable Security Auditor findings, remaining risks, and follow-up work.

Complete when another person or agent can understand the outcome and continue without reconstructing the task history.
