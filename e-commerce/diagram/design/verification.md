---
name: E-commerce Diagram Hierarchy Verification
description: ผลตรวจ diagram ฉบับ hierarchy ทั้ง15ภาพ วันที่2026-11-08 พร้อมขอบเขตหลักฐานและสิ่งที่ยังไม่ได้ทดสอบ อ่านก่อนรับงานหรือสร้างภาพซ้ำ
---

# ผลตรวจฉบับ hierarchy — 2026-11-08

แก้ทั้งสามภาพเดิมและสิบสองภาพเสริมตามข้อทักท้วงเรื่องความหมายและกล่องซ้อน ใช้ skill `diagram-design` กับ style light/orange ที่เจ้าของงานเลือก [สารบัญ](../README.md) แสดง PNG และคำอธิบายทุกภาพ [semantic contract](diagram-semantics.md) แยกคำถาม, notation, parent/child และความหมายของเส้นก่อนจัดภาพ

## Source และความหมาย

ตรวจ code facts จาก Component Repository `e-commerce-backend` ที่ pin `d8255183cba54d0c2b218607456b895a70df32f0` ตาม Project manifest บน Showcase `origin/main` ที่ตรวจถึง `90c589a` โดยอ่าน remote tree/contents แบบ read-only ไม่ย้ายหรือเขียนทับ legacy checkout ของ branch ที่มีงานค้าง Direct project refs มี9 production +5 test; Authenมี4commands/1query, 4command validators และ5handlers โดย GetCurrentUserไม่มีvalidator

Applicationแยก Command/Query, Validator, Handler, Mapping และ Ports เป็น native children ภายใต้ layer Dispatcherเป็นSharedและเรียกValidatorก่อนHandler Repositoryแยกsrc/tests/projectsและFeatures/Authenจริง กล่องสรุปfile rolesไม่ใช่โฟลเดอร์ที่สร้างขึ้นใหม่ State guards/effectsไม่ใช่persisted statesเพิ่ม Sequence header childrenแสดงownershipและไม่นับเป็นlifelinesเพิ่ม Document referencesไม่ใช่SQLforeign keys Recoveryใช้กิจกรรมและdecision gates

ตรวจเชิงsemanticแยกจากgeometryแล้วแก้ปัญหาduplicate nativeID, dispatcher-call ownership, รายละเอียดข้อความsequence, role-parentของfeature, ทิศทางtelemetry, เงื่อนไขrecovery gates และcheckout admission fragment ก่อนส่งออกชุดสุดท้าย

## ผลตรวจที่รันจริง

- `generate_layered_diagrams.py --check`: PASS ทั้ง15ภาพ Sourceตรงrenderer, grid/frame/containment/text capacity/orthogonal routesผ่าน Structural viewsมีnativeparent/childจริง ทุกcellIDไม่ซ้ำและparentอ้างถึงcellที่มีอยู่
- Packaged `self_check.py`: PASS ทั้ง15HTML AccessibleSVG, title/description, single-file contractและviewBoxผ่าน
- Packaged `export_svg.py`: PASS ทั้ง15ภาพ โดยส่งSVGไปtemporary QA directory
- Browser QAที่390×844: ทั้ง15ภาพมีSVG1584pxในlocalhorizontal scroller ไม่มีwhole-page overflowและไม่พบข้อความล้นกรอบ ตรวจหกsequenceซ้ำหลังแก้ข้อความ/fragment; การแก้legendสุดท้ายของconfigตรวจnativePNGและself-checkซ้ำ
- NativePNG2378×1682ทุกภาพ ส่งออกด้วยdraw.io Desktop32.6.10ที่scale1.5 ทุกไฟล์ต่ำกว่า1MiB รายละเอียดขนาดตามตาราง
- CRC/embeddedsourceตรวจผ่าน Packaged `drawio_extract.py --json` ให้IRจากPNGตรงกับ`.drawio` และfinalizerเพิ่มcompatiblecompressedmetadataโดยไม่เปลี่ยนIDAT
- เปิดPNGทั้ง15กลับในdraw.ioแล้วexportใหม่ไปtemporary QA directory: IDATเหมือนเดิมทุกbyte และnativeembeddedXMLหลังroundtripตรงsourceทุกภาพ
- ตรวจภาพPNGจริงทั้ง15ไฟล์ การทบทวนโครงสร้างและการอ่านภาพมีทั้งprimaryagentและfocusedreviewstreams แก้ผลที่พบแล้ว; ไม่ใช้sourcevalidationแทนvisualreview
- YAMLfrontmatterตรวจด้วยRubyPsych และlocalMarkdownlinksตรวจเทียบfilesystem; `git diff --check`และassignment-scopeตรวจผ่าน ไม่ติดตั้งdependency/fontเพิ่ม

| ภาพ | Native containers | ความลึกparentสูงสุด¹ | รายละเอียดหลัก | PNG bytes |
| --- | ---: | ---: | --- | ---: |
| `architecture-design` | 7 | 3 | 24 child responsibilities | 859,217 |
| `repository-architecture` | 13 | 5 | 21 child responsibilities | 724,303 |
| `system-design` | 7 | 2 | 15 child responsibilities | 550,086 |
| `event-outbox-design` | 6 | 2 | 13 child responsibilities | 466,966 |
| `commerce-overview` | 6 | 3 | 13 child responsibilities | 445,420 |
| `mongodb-document-model` | 7 | 3 | 15 child responsibilities | 509,872 |
| `deployment-security` | 10 | 4 | 6 child responsibilities | 402,431 |
| `observability-design` | 7 | 3 | 11 child responsibilities | 512,193 |
| `recovery-design` | 4 | 2 | 9 child responsibilities | 394,856 |
| `checkout-sequence` | 14 | 4 | 10 messages / 5 lifelines | 470,963 |
| `start-payment-sequence` | 12 | 4 | 10 messages / 4 lifelines | 460,227 |
| `payment-webhook-sequence` | 12 | 4 | 10 messages / 4 lifelines | 473,724 |
| `refund-sequence` | 12 | 4 | 10 messages / 4 lifelines | 472,079 |
| `outbox-delivery-sequence` | 7 | 3 | 8 messages / 3 lifelines | 406,774 |
| `config-publication-sequence` | 13 | 4 | 9 messages / 5 lifelines | 441,362 |

¹ นับrootlayerเป็นระดับแรก ความลึกนี้ยืนยันeditablehierarchy ไม่ใช่จำนวนsoftwarelayersหรือservices

## ขอบเขตผลตรวจ

ไม่มีbackend/API/schema implementation, MongoDBcollection/index provisioning, providercalls หรือruntime/load/concurrency/failover/restore tests ค่าSLO/load/RPO/RTO/lease/retry/retentionและreplica countเป็นcandidateในเอกสาร`in-review` ไม่มีผลproductionวัดจริงและยังต้องอนุมัติก่อนimplementation

PNGใช้nativeGeorgia/Arial/CourierNewfallbacksที่เปิดเผยในREADME HTMLคงwebfontstacksของstyle ไม่มีPythonPlaywrightสำหรับskillPNGhelperจึงใช้nativeexportและตรวจภาพจริงแทน แหล่งSQL/APIยังเป็นcanonicalspecs; safe provider recovery, durableintent/receipt, outboxและMongo/Redispoliciesที่ขยายไว้เป็นPROPOSED

งานอยู่ในmanagedJinnycloneบนbranch`docs/jinny-architecture-details` เฉพาะ`e-commerce/diagram`, `tasks/todo.md`, `tasks/lessons.md` ช่วงสร้างและตรวจภาพไม่มีcommit/push/PR; ภายหลังเจ้าของงานสั่งส่งชุดนี้ด้วยcommit-and-pr Previewserver/tabและviewportoverrideที่สร้างเพื่อตรวจถูกปิดแล้ว Editing-sessionlockปล่อยเมื่อจบhandoffตามagent-workspace; assignmentและbranchคงไว้ตามPR lifecycle; สถานะการส่งงานตรวจจากGit/GitHub

## Owner refinement: `Domain` สำหรับ business logic ที่ใช้ซ้ำ

วันที่ 2026-11-08 เพิ่ม native child `a-business` ชื่อ `Domain` ใต้ `a-domain` และ `r-business` ชื่อ `Authen/Domain/` ใต้ `r-domain` แก้เฉพาะ Architecture/Repository และเอกสารที่อธิบายโครงสร้างนั้น ตรวจ remote tree ที่ pinned revision ซ้ำแล้ว path ใหม่นี้ยังไม่มีโค้ด จึงระบุ `PROPOSED · OWNER REQUEST` ตัวอย่างภาษีไม่ได้เป็นการเพิ่ม tax capability ให้ Authen

ตรวจซ้ำจริง: source/geometry check ทั้ง15, packaged HTML/SVG checks สำหรับสองภาพที่แก้, browser390pxไม่มีpage/text overflow และparentที่แสดงตรงDomain project/layer, nativePNG reviewพร้อมเพิ่มbottompadding, exact embeddedsource/IR และnative PNG reopening/export roundtripผ่านทั้งสองภาพ ภาพยัง2378×1682และต่ำกว่า1MiB เปรียบเทียบSHA-256กับก่อนเริ่ม refinement แล้ว artifactทั้ง52ไฟล์ของอีก13viewsไม่เปลี่ยน เอกสารcompanionระบุHandler orchestration, reusable rules และentity invariantsแยกกัน ไม่มีbackendcode, class, project reference, taxformula, API หรือschemaเปลี่ยน

## PR delivery authorization

คำสั่งล่าสุดของ Ittikorn "เปิด pr มา" อนุญาตส่งชุด diagram ที่ตรวจเสร็จแล้ว รวม Domain refinement ใช้ branch และ scope เดิม โดยเปลี่ยน delivery grant ของ assignment จาก none เป็น open-pr หลังตรวจตัวตน/registry ไม่มีการขยาย scope หรืออนุมานสิทธิ์ merge รายการในขั้น authoring ที่ระบุว่ายังไม่มี PR เป็นหลักฐานของช่วงเวลานั้น ไม่ใช่สถานะการส่งงานปัจจุบัน
