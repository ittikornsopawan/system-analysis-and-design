---
name: Spec Structure and Formatting
description: Required sections, table, JSON and SQL formatting rules, and example hygiene for e-commerce API specs, with how to generate the shared parts. Read while writing a spec file.
---

# Spec structure

## Sections, in this order (see `assets/api-spec.md.tmpl`)

1. Title `# [METHOD]: v1/<path>` and the summary table (Name, Method, Endpoint with `{version}`, Version, Description: one sentence listing every behaviour of the endpoint).
2. `## Domain` (the five environments), `---`.
3. `## Request Parameters`: `### Header Parameters` (`authorization` only on private APIs), `### Query Parameters` or `### Body Parameters`, one table per nested object, a `### ... Rules` section (the behaviour in bullets), `#### Example Body Parameters` (one block per case: insert, update, delete, archive).
4. `## Example Request`: `### HTTP Request`, `### cUrl Request`.
5. `---`, `## Response Parameters`: top table, `### Status Object`, `### Data Object` (and its nested objects).
6. `### Example Response Parameters`: every success (`#### Success - <case>`) and every error (`#### Fail - <case>`): bad request, unauthorized, forbidden, not found, not found reference, conflict, in use, timeout.
7. `---`, `## Database Relations`: for each table `### Table: [schema.table](../../../schema/<schema>/<table>.md)` and `#### QUERY - ...`, `#### INSERT - ...`, `#### UPDATE - ...` blocks, one per statement the endpoint runs, including the checks before the write (existence, duplicate, in use, permission) and the stock guard where there is one.

## Formatting the checker enforces

- Every markdown table is padded so all rows have equal column widths. Never edit a table cell without realigning (`../data-modeling/scripts/realign_tables.py`), or generate tables with `scripts/spec_helpers.py`.
- Every `JSON` block parses. Field names are camelCase, columns snake_case. The success example's `status.code` equals the HTTP code of that case.
- Relative links to schema docs resolve.
- SQL uses `'<sequence.name>'` placeholders and a comment `-- only when <field> is specified` on a condition that is added only when the request has the field. `NOW()` is written `NOW() AT TIME ZONE 'UTC'`. Tables, columns and aliases must exist in the migration (`audit_all.py` checks every block).
- Public API: no word `authorization`, `costPrice`, `margin` in the file (the checker lists them).

## Example hygiene

- One id keeps the same meaning in the whole file (do not reuse a product id for another product).
- Numbers add up: line total = price × quantity, order total = sum of items, summary counts equal the lists, `totalPages` equals the ceiling of `totalItems / pageSize`, one page holds everything when `totalPages` is 1.
- An example must obey the rule written above it (a "complete set" rule means the update example sends the complete set; a sort rule means the example is in that order, with a tie to show the tie-break).
- The batch examples show an item-position error (`items[1]: ...`).
- Rows hidden from the caller show `null` and a sentence names the caller of the example.

## Writing specs with a generator

For a group of specs that share a lot of text, write a small Python generator outside the repo (a scratch directory), import `scripts/spec_helpers.py`, assemble each file as a list of sections joined by blank lines, and write `spec.md`. Re-run it to apply a change to every file, and compare against the previous version with a diff to confirm only the intended lines changed. Do not keep the generator in the repo unless the owner asks.

## Allow Scope inventory and API section

When the owner requests an Allow Scope inventory, locate the unique `# [METHOD]: endpoint` heading after any YAML frontmatter rather than assuming it is the first line. Test the inventory on both metadata-bearing and legacy specs and require exactly one heading per endpoint; a failed parser is incomplete evidence, not an empty API set. When fault-testing a mixed authorization inventory, select an actual scoped row for scope/effect mutations rather than the first public/token-only row; prove each candidate changes its target before interpreting checker results.

Use `### Allow Scope` in each paired endpoint revision when authorized by the task. Use `<module>:<resource>:<action>:<effect>` (for example `management:user:read:allow`, `management:user:crud:deny`), with ALL/SHOP/OWN documented separately as data boundaries. Match the exact namespace/resource and overlapping action group before applying same-resource deny precedence; CRUD includes read and does not include custom cancel/refund. Link the central matrix and retain operation/field-specific exceptions. Before choosing an authorization notation, distinguish capability namespace, action, effect and resource boundary; never infer effect storage or a new permission grant from a display-format request. Distinguish proposed mappings from enforced policy; documenting a scope does not create a grant, replace a required role, expand an owner route or bypass a live shop-membership/business invariant. Public, reference-data, refresh/reset and provider-verification routes may require no permission scope; state that explicitly instead of inventing PUBLIC or SYSTEM scope masters. Keep the spec and sequence enforcement narrative aligned in the same one-API PR.
