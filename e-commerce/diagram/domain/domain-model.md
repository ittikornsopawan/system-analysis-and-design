---
name: E-commerce domain map from the database — explanation and SQL traceability
description: อธิบาย domain diagram domain-model พร้อมเหตุผล ตารางต้นทาง ความสัมพันธ์และcardinalityจากSQL ใช้ก่อนreviewหรือแก้ภาพนี้
status: in-review
approved_by: null
approved_at: null
---

# E-commerce domain map from the database

[ภาพแก้ไขได้](domain-model.drawio.png) · [draw.io source](domain-model.drawio) · [HTML](domain-model.html) · [สารบัญ](README.md)

## ความหมายและขอบเขต

ภาพนี้ตอบว่า **ระบบมีแนวคิดทางธุรกิจอะไรบ้าง และข้อมูลของแนวคิดนั้นอยู่ที่ใด** จัดเป็นแผนที่สำหรับเปิดอ่านรายละเอียดสามหน้า ไม่ใช่ HTTP flow, software layer, deployment หรือการประกาศว่ามี microservices ตามจำนวนกล่อง กล่องใหญ่สามกล่องเป็นขอบเขตการอ่าน กล่องเล็กสิบเอ็ดกล่องคือกลุ่มแนวคิดที่มีฐานจาก SQL schemas ไม่ใช่ DDD aggregates ที่ยืนยันจากฐานข้อมูลได้โดยอัตโนมัติ

Domain model ให้ความสำคัญกับชื่อและความสัมพันธ์ของธุรกิจ ส่วน physical ER เดิมแสดงโครงสร้างการเก็บข้อมูล ภาพรายละเอียดจึงใช้ conceptual ER: entity มีชื่อธุรกิจ ชื่อตารางเพื่อ trace และ attributes ที่จำเป็น ตัด universal audit fields, SQL types, indexes และเส้น FK รองออกจากภาพ แต่เก็บข้อมูลอ้างอิงทั้งหมดในเอกสารและ inventory ไม่ใส่ methods ของ C# หรือ UML composition จาก ON DELETE CASCADE เพราะ DDL ไม่ได้พิสูจน์พฤติกรรมของ class หรือ aggregate lifecycle [Microsoft domain analysis](https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis)

## เหตุผลที่แบ่งเป็นสามหน้า

| หน้า | หน้าที่ | เหตุผล |
| --- | --- | --- |
| Identity / Access / Consent / public | Account, credential, evidence, grants, consent publication และ key material | แยกผู้ใช้ สิทธิ์ และหลักฐานการยินยอม; key material เป็น technical support |
| Product / Shop | Global catalog, variant selections, merchant listing และ stock lot | Product SKU ไม่ใช่ Shop SKU และไม่ใช่ stock lot; ราคา/จำนวนขายอยู่ที่ lot |
| Cart / Sales / Payment / Shipping / Campaign | Selection, stored business snapshots, financial attempts, fulfilment allocation และ budget movement | เน้นความสัมพันธ์ของธุรกรรมและประวัติ ไม่สรุปว่าทุกชุดอยู่ใน aggregate/transaction เดียว |

หน้ารายละเอียดมี 21, 19 และ 13 concepts รวม53ตาราง แต่ไม่มีการบังคับว่าตารางหนึ่งต้องเท่ากับ C# entity หนึ่งตัว การแยก class/value object/aggregate ต้องใช้ requirements และ use cases เพิ่มเติม ตารางเชื่อมที่มีข้อมูลของตนเองถูกตั้งชื่อให้เห็นความหมาย เช่น Scoped role grant, Shipment allocation และ Budget movement

## ข้อมูลที่ต้องอ่านให้ถูก

- `cart.t_cart` คือ Cart line ไม่มี Cart header; token สองชนิดมี session_id แต่ไม่มี Session table หรือ token-to-token FK
- Order มี address FK พร้อม ship_* snapshot และ Order line อ้าง original lot; การอ่านยอดเงินไม่ควรย้อนคำนวณจากราคาของ lot ปัจจุบัน
- Order → Payment attempt เป็น0..*เมื่อรวมประวัติ การจำกัด live payment เป็น partial unique subset ไม่ใช่ unconditional1:1
- Campaign budget movement แม้ขึ้นต้น m_ ก็เป็น movement ledger ที่เชื่อม budget, campaign และ order ไม่ใช่ config ทั่วไป
- `public.t_key` เป็น binary key material ไม่ใช่ MongoDB configuration ตามภาพ operational เดิม ไม่มี key values หรือ secret ถูกอ่านจาก runtime
- MongoDB/Redis/outbox ที่เสนอในชุดก่อนหน้าไม่มีตารางใน SQL53ตารางนี้ จึงไม่เพิ่มเป็น entity ที่มีอยู่จริงใน domain model จาก DB

## ความเชื่อมโยงกับโฟลเดอร์ Domain ที่เจ้าของงานกำหนด

เจ้าของงานใช้ `<Feature>/Domain/` เก็บ business logic ที่ใช้ซ้ำ ภาพใหม่นี้ช่วยค้นหาว่า **กฎเป็นของแนวคิดใด** ไม่ได้สร้าง implementation ให้โดยอัตโนมัติ ตัวอย่าง candidate ที่ต้องออกแบบต่อคือการคำนวณ OrderTotal ตามสมการที่ SQLมีอยู่, การตรวจ SKU/lot ว่าสอดคล้องกับสินค้าที่อ้าง, และการเทียบ shipping allocations กับ ordered quantity แต่ภาษี/rounding/discount priority ไม่ได้กำหนดครบจาก DDL ต้องมี spec ที่อนุมัติก่อนเขียนโค้ด การคำนวณภาษีไม่ถูกย้ายไป Authen เพียงเพราะมีตัวอย่าง path `Authen/Domain/`

## ข้อจำกัดของการอนุมานจากฐานข้อมูล

FKยืนยันแต่ละ reference แต่ไม่รับรองว่าหลายreferencesอยู่ใน ownership เดียวกัน, CHECKโดยทั่วไปตรวจระดับแถว, schemaไม่พิสูจน์ bounded context และ partial unique indexใช้เฉพาะแถวตามpredicate การตั้งชื่อธุรกิจ/ขอบเขตการอ่านเป็น interpretation สำหรับ review ไม่ใช่ architecture approval [PostgreSQL constraints](https://www.postgresql.org/docs/18/ddl-constraints.html), [partial indexes](https://www.postgresql.org/docs/18/indexes-partial.html)

## ตารางต้นทางและ concept ที่แสดง

กล่อง/ชื่อเป็นconceptual interpretationของschemaที่มีอยู่ ไม่ใช่รายชื่อclassที่implementแล้ว Universal audit fieldsยังคงอยู่ในDDL แม้ไม่แสดงบนภาพ

| SQL table / schema doc | Business concept | รายละเอียดที่เลือกแสดง | Migration |
| --- | --- | --- | --- |
| [public.t_key](../../doc/schema/public/t_key.md) | Key material | `# id; key_name; effective_at / expired_at` | [00-common.schema.up.sql](../../db/migrations/up/00-common.schema.up.sql) |
| [consent.m_consent_type](../../doc/schema/consent/m_consent_type.md) | Consent type | `# id; name / is_required` | [00-common.schema.up.sql](../../db/migrations/up/00-common.schema.up.sql) |
| [consent.t_consent](../../doc/schema/consent/t_consent.md) | Consent version | `# id / code; consent_type_id; consent_version / body` | [00-common.schema.up.sql](../../db/migrations/up/00-common.schema.up.sql) |
| [authen.m_user](../../doc/schema/authen/m_user.md) | User | `# id; username / email_address; display_name` | [01-authen.schema.up.sql](../../db/migrations/up/01-authen.schema.up.sql) |
| [authen.t_user_consent](../../doc/schema/authen/t_user_consent.md) | Consent acknowledgement | `# id; user_id / consent_id; result / is_read` | [01-authen.schema.up.sql](../../db/migrations/up/01-authen.schema.up.sql) |
| [authen.m_user_password](../../doc/schema/authen/m_user_password.md) | Password credential | `# id / user_id; row_type; password / password_salt` | [01-authen.schema.up.sql](../../db/migrations/up/01-authen.schema.up.sql) |
| [authen.t_user_reset_password](../../doc/schema/authen/t_user_reset_password.md) | Password reset request | `# id / user_id; reset_token; expired_at` | [01-authen.schema.up.sql](../../db/migrations/up/01-authen.schema.up.sql) |
| [authen.l_user_referral](../../doc/schema/authen/l_user_referral.md) | Referral event | `# id / user_id; referrer_id?` | [01-authen.schema.up.sql](../../db/migrations/up/01-authen.schema.up.sql) |
| [authen.m_user_information](../../doc/schema/authen/m_user_information.md) | User profile | `# id / user_id; phone_number / date_of_birth; gender` | [01-authen.schema.up.sql](../../db/migrations/up/01-authen.schema.up.sql) |
| [authen.t_user_address](../../doc/schema/authen/t_user_address.md) | Delivery address | `# id / user_id; address / city / postal_code; is_default` | [01-authen.schema.up.sql](../../db/migrations/up/01-authen.schema.up.sql) |
| [authen.t_user_access_token](../../doc/schema/authen/t_user_access_token.md) | Access token | `# id / user_id; session_id / token; expired_at` | [01-authen.schema.up.sql](../../db/migrations/up/01-authen.schema.up.sql) |
| [authen.t_user_refresh_token](../../doc/schema/authen/t_user_refresh_token.md) | Refresh token | `# id / user_id; session_id / token; expired_at` | [01-authen.schema.up.sql](../../db/migrations/up/01-authen.schema.up.sql) |
| [authen.l_user_login_attempt](../../doc/schema/authen/l_user_login_attempt.md) | Login attempt | `# id / user_id?; identifier_hash; result` | [01-authen.schema.up.sql](../../db/migrations/up/01-authen.schema.up.sql) |
| [author.m_role](../../doc/schema/author/m_role.md) | Role | `# id / name; description` | [02-author.schema.up.sql](../../db/migrations/up/02-author.schema.up.sql) |
| [author.m_permission](../../doc/schema/author/m_permission.md) | Permission | `# id / name; description` | [02-author.schema.up.sql](../../db/migrations/up/02-author.schema.up.sql) |
| [author.m_scope](../../doc/schema/author/m_scope.md) | Scope | `# id / scope; name / description` | [02-author.schema.up.sql](../../db/migrations/up/02-author.schema.up.sql) |
| [author.t_permission_scope](../../doc/schema/author/t_permission_scope.md) | Scoped permission | `# id / permission_id; scope_id` | [02-author.schema.up.sql](../../db/migrations/up/02-author.schema.up.sql) |
| [author.t_role_permission](../../doc/schema/author/t_role_permission.md) | Role permission grant | `# id / role_id; permission_id` | [02-author.schema.up.sql](../../db/migrations/up/02-author.schema.up.sql) |
| [author.t_role_permission_scope](../../doc/schema/author/t_role_permission_scope.md) | Scoped role grant | `# id / role_permission_id; permission_scope_id` | [02-author.schema.up.sql](../../db/migrations/up/02-author.schema.up.sql) |
| [author.t_user_role](../../doc/schema/author/t_user_role.md) | User role assignment | `# id / user_id; role_id` | [02-author.schema.up.sql](../../db/migrations/up/02-author.schema.up.sql) |
| [author.t_user_permission](../../doc/schema/author/t_user_permission.md) | Direct permission grant | `# id / user_id; permission_id; permission_scope_id?` | [02-author.schema.up.sql](../../db/migrations/up/02-author.schema.up.sql) |
| [product.m_product_type](../../doc/schema/product/m_product_type.md) | Product type | `# id / name; description` | [03-product.schema.up.sql](../../db/migrations/up/03-product.schema.up.sql) |
| [product.m_product_category](../../doc/schema/product/m_product_category.md) | Category | `# id / parent_id?; name / slug` | [03-product.schema.up.sql](../../db/migrations/up/03-product.schema.up.sql) |
| [product.m_product_category_attribute](../../doc/schema/product/m_product_category_attribute.md) | Category attribute definition | `# id / category_id; name` | [03-product.schema.up.sql](../../db/migrations/up/03-product.schema.up.sql) |
| [product.m_product_brand](../../doc/schema/product/m_product_brand.md) | Brand | `# id / name; description` | [03-product.schema.up.sql](../../db/migrations/up/03-product.schema.up.sql) |
| [product.m_product](../../doc/schema/product/m_product.md) | Product | `# id / name; type_id / category_id / brand_id; slug / body` | [03-product.schema.up.sql](../../db/migrations/up/03-product.schema.up.sql) |
| [product.m_product_attribute](../../doc/schema/product/m_product_attribute.md) | Product attribute value | `# id / product_id; attribute_id / value` | [03-product.schema.up.sql](../../db/migrations/up/03-product.schema.up.sql) |
| [product.m_product_option](../../doc/schema/product/m_product_option.md) | Option level | `# id / product_id; name / level_no` | [03-product.schema.up.sql](../../db/migrations/up/03-product.schema.up.sql) |
| [product.m_product_option_value](../../doc/schema/product/m_product_option_value.md) | Option value | `# id / option_id; value / sort_order` | [03-product.schema.up.sql](../../db/migrations/up/03-product.schema.up.sql) |
| [product.m_product_image](../../doc/schema/product/m_product_image.md) | Product image | `# id / product_id; option_value_id?; image_path` | [03-product.schema.up.sql](../../db/migrations/up/03-product.schema.up.sql) |
| [product.m_product_sku](../../doc/schema/product/m_product_sku.md) | Product SKU | `# id / product_id; name / combination_key` | [03-product.schema.up.sql](../../db/migrations/up/03-product.schema.up.sql) |
| [product.m_product_sku_option_value](../../doc/schema/product/m_product_sku_option_value.md) | SKU option selection | `# id / sku_id; option_value_id` | [03-product.schema.up.sql](../../db/migrations/up/03-product.schema.up.sql) |
| [shop.m_shop_type](../../doc/schema/shop/m_shop_type.md) | Shop type | `# id / name; description` | [04-shop.schema.up.sql](../../db/migrations/up/04-shop.schema.up.sql) |
| [shop.m_shop](../../doc/schema/shop/m_shop.md) | Shop | `# id / type_id; platform_margin_rate; shop_margin_rate` | [04-shop.schema.up.sql](../../db/migrations/up/04-shop.schema.up.sql) |
| [shop.t_shop_user](../../doc/schema/shop/t_shop_user.md) | Shop membership | `# id / shop_id; user_id / role` | [04-shop.schema.up.sql](../../db/migrations/up/04-shop.schema.up.sql) |
| [shop.m_shop_image](../../doc/schema/shop/m_shop_image.md) | Shop image | `# id / shop_id; type / seq / image_path` | [04-shop.schema.up.sql](../../db/migrations/up/04-shop.schema.up.sql) |
| [shop.t_shop_product](../../doc/schema/shop/t_shop_product.md) | Shop listing | `# id / shop_id; product_id` | [04-shop.schema.up.sql](../../db/migrations/up/04-shop.schema.up.sql) |
| [shop.t_shop_product_sku](../../doc/schema/shop/t_shop_product_sku.md) | Shop SKU | `# id / shop_product_id; sku_id / code` | [04-shop.schema.up.sql](../../db/migrations/up/04-shop.schema.up.sql) |
| [shop.t_shop_product_sku_lot](../../doc/schema/shop/t_shop_product_sku_lot.md) | Stock lot | `# id / shop_product_sku_id; cost_price / selling_price; quantity / is_on_sale` | [04-shop.schema.up.sql](../../db/migrations/up/04-shop.schema.up.sql) |
| [shop.t_shop_product_review](../../doc/schema/shop/t_shop_product_review.md) | Product review | `# id / shop_product_id; user_id / rating; comment?` | [04-shop.schema.up.sql](../../db/migrations/up/04-shop.schema.up.sql) |
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

## Cross-schema references ที่เลือกในภาพรวม

เส้นไม่มีหัวลูกศร แต่ละปลายคือกลุ่มหลายconcept จึงไม่ใส่cardinalityระดับentityหรือสื่อการเรียกservice ใช้FKต่อไปนี้เป็นหลักฐานและอ่านตัวเลขในหน้ารายละเอียดแทน

| กลุ่มที่เชื่อม | FK evidence | Parent table |
| --- | --- | --- |
| Identity — Authorization | `author.t_user_role.user_id` | `authen.m_user` |
| Consent — Identity | `authen.t_user_consent.consent_id` | `consent.t_consent` |
| Product catalog — Merchant offers & inventory | `shop.t_shop_product.product_id` | `product.m_product` |
| Merchant offers & inventory — Order & snapshot | `sales.t_order.shop_id` | `shop.m_shop` |
| Order & snapshot — Payment attempts | `payment.t_payment.order_id` | `sales.t_order` |
| Order & snapshot — Parcel fulfilment | `shipping.t_shipping.order_id` | `sales.t_order` |
| Order & snapshot — Campaign & budget | `campaign.m_campaign_budget_ledger.order_id` | `sales.t_order` |

## เปิดภาพรายละเอียด

- [Identity / Access / Consent](domain-identity-model.md):21ตาราง /23FK
- [Catalog / Shop / Stock](domain-merchandising-model.md):19ตาราง /25FK
- [Commerce](domain-commerce-model.md):13ตาราง /27FK

ทั้งสามหน้าแบ่ง53ตารางแบบไม่ซ้ำกัน มีFKcatalogueรวม75รายการ รวมถึง7nullableFK ไม่บังคับให้วาดเส้นทั้ง75บนภาพเดียว

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
