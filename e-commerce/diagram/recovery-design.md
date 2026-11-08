---
name: E-commerce Recovery Activity and Owner Gates
description: อธิบาย owner swimlanes, recovery actions, financial reconciliation และ reopening decision gates ใช้อ่านก่อนกำหนด runbook หรือทดสอบ restore/replay
status: in-review
approved_by: null
approved_at: null
---

# Recovery activity และ handoff ระหว่างเจ้าของงาน

ภาพนี้ตอบว่า **ใครต้องทำอะไรและผ่านเงื่อนไขใดก่อนเปิดระบบอีกครั้ง** ใช้ activity/swimlane: สี่ lane คือผู้รับผิดชอบ กล่องสี่เหลี่ยมคือ action, diamond คือ decision gate และ terminator คือจบกระบวนการเปิดบริการ ไม่ได้สร้าง persisted order/payment/operational states ใหม่

## โครงสร้างและลำดับในภาพ

| Owner lane | Action / gate ที่เป็นกล่องลูกจริง | หลักฐานก่อนส่งต่องาน |
| --- | --- | --- |
| Incident command | Declare incident; Hold & investigate | Impact, scope, evidence, backup points และผู้รับผิดชอบ |
| Data / platform operator | Contain & fence; Restore authority | หยุด unsafe writes/old relays, revoke credentials, restore point และ new external sourceEpoch |
| Payment operations | Reconcile provider money; MATCH? | เทียบ provider effect กับ SQL source ที่ restore แล้ว |
| Application service owner | Rebuild derived data; READY?; Reopen & watch | New-epoch snapshots, bounded cache refill, checks และ operator approval |

เส้นหลักเดินจาก declare → contain → restore → reconcile → MATCH? เมื่อ YES จึง rebuild และผ่าน READY? ก่อน reopen เมื่อ MATCH? เป็น NO ให้ Hold & investigate แล้วกลับไป contain เพื่อแก้ timeline/money discrepancy อย่างมีหลักฐาน READY? เป็น NO กลับ hold เช่นกัน ไม่เปิด uncertain writes เพื่อให้ภาพดูจบครบลำดับ

Diamond MATCH? ตรวจ source integrity และ money reconciliation; READY? ตรวจ smoke, invariants, load behavior, config authorization/revision/fleet activation และการยอมรับ recorded data-loss window ผู้รับผิดชอบต้องตัดสินจากหลักฐาน ไม่ใช่เพียง host ตอบ health check

## Source authority และ fencing

SQL restore อาจย้อน aggregate version ขณะที่ MongoDB ยังถือ snapshot จากอนาคต กฎ newer-version เดิมจึงแก้เองไม่ได้ ต้อง fence old worker credentials และ namespace, quarantine copies จาก timeline เดิม แล้วออก **sourceEpoch ใหม่ที่ควบคุมนอก backup ที่ restore** ให้ readers/writers ใช้ generation เดียวกันก่อนเปิดใช้งาน

New-epoch rebuild ใช้ eventId ใหม่ ไม่แก้ epoch/hash ของ eventId เก่า และห้ามนำ old-timeline event มา settle current money เก็บ superseded evidence แยกตาม retention ที่อนุมัติ Old worker ที่หยุดค้างต้องไม่สามารถเขียนปน active generation หลัง resume ได้

## ความล้มเหลวและข้อแลกเปลี่ยน

- Restore SQL ไม่ย้อน Stripe payment/refund ต้องตรวจ provider state จริงและบันทึก manual correction ทุกครั้ง
- Current projection rebuild ไม่คืน actors, intermediate audit transitions หรือ payload ที่หายไป ต้อง restore audit/config history จากหลักฐานของตนและรายงาน gap
- Replication ไม่ใช่ backup; SQL PITR ต้องมี base backup และ continuous WAL ส่วน MongoDB backup ต้องสอดคล้องกับ topology และ config/history ownership
- Cache อาจเริ่ม cold ได้ แต่ต้อง bounded refill เพื่อไม่ทำให้ restored SQL ล้มซ้ำ ส่วน admission policy/counter loss มีข้อกำหนดแยก
- การ hold ลด availability แต่ป้องกันเงินหรือ stock ที่ไม่แน่นอนถูกเปิดใช้งาน ไม่มีตัวเลข RPO/RTO ที่อ้างได้ก่อนซ้อม restore/replay และวัดผลจริง

## แหล่งข้อมูลและสถานะ

- [Supporting recovery research](supporting-data-operations-research.md), [MongoDB design](mongodb-design.md), [Redis design](redis-design.md)
- [Outbox delivery](outbox-delivery-sequence.md), [document model](mongodb-document-model.md), [payment webhook](payment-webhook-sequence.md), [refund recovery](refund-sequence.md)
- [PostgreSQL PITR](https://www.postgresql.org/docs/current/continuous-archiving.html), [MongoDB backup methods](https://www.mongodb.com/docs/manual/core/backups/)

Runbook flow นี้ยัง `in-review` ไม่เปลี่ยน workflow, API หรือ schema จริง และไม่อ้างว่ามี incident drill, financial reconciliation, fenced-worker race test หรือ measured RPO/RTO แล้ว

## Recovery objectives ที่เสนอเพื่อการซ้อม

ยังไม่มี measured RPO/RTO ตัวเลขต่อไปนี้เป็น candidate สำหรับ owner review และต้องพิสูจน์ด้วย restore drill ก่อน production: RPO คือช่วงข้อมูลที่ยอมสูญเสียได้ ส่วน RTO คือเวลาจากประกาศเหตุจนกลับมาให้บริการตามขอบเขตที่ตกลง

| ข้อมูล / ความสามารถ | Candidate RPO / RTO | วิธีและข้อจำกัด |
| --- | --- | --- |
| PostgreSQL business + outbox | ≤5นาที / ≤60นาที | encrypted base backup + retained WAL/PITR; การrestoreไม่ย้อน Stripe จึงต้อง reconcile provider ก่อน unsafe writes |
| MongoDB config + audit/event evidence | ≤5นาที / ≤60นาที | consistent tested backups; auditเป็นข้อมูลที่สร้างกลับจาก current SQL snapshot ไม่ครบ |
| Transaction status projections | ไม่กำหนดให้เป็น financial truth / rebuildภายใน4ชั่วโมง | สร้าง current snapshots จาก active source epoch และ replayเฉพาะหลักฐานที่ยังretain; แสดง rebuilt/as-of version |
| Redis public cache | ข้อมูลสร้างใหม่ได้ / เริ่ม emptyและwarmupแบบboundedภายใน15นาทีเป็นcandidate | cache lossไม่ทำให้ business data หาย; ต้องตรวจSQL capacityระหว่างcold-start |
| Redis admission | ไม่ใช่durable entitlement; lossอาจคืนburstตามcapacity / ฟื้นservice≤15นาทีเป็นcandidate | ใช้outagepolicyที่อนุมัติ; ไม่อ้างquotaไม่หายเพียงเพราะมีreplica |

Backup ต้องแยก failure domain จาก primary มี encryption/access policy และทดสอบ restore จริง ไม่ถือว่า replica หรือการ export projections คือ backup หลักฐานการซ้อมต้องระบุ backup point, source high-water marks, config revision, epochs, manual corrections และเวลาที่วัดจริง

## ขั้นตอนตรวจเงินและ timeline

1. Incident owner ระบุขอบเขตเหตุและหยุด writes ที่อาจเพิ่มผลข้างเคียง พร้อมเก็บ provider correlation/operation IDs ห้ามเริ่ม chargeใหม่เพียงเพราะแถวใน SQL snapshot ไม่มี
2. Database owner เลือก restore points ที่อธิบายได้สำหรับ SQL และ MongoDB config/audit พร้อมตรวจ consistency และไม่ลบหลักฐาน timeline เดิม
3. Application owner เปรียบเทียบ durable operations/receipts/outbox กับ provider object/event outcomes: แยก succeeded, pending, failed และunknown; คืนstock/budgetเฉพาะเมื่อ guard และผลเงินถูกต้อง
4. Fence workersเก่าก่อนกำหนด active sourceEpoch ใหม่ ตรวจว่า lease/token/credential/control generation เก่าไม่สามารถเขียน current projections หรือ ACK claim ใหม่ได้
5. หาก MongoDB copy อยู่ ahead of restored SQL ให้ quarantine generationเก่า ไม่ใช้เพียงคำว่า versionมากกว่าเพื่อชนะ source ที่restore; สร้างsnapshotและeventIDsใหม่ในepochใหม่
6. Replay eventเดิมเฉพาะenvelope/hash/epochเดิมที่ถูกอนุญาต ไม่เปลี่ยน payloadภายใต้IDเดิม และไม่ปะปนhistorical evidenceกับactive current projection
7. ผ่าน MATCH?/READY? gates, smoke/invariant/load checks แล้ว incident owner อนุมัติ reopen พร้อม watch window และบันทึก actual data-loss window

## การซ้อมและเกณฑ์ตรวจรับ

ต้องซ้อม SQL restoreที่เก่ากว่าMongoDB, lost ACKหลังdestination commit, workerเก่ากลับมาหลังfencing, poison event, configbackupเก่า, provider successที่SQLไม่มี และaudit retentionที่ไม่พอ ตรวจทั้ง happy recovery และเส้นทาง reworkในlane ไม่ยอมผ่าน gateเพราะ databaseตอบhealthcheckอย่างเดียว Quarantineต้องรักษาหลักฐานและมีoperator/ownerตัดสิน ไม่ทำsilenttruncateหรือชดเชยเงินอัตโนมัติจากสำเนา

## Retention และความครบของการสร้างกลับ

Outboxที่purgeแล้วไม่ใช่event archive สำหรับทุกยุค Current SQL snapshotสร้างได้เฉพาะสถานะปัจจุบัน ไม่คืนลำดับทุกเหตุการณ์ Auditที่เก็บไม่ครบต้องรายงานcoverage gapและใช้backup/archiveที่ได้รับอนุมัติ ระยะbackup/WAL/outbox/audit retention ต้องสอดคล้องrecovery windowและprivacy/capacityที่เจ้าของงานตกลง งานนี้ไม่เปิดautomatic TTLและไม่อ้างcompliance retention guarantee
