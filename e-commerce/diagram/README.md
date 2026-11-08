---
name: E-commerce Diagram Set and Reading Guide
description: สารบัญและวิธีอ่าน diagram ทั้ง15มุมมอง พร้อม native containment แหล่งหลักฐาน วิธีสร้างและเกณฑ์ตรวจ ใช้เมื่ออ่านหรือแก้ไขภาพระบบชุดนี้
---

# E-commerce diagrams

ชุดนี้แยก **คำถามและ notation ของแต่ละภาพ** ก่อนจัด layout ตามข้อทักท้วงวันที่2026-11-08 อ่าน [ความหมายและขอบเขตทั้ง15ภาพ](design/diagram-semantics.md) และ [แผน/approval boundary](design/implementation-readiness-plan.md) ก่อนใช้ภาพประกอบการพัฒนา

Architecture มี Presentation/Application/Domain/Infrastructure/Shared เป็น parent layers และ Command/Query, Validator, Handler, Mapping, Ports เป็น child boxes จริง Repository ใช้ project/feature ownership; State ใช้ guard/effect compartments; Sequence ใช้เวลา/lifelines/activation/OPT/ALT; Document model ใช้ fields/cardinality; Deployment ใช้ zones/hosts/artifacts; Observability ใช้ signal pipelines; Recovery ใช้ owner lanes/actions/decision gates

กล่องซ้อนทุกกลุ่มเป็น native draw.io parents ไม่ใช่เส้นกรอบตกแต่ง ตัวเลข child boxes ไม่ใช่จำนวน microservices, tables หรือ persisted states ภาพที่ต้องแสดง decomposition ใช้รายละเอียดตาม hierarchy ที่เจ้าของงานขอ แทนการตัดให้เหลือเก้ากล่องใหญ่

## โครงสร้างโฟลเดอร์

```text
diagram/
├── README.md
├── main/                  # 4 ภาพหลัก พร้อม PNG/draw.io/HTML/คำอธิบาย
├── reference/             # ภาพเพิ่มเติม เก็บเป็น reference ตามเรื่อง
│   ├── business/          # Commerce overview และ checkout
│   ├── payment/           # Start payment, webhook และ refund
│   ├── data/              # MongoDB documents และ configuration
│   ├── operations/        # Deployment, observability และ recovery
│   └── repository/        # Source code และ tests
├── design/                # Design proposals, research, semantics และผลตรวจ
└── scripts/               # Content models, generators และ output-path map
```

ไฟล์ทั้งสี่รูปแบบของแต่ละภาพอยู่โฟลเดอร์เดียวกัน เปิด PNG เพื่อนำเสนอหรือเปิดแก้ใน draw.io; อ่าน `.md` สำหรับขอบเขตและแหล่งอ้างอิง ส่วน `scripts/diagram_paths.py` กำหนดตำแหน่ง output ของตัวสร้างภาพ

## ชุดนำเสนอหลัก — 4 ภาพ

| ภาพ PNG ที่เปิดแก้ไขได้ | คำอธิบาย | คำถามที่รับผิดชอบ |
| --- | --- | --- |
| [architecture-design.drawio.png](main/architecture-design.drawio.png) | [architecture-design.md](main/architecture-design.md) | Backend ร่วมงานกันอย่างไร: Controller → Dispatcher → Handler (Application use case) → Domain/ports → Infrastructure |
| [event-outbox-design.drawio.png](main/event-outbox-design.drawio.png) | [event-outbox-design.md](main/event-outbox-design.md) | Publication lifecycle เริ่มจาก checkout transaction; quarantine ต้องผ่าน operator review ก่อน controlled replay |
| [outbox-delivery-sequence.drawio.png](main/outbox-delivery-sequence.drawio.png) | [outbox-delivery-sequence.md](main/outbox-delivery-sequence.md) | Relay, PostgreSQL และ MongoDB ประสาน claim transaction → destination transaction → guarded ACK รวม replay/lease expiry |
| [order-lifecycle.drawio.png](main/order-lifecycle.drawio.png) | [order-lifecycle.md](main/order-lifecycle.md) | สถานะธุรกิจของ Order และ transition guards; เปลี่ยนชื่อจาก `system-design` และแยกจาก publication states |

Checkout สร้าง `WAIT_PAYMENT`, จอง stock/budget, บันทึกข้อมูลที่เกี่ยวข้องและ proposed outbox intent ใน PostgreSQL transaction เดียว เมื่อ commit จึงมี event `READY` ให้ relay ส่ง Payment success เป็นอีก event ภายหลัง การ replay ไม่เรียก checkout หรือจอง stock/budget ซ้ำ ทั้งหมดที่เป็น outbox ยังคง **PROPOSED / in-review** ต้องออกแบบและอนุมัติก่อน implementation

## Reference ตามเรื่อง

เก็บทุกภาพด้านล่างไว้เป็น reference ไม่ลบทิ้ง `repository-architecture` พักจากชุดนำเสนอ เพราะคำถามเรื่องตำแหน่ง source/tests ใช้ [project-structure.md](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/project-structure.md) เป็นคู่มือหลักได้ ส่วน architecture หลักรับผิดชอบการทำงานร่วมกัน

| กลุ่ม | ภาพ / คำอธิบาย |
| --- | --- |
| Source และ tests | [repository-architecture PNG](reference/repository/repository-architecture.drawio.png) · [คำอธิบาย](reference/repository/repository-architecture.md) |
| ธุรกิจและ checkout | [commerce-overview PNG](reference/business/commerce-overview.drawio.png) · [คำอธิบาย](reference/business/commerce-overview.md); [checkout-sequence PNG](reference/business/checkout-sequence.drawio.png) · [คำอธิบาย](reference/business/checkout-sequence.md) |
| Payment recovery | [start-payment-sequence PNG](reference/payment/start-payment-sequence.drawio.png) · [คำอธิบาย](reference/payment/start-payment-sequence.md); [payment-webhook-sequence PNG](reference/payment/payment-webhook-sequence.drawio.png) · [คำอธิบาย](reference/payment/payment-webhook-sequence.md); [refund-sequence PNG](reference/payment/refund-sequence.drawio.png) · [คำอธิบาย](reference/payment/refund-sequence.md) |
| MongoDB และ configuration | [mongodb-document-model PNG](reference/data/mongodb-document-model.drawio.png) · [คำอธิบาย](reference/data/mongodb-document-model.md); [config-publication-sequence PNG](reference/data/config-publication-sequence.drawio.png) · [คำอธิบาย](reference/data/config-publication-sequence.md) |
| Operations | [deployment-security PNG](reference/operations/deployment-security.drawio.png) · [คำอธิบาย](reference/operations/deployment-security.md); [observability-design PNG](reference/operations/observability-design.drawio.png) · [คำอธิบาย](reference/operations/observability-design.md); [recovery-design PNG](reference/operations/recovery-design.drawio.png) · [คำอธิบาย](reference/operations/recovery-design.md) |

ทุกภาพมี `.drawio` และ self-contained `.html` ชื่อเดียวกัน PNGฝังmodelที่เปิดแก้ไขได้ HTMLมีinlineSVG, accessible title/description และlocal horizontal scrollingเมื่อหน้าจอแคบ

เพิ่มตาม convention ของเจ้าของงาน: Domain Layer มีกล่องย่อย **`Domain`** สำหรับ business logic ที่ใช้ซ้ำ และ repository view แสดง **`src/Ecommerce.Domain/Authen/Domain/`** ใต้ Domain project กล่องใหม่เป็น `PROPOSED · OWNER REQUEST` เพราะยังไม่อยู่ใน pinned code ตัวอย่างคำนวณภาษีอธิบายชนิดงาน ไม่ใช่ความสามารถ Authen ที่ implement แล้ว อ่านหน้าที่และเหตุผลใน [Architecture](main/architecture-design.md) และ [Repository](reference/repository/repository-architecture.md)

## แหล่งหลักฐานและสถานะ

Backend baseline ถูกย้ายไป [e-commerce-backend](https://github.com/ittikornsopawan/e-commerce-backend/tree/d8255183cba54d0c2b218607456b895a70df32f0) ตาม [Project manifest บน main](https://github.com/ittikornsopawan/system-analysis-and-design/blob/main/e-commerce/REPOS.md) โดย pin `d8255183cba54d0c2b218607456b895a70df32f0` มีห้าproduction projects, สองtest projects, direct refs9+5, สี่command validatorsและห้าhandlers ส่วนGetCurrentUserไม่มีvalidator ภาพไม่อ้างว่าความสามารถcommerceหรือAuthen specใหม่ถูกimplementครบแล้ว

การทำงานครั้งนี้คง checkoutเดิมของbranchที่มีงานค้าง ไม่ย้าย/cloneทับโค้ดเก่า ใช้read-only remote tree/contentsเทียบpinned Component Repositoryและเปลี่ยนCODE source linksเป็นimmutableblob links จึงไม่ผูกdiagramกับlegacy source pathที่ถูกลบออกจากShowcaseบนmainใหม่

- `CODE`: ตรวจพบในcomponent baseline ไม่ใช่ผลbuild/runtimeของงานภาพนี้
- `SPEC`: พฤติกรรมcommerceอ้างอิง [API specs](../doc/api/) และSQL/schemaของโครงการ
- `PROPOSED`: Redis, MongoDB, operation intents/receipts, outbox, deploymentและoperating controlsที่ยังรอreview/approval

PostgreSQLยังเป็นbusiness/financial authority Redisเป็นpublic metadata cache/shared admission MongoDBเป็นnon-secret config sourceและaudit/event/derived status store ไม่มีtransactionร่วมPostgreSQL/MongoDB/Stripe และไม่มีcross-store exactly-once guarantee

Provider researchพบว่าSQLrollbackไม่ย้อนprovider success, unknown eventอาจต้องreconcile และaccepted/pending/partial refundไม่เท่ากับfull settled refund ภาพเสริมระบุsafe recoveryเป็นข้อเสนอ ไม่แก้canonical API/schemaหรือสร้างstateใหม่เงียบ ๆ

## Research และ policy records

- [Diagram semantics](design/diagram-semantics.md): ความหมาย, viewpoints, parent/child และสิ่งที่ห้ามสับสน
- [Diagram research เดิม](design/research.md): C4/Microsoft/W3C และbusiness lifecycle evidence; การจัดรูปแบบเดิมถูกแทนด้วยฉบับhierarchyนี้
- [Redis design](design/redis-design.md), [research](design/redis-research.md), [review](design/redis-review.md)
- [MongoDB design](design/mongodb-design.md), [research](design/mongodb-research.md)
- [Payment evidence](design/supporting-payments-research.md), [data/operations evidence](design/supporting-data-operations-research.md)

ค่าSLO/load/RPO/RTO/lease/retry/retentionและreplica countsเป็นcandidateที่อธิบายเหตุผล/ข้อแลกเปลี่ยนไว้ในcompanion ยังไม่ใช่production capacity, SLA, compliance certification หรือผลทดสอบสำเร็จ

## Source และการสร้างซ้ำ

`layered_core_content.py` กำหนดsoftware layers/package ownership; `layered_lifecycle_content.py` กำหนดguard/effect compartments; `layered_operations_content.py` กำหนดcapability/data/deployment/telemetry/activity views; `layered_sequence_content.py` จัดtime/activation/OPT/ALTและheader ownershipโดยใช้message contractsจาก `supporting_content.py`

`generate_layered_diagrams.py` เป็นentrypointปัจจุบัน ใช้paper `#f5f5f5`, ink `#2d3142`, accent `#bf4520` ตามที่เจ้าของงานเลือก Canvas A3แนวนอน1584×1120 พร้อมprinttype ramp ไม่ติดตั้งdependenciesหรือfontsเพิ่ม

```sh
python3 -B e-commerce/diagram/scripts/generate_layered_diagrams.py
python3 -B e-commerce/diagram/scripts/generate_layered_diagrams.py --check
```

ส่งออกด้วยdraw.io Desktopที่ติดตั้งอยู่ ตัวอย่างหนึ่งไฟล์ (ทำกับทุกslugในสารบัญ):

```sh
/Applications/draw.io.app/Contents/MacOS/draw.io \
  -x -f png --embed-diagram --size page -s 1.5 --theme light \
  --disable-update --timeout 45 \
  -o e-commerce/diagram/main/architecture-design.drawio.png \
  e-commerce/diagram/main/architecture-design.drawio

python3 -B e-commerce/diagram/scripts/generate_layered_diagrams.py --finalize-pngs
```

draw.io Desktop32.6.10มีpage frameหนึ่งpixelก่อนscale ผลscale1.5คือ2378×1682 Native PNGเก็บcompressed `mxGraphModel` metadata; finalizerตรวจว่าตรงXMLsourceและเพิ่มcompressed compatible `mxfile` key โดยไม่เปลี่ยนIDAT pixels ไม่cropหรือraster-resampleหลังexport Native outputใช้Georgia/Arial/Courier New fallbacks; HTMLยังประกาศInstrument Serif/Geist/Geist Mono web stacks Python PNGhelperของskillไม่มีPlaywright จึงใช้native rendererและตรวจผลจริง

ดู [ผลตรวจ handoff ชุดหลัก 4 ภาพ](design/handoff-verification.md) และ [ผลตรวจเดิมทั้ง15ภาพ](design/verification.md) สำหรับผลที่รันจริง, native hierarchy counts, PNG sizes และข้อจำกัด

## เกณฑ์ตรวจฉบับ hierarchy

ตรวจsource/geometry/text capacity, nativecellIDsไม่ซ้ำ, parent references/child relative coordinates, intended Application sublayers, source/XML parity และPNG extraction ตรวจภาพจริงทุกไฟล์และเปิดPNG/exportซ้ำเทียบIDAT อีกครั้ง HTMLต้องผ่านpackaged self-checkและทดสอบ390pxโดยไม่ทำให้ทั้งหน้าoverflow

State compartmentsไม่ถูกนับเป็นpersisted states; participant-header decompositionไม่ถูกนับเป็นservices/lifelinesเพิ่ม; document referencesไม่ถูกนับเป็นSQLforeign keys; recovery checkpointsไม่ใช่order states ขนาดไฟล์PNGเป็นประเด็นpackaging แก้จากexport/sourceได้โดยไม่ตัดองค์ประกอบสำคัญ

งานนี้ไม่มีbackend/API/schema implementation, package installation, provider calls หรือruntime/load/failover/restore tests การอนุมัติdesignและdownstream verificationยังต้องทำตามSDDก่อนimplementation เจ้าของงานสั่งเปิดPRสำหรับชุดที่เสร็จแล้วภายหลัง ใช้สถานะGit/GitHubสำหรับการส่งงาน; คำสั่งส่งPRไม่เปลี่ยนสถานะอนุมัตินโยบาย
