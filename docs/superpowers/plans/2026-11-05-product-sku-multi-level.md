---
name: "Plan: multi-level product SKU"
description: "Implementation plan of 2026-11-05 that lets one product define up to three option levels (a configurable limit) for its SKUs; read it for the steps and the reasons of that change."
---

# Product SKU หลาย level — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ให้สินค้าหนึ่งตัวนิยาม level ของตัวเลือก (ไม่เกิน 3, ปรับได้ด้วย config) พร้อมค่าและรูปของค่า และสร้าง SKU ครบทุกคู่ ผ่าน product upsert/batch/inquiry

**Architecture:** เพิ่มตาราง `m_product_option` (level), `m_product_option_value` (ค่า), `m_product_sku_option_value` (SKU ประกอบด้วยค่าอะไร) แก้ `m_product_sku` (เพิ่ม `combination_key`) และ `m_product_image` (เพิ่ม `option_value_id`) แล้วแก้ spec ของ product 3 เส้นให้รับและคืน `options[]` ฝั่ง lot/ราคา/หน้าสินค้าอยู่นอกแผนนี้

**Tech Stack:** PostgreSQL (migration SQL), Markdown (schema doc และ API spec), draw.io XML (ER diagram), Python 3 (สคริปต์ตรวจ)

**Spec:** `docs/superpowers/specs/2026-11-05-product-sku-multi-level-design.md`

## Global Constraints

- ตารางใหม่ทุกตัวมีคอลัมน์มาตรฐาน `id UUID PK DEFAULT GEN_RANDOM_UUID()`, `created_by VARCHAR(64) NOT NULL`, `created_at`, `updated_by`, `updated_at`, `row_status` (CHECK ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED) เหมือนตารางเดิมใน `03-product.schema.up.sql`
- ใช้ soft delete ผ่าน `row_status` ไม่ลบแถวจริง
- เลข 3 level ห้ามฝังใน schema (อยู่ใน config ของแอป ค่าเริ่มต้น 3) เพดาน SKU ต่อสินค้าอยู่ใน config ค่าเริ่มต้น 500
- สินค้าที่ไม่มี level มี SKU เริ่มต้น 1 ตัว (`combination_key` เป็นค่าว่าง) ราคา/สต็อก/lot ไม่เพิ่มที่ฝั่ง product
- ห้าม commit หรือ push เว้นแต่เจ้าของงานสั่ง (repo นี้เจ้าของ commit เอง) ทุก task จบที่ checkpoint ที่รันตัวตรวจผ่าน
- Spec ทุกไฟล์ใช้รูปแบบเดิมของ `e-commerce/doc/api/product/*/spec.md` (ตารางจัดความกว้างให้ตรงกัน, JSON ทุกบล็อก parse ได้, bizCode ต่อจากชุดเดิม: E10001 ฟิลด์ผิด, E10002 unauthorized, E10003 conflict, E10004 ไม่พบ, E10005 ไม่พบ reference, E10006 ถูกใช้งานอยู่, E90001 timeout)
- ชื่อฟิลด์ API เป็น camelCase ชื่อคอลัมน์เป็น snake_case ลิงก์ schema ในคำสั่ง spec เป็น `../../../schema/product/<table>.md`

## Review Focus

1. ค่า/level/SKU ที่ถูกลบแบบ soft แล้วเพิ่มใหม่ชื่อหรือ combination เดิม ต้องไม่ชน unique (ใช้ partial unique index `WHERE row_status <> 'DELETED'`) — Task 1 มีแบบทดสอบ
2. สินค้า 0 level ต้องมี SKU เริ่มต้น 1 ตัว (`combination_key = ''`) และไม่ซ้ำ — Task 1 แบบทดสอบ, Task 4 กฎใน spec
3. จำนวน SKU เกินเพดาน ต้องตอบ 400 ไม่สร้างบางส่วน — Task 4 และ Task 6 ตรวจว่ามี error example
4. แก้จำนวน level ตอนที่ SKU ถูกร้าน ตะกร้า หรือออเดอร์ใช้อยู่ ต้องตอบ 409 — Task 4 และ Task 6
5. รูปของค่า (`option_value_id` ไม่ว่าง) ต้องไม่ปนใน `images[]` ระดับสินค้าของ inquiry — Task 5 ตรวจ SQL

---

## ตัวตรวจร่วม (สร้างใน Task 1 ใช้ใน Task 2-6)

ไฟล์ `e-commerce/db/tests/check_docs.py` รับ subcommand `schema`, `er`, `spec01`, `spec02`, `spec03` แต่ละ subcommand คืน exit code 0 เมื่อผ่าน และพิมพ์ข้อความ `FAIL: <เหตุผล>` เมื่อไม่ผ่าน ฟังก์ชันร่วมที่ต้องมี:

- `table_lines_aligned(md: str) -> list[str]` คืนรายการตารางที่บรรทัดยาวไม่เท่ากัน
- `json_blocks_parse(md: str) -> list[str]` คืนรายการบล็อก ```` ```JSON ```` ที่ parse ไม่ได้
- `require(md: str, needles: list[str]) -> list[str]` คืน needle ที่ไม่พบ

---

### Task 1: Migration ใหม่ + แบบทดสอบ SQL + ตัวตรวจ

**Files:**
- Create: `e-commerce/db/tests/03-product-sku-levels.test.sql`
- Create: `e-commerce/db/tests/check_docs.py` (โครงตัวตรวจร่วมด้านบน ยังไม่มี subcommand)
- Modify: `e-commerce/db/migrations/up/03-product.schema.up.sql`
- Modify: `e-commerce/db/migrations/down/03-product.schema.down.sql`

**Interfaces:**
- Produces: ตาราง `product.m_product_option(product_id, name, level_no)`, `product.m_product_option_value(option_id, value, sort_order)`, `product.m_product_sku_option_value(sku_id, option_value_id)`, คอลัมน์ `product.m_product_sku.combination_key TEXT NOT NULL DEFAULT ''`, คอลัมน์ `product.m_product_image.option_value_id UUID NULL` ชื่อ index: `uq_m_product_option_product_id_level_no`, `uq_m_product_option_product_id_name`, `uq_m_product_option_value_option_id_value`, `uq_m_product_sku_product_id_combination_key` (ทั้งหมด partial unique `WHERE row_status <> 'DELETED'`) และ `UNIQUE (sku_id, option_value_id)` ใน junction

- [ ] **Step 1: เขียนแบบทดสอบ `03-product-sku-levels.test.sql`** — ทำใน transaction แล้ว `ROLLBACK` ใช้ `DO` block + `RAISE EXCEPTION` เมื่อ assertion ไม่ผ่าน สร้าง fixture: 1 แถวใน `m_product_type`, `m_product_category` (ใส่ `slug`), `m_product_brand`, `m_product` (ใส่ `slug`) แล้วทดสอบ (แต่ละข้อเป็น `DO` block แยก ใช้ `BEGIN ... EXCEPTION WHEN unique_violation THEN ... END` เพื่อยืนยันว่าชนจริง):
  - `m_product_option` ซ้ำ `(product_id, level_no)` ที่ `ACTIVE` → `unique_violation`; แต่ถ้าแถวเดิมเป็น `DELETED` เพิ่มซ้ำได้
  - `m_product_option` ซ้ำ `(product_id, name)` ที่ `ACTIVE` → `unique_violation`; ถ้าแถวเดิม `DELETED` เพิ่มซ้ำได้
  - `m_product_option_value` ซ้ำ `(option_id, value)` → `unique_violation`; ถ้าแถวเดิม `DELETED` เพิ่มซ้ำได้
  - `m_product_sku` 2 แถว `combination_key = ''` ของสินค้าเดียวกันที่ไม่ `DELETED` → `unique_violation`; ถ้าแถวแรก `DELETED` ได้ (SKU เริ่มต้น)
  - `m_product_sku_option_value` ซ้ำ `(sku_id, option_value_id)` → `unique_violation`
  - `m_product_image.option_value_id` ใส่ `NULL` ได้ ใส่ id ที่มีอยู่ได้ ใส่ `GEN_RANDOM_UUID()` ที่ไม่มีอยู่ → `foreign_key_violation`
  - ลบแถว `m_product_option_value` จริง แล้ว `m_product_sku_option_value` และรูปที่ผูกกับค่านั้นหายตาม (`ON DELETE CASCADE`)

- [ ] **Step 2: รัน migration เดิมใน cluster ชั่วคราวแล้วรันแบบทดสอบให้เห็นว่า FAIL**

  ```bash
  export PGTMP="$(mktemp -d)" && initdb -D "$PGTMP" -A trust >/dev/null && pg_ctl -D "$PGTMP" -o "-p 54329 -k $PGTMP" -l "$PGTMP/log" -w start
  psql -h "$PGTMP" -p 54329 -d postgres -v ON_ERROR_STOP=1 -f e-commerce/db/migrations/up/03-product.schema.up.sql
  psql -h "$PGTMP" -p 54329 -d postgres -v ON_ERROR_STOP=1 -f e-commerce/db/tests/03-product-sku-levels.test.sql
  ```
  Expected: บรรทัดสุดท้ายล้มด้วย `relation "product.m_product_option" does not exist`

- [ ] **Step 3: แก้ `03-product.schema.up.sql`** ตามลำดับนี้ (ลำดับสำคัญเพราะ FK): (a) วาง `m_product_option` และ `m_product_option_value` ต่อจาก `m_product_attribute` ก่อน `m_product_image`; (b) `m_product_image` เพิ่ม `option_value_id UUID REFERENCES product.m_product_option_value (id) ON DELETE CASCADE` ต่อท้าย `image_path`; (c) `m_product_sku` เพิ่ม `combination_key TEXT NOT NULL DEFAULT ''` ต่อท้าย `description`; (d) วาง `m_product_sku_option_value` ต่อจาก `m_product_sku` (`sku_id` และ `option_value_id` เป็น `NOT NULL REFERENCES ... ON DELETE CASCADE`, `UNIQUE (sku_id, option_value_id)`) ชนิดคอลัมน์: `level_no SMALLINT NOT NULL CHECK (level_no >= 1)`, `name VARCHAR(128) NOT NULL`, `value VARCHAR(128) NOT NULL`, `sort_order INT NOT NULL DEFAULT 0` แต่ละ partial unique index เป็นคำสั่ง `CREATE UNIQUE INDEX IF NOT EXISTS <ชื่อใน Interfaces> ON ... WHERE row_status <> 'DELETED'` ต่อท้ายตารางของมัน

- [ ] **Step 4: แก้ `03-product.schema.down.sql`** ให้ drop ตามลำดับ: `m_product_sku_option_value`, `m_product_sku`, `m_product_image`, `m_product_option_value`, `m_product_option`, แล้วที่เหลือตามเดิม (ลบ `DROP TABLE` ของ sku/image ที่ซ้ำตำแหน่งเดิมออก)

- [ ] **Step 5: รัน migration ใหม่ + แบบทดสอบ ให้ PASS แล้วทดสอบ down/up ซ้ำ**

  ```bash
  psql -h "$PGTMP" -p 54329 -d postgres -v ON_ERROR_STOP=1 -c "DROP SCHEMA product CASCADE"
  psql -h "$PGTMP" -p 54329 -d postgres -v ON_ERROR_STOP=1 -f e-commerce/db/migrations/up/03-product.schema.up.sql
  psql -h "$PGTMP" -p 54329 -d postgres -v ON_ERROR_STOP=1 -f e-commerce/db/tests/03-product-sku-levels.test.sql
  psql -h "$PGTMP" -p 54329 -d postgres -v ON_ERROR_STOP=1 -f e-commerce/db/migrations/down/03-product.schema.down.sql
  psql -h "$PGTMP" -p 54329 -d postgres -v ON_ERROR_STOP=1 -f e-commerce/db/migrations/up/03-product.schema.up.sql
  ```
  Expected: ทุกคำสั่งจบโดยไม่มี `ERROR` แล้วหยุด cluster: `pg_ctl -D "$PGTMP" stop && rm -rf "$PGTMP"`

- [ ] **Step 6: Checkpoint** — ตัวตรวจร่วมสร้างแล้วและ import ได้ (`python3 e-commerce/db/tests/check_docs.py` ไม่ error) ไม่ commit

---

### Task 2: เอกสาร schema และ README

**Files:**
- Create: `e-commerce/doc/schema/product/m_product_option.md`, `m_product_option_value.md`, `m_product_sku_option_value.md`
- Modify: `e-commerce/doc/schema/product/m_product_sku.md`, `m_product_image.md`, `e-commerce/doc/schema/README.md`
- Modify (test): `e-commerce/db/tests/check_docs.py` (subcommand `schema`)

**Interfaces:**
- Consumes: ชื่อตาราง/คอลัมน์/index จาก Task 1
- Produces: ไฟล์ doc ที่ README และ spec ลิงก์ถึง

- [ ] **Step 1: เพิ่ม subcommand `schema` ที่ตรวจ:** (a) ทั้ง 3 ไฟล์ใหม่มีหัว `# Table: product.<ชื่อ>`; (b) `m_product_sku.md` มี `combination_key` ทั้งในตาราง Columns และบล็อก SQL; `m_product_image.md` มี `option_value_id` ทั้งสองที่; (c) บล็อก SQL ของแต่ละไฟล์ (CREATE TABLE และ CREATE UNIQUE INDEX ของตารางนั้น) เมื่อ normalize ช่องว่างแล้วเท่ากับข้อความของตารางเดียวกันใน `03-product.schema.up.sql`; (d) `README.md` มี `50 tables in 11 schemas` และแถว `| [m_product_option](product/m_product_option.md) | Master | 9 | 1 |`, `| [m_product_option_value](product/m_product_option_value.md) | Master | 9 | 1 |`, `| [m_product_sku_option_value](product/m_product_sku_option_value.md) | Master | 8 | 2 |`, `m_product_sku` เป็น `| 10 | 1 |`, `m_product_image` เป็น `| 9 | 2 |`

- [ ] **Step 2: รัน `python3 e-commerce/db/tests/check_docs.py schema`** Expected: FAIL (ไฟล์ยังไม่มี)

- [ ] **Step 3: เขียน 3 ไฟล์ใหม่ตาม `doc/schema/template.md`** (ตาราง Columns, ตาราง Constain, บล็อก SQL ตรงกับ migration) Description ของคอลัมน์ที่ต้องมี: `level_no` = "Level of the option starting from 1, Order in the product options", `combination_key` = "Value ids of the SKU joined in level order, Empty for the default SKU", `option_value_id` = "Reference to `product.m_product_option_value.id`, Null for product level image" ชื่อ constraint ใช้รูปแบบ `pk_`, `fk_`, `uq_` ตามไฟล์เดิม และระบุในคอลัมน์ Description ของ `uq_` ที่เป็น partial ว่า "Unique among rows where row_status <> 'DELETED'"

- [ ] **Step 4: แก้ `m_product_sku.md`, `m_product_image.md`** (เพิ่มแถวคอลัมน์ และ constraint ที่เพิ่ม และบล็อก SQL) **และ README** (เพิ่ม 3 แถวใน section product ต่อจาก `m_product_sku`, แก้จำนวนคอลัมน์/FK ของ sku และ image, แก้ 47 → 50)

- [ ] **Step 5: รัน `python3 e-commerce/db/tests/check_docs.py schema`** Expected: exit 0

---

### Task 3: ER diagram

**Files:**
- Modify: `e-commerce/db/er-diagram.drawio` (หน้า "3 Product" และ "7 All Tables" ในกรอบ `product`)
- Modify (test): `e-commerce/db/tests/check_docs.py` (subcommand `er`)

**Interfaces:**
- Consumes: ชื่อตารางและคอลัมน์จาก Task 1

- [ ] **Step 1: เพิ่ม subcommand `er`** ที่ parse XML แล้วตรวจต่อหน้า "3 Product" และ "7 All Tables": (a) XML well-formed และ `id` ของ mxCell ไม่ซ้ำ; (b) มีตารางชื่อ `product.m_product_option`, `product.m_product_option_value`, `product.m_product_sku_option_value` และมีแถว `option_value_id : uuid` ใต้ `product.m_product_image` กับ `combination_key : text` ใต้ `product.m_product_sku`; (c) ตารางระดับบนสุดของแต่ละหน้า/กรอบ (กลุ่มที่ parent เดียวกัน) กรอบสี่เหลี่ยมไม่ทับกัน (ตรวจ x,y,width,height); (d) ทุก edge ที่มี `source`/`target` ชี้ไปยัง id ที่มีอยู่; (e) มี edge จาก FK ของตารางใหม่ไปตารางแม่ครบ: option→m_product, option_value→option, sku_option_value→m_product_sku และ →option_value, image→option_value

- [ ] **Step 2: รัน `python3 e-commerce/db/tests/check_docs.py er`** Expected: FAIL (b)

- [ ] **Step 3: แก้ diagram** ตามแบบที่ใช้อยู่: ตารางเป็น mxCell หัวกล่อง (ความสูง 28 + 22 ต่อแถว) แถวใช้ข้อความ `PK    id : uuid`, `FK    <col> : uuid`, `UK    ...`, `      <col> : <type>` (nullable ต่อท้าย ` ?`) เพิ่มแถวใหม่ท้ายตาราง `m_product_sku` และ `m_product_image` แล้วขยายความสูงตารางและเลื่อนตารางที่อยู่ใต้ลงเท่าความสูงที่เพิ่ม (หน้า 7 ขยายกรอบ `product` ด้วย) เส้น FK ใช้ edge แบบ `edgeStyle` ธรรมดาที่ไม่มี waypoint ยกเว้นต้องเลี่ยงตารางอื่น ให้วางตารางใหม่ในพื้นที่ว่างข้างตารางที่อ้างถึง ถ้าตารางที่เลื่อนมี edge ที่มี waypoint ให้เลื่อนค่า y ของ waypoint ตามเท่ากัน

- [ ] **Step 4: รัน `python3 e-commerce/db/tests/check_docs.py er`** Expected: exit 0 แล้วเปิดไฟล์ใน draw.io ดูภาพว่าเส้นไม่พาดข้ามตารางผิดปกติ

---

### Task 4: Spec product upsert (`01-upsert-product`)

**Files:**
- Modify: `e-commerce/doc/api/product/01-upsert-product/spec.md`
- Modify (test): `e-commerce/db/tests/check_docs.py` (subcommand `spec01`)

**Interfaces:**
- Consumes: ตาราง/คอลัมน์จาก Task 1, ลิงก์ doc จาก Task 2
- Produces: ชื่อ object และฟิลด์ที่ Task 5/6 ใช้ซ้ำ — `options[]` (Option Object) → `values[]` (Value Object) → `images[]` (Value Image Object); กฎ error E10001/E10004/E10006

- [ ] **Step 1: เพิ่ม subcommand `spec01`** ตรวจ `table_lines_aligned`, `json_blocks_parse` และ `require` ต่อไปนี้: หัวข้อ `#### Option Object`, `#### Value Object`, `#### Value Image Object`; ฟิลด์ `sortOrder` ต้องไม่มีในตาราง Body Parameters (ลำดับของ level และของค่ามาจากตำแหน่งใน array และเก็บเป็น `level_no` และ `sort_order` ฝั่ง DB); ข้อความ error `Options must not contain more than 3 levels.`, `SKU count exceeds the maximum of 500.`, `Product options cannot be changed because SKUs are used.`, `Product option not found.`, `Product option value not found.`; หัวข้อ SQL `#### INSERT - Create product option`, `#### INSERT - Create product SKU`, `#### INSERT - Create product SKU option value`, `#### UPDATE - Close product SKUs of closed option values`; ตัวอย่าง JSON Insert มี `options` 3 level (ลาย, ไซส์, สี)

- [ ] **Step 2: รัน `python3 e-commerce/db/tests/check_docs.py spec01`** Expected: FAIL

- [ ] **Step 3: แก้ spec ส่วน Body Parameters:** เพิ่มฟิลด์ `options` (Array of Option, OPTIONAL) คำอธิบาย: "Product options (levels), Specified: replace by id rules, Not specified: keep the current options, Maximum 3 levels (configurable), Level number is the position in the array ignoring DELETED options, Empty array removes all levels and keeps one default SKU" ตาราง Option Object: `id` (O, UUID), `name` (M, max 128, ไม่ซ้ำในสินค้า), `rowStatus` (O, default ACTIVE, DELETED = ลบ), `values` (M, Array of Value, อย่างน้อย 1 ค่าที่ไม่ DELETED) ตาราง Value Object: `id` (O), `value` (M, max 128, ไม่ซ้ำใน level), `rowStatus` (O), `images` (O, Array of Value Image) ตาราง Value Image Object: `id` (O), `imagePath` (M), `rowStatus` (O) ใส่ตัวอย่าง Insert/Update/Delete ใน `##### Example Body Parameters` (Insert: 3 level ลาย [A,B] ไซส์ [S,M,L] สี [แดง,ดำ] โดยค่าสีมีรูป; Update: เพิ่มค่าสี "ขาว" และตั้ง `rowStatus: "DELETED"` ให้ไซส์ L; Delete: ไม่มี `options`) และแก้คำอธิบายของ `images` ระดับสินค้าว่า "Product level images, Images of option values are in options[].values[].images"

- [ ] **Step 4: เพิ่มกฎและ error examples ท้าย `#### Fail - ...`:** 400 `Fail - Bad Request Option` ("options[0]: Name is required and Values must contain at least 1 value."), 400 `Fail - Bad Request Option Duplicate` ("options[1]: Name is duplicated with options[0]."), 400 `Fail - Bad Request Level` ("Options must not contain more than 3 levels."), 400 `Fail - Bad Request SKU Limit` ("SKU count exceeds the maximum of 500."), 404 `Fail - Not Found Option` ("Product option not found.") และ `Fail - Not Found Option Value` ("Product option value not found.") ทั้งคู่ E10004, 409 `Fail - Conflict SKU In Use` E10006 ("Product options cannot be changed because SKUs are used.") ซึ่งใช้เมื่อเพิ่มหรือลด level ขณะที่ SKU ถูกใช้ใน `shop.t_shop_product_sku`, `cart.t_cart` หรือ `order.t_order_item` (การเพิ่มค่าใน level เดิมไม่ติด 409)

- [ ] **Step 5: เพิ่ม SQL ใน Database Relations** (ตามตารางด้วยหัวข้อ `### Table: [...]` และลิงก์ doc): `m_product_option` — QUERY existing options of product, INSERT, UPDATE (name, level_no, row_status; รวมการเรียง level_no ใหม่เฉพาะแถวที่ไม่ DELETED); `m_product_option_value` — QUERY existing values, INSERT, UPDATE (value, sort_order, row_status); `m_product_image` — แก้ INSERT/UPDATE ให้มี `option_value_id` และ query รูปเดิมของค่า; `m_product_sku` — QUERY SKU in use (นับจาก 3 ตารางอ้างอิง), INSERT generated SKUs (`name` = ชื่อค่าคั่น ` / `, `combination_key` = id ค่าตามลำดับ level คั่น `-`), `UPDATE - Close product SKUs of closed option values` (ตั้ง `row_status` ตามค่าที่ปิด และเปิดกลับเมื่อค่ากลับเป็น ACTIVE); `m_product_sku_option_value` — INSERT ผูก SKU กับค่า

- [ ] **Step 6: รัน `python3 e-commerce/db/tests/check_docs.py spec01`** Expected: exit 0

---

### Task 5: Spec product inquiry (`02-inquiry-product`)

**Files:**
- Modify: `e-commerce/doc/api/product/02-inquiry-product/spec.md`
- Modify (test): `e-commerce/db/tests/check_docs.py` (subcommand `spec02`)

**Interfaces:**
- Consumes: ชื่อ Option/Value object จาก Task 4

- [ ] **Step 1: เพิ่ม subcommand `spec02`** ตรวจ alignment, JSON parse และ `require`: `#### Option Object`, `#### Option Value Object`, `#### SKU Object`, ฟิลด์ `levelNo`, `optionValueIds`, `combinationKey`; ต้องไม่มี `price`, `quantity`, `sellingPrice`; SQL ของรูประดับสินค้าต้องมี `pi.option_value_id IS NULL` และ SQL รูปของค่าต้องมี `pi.option_value_id IN`

- [ ] **Step 2: รัน `spec02`** Expected: FAIL

- [ ] **Step 3: แก้ Product Object:** เพิ่ม `options` (Array of Option, M, ว่างเมื่อสินค้าไม่มี level) และ `skus` (Array of SKU, M) ตาราง Option Object: `optionId`, `name`, `levelNo`, `values`; Option Value Object: `valueId`, `value`, `sortOrder`, `images` (`imageId`, `imagePath`); SKU Object: `skuId`, `name`, `combinationKey`, `optionValueIds` (Array of UUID เรียงตาม level), `rowStatus` ใส่ใน Example Response (Success และ By Id) ให้ครบ 2 ตัวอย่างสินค้า: ตัวที่มี 3 level และตัวที่ไม่มี level (`options: []`, `skus` มี SKU เริ่มต้น 1 ตัว `combinationKey: ""`, `optionValueIds: []`) และแก้คำอธิบาย `images` ว่าคืนเฉพาะรูประดับสินค้า พร้อมเพิ่มประโยคใน Description ของเส้นนี้ว่า "Image shown for a selection is the image of the lowest level selected value that has an image, otherwise the product level images" (กติกาให้ฝั่งแสดงผลนำไปใช้ API ไม่ได้คำนวณให้)

- [ ] **Step 4: เพิ่ม SQL:** QUERY options (`WHERE po.product_id IN (...) AND po.row_status = 'ACTIVE' ORDER BY po.level_no`), QUERY option values (`ORDER BY pov.sort_order`), QUERY option value images (`pi.option_value_id IN (...) AND pi.row_status = 'ACTIVE'`), QUERY SKUs (ไม่ DELETED) พร้อม QUERY SKU option values (`m_product_sku_option_value` join `m_product_option` เรียง `level_no`); แก้ QUERY รูประดับสินค้าให้เติม `AND pi.option_value_id IS NULL`

- [ ] **Step 5: รัน `spec02`** Expected: exit 0

---

### Task 6: Spec product upsert batch (`03-upsert-product-batch`)

**Files:**
- Modify: `e-commerce/doc/api/product/03-upsert-product-batch/spec.md`
- Modify (test): `e-commerce/db/tests/check_docs.py` (subcommand `spec03`)

**Interfaces:**
- Consumes: Option/Value/Value Image object จาก Task 4 (ฟิลด์และกฎเดียวกัน)

- [ ] **Step 1: เพิ่ม subcommand `spec03`** ตรวจ alignment, JSON parse และ `require`: `#### Option Object`, `#### Value Object`, `#### Value Image Object`, `products[0].options[0]` ในข้อความ error, `SKU count exceeds the maximum of 500.`, `Product options cannot be changed because SKUs are used.`, placeholder `sequence.products.options`

- [ ] **Step 2: รัน `spec03`** Expected: FAIL

- [ ] **Step 3: แก้ spec:** เพิ่ม `options` ใน Product Object (คำอธิบาย ฟิลด์ และตาราง 3 object เหมือน Task 4) ใส่ options ในตัวอย่างสินค้า INSERT (3 level) และ UPDATE (เพิ่มค่าสี) ข้อความ error เติม prefix ตำแหน่ง เช่น `products[0].options[1]: Name is duplicated with products[0].options[0].`; เพดาน 500 SKU และการแก้ level ที่ SKU ถูกใช้ ตรวจต่อสินค้าแต่ละตัว ตอบ error ของสินค้าตัวแรกที่ผิดและไม่เปลี่ยนอะไรเลย (all-or-nothing เดิม) ส่วน SQL ใช้ชุดเดียวกับ Task 4 แต่ placeholder เป็น `sequence.products.options...`

- [ ] **Step 4: รัน `spec03`** Expected: exit 0

- [ ] **Step 5: ตรวจรวม** — `for c in schema er spec01 spec02 spec03; do python3 e-commerce/db/tests/check_docs.py $c || exit 1; done` Expected: ทุกคำสั่ง exit 0 และ `git status` เห็นเฉพาะไฟล์ในแผนนี้ ไม่ commit
