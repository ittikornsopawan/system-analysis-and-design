---
name: E-commerce MongoDB Logical Collection Model
description: อธิบาย ownership ของ collection, identity/payload/integrity compartments และ logical cardinality ของ MongoDB ใช้ก่อนทบทวนแบบจำลองหรือออกแบบ schema จริง
status: in-review
approved_by: null
approved_at: null
---

# แบบจำลอง collection และ logical references

ภาพนี้ตอบว่า **เอกสารแต่ละชนิดเก็บอะไร ระบุตัวตนอย่างไร และอ้างถึงกันแบบใด** ใช้ ER/document notation เส้นไม่มีหัวลูกศรและมี cardinality จึงไม่ใช่ลำดับ publish หรือ delivery และไม่อ้างว่า MongoDB บังคับ foreign key เหมือน PostgreSQL

## โครงสร้างที่เห็นในภาพ

ระดับบนมีสอง owner groups; แต่ละ collection เป็น container จริงและมี compartment ลูก `Identity`, `Payload`, `Integrity` ที่แก้ไขแยกกันได้ ไม่ใช้ field list ยาวแทน decomposition

| กลุ่ม / collection | Identity | Payload และ integrity สำคัญ |
| --- | --- | --- |
| Configuration authority / `runtime_config_current` | environment + canonical scope + key | typed value, schemaVersion, revision; unique logical identity และ compare-and-set |
| Configuration authority / `runtime_config_revisions` | config identity + revision | immutable published value, actor/time, rollback provenance; rollback สร้าง revision ใหม่ |
| Shared audit / `application_audit_events` | eventId; configRef หรือ sourceRef | allowlisted action evidence; restricted append; ไม่ใช่ financial ledger |
| Delivery evidence / `integration_events` | stable eventId + payloadHash; sourceEpoch และ aggregate identity/version | event envelope และ full allowed snapshot; duplicate ตรวจ hash; conflict เข้า quarantine |
| Derived status / `transaction_status_projections` | sourceEpoch + aggregateType + aggregateId | sourceVersion, status และ allowed references; newer full snapshot เท่านั้น |

กลุ่มบนรวม audit เพื่อแสดง config transaction แต่ label ระบุชัดว่า audit ใช้กับ business events ได้ด้วย ไม่ได้ยก audit ให้เป็น configuration authority เส้น current `1` ↔ revisions `N`, revision `1` ↔ related audit `0..N` และ integration events `N` ↔ current projection `0..1` เป็น logical associations ตาม aggregate ที่เกี่ยวข้อง ไม่มี cross-store foreign key

## ขอบเขต atomicity

Local transaction A ใน MongoDB รวม current value + revision + related publication audit ส่วน local transaction B รวม event marker + conditional projection + related business audit ทั้งสองต้องใช้ topology ที่รองรับ transaction และ explicit majority outcome; ไม่มี PostgreSQL/MongoDB transaction ร่วมกัน

`aggregateVersion` ของ event map เป็น `sourceVersion` ของ projection; schemaVersion, config revision และ sourceEpoch เป็นคนละมิติ ตัวอย่าง field และ candidate index อยู่ใน [MongoDB design](mongodb-design.md) และ [operations research](supporting-data-operations-research.md) ภาพไม่สร้าง collection, validator หรือ index จริง

## ความล้มเหลวและการกู้คืน

- Marker ที่ commit ก่อน effect อาจกด replay จน projection หายถาวร จึงต้อง commit ร่วมกัน
- Same eventId/same hash คือ replay; same ID/different hash เป็น integrity conflict ไม่ใช่ duplicate success
- Old sourceVersion อาจเก็บเป็นประวัติได้ แต่ห้ามย้อน current projection; current snapshot ไม่ใช่ event history ครบถ้วน
- หลัง SQL restore ข้อมูล MongoDB อาจอยู่ timeline อนาคต ต้อง fence old workers และ rebuild ด้วย externally controlled `sourceEpoch` ใหม่ ห้ามแก้ epoch/hash ใต้ eventId เดิม
- Audit history ที่หายไม่สามารถสร้าง actors หรือ intermediate transitions จาก current snapshot ได้ ต้องมี backup และรายงาน gap ตามจริง
- ยังไม่มี automatic TTL; finite retention, replay horizon และ storage budget ต้องอนุมัติแยก ไม่ได้สัญญาว่าเก็บตลอดไปฟรี

## เหตุผลและข้อแลกเปลี่ยน

การแยก current config ออกจาก immutable revisions ทำให้ current read สั้นและ rollback provenance ชัด แต่เพิ่ม write amplification และ index/backup responsibilities การใช้ local transaction ป้องกัน partial destination effect แต่ยังต้องรับ at-least-once delivery, ambiguous commit และ out-of-order events ไม่มี exactly-once cross-store guarantee

Read projection จำกัด platform operational/admin ตาม live authorization และ allowlisted fields ไม่มี customer address, card data, credentials, private margins หรือ raw webhook body การเพิ่มรายละเอียดต้องผ่าน contract/data review แยก

## แหล่งข้อมูลและสถานะ

- [MongoDB proposal](mongodb-design.md), [supporting data operations research](supporting-data-operations-research.md)
- [Configuration publication](config-publication-sequence.md), [outbox delivery](outbox-delivery-sequence.md), [recovery activity](recovery-design.md)
- [MongoDB transactions](https://www.mongodb.com/docs/manual/core/transactions/), [unique indexes](https://www.mongodb.com/docs/manual/core/index-unique/), [schema validation](https://www.mongodb.com/docs/manual/core/schema-validation/)

แบบจำลองยัง `in-review` ไม่มี schema หรือ backend เปลี่ยนแปลง การตรวจเอกสารไม่ใช่ runtime, capacity, failover, restore หรือ security proof
