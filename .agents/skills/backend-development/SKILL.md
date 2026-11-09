---
name: backend-development
description: Implement approved backend behavior in any programming language, fix implementation bugs, or perform behavior-preserving refactors using the project's actual stack, architecture and test tools. Read the spec first, clarify gaps with four-part questions, and use test-first changes with real database or API evidence for the guarantees affected. Use for backend implementation work; route specification, schema and API-contract changes through their design skills before coding.
---

# Backend development

Turn an understood, approved specification into a small verified code change. Discover the project's language and conventions rather than prescribing a framework, library or universal layer layout.

Load `.agents/README.md`, applicable rules, the SDD workflow and the active project's knowledge. Use only ready roles/resources matching the task. The existing backend-developer role specializes in .NET; this skill also supports other backend stacks without assigning them that role's language-specific assumptions.

## Before implementation

1. **Locate the writable boundary.** Identify the active project, implementation repository and task scope. For a manifest-managed component, read its `REPOS.md` and component-repository rules; use repository-bootstrap if setup or baseline verification is needed. Preserve existing checkouts and keep component source/commits separate from Showcase specs and manifests. Named-agent work follows agent-workspace; ordinary work preserves unrelated edits too.
2. **Read the spec before writing code.** Follow [spec readiness and clarification](references/spec-and-clarification.md), including its question-language contract and four-part format. Read the full relevant rules, request/response examples, SQL/sequence and acceptance criteria, not just an endpoint title. Require durable approval and the published API contract when applicable. Resolve material ambiguity before implementation or implementation tests.
3. **Inspect the actual stack.** Read project manifests, lock files, runtime/language settings, architecture, neighboring code, test configuration and CI/scripts. Discover the supported build/test commands and data-access patterns. Preserve versions, dependencies, public contracts and dependency direction unless the approved task changes them. For e-commerce/.NET work, read the conditional [project reference](references/e-commerce-dotnet.md); it does not govern other stacks.
4. **Make the implementation and evidence plan.** Classify the work as feature, bug fix or refactor. Map each affected acceptance criterion to its code boundary, expected outcomes and tests. Agree observable test seams from the approved spec/test plan; clarify any seams that are still undecided through the four-part question format. Identify actual DB/API test prerequisites before starting. Persist the scoped plan in `tasks/todo.md`.

## Execute one verified slice at a time

- **Feature:** derive an observable example from the approved behavior, write one relevant test that fails for the missing behavior, implement the smallest slice and rerun it. Continue with the next criterion rather than writing every test and every implementation as separate bulk phases.
- **Bug fix:** reproduce the approved-behavior failure, capture why the test is red, isolate the cause, implement the fix and prove the reproducer turns green. A compile failure or unavailable dependency does not prove the bug. Inspect related paths affected by that same cause.
- **Refactor:** establish the existing behavior and relevant passing baseline first. Make the requested structural change separately from feature/fix cycles, then verify the same observables. Return any intended behavior or architecture change to approval; preserve unrelated formatting and dependencies.

Use the project's public contracts, conventions and smallest complete design. Add only the validators, handlers, business operations, mappings or adapters the use case needs. Reuse model invariants and approved ports; keep business decisions distinct from transport and storage mechanics. Do not create a wrapper, service or interface merely to fill a template.

For persistence and external effects, derive transaction completion, retained writes, ordering, idempotency and failure outcomes from each approved branch. A failure Result or HTTP error can still require a committed audit/security effect. Bind parameters rather than interpolating inputs, propagate cancellation/timeouts through actual I/O, dispose resources through the stack's lifetime model, and check conditional-write/affected-row outcomes. Test required constraints, locks and race behavior at their real boundary.

## Verify and hand off

Follow [verification and worked examples](references/verification.md). Unit tests/fakes can prove business decisions or orchestration; changed SQL, transactions, locking and concurrency require appropriate real database evidence, and changed HTTP/authentication behavior requires the actual relevant framework pipeline. Choose tests by the claim being made. Inspect configured build/test/static checks and compare resulting behavior with the governing spec and published contract.

When prerequisites or required checks are unavailable, report the exact gap and keep its verification criterion open; a fake is not a substitute for a claimed database or HTTP guarantee. Continue independent authorized work where possible. Resolve spec/contract/schema gaps through their design/approval workflows rather than guessing or editing a check to accept incorrect behavior. Use the SDD security-review trigger for relevant changes; distinguish performed reviews from requested or unavailable ones.

Report the governing spec and approval, requirement-to-code-to-test mapping, changed files with individual summaries, actual commands/results, contract/data/security impacts and remaining uncertainty. Implementation completion requires the accepted behavior and required evidence; report incomplete work explicitly. Commit/push/PR publication follows commit-and-pr only under its delivery authorization, in the correct repository. A Showcase manifest revision advances only after verified component delivery under the component rules.

## Learn from every bug, conflict and issue

Every actual bug, conflict or issue encountered while using this workflow requires both a correction and a preventive skill improvement in the same task. This includes a pre-existing bug assigned for repair, implementation/regression defects, Git merge conflicts, spec conflicts, tooling/environment issues and owner/reviewer corrections; the trigger is not limited to mistakes newly introduced by the agent.

Track the underlying issue once per occurrence and link its reproducer, repeated failures and resolution evidence to that record. A deliberately red TDD test or expected business rejection is evidence, not a separate issue by itself; reproducing a real bug still carries that bug's skill-improvement requirement. Even when existing guidance covers the cause, improve the relevant trigger, example, verification check or helper rather than ending with a code-only fix or appending duplicate rules.

Capture the root cause, correct the affected work, update the governing skill or its applicable reference/example/helper and recheck the original scenario. Record the exact skill path/change and evidence in `tasks/lessons.md` and update the plan/handoff. Keep the improvement at its authoritative source instead of duplicating another skill's rules here.

Diagnose tool-startup failures separately from validation findings; document equivalent-check coverage and remaining gaps without claiming an unavailable tool passed. If an approval-review service cannot complete a review, treat the protected action as unexecuted, report the review failure and resume through the required approval gate when it is available; do not perform the blocked action by another route. Continue only unaffected authorized work while that gate is unavailable.

Preserve approval and delivery boundaries. If a required skill edit lies outside the assigned repository/scope, prepare the concrete change and use the four-part clarification and question-language contract to obtain the needed scope decision. Keep that improvement pending rather than editing outside authorization or claiming the issue fully resolved.

## Complete when

- The understood governing spec and required contract are approved/current; no unresolved decision was implemented by assumption.
- Each affected criterion is represented in the scoped code and meaningful tests; test-first/reproduction or refactor-baseline evidence is recorded for the applicable mode.
- Required real DB/API evidence and configured checks pass; every blocked/skipped item remains explicitly unverified rather than being claimed complete.
- Changed paths, transaction/error semantics and public behavior match the approved scope; unrelated changes are preserved and excluded.
- Every actual bug, conflict or issue has a verified correction, preventive skill/resource improvement and lesson record. Deliberate red evidence is linked to its underlying issue; blocked/out-of-scope improvements remain pending and the task is not reported fully complete. The handoff supports subsequent code review.
