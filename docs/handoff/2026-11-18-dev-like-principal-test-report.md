---
name: dev-like-principal Skill Test Report
description: Structure check and three-case evaluation (feature development, architecture design, code review) of the dev-like-principal skill, with and without the skill, plus sample outputs. Read when reviewing, approving or improving the skill.
---

# Test report: `dev-like-principal` skill

- Date: 2026-11-18
- Skill: `.agents/skills/dev-like-principal/`
- Method: skill-creator evaluation loop, iteration 1. Each case ran once with the skill and once without (baseline), as independent subagents on the same model. Outputs were graded against written assertions (`evals/<case>/graders/`).

## 1. Structure and instruction checks

| Check | Result |
| --- | --- |
| skill-creator `quick_validate` (run with PyYAML via `uv run --with pyyaml`) | `Skill is valid!` |
| Every `references/` and `assets/` path named in `SKILL.md` exists | 10 of 10 found (after the code-quality update) |
| Frontmatter `name` + `description` on every reference (`.agents/rules/markdown.md`) | 8 of 8 |
| `SKILL.md` size | 101 lines (guideline: under 500) |
| Registered in `.agents/README.md` | Yes, status `ready` |
| Brief coverage | All 12 responsibilities, coding philosophy, working principles, decision requirements, expected behaviour and the 9 deliverables map to a file (table below) |

| Deliverable in the brief | Where |
| --- | --- |
| Skill definition and metadata | `SKILL.md` frontmatter |
| Core instructions, working principles, expected behaviour | `SKILL.md` |
| Decision-making framework, technology selection | `references/decision-framework.md`, `assets/adr.md.tmpl` |
| Architecture review guidelines (responsibilities 1–3, 5, 7–12) | `references/architecture-review.md` |
| Coding guidelines, C#/.NET practice | `references/coding-guidelines.md` |
| Technical review checklist | `references/review-checklist.md` |
| Practical C#/.NET examples | `references/examples.md`, `references/coding-guidelines.md` |
| Anti-patterns | `references/anti-patterns.md` |
| Verification guidelines | `references/verification.md` |

## 2. Evaluation results

| Case | With skill | Without skill |
| --- | --- | --- |
| Feature development: `feature-money-and-coupon` | 7 / 7 | 6 / 7 |
| Architecture design: `architecture-multi-warehouse-stock` | 7 / 7 | 7 / 7 |
| Code review: `review-order-fulfilment-pr` | 8 / 8 | 6 / 8 |
| **Total** | **22 / 22 (100%)** | **19 / 22 (87%)** |

Cost: with the skill, runs took about +67 s and +16k tokens on average. That time went into verification the skill asks for: compiled tests and mutation checks in the feature case, and a PostgreSQL concurrency test in the architecture case.

### What the baseline missed

- **Feature:** no tests for coupon expiry or max uses. Its own note admits the concurrency guarantee is untested.
- **Review:** `review.md` never says what was not verified (that appears only in the agent's chat reply), and most "should fix" rows give no failure scenario.

### What only the skill run did

- **Feature:** labelled facts, assumptions and open questions, each question with a default. It compiled 12 tests in a throwaway harness and broke each rule on purpose to show the matching test fails. It wrote PostgreSQL concurrency tests for CI and split its report into Ran and Not run.
- **Architecture:** measured the claim instead of asserting it. 50 concurrent buyers making 2,000 attempts on 10 units: the read-then-write approach created 827 reservations, the conditional `UPDATE` exactly 10. It also gave a rollback for each rollout phase and labelled assumptions A1–A5.
- **Review:** used the review-checklist format: Blocker, Major, Minor and Nit, with a Scenario and a Fix for each finding. It also listed what is good and should stay, questions with defaults (including whether an approved API spec exists, per this repo's SDD), and a "not checked" section.

### Analyst notes

- The architecture assertions don't separate the two configurations: the base model already rejects Redis as the source of truth and Kafka at this scale. A harder case should be added (see section 5).
- Only one run per configuration, so there is no variance estimate.
- A usage-limit interruption stopped every run once. They were resumed, but timings cover only the resumed part, so both time and token figures are understated.

## 3. Acceptance criteria

| Criterion | Evidence |
| --- | --- |
| Usable for real development work | The feature case produced working C#, tests and a reviewer note; its tests compiled and passed in a harness |
| Analyses architecture and trade-offs | The architecture case gave an options table, a decision, a revisit trigger, a phased rollout with rollback, and measured spike evidence |
| Reviews beyond syntax and style | The review case found 5 blockers (security, authorization, migration compatibility, swallowed errors, a transaction holding an external call) ranked above the style items |
| Identifies risks, constraints and long-term impact | All three outputs have risk, open-question and consequence sections |
| Does not over-engineer | The feature run rejected Redis and queues for coupons; the architecture run kept a modular monolith with an outbox; the review said not to build an outbox in this PR |
| Practical examples and checklists | `references/examples.md`, `references/review-checklist.md` |
| Completeness and consistency of the instructions | Section 1 |

## 4. Sample outputs (excerpts from the with-skill runs)

**Feature (`REVIEWER-NOTE.md`):**

```text
- Fact: turning `total` from a number into an object is a breaking change. Old apps that parse
  `total` as a number will fail ...
UPDATE coupons SET used_count = used_count + 1
WHERE id = @id AND used_count < max_uses AND expires_at > @now;   -- 1 row = redeemed, 0 = refused
- Rejected: a Redis counter or a queue. Each adds infrastructure and a second source of truth ...
- Not run: ... So the concurrency guarantee and the HTTP 409/422 mapping are not verified yet.
```

**Architecture (`design.md`):**

```text
1. PostgreSQL ยังเป็น source of truth ของ stock. เพิ่ม module `Inventory` ใน monolith เดิม ...
2. ยังไม่ใช้ Kafka. ระบบมี service เดียว (monolith) ...
Revisit เมื่อ: peak เกิน ~500 reservation/s บน SKU เดียว, มีทีมที่สองเป็นเจ้าของ ...
```

**Review (`review.md`):**

```text
### B1. [Blocker] FulfilmentController.cs:29 มี SQL injection จากต่อ string ด้วย `id`
### B3. [Blocker] 0042_rename_tracking.sql:4 rename คอลัมน์ทับที่เดิม ทำให้ pod เก่าและ carrier-sync พัง
ถ้าจำเป็นต้อง rename จริง: ทำเป็น PR แยก แบบ expand → migrate → contract
```

The full outputs, grading files, benchmark and the static review page are in the session scratchpad. They are temporary and are not committed.

## 5. Known gaps and follow-ups

- The eval `prompt.md` and `graders/*.md` files use the `claude plugin eval` frontmatter (`tags`/`type`) instead of `name`/`description`. That loader rejects unknown keys, so these tool-format files cannot follow the Markdown frontmatter rule. The owner should confirm the exemption.
- Triggering (description optimisation with `run_loop`) was not run.
- Add a harder architecture case that separates the two configurations, e.g. a request where the right answer is a breaking API change with a deprecation plan, or where splitting a service *is* justified.
- Iteration 2 is pending owner feedback on the outputs.

## 6. Update: code quality standards and the code gate (iterations 2–3)

The owner added mandatory code quality standards:

- function reuse through a Function Book
- formatting
- short, single-purpose functions
- meaningful comments
- class and domain separation

The owner also required every code-writing skill to pass through this skill first.

### What changed

| Change | Files |
| --- | --- |
| Standards, the steps before coding, and the quality check before delivery | `.agents/skills/dev-like-principal/references/code-quality-standards.md` |
| Function Book template | `.agents/skills/dev-like-principal/assets/function-book.md.tmpl` |
| E-commerce Function Book, seeded from component revision `648226c` (about 50 shared functions) | `e-commerce/doc/function-book.md` |
| A "Writing code" gate section, a read-table row, and a done criterion | `.agents/skills/dev-like-principal/SKILL.md` |
| Checks for Function Book use and the quality standards | `.agents/skills/dev-like-principal/references/review-checklist.md` |
| A code gate before the first line of code | backend-development, data-modeling, api-contract-design and diagram-creator skills |
| The same requirement for all tasks | `.agents/rules/global.md` |
| Role hooks | `.agents/agents/backend-developer.md`, `.agents/agents/code-reviewer.md` |
| Knowledge pointers | `.agents/knowledge/projects/e-commerce.md` |
| Registry trigger | `.agents/README.md` |

**Finding while seeding the Function Book:** the e-commerce backend has two email rules that disagree. `EmailAddressFormat.IsValid`, used by the validators, and `EmailAddress.Create`, which is stricter (`MailAddress` parse, ≤ 254 characters, must contain `.`). This change records the divergence in the Function Book and does not fix it, because the fix is a behaviour change the owner must decide.

### Eval `code-gate-newsletter-subscription`

The task asks a run to implement an approved spec in a small codebase that already has a Function Book and shared helpers. Each run used the backend-development skill, so the eval also checks that the gate is reached through another skill.

| Run | Skill | Score | Notes |
| --- | --- | --- | --- |
| Iteration 2, old_skill | backend-development at `HEAD`, without the gate | 5 / 8 | Validation inline in a 61-line method; no quality check in the handoff |
| Iteration 2, with_skill | backend-development with the gate | 7 / 8 | Separate `Validate`, quality check present, but a 50-line `Handle()` reported as "Functions: Pass" without a count |
| Iteration 3, with_skill | after tightening the standard | **8 / 8** | Largest method 21 lines, measured. The run split a 34-line handler itself. Every quality-check row names its evidence |

**Skill fix between iterations 2 and 3.** `code-quality-standards.md` now:

- sets the length rule: aim for 20 lines or fewer; over 30 lines, split or justify
- requires measuring line counts, with no exemption for handlers
- requires every "pass" to name its evidence

The lesson is recorded in `tasks/lessons.md`.

**Caveats.**

- One run per configuration.
- The old_skill run built a temporary test project from the local NuGet cache and ran its 10 tests. The gated runs did not compile or run their tests. They reported this honestly, but runtime verification was stronger in the baseline for this case.
- Method length was measured with a brace-to-brace count script, not a C# parser.
