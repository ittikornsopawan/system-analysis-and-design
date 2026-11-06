---
name: ตารางหลักที่ยังขาด (product type, product brand, consent type) — WP6
description: เอกสารออกแบบรอบ 1 ของ WP6 ใช้อ่านก่อนแก้ migration, schema doc, ER และเขียน API 9 เส้นของ m_product_type, m_product_brand, m_consent_type
status: approved
approved_by: Ittikorn (Aof) Sopawan (product owner, ตอบผ่าน Josh)
approved_at: 2026-11-06
---

# ตารางหลักที่ยังขาด (product type, product brand, consent type) — WP6

วันที่: 2026-11-06 · ผู้เขียน: Marry (SA) · สถานะ: รอบ 1 รอ Josh ตรวจ (ประตู 1) ยังไม่เริ่มแก้ migration หรือเขียน spec · `approved_by`: Ittikorn (Aof) Sopawan ตอบผ่าน Josh 2026-11-06 ("ตามที่แนะนำ" ต่อ Q1 และ Q4) · Josh (Lead SA) ตัดสินแล้ว 2026-11-06: ชื่อซ้ำหลังลบ (B1), `is_required` (B7), ชื่อ endpoint (B5), และให้ upsert เป็น `PLATFORM_ADMIN` เท่านั้น (B6) ข้อความของ Josh ไม่ใช่การอนุมัติแทนเจ้าของงาน

ตามแผน WP6 ใน [roadmap](../plans/2026-11-06-api-roadmap.md) ใช้ต้นแบบ `shop/05`–`07` (shop type) ข้อเท็จจริงทั้งหมดอ่านจาก `origin/main` (738f215)

## เป้าหมาย

- ผู้ดูแลสร้าง แก้ ลบ และ archive ประเภทสินค้า ยี่ห้อสินค้า และประเภท consent ได้ผ่าน API ที่มีอยู่ในรูปแบบเดียวกับตารางหลักอื่น (upsert, upsert batch, inquiry)
- ลบหรือ archive ไม่ได้ขณะที่ยังมีสินค้าหรือ consent ใช้อยู่ ฐานข้อมูลบังคับกฎนี้อีกชั้น (FK `RESTRICT`)
- ชื่อที่ถูกลบแบบ soft ใช้ซ้ำได้ เหมือน shop type

## ไม่ใช่เป้าหมาย

- การตรวจสิทธิ์แบบ permission/scope (เป็นของ WP5) WP6 ใช้เฉพาะ role `PLATFORM_ADMIN` ตามสัญญาที่ spec อื่นใช้อยู่ (ดู B6)
- แก้ spec ที่ส่งแล้ว (`product/01`–`09`, `consent/01`–`05`) การเปลี่ยนจะเป็นข้อเสนอถึง Josh
- แก้ปัญหาแบบเดียวกันของตารางที่ส่งแล้วอื่น (`m_product_category`, `m_product_category_attribute`, `m_product.category_id`) รายงานแยกท้ายเอกสาร
- ความหมายเชิงบังคับของ `m_consent_type.is_required` (ดู B7)

## ผลงาน

- Migration `00-common` (`m_consent_type`) และ `03-product` (`m_product_type`, `m_product_brand`): partial unique index 3 ตัว และถ้าเจ้าของงานอนุมัติ B2: FK 3 ตัวของ `m_product` และ `t_consent` เป็น `RESTRICT` (ส่วน B2 **ไม่แตะ migration จนกว่า Josh แจ้งอนุมัติ**)
- schema doc 5 ไฟล์ (`m_product_type`, `m_product_brand`, `m_product`, `m_consent_type`, `t_consent`), README (จำนวนตารางและคอลัมน์ไม่เปลี่ยน), ER diagram (หน้า 1 ถึง 8 เท่าที่ตารางเหล่านี้ปรากฏ ไม่มีตารางใหม่)
- แบบทดสอบ SQL `db/tests/03-product-master.test.sql` และ `db/tests/00-consent-type.test.sql`
- Spec 9 เส้น: `product/10`–`15`, `consent/06`–`08` (upsert และ batch มี 403 `PLATFORM_ADMIN`)
- ตัวตรวจ `product-master-spec`, `product-master-schema`, `consent-type-spec`, `consent-type-schema` ต่อท้าย `check_docs.py`

## ตารางข้อเท็จจริงที่อ้างอิง

| ข้อเท็จจริง | ที่มา | สถานะการตรวจ |
|---|---|---|
| `m_product_type`, `m_product_brand`: `name VARCHAR(128) NOT NULL UNIQUE`, `description VARCHAR(256) NOT NULL` | `03-product.schema.up.sql` | อ่านจากไฟล์ |
| `m_consent_type`: `name VARCHAR(128) NOT NULL UNIQUE`, `description TEXT` (nullable), `is_required BOOLEAN NOT NULL DEFAULT FALSE` | `00-common.schema.up.sql` | อ่านจากไฟล์ |
| FK เข้า: `m_product.type_id`, `m_product.brand_id`, `t_consent.consent_type_id` เป็น `ON DELETE CASCADE` | migration ข้างต้น | อ่านจากไฟล์ |
| แบบ shop type: partial unique `uq_m_shop_type_name`, `shop.m_shop.type_id` เป็น `RESTRICT`, ทดสอบด้วย `04-shop-type.test.sql` และ `04-shop-profile.test.sql` test 4 | `04-shop.schema.up.sql` | อ่านจากไฟล์ |
| `product/01`, `03` ตรวจ type และ brand ว่า `row_status = 'ACTIVE'` และ `typeId`, `brandId` บังคับทุกคำขอ | `product/01` หัวข้อ Database Relations | อ่านจากไฟล์ |
| `consent/02` ตรวจ consent type ว่า `ACTIVE`, `consent/01`, `03`, `05` อ่านเฉพาะ `ct.name` | `consent/*/spec.md` | อ่านจากไฟล์ |
| ไม่มี spec ใดอ่านหรือเขียน `m_consent_type.is_required` | `grep` ทั้ง `e-commerce/doc` | ค้นแล้ว ไม่พบ |
| สิทธิ์ของ category และ shop type: ผู้ถือ access token ทุกคน ไม่มีการตรวจ role | `product/04`, `shop/05` กฎของ spec | อ่านจากไฟล์ |

## การตัดสินใจ

ป้าย: **เจ้าของงานตอบแล้ว** (ยังไม่มี), **Lead ตัดสิน** (Josh), **รอเจ้าของงาน** (Josh นำไปถาม), **ตัดสินเอง** (ผมเลือก ถ้าผิดแก้ตามที่ระบุ)

- **B1 (Lead ตัดสิน: Q2 ชื่อที่ลบแล้วใช้ซ้ำได้; ตามกติกา 4.4)** `name` ของทั้งสามตารางเป็น partial unique `WHERE row_status <> 'DELETED'` แทน `UNIQUE` ธรรมดา ชื่อ index `uq_m_product_type_name`, `uq_m_product_brand_name`, `uq_m_consent_type_name` ลบ `UNIQUE` ออกจาก `CREATE TABLE` เพราะชื่อที่ถูกลบแบบ soft ต้องใช้ซ้ำได้ และไม่มีเส้น API ลบจริง การเทียบชื่อตรงตัว (ตัวพิมพ์ต่างกันคือคนละชื่อ) ชื่อที่ถือโดยแถว `INACTIVE`, `LOCKED`, `ARCHIVED` ยังถือว่าถูกใช้ ถ้าผิด (ต้องการให้ชื่อใช้ซ้ำไม่ได้ตลอดไป): กลับเป็น `UNIQUE` ในตาราง ผลต่อ spec คือ query "Check duplicate name" ไม่กรอง `DELETED` (ตรงกับ spec category)
- **B2 (ข้อเสนอ รอเจ้าของงาน Q4; ห้ามแก้ migration จนกว่า Josh แจ้งอนุมัติ)** เปลี่ยน FK `product.m_product.type_id`, `product.m_product.brand_id` และ `consent.t_consent.consent_type_id` จาก `ON DELETE CASCADE` เป็น `RESTRICT` ตามแบบ `shop.m_shop.type_id` เพราะ `CASCADE` ทำให้การลบแถว type, brand หรือ consent type จริงลามต่อเงียบๆ: ลบ brand → `m_product` → `cart` item, `shop.t_shop_product`, `sales.t_order_item` (ประวัติออเดอร์), `m_product_*` ลูก, `campaign`; ลบ consent type → `t_consent` → `authen` การยอมรับ consent ของผู้ใช้ (หลักฐานทางกฎหมาย) นี่คือการแก้ `CREATE TABLE` ของ `m_product` และ `t_consent` ที่ส่งแล้ว
  - **ผลต่อ spec ที่ส่งแล้ว: ไม่มี** ตรวจด้วย `grep "DELETE FROM" e-commerce/doc/api` ไม่พบคำสั่งลบแถวจริงในทุก spec ทุกเส้นลบแบบ soft (`row_status = 'DELETED'`) และ `FK` เปลี่ยนเฉพาะการลบจริงที่เกิดนอก API spec ที่อ่านหรือเขียนตารางเหล่านี้ไม่ต้องแก้: `product/01`–`03` (เขียน `m_product`), `product/04`, `06` (อ่าน `m_product` เพื่อตรวจ category ถูกใช้), `consent/01`–`05` (อ่านหรือเขียน `t_consent`) และ `cart/01`–`03`, `sales/01`–`03`, `shop/01`, `02`, `04`, `14`–`16` (อ่าน `m_product`)
  - **ที่ต้องแก้ถ้าอนุมัติ:** migration `03-product` และ `00-common` (3 FK), schema doc `m_product.md`, `t_consent.md` (ตารางข้อจำกัดและ SQL block), แบบทดสอบ SQL (ตรวจ `pg_constraint.confdeltype = 'r'`) ไม่แตะ ER diagram (ไม่แสดงกฎลบ) และไม่ต้องแก้ README (จำนวนคอลัมน์และ FK เท่าเดิม)
  - **แบบทดสอบเดิมที่แตะตารางเหล่านี้ (ไล่แล้ว อ่านอย่างเดียว):** มีไฟล์เดียวคือ `db/tests/03-product-sku-levels.test.sql` (สร้าง `m_product_type`, `m_product_brand`, `m_product` เป็นข้อมูลตั้งต้น) การลบจริงในไฟล์นี้คือ test 7 ลบ `m_product_option_value` เท่านั้น (ลูกของ option ไม่ใช่ของ type หรือ brand) และไฟล์จบด้วย `ROLLBACK` จึงไม่พึ่ง `CASCADE` ของ FK ที่จะเปลี่ยน การลบจริงอื่นใน `db/tests` คือ `m_shop_type` (`04-shop-profile.test.sql`) และ `m_campaign` (`09-campaign.test.sql`) ซึ่งไม่เกี่ยว ไม่มีแบบทดสอบใดแตะ `t_consent` หรือ `m_consent_type` และ migration ขา down ใช้ `DROP TABLE` เรียงย้อนลำดับอยู่แล้ว ไม่ขึ้นกับการกระทำของ FK **ต้องรัน `run_db_tests.sh` หลังแก้ เพื่อยืนยันอีกครั้ง** (ตอนนี้ยังไม่ได้รัน)
  - ถ้าไม่อนุมัติ: WP6 ใช้ได้โดยไม่มี B2 กฎ B3 ยังบังคับที่ชั้น API เท่านั้น และตารางเหล่านี้ลบจริงแล้วลามต่อได้ ถ้าเจ้าของงานอนุมัติทีหลัง ทำได้โดยไม่ย้ายข้อมูล เพราะยังไม่มี DB จริง
- **B3 (ตัดสินเอง ตามแบบ shop type และ category)** ลบ (`DELETED`) หรือ archive (`ARCHIVED`) ไม่ได้ถ้ามี `m_product` (สำหรับ type และ brand) หรือ `t_consent` (สำหรับ consent type) ที่ไม่ใช่ `DELETED` อ้างอยู่ → 409 `E10006` `INACTIVE` และ `LOCKED` ทำได้แม้มีแถวใช้อยู่ แถวเหล่านั้นไม่ถูกแก้ ถ้าผิด (ต้องการให้ลบแล้วแถวที่ใช้ตามไปด้วย): ต้องมีกติกาการลบต่อเนื่องซึ่งขัดกับ B2
- **B4 (ตัดสินเอง, ผลที่ตามมา)** `product/01`, `03` ตรวจว่า type และ brand เป็น `ACTIVE` ทุกคำขอเขียนสินค้า และ `consent/02` ตรวจ consent type เป็น `ACTIVE` ดังนั้นเมื่อตั้ง type, brand หรือ consent type เป็น `INACTIVE`, `LOCKED` หรือ `ARCHIVED` สินค้าหรือ consent ที่ใช้อยู่จะแก้ไขไม่ได้จนกว่าจะเปิด `ACTIVE` อีกครั้ง (ไม่มีสินค้าหรือ consent ถูกเปลี่ยนเอง) ผมเขียนผลนี้ไว้ในคำอธิบาย `rowStatus` ของ spec ใหม่ ไม่แก้ spec เดิม ถ้าผิด (ต้องการให้แก้สินค้าเดิมได้): ต้องแก้ query ตรวจใน `product/01`, `03` และ `consent/02` ให้ตรวจเฉพาะเมื่อ id เปลี่ยน — เสนอ Josh ได้ภายหลัง
- **B5 (Lead ตัดสินกรอบ; ผมตรวจ consent แล้ว)** ชื่อ endpoint เดิมของ consent คือ `v1/consent/active`, `v1/consent/submit`, `v1/consent`, `v1/consent/upsert`, `v1/consent/pending` ดังนั้น `v1/consent/type`, `v1/consent/type/upsert`, `v1/consent/type/upsert/batch` ไม่ชนกับเส้นเดิม (ตัวเลือก path ต่างกัน) ชื่อ endpoint: `POST v1/product-type/upsert`, `POST v1/product-type/upsert/batch`, `GET v1/product-type` และ `product-brand` ทำนองเดียวกัน (ตามที่ `product-category` ใช้ในกลุ่มเดียวกัน) ส่วน consent ใช้ `v1/consent/type/...` (ตามที่ shop ใช้ `v1/shop/type`) ลำดับโฟลเดอร์ upsert, batch, inquiry ตาม shop type: `product/10`–`12` type, `13`–`15` brand, `consent/06`–`08` ฟิลด์ใน response: `productTypeId`, `productBrandId`, `consentTypeId`; array ใน batch: `productTypes`, `productBrands`, `consentTypes` ถ้าผิด: เปลี่ยนชื่อโฟลเดอร์และ endpoint ในไฟล์ใหม่เท่านั้น
- **B6 (Lead ตัดสิน upsert และ batch; inquiry ผมเสนอ; ทั้งหมดรอเจ้าของงานยืนยัน Q1)**
  - **upsert และ upsert batch ของทั้งสามตาราง: `PLATFORM_ADMIN` เท่านั้น** ผู้เรียกที่ไม่ใช่ → 403 `E10009` ใช้สองคำสั่งเดิมของสัญญาข้ามโดเมนโดยไม่เปลี่ยน: "Get the platform administrator role" (`author.m_role` ชื่อ `PLATFORM_ADMIN` สถานะ `ACTIVE`) และ "Check platform administrator" (`author.t_user_role` ของ `userId` จาก token) คัดจาก `sales/05` ให้ตรงตัว ลำดับตรวจ: validate (400) → ไม่พบ (404) → สิทธิ์ (403) → ซ้ำ/ถูกใช้ (409) → เขียน
  - **inquiry: ผู้ถือ access token ที่ถูกต้องทุกคน** (มี `authorization` 401 ได้ ไม่มี 403) เพราะข้อมูลเป็นชื่อและคำอธิบายของประเภท/ยี่ห้อ/ประเภท consent ซึ่งหน้าจอผู้ดูแลร้านต้องอ่านเพื่อสร้างสินค้า (`typeId`, `brandId`) และ consent type แสดงอยู่ในผลของ `consent/01`, `03`, `05` อยู่แล้ว (`consentTypeName`) ไม่มีข้อมูลบุคคลหรือราคา ถ้าผิด (อยากให้ผู้ดูแลเท่านั้นอ่าน): เพิ่ม query สิทธิ์และ 403 ใน inquiry อีก 3 เส้น
  - **ผลที่ตามมา:** role `PLATFORM_ADMIN` ยังไม่มี seed (WP5 จะเสนอ) จนกว่าจะมี ไม่มีผู้ใช้คนใดแก้ type, brand, consent type ได้ ซึ่งตรงกับ spec อื่นที่พึ่งสัญญาเดียวกัน (shop, sales, payment) ถ้าผิด (ไม่ต้องการพึ่ง WP5): ทำตาม category/shop type คือผู้ถือ token ทุกคน
  - **ประเด็นย้อนแก้ (ไม่แก้ใน WP6):** `shop/05`–`07` (shop type), `product/04`–`09` (category, category attribute) ที่ส่งแล้วยังเปิดให้ผู้ถือ token ทุกคนเขียน ซึ่งไม่ตรงกับกติกาใหม่นี้ ลงเป็นงานค้างย้อนแก้
- **B7 (Lead ตัดสิน: Q3 ตามที่ผมเสนอ)** `m_consent_type.is_required` เก็บและรับ/คืนผ่าน API ของ consent type เป็นข้อมูลอ้างอิงเท่านั้น (ไม่บังคับ default FALSE) `consent.t_consent.is_required` ยังเป็นตัวตัดสินว่า consent นั้นต้องยอมรับหรือไม่ ไม่แก้ `consent/02` ถ้าผิด (ต้องการให้ค่าของ type เป็นค่าตั้งต้นของ consent ใหม่ หรือบังคับให้ consent ใต้ type ที่ required ต้อง required): แก้ `consent/02` และ `consent/05` (ซึ่งอยู่ในงานที่ส่งแล้ว) ต้องผ่าน Josh
- **B8 (ตัดสินเอง)** `description`: product type และ brand บังคับ ไม่เกิน 256 ตัวอักษร (ตาม schema) consent type ไม่บังคับ (schema เป็น `TEXT` nullable) จำกัด 1,000 ตัวอักษรที่ชั้น API ซึ่งเป็นค่า config ไม่ฝังใน schema ส่ง `null` หรือไม่ส่งแล้วเก็บ `NULL` ถ้าผิด: เปลี่ยนค่าจำกัด ไม่กระทบ schema
- **B9 (ตัดสินเอง)** Inquiry ตาม shop type `07`: พารามิเตอร์ `id`, `pageIndex`, `pageSize`, `search` (ILIKE ที่ name และ description), `rowStatus` (ACTIVE, INACTIVE, LOCKED, ARCHIVED, ไม่ส่ง = ทุกสถานะยกเว้น DELETED) consent type เพิ่มตัวกรอง `isRequired` เรียง `created_at DESC, id` — shop type `07` เรียง `created_at DESC` อย่างเดียว ซึ่งขัดกับกติกา ORDER BY ลงท้ายคอลัมน์ unique (หัวข้อด้านล่าง) ผมใส่ `id` เพิ่มใน spec ใหม่ ต้องมี `authorization` ถ้าผิด: เปลี่ยนการเรียงใน query
- **B10 (ตัดสินเอง)** ลำดับตรวจ: validate (400 `E10001`) → ไม่พบ (404 `E10004`) → สิทธิ์ (403 `E10009`, B6) → ชื่อซ้ำ (409 `E10003`) → ถูกใช้งาน (409 `E10006` เฉพาะ `rowStatus` เป็น `DELETED` หรือ `ARCHIVED`) → เขียน ไม่มีรหัส error ใหม่ (shop type ไม่มีขั้น 403 ตัวนี้เพิ่มเข้ามา) การตรวจสิทธิ์อยู่หลัง 404 ตามกติกาของโปรเจกต์ แต่ **ก่อนอ่านว่าชื่อซ้ำหรือไม่** เพื่อไม่รั่วข้อมูลให้ผู้ไม่มีสิทธิ์ batch ทำตามกติกา 4.1 (1–100 รายการ, id ซ้ำและชื่อซ้ำในคำขอเป็น 400, สลับชื่อสองแถวในคำขอเดียวเป็น 409 ตามที่ shop type บันทึกไว้)
- **B11 (ตัดสินเอง)** แบบทดสอบ SQL แยกตามไฟล์ migration ที่แก้: `03-product-master.test.sql` (type และ brand: partial unique, ชื่อที่ถูกถือโดยสถานะอื่น, ชื่อที่ลบแล้วใช้ซ้ำ, `confdeltype` ของ FK เป็น `r` และลบจริงถูกขวางเมื่อมีสินค้า) และ `00-consent-type.test.sql` (เช่นเดียวกัน กับ `t_consent`) ตั้งชื่อไฟล์ให้ลำดับรันถูกต้องหลัง migration ที่เกี่ยวข้อง ส่วนที่ตรวจ FK `RESTRICT` เขียนเมื่อ B2 ได้รับอนุมัติ
- **B12 (ตัดสินเองระหว่างรอบ 2)** การแก้ consent type: `name` ต้องส่งทุกคำขอ (รวมลบและ archive) ส่วน `description` และ `isRequired` ไม่บังคับ ถ้าไม่ส่งตอนแก้ ค่าเดิมคงไว้ (ตอนเพิ่ม: `description` เป็น NULL, `isRequired` เป็น FALSE) และส่ง `description: null` เพื่อล้างค่า เหตุผล: ส่งไม่ครบแล้วค่าถูกรีเซ็ตเงียบๆ อันตรายกว่า ถ้าผิด (ต้องการให้แก้แบบแทนที่ทั้งแถว): เปลี่ยนคำอธิบายฟิลด์และ SQL ของ update ใน `consent/06`, `07`
- **B13 (ตัดสินเองระหว่างรอบ 2)** ตัวอย่างคำขอของ inquiry เป็นรายการธรรมดา (`?pageIndex=1&pageSize=10&rowStatus=ACTIVE`) ส่วนตัวอย่าง "By Id" ระบุคำขอของตัวเองในบรรทัด `Request:` ต่างจาก `shop/07` ที่แสดงคำขอที่มี `id` แต่ตอบสองรายการ เหตุผล: ตัวอย่างต้องสอดคล้องกับคำขอ ถ้าผิด: ไม่กระทบอื่น
- **B14 (ตัดสินเองระหว่างรอบ 2)** สร้างไฟล์ spec 9 เส้นจากต้นแบบ `shop/05`–`07` ด้วยสคริปต์ชั่วคราวนอก repo แล้วอ่านและแก้เอง (คัดลอกทั้งโฟลเดอร์ตามกติกา) ตัวอย่างใช้ id ตัวเดียวกับ `typeId`, `brandId` ใน `product/01` และ `consentTypeId` ใน `consent/02` และตัวตรวจเทียบ id นี้ข้ามไฟล์ ถ้าผิด: เปลี่ยนตัวอย่างและเงื่อนไขของตัวตรวจ

## คำถามธุรกิจ (Josh นำไปถามเจ้าของงาน เรียงตามความสำคัญ)

1. **Q4 เปลี่ยน FK ของ `m_product.type_id`, `brand_id` และ `t_consent.consent_type_id` เป็น `RESTRICT` (B2)** — คำแนะนำ: อนุมัติ เพราะลบ type, brand หรือ consent type จริงจะลามไปลบสินค้า รายการสั่งซื้อ และหลักฐานการยอมรับ consent โดยไม่มีใครเห็น และไม่กระทบ spec ที่ส่งแล้วเพราะไม่มี spec ใดลบแถวจริง · ถ้าผิด (ไม่อนุมัติ): กติกาห้ามลบที่ใช้อยู่ (B3) บังคับที่ชั้น API เท่านั้น ลบจริงนอก API ลามต่อได้ · แก้ตามที่อนุมัติทีหลังได้โดยไม่ย้ายข้อมูล
2. **Q1 สิทธิ์ (B6)** — คำแนะนำของ Josh: upsert และ batch ของ 3 ตารางเป็น `PLATFORM_ADMIN` เท่านั้น (403 `E10009`) inquiry เปิดให้ผู้ถือ token ทุกคน · ถ้าผิด: ถ้าต้องการให้ทุก token เขียนได้เหมือน category/shop type ให้ตัด query สิทธิ์และ 403 ออกจาก spec ใหม่ 6 เส้น ถ้าต้องการจำกัด inquiry ด้วยให้เพิ่ม 403 ใน inquiry อีก 3 เส้น · ข้อแนบ: shop type, category, category attribute ที่ส่งแล้วยังเปิดให้ทุก token (ย้อนแก้เป็นงานค้าง) และ role `PLATFORM_ADMIN` ยังไม่มี seed จนกว่า WP5 เสนอ

ตัดสินแล้วโดย Lead (ไม่ต้องถามเจ้าของงานเพิ่ม เว้นแต่ Josh เห็นว่าควร): ชื่อที่ลบแล้วใช้ซ้ำได้ (B1), `is_required` ของ consent type เป็นข้อมูลอ้างอิง (B7)

## สิ่งที่พบนอกขอบเขต (ไม่แก้ รายงานแยก)

- `product.m_product.category_id` เป็น `ON DELETE CASCADE` ขณะที่ spec `product/04` ห้ามลบ category ที่มีสินค้าใช้ (กฎอยู่ที่แอป ฐานข้อมูลไม่บังคับ) ควรเป็น `RESTRICT` เหมือน B2
- `m_product_category.name` และ `m_product_category_attribute.name` เป็น `UNIQUE` ธรรมดา ต่างจาก shop type, type และ brand หลัง WP6 (Lead ตัดสินแล้วว่าชื่อที่ลบใช้ซ้ำได้) ควรทำให้เหมือนกันทุกตารางหลัก ลงเป็นงานค้างย้อนแก้
- `shop/07-inquiry-shop-type` เรียง `ORDER BY st.created_at DESC` อย่างเดียว ไม่ลงท้ายด้วยคอลัมน์ unique จึงอาจซ้ำหรือข้ามแถวระหว่างหน้า
- `shop/05`–`07` (shop type) และ `product/04`–`09` (category, category attribute) เปิดให้ผู้ถือ token ทุกคนเขียน ขัดกับ B6 ลงเป็นงานค้างย้อนแก้ (ส่ง Josh)
- `product/01`, `03` และ `consent/02` ปฏิเสธการแก้เมื่อ type, brand หรือ consent type ไม่ใช่ `ACTIVE` (ดู B4)

## ยังไม่ได้ตรวจ

ยังไม่ได้รัน `check_docs.py`, `audit_all.py`, `run_db_tests.sh` (รอบ 1 ไม่ใช่การลงมือ) และไม่ได้ตรวจว่า branch อื่นของ Tommy (shipping, campaign) แตะ `00-common` หรือ `03-product` หรือไม่ ซึ่งจะชนกับ B1 และ B2 ที่ merge
