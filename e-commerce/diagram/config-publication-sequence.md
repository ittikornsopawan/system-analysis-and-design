---
name: E-commerce Configuration Publication Sequence
description: อธิบาย authorization, revision CAS, local transaction และการกระจาย validated config snapshot ใช้ทบทวนก่อนออกแบบ API และ publisher จริง
status: in-review
approved_by: null
approved_at: null
---

# Config publication: validate, version & activate

ภาพนี้แยก “มีสิทธิ์เผยแพร่”, “บันทึก revision สำเร็จ” และ “fleet เริ่มใช้นโยบาย” ออกจากกัน เพื่อไม่ให้ config update กลายเป็นการ reset quota โดยไม่ตั้งใจ
ทั้งหมดเป็น **PROPOSED**; MongoDB เป็น authority ของ non-secret configuration ตามทิศทางที่เลือก แต่ detailed behavior ยังรออนุมัติ
PostgreSQL ยังคงเป็น permission authority; feature flag หรือ config document ไม่ให้สิทธิ์ผู้เผยแพร่ตนเอง

[ภาพ PNG](config-publication-sequence.drawio.png) · [ไฟล์แก้ไข](config-publication-sequence.drawio) · [HTML](config-publication-sequence.html)

## Actors และขอบเขต

| ID ใน model | Actor / คำกำกับ | หน้าที่ |
| --- | --- | --- |
| `admin` | Platform admin / LIVE AUTHORIZATION | ส่ง typed config พร้อม expectedRevision |
| `api` | Config publisher / PROPOSED VALIDATION | Validate, authorize, CAS, จัดการผลไม่แน่นอน |
| `sql` | PostgreSQL / PERMISSION AUTHORITY | ตรวจ PLATFORM_ADMIN ปัจจุบัน |
| `mongo` | MongoDB / CONFIG LOCAL TX | Commit current, immutable revision และ audit |
| `instances` | API instances / VALIDATED SNAPSHOTS | Reconcile revision และใช้ immutable last-known-good |

SQL authorization เป็นการตรวจแยกจาก MongoDB local transaction ไม่มี distributed transaction ที่ล็อก permission ทั้งสอง store ร่วมกัน
หากต้องการ immediate revocation semantics ระหว่าง check กับ publish ต้องออกแบบและอนุมัติกฎ race โดยเฉพาะ; ภาพนี้ไม่อ้างว่า check ครั้งเดียวขจัด race นั้น
Configuration credentials/URIs/bootstrap secrets ต้องอยู่ใน secret management ไม่ใช่ดึงจาก MongoDB ที่ต้องใช้ secret เดียวกันเพื่อเริ่มเชื่อมต่อ

## Messages ที่ตรงกับภาพ

| ลำดับ | จาก → ถึง | Label | ความหมาย |
| --- | --- | --- | --- |
| 1 | `admin` → `api` | PUBLISH | Typed config + expectedRevision; no secrets/scripts |
| 2 | `api` → `sql` | AUTHORIZE | Current PLATFORM_ADMIN permission |
| 3 | `sql` → `api` | PERMITTED | Config cannot grant itself authorization |
| 4 | `api` → `mongo` | CAS + PUBLISH | Current + revision + audit in MongoDB transaction |
| 5 | `mongo` → `api` | REVISION | Majority outcome; reload on ambiguity |
| 6 | `api` → `admin` | PUBLISHED | Return confirmed published revision |
| 7 | `mongo` → `instances` | REFRESH HINT | Change stream is a hint; resume can expire |
| 8 | `instances` → `mongo` | RECONCILE | Poll revision; full validated reload if needed |
| 9 | `mongo` → `instances` | SNAPSHOT | Immutable LKG + age; controlled fleet activation |

Model นี้ไม่มี ALT fragment; message table แสดง successful publication และ asynchronous refresh responsibilities
Permission denial, CAS conflict, validation rejection และ ambiguous commit เป็นทางเลือกที่หยุด/ตรวจผล ไม่ใช่ข้อความทั้งหมดที่ต้องเกิดตาม PUBLISHED
REFRESH HINT ไม่ใช่หลักฐานว่า instance ทุกตัวได้รับหรือเปิดใช้ revision แล้ว และไม่ใช่ durable audit history
การ poll/full reload ยังจำเป็นเมื่อ change-stream resume token ใช้ไม่ได้หรือ notification สูญหาย

## Current, revision และ audit ต้อง commit ร่วมกัน

ใน MongoDB transaction เดียว publisher ต้อง match current expectedRevision, สร้าง revision ถัดไป และ append related audit
หาก CAS match ไม่ได้ต้องยกเลิก transaction ทั้งชุด ไม่เขียน audit ว่า publish สำเร็จหรือสร้าง orphan revision
Rollback เป็นการ publish revision ใหม่ที่อ้าง rollbackFromRevision ไม่แก้ current/history ย้อนเงียบ ๆ
Transaction ต้องใช้ supported replica set/sharded deployment; standalone ไม่รองรับ multi-document transaction นี้
ใช้ explicit majority write concern พร้อม journaling setting ที่ตรวจแล้ว; ไม่อาศัย default ที่อาจต่างกันตาม deployment
Write-concern timeout หรือ lost reply ไม่ยืนยันว่า MongoDB ไม่บันทึก ต้อง reload โดย stable publication identity/revision/hash ก่อนตัดสินใจ retry
Publication request identity และ response/error envelope ยังต้องออกแบบใน API contract ภายหลัง; ภาพนี้ไม่กำหนด HTTP/bizCode ใหม่

## ตัวอย่าง document สำหรับทบทวน

ตัวอย่างเป็น conceptual shape ใช้ ID สมมติ; ไม่ใช่คำสั่งสร้าง collection หรือ final JSON contract

```json
{
  "environment": "demo", "scopeType": "platform", "scopeId": "platform",
  "key": "publicMetadataCache", "schemaVersion": 1, "revision": 12,
  "effectiveAt": "2026-11-07T00:00:00Z", "publishedBy": "actor_demo_001",
  "value": { "enabled": true, "maxTtlSeconds": 60 },
  "publicationId": "pub_demo_012", "payloadHash": "sha256:<demo>"
}
```

Immutable revision เก็บ identity เดียวกัน + revision พร้อม publishedAt/actorId/rollbackFromRevision เมื่อเกี่ยวข้อง
Audit event อ้าง configRef/publicationId และ action ที่ allowlist; ไม่เก็บ credentials, raw request หรือข้อมูลส่วนบุคคลที่ไม่จำเป็น
`schemaVersion` คือรูปแบบข้อมูล; `revision` คือเนื้อหา config; Redis policy version และ counter epoch เป็นคนละค่า

## Conceptual validation และ index candidates

| กฎ | เหตุผล / ผลเมื่อไม่ผ่าน |
| --- | --- |
| Canonical environment + scopeType + scopeId + key | ไม่มี null scope ที่ทำให้ unique identity กำกวม |
| Typed value + schemaVersion ที่รองรับ | ป้องกัน scripts/expressions/Redis commands จาก config |
| TTL/quota/refill/failure enum อยู่ใน approved bounds | Config ไม่ขยายอำนาจเกิน policy ที่อนุมัติ |
| expectedRevision ตรงกับ current | ป้องกันผู้แก้สองคน overwrite กัน |
| Actor จาก authenticated context | ไม่รับ publishedBy ที่ client ปลอมเอง |
| Payload hash ตรง immutable publication | Same publication ID ต่าง content ต้อง conflict/investigate |
| Scope เริ่ม platform/environment เท่านั้น | Shop overrides/pricing rules อยู่นอกขอบเขตนี้ |

| Query shape | Candidate index |
| --- | --- |
| Read current key ใน environment/scope | Unique environment + scopeType + scopeId + key |
| Fetch revision ที่ระบุ | Unique logical config identity + revision |
| List history ตามเวลาและ ID | Config identity + publishedAt + stable revision/event ID |
| Reconcile publication outcome | Stable publication identity ที่ unique; shape ต้องตกลงใน downstream model |
| Audit investigation | Config reference + occurredAt + eventId ตาม actual filter |

Field order ต้องตรวจด้วย query/explain จริงและข้อมูลตัวอย่าง; ไม่มี physical index provisioning หรือ migration ในงานนี้

## Snapshot, LKG และ controlled activation

| Proposal | ค่าเสนอที่ยังไม่ทดสอบ | พฤติกรรม |
| --- | --- | --- |
| Revision reconciliation | ทุก 30 วินาที | Poll เสริม change-stream hints; full reload เมื่อ resume window หาย |
| Last-known-good allowance | ไม่เกิน 5 นาทีระหว่าง MongoDB outage | ใช้เฉพาะ bundle ที่ผ่าน validation แล้ว พร้อม revision/age |
| Unknown/stale flags | Off เมื่อเกิน allowance | ห้าม config ที่ไม่เคยตรวจกลายเป็น permissive default |
| Public cache เมื่อ config ไม่น่าเชื่อถือ | Bypass | Public read ใช้ approved local degraded admission |
| Protected policy ที่ระบุไม่ได้ | Unavailable | ไม่คิด sensitive quota/failure policy ที่ permissive เอง |
| Signed webhook / SQL expiry | ทำงานตาม existing verified contract | Host readiness ไม่ผูกทุก route กับ MongoDB โดยไม่มีเงื่อนไข |

Cold start ต้องมี last-approved deployment bundle หรือ valid MongoDB snapshot; ยังต้องมี secrets และ valid authorization
Instance โหลดและ validate bundle ทั้งชุดแล้วสลับ immutable snapshot ไม่ให้ request เห็นครึ่ง revision
Publication กับ activation เป็นคนละเหตุการณ์: rate policy ต้อง rollout approved active policy version ให้สอดคล้องกันทั้ง fleet
Banner/flag/TTL update ไม่ reset bucket epoch; explicit quota reset ต้องมี approval/audit แยก
Readiness/health ต้องบอก per-role degraded state ไม่รายงานทั้ง host พร้อมทั้งที่ protected paths ไม่มี policy

## Retention, recovery และ tradeoffs

Current document ทำให้ read ง่าย แต่ audit/revisions เพิ่ม storage/write cost และต้องมี finite retention/archive/deletion policy ที่อนุมัติ
ยังไม่ใช้ automatic TTL; delayed TTL cleanup ไม่ใช่ deletion deadline หรือข้ออ้างเก็บประวัติตลอดไป
Backup ต้องครอบคลุม current/revisions/audit และ validation/index metadata ตาม restore strategy
Restore configuration แยกจาก SQL-derived projection recovery; revision สูงสุดที่พบไม่ใช่หลักฐานว่าควร activate ทันที
ตรวจ authorization, integrity, approved policy version และ fleet consistency ก่อนเปิด protected functions
Current value เพียงตัวเดียวสร้างประวัติผู้แก้ เหตุผล และ rollback provenance ที่สูญหายกลับมาไม่ได้

## Acceptance cases ที่ต้องพิสูจน์ภายหลัง

1. Admin สองราย publish expectedRevision เดียวกัน ได้ current ใหม่เพียงชุดเดียวและไม่มี orphan revision/audit
2. Audit write ล้มเหลวทำให้ current/revision ไม่ commit ครึ่งชุด
3. Majority timeout ถูก reconcile ด้วย identity/hash ไม่ publish revision ใหม่ซ้ำโดยไม่รู้ผลเดิม
4. Invalid keys/types/ranges/scripts/secrets ถูกปฏิเสธก่อน activation
5. Change stream หายหรือ resume token หมดอายุแล้ว full reload ได้ validated snapshot
6. Cold start/outage/เกิน 5 นาทีรักษา unavailable/degraded behavior ของแต่ละหน้าที่
7. Ordinary config revision ไม่เปลี่ยน Redis counter epoch; controlled fleet activation ตรวจได้
8. Restore/replay ไม่อ้างว่าประวัติ audit ที่ไม่มี backup สร้างคืนจาก current ได้

## แหล่งข้อมูลและสถานะการตรวจ

- [MongoDB transactions](https://www.mongodb.com/docs/manual/core/transactions/), [production prerequisites](https://www.mongodb.com/docs/manual/core/transactions-production-consideration/), [write concern ambiguity](https://www.mongodb.com/docs/manual/core/replica-set-write-concern/)
- [Schema validation](https://www.mongodb.com/docs/manual/core/schema-validation/), [change streams](https://www.mongodb.com/docs/manual/changestreams/), [TTL](https://www.mongodb.com/docs/manual/core/index-ttl/)
- [MongoDB design](mongodb-design.md), [document model](mongodb-document-model.md), [Redis proposal](redis-design.md), [research](supporting-data-operations-research.md)

เอกสารตรวจ semantic alignment กับภาพและแหล่งอ้างอิง; ยังไม่ใช่ runtime proof, security approval หรือ final API contract

## โครงสร้างภาพหลังการทบทวนความหมาย

ภาพนี้เป็น **Sequence ของสถานการณ์หนึ่ง**: แกนตั้งคือเวลา ลูกศรคือข้อความระหว่าง interaction boundaries และ activation bar แสดงช่วงที่กำลังประมวลผล ไม่ใช่ compile dependency หรือสถานะที่บันทึกใน order

Header แสดง ownership เป็นกล่องซ้อนที่มี parent/child จริงใน draw.io: caller/provider อยู่ในขอบเขตภายนอก, PostgreSQL/MongoDB/Redis อยู่ในขอบเขตข้อมูลของตน และ backend request boundary แสดง Application coordination ที่แยก `Command / Query`, `Validator / policy guard`, `Handler / transaction ports` เป็นกล่องย่อย ผู้เรียกผ่าน API/transport ตาม contract; lifeline ฝั่ง backend เป็นตัวแทน use-case boundary รวม ไม่ได้อ้างว่ากล่องย่อยทั้งสามมีเวลาแยกกันหรือเป็นสาม services การดูรายละเอียดการเรียกภายใน/ตำแหน่ง Dispatcher ให้ใช้ [Architecture](architecture-design.md) และ [Repository](repository-architecture.md)

กรอบ `ALT` และข้อความภายในเป็นกลุ่ม native แยกจาก header ownership: สองแขนงคือทางเลือกที่ขึ้นกับ guard ไม่ใช่ขั้นตอนที่ต้องทำต่อกันทุกครั้ง Return ใช้เส้นประหัวทึบ; async refresh hint ใช้หัวโปร่ง; SQL/provider ไม่ได้เป็น participant ใน transaction เดียวข้ามระบบ อ่านขอบเขตและข้อจำกัดของ notation จาก [ความหมายทั้งชุด](diagram-semantics.md)
