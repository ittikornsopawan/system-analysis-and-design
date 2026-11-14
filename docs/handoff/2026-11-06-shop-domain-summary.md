---
name: "Summary of the shop domain (T1 to T5)"
description: "Summary of the five shop domain tasks T1 to T5 done by the junior SA and reviewed by Josh on 2026-11-06, with the results of the checks; read it for the state of the shop domain at that date."
---

# สรุปรวมโดเมน shop (T1–T5)

วันที่: 2026-11-06 · ผู้ทำ: งาม (SA jr) · ผู้ตรวจ: Josh (lead SA) · สถานะ: T1–T5 ผ่านการตรวจของ Josh แล้ว เจ้าของงานตอบ "ตามนั้น" ยืนยันทุกกฎที่ค้างตามเอกสารนี้แล้ว (รวม G2) ยังไม่มีการ commit

เอกสารนี้สรุปงานที่รับต่อจาก [`2026-11-06-shop-domain-handoff.md`](2026-11-06-shop-domain-handoff.md) หัวข้อ 7 ทั้ง 5 งาน (shop type, shop และรูปของร้าน, ผู้ใช้ของร้าน, รายการสินค้าของร้าน, รีวิวสินค้า) พร้อมการตัดสินใจ คำถามค้าง และข้อสังเกตเรื่องเครื่องมือตรวจ

## ผลการตรวจล่าสุด (รันบนไฟล์จริงก่อนเขียนเอกสารนี้)

- `check_docs.py` ครบทุกชุดที่มี ผ่านหมด: `schema`, `shop-schema`, `er`, `er-lot`, `spec01`–`spec03`, `shop-spec`, `status-codes`, `biz-codes`, `shop-type-schema`, `shop-type-spec`, `shop-profile-schema`, `shop-profile-spec`, `shop-user-schema`, `shop-user-spec`, `shop-product-schema`, `shop-product-spec`, `shop-review-schema`, `shop-review-spec`, `cart-spec`, `order-spec`
- `audit_all.py`: `52 tables audited, 0 findings`
- `run_db_tests.sh`: `ALL PASSED` (migration up, down, up ซ้ำ และ `*.test.sql` ทุกไฟล์)
- ทดสอบตัวตรวจด้วยความผิดจงใจในสำเนา (ไม่แตะไฟล์จริง): T1 26 แบบ, T2 52 แบบ, T3 49 แบบ, T4 37 แบบ, T5 46 แบบ, `audit_all.py` 10 แบบ (ของ T3–T5 รันซ้ำหลังเปลี่ยนข้อความอนุมัติ) จับได้ครบทุกแบบ (ตัวที่หลุดระหว่างทางถูกแก้ตัวตรวจแล้ว ดูหัวข้อ 4)
- แบบทดสอบ SQL ของแต่ละงานล้มก่อนแก้ schema และผ่านหลังแก้ ทดสอบกับ migration ที่ถูกทำให้ผิดในสำเนาด้วย (T1 3 แบบ, T2 5 แบบ, T3 4 แบบ, T4 4 แบบ, T5 5 แบบ)

## 1. ไฟล์ที่เพิ่มหรือแก้

### API spec ใหม่ใน `e-commerce/doc/api/shop/` (แต่ละโฟลเดอร์มี `spec.md` และ `sequence.wsd` ว่าง)

| งาน | โฟลเดอร์ | endpoint |
|---|---|---|
| T1 shop type | `05-upsert-shop-type`, `06-upsert-shop-type-batch`, `07-inquiry-shop-type` | `POST v1/shop/type/upsert`, `POST v1/shop/type/upsert/batch`, `GET v1/shop/type` |
| T2 shop และรูป | `08-upsert-shop`, `09-upsert-shop-batch`, `10-inquiry-shop` | `POST v1/shop/upsert`, `POST v1/shop/upsert/batch`, `GET v1/shop` |
| T3 ผู้ใช้ของร้าน | `11-upsert-shop-user`, `12-upsert-shop-user-batch`, `13-inquiry-shop-user` | `POST v1/shop/user/upsert`, `POST v1/shop/user/upsert/batch`, `GET v1/shop/user` |
| T4 รายการสินค้าของร้าน | `14-inquiry-storefront-shop-product` | `GET v1/storefront/shop/product` (public) |
| T5 รีวิวสินค้า | `15-upsert-shop-product-review`, `16-inquiry-storefront-product-review` | `POST v1/shop/product-review/upsert`, `GET v1/storefront/product-review` (public) |

### Schema (แก้ที่ `CREATE TABLE` โดยตรง ไม่มี `ALTER TABLE`)

ไฟล์ `e-commerce/db/migrations/up/04-shop.schema.up.sql` (migration ขา down ไม่ต้องแก้ เพราะ `DROP TABLE` ลบ index ตามตารางอยู่แล้ว)

| ตาราง | การเปลี่ยนแปลง | งาน |
|---|---|---|
| `shop.m_shop_type` | `name` เปลี่ยนจาก `UNIQUE` ธรรมดาเป็น partial unique `uq_m_shop_type_name` | T1 |
| `shop.m_shop` | `name` เป็น partial unique `uq_m_shop_name`, เพิ่ม `CHECK ck_m_shop_margin_rate_total` (`platform_margin_rate + shop_margin_rate <= 100`), `type_id` เปลี่ยนจาก `ON DELETE CASCADE` เป็น `ON DELETE RESTRICT` | T2 |
| `shop.m_shop_image` | partial unique `uq_m_shop_image_shop_id_logo` และ `uq_m_shop_image_shop_id_wallpaper` (หนึ่ง LOGO และหนึ่ง WALLPAPER ต่อร้าน) | T2 |
| `shop.t_shop_user` | `UNIQUE (shop_id, user_id)` เปลี่ยนเป็น partial unique `uq_t_shop_user_shop_id_user_id` | T3 |
| `shop.t_shop_product` | ลบคอลัมน์ `quantity` และ `CHECK`, `UNIQUE (shop_id, product_id)` เปลี่ยนเป็น partial unique `uq_t_shop_product_shop_id_product_id` | T4 |
| `shop.t_shop_product_review` | เพิ่ม partial unique `uq_t_shop_product_review_shop_product_id_user_id` | T5 |

ไฟล์ที่ตามแก้ให้ตรงกับ migration:
- `e-commerce/doc/schema/shop/m_shop_type.md`, `m_shop.md`, `m_shop_image.md`, `t_shop_user.md`, `t_shop_product.md`, `t_shop_product_review.md`
- `e-commerce/doc/schema/README.md` (แก้เฉพาะจำนวนคอลัมน์ของ `t_shop_product` จาก 9 เป็น 8)
- `e-commerce/db/er-diagram.drawio` (หน้า 5 Shop และหน้า 8 All Tables): เอาป้าย `UK` ออกจาก `m_shop_type.name` และ `m_shop.name`, ลบแถว `UNIQUE (shop_id, user_id)` ของ `t_shop_user`, ลบแถว `quantity` และ `UNIQUE (shop_id, product_id)` ของ `t_shop_product` (ตารางหดที่ท้ายตาราง เส้น FK ไม่กระทบ) เรนเดอร์ด้วย draw.io ดูภาพจริงแล้วทุกครั้งที่แก้

### แบบทดสอบ SQL ใหม่ใน `e-commerce/db/tests/`

`04-shop-type.test.sql` (3 เทสต์), `04-shop-profile.test.sql` (4), `04-shop-user.test.sql` (3), `04-shop-product.test.sql` (3), `04-shop-review.test.sql` (3)

### เครื่องมือตรวจ

- `e-commerce/db/tests/check_docs.py`: เพิ่ม subcommand `shop-type-spec`, `shop-type-schema`, `shop-profile-spec`, `shop-profile-schema`, `shop-user-spec`, `shop-user-schema`, `shop-product-spec`, `shop-product-schema`, `shop-review-spec`, `shop-review-schema`, `biz-codes` และเพิ่ม spec ใหม่ใน `SINGLE_UPSERT_SPECS` (05, 08, 11) กับ `BATCH_UPSERT_SPECS` (06, 09, 12) ของ `status-codes`
- `e-commerce/db/tests/audit_all.py`: แก้ช่องโหว่ทิศ doc ไปหา migration (ดูหัวข้อ 4)

### ที่ไม่ใช่งานของผมและไม่ได้แตะ

`e-commerce/doc/api/sales/`, `cart` และ `order-spec` / `cart-spec` ใน `check_docs.py` (ของ Josh และเซสชันอื่น) รวมถึงการแก้ `shop/01`–`shop/04` ที่ Josh ทำเอง (เพิ่มกฎสิทธิ์ `E10009`, เงื่อนไข "ร้านต้อง ACTIVE", `sp.row_status <> 'DELETED'`, และล่าสุดกฎห้ามขายต่ำกว่าต้นทุนที่ lot: `CHECK ck_t_shop_product_sku_lot_price_not_below_cost` ใน `t_shop_product_sku_lot` พร้อม doc และ `04-shop-lot.test.sql` ซึ่ง Josh แก้เอง ไม่รวมในไฟล์ของ T1–T5 ข้างบน)

## 2. การตัดสินใจรวม

รูปแบบ: ตัดสินอะไร / ถ้าผิดเสียอะไร

### 2.1 เจ้าของงานอนุมัติแล้ว

เจ้าของงานตอบ "ตามนั้น" ยืนยันทุกกฎที่เขียนไว้ในเอกสารนี้ รวม G2 ทุกกฎจึงเป็น "approved by the product owner" และข้อความในหัวข้อกฎของ spec 11–16 เป็นประโยคนี้แล้ว

#### ก. อนุมัติระหว่างทำงาน (ตามที่ Josh แจ้งมา)

- เพดาน `platformMarginRate + shopMarginRate <= 100` (CHECK ใน schema และใน spec 08–09) / ถ้าผิด: ต้องถอด CHECK และกฎใน spec (ถ้าอัตราเป็น markup บนต้นทุน เพดาน 100 จะผิด)
- โมเดลสิทธิ์: แก้/ลบ/archive ร้านต้องเป็น ADMIN ของร้านหรือผู้ใช้ที่มี role `PLATFORM_ADMIN` ตอบ 403 `E10009` และเปลี่ยน `platformMarginRate` ได้เฉพาะ `PLATFORM_ADMIN` / ถ้าผิด: ต้องเปลี่ยนชื่อ role หรือสิทธิ์ใน SQL และข้อความของ spec 08–09, 11–13
- รหัส 403 Forbidden ใช้ `E10009` (ไม่ใช่ `E10007` ที่ cart ใช้เป็น 409) / ถ้าผิด: bizCode ชนกันข้าม spec (ตัวตรวจ `biz-codes` จับได้)
- margin (`platformMarginRate`, `shopMarginRate`) ใน `GET v1/shop` คืนเฉพาะร้านที่ผู้เรียกเป็นสมาชิก ACTIVE หรือผู้เรียกเป็น `PLATFORM_ADMIN` ร้านอื่นคืน `null` คงคีย์ไว้ / ถ้าผิด: margin ของแพลตฟอร์มอาจรั่วไปยังร้านอื่น
- ร้านที่ไม่ใช่ ACTIVE ไม่มีหน้า สินค้าของร้านนั้นดูและซื้อไม่ได้ (ใช้ใน spec 14 และ 16 ด้วย) / ถ้าผิด: ร้านที่ปิดแล้วยังขายได้
- `shop.m_shop.type_id` เป็น `ON DELETE RESTRICT` / ถ้าผิด: การลบ shop type ตรง ๆ ในฐานข้อมูลจะลบร้านทั้งหมดของ type นั้นตาม

#### ข. อนุมัติเมื่อเจ้าของงานตอบ "ตามนั้น"

กฎของ T1–T2 เดิมได้คำตอบ "ตามที่เสนอ" ในแชตระหว่างทำงาน กฎของ T3–T5 เดิมเขียนใน spec ว่า "decided by the lead SA, pending product owner confirmation" ตอนนี้ทั้งหมดได้รับการยืนยันแล้ว

T1 shop type
- `name` ไม่ซ้ำเฉพาะแถวที่ไม่ใช่ DELETED (partial unique) ชื่อที่ลบแล้วใช้ซ้ำได้ / ถ้าผิด: ชื่อที่ลบแล้วใช้ซ้ำไม่ได้ตลอดไป
- ลบ/archive type ไม่ได้ถ้ามีร้านที่ไม่ใช่ DELETED ใช้อยู่ (409 `E10006`) / ถ้าผิด: ร้านที่ archive ไว้อาจชี้ไป type ที่ถูกลบ
- DELETED เป็นสถานะสุดท้าย (id ที่ลบแล้วนับเป็น 404) INACTIVE/LOCKED/ARCHIVED กลับเป็น ACTIVE ได้ / ถ้าผิด: ถ้าต้องเปิดแถวที่ลบกลับ ต้องแก้กฎและ SQL
- การเปรียบเทียบชื่อแบบตรงตัว (ตัวพิมพ์ใหญ่เล็กต่างกันถือว่าไม่ซ้ำ) / ถ้าผิด: ได้ "Fashion" กับ "fashion" พร้อมกัน ต้องเปลี่ยนเป็น index บน `lower(name)`
- ทุกคนที่มี token เรียก API จัดการ shop type ได้ (ยังไม่จำกัด role) / ถ้าผิด: ผู้ใช้ทั่วไปแก้ข้อมูลกลางของแพลตฟอร์มได้
- endpoint เป็นรูป `v1/shop/<ชื่อ>` / ถ้าผิด: ต้องเปลี่ยนชื่อ endpoint ใน spec และตัวตรวจ

T2 shop และรูป
- ผู้เรียกที่มี token สร้างร้านได้ และกลายเป็น ADMIN ของร้านใหม่ในธุรกรรมเดียวกัน / ถ้าผิด: ถ้าให้แพลตฟอร์มสร้างแล้วกำหนด ADMIN เอง ต้องตัดข้อนี้และออกแบบวิธีตั้ง ADMIN คนแรก
- ลบร้านไม่ได้ถ้ามีสินค้า (`t_shop_product`) หรือออเดอร์ (`sales.t_order`) ที่ไม่ใช่ DELETED, archive ทำได้เสมอ, ลบร้านลบรูปตามด้วย (soft delete) / ถ้าผิด: ไม่ตรวจ `campaign.campaign_shop` และ `cart.t_cart` (Josh บันทึกเป็นงาน WP7)
- รูป: LOGO 1 รูป, WALLPAPER 1 รูป (บังคับด้วย partial unique), BANNER ไม่เกิน 10 (ค่า config) / ถ้าผิด: ถ้าต้องการ WALLPAPER หลายรูป ต้องถอด index ของ WALLPAPER
- ส่งโลโก้ใหม่โดยไม่มี `id` ขณะมีโลโก้เดิมอยู่ = 409 `E10003` เปลี่ยนโลโก้ทำได้โดยแก้แถวเดิมด้วย `id` หรือลบแถวเก่าในคำขอเดียวกัน / ถ้าผิด: ถ้าต้องการให้ส่งใหม่แล้วแทนอัตโนมัติ ต้องเปลี่ยนกฎ
- ลำดับรูป `ORDER BY type, seq, created_at, id` (type เรียงตามตัวอักษร BANNER, LOGO, WALLPAPER) / ถ้าผิด: ถ้าต้องการโลโก้ก่อน ให้ client หยิบตาม `type`
- การเปลี่ยน margin rate ไม่คำนวณ lot ย้อนหลัง (margin ของ lot คำนวณตอนบันทึก lot) / ถ้าผิด: ต้องแก้ `shop/01` ให้คำนวณใหม่
- role `PLATFORM_ADMIN` ตั้งชื่อเอง เพราะ schema ยังไม่มี seed ของ role / ถ้าผิด: แก้ SQL และข้อความในหลาย spec

T3 ผู้ใช้ของร้าน
- เพิ่มสมาชิกมีผลทันที ไม่มีขั้นตอนตอบรับคำเชิญและไม่แจ้งเตือน / ถ้าผิด: ผู้ใช้ถูกเพิ่มเข้าร้านโดยไม่รู้ตัว ต้องเพิ่มสถานะและ endpoint ตอบรับ
- ADMIN คนสุดท้ายของร้านห้ามลบ, archive, ลดเป็น STAFF, หรือเปลี่ยนเป็น INACTIVE/LOCKED/ARCHIVED (409 `E10006`) `PLATFORM_ADMIN` ข้ามไม่ได้ ตรวจจากสถานะสุดท้ายหลังเขียนทั้งคำขอ และ service ต้องล็อกแถวของร้านใน transaction เดียวกัน / ถ้าผิด: ร้านอาจไม่มี ADMIN เลย
- STAFF ทำได้เฉพาะลบหรือ archive แถวของตัวเอง (ออกจากร้าน) / ถ้าผิด: STAFF ที่ควรเชิญเพื่อนได้จะทำไม่ได้
- `GET v1/shop/user` ต้องส่ง `shopId` หรือ `userId` อย่างใดอย่างหนึ่ง "ร้านของฉัน" คือ `userId` ของผู้เรียกโดยไม่มี `shopId` `userId` ของคนอื่นใช้ได้เฉพาะ `PLATFORM_ADMIN` / ถ้าผิด: ADMIN ของร้านกรอง `userId` ของลูกทีมไม่ได้
- inquiry ไม่คืน username และอีเมล (เก็บเข้ารหัส) คืนเฉพาะ `displayName` และ `profilePicturePath` / ถ้าผิด: ถ้า UI ต้องแสดงอีเมล ต้องออกแบบการถอดรหัส
- `shopId` และ `userId` เปลี่ยนไม่ได้ตอน update (400) / ถ้าผิด: ถ้าอยากย้ายสมาชิก ต้องตรวจ unique ที่ปลายทางเพิ่ม

T4 รายการสินค้าของร้าน
- ลบ `t_shop_product.quantity` (ไม่มี spec ใดอ่านหรือเขียนคอลัมน์นี้ และสต็อกจริงอยู่ที่ lot) / ถ้าผิด: ถ้าต้องเก็บเป็นค่าที่คำนวณ ต้องนิยามสูตรและที่เก็บ
- `GET v1/storefront/shop/product` เป็น public มีบล็อกร้าน (ชื่อ คำอธิบาย ชื่อ type และรูป ACTIVE) ไม่มี margin ไม่มีสมาชิก / ถ้าผิด: ถ้าต้องการข้อมูลร้านเพิ่ม ไม่มีคอลัมน์รองรับ
- สินค้าหมดทุก SKU แสดงด้วย `OUT_OF_STOCK` และราคา `null` มี filter `inStock=true` ซ่อนได้ / ถ้าผิด: ถ้าต้องซ่อนเสมอ ต้องตัด filter
- sort `NEWEST` (default), `PRICE_ASC`, `PRICE_DESC` (สินค้าหมดต่อท้ายเสมอ), `NAME_ASC` ทุก sort ลงท้ายด้วย `productId` เป็น tie-break; `categoryId` รวมหมวดย่อยด้วย recursive query / ถ้าผิด: ORDER BY ผิดทำให้หน้าซ้ำหรือข้ามสินค้า
- สถานะ shop product ไม่เปลี่ยนด้วย API ร้านซ่อนสินค้าโดยปิด SKU ทุกตัวผ่าน `shop/01` ไม่ทำ upsert shop product / ถ้าผิด: ร้านซ่อนสินค้าทั้งตัวไม่สะดวก ต้องเพิ่ม upsert ภายหลัง
- ตัวอย่าง `NEWEST` ไม่คืนเวลาที่ร้านเพิ่มสินค้า จึงตรวจลำดับ NEWEST จากตัวอย่างไม่ได้ / ถ้าผิด: ต้องเพิ่มฟิลด์ `listedAt` ถ้าต้องการเทสต์ลำดับนี้

T5 รีวิวสินค้า
- เขียนรีวิวได้เฉพาะคนที่เคยซื้อ: ผู้เรียกมีออเดอร์ `COMPLETED` ที่มีรายการของร้านและสินค้าเดียวกัน ตรวจเฉพาะตอนเพิ่มใหม่ (403 `E10009`) สถานะ `COMPLETED` ตั้งโดย API จัดส่ง (WP3) ซึ่งยังไม่มี spec / ถ้าผิด: ถ้านิยามเปลี่ยน (เช่นรวม REFUNDED) ต้องแก้คิวรีและตัวตรวจ
- 1 user รีวิวสินค้าหนึ่งตัวของร้านหนึ่งได้ครั้งเดียว (partial unique) แก้รีวิวเดิมด้วย `id` ลบได้ (204) และรีวิวใหม่ได้โดยผ่านกฎ "เคยซื้อ" ใหม่ / ถ้าผิด: ถ้าต้องการรีวิวต่อการซื้อแต่ละครั้ง ต้องผูกกับ order item และเปลี่ยน schema
- ไม่มี moderation: ผู้ใช้ตั้งสถานะได้เฉพาะ `ACTIVE`/`DELETED` / ถ้าผิด: ต้องเพิ่ม API และสิทธิ์ `PLATFORM_ADMIN`
- inquiry สาธารณะแสดงผู้เขียนด้วย `displayName` และ `profilePicturePath` เท่านั้น คืน `summary` (`averageRating` ปัด half up 2 ตำแหน่ง, `ratingCount`, `ratingBreakdown`) จากรีวิว ACTIVE ทั้งหมด ไม่ขึ้นกับ filter / ถ้าผิด: ถ้าต้องปิดบังชื่อ ต้องกำหนดกฎซ่อนชื่อ
- เส้นเขียนรีวิวไม่ใส่ใน `SINGLE_UPSERT_SPECS` ของ `status-codes` (ไม่มี Archive สำหรับลูกค้า) ตัวตรวจ `shop-review-spec` ตรวจรหัส 201/200/204 เอง / ถ้าผิด: ต้องปรับตัวตรวจกลาง
- PLATFORM_ADMIN ไม่ได้รับยกเว้นกฎ "เคยซื้อ" / ถ้าผิด: ผู้ดูแลที่ต้องเขียนรีวิวทดสอบทำไม่ได้
- G2 (เจ้าของงานยืนยันแล้ว): update แทนที่ `comment` ทั้งค่า คำขอแก้ที่ไม่ส่ง `comment` ลบ comment (ต่างจากกฎ "คงเดิมเมื่อไม่ส่ง" ของ margin) / ถ้าผิด: ไคลเอนต์ที่ลืมส่ง `comment` ลบคอมเมนต์โดยไม่ตั้งใจ

## 3. คำถามค้างสำหรับเจ้าของงาน

เจ้าของงานยืนยันกฎทั้งหมดในหัวข้อ 2 แล้ว (รวม G2) คำถามด้านล่างยังเปิดอยู่ เพราะเจ้าของงานยังไม่ได้ตอบ

1. ชื่อ role `PLATFORM_ADMIN` ใช้ตามนี้ได้ไหม และจะ seed role ใน `author.m_role` อย่างไร
2. ควรแสดงคะแนนเฉลี่ยในหน้าสินค้า (`shop/04`) และรายการสินค้าของร้าน (`shop/14`) ด้วยไหม (ตอนนี้มีเฉพาะใน inquiry รีวิว)
3. ลบร้านที่มี `campaign_shop` ผูกอยู่ควรห้ามไหม (Josh บันทึกเป็น WP7, ตอนนี้ spec 08–09 ไม่ตรวจ)
4. กฎ "เคยซื้อ" พึ่งสถานะ `COMPLETED` ที่ API จัดส่ง (WP3) ตั้ง ซึ่งยังไม่มี spec ต้องกำหนดเมื่อออกแบบ API จัดส่ง
5. ตารางหลักของโดเมน product ที่ส่งมอบแล้ว (`m_product_type`, `m_product_category`, `m_product_brand` ฯลฯ) ยังใช้ `name UNIQUE` ธรรมดา ซึ่งบล็อก soft delete เหมือนที่ T1 แก้ให้ shop type จะแก้ให้ตรงกันไหม (Josh บันทึกเป็น backlog)
6. การป้องกัน race ของกฎ ADMIN คนสุดท้ายเขียนเป็นกฎให้ service ล็อกแถวร้าน ไม่มี SQL ล็อกใน spec ต้องการให้กำหนดรูปแบบล็อกชัดกว่านี้ตอนเขียนโค้ดไหม

(เลขข้อเดิมในฉบับก่อนหน้า: ข้อ 3–8 ตอนนี้เป็นข้อ 1–6 ส่วนข้อ 1 และ 2 เดิมถูกตัดออกเพราะเจ้าของงานตอบแล้ว)

## 4. ข้อสังเกตเครื่องมือ

### `audit_all.py` ที่แก้ (C2)

ช่องโหว่เดิม: ตรวจเฉพาะทิศ migration ไปหา doc (index ใน migration ต้องอยู่ใน doc) ไม่ตรวจทิศกลับ ทำให้ doc ที่มี index เกินจาก migration ยังได้ `0 findings`

ทดสอบก่อนแก้ด้วย mutation 10 แบบในสำเนา จับได้ 3 หลุด 7 (doc มี unique index เกิน, index ธรรมดาเกิน, index ในตารางที่ migration ไม่มี index, `CREATE TABLE` เกิน, `ALTER TABLE`, แถว `uq_...` เกิน 2 แบบ) หลังแก้จับได้ 10 จาก 10 และบนงานจริงยัง `0 findings`

ที่เพิ่มใน `audit_docs`: (ก) ทุกคำสั่ง `CREATE`/`ALTER`/`DROP` ในบล็อก SQL ของ doc ต้องตรงกับ DDL หรือ index ของตารางนั้นใน migration (ข) แถว `uq_...` ในตาราง constraint ต้องเป็นชื่อ index ที่ migration มี หรือตารางนั้นต้องมี `UNIQUE` ในตัวตาราง

### เพิ่ม `biz-codes` ใน `check_docs.py`

bizCode ที่ขึ้นต้นด้วย `E` หนึ่งตัวต้องมี HTTP status เดียวทั้ง `doc/api` เพิ่มหลังเจอ `E10007` ชนกับ cart (403 กับ 409) ตัวตรวจเดิม `status-codes` ไม่จับรหัสชนข้าม spec

### ช่องโหว่ที่เหลือ

- `audit_all.py` ตรวจคอลัมน์ของ alias ที่มาจาก CTE ไม่ได้ (เช่น `v.price_form` ผ่าน audit) มีตัวตรวจเฉพาะ spec 14 ใน `shop-product-spec` ชดเชย ส่วน spec อื่นที่ใช้ CTE ในอนาคตต้องมีตัวตรวจเอง (Josh ระบุว่ายังไม่ต้องเพิ่มใน `audit_all.py`)
- ไม่มีการตรวจแถว `UNIQUE (...)` ใน ER diagram เทียบกับ migration และแถว `uq_...` ของตารางที่มี `UNIQUE` inline ตรวจไม่ได้ (migration ไม่ตั้งชื่อ constraint)
- `status-codes` บังคับตัวอย่าง Archive จึงไม่ครอบคลุมเส้นที่ไม่มี Archive (เส้นรีวิว) ตัวตรวจของเส้นนั้นตรวจเอง
- `run_db_tests.sh` ใช้พอร์ต 54339 ตายตัว เคยพบความล้มเหลวชั่วคราวครั้งเดียวที่รันซ้ำแล้วผ่าน น่าจะชนกับการรันของอีกเซสชัน
- `check_docs.py` ถูกแก้โดยหลายเซสชัน (shop, cart, order) ต้องอ่านไฟล์ล่าสุดก่อนบันทึกทุกครั้ง เสี่ยงทับกันถ้าแก้พร้อมกัน
- สคริปต์ช่วยของผม (จัดความกว้างตาราง, ตัวสร้าง spec, mutation test) อยู่ใน scratchpad ไม่ได้อยู่ใน repo ถ้าต้องการให้เก็บไว้ ต้องย้ายเข้ารีโปและแก้ path
- ตัวตรวจ `shop-*-spec` ตรวจโครงสร้าง ตัวอย่าง และความสอดคล้องข้าม spec แต่ไม่ได้รัน SQL ใน spec กับฐานข้อมูลจริง (audit ตรวจแค่ว่าตารางและคอลัมน์มีจริง)
