---
name: Peter API Review Decisions
description: Owner-confirmed JWT authorization, consent/profile/address behavior, review scope and delivery rules; read before revising the affected e-commerce API specifications and sequences.
status: approved
approved_by: Ittikorn (product owner, directly in Peter chat)
approved_at: 2026-11-07T08:31:05+07:00
---

# Peter API review decisions

The owner confirmed Q13 in this chat on 2026-11-07 with the exact answer **“ใช่ เริ่มตามข้อตกลงนี้”**, accepting the complete summary of Q1–Q12 below. This approves the behavior and review scope, not an unseen detailed endpoint revision or backend implementation. Detailed revised endpoint specs remain `in-review` until reviewed. Peter is the System Analyst; no backend changes are authorized by this document.

## Approved decisions

| Decision               | Owner-confirmed behavior                                                                                                                                                                                                                                                                                                |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Q1 (superseded by Q15) | Register Peter and retain the existing managed-clone lifecycle. One active API task or PR at a time; one API (complete spec and sequence) per PR. Read-only analysis of the next API may continue while a PR is open.                                                                                                   |
| Q2, Q4                 | JWT claims are the authorization source. Changes to role, permission or scope assignments do not revoke an existing access token's claims: former privileges may remain until its expiry (15 minutes by the existing configuration). This supersedes WP5 A16 and the immediate authorization-revocation portion of A18. |
| Q7                     | Resolve current ACTIVE role, permission and assigned scope data for every new access token at login and refresh. A refresh must not perpetuate the original login's claims.                                                                                                                                             |
| Q12                    | Retain the association between each permission and its granted scopes; a scope of one permission never grants that scope to another permission.                                                                                                                                                                         |
| Q11                    | `author/me` returns the caller's effective role snapshot from the access token used for that call. A refreshed token reflects the newly resolved assignments.                                                                                                                                                           |
| Q13                    | Keep signature/issuer/audience/expiry checks and the ACTIVE access-token/user database checks from WP4. Logout and password reset still revoke tokens immediately; this is distinct from assignment changes.                                                                                                            |
| Q3                     | Hide consents whose consent type is not ACTIVE, even if the consent itself is ACTIVE and within its effective period.                                                                                                                                                                                                   |
| Q5                     | Registration and submission reject new answers for a consent whose type is not ACTIVE; preserve previously stored answers.                                                                                                                                                                                              |
| Q6                     | Registration requires acceptance of the current version of every required consent that is ACTIVE, currently effective, and belongs to an ACTIVE type. Optional consents may be rejected or omitted.                                                                                                                     |
| Q8                     | A required consent remains pending until the current version is both read and accepted; an optional consent stops being pending once the current version is read, including an explicit rejection or omitted answer.                                                                                                    |
| Q9                     | Existing users may still log in when a new required consent or version appears. Expose the pending list; this review does not add service-access gates.                                                                                                                                                                 |
| Q10                    | Include APIs outside the original three folders where JWT authorization changes affect the contract. Preserve ownership, shop membership, and business invariant checks.                                                                                                                                                |

Acceptance submitted at registration also records that submitted version as read, so an accepted required consent does not immediately reappear as pending. This follows Q6 and Q8 together; timestamp and SQL details belong in the registration revision.

## Additional confirmed decision

Q14: The owner answered **“ใช่ ปฏิเสธกรณีตรงกับสองบัญชี”** on 2026-11-07. If a login identifier matches the username of one ACTIVE account and the email of another ACTIVE account, refuse with the same 401, record FAILED and do not choose an account.

## Current delivery override (Q15, 2026-11-07)

The owner subsequently instructed: **“เสร็จแล้วเปิด pr ทิ้งไว้เดียวฉันมาอ่าน ไม่ต้องรอ merge switch ไปที่ main แล้วเกิด brach ใหม่ได้เลย”**. This supersedes Q1's one-open-PR and wait-for-merge restriction, including conflicting skill defaults, for this API review. Open one PR per completed API and leave it available for the owner; switch the clean managed clone back to current main and create the next API branch immediately. Preserve branch-scoped assignment/PR records for later review fixes. This does not authorize merging PRs, force pushes, overwriting other work or granting delegation capabilities.

## Scope and delivery

The original source inventory was 30 APIs / 60 files in `authen-and-author` (10), `author` (12), and `consent` (8). All files were read; 12 author diagrams were empty. Populated diagrams copied SQL in document order, which did not reliably match execution order.

The initial impact search found at least 23 further API specs with database-based platform-administrator authorization: campaign 01–03; payment 04–05; product 10–11 and 13–14; sales 04–05; shipping 01–04; shop 01–02 and 08–13. Reconcile later merged changes, including PR #20, before each assignment. This list is a discovery baseline, not permission to omit another proven dependency.

Start with login, then refresh, then remaining APIs in dependency order. Each PR includes only one endpoint's `spec.md` and complete `sequence.wsd`, plus the governing-document and checker changes necessary for that endpoint. The new rule is the target contract: existing dependent specs awaiting their own PRs are explicitly outstanding, not claimed synchronized by the login delivery.

Use `commit-and-pr`. Do not merge PRs or enable auto-merge. Follow Q15: leave each completed PR open, retain its branch and review record, and start the next API from updated main without waiting for merge. Business decisions already confirmed above do not need repeated approval. Ask only about a newly discovered behavior-changing ambiguity.

## Verification expectations

- Every SQL statement agrees with the migration and schema and appears in the sequence under the actual branch in which it executes.
- Table activations enclose SQL notes and returned results. Include input failures, authentication/authorization failures, transaction commits/rollbacks and timeout behavior.
- SQL parity checks protect the definitions and table lifecycles; endpoint flow checks additionally enforce ordering, mutually exclusive outcomes and transaction behavior. A shared SQL step may follow alternative branches when its parameters and preconditions are explicit.
- Run every documentation subcommand, the complete SQL audit, and database tests for delivery. Mutation-test the changed checker; static SQL parity alone is insufficient proof of flow correctness.
- Report rendering and runtime checks separately. The existing backend is outside this documentation review; a passing checker does not prove backend conformance.

## Consent display and version decisions (Q16–Q17)

Q16: The owner answered **“แสดงหน้านั้นถือว่าอ่านแล้ว ส่งมาก่อน 1 ทีเพื่อ update ว่าอ่าน ถ้ากดส่ง result ก็เส้นเดียวกันนั้นแหละแค่แปะ result มาด้วย ถ้ามี read อยู่แล้วก็ไม่ต้อง update”**. Displaying a consent triggers the same submission endpoint without result and records the displayed version as read. A later answer sends result on that endpoint; a read-only call preserves an existing answer. Already-read evidence keeps its original read flag/timestamp and read-only calls perform no UPDATE. Required registration still needs explicit true.

Q17: The owner answered **“ใช่ บังคับระบุเวอร์ชันที่แสดง”**. Every supplied consent object must identify its displayed consentVersion, including read-only requests; reject an omitted or non-current version without silently accepting a newer unseen version.

## Profile and address decisions (Q20–Q21, 2026-11-08)

Q20: The owner answered **“คืน null สำหรับค่าว่างเดิม (แนะนำ)”**. `08-inquiry-user-profile` projects legacy `gender = ''` to response `null` using `NULLIF`; keep existing NULL/MALE/FEMALE/OTHER values and do not rewrite history. This decision is already recorded in the endpoint revision delivered as PR #60.

Q21: The owner answered **“ตอบ 400 เมื่อ Delete ส่ง true (แนะนำ)”**. `09-upsert-user-address` rejects `rowStatus = DELETED` with explicit `isDefault = true` as 400 E10001, matching the existing normative default rule. Correct the contradictory Delete example and checker exception. A valid delete with false/omitted isDefault still clears the stored default and promotes another ACTIVE address under the existing rule. This does not disallow deletion of a default address.

## Permission scope decisions (Q22–Q23, 2026-11-08)

Q22: The owner answered **“ใช่ ปฏิเสธจนถอน grant เดิมครบ”**. Reject a transition from at least one non-DELETED permission-scope definition before the request to zero definitions after the whole request when any non-DELETED role or direct user grant still references that permission (409 E10006, whole transaction rollback). Withdraw those grants before changing a scoped permission into an unscoped permission. Already-unscoped permissions are not prohibited from retaining valid unscoped grants. The final-state guard prevents existing grants from becoming newly eligible for unscoped claims on a later login/refresh; it does not change an already-issued access token's snapshot.

Q23: The owner answered **“ใช่ อนุญาตถอน link ของ scope ที่ปิดแล้ว”**. Removing an existing permission-scope link does not require its scope master to remain ACTIVE. Still require the owned non-DELETED link, its original immutable scopeId and no non-DELETED role/user references to that link. Adding/retaining an ACTIVE link still requires an ACTIVE scope master. This cleanup exception does not bypass Q22: removal of the last definition with surviving grants still rolls back.

## Permission deletion decision (Q24, 2026-11-09)

Q24: The owner answered **“ต้องถอน links ให้ครบก่อนลบ permission (แนะนำ)”**. A permission may become DELETED only when its final whole-request count of non-DELETED permission-scope definitions is zero. Otherwise return 409 E10006 and roll back all parent, child and audit changes (the entire batch for a batch request). Count ACTIVE/INACTIVE/LOCKED/ARCHIVED definitions regardless of master status. Complete explicit scope-link withdrawal and permission deletion in the same request are allowed, subject to the existing ownership/reference checks. Do not add an implicit cascade. ARCHIVED and other reversible parent statuses may retain definitions. Apply to permission single and batch through their separate paired spec/sequence PRs. Q22 grant-transition protection and Q23 closed-master cleanup remain in force. This prevents new irreversible parents with stranded live definitions; it does not approve a legacy-data rewrite or a new deleted-parent cleanup endpoint.

## Consent management decisions (Q18–Q19, 2026-11-09)

Q18: The owner answered **“q18 ถูกต้อง”** to the recommended PLATFORM_ADMIN-only management inquiry. `consent/03-inquiry-consent` requires the exact role from verified JWT claims, with the current token/user gate retained. This does not change token-only consent-type reference inquiry.

Q19: The owner answered **“q19 ทั้งหมด”**. The management inquiry may retrieve all consent records according to its documented filters, including expired consent and consent whose type is not ACTIVE. Consumer visibility rules do not hide those management records. Detailed query/filter behavior belongs in the paired consent/03 revision; no new historical-content storage is approved here.

## Allow Scope notation and deny precedence (2026-11-09)

> **Superseded 2026-11-13:** the four-part notation, the effect `deny` and the deny-wins precedence below are replaced by the [JWT payload decision](#jwt-payload-decision-2026-11-13). The text is kept as history.

The two-part display notation below is historical and superseded by the Four-part Allow Scope refinement at the end of this record; its deny-precedence decision remains in force.

The owner requested `permission-scope.md`, API allowlists and spec links, then specified **“เพิ่ม section ขึ้นมา ประมาณว่า Allow Scope แล้วใส่ชื่อ scope มา”** and **“อยากปรับให้ scope มันประมาณนี้ <scope-name>:<allow, deny, อื่นๆ>”**. Use an `Allow Scope` section with notation such as `ALL:allow`, `SHOP:allow`, `OWN:deny`; keep the scope name distinct from its effect and associate every rule with its exact permission.

The owner answered **“ใช่ deny ชนะเมื่อครอบคลุมข้อมูลเดียวกัน (แนะนำ)”** to the concrete same-permission example SHOP:allow plus ALL:deny. A matching deny wins over allow when both cover the requested resource. A deny for a different permission or a scope that does not cover that resource does not match. This approval covers the design rule and document format; it does not approve new scope/API pairings, effect values beyond allow/deny, JWT payload changes, schema/seed changes, delegated access or backend enforcement. Those remain detailed in-review work in [the permission/scope matrix](../../../e-commerce/doc/permission-scope.md), delivered per API with its spec/sequence when applicable.

### Four-part Allow Scope refinement (2026-11-09)

The owner subsequently requested **“ปรับนิดนึงอยากได้ประมาณนี้ management:user:read:allow, management:user:crud:deny ปรับ”**. This supersedes scope-name:effect as the active display format: use `<module>:<resource>:<action>:<effect>`, lowercase names and allow/deny. Keep ALL/SHOP/OWN as separate data boundaries, not the module/resource/action. CRUD means create/read/update/delete; a matching crud:deny therefore overrides read:allow on the same module/resource/data under the previously approved deny precedence. Do not silently redefine CRUD as write-only. Specific namespace/API mappings, grant storage, JWT/schema changes and additional effects remain in-review, not implicitly approved by this format correction.

## JWT payload decision (2026-11-13)

The owner replaced the JWT authorization claims and the Allow Scope notation. The choice of the new shape was the owner's: **“ใช้รูปแบบใหม่แทน”** (use the new format instead), with the payload example below. On the four open points the owner answered through the SA Lead **“ตามคำแนะนำทั้ง 4 ข้อ”**, that is the recommendations recorded here.

New access-token payload: `iss`, `sub`, `aud`, `jti`, `iat`, `exp`, `user` (`id`, `username`, `displayName`, `email`), `roles` (role names, for example `"ADMIN"`), `permissions` (`"resource:action"`, for example `"users:create"`) and `scopes` (`"type:value"`, for example `"org:company_a"`).

- **Supersedes** the structured `roles` (`{roleId, name}`), `permissions` (`{permissionId, name}`) and `scopes` (`{permissionId, scopeId, scope}`) claims of the WP4/WP5 payload, and the sentences of Q2, Q7, Q11 and the earlier specs that name the structured roles claim; the behaviour of those decisions (claims are the authorization source, refresh resolves current assignments, `author/me` reports the calling token) is unchanged.
- **Permission claim:** the stored permission name with its last `.` replaced by `:` (`catalog.manage` becomes `catalog:manage`, `shop.product.manage` becomes `shop.product:manage`). The name in the database and the seed do not change.
- **Scope claim:** `<lower-case scope code>:*` (`shop:*`), meaning every instance of that type. The database holds no instance value. Membership and ownership of the data stay API checks (Q10); no schema change is approved.
- **Q12 stays** as the resolution rule at login and refresh (a scope of one permission never grants another permission). The flat payload does not show the association, so a consumer must not read a scope as granted to every permission.
- **Allow Scope four-part notation and deny precedence are cancelled.** `module:resource:action:effect`, the effect `deny` and “a matching deny wins” (2026-11-09) no longer apply: having the permission allows, not having it denies. [The matrix](../../../e-commerce/doc/permission-scope.md) records the replacement (`module:resource:action:allow` becomes the permission claim `module.resource:action`).
- **`user` is a display snapshot** taken at login or refresh from the locked user row; it is never an authorization input. The API authorizes only from `sub`, `roles`, `permissions` and `scopes`.
- **Scope of this change:** `login/02`, `refresh/05`, `author/12-me` and the matrix. `author/12-me` now returns `data.roles` as role-name strings because the token no longer carries role ids (decided by the SA, pending confirmation). Every other specification, sequence and checker that still says `roles` is an array of `{roleId, name}` is outstanding and is corrected by each analyst in their own group.

## Consent management upsert decisions (2026-11-13)

For `consent/02-upsert-consent` the owner answered the SA Lead's five recommendations **“ใช้คำแนะนำทั้งหมด”**: (1) DELETED is final, an id of a DELETED consent is 404 E10004, while INACTIVE, LOCKED and ARCHIVED can return to ACTIVE; (2) when both are supplied, `expiredAt` must be later than `effectiveAt` (400 E10001); (3) deleting or archiving a consent that already has user answers is not blocked and adds no 409 in-use rule; (4) `consentVersion` may change to any different value of at most 8 characters, answers of the old version become pending again under Q8 and existing user consent rows are never overwritten; (5) `code` stays plainly UNIQUE, the code of a DELETED row cannot be reused and returns 409 E10003, with no schema change. The SA Lead also confirmed (6) the technical corrections of 2026-11-08 for this API: verified JWT claims, the current credential gate, and `FOR UPDATE` locks of the consent type first and then the target consent.

### Consent type of a consent (2026-11-14)

The owner answered the SA Lead's question on `consent/02`, relayed in the SA Lead's words: a consent whose consent type is no longer ACTIVE can still be deleted or archived, in the same way as Q23 lets a link of a closed scope be removed; the type must be ACTIVE only when a consent is created or a consent is opened back to ACTIVE. The consent type row must always exist (404 E10005 otherwise). Sentence of the SA Lead for the case that the owner's words left open: a request that moves an ACTIVE consent to another consent type also needs the new type to be ACTIVE, so that a consent cannot be moved to a closed type (decided by the SA Lead; remove that condition if the owner disagrees). This replaces the earlier rule that the type must be ACTIVE for every request on this API.
