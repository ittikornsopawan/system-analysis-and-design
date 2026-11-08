---
name: Cart, orders, money & fulfilment concepts — explanation and SQL traceability
description: อธิบาย domain diagram domain-commerce-model พร้อมเหตุผล ตารางต้นทาง ความสัมพันธ์และcardinalityจากSQL ใช้ก่อนreviewหรือแก้ภาพนี้
status: in-review
approved_by: null
approved_at: null
---

# Cart, orders, money & fulfilment concepts

[ภาพแก้ไขได้](domain-commerce-model.drawio.png) · [draw.io source](domain-commerce-model.drawio) · [HTML](domain-commerce-model.html) · [สารบัญ](README.md)

## สิ่งที่ภาพนี้อธิบาย

Cart lineคือรายการที่เลือกซื้อ ไม่มีCart headerและไม่มีFK Cart→Order การcheckoutเป็นuse-case conversionที่ต้องอ่านspec ไม่ใช่associationในDB เมื่อสร้างOrderจะมีOrder lineที่อ้างProduct/SKU/Shop/Lot พร้อมprice/profit fields และOrderมีทั้งaddress_idกับship_*snapshot

Payment attemptเป็นประวัติการติดต่อproviderของOrder ไม่ใช่คำยืนยันว่ามีหนึ่งแถวตลอดอายุOrder Partialunique uq_t_payment_order_id_liveจำกัดเฉพาะACTIVEในPENDING/PROCESSING/COMPLETEDเท่านั้น การคืนเงินอยู่ในrefund fieldsของt_payment ไม่มีRefund tableแยกในDBชุดนี้

Shipmentเป็นparcelของOrder ส่วนShipment allocationเชื่อมparcelกับOrder lineและquantity จึงรองรับการแบ่งส่ง Shipment stopเป็นจุดแวะ/ลำดับของparcel ไม่ใช่order status แยกความหมายนี้ช่วยไม่ให้วาดOrder lineหนึ่งรายการเท่ากับShipmentหนึ่งแถว

CampaignมีProduct/category target, Shop eligibility, Discount rule, Campaign budgetและBudget movement ตัวmovementเก็บRESERVE/RELEASEและอ้างOrder แม้ชื่อphysicaltableขึ้นต้นm_ก็ไม่ใช่configuration

## กฎเงินและข้อจำกัดที่ตรวจพบ

| เรื่อง | DDL evidence | สิ่งที่ยังต้องตรวจเพิ่ม |
| --- | --- | --- |
| Order total | ck_t_order_total_amount_sum: amount = price - discount + tax + shipping | DDLไม่กำหนดtax rate, discount priorityหรือrounding |
| Order line total | total_price = price * quantity | ไม่หักdiscountซ้ำเข้าในสมการนี้โดยพลการ |
| Payment completion | COMPLETED/REFUNDEDต้องมีtransaction_at | FK/CHECKไม่ใช่การยืนยันผลจากproviderจริง |
| Refund evidence | REFUNDEDสัมพันธ์กับrefunded_at/provider_refund_id | ไม่ได้แทนpartial/unknown provider recoveryที่ต้องอ่านpayment specs |
| Shipment | shipped/returned statesต้องมีtrackingและshipped_at; deliveredสัมพันธ์กับdelivered_at | ไม่มีSUMcheckว่าallocationรวมไม่เกินorderedquantity |
| Budget | remainingระหว่าง0กับbudget | ไม่มีCHECKว่าremainingตรงกับผลรวมledgerทุกแถว |
| Movement identity | UNIQUE(budget,order,entry_type) | ไม่รับรองcampaign_idตรงกับcampaignของbudgetหรือreservation atomicityทั้งหมด |
| Eligibility | product_id XOR product_category_id | สองFKnullableไม่ได้แปลว่าไม่มีtargetเลยก็ได้ |

Order DDLมี7statusesรวมPENDING ภาพนี้ไม่ได้คัดหกbusinessstatesจากภาพlifecycleเดิมมาอ้างว่าเป็นenumทั้งหมด การคำนวณ OrderTotal, stock/parcel allocation guards และbudget reconciliationเป็นcandidateที่ควรมีในDomainของfeatureที่เป็นเจ้าของกฎ แต่การกำหนดtransaction/locking/provider recoveryต้องใช้approvedspecเพิ่มเติม

## เหตุผลของการจัดรูป

ภาพแยกกรอบCart, Sales, Payment, ShippingและCampaignตามข้อมูลจริง ใช้associationlines11เส้นและall-row cardinality ไม่วาดลูกศรสั่งงานหรือSQLtransactionเดียวครอบทุกกรอบ FKไปUser/Shop/Product/SKU/Lotและmovement→Orderที่ไม่ลากข้ามทั้งหน้าแสดงครบในcatalogueด้านล่าง จำนวนFK27ช่องของหน้านี้จึงตรวจย้อนหลังได้ทั้งหมด

## ตารางต้นทางและ concept ที่แสดง

กล่อง/ชื่อเป็นconceptual interpretationของschemaที่มีอยู่ ไม่ใช่รายชื่อclassที่implementแล้ว Universal audit fieldsยังคงอยู่ในDDL แม้ไม่แสดงบนภาพ

| SQL table / schema doc | Business concept | รายละเอียดที่เลือกแสดง | Migration |
| --- | --- | --- | --- |
| [cart.t_cart](../../doc/schema/cart/t_cart.md) | Cart line | `# id / user_id / shop_id; product_id / sku_id; quantity > 0` | [05-cart.schema.up.sql](../../db/migrations/up/05-cart.schema.up.sql) |
| [sales.t_order](../../doc/schema/sales/t_order.md) | Order | `# id / user_id / shop_id; address_id + ship_* snapshot; total_price / total_discount / total_tax; total_shipping / total_amount; status / expires_at` | [06-sales.schema.up.sql](../../db/migrations/up/06-sales.schema.up.sql) |
| [sales.t_order_item](../../doc/schema/sales/t_order_item.md) | Order line | `# id / order_id; shop_id / product_id / sku_id; lot_id / quantity; price / discount / total_price; gross_profit / profit shares` | [06-sales.schema.up.sql](../../db/migrations/up/06-sales.schema.up.sql) |
| [payment.t_payment](../../doc/schema/payment/t_payment.md) | Payment attempt | `# id / order_id; provider_payment_id / status; amount / currency / refund IDs` | [07-payment.schema.up.sql](../../db/migrations/up/07-payment.schema.up.sql) |
| [shipping.t_shipping](../../doc/schema/shipping/t_shipping.md) | Shipment | `# id / order_id; status / carrier / tracking; shipped_at / delivered_at` | [08-shipping.schema.up.sql](../../db/migrations/up/08-shipping.schema.up.sql) |
| [shipping.t_shipping_item](../../doc/schema/shipping/t_shipping_item.md) | Shipment allocation | `# id / shipping_id; order_item_id; quantity > 0` | [08-shipping.schema.up.sql](../../db/migrations/up/08-shipping.schema.up.sql) |
| [shipping.t_shipping_stop](../../doc/schema/shipping/t_shipping_stop.md) | Shipment stop | `# id / shipping_id; stop_number / stop_type; location_name` | [08-shipping.schema.up.sql](../../db/migrations/up/08-shipping.schema.up.sql) |
| [campaign.m_campaign](../../doc/schema/campaign/m_campaign.md) | Campaign | `# id / name; start_at / end_at` | [09-campaign.schema.up.sql](../../db/migrations/up/09-campaign.schema.up.sql) |
| [campaign.m_campaign_budget](../../doc/schema/campaign/m_campaign_budget.md) | Campaign budget | `# id / campaign_id; budget / remaining` | [09-campaign.schema.up.sql](../../db/migrations/up/09-campaign.schema.up.sql) |
| [campaign.m_campaign_budget_ledger](../../doc/schema/campaign/m_campaign_budget_ledger.md) | Budget movement | `# id / campaign_budget_id; campaign_id / order_id; entry_type / usage / remaining` | [09-campaign.schema.up.sql](../../db/migrations/up/09-campaign.schema.up.sql) |
| [campaign.t_campaign_product](../../doc/schema/campaign/t_campaign_product.md) | Product/category target | `# id / campaign_id; product_id?; product_category_id? (XOR)` | [09-campaign.schema.up.sql](../../db/migrations/up/09-campaign.schema.up.sql) |
| [campaign.t_campaign_shop](../../doc/schema/campaign/t_campaign_shop.md) | Shop eligibility | `# id / campaign_id; shop_id` | [09-campaign.schema.up.sql](../../db/migrations/up/09-campaign.schema.up.sql) |
| [campaign.t_campaign_discount](../../doc/schema/campaign/t_campaign_discount.md) | Discount rule | `# id / campaign_id; discount_type / discount_value` | [09-campaign.schema.up.sql](../../db/migrations/up/09-campaign.schema.up.sql) |

## Associations ที่เลือกวาด

ตัวเลขใกล้parentคือจำนวนparentต่อchild ตัวเลขใกล้childคือจำนวนchildต่อparent เมื่อรวมทุกแถวในประวัติ เส้นไม่มีหัวลูกศรและไม่บอกลำดับเวลา

| Parent → child (อ่านassociation ไม่ใช่call) | FKของchild | Cardinalityที่ปลาย parent / child |
| --- | --- | --- |
| Order — Order line | `sales.t_order_item.order_id` | `1` / `0..*` |
| Order — Payment attempt | `payment.t_payment.order_id` | `1` / `0..*` |
| Order — Shipment | `shipping.t_shipping.order_id` | `1` / `0..*` |
| Order line — Shipment allocation | `shipping.t_shipping_item.order_item_id` | `1` / `0..*` |
| Shipment — Shipment allocation | `shipping.t_shipping_item.shipping_id` | `1` / `0..*` |
| Shipment — Shipment stop | `shipping.t_shipping_stop.shipping_id` | `1` / `0..*` |
| Campaign — Campaign budget | `campaign.m_campaign_budget.campaign_id` | `1` / `0..*` |
| Campaign — Discount rule | `campaign.t_campaign_discount.campaign_id` | `1` / `0..*` |
| Campaign budget — Budget movement | `campaign.m_campaign_budget_ledger.campaign_budget_id` | `1` / `0..*` |
| Campaign — Product/category target | `campaign.t_campaign_product.campaign_id` | `1` / `0..*` |
| Campaign — Shop eligibility | `campaign.t_campaign_shop.campaign_id` | `1` / `0..*` |

## FK catalogue — ครบทุกreferenceของตารางในหน้านี้

รายการที่ไม่ลากเส้นยังเป็นความสัมพันธ์จริงในDB ใช้ตารางนี้ต่อข้ามภาพ 1หมายถึงFKบังคับ, 0..1หมายถึงnullable FK; ด้านจำนวนchildrenเป็น0..*ในโมเดลรวมประวัติ การลบตามFKไม่ใช่หลักฐานUMLcompositionหรือDDDaggregate

| Child FK | Parent table | Parentต่อchild | Childต่อparent | ON DELETE | ในภาพ |
| --- | --- | --- | --- | --- | --- |
| `cart.t_cart.user_id` | `authen.m_user` | 1 | 0..* | CASCADE | field / catalogue |
| `cart.t_cart.shop_id` | `shop.m_shop` | 1 | 0..* | CASCADE | field / catalogue |
| `cart.t_cart.product_id` | `product.m_product` | 1 | 0..* | CASCADE | field / catalogue |
| `cart.t_cart.sku_id` | `product.m_product_sku` | 1 | 0..* | CASCADE | field / catalogue |
| `sales.t_order.user_id` | `authen.m_user` | 1 | 0..* | CASCADE | field / catalogue |
| `sales.t_order.shop_id` | `shop.m_shop` | 1 | 0..* | CASCADE | field / catalogue |
| `sales.t_order.address_id` | `authen.t_user_address` | 1 | 0..* | RESTRICT | field / catalogue |
| `sales.t_order_item.order_id` | `sales.t_order` | 1 | 0..* | CASCADE | วาดเส้น |
| `sales.t_order_item.shop_id` | `shop.m_shop` | 1 | 0..* | CASCADE | field / catalogue |
| `sales.t_order_item.product_id` | `product.m_product` | 1 | 0..* | CASCADE | field / catalogue |
| `sales.t_order_item.sku_id` | `product.m_product_sku` | 1 | 0..* | CASCADE | field / catalogue |
| `sales.t_order_item.lot_id` | `shop.t_shop_product_sku_lot` | 1 | 0..* | RESTRICT | field / catalogue |
| `payment.t_payment.order_id` | `sales.t_order` | 1 | 0..* | RESTRICT | วาดเส้น |
| `shipping.t_shipping.order_id` | `sales.t_order` | 1 | 0..* | RESTRICT | วาดเส้น |
| `shipping.t_shipping_item.shipping_id` | `shipping.t_shipping` | 1 | 0..* | CASCADE | วาดเส้น |
| `shipping.t_shipping_item.order_item_id` | `sales.t_order_item` | 1 | 0..* | RESTRICT | วาดเส้น |
| `shipping.t_shipping_stop.shipping_id` | `shipping.t_shipping` | 1 | 0..* | CASCADE | วาดเส้น |
| `campaign.m_campaign_budget.campaign_id` | `campaign.m_campaign` | 1 | 0..* | CASCADE | วาดเส้น |
| `campaign.m_campaign_budget_ledger.campaign_budget_id` | `campaign.m_campaign_budget` | 1 | 0..* | CASCADE | วาดเส้น |
| `campaign.m_campaign_budget_ledger.campaign_id` | `campaign.m_campaign` | 1 | 0..* | CASCADE | field / catalogue |
| `campaign.m_campaign_budget_ledger.order_id` | `sales.t_order` | 1 | 0..* | RESTRICT | field / catalogue |
| `campaign.t_campaign_product.campaign_id` | `campaign.m_campaign` | 1 | 0..* | CASCADE | วาดเส้น |
| `campaign.t_campaign_product.product_category_id` | `product.m_product_category` | 0..1 | 0..* | CASCADE | field / catalogue |
| `campaign.t_campaign_product.product_id` | `product.m_product` | 0..1 | 0..* | CASCADE | field / catalogue |
| `campaign.t_campaign_shop.campaign_id` | `campaign.m_campaign` | 1 | 0..* | CASCADE | วาดเส้น |
| `campaign.t_campaign_shop.shop_id` | `shop.m_shop` | 1 | 0..* | CASCADE | field / catalogue |
| `campaign.t_campaign_discount.campaign_id` | `campaign.m_campaign` | 1 | 0..* | CASCADE | วาดเส้น |

## Partial uniqueness ที่ต้องไม่อ่านเป็น unconditional1:1

| Table | Unique index / predicate |
| --- | --- |
| `cart.t_cart` | `uq_t_cart_user_id_shop_id_product_id_sku_id ON cart.t_cart (user_id, shop_id, product_id, sku_id) WHERE row_status <> 'DELETED';` |
| `payment.t_payment` | `uq_t_payment_order_id_live ON payment.t_payment (order_id) WHERE status IN ('PENDING', 'PROCESSING', 'COMPLETED') AND row_status = 'ACTIVE';` |
| `shipping.t_shipping` | `uq_t_shipping_carrier_name_tracking_number ON shipping.t_shipping (carrier_name, tracking_number) WHERE tracking_number IS NOT NULL AND row_status <> 'DELETED';` |
| `shipping.t_shipping_item` | `uq_t_shipping_item_shipping_id_order_item_id ON shipping.t_shipping_item (shipping_id, order_item_id) WHERE row_status <> 'DELETED';` |
| `shipping.t_shipping_stop` | `uq_t_shipping_stop_shipping_id_stop_number ON shipping.t_shipping_stop (shipping_id, stop_number) WHERE row_status <> 'DELETED';` |
| `campaign.m_campaign` | `uq_m_campaign_name ON campaign.m_campaign (name) WHERE row_status <> 'DELETED';` |
| `campaign.m_campaign_budget` | `uq_m_campaign_budget_campaign_id ON campaign.m_campaign_budget (campaign_id) WHERE row_status <> 'DELETED';` |
| `campaign.t_campaign_product` | `uq_t_campaign_product_campaign_id_product_id ON campaign.t_campaign_product (campaign_id, product_id) WHERE product_id IS NOT NULL AND row_status <> 'DELETED';` |
| `campaign.t_campaign_product` | `uq_t_campaign_product_campaign_id_product_category_id ON campaign.t_campaign_product (campaign_id, product_category_id) WHERE product_category_id IS NOT NULL AND row_status <> 'DELETED';` |
| `campaign.t_campaign_shop` | `uq_t_campaign_shop_campaign_id_shop_id ON campaign.t_campaign_shop (campaign_id, shop_id) WHERE row_status <> 'DELETED';` |
| `campaign.t_campaign_discount` | `uq_t_campaign_discount_campaign_id ON campaign.t_campaign_discount (campaign_id) WHERE row_status <> 'DELETED';` |

## การตรวจและการสร้างซ้ำ

```sh
python3 -B e-commerce/diagram/domain/generate_domain_diagrams.py --check
```

Generatorเทียบtable/column/nullability/reference/constraint/indexและhashของmigration/schema docsกับ [source inventory](domain-source-inventory.json) ก่อนตรวจmodel, nativeparent/child, text capacity, routesและcardinality positions ถ้าDBหรือmappingเปลี่ยนให้reviewmodelแล้วใช้ `--refresh-inventory` และสร้างภาพใหม่ ไม่แก้DDLเพื่อให้ภาพผ่าน

```sh
python3 -B e-commerce/diagram/domain/generate_domain_diagrams.py
# export each .drawio with draw.io Desktop as shown in README
python3 -B e-commerce/diagram/domain/generate_domain_diagrams.py --finalize-pngs
```

ใช้styleอ่อน/แต้มส้มเดิมและA3landscape1584×1120 NativePNGใช้fontfallbacksที่READMEเปิดเผย ผลตรวจภาพจริงและeditabilityอยู่ใน [domain-model-verification.md](domain-model-verification.md) ไม่มีbackend/API/schema implementationหรือruntimeDB/provider testsในงานนี้

## แหล่งอ้างอิง

- [Schema index](../../doc/schema/README.md), [migrations](../../db/migrations/up/), [physical ER เดิม](../../db/er-diagram.drawio)
- [Microsoft domain analysis](https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis): ใช้ประกอบการแยกconcept/ขอบเขตเชิงธุรกิจ; ไม่ถือว่าSQLschemaเท่ากับboundedcontext
- [PostgreSQL constraints](https://www.postgresql.org/docs/18/ddl-constraints.html) และ [partial indexes](https://www.postgresql.org/docs/18/indexes-partial.html): ใช้ตีความFK, nullabilityและconditionaluniqueness

SQL/schema baseline commit: `7007015ba770973daab0460f850b01bb789a4989`; file hashesบันทึกในinventoryเพื่อให้ตรวจdriftได้ แม้ภายหลังbranchมีcommitงานภาพเพิ่ม
