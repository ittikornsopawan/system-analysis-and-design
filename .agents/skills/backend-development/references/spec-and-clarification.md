---
name: Backend Specification Readiness and Clarification
description: Spec-first readiness gates and the four-part question format for backend work in any stack. Read before writing implementation or tests and whenever the intended behavior is unclear.
---

# Read and understand the governing spec

Locate the authoritative artifact before coding. Inspect the full applicable rules, input/output definitions, success/error examples, acceptance criteria, data effects and linked contracts/models. Search the repository for discoverable facts before asking the owner to supply them.

Approval requires `status: approved` with populated `approved_by` and `approved_at`. If the owner approves an identified spec in the active task, persist the evidence before implementation. A draft guide, reviewed code sample or passing legacy test is not approval of a new behavior. With multiple questions open, bind an answer only to the item it actually names.

For an API change, inspect the published machine-readable contract and trace the requested operations back to their approved specs. HTTP APIs use the project's OpenAPI contract; non-HTTP work uses its applicable interface/message contract without inventing an OpenAPI dependency. Missing paths or contradictory status/body/security definitions must be resolved through contract publication/design before implementation. Spec or schema changes use the applicable ready specialist skill and approval workflow first.

## Readiness record

Before the first implementation/test edit, be able to state:

- The exact requested behavior and approval evidence, including defaults, null/omitted inputs, permissions, outcomes and examples relevant to the change.
- The scope of the code change and the current implementation gaps. Clear code/spec drift is an implementation task; contradictory requirements or undecided behavior need clarification.
- For each branch, HTTP/result outcome, required durable effects, transaction outcome, conditional-write result and any external effects. Do not infer rollback from an error response alone.
- The observed test seams, planned examples/expected values and what each proposed test boundary proves or leaves unproven. Use already approved seams; confirm only those not yet agreed.
- Any missing contract, schema, architecture or test-environment prerequisite preventing the promised behavior/evidence.

## Ask before implementing unclear behavior

When the spec is missing, unapproved, ambiguous or internally inconsistent, or its intended effect is not understood, stop dependent implementation and ask. Continue only independent authorized inspection/planning while waiting. Small implementation choices inside clear approved boundaries remain the developer's responsibility.

Use `AskUserQuestion` when that tool exists. Otherwise use the runtime's structured question tool, such as `request_user_input_async`. If no question UI is available, present the same structure in the conversation and wait. Submitting an asynchronous question or showing a preselected option does not supply an answer.

### Question language

- Write the question topic/title in English.
- Write the question body, the four explanations and answer-choice explanations in Thai. Keep technical terms, API/type names, identifiers, commands and status codes in English; preserve their exact spelling where they identify a contract or code element.
- If the tool exposes one combined question field, put the English topic first and the Thai body below it. Use this language contract for every question, including spec, scope and issue-resolution questions.

Ask every independent material question that can already be answered; defer questions whose prerequisites are unsettled. Each question must include all four parts and a recommended resolution:

1. **What happened / what is unclear:** cite the relevant rule, example or observed conflict and give a concrete scenario. Separate evidence from the missing decision.
2. **Impact:** explain how the uncertainty changes behavior, callers, data integrity, security, tests or compatibility.
3. **Recommended fix:** propose a concrete resolution and meaningful alternatives when needed, identifying which spec/contract/code areas would change. Phrase confirmation so yes accepts that recommendation.
4. **Future consequences:** explain maintenance, compatibility, migration, operational or testing implications after that fix. State uncertainty rather than pretending an unproven outcome is certain.

### Self-contained example

The following is an illustrative ambiguity, not a production requirement:

> **Retain audit records before HTTP 401?**
>
> 1. **เกิดอะไรขึ้น:** `Rule A` กำหนดให้เก็บ `audit record` ของทุก rejected attempt แต่ส่วน `transaction` กำหนดให้ `rollback` ทุก error outcome จึงยังไม่ชัดว่าเมื่อ credentials ไม่ถูกต้อง ต้องเก็บหรือลบ `audit record`
> 2. **ส่งผลอย่างไร:** แต่ละทางเลือกทำให้ข้อมูลใน `database`, `security history`, `throttling` และผลของ `rollback tests` ต่างกัน หากเลือกเองอาจทำให้ implementation ไม่ตรงกับ spec
> 3. **แก้อย่างไร:** แนะนำให้ระบุ branch นี้ใน spec ว่าต้อง `commit audit record` ก่อนตอบ `HTTP 401` แล้วปรับ `sequence`, contract examples และ tests ให้สอดคล้องกัน ยืนยันตามข้อเสนอนี้ใช่ไหม หรือเลือก `rollback` ทั้งหมดและแก้ข้อกำหนดการเก็บ `audit record` ให้ตรงกัน
> 4. **ในอนาคตจะส่งผลอย่างไรหลังแก้:** `audit record` จะยังอยู่เพื่อรองรับ `audit` และ `throttling` จึงต้องกำหนด `retention` และ counting rules ให้ชัด ส่วน `transaction tests` จะช่วยป้องกันไม่ให้ refactor ในอนาคตลบข้อมูลที่ต้องเก็บโดยไม่ตั้งใจ
>
> **ตัวเลือก:** “ยืนยันให้ commit audit ก่อนตอบ HTTP 401 (แนะนำ)” / “rollback ทั้งหมดและแก้ Rule A”

After an answer, record the exact decision against the affected item, update/approve the governing artifacts as required, and revise the test plan. Resume dependent code only once the behavior and required approvals are clear. This gate does not authorize redesigning unrelated endpoints or adding business rules absent from the approved scope.
