---
name: Checker Patterns
description: How to add a spec-group checker to e-commerce/db/tests/check_docs.py and test it with deliberate mistakes. Read when a new API group or a new rule needs automatic checking.
---

# Writing the checker for a spec group

`e-commerce/db/tests/check_docs.py` is a single file of checks, each registered as a sub-command (`COMMANDS["<name>"] = function`). Look at `check_order_spec`, `check_shop_profile_spec` or `check_cart_spec` and copy their shape. Helper functions you can reuse: `read`, `table_lines_aligned`, `json_blocks_parse`, `relative_links_exist`, `missing_needles`, `success_codes`, `fail`.

## What one checker contains

1. **The file list** of the group (a dict from number to path) and a failure when a file is missing.
2. **Generic checks per file**: tables aligned, JSON parses, relative links resolve.
3. **Needles**: for each file the headings and sentences that must exist (the rule section, each SQL block title, the key guard such as `AND quantity >= '<sequence.quantity>'`, the approval sentence, the error code). Make a needle as specific as the thing it protects; a broad text such as `Authorization` matches a header and hides a deleted rule. Anchor phase-specific rules to the complete clause (for example the before-count definition); mutation-test removing that clause while leaving similar wording in unrelated paragraphs. Rerun these mutations after adding a neighbouring rule: repeated wording such as final whole-request state can silently turn a formerly unique needle into a false pass.
4. **Success codes**: `success_codes(md)` must equal the expected map (`{"Success - Insert": 201, ...}`).
5. **Example arithmetic**: parse the success examples and recompute totals, counts, paging, ordering and tie-breaks; compare with what the example says. Check the existing example parser's accepted heading/prelude format first; when it expects adjacent fenced JSON (optionally after `Request:`), put other explanatory prose after the JSON fence rather than weakening the parser.
6. **Forbidden words** for public or limited APIs (`authorization`, `costPrice`, `email`, `userId` in a request).
7. **Cross-file agreement** where two specs describe the same thing (the shop name in a shop list and a shop page; a price in a list and on the product page).

Register the new endpoints in `status-codes` (single and batch lists) only when they have the full insert/update/delete/archive set; a different set gets its own checks. `biz-codes` scans every spec automatically.

## Test the checker

Build a list of deliberate mistakes (a JSON file for `mutation_harness.py`) and run it; every case must be caught. Cases that matter: change a number in an example, remove each rule sentence, remove each guard in the SQL, change a column name in a query, flip an HTTP code, expose a hidden field, break the sort order, remove the approval sentence, put a forbidden word back. When a case is missed, the checker (not the case) is wrong. Report `caught / total` and mention what slipped through first.

For paired spec/sequence rules, mutate the same SQL predicate in both files and also reorder complete orchestration blocks. Generic SQL parity may still pass; the focused checker must reject the semantic or phase fault. Report those cases separately from isolated text mutations.

For SQL fixtures, assert lifecycle and ownership preconditions before testing error precedence, especially when earlier scenarios delete or archive reused ids. Identify whether a failed precondition comes from setup or the artifact under test; correct that cause, preserve the approved contract, and rerun the scenario and dependent fixtures. Before optional rendering steps, check tool availability; use an available image viewer plus counted SVG SQL verification when a crop dependency is absent, and report the actual coverage.

## Common mistakes

- Before irreversible parent deletion, trace retained children through their cleanup endpoints and downstream usage guards. For an atomic batch, separately prove final-state rejection before per-item result mapping and use a concrete later-item failure to verify earlier parent, child and audit writes all roll back; a representative structural loop trace alone cannot prove multi-item atomicity.

- Execution-order prose copied into scaffold hints can be counted as transaction commands. Use wording such as `begin transaction (READ COMMITTED)` in that prose, keep real transaction messages explicit, and rerun the skeleton suite after changing an execution-order sentence even when SQL is unchanged.

- Saving `check_docs.py` from an old copy and erasing another person's sub-command: read the file again right before editing.
- When adapting prototype SQL, replace a qualified alias only at token boundaries; an unbounded `r.` replacement also changes the end of `author.`. Verify every schema-qualified relation against the migrations and mutation-test a synchronized wrong-schema edit in both artifacts. Derive follow-up edit anchors from the current file or AST, assert replacement counts before writing, and start fail-fast handling before the first edit so a failed precondition stops dependent checks.
- A needle that also appears in another place and therefore never fails.
- A check on example arithmetic that skips examples with empty lists; check them too.
