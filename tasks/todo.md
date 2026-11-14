---
name: Task Plan
description: Shared checklist for planning and tracking non-trivial tasks without overwriting work belonging to another project or task.
---

# Task Plan

Use one section per task, named `<scope>: <task-name>`. Preserve other task sections and mark an item complete only after its completion criterion is satisfied.

## repository-wide: Create the API test-case creator skill

Status: Skill, verification and publication package complete. The owner selected documented test cases derived from API specs, rather than document checkers or executable API tests. `api-test-case-creator` provides rule traceability, reproducible inputs/steps and explicit HTTP/body/data expectations. Preserve English question topics, Thai question bodies with English technical terms, the four-part clarification format and learning after every actual bug, conflict or issue. PR89 is merged; this task starts from current origin/main on a separate branch. Actual integration and PR state are reported from Git/GitHub in the delivery handoff.

1. [x] Inspect the registry, applicable rules, lessons, existing API/testing skills and owner-selected scope; establish a clean task branch.
2. [x] Author the skill, focused case-design reference and reusable Markdown template; register the skill as ready without changing the broader placeholder test-design skill.
3. [x] Exercise the skill with isolated valid/ambiguous spec fixtures; verify source-to-case coverage, exact expected outcomes, unresolved decisions and execution-status honesty. Correct observed gaps and record preventive improvements.
4. [x] Verify metadata, local references and scoped diff; prepare the commit/PR package with per-file summaries under standing skill-delivery authorization. Record actual integration SHA, publication and remote PR state from Git/GitHub in the delivery handoff.

Design choices: Use project conventions when supplied; otherwise place `test-cases.md` beside the endpoint's `spec.md`. Default to Markdown with a source baseline, coverage matrix, detailed cases and open gaps. Draft specs permit provisional design only; unresolved outcomes remain blocked. Generated cases start Not run, and document verification never establishes API runtime correctness. No application implementation, spec behavior, schema, dependency or live API operation is authorized by this task.

Verification: Five Markdown frontmatters passed Ruby YAML parsing; naming, local references, ready registration, scaffold/whitespace checks and the six-file scoped preflight passed. Existing task/lesson content was preserved byte-for-byte. PyYAML is unavailable, so the original Python skill validator was not claimed run. No application or live DB/API tests were run.

Behavioral evidence: The first independent evaluation created no artifacts after planning and supports no behavioral conclusion. The inventory step was corrected to write a representative case before expanding the suite. Its bounded replay produced six detailed cases and a four-part question in two tool calls: explicit partial coverage, unchanged raw source/history, stable TC-RES-003 identity, preserved historical v1 Pass, revised v2 Not run, exact success/rejection/rollback outcomes and blocked R6 durable effects. A separate parent replay produced six cases and verified the same core guarantees against R1–R6. Synthetic approval and the unresolved fixture question are not production decisions or execution evidence. Temporary fixtures/artifacts are excluded from delivery.

## repository-wide: Refine backend questions and issue learning

Status: Guidance, verification and publication package complete. Ittikorn requested English question topics, Thai question bodies with English technical terms, and a skill improvement after every actual bug, conflict or issue. PR87 is merged; this is a separate follow-up. Preserve the four-part question structure and approved implementation/delivery boundaries. Actual integration SHA, PR state and final file coverage are reported from Git/GitHub.

1. [x] Inspect the current skill/reference, lessons and PR state; start a clean branch from current origin/main. The first branch attempt was not executed because approval review could not run due to a usage limit; retry through the same approval gate succeeded after the user asked to continue.
2. [x] Define the question language contract and update its complete example; explicitly include existing bugs, conflicts and issues in the learning trigger and reconcile older execution-only wording.
3. [x] Verify examples, trigger scenarios, metadata, links and scoped diff; prepare the per-file PR package and required main-integration/check commands. Report actual integration and publication from Git/GitHub.

Verification: Five Markdown frontmatters and local references passed; the complete example has an English topic, four Thai explanations, Thai choices and preserved English technical terms. The corrected semantic checker accepts both valid Markdown emphasis variants and rejects four controls (missing explanation, Thai topic, English body and English choices). Independent evaluation generated three compliant questions and replayed five cases covering an existing bug, real merge conflict, expected rejection, deliberate TDD red and read-only scope. Existing sandbox reports/fixtures were preserved; application tests were not rerun because no application code changed. The new policy supersedes the earlier exemption for assigned known bugs without treating every red run as a separate incident.

Issue improvements: Approval review initially could not complete due to a usage limit; the protected branch action remained unexecuted until a successful retry through the same gate. A brittle Markdown checker and masked aggregate exit status were corrected; the verification reference and lesson now preserve per-check status and validate semantic question content, including choice labels. Scoped preflight reports five task files and no blockers. PyYAML remains unavailable, so Ruby YAML parsing and direct metadata/language/reference checks are used without claiming the original validator ran. No production backend, API contract, schema or dependency changed.

## repository-wide: Design the backend development skill

Status: Skill, bundled references and behavioral evaluation complete; publication package prepared. All five interview decisions confirmed. The owner approved backend development in any language, feature/bug/refactor workflows, spec-first four-part clarification, real DB/HTTP evidence for relevant guarantees, canonical name `backend-development`, and test-first business changes/bug fixes. Authoring is now authorized in an isolated managed worktree. No component implementation or architecture change is authorized by this skill-design discussion. Preserve the existing code-review scope correction in lessons and unrelated cache files.

1. [x] Load repository rules, SDD workflow, backend-developer role, component manifest, project knowledge and relevant lessons; inspect the current guide and approval/OpenAPI state.
2. [x] Use a read-only fresh-context investigation to verify the pinned component and inspect actual architecture, libraries, transaction semantics and test coverage without changing either repository.
3. [x] Confirm the design frontier with the owner: Q4 approved the `backend-development` name and Q5 approved test-first cadence, completing the material decisions and shared understanding.
4. [x] After shared-understanding confirmation, write the skill and only necessary bundled references/examples; preserve existing approval, repository, architecture and delivery boundaries.
5. [x] Finish the post-correction prose regression check and static/delivery preflight; register the actionable skill as ready and connect it to the specialized .NET role. Report actual changed files and verification.

Proposed coverage: discover project/version/component boundaries; verify Approved Specs and published OpenAPI; map requirements to code/tests; implement use cases within existing layers and the owner's Business Domain convention; derive transaction/lock/error outcomes from each approved branch; choose meaningful unit/database/API evidence; run configured build/test/static checks; report traceability and improve the skill after each error. Keep dynamic project facts discoverable and provide instructional conventions/examples inside the skill rather than requiring a particular endpoint example to remain present.

Owner decisions from round 1:

- Q1: “ภาษาไหนก็ได้เลย” — support backend projects in any programming language; inspect the actual project stack and keep .NET/e-commerce conventions scoped to that project rather than imposing them globally.
- Q2: “ใช่” — cover feature development, bug fixes and behavior-preserving refactors with the appropriate workflow for each.
- Q3: “ใช่” with a spec-first clarification requirement — require real database/HTTP evidence appropriate to changed guarantees. Read the governing spec before writing code; if it is not understood, ask before implementing. Every clarification must explain (1) what happened or is unclear, (2) its impact, (3) the recommended resolution and (4) the future consequences of that resolution.
- Use AskUserQuestion when available; this runtime has no tool with that name, so the current interview uses `request_user_input_async` as the available structured question UI, preserving all four required explanation fields.

Round 2 confirmed through the question UI: Q4 “ใช่ เปลี่ยนเป็น backend-development (แนะนำ)” and Q5 “ใช่ ใช้ test-first ตามที่เสนอ (แนะนำ)”. These confirmations authorize the proposed skill design; they do not approve any production feature, new library or architecture change. Keep the existing .NET role specialized and connect it to the generic skill with the .NET project reference.

Discovery evidence at the start of this task: The existing backend-developer role was ready, but the skill was a placeholder. The manifest-pinned child checkout is clean at `d8255183cba54d0c2b218607456b895a70df32f0`, with the exact declared origin. Read-only source inspection found .NET10, five production layers, custom CQRS, Dapper/Npgsql, exception-based UnitOfWork and Domain/Application tests using fakes; no new builds/tests or remote-reachability checks were performed. Login/refresh specs remain in-review, the code-structure guide remains draft and the OpenAPI paths are empty. These are evidence for readiness/consistency gates, not approval to implement those contracts. HTTP/Result failure alone cannot determine rollback: branch-specific retained effects must come from the approved spec.


Verification: Eight authored Markdown frontmatters, local links/anchors, fences and registry paths passed static checks; skill naming/description/scaffold checks passed. Scoped delivery preflight reports nine task paths (one deleted placeholder, four new skill/reference files) with no blockers. PyYAML is unavailable, so Ruby YAML parsing and direct metadata/reference checks were used without claiming the original Python validator ran. No production component code, schema, API contract, dependency or architecture changed.

Independent evaluation: An approved synthetic Python/SQLite bug-fix fixture captured a behavioral red on insufficient stock, then passed four public-interface tests after the minimal fix, including independent competing connections. A Go HTTP fixture with an in-review contradictory spec and empty OpenAPI produced two complete four-part questions and no implementation; its raw inputs stayed unchanged. A transaction planning fixture preserved the current callback interface and required successful audit commit before 401, with DB/HTTP tests identified as planned rather than executed. This is bounded evidence for the skill's decisions, not proof for every language/framework or production authentication.

Improvement verified: The evaluation exposed the blanket error-learning wording's confusion between intended red evidence and execution mistakes. The skill and lesson now distinguish them, retain mandatory preventive updates after actual mistakes and preserve authorization for out-of-scope skill edits. An independent prose replay confirmed the gap is resolved; initial report and fixture source/tests remain unchanged. Evaluation artifacts stay in an isolated temporary directory and are excluded from the PR.

Later owner policy: English topics/Thai question bodies and learning after every actual bug, conflict or issue are specified in the follow-up task above. That broader trigger supersedes the original execution-only/assigned-bug exemption; earlier evaluation records remain historical evidence, and deliberate red remains evidence linked to its actual underlying issue.

Delivery readiness: The agreed skill is implemented on `codex/backend-development-skill` in its managed worktree. Existing skill-work delivery authorization continues for this bounded resource package; final integration SHA, PR inventory and publication state are reported from Git/GitHub. The primary checkout's uncommitted code-review lesson, draft interview plan and cache remain untouched. Actual .NET/Go application builds, real production PostgreSQL/HTTP integration and fresh component remote reachability were not run because no production application change was made.

## repository-wide: Show per-file PR change summaries

Status: Guidance and delivery package complete. Ittikorn requested a file-by-file list with a nested summary in the PR delivery skill (called submit-and-pr in the request; the existing resource is commit-and-pr). The format now applies to PR Changes and chat Included, preserves the six PR sections and derives its inventory from the final integrated task diff. Actual integration, remote publication and file coverage are reported from Git/GitHub in the handoff.

1. [x] Read the current skill, formats, templates and lessons; confirm PR76 is merged and start a separate branch from current origin/main.
2. [x] Replace area/count-only summaries with the requested per-file nested format in the governing instructions and both templates; record the correction.
3. [x] Verify metadata, links and diff; prepare the scoped package, per-file inventory and required integration/check commands. Report actual integration/publication and file coverage from Git/GitHub.

Verification: Four Markdown frontmatters passed YAML parsing; skill metadata and Markdown targets/anchors passed direct checks. Both templates use the requested file/summary nesting, the PR template retains its six required sections and `git diff --check` passed. Scoped preflight reports six task files and no blockers. This correction updates the source format and both consumers so the delivered PR and chat must account for every file rather than collapse the list into areas/counts. No executable helper, API contract, database or diagram changed, so runtime/database tests and rendering were not required. The Python validator's missing PyYAML dependency was confirmed without starting a failing validator; Ruby YAML parsing and direct metadata/template checks cover this documentation-only change. The pre-existing untracked agent-workspace Python cache stays excluded.

## e-commerce: English code structure guide

Status: Translate the complete guide to English under the existing documentation delivery authorization. PR78 is merged; deliver this language revision as a separate follow-up PR. Preserve every layer/sub-layer, source reference, diagram and implementation/design distinction. The owner's ordinary-Codex/current-checkout instruction remains applicable.

1. [x] Inspect current guide, governing guidance, source baseline and merged PR state; preserve the source snapshot and reference inventory.
2. [x] Translate all prose, headings, tables, captions and code-block comments, retaining Service = Domain and all five layers / 24 sub-layer groups.
3. [x] Verify English-only content, unchanged link targets and structural coverage, frontmatter, source boundaries and all diagram bundles; record the translation-check correction and preventive delivery guidance.
4. [x] Prepare the scoped delivery package and latest-main integration/check procedure; report actual integration and follow-up PR publication from Git/GitHub without merging the PR.

Verification: English-only scan and heading/table/fence/link preservation passed; all five layers and 24 sub-layer groups retain substantive responsibilities, inputs/outputs, examples and boundaries. Four frontmatters, 20 local and 39 pinned component references passed. Three model/PNG integrity checks passed (72/47/99 cells), all 12 bundle hashes are unchanged and the component remains clean at its pin with 9 production / 5 test references. The captured positional-translation defect is rejected by the same gate that accepts the corrected guide; the delivery checklist and lesson record the prevention. No runtime build/tests are needed for this documentation-only change.

## e-commerce: Explain every code layer and sub-layer

Status: Content and verification complete; scoped follow-up publication package prepared after owner review. Ittikorn requested that the guide's meaning/scope cover every layer, then explicitly included sub-layers. PR75 is already merged, so deliver a separate follow-up PR under the existing documentation delivery authorization. Preserve the pre-existing table formatting and the other task's unpublished commit on its branch; read the component and diagrams without changing them. Actual base integration and remote PR state are reported from Git/GitHub at delivery.

1. [x] Inspect the owner's scope correction, current guide, pinned source, diagram responsibilities, Git/PR state and applicable writing/delivery guidance.
2. [x] Rewrite the introduction around all five layers and explain each layer's sub-responsibilities, inputs/outputs, boundaries, interactions and concrete source examples; retain Service = Domain and current/proposed status.
3. [x] Update the lesson and delivery checklist with a substantive coverage gate; verify all requested layers/sub-layers against source, Markdown/links and unchanged diagram/component evidence.
4. [x] Prepare the scoped follow-up publication package and required current-main integration/check commands; report the actual integrated base and remote PR state from Git/GitHub without merging the PR.

Coverage target: API (controllers, contracts, HTTP results, composition/authentication); Application (commands/queries, validators, handlers, mapping/responses, ports/common); Domain (entities/aggregates, value objects, business Domain, repository contracts, primitives/errors/status); Infrastructure (repository adapters, DbSession/UnitOfWork, security, email, options/DI, explicitly proposed adapters); Shared (messaging, dispatch/registration, results/errors). Cross-layer explanations must trace validation, transactions, security and error mapping without implying every request traverses every sub-layer.

Verification: The pre-review guide fails the new coverage audit on nine missing intro/detail requirements; the revised guide passes for all five layers and 24 sub-layer groups, plus cross-layer responsibilities and both test projects. Four Markdown frontmatters, 20 local references, 39 pinned component references, table/fence/whitespace structure and seven project-reference counts passed. All three model/PNG integrity checks passed; hashes of 12 diagram bundle files and section 3–9 user formatting are unchanged. The component is clean at the manifest revision. The preventive delivery-checklist gate was reviewed against the original omission and the correction; no backend/API/schema/diagram edits or runtime tests were required.

## repository-wide: Improve the delivery skill after every error

Status: Guidance and publication package complete. Ittikorn requested that every error encountered with `commit-and-pr` lead to a preventive skill improvement as well as correction of the immediate failure. The existing skill now includes the loop in its procedure, completion and report criteria, preserving delivery authority, scope and protected-branch rules. PR72 is merged; this is an independent follow-up PR. Actual base integration and publication state are reported from Git/GitHub.

1. [x] Read applicable rules, lessons and the current skill; confirm PR72 is merged and start a separate branch from current origin/main.
2. [x] Add the root-cause, preventive skill update, verification and lesson loop; record the correction.
3. [x] Verify metadata, links, diff and failure-scenario coverage; prepare the scoped package and required main-integration/check commands for publication. Report actual integration and PR state from Git/GitHub.

Verification: YAML parsing passed for all three changed Markdown files; direct skill checks passed allowed metadata, name/description constraints, unfinished-placeholder checks and Markdown targets/anchors. Scoped preflight reports three task files and no blockers, and `git diff --check` passed. The loop was exercised when `quick_validate.py` could not start (`ModuleNotFoundError: No module named 'yaml'`): a preventive instruction now distinguishes startup failures from validation findings and requires explicit coverage/gaps for equivalent checks. Ruby YAML parsing and direct metadata/reference checks cover the relevant skill validation properties; no original-validator success is claimed. Review also confirms errors must produce an actual skill/resource change, lesson and evidence before completion, with integration/publication gates retained. No helper, API contract, schema or diagram changed, so runtime/database/generator tests and rendering were not run.

Scope correction during publication: A temporary verification script rejected an unrelated concurrent edit to `e-commerce/doc/code-structure.md` because it demanded a globally clean working tree. The check was corrected to validate task paths and the three-file PR diff while preserving the other task's file; the skill's merged-result step and the lesson were improved accordingly. The unrelated edit is excluded from publication.

## e-commerce: Code structure guide with existing diagrams

Status: Documentation complete; PR delivery directly authorized by Ittikorn's “เปิด pr มา”. Ittikorn requested `e-commerce/doc/code-structure.md` with diagrams reused from `e-commerce/diagram/`, following the clarification that Service = Domain means reusable business logic and the owner-selected path is `Ecommerce.Domain/Authen/Domain/`. The original writing phase read the pinned component and reused diagram bundles without changing them. The initial guide and lesson clarification are already in main at `ec4645e` through the separate handoff commit; this PR finalizes the guide's verification record and task completion rather than claiming to introduce that existing content.

1. [x] Read applicable rules, lessons, component manifest, current backend conventions and diagram-creator; inspect the three selected renders and their source/companion evidence.
2. [x] Write the Thai guide with runtime/repository/identity diagrams, layer and feature responsibilities, Service = Domain terminology, current versus owner-directed structure, CQRS flows and source links.
3. [x] Record the terminology correction in lessons; verify Markdown/frontmatter/links, model/PNG integrity, component evidence and unchanged diagram/component hashes; record actual results.

Selected views: runtime architecture explains collaboration and the proposed reusable Domain child; repository architecture explains source ownership and compile references; identity domain explains business concepts derived from schema without implying implemented classes or aggregate ownership. Existing pictures are embedded and linked to editable sources; no new rendering or diagram redesign is requested.

Verification: The Thai guide has 11 main sections, three existing PNG embeds, 20 local references and 15 pinned component references. YAML/frontmatter, fences, table widths, links and all seven project-reference counts passed; production/test references total 9/5. All three existing editable model/PNG bundles passed integrity and native nesting checks, and their PNGs were opened for visual inspection. Hashes of all 12 selected bundle files are unchanged; the component remains clean at the pinned revision. The existing Domain-convention lesson was extended rather than duplicated. No backend/API/schema/diagram changes, runtime tests, new diagram rendering or native-editor interaction were performed for this documentation-only task.

Delivery plan: use a two-file documentation commit (`code-structure.md` verification subsection and this task section), fetch and merge latest origin/main into the task branch, resolve any overlaps while preserving both sides, rerun document/diagram checks and publish a Showcase PR without merging it. Integration SHA and actual PR state are reported from Git/GitHub at delivery.

## repository-wide: Improve the API skill after every error

Status: Guidance and follow-up PR package complete. Ittikorn requested that every error lead to an improvement of `api-contract-design`, in addition to correcting the work. The existing skill now requires a root-cause, preventive skill-improvement and verification loop while preserving specification approvals. Follow-up publication continues under the existing direct delivery instruction for this skill work; actual PR state is reported from GitHub.

1. [x] Review the skill's procedure/completion criteria, relevant lessons and applicable authoring rules.
2. [x] Add the improvement loop and record the owner's correction, with explicit coverage of self-discovered failures and review feedback.
3. [x] Verify Markdown metadata, references, scope and diff; prepare the follow-up PR under the existing delivery instruction for this skill work.

Verification: YAML parsing passed for all three changed Markdown files; skill name/description constraints, Markdown links/anchors and `git diff --check` passed. Review against the prior missing-example failure confirms owner corrections now trigger an actual preventive skill change, not only an artifact fix; command/check/render failures and self-discovered errors are explicit triggers too. Completion criteria and the report require the improvement and its evidence. Scoped delivery preflight reports three task files and no blockers. No examples, helpers, checkers, API contracts or database artifacts changed, so runtime/database/generator tests and rendering were not repeated. The Python skill validator's missing PyYAML dependency remains covered by YAML and direct metadata/structure validation without installing dependencies. The three unrelated untracked handoff documents are excluded.

Loop exercised during delivery: Rebasing onto current main stopped at overlapping task-plan insertions. The resolved plan retains both independent sections and preserves all upstream content byte-for-byte; the skill's correction step was strengthened to require that preservation check, and the lesson records the cause and evidence.
## repository-wide: Integrate main before opening a PR

Status: Guidance, verification and publication package complete. Ittikorn requested that `commit-and-pr` merge the latest main into the task branch, resolve conflicts and verify the result before opening the PR. Update the existing skill, checklist, formats and PR template; clarify the named-workspace rule's merge wording to match the approved design's prohibition on merging PRs into main. Preserve protected-main and no-force-push boundaries. Keep the prior API skill PR separate. The final integrated SHA and actual PR state are reported from Git/GitHub after publication.

1. [x] Read the delivery skill, preflight behavior, applicable rules and lessons; start an independent task branch from current origin/main.
2. [x] Define the mandatory main-to-task merge, conflict resolution, post-merge checks and publication evidence consistently across the existing resources.
3. [x] Exercise clean and conflicting merges in isolated temporary repositories; verify metadata, links and the scoped diff.
4. [x] Prepare the scoped delivery package and integration/check commands; report actual base integration and publication evidence from Git/GitHub.

Verification: Isolated local Git repositories exercised a real clean merge, a real same-position task-plan conflict, an already-up-to-date result and an ordinary push after integrating main into a previously published task branch. Both sides' content survived, the integrated base was an ancestor of HEAD, no unmerged entries remained, final PR diffs contained only task changes and integration did not change remote main. YAML, skill metadata/link/anchor checks and `git diff --check` passed. The preflight script is unchanged and its limited uncommitted-file coverage is now explicit; integration evidence is a separate required gate. The named-workspace clarification follows the approved design's explicit no-PR-merge safety boundary; no registry capability or lifecycle operation changed.

Delivery readiness: Named-workspace regression tests passed 15/15, scoped preflight reports seven task files and no blockers, and the task commit/PR messages are prepared. The three untracked handoff documents remain excluded. No API, schema, backend or production diagram changes require project runtime/database tests. The Python skill validator's missing PyYAML dependency is covered by Ruby YAML parsing and direct metadata/reference validation without installing dependencies.

## repository-wide: Operational diagram-creator and script separation

Status: Implementation and verification complete on `chore/jinny-diagram-creator-skill`. Direct owner request: adapt Jinny's verified diagram work into the existing `.agents/skills/diagram-creator` and move reusable Python out of `e-commerce/diagram`. Scope includes that skill, its registry/role pointer, task plan, diagram references and `e-commerce/scripts/diagrams`; delivery none. Named workspace prepared from current main; both existing diagram generator checks passed before changes.

Use skill-creator for the existing skill, writing-for-agents for concise instructions, and agent-workspace for isolation. Keep diagram-creator as the repository evidence/packaging/verification workflow and diagram-design as an optional available visual-design companion. Promote real lessons on diagram meaning, native hierarchy, source status, database cardinality, artifact folders and visual review; preserve project-specific choices as examples rather than global mandates. Extract reusable native draw.io/PNG and geometry helpers into skill scripts; retain e-commerce content/generators in project scripts. No schema, API, backend or rendered-diagram redesign is authorized.

- [x] Inspect current resources, lessons, latest artifact layout and Python dependencies; prepare a bounded managed assignment and record baselines.
- [x] Replace the existing placeholder with an actionable skill and focused references/template; connect its registry and role discovery without changing agent authority.
- [x] Extract reusable helpers/checker with meaningful invalid-artifact tests; move all 13 project Python files outside diagram outputs and update imports/path resolution/source links/commands.
- [x] Verify generators, table/FK evidence, script behavior, Markdown and artifact parity; forward-test realistic skill behavior in isolated temporary output when available.
- [x] Review the resulting diff, mark only verified work ready and record limitations. Retain the uncommitted task branch; release the editing-session lock as the final session operation. No commit/push/PR is included.

Progress: The existing placeholder now has an evidence-first entrypoint, three focused references and an explanation template; registry and Jinny role point to the ready skill. Extracted native cell/geometry/PNG helpers are used by the relocated e-commerce generators. All 13 project Python files now live outside `diagram/`; imports, output routing and Markdown source/reproduction paths were updated. The nine content/render modules needing no path/helper edit remain byte-identical.

Verification: Both relocated generator families pass `--check` and `--finalize-pngs`; the new CLI verifies all 19 bundles with native nesting required. SHA-256 confirms all 19 draw.io sources, 19 PNGs, 19 HTML files and the frozen SQL inventory are unchanged. Domain accounting remains 53/53 tables and 75/75 FK columns with zero schema-doc findings. Eleven artifact regression tests pass. Python syntax, 19 changed/new Markdown frontmatters/links/fences, CWD-independent compatibility entrypoints and `git diff --check` pass. `quick_validate.py` cannot start because PyYAML is absent in both installed Python interpreters; Ruby YAML parsing and direct metadata/structure checks substitute without installing dependencies. No new render/browser/native-editor session is needed for unchanged artifacts, and none is claimed. Independent forward-testing completed in `/private/tmp/jinny-diagram-forward-VczY7U`: generated a four-concept/four-association domain model, editable PNG and detailed companion from raw SQL. Partial uniqueness, nullable shipment order and unenforced shop consistency were represented correctly; source/cardinality checks and local relational witnesses passed. Native draw.io 32.6.10 export and shared PNG verification passed (one page, 30 cells, 1659 × 1430), and the evaluator and primary visually inspected the sample. No substantive skill gap was observed. Interactive editor drag/re-save/re-export was not performed in the evaluation; its companion records that limit. No evaluation artifact entered the repository.

Delivery authorization (2026-11-08): Ittikorn requested the PR with “pr มายัง”, authorizing commit, task-branch push and PR against `main` for the completed skill/script-separation package. This supersedes the earlier delivery-none boundary for the same task only. The current origin/main registry, managed clone identity, original task/branch/scope and authorized user were validated before recording `open-pr`; no task or scope was expanded.

- [x] Run delivery preflight, verify the exact staged package and create the fixed-format commit.
- [x] Reconcile the commit with latest `origin/main`, repeat affected checks and prepare the authorized task-branch/PR publication. Report actual remote URL/status in the handoff after publication; release the session lock as the final session operation.

Delivery verification: Reconciled with `origin/main` at `c69dc19`. The only rebase conflict was the shared task plan; preserved upstream task records byte-for-byte and inserted this task section separately. The final package has 36 changed files including 13 detected renames. Eleven tests and both generator families pass after reconciliation; all 19 native bundles pass the shared verifier and all model/PNG/HTML/inventory hashes remain unchanged. Named-agent delivery preflight reports `no blockers found`. Publication is authorized; the final PR URL and remote state are derived from GitHub in the handoff rather than presumed here.

## repository-wide: Make sequence guidance self-contained

Status: Guidance correction and publication package complete under Ittikorn's existing “ส่ง pr มา” instruction for this skill change and subsequent direction to continue the correction. The example and presentation rules now live in the skill's existing reference and remain available if the original project example is moved or deleted. The agreed complete-flow and exact-SQL requirements are preserved. Actual remote publication is reported from GitHub in the handoff.

1. [x] Inspect the current guidance, generator and original visual conventions; identify mandatory references to the external example.
2. [x] Replace those references with explicit presentation rules and an embedded, complete spec/sequence example in the skill's existing reference.
3. [x] Record the correction and verify metadata, links, example SQL parity, rendered output and independence from the original file.
4. [x] Prepare the four-file follow-up commit and PR package, preserving the three unrelated handoffs; report the actual PR URL and state from GitHub.

Verification: YAML parsing passed for the skill, reference and both task records. Markdown links/anchors resolve, and neither skill document retains a login-file dependency. The embedded sample's SQL matches its sample spec character-for-character; database lifecycle, structure, request-heading and public response checks pass. Copying only the generator and sample spec to an isolated temporary directory with no project/login files successfully generated the matching scaffold. PlantUML rendered the embedded complete example to PNG/SVG; visual inspection passed and occurrence counting found all 6 SQL lines visible. `api-sequence-spec` passed all 83 current specs; `git diff --check` passed. No generator, checker, endpoint contract or production diagram was changed.

Delivery readiness: `codex/self-contained-api-sequence` targets `main`; scoped preflight reports 4 task files and no blockers. The three untracked handoff documents stay outside this package. The commit message and six-section PR body are prepared; the actual PR link and status are determined after publication.

## repository-wide: Complete API sequence authoring guidance

Status: Complete. Guidance confirmed by Ittikorn on 2026-11-08 with “ใช่” in response to the concrete proposal: complete flow in the login presentation style, strict SQL equality allowing only note indentation and leading-apostrophe escaping, and documentation-only changes. Scope is the API contract skill and its existing sequence reference, with task bookkeeping. The login sequence is the presentation prototype; each endpoint's spec remains the source of behavior and SQL.

1. [x] Read global and Markdown rules, relevant lessons, the requested skills, the existing API skill, login prototype, generator and parity checker; preserve unrelated working-tree changes.
2. [x] Confirm the concrete sequence guidance, including the meaning of exact SQL parity and the documentation-only change boundary, with the owner before editing the skill.
3. [x] Update the existing skill and sequence reference to require complete endpoint-specific flows in the login format, with explicit SQL parity and rendered verification criteria.
4. [x] Validate skill metadata, reference links, consistency with the prototype and tooling, and the scoped diff; report existing checker failures separately.

Discovery evidence: The current sequence reference already copies SQL through a skeleton but does not fully describe the login narrative or require rendering every completed diagram. The SQL checker decodes a leading `&#39;` and normalizes whitespace, so its success alone does not establish character-for-character SQL equality. No endpoint, generator, checker, or backend change is planned.

Verification: Ruby YAML parsing passed for all three changed Markdown files; skill name/description constraints, reference links/anchor, fence balance and `git diff --check` passed. A separate strict comparison of the login prototype passed all 15 SQL occurrences without whitespace normalization; `check_docs.py login-flow` passed all 7 outcome paths. `quick_validate.py` could not start because both installed Python interpreters lack PyYAML; the metadata and structural checks above were used instead, without installing dependencies. `api-sequence-spec` retains the pre-existing failure at `authen-and-author/08-inquiry-user-profile/sequence.wsd`: it already has token/timeout answers but remains in `LEGACY_TOKEN_SEQUENCES`. That unrelated checker issue was not changed. No API spec, sequence, generator, checker or backend was modified; runtime/database tests, generator mutation tests and diagram rendering were not required for this documentation-only change.

Delivery authorization (2026-11-08): Ittikorn requested “ส่ง pr มา”, directly authorizing a commit, task-branch push and PR against `main` for these two skill documents and this task record. The existing checkout sequence diagram edits and three untracked handoff documents belong to other work and are excluded.

- [x] Create the task branch, run scoped delivery preflight and inspect the exact staged files.
- [x] Commit the three-file package, reconcile with current `origin/main` and verify the final PR diff.
- [x] Prepare the authorized task-branch push and PR body with verification, approved decisions and exclusions; derive the final publication URL/status from GitHub for the handoff.

Delivery verification: The task commit was rebased onto `origin/main` at `def2eb2`; all five excluded files were restored byte-for-byte, and the PR diff contains only the two skill documents and this task record. Scoped preflight has no blockers. The previously observed legacy-list failure was fixed upstream: `api-sequence-spec` now passes all 83 specs, and `login-flow` passes all 7 outcome paths. No API checker change belongs to this task. The committed checklist records publication readiness; the actual PR URL and remote state are reported from GitHub after publication.

## e-commerce: Migrate backend to a Component Repository

Status: Implementation and verification complete; approved Showcase PR package prepared. Ittikorn explicitly approved M1–M8 in `docs/superpowers/specs/2026-11-07-e-commerce-component-migration.md` with “อนุมัติตามแผน ใช้ repository แบบ Public”. Approval was persisted at 2026-11-07T14:00:23Z before export/publication/moves. Continue as ordinary Codex in the current checkout under the earlier selected backend-developer perspective. The scope includes public `ittikornsopawan/e-commerce-backend`, filtered backend history, backup, manifest-managed checkout and a separate Showcase migration PR without merging. Actual remote PR delivery is verified through GitHub; PR #33 is merged.

- [x] Read component-repository rules, bootstrap skill, ADR, project knowledge, current Git state and references; confirm missing manifest, 81 tracked backend files and migration-pending status.
- [x] Verify the current backend baseline and prepare the concrete migration design without moving existing files or publishing a new repository.
- [x] Confirm the proposed GitHub identity, visibility, history strategy and migration/delivery scope; persist approval before executing migration.
- [x] Export only backend history in temporary storage, update cross-repository documentation links and prove source-tree preservation plus component verification.
- [x] Create/deliver the new GitHub repository and verify its default-branch commit exists remotely before recording a manifest revision.
- [x] Preserve the complete legacy checkout including ignored artifacts in an identified backup, replace tracked backend ownership with manifest/.gitkeep/ignore entries and bootstrap the declared component safely.
- [x] Update live references and project knowledge, validate manifest/revision/ownership/link boundaries and record actual build/test/bootstrap evidence.
- [x] Prepare the verified migration commit and authorized Showcase PR package; report actual remote delivery state from GitHub and leave merge to the owner.

Progress: Export preserved 81/81 tracked files and four backend-only history commits. The component build passed with 0 warnings/errors and all 40 tests passed. Public child main is remotely verified at `d8255183cba54d0c2b218607456b895a70df32f0`. The shared primary checkout was externally switched/updated during export; the migration branch was reconciled with current origin/main, backend snapshot equality was checked and this task section was restored without replacing other task sections.

Bootstrap/backup evidence: The actual GitHub clone is clean and detached at the manifest SHA with exact origin `https://github.com/ittikornsopawan/e-commerce-backend.git`. Restore, full solution build (0 warnings/errors) and 40/40 tests passed again from `e-commerce/repository/e-commerce-backend/`. The original directory is retained at `/private/tmp/ecommerce-component-migration-ofejl0ty/legacy-checkout` with all 591 file/directory entries hash-verified, including ignored artifacts. Cross-repository guide links were updated only in the component; source/tests/configuration are unchanged. No legacy backup or unrelated handoff was deleted.

## e-commerce: Backend code structure guide

Status: Complete. Ittikorn requested a detailed `e-commerce/repository/code.md` for later diagram review and explicitly selected ordinary Codex in the current checkout, using the backend-developer perspective, without a commit. This assignment does not use named-agent delivery authority. The guide remains draft; writing it does not approve the architecture proposals it contains.

- [x] Read applicable rules, project knowledge, backend conventions, source files, tests, and the preceding Domain/CQRS discussion.
- [x] Write the Thai guide with source-linked project structure, dependency direction, layer responsibilities, Domain modeling decisions, CQRS dispatch, Authen flows, transactions, error handling, and testing conventions.
- [x] Separate observed implementation from proposed policies, missing capabilities, and decisions awaiting specification approval; include a checklist for the upcoming diagram review.
- [x] Validate frontmatter, local references, source correspondence, Markdown structure, and the exact changed-file scope; record verification results without changing backend behavior or committing.

Verification: YAML/frontmatter, local references, section/table/fence structure, C# excerpts, all five project-reference sets, all five controller routes, Authen-only implementation scope and login/refresh in-review metadata passed static checks. `git diff --check` and a separate whitespace check of the new guide passed. Existing unrelated untracked handoff files were preserved. No backend build, runtime tests, database verification, diagram changes or commit were performed for this documentation-only assignment.

Delivery authorization (2026-11-07): Ittikorn subsequently requested a PR using `commit-and-pr`, superseding the earlier no-commit boundary for these two task files only. Use ordinary Codex in the current checkout; include `e-commerce/repository/code.md` and this task-plan section, exclude the three pre-existing handoff files, and target `main`. The guide and its architecture proposals remain draft. Remote delivery state will be reported from GitHub rather than presumed in this plan.

- [x] Confirm direct delivery authorization, isolate the task branch and inspect the latest main without including another task's files.
- [x] Revalidate the guide, run the scoped delivery preflight and prepare the fixed-format commit and PR package.
- [x] Create the scoped local commit, reconcile the task branch with current origin/main and prepare the authorized push/PR handoff; report actual remote delivery state from GitHub.

## e-commerce: Jinny architecture diagrams

Status: Detailed diagrams and the combined Redis/MongoDB design proposal are verified locally in `.workspace/jinny` on `docs/jinny-ecommerce-diagrams`. The owner selected the store responsibilities; detailed policy documents remain in review before downstream implementation. Registration PR 22 is merged. Delivery was initially local only; the owner subsequently authorized the completed-package PR on 2026-11-07 (see delivery section below). The approved default light style is retained.

- [x] Read the bootstrap, applicable rules, lessons, diagram-design skill, existing diagram payload, backend project structure, project references, and relevant payment/shipping specifications.
- [x] Register Jinny with a dedicated diagram designer role, reporting to Josh, repository-wide scope for diagram assignments and required task bookkeeping, and no delegation capabilities; validate the role, registry, and existing workspace tests.
- [x] Obtain direct user authorization for registration delivery; prepare the registration branch and PR package, preserving unrelated handoff files. Merge remains the owner's action.
- [x] After registration reaches origin/main, prepare Jinny's managed workspace with an assignment limited to `e-commerce/diagram/` and required task bookkeeping; delivery remains none.
- [x] Record the visual plan before drawing: Architecture views for compile-time project dependencies (5 nodes, 5 core arrows with 4 Shared references summarized), backend request flow (8 functional nodes), and specification-level commerce domains (9 nodes); `doc-wide` 1280 x 720, engineer audience, default light style, at most nine functional nodes per image.
- [x] Create self-contained HTML sources and editable draw.io PNGs for `architecture-design`, `repository-architecture`, and `system-design`, based on inspected evidence without introducing architecture changes; mark specification-only capabilities explicitly.
- [x] Run skill self-checks, inspect connector geometry and text bounds, reopen embedded draw.io models, render and visually review all three final PNGs, and document any merged or omitted source content.
- [x] Deliver the three requested files with verification evidence and any unresolved limitations.

Evidence: `architecture-design.drawio.png` and `system-design.drawio.png` are zero-byte files; the extractor reports `not a draw.io file (no mxfile, mxGraphModel, or payload)` for each. `repository-architecture.drawio.png` contains eight functional components plus decorative cells and legend edges. The current backend implements Authen in five .NET 10 projects; broader payment and shipping capabilities are described in specifications and must not be presented as implemented code. Jinny was absent at initial inspection and is now enabled on origin/main after PR 22. Registration must be effective on origin/main before managed-workspace mutation begins, per `.agents/rules/named-agent-workspaces.md`.

Registration verification: `python3 -B -m unittest discover -s .agents/skills/agent-workspace/tests -v` passed all 13 tests, including Jinny's role, enabled registry lookup, reporting line, workspace key, and inability to delegate delivery. Role frontmatter and registry pointer checks passed; `git diff --check` passed. Initial diagram verification was deferred until registration; current diagram verification is recorded below. Existing unrelated untracked handoff files were preserved.

Assignment: agent `jinny`, role `.agents/agents/diagram-designer.md`, task `Create and visually verify the three e-commerce architecture drawio PNG diagrams from current project evidence`, scope `e-commerce/diagram`, `tasks/todo.md`, `tasks/lessons.md`, delivery `none`, authorized by `ittikorn`. The helper stored the assignment and acquired the execution lock. No repository baseline command is declared for this diagram-only scope; preparation reports `not-declared`.

Rendering plan: generate self-contained HTML and editable draw.io XML from one reproducible semantic/geometry model, export PNG using installed draw.io Desktop with embedded editable models, and extract/re-export each PNG to verify editability. The skill's Python PNG exporter is unavailable: `python3` has no Playwright and `python` is not installed. No dependency installation is planned. HTML follows the default web-font stacks; native draw.io exports may use the explicitly supplied Arial/Georgia/Courier New fallbacks. Keep all exports on the light paper background and inspect actual text bounds and the final images.

Initial compact revision verification (superseded by the detailed revision below, 2026-11-07): all 3 HTML self-checks passed. The generator accounts for all 9 direct project references and verifies 5/8/9 functional nodes, 5/9/8 connectors, orthogonal routing, distinct ports, 6–10px label gaps, no node or label overlaps, no connector crossings, and no transit through unrelated boxes. All 3 final PNGs were visually reviewed. A WAIT_PAYMENT label was moved away from the Stripe API path before the final review. Browser QA at 390px found no page overflow and no node text overflow in any HTML, with local diagram scrolling retained. Native and compatibility PNG metadata match each `.drawio` source; the skill extractor produces identical models except for input filenames. Reopening each final PNG in draw.io and exporting again preserves identical IDAT bytes. Native PNG dimensions are 2562 x 1442, including draw.io's page frame; file sizes are 379571, 488606, and 461986 bytes respectively. `git diff --check` passed. `e-commerce/diagram/README.md` documents source evidence, fidelity changes, reproduction and font/export limitations. Backend/API/database checks were not run because no governed behavior, contract, schema, or code changed. The default web fonts were unavailable during browser QA; the reviewed native PNGs use the declared system fallbacks. The skill's repository-only geometry script is not installed, so explicit route checks and rendered review were used. The owner subsequently requested deeper research and a redesign because the three views were too shallow and too similar; the revision checklist below supersedes this completion assessment.

Revision requested by Ittikorn (2026-11-07): add substantially more useful detail to all three files, research diagram conventions first, and revise with diagram-design. Continue the existing assignment and branch; delivery remains none.

- [x] Reacquire the editing-session lock after validating the same agent, branch, assignment, scope, and no open Jinny PR; preserve all existing files.
- [x] Record the owner's correction and its root cause in `tasks/lessons.md`.
- [x] Research primary sources for architecture/context, repository/code structure, and system lifecycle views; write findings and citations under `e-commerce/diagram/`.
- [x] Inspect current project files and specifications deeply enough to ground the added components, source hierarchy, state transitions, guards, and transaction effects.
- [x] State a new per-file purpose, visual grammar, canvas/detail decision, and fidelity ledger before redrawing.
Revised visual decisions: all three use `print-a3-landscape` 1584 x 1120 and the previously approved default light style. Architecture uses a runtime boundary/integration layout with eight functional elements and explicit CODE/SPEC wording; repository uses a three-level Tree with nine nodes (root, src/tests/build, five production project leaves) and declared references inside each leaf; system uses the Lifecycle phase map pattern and State Machine grammar, with four primary order phases, separate retry/recovery routes, two alternate terminal outcomes, and local transaction effects. This replaces the earlier uniform 1280 x 720 component-card treatment. Keep native PNG export and editable metadata verification because Playwright remains unavailable. `research.md` contains official C4/Microsoft/W3C sources and project evidence. No new behavior or architecture is approved or implemented by these presentation changes.

- [x] Rebuild all three PNGs and matching editable/HTML sources with distinct compositions and concrete details; preserve implemented-versus-specified status.
- [x] Run geometry/content/skill checks, render and review all three side by side, and verify each PNG's editable model round trip.
- [x] Update the diagram README and deliver the revised files with a concise explanation of what each now communicates.

Detailed revision verification (2026-11-07): `research.md` records official C4/Microsoft/W3C sources and linked repository evidence; the owner correction is recorded in `tasks/lessons.md`. All three source views use A3 landscape 1584 x 1120 with distinct grammars: runtime Architecture (8 nodes/9 connectors), source Tree (9 nodes/8 connectors), and order Lifecycle phase map/State Machine (6 persisted states + initial marker/8 transitions). Content accounts for all 9 production references, 5 test references and all 6 displayed order states. Rich local detail covers interfaces, actual filenames, actor responsibilities, provider callbacks, expiry, guards, stock/budget effects, transaction scope and lock order. Geometry checks passed including annotation/connector separation; visual review corrected a webhook path through a boundary label and lifecycle notes near cancel/retry routes. All three skill HTML self-checks passed; SVG export helper passed in temporary QA output. Browser checks at 390px passed with 1584px local scrollers, no page overflow and no node text overflow. Final PNG dimensions are 3170 x 2242; sizes are 1256035, 1117069 and 1160181 bytes. The PNGs' native/compatible editable metadata exactly matches source XML; packaged extraction matches the sources, and reopening all three PNGs in draw.io and exporting again yields identical IDAT bytes. All final images were visually reviewed and compared as a set. README and research decisions were updated; frontmatter, recorded scope (15 changed paths) and `git diff --check` passed. No backend/API/database tests or provider calls were run because behavior, code and schema are unchanged. PNG rendering uses installed draw.io and disclosed system font fallbacks because Playwright/web fonts are unavailable. High-resolution PNGs exceed 1 MB and remain local; no delivery exception or PR approval is inferred. All requested revision work is complete.

Redis extension requested by Ittikorn (2026-11-07): add Redis for rate limiting, caching and appropriate related capabilities to the ongoing diagram/design work. The request establishes the Redis direction; detailed policies and failure behavior remain a draft architecture decision. Continue the existing diagram assignment with delivery none, retaining prior artifacts. New design/research files stay under `e-commerce/diagram/`.

- [x] Resume the same workspace/assignment after identity, scope and open-PR checks; inspect existing Redis/cache/rate-limit evidence and the governing SDD approval gate.
- [x] Research official Redis/.NET documentation for distributed limits, cache-aside/invalidation, eviction isolation and outage behavior; record direct sources.
- [x] Inspect public storefront queries, master-data writes, authentication lock rules and transactional order/payment paths to identify safe cache boundaries.
- [x] Write an in-review Redis architecture proposal with concrete use cases, keys/TTLs, invalidation, rate policies, outage decisions, security boundaries, acceptance criteria and downstream changes.
- [x] Add Redis to the three diagram views as an explicitly proposed design, preserving current-code and business-state truth; render and review the proposal.
- [x] Validate the proposal, diagram geometry/HTML, source metadata and editable PNG round trips; record limitations and verification.
- [x] Prepare the concrete proposal and verified diagram changes for owner review; keep policy approval separate from the selected high-level Redis/MongoDB direction.

MongoDB extension requested by Ittikorn during the Redis design (2026-11-07): add MongoDB for configuration and selected transactions. This continues the same diagram assignment and path scope; no implementation or database migration is authorized. The owner has selected audit/integration events and historical transaction copies, plus feature flags/general config including Redis policies; PostgreSQL remains business authority.

- [x] Clarify MongoDB transaction ownership and configuration scope; preserve PostgreSQL authority until the owner chooses otherwise.
- [x] Research MongoDB primary sources for configuration documents, validation/versioning, indexes, TTL, transactions and cross-store consistency.
- [x] Extend the proposed architecture and three diagram views based on the owner's answers, with explicit current/proposed status and no invented financial ownership.
- [x] Verify the combined Redis/MongoDB design and rendered artifacts before the owner handoff.
- [ ] Obtain approval of the detailed in-review policies before any backend, collection/outbox schema or endpoint contract implementation; this is outside the completed diagram work.

Owner clarification (2026-11-07): MongoDB stores feature flags/general configuration including cache/rate policy, plus audit/integration events and transaction copies for historical search. PostgreSQL retains business/financial authority. `mongodb-design.md` records the selected ownership and proposed publication/outage rules. Remaining policy approval is not inferred from the selection. Runtime view merges in-process HTTP/CQRS use cases into one host node so two Redis roles, MongoDB and PostgreSQL fit the nine-node budget without pretending layers are separate services. Existing source references and order states remain unchanged.

Combined proposal verification (2026-11-07): official Redis/MongoDB research and design records are linked from the README. The independent Redis documentation review is retained with a separately attributed primary-agent remediation note; it is not runtime certification. Source/geometry checks pass for runtime 9 nodes/11 connectors, repository 9/8 and lifecycle 6 persisted states + initial marker/8 transitions. All three packaged HTML self-checks pass. Final browser review at 390px has 1584px local scrolling, no page overflow and no node text overflow. All three final native PNGs were visually reviewed; dimensions are 3170 x 2242 and sizes 1542604, 1252053 and 1222724 bytes. Native/compatible embedded metadata matches source XML, packaged extraction matches each source, and opening each PNG in draw.io and exporting again preserves identical IDAT image data. Detailed config/outage/retention/quota values remain proposals; production sizing and runtime load/failover/clock/outbox tests are unperformed. Backend/API/database tests were not run because no implementation or contracts changed. The default light style and declared native font fallbacks remain in use. No commit, push or diagram PR was performed. Markdown frontmatter/local links and in-review approval markers pass; all 22 changed paths stay within the recorded assignment; `git diff --check` passes.





## e-commerce: Detailed explanations for the three diagrams

Status: Complete locally; requested directly by Ittikorn on 2026-11-07. Continue the same Jinny diagram assignment and managed branch; delivery was none at authoring and is superseded by the later explicit PR instruction below. This is explanatory documentation of the existing diagrams and proposals, not a new architecture approval or implementation task.

- [x] Read the three diagrams' semantic sources, current README, Redis/MongoDB proposals, project evidence, rules and relevant lessons; verify the same workspace identity and assignment and acquire a fresh editing-session lock.
- [x] Write one detailed Thai Markdown companion per diagram, covering how to read it, every component/relationship, concrete flows, design rationale, trade-offs, authority boundaries and source references.
- [x] Link the explanations from the diagram README; keep policy numbers and CODE/SPEC/PROPOSED status aligned with the existing design records.
- [x] Verify source/model coverage, local links, Markdown frontmatter, consistency, unchanged PNGs and the final diff; record results and release the editing-session lock.

Verification (2026-11-07): three Thai companion documents total 511 lines and are linked from the diagram README. Reviewed their rationale, CODE/SPEC/PROPOSED status and authority/failure claims against the semantic model, current source/specs and in-review Redis/MongoDB records. Coverage checks pass for all 11 runtime relationships, five production/two test projects, six order states and eight lifecycle transitions. Source checks still match 9 production/5 test references and six displayed order states. All diagram Markdown frontmatter/local links/code fences pass. PNG IDAT data remains identical to the previously verified native round-trip exports; no diagram regeneration was needed. Official Microsoft/Redis/MongoDB references were consulted for the technical rationale. `git diff --check` passes. No backend/API/schema changes, builds, runtime tests, commit, push or PR were performed.

## e-commerce: Deliver the completed diagram package

Status: Verified and ready for commit/push/PR; actual delivery state is derived from Git/GitHub. On 2026-11-07 Ittikorn directly requested a PR for the completed three diagrams and their Markdown explanations using commit-and-pr, before work on the additional views. This supersedes delivery none for this completed package only; it does not approve detailed Redis/MongoDB policies or implementation. Continue the same assignment, branch and path scope.

- [x] Read commit-and-pr and its exact formats/checklist; select the completed diagram package and preserve the unstarted additional-view work.
- [x] Persist the direct owner's delivery grant for the active assignment; run delivery preflight and resolve or explicitly obtain approval for findings.
- [x] Recheck source/model consistency, HTML, editable PNGs, Markdown frontmatter/links and the exact staged diff.
- [ ] Commit the chosen paths, push the existing task branch and open one PR against main; attach it to this chat and inspect its status once.
- [ ] Release the editing-session lock and hand off the PR; additional views wait for this PR's reconciliation under the named-agent lifecycle.

PR preparation verification (2026-11-07): delivery-check recognizes the direct owner authorization and all 23 paths remain in scope (21 diagram package files plus tasks/todo.md and tasks/lessons.md). Preflight reports no blockers. Refreshed origin/main revealed merged WP3b; the lifecycle/runtime note/research/explanation now include guarded seven-day completion instead of the superseded no-job rule. Native exports use scale 1.5 (2378 x 1682) and compressed compatible mxfile metadata; final PNG sizes are 1014302, 824217 and 829340 bytes, all below 1 MiB. Every final image was visually reviewed; packaged extraction equals source and native PNG reopening/re-export preserves exact IDAT data. Three HTML self-checks and all 12 authored Markdown frontmatters/local links pass. Geometry/evidence checks pass. Backend/API/database checks are outside this diagram-only change. Additional architecture-package views are unstarted and excluded from this delivery.

## e-commerce: Supporting architecture and operational diagrams

Status: Complete. Editing session closed after GitHub verified PR 48 merged and agent-workspace parked the clean previous branch. New branch `docs/jinny-architecture-details`; owner requested all previously identified gaps, in the same editable PNG plus detailed Markdown format. Scope remains `e-commerce/diagram`, `tasks/todo.md`, `tasks/lessons.md`; delivery none. No repository baseline command is declared for this diagram-only scope.

Replanned 2026-11-08 after the owner's correction: revise all 15 views (the original three plus twelve supporting views). The initial supporting HTML/drawio drafts are superseded; no supporting PNG has been delivered. First research meanings, then model ownership/decomposition, then choose layout. Preserve current in-review policy and implementation boundaries.

- [x] Record the correction/root cause and inspect all existing drafts without discarding unrelated work.
- [x] Define a per-diagram semantics matrix backed by primary sources; distinguish structural, temporal, lifecycle, deployment, data and recovery viewpoints.
- [x] Rebuild architecture with nested Presentation/Application/Domain/Infrastructure/Shared layers and explicit Command/Query, Validator, Handler and ports; rebuild repository as nested packages and system as guarded lifecycle regions.
- [x] Rebuild supporting structural views with meaningful native parent/child boxes; revise sequence grouping/activation, collection field compartments and recovery lanes/gates using their own notation.
- [x] Synchronize all explanations and the index, render all 15 PNGs, inspect nesting/content/readability, validate native parent-child relationships, geometry and round trips, then hand off only verified results.

- [x] Verify and park PR 48, prepare the new managed assignment, read applicable rules/lessons and retain the owner's light/orange style.
- [x] Record the complete plan and per-view purpose before drawing; use A3 landscape 1584 x 1120. The correction supersedes the initial flat nine-node target: use zoned faithful decomposition (up to 24 responsibility leaves) and no more than five sequence lifelines/twelve messages per image. Split start-payment from checkout to keep uncertainty/recovery readable.
- [x] Research current local specifications and primary provider/data/operations sources; capture current-contract gaps separately from proposed recovery behavior.
- [x] Build commerce overview, checkout, start-payment, webhook, refund, outbox-delivery and config-publication views.
- [x] Build outbox lifecycle/contracts, MongoDB logical model, deployment/security, observability/SLO/capacity and backup/recovery views.
- [x] Write a detailed Thai Markdown companion per image with rationale, trade-offs, sources, acceptance scenarios and approval boundaries; link them through the readiness plan/README.
- [x] Render and visually inspect every final PNG; check geometry/text bounds, HTML, source parity, PNG metadata/editability and native round trips; keep final PNGs below 1 MiB.
- [x] Reconcile source baseline, review the full package, record verification/limitations and release the editing-session lock. No backend/API/schema implementation or PR is included in this authorization.

Verification (2026-11-08): All 15 views and companions are rebuilt using meaning-specific notation and native parent/child containment. Source/geometry, skill HTML checks, SVG export, 390px browser bounds, PNG CRC/extraction and native reopening/re-export checks pass. All PNGs are 2378 x 1682, below 1 MiB, visually reviewed, with exact source metadata and identical round-trip IDAT. Backend facts use manifest-pinned Component Repository d825518; no checkout migration or implementation was performed. Detailed evidence and unperformed runtime/load/restore tests are recorded in `e-commerce/diagram/verification.md`. No commit, push or PR is included.

### Owner refinement — reusable business logic in `Domain` (2026-11-08)

Resume the same assignment/branch; delivery remains none. Update only the architecture/repository views and their related documentation. Architecture remains logical layer decomposition, repository remains native package ownership; A3 landscape/light-orange style/faithful detail remain. Add one child per affected view, keeping 24 or fewer responsibility leaves. No backend files, tax formula, API or schema implementation is included.

- [x] Inspect the owner's naming/path, pinned source and existing diagrams; reacquire the existing assignment's editing-session lock without replacing its dirty files.
- [x] Add native `Domain` child for reusable business logic and `Authen/Domain/` path summary; preserve entity invariants, Application orchestration and all existing responsibilities.
- [x] Update explanations, semantic contract, index/readiness/verification and correction lesson with ownership, examples, dependencies and source status.
- [x] Generate/export both affected PNGs, review them, check HTML/bounds/editability/round trips, verify the other13 views remain unchanged, and release the session lock.

Refinement verification: two PNGs visually reviewed; native parent/source/IR and pixel-identical draw.io round trips pass. All15 source checks, two HTML/SVG checks, 390px text bounds, 27 Markdown frontmatters, 276 local links and scope/diff checks pass. Exactly15 paths refined; the other13 views (52 artifact files) are unchanged. Backend tests are not applicable to this diagram-only refinement.

### Deliver the completed 15-view package — direct owner grant

Ittikorn's current instruction, "เปิด pr มา", authorizes commit, push and one PR for this completed diagram package, including the Domain refinement. This supersedes delivery none for the same assignment, scope and branch only. The direct grant is persisted in ignored assignment metadata after registry/identity/scope validation. No implementation/design-policy approval or merge authority is inferred.

- [x] Load commit-and-pr formats/checklist, verify the same managed workspace and current origin/main registry, record the direct grant and acquire an editing-session lock.
- [x] Verify the 15-view artifacts/Markdown, select all80 task paths, run delivery preflight and inspect the staged diff.
- [ ] Commit once with the fixed format, verify merge compatibility, push the existing branch and open a PR against main.
- [ ] Inspect the PR status once, release the editing-session lock and hand off the PR for owner review.

PR preflight (2026-11-08): 80 paths (78 diagram files +2 task records), no deletions, managed delivery authorized, no blockers. All15 source/geometry checks and HTML checks pass; PNG dimensions/sizes/CRC/extraction/source XML and saved native round trips pass15/15. All27 Markdown frontmatters and276 local links pass. No backend/API/schema paths changed; runtime/provider/load/restore tests are outside this documentation-only delivery.

## e-commerce: Database-grounded domain model diagrams

Status: Complete on `docs/jinny-domain-model` after GitHub verified PR61 merged and agent-workspace parked the previous assignment. Scope: `e-commerce/diagram`, `tasks/todo.md`, `tasks/lessons.md`; delivery none. Existing diagram source checks passed as the prepare baseline; no repository-wide baseline is declared specifically for new diagram artifacts.

Purpose: model business concepts and evidenced relationships from all53 SQL tables in11schemas, rather than software layers, deployment or a copy of the physical ER diagram. Use diagram-design, the owner's light/orange style, A3 landscape and faithful nested detail. Split into `domain-model` overview plus `domain-identity-model` (21 tables), `domain-merchandising-model` (19) and `domain-commerce-model` (13). Detail pages use conceptual ER notation, business names, selected fields and cardinalities; grouping expresses schema/responsibility only, not approved DDD aggregate/transaction boundaries. Omit universal audit fields and secondary relationship lines from images but retain full table/FK traceability in Markdown/inventory. No schema, canonical ER, API or backend implementation changes.

- [x] Reconcile PR61, prepare a fresh scoped Jinny branch/lock, load applicable skills/rules/lessons and inspect the DB/schema inventory.
- [x] Read every migration/schema explanation and meaningful constraint; generate a source inventory and research the conceptual notation using primary sources.
- [x] Model the overview and three focused domain diagrams with native parent/child boxes, explicit selected associations and correct cardinality, separating evidence from inferred business ownership/rule candidates.
- [x] Produce editable PNG/drawio/HTML and detailed Thai companions; map all53 tables and foreign keys and link the index.
- [x] Verify source coverage, geometry/text/routes, HTML, Markdown, visual output and editable PNG/native round trips; record results and release the editing-session lock.

Verification (2026-11-08): four conceptual domain diagrams and detailed companions cover53SQLtables in11schemas and75FKcolumns. Detail drawings select35entity associations; overview selects7cross-schema references. SQL/schemaaudit reports53tables audited,0findings. Source/model/geometry, packagedHTML/SVG,390pxbrowserbounds, exact editablePNG extraction/nativeXML and pixel-identicalnative round trips pass; PNGs2378x1682 and below1MiB. All7Markdown frontmatters,311local links,23-pathscope andwhitespace checks pass. Prior45image/source/HTML artifacts remain unchanged. Full evidence and limits are in e-commerce/diagram/domain/domain-model-verification.md. No SQL/API/backend implementation or PR is included.

### Separate the Domain package and deliver its PR

The owner's current instruction "แยก folder แล้วเปิด pr ให้หน่อย" authorizes reorganizing this existing package into `e-commerce/diagram/domain/`, updating references/generator paths, committing, pushing the existing task branch and opening one PR against main. This supersedes delivery none for the same task/scope only; it does not authorize merging or backend/schema changes. The grant is persisted after registry/identity validation.

- [x] Verify the existing workspace/branch/assignment, record the direct delivery grant, reacquire the editing-session lock and snapshot the21Domain files before moving.
- [x] Move the complete Domain package into its own folder, add a local index and update generators/links/commands without changing diagram pixels or database evidence.
- [x] Recheck53-table/75-FK coverage, source/HTML/Markdown/PNG parity, old diagram preservation and delivery preflight; inspect the exact staged files.
- [ ] Commit one reviewed package, verify merge compatibility, push the existing branch, open/attach the PR and inspect its status once. Release the session lock after delivery; actual state is derived from Git/GitHub.

Delivery preparation:25files (22dedicatedDomain files, parentREADME, sharedPNGhelper andtaskrecord). Preflight hasno blockers; all4PNG/draw.io pairs andsourceinventory match pre-move SHA-256. All53tables/75FKs,4HTML/SVG checks,PNGIR/native roundtrips,8Markdown frontmatters,328local links andprior45artifact preservation pass. No backend/API/schema implementation; no excluded task files.

## repository-wide: Make agent instructions operational

Status: Complete

- [x] Audit `AGENTS.md`, `CLAUDE.md`, and referenced agent resources.
- [x] Resolve task artifact, loading order, active scope, approval evidence, new-spec planning, and placeholder-role decisions.
- [x] Create task tracking, lessons, and canonical terminology documents.
- [x] Align root instructions, rules, workflow, registry, and ready spec templates.
- [x] Verify frontmatter, resource references, parity, numbering, and instruction consistency.
- [x] Record the final verification result and mark this task complete.

Verification: All 32 governed Markdown files have valid required frontmatter; root instructions match apart from runtime-specific names; workflow numbering is 1–14; all required resources exist; scope and approval rules are consistent; `git diff --check` passes.

## repository-wide: Fill the data-modeling and api-contract-design skills

Status: Complete

- [x] Inspect the registry, the placeholder skills, the project templates, and the conventions used in the e-commerce schema and API work.
- [x] Write `data-modeling` (schema, migration, ER diagram, SQL tests) with references, templates, and scripts.
- [x] Write `api-contract-design` (upsert, batch, inquiry specs, checkers) with references, template, and a spec generator helper.
- [x] Register both skills as ready in `.agents/README.md`.
- [x] Test the scripts and validate the frontmatter of every new Markdown file.

Verification: both `SKILL.md` files and all seven references have valid frontmatter; `realign_tables.py`, `mutation_harness.py`, and `spec_helpers.py` were run against real inputs; `spec_helpers.py` output passes the checker's table and JSON checks. The skills have not been run against test prompts with a baseline.

## repository-wide: Write the commit-and-pr skill

Status: Complete

- [x] Ask the user which formats must be fixed, the language, the subject style, and how to treat files of other tasks.
- [x] Write `commit-and-pr` (Conventional Commits in English, fixed PR title and body, fixed chat summary, pre-send checklist) with references and `.tmpl` templates.
- [x] Write and test `scripts/preflight.py` (branch, files by area, secrets, large files, junk, `git diff --check`, optional project checkers).
- [x] Register the skill as ready in `.agents/README.md`.

Verification: `preflight.py` flagged every planted problem in a scratch repository (main branch, secret, private key, 1.2 MB file, build output, trailing whitespace) and passed a placeholder bearer token and a clean file; `--run-checks` ran 22 `check_docs.py` sub-commands, `audit_all.py` (0 findings) and `run_db_tests.sh` (ALL PASSED) on the real repository. The skill has not been run against test prompts with a baseline, and nothing was committed.

## repository-wide: Define independent Component Repository standard

Status: Complete

- [x] Inspect the current `e-commerce/repository/` ownership and references without moving files.
- [x] Decide the manifest-managed independent repository model, naming, revision, ignore, and migration boundaries.
- [x] Create the Component Repository rule, Repository Manifest template, bootstrap skill, ADR, and canonical glossary terms.
- [x] Register the new resources and update root structure, SDD implementation routing, and e-commerce migration status.
- [x] Validate the skill package, frontmatter, manifest contract, routing parity, references, and unchanged e-commerce backend layout.
- [x] Record verification and mark this task complete.

Verification: isolated forward tests covered a valid staged clone, a dirty existing checkout, a migration-pending Project, and a revision outside the declared default branch; declared targets and existing work were preserved and staging directories were cleaned. Ruby fallback validation passed for skill structure and YAML because the bundled Python validator could not import PyYAML. Root instruction parity, workflow numbering, registry entries, ADR, manifest fields, full-SHA and remote safety instructions, e-commerce migration state, and `git diff --check` all passed. No `e-commerce` backend file was moved and no nested Git metadata or `e-commerce/REPOS.md` was created.

## e-commerce: Master tables WP6 (product type, product brand, consent type)

Status: Complete, reviewed by the lead SA (gates 1 and 2), waiting for the product owner to merge the pull request

- [x] Write `docs/superpowers/specs/2026-11-06-master-tables-design.md` (decisions B1 to B14) and get the owner's answers on permission (Q1) and the foreign key change (Q4).
- [x] Write `db/tests/03-product-master.test.sql` and `db/tests/00-consent-type.test.sql` first and watch them fail on the old migrations.
- [x] Change migrations `00-common` and `03-product`: partial unique name indexes, `RESTRICT` on `m_product.type_id`, `m_product.brand_id` and `t_consent.consent_type_id`, with no `ALTER TABLE`.
- [x] Update the five schema docs and the ER diagram (the `UK name` rows of the three tables).
- [x] Write nine specs: `product/10` to `15` and `consent/06` to `08` (upsert, batch and inquiry; upsert and batch need `PLATFORM_ADMIN`).
- [x] Add the checkers `product-master-spec`, `product-master-schema`, `consent-type-spec`, `consent-type-schema` and mutation-test them.
- [x] Run every checker, the audit and the database tests after rebasing on `origin/main`.

Verification: `check_docs.py` 30 sub-commands OK, `audit_all.py` 52 tables 0 findings, `run_db_tests.sh` ALL PASSED. The new checkers caught 105 of 105 deliberate faults after the first run missed 6 and was tightened; the migrations caught 9 of 9. Tests 4 of the product file and 5 of the consent file were not seen failing before the migration change (the script stops at the first error of a file); their sharpness was shown by restoring `CASCADE`. ER pages Overview and All Tables were not looked at as pictures by the author; the lead looked at the Product page. Nothing was run against a real database beyond the throw-away test cluster.

## repository-wide: Select the minimum SDD agent set

Status: Complete

- [x] Map the roles and phase responsibilities required by `.agents/workflows/spec-driven-development.md`.
- [x] Inventory relevant candidates in `awesome-claude-code-subagents/categories`.
- [x] Compare the minimum candidate agents with the repository's existing agent files and terminology.
- [x] Present the recommended initial agent set, gaps, and decisions for user confirmation.
- [x] After confirmation, identify the exact content to adapt from each selected source file.
- [x] Adapt the six canonical SDD agent roles with `model: inherit` and explicit boundaries and handoffs.
- [x] Build the System Analyst as the specification, traceability, and SQL-analysis lead.
- [x] Add Security Auditor as an optional specialist for security-sensitive work.
- [x] Register the seven roles and document the optional security-review trigger in the SDD workflow.
- [x] Verify frontmatter, registry consistency, role boundaries, source-specific boilerplate removal, and clean Markdown diffs.

Verification: all seven selected agent files have valid YAML frontmatter, matching path/name, explicit tools, and `model: inherit`; every selected role is registered `ready`; imported context-manager protocols, fixed models, arbitrary thresholds, fake delivery metrics, and unselected agent dependencies are absent; the System Analyst includes project-backed PostgreSQL, transaction, constraint, index, and query-specification expertise while excluding DBA operations; `git diff --check` passes. The pre-existing unregistered agent copies were left untouched, and no build or runtime test was required for this documentation-only change.

## repository-wide: Add the pre-implementation OpenAPI role

Status: Complete

- [x] Remove unregistered agent copies that are outside the approved SDD team.
- [x] Adapt API Documenter to publish OpenAPI 3.1 from Approved API Specs into the project API contract.
- [x] Insert API Documenter between architecture approval and backend implementation.
- [x] Register API Documenter as ready and align System Analyst, Backend Developer, and Code Reviewer handoffs.
- [x] Verify frontmatter, registry and workflow consistency, JSON validity, preserved unrelated work, and clean Markdown diffs.

Verification: the eight selected Agent Roles have valid frontmatter, matching names and paths, `model: inherit`, and `ready` registry rows; the SDD workflow has nine sequential phases with API Documenter publishing the contract before implementation; System Analyst, Solution Architect, Backend Developer, and Code Reviewer handoffs reference OpenAPI consistently; `e-commerce/api/api-contract.json` parses as JSON; `git diff --check` passes. No semantic OpenAPI validator is configured in the repository, so the role reports semantic validation as unverified until a validator is available.
## e-commerce: Authentication WP4 (tokens, refresh, logout, reset password, profile, address)

Status: Complete, reviewed by the lead SA (gate 1, gate 2 and one re-check), waiting for the product owner to merge the pull request

- [x] Write `docs/superpowers/specs/2026-11-06-authen-design.md` (decisions U1 to U29) and get the owner's answers on token lifetime, login lock, logout scope, scope of work, field encryption and the unique indexes on delivered tables.
- [x] Write `db/tests/01-authen.test.sql` first and watch it fail on the old migration.
- [x] Change migration `01-authen` (up and down): `session_id` on both token tables, four partial unique indexes, the new log table `authen.l_user_login_attempt` (53 tables), with no `ALTER TABLE`.
- [x] Update seven schema docs, the README counts and the ER diagram (Common and Authen page and All Tables page).
- [x] Write eight specs `03` to `10` and change `01-register` and `02-login` (plain text over TLS, session and token rows, login lock, token lifetime, default address).
- [x] Add the checkers `authen-spec` and `authen-schema`, extend `audit_all.py` to plain indexes, and mutation-test them.
- [x] Run every checker, the audit and the database tests after rebasing on `origin/main`.

Verification: 45 of 45 `check_docs.py` sub-commands OK, `api-sequence-spec` OK (83 specs, product 5/15 and shop 5/16 filled), audit 53 tables 0 findings, database tests ALL PASSED. `test_sequence_skeleton.py` fails on `main` already (the test compares the block order of the hand-written diagrams with the skeleton; 4 files of `main` and now also `product/02` and `shop/04`, where blocks run in the order of the work); the test is outside this assignment and the lead is told. The authen checkers caught 120 of 120 deliberate faults and the migration 10 of 10 according to the author; the lead did not rerun them. Tests 2 to 6 of the SQL file were not seen failing before the migration change (the script stops at the first error of a file); their sharpness was shown by deliberate migration faults. Nothing was run against a backend or a real database; the existing backend differs from the specs in endpoint paths and token lifetime, as written in the design document.

## e-commerce: Shipping domain (WP3)

Status: Complete (PR #10 merged into `main` at `85e64de` on 2026-11-06); S3 was answered by the product owner (7 days, reported by the lead SA) and is written up in WP3b below

- [x] Read the shop-domain hand-off, roadmap WP3, order design R38–R50, migrations 06 and 08, schema docs, sales specs, and the data-modeling and api-contract-design skills.
- [x] Ask the product owner the business questions and agree the payment contract with the lead SA.
- [x] Write `docs/superpowers/specs/2026-11-06-shipping-design.md` (round 1) and get the product owner's approval.
- [x] Round 2: `08-shipping.test.sql` red then green, migration 08, schema docs, README, ER diagram pages 6 and 8 rendered and viewed.
- [x] Round 2: six specs in `e-commerce/doc/api/shipping/` and the `shipping-schema` and `shipping-spec` checkers, mutation-tested.
- [x] Rebase onto `main` after the payment work, pass the lead SA's gate 2, commit and open the PR with the `commit-and-pr` skill.
- [x] S17 to S22 (decisions added during round 2) decided by the lead SA on 2026-11-06 (technical details, not an owner approval).
- [x] Product owner answers S3: an order completes by itself 7 days after `shipped_at` when the customer does not confirm (config, reported by the lead SA on 2026-11-06).

Verification: `check_docs.py` 26/26 OK, `audit_all.py` 52 tables 0 findings, `run_db_tests.sh` ALL PASSED. Checkers were mutation-tested on a copy of the merged tree: spec 58/58, schema doc, README and ER 8/8, migration 10/10 through the checker and 10/10 through `run_db_tests.sh`, audit 8/8 (the audit run was before the last rebase). No backend was run against the specs.

## e-commerce: Campaign and discount (WP7)

Status: Round 2 done, reported to the lead SA for gate 2 (round 1 approved by the product owner on 2026-11-06 at 13:00:05Z); not committed

- [x] Round 1: `docs/superpowers/specs/2026-11-06-campaign-design.md` with decisions C1 to C16 and proposals E1 to E8.
- [x] `09-campaign.test.sql` extended to tests 1 to 11 and red before the migration change (`column "remaining" ... does not exist`), green after.
- [x] Migration 09 edited in place (period check, unique name, `remaining`, ledger `entry_type` and `order_id`, product target check, partial unique indexes, discount checks); schema docs, README counts, ER pages 7 and 8 rendered and viewed.
- [x] Three specs in `e-commerce/doc/api/campaign/`: upsert campaign, inquiry campaign, inquiry campaign ledger.
- [x] `campaign-schema` and `campaign-spec` checkers added before `def main` in `check_docs.py`.
- [x] E1 to E7 in the delivered specs: `sales/01`, `sales/02` (discount rules, budget reservation, lot order by `id`, campaign examples), `sales/05`, `payment/05`, `payment/02` (budget release), `shop/08–09`, `product/01`, `03`, `04`, `06` (delete blocked while in a running campaign); `order-spec` changed on purpose for the discount examples.
- [x] Mutation-test the new and the changed checkers with deliberate mistakes (campaign-schema, campaign-spec, order-spec): spec 48/48 (includes the delivered-spec effects and 5 order-spec cases), doc, README, ER and test file 8/8, migration through the checker 11/11 and through `run_db_tests.sh` 11/11 (10/11 first, SQL test 6 was tightened for an INACTIVE budget), audit 10/11 (the miss is an audit limitation, covered by a needle).
- [x] Full run after the mutation work: every `check_docs.py` sub-command OK, `audit_all.py` 0 findings, `run_db_tests.sh` ALL PASSED (preflight with `--run-checks`); the ER file did not change after it was rendered and viewed.
- [x] Report gate 2 to the lead SA (new WP7 files separate from the delivered files that were edited).
- [x] Gate 2 result: passed with one fix (an example where the cap cuts a `FIXED_AMOUNT` discount): `sales/02` now has the Discount Example table and `Success - With Capped Discount`, `campaign-spec` checks the cap and the profits, 8/8 deliberate mistakes caught.
- [ ] Wait for the lead SA to say that PR #12 is merged, then fetch and rebase once (no rebase before that), and wait for the owner's order to commit.

Verification: `preflight.py --base main --run-checks`: `check_docs.py` 28/28 OK, `audit_all.py` 52 tables 0 findings, `run_db_tests.sh` ALL PASSED (tests 1 to 11 of `09-campaign.test.sql`), no blockers. No backend was run against the specs.

## e-commerce: Shipping automatic completion (WP3b)

Status: Round 2 done and reported to the lead SA for gate 2 (gate 1 passed on 2026-11-07 with two fixes, both done); not committed. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `feat/tommy-shipping-auto-complete`.

- [x] Prepare the managed workspace (registry scope of `tommy` widened by PR #18; baseline `audit_all.py` 0 findings and `run_db_tests.sh` ALL PASSED).
- [x] Appendix S23 to S32 in `docs/superpowers/specs/2026-11-06-shipping-design.md` (eligibility, stuck partial shipment, effect on the rows, lock order and clashes, where the rule is written, the scan index, the `deliveredAt` wording); C17 to C22 of the campaign design relabelled as decided by the lead SA.
- [x] Gate 1 fixes: the partial index `ix_t_shipping_shipped_at` (S31, SQL test 7 red then green, migration 08, schema doc) and `deliveredAt` as "the customer or the system confirmed" in `shipping/04`, `05`, `06` (S32).
- [x] Spec `shipping/06`: Automatic Completion Rules, the Automatic Completion Example (7 cases) and three queries; the seven days are inclusive (a shipping that is exactly 7 days old qualifies).
- [x] Checkers: `shipping-spec` (needles, `deliveredAt` wording, the example is judged again with the five conditions) and `shipping-schema` (the index, test 7); mutation-tested with deliberate mistakes.
- [x] Run every `check_docs.py` sub-command, `audit_all.py` and `run_db_tests.sh`.
- [x] Gate 2 fix (lead SA, 2026-11-07): the scan query of the job now applies conditions 1, 2, 4 and 5 (a dead-end order no longer fills the batch and starves the others); S26, the rules, the example text and the checker `check_shipping_scan_query` (12 mutations caught) are updated.
- [ ] Gate 2 result of the fix: the lead SA reads the short result; then merge the current `main` into the branch, commit and open the PR with `commit-and-pr` from `.workspace/tommy` (delivery is authorized), without merging.

Verification: see the gate 2 report; mutation tests on a copy of the tree: spec 30/30, schema doc and test file 3/3, migration through the checker 4/4 and through `run_db_tests.sh` 4/4. No backend was run against the specs.

## repository-wide: Add named-agent workspace lifecycle

Status: Complete

- [x] Persist the user-approved named-agent workspace design and its approval evidence.
- [x] Add the named-agent rule, canonical team registry, workspace ignore, and matching Codex/Claude routing.
- [x] Implement the `agent-workspace` skill and deterministic lifecycle script.
- [x] Add isolated tests for registry authority, path safety, locking, clone preparation, and merged-PR parking.
- [x] Align `commit-and-pr` and supersede the conflicting dated team protocol without changing merge authority.
- [x] Validate skill structure, Markdown frontmatter, routing parity, registry references, script behavior, and diffs.
- [x] Record verification evidence and mark this task complete.

Verification: `python3 -B -m unittest discover -s .agents/skills/agent-workspace/tests -v` passed all 12 tests, covering registry authority from `origin/main`, scope-bound delivery preflight, cleared-marker bypass prevention, symlink and linked-worktree rejection, execution locking, baseline contamination, open PRs on any base, cross-repository PR rejection, clone preparation, and squash-merge parking while preserving the remote branch. Independent forward review found no remaining P1/P2 issues. Team registry YAML, 11 modified Markdown frontmatters, and `AGENTS.md`/`CLAUDE.md` parity passed. `git diff --check` passed. The bundled `quick_validate.py` could not start because PyYAML is not installed; an equivalent Ruby YAML fallback passed its frontmatter, allowed-key, naming, description, and unfinished-placeholder checks.

## e-commerce: WP5 author permissions (5a, 5b, 5c)

Status: 5a complete and rebased on the current `main`, waiting for gate 2 of the lead SA; 5b is deferred and 5c is planned (the product owner told the lead SA to stop after 5a until he gives the next order)

Governing spec: `docs/superpowers/specs/2026-11-06-author-design.md` (approved by the product owner through the lead SA, 2026-11-06). Worktree `.claude/worktrees/author`, branch `feat/author-permissions`.

5a (now): role, permission, scope, user role, me, seed

- [x] Write `db/tests/02-author.test.sql` and `db/tests/02-author-seed.test.sql`, run them against the old migration and see them fail.
- [x] Change `02-author.schema.up.sql` (partial unique names and pairs, role scope points at the permission scope, `t_user_permission.permission_scope_id`, `RESTRICT` to the master tables) until `run_db_tests.sh` prints `ALL PASSED`.
- [x] Write `e-commerce/db/seed/author.seed.sql` (role `PLATFORM_ADMIN`, scopes, permission list; idempotent, creates no user) and `grant-platform-admin.sql` (first administrator by `userId`, only when no ACTIVE holder exists).
- [x] Update the 8 schema docs, the README (`t_user_permission` 9 columns and 3 foreign keys), the ER diagram (rendered and looked at), and record the `seed` folder in `e-commerce/doc/schema/README.md`.
- [x] Write specs `author/01`–`12` (role, permission, scope: upsert, batch, inquiry; user role: upsert, inquiry; me).
- [x] Add `author-spec` and `author-schema` to `check_docs.py` before `def main` and mutation-test them (every deliberate mistake caught).
- [x] Run every `check_docs.py` sub-command, `audit_all.py` (0 findings) and `run_db_tests.sh`; send the gate 2 report to the lead SA.

Verification: on `main` at 553c8f4 plus this change: all 34 `check_docs.py` sub-commands OK, `audit_all.py` 53 tables 0 findings, `run_db_tests.sh` ALL PASSED (including `02-author` 6 tests and `02-author-seed` 4 tests). Deliberate mistakes: 142 of 142 caught by the two new checkers (including the grant-only ACTIVE rule of the user role spec), 15 of 15 caught through the SQL tests (migration, seed and grant script). The first administrator command was tested one after another, not with two sessions at the same time.

## e-commerce: WP5b author permission assignment (deferred)

Status: Deferred until an API enforces permissions (product owner chose the small scope, 2026-11-06)

- [ ] Specs `13`–`17`: role permission (upsert, inquiry), user permission (upsert, inquiry), check. The schema of these tables is already changed in 5a.

Verification: not started

## e-commerce: WP5c admin-only writes for delivered master data APIs

Status: Implemented and committed locally by the author (commit 05c7d4a in her managed workspace); the push was refused by the permission system of her session, so there is no pull request yet. Gate 2 of the lead is open. The lead wrote this section from the author's report because her assignment scope was `e-commerce` only.

- [x] Read the nine specs on `main` (with the WP7 changes of `product/01`, `03`, `04`, `06`) and find the checkers that cover them.
- [x] Add the `PLATFORM_ADMIN` rule, the 403 example and the two permission queries to `shop/05`, `06`, `product/01`, `03`, `04`, `06`, `07`, `09` and `consent/02`, and the two queries to the `consent/02` sequence diagram.
- [x] Add the checker `admin-write-spec`, narrow the leftover-word rule of `shop-type-spec`, and mutation-test every change (the author reports 150 of 150 caught).
- [x] Run every checker, `audit_all.py` and `run_db_tests.sh` (the author reports 38 of 38, 0 findings, ALL PASSED).
- [ ] Gate 2 of the lead, then push and open the pull request.

Verification: the numbers above are the author's; the lead has not rerun them yet.

## e-commerce: Payment WP2 (Stripe)

Status: Complete, merged in pull request 8

- [x] Write `docs/superpowers/specs/2026-11-06-payment-design.md` (rules R51 to R72) after the owner chose Stripe.
- [x] Write `db/tests/07-payment.test.sql` and change migration `07-payment` (provider, shipping method and fee, failure and refund columns, one live payment per order, `RESTRICT` on `order_id`).
- [x] Update the schema doc, the README and the ER diagram (pages 6 and 8).
- [x] Write five specs `payment/01` to `05` (start, Stripe webhook, inquiry for the customer and the shop, refund) and change `sales/01`, `sales/02`, `sales/05`.
- [x] Add the checkers `payment-spec` and `payment-schema` and mutation-test them.

Verification: when the pull request was opened `check_docs.py` passed 24 of 24, `audit_all.py` had 0 findings and `run_db_tests.sh` printed ALL PASSED. Nothing was run against Stripe; the Stripe event name for refunds and the THB 10 minimum are not confirmed against the Stripe reference.

## e-commerce: Lead review of the SA work packages

Status: In progress. Merged after the lead's review: WP3 shipping (pull request 10), WP6 master tables (11), WP4 authen (12), WP7 campaign (15), WP5 step 5a (17) and step 5c (20). Open work: WP3b (Tommy; gate 1 passed on 2026-11-07, round 2 in progress).

- [x] Review gate 1 and gate 2 of WP3, WP6, WP4, WP7 and WP5 5a and 5c, run the checkers in each analyst's tree and read the changed specs.
- [x] Fix the first team protocol so that the analysts write `tasks/todo.md` and `tasks/lessons.md` as `CLAUDE.md` requires.
- [x] Move the analysts' assignments to managed workspaces and widen the registry scope of tommy and marry (pull request 18) after the named-agent rule was merged.
- [x] Decide the 409 of `01-register` (owner on 2026-11-07: "เลือกให้เลย", the choice is the lead's). Decision: keep the 409 with its single message that does not say whether the username or the email exists, no change to the spec. Why: there is no email verification, so a neutral answer would leave a real user without a way to know why registration failed; the login answer is already the same for every failure and the lock limits guessing. Cost if wrong: add email verification and answer every registration the same way, which is a new work package. The registration rate limit belongs to the gateway and is not specified.
- [x] First platform administrator (owner on 2026-11-07, answered the lead's recommendation that the system operator runs `grant-platform-admin.sql` after confirming the user id: "แค่เก็บ data ไว้ เดี๋ยว dba มา export ให้การเงิน"). The lead reads this as: the database administrator is the system operator who runs the command, and the data is only stored, with no API for finance because the DBA exports it directly. This reading is not confirmed by the owner. Nothing in the specs changes.
- [ ] Review gate 2 of WP3b.
- [ ] Backlog for the owner's order: merge the two `er_name_rows` helpers of `check_docs.py` (check first that the API review did not already do it), extend `audit_all.py` to a column without an alias in the `WHERE` of an `UPDATE`, retrofit the plain `UNIQUE` and `CASCADE` of the older master tables, rewrite the team protocol in `docs/handoff/` to match the named-agent rule. Decided elsewhere: JWT claims are the authorization source (owner with Peter, 2026-11-07).

Verification: each gate was checked by running every `check_docs.py` sub-command, `audit_all.py` and `run_db_tests.sh` in the analyst's tree and by reading the changed specs. The analysts' own mutation tests were not rerun by the lead.


## repository-wide: Register Peter for the e-commerce API review

Status: Complete. PR #21 merged into origin/main at eee8add on 2026-11-07 (Asia/Bangkok); Peter's full managed clone was created and the first login assignment prepared through agent-workspace.

- [x] Read the bootstrap, global rules, team registry, named-agent workspace design, lessons, and delivery skill.
- [x] Confirm the owner chose to register Peter and retain the existing lifecycle rather than allow concurrent API pull requests.
- [x] Register Peter as an enabled System Analyst with the same repository-wide registry scope as the existing team, reporting to Josh, without delegation capabilities; bound actual assignments to e-commerce and required task bookkeeping.
- [x] Validate registry parsing and role/scope consistency, run the existing workspace tests and delivery preflight, and review the exact diff.
- [x] Prepare the commit and registration PR package using commit-and-pr; keep API changes out of this prerequisite PR.
- [x] After the owner merges registration into origin/main, create Peter's managed workspace with agent-workspace and record the bounded first-API assignment before edits.

Verification: The canonical registry test failed before adding Peter (expected four entries, found three). After registration, `python3 -B -m unittest discover -s .agents/skills/agent-workspace/tests -v` passed all 12 tests, including Peter's direct-user delivery authorization and inability to delegate. `preflight.py --base main` reported three in-scope files and no blockers; `git diff --check` passed. API/database tests were not rerun for this registry-only change. Registration takes effect only after merge into origin/main. The initial one-open-PR rule was superseded for this review by the owner's Q15 instruction; completed API PRs may stay open while Peter starts the next branch from main. Each API delivery will contain its spec.md and complete sequence.wsd, with the verification changes required for that API.


## e-commerce: Peter API review — login (API 1)

Status: Login artifacts verified and ready for one-API PR delivery. Owner confirmed Q1–Q13 and the additional Q14 ambiguity rule in this chat on 2026-11-07. Governing decisions are recorded in `docs/superpowers/specs/2026-11-07-api-review-design.md`; detailed endpoint changes remain in-review until reviewed. Assignment: Peter, System Analyst, delivery open-pr, authorized directly by ittikorn; branch `fix/peter-login-contract` in `.workspace/peter`.

- [x] Read all 30 APIs (60 files), identify SQL/sequence/approval contradictions, and settle the JWT and consent behavior with the owner.
- [x] Verify PR #21 merged, create Peter's managed clone, and prepare the bounded login assignment with the declared baseline checks.
- [x] Persist the exact owner-approved decisions and scope; reconcile superseded A16/A18 and token-design statements without marking detailed endpoint work approved.
- [x] Correct login SQL and specify the role/permission-specific scope payload, password verification, lock order, counter and transaction behavior.
- [x] Rewrite sequence.wsd with success, validation, REFUSED, FAILED, rollback and timeout branches and exact table-bound SQL.
- [x] Extend SQL/sequence and login-behavior checks; prove the old defects fail and mutation-test the changed checker.
- [x] Run every documentation check, SQL audit and database test; verify source structure and review the exact diff.
- [x] Prepare the one-login-API commit-and-pr package; verify actual PR/lock state through GitHub and agent-workspace during delivery.
- [x] Verify login PR #23 merged, park the completed workspace and prepare refresh as a fresh assignment. Subsequent APIs follow the owner's newer continue-without-merge instruction below.

Baseline: all 37 documentation subcommands passed, audit reported 53 tables and 0 findings, and database tests reported ALL PASSED during agent-workspace prepare. The initial PATH-only Java probe failed; the paired-review follow-up below discovered the installed OpenJDK and PlantUML JAR and records completed rendering verification.

Queue after login: refresh, then the remaining original 30 APIs and the additional APIs affected by JWT authorization. Each API owns one PR; after opening it, owner decision Q15 permits the next editing assignment from current main without waiting for merge. The existing registration worktree was retained because Codex's archive tool refused to remove the chat's primary checkout; Peter's API edits use only his managed full clone.

Login verification evidence: the new login-flow check rejected the old files before correction. Final mutation run caught 56/56 deliberate faults (the first 53-case run caught 48/53; selectors and projection/threshold checks were tightened before rerunning). The SQL and sequence now contain 15 exact operations and seven outcome paths. The delivery preflight ran 38/38 documentation checks, audited 53 tables with 0 findings, ran database tests with ALL PASSED, and found no blockers. PostgreSQL verification executed the specification's exact queries against adversarial role/direct-scope fixtures, empty arrays and ambiguous identifiers, proved token/attempt rollback, and used two connections to verify serialized counting. No backend or published OpenAPI was changed; the detailed login and revised WP4/WP5 documents remain in-review, while the separate owner-decision record is approved. The initial delivery did not render PlantUML; the paired-review follow-up below now records real rendering and visible-SQL verification.


### Login PR #23 — paired sequence/spec review follow-up

Status: Paired-review artifacts verified and ready for the existing PR update, resumed through agent-workspace with the original login assignment after the owner's 2026-11-07 correction. GitHub reported the PR OPEN when verified; no next API assignment has started.

- [x] Verify the PR changes both spec.md and sequence.wsd and rerun SQL parity and seven-path flow checks.
- [x] Find installed OpenJDK and the VS Code PlantUML JAR rather than treating the system Java launcher as proof that no runtime exists.
- [x] Render the source and reproduce that PlantUML omits SQL value lines beginning with a single quote, despite passing source parity.
- [x] Preserve all quoted SQL values in the rendered diagram and make decoded SQL parity and application/infrastructure exchanges explicit.
- [x] Add a scenario correspondence table and strengthen mutation checks for rendered SQL and request/result handoff gaps.
- [x] Render SVG/PNG, inspect the complete diagram and critical SQL/branch regions, and run paired source/flow/rendered-text checks.
- [x] Prepare the existing PR update with the observed before/after evidence; verify final delivery through GitHub and release the session lock.


Paired-review evidence: PlantUML -syntax reports SEQUENCE (19 participants); SVG and PNG were generated and visually inspected. The original SVG is rejected for missing 15/113 SQL lines; the corrected SVG has 113/113 visible SQL lines. Exact decoded SQL parity passes for the 18 existing source pairs, and login-flow verifies the seven outcomes plus all query requests/results, parameter mappings and four success fields. Mutation testing caught 67/67 faults. The complete preflight reran all 38 documentation commands, audited 53 tables with 0 findings and passed database tests; its first attempt also flagged an extra blank line at the end of this task file, which was removed before final delivery.


PR #23 integration: origin/main advanced to 01a5e41 with the already merged Jinny registration (#22) and administrator-write spec retrofit (#20). Reconcile this base into Peter's existing branch without force-pushing; preserve both login-flow and admin-write-spec in the checker. Verify the PR diff against the current main contains only Peter's recorded assignment paths, rerun all current checks and rendered SQL verification, then push the reconciliation commit and release the session lock. Imported main changes are base history, not additional APIs authored in this PR.

Integration verification: both checker registrations are present, all 39 documentation commands pass, the audit reports 53 tables / 0 findings, database tests report ALL PASSED, login mutations remain 67/67, and the rendered SVG still contains 113/113 SQL lines. The working-tree PR diff against the updated main was checked before the reconciliation commit: all eight changed paths match Peter's original assignment.


## e-commerce: Peter API review — refresh token (API 2)

Status: In progress. Login PR #23 merged at 9ae6b6d; branch `fix/peter-refresh-token-contract` was prepared in Peter's managed clone with all 39 baseline documentation commands, audit and database tests. Direct delivery authorization remains ittikorn.

Owner delivery override (2026-11-07): “เสร็จแล้วเปิด pr ทิ้งไว้เดียวฉันมาอ่าน ไม่ต้องรอ merge switch ไปที่ main แล้วเกิด brach ใหม่ได้เลย”. This supersedes the earlier one-open-PR/wait-for-merge choice and skill defaults for this API review. Finish each API, open its own PR, preserve the branch/assignment for review, return to updated main and begin the next API immediately. Keep explicit scope, one active editing session, clean transitions and no force pushes or PR merging. Do not ask again whether to continue after opening a PR.

- [x] Verify/park merged login, read refresh spec and sequence together, and prepare the scoped refresh assignment with passing baselines.
- [x] Persist the superseding delivery decision and capture the workflow lesson without changing unrelated team capabilities.
- [x] Correct refresh ownership lookup, user-first lock, post-lock token reread/time capture, single-use update, fresh claims and distinct old/new token hashes.
- [x] Rewrite sequence with every request/result, SQL, rotation, recent duplicate, older replay, invalid/expired/inactive, rollback and timeout outcome.
- [x] Add paired flow/SQL/render checks and mutation-test them; validate concurrent refresh/replay SQL in temporary PostgreSQL.
- [x] Render and inspect SVG/PNG; pass all documentation commands, audit, database tests and preflight.
- [x] Prepare the refresh-only commit-and-pr package with paired verification evidence and owner decision Q15. After opening, preserve its branch/assignment record and continue immediately on main; actual delivery state is verified through GitHub and the local history record.

Refresh verification so far: the old spec/sequence pair is rejected by refresh-flow. The corrected pair has 16 exact SQL operations, 10 outcome paths and 128/128 SQL lines visible in the rendered SVG. Mutations caught 44/44 (43/44 initially; the consume ownership check was tightened to require the WHERE user_id predicate rather than merely seeing userId in updated_by). Temporary PostgreSQL checks passed concurrent post-lock reread/recent duplicate, newly assigned role reads, single-use consume, older replay revoking both tables while preserving other sessions/users, atomic rollback, inactive user and expiry while waiting for the user lock.

Refresh delivery verification: preflight ran 40/40 documentation checks, audit 53 tables / 0 findings and database tests ALL PASSED. Its first run flagged a bytecode file generated by the temporary builder; only that generated file was removed, and all six intended task paths then passed. PlantUML syntax reports 17 participants; SVG/PNG were rendered and inspected, and refresh-flow confirms 128/128 visible SQL lines and ten outcome paths. No backend implementation or schema changes are included.

## e-commerce: Sequence phase 0 — api-sequence-spec checker for all 83 specs

Status: Implemented in the managed workspace of Marry on branch `feat/marry-sequence-checker`; the pull request is opened after the preflight and merged by the lead, not by the author. Scope: `e-commerce/db/tests/check_docs.py` and `tasks/`. No spec and no `sequence.wsd` is changed.

- [x] Remove the fixed list of 18 specs and the fixed list of directories; check every spec folder under `e-commerce/doc/api` and require a `sequence.wsd` in each of them.
- [x] For every non-empty `sequence.wsd`: the SQL is identical to the spec, the lifecycle (activate, note, return, deactivate) is complete and the database participants are in the order of the spec.
- [x] Add `REQUIRED_GROUPS` (`authen-and-author`, `consent`) that must have no empty file; other groups may be empty (pending) and the output prints filled/total per group.
- [x] Add the structure check modelled on `02-login`: `@startuml`, title, `skinparam` Sarabun, `hide footbox`, actor `User`, boxes Frontend / Web API / Database, participant chain API -> Application -> Domain -> Infrastructure, the handler line and no `TODO(author)` marker.
- [x] Add the login standard for every spec with INSERT, UPDATE or DELETE (BEGIN, COMMIT, ROLLBACK, HTTP 400 `E10001`, HTTP 408 `E90001`, HTTP 500) with the explicit named list `LEGACY_SEQUENCES` for the 10 diagrams that do not follow it yet.
- [x] Mutation-test the checker: 35 cases of `mutation_harness.py` and 10 special cases (empty file, only blanks, missing file, pending group, moved BEGIN, moved COMMIT, TODO marker).
- [x] Run every `check_docs.py` sub-command (40), `audit_all.py` and `run_db_tests.sh`.
- [x] Preflight, commit, push, open the pull request (PR #27), tell the lead.
- [x] Lead review of PR #27, fix 1: a locking statement (`FOR UPDATE`, `pg_advisory_xact_lock`) must come after BEGIN.
- [x] Lead review of PR #27, fix 2: every `HTTP 4xx/5xx` answer after the first BEGIN follows ROLLBACK or COMMIT in its own block (by indentation, so the ROLLBACK of a sibling branch does not count).
- [x] Lead review of PR #27, fix 3: fail when no spec is found or a required group has no spec; mutation-test the three fixes and rerun every check.
- [ ] Push the fixes to the same branch, tell the lead; hold the lock until the merge, then release and park.

Verification: `api-sequence-spec` prints `OK: api-sequence-spec (83 specs; ... 10 legacy without the login standard)`; harness 35 of 35 caught; special cases 10 of 10 as expected after the BEGIN case was rebuilt (see the lesson of 2026-11-07); 40 of 40 sub-commands OK; audit 53 tables, 0 findings; database tests ALL PASSED.

## repository-wide: Sequence phase 0, generator side (`sequence_skeleton.py`)

Status: Complete in the branch, waiting for gate review. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh` (the product owner ordered phase 0 and the split of the work), workspace `.workspace/tommy`, branch `feat/tommy-sequence-skeleton-generator`, scope `.agents/skills/api-contract-design` and `tasks`. Marry owns the checker side (`check_docs.py`, PR 27 merged).

- [x] Read the login and consent diagrams and `spec_database_operations` / `sequence_database_operations` of `check_docs.py`.
- [x] Write `.agents/skills/api-contract-design/scripts/sequence_skeleton.py` (stdout, `--write`, `--force`, refuses a file with content).
- [x] Write `scripts/test_sequence_skeleton.py`: all 83 specs through the parser and the structure and login-standard checks of `check_docs.py`, the 18 hand-written diagrams against the generated database blocks and participants, the command line.
- [x] Mutation-test the script with `mutation_harness.py` (24 cases) and parse every skeleton with PlantUML.
- [x] Update `SKILL.md` and `references/api-conventions.md` (no empty `sequence.wsd`: generator, checker, no `TODO(author)` left).
- [x] Run the project checkers and open the PR with `commit-and-pr`; do not merge.

Verification: see the PR. Not run: the script was not used to fill the 65 empty diagrams (that is the next step of phase 0 and changes `e-commerce/doc/api`, outside this scope).

## e-commerce: api-sequence-spec accepts the blocks of a diagram in any order

Status: Implemented in the managed workspace of Marry on branch `feat/marry-sequence-any-order`; the pull request is opened after the preflight and merged by the lead, not by the author. Scope: `e-commerce/db/tests/check_docs.py`, `.agents/skills/api-contract-design/references/api-conventions.md` and `tasks/`. No spec, no `sequence.wsd` and no `sequence_skeleton.py` is changed. Decision of the lead (owner order): most specs order the SQL by table, not by execution (for example `sales/05-cancel-order` checks the shop permission after the UPDATE in the document, but runs it before), so the checker stops forcing the order of the spec instead of reordering 65 specs that the API review is working on. If wrong: force the order again and reorder the specs.

- [x] Prepare the workspace from `main` (e132139) with the baseline `check_docs.py api-sequence-spec`; the first prepare recorded the three scope paths as one string, so the assignment record was reset with the approval of the lead and prepared again with three `--scope` flags.
- [x] Every interaction of a diagram must be a block of the spec: table, heading and normalized SQL all equal; an interaction that is not in the spec fails.
- [x] Every block of the spec must appear at least once, in any order, and may repeat in several branches; two blocks with the same table and heading are matched by their full SQL and the report says which one is missing.
- [x] Database participants: the tables of the spec, declared in the order of first use in the diagram (missing, extra, declared twice and wrong order are separate messages).
- [x] Keep the earlier rules: lifecycle, structure, `TODO(author)`, BEGIN before a write or a lock, ROLLBACK or COMMIT before an error answer, `LEGACY_SEQUENCES`, `REQUIRED_GROUPS`.
- [x] Update `api-conventions.md` (intro and steps 1 and 2 of the sequence section): move blocks to the order of the work and into every branch that needs them, and move the participants with them.
- [x] Mutation and control tests: 35 cases of `mutation_harness.py` and 14 cases on `02-login` plus 4 direct cases for the same-heading rule.
- [x] Run every `check_docs.py` sub-command (40), `audit_all.py`, `run_db_tests.sh` and `test_sequence_skeleton.py`; 65 skeletons from the generator are checked on a copy.
- [ ] Preflight, commit, push, open the pull request, tell the lead; hold the lock until the merge, then release and park.

Verification: `api-sequence-spec` prints `OK: api-sequence-spec (83 specs; ... 10 legacy without the login standard)`; the 18 diagrams of the earlier round pass; on a copy of the repository the 65 skeletons of the generator fail only with `TODO(author)` (0 other errors); harness 35 of 35 caught; on `02-login` these fail as they must: a block removed, one letter of the SQL changed, an extra block with a new heading, an extra block with the same heading and other SQL, a changed heading, a participant missing, an extra participant, a participant declared twice, participants in the wrong order, two blocks swapped with the participants left in the old order, a write moved before BEGIN; these pass as they must: two blocks swapped together with their participants, one block repeated right after itself, one block repeated in another branch; 40 of 40 sub-commands OK; audit 53 tables, 0 findings; database tests ALL PASSED; `test_sequence_skeleton.py` 11 tests OK.

## repository-wide: agent_workspace.py rejects a comma in --scope

Status: Implemented in the managed workspace of Marry on branch `fix/marry-reject-comma-scope`; the pull request is opened after the preflight and merged by the lead. Scope: `.agents/skills/agent-workspace` and `tasks/`. Reason: a `--scope "a,b,c"` was recorded as one path and blocked the next `prepare` (see the lesson of 2026-11-07 about repeated options).

- [x] `normalize_scopes` blocks any value with a comma, before the lock, the branch and the metadata, and says to repeat `--scope` once per path with an example.
- [x] Two tests in `test_agent_workspace.py`: a comma (alone or in one of several values) blocks and leaves no branch and no `.state` file; separate `--scope` flags are recorded one by one.
- [x] One sentence in `SKILL.md` next to the `prepare` example.
- [x] Mutation tests: 7 of 7 caught (check removed, only the first value checked, only `", "` checked, message without the instruction, message without the example, scopes collapsed into one, comma accepted as one scope).
- [ ] Preflight, commit, push, open the pull request, tell the lead; hold the lock until the merge, then release and park.

Verification: `python3 .agents/skills/agent-workspace/tests/test_agent_workspace.py` runs 15 tests OK (13 before).


## e-commerce: Peter API review — register (API 3)

Owner Q15 supersedes the earlier one-open-PR lifecycle: keep completed PRs open, preserve each branch/assignment history, return to main and begin the next API without waiting for merge. PR #23 is merged; refresh PR #24 was preserved separately and subsequently merged before register delivery. Register uses a fresh bounded assignment on fix/peter-register-contract.

- [x] Verify clean main, preserve PR #24 and its assignment, and prepare register with all baseline checks.
- [x] Read register spec/sequence, consent submission, migration/schema and prior lessons.
- [x] Persist Q16 display/read semantics and settle explicit consent-version handling.
- [x] Correct register validation, required consent coverage, optional writes and atomic transaction in spec.md and complete sequence.wsd.
- [x] Add register-flow invariants and mutation-test old failures, branching and rendered SQL.
- [x] Execute exact SQL against temporary PostgreSQL, render and inspect SVG/PNG, then run all documentation checks, audit, database tests and delivery preflight.
- [x] Deliver one-register-API PR with commit-and-pr; release editing lock and continue from main under Q15.

Register verification: the original pair fails register-flow; the revised pair has ten identical SQL operations, 28 terminal traces (including optional-child combinations) and a whole-transaction retry path. Mutation testing caught 53/53 faults, including an actual SVG with a dropped quoted value. PlantUML syntax passes with 14 participants; SVG/PNG were rendered and visually inspected, with 123/123 SQL lines visible. Temporary PostgreSQL executed the exact queries/inserts and verified active/effective/type filtering, required-current coverage predicates, read-only evidence, omitted children, complete rollback on final-child failure, repeatable policy snapshots across two connections and one winning concurrent identifier insert (23505 for the loser). These checks validate the design/SQL, not backend conformance. All 40 current documentation commands pass and the audit reports 53 tables / 0 findings.

Register delivery preflight: all 40 checks, audit 53/0 and database ALL PASSED; six paths in the authorized assignment, no blockers. Origin/main then advanced through PR #31, including refresh #24 and the repository-wide sequence checker. Integrate that base before opening the register PR, preserve every incoming checker and rerun the current checks.

Register integration verified: preserved upstream refresh, shipping and sequence-checker changes; the task diff against origin/main remains the same six assignment paths. The global sequence check now covers 83 specs; register passes its standard, so its legacy exemption was removed. All 41 documentation commands pass, audit remains 53/0, database tests ALL PASSED, mutations 53/53 and rendered SQL 123/123. Final SVG/PNG were regenerated from the restored source after mutation tests and inspected.
## e-commerce: Peter API review — submit consent (API 4)

Status: Register delivered in PR #32 (six files; MERGEABLE when opened), branch/history preserved, clean main-based submit-consent assignment prepared under Q15. Owner Q16: display records reading, optional result answers later, already-read evidence keeps its read timestamp. Q17: require the displayed version. No next-API merge gate applies.

- [x] Preserve register PR/history, return to main and prepare the scoped submit-consent assignment with passing baselines.
- [x] Read existing submit spec/sequence, token/user revocation design and consent/evidence migrations.
- [x] Persist Q16/Q17 and define read-only, answer, no-op and history behavior without a schema change.
- [x] Correct the spec and complete sequence with user-first serialization, fresh token check, current/active-type validation, deterministic existing evidence and atomic batch branches.
- [x] Add focused consent-submit-flow checks, reject the original pair and mutation-test guards/results/rendered SQL.
- [x] Verify exact SQL/no-op/rollback/concurrency in temporary PostgreSQL, render/inspect the sequence and pass all current checks/audit/database tests.
- [x] Open one API PR through commit-and-pr, preserve its review record and continue from main under Q15.

Submit verification: original pair rejected; six exact SQL operations, twelve terminal traces with distinct insert/update/no-op and aborted-update failure. The shared path parser now terminates an explicit PlantUML break, preventing failed updates from falling through to COMMIT/200; mutation coverage includes disabling that termination. All 52/52 deliberate faults are caught, including a real rendered SQL omission. PlantUML syntax reports ten participants; SVG/PNG generated and inspected, 75/75 visible SQL lines. Exact SQL in temporary PostgreSQL proves policy/type filtering, first-read preservation, no-op audit preservation, explicit false, legacy NULL timestamp and deterministic duplicates, ownership/old-version history, whole-batch rollback, two-call serialization to one evidence row, and fresh token revocation visibility after a lock wait. No backend implementation is claimed.

Submit delivery preflight: six authorized task files, all 41 documentation commands OK, audit 53 tables / 0 findings, database ALL PASSED, managed assignment authorized for Peter, no blockers. Origin/main unchanged at the pre-delivery fetch; register remains a separate review PR.
## e-commerce: Peter API review — pending consent (API 5)

Status: Submit consent delivered as PR #34 (six files, MERGEABLE when opened); its branch/assignment was preserved, and a clean main-based pending-consent assignment passed baselines under Q15. Q8 governs required versus optional pending; Q3 hides inactive types; Q16/Q17 govern displayed/current-version evidence.

- [x] Preserve PR #34/history and prepare the next bounded main-based API assignment without waiting for merge.
- [x] Read pending spec/sequence, current consent schema and the confirmed display/acceptance rules.
- [x] Persist shared Q16/Q17 decisions and define current-version canonical evidence and coherent response snapshot.
- [x] Correct spec and full sequence with credential/user checks, required/optional predicate, active type visibility, stable history/name mapping and empty success.
- [x] Add pending-consent-flow checks; reject the original pair and mutation-test SQL, outcome and rendered-text guards.
- [x] Execute the documented SQL against adversarial PostgreSQL fixtures and snapshot races; render/inspect SVG/PNG and pass all current docs/audit/database/delivery checks.
- [x] Open one pending-consent API PR with commit-and-pr, preserve its review record and continue from main under Q15.

Pending verification: original pair rejected; four identical SELECT operations and seven terminal traces. Mutation testing initially caught 42/43 because the canonical-order phrase could be found in the unrelated latest-history paragraph; scoping the guard to its canonical paragraph yields 43/43. Five synchronized spec/sequence faults (required acceptance, NULL default, active type, canonical order and projection alias) pass SQL parity but are rejected by the semantic checker. A genuine rendered omission is rejected independently with the correct source unchanged. Final SVG/PNG were generated and inspected; PlantUML reports ten participants and 60/60 visible SQL lines. Temporary PostgreSQL executed the exact queries against every required/optional read/result state, different user/version/status, duplicate canonical rows, type/time boundaries, complete response projection, latest evidence/null mapping and credential failures. Two connections prove policy/history/type-name enrichment remains coherent in one snapshot while the next inquiry sees changed policy; read-only mode rejects evidence writes. No backend conformity is claimed.

Pending delivery preflight: five authorized task paths, all 41 documentation commands OK, audit 53 tables / 0 findings, database ALL PASSED, managed assignment delivery authorized for Peter, no blockers. Origin/main unchanged at the pre-delivery fetch.
## e-commerce: Peter API review — active consent (API 6)

Status: Pending consent delivered in PR #35 (five files; MERGEABLE when opened); branch/assignment history preserved. A clean main-based active-consent assignment passed baselines under Q15. Q3 requires hiding consent when its type is not ACTIVE.

- [x] Preserve PR #35/history and prepare the bounded active-consent assignment from main without waiting for merge.
- [x] Read both active-consent artifacts, schema/type rules and paired SQL/rendering lessons.
- [x] Correct spec and full sequence for public visible consents, mandatory type-name mapping, consistent snapshot, stable order and explicit empty/error outcomes.
- [x] Add active-consent-flow checks, reject the original pair, and mutation-test source and synchronized semantic faults.
- [x] Execute exact SQL including time/type boundaries and a concurrent type/name change; render/inspect SVG/PNG and run all current docs/audit/database/delivery checks.
- [x] Open one active-consent API PR with commit-and-pr, preserve its review record and continue from main under Q15.

Active-consent verification: two identical SELECT operations and five terminal traces. Original pair rejected; mutations caught 30/30. Three additional synchronized spec/sequence faults (active type, stable order and response alias) pass source parity but fail semantic checks; a genuine rendered omission is rejected with correct source unchanged. PlantUML reports eight participants, SVG/PNG generated and inspected, 29/29 visible SQL lines. Temporary PostgreSQL executed the exact queries against all non-ACTIVE type/consent states, future/expired/exact boundaries, stable id ties, required/optional projection, full eleven-field mapping, nulls/body/version preservation and empty typed arrays. Two connections prove the mandatory original type name remains coherent in the snapshot and the next request hides the disabled type. Read-only mode rejects writes; inquiry creates no user evidence. Backend conformity is not claimed.

Active-consent delivery preflight: four authorized paths, 41/41 documentation commands OK, audit 53 tables / 0 findings, database ALL PASSED, Peter delivery authorized, no blockers. Origin/main unchanged at pre-delivery fetch.
## e-commerce: Peter API review — author/me (API 7)

Status: Active consent delivered in PR #36 (four files; MERGEABLE when opened), branch/history preserved. A clean main-based author/me assignment passed baselines. Owner Q11 requires returning the calling token's roles/isPlatformAdmin; Q13 still checks current credential/user. Management-consent questions Q18/Q19 remain pending; work continues on this already-decided API.

- [x] Preserve PR #36/history and prepare author/me from main under Q15 without waiting for merge.
- [x] Read me spec/empty sequence, author checker, approved Q11 and A16/A18 supersession.
- [x] Correct the spec to return verified token roles without live assignment/master filtering and retain active credential/user validation and the response shape.
- [x] Generate the empty sequence using the ready skeleton tool, then finish every real branch, SQL, mapping and outcome; leave no author TODO marker.
- [x] Update only the obsolete me-specific author checks, add token-snapshot flow checks, and prove old/synchronized faults fail.
- [x] Verify exact credential SQL and token-snapshot semantics, mutation coverage, rendered SQL/visuals and all current delivery checks.
- [x] Open one author/me PR with commit-and-pr, preserve its review record and continue from main under Q15.

Me verification: replaced the obsolete live-role query with one exact credential/user SELECT; roles/admin come from the calling verified token. Generated the previously empty sequence with the ready skeleton tool and completed every TODO/branch/mapping; the global check now reports author 1/12 filled, not the whole group complete. The finished sequence has eight terminal traces and seven participants; SVG/PNG were generated and inspected with 13/13 visible SQL lines. Original pair rejected; mutations caught 31/31, and three synchronized ownership/user-status/live-assignment faults pass SQL parity but fail semantic guards. A real renderer omission is also rejected with correct source unchanged. Temporary PostgreSQL executed the exact credential SQL alongside ephemeral locally signed JWT reference fixtures: old roles survive assignment revocation, new empty snapshot reports false, independent admin flags are ignored, sorting/response shape remain correct, malformed/duplicate roles and tampering fail before lookup, and wrong owner/expiry/inactive user/revoked or unstored token are rejected. This is reference/design and SQL verification, not backend conformance.

Me delivery preflight: four authorized paths, 41/41 documentation commands OK, audit 53 tables / 0 findings, database ALL PASSED, Peter delivery authorized, no blockers. Origin/main unchanged at pre-delivery fetch.

## e-commerce: Sequence diagrams of 10 inquiry APIs of product and shop

Status: Diagrams written in the managed workspace of Marry on branch `docs/marry-inquiry-sequences`; `main` (929012e, after the repair of `check_docs.py`) is merged into the branch and the pull request is open for the lead. Scope: the ten folders below and `tasks/`. No `spec.md` is changed.

Folders: `product/02-inquiry-product`, `05-inquiry-product-category`, `08-inquiry-product-category-attribute`, `12-inquiry-product-type`, `15-inquiry-product-brand`, `shop/03-inquiry-shop-product-sku`, `04-inquiry-storefront-product`, `07-inquiry-shop-type`, `14-inquiry-storefront-shop-product`, `16-inquiry-storefront-product-review`.

- [x] Write the skeletons with `sequence_skeleton.py --write` and replace every `TODO(author)` with the branches of the spec: 400, 401 for the eight APIs that need an access token (none for the three public storefront APIs), 404 for the storefront APIs, a 200 with empty items when nothing matches, 408, then the reads and 200. An inquiry has no transaction.
- [x] Put every block where it runs: the blocks that need the result of another block come after it (for example the option value images of `product/02` after the option values; `shop/04` finds the shop product, the product and its SKUs, each with its own 404, before it reads the images and options); the participants follow the first use.
- [x] Keep every SQL block letter for letter; run `api-sequence-spec` (OK, 83 specs, product 5/15 and shop 5/16 filled) and `grep TODO(author)` on the ten folders (nothing).
- [x] PlantUML: `-checkonly` and `-syntax` pass for all ten; the SVGs show every SQL line except five lines with two `--` (three in `shop/14`, two in `shop/16`), which PlantUML draws struck through; the spec is not changed in this round and the lead is told.
- [x] After the repair of `check_docs.py` was merged (929012e): merge `main` into the branch (no force push; the only conflict was the end of this file, both sections kept), rerun every checker and the preflight.
- [ ] Push, open the pull request, tell the lead; hold the lock until the merge, then release and park.

Verification: 45 of 45 `check_docs.py` sub-commands OK, `api-sequence-spec` OK (83 specs, product 5/15 and shop 5/16 filled), audit 53 tables 0 findings, database tests ALL PASSED. `test_sequence_skeleton.py` fails on `main` already (the test compares the block order of the hand-written diagrams with the skeleton; 4 files of `main` and now also `product/02` and `shop/04`, where blocks run in the order of the work); the test is outside this assignment and the lead is told.

## repository-wide: Sequence phase 1, five prototype diagrams

Status: Complete in the branch, waiting for review. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh` (the product owner ordered real diagrams instead of a notes document), workspace `.workspace/tommy`, branch `feat/tommy-sequence-cart-order-webhook`, scopes `e-commerce/doc/api/cart`, `e-commerce/doc/api/sales/02-create-order`, `e-commerce/doc/api/payment/02-stripe-webhook`, `e-commerce/db/tests/check_docs.py`, `tasks`.

- [x] Close the earlier notes task (discarded by the lead SA; the note is kept in the scratchpad) and park the workspace.
- [x] Write `sequence.wsd` of `cart/01`, `cart/02`, `cart/03`, `sales/02` to the login standard with no `TODO(author)` left: real order of checks (400, 404, 409, write), blocks placed on the branch where they run, every error after `BEGIN` after a `ROLLBACK`, every lock after `BEGIN`, participants in order of first use.
- [x] Write `sequence.wsd` of `payment/02` with Stripe as `participant "Stripe" as stripe` in `box "External"`, and let `sequence_structure_errors` accept `External, Web API, Database` (no Frontend, no actor User, the External box holds a participant).
- [x] Mutation-test the diagrams and the new rule, render every diagram with PlantUML, run all checkers.
- [x] Open the PR with `commit-and-pr`; do not merge.

Verification: see the PR. No `spec.md` and no `sequence_skeleton.py` was changed. Gaps of the specs found while writing are reported to the lead SA in the PR body.

## repository-wide: Repair check_docs.py after the merge of PR 34

Status: Complete in the branch, waiting for review. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh` (urgent repair, `main` could not run any `check_docs.py` command), workspace `.workspace/tommy`, branch `fix/tommy-check-docs-merge-syntax`, scopes `e-commerce/db/tests/check_docs.py` and `tasks`.

- [x] Find the cause: the merge `f3505f9` (PR 34) interleaved two checkers that share a template (`check_consent_submit_flow` from the submit branch and `check_pending_consent_flow` from PR 35), so `required={` of the submit checker was never closed.
- [x] Rebuild the region from the whole functions of each side (submit from `3f71d37`, pending from `4e6de08`), without deleting any needle.
- [x] Find the damage that the earlier merges left without a syntax error: `check_pending_consent_flow` and `check_active_consent_flow` had lost their tail (JSON and table checks, the rendered SVG check, `print` and `return 0`) and their `COMMANDS[...]` registration; restore them from `6e721ce` and `80cfe22`, where the common beginning is identical line by line.
- [x] Check that every `check_*` function returns and is registered or called.
- [x] Run every sub-command, `audit_all.py`, `run_db_tests.sh`, the preflight and mutation tests (needles of every `required` of the submit and pending checkers, JSON and table checks of the three consent checkers).
- [x] Open the PR with `commit-and-pr`; do not merge.

Verification: see the PR. No spec, diagram or other checker is changed.

Lesson for the team: a merge that keeps a file parseable can still drop the end of a function; after resolving a conflict in `check_docs.py`, run `python3 -c "import ast"` on it and run every sub-command, not only the one that was edited.


## e-commerce: Peter API review — own-user profile upsert (API 11, 2026-11-08)

Scope: authen-and-author/07-upsert-user-profile with its checker/task evidence. Owner Q13 preserves immediate credential/user revocation; WP4 U18/U23 governs own-user partial profile writes. Q15 permits moving to a fresh main-based branch after open PR delivery without waiting for merge. No backend/schema/publication implementation. Consent Q18/Q19 remain pending.

- [x] Preserve reset-password PR #56 and assignment history, return to main and prepare a fresh authorized profile-upsert branch with all baselines.
- [x] Read both profile endpoints, current credential rules, user/information schema and partial unique index. Reproduce the old diagram running INSERT and UPDATE in sequence and omitting current stored-token checks.
- [x] Revise spec and generated-then-completed sequence together: verified own user, post-lock credential check, per-field presence masks/null clearing, separate information insert/update and 17 complete terminal traces.
- [x] Add exact SQL/path/semantic/render checks; 64/64 mutations caught; synchronized semantic faults, pre-lock credential read, original sequential INSERT/UPDATE and real renderer omission rejected. Six exact PostgreSQL statements passed typed presence/null/date/bytea, ownership, preserved lifecycle/audit, rollback and concurrent first/disjoint writes plus revocation/expiry wait fixtures. PlantUML inspected with nine participants and 58/58 visible SQL lines; no backend/encryption-runtime certification.
- [x] Run all current checker commands (49/49), SQL audit (53 tables/0 findings), database suite (ALL PASSED), skeleton tests (12/12) and authorized preflight (four paths/no blockers).
- [x] Open one profile-upsert API PR, preserve branch/history and continue from main.
## e-commerce: Peter API review — reset-password (API 10, 2026-11-08)

Scope: authen-and-author/03-reset-password and its checker/task evidence. Existing WP4 U11/U12/U23 controls public uniform responses, three issuances per rolling hour, one ACTIVE reset and user-first serialization. Owner Q15 permits one editing branch at a time and continuation without a merge gate. No backend, email transport, outbox, schema or published API implementation.

- [x] Preserve PR #53/#55 history, return to main and prepare an authorized fresh branch with all baselines after the completed reset legacy correction merged.
- [x] Read both endpoint files, user/reset schema, register/login identifier handling and prior reset/refresh locking rules. Reproduce transaction-start created_at backdating under a shorter configured test window; run the fixture in UTC as the contract requires.
- [x] Update spec and generated-then-completed sequence together: fresh post-lock throttle/creation/expiry time, atomic replacement, ten terminal traces, mappings and post-commit email boundary.
- [x] Add exact SQL/semantic/path/render checks; mutations 49/49 after tightening database/Application result mapping (initial run 48/49); synchronized semantic faults and real rendered omission rejected. Exact PostgreSQL issuance/quota/completion races and rollback passed; PlantUML inspected with eight participants and 39/39 visible SQL lines. Email transport and real HTTP timing remain outside verification.
- [x] Run every current checker (49/49), audit (53 tables/0 findings), database suite (ALL PASSED), skeleton tests (12/12) and authorized delivery preflight (four paths/no blockers).
- [x] Open one reset-password API PR, preserve its branch/assignment history and continue from main.

## Peter — API 9: create-new-password paired contract review (2026-11-07)

Scope: authen-and-author/04-create-new-password; owner Q13 credential revocation and existing reset rules. One API per PR; continue from main without waiting for merge under Q15. No backend/schema implementation. Q18–Q19 remain pending for consent inquiry.

- [x] Prepare a fresh authorized Peter branch from current main after preserving logout PR #44; baseline all doc commands, SQL audit and database suite.
- [x] Read both existing files, password/reset/token schema, and shared login/refresh/logout locking rules; reproduce reset consumption before user lock in the old sequence.
- [x] Revise spec and generated-then-completed sequence together: fresh post-lock single-use guard, password comparison/history, all-session revocation, 12 terminal traces and rollback.
- [x] Complete final image inspection: scoped flow/character-for-character SQL checks pass; 59/59 mutations caught; synchronized SQL faults, whitespace drift and rendered omission rejected; exact PostgreSQL reset/refresh races and rollback fixtures passed.
- [x] Run every current doc command (48/48), audit (53 tables, 0 findings), database suite (ALL PASSED) and authorized delivery preflight (5 files, no blockers).
- [x] Commit paired files and support changes and open API PR #53; initial head 863d47a.
- [x] Retain branch/assignment history and continue from updated main under owner Q15; PR #55 merged and clean main baselines passed before API 10.

Integration: GitHub reported a conflict after main advanced. Preserve all upstream diagram, component-repository migration and task changes; conflict is only the shared todo append. Re-run all checks before the integration push; this PR changes only the five authorized task paths relative to current origin/main.

Delivery correction: the first integration preflight compared against stale local main and rejected imported upstream paths. The following shell step pushed despite that failure. Fast-forward local main, prove only the five task paths differ, re-run delivery authorization successfully, and require fail-fast dependent commands. A second upstream checker rule added a token/timeout legacy entry for this API; remove only its completed entry and re-run every check before the follow-up push.

Follow-up: PR #53 was merged externally at head 5635a53 while its final integration correction was being pushed. The local correction is preserved. Main still lists the completed reset in LEGACY_TOKEN_SEQUENCES, which the checker rejects. Deliver a checker/task-only follow-up under this same bounded assignment; the API spec and sequence remain byte-identical to main. Do not overwrite external branch history.

## e-commerce: Peter API review — own-user profile inquiry (API 12, 2026-11-08)

Scope: authen-and-author/08-inquiry-user-profile with checker/task evidence. Owner Q13 requires current token/user checks; existing profile inquiry returns the caller's ten keys and non-DELETED information. Q15 permits immediate fresh main-based branch after PR #57, without waiting for merge. Q20 approved by Ittikorn on 2026-11-08: “คืน null สำหรับค่าว่างเดิม (แนะนำ)”. Normalize legacy empty gender to response null with NULLIF and preserve stored history; detailed endpoint revision remains in-review. No backend/schema implementation.

- [x] Preserve profile-upsert PR #57/history, return to clean main and prepare an authorized fresh inquiry branch with all baselines.
- [x] Read both profile contracts and actual nullable/lifecycle schema. Identify missing current credential checks, missing explicit outcomes, and multi-read consistency; ask Q20 and persist the explicit owner response.
- [x] Update spec and generated-then-completed sequence together: verified caller, joined current token/user projection, consistent read-only snapshot, all ten keys/null mappings and eight terminal traces; owner Q20 projects legacy empty gender to null without rewriting history.
- [x] Add exact SQL/semantic/path/render checks; 39/39 mutations caught after tightening the unique snapshot-rule needle (initially 38/39); synchronized credential/projection/Q20 faults, early information query, SQL whitespace and real renderer omission rejected. Exact PostgreSQL SELECTs passed own-user/current token, strict expiry, non-DELETED visibility, immutable Q20 normalization, READ ONLY rejection and two-connection snapshot consistency. PlantUML inspected with eight participants and 23/23 visible SQL lines; no backend/decryption-runtime claim.
- [x] Run pre-integration checkers (49/49), audit (53 tables/0 findings), database suite (ALL PASSED), skeleton tests (12/12), and authorized preflight (four paths/no blockers).
- [x] Preserve latest main, remove restored stale exemptions for #56/#57, pass all 51 integrated checker commands/audit/database tests and deliver inquiry PR #60. Preserve branch/history and continue from main under Q15.

Integration finding: current main restored stale transaction/token-timeout exemptions for already-complete API #56 (reset request) and #57 (profile upsert). The full merged check catches this. Remove only those four stale checker entries, preserve their API artifacts byte-for-byte and keep every registered function; rerun all commands before push. This is checker reconciliation within the existing assignment scope, not another API revision.

## e-commerce: Peter API review — own-user address upsert (API 13, 2026-11-08)

Scope: authen-and-author/09-upsert-user-address plus checker, shared confirmed-decision log and task evidence. WP4 U19/U23 and owner Q13 govern ownership/current credentials, quota and default invariant. Q21 explicitly rejects DELETED plus isDefault=true with 400. Q20 is recorded in the shared decision log from its already-delivered profile inquiry. No backend/schema implementation. Q15 permits independent PRs without a merge gate.

- [x] Preserve inquiry PR #60/history and return to main. Its checker repair merged before successful fresh address branch preparation; no baseline failure was bypassed.
- [x] Read spec/sequence, address schema/unique index, inquiry rules and existing checker. Ask Q21 about the contradictory Delete example/checker and persist the owner's explicit answer.
- [x] Revise spec and generated-then-completed sequence together: full-body/Q21 validation, post-lock current credential, owned/non-DELETED target, serialized quota, nullable insert id, computed default and 14 atomic insert/update/delete/promotion traces.
- [x] Add exact SQL/path/semantic/render checks: 66/66 mutations caught, including old checker Delete exception; synchronized wrong guards, clear-after-insert and Q21-after-BEGIN ordering, original sequence, whitespace and real renderer omission rejected. Nine exact SQL definitions passed UTC PostgreSQL reference Application/default logic, quota and credential lock waits confirmed via pg_stat_activity, rollback/default promotion/soft-history/ownership fixtures. Diagram inspected with nine participants and 136/136 visible SQL lines including reused blocks; no backend/encryption-runtime claim.
- [x] Run pre-integration checkers (51/51), audit (53 tables/0 findings), database suite (ALL PASSED), skeleton tests (12/12), and authorized preflight (five paths/no blockers).
- [x] Integrate latest main including inquiry #60 and architecture #61, rerun all combined checks, deliver address API PR #62 and continue from main; #62 is now verified merged.


Integration finding: GitHub merge commit 87162eb for inquiry #60 re-added its completed API 08 token/timeout exemption (verified against its first parent b1c5c90). The full merged check rejects it. Remove only that stale checker entry; preserve the API 08 artifacts and every imported checker/function. This is the cause of the main baseline regression, not permission to weaken the legacy check or modify another endpoint.

## e-commerce: Peter API review — own-user address inquiry (API 14, 2026-11-08)

Authority: original API review, owner Q13 credentials and Q15 immediate main-based continuation without a merge gate; every checker must pass before push. One API pair per PR. Assignment includes the shared checker and tasks. No backend/schema implementation.

- [x] Preserve PR #62/history and return to clean main. Reproduce list/count snapshot mismatch in isolated PostgreSQL during read-only analysis.
- [x] Run every baseline command plus audit/database tests; record the exact known main API08 stale exemption failure honestly in /private/tmp/peter_address_inquiry_red_baseline.log. No other failing command is accepted.
- [x] Apply the same one-line shared-checker repair already delivered in #62 on this fresh main-based branch, without changing the API08 pair; all 51 documentation checks plus audit/database baselines passed before API10 edits. This bounded repair honors Q15 rather than waiting for #62 to merge; it is not a checker suppression or a general failed-baseline waiver.
- [x] Revise API10 spec/complete generated sequence together: current credential gate, identical typed filters, consistent count/page snapshot, bounds and complete mapping/outcomes.
- [x] Add exact SQL/semantic/path/render checks; mutation-test and execute pagination/ownership/snapshot SQL fixtures; inspect the diagram.
- [x] Run all checkers/audit/database tests and authorized delivery preflight; open API10 PR #65 and continue from main. Main merged #62 during delivery; resume #65 to reconcile shared checker/tasks and verify the combined tree before returning to main again.

Verification before main integration: three character-identical SQL operations, nine terminal traces, 56/56 mutations caught after closing the late-JWT-expiry branch gap; eight synchronized semantic SQL faults and intact pre-credential count/whitespace/old-diagram/render-omission faults rejected. Rendered SQL is 35/35 visible lines; SVG/PNG inspected, eight participants. Isolated PostgreSQL executes actual credential/count/page SQL: typed null filters, wildcard/apostrophe/Thai search, owner/deleted/missing id, status visibility, deterministic ties and four pages/beyond-range, expiry equality/inactive credentials, read-only write rejection and concurrent committed insert/delete between count/page with a consistent snapshot. Reference pagination bounds cover signed Int64 and checked offset; no backend implementation/conformance claim. All 52 documentation commands, audit 53 tables / 0 findings, database ALL PASSED and 12 skeleton tests passed. The initial main API08 exemption failure and its bounded checker-only repair are recorded above.

Integration with origin/main 5dda686 preserves the domain diagram package byte-for-byte; only the five authorized paths differ from that base. API10 pair and checker bytes equal the verified task commit. On the integrated tree all 52 documentation commands, audit 53/0, database ALL PASSED, 12 skeleton tests and 35/35 rendered SQL lines passed again. Authorized preflight passed before the task commit; final committed delivery scope is checked before push.

PR #65 base reconciliation: preserve both completed API09/API10 exemption removals and complete flow-checker functions after #62 merged. The API09 pair/owner decision log remain byte-identical to main; only the five owned API10 paths differ. No PR merge is performed.

## e-commerce: Peter API review — logout (API 8)

Status: Author/me delivered as PR #37 (four files; MERGEABLE when opened), branch/history preserved. Clean main-based logout assignment passed baselines under Q15. Q13 keeps immediate credential revocation; WP4 U9/U23 requires the user lock and atomic closure of every token in the caller's session. Management-consent Q18/Q19 remains pending; independent authorized work continues.

- [x] Preserve PR #37/history and prepare logout from main without waiting for merge. The first prepare label exceeded the helper's 240-character formatting limit; shorten only that label, retaining scope/requirements/authority, then prepare successfully.
- [x] Read logout spec/sequence and relevant transaction, full-session revocation and lock-order lessons; reproduce the sequence's access-token UPDATE before user lock.
- [x] Correct spec with user-first lock, fresh post-lock token/session/expiry validation, server-derived ids, complete atomic revocation and error/retry semantics.
- [x] Regenerate then finish sequence with actual execution order, every SQL request/result and success/invalid/revoked/rollback/timeout paths; remove its legacy exemption only when the new standard passes.
- [x] Add logout-flow checks, reject original/synchronized faults and mutation-test ordering, scope, transaction and rendered SQL.
- [x] Execute exact SQL for session-wide closure, rollback, concurrent refresh/logout and expiry/revocation while waiting; render/inspect SVG/PNG and pass all current delivery checks.
- [x] Open one logout PR through commit-and-pr, preserve its review record and continue from main under Q15.

Logout verification: four identical SQL operations in user-lock -> fresh session -> access closure -> refresh closure order; eight terminal paths. Regenerated via the ready skeleton tool, completed all markers/branches/mappings and removed the now-complete legacy exemption. Original pair rejected; mutations caught 36/36 (durable temporary log retained). Four additional synchronized faults, including moving the complete access UPDATE before the user lock while preserving SQL parity/participant first use, are rejected by logout-flow. Real rendered omission rejected independently; final PlantUML has nine participants, inspected SVG/PNG and 29/29 visible SQL lines. Temporary PostgreSQL executed exact logout and refresh credential statements: full closure includes older/expired ACTIVE access rows, preserves other devices/users even with a shared session id and inactive history, actual mid-transaction error rolls back, zero refresh closure is valid, zero access closure is detected, repeated/concurrent logout sees revocation, both refresh/logout races leave no new usable pair, and post-lock time rejects expiry while waiting. These are design/SQL checks, not backend conformance.

Logout pre-integration preflight passed 41/41 commands, audit 53/0, database ALL PASSED and four authorized paths. Origin/main then advanced through the already merged API reviews and cart/order/webhook diagrams; checker syntax at 4c263c7 was broken by incomplete merged function bodies. Latest main was checked again before integration and now carries the upstream repair. Integrate the latest complete checker, preserve every command/body and rerun the full current checks before delivery.

Logout integration: latest origin/main at 929012e includes upstream checker repair #39 and the now-merged API PRs #32/#34/#35/#36/#37. Preserve their complete functions/registrations plus upstream cart/order/webhook and backend guide changes; the working-tree task diff against origin/main is still only the four authorized logout paths. Prior Peter delivery checkboxes are now reconciled to those verified merged PRs. Q18/Q19 remains pending for consent management; no detailed spec approval or backend implementation is inferred from merge.

Logout post-integration verification: complete checker parses, all 46 current documentation commands pass, audit 53 tables / 0 findings, database ALL PASSED, logout mutations remain 36/36 and the unchanged spec/sequence still have 29/29 visible SQL lines. Manual diff against current origin/main is exactly the four authorized logout paths; imported main files are base history, not additional APIs in this PR.
## repository-wide: Make the skeleton test read finished diagrams like the checker

Status: Complete in the branch, waiting for review. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `test/tommy-sequence-skeleton-order-free`, scopes `.agents/skills/api-contract-design/scripts` and `tasks`.

- [x] Replace the comparison of a finished diagram with the skeleton in spec order by the checker's reading: the blocks (table, heading, SQL) as a set, repeated blocks allowed, no block that the spec lacks, database participants in the order of first use.
- [x] Add a test of the comparison itself (reordered and repeated blocks pass; a missing block, a changed SQL letter, a block with another heading, a broken lifecycle, participants out of order and an extra participant fail).
- [x] Mutation-test the test (7 changes of the test, 5 changes of real diagrams): 12/12 caught.
- [x] Open the PR with `commit-and-pr`; do not merge.

## repository-wide: Guard check_docs.py against a merge that cuts it

Status: Complete in the branch, waiting for review. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh` (queue item 1.5 after the repair of PR 39), workspace `.workspace/tommy`, branch `feat/tommy-check-docs-integrity`, scopes `e-commerce/db/tests/check_docs.py`, `.agents/skills/commit-and-pr/scripts`, `.agents/skills/commit-and-pr/references` and `tasks`.

- [x] Find why the preflight let a file that does not parse pass: the list of sub-commands came back empty and the report said `0/0 OK`.
- [x] Make the preflight parse `check_docs.py` first and report a blocker with the line, and report a blocker when no sub-command is listed.
- [x] Add the sub-command `check-registry`: every top-level `check_*` function ends with `return` or `raise` and is registered in `COMMANDS` or called, and no sub-command is registered twice.
- [x] Say it in `references/checklist.md`.
- [x] Mutation-test it (6 changes of `check_docs.py`) and show the old preflight passing a broken file and the new one failing.
- [x] Open the PR with `commit-and-pr`; do not merge.
## e-commerce: Reword the SQL comments with two `--` in shop/14 and shop/16

Status: Implemented in the managed workspace of Marry on branch `docs/marry-reword-double-dash-comments`; the pull request is opened after the preflight and merged by the lead. Scope: `shop/14-inquiry-storefront-shop-product`, `shop/16-inquiry-storefront-product-review` and `tasks/`. Only comments change; no SQL that runs.

- [x] Find the five lines (three in `shop/14`, two in `shop/16`) in `spec.md` and `sequence.wsd`, and every other user of them: `check_docs.py` (`shop-spec`) uses the start of each line (`-- ORDER BY ... , p.id`) as a needle, so the form `-- sort X: ORDER BY ...` would break it.
- [x] Reword the five lines in one form with one `--`: `-- ORDER BY p.name, p.id (sort NAME_ASC)`; the needles stay valid and the sequence equals the spec letter for letter.
- [x] Check: 45 of 45 `check_docs.py` sub-commands, `api-sequence-spec`, `audit_all.py`, database tests, `test_sequence_skeleton.py` (12 tests); the skeleton script prints no struck-through warning for any spec; no `sequence.wsd` of the repository has a SQL line with two `--`; the rendered SVGs show 115 of 115 (`shop/14`) and 57 of 57 (`shop/16`) SQL lines with no strike-through mark.
- [ ] Preflight, commit, push, open the pull request, tell the lead; hold the lock until the merge, then release and park.

## e-commerce: Sequence diagrams of 10 product write APIs (set A)

Status: Diagrams written in the managed workspace of Marry on branch `docs/marry-product-write-sequences`; the pull request is opened after the checks and merged by the lead. Scope: the ten folders below and `tasks/`. No `spec.md` is changed.

Folders (`e-commerce/doc/api/product/`): `01-upsert-product`, `03-upsert-product-batch`, `04-upsert-product-category`, `06-upsert-product-category-batch`, `07-upsert-product-category-attribute`, `09-upsert-product-category-attribute-batch`, `10-upsert-product-type`, `11-upsert-product-type-batch`, `13-upsert-product-brand`, `14-upsert-product-brand-batch`.

- [x] Skeletons from `sequence_skeleton.py`; every `TODO(author)` replaced. Flow of every diagram: 400 in Application -> `Verify JWT` -> 401 E10002 -> BEGIN READ COMMITTED -> existence checks (404) -> platform administrator (403 E10009) -> the 400 for a parent that is the category itself or its sub category (`04`, `06`; lead decision in the review of PR 46: it reads the database so it stays after the 403, and it comes before every 409) -> duplicate, in-use and other conflicts (409) -> write -> COMMIT -> 201 / 200 / 204 (single) or 200 with every item (batch); every error after BEGIN has a ROLLBACK before it; 408 and 500 as in `02-login`.
- [x] Batch diagrams: loops in request order inside one transaction (all or nothing), the existence checks of all items first, the permission check once, then the per-item conflict checks and writes; the errors carry `items[i]`. `09` checks categories, existing attributes and attributes in use for all items in one query each, because the spec writes those blocks in the plural.
- [x] Every SQL block is copied letter for letter and used exactly once; blocks are put in the order of the work and the participants follow the first use.
- [x] Checks: `api-sequence-spec` (`product` 15/15), PlantUML `-checkonly` and `-syntax` for all ten, SVG: every SQL line visible and no strike-through, mutation test of the new files (see the pull request).
- [ ] Merge `main` into the branch, run every checker and the preflight, push, open the pull request, tell the lead; hold the lock until the merge, then release and park.

## repository-wide: Sequence diagrams of the remaining customer APIs (set B)

Status: Complete in the branch, waiting for review. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `feat/tommy-sequence-remaining-seven`, scopes `e-commerce/doc/api/cart`, `sales/01-inquiry-checkout`, `sales/02-create-order`, `sales/03-inquiry-order`, `payment/01-start-payment`, `payment/03-inquiry-payment`, `shipping/05-inquiry-shipping`, `shipping/06-confirm-delivery`, `shop/15-upsert-shop-product-review` and `tasks`.

- [x] Move the 401 of `cart/01`, `02`, `03` and `sales/02` into the Application (400, verify the JWT, 401 in an `alt`), the way `consent/05` and `author/12` draw it (lead SA decision).
- [x] Write `sequence.wsd` of `payment/01`, `payment/03`, `sales/01`, `sales/03`, `shipping/05`, `shipping/06`, `shop/15` to the same standard.
- [x] `shipping/06`: the endpoint, then the automatic completion job as a second section under `== Automatic completion job (caller: system scheduler, not an endpoint) ==` because its SQL blocks are in the spec and the checker needs every block (lead SA decision (a)).
- [x] Check every file with `api-sequence-spec`, the skeleton test, PlantUML and mutation tests.
- [x] Open the PR with `commit-and-pr`; do not merge.

## e-commerce: Sequence diagrams of 10 shop APIs (set B)

Status: Diagrams written in the managed workspace of Marry on branch `docs/marry-shop-write-sequences`; the pull request is opened after the checks and merged by the lead. Scope: the ten folders below and `tasks/`. No `spec.md` is changed. With this set `shop` is 16/16 filled.

Folders (`e-commerce/doc/api/shop/`): `01-upsert-shop-product-sku`, `02-upsert-shop-product-sku-batch`, `05-upsert-shop-type`, `06-upsert-shop-type-batch`, `08-upsert-shop`, `09-upsert-shop-batch`, `10-inquiry-shop`, `11-upsert-shop-user`, `12-upsert-shop-user-batch`, `13-inquiry-shop-user`.

- [x] Write APIs (`01`, `02`, `05`, `06`, `08`, `09`, `11`, `12`): 400 in Application -> `Verify JWT` -> 401 E10002 -> BEGIN READ COMMITTED -> existence checks (404) -> permission (403) -> conflicts (409) -> write -> COMMIT -> 201 / 200 / 204 (single) or 200 (batch); a ROLLBACK before every error after BEGIN; 408 and 500 as in `02-login`.
- [x] Permission of each API as its spec writes it: platform administrator only (`05`, `06`); shop member (ADMIN or STAFF) or platform administrator (`01`, `02`; in `02` once for the request with the position `skus[i]`); open insert and ADMIN or platform administrator for update, delete and archive, and a platform administrator for a changed `platformMarginRate` (`08`, `09`); ADMIN or platform administrator, and a STAFF member may only leave the shop (`11`, `12`), followed by the ADMIN rule on the result (409 E10006, the request is rolled back; in `12` once for each shop after the last item).
- [x] Inquiries (`10`, `13`): 400 -> 401 -> reads -> 200, with no transaction; `10` returns an empty list when nothing matches (the margin rates of other shops are masked in the Domain step by the rule of the spec); `13` answers 403 E10009 before the reads when the caller may not read the requested shop or user.
- [x] Every SQL block is copied letter for letter and used once, in the order of the work; the participants follow the first use.
- [x] Checks: `api-sequence-spec` (`shop` 16/16), PlantUML `-checkonly` and `-syntax`, SVG (every SQL line visible, no strike-through), mutation tests of the new files (see the pull request).
- [ ] Merge `main` into the branch, run every checker and the preflight, push, open the pull request, tell the lead; hold the lock until the merge, then release and park.

## repository-wide: Sequence diagrams of the shop and operations APIs (set C)

Status: Complete in the branch, waiting for review. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `feat/tommy-sequence-set-c`, scopes: the eight API folders below and `tasks`.

- [x] Write `sequence.wsd` of `shipping/01-create-shipping`, `02-update-shipping-status`, `03-upsert-shipping-stop`, `04-inquiry-shop-shipping`, `sales/04-inquiry-shop-order`, `05-cancel-order`, `payment/04-inquiry-shop-payment`, `05-refund-payment` to the agreed standard (order row locked first where the spec says so).
- [x] Check them with `api-sequence-spec`, the skeleton test, PlantUML and mutation tests.
- [x] Open the PR with `commit-and-pr`; do not merge.

## repository-wide: Sequence diagrams of the campaign APIs (set D, campaign)

Status: Complete in the branch, waiting for review. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `feat/tommy-sequence-campaign`, scopes `e-commerce/doc/api/campaign` and `tasks`.

- [x] Write `sequence.wsd` of `campaign/01-upsert-campaign`, `02-inquiry-campaign` and `03-inquiry-campaign-ledger` to the agreed standard.
- [x] Check them with `api-sequence-spec`, the skeleton test, PlantUML and mutation tests.
- [x] Open the PR with `commit-and-pr`; do not merge. The author APIs (`author/01` to `11`) follow in the next pull request.

## repository-wide: Sequence diagrams of the author APIs (set D, author)

Status: Complete in the branch, waiting for review. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `feat/tommy-sequence-author`, scopes: the eleven folders `e-commerce/doc/api/author/01-upsert-role` to `11-inquiry-user-role` and `tasks`.

- [x] Write `sequence.wsd` of `author/01` to `11` (role, permission and scope upsert and batch, the three inquiries, the user role upsert with the lock order and the last administrator rule, the user role inquiry) to the agreed standard.
- [x] Check them with `api-sequence-spec`, the skeleton test, PlantUML and mutation tests.
- [x] Open the PR with `commit-and-pr`; do not merge. With this set every one of the 83 API specs has a finished diagram.
## e-commerce: api-sequence-spec requires the 401 and 408 answers and matching headings

Status: Implemented in the managed workspace of Marry on branch `test/marry-enforce-401-408-heading`; the pull request is opened after the checks and merged by the lead. Scope: `e-commerce/db/tests/check_docs.py` and `tasks/`. No spec and no `sequence.wsd` is changed. Decisions of the lead (chat, 2026-11-07): the token rule applies when the spec has a mandatory `authorization` header only; the verify step may say `JWT` or `access token`; the older diagrams that do not pass are listed by name.

- [x] Measure the three rules on every non-empty diagram before writing the code: the heading rule passes on all 72, the token rule fails on 19 and the 408 rule on 11 (see the pull request).
- [x] Rule 1: when the spec has a mandatory `authorization` header row, the diagram has `app -> app: Verify ... JWT / access token ...` followed by an `alt` with `app -> api: HTTP 401 E10002`, all before the first `app -> infra:` line; a public API (no authorization header and the words "Public API" or "API is public") must not answer 401. Login and refresh-token are not forced (their 401 is about credentials).
- [x] Rule 2: every non-empty diagram has `app -> api: HTTP 408 E90001`.
- [x] Rule 3: every `app -> infra: QUERY|INSERT|UPDATE|DELETE - X` line is followed at once by `infra -> <table>: X`.
- [x] `LEGACY_TOKEN_SEQUENCES`: 11 older diagrams (`authen-and-author` 03, 04, 07, 08, 09, 10 and `consent` 02, 03, 06, 07, 08) are exempt from rules 1 and 2; an entry must be a real spec folder and must still fail one of the two rules, so a diagram that is fixed has to leave the list; the count is printed in the OK line. `consent/04` passed both rules and is not listed.
- [x] Mutation tests: 15 cases of the harness on the three rules and the list, 13 cases that check which message fires (10 must fail, 3 controls must pass); the earlier mutation sets still behave (see the pull request).
- [x] Run every `check_docs.py` sub-command, `audit_all.py`, `run_db_tests.sh`, `test_sequence_skeleton.py`.
- [ ] Merge `main` into the branch, preflight, push, open the pull request, tell the lead; hold the lock until the merge, then release and park.

## e-commerce: Cart upsert (cart/01, 02) — 404 for an inactive SKU, ON CONFLICT merge, line limit after the write (M1)

Status: Implemented in the managed workspace of Marry on branch `docs/marry-cart-sku-404-on-conflict`; the pull request is opened after the checks and the lead is told at once. Scope: `cart/01-upsert-cart-item`, `cart/02-upsert-cart-item-batch`, the needles of `cart-spec` in `check_docs.py`, and `tasks/`. No schema is changed. Decision (C) of the lead, approved by the product owner on 2026-11-08.

- [x] Rule text: a shop, product, shop product, shop product SKU or product SKU that is not ACTIVE answers 404 (E10005) as the SQL already did; 409 (E10007) stays for no lot on sale, not enough stock and a quantity over the maximum. The example "The SKU is out of stock or no longer on sale." becomes "The SKU is out of stock.".
- [x] The add is one `INSERT ... ON CONFLICT (user_id, shop_id, product_id, sku_id) WHERE row_status <> 'DELETED' DO UPDATE` that merges into the existing line and applies the stock rule in the same statement (no row returned = 409 E10007); `RETURNING ... (xmax = 0) as is_insert` tells 201 from 200. The predicate is required because `uq_t_cart_user_id_shop_id_product_id_sku_id` is a partial index; a soft-deleted line is outside it, so adding the SKU again inserts a new line. The read "Get the line of the same SKU for merging" is removed and "UPDATE - Merge, update or delete a line" is renamed "UPDATE - Update or delete a line".
- [x] The line limit (100) is checked after the write in the same transaction; more than 100 lines rolls back with 409 (E10008).
- [x] Spec and diagram changed together (`cart/01` and `cart/02`); the needles of `cart-spec` that depended on the old wording are updated and new needles guard the `ON CONFLICT` clause (tied to the SQL, not to the prose), `DO UPDATE SET`, the stock `WHERE`, `is_insert`, the renamed UPDATE and the limit rule.
- [x] Proof on PostgreSQL 17 with the real migrations (throw-away cluster): insert, merge, merge over the stock (no row), re-add after a soft delete (new line) and the count behave as designed; without the predicate PostgreSQL rejects the statement.
- [x] Mutation tests: 24 of 24 caught (each new clause removed from the spec and from the diagram, the 404 rule, the limit rule).
- [x] Lesson of the notice before the owner merges (see `tasks/lessons.md`).
- [ ] Merge `main`, preflight, push, open the pull request, tell the lead at once; hold the lock until the merge, then release and park.

## e-commerce: Spec risks T1 (payment and sales)

Status: Complete in the branch, waiting for review. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh` (the product owner approved the changes on 2026-11-08), workspace `.workspace/tommy`, branch `fix/tommy-spec-risks-payment-sales`, scopes `payment/01-start-payment`, `payment/02-stripe-webhook`, `payment/05-refund-payment`, `sales/02-create-order`, `sales/05-cancel-order`, `e-commerce/db/tests/check_docs.py` (needles only) and `tasks`.

- [x] (A) Every call to Stripe has an `Idempotency-Key` written in the spec (`payment-<orderId>-<attempt>-<paymentMethod>-<shippingMethod>`, `cancel-<paymentIntentId>`, `refund-<paymentId>`), and each API says what makes the database match when the `COMMIT` fails after Stripe answered; the webhook has a branch for each of those states.
- [x] (D) `FOR UPDATE` and `ORDER BY` for the lock order cart lines, order row, lots by id, budgets by id: `sales/02` locks the cart lines, `sales/05` locks the order row and sorts the items by `lot_id`, `payment/05` and the webhook sort the items by `lot_id`; the webhook writes `system` in the ledger and the budget.
- [x] Move the matching diagrams, add the needles to `payment-spec` and `order-spec`, run every checker and the mutation tests.
- [x] Open the PR with `commit-and-pr`; do not merge. T2 (shipping and campaign) follows after T1 is merged.

- [x] Merge `main`, preflight, push, open the pull request #58, tell the lead at once.
- [x] Follow-up decided by the lead after the review (the owner merged #58 before it was pushed, so it is a second pull request): the transaction of `cart/01` and `cart/02` starts with `QUERY - Lock the user` (`authen.m_user`, `WHERE u.id = <verified userId> AND u.row_status = 'ACTIVE' FOR UPDATE`, as every authen API does) so that the merge, the stock rule and the 100-line count are exact for two requests of the same user; a missing or inactive user answers 401 (E10002) after a ROLLBACK. Spec and diagram change together; needles guard the query, its `FOR UPDATE` line and the rule; 10 of 10 mutations caught and BEGIN moved after the lock is rejected; proved on PostgreSQL 17 (the lock returns the row of an ACTIVE user, no row for a missing one, and a second transaction of the same user waits for the first).
- [x] Repair of `main` found while checking M1 (`api-sequence-spec` was red at 31327ab): `authen-and-author/03-reset-password` and `07-upsert-user-profile` pass the checks since PR #56 and #57, so they leave `LEGACY_SEQUENCES` and `LEGACY_TOKEN_SEQUENCES` (decision of the lead).
- [x] Found while rendering the changed diagrams: the INSERT of `cart/01` and `cart/02` merged in #58 had its value lines (`'<sequence.userId>',`) written with a bare leading quote, which PlantUML draws as a comment, so six lines were missing from the picture while the checker (which reads raw text) passed. They are written `&#39;` now, as the skeleton script does; every SQL line shows at least as often as in the spec. The same defect is in four older diagrams outside this assignment (`authen-and-author/09` 10 lines, `consent/02` 11, `consent/06` 5, `consent/07` 5), reported to the lead.
- [ ] Merge `main`, preflight, push, open the follow-up pull request, tell the lead at once; hold the lock until the merge, then release and park.

## e-commerce: Curate four presentation diagrams from the owner handoff

Assignment: Codex executing with the Diagram Designer perspective; delivery `none`; authorized by `ittikorn`. The owner explicitly requested a separate workspace after Jinny's managed clone was found locked by an active domain-model task. This task uses the app-managed `diagram-handoff` worktree on `codex/diagram-handoff`; it does not acquire, release or modify Jinny's workspace or assignment. Scope: `e-commerce/diagram/` and required task records. Governing content: owner handoff in this chat, existing diagram companions and API-source references. Outbox remains proposed; no backend/API/schema implementation or approval is included.

- [x] Inspect sources, task isolation, existing changes and baseline checks for the four diagrams.
- [x] Add the Controller → Dispatcher → Handler → Domain/ports → Infrastructure call paths, preserving real layer containment and CODE/SPEC/PROPOSED distinctions.
- [x] Show checkout's atomic source transaction before READY and mandatory operator review before controlled quarantine replay.
- [x] Retain and clarify outbox sequence claim transaction, destination transaction, fenced ACK, replay and lease expiry.
- [x] Rename system-design to order-lifecycle and remove Redis/MongoDB detail from its image and companion.
- [x] Curate the four primary images and topic-based references; synchronize source generators, companions and links.
- [x] Regenerate only the four selected views; export editable PNGs and verify source parity, geometry, HTML accessibility, links and final visual renders.
- [x] Record final results and hand off the separate workspace without committing or opening a PR.

## e-commerce: Organize diagram folders and deliver the handoff PR

Authority: direct request from Ittikorn in this chat to separate folders and open a PR; delivery is now `open-pr` for this task's existing Codex worktree/branch. The prior Jinny workspace remains untouched. Scope: `e-commerce/diagram/` plus required task records. The owner handoff still governs content; proposed outbox design remains unapproved for implementation.

- [x] Inspect delivery rules, baseline, existing files and generator/link dependencies.
- [x] Group four primary bundles under main/, eleven reference bundles by topic under reference/, supporting design records under design/, and generators under scripts/.
- [x] Adapt generator output resolution and update all affected Markdown links, HTML navigation and reproduction commands.
- [x] Verify all fifteen generated views, editable PNG/source parity, folder membership, Markdown links/frontmatter, HTML checks and preservation of reference diagram content.
- [x] Update final verification and task records; run delivery preflight and inspect the staged diff.
- [x] Commit the scoped work, push codex/diagram-handoff and open a PR targeting main; report checks and remaining limitations. PR #64 is open at cfd6f72.

Delivery state in this checklist is the pre-send snapshot captured by the commit. Confirm the actual commit, branch push and PR outcome from Git/GitHub; do not infer an open or merged PR from a checkbox.

## e-commerce: Resolve PR #64 conflicts with the Domain diagram package

Authority: Ittikorn requested resolving branch conflicts in this chat, specifically the shared `e-commerce/diagram/generate_diagrams.py` renderer (renamed to `scripts/generate_diagrams.py` here). Integrate `origin/main` into `codex/diagram-handoff`; this does not authorize merging PR #64 into main. Main now contains PR #63's dedicated domain/ package. The worktree was clean before integration; Git reported one content conflict in the renamed renderer.

- [x] Refresh main/PR state and identify the incoming Domain package and exact renderer conflict.
- [x] Preserve output_dir support and new artifact routing in the shared PNG finalizer.
- [x] Adapt Domain imports/HTML navigation to the scripts/ layout; preserve all incoming domain models and PNGs, and retain Domain entries in the guide.
- [x] Verify the original fifteen diagrams plus four Domain diagrams, source/editable PNG parity, local links and Markdown frontmatter; resolve all index conflicts.
- [ ] Run preflight, inspect the merge diff and record verification; commit the resolved merge and push to PR #64, then confirm its mergeability.

## e-commerce: Peter API review — role batch upsert (API 16, 2026-11-08)

Authority: owner Q2/Q4/Q10/Q13/Q15, one paired API per PR; author/01 was delivered as PR67 (four files, MERGEABLE, 54 checks/80 mutations/85 visible SQL lines) and preserved without a merge gate. Main-based batch baseline is green. Scope: author/02 pair, shared checker and tasks; no schema/backend implementation.

- [x] Deliver PR67, archive assignment/history, return to main and prepare a fresh authorized batch branch with complete baselines. Read the full batch pair, role schema and single-role review.
- [x] Reconcile whole-request 400/existence-before-permission with ordered per-item checks/writes; preserve earlier-item visibility, indexed errors, all-or-nothing response and delete/name-reuse behavior.
- [x] Update spec/complete sequence together: verified claims and current credentials, caller-first/sorted target locks, null-safe conflict checks, immutable system role, guarded writes and exact ordered result mapping.
- [x] Add strict SQL/path/loop/semantic/render checks; execute exact PostgreSQL mixed-batch, ordering, rollback and concurrency fixtures; mutation-test and inspect the finished diagram.
- [x] Deliver batch PR69 after full verification, preserve its history and continue from main; GitHub now verifies #69 merged at c35aaa5.

Verification: nine exact SQL definitions across ten note occurrences; one request-order loop, one claims permission and one final commit. The checker expands 19 representative single-iteration terminal traces; actual multi-item semantics are verified by PostgreSQL fixtures, not inferred from one unrolled iteration. Mutations caught 87/87 faults after closing initial repeated-rule/lock-description gaps (83/85 first pass), including explicit caller/target SQL lock-strength faults. Eight synchronized SQL semantic faults, early permission, COMMIT moved into the loop, SQL whitespace drift, the original diagram and a real rendered VALUES omission are rejected. Final SVG/PNG inspected with 11 participants and 75/75 visible SQL lines including the repeated duplicate query.

Actual PostgreSQL fixtures passed mixed four-action and all-delete batches, insert-ARCHIVED action, canonical duplicate ids, whole-target 404 precedence, one exact claims permission, delete/rename-then-name-reuse and reversed-order failure, later conflict/system/binding rollback, real SQL error and zero guarded update rollback, concurrent unique-index collision at item 1 undoing its earlier insert, opposite input orders over sorted role locks, caller revocation/expiry lock waits, inactive caller, and all 100 returned indexed results at the maximum. These are exact SQL with reference Application orchestration; backend/JWT crypto and unmigrated cross-API reference writers remain outside certification. All 54 documentation commands, audit 53/0, database ALL PASSED, 12 skeleton tests and authorized dirty-tree preflight are required before delivery.

## e-commerce: Peter API review — single role upsert (API 15, 2026-11-08)

Authority: owner Q2/Q4/Q10/Q13/Q15; one API pair per PR, claims authorize until access expiry but current credentials still revoke immediately. Main-based branch passed 52 documentation baseline commands plus audit/database tests after PR #62 merged. PR #65 was delivered and its conflicting base reconciled with 53 passing commands; preserve its branch/revision history without a merge gate. Scope: author/01 pair, shared checker, tasks; no backend/schema implementation.

- [x] Preserve PR65 and prepare a fresh main-based assignment with complete green baselines. Read role spec/sequence/schema, system-role/in-use/name uniqueness rules and neighboring assignment locking.
- [x] Reproduce current null-exclusion duplicate behavior and unguarded update; define current credentials versus JWT-only caller authorization without changing the approved 400/404/403/409 order.
- [x] Update spec and generated-then-finished sequence together, with exact SQL, complete branches, mapped write ids, current credentials, system role protection and atomic conflict outcomes.
- [x] Add focused semantic/path/SQL/render checks, mutation-test them, execute exact PostgreSQL concurrency/rollback/ownership fixtures and inspect the diagram.
- [x] Integrate latest main preserving all other APIs, run every checker/audit/database/skeleton/preflight, deliver one PR and continue from main under Q15.

Verification: nine SQL definitions copied character-for-character across eleven executed note occurrences; 21 terminal paths. Focused mutation tests caught 80/80 faults (initial 75/78 exposed missing per-branch UPDATE-result/guard checks, now fixed), eight synchronized SQL faults still pass normalized parity but fail semantics; authorization moved before existence, exact SQL whitespace drift, the old live-grant diagram and a real rendered VALUES omission are rejected. The final narrative includes every API/frontend/caller outcome, user-first and target locks, explicit activations and full rollback/commit effects. Actual PostgreSQL reproduced baseline NULL-exclusion and deleted-row resurrection risks, then passed lifecycle/system-role/binding status/name reuse, bound apostrophe/Thai/audit, actual error rollback, two-caller unique-index race, deletion lock wait, revocation/expiry wait and inactive-user checks. Reference Application driver only; unmigrated binding writers and backend/JWT/encryption implementation are not certified.

Pre-integration: all 53 documentation commands, audit 53/0, database ALL PASSED, 12 skeleton tests, 85/85 rendered SQL lines. The skeleton initially counted a repeated BEGIN token inside its copied execution hint; rephrase the hint without changing SQL, and the unchanged generator tests pass. PR65 is now verified merged; integrate its checker plus the new sequence guidance and diagram package, preserving every unrelated artifact.

Integrated origin/main aab155b: API10 review, updated sequence guidance and diagram organization retained exactly, with no off-scope changes relative to main. Final 54/54 documentation commands, audit 53/0, database ALL PASSED, 12 skeleton tests, 80/80 mutations and eight synchronized semantic SQL faults passed/rejected as expected; all 85/85 SQL lines visible, including repeated blocks. Four owned files differ from main. Recovered SQL preserves note prefixes and original whitespace exactly.

## e-commerce: Peter priority review — reconcile PR67 with merged role batch (2026-11-08)

Owner requested checking check_docs.py in PR67 before any other work and opening a fresh PR. Live GitHub evidence: PR67 is OPEN/CONFLICTING, not merged; PR69 is MERGED at c35aaa5. Main correctly contains role-batch-flow; PR67 correctly contains role-upsert-flow. Their author_needles branches and adjacent function insertions conflict when combined. The absence of an unmerged PR's function on main is not a lost-function regression. Inquiry remains clean/pushed at 2a85351 on its preserved branch, with its assignment and Q22/Q23 answers suspended locally.

- [x] Verify actual PR states/head identities; reproduce checker/task conflicts with merge-tree without changing the working tree. Preserve inquiry and prepare a fresh main-based reconciliation assignment with all 54 checker/audit/database baselines green.
- [x] Carry the exact reviewed API01 spec/sequence from PR67; start checker from current main and add only its role-upsert flow and API01 compatibility, retaining merged batch behavior and every other function/registration.
- [x] Prove all pre-existing main functions unchanged except author_needles; compare each API's expected needles against its correct source. Run both flow/mutation/render suites and every registered checker, audit, database/skeleton tests and authorized preflight.
- [x] Open a verified replacement PR with one API pair, preserve PR67 history and report the new link before resuming inquiry.

Verified combined checker: all 159 pre-existing main functions retained; only author_needles changes, preserving API02..09 expectations exactly. API01 expectations and its full check_role_upsert_flow source equal PR67. COMMANDS is exactly main's 54-command set plus role-upsert-flow (55). Both API01 files equal PR67 byte-for-byte; the API02 pair equals main. Mutation runs passed 6/6 integration/registration-loss faults, 80/80 single-role faults and 87/87 batch faults (173/173 total). All 55 documentation commands, audit 53/0, database ALL PASSED, 12 skeleton tests, both actual PostgreSQL fixture drivers, and counted render checks (85/85 single, 75/75 batch) passed on the combined tree. Backend/JWT implementation and unmigrated cross-API binding writers are not certified.

## e-commerce: Peter API review — role inquiry (API 17, 2026-11-08)

Authority: owner Q2/Q4/Q10/Q13/Q15; one API spec/sequence pair per PR. Role single PR67 and batch PR69 are open and MERGEABLE as delivered, with preserved branch/assignment histories. A fresh main-based inquiry branch passed 53 documentation baselines plus audit/database tests. Scope: author/03 pair, shared checker and tasks; no backend/schema implementation.

- [x] Deliver role-batch PR69, verify its actual returned URL/branch/head, archive the matching history and prepare the next authorized branch without a merge gate. Read the entire role inquiry pair and governing nullable/filter/schema/security rules.
- [x] Update inquiry spec/sequence together: verified JWT platform-admin claim, current credentials, read-only consistent count/page, bound nullable filters/checked paging, exact projection and every response.
- [x] Add strict SQL/flow/result/render checks, mutation and synchronized semantic faults; execute exact PostgreSQL filter/credential/pagination/snapshot fixtures; inspect the diagram.
- [x] Preserve latest main, run every checker/audit/database/skeleton/preflight and deliver one inquiry PR; continue from main immediately.

Verification: three SQL definitions match every character, including comments/indentation; 10 terminal traces cover 400, three 401 cases, claims-only 403 before role reads, three pagination successes, timeout and unexpected failure. Mutations caught 64/64; eight synchronized SQL semantic faults pass normalized parity but fail the focused checker; permission before current credentials, count before permission, whitespace drift, old diagram and actual rendered omission also fail. SVG/PNG inspected with eight participants and 28/28 visible SQL lines. Actual PostgreSQL verified four-field projection, all non-DELETED statuses, every nullable/combined filter, name OR description search with case/apostrophe/Thai/wildcards, paging/beyond/missing id, current credential expiry equality/owner/status, read-only rejection/audit preservation and concurrent insert/delete snapshot isolation. Reference claims orchestration rejects before role queries despite a live grant, and permits a current old admin claim without one. HTTP/JWT cryptography/backend conformance is excluded. All 54 documentation commands, audit 53/0, database ALL PASSED and 12 skeleton tests pass. Latest fetched main remains aab155b; only the five authorized inquiry/checker/task/lesson paths differ.

Integration: origin/main c69dc19 adds the self-contained sequence example/guidance; its skill files match main byte-for-byte. API17 pair and complete checker match the verified task commit unchanged, and exactly five owned paths differ from main. All 54 documentation checks, audit 53/0, database ALL PASSED, 12 skeleton tests and 28/28 rendered SQL lines passed again on the integrated tree. Owner Q22/Q23 were subsequently answered: reject a scoped-to-unscoped transition with surviving non-DELETED role/user grants (409 E10006), and allow unlinking an existing closed scope while retaining ownership/immutable-id/in-use checks. These decisions are preserved for the separate permission API review, not implemented in inquiry.

Resume: owner explicitly requested continuing the pending work. Restore the original inquiry assignment/branch and merge current main f5580ed087c8ffcc6a740b256fcb6aacd36ec5ae. Preserve all single/batch checker bodies and registrations from merged PR73/69; modify only API03 expectations and add its exact previously-tested checker. Q22 quote: “ใช่ ปฏิเสธจนถอน grant เดิมครบ”; Q23 quote: “ใช่ อนุญาตถอน link ของ scope ที่ปิดแล้ว”. Do not close PR67 without explicit owner approval; the earlier closure attempt was rejected and no closure was performed.

API17 resumed integration verification: main f5580ed087c8ffcc6a740b256fcb6aacd36ec5ae retained byte-for-byte outside the five owned paths, including both completed role API pairs. Main functions/registrations are preserved, adding only role-inquiry-flow (55 -> 56 commands). On the combined tree 56/56 documentation checks, audit 53 tables / 0 findings, database ALL PASSED, 12 skeleton tests, 64/64 mutations, synchronized semantic faults, actual PostgreSQL inquiry fixtures and 28/28 rendered SQL lines passed. The saved inquiry API pair/checker remain unchanged; resolve checker/task conflicts by preserving the whole current-main definitions and the exact inquiry additions.

## e-commerce: Peter API review — permission upsert and scope links (API 18, 2026-11-09)

Authority: original review plus Q2/Q4/Q10/Q13/Q15, owner Q22/Q23 confirmed 2026-11-08. Inquiry PR74 delivered with spec/sequence, 56 checks, 64 mutations and 28 visible SQL lines; its history is preserved and main now includes it. New permission branch passed 56 documentation baselines plus audit/database tests. Scope: author/04 pair, shared checker, confirmed-decision log and tasks; no backend/schema implementation.

- [x] Deliver/archive PR74 and prepare a clean main-based permission assignment with complete green baselines. Read the full permission pair, master/link schema, current claim resolver and generic author checks.
- [x] Persist Q22/Q23 verbatim and revise the contract: claims-only caller authorization plus current credentials; owned immutable scope links; ACTIVE-master validation only when retaining/adding; final scoped-to-unscoped guard; guarded writes and complete response mapping.
- [x] Finish the generated sequence with every SQL at its actual phase, scope loops, explicit result mapping, all rejection/rollback/commit outcomes and no incomplete scaffold.
- [x] Add strict SQL/phase/transaction/render checks; mutation-test them and execute actual PostgreSQL parent/child/Q22/Q23/rollback/concurrency fixtures. Inspect the rendered diagram.
- [x] Integrate newest main, preserve every other checker/API, run all required suites/preflight, open one paired API PR and continue from main without a merge gate.

Preserve the existing single-permission precheck semantics: child duplicate/in-use validation occurs before any parent/child mutation; delete-and-readd of an already-defined scope in the same array still conflicts until the old link is removed in a prior request. No new child count limit, schema field, grant writer or response child-id array is added. Q22 checks a real transition (before non-DELETED definition count > 0, final count = 0), not ordinary updates to already-unscoped permissions.

Verification before base integration: 57/57 documentation commands, audit 53 tables / 0 findings, database ALL PASSED, 12 skeleton tests and authorized dirty-file preflight passed. The 16 unique SQL definitions occupy 19 actual sequence occurrences; counted SVG contains all 139/139 SQL lines. Mutation testing caught 66/66 isolated faults plus 10 synchronized SQL semantic faults that still pass generic spec/sequence parity (76 total). Actual PostgreSQL reference orchestration verified derived parent ids, typed nullable exclusions, owned immutable links, pre-write conflict semantics, Q22 final-state rollback for non-DELETED role/direct grants, Q23 closed-master cleanup, already-unscoped updates, actual unique races, fault rollback and caller-lock revocation/expiry. Structural traversal is one representative pass through each of three loops, not proof of all concrete multi-item requests; real SQL fixtures cover concrete requests. Backend/JWT cryptography and unmigrated reference writers remain outside this review.

API18 integration: fetched origin/main d1ad5d97dcf738421a3c66bb9ca350b3300ada9e into this task branch without conflicts; incoming delivery-skill and code-structure changes are preserved. All 161 pre-existing checker functions remain identical except the bounded API04 author_needles update, with exactly one new permission-upsert function/registration. Only the six authorized API04/checker/decision/task/lesson paths differ from the fetched base. Post-integration 57/57 documentation commands, audit 53/0, database ALL PASSED, 12 skeleton tests, 66/66 mutations plus 10/10 synchronized faults, actual PostgreSQL fixtures and 139/139 counted rendered SQL lines passed again. No backend implementation is certified.

Delivery: PR77 https://github.com/ittikornsopawan/system-analysis-and-design/pull/77 opened on the verified API18 branch. Initial GitHub mergeability is UNKNOWN (not yet computed), not a reported conflict. Preserve this open PR and its branch; continue under owner Q15 without merging or waiting.

## e-commerce review: reusable verification guidance (2026-11-09)

Required follow-up to the repository error-improvement rules. API18 PR77 and API19 PR79 each contain only their own API pair and scoped verification work; preserve both histories and avoid adding skill files to the API19 assignment after the fact. This fresh assignment changes only existing checker/delivery references and task/lesson records.

- [x] Deliver/report PR79 with five files, preserve its verified head/history and return to main without a merge gate. Prepare a separately scoped guidance branch after green baselines.
- [x] Strengthen existing guidance for phase-specific guard mutations, fixture lifecycle/ownership preconditions, supported comparison domains and recovery of required command inputs.
- [x] Verify the guidance against the corrected permission single/batch scenarios and registry comparisons; retain scope/approval safeguards and inspect the complete prose diff.
- [x] Integrate current main, run required preflight/format checks and publish the preventive guidance separately.

API19 delivery evidence: https://github.com/ittikornsopawan/system-analysis-and-design/pull/79 at head 8d0d80ad5f1534803a6f1c8fb03b0836bd4a37e6; integrated main 878d11229c8d78f385741da2fc6397d103ac7bda, 58/58 checks, audit 53/0, database ALL PASSED, 12 skeleton tests, 107 negative cases, real PostgreSQL batch fixtures and 141/141 visible SQL lines. Initial remote mergeability UNKNOWN was not a reported conflict. No PR was merged by Peter.

Guidance verification: the phase-specific mutation fails with the unrelated phrase still present, both delivered flow checkers pass on their unchanged published pairs, helper-supported-family/registry comparisons pass, recreated readable commit input matches the successful merge subject, and the corrected entire PostgreSQL batch driver passes again against exact PR79 SQL. Review distinguishes setup defects from defects in the artifact under test; approved contract expectations and delivery authorization remain unchanged. Four owned Markdown files only; preflight and diff whitespace checks pass.
## e-commerce: Peter API review — permission batch (API 19, 2026-11-09)

Authority: owner Q2/Q4/Q10/Q13/Q15/Q22/Q23; API18 PR77 is delivered/open and its branch/history preserved. Start from main without requiring merge. Scope: author/05 pair, checker, approved-decision log and task/lesson records; no backend/schema implementation.

- [x] Open PR77, report its actual URL immediately, preserve assignment history and return to main; prepare API19 after all baseline checks pass. Read the entire existing batch pair and relevant single/batch contracts.
- [x] Persist Q22/Q23 and revise batch rules/SQL: current credentials, one claims guard, deterministic bulk locks, indexed errors, request-order processing and derived parent ids; apply final scoping and closed-master rules per distinct permission.
- [x] Complete paired sequence with every SQL at the actual phase, nested input/child loops, full rollback on any item failure and one ordered 200 result after all mapping/commit.
- [x] Add focused checker and mutation/render verification; execute real PostgreSQL mixed/100-item/Q22/Q23/order/rollback/concurrency fixtures. Run every registered checker, audit/database and skeleton tests.
- [x] Integrate newest main, preserve all other API/checker work and publish this API alone; continue under owner Q15.

Preserve the existing response schema exactly: each result contains index, permissionId and action (no rowStatus or scope ids). All parent/child input validation completes before SQL; repeated parent ids are rejected. Before mutation lock all target parents by id, then all ACTIVE referenced masters by id, then requested owned child definitions by id. Check all parent existence before the one caller-permission guard, as in the completed role batch. Within each permission all child prechecks precede its writes; prior permission writes remain visible for later name checks. Because a permission appears only once, its post-child Q22 check is its final state for the whole batch.

API19 verification before integration: 57/57 documentation commands, audit 53 tables / 0 findings, database ALL PASSED, 12 skeleton tests and authorized preflight passed. All 16 unique SQL definitions match exactly at 19 sequence occurrences; SVG/PNG inspected and 141/141 SQL lines are visible. Isolated mutations caught 93/93, synchronized SQL semantic faults caught 10/10 despite generic parity passing, and four genuine phase reorderings (existence/permission, early loop commit, mapping before final Q22) were rejected despite generic parity passing: 107 negative cases total. Exact PostgreSQL reference orchestration passes mixed/all-delete/insert-ARCHIVED/100-item results, parent-derived child ids, closed-master cleanup, all non-DELETED grant statuses, later-item Q22 rollback of all earlier rows/audits, pre-write child conflicts, ownership/immutable scopes, delete/reuse order, real SQL/unique/zero-row faults, opposite-order concurrent locks and actual master/token/expiry waits. Backend/JWT implementation and unmigrated reference writers remain unverified.

API19 integration: fetched origin/main 878d11229c8d78f385741da2fc6397d103ac7bda (including API18 PR77). Resolve checker/lesson/task conflicts from whole current-main content plus only the batch function, API05 expectations and API19 records. All 162 existing function bodies remain byte-identical except author_needles; every other master API expectation (01..09) is identical, and COMMANDS is exactly main 57 plus permission-batch-flow (58). API18 pair and confirmed-decision log remain byte-identical to main, leaving five owned changed files. Post-integration 58/58 documentation commands, audit 53/0, database ALL PASSED, 12 skeleton tests, 107 negative checks, actual PostgreSQL batch fixtures and counted 141/141 rendered SQL lines pass.

## e-commerce: Peter API review — permission inquiry (API 20, 2026-11-09)

Authority: owner Q2/Q4/Q7/Q10/Q12/Q13/Q15 and direct instruction to proceed. Permission single PR77, batch PR79 and verification-guidance PR80 are merged; preserve their complete contracts/checkers. Start from updated main with all 58 documentation baselines plus audit/database green. Scope is the author/06 pair, its checker/task evidence and only necessary preventive reference changes. No schema/backend implementation.

- [x] Prepare a clean main-based assignment and read the complete inquiry pair, role inquiry prototype, permission/link/scope schema and governing owner decisions.
- [x] Reconcile the complete permission inquiry contract: current credentials and verified JWT administration, nullable bound filters/checked paging, one read-only snapshot for count/page/definitions/masters, exact nested mapping and every outcome.
- [x] Generate and finish sequence.wsd alongside spec.md, placing every SQL at its real branch and mapping input/result sets, empty-page/link cases, commit/rollback, timeout and unexpected failure.
- [x] Add strict SQL/flow/projection/render checks; mutation-test semantic/phase faults; execute exact PostgreSQL filter/page/link/master/status/snapshot fixtures and inspect the render.
- [x] Reconcile stale Peter delivery checkboxes against confirmed merged evidence; integrate latest main preserving all other API/checker work, run complete verification/preflight and deliver one API PR. Return to main without a merge gate.

Preserve the existing management inquiry behavior: non-DELETED permission definitions are returned even when their referenced master is INACTIVE/LOCKED/ARCHIVED/DELETED; metadata still comes from that exact master id. This is an administrative catalog, not the ACTIVE-only login/refresh claim resolver. Preserve the five-field permission object (including scopes) and five-field scope object, database collation for name/code order, all pagination metadata and empty-list HTTP 200. Use page-derived typed UUID arrays, no interpolated IN list or per-item queries. Scope rowStatus describes the definition, not its master.

API20 verification before integration: all 59 documentation commands, audit 53 tables / 0 findings, database ALL PASSED and 12 skeleton tests pass. Five SQL definitions equal the sequence character-for-character at their five actual phases. The 11 terminal structural traces cover 400, three credential/JWT 401 branches, claims-only 403, four populated/empty success modes, 408 and generic 500; two mapping loops have no SQL/commit/response. Isolated mutations caught 81/81, synchronized semantic SQL faults 12/12 (including wrong schema and hidden extra predicate) and flow/strict/legacy/render faults 9/9: 102 negative cases. SVG/PNG inspected; counted SQL is 44/44 visible lines and removing one repeated WHERE line is rejected. Exact PostgreSQL fixtures verify bound null/filter/page/ILIKE/bounds, parent-only page ids, no N+1 SQL, all definition/master statuses, reused-code identity, exact five-field nested mapping, read-only preservation, malformed result handling and concurrent parent/link/master snapshot isolation. Reference mapper/JWT-verified orchestration only; no HTTP/JWT cryptographic/backend conformance claim.

Delivery-record reconciliation: live GitHub confirmed PR23/24/32/34/35/36/37/44/53/55/56/57/60/62/65/69/73/74/77/79/80 MERGED. Nine stale Peter checkboxes were reconciled, including logout SQL/render evidence already recorded in its own section, single-role replacement PR73, role inquiry PR74, permission batch PR79 and guidance PR80. Unrelated task checkboxes and old historical narratives are preserved.

## e-commerce: Peter API review — scope upsert (API 21, 2026-11-09)

Authority: owner Q2/Q4/Q7/Q10/Q13/Q15 and direct instruction to proceed. API20 permission inquiry delivered as PR82 (6f6eecc), six files, 59 checks, 102 negative cases and 44/44 rendered SQL lines; preserve its branch/history without a merge gate. This branch starts from current main after complete baselines. Scope: author/07 pair, checker/task evidence and only required preventive references. No backend/schema implementation.

- [x] Report/preserve PR82, return to main and prepare the next scoped assignment. Read the entire scope pair, migration/schema, approved A8/A12/A14/A15 and the owner claim/revocation decisions.
- [x] Revise scope spec/SQL with verified JWT administration/current credentials, caller-first and target locking, nullable duplicate exclusion, all non-DELETED reference checks and guarded audited writes. Preserve existing scope-code editability, status lifecycle and exact messages/response shape.
- [x] Finish paired sequence with actual SQL branches/results, complete validation/credential/permission/conflict/write/rollback/commit and delete/archive/insert-ARCHIVED outcomes.
- [x] Add exact SQL/phase/response/render checking, mutation-test it and execute actual PostgreSQL lifecycle/usage/rollback/unique and credential/reference-writer lock races; inspect SVG/PNG.
- [ ] Integrate newest main, preserve all unrelated API/checker work, run all required checks/preflight and publish one API PR; continue from main without waiting for merge.

Lock protocol: caller user -> target scope -> reference reads/write. Active definition writers already lock their permission parents, then ACTIVE referenced scope masters; verify these shared statements when testing the scope deletion race. Q23 removal may skip a closed master and can only reduce usage. A definition with non-DELETED status blocks master delete/archive even if its permission parent is closed/deleted; no JOIN may hide usage. INACTIVE/LOCKED and ordinary code/name/description updates keep links unchanged. No reserved-scope rule or code immutability is introduced.

API21 verification before integration: seven SQL definitions across nine exact executed-note occurrences; 20 terminal structural traces. Isolated mutations caught 72/72; synchronized SQL semantic faults 11/11; reordered flow/native whitespace/legacy/render faults 8/8 (including a real PlantUML leading-quote omission and one missing repeated SQL line): 91 negative cases. SVG/PNG inspected with 76/76 SQL lines visible. Exact PostgreSQL scope lifecycle/code uniqueness/editability/audit/rollback/result guards and user/token/target lock waits pass. Actual delivered permission-writer parent/master/duplicate/INSERT SQL serializes both new-link/master-delete race orders correctly. Backend/HTTP/JWT cryptographic conformance and unmigrated writers are excluded.

Initial full suite passed all 59 documentation commands, audit 53/0 and database tests but failed the skeleton suite on the copied execution-hint BEGIN count. Root cause was reproduced; only prose was rephrased, all SQL and the completed sequence remain unchanged, and both the unchanged skeleton suite (12 tests) and the entire 59-command/audit/database/preflight suite now pass. The expired old runtime process id is separately explained in lessons; its durable SQL log already contained complete passing evidence.

Pending owner Q24: permission 04/05 currently permit a DELETED parent to retain non-DELETED scope definitions, while the parent can no longer be edited and those definitions still block scope delete/archive under A14. Ask whether final parent deletion must require all definitions withdrawn (409 E10006 otherwise, same-request complete withdrawal allowed). This is not yet approved and would require separate API04/API05 PRs. Scope API21 preserves the already-approved non-DELETED usage guard; no parent-status bypass or cascade is introduced. Consent-management Q18/Q19 also remain pending.

API21 integration: fetched origin/main 014380a906c7b2f571cfddf5f19e049e2b669642, which includes merged inquiry PR82. Resolve checker/task/lesson conflicts from whole current-main content plus only scope-upsert-flow, API07 expectations and API21 records; retain incoming reference improvements. All 164 existing function bodies are identical except bounded author_needles changes, all author_counted outputs and unaffected master expectations are identical, and COMMANDS is exactly 59 -> 60. API06 pair is byte-identical to main; API07 pair equals the verified task commit. Seven owned files differ. On the combined tree all 60 documentation commands, audit 53/0, database ALL PASSED, 12 skeleton tests, 72 isolated + 11 synchronized + 8 flow/strict/legacy/render faults, actual scope/reference-writer SQL fixtures and 76/76 visible SQL lines pass. API20 delivery checkbox is reconciled using verified 6f6eecc ancestry in main. Q18/Q19/Q24 remain unanswered and no dependent business behavior is implemented.

## e-commerce: Peter Q24 follow-up — batch permission delete (2026-11-09)

Authority: Q24 owner answer “ต้องถอน links ให้ครบก่อนลบ permission (แนะนำ)”. Single API04 is delivered in open PR85; its branch/history are preserved under Q15 and this independent author/05 task starts from current main after 60 documentation baselines plus audit/database. Preserve Q22/Q23, indexed error precedence, HTTP 200 ordered results and full batch atomicity. No schema/backend work.

- [x] Prepare the bounded main-based assignment and persist Q24 approval identically to the single-API PR.
- [x] Reproduce the old batch gap and make the Q24-aware focused checker reject the old pair before artifact edits.
- [x] Update spec/sequence together: final current-permission count, indexed 409, whole-batch rollback, complete withdrawal examples and unchanged SQL.
- [x] Execute exact SQL fixtures for final-state cases, earlier-item/audit rollback, request-order behavior and parent-lock races; mutation-test and render/count visible SQL.
- [ ] Integrate latest main, preserve unrelated functions/APIs, run full verification/preflight and open one batch-API PR without merging.

Batch Q24 evidence: the Q24-aware checker rejected the old pair before editing. Exact-SQL reference execution reproduced the old retained-definition deletion and indexed 404 on later cleanup. The new rule rejects omitted/empty/partial withdrawal, a newly added surviving link and every non-DELETED definition/closed-master state. Later-item failure returns no result and restores earlier inserted/updated parents, child links and all audit columns. Complete same-request withdrawal, zero definitions and DELETED-only history return ordered 200 DELETE actions; archive retention and Q22/Q23 remain valid. Actual parent-lock races pass in both orders; existing mixed/all-delete/100-item, credential wait, owner/immutable/reference, unique and SQL-failure fixtures remain green.

Negative verification: 94 isolated mutations, 10 synchronized SQL semantic faults, 4 phase reorderings and 22 Q24 guard/index/example faults all rejected (130 total). The initial 93/94 miss was corrected by anchoring the entire Q22 finality clause; skill guidance and lessons record its prevention. Q24 SQL-only definition parity stays exact; the combined generic CLI additionally rejects transaction-closure faults. All 16 SQL definitions and 19 occurrences are unchanged. Rendered SVG/PNG inspected, with SQL 141/141 visible lines. Backend/HTTP/JWT implementation conformance and unmigrated writers are outside this reference verification.
## e-commerce: Peter Q24 follow-up — single permission delete (2026-11-09)

Authority: owner answered Q24 “ต้องถอน links ให้ครบก่อนลบ permission (แนะนำ)”; preserve Q22/Q23 and one API pair per PR. Scope PR83 is merged and the managed clone was returned to main with its branch/history retained. New main-based assignment passed all 60 documentation baselines plus audit/database. This task updates only author/04, its checker/approval/task evidence and required preventive guidance; author/05 is the next independent PR. No schema/backend implementation.

- [x] Prepare the clean assignment and persist the exact Q24 approval, final-state semantics, no-cascade rule and separate batch delivery scope.
- [x] Reproduce rejection of the old contract with a Q24-aware checker before changing the endpoint pair; record the legacy allowed delete/retained-link behavior.
- [x] Update spec/sequence together: after all child writes reuse the final definition count; reject a DELETED parent with a positive count, roll back everything and preserve same-request complete withdrawal. Retain all existing SQL definitions unchanged.
- [x] Verify concrete zero/one/many and closed/legacy definition cases, partial/full withdrawal, archive, grant/reference guards, audit rollback and deletion-vs-writer ordering; mutation-test the final guard and inspect the rendered diagram.
- [ ] Integrate current main preserving every unrelated API/checker, run all required checks/preflight and publish one single-API PR; proceed immediately to the batch Q24 PR under Q15.

Single Q24 evidence: approved-policy checker rejected the old pair before artifact edits. The unchanged SQL with legacy reference orchestration reproduced a deleted parent retaining a live definition and a later 404 cleanup attempt. New reference execution rejects every non-DELETED definition state, closed master, omitted/empty/partial withdrawal and newly inserted link on delete; all failures restore parent, children and audit. Complete same-request withdrawal and DELETED-only history permit 204; archive retention stays valid. Actual parent-lock races serialize definition creation versus deletion in both orders. Existing Q22/Q23/ref/unique/current-credential fixtures remain green.

All 60 documentation commands, audit 53 tables / 0 findings, database ALL PASSED and 12 skeleton tests pass. Mutations reject 67 regressions, 10 synchronized SQL semantic faults and 16 Q24 guard/phase/example faults (93 total). Q24 cases preserve exact SQL definition coverage; the combined generic checker additionally rejects missing rollback, as correctly reported by layer. All 16 SQL definitions and 19 diagram occurrences are unchanged from the pre-Q24 contract. SVG/PNG inspected and counted SQL is 139/139 visible lines. Batch API05 remains explicitly outstanding for its separate Q24 PR.

## e-commerce: Peter permission and Allow Scope matrix (2026-11-09)

Authority: owner requested `permission-scope.md`, API allowlists with spec links, then clarified “เพิ่ม section ขึ้นมา ประมาณว่า Allow Scope แล้วใส่ชื่อ scope มา”. Produce the reviewable cross-API design before individual endpoint rollout. Persist the already-answered Q18/Q19. Owner subsequently requested `<scope-name>:<allow, deny, อื่นๆ>` and approved same-permission/same-resource deny precedence with “ใช่ deny ชนะเมื่อครอบคลุมข้อมูลเดียวกัน (แนะนำ)”. Use ALL/SHOP/OWN with lowercase allow/deny; other effects remain undefined. New permission pairings remain in-review; this task does not approve delegated grants, seed changes, backend enforcement or WP5b implementation. API spec/sequence changes continue one API per PR under Q15.

- [x] Prepare the bounded documentation assignment from clean current main and run the 60 documentation, audit and DB baselines.
- [x] Inventory all 83 endpoint specs, existing ALL/SHOP/OWN scope codes and seven seeded permissions; identify the 40 queued endpoints and special authorization branches.
- [x] Write permission-scope.md with Allow Scope, reverse API allowlists and direct spec links; distinguish existing gates, seed definitions, proposed pairings and rollout status.
- [x] Persist Q18/Q19 and the requested per-API Allow Scope section format, preserving owner/shop/public/webhook exceptions.
- [ ] Verify complete endpoint coverage, links, exact route names, permission-specific pairs, seed parity, special cases and unchanged API pairs; integrate latest main and publish the documentation PR.

Matrix verification: all 83 route headings and forward matrix entries are unique and agree with the real API methods/paths; every local spec/source link resolves. The 40 queued endpoints and all special operation/field exceptions match the reviewed inventory. Seed is unchanged at 3 scope codes, 7 permissions and 12 definitions. The proposal groups 11 permissions (4 new) and flags missing definitions; it does not claim grants or effect storage already exist. Eight in-memory document faults are rejected; eight reference deny-overlap cases pass, including cross-permission isolation and nonmatching SHOP denies. Metadata-bearing and legacy specs both parse. All 5 authored Markdown frontmatters parse via Ruby YAML. All 60 documentation commands, audit 53/0, database ALL PASSED and 12 skeleton tests pass. Every API spec/sequence, checker function, SQL and seed remains unchanged. No backend/HTTP/JWT effect enforcement is implemented or certified.

Two authoring-tool failures were corrected before delivery: the route parser initially assumed line 1 and the mutation harness initially chose a public row for a scope effect edit. Both corrected scenarios were rerun across the full inventory; reusable prevention is in the API reference and incident records in lessons. Q18/Q19 and the approved notation/deny decision are now persisted in the governing review document. The API section format is recorded for subsequent one-API paired revisions; this cross-API document does not claim all 83 endpoint sections were already changed.

### PR88 review revision — four-part Allow Scope

Owner request: management:user:read:allow and management:user:crud:deny. Resume the same assignment/PR without force-push; replace the active two-part display throughout the matrix, examples, section guide and traceable decision record. Keep endpoint/seed/JWT behavior unchanged and preserve all 83 links and 40 queue markers.

- [x] Verify PR88 is OPEN at the published head and resume its original scoped assignment with full fresh baselines.
- [x] Rewrite forward/reverse mappings with module:resource:action:effect; separate ALL/SHOP/OWN boundaries and explain CRUD includes read under deny precedence.
- [x] Verify every route/rule/link and action-group example, update preventive guidance/lessons, integrate latest main and update the same PR with an ordinary push.

Four-part revision verification: 83 API entries, 40 queued markers and 33 exact module:resource:action:effect allow-rule groups agree in both mapping directions. All local links and five YAML frontmatters pass. Nine in-memory document faults, 13 CRUD/action/namespace/boundary reference cases and five malformed/unknown rule cases pass; the user's read:allow + crud:deny example returns deny. The old two-part notation is marked historical in the owner-decision record and removed from the active matrix. All 60 documentation commands, audit 53/0, database ALL PASSED and 12 skeleton tests pass. API pairs, checkers, SQL, seed and schema are unchanged. This proves the document/reference semantics only, not backend/JWT storage or enforcement.

## repository-wide: GitHub Actions workflow that runs every check (M3)

Status: Written in the managed workspace of Marry on branch `ci/marry-github-actions-checks`; the first real run is the pull request itself. Scope: `.github/workflows` and `tasks/`. Authorized by the owner through the lead (2026-11-11). No secret is used.

- [x] One workflow, `.github/workflows/checks.yml`, job `checks`, on `pull_request` and on `push` to `main`, with `permissions: contents: read` and one run per pull request at a time.
- [x] Python 3 (3.12) and PostgreSQL 17 (the major version `run_db_tests.sh` was written against) from the PostgreSQL apt repository, plus the `en_US.UTF-8` locale. `run_db_tests.sh` starts its own throw-away cluster from `initdb`, `pg_ctl` and `psql` on the PATH, so a database service container would not be used by it.
- [x] Steps: every sub-command of `check_docs.py` (the list is read from the script, not written in the workflow; the step fails when the list is empty), `audit_all.py`, `run_db_tests.sh`, `test_sequence_skeleton.py` and `test_agent_workspace.py`; each step after the first runs even when an earlier one failed, so one run shows every failure, and the job fails when any step fails.
- [x] The same commands run locally on the tree with `main` merged: 60 sub-commands, 0 failed; audit 0 findings; database tests ALL PASSED; skeleton test OK; workspace test 15 tests OK.
- [x] Real runs on pull request #91: passing https://github.com/ittikornsopawan/system-analysis-and-design/actions/runs/43008956970 (10 steps, 40 seconds); one temporary commit removes the heading `### Cart Rules` from `cart/01` so `cart-spec` fails: https://github.com/ittikornsopawan/system-analysis-and-design/actions/runs/43009141504 failed (only `check_docs.py` red, the other four steps still ran and passed; "60 sub-commands, 1 failed"); the revert commit on the same branch (no force push): https://github.com/ittikornsopawan/system-analysis-and-design/actions/runs/43009341327 passed. The net diff of the pull request is the workflow and `tasks/todo.md`.
- [ ] Tell the lead; the owner sets the branch protection of `main` (required status check `checks`, require branches to be up to date); hold the lock until the merge, then release and park.

## repository-wide: A named agent starts the next task after opening a pull request (M5)

Status: Implemented in the managed workspace of Marry on branch `feat/marry-suspend-assignment-after-pr`; the pull request waits for the merge because it opens this way for the other agents. Scope: `.agents/skills/agent-workspace`, `.agents/rules/named-agent-workspaces.md`, the one sentence of `.agents/skills/commit-and-pr` and `tasks/`. Order of the owner (2026-11-11): a worker who finishes starts the next task without waiting for the merge.

- [x] `suspend --agent --token`: clean task branch, pushed `HEAD`, an open GitHub pull request of the branch with the same head; the assignment moves to `.workspace/.state/<agent>-prs/<branch-slug>.json` (the format of the earlier reviewer records, which are not touched), the workspace returns to `main` and the lock is released.
- [x] `prepare` accepts open pull requests when every one is suspended (one active task as before); `prepare --resume-pr` restores a suspended record (no other active task, fast-forward only); `park --pr` closes a suspended record after the merge is verified, whichever branch is checked out; `status` lists the records.
- [x] Rule, `agent-workspace` skill and one sentence of `commit-and-pr` say so.
- [x] 24 tests (9 new) cover the blocking cases (no pull request, wrong head, dirty, not pushed, wrong token, no lock, resume with another task or with metadata left on main, park before the merge, mismatched head) and 16 mutations are caught.
- [ ] Merge `main`, run every check, push, open the pull request, tell the lead at once, check that `checks` is green.

### Author API08 scope batch — claims, sorted target locks and atomic writes

Authority: owner Q2/Q4/Q7/Q10/Q13/Q15 and the owner-approved lock-before-in-use correction (2026-11-08) relayed by Josh (SA Lead); assignment `authorized_by: josh`, delivery `open-pr`. New Peter session after the previous one ended; workspace recovered and PR88 parked under Josh's approval.

- [x] Recover the managed clone (release stale lock, named stash `peter-owner-scope-note`, park PR88) and prepare a branch from main e361a4b with the audit baseline.
- [x] Revise spec.md and sequence.wsd together: verified JWT roles claim instead of live grants, caller lock and fresh credential gate, one ascending `FOR UPDATE` lock of all target scopes before any in-use check or write, whole-target 404 before one 403, request-order conflicts/writes, indexed results and one final commit.
- [x] Add `scope-batch-flow` (seven exact SQL definitions, 18 representative traces) and move API08 to the claims needles in `author-spec`.
- [x] Mutation-test the checker, render the diagram, and run every documentation command, the SQL audit, database tests and skeleton tests on the branch merged with origin/main.

Scope-batch verification: 35/35 deliberate faults rejected (6 spec rules, 10 synchronized spec+sequence SQL faults, 15 sequence flow faults including permission before the target lock, 3 example faults, 1 rendered omission). PlantUML render shows 66/66 SQL lines. No schema, seed or backend change; SQL was not executed against concurrent PostgreSQL sessions in this task, so lock behaviour is proven by document checks only.
## e-commerce: Spec risks T2 (shipping and campaign)

Status: Complete in the branch, waiting for review. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh` (the product owner approved the changes on 2026-11-08), workspace `.workspace/tommy`, branch `fix/tommy-spec-risks-shipping-campaign`, scopes `shipping/02-update-shipping-status`, `shipping/03-upsert-shipping-stop`, `shipping/06-confirm-delivery`, `campaign/01-upsert-campaign`, `e-commerce/db/tests/check_docs.py` (needles only) and `tasks`.

- [x] `shipping/02` and `shipping/06`: after the order row is locked the shipping row is locked and read again (`QUERY - Lock the shipping`, `FOR UPDATE`) and the status is checked on that read.
- [x] `shipping/03`: the example `Fail - Not Found Shipping` (404 E10004) and the rule sentence.
- [x] `campaign/01`: `QUERY - Check existing campaign shop` and `QUERY - Check existing campaign product` answer 404 for a row id that is not a live row of the campaign; deleting a campaign soft-deletes its discount, shops and products with one statement each.
- [x] Move the diagrams of `shipping/02`, `shipping/06` and `campaign/01`, add the needles to `shipping-spec` and `campaign-spec`, run every checker and the mutation tests.
- [x] Open the PR with `commit-and-pr`; do not merge.

## e-commerce: JWT claims, payment/04 (inquiry shop payment)

Status: Complete in the branch, waiting for review. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `fix/tommy-jwt-claims-payment-04`, scopes `payment/04-inquiry-shop-payment`, `e-commerce/db/tests/check_docs.py` (needles only) and `tasks`. Governing: `docs/superpowers/specs/2026-11-07-api-review-design.md` (Q2, Q4, Q10, Q13).

- [x] Authorization comes from the verified JWT: the platform administrator is the exact role `PLATFORM_ADMIN` in the `roles` claim, the two `author` queries are removed, shop membership stays a database check.
- [x] Add the current credential check (`QUERY - Check active credential and user`), the Allow Scope section (`payment:payment:read:allow`) and the order 400, 401, 404, 403.
- [x] Move the diagram and the needles of `payment-spec`, run every checker and the mutation tests.
- [x] Open the PR with `commit-and-pr`; do not merge. The next API of the queue is `payment/05`.
### Author API09 scope inquiry — claims, credential gate and consistent pagination

Authority: owner Q2/Q4/Q7/Q10/Q13/Q15, assignment `authorized_by: josh`, delivery `open-pr`. Built from the reviewed role inquiry (author/03) with scope-specific fields; Josh asked (PR94 review) for a slim API-specific checker that covers only what parity/lifecycle checks cannot.

- [x] Revise spec.md and sequence.wsd together: verified JWT roles claim, fresh credential gate in a REPEATABLE READ READ ONLY snapshot, one 403 before count/page, identical count/page filters, five-field scope items, scope-then-id order, one COMMIT.
- [x] Add the slim `scope-inquiry-flow` (about 25 lines: no live grants, read-only SQL, identical WHERE, step order, one decision and one COMMIT, rollback before post-BEGIN rejections, exact columns, still in-review) and point `author-spec` needles for API09 at the claims wording.
- [x] Mutation-test, render, and run all documentation commands, audit and database tests on the branch merged with origin/main.

Scope-inquiry verification: 14/14 deliberate faults rejected (including synchronized spec+sequence SQL faults); SQL lines visible in the PlantUML render are counted above. No schema, seed or backend change.

## e-commerce: JWT claims, product/01 (upsert product)

Status: Implemented in the managed workspace of Marry on branch `docs/marry-product-upsert-jwt-claims`; first API of the queue of the lead (product 01, 03, 04, 06, 07, 09, 10, 11, 13, 14 and shop 01, 02, 05, 06, 08-13, one API per pull request). Scope: `product/01-upsert-product`, `e-commerce/db/tests/check_docs.py` and `tasks/`. Governing decisions: Q2, Q4, Q10 and Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`. No Allow Scope mapping is added (the four-part notation is still in review).

- [x] Permission: the platform administrator is the exact role `PLATFORM_ADMIN` in the verified JWT `roles` claim (structured claim of login: array, UUID `roleId`, non-empty `name`, unique ids; missing or malformed is 401, no empty-role fallback). `QUERY - Get the platform administrator role` and `QUERY - Check platform administrator` are removed from the spec and the diagram; a change of the assignments does not change an issued token (up to 15 minutes).
- [x] Order: validate (400) -> verify the JWT and its `roles` claim (401) -> BEGIN, `QUERY - Lock the caller user` (`FOR UPDATE`), fresh `now`, recheck of the JWT expiry, `QUERY - Check current credential and user` (401) -> existence checks (404) -> permission from the claim (403, E10009) -> conflicts (409) -> writes -> COMMIT. SQL of the two new blocks is the SQL of `author/08`.
- [x] `admin-write-spec`: `ADMIN_WRITE_JWT_CLAIMS` lists the migrated specs; they must carry the claims rule, the two new blocks and the order text, must not carry the old queries, and their diagram must run BEGIN -> lock -> credential -> existence -> claims permission -> conflict -> write and must not read the author tables. Other specs are unchanged.
- [x] Proof: 12 mutations of the spec, the diagram and the new order caught (one first miss because a phrase stood in two places; each place has its own needle now), control passes; PlantUML passes and all 457 SQL lines are drawn; 62 sub-commands, audit and skeleton test pass.
- [ ] Merge `main`, run every check, push, open the pull request, tell the lead at once, suspend the assignment, check that `checks` is green.

## e-commerce: JWT claims, sales/05-cancel-order

Status: Complete in the branch, waiting for review. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `fix/tommy-jwt-claims-sales-05`, scopes `sales/05-cancel-order`, `e-commerce/db/tests/check_docs.py` (needles only) and `tasks`. Governing: `docs/superpowers/specs/2026-11-07-api-review-design.md` (Q2, Q4, Q10, Q13).

- [x] The platform administrator is the exact role `PLATFORM_ADMIN` in the verified `roles` claim, the two `author` queries are removed, shop membership stays a database check.
- [x] Add the current credential gate, the Allow Scope and the order 400, 401, 404, 403; move the diagram and the needles, run every checker and the mutation tests.
- [x] Open the PR with `commit-and-pr`, tell the lead SA when CI is green, then suspend. Next: `shipping/01`.

### Author API10 user role upsert — claims, user/role/assignment locks and last-administrator protection

Authority: owner Q2/Q4/Q7/Q10/Q13/Q15 and the owner-approved technical corrections of 2026-11-08 (target-row `FOR UPDATE` before checks, 404 E10005 for a missing target user) confirmed by Josh (SA Lead); assignment `authorized_by: josh`, delivery `open-pr`. Slim API-specific checker as Josh asked.

- [x] Revise spec.md and sequence.wsd together: verified JWT roles claim instead of the two live-admin queries, caller+target user lock in ascending id order, fresh credential gate, role lock, assignment lock before duplicate/write, 404 E10005 for a missing target user (also when taking the role away), one 403, guarded write with bound time, administrator count on the final state, one COMMIT.
- [x] Add the slim `user-role-upsert-flow` and move the `author-spec` needles of API10 to the new contract.
- [x] Mutation-test, render, and run every documentation command, audit and database tests on the branch merged with origin/main.

User-role verification: 21/21 deliberate faults rejected (including synchronized spec+sequence SQL faults); PlantUML render shows 73/73 SQL lines. No schema, seed or backend change; locking is proven by documents and checkers only.
## e-commerce: JWT claims, sales/04-inquiry-shop-order

Status: Complete in the branch, waiting for review. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `fix/tommy-jwt-claims-sales-04`, scopes `sales/04-inquiry-shop-order`, `e-commerce/db/tests/check_docs.py` (needles only) and `tasks`. Governing: `docs/superpowers/specs/2026-11-07-api-review-design.md` (Q2, Q4, Q10, Q13).

- [x] The platform administrator is the exact role `PLATFORM_ADMIN` in the verified `roles` claim, the two `author` queries are removed, shop membership stays a database check.
- [x] Add the current credential gate, the Allow Scope and the order 400, 401, 404, 403; move the diagram and the needles, run every checker and the mutation tests.
- [x] Open the PR with `commit-and-pr`, tell the lead SA when CI is green, then suspend. Next: `sales/05`.
## e-commerce: api-sequence-spec fails a note line that starts with a bare quote (M4)

Status: Implemented in the managed workspace of Marry on branch `test/marry-reject-bare-quote-sql`. Scope: `consent/02-upsert-consent`, `06-upsert-consent-type`, `07-upsert-consent-type-batch`, `e-commerce/db/tests/check_docs.py` and `tasks/`. The lead chose option (A) and confirmed that the new reviewer does not touch these three files.

- [x] Rule: inside a PlantUML note, a line that starts with a bare quote (after the indentation) is drawn as a comment, so the SQL line is missing from the picture; the checker fails it and says to write `&#39;`. It applies to every non-empty diagram, the legacy ones included. A real comment line outside a note is not flagged.
- [x] Re-scan of `main` (4796ac2): 21 such lines were left, all in `consent` (`02` 11, `06` 5, `07` 5); `authen-and-author/09` had been fixed already. The 21 lines are written `&#39;`; only the encoding changes, no SQL and no spec.
- [x] Proof: mutations 5 of 5 caught (a bare quote put back in `cart/01`, `cart/02` and the three consent diagrams) and one control passes; PlantUML `-checkonly` passes for the three diagrams and every SQL line appears in the picture at least as often as in the spec.
- [ ] Merge `main`, run every check, push, open the pull request, tell the lead at once, suspend the assignment, check that `checks` is green.
## e-commerce: JWT claims, payment/05 (refund payment)

Status: Complete in the branch, waiting for review. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `fix/tommy-jwt-claims-payment-05`, scopes `payment/05-refund-payment`, `e-commerce/db/tests/check_docs.py` (needles only) and `tasks`. Governing: `docs/superpowers/specs/2026-11-07-api-review-design.md` (Q2, Q4, Q10, Q13).

- [x] The platform administrator is the exact role `PLATFORM_ADMIN` in the verified `roles` claim, the two `author` queries are removed, shop membership stays a database check.
- [x] Add the caller lock and the current credential gate after `BEGIN` (lock order: caller user, order row, lots by id, budgets by id), the Allow Scope (`payment:payment:refund:allow`) and the order 400, 401, 404, 403, 409.
- [x] Move the diagram and the needles of `payment-spec`, run every checker and the mutation tests.
- [x] Open the PR with `commit-and-pr`, tell the lead SA when CI is green, then suspend. Next: `sales/04`.

### Author API11 user role inquiry — claims, credential gate and consistent pagination

Authority: owner Q2/Q4/Q7/Q10/Q13/Q15, assignment `authorized_by: josh`, delivery `open-pr`. Derived from the delivered scope inquiry (author/09) with user-role joins and filters; slim API-specific checker.

- [x] Revise spec.md and sequence.wsd together: verified JWT roles claim, credential gate in a REPEATABLE READ READ ONLY snapshot, one 403 before count/page, count and page with identical joins and bound nullable filters (id/userId/roleId/rowStatus), six-field items, role name/user display name/id order, one COMMIT; remove the two live-admin queries.
- [x] Generalize the slim inquiry check into `author_inquiry_flow` (now also compares FROM/JOIN) and add `user-role-inquiry-flow`; update the `author-spec` needles and counted filter lines for API11.
- [x] Mutation-test, render, run every documentation command, audit and database tests on the branch merged with origin/main.
- [ ] Open question for the SA Lead: two JWT wording defects in the delivered author/09 (spec lines "verify JWT/scopes (401)" and "verified token scopes") need a separate scoped fix; see the lesson of 2026-11-12.

User-role-inquiry verification: 16/16 deliberate faults rejected (including synchronized spec+sequence faults and the damaged JWT wording); PlantUML render shows 40/40 SQL lines. No schema, seed or backend change.
### Author API09 wording fix — JWT statements said scopes instead of roles

Authority: SA Lead (Josh) approved this one-folder fix after Peter reported two defects introduced in PR #95; assignment `authorized_by: josh`, delivery `open-pr`. Behaviour, SQL and sequence are unchanged.

- [x] Correct `verify JWT/scopes (401)` and `verified token scopes` to roles in `author/09-inquiry-scope/spec.md`.
- [x] Guard both phrases in `scope-inquiry-flow`; mutation: both reverted phrases are rejected (2/2).
- [x] Run every documentation command, audit and database tests on the branch merged with origin/main.

## repository-wide: park of a suspended assignment accepts a branch the owner updated

Status: Implemented in the managed workspace of Marry on branch `fix/marry-park-suspended-ancestor`. Scope: `.agents/skills/agent-workspace` and `tasks/`. Approved by the lead after the first real use of `suspend` (park of PR 99 blocked).

- [x] Cause: the owner presses "update branch" on GitHub, so the merged head is ahead of the local branch of a suspended task; `resume` accepted a fast-forward but `park` of the suspended record blocked with "local task branch does not match the merged pull-request head".
- [x] Fix: when the local branch differs from the merged head, `park` fetches the merged head (the branch, or `refs/pull/<n>/head` when the branch was deleted) and accepts the local branch only when it is an ancestor of the merged head; a diverged branch blocks as before and keeps the record and the branch. The remote branch may equal the merged head.
- [x] Tests: 26 (2 new): a branch the owner updated is parked, a diverged branch blocks and is kept; 3 of 3 mutations caught (the ancestor test, the fetch and the remote tolerance). A fourth check (the fetched ref equals the merged head) was removed because the ancestor test already fails without the object.
- [ ] Merge `main`, run every check, push, open the pull request, tell the lead at once, suspend, close the record of PR 99 with the fixed script.

## e-commerce: spec template, cart

Status: Complete in the branch, waiting for review. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `docs/tommy-spec-template-cart`, scopes `e-commerce/doc/api/cart`, `e-commerce/db/tests/check_docs.py`, `tasks`.

- [x] Remove `### Cart Rules` (cart/01, cart/02) and `### Availability Rules` (cart/03) from the specs; the rules become short bullets under `## Domain`; the `####` object headings stay (confirmed by the lead SA).
- [x] Move the order of the checks, the lock and the merge details into a note of `sequence.wsd` (cart/01, cart/02); no SQL and no behavior is changed.
- [x] Adjust the needles of `cart-spec`; run every checker, strict SQL parity and the render check.
- [x] Open the PR with `commit-and-pr`, tell the lead SA when CI is green, then suspend. Next: `payment`.

## e-commerce: spec-template checker and guidance (M6)

Status: Implemented in the managed workspace of Marry on branch `test/marry-spec-template-checker`. Scope: `e-commerce/db/tests/check_docs.py`, `.agents/skills/api-contract-design` (SKILL.md, references, the snapshot of the template), the guidance sentence of `e-commerce/doc/api/template.md` and `tasks/`. Owner decision of 2026-11-13 given by the lead; the JWT work per API is paused until the template is in place.

- [x] `check_docs.py spec-template`: a `spec.md` has only the `##` and `###` sections of `template.md` (`Domain`, `Request Parameters` with Header/Path/Query/Body Parameters, `Example Request` with HTTP/cUrl Request, `Response Parameters` with Status Object, Data Object and Example Response Parameters, `Database Relations` with `### Table: [...]`, `External Services` with `### API: ...`); `####` and `#####` are free; text inside code fences is not read.
- [x] Links only to schema docs (`../../../schema/...`), external `http(s)` URLs and anchors that match a heading of the same file; a link to a design document, `permission-scope.md` or another spec fails, and so does an anchor to nothing.
- [x] `LEGACY_SPEC_TEMPLATE`: the specs that do not pass are named (73 of 83 when measured, 68 after the five payment specs fixed on `main` meanwhile left the list); an entry must be a spec folder and must still fail, so a spec that passes leaves the list in the same change; the OK line prints how many are left. The work of fixing product and shop specs follows this pull request.
- [x] Guidance: one sentence in `template.md` (and its snapshot `assets/api-spec.md.tmpl`), the new section "Template sections and links" in `references/spec-structure.md`, the correction of the two passages that told authors to add `### ... Rules` and `### Allow Scope` sections, and the rule "ask the owner before adding a section" in `SKILL.md`.
- [x] Mutation tests: 9 of 9 caught (an extra `###` and `##` section, a link to another spec, to a design document and to `permission-scope.md`, an anchor to nothing, an entry removed from, added to and invented in the list) and 5 controls pass (`####` and `#####` headings, an own anchor, an external URL, a schema link).
- [ ] Merge `main`, run every check, push, open the pull request, tell the lead at once, suspend, then close the records of PR 99 and 107 with the script on `main`.

### JWT payload contract — new access-token claims in login, refresh, me and the permission matrix

Authority: owner decision of 2026-11-13 relayed by Josh (SA Lead): "ใช้รูปแบบใหม่แทน" with the payload `iss`, `sub`, `aud`, `jti`, `iat`, `exp`, `user`, `roles` (names), `permissions` (`resource:action`), `scopes` (`type:value`), and the owner's answer "ตามคำแนะนำทั้ง 4 ข้อ" on permission naming, scope value, Q12 and deny; assignment `authorized_by: josh`, delivery `open-pr`. One outcome (the payload contract) across the three APIs that issue or report it and the matrix.

- [x] Record the decision and the 2026-11-13 consent/02 answers in `api-review-design.md`; mark the Allow Scope four-part and deny-wins text superseded.
- [x] login/02 and refresh/05 (spec + sequence): map roles to names, permissions to names with the last `.` as `:`, scopes to `<lower-case code>:*`, add the `user` snapshot (the user lock now returns `username`, `email_address`, `display_name`), keep Q12 in the resolution, new example payload.
- [x] author/12-me: roles claim is unique non-empty strings; `data.roles` is an array of role names (roleId removed because the token no longer carries it; pending confirmation).
- [x] permission-scope.md: rules converted to permission claims (`module.resource:action`) and scope claims (`all:*`, `shop:*`, `own:*`); deny and deny-wins removed; 83 links and 40 queue markers kept.
- [x] Update the login payload check, the me checks and the refresh/login needles; mutation 15/15; render 116/116, 131/131 and 13/13 SQL lines.
- [ ] Outstanding by design: every other spec, sequence and checker that still says roles are `{roleId, name}` objects (author 01–11, consent, payment, sales, product, shop) — each analyst corrects their group during the template work.
## e-commerce: spec template, payment

Status: Complete in the branch, waiting for review. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `docs/tommy-spec-template-payment`, scopes `e-commerce/doc/api/payment`, `e-commerce/db/tests/check_docs.py`, `tasks`.

- [x] Remove `### Payment Rules`, `### Webhook Rules`, `### Refund Rules`, `### Payment Inquiry Rules`, `### Shop Payment Inquiry Rules` and the two `### Allow Scope` sections; the rules become short bullets under `## Domain`; remove the links to the design doc, login and permission-scope.
- [x] Move the JWT checks, the lock order, the Idempotency-Key, the failed `COMMIT`, the state table of the webhook and the order of the checks into a note of `sequence.wsd`; no SQL and no behavior is changed.
- [x] The `payment-spec` and `campaign-spec` checkers search the spec and its sequence note; adjust the needles; run every checker, strict SQL parity and the render check.
- [x] Open the PR with `commit-and-pr`, tell the lead SA when CI is green, then suspend. Next: `sales`.

## e-commerce: spec template, shipping

Status: Complete in the branch, waiting for review. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `docs/tommy-spec-template-shipping`, scopes `e-commerce/doc/api/shipping`, `e-commerce/doc/api/payment`, `e-commerce/db/tests/check_docs.py`, `tasks`.

- [x] Remove the six `### ... Rules` sections of shipping/01 to 06, `### Automatic Completion Rules` and `### Automatic Completion Example` (a bold label with its table under `## Domain`); the rules become short bullets under `## Domain`; the design doc path becomes plain words.
- [x] Move the order of the checks, the lock details, the job scan and the clashes into notes of `sequence.wsd`; no SQL and no behavior is changed.
- [x] The roles claim sentences of the payment notes (`payment/04`, `payment/05`) follow the new JWT payload (role names).
- [x] The `shipping-spec` checker searches the spec and its sequence note; adjust the needles; the shipping files, and the sales and authen-and-author files that already follow the template, leave `LEGACY_SPEC_TEMPLATE`.
- [x] Open the PR with `commit-and-pr`, tell the lead SA when CI is green, then suspend. Next: `campaign`.

### Template alignment — authen-and-author group (10 specs)

Authority: owner decision that API specs follow `e-commerce/doc/api/template.md`, relayed by Josh (SA Lead); assignment `authorized_by: josh`, delivery `open-pr`; same rules as the cart group (PR #106) and payment (#108). No SQL and no behaviour change.

- [x] Remove every `### ... Rules` section and the `####` blocks that are not objects or examples (Scenario correspondence, Acceptance criteria, Claim resolution); keep `#### Example Body Parameters`, the objects and the examples; move `#### Example JWT Payload` under `### Example Response Parameters` in login.
- [x] Short bullets under `## Domain` (first sentences of the removed rules, links turned into text) and a rendered note with the order of the checks and the lock order in every sequence.
- [x] The full removed rule text stays in each `sequence.wsd` as a PlantUML comment block (`' --- Rules moved ...`); `read()` in `check_docs.py` returns a spec together with that block, so every existing needle keeps protecting the rules without changing any flow check.
- [x] Verify: headings and links of the 10 specs, all 64 documentation commands, audit, database tests, render of the 10 diagrams (all SQL lines visible), mutation of the moved text (4/4).
- [ ] Open for Marry's `spec-template` checker: take the ten files out of its exception list when it merges.
## e-commerce: spec template, sales

Status: Complete in the branch, waiting for review. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `docs/tommy-spec-template-sales`, scopes `e-commerce/doc/api/sales`, `e-commerce/db/tests/check_docs.py`, `tasks`.

- [x] Remove `### Checkout Rules`, `### Order Rules`, `### Order Inquiry Rules`, `### Shop Order Inquiry Rules`, `### Cancel Rules`, `### Discount Example` and both `### Allow Scope` sections; the rules become short bullets under `## Domain` (the worked discount example is a bold label with its table under `## Domain`); remove the links to the design doc, login and permission-scope.
- [x] Move the JWT checks, the lock order, the Idempotency-Key, the budget and stock updates and the order of the checks into a note of `sequence.wsd`; no SQL and no behavior is changed.
- [x] The roles claim sentences follow the new JWT payload (role names), as recorded in the API review design.
- [x] The `order-spec` checker searches the spec and its sequence note; adjust the needles; run every checker, strict SQL parity and the render check.
- [x] Open the PR with `commit-and-pr`, tell the lead SA when CI is green, then suspend. Next: `shipping`, with the roles sentence of the payment notes.

## e-commerce: product/01-03 follow the spec template (template PR1)

Status: Implemented in the managed workspace of Marry on branch `docs/marry-product-spec-template`. Scope: `product/01-upsert-product`, `02-inquiry-product`, `03-upsert-product-batch`, `check_docs.py` and `tasks/`. First of six template pull requests of the lead (product 01-03, 04-09, 10-15, shop 01-04, 05-10, 11-16).

- [x] Measured with `spec-template`: product/02 and 03 already pass it (never listed); product/01 failed only on two links (the review design document and the login spec). 02 is unchanged. 03 has a `#### Permission Rules` section, which the checker allows but the owner's intent removes: on the review of the lead its permission and order text moved the same way as product/01 (a short Domain bullet in the spec, a visible note in its diagram) while it keeps the live role queries (its JWT migration is paused).
- [x] product/01: the `#### Permission Rules` section and the long "Execution order" bullet leave the spec; two short bullets under `## Domain` say who may call it (the exact role `PLATFORM_ADMIN` in the verified `roles` claim, now an array of role names as in the new login payload; never the author tables; 401 for a missing or malformed claim; approval Q2, Q4, Q10, Q13) and that the caller is locked first; the order of the checks and the locks is a visible `note over app, infra` in the diagram at the step where it starts (no PlantUML comment). The two links are gone. SQL is unchanged.
- [x] `admin-write-spec` for the migrated spec checks the new Domain wording and the order text directly in `sequence.wsd` (the JWT step, the lock, the claims permission, the author tables), and needs E10009 twice (rule and example).
- [x] `LEGACY_SPEC_TEMPLATE`: product/01 and 15 entries that passed on `main` (authen 01-10 and sales 01-05, fixed by other pull requests) are removed; 52 remain.
- [x] Proof: 9 of 9 mutations caught (each phrase of the diagram note and of the Domain bullets, an added `### Permission Rules`, a link to another spec and to the design document); 65 sub-commands pass; PlantUML passes and the note is drawn.
- [x] Review of the lead: product/03 done the same way (needles of `admin-write-spec` for it now check its diagram, `ADMIN_WRITE_RULE_IN_DIAGRAM`), 8 of 8 mutations caught.
- [ ] Merge `main` (the lead's pull request that also prunes the list lands first; keep its result), run every check, push, tell the lead, suspend.
