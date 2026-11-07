---
name: สิทธิ์ผู้ใช้ (author) — WP5
description: เอกสารออกแบบรอบ 1 ของ WP5 ใช้อ่านก่อนแก้ schema author, เขียน seed ของ role PLATFORM_ADMIN, เขียน API role, permission, scope, การกำหนดสิทธิ์ และการตรวจสิทธิ์ และก่อนย้อนแก้ API ที่ส่งแล้วซึ่งยังเปิดให้ทุก token เขียน
status: in-review
approved_by: null
approved_at: null
---

# สิทธิ์ผู้ใช้ (author) — WP5

> Behavior decisions confirmed directly by the product owner on 2026-11-07 (Peter Q13); this revised document remains in-review: [API review decisions](2026-11-07-api-review-design.md) govern JWT authorization and consent changes. Detailed dependent endpoint revisions are delivered separately; this note does not claim that every endpoint already matches the new decisions.

วันที่: 2026-11-06 · ผู้เขียน: Marry (SA) · สถานะ: อนุมัติแล้ว (ประตู 1 ผ่าน) เริ่มรอบ 5a · `approved_by`: Ittikorn (Aof) Sopawan ตอบผ่าน Josh 2026-11-06 ("ตามที่แนะนำ" ต่อ Q1–Q7 ตามความหมายที่ Josh เสนอ และอนุมัติ A13) · Lead ตัดสินแล้ว: A7, A9, A16, A18, การแบ่งรอบ 5a/5b/5c

ตาม [roadmap](../plans/2026-11-06-api-roadmap.md) WP5 และข้อ 7 ของคำถามใน roadmap ข้อเท็จจริงอ่านจาก `origin/main` (85e64de) ไม่แก้ spec ที่ส่งแล้ว ข้อเสนอแก้อยู่ในหัวข้อ "ข้อเสนอแก้งานที่ส่งแล้ว"

## เป้าหมาย

- ยืนยันสัญญา `PLATFORM_ADMIN` ที่ spec 16 เส้นพึ่งอยู่ และกำหนดว่า role นี้ถูกสร้าง (seed) ผู้ใช้คนแรกได้ role นี้ และผู้อื่นได้ role นี้อย่างไร โดยไม่ต้องเปลี่ยน spec ที่ส่งแล้ว
- กำหนดความหมายของ role, permission และ scope ให้ใช้งานได้จริง และบอกว่า permission/scope จะใช้กับ API ใด
- API ของ role, permission, scope (upsert, inquiry), การกำหนดสิทธิ์ให้ role และผู้ใช้, การตรวจสิทธิ์
- กันผู้ดูแลล็อกตัวเอง (ห้ามเหลือแพลตฟอร์มโดยไม่มี `PLATFORM_ADMIN`)

## ไม่ใช่เป้าหมาย

- บังคับให้ spec ที่ส่งแล้วเปลี่ยน (ข้อเสนอแก้เป็นรายการแยก รอ Josh และเจ้าของงาน)
- ระบบ deny, สิทธิ์ที่หมดอายุเอง, การอนุมัติสองชั้นก่อนให้ `PLATFORM_ADMIN`
- การเปลี่ยนสถานะผู้ใช้ (ไม่มี API ในตอนนี้) ข้อกำหนดที่ API นั้นต้องรักษาถูกเขียนไว้ใน A6
- `public.t_key` (นอกขอบเขตจนกว่าเจ้าของงานบอก)

## ผลงาน (หลังประตู 1)

แบ่งเป็นรอบย่อยที่มีประตู 2 ของตัวเอง ทีละรอบ (Lead อนุมัติการแบ่งแล้ว):

- **5a (ทำตอนนี้):** role, permission, scope ตาราง 9 เส้น, schema ของทั้ง 8 ตาราง (A13), seed, การกำหนด role ให้ผู้ใช้ (2 เส้น) และ `me` (1 เส้น) ซึ่งจำเป็นต่อการมอบ `PLATFORM_ADMIN` ตาม A11 "แบบเล็ก"
- **5b (เลื่อน เจ้าของงานเลือกแบบเล็กตาม Q6):** การกำหนด permission ให้ role และผู้ใช้ และ `check` (5 เส้น) จนกว่ามี API ที่ใช้จริง schema ของตารางเหล่านี้แก้ตาม A13 ในรอบ 5a อยู่แล้ว (ไม่เสียค่าใช้จ่าย)
- **5c (หลัง 5a ผ่านประตู 2 และ seed กับขั้นตอน A4 พร้อมใช้):** ย้อนแก้ API ที่ส่งแล้วให้เขียนได้เฉพาะ `PLATFORM_ADMIN` (หัวข้อ "ข้อเสนอแก้งานที่ส่งแล้ว", 9 spec และตัวตรวจหลายชุด ต้องปรับตัวตรวจและทดสอบด้วยความผิดจงใจ) มีประตู 2 ของตัวเอง ไม่ทำก่อนเจ้าของงานตอบ Q5

- Schema (แก้ที่ `CREATE TABLE`): partial unique ของ 3 ตารางหลักและ 5 ตารางผูก, FK `t_role_permission_scope.permission_scope_id` ชี้ `t_permission_scope`, เพิ่มคอลัมน์ `t_user_permission.permission_scope_id`, FK ไปตารางหลักเป็น `RESTRICT` พร้อมแบบทดสอบ SQL, schema doc, README, ER
- Seed: `e-commerce/db/seed/author.seed.sql` (role `PLATFORM_ADMIN`, scope, รายการ permission) พร้อมแบบทดสอบที่รัน seed ซ้ำ
- Spec ในกลุ่ม `e-commerce/doc/api/author/` ตามตาราง A11 และตัวตรวจ `author-spec`, `author-schema`

## ตารางข้อเท็จจริงที่อ้างอิง

| ข้อเท็จจริง | ที่มา | สถานะการตรวจ |
|---|---|---|
| spec 16 เส้นใช้ query ชื่อ "Get the platform administrator role" (`author.m_role` `name = 'PLATFORM_ADMIN'` ACTIVE) และ "Check platform administrator" (`author.t_user_role` ACTIVE ของผู้เรียก): `shop/01`, `02`, `08`–`13`, `sales/04`, `05`, `payment/04`, `05`, `shipping/01`–`04` | `grep PLATFORM_ADMIN e-commerce/doc/api` | ค้นแล้ว |
| ตัวตรวจใน `check_docs.py` และกติกาใน `api-conventions.md` อ้างชื่อ `PLATFORM_ADMIN` | `grep` | ค้นแล้ว |
| ตาราง author ที่ spec ใช้มีสองตารางเท่านั้น: `m_role`, `t_user_role` อีก 6 ตารางไม่มี spec ใดอ่านหรือเขียน | `grep "author\\."` | ค้นแล้ว |
| ไม่มีโค้ด backend ของ author และไม่มีไฟล์ seed ในโปรเจกต์ (`e-commerce/db` มี `migrations`, `tests` และ ER เท่านั้น) | `find`, `ls` | ค้นแล้ว |
| `m_role.name`, `m_permission.name`, `m_scope.scope` เป็น `UNIQUE` ธรรมดา และตารางผูกทั้ง 5 ใช้ `UNIQUE (...)` ธรรมดาของคู่ (ลบแบบ soft แล้วให้สิทธิ์เดิมซ้ำไม่ได้) | migration `02` | อ่านจากไฟล์ |
| `t_role_permission_scope.permission_scope_id` อ้าง `author.m_scope (id)` ทั้งที่ชื่อบอกว่าเป็น permission scope (`t_permission_scope`) ทำให้ role ได้ scope ที่ permission นั้นไม่รองรับได้ | migration `02` | อ่านจากไฟล์ |
| `t_user_permission` ไม่มีคอลัมน์ scope (ตารางของ role มี) | migration `02` | อ่านจากไฟล์ |
| FK จากตารางผูกไป `m_role`, `m_permission`, `m_scope` เป็น `CASCADE` | migration `02` | อ่านจากไฟล์ |
| สิทธิ์ของ API เขียนที่ส่งแล้ว: `shop/05`, `06` ระบุว่าทุก token เรียกได้ "ยังไม่ได้กำหนดการตรวจ role"; `product/01`, `03`, `04`, `06`, `07`, `09` และ `consent/02` ไม่มีข้อความเรื่องสิทธิ์เลย (ทุก token เรียกได้โดยปริยาย); `shop/08`, `09` เพิ่มร้านได้ทุก token (ผู้เพิ่มเป็น ADMIN ของร้าน) | อ่าน spec | อ่านจากไฟล์ |
| กฎ "ADMIN คนสุดท้ายของร้าน" (`shop/11`): ตรวจจากผลหลังเขียนทั้งคำขอ, `409 E10006`, ล็อกแถว `shop.m_shop`, ผู้ดูแลแพลตฟอร์มข้ามไม่ได้ | `shop/11` กฎ | อ่านจากไฟล์ |
| `authen.m_user` ถูกล็อกก่อนเสมอ ในทุก API ของ authen (U23 ของ WP4) | WP4 | อ่านจากเอกสารออกแบบ WP4 (ยังไม่ merge) |

## การตัดสินใจ

ป้าย: **เจ้าของงานตอบแล้ว** (ยังไม่มี), **รอเจ้าของงาน** (Josh นำไปถาม), **รอ Josh** (แตะงานที่ส่งแล้วหรือข้อตกลงข้ามโดเมน), **ตัดสินเอง** (ผมเลือก ถ้าผิดแก้ตามที่ระบุ)

### สัญญา PLATFORM_ADMIN

- **A1 (เจ้าของงานตอบแล้ว Q1: คงชื่อ)** ใช้ชื่อ `PLATFORM_ADMIN` ต่อ เหตุผล: spec 16 เส้น, ตัวตรวจ และกติกาโปรเจกต์ฝังชื่อนี้ การเปลี่ยนชื่อต้องแก้ทั้งหมด และไม่ได้อะไรเพิ่ม ถ้าผิด (เจ้าของงานอยากได้ชื่ออื่น): แก้ 16 spec, ตัวตรวจ, `api-conventions.md` และ seed (ไม่กระทบ schema)
- **A2 (ตัดสินเอง)** สัญญาไม่เปลี่ยน: ผู้ใช้เป็นผู้ดูแลแพลตฟอร์มเมื่อมีแถว `author.t_user_role` ที่ ACTIVE ชี้ไปที่ `author.m_role` ชื่อ `PLATFORM_ADMIN` ที่ ACTIVE (สถานะผู้ใช้ตรวจแล้วโดยการตรวจ access token) role นี้เป็น **role ระบบ**: ผ่าน API ลบ, archive, ล็อก, ปิด (INACTIVE) หรือเปลี่ยนชื่อไม่ได้ (409 `E10006`) และผู้ถือ role นี้มีทุก permission ในทุก scope โดยปริยาย (ไม่ต้องมีแถวใน `t_role_permission`) ถ้าผิด: ถ้าต้องการแก้ role นี้ได้ ต้องมีกติกากันล็อกตัวเองเพิ่ม
- **A3 (เจ้าของงานอนุมัติโฟลเดอร์ `seed` แล้ว Q7)** seed อยู่ใน `e-commerce/db/seed/author.seed.sql` (โฟลเดอร์ใหม่ รันหลัง migration) สร้าง role `PLATFORM_ADMIN`, scope `ALL`, `SHOP`, `OWN` และรายการ permission ตาม A9 ด้วย `INSERT ... ON CONFLICT (...) WHERE row_status <> 'DELETED' DO NOTHING` จึงรันซ้ำได้ `created_by` เป็น `system` **seed ไม่สร้างผู้ใช้ใดเลย และไม่มีแถว `t_role_permission` หรือ `t_user_role`** `run_db_tests.sh` **ไม่รัน seed เอง** รันเฉพาะผ่านแบบทดสอบ `db/tests/02-author-seed.test.sql` ซึ่งเรียก `\ir ../seed/author.seed.sql` สองครั้งแล้วนับแถว (ไม่ต้องแก้ `run_db_tests.sh`) การเพิ่มโฟลเดอร์ `seed` เปลี่ยนโครงสร้างโปรเจกต์ (ตอนนี้ `e-commerce/db` มี `migrations`, `tests` และ ER): ผมจะบันทึกโฟลเดอร์นี้ในประโยคของ `e-commerce/doc/schema/README.md` ส่วน `.agents/knowledge/projects/e-commerce.md`, `CLAUDE.md` และ `AGENTS.md` ที่บันทึกโครงสร้างโปรเจกต์ ผมไม่แตะ (Josh จัดการ) ถ้าผิด (เจ้าของงานไม่ให้เพิ่มโฟลเดอร์): วาง seed ไว้ใน `e-commerce/db/migrations/seed/` หรือเป็นสคริปต์ที่แนบกับเอกสาร ไม่กระทบ schema
- **A4 (เจ้าของงานตอบแล้ว Q2: ตามที่ Josh เสนอ)** ผู้ใช้คนแรกได้ `PLATFORM_ADMIN` ด้วย **คำสั่งของผู้ดูแลระบบที่รันด้วยมือ ระบุ `userId` (ไม่ใช่ email)** ไม่ทำเองอัตโนมัติตอนระบบเริ่ม และไม่มีค่า config ที่ชี้ email เหตุผล: ระบบสมัครไม่ยืนยัน email (WP4 ไม่ได้เพิ่ม) และ `register` ตอบ 409 เมื่อชื่อหรือ email ถูกใช้แล้ว ใครที่รู้ email ของผู้ดูแลและสมัครก่อนจึงได้สิทธิ์สูงสุด หรือแย่งชื่อจนผู้ดูแลตัวจริงสมัครไม่ได้ ขั้นตอน: ผู้ดูแลระบบตรวจนอกระบบว่าบัญชีที่มี `userId` นั้นเป็นของผู้ดูแลตัวจริง (เช่นให้เจ้าของงานสมัครแล้วบอก `userId` จากหน้าโปรไฟล์) แล้วรัน `grant-platform-admin --user-id <uuid>` ซึ่งเป็นคำสั่ง SQL เดียวที่เขียนแถว `t_user_role` (`created_by` = `system`) **เฉพาะเมื่อไม่มีผู้ถือ role ที่ ACTIVE เลย** (ผู้ถือ = แถว `t_user_role` ACTIVE ของ role ACTIVE ที่ผู้ใช้ ACTIVE) และผู้ใช้เป้าหมายต้อง ACTIVE ทำในธุรกรรมเดียวหลังล็อกแถว role (A7) มีผู้ถืออยู่แล้วคำสั่งไม่ทำอะไรและแจ้งว่าปฏิเสธ จึงใช้เพิ่มผู้ดูแลคนที่สองไม่ได้ (คนที่สองมอบผ่าน API ตาม A5) คำสั่งไม่ใช่ API จึงไม่มี spec ผมจะเขียนคำสั่ง SQL ที่มีเงื่อนไขนี้ในเอกสารรอบ 2 และทดสอบพฤติกรรมของมัน (ไม่มีผู้ถือ → เพิ่ม, มีผู้ถือ → ไม่เพิ่ม, ผู้ใช้ไม่ ACTIVE → ไม่เพิ่ม, รันสองคำสั่งพร้อมกัน → ได้แถวเดียว) ใน `db/tests/02-author-seed.test.sql` ถ้าผิด: ถ้าต้องการทางอื่น (สมัครแล้วยืนยัน email) ต้องมีงานยืนยัน email ใน WP4 ซึ่งไม่ได้ทำ
- **A5 (เจ้าของงานตอบแล้ว Q2)** ผู้ที่มอบหรือถอน `PLATFORM_ADMIN` ให้คนอื่นได้: เฉพาะผู้ถือ role นี้ที่ ACTIVE ผ่าน API กำหนด role ให้ผู้ใช้ (403 `E10009` สำหรับคนอื่น) ผู้ใช้เป้าหมายต้อง ACTIVE ไม่มีขั้นอนุมัติสองชั้น ถ้าผิด: ต้องมีกระบวนการอนุมัติ ซึ่งเป็นงานใหม่
- **A6 (ตัดสินเอง ตามแบบ `shop/11`)** **กันล็อกตัวเอง:** หลังเขียนทั้งคำขอ ต้องมีอย่างน้อยหนึ่งแถว `t_user_role` ที่ ACTIVE ของ role `PLATFORM_ADMIN` ที่ผู้ใช้ของแถวนั้น ACTIVE มิฉะนั้น 409 `E10006` และ rollback ทั้งคำขอ ครอบคลุม: ลบ, archive, ปิดหรือล็อกแถวผู้ถือ role คนสุดท้าย (รวมกรณีผู้ดูแลถอน role ของตัวเอง) ผู้ดูแลข้ามกฎนี้ไม่ได้ ข้อกำหนดต่อ API ในอนาคตที่เปลี่ยนสถานะผู้ใช้ (ยังไม่มี): ต้องรักษากฎนี้ด้วย ถ้าผิด: ผู้ดูแลคนเดียวถอนตัวเองได้และแพลตฟอร์มไม่มีผู้ดูแล ต้องใช้ขั้นตอน A4 ช่วย
- **A7 (Lead ตัดสิน: อนุมัติ สอดคล้อง U23 ของ WP4)** ลำดับล็อกของ author: เมื่อล็อกผู้ใช้หลายคนให้เรียง `id` จากน้อยไปมาก และล็อกแถว role `PLATFORM_ADMIN` **เฉพาะเมื่อคำขอแตะการกำหนด role นี้** ลำดับคือ **แถว `authen.m_user` ของผู้ใช้เป้าหมาย (เรียง id จากน้อยไปมาก) → แถว `author.m_role` ของ `PLATFORM_ADMIN` (`SELECT ... FOR UPDATE`) → แถว author อื่น** ใช้เมื่อคำขอแตะการกำหนด `PLATFORM_ADMIN` เพื่อให้นับผู้ถือคนสุดท้ายได้ถูกเมื่อสองคำขอพร้อมกัน และไม่ชนลำดับ "ล็อกผู้ใช้ก่อน" ของ WP4 ถ้าผิด: เปลี่ยนลำดับ (ผลต่อประโยคกติกาของ spec ที่เขียนใหม่)

### โมเดลสิทธิ์

- **A8 (ตัดสินเอง)** ความหมาย: **permission** คือความสามารถที่ตั้งชื่อ รูป `<ส่วนงาน>.<การกระทำ>` ตัวพิมพ์เล็ก เช่น `catalog.manage` (ไม่เกิน 64 ตัวอักษร ตรวจที่ API 400 `E10001`); **scope** คือขอบเขตของสิทธิ์ ใช้รหัสตัวพิมพ์ใหญ่ `ALL` (ทั้งแพลตฟอร์ม), `SHOP` (ร้านที่ผู้เรียกเป็นสมาชิก ACTIVE), `OWN` (ข้อมูลของผู้เรียกเอง) `m_scope.scope` คือรหัส `name` คือป้ายแสดงผล; `t_permission_scope` คือ scope ที่ permission นั้นใช้ได้; `t_role_permission` คือ role มี permission; `t_role_permission_scope` คือ scope ที่ role ได้ (เป็นส่วนหนึ่งของที่ permission ใช้ได้); `t_user_permission` คือให้ permission ตรงๆ กับผู้ใช้ สิทธิ์ที่มีผลคือ **ผลรวม** ของสิทธิ์จาก role ที่ ACTIVE ที่กำหนดให้ผู้ใช้ (ทั้ง role, permission และ scope ต้อง ACTIVE) กับสิทธิ์ตรงของผู้ใช้ ไม่มี deny scope `SHOP` ไม่แทนการตรวจสมาชิกร้าน: API ที่ขอ `permission + SHOP` ยังต้องเป็นสมาชิกร้านนั้น ส่วน `ALL` ข้ามการตรวจสมาชิก ถ้าผิด: เปลี่ยนความหมาย scope ในเอกสารและ seed
- **A9 (Lead ตัดสิน: อนุมัติ)** รายการ permission ที่ seed (ข้อมูลอ้างอิงเท่านั้น ยังไม่มี API ใดบังคับ):

| permission | scope ที่ใช้ได้ | ใช้กับกลุ่ม API ในอนาคต |
|---|---|---|
| `catalog.manage` | `ALL` | ประเภท/ยี่ห้อ/หมวดหมู่/แอตทริบิวต์สินค้า, ประเภทร้าน (WP6 และข้อเสนอแก้) |
| `consent.manage` | `ALL` | ประเภท consent และเนื้อหา consent |
| `shop.manage` | `ALL`, `SHOP` | แก้ร้าน, สมาชิกร้าน, SKU และ lot |
| `order.read` | `ALL`, `SHOP`, `OWN` | อ่านออเดอร์ทั้งหมด, ของร้าน, ของตัวเอง |
| `payment.refund` | `ALL`, `SHOP` | คืนเงิน |
| `shipping.manage` | `ALL`, `SHOP` | จัดส่ง |
| `author.manage` | `ALL` | จัดการ role และ permission |

  ถ้าผิด: เพิ่มหรือลบรายการใน seed ไม่กระทบ schema
- **A10 (ตัดสินเอง; ผลต่อ spec ที่ส่งแล้ว: ไม่มี)** permission/scope ใช้กับ API ใดจริง: (ก) **ตอนนี้ไม่มี API ที่ส่งแล้วใดเรียกตัวตรวจ permission** spec เดิมใช้แค่ `PLATFORM_ADMIN` และสมาชิกร้าน ซึ่งยังถูกต้องเพราะผู้ถือ `PLATFORM_ADMIN` มีทุกสิทธิ์ (A2) (ข) API ของ WP5 เขียนได้เฉพาะ `PLATFORM_ADMIN` (A12) ไม่ใช้ permission เพื่อไม่ให้ต้องมีข้อไก่กับไข่ (ใครมี `author.manage`) (ค) API ใหม่ของ WP ต่อๆ ไปใช้ "มี permission ใน scope ที่ต้องการ **หรือ** เป็น `PLATFORM_ADMIN`" ได้ และ API ของ WP6 (ประเภทสินค้า ยี่ห้อ ประเภท consent) เปลี่ยนเป็น `catalog.manage`/`consent.manage` หรือ `PLATFORM_ADMIN` ได้ภายหลังโดยไม่เปลี่ยนข้อมูล เป็นข้อเสนอแยกที่ไม่บังคับ ถ้าผิด (อยากให้ spec เดิมใช้ permission ทันที): ต้องแก้ 16 spec และตัวตรวจ ซึ่งเป็นงานย้อนแก้ที่ต้องผ่าน Josh
- **A11 (เจ้าของงานเลือกแบบเล็กแล้ว Q6: ตามที่ Lead แนะนำ)** spec ที่เขียนตอนนี้ (รอบ 5a) กลุ่มใหม่ `e-commerce/doc/api/author/` เลขเริ่ม 01 (12 เส้น):

| เลข | endpoint | หมายเหตุ |
|---|---|---|
| `01`–`03` | `POST v1/author/role/upsert`, `.../upsert/batch`, `GET v1/author/role` | role (ไม่ให้เปลี่ยน role ระบบ) |
| `04`–`06` | `POST v1/author/permission/upsert`, `.../upsert/batch`, `GET v1/author/permission` | permission, `scopes[]` ซ้อน (ผูก `t_permission_scope`) |
| `07`–`09` | `POST v1/author/scope/upsert`, `.../upsert/batch`, `GET v1/author/scope` | scope |
| `10`–`11` | `POST v1/author/user/role/upsert`, `GET v1/author/user/role` | กำหนด role ให้ผู้ใช้ (กฎ A5, A6) จำเป็นต่อการมอบ `PLATFORM_ADMIN` |
| `12` | `GET v1/author/me` | role และ `isPlatformAdmin` ของผู้เรียก |

  **เลื่อนไปจนกว่ามี API ที่บังคับใช้จริง (ไม่ทำตอนนี้):** การกำหนด permission ให้ role (`POST v1/author/role/permission/upsert`, `GET v1/author/role/permission`), การกำหนด permission ตรงให้ผู้ใช้ (`POST v1/author/user/permission/upsert`, `GET v1/author/user/permission`) และ `GET v1/author/check` (5 เส้น เลขที่สงวนไว้ `13`–`17`) schema ของตารางเหล่านี้แก้ตาม A13 ในรอบ 5a ไม่เสียค่าใช้จ่าย `me` คืนเฉพาะ `roles[]` และ `isPlatformAdmin` จนกว่ารอบที่เลื่อนไปจะมีข้อมูล permission ให้คำนวณ ตารางผูกไม่มี batch (กระบวนการกำหนดสิทธิ์ทีละรายการ) `me` ตรวจแค่ของตัวเอง ไม่มีพารามิเตอร์ `userId` ถ้าผิด (ต้องการสิทธิ์ละเอียดเร็วขึ้น): เพิ่มรอบที่เลื่อนไว้โดยไม่แก้งานที่ส่งแล้ว
- **A12 (เจ้าของงานตอบแล้ว Q3: ผู้ดูแลเท่านั้น)** สิทธิ์ของ API WP5: ทุกเส้นเขียน และ inquiry ของ role, permission, scope, การกำหนดสิทธิ์ เป็น `PLATFORM_ADMIN` เท่านั้น (403 `E10009` ตามลำดับ 400 → 404 → 403 → 409) เพราะข้อมูลเหล่านี้อธิบายโมเดลความปลอดภัย (ต่างจาก inquiry ของ WP6 ที่เปิดให้ทุก token) ส่วน `me` และ `check` เปิดให้ทุก token (ของตัวเอง) ถ้าผิด (อยากให้ทุก token อ่าน role/permission): ตัดคำสั่งตรวจสิทธิ์ออกจาก inquiry
- **A13 (เจ้าของงานอนุมัติแล้ว 2026-11-06 ผ่าน Josh)** การเปลี่ยน schema: (1) `name` ของ `m_role`, `m_permission` และ `scope` ของ `m_scope` เป็น partial unique `WHERE row_status <> 'DELETED'` (ตามแบบ WP6 B1 ที่ Lead ตัดสินแล้ว) ตัด `UNIQUE` ในตาราง; (2) ตารางผูกทั้ง 5 เปลี่ยน `UNIQUE (...)` เป็น partial unique ของคู่ เพื่อให้ให้สิทธิ์เดิมซ้ำได้หลังเพิกถอนแบบ soft; (3) `t_role_permission_scope.permission_scope_id` ชี้ `author.t_permission_scope (id)` แทน `m_scope`; (4) `t_user_permission` เพิ่ม `permission_scope_id UUID REFERENCES author.t_permission_scope (id)` (NULL ได้ ใช้ NULL เมื่อ permission ไม่มี scope) พร้อม partial unique สองตัว (`(user_id, permission_id)` เมื่อ scope เป็น NULL, `(user_id, permission_id, permission_scope_id)` เมื่อไม่ใช่) ผู้ใช้จึงได้ permission ที่มี scope ต้องระบุ scope (400 `E10001`) เหมือน role; (5) FK ไป `m_role`, `m_permission`, `m_scope`, `t_permission_scope` เป็น `ON DELETE RESTRICT` (ตาม WP6 B2) ส่วน `user_id` (ไป `authen.m_user`) และ `role_permission_id` คงเป็น `CASCADE` ผลต่อ README: `t_user_permission` เพิ่ม 1 คอลัมน์ (6 FK เท่าเดิม) ถ้าผิด: เปลี่ยนที่ migration, doc, ER และแบบทดสอบ 8 ตาราง **ผลต่อ spec ที่ส่งแล้ว 16 เส้น (อ่าน `m_role` และ `t_user_role`):** คอลัมน์ที่ spec เหล่านั้นอ่านและกรองคือ `m_role.id`, `name`, `row_status` และ `t_user_role.id`, `user_id`, `role_id`, `row_status` **ไม่เปลี่ยนชื่อ ชนิด หรือความหมาย** สิ่งที่เปลี่ยนคือรูปแบบ unique และการกระทำของ FK เท่านั้น ดัชนีใหม่รองรับสอง query เดิมโดยไม่แก้ spec: `WHERE r.name = 'PLATFORM_ADMIN' AND r.row_status = 'ACTIVE'` ใช้ `uq_m_role_name` และ `WHERE ur.user_id = ... AND ur.role_id = ... AND ur.row_status = 'ACTIVE'` ใช้ `uq_t_user_role_user_id_role_id` (เงื่อนไข `= 'ACTIVE'` ของ query แปลว่า `<> 'DELETED'` จึงเข้ากับเงื่อนไขของดัชนีบางส่วน) ผมจะตรวจด้วย `EXPLAIN` ในฐานข้อมูลทดสอบชั่วคราวของรอบ 2 (ยังไม่ได้ตรวจ)
- **A14 (ตัดสินเอง ตามแบบ WP6 B3)** ลบ (`DELETED`) หรือ archive ตารางหลักไม่ได้ขณะมีแถวผูกที่ไม่ใช่ `DELETED` ใช้อยู่ (role ที่ยังมีผู้ใช้หรือ permission, permission ที่ role/ผู้ใช้ยังถืออยู่, scope ที่ยังผูกกับ permission) → 409 `E10006` ต้องเพิกถอนแถวผูกก่อน ปิด (`INACTIVE`) หรือล็อกทำได้ แต่ role/permission/scope ที่ไม่ ACTIVE ไม่ให้สิทธิ์ใดๆ (ตัดออกจากการคำนวณสิทธิ์) ถ้าผิด (อยากให้ลบแล้วเพิกถอนตาม): ต้องมีกติกาลบต่อเนื่อง
- **A15 (ตัดสินเอง)** รูปแบบชื่อ (ตรวจที่ API 400 `E10001`): role และ scope เป็นตัวพิมพ์ใหญ่ ตัวเลข และ `_` ขึ้นต้นด้วยตัวอักษร (ไม่เกิน 64) เช่น `PLATFORM_ADMIN`; permission เป็นตัวพิมพ์เล็ก ตัวเลข `_` และ `.` อย่างน้อยสองส่วน เช่น `catalog.manage` ไม่ใช่ข้อจำกัดใน schema (config) ถ้าผิด: เปลี่ยนรูปแบบ ไม่กระทบ schema
- **A16 (superseded by owner decision, 2026-11-07, Peter Q2/Q4/Q13)** Store role, permission and permission-specific scope claims in the access token. Use those claims for authorization until the access token expires (15 minutes by configuration); assignment changes may leave former privileges usable until then. Rebuild claims from current ACTIVE assignments on every login and refresh. Keep the WP4 token/user checks for immediate logout and password-reset revocation. See [approved review decisions](2026-11-07-api-review-design.md).
- **A17 (ตัดสินเอง)** ไม่เพิ่ม bizCode ใหม่: 400 `E10001` (รูปแบบ, ชื่อ, scope ไม่ตรง permission, ขาด scope), 403 `E10009` (ไม่ใช่ `PLATFORM_ADMIN`), 404 `E10004` (ไม่พบแถวจาก `id`), 404 `E10005` (ไม่พบ role/permission/scope/ผู้ใช้ที่อ้างถึง), 409 `E10003` (ชื่อซ้ำ หรือกำหนดซ้ำ), 409 `E10006` (ถูกใช้อยู่, role ระบบ, ผู้ดูแลคนสุดท้าย) ถ้าผิด: ต้องถามเรื่องรหัสใหม่

### ประสิทธิภาพ

- **A18 (authorization source superseded by owner decision, 2026-11-07, Peter Q4/Q10/Q13)** Caller platform-administrator authorization uses the verified JWT role claims, not a live assignment lookup on every request. Existing specs that still contain the two database guard queries are outstanding migration work, delivered one API per PR. Preserve the database queries needed for ownership, shop membership, reference validation and last-administrator invariants. The existing partial indexes remain useful when resolving claims at login/refresh and when managing assignments. `author/me` reports the calling token's role snapshot (Q11), not newer assignments from the database. See [approved review decisions](2026-11-07-api-review-design.md).

## ข้อเสนอแก้งานที่ส่งแล้ว (รอ Josh และเจ้าของงาน ไม่แก้ใน WP5)

ใช้กติกา "เขียนต้องเป็น `PLATFORM_ADMIN`" ของ WP6 (403 `E10009` หลัง 404 ก่อน 409, query สองตัวคัดจาก `sales/05`) กับ API เขียนที่ยังเปิดให้ทุก token:

| API ที่ส่งแล้ว | กติกาปัจจุบัน | ข้อเสนอ |
|---|---|---|
| `shop/05`, `06` (ประเภทร้าน) | ทุก token (เขียนไว้ว่ายังไม่กำหนด) | `PLATFORM_ADMIN` เท่านั้น |
| `product/04`, `06` (หมวดหมู่) | ทุก token (ไม่มีข้อความ) | `PLATFORM_ADMIN` เท่านั้น |
| `product/07`, `09` (แอตทริบิวต์หมวดหมู่) | ทุก token (ไม่มีข้อความ) | `PLATFORM_ADMIN` เท่านั้น |
| `consent/02` (เนื้อหา consent ทางกฎหมาย) | ทุก token (ไม่มีข้อความ) | `PLATFORM_ADMIN` เท่านั้น |
| `product/01`, `03` (สินค้า) | ทุก token (ไม่มีข้อความ) | **ต้องถามเจ้าของงาน Q4** ว่าใครสร้างสินค้า |
| `shop/08`, `09` เพิ่มร้าน | ทุก token แล้วผู้เพิ่มเป็น ADMIN ของร้าน | ไม่เปลี่ยน (ตั้งใจเป็นตลาดเปิด) |

ผลถ้าอนุมัติ **(เป็นรอบย่อย 5c ที่มีประตู 2 ของตัวเอง ทำหลัง 5a ผ่านประตู 2 และ seed กับขั้นตอน A4 พร้อมใช้)**: 9 spec (`shop/05`, `06`; `product/04`, `06`, `07`, `09`; `consent/02`; และ `product/01`, `03` ถ้า Q4 ตอบ `PLATFORM_ADMIN`) เพิ่มกฎ ตัวอย่าง 403 และสอง query และเปลี่ยนลำดับตรวจเป็น 400 → 404 → 403 → 409 ตัวตรวจที่เกี่ยวข้อง (`shop-type-spec`, ชุด `spec0x` ของ product, `status-codes` ไม่เปลี่ยนรหัส HTTP) ต้องปรับ needle และทดสอบด้วยความผิดจงใจใน 5c ผมยังไม่ได้ไล่ตัวตรวจทีละตัว **ต้องทำหลัง seed และขั้นตอน A4 พร้อมใช้ มิฉะนั้นไม่มีใครเขียนข้อมูลหลักได้เลย** (รวม API ของ WP6)

## คำถามธุรกิจ (เจ้าของงานตอบแล้ว 2026-11-06: "ตามที่แนะนำ" ทั้ง 7 ข้อ ตามคำแนะนำที่เขียนในแต่ละข้อ ยกเว้น Q6 ให้ยึด "แบบเล็ก")

1. **Q1 ชื่อ role (A1)** — คำแนะนำ: ใช้ `PLATFORM_ADMIN` ต่อ · ถ้าผิด: แก้ 16 spec และตัวตรวจ
2. **Q2 ผู้ดูแลคนแรกและการมอบสิทธิ์ (A4, A5)** — คำแนะนำ: ผู้ดูแลระบบรันคำสั่งด้วยมือ ระบุ `userId` หลังตรวจนอกระบบว่าบัญชีนั้นเป็นของผู้ดูแลตัวจริง คำสั่งทำงานเฉพาะเมื่อยังไม่มีผู้ดูแลเลย หลังจากนั้นมอบให้ผู้อื่นได้เฉพาะผู้ดูแลที่มีอยู่ · ถ้าผิด: ใช้ email ที่ตั้งค่าไว้ (ระบบสมัครไม่ยืนยัน email ใครสมัครก่อนได้สิทธิ์สูงสุด) หรือ "คนแรกที่สมัคร" (แย่งกันได้)
3. **Q3 ใครอ่านข้อมูล role และ permission (A12)** — คำแนะนำ: ผู้ดูแลแพลตฟอร์มเท่านั้น · ถ้าผิด: ให้ทุก token อ่านได้ ซึ่งเปิดเผยโครงสร้างสิทธิ์
4. **Q4 ใครสร้างและแก้สินค้า (product/01, 03)** — คำแนะนำ: ผู้ดูแลแพลตฟอร์มสร้างสินค้า ร้านตั้ง SKU และ lot ของสินค้านั้น (ตรงกับที่ `shop/01` ทำ) · ถ้าผิด: ร้านสร้างสินค้าได้เอง ต้องกำหนดว่าร้านแก้สินค้าของร้านอื่นไม่ได้อย่างไร
5. **Q5 ย้อนแก้ API ข้อมูลหลักให้เป็นผู้ดูแลเท่านั้น (ตารางด้านบน ทำเป็นรอบย่อย 5c)** — คำแนะนำ: อนุมัติ หลัง seed และขั้นตอน A4 พร้อมใช้ · ถ้าผิด: ประเภทร้าน หมวดหมู่ และ consent ยังถูกแก้ได้โดยลูกค้าทั่วไป
6. **Q6 ขอบเขตของ permission และ scope ตอนนี้ (A10, A11)** — มีสองทาง **แบบเล็ก (Lead แนะนำ):** ทำ role, permission, scope, การกำหนด role ให้ผู้ใช้ และ `me` (12 เส้น) ซึ่งจำเป็นต่อการมอบ `PLATFORM_ADMIN` ส่วนการกำหนด permission ให้ role/ผู้ใช้ และ `check` (5 เส้น) เลื่อนไปจนกว่ามี API ที่ใช้จริง (schema แก้ไว้แล้ว ไม่เสียค่าใช้จ่าย) · ถ้าผิด: ต้องการสร้างสิทธิ์ละเอียดเร็วขึ้น เพิ่มรอบ 5b ภายหลังโดยไม่แก้งานที่ส่งแล้ว **แบบเต็ม:** ทำครบ 17 เส้นตอนนี้ แต่ยังไม่บังคับใช้กับ API ใด · ถ้าผิด: มี 5 เส้นที่ไม่มีผู้ใช้ ต้องดูแลตัวตรวจและ spec ที่ยังไม่มี API ไหนเรียก ผมแนะนำแบบเล็ก
7. **Q7 โฟลเดอร์ seed ใหม่ (A3)** — คำแนะนำ: ยอมให้เพิ่ม `e-commerce/db/seed/` (ไม่มีผู้ใช้ใน seed รันผ่านแบบทดสอบเท่านั้น) · ถ้าผิด: วาง seed ใน `migrations/seed/` หรือเป็นสคริปต์แนบเอกสาร

เจ้าของงานอนุมัติ A13 แล้ว (แก้ schema 8 ตารางของ author รวม `m_role` และ `t_user_role` ที่ spec 16 เส้นอ่าน โดยไม่เปลี่ยนคอลัมน์ที่อ่าน) ตัดสินโดย Lead แล้ว: A7, A9, A16, A18 และการแบ่งรอบ 5a/5b/5c

## สิ่งที่พบนอกขอบเขต (ไม่แก้ รายงานแยก)

- `public.t_key` (เก็บอะไรไม่ทราบ) อาจเป็นที่เก็บกุญแจเข้ารหัสของ `FieldProtector` แต่ไม่มีข้อมูลยืนยัน ผมไม่ได้พึ่งตารางนี้
- spec 16 เส้นใช้ query สองตัวซ้ำกัน ถ้าจะรวมเป็น query เดียวในอนาคตต้องแก้ทั้ง 16 spec (ไม่แนะนำ ดู A18)

## ยังไม่ได้ตรวจ

ยังไม่ได้รัน `check_docs.py`, `audit_all.py`, `run_db_tests.sh` (รอบ 1) ไม่ได้ไล่ตัวตรวจที่เกี่ยวข้องกับข้อเสนอแก้งานที่ส่งแล้วทีละตัว ไม่ได้ตรวจว่า branch WP4 (`feat/authen-complete`) และ WP6 (`feat/master-tables`) ที่ยังไม่ merge แตะ `02-author`, `check_docs.py` หรือ README ตรงเดียวกัน (WP4 และ WP6 แทรกตัวตรวจก่อน `def main` เหมือนกัน และ WP4 เปลี่ยน `audit_all.py` กับเลขตารางรวม 53) ไม่ได้ตรวจเอกสารภายนอกใดๆ
