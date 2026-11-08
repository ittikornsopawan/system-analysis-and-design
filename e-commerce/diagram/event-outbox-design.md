---
name: E-commerce Event Outbox Lifecycle Design
description: อธิบาย proposed publication states, lease/retry/quarantine และ stable envelope ใช้ตรวจ state diagram ก่อนออกแบบ SQL schema และ worker จริง
status: in-review
approved_by: null
approved_at: null
---

# Publication lifecycle & delivery guarantees

ภาพนี้ตอบว่า publication record เดินทางจาก committed intent ไปถึง delivered หรือ quarantine ด้วย guard ใด
เป็น **PROPOSED delivery states** ไม่ใช่ order/payment statuses ใหม่ ไม่ใช่ queue ที่ deploy แล้ว และไม่มี cross-store exactly-once guarantee
Business state และ publication intent ต้อง commit ด้วยกันใน PostgreSQL ก่อนเข้า READY

[ภาพ PNG](event-outbox-design.drawio.png) · [ไฟล์แก้ไข](event-outbox-design.drawio) · [HTML](event-outbox-design.html)

## Nodes ที่ตรงกับ model

| Node ID | State / คำกำกับ | ความหมาย |
| --- | --- | --- |
| `ready` | READY / PROPOSED PUBLICATION STATE | SQL business + intent committed; immutable eventId/payload, epoch/version; due เมื่อ availableAt <= now |
| `claimed` | CLAIMED / SHORT SQL CLAIM TX | Durable leaseOwner/leaseToken/leaseUntil; commit claim ก่อน network I/O |
| `delivered` | DELIVERED / ACK AFTER DESTINATION COMMIT | MongoDB majority local TX สำเร็จและ SQL ACK ผ่าน token guard |
| `retry` | RETRY_WAIT / TRANSIENT / AMBIGUOUS | Backoff/jitter; envelope เดิม ไม่มี business mutation รอบใหม่ |
| `quarantine` | QUARANTINED / SCHEMA / IDENTITY CONFLICT | Poison/conflict หรือหมด retry budget; operator review และ audited replay |

## Directed transitions ที่ตรงกับภาพ

| จาก → ถึง | Label | Guard / การกระทำ |
| --- | --- | --- |
| Start → READY | SQL COMMIT | Business mutation + intent สำเร็จใน SQL transaction เดียว |
| READY → CLAIMED | CLAIM | Eligible due record; short claim transaction ลง durable ownership |
| CLAIMED → DELIVERED | COMMIT + ACK | Confirm destination transaction แล้ว ACK ด้วย owner/token ปัจจุบัน |
| CLAIMED → RETRY_WAIT | RETRY | Transient/uncertain outcome; preserve identity และ schedule bounded delay |
| CLAIMED → QUARANTINED | POISON | Unsupported schema, identity/hash/epoch conflict หรือ retry budget หมด |
| RETRY_WAIT → READY | DUE | availableAt ถึงเวลาและยังอยู่ใน budget |
| CLAIMED → CLAIMED | LEASE EXPIRED | Reclaim เป็น claim ใหม่/token ใหม่; ไม่ใช่สิทธิ์ให้ owner เก่า ACK |

CLAIMED self-loop เป็น lease replacement ตาม guard ไม่ใช่ automatic renewal ไม่จำกัดเวลา
เส้น RETRY และ POISON เป็นทางเลือกตามประเภทปัญหา ไม่ใช่ทุก event ต้องผ่านทุก state
ภาพไม่วาด QUARANTINED → READY เพื่อไม่สื่อว่า auto retry ได้เอง; operator replay เป็น controlled administrative operation ที่ต้องออกแบบภายหลัง
DELIVERED ไม่หมายความว่า source business transaction ทำใหม่ หรือพิสูจน์ว่ามีการส่งทาง network ครั้งเดียว

## ทำไมใช้ outbox

SQL transaction ทำให้ business mutation กับ publication intent สำเร็จหรือ rollback ด้วยกัน
การเขียน SQL แล้วเรียก MongoDB ตรงจาก request โดยไม่มี durable intent เสี่ยงสูญ event เมื่อ process หยุดหลัง SQL commit
Outbox เพิ่ม storage, worker, reconciliation และ eventual delay แต่ปล่อย business commit ได้เมื่อ destination unavailable
MongoDB ไม่ใช้เป็น authority ในการ settle money, authorize refund หรือคำนวณ stock; อ่านสำเนาต้องแสดง sourceVersion/time และยอมรับ lag
ไม่มี broker ใหม่หรือ microservice ใหม่ถูกเลือกโดยภาพนี้; relay เป็น responsibility ที่ต้องเลือก hosting ภายหลัง

## Stable envelope และตัวอย่าง

| Field กลุ่ม | Proposed meaning |
| --- | --- |
| eventId / eventType / schemaVersion | Globally unique immutable event identity, supported type และ document shape |
| sourceEpoch / aggregateId / version | Timeline authority, source entity และ monotonic aggregate version ภายใน epoch |
| occurredAt / correlationId | Source occurrence และ trace reference ที่ไม่เป็น metric label |
| payloadHash / allowlisted snapshot | Canonical immutable payload evidence กับ full permitted state snapshot |

```json
{
  "eventId": "evt_demo_021", "eventType": "OrderStatusSnapshot",
  "schemaVersion": 1, "sourceEpoch": "epoch_demo_b",
  "aggregateType": "Order", "aggregateId": "order_demo_021",
  "aggregateVersion": 4, "occurredAt": "2026-11-07T01:00:00Z",
  "correlationId": "corr_demo_021", "payloadHash": "sha256:<demo>",
  "payload": { "status": "WAIT_PAYMENT", "shopRef": "shop_demo_002" }
}
```

ตัวอย่าง ID เป็นข้อมูลสมมติและ hash เป็นคำกำกับ ไม่ใช่ digest ที่ใช้จริงหรือ final contract
Snapshot เป็น status/allowed references ตามขอบเขตเดิม ไม่รวมที่อยู่ลูกค้า ข้อมูลบัตร secrets หรือ raw provider request
Full snapshot ช่วยให้ event ใหม่มาถึงก่อนเก่าได้โดยไม่ต้องประกอบ unordered deltas; เพิ่ม payload/write cost แลกกับ replay ที่เข้าใจได้
Same eventId + same hash คือ duplicate; same ID + different hash ต้อง quarantine ทันที ห้ามถือว่า unique index conflict คือ success เสมอ
Hash canonicalization/version ต้องตกลงก่อน implementation; hash ไม่ใช่หลักฐานทางกฎหมายหรือ authorization

## Lease/retry defaults ที่เสนอและยังไม่ทดสอบ

| Parameter | Proposed default | เงื่อนไข |
| --- | --- | --- |
| Claim batch | 50 events | Bound concurrency/per-tenant work; ไม่กวาดทั้ง backlog |
| Lease duration | 30 วินาที | Durable owner/token/deadline ใช้ database clock |
| Destination attempt deadline | 5 วินาที | Timeout อาจมี write สำเร็จแล้ว; ไม่ยืนยัน cancellation |
| Retry delay | 1 วินาที คูณสองจน 300 วินาที + jitter | ค่าไม่ reset event identity/payload |
| Automatic quarantine | ครบ 20 attempts หรืออายุ 24 ชั่วโมง อย่างใดก่อน | Alert/operator disposition; ไม่ทิ้ง event |
| Unsupported schema/hash poison | ทันที | ไม่เผา retry budget กับ payload ที่รู้ว่าใช้ไม่ได้ |

Batch 50 × deadline 5 วินาทีเกิน lease 30 วินาทีหากทำทีละรายการ จึงต้องออกแบบ bounded scheduling/heartbeat ไม่ใช่อ้างว่าค่านี้ปลอดภัยแล้ว
Heartbeat/retry/ACK เป็น conditional ownership update; หมด lease ต้องหยุด ACK และยอมให้ reclaim
Worker ที่หมดสิทธิ์อาจยังส่ง MongoDB สำเร็จ จึงยังต้อง unique/hash/version guards และ atomic destination effects
Reclaim/claim order ไม่ใช่ global completion order; ยังต้องทดสอบ starvation และ tenant fairness

## Destination transaction และ conceptual validation

MongoDB local transaction รวม integration event marker, newer-version projection และ related audit; ไม่รวม SQL ACK
Majority commit ยกระดับ durability ตาม settings แต่ write-concern timeout เป็นผลไม่แน่นอน ต้อง reconcile/retry ด้วย identity เดิม
หาก marker บันทึกแต่ projection ไม่บันทึก replay จะถูก suppress ผิด จึงต้องตรวจ atomicity ทั้งชุด

| Validation | Proposed action |
| --- | --- |
| Unsupported schema/type หรือ invalid bounded shape | Immediate quarantine พร้อม reason ที่ไม่เปิดข้อมูลลับ |
| Event ID/hash conflict | Quarantine + integrity investigation; ไม่ overwrite |
| Old aggregateVersion ใน active epoch | Append valid history แต่ conditional projection no-op |
| Unknown/old sourceEpoch | Quarantine หรือ controlled recovery flow; ห้ามเทียบ version ข้าม epoch |
| Destination uncertain | Retry/reconcile เดิม; ไม่สร้าง business operation ใหม่ |
| ACK token mismatch | ถือว่า claim ownership หาย; ไม่เปลี่ยน owner ใหม่ |

## Candidate query shapes และ indexes

| Query | Candidate access path; ยังไม่ใช่ DDL |
| --- | --- |
| Claim due READY/RETRY_WAIT ตามเวลา + limit | Partial active-state index, availableAt + stable ID |
| Reclaim expired CLAIMED | State + leaseUntil + stable ID |
| Operator quarantine review | State + quarantinedAt/reason + stable ID ตาม filter ที่อนุมัติ |
| Source aggregate reconciliation | Source epoch + aggregate identity + version |
| Destination dedupe | Unique eventId พร้อม stored payloadHash |

Data-modeling workflow ต้องออกแบบ constraints, ownership transition, index tests และ scan fairness ก่อนสร้าง migration

## Retention และ source restoration

DELIVERED record ไม่ได้แปลว่าลบได้ทันที: ต้องกำหนด replay horizon, marker retention, archive และ backup recovery horizon ให้สัมพันธ์กัน
ยังไม่เปิด automatic TTL; ต้องอนุมัติ finite capacity/retention/deletion policy ก่อน production และ enforce logical expiry หากจำเป็น
หลัง SQL restore ต้อง fence old workers, quarantine MongoDB timeline ที่อาจล้ำหน้า และเริ่ม externally controlled sourceEpoch ใหม่
New snapshots ใน epoch ใหม่ใช้ eventId ใหม่; operator replay รักษา eventId/envelope เดิมและไม่แก้ sourceEpoch ใต้ identity เดิม
Active epoch selector และ credential/network fencing ต้องกัน paused old worker ไม่ให้ปน current namespace
Current SQL snapshot rebuild คืน current projection ได้ แต่คืน historical actor/intermediate event ที่ไม่มีหลักฐานไม่ได้
Audit/integration history ต้องมี backup/retention ของตน; ไม่อ้าง completeness เมื่อมี gap

## Acceptance cases และสถานะการตรวจ

1. Crash ก่อน/หลัง source commit แยกได้ และไม่เกิด ghost event ของ SQL rollback
2. Lease reclaim ให้ token ใหม่; owner เก่า ACK/renew ไม่ได้แม้ write จบช้า
3. Lost destination/ACK response ส่งซ้ำได้โดยไม่มี second projection/audit effect
4. Hash poison/quarantine budget มี alert และ audited operator replay ที่เก็บ identity เดิม
5. Concurrent out-of-order snapshots ไม่ย้อน version; recovery epoch ไม่รับ event timeline เก่า
6. Eligibility/reclaim scans ใช้ access paths ที่ทดสอบแล้วและไม่ starvation เมื่อ backlog โต

ตรวจเฉพาะ design/model alignment; ยังไม่มี runtime, failover, throughput หรือ restore proof และไม่ใช่ final API contract

## แหล่งข้อมูล

- [PostgreSQL transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html), [queue-like SKIP LOCKED](https://www.postgresql.org/docs/current/sql-select.html), [lock lifetime](https://www.postgresql.org/docs/current/explicit-locking.html)
- [MongoDB atomic transactions](https://www.mongodb.com/docs/manual/core/transactions/), [write concern ambiguity](https://www.mongodb.com/docs/manual/core/replica-set-write-concern/), [unique indexes](https://www.mongodb.com/docs/manual/core/index-unique/)
- [Delivery sequence](outbox-delivery-sequence.md), [document model](mongodb-document-model.md), [supporting research](supporting-data-operations-research.md)

## รูปแบบภาพที่ปรับตามความหมาย

ภาพนี้เป็น state machine ของ publication record ห้าสถานะ ไม่ใช่ application layer หรือ order lifecycle: `READY`, `CLAIMED`, `DELIVERED`, `RETRY_WAIT`, `QUARANTINED` แต่ละ parent state มี child compartments แยก durable identity/lease/proof ออกจาก eligibility/effect/operator action กล่อง Event envelope เป็น contract annotation ที่มี Identity, Source/version, Payload/observability อยู่ภายใน ไม่ใช่สถานะที่หก

Transition `ACK` หมายถึง destination local transaction สำเร็จแล้วและ SQL acknowledgement ผ่าน lease guard ตามรายละเอียดในเอกสารนี้ ไม่ใช่ SQL business transaction ร่วม MongoDB เส้น `LEASE EXPIRED`, `RETRY`, `DUE`, `POISON` แสดงการเคลื่อนของ delivery state ส่วน business operation ไม่ถูกเล่นใหม่ โครงสร้าง native รวม state/annotation parents หกกล่องและ child compartments สิบสามกล่อง ดูข้อแตกต่างของ viewpoint ใน [diagram-semantics.md](diagram-semantics.md)
