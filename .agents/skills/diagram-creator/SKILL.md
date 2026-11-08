---
name: diagram-creator
description: Create, update, or review architecture, repository, domain, sequence, lifecycle, and operational diagrams from specifications, code, or database evidence, with editable artifacts and source-linked explanations.
---

# Diagram Creator

Turn inspected evidence into diagrams that answer different engineering questions. Preserve the user's requested paths and formats. This skill owns evidence, view semantics, reproducibility and review; an available `diagram-design` skill supplies visual language and rendering conventions when requested or useful.

## Establish the drawing contract

1. Identify the audience, question, source baseline and requested outputs. For existing diagrams, inspect both the render and editable model before changing them; account for meaningful nodes and relationships that will be retained, split or omitted.
2. Read [viewpoints](references/viewpoints.md) when selecting or comparing views, decomposing layers, or changing notation. Write a short plan per diagram: question, notation, ownership hierarchy, edge meaning, evidence status and deliberate cuts. Multiple diagrams must have distinct questions and reading paths.
3. Resolve project style from existing assets/profile or the requested visual skill. Reuse an already selected style. Complete a visual skill's required first-use choice only when it is unresolved. Choose detail and canvas for readability; split a dense view into overview and focused views when necessary.

The contract is complete when every view has a stated purpose and each meaningful element can be traced to inspected evidence or explicitly identified as a proposal. A diagram title alone does not establish its semantics.

## Build from evidence

- Cite file paths and relevant sections, source revisions or a reproducible inventory. Separate implemented behavior, approved design, unapproved specification and proposed capability with a visible legend; apply status to the affected element or relation, not merely the page footer.
- For repository views, inspect actual source trees, project references and test dependencies. For runtime views, inspect entrypoints, dispatch, handlers, ports, adapters and transaction boundaries. A compile-time reference is different from a runtime call.
- For diagrams derived from SQL/DB, read [database-domain](references/database-domain.md) before extracting concepts, cardinalities or ownership. Keep conceptual modeling distinct from the physical ER/schema maintenance workflow.
- For layered structural views, draw actual child components inside their owners. Application may contain Command/Query, Validator and Handler; inspect their existence/status rather than turning a list of names into implied implementation. Preserve project terminology for reusable business logic and distinguish it from application orchestration.
- Record uncertainty and contradictions. Drawing a proposal does not approve implementation. Follow the repository's approval workflow for changes to architecture, behavior, APIs or data; use the corresponding ready skill for those changes.

Proceed when labels, boundaries, relationships and status are supported; resolve product decisions with the owner while continuing independent evidence work.

## Produce editable, reproducible artifacts

Read [artifacts and review](references/artifacts-and-review.md) when creating/exporting diagrams, moving generators, or delivering editable PNGs. Keep each requested diagram bundle together; store project generators/content outside the artifact folder and reusable helpers in this skill's `scripts/`.

For a native draw.io bundle, retain `.drawio`, editable `.drawio.png`, and the requested explanation. Include `.html`/SVG when used as the reproducible preview source. Adapt [the companion template](assets/companion.md.tmpl) to explain purpose, reading order, source status, decisions and limits; omit sections that do not apply.

Use native parent/child cells for hierarchy so moving a container in the editor moves its children. Keep connectors editable. Sequence, lifecycle, physical entity and deployment views retain their own notation even when they include nested groups.

## Verify before delivery

1. Reconcile sources with the model: components, directions, guards, cardinalities, status, omitted relationships and coverage. Run project evidence/generator checks where available.
2. Check native integrity with `python3 -B <skill>/scripts/verify_diagram.py <source.drawio> <image.drawio.png>`. Add `--require-nested` for views whose contract requires real containment. Read `--help` for optional same-renderer roundtrip and size checks. These checks establish metadata/model integrity; they do not establish visual quality or business correctness.
3. Open every final render at a readable scale. Check wrapping, clipping, contrast, hierarchy, arrow direction, label/connector collisions and margins. Compare the set for genuinely distinct viewpoints. Reopen an editable artifact in draw.io and, for significant hierarchy work, move a container and confirm child/connector behavior. Re-export with the same renderer settings when checking pixel parity. Correct defects and repeat affected checks.
4. For a code/path refactor, compare pre/post `.drawio` and PNG hashes and run all consumers. Update generated links, source commands and output routing together. A successful import alone is insufficient.

Complete only when requested outputs exist, meaningful content is accounted for, applicable checks pass, and final visual review is recorded. Report exact paths, evidence baseline, verification, cuts and unavailable checks. Delivery/PR actions follow the user's or assignment's existing authorization; this skill grants none.
