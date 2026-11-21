---
name: Database-derived Domain Evidence
description: Derive conceptual domain diagrams and defensible cardinalities from database definitions without inventing business ownership.
---

# Derive concepts from the database

Use the approved schema/migration baseline, associated schema documentation and relevant business specifications. Identify the repository revision and inspect the actual constraints. Reuse a project's SQL parser/checker when available; a new regex extractor must account for multiline and composite definitions and be checked against the source rather than silently accepting an incomplete catalog.

Create a reproducible inventory containing tables, primary keys, foreign-key columns/targets, nullability, unique constraints/index predicates and relevant checks. If database access is unavailable, describe the result as migration-derived rather than live-DB-verified. Keep existing source inventories frozen unless intentionally refreshing their baseline; verify and explain drift.

## Conceptual map and coverage

Map physical tables to business concepts and groups. A concept may summarize several tables, but preserve the mapping and explain the grouping. Include master/configuration and transaction/supporting tables in the accounting even when an overview hides them. Document shown, summarized and omitted relationships separately; counts must reconcile to the chosen source inventory.

Use an overview for business areas and focused views for concepts/associations. Put the complete FK catalog, including cross-view links, in the companion or inventory. Count FK constraints and FK columns separately for composite keys. Claim full coverage only against the declared set; selecting a few readable associations is compatible with full table coverage when cuts are explicit.

## Cardinality evidence

- For a child row, a non-null FK usually establishes exactly one referenced parent, and a nullable FK permits zero or one. A composite FK with nullable members requires inspecting MATCH semantics and checks before declaring mandatory participation.
- For a parent row, an ordinary FK permits zero to many children. A unique FK can reduce the upper bound to one; mandatory child participation requires additional evidence beyond the FK.
- A partial unique index only restricts rows matching its predicate. For example, uniqueness for non-deleted payment attempts does not imply one payment attempt across all historical rows. Label the qualified association or retain all-row `0..*` with the live-row rule as a note.
- An FK to Order and a separate FK to Shop do not prove that the chosen Shop owns that Order. Inspect composite keys or explicit cross-entity checks; list unenforced consistency as a gap rather than inventing a guarantee.
- ON DELETE behavior controls referential actions. `CASCADE` alone does not prove UML composition or aggregate ownership. Business rules and transaction boundaries need their own evidence.

Read each endpoint label from the opposite entity and explain the notation once. Distinguish all stored rows, active rows and a single scenario. Verify selected associations against constraints and capture the rule that changes a multiplicity.

## Scope boundary

A conceptual diagram may describe evidence gaps without repairing them. Use the data-modeling skill and its approval/checker workflow for a schema or physical ER change; use the API contract workflow for API behavior. Reusable business operations belong on a domain responsibility view only when supported by code/spec or visibly proposed; tables alone do not establish methods.
