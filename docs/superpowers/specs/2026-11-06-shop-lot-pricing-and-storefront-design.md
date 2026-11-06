# ราคา ต้นทุน สต็อกแบบ lot ฝั่งร้าน และ API หน้าสินค้า

วันที่: 2026-11-06 · สถานะ: อนุมัติแล้วโดยเจ้าของงาน (2026-11-06) รวมการตัดสินใจระหว่างทาง R14–R24

โปรเจกต์ 2 และ 3 ต่อจาก [product SKU หลาย level](2026-11-05-product-sku-multi-level-design.md)

## ที่มา

แต่ละ lot ของสินค้ามีต้นทุนและราคาขายไม่เท่ากัน ร้านเปิดขายทีละ lot ต่อ SKU และลูกค้าเห็นและซื้อในราคาของ lot ที่เปิดขายอยู่ ตอนนี้ `shop.t_shop_product_sku` เก็บ `cost_price`, `selling_price` และ `quantity` อย่างละค่าเดียวต่อ SKU ซึ่งใช้ไม่ได้กับหลาย lot

## เป้าหมาย

- เก็บราคา ต้นทุน และจำนวนคงเหลือที่ระดับ lot ใต้ shop product SKU
- ร้านเปิดขายทีละ lot ต่อ SKU (บังคับด้วย unique index ในฐานข้อมูล)
- ออเดอร์จำได้ว่ารายการสินค้าขายจาก lot ไหน เพื่อคิดกำไรจากต้นทุนของ lot นั้น
- ร้านตั้ง SKU ของสินค้า และ lot ในคำขอเดียว (upsert, batch และ inquiry ฝั่งร้าน)
- หน้าสินค้าได้ level ค่า รูป ราคาต่อ SKU ช่วงราคา สถานะสต็อก และรู้ว่าค่าไหนหมด ผ่านเส้นสาธารณะเส้นเดียว

## ไม่ใช่เป้าหมาย

- การตัดสต็อกตอนสั่งซื้อและการล็อกแข่งกัน (concurrency) ยังไม่ออกแบบ จะอยู่กับ API ฝั่งออเดอร์
- API ออเดอร์และตะกร้า (มีแต่การเพิ่ม `lot_id` ใน `sales.t_order_item`)
- สูตรคำนวณ margin ละเอียด ระบุแค่ว่าระบบคำนวณจากต้นทุน ราคาขาย และ margin rate ของร้าน
- ไม่ย้ายข้อมูลเก่า (ยังไม่มีข้อมูลจริง และยังไม่ได้รัน migration)

## ผลงาน

- Schema: ตารางใหม่ `shop.t_shop_product_sku_lot`, ลบ 6 คอลัมน์ที่ย้ายออกจาก `shop.t_shop_product_sku`, เพิ่ม `sales.t_order_item.lot_id` (migration `04` และ `06`, schema doc, README, ER diagram, แบบทดสอบ `db/tests/04-shop-lot.test.sql`)
- Spec ใน `e-commerce/doc/api/shop/`: `01-upsert-shop-product-sku`, `02-upsert-shop-product-sku-batch`, `03-inquiry-shop-product-sku`, `04-inquiry-storefront-product`
- ตัวตรวจ `check_docs.py`: `shop-schema`, `er-lot`, `shop-spec`, `status-codes`

## การตัดสินใจระหว่างทาง (เจ้าของงานอนุมัติแล้ว)

คำสั่งของเจ้าของงานตอนทำรอบนี้

- รหัส HTTP ของ upsert: Insert 201, Update 200, Delete 204 No Content (ไม่มี body), Archive 200 ส่วน batch ตอบ 200 เสมอ และกรณีอื่นให้ตาม error handler ที่ใช้อยู่ (ปรับครบทั้ง 9 เส้น upsert ที่มี รวม consent, product, category, attribute และ shop)
- เปลี่ยนชื่อ schema `order` เป็นคำอื่นที่เข้าใจได้ เพราะ `order` เป็นคำสงวนของ PostgreSQL

ที่ผมเลือกเอง

- R14 ชื่อ schema ใหม่คือ `sales` (ทางเลือก: `orders`) เปลี่ยนชื่อไฟล์ migration เป็น `06-sales.schema.*` และโฟลเดอร์ doc เป็น `doc/schema/sales/` ชื่อตาราง `t_order`, `t_order_item` คงเดิม
- R15 lot ที่เปิดขายอยู่หมดสต็อก SKU จะเป็น OUT_OF_STOCK จนกว่าร้านจะเปิด lot ถัดไป ระบบไม่เปิด lot ถัดไปเอง
- R16 การเปิดขาย lot หนึ่งจะปิด lot ที่เปิดอยู่ของ SKU เดียวกันให้ในธุรกรรมเดียว (สลับ lot) และเปิดได้เฉพาะ lot ที่ `ACTIVE` และมีจำนวน > 0
- R17 lot ไม่ถูกลบเพราะไม่ได้ส่งมา (ต่างจาก level ของ product) เพราะ lot คือประวัติต้นทุนของสินค้าที่ขายไปแล้ว ลบ (soft) ไม่ได้ถ้า lot กำลังเปิดขายหรือมีรายการสั่งซื้ออ้างอยู่ (409)
- R18 รายการสั่งซื้อหนึ่งรายการตัดจาก lot เดียว (lot ที่เปิดขาย ณ ตอนสั่ง) และจำนวนต้องไม่เกินจำนวนคงเหลือของ lot นั้น `unique (order_id, product_id, sku_id)` จึงยังใช้ได้
- R19 `sales.t_order_item.lot_id` เป็น FK ที่ต้องมีค่า (NOT NULL ตาม `sku_id` ซึ่งเปลี่ยนเป็น NOT NULL ในรอบ cart) และใช้ `ON DELETE RESTRICT` ต่างจากตารางอื่นที่ใช้ `CASCADE` เพื่อไม่ให้ประวัติการขายหายตามการลบ lot
- R20 `gross_margin`, `share_margin`, `platform_margin` ย้ายไปอยู่ที่ lot และระบบคำนวณ ไม่อยู่ในคำขอ
- R21 `shop.t_shop_product.quantity` ยังคงอยู่โดยไม่แตะ แต่ซ้ำซ้อนกับผลรวมของ lot จึงควรพิจารณาลบหรือให้เป็นค่าที่คำนวณ
- R22 ร้านตั้ง SKU กับ lot ด้วยเส้นเดียว (upsert shop product SKU ที่มี `lots[]`) และระบบสร้างแถว `t_shop_product` ให้เมื่อสินค้ายังไม่ถูกเปิดขายในร้านนั้น จึงไม่มีเส้นแยกสำหรับ shop product
- R23 หน้าสินค้าเป็นเส้นสาธารณะ ไม่ต้องมี access token ไม่คืนต้นทุน margin หรือจำนวนของ lot ที่ไม่ได้เปิดขาย และคืน `maxOrderQuantity` (จำนวนคงเหลือของ lot ที่เปิดขาย) แทนจำนวนทั้งหมด
- R24 migration เดิมมี bug ที่ผมแก้เพราะเป็นข้อผิดไวยากรณ์ชัดเจน: คอมมาเกินท้ายตารางใน `00-common` (`m_consent_type`) และ `04-shop` (`m_shop`) ทั้งใน migration และใน doc ของสองตารางนั้น

## ปัญหาเดิมใน migration ที่แก้แล้ว (ตามคำสั่ง "จัดการเลย")

- R25 `sales.t_order` มี `UNIQUE (user_id, shop_id, product_id, sku_id)` ที่อ้างคอลัมน์ซึ่งไม่มีในตาราง จึงตัด constraint นี้ออก (migration, doc ของตาราง และแถว UNIQUE ใน ER diagram ทั้ง 2 หน้า) เพราะ `code` ของ `t_order` เป็น unique อยู่แล้ว
- R26 `campaign.m_campaign` และ `campaign.m_campaign_budget` อ้างถึงกันและกัน (`budget_id` และ `campaign_id` เป็น NOT NULL ทั้งคู่) ซึ่งสร้างตารางตามลำดับก็ไม่ได้และใส่ข้อมูลไม่ได้ เปลี่ยนจาก `ALTER TABLE` (ที่ใช้ชั่วคราวและเจ้าของงานไม่ต้องการ) เป็นการตัดวง: ลบคอลัมน์ `budget_id` ออกจาก `m_campaign` ให้ budget เป็นฝ่ายอ้าง campaign (`m_campaign_budget.campaign_id` เป็น FK ธรรมดา) สร้าง `m_campaign` ก่อน แล้ว `m_campaign_budget` และ `m_campaign_budget_ledger` ตามลำดับ ผลคือ campaign หนึ่งมีได้หลาย budget (เช่นเติมงบ) และ ledger อ้าง budget ของแต่ละรอบ (ทางเลือกคือเก็บ `budget_id` ที่ campaign และลบ `campaign_id` ออกจาก budget ซึ่งทำให้ campaign มี budget เดียว) ถ้าต้องการ budget เดียวต่อ campaign ให้เพิ่ม unique บน `campaign_id`
- ผล: ไม่มี `ALTER TABLE` ใน migration และ doc อีกแล้ว migration ทั้ง 10 ไฟล์รันผ่านใน PostgreSQL ชั่วคราวแบบ up, down ย้อนลำดับ แล้ว up ซ้ำ โดยไม่ต้องแก้ในสำเนา และแบบทดสอบ SQL 3 ไฟล์ผ่าน (`03-product-sku-levels`, `04-shop-lot`, `09-campaign`)
