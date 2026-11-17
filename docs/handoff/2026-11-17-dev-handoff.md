---
name: E-commerce Dev Handoff
description: Handoff list from the SA team to the dev team for the e-commerce backend (what is approved, where each artifact lives, the rules that bind the code, how to verify, and what is still open); read before planning or starting any backend implementation.
---

# Handoff ให้ทีม Dev: e-commerce backend

วันที่: 2026-11-17 · จาก: Josh (SA Lead) ตามคำสั่งเจ้าของงาน · สถานะงานออกแบบ ณ `main` หลัง PR #193–#194

งานออกแบบจบแล้วและทีม SA หยุดงาน (freeze) spec คือแหล่งความจริง (SDD): โค้ดและเทสต้องย้อนกลับไปหา spec, schema และ sequence ที่อนุมัติแล้วได้ทุกจุด ถ้าเจอจุดที่ spec ไม่ครอบคลุมหรือขัดกันเอง ให้ถาม Josh ก่อนเขียนโค้ด อย่าเดา

## 1. สิ่งที่อนุมัติแล้ว (พร้อมใช้)

| สิ่งที่ส่งมอบ | ที่อยู่ | สถานะ |
| --- | --- | --- |
| API spec 83 ตัว (spec + `sequence.wsd` ต่อ API) | `e-commerce/doc/api/<domain>/<nn>-<api>/` | approved 2026-11-16 |
| เอกสารออกแบบ 13 ฉบับ | `docs/superpowers/specs/` | approved |
| Migration (PostgreSQL 17) และ DB tests | `e-commerce/db/migrations/up`, `down`, `e-commerce/db/tests/*.test.sql` | ผ่าน `run_db_tests.sh` |
| Schema doc ต่อตาราง (53 ตาราง) และ ER diagram | `e-commerce/doc/schema/`, `e-commerce/db/er-diagram.drawio` | ตรงกับ migration (audit 0 findings) |
| Domain และ architecture diagram (รวม Redis/MongoDB/outbox) | `e-commerce/diagram/` | approved (2 ไฟล์ domain อนุมัติซ้ำ 2026-11-16) |

API แยกตาม domain:

| Domain | จำนวน | ตัวอย่าง |
| --- | --- | --- |
| authen-and-author | 10 | register, login, reset password, refresh token, logout, profile, address |
| author | 12 | role, permission, scope, user role, me |
| consent | 8 | consent, submit, pending, consent type |
| product | 15 | product, category, category attribute, type, brand |
| shop | 16 | shop SKU และ lot, shop, shop type, shop user, storefront, review |
| cart | 3 | cart item, cart inquiry |
| sales | 5 | checkout, create order, order inquiry, shop order, cancel |
| payment | 5 | start payment (Stripe), webhook, inquiry, shop payment, refund |
| shipping | 6 | create, status, stop, shop shipping, inquiry, confirm delivery |
| campaign | 3 | campaign, campaign inquiry, campaign ledger |

## 2. กฎที่โค้ดต้องตาม

- **Auth:** verify JWT (signature, issuer, audience, expiry, UUID `sub`, `roles` claim) ก่อนทุกอย่าง แล้วใน transaction: lock caller user (`FOR UPDATE`) → ตรวจ credential และ user ปัจจุบัน (401 E10002) รูปแบบ payload: `user`, `roles` (array ของชื่อ role), `permissions` แบบ `catalog:manage`, scopes แบบ `shop:*` ดู `docs/superpowers/specs/2026-11-07-api-review-design.md`
- **PLATFORM_ADMIN** อ่านจาก `roles` claim ตรงตัวพิมพ์ ห้าม query `author.m_role` หรือ `author.t_user_role` เพื่อตัดสินสิทธิ์
- **Shop role** (OWNER, ADMIN, STAFF แบบ fixed permission) อ่านจาก `shop.t_shop_user` ใน transaction ไม่ใช่ JWT claim ร้านต้องมี OWNER ที่ ACTIVE อย่างน้อย 1 คน OWNER มาจากการ promote เท่านั้น ดู `docs/superpowers/specs/2026-11-14-shop-roles-design.md`
- **ลำดับการตรวจ:** validate 400 → JWT 401 → ไม่พบ 404 → สิทธิ์ 403 → ชน/ใช้งานอยู่ 409 → เขียน ลำดับจริงของแต่ละ API อยู่ใน `sequence.wsd` ของ API นั้น
- **Lock:** ทำตามลำดับใน sequence เช่น caller user ก่อนเสมอ แถวเป้าหมายใช้ `FOR UPDATE` batch lock แถวเดิมตาม id จากน้อยไปมากก่อนวน item
- **รหัสผลลัพธ์:** S10000 สำเร็จ, E10001 400, E10002 401, E10009 403, E10004/E10005 404, E10003/E10006/E10007/E10008 409, E90001 408 ดู `.agents/skills/api-contract-design/references/api-conventions.md` หนึ่ง bizCode ต่อหนึ่ง HTTP status
- **SQL:** ใช้ SQL ใน spec เป็นต้นแบบ (ชื่อคอลัมน์และเงื่อนไขตรวจแล้วกับ schema) ลบแบบ soft delete ด้วย `row_status = 'DELETED'` และ DELETED ถือว่าไม่พบ
- **Schema:** ห้าม `ALTER TABLE` ระหว่างยังไม่มี DB จริง แก้ที่ `CREATE TABLE` และอัปเดต schema doc, ER และ DB test พร้อมกัน

## 3. วิธีตรวจ

- `python3 e-commerce/db/tests/check_docs.py <sub-command>` ทุกตัว (70 ตัว), `python3 e-commerce/db/tests/audit_all.py`
- `bash e-commerce/db/tests/run_db_tests.sh`: migration up, down, up และ SQL test ทั้งหมด **CI ไม่รันข้อนี้** (คำสั่งเจ้าของงาน 2026-11-15) ต้องรันเองในเครื่อง
- CI (`.github/workflows/checks.yml`) รัน check_docs, audit และเทสของ tooling ทุก PR

## 4. Repository ของโค้ด

- Backend อยู่ใน Component Repository แยก: `e-commerce-backend` (.NET 10) ตาม `e-commerce/REPOS.md` ใช้ skill `repository-bootstrap` เพื่อ checkout ลงใน `e-commerce/repository/` ห้าม clone เอง
- baseline ใน REPOS.md เป็นโค้ด Authen รุ่นเก่า มีช่องว่างกับ spec ใหม่ที่บันทึกไว้ใน code guide ของ repo นั้น
- Showcase repo นี้ไม่เก็บ source ของ backend

## 5. ยังเปิดอยู่ (dev ต้องรู้)

| เรื่อง | สถานะ | ผลต่อ dev |
| --- | --- | --- |
| `e-commerce/api/api-contract.json` | ยังเป็น template ไม่มี path เลย | ยังไม่มี OpenAPI ให้ generate client ใช้ spec Markdown ไปก่อน หรือขอให้ทำ contract เป็นงานแรก |
| `e-commerce/doc/permission-scope.md` (permission matrix) | in-review | การ map permission และ scope ต่อ API ยังไม่อนุมัติ อย่า hard-code จากไฟล์นี้จนกว่าจะอนุมัติ |
| `e-commerce/doc/code-structure.md` | draft | โครงสร้าง layer ของโค้ดยังเป็นร่าง |
| WP5b: author spec 13–17 (role permission, user permission, check) | Blocked (`tasks/owner/todo.md`) | ยังไม่มี spec ของ API ที่ assign permission ทำได้เมื่อจะสร้าง API ที่บังคับ permission |
| Branch protection ของ `main` | เจ้าของงานตั้งเอง | จนกว่าจะตั้ง ให้ merge `origin/main` ในเครื่องก่อนเปิด PR และห้ามกด "Update branch" |
| SQL ใน spec | ตรวจกับ schema แล้ว แต่ไม่เคยรันกับ backend จริง | เขียน integration test ตาม spec และแจ้ง Josh ถ้า SQL ผิด |
| `sequence.wsd` | ตรวจด้วย checker แล้ว แต่ยังไม่ได้ render ทุกไฟล์ | ถ้าเปิดแล้ว render ไม่ได้ แจ้ง Josh |
| FK ที่ชี้ไป `product.m_product` (cart, campaign, sales, shop) | คงเป็น `CASCADE` ตามที่เจ้าของงานเลือก | API ลบแบบ soft delete เท่านั้น ห้าม hard delete สินค้าที่ถูกใช้อยู่ |

## 6. ช่องทาง

- คำถามเรื่อง spec ส่งถึง Josh บรรทัดแรกบอก API และหัวข้อที่สงสัย Josh พาคำถามธุรกิจไปหาเจ้าของงาน
- การเปลี่ยน spec ต้องผ่าน PR และเจ้าของงานอนุมัติก่อนแก้โค้ดตาม
- ข้อตกลงทีมฉบับปัจจุบัน: `docs/handoff/2026-11-16-team-protocol.md`
