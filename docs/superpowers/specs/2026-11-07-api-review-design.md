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
