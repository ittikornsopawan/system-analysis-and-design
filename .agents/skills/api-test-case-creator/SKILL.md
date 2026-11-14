---
name: api-test-case-creator
description: Create or update documented API test cases from API specifications, with rule traceability, reproducible scenarios and expected HTTP, response and data outcomes. Use for API test-case documents and coverage/gap analysis; executable tests and spec checkers belong to their own workflows.
---

# API Test-Case Creator

Turn an inspected API spec into test cases that QA can execute and developers can later automate. The deliverable is a test design document; creating it or checking its coverage supplies no API execution evidence.

Load `.agents/README.md`, applicable rules and the active project's knowledge when available. Keep this skill scoped to documented cases. Use the project's ready design skill for changes to API behavior/schema and backend-development for separately requested executable implementation/tests.

## Establish the source and output

1. Identify the requested endpoint set and output conventions. Preserve requested paths/formats and existing case IDs. Otherwise use Markdown `test-cases.md` beside each endpoint's `spec.md`, based on [the template](assets/test-cases.md.tmpl). For multiple endpoints, retain per-endpoint cases and explicitly link any cross-endpoint workflow.
2. Read the entire relevant spec: headers, inputs, validation order, permissions, business rules, response fields/examples, SQL/data effects, transaction paths and acceptance criteria. Inspect linked requirements, schema, sequence and published API contract when present. Record the source paths, sections and revision/content fingerprint; explicitly identify relevant uncommitted sources.
3. Establish source approval from its metadata and recorded owner decisions. Approved means `status: approved` with populated `approved_by` and `approved_at` under repository rules. Draft/unapproved specs can support provisional test design, visibly labeled as such; generating cases does not approve behavior. A contradiction between rules, examples, SQL, sequence or contract is a gap to resolve, rather than a choice the author may silently make.
4. Start a coverage matrix from an understood rule and write one representative detailed case. Then expand the inventory and cases until every scoped obligation and material decision branch is accounted for; keep uncovered rows explicit while drafting rather than waiting for a fully planned suite before producing an artifact. Cite source headings/anchors; assign clearly labeled local obligation IDs when the spec has none. A list of HTTP status codes alone is insufficient coverage.

Proceed with the understood portions while material uncertainties remain isolated. Ask about missing specs and unresolved expected outcomes before writing dependent assertions; use the clarification contract below. Track non-trivial work in the accountable task owner's `todo.md` as resolved by `.agents/rules/task-management.md`.

## Derive and write the cases

Read [case design and worked example](references/case-design.md) before selecting scenarios or writing expected results. It defines reachable negative cases, boundary/data/concurrency checks and a complete self-contained example.

- Cover each specified success/error branch, input partition, boundary and affected business/data rule with independently checkable cases. Apply auth/authz, batch, paging, time, concurrency and failure categories only where supported by the endpoint. Explain genuine exclusions and unresolved rules in the matrix; do not manufacture behavior to fill a generic checklist.
- Give every case a stable ID, source reference, purpose, design readiness, isolated preconditions/fixtures, concrete request/input, numbered steps and exact expected observations. Include the relevant HTTP status, bizCode presence/value, response fields and durable/external effects from the spec. Identify the evidence needed for each assertion, including effects HTTP alone cannot expose.
- Keep known expectations separate from blocked decisions. Each runnable case has an unambiguous expected outcome; a blocked case identifies the precise missing decision without turning a suggested fix into its expected result.
- Use safe synthetic data and state reset/cleanup instructions. Document controlled clock, separate connections/actors or failure-injection prerequisites when needed; designing these prerequisites does not authorize live writes, privileged access, installed dependencies or runtime execution.
- New cases start with execution status `Not run`, empty actual results and no pass/fail evidence. When updating existing cases, preserve IDs and historical evidence with its original source revision; substantive changes require a new Not run revision and a link to the superseded evidence.

## Clarify material gaps

Use `AskUserQuestion` when available, otherwise the runtime's structured question tool. Write the topic/title in English and the body/choice explanations in Thai, keeping technical terms and identifiers in English. For a single question field, put the English topic first. Include a recommended resolution and all four explanations:

1. **เกิดอะไรขึ้น:** cite the conflicting/missing source and a concrete scenario.
2. **ส่งผลอย่างไร:** explain the consequences for expected HTTP/body/data outcomes, callers or test validity.
3. **แก้อย่างไร:** propose a concrete spec resolution with meaningful alternatives; distinguish the proposal from an approved rule.
4. **ในอนาคตจะส่งผลอย่างไรหลังแก้:** explain future compatibility, maintenance, data or testing effects.

Wait for an answer before resolving dependent expectations. Persist decisions through the governing design/approval workflow before promoting a provisional suite to an approved-source baseline. A question submission or preselected option is not approval.

## Verify and hand off

Reconcile every scoped obligation with its matrix row and detailed case, then read each case back against its source and fixture. Check that the request reaches its intended branch, expected values follow the rule, IDs/links resolve and all necessary observations/prerequisites are documented. Preserve each check's output and exit status; distinguish unavailable tooling from findings.

Report changed files individually, source/approval baseline, designed coverage, unresolved gaps and verification performed. Separate document checks from runtime execution. Keep out-of-scope endpoints, spec edits, implementation and existing execution history intact. Commit/PR delivery follows commit-and-pr under existing delivery authorization.

## Learn from every bug, conflict and issue

Every actual bug, conflict or issue discovered in this workflow, including assigned existing problems, spec contradictions, authoring defects, tool failures and owner/reviewer corrections, requires correction and a preventive improvement to the governing skill/reference/template/helper. Capture evidence and root cause, strengthen the relevant existing instruction rather than duplicating it, replay the original scenario and record the changed resource and result in `tasks/lessons.md` and the task plan/handoff.

Expected negative API outcomes and deliberate invalid examples are case evidence; link repeated observations to the underlying issue instead of creating an incident per run. Keep fixes within current scope and approval boundaries. For a required source/skill change outside authorization, prepare the concrete correction, ask the four-part scope question and keep the affected case/improvement pending. Continue only independent authorized work; report blocked completion honestly.

## Complete when

- The requested document set exists, its source revision and approval/provisional status are visible, and existing case identity/history is preserved.
- Every scoped obligation maps to detailed cases or an explicitly justified exclusion/gap; blocked decisions are distinguishable from established expectations.
- Each ready case has reproducible fixtures, request, steps, source-derived expected observations and the prerequisites needed to verify them.
- Document verification and any remaining blockers are recorded; new/revised cases remain Not run until actual execution provides evidence.
- Actual issues have a verified correction and preventive resource improvement, or remain explicitly pending outside scope. No runtime pass is inferred from design completeness.
