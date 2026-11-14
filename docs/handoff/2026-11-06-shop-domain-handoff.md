---
name: "Hand-off: shop domain"
description: "Historical hand-off of 2026-11-06 from Josh to the junior SA for the remaining work of the shop domain; read it only for the history of that assignment."
---

# Hand-off: โดเมน shop (สำหรับ SA jr)

วันที่: 2026-11-06 · ผู้ส่งงาน: Josh (Claude) ร่วมกับเจ้าของงาน · ผู้รับงาน: SA jr

เอกสารนี้ให้ครบพอที่คุณจะทำส่วนที่เหลือของโดเมน shop ได้งานหน้าตาและคุณภาพเดียวกับที่ส่งมอบแล้ว อ่านหัวข้อ 1–4 ก่อนเริ่มลงมือ หัวข้อ 7 คือรายการงานที่ส่งต่อ

## 1. เป้าหมายและนิยามคำว่า "เสร็จ"

งานของเรายังอยู่ในช่วงออกแบบ ผลงานคือเอกสาร SQL และ diagram ไม่ใช่โค้ดแอป และยังไม่ได้รัน migration กับ DB จริง

งานหนึ่งชิ้น (เช่น API หนึ่งชุด) ถือว่าเสร็จเมื่อครบทุกข้อ:

1. มี spec ของทุกเส้นในชุดนั้น ตามรูปแบบหัวข้อ 4 และ SQL ใน spec ใช้คอลัมน์ที่มีจริง
2. ถ้าต้องมีคอลัมน์หรือ constraint เพิ่ม แก้ที่ `CREATE TABLE` ใน migration โดยตรง **ห้ามใช้ `ALTER TABLE`** (ช่วงออกแบบ ยังไม่มี DB จริง) แล้วแก้ให้ตรงกันทั้ง 4 ที่: schema doc, README (จำนวนตาราง/คอลัมน์/FK), ER diagram และ migration ขา down
3. ตัวตรวจทุกชุดผ่าน (หัวข้อ 8) และ `audit_all.py` ได้ 0 ข้อพบ
4. ถ้าแก้ schema ต้องมีแบบทดสอบ SQL (`*.test.sql`) ที่ล้มก่อนแก้และผ่านหลังแก้
5. ถ้าแตะ ER diagram ต้องเรนเดอร์ดูภาพจริงด้วย draw.io (คำสั่งอยู่ในหัวข้อ 8) ไม่ใช่ดูแค่ XML
6. สรุปการตัดสินใจที่คุณเลือกเอง พร้อมผลถ้าผิด (หัวข้อ 10)

## 2. สถานะปัจจุบัน

| ส่วน | สถานะ | ที่อยู่ |
|---|---|---|
| ตาราง `shop.*` (8 ตาราง) | ออกแบบแล้ว | `e-commerce/db/migrations/up/04-shop.schema.up.sql`, `e-commerce/doc/schema/shop/` |
| ราคา ต้นทุน สต็อกแบบ lot | เสร็จ (schema + spec) | `shop.t_shop_product_sku_lot`, `doc/api/shop/01`–`03` |
| หน้าสินค้า (storefront) | เสร็จ | `doc/api/shop/04-inquiry-storefront-product` |
| API ของ shop type, shop, shop image, shop user, review | **ยังไม่มี (งานที่ส่งต่อ)** | หัวข้อ 7 |
| Login/reset-password | ไม่ใช่งานของคุณ | `doc/api/authen-and-author/` |

เอกสารตัดสินใจฉบับเต็ม: `docs/superpowers/specs/2026-11-06-shop-lot-pricing-and-storefront-design.md` และ `2026-11-05-product-sku-multi-level-design.md` อ่านทั้งสองฉบับก่อน เพราะอธิบายว่าทำไมถึงออกแบบแบบนี้

## 3. ข้อมูลตาราง shop (ฉบับย่อ)

ทุกตารางมีคอลัมน์มาตรฐาน `id`, `created_by`, `created_at`, `updated_by`, `updated_at`, `row_status` (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED) ด้านล่างแสดงเฉพาะคอลัมน์ของตัวเอง

| ตาราง | คอลัมน์ | ข้อควรระวัง |
|---|---|---|
| `m_shop_type` | `name` (unique), `description` | ตารางหลักแบบง่ายที่สุด |
| `m_shop` | `type_id` → `m_shop_type`, `name` (unique), `description`, `platform_margin_rate`, `shop_margin_rate` (NUMERIC 8,2, ช่วง 0–100) | อัตรา margin ใช้คำนวณ margin ของ lot |
| `m_shop_image` | `shop_id` → `m_shop`, `type` (LOGO, BANNER, WALLPAPER), `seq`, `image_path` | ไม่มี unique บน `(shop_id, type, seq)` |
| `t_shop_user` | `shop_id`, `user_id` → `authen.m_user`, `role` (ADMIN, STAFF) | unique `(shop_id, user_id)` |
| `t_shop_product` | `shop_id`, `product_id`, `quantity` | unique `(shop_id, product_id)`, สร้างอัตโนมัติจาก upsert shop product SKU, `quantity` ซ้ำกับผลรวมของ lot (ดู R21) |
| `t_shop_product_sku` | `shop_product_id`, `sku_id`, `code`, `name`, `description` | ราคาและสต็อกย้ายไปที่ lot แล้ว |
| `t_shop_product_sku_lot` | `shop_product_sku_id`, `lot_no`, `cost_price`, `selling_price`, margin 3 ตัว, `quantity`, `is_on_sale` | เปิดขายได้ทีละ lot ต่อ SKU (partial unique index) |
| `t_shop_product_review` | `shop_product_id`, `user_id`, `rating` (1–5), `comment` | ยังไม่มี unique ต่อ user ต่อสินค้า |

## 4. ข้อตกลงที่ใช้ทั้งโปรเจกต์ (ต้องทำตามเป๊ะ)

### 4.1 รูปแบบ API

- ทุก API เป็นโฟลเดอร์ `doc/api/<กลุ่ม>/<NN>-<ชื่อ>/` มี `spec.md` และ `sequence.wsd` (ว่างได้) กลุ่ม shop อยู่ที่ `doc/api/shop/` และเลขนำหน้าต่อจากของเดิม
- หนึ่งตารางหลักได้ **3 เส้น**: upsert (เดี่ยว), upsert batch และ inquiry ชื่อ endpoint: `POST v1/<กลุ่ม>/<ชื่อ>/upsert`, `POST v1/<กลุ่ม>/<ชื่อ>/upsert/batch`, `GET v1/<กลุ่ม>/<ชื่อ>`
- **Upsert** เส้นเดียวทำ insert, update, delete, archive: ไม่ส่ง `id` = insert, ส่ง `id` = update, `rowStatus: "DELETED"` = delete (soft), `rowStatus: "ARCHIVED"` = archive ไม่ลบแถวจริงเด็ดขาด
- รหัส HTTP ของ upsert เดี่ยว: Insert **201**, Update **200**, Delete **204 No Content ไม่มี body**, Archive **200** ส่วน **batch ตอบ 200 เสมอ** แม้มีรายการลบ ผลแต่ละรายการอยู่ใน body (`index`, id, `action` = INSERT/UPDATE/DELETE/ARCHIVE) กรณีอื่น (error) ใช้ตัวจัดการ error เดิมตามตารางด้านล่าง
- **Batch**: ใส่ได้ 1–100 รายการ ทำใน transaction เดียว ถ้าตัวใดผิดจะไม่เปลี่ยนอะไรเลย ข้อความ error ใส่ตำแหน่ง เช่น `skus[2]: ...` ตรวจ `id` ซ้ำและค่าที่ต้อง unique ซ้ำในคำขอเดียวกันด้วย
- **Inquiry**: query parameter `id` (ได้ list ที่มี 1 item), `pageIndex` (เริ่ม 1), `pageSize` (default 10, สูงสุด 100), `search` (ILIKE) บวกตัวกรองที่จำเป็น ไม่แสดงแถว `DELETED` response เป็น `data.items[]`, `pageIndex`, `pageSize`, `totalItems`, `totalPages` ไม่พบ = 200 พร้อม `items: []`
- ลูกที่เป็นตารางย่อย (เช่นรูป) ส่งซ้อนมาในคำขอของแม่ได้: ไม่ส่ง id = เพิ่ม, ส่ง id = แก้, `DELETED` = ลบ รายการที่ไม่ได้ส่ง **คงไว้** (ต่างจาก level ของ product ที่ส่ง array มาแล้วถือเป็นชุดสมบูรณ์ อ่านเหตุผลในเอกสารตัดสินใจ)
- ทุกเส้นฝั่งผู้ดูแลมี header `authorization` ส่วนหน้าลูกค้า (storefront) เป็น public ไม่มี

### 4.2 ตารางใน spec

หัวข้อบังคับ (ดูตัวอย่างจริงใน `doc/api/product/04-upsert-product-category/spec.md`): ตารางสรุป (Name, Method, Endpoint, Version, Description) → Domain → Request Parameters (Header, Body/Query, ตารางของ object ลูก, Example Body) → Example Request (HTTP และ cUrl) → Response Parameters (Status Object, Data Object) → Example Response (ทุกกรณีสำเร็จ และทุก error) → Database Relations (ลิงก์ไปไฟล์ schema ของทุกตาราง พร้อม SQL ของแต่ละคำสั่ง)

ข้อกำหนดย่อย:

- ตารางจัดความกว้างคอลัมน์ให้ตรงกันทุกแถว (ตัวตรวจจะล้มถ้าไม่ตรง)
- JSON ทุกบล็อก parse ได้ ชื่อฟิลด์ camelCase ชื่อคอลัมน์ snake_case
- ตัวอย่างต้องสอดคล้องกัน (id เดียวกันใช้ซ้ำใน request และ response ได้ แต่ห้ามเอา id ของสินค้าตัวหนึ่งไปใช้กับอีกตัวในไฟล์เดียวกัน)
- SQL ใช้ placeholder แบบ `'<sequence.ชื่อ>'` และคอมเมนต์ `-- only when xxx is specified` กับเงื่อนไขที่ใส่เฉพาะเมื่อส่งค่ามา เวลาใช้ `NOW()` เขียน `NOW() AT TIME ZONE 'UTC'`
- ห้ามเขียนคำว่า `order` เป็นชื่อ schema (คำสงวนของ PostgreSQL) schema ของออเดอร์คือ `sales`

### 4.3 รหัส error (bizCode)

| HTTP | bizCode | ใช้เมื่อ |
|---|---|---|
| 400 | E10001 | ฟิลด์ขาดหรือผิดรูปแบบ, ค่าซ้ำในคำขอเดียวกัน, จำนวนรายการเกิน |
| 401 | E10002 | access token ไม่ถูกต้องหรือหมดอายุ |
| 409 | E10003 | ชื่อหรือ code ซ้ำกับของเดิม |
| 404 | E10004 | ไม่พบแถวที่ระบุด้วย `id` |
| 404 | E10005 | ไม่พบแถวที่อ้างถึง (FK) |
| 409 | E10006 | ลบหรือแก้ไม่ได้เพราะถูกใช้งานอยู่ |
| 408 | E90001 | timeout |

### 4.4 รูปแบบ SQL และ schema

- ทุกตารางมีคอลัมน์มาตรฐานเหมือนกัน (คัดจากตารางเดิม) และ FK ใช้ `ON DELETE CASCADE` ยกเว้นกรณีที่ต้องปกป้องประวัติ (เช่น `sales.t_order_item.lot_id` ใช้ `RESTRICT`)
- ค่าที่ต้อง unique แต่อนุญาตให้ใช้ชื่อเดิมซ้ำหลังลบแบบ soft ให้ใช้ partial unique index `WHERE row_status <> 'DELETED'` ไม่ใช่ `UNIQUE` ธรรมดา (ตัวอย่าง: `uq_t_shop_product_sku_lot_shop_product_sku_id_lot_no`)
- ห้ามสร้าง FK ที่ชี้หากันเป็นวง (สร้างตารางไม่ได้) ถ้าเจอให้ตัดทิศหนึ่งออก
- ตัวเลข/สถานะที่เป็น config (เช่นเพดานจำนวน level) ไม่ฝังใน schema

## 5. ขั้นตอนทำทีละเส้น

1. อ่านไฟล์ schema ของตารางที่เกี่ยวข้องใน `doc/schema/shop/` และ migration จริง ดู constraint และ default ให้ครบ
2. เลือก spec ต้นแบบจากด้านล่าง แล้ว **คัดลอกทั้งโฟลเดอร์** มาแก้ อย่าเขียนใหม่จากศูนย์

   | งาน | ต้นแบบ |
   |---|---|
   | ตารางหลักแบบง่าย (name, description) | `doc/api/product/04`, `05`, `06` (category) |
   | ตารางที่มี FK ไปแม่ | `doc/api/product/07`, `08`, `09` (category attribute) |
   | ตารางที่มีลูกซ้อน (รูป) | `doc/api/product/01`, `02`, `03` (product) |
   | upsert ที่ซับซ้อนมีตารางลูกและ lot | `doc/api/shop/01`–`03` |
   | หน้าสำหรับลูกค้า (public) | `doc/api/shop/04` |

3. เขียนรายการ "กฎที่ต้องตัดสินใจ" ของงานนั้นก่อน (ตัวอย่างอยู่ในหัวข้อ 7) ถ้าข้อไหนเป็นเรื่องธุรกิจที่ไม่แน่ใจ **ถามเจ้าของงานก่อนเขียน** ถ้าเป็นเรื่องเล็กที่ตัดสินเองได้ ให้เลือกแล้วจดไว้ (หัวข้อ 10)
4. แก้ schema ถ้าจำเป็น (4.4) พร้อมแบบทดสอบ SQL: เขียน test ก่อน รันให้เห็นว่าล้ม แล้วแก้ migration ให้ผ่าน
5. เขียน spec ทั้ง 3 เส้น ตามหัวข้อ 4 SQL ต้องครบทุกตารางที่แตะ รวมการตรวจก่อนเขียน (ตรวจ FK มีอยู่จริง, ตรวจซ้ำ, ตรวจถูกใช้งานก่อนลบ)
6. แก้ schema doc, README, ER diagram ให้ตรงกับ migration (ถ้าแก้ schema)
7. เพิ่มตัวตรวจของชุดใหม่ใน `db/tests/check_docs.py` (ดู `check_shop_spec` เป็นแบบ): ตรวจตารางจัดความกว้าง, JSON, ลิงก์ schema, หัวข้อและข้อความ error ที่ต้องมี และความสอดคล้องของตัวอย่าง
8. รันตัวตรวจทุกชุดและ `audit_all.py` (หัวข้อ 8) จนผ่านหมด
9. **ทดสอบตัวตรวจเอง**: ลองใส่ความผิดพลาดในสำเนา (ลบแถวใน doc, พิมพ์ชื่อคอลัมน์ผิดใน spec) แล้วดูว่าตัวตรวจจับได้ ตัวตรวจที่ไม่เคยล้มเชื่อถือไม่ได้
10. สรุปงานและการตัดสินใจให้เจ้าของงาน (หัวข้อ 10)

## 6. การตัดสินใจที่กระทบ shop (สรุป)

รายละเอียดและเหตุผลอยู่ในเอกสารตัดสินใจสองฉบับในหัวข้อ 2

- ราคา ต้นทุน และจำนวนอยู่ที่ lot ใต้ SKU ร้านเปิดขายทีละ lot เมื่อ lot ที่เปิดอยู่หมด SKU เป็น OUT_OF_STOCK จนกว่าร้านจะเปิด lot ใหม่ (ระบบไม่เปิดให้เอง)
- รายการสั่งซื้อหนึ่งรายการตัดจาก lot เดียว และ `sales.t_order_item.lot_id` อ้าง lot (`RESTRICT`)
- lot ไม่ถูกลบเพราะไม่ได้ส่งมา และลบไม่ได้ถ้ากำลังเปิดขายหรือมีออเดอร์อ้างอยู่ (409)
- ร้านตั้ง SKU กับ lot ด้วยเส้นเดียว และระบบสร้างแถว `t_shop_product` ให้เอง จึงไม่มี API แยกของ shop product
- หน้าสินค้าเป็น public ไม่คืนต้นทุน margin หรือจำนวนของ lot ที่ไม่ได้เปิดขาย
- schema ของออเดอร์ชื่อ `sales` และ `campaign.m_campaign_budget` เป็นฝ่ายอ้าง `m_campaign` (campaign หนึ่งมีได้หลาย budget)

## 7. งานที่ส่งต่อให้คุณ

ทุกงานต้องครบ 3 เส้น (upsert, batch, inquiry) ยกเว้นที่ระบุ ลำดับที่แนะนำ: T1 → T2 → T3 → T4 → T5

### T1 shop type (`m_shop_type`)

- โฟลเดอร์: `doc/api/shop/05-upsert-shop-type`, `06-upsert-shop-type-batch`, `07-inquiry-shop-type`
- ต้นแบบ: `doc/api/product/04`–`06`
- กฎ: `name` unique ทั้งตาราง (409 E10003 เมื่อซ้ำ) ลบ/ archive ไม่ได้ถ้ามีร้านใช้ type นั้นอยู่ (409 E10006)
- เสร็จเมื่อ: ผ่านตามหัวข้อ 1

### T2 shop + รูปของร้าน (`m_shop`, `m_shop_image`)

- โฟลเดอร์: `08`–`10` ต่อจาก T1
- ต้นแบบ: `doc/api/product/01`–`03` (รูปซ้อนในแม่)
- ฟิลด์: `typeId`, `name`, `description`, `platformMarginRate`, `shopMarginRate` และ `images[]` (`type` = LOGO/BANNER/WALLPAPER, `seq`, `imagePath`)
- กฎที่ต้องตัดสินใจ: อัตรา margin อยู่ในช่วง 0–100 และ `platformMarginRate + shopMarginRate` ต้องไม่เกิน 100 หรือไม่ (ถามเจ้าของงาน), `name` ของร้าน unique (409), รูปชนิดเดียวกันมีกี่รูปได้ (โลโก้ควรมี 1 รูป), การเปลี่ยน margin rate กระทบ lot ที่มีอยู่ไหม (แนะนำ: ไม่กระทบย้อนหลัง margin คำนวณตอนบันทึก lot)
- inquiry: ตอบ `typeName` และ `images[]` ติดมา ค้นด้วย `typeId` ได้

### T3 ผู้ใช้ของร้าน (`t_shop_user`)

- โฟลเดอร์: `11`–`13`
- ฟิลด์: `shopId`, `userId`, `role` (ADMIN/STAFF) unique `(shop_id, user_id)`
- กฎที่ต้องตัดสินใจ: ADMIN คนสุดท้ายของร้านลบหรือลดสิทธิ์ไม่ได้ (409 E10006), ใครเพิ่มผู้ใช้ได้ (ADMIN ของร้านนั้นเท่านั้น?), ลบแล้วเพิ่มใหม่ได้ไหม (unique ธรรมดาใน migration ปัจจุบันบล็อก ถ้าให้ได้ เปลี่ยนเป็น partial unique index ใน `CREATE TABLE`)

### T4 รายการสินค้าของร้าน (`t_shop_product`)

- ไม่ต้องมี upsert เพราะระบบสร้างให้จาก shop product SKU
- เขียนเฉพาะ inquiry รายการสินค้าที่ร้านขาย (ชื่อ รูปแรก ช่วงราคา สถานะสต็อก) สำหรับหน้า "สินค้าของร้าน" ใช้ข้อมูลจาก `doc/api/shop/03` และ `04` เป็นฐาน
- ต้องตัดสินใจกับเจ้าของงานก่อน: คอลัมน์ `t_shop_product.quantity` ซ้ำกับผลรวมของ lot ควรลบทิ้งหรือเก็บเป็นค่าที่คำนวณ (เสนอ: ลบ ถ้าลบให้แก้ migration, doc, README, ER diagram และเพิ่มแบบทดสอบ)

### T5 รีวิวสินค้า (`t_shop_product_review`)

- เส้น: ลูกค้าสร้างหรือแก้รีวิวของตัวเอง (upsert เดี่ยว) และ inquiry รีวิวของสินค้า (public) พร้อมคะแนนเฉลี่ย ไม่ต้องมี batch
- กฎที่ต้องตัดสินใจ: หนึ่ง user รีวิวสินค้าหนึ่งตัวได้ครั้งเดียวหรือไม่ (ถ้าครั้งเดียว เพิ่ม partial unique `(shop_product_id, user_id) WHERE row_status <> 'DELETED'` ใน `CREATE TABLE` พร้อมแบบทดสอบ), รีวิวได้เฉพาะคนที่เคยซื้อไหม (ถ้าใช่ ต้องดูตาราง `sales.t_order_item`), ผู้ใช้ลบรีวิวของตัวเองได้ไหม, คะแนนอยู่ในช่วง 1–5 (มี CHECK แล้ว)
- ต้นแบบ: `doc/api/consent/04-submit-consent` (ทำแทน user จาก token) และ `doc/api/shop/04` (public)

## 8. เครื่องมือและคำสั่งตรวจ

รันจากรากของ repo

```bash
for c in schema shop-schema er er-lot spec01 spec02 spec03 shop-spec status-codes; do PYTHONDONTWRITEBYTECODE=1 python3 e-commerce/db/tests/check_docs.py $c; done
```

```bash
PYTHONDONTWRITEBYTECODE=1 python3 e-commerce/db/tests/audit_all.py
```

```bash
bash e-commerce/db/tests/run_db_tests.sh
```

- `check_docs.py` ตรวจเป็นชุด: `schema`/`shop-schema` (doc, README ตรงกับ migration), `er`/`er-lot` (ER diagram), `spec01`–`spec03` (product), `shop-spec` (shop) และ `status-codes` (รหัส HTTP ของทุกเส้น upsert) ชุดตรวจใหม่ให้เพิ่มเป็น subcommand ในไฟล์เดียวกัน ตามรูปแบบ `check_shop_spec`
- `audit_all.py` ตรวจทั้งระบบ: ทุกตารางใน migration ต้องตรงกับ schema doc, README, ER diagram และ SQL ทุกบล็อกใน spec (ตาราง คอลัมน์ alias) ผลต้องเป็น `0 findings`
- `run_db_tests.sh` ต้องมี PostgreSQL ในเครื่อง (`brew install postgresql`) สร้างฐานข้อมูลชั่วคราว รัน migration ทุกไฟล์แบบ up, down, up ซ้ำ และรันทุก `*.test.sql` ลบทิ้งเมื่อจบ ไม่แตะฐานข้อมูลอื่น

ดู ER diagram จริง (ต้องติดตั้ง draw.io Desktop: `brew install --cask drawio`) ตัวเลขหน้าเริ่มที่ 1: 1 Overview, 2 Common·Authen, 3 Author, 4 Product, 5 Shop, 6 Order·Pay·Ship, 7 Campaign, 8 All Tables

```bash
/Applications/draw.io.app/Contents/MacOS/draw.io -x -f png -p 5 -s 1 -o /tmp/er-shop.png e-commerce/db/er-diagram.drawio
```

แล้วเปิดไฟล์ PNG ดู ตรวจว่าตารางไม่ทับกัน เส้น FK ไม่พาดผ่านตาราง และแถวที่เพิ่มมองเห็นครบ

## 9. กับดักที่เจอมาแล้ว

- **คอมมาท้ายตาราง**: `,` ก่อน `);` ใน `CREATE TABLE` ทำให้ migration พัง (เจอมาแล้ว 2 ตาราง ทั้งใน migration และ doc) ให้รัน `run_db_tests.sh` ทุกครั้งที่แก้ SQL
- **`order` เป็นคำสงวน**: ใช้เป็นชื่อ schema ไม่ได้ (เปลี่ยนเป็น `sales` แล้ว)
- **unique ธรรมดาชนกับ soft delete**: ถ้า `UNIQUE (name)` แล้วลบแบบ soft จะสร้างชื่อเดิมใหม่ไม่ได้ ใช้ partial unique index
- **FK วงกลม**: สองตารางที่ชี้หากันและเป็น NOT NULL ใส่ข้อมูลไม่ได้ ตัดทิศหนึ่งออก (ตัวอย่าง `campaign`)
- **README นับผิด**: จำนวนตารางใน README เคยคลาด ตัวตรวจ `audit_all.py` จับได้ อย่าแก้ตัวเลขด้วยมือโดยไม่รันตัวตรวจ
- **ER diagram ที่เลื่อนตาราง**: เมื่อเพิ่มแถวในตาราง ตารางที่อยู่ใต้ต้องเลื่อนลง และเส้น FK ที่มีจุดโค้ง (`mxPoint`) ผูกกับตำแหน่งแถว ต้องเลื่อนค่า y ตาม วิธีที่ง่ายที่สุดคือเพิ่มแถวที่ท้ายตาราง และเพิ่มตารางใหม่ในช่องว่างข้างตารางที่อ้างถึง แล้วเรนเดอร์ดู
- **ตารางใน markdown จัดความกว้างไม่ตรง**: ตัวตรวจจะล้ม ให้ใช้สคริปต์จัดความกว้างแทนการแก้ด้วยมือ
- **ตัวอย่างที่ขัดกับกฎของตัวเอง**: ตัวอย่างต้องทำตามกฎที่เขียนไว้ (เช่นกฎ "ส่งมาเป็นชุดสมบูรณ์" ตัวอย่าง update ต้องมีครบทุกตัว)
- **สมมติฐานเงียบ**: ถ้าต้องเดากฎธุรกิจ ให้จดเป็นการตัดสินใจ (หัวข้อ 10) อย่าปล่อยให้เป็นสิ่งที่ผู้อ่านต้องเดา

## 10. วิธีรายงานงาน

- **ห้าม commit** จนกว่าเจ้าของงานสั่ง (เจ้าของ commit เอง) ใช้ `git status` ดูว่ามีไฟล์อะไรเปลี่ยน
- เมื่อจบแต่ละงาน ส่งสรุป 4 ข้อ: (1) ไฟล์ที่เพิ่ม/แก้ (2) ผลตัวตรวจและแบบทดสอบ (วางผลลัพธ์จริง) (3) **รายการการตัดสินใจที่คุณเลือกเอง** แต่ละข้อมี 3 ส่วน: ตัดสินใจอะไร, เพราะอะไร, ถ้าผิดเสียอะไร (ดูรูปแบบ R14–R26 ใน `2026-11-06-shop-lot-pricing-and-storefront-design.md`) (4) คำถามที่ยังต้องการคำตอบ
- ถ้าเจอปัญหาเดิมในงานของคนอื่น (เช่น migration พัง) ให้แยกรายงานออกจากงานของคุณ ห้ามแก้เงียบ ๆ ถ้าแก้ ให้จดเป็นการตัดสินใจ
- ถ้าต้องแก้สิ่งที่ส่งมอบแล้ว (เช่น เปลี่ยนกฎของ lot) ให้ถามก่อน เพราะกระทบ spec หลายเส้นพร้อมกัน

## 11. ดัชนีไฟล์

| หมวด | ที่อยู่ |
|---|---|
| Migration (up/down) | `e-commerce/db/migrations/` |
| ER diagram | `e-commerce/db/er-diagram.drawio` |
| Schema doc และ README | `e-commerce/doc/schema/` |
| API spec | `e-commerce/doc/api/<กลุ่ม>/<NN>-<ชื่อ>/spec.md` |
| ตัวตรวจ และแบบทดสอบ SQL | `e-commerce/db/tests/` |
| เอกสารตัดสินใจ | `docs/superpowers/specs/` |
| แผนงานที่ทำไปแล้ว | `docs/superpowers/plans/` |
