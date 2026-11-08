---
name: Catalog, shop listings & stock concepts — explanation and SQL traceability
description: อธิบาย domain diagram domain-merchandising-model พร้อมเหตุผล ตารางต้นทาง ความสัมพันธ์และcardinalityจากSQL ใช้ก่อนreviewหรือแก้ภาพนี้
status: in-review
approved_by: null
approved_at: null
---

# Catalog, shop listings & stock concepts

[ภาพแก้ไขได้](domain-merchandising-model.drawio.png) · [draw.io source](domain-merchandising-model.drawio) · [HTML](domain-merchandising-model.html) · [สารบัญ](README.md)

## สิ่งที่ภาพนี้อธิบาย

Productคือคำอธิบายสินค้ากลาง เชื่อม Type, Category, Brand และattributes Category attribute definitionกำหนดหัวข้อ attribute ส่วน Product attribute valueเก็บค่าของสินค้า Option level/Option valueใช้สร้างvariant; SKU option selectionเป็นassociationของSKUกับค่าตัวเลือก ไม่ใช่ stock

ฝั่ง Shopแยก Shop listingที่นำสินค้าในcatalogมาขาย, Shop SKUที่ร้านเลือกมาขาย และ Stock lotที่เก็บcost_price, selling_price, quantityและสถานะขาย เหตุผลที่แยกคือร้านต่างกันและlotต่างกันมีข้อมูลเชิงพาณิชย์ต่างกัน แม้ใช้Product SKUเดียวกัน Product reviewอ้างlistingและuser ส่วนShop membershipอ้างshopและuser จึงไม่ควรผูกreviewกับglobalproductเพียงอย่างเดียว

## Constraints ที่ต้องรักษา

| กฎ | หลักฐาน | ความหมาย |
| --- | --- | --- |
| Lotขายไม่ต่ำกว่าต้นทุน | ck_t_shop_product_sku_lot_price_not_below_cost | selling_price >= cost_price |
| Lotที่ขายปัจจุบัน | uq_t_shop_product_sku_lot_on_sale | จำกัดหนึ่ง ACTIVE+is_on_saleต่อShop SKU ไม่ได้จำกัดประวัติlotทั้งหมด |
| Marginของร้าน | ck_m_shop_margin_rate_total | platform_margin_rate + shop_margin_rate <=100 |
| SKU combination | uq_m_product_sku_product_id_combination_key | combination_keyไม่ซ้ำต่อproductเฉพาะnon-DELETED |
| Option levels | unique product_id/level_no และ product_id/name | ขอบเขตคือproductและแถวที่เข้าpredicate |
| SKU selection | UNIQUE(sku_id,option_value_id) | ไม่เท่ากับบังคับหนึ่งvalueต่อoption level |

Categoryมี optional parent_id แต่ FKไม่ป้องกันcycle Product imageมี optional option_value_id จึงเป็นได้ทั้งภาพทั่วไปและภาพเฉพาะตัวเลือก เส้น Option value→Product image แสดง0..1ที่ปลายOption valueอย่างชัดเจน

## กฎที่หลายFKยังไม่รับรองร่วมกัน

DDLยืนยันว่าทุกidมีปลายทาง แต่ไม่ได้ยืนยันด้วยcompositeFKว่า SKUเป็นของProductที่listingอ้าง, attribute valueใช้attributeจากcategoryที่ถูกต้อง, image/optionเป็นของProductเดียวกัน หรือselectedvaluesใช้เพียงหนึ่งต่อlevel กฎเหล่านี้ต้องตรวจในbusiness logic/specก่อนimplementation ไม่อ้างว่า FKเดี่ยวปิดช่องว่างทั้งหมด

Candidateสำหรับ `<Feature>/Domain/` ได้แก่ SKU combination consistency, lot pricing/margin calculations และoffer eligibility โดยใช้ข้อมูล business values/approved policy ไม่ส่งRedis/MongoSDKเข้ามาในกฎ ส่วนการคำนวณภาษีไม่สามารถหาอัตราหรือroundingจากschemaสินค้านี้ได้

## เหตุผลของการจัดรูป

กรอบ CatalogและMerchantแยกข้อมูลสินค้ากลางจากข้อเสนอขายจริง เลือก12associationsที่อธิบายProduct→SKU→selection/option และShop→listing→Shop SKU→lot/review ส่วนFKรองและcross-schema User referencesอยู่ในcatalogueด้านล่าง กล่องมีfieldชื่อidช่วยตามความสัมพันธ์ที่ไม่วาดโดยไม่ลากทุกFKตัดกัน

## ตารางต้นทางและ concept ที่แสดง

กล่อง/ชื่อเป็นconceptual interpretationของschemaที่มีอยู่ ไม่ใช่รายชื่อclassที่implementแล้ว Universal audit fieldsยังคงอยู่ในDDL แม้ไม่แสดงบนภาพ

| SQL table / schema doc | Business concept | รายละเอียดที่เลือกแสดง | Migration |
| --- | --- | --- | --- |
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

## Associations ที่เลือกวาด

ตัวเลขใกล้parentคือจำนวนparentต่อchild ตัวเลขใกล้childคือจำนวนchildต่อparent เมื่อรวมทุกแถวในประวัติ เส้นไม่มีหัวลูกศรและไม่บอกลำดับเวลา

| Parent → child (อ่านassociation ไม่ใช่call) | FKของchild | Cardinalityที่ปลาย parent / child |
| --- | --- | --- |
| Category — Product | `product.m_product.category_id` | `1` / `0..*` |
| Option value — Product image | `product.m_product_image.option_value_id` | `0..1` / `0..*` |
| Product type — Product | `product.m_product.type_id` | `1` / `0..*` |
| Product — Product SKU | `product.m_product_sku.product_id` | `1` / `0..*` |
| Product SKU — SKU option selection | `product.m_product_sku_option_value.sku_id` | `1` / `0..*` |
| Option value — SKU option selection | `product.m_product_sku_option_value.option_value_id` | `1` / `0..*` |
| Option level — Option value | `product.m_product_option_value.option_id` | `1` / `0..*` |
| Shop type — Shop | `shop.m_shop.type_id` | `1` / `0..*` |
| Shop — Shop listing | `shop.t_shop_product.shop_id` | `1` / `0..*` |
| Shop listing — Shop SKU | `shop.t_shop_product_sku.shop_product_id` | `1` / `0..*` |
| Shop SKU — Stock lot | `shop.t_shop_product_sku_lot.shop_product_sku_id` | `1` / `0..*` |
| Shop listing — Product review | `shop.t_shop_product_review.shop_product_id` | `1` / `0..*` |

## FK catalogue — ครบทุกreferenceของตารางในหน้านี้

รายการที่ไม่ลากเส้นยังเป็นความสัมพันธ์จริงในDB ใช้ตารางนี้ต่อข้ามภาพ 1หมายถึงFKบังคับ, 0..1หมายถึงnullable FK; ด้านจำนวนchildrenเป็น0..*ในโมเดลรวมประวัติ การลบตามFKไม่ใช่หลักฐานUMLcompositionหรือDDDaggregate

| Child FK | Parent table | Parentต่อchild | Childต่อparent | ON DELETE | ในภาพ |
| --- | --- | --- | --- | --- | --- |
| `product.m_product_category.parent_id` | `product.m_product_category` | 0..1 | 0..* | CASCADE | field / catalogue |
| `product.m_product_category_attribute.category_id` | `product.m_product_category` | 1 | 0..* | CASCADE | field / catalogue |
| `product.m_product.type_id` | `product.m_product_type` | 1 | 0..* | RESTRICT | วาดเส้น |
| `product.m_product.category_id` | `product.m_product_category` | 1 | 0..* | CASCADE | วาดเส้น |
| `product.m_product.brand_id` | `product.m_product_brand` | 1 | 0..* | RESTRICT | field / catalogue |
| `product.m_product_attribute.product_id` | `product.m_product` | 1 | 0..* | CASCADE | field / catalogue |
| `product.m_product_attribute.attribute_id` | `product.m_product_category_attribute` | 1 | 0..* | CASCADE | field / catalogue |
| `product.m_product_option.product_id` | `product.m_product` | 1 | 0..* | CASCADE | field / catalogue |
| `product.m_product_option_value.option_id` | `product.m_product_option` | 1 | 0..* | CASCADE | วาดเส้น |
| `product.m_product_image.product_id` | `product.m_product` | 1 | 0..* | CASCADE | field / catalogue |
| `product.m_product_image.option_value_id` | `product.m_product_option_value` | 0..1 | 0..* | CASCADE | วาดเส้น |
| `product.m_product_sku.product_id` | `product.m_product` | 1 | 0..* | CASCADE | วาดเส้น |
| `product.m_product_sku_option_value.sku_id` | `product.m_product_sku` | 1 | 0..* | CASCADE | วาดเส้น |
| `product.m_product_sku_option_value.option_value_id` | `product.m_product_option_value` | 1 | 0..* | CASCADE | วาดเส้น |
| `shop.m_shop.type_id` | `shop.m_shop_type` | 1 | 0..* | RESTRICT | วาดเส้น |
| `shop.t_shop_user.shop_id` | `shop.m_shop` | 1 | 0..* | CASCADE | field / catalogue |
| `shop.t_shop_user.user_id` | `authen.m_user` | 1 | 0..* | CASCADE | field / catalogue |
| `shop.m_shop_image.shop_id` | `shop.m_shop` | 1 | 0..* | CASCADE | field / catalogue |
| `shop.t_shop_product.shop_id` | `shop.m_shop` | 1 | 0..* | CASCADE | วาดเส้น |
| `shop.t_shop_product.product_id` | `product.m_product` | 1 | 0..* | CASCADE | field / catalogue |
| `shop.t_shop_product_sku.shop_product_id` | `shop.t_shop_product` | 1 | 0..* | CASCADE | วาดเส้น |
| `shop.t_shop_product_sku.sku_id` | `product.m_product_sku` | 1 | 0..* | CASCADE | field / catalogue |
| `shop.t_shop_product_sku_lot.shop_product_sku_id` | `shop.t_shop_product_sku` | 1 | 0..* | CASCADE | วาดเส้น |
| `shop.t_shop_product_review.shop_product_id` | `shop.t_shop_product` | 1 | 0..* | CASCADE | วาดเส้น |
| `shop.t_shop_product_review.user_id` | `authen.m_user` | 1 | 0..* | CASCADE | field / catalogue |

## Partial uniqueness ที่ต้องไม่อ่านเป็น unconditional1:1

| Table | Unique index / predicate |
| --- | --- |
| `product.m_product_type` | `uq_m_product_type_name ON product.m_product_type (name) WHERE row_status <> 'DELETED';` |
| `product.m_product_brand` | `uq_m_product_brand_name ON product.m_product_brand (name) WHERE row_status <> 'DELETED';` |
| `product.m_product_option` | `uq_m_product_option_product_id_level_no ON product.m_product_option (product_id, level_no) WHERE row_status <> 'DELETED';` |
| `product.m_product_option` | `uq_m_product_option_product_id_name ON product.m_product_option (product_id, name) WHERE row_status <> 'DELETED';` |
| `product.m_product_option_value` | `uq_m_product_option_value_option_id_value ON product.m_product_option_value (option_id, value) WHERE row_status <> 'DELETED';` |
| `product.m_product_sku` | `uq_m_product_sku_product_id_combination_key ON product.m_product_sku (product_id, combination_key) WHERE row_status <> 'DELETED';` |
| `shop.m_shop_type` | `uq_m_shop_type_name ON shop.m_shop_type (name) WHERE row_status <> 'DELETED';` |
| `shop.m_shop` | `uq_m_shop_name ON shop.m_shop (name) WHERE row_status <> 'DELETED';` |
| `shop.t_shop_user` | `uq_t_shop_user_shop_id_user_id ON shop.t_shop_user (shop_id, user_id) WHERE row_status <> 'DELETED';` |
| `shop.m_shop_image` | `uq_m_shop_image_shop_id_logo ON shop.m_shop_image (shop_id) WHERE type = 'LOGO' AND row_status <> 'DELETED';` |
| `shop.m_shop_image` | `uq_m_shop_image_shop_id_wallpaper ON shop.m_shop_image (shop_id) WHERE type = 'WALLPAPER' AND row_status <> 'DELETED';` |
| `shop.t_shop_product` | `uq_t_shop_product_shop_id_product_id ON shop.t_shop_product (shop_id, product_id) WHERE row_status <> 'DELETED';` |
| `shop.t_shop_product_sku_lot` | `uq_t_shop_product_sku_lot_shop_product_sku_id_lot_no ON shop.t_shop_product_sku_lot (shop_product_sku_id, lot_no) WHERE row_status <> 'DELETED';` |
| `shop.t_shop_product_sku_lot` | `uq_t_shop_product_sku_lot_on_sale ON shop.t_shop_product_sku_lot (shop_product_sku_id) WHERE is_on_sale AND row_status = 'ACTIVE';` |
| `shop.t_shop_product_review` | `uq_t_shop_product_review_shop_product_id_user_id ON shop.t_shop_product_review (shop_product_id, user_id) WHERE row_status <> 'DELETED';` |

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
