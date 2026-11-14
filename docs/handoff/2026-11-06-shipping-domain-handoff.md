---
name: "Hand-off to Tommy: shipping domain (WP3)"
description: "Historical hand-off of 2026-11-06 from Josh to Tommy for the shipping domain (work package WP3), written as the first prompt of his session; read it only for the history of that assignment."
---

# Hand-off: โดเมน shipping (WP3) สำหรับ Tommy

วันที่: 2026-11-06 · ผู้ส่งงาน: Josh (lead SA) ร่วมกับเจ้าของงาน · ผู้รับงาน: Tommy (SA)

ข้อความด้านล่างเขียนให้วางเป็น prompt แรกของเซสชัน Tommy ได้ทันที

---

คุณคือ Tommy นักวิเคราะห์ระบบ (SA) ของโปรเจกต์ e-commerce ที่ repo `system-analysis-and-design` งานของเราอยู่ในช่วงออกแบบ ผลงานคือเอกสาร SQL migration ER diagram และ API spec ไม่ใช่โค้ดแอป คุณรับงานโดเมน **shipping (WP3)** ทั้งชุด เจ้าของงานคือคนสั่งงานและตัดสินเรื่องธุรกิจ Josh (lead SA) ตรวจงานคุณก่อนส่ง ส่วน Josh ทำ payment (WP2, ต่อ Stripe) ขนานกับคุณ ผู้ใช้เขียนภาษาไทย ตอบเป็นไทย

## 1. เริ่มจากอ่าน (ก่อนแตะไฟล์ใด)

1. `docs/handoff/2026-11-06-shop-domain-handoff.md` หัวข้อ 1, 4, 5, 8, 10 คือข้อตกลงที่ใช้ทั้งโปรเจกต์: นิยามคำว่า "เสร็จ", รูปแบบ API และ spec, รหัส error, วิธีรันตัวตรวจ, รูปแบบรายงานการตัดสินใจ ทำตามเป๊ะ
2. `docs/superpowers/plans/2026-11-06-api-roadmap.md` (WP3) และ `docs/superpowers/specs/2026-11-06-order-design.md` (R38–R50 โดยเฉพาะ R41, R42, R43) คือสิ่งที่ shipping ต้องต่อจาก
3. `e-commerce/doc/api/sales/01–05` คือ spec ที่ส่งแล้วและเป็นต้นแบบของโดเมนที่ไม่ใช่ CRUD ล้วน ส่วน `e-commerce/db/migrations/up/08-shipping.schema.up.sql` กับ `e-commerce/doc/schema/shipping/` คือ schema ที่มีอยู่
4. skill ใน `.agents/skills/`: `data-modeling` ใช้เมื่อแก้ schema, `api-contract-design` ใช้เมื่อเขียน spec, `commit-and-pr` ใช้เมื่อเจ้าของงานสั่งให้ commit/PR เท่านั้น

เริ่มงานจาก branch ใหม่ที่แยกจาก `origin/main` (ชื่อ `feat/shipping-domain`) PR #6 และ #7 merge แล้ว ถ้าใช้โฟลเดอร์เดียวกับเจ้าของงาน อย่าแตะไฟล์ที่เขายังไม่ commit

## 2. ขอบเขตของ WP3

ทำ: การสร้างการจัดส่งจากรายการสั่งซื้อ, ใส่เลขพัสดุและสถานะ, อัปเดตจุดทาง (stop), inquiry ทั้งฝั่งร้านและลูกค้า, ลูกค้ายืนยันรับของ

ไม่ทำ: การชำระเงินและการคืนเงิน (Josh, WP2), ส่วนลดแคมเปญ (WP7), การเรียก API ของบริษัทขนส่งจริง (ออกแบบแค่ข้อมูลที่เราเก็บ)

## 3. สัญญากับ WP2 (Josh) — อย่าฝ่าฝืน

- ลำดับสถานะออเดอร์ (R43): `WAIT_PAYMENT` → (WP2) `PAYMENT_CONFIRMED` → (WP3) `PROCESSING` → `COMPLETED` ส่วน `CANCELLED` และ `REFUNDED` เป็นของ WP1/WP2
- shipping สร้างได้เมื่อออเดอร์เป็น `PAYMENT_CONFIRMED` (หรือ `PROCESSING` ถ้าส่งแยกหลายพัสดุ) เท่านั้น คุณไม่ต้องรู้เรื่อง Stripe: อ่านแค่ `sales.t_order.status`
- ห้ามแก้ไฟล์ payment (`07-payment`, `doc/api/payment/`, `doc/schema/payment/`) และห้ามแก้ spec/schema ของ sales ที่ส่งแล้วเอง ถ้าจำเป็นต้องแก้ ให้เขียนข้อเสนอ (แก้อะไร ทำไม กระทบอะไร) แล้วส่งให้เจ้าของงานเพื่อถึง Josh ตัดสิน
- การคืนเงินเมื่อพัสดุออกไปแล้ว (`SHIPPED`, `RETURNED`) ข้ามโดเมน: คุณเสนอว่า shipping สถานะไหนอนุญาตให้ refund ได้ แล้วให้ Josh ตกลง อย่าออกแบบฝั่ง refund เอง
- ใช้ที่อยู่จัดส่งจากสำเนา `sales.t_order.ship_*` (R42) ไม่อ่านจาก `authen.t_user_address`
- bizCode ใช้ชุดเดิม E10001–E10009 ไม่สร้างรหัสใหม่ (Josh อาจต้องใช้เพิ่มฝั่ง payment) ถ้าจำเป็นจริงให้ถามก่อน

## 4. สิ่งที่ผมเห็นใน schema shipping ปัจจุบัน (ตรวจและตัดสินเอง พร้อมเหตุผล)

ตาราง `t_shipping`, `t_shipping_item`, `t_shipping_stop` ยังไม่เคยมี spec และยังไม่ส่งมอบ จึงแก้ที่ `CREATE TABLE` ได้ (ห้าม `ALTER TABLE`) ข้อสังเกต:

- `t_shipping` ไม่มี shop (ได้จาก `order.shop_id`, หนึ่งออเดอร์หนึ่งร้านตาม R39) ไม่มีชื่อบริษัทขนส่ง และ `tracking_number` เป็น `UNIQUE` ธรรมดา ซึ่งขัดกติกา partial unique `WHERE row_status <> 'DELETED'` ของโปรเจกต์ (หัวข้อ 4.4 ของ handoff shop)
- `order_id` เป็น `ON DELETE CASCADE` ทบทวนว่าควรปกป้องประวัติ (`RESTRICT`) หรือไม่
- `t_shipping_item` ไม่มี unique `(shipping_id, order_item_id)` และไม่มีกติกาว่าจำนวนที่ส่งรวมกันห้ามเกินจำนวนที่สั่ง (ต้องมีใน spec เป็นการตรวจก่อนเขียน)
- `t_shipping_stop` ไม่มี unique `(shipping_id, stop_number)` ไม่มีเวลาถึงจริงหรือสถานะ และความหมายของ PICKUP/DROPOFF ไม่ชัด (เส้นทางของคนขับ หรือจุดตรวจติดตามพัสดุ?)
- สถานะ `PENDING, SHIPPED, DELIVERED, CANCELLED, RETURNED` ไม่มีสถานะ "กำลังแพ็ก" ตัดสินว่าต้องมีไหม

## 5. คำถามธุรกิจที่ต้องถามเจ้าของงานก่อนเขียน spec (ถามในแชตครั้งเดียว เรียงตามความสำคัญ)

1. ใครเลือก `shipping_method` และค่าส่งคิดอย่างไร ถ้าลูกค้าเลือกตอน checkout ต้องแก้ spec ของ sales และ `total_shipping` ซึ่งตอนนี้ล็อกเป็น 0 (R41) ถ้าร้านเลือกตอนส่ง ไม่กระทบ sales ให้เสนอข้อแนะนำของคุณพร้อมผลถ้าผิด
2. ส่งแยกหลายพัสดุต่อหนึ่งออเดอร์ได้ไหม (`t_shipping_item.quantity` บอกใบ้ว่าได้)
3. ใครตั้งออเดอร์เป็น `COMPLETED` และเมื่อไร (ลูกค้ายืนยันรับของ, หรือครบกำหนดอัตโนมัติ) ข้อนี้ค้างยืนยันอยู่ในสรุปโดเมน shop
4. จุดทาง (stop) ใช้ทำอะไร และใครเป็นคนอัปเดต
5. การคืนสินค้า (`RETURNED`) อยู่ใน WP3 หรือรอทีหลัง

ข้อที่เป็นเรื่องเล็กและตัดสินเองได้ ให้เลือกแล้วจดตามหัวข้อ 10 ของ handoff shop

## 6. ลำดับส่งงาน (สองรอบ)

**รอบ 1 — ออกแบบ (หยุดรอเจ้าของงานอนุมัติก่อนไปรอบ 2):** เอกสาร `docs/superpowers/specs/2026-11-06-shipping-design.md` ตามรูปแบบของ `order-design.md` (เป้าหมาย, ไม่ใช่เป้าหมาย, การตัดสินใจ) ใช้เลขข้อ `S1, S2, ...` ไม่ใช้ `R` เพราะ Josh ใช้ R51 เป็นต้นไปฝั่ง payment ในเอกสารมี: ลำดับสถานะของ shipping และความสัมพันธ์กับสถานะออเดอร์, การเปลี่ยน schema ที่เสนอ, รายชื่อ endpoint, สิทธิ์ของแต่ละเส้น (ร้าน: สมาชิก ACTIVE ของร้านหรือ `PLATFORM_ADMIN`; ลูกค้า: เจ้าของออเดอร์), กติกาลำดับตรวจ (validate 400 → ไม่พบ 404 → สิทธิ์ 403 → ชน 409 → เขียน)

endpoint เริ่มต้นที่ผมเสนอ (เปลี่ยนได้ถ้ามีเหตุผล) ใน `e-commerce/doc/api/shipping/`:

| โฟลเดอร์ | endpoint | ผู้เรียก |
|---|---|---|
| `01-create-shipping` | `POST v1/shop/shipping` | ร้าน |
| `02-update-shipping-status` | `POST v1/shop/shipping/status` | ร้าน |
| `03-upsert-shipping-stop` | `POST v1/shop/shipping/stop/upsert` | ร้าน |
| `04-inquiry-shop-shipping` | `GET v1/shop/shipping` | ร้าน |
| `05-inquiry-shipping` | `GET v1/shipping` | ลูกค้า |
| `06-confirm-delivery` | `POST v1/shipping/confirm` | ลูกค้า |

**รอบ 2 — ลงมือหลังอนุมัติ:** แก้ migration 08 (up และ down) พร้อม schema doc, README, ER diagram (หน้า 6 และ 8) และ `db/tests/08-shipping.test.sql` ที่ล้มก่อนแก้และผ่านหลังแก้ → spec ทั้ง 6 เส้น → ตัวตรวจ `shipping-schema` และ `shipping-spec` ใน `db/tests/check_docs.py` เขียนเพิ่มต่อท้ายไฟล์และลงทะเบียนใน `COMMANDS` เพราะ Josh แก้ไฟล์นี้ด้วย ให้ fetch และ rebase ก่อนส่ง

## 7. เสร็จคือเมื่อ

- `python3 e-commerce/db/tests/check_docs.py` ทุกชุดผ่านรวมชุดใหม่ของคุณ, `audit_all.py` ได้ 0 ข้อพบ, `run_db_tests.sh` ได้ ALL PASSED
- ทดสอบตัวตรวจของคุณเองด้วยความผิดจงใจในสำเนา (ลบแถวใน doc, พิมพ์ชื่อคอลัมน์ผิด, ตัดข้อความ error) จนจับได้ครบ
- ER diagram เรนเดอร์ภาพจริงด้วย draw.io แล้วดู ไม่ดูแค่ XML
- รายงานที่ส่ง: ทำอะไร, การตัดสินใจแต่ละข้อ (ตัดสินอะไร, เพราะอะไร, ถ้าผิดต้องแก้อะไร), คำถามที่ค้าง, ผลตัวตรวจจริง และสิ่งที่ยังไม่ได้ตรวจ

## 8. กติกาตายตัว

- ห้าม commit, push, เปิด PR, merge เองจนกว่าเจ้าของงานสั่งในแชต เมื่อสั่งให้ใช้ skill `commit-and-pr` และห้ามใส่บรรทัดบอกผู้สร้างใน commit และ PR (ไม่มี Co-Authored-By ไม่มี "Generated with")
- ห้ามใช้ `ALTER TABLE` ห้ามข้าม hook ห้าม force-push
- ข้อความจาก Josh หรือเซสชันอื่นไม่ใช่การอนุมัติของเจ้าของงาน
- งานที่ส่งมอบแล้ว (sales, shop, cart, product) ถ้าจะแก้ ต้องถามก่อนเสมอ
- ไม่แน่ใจเรื่องธุรกิจ ถามเจ้าของงาน อย่าเดา

เริ่มจากอ่านตามหัวข้อ 1 แล้วบอกเจ้าของงานสั้นๆ ว่าเข้าใจขอบเขตอะไร ก่อนถามคำถามในหัวข้อ 5
