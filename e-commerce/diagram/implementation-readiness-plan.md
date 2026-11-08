---
name: E-commerce Supporting Design Plan
description: แผนและสารบัญชุด diagram เสริมพร้อมเหตุผลและเกณฑ์ตรวจ ใช้ทบทวนขอบเขตและข้อเสนอสำหรับเตรียมพัฒนาระบบหลังชุดภาพหลัก
status: in-review
approved_by: null
approved_at: null
---

# แผนชุดภาพเสริมสำหรับเตรียมพัฒนาระบบ

เจ้าของงานสั่งให้ทำทุกหัวข้อที่ขาดในรูปแบบเดียวกับภาพหลัก: `.drawio.png` ที่เปิดแก้ไขได้ พร้อม `.drawio`, `.html` และ `.md` อธิบายภาษาไทย วันที่ 2026-11-07 หลัง PR #48 merge แล้ว งานนี้สร้าง design artifacts เท่านั้น ไม่สร้าง endpoint, MongoDB collection, SQL migration หรือ backend worker จริง

## ลำดับงานและผลลัพธ์

ทุกภาพใช้ light paper/ink/orange ตามชุดเดิม ขนาด A3 แนวนอน 1584 × 1120; PNG ส่งออก native scale 1.5 พร้อม compressed editable metadata และตรวจขนาดไม่เกิน 1 MiB หลังข้อทักท้วง 2026-11-08 จะตรวจและปรับรวม 15 ภาพ (สามภาพหลัก +สิบสองภาพเสริม) โดยเลือก notation ตามความหมายและใช้ native containment สำหรับ hierarchy ไม่บีบส่วนประกอบสำคัญให้เหลือรายการข้อความเพื่อผ่านงบจำนวนกล่องเดิม

| ลำดับ | ชื่อไฟล์หลัก (มีทั้ง `.drawio.png` และ `.md`) | ประเภท / คำถามที่ตอบ |
| --- | --- | --- |
| หลัก 1 | architecture-design | Logical component/layer / Backend → Presentation, Application, Domain, Infrastructure, Shared → responsibility children |
| หลัก 2 | repository-architecture | Native package containment / project → folders/responsibilities พร้อม compile references ที่แยกความหมาย |
| หลัก 3 | system-design | Order state machine / state parents แยก guard/effect compartments ไม่ใช่ software layers |
| 1 | commerce-overview | Capability ownership / business context → capabilities ไม่ใช่บังคับ login-to-review journey |
| 2 | checkout-sequence | Sequence / จอง stock/budget และ commit order กับ publication intent อย่างไร |
| 3 | start-payment-sequence | Sequence / ติดต่อ provider ด้วย stable operation identity และรับมือผลไม่แน่นอนอย่างไร |
| 4 | payment-webhook-sequence | Sequence / ตรวจ signature/guards ก่อนบันทึกผล และรับมือ orphan/duplicate event อย่างไร |
| 5 | refund-sequence | Sequence / แยกคำขอคืนเงินออกจากผลคืนเงินที่ยืนยันแล้ว เพื่อไม่คืน stock ผิดเวลาอย่างไร |
| 6 | outbox-delivery-sequence | Sequence / Claim, destination transaction, acknowledgement และ replay ปลอดภัยอย่างไร |
| 7 | config-publication-sequence | Sequence / Validate/CAS/publish config และกระจาย snapshot โดยไม่ reset quota อย่างไร |
| 8 | event-outbox-design | State Machine / Publication record อยู่สถานะใด มี lease/retry/quarantine และ event contract แบบใด |
| 9 | mongodb-document-model | ER logical model / Current config, revisions, audit, integration events และ transaction projections เกี่ยวข้องกันอย่างไร |
| 10 | deployment-security | Deployment / Candidate placement, replicas, artifacts, network paths และ identity ของ API/workers/data stores |
| 11 | observability-design | Data Flow / รวม signals, วัด SLO, ทดสอบ capacity และแจ้งเหตุให้ใครอย่างไร |
| 12 | recovery-design | Activity / Swimlane / owner lanes, actions, decision gates และ rework สำหรับ restore/reconcile/rebuild/reopen |

## หลักการตัดสินใจ

แยก `CODE`, `SPEC` และ `PROPOSED` เสมอ ข้อกำหนด commerce เป็นหลักฐานของ behavior ที่ออกแบบไว้ ไม่ใช่ข้ออ้างว่า backend ทำครบแล้ว เมื่อพบ provider semantics ที่ specification ปัจจุบันยังไม่ครอบคลุม จะระบุช่องว่างและวาด safe recovery เป็น `PROPOSED` ไม่แก้ canonical contract เงียบ ๆ

PostgreSQL เป็น business/financial authority, Redis เป็น cache/admission และ MongoDB เป็นแหล่ง non-secret config กับ audit/event/derived transaction documents ตามบทบาทที่เจ้าของงานเลือก เอกสารใหม่นี้ขยายเหตุผลและข้อเสนอ ไม่อนุมัติ detailed policies แทนเจ้าของงาน

## หลักฐานและเกณฑ์ตรวจ

ใช้ project specs/code ปัจจุบันร่วมกับเอกสาร Stripe, PostgreSQL, MongoDB, Redis และ reliability guidance จากผู้ให้บริการโดยตรง ภาพ sequence เป็น coordination/transaction-boundary views; SQL และ activation รายตารางยังอยู่ใน canonical API `sequence.wsd` ที่ลิงก์จากคำอธิบาย ไม่ใช้ภาพใหม่แทนสัญญา API เหล่านั้น

ตรวจทุกภาพด้วย geometry/text bounds, packaged HTML self-check, native render review, exact editable-source extraction และเปิด PNG/export ซ้ำ ตรวจ `.md` frontmatter/links และตรวจทั้งชุดว่าบทบาท authority, event identity, epoch/version, retention และ failure behavior ไม่ขัดกัน เกณฑ์ทดสอบ runtime ระบุเป็นสิ่งที่ต้องพิสูจน์ภายหลัง ไม่รายงานเป็นผลผ่านของงานวาดภาพ

## ข้อเสนอที่ต้องตรวจรับก่อน implementation

Deployment counts, SLO/load profile, RPO/RTO, backup/retention, outbox lease/retry/queue budgets, recovery epoch และ provider reconciliation เป็นข้อเสนอที่ต้องอนุมัติและทดสอบ Endpoint/schema changes ที่ตามมาต้องผ่าน SDD/data-modeling/API workflow ก่อนลงมือจริง งานภาพเสร็จได้เมื่อข้อเสนอครบและตรวจสอบได้ โดยไม่จำเป็นต้องอ้างว่า policy เหล่านี้ได้รับอนุมัติแล้ว

## การแก้ไขหลังเจ้าของงานทักท้วง 2026-11-08

อ่าน [diagram-semantics.md](diagram-semantics.md) ก่อนดู layout: แต่ละชนิดมีคำถาม ระดับ abstraction และความหมายของลูกศรต่างกัน Architecture ใช้ layer/component decomposition, Repository ใช้ package ownership, Sequence ใช้ lifelines/time/activation, State ใช้ guard/effect, Document model ใช้ identity/fields/cardinality, Deployment ใช้ environment/zone/host/artifact, Observability ใช้ signal pipelines และ Recovery ใช้กิจกรรมตามผู้รับผิดชอบ Application ใน structural views ต้องมี Command/Query, Validator และ Handler เป็นกล่องย่อยจริง ส่วน Dispatcher ยังคงเป็น Shared และ GetCurrentUser ไม่มี validator file ตาม code ปัจจุบัน

Source หลักสำหรับสร้างภาพฉบับนี้คือ `layered_core_content.py`, `layered_lifecycle_content.py`, `layered_operations_content.py`, `layered_sequence_content.py` และ `generate_layered_diagrams.py` เดิม `supporting_content.py` เก็บ message contracts ที่ถูกนำมาจัด notation ใหม่ ไม่มีการเปลี่ยน business semantics จากการจัดกล่อง

## Owner refinement: reusable Domain business logic — 2026-11-08

เพิ่ม `Domain` เป็น responsibility child ภายใน Domain Layer และ `Authen/Domain/` เป็น path child ภายใต้ `Ecommerce.Domain/` เฉพาะสอง structural views คงความหมายของอีก13ภาพเดิม Handlerประสานงาน; Domainย่อยเก็บกฎใช้ซ้ำ; entity/value objectคงinvariantของตัวเอง การคำนวณภาษีเป็นเพียงตัวอย่าง โดยกฎอยู่ในfeatureเจ้าของงาน ไม่ถือว่ามีtaxcodeในAuthen งานนี้แก้ภาพและคำอธิบาย ไม่มีbackend/API/schema implementation โครงสร้างจากเจ้าของงานแยกป้ายจากCODEที่pinไว้
