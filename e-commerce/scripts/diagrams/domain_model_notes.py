"""Thai rationale for the conceptual domain views; SQL evidence is added by the renderer."""
NOTES={
'domain-model':'''## ความหมายและขอบเขต

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
''',
'domain-identity-model':'''## สิ่งที่ภาพนี้อธิบาย

User เป็นตัวตนบัญชี ส่วน Password credential, Password reset request, User profile, Delivery address, Access/Refresh token และ evidence records เป็นแนวคิดที่ต่างหน้าที่กัน กล่อง authen เป็นการจัดกลุ่มตาม schema ไม่ได้ประกาศว่า objects ทั้งหมดเป็น aggregate เดียวหรือควรโหลดใน transaction เดียว

Authorization แยก Role, Permission, Scope และ association entities สามารถตามว่า role ได้ permission ใด มี scope ใด และ user ได้สิทธิ์ผ่าน role หรือ direct grant ใด คำว่า author ในชื่อ schema หมายถึง authorization ไม่ใช่ผู้เขียนบทความ การซ้อนกรอบไม่แปลว่า config/feature flag สามารถให้สิทธิ์แทนตารางเหล่านี้

Consent type เป็นชนิดข้อยินยอม Consent version คือเนื้อหาที่เผยแพร่ ส่วน Consent acknowledgement อยู่ authen และบันทึกผู้ใช้/เวอร์ชัน/ผลการตอบรับ การแยกสามแนวคิดนี้ช่วยไม่ให้สับสนระหว่างการแก้เอกสารกับหลักฐานที่ผู้ใช้เคยเห็น

## Cardinality และประวัติ

ใช้ all-row cardinality ตาม FK: แถวลูกที่มี FK NOT NULL อ้าง parentหนึ่งแถว; ลูกอาจมี0..*ต่อparent เพราะ DDL ไม่บังคับให้ parentต้องมีลูก และ partial indexesยังอนุญาตแถวเก่า/แถวที่ไม่เข้าpredicate กรณี User profile ไม่ใช่ unconditional1:1; Password credential จำกัดหนึ่ง ACTIVE PASSWORD; reset request จำกัดหนึ่ง ACTIVE; addressจำกัดหนึ่งdefaultที่ไม่DELETED แต่ไม่จำกัดว่าผู้ใช้มีaddressได้เพียงหนึ่ง

Scoped permission → Direct permission grant เป็น optional0..1จาก nullable permission_scope_id อีกด้านของ grantยังมี permission_id ที่ต้องตรวจความสอดคล้องกันเพิ่มเติม ไม่ใช่ FKแบบcompositeที่รับรองให้แล้วทุกกรณี

## ความแตกต่างระหว่าง DB evidence กับกฎที่ต้องออกแบบต่อ

| จุด | DDL ที่ยืนยันได้ | สิ่งที่ไม่ได้พิสูจน์จาก DDL |
| --- | --- | --- |
| Session | tokenทั้งสองชนิดมี session_id | ไม่มี Session table หรือ FKยืนยันว่า access/refreshเป็นคู่เดียวกัน |
| Consent acknowledgement | user_id/consent_id และ fields consent_version, result, is_read, read_at | ไม่มี UNIQUE(user,consent,version) หรือ CHECKบังคับread_atสัมพันธ์กับis_read |
| Referral event | user_idบังคับ, referrer_id nullable | ไม่ได้เป็นหนึ่งreferralต่อuserโดยอัตโนมัติ |
| Login attempt | user_id nullable รองรับidentifierที่ไม่ตรงบัญชี | ไม่มี User เป็นparentบังคับทุกattempt |
| Scoped grant | แต่ละFKมีparentจริง | ไม่รับรองว่า scoped permissionเป็นของ permission_idเดียวกับ direct grant |
| Key material | key_nameไม่ซ้ำ, binary value, effective/expiry fields | ไม่พิสูจน์ runtime key rotation, secret storage controls หรือ encryption of the value |

## เหตุผลของการจัดรูป

ใช้ entityชื่อธุรกิจแทน prefix m_/t_/l_ ทุกconceptมีชื่อตารางกำกับและ attributesที่ช่วยแยกบทบาท เส้นที่เลือก12เส้นเน้นบัญชี/credential, role grants และconsent publication; ความสัมพันธ์อื่นรวมทั้งUser→token,User→acknowledgement และoptionalreferrerอยู่ใน FK catalogue ด้านล่าง จึงไม่ควรตีความ entityที่ไม่มีเส้นในภาพว่าไม่มีreference

กฎที่ควรพิจารณาใน `Authen/Domain/` หรือ authorization domain เช่นความสอดคล้องของ grant เป็น candidateของการออกแบบต่อ ไม่อนุมานว่ามี methods/validatorsครบแล้ว และไม่ย้ายการคำนวณเงินภาษีเข้ามาใน Authen
''',
'domain-merchandising-model':'''## สิ่งที่ภาพนี้อธิบาย

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
''',
'domain-commerce-model':'''## สิ่งที่ภาพนี้อธิบาย

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
'''
}
