---
name: E-commerce Outbox Delivery Sequence
description: อธิบาย claim lease, MongoDB transaction, fenced acknowledgement และการส่งซ้ำ ใช้ตรวจภาพก่อนออกแบบ schema และ worker จริง
status: in-review
approved_by: null
approved_at: null
---

# Outbox delivery: claim → destination transaction → guarded ACK

ภาพนี้ตอบว่าการส่ง publication intent จาก PostgreSQL ไป MongoDB จะรับมือ crash, timeout และหลาย worker โดยไม่ทำ business mutation ซ้ำได้อย่างไร
ทั้งหมดเป็น **PROPOSED**; ยังไม่มี outbox table, collection, worker หรือผลทดสอบ runtime ที่ยืนยันการทำงาน
PostgreSQL ยังคงเป็น authority ของ order/payment/refund/stock/budget ส่วน MongoDB เป็นสำเนาสำหรับงานค้นหาและตรวจสอบ

[ภาพ PNG](outbox-delivery-sequence.drawio.png) · [ไฟล์แก้ไข](outbox-delivery-sequence.drawio) · [HTML](outbox-delivery-sequence.html)

## Actors และขอบเขต

| ID ใน model | Actor / คำกำกับ | หน้าที่ |
| --- | --- | --- |
| `relay` | Outbox relay / PROPOSED BOUNDED WORKER | Claim, ส่ง envelope เดิม, retry และ ACK ตามสิทธิ์ของ claim |
| `sql` | PostgreSQL / OUTBOX / LEASE OWNER | เก็บ durable intent, lease และผล delivery |
| `mongo` | MongoDB / MAJORITY LOCAL TX | Commit marker, projection และ related audit ภายใน store เดียว |

ไม่มี payment provider ในภาพ เพราะ relay ไม่สร้าง charge/refund และไม่เรียก business command ซ้ำเพื่อชดเชยเอกสารที่หาย
Precondition ที่แสดงในภาพ: checkout สร้าง `WAIT_PAYMENT`, จอง stock/budget, บันทึกข้อมูลเกี่ยวข้องและ proposed outbox intent แล้ว commit พร้อมกันก่อนเริ่มลำดับนี้ Payment success เป็น event ภายหลัง; ดู [checkout](../reference/business/checkout-sequence.md) และ [publication states](event-outbox-design.md)

## Message ที่ตรงกับภาพ

| ลำดับ | จาก → ถึง | Label | ความหมายและจุดตรวจ |
| --- | --- | --- | --- |
| 1 | `relay` → `sql` | CLAIM BATCH | Short claim TX; availableAt + durable lease token |
| 2 | `sql` → `relay` | LEASE COMMIT | No SQL row lock held over network call |
| 3 | `relay` → `mongo` | APPLY EVENT | Stable event ID + hash + source epoch/version |
| 4 | `mongo` → `relay` | TX COMMITTED | Marker + conditional projection + audit together |
| 5 | `relay` → `sql` | ACK LEASE | Guard current unexpired owner/token; destination already committed |
| 6 | `sql` → `relay` | DELIVERED | ACK loss may cause replay, not new business work |
| 7 | `relay` → `sql` | RETRY LATER | Timeout is ambiguous; preserve event ID and payload |
| 8 | `sql` → `relay` | RECLAIMABLE | Lease expiry ออก token ใหม่; stale ACK ต้องถูกปฏิเสธ |

ALT ในภาพมีสองทางเลือกหลัง APPLY EVENT ไม่ใช่ทำ message 4–8 ต่อกันทุกครั้ง
ทาง `majority destination commit confirmed` ใช้ message 4–6
ทาง `destination/ACK uncertain or retryable error` ใช้ message 7–8
หาก MongoDB commit แล้วแต่ ACK สูญหาย worker รอบถัดไปยังต้องตรวจ duplicate; คำว่า uncertain ไม่ได้แปลว่า destination rollback แน่นอน
Schema/hash/epoch poison เป็นเส้นทาง quarantine ที่อธิบายละเอียดใน state diagram ไม่ใช่ผล retry ที่ถูกยอมรับเป็น delivery สำเร็จ

## Durable claim และค่าเริ่มต้นที่เสนอ

| ตัวควบคุม | ค่าเสนอที่ยังไม่ทดสอบ | เหตุผล / ข้อจำกัด |
| --- | --- | --- |
| Batch | ไม่เกิน 50 events ต่อ claim | จำกัดงานค้างและขนาด recovery batch; ต้องทดสอบ tenant fairness |
| Lease | 30 วินาที | Claim มี owner/token/deadline ที่ durable; ไม่อาศัย process lock |
| Destination deadline | 5 วินาทีต่อ event attempt | จำกัดการรอของ client; ไม่รับรองว่า server ยกเลิก write แล้ว |
| Backoff | เริ่ม 1 วินาที คูณสองถึง 300 วินาที พร้อม jitter | ลด retry storm; ต้องคง eventId/payload เดิม |
| Quarantine budget | ครบ 20 attempts หรืออายุ 24 ชั่วโมง อย่างใดถึงก่อน | หยุด automatic retry และแจ้ง operator; ไม่ลบหลักฐาน |
| Hard poison | Schema ที่ไม่รองรับหรือ ID/hash conflict: ทันที | Retry payload เดิมไม่แก้ semantic corruption |

Batch 50 ไม่ได้แปลว่าส่งทีละรายการครบ 50 ภายใต้ lease เดียวได้เสมอ เพราะ 50 × 5 วินาทีเกิน 30 วินาที
Worker ต้องจำกัด concurrency, เริ่มงานเฉพาะเมื่อเหลือ lease พอ และ heartbeat ต่ออายุด้วย token ก่อนหมดอายุ หรือปล่อยรายการให้ reclaim
ACK/retry/heartbeat ต้อง match owner และ leaseToken ปัจจุบัน; worker ที่เสีย lease ต้องหยุดอ้างสิทธิ์ แม้ network write จะยังจบภายหลัง
ใช้เวลาจากฐานข้อมูลสำหรับ lease และระบุ index ของ eligibility/reclaim ใน downstream data model
`SKIP LOCKED` ช่วยให้หลาย consumer claim งาน แต่ SQL lock สิ้นสุดเมื่อ claim transaction commit จึงแทน durable lease ไม่ได้

## Envelope และ idempotent destination

ตัวอย่างเป็นข้อมูลสมมติ ไม่ใช่ final event/API contract และไม่มี PII หรือข้อมูลบัตร

```json
{
  "eventId": "evt_demo_001", "eventType": "OrderStatusSnapshot",
  "schemaVersion": 1, "sourceEpoch": "epoch_demo_a",
  "aggregateType": "Order", "aggregateId": "order_demo_001",
  "aggregateVersion": 7, "occurredAt": "2026-11-07T00:00:00Z",
  "correlationId": "corr_demo_001", "payloadHash": "sha256:<demo>",
  "payload": { "status": "PAYMENT_CONFIRMED", "paymentRef": "pay_demo_001" }
}
```

Payload เป็น **full allowlisted snapshot**; ห้ามใช้ unordered delta เช่น “บวก stock” หรือ “เปลี่ยนบาง field” แล้วอ้างว่า sourceVersion guard เพียงอย่างเดียวทำให้ถูกต้อง
Canonicalization/hash version ต้องระบุใน contract ภายหลัง; hash ใช้เปรียบเทียบ immutable envelope/payload ตามกติกาเดียวกันทุก writer
eventId ต้อง unique ตาม model; same ID + same canonical hash คือ replay ส่วน same ID + different hash ต้อง quarantine และไม่ overwrite
MongoDB local transaction ทำ marker insert, conditional newer-version projection replacement และ related audit ร่วมกัน
หาก marker commit ก่อน effect แล้ว crash จะทำให้ retry เห็น marker แต่ projection หาย จึงห้ามแยก commit
เหตุการณ์เก่าที่ถูกต้องยัง append history ได้ แต่ projection เป็น no-op หาก version ไม่ใหม่ใน epoch เดียวกัน
Source epoch ต่างกันไม่ให้นำ version มาเทียบข้าม timeline แบบจำนวนเต็มธรรมดา

## Conceptual validation และ candidate access paths

| สิ่งตรวจ | กฎเสนอ | เมื่อไม่ผ่าน |
| --- | --- | --- |
| Identity | eventId ไม่ว่าง, type/ID มีขอบเขต, epoch เป็น active source | Quarantine ไม่สร้างสิทธิ์จากข้อมูลปลายทาง |
| Schema | รองรับ schemaVersion/eventType และ typed snapshot | Hard poison ทันที |
| Hash | Same ID ต้องตรง hash ตาม canonicalization version | Integrity conflict ทันที |
| Version | Integer เพิ่มจาก source; replace เฉพาะ version ใหม่ | Old version เก็บ history และไม่ย้อน projection |
| Payload | Allowlist, bounded size, no secrets/PII/raw provider body | Reject และตรวจสาเหตุ |
| Lease | ACK/renew/retry ต้องตรง owner/token ที่ยังใช้ได้ | ไม่เปลี่ยน claim ของ worker ใหม่ |

| Query shape | Candidate index / เหตุผล |
| --- | --- |
| Claim READY/RETRY_WAIT ที่ due ตาม availableAt พร้อม limit | Partial eligible-state index เรียง availableAt และ stable ID; ยังไม่กำหนด SQL |
| Reclaim CLAIMED ที่ leaseUntil หมด | State + leaseUntil + stable ID แยกจาก due scan |
| Mongo duplicate lookup | Unique eventId; ตรวจ payloadHash หลังพบ identity |
| Current snapshot lookup | Unique sourceEpoch + aggregateType + aggregateId |

QUARANTINED ต้องหยุด automatic retry และผ่าน operator review, authorization และ audited disposition ก่อน controlled replay โดยคง original eventId/hash การ replay ส่ง event เดิมเท่านั้น ไม่สร้าง order หรือจอง stock/budget ใหม่

ไม่มีการ provision index/collection หรือสร้าง migration จากเอกสารนี้

## Retention, restore และข้อแลกเปลี่ยน

At-least-once delivery ยอมให้ส่งซ้ำเพื่อไม่เสีย committed intent; ใช้ destination transaction/idempotency รับต้นทุนเพิ่มแทนการอ้าง cross-store exactly-once
หลัง restore PostgreSQL MongoDB อาจอยู่อนาคตกว่า source จึงต้อง fence worker เก่าและกัก derived copies ก่อนเปิด timeline ใหม่
New authority epoch ต้องมาจาก recovery control ที่ไม่ย้อนตาม backup เดิม; rebuild snapshot เป็น event ใหม่ ไม่แก้ epoch/hash ใต้ eventId เดิม
Operator replay รักษา eventId/envelope เดิม ตรวจ epoch และ authorization ใหม่; old-timeline event ไม่ใช่ current business truth
Retention ของ marker/event ต้องครอบคลุมทุก replay horizon ที่อนุญาต; การลบก่อนเวลาทำให้ dedupe guarantee เปลี่ยน
Current snapshot rebuild ไม่คืน actor, intermediate transitions หรือ payload audit ที่ลบแล้ว; audit ต้องมี backup/retention ของตนเอง
ยังไม่เปิด automatic TTL และยังไม่อนุมัติ infinite retention; ต้องตั้ง finite budget/deletion/archive policy ก่อน production

## Acceptance cases ที่ต้องพิสูจน์ภายหลัง

1. Crash หลัง business commit ยังเหลือ intent; crash ก่อน commit ไม่ส่ง event ของธุรกรรมที่ rollback
2. Crash ระหว่าง marker/projection/audit ไม่มี partial MongoDB commit
3. MongoDB commit แต่ ACK loss ส่งซ้ำแล้วได้ effect เดียวและไม่เกิด business mutation ใหม่
4. Lease หมดและสอง worker แข่งกัน: stale token ACK ไม่สำเร็จ; duplicate destination ยังปลอดภัย
5. Same ID ต่าง hash และ unsupported schema ถูก quarantine ทันที พร้อมหลักฐานที่ไม่เปิดข้อมูลลับ
6. Out-of-order full snapshots ไม่ย้อน current version; restoration epoch ไม่ยอมรับ old worker
7. Backlog, attempt budget, heartbeat และ recovery replay ถูกทดสอบที่จำนวน instance ที่คาดใช้

## แหล่งข้อมูลและสถานะการตรวจ

- [PostgreSQL transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html), [SKIP LOCKED](https://www.postgresql.org/docs/current/sql-select.html), [lock lifetime](https://www.postgresql.org/docs/current/explicit-locking.html)
- [MongoDB transactions](https://www.mongodb.com/docs/manual/core/transactions/), [majority timeout ambiguity](https://www.mongodb.com/docs/manual/core/replica-set-write-concern/), [.NET transaction retries](https://www.mongodb.com/docs/drivers/csharp/current/crud/transactions/)
- [Research note](../design/supporting-data-operations-research.md), [MongoDB proposal](../design/mongodb-design.md), [implementation boundary](../design/implementation-readiness-plan.md)

ตรวจความสอดคล้องกับ actor/message model เท่านั้น; ยังไม่ทดสอบ worker, database failover, load, security หรือ restore จริง

## โครงสร้างภาพหลังการทบทวนความหมาย

ภาพนี้เป็น **Sequence ของสถานการณ์หนึ่ง**: แกนตั้งคือเวลา ลูกศรคือข้อความระหว่าง interaction boundaries และ activation bar แสดงช่วงที่กำลังประมวลผล ไม่ใช่ compile dependency หรือสถานะที่บันทึกใน order

Header แสดง ownership เป็นกล่องซ้อนที่มี parent/child จริงใน draw.io: caller/provider อยู่ในขอบเขตภายนอก, PostgreSQL/MongoDB/Redis อยู่ในขอบเขตข้อมูลของตน และ backend request boundary แสดง Application coordination ที่แยก `Command / Query`, `Validator / policy guard`, `Handler / transaction ports` เป็นกล่องย่อย ผู้เรียกผ่าน API/transport ตาม contract; lifeline ฝั่ง backend เป็นตัวแทน use-case boundary รวม ไม่ได้อ้างว่ากล่องย่อยทั้งสามมีเวลาแยกกันหรือเป็นสาม services การดูรายละเอียดการเรียกภายใน/ตำแหน่ง Dispatcher ให้ใช้ [Architecture](architecture-design.md) และ [Repository](../reference/repository/repository-architecture.md)

กรอบ `ALT` และข้อความภายในเป็นกลุ่ม native แยกจาก header ownership: สองแขนงคือทางเลือกที่ขึ้นกับ guard ไม่ใช่ขั้นตอนที่ต้องทำต่อกันทุกครั้ง Return ใช้เส้นประหัวทึบ; async refresh hint ใช้หัวโปร่ง; SQL/provider ไม่ได้เป็น participant ใน transaction เดียวข้ามระบบ อ่านขอบเขตและข้อจำกัดของ notation จาก [ความหมายทั้งชุด](../design/diagram-semantics.md)

ภาพนี้ไม่มี backend request participant; header worker แยกจาก SQL lease owner และ MongoDB destination transaction อย่างชัดเจน จึงไม่มี Command/Validator/Handler ยัดเข้า worker หรือ database boundary ที่ไม่ได้สื่อสิ่งนั้น

[กลับสารบัญ diagram](../README.md)
