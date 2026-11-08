---
name: E-commerce Proposed Deployment and Security Placement
description: อธิบาย environment, network zones, host pools และ artifact placement ใน deployment-security ใช้ก่อนทบทวน topology หรือเลือก hosting จริง
status: in-review
approved_by: null
approved_at: null
---

# Proposed private deployment และ security placement

ภาพนี้ตอบว่า **artifact ใดติดตั้งบน host pool ใดและอยู่ใน network boundary ใด** เป็น self-hosted reference ที่เสนอเพื่อทบทวน ไม่ใช่หลักฐานว่ามี infrastructure นี้ทำงานอยู่ ไม่เลือก cloud vendor, region, product image หรือ capacity ที่ยังไม่มีการตัดสินใจ

## โครงสร้างที่เห็นในภาพ

Containment มี environment → security zone → host pool → deployable artifact เป็น parent/child จริง ทั้ง replica count และ pin metadata อยู่กับ host/artifact ที่เกี่ยวข้อง ไม่เปลี่ยน logical component ทุกตัวให้กลายเป็น service แยก

| Security zone | Host pool | Artifact / candidate replicas | Version pin |
| --- | --- | --- | --- |
| Application subnet | API host pool | `Ecommerce.Api` x2 stateless | `releaseSha` ของ release เดียวกัน |
| Application subnet | Worker host pool | Scheduling / outbox responsibilities x1 pool | `releaseSha`; worker hosting ยังเป็น proposal |
| Private data subnet | PostgreSQL host pool | Primary + standby x2 | เลือก supported major และ pin ก่อน deploy |
| Private data subnet | MongoDB host pool | Replica set x3 data-bearing members | เลือก supported major และ pin ก่อน deploy |
| Isolated Redis zone | Cache host | Rebuildable cache x1 | Pin supported release |
| Isolated Redis zone | Admission hosts | Primary + replica x2 | Pin supported release |

จำนวนเป็น candidate ที่ยังไม่วัด capacity หรือ failure-domain behavior; host pool หนึ่งกล่องแทนหลาย replicas ไม่ได้อ้างว่าแต่ละ copy อยู่บนเครื่องเดียวกัน Artifact ของ worker เป็น responsibility ที่เสนอ ไม่อ้างว่ามี worker binary หรือ project ใหม่แล้ว

## เส้นทางและขอบเขตสิทธิ์

เส้น orthogonal ระบุ TLS:5432 สำหรับ SQL, TLS:27017 สำหรับ MongoDB และ TLS:6379 สำหรับ Redis API ใช้ SQL, config/documents และ Redis สองหน้าที่ ส่วน worker ใช้ SQL claim/ack และ MongoDB delivery เส้น worker เป็น dashed เพื่อสื่อ background delivery ไม่ใช้ SQL row lock ค้างข้าม network I/O

Application zone รับเฉพาะ trusted ingress HTTPS 443; data/admin ports ไม่เปิด public เส้น client, Stripe API และ signed webhook อยู่ใน [runtime architecture](architecture-design.md) เพราะภาพนี้จำกัดคำถามไว้ที่ private placement MongoDB แยก reader/publisher/projection-writer roles; Redis cache กับ rate มี memory budget และ credentials คนละชุด

## ความล้มเหลวและข้อแลกเปลี่ยน

- Replica ไม่ใช่ backup: SQL PITR ต้องมี base backup/WAL chain และต้องซ้อม restore; MongoDB-owned config/audit ต้องมี backup ที่เหมาะกับ topology
- MongoDB x3 สนับสนุน replica-set transaction capability แต่ไม่รับรอง availability หรือ isolation ระหว่าง config กับ projection workloads ต้องทดสอบ resource contention
- Cache x1 ลดต้นทุนและยอมให้สูญเสีย cache ได้ แต่ cold refill ต้องมี bounded concurrency และ live SQL eligibility
- Admission primary/replica อาจสูญเสีย counter updates ตอน failover; `noeviction` ป้องกันการขับ key ออกแต่ไม่ได้ทำให้ failover linearizable
- API x2 ต้องใช้ shared admission identity/policy และ compatible pinned artifacts; worker lease ต้อง fenced ข้าม restart ไม่ใช้ process lock เป็นความจริงร่วม

## แหล่งข้อมูลและสถานะ

- [Operations research](supporting-data-operations-research.md), [MongoDB design](mongodb-design.md), [Redis design](redis-design.md)
- [Outbox protocol](outbox-delivery-sequence.md), [recovery activity](recovery-design.md)
- [MongoDB three-member architecture](https://www.mongodb.com/docs/manual/core/replica-set-architecture-three-members/), [PostgreSQL continuous archiving](https://www.postgresql.org/docs/current/continuous-archiving.html)

Topology และตัวเลขทั้งหมดเป็นข้อเสนอ `in-review` ยังไม่มี provision, deployment, version selection, load/failover/security หรือ restore test จากงานภาพนี้

## Artifact และ configuration lifecycle

`releaseSha` ในกล่อง artifact เป็นพารามิเตอร์การ pin เวอร์ชันของ deployment proposal ไม่ใช่ชื่อ image ที่สร้างหรือ deploy แล้ว ต้องผูก releaseของAPI/workerกับsource revisionและschema/config compatibility ที่ตรวจผ่านจริง ส่วน PostgreSQL/MongoDB/Redis ต้องpin supported versionที่เลือกหลังตรวจprovider/security/support ไม่ใช้floating latestเป็นหลักฐานความสามารถ

## สิทธิ์ต่อเส้นทาง

| ผู้เชื่อมต่อ | สิ่งที่อนุญาตตาม proposal | สิ่งที่ต้องแยก |
| --- | --- | --- |
| Public client → trusted edge → API | HTTPS443 และroute/body/concurrency policyที่กำหนด | ไม่เปิดDB/admin portsให้public; เชื่อforwardedIPเฉพาะproxyที่ตั้งค่า |
| API → PostgreSQL | SQLผ่านTLS5432 ด้วยapp roleที่จำเป็น | migration/admin/backup roleแยกจากrequest credentials |
| Worker → PostgreSQL | claim/ACK/outbox/guardedjobตามหน้าที่ | ไม่ให้workerทุกชนิดเป็นdatabase owner |
| API/worker → MongoDB | TLS27017; config reader/publisher/event writerแยกrole | คำสั่งconfig/adminและการค้นauditต้องไม่อาศัยรู้documentIdอย่างเดียว |
| API → Redis cache | TLS6379; cache namespace/scriptที่จำกัด | ไม่มีflush/config/admin permission |
| API → Redis admission | TLS6379; bounded limiter operations | memory/ACL/credentialsแยกจากcache; noevictionไม่แก้OOM |
| API → Stripe | HTTPS443 ที่จำเป็นและverifiedcallbacksตามcontract | Signing/API secretsอยู่secret managementไม่ใช่Mongo configdocuments |

Network policiesต้องระบุผู้อนุญาตจริงก่อนdeploy การวางกล่องในsubnetเป็นphysical proposalของself-hostedreference ไม่ใช่คำอ้างว่าmanaged PaaSถูกคุมด้วยsubnetrulesเดียวกัน หากเลือกmanagedserviceต้องวาดendpoint/controlplaneใหม่ให้ตรงprovider

## Health, rollout และการเปลี่ยน secrets

Readinessต้องแยกrole: Redis/MongoDBไม่พร้อมไม่ทำให้valid payment callbackหายไปเพราะทั้งhostถูกถอนจากrouting แต่protectedrouteที่ไม่มีpolicyถูกต้องยังต้องunavailableตามdesign ใช้validatedconfigsnapshotsและตรวจversionก่อนrollout; policyrevisionไม่เท่ากับbucketepoch การrotatecredentialsต้องมีoverlap/reconnect/rollbackที่ทดสอบแล้ว ห้ามlogค่าsecretหรือเพิ่มclientconnectionใหม่ทุกrequest

Replica countsในภาพคือcandidateเพื่อออกแบบ failure domains ไม่ใช่capacity/SLA proof MongoDBสามdata-bearingmembersรองรับlocal transactions/majorityตามsupportedtopologyแต่ยังต้องกำหนดwrite/readconcernและplacement ส่วนRedisreplicationอาจสูญเสียacknowledgedupdatesหลังfailoverตามข้อจำกัดที่researchอธิบาย ต้องทดสอบกับcounterpolicyและclockassumptionsจริง
