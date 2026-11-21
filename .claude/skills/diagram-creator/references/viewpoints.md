---
name: Diagram Viewpoints
description: Select and review diagram meaning before layout when creating multiple views or decomposing structural layers.
---

# Viewpoints before shapes

Choose the question first. Reusing a palette and typography is useful; reusing one flat arrangement for every analytical question loses information. Record the chosen notation in the explanation. Use official notation documentation when a task requires formal conformance or a term is uncertain; distinguish that sourced definition from local presentation choices.

| View | Question and content | Relationship / reading semantics |
| --- | --- | --- |
| Runtime architecture | Which components collaborate, who owns responsibilities, and where do trust and transaction boundaries lie? | Labeled synchronous calls, asynchronous events and data access; group components by evidenced ownership/layer. |
| Repository architecture | Where do source modules and tests live, and which projects may depend on which? | Native folder/project containment plus actual compile-time references. Distinguish a reference arrow from a proposed dependency policy. |
| Conceptual domain | Which business concepts and relationships define the domain? | Business names, selected associations and justified cardinalities. Map every concept to its source tables; keep physical fields and full FK detail in the evidence catalog or a separate schema view. |
| Physical ER / document model | What is stored, how is it keyed, and which constraints actually hold? | Entities/collections, fields, PK/FK or document references, nullability, indexes and multiplicities. Distinguish enforced links from application conventions. |
| Sequence | How does one scenario unfold across participants? | Time progresses along lifelines; ordered calls/replies, activations and alt/opt/loop/par fragments. Show relevant failure/timeout/duplicate branches from the spec; lane adjacency does not imply a call. |
| Lifecycle | Which states and transitions are legal? | Initial/final states; event [guard] / effect. A task checkpoint is an activity, not automatically a persistent state. |
| Deployment | What runs where, and where are security boundaries? | Nodes/environments, deployed artifacts, replicas, network paths and protocols. Separate proposed topology from observed infrastructure. |
| Data flow / observability | What data is produced, transformed, stored and consumed? | Directed, labeled data movement and stores; include data owner/sensitivity and telemetry correlation when evidenced. |
| Recovery / activity swimlane | Who acts, in which order, and what controls recovery? | Owner lanes, actions, decisions, gates and handoff; include entry criteria, stop/retry conditions and verification. |

An ambiguous request for “system design” needs a concrete reading contract: runtime structure, behavior, state or deployment. Infer from supplied evidence when clear; ask about materially different outcomes when it is not. Explain the chosen view rather than silently relabeling an unrelated picture.

## Structural decomposition

For a layered application, a useful hierarchy is System → Layer → Responsibility → selected component. Parent boxes express ownership; edges express collaboration. Render child boxes as native descendants and give the header its own space. Split detail when a reader must zoom excessively to follow one flow.

Application detail commonly includes:

- Command/Query contracts: input and intent.
- Validators: request constraints and their invocation point, when present or explicitly proposed.
- Handlers: use-case orchestration, transaction ownership and port calls.

Domain detail separates entity/value-object invariants, reusable domain business logic and repository/port contracts according to the project's convention. In the e-commerce example, the owner chose a child named `Domain` and the feature path `src/Ecommerce.Domain/Authen/Domain/`. That is a project decision, not a universal folder name. Tax calculation belongs to its relevant business feature and must be labeled illustrative/proposed unless source code implements it.

Avoid presenting several handlers as separate services unless deployment evidence establishes that boundary. A database schema or namespace does not establish a bounded context, aggregate, microservice or transaction boundary.

## Review a set

Compare each view's question, node vocabulary, edge legend and omissions. Architecture and repository can share component names while using different relationships. Domain associations should not become request arrows; lifecycle transitions should not become folder dependencies. A legend must define exactly what the visible lines mean, including dashed/status styles and omitted links.
