---
name: E-commerce Runtime Architecture Explanation
description: คำอธิบายภาพ architecture-design อย่างละเอียด พร้อมเหตุผล ข้อแลกเปลี่ยน และแหล่งอ้างอิง ใช้อ่านประกอบการทบทวน runtime architecture และข้อเสนอ Redis/MongoDB
---

# คำอธิบาย Architecture Design

เอกสารนี้อธิบาย [architecture-design.drawio.png](architecture-design.drawio.png) ซึ่งตอบคำถามว่า **ขณะระบบทำงาน ส่วนใดรับผิดชอบอะไร ติดต่อกันอย่างไร และข้อมูลใดเชื่อถือได้จากที่ใด** อ่านต่อเรื่องตำแหน่งโค้ดได้ใน [Repository Architecture](repository-architecture.md) และเรื่องสถานะคำสั่งซื้อใน [System Design](system-design.md)

## 1. ขอบเขตและสถานะของภาพ

ภาพรวม runtime ของ backend หนึ่งแอปพลิเคชัน ประกอบกับความสามารถ commerce ที่ระบุในเอกสาร และส่วน Redis/MongoDB ที่ผู้ใช้ขอเพิ่ม ไม่ใช่แผน deployment หรือคำยืนยันว่าทุกความสามารถทำงานจริงแล้ว

| ป้ายในภาพ | ความหมาย | หลักฐานและขอบเขต |
| --- | --- | --- |
| `CODE` | มีโค้ดรองรับส่วนที่ระบุ | Backend ปัจจุบันมี Authen 5 use cases; ไม่ได้หมายความว่าทำตามข้อกำหนด Authen ทุกข้อแล้ว |
| `SPEC` | มีข้อกำหนดอธิบายพฤติกรรม | Order, payment, shipping และ expiry ต้องอ่านข้อกำหนดของแต่ละเรื่อง; ภาพไม่ขยายสถานะอนุมัติให้เอกสารต้นทาง |
| `PROPOSED` | ส่วนที่เสนอเพิ่ม | Redis, MongoDB, outbox, adapters และนโยบายยังอยู่ใน [Redis design](redis-design.md) และ [MongoDB design](mongodb-design.md) สถานะ `in-review` |

ผู้ใช้เลือก MongoDB สำหรับ feature flags/config ทั่วไป รวม cache/rate-limit policy ตลอดจน audit/integration events และสำเนาธุรกรรมสำหรับค้นย้อนหลัง PostgreSQL ยังเป็นข้อมูลหลักของธุรกรรม การเลือกบทบาทนี้ไม่ใช่การอนุมัติค่าทางปฏิบัติทั้งหมด เช่น quota, TTL, retention หรือระยะเวลายอมใช้ config เก่า

## 2. วิธีอ่านขอบเขต สี และเส้น

กรอบ `BACKEND / PRIMARY DATA BOUNDARY` จัดกลุ่ม backend และ PostgreSQL ส่วนกรอบ `ONE BACKEND APPLICATION / IN-PROCESS CORE AND ADAPTERS` ชี้ว่า API, use cases, Domain และ Infrastructure อยู่ในแอปพลิเคชันเดียว การวาง MongoDB/Redis นอกกรอบนี้แยกบทบาท data services ไม่ได้กำหนดว่าต้องอยู่คนละเครือข่ายหรือผู้ดูแล

สีส้มเน้น API host ซึ่งเป็นจุดประสานการทำงาน กรอบเส้นประใช้กับส่วน specified/proposed และระบบภายนอก ต้องอ่านป้ายสถานะร่วมด้วย เพราะเส้นประเพียงอย่างเดียวไม่ได้แปลว่า asynchronous ทุกเส้น เส้นสีน้ำเงินเป็นเส้นทาง Stripe ที่ระบุในข้อกำหนด

ภาพมี 9 องค์ประกอบและ 11 ความสัมพันธ์ รวม HTTP/CQRS ไว้ในกล่อง host เดียวเพื่อให้เห็นภาพรวม โดยรายละเอียด 5 production projects อยู่ในภาพ repository การแยก logical layers ไม่จำเป็นต้องแยก deployment units; เอกสาร Microsoft อธิบายความแตกต่างนี้ไว้ใน [Common web application architectures](https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures)

## 3. องค์ประกอบทั้งเก้า

### 3.1 Client touchpoints

ลูกค้าใช้ดูสินค้า จัดการตะกร้า สั่งซื้อ ชำระเงิน และยืนยันรับสินค้า สมาชิกของร้านจัดการ stock/price/parcels ส่วนผู้ดูแลแพลตฟอร์มจัดการ master data, roles และ campaigns กล่องนี้แสดงบทบาทผู้ใช้ ไม่ได้หมายถึงมี frontend ทั้งสามตัวอยู่ใน repository

เหตุผลที่แยก client ออกจาก backend คือสิทธิ์และความถูกต้องต้องตรวจฝั่งเซิร์ฟเวอร์ แม้หน้าจอซ่อนปุ่มไว้ ผู้เรียกยังส่งคำขอโดยตรงได้ ข้อมูลบัตรถูกส่งผ่าน Stripe.js ตามการออกแบบ payment ไม่ผ่าน commerce API

### 3.2 API host · HTTP, CQRS & use cases

เส้นทางที่มีโค้ดคือ `AuthenController → IDispatcher → validator → handler → Result/ProblemDetails` ส่วน `/me` ใช้ JWT Bearer และ `Program.cs` ประกอบ dependency injection ข้อมูลยืนยันได้จาก [Program.cs](../repository/src/Ecommerce.Api/Program.cs), [AuthenController.cs](../repository/src/Ecommerce.Api/Controllers/AuthenController.cs) และ [Dispatcher.cs](../repository/src/Ecommerce.Shared/Cqrs/Dispatcher.cs)

Controller แปลง HTTP เป็น command/query, validator ตรวจรูปแบบและกฎอินพุต, handler ประสาน use case แล้วส่งผลกลับ เหตุผลที่แบ่งหน้าที่เช่นนี้คือกฎธุรกิจไม่ผูกกับ HTTP และทดสอบ handler โดยไม่ต้องเปิดเว็บเซิร์ฟเวอร์ได้ CQRS ในที่นี้แยก command/query ไม่ได้บังคับให้มี broker หรือฐานข้อมูลคนละชุด

ส่วนที่เสนอเพิ่มคือ quota checks ก่อนเข้า handler, public metadata cache ผ่าน interface ฝั่งใน และ config snapshots/event-projection ports กล่อง host ไม่ได้ประกาศว่า middleware หรือ commerce handlers เหล่านี้มีอยู่แล้ว

### 3.3 Domain model & interfaces

Domain ปัจจุบันมี `User`, `PasswordResetToken`, value objects เช่น `Username`, `EmailAddress`, `PlainPassword` และ repository interfaces กฎของ entity/value object อยู่ใกล้ข้อมูลที่ต้องคุ้มครอง อ้างอิง [project-structure.md](../repository/project-structure.md)

เหตุผลที่ไม่ให้ Domain รู้จัก HTTP, SQL หรือ Redis/MongoDB SDK คือกฎธุรกิจไม่ควรเปลี่ยนเพราะย้ายเทคโนโลยีจัดเก็บ อย่างไรก็ตาม interface ไม่ได้ทำให้การเปลี่ยนฐานข้อมูลเป็นงานฟรี ความหมายเรื่อง transaction, ordering และ consistency ยังต้องออกแบบให้ตรง use case

### 3.4 Infrastructure adapters

ชั้นนี้แปลง interface เป็นเทคโนโลยีจริง ได้แก่ Dapper/Npgsql, scoped `DbSession`, password hashing, JWT และ field encryption ส่วน email ปัจจุบันเป็น `LoggingEmailSender` สำหรับพัฒนา ไม่ใช่บริการส่งอีเมล production หลักฐานอยู่ใน [DependencyInjection.cs](../repository/src/Ecommerce.Infrastructure/DependencyInjection.cs)

Redis/MongoDB adapters เป็นข้อเสนอให้เพิ่มในชั้นนี้ ส่วน Stripe ยังเป็น integration ตาม specification เหตุผลคือความรู้เรื่อง connection, serialization, retry และ SDK ควรอยู่ที่ขอบระบบ ขณะที่ Application กำหนดว่าต้องการผลลัพธ์อะไร

### 3.5 PostgreSQL business authority

PostgreSQL เป็นข้อมูลหลักของ stock/lot, ราคาที่ checkout, order/payment/refund, campaign budget ตลอดจน account/session/permission ใช้ transaction, constraints, locks และเงื่อนไขสถานะใน SQL เพื่อป้องกันข้อมูลขัดแย้ง ดู [สร้างคำสั่งซื้อ](../doc/api/sales/02-create-order/spec.md), [Stripe webhook](../doc/api/payment/02-stripe-webhook/spec.md) และ [ยกเลิกคำสั่งซื้อ](../doc/api/sales/05-cancel-order/spec.md)

เหตุผลที่ยังคง authority นี้คือการขายสินค้าคงเหลือและการคืนเงินต้องตัดสินจากข้อมูลที่ประสานกันได้ในขอบเขตธุรกรรมหลัก Cache ที่เก่าหรือ transaction copy ที่ส่งช้าไม่เหมาะใช้ตัดสินเรื่องเงิน

`transactional outbox intent` ยังเป็นข้อเสนอ: บันทึกการเปลี่ยนข้อมูลธุรกิจและความตั้งใจส่ง event ใน PostgreSQL transaction เดียวกัน จากนั้นส่งต่อภายหลัง เหตุผลคือหลีกเลี่ยงช่องว่างที่ธุรกรรมสำเร็จแล้ว process ตายก่อนเขียน MongoDB

### 3.6 MongoDB config & event documents

MongoDB มีสองบทบาทที่มีความเป็นเจ้าของต่างกัน:

| ข้อมูล | บทบาท MongoDB | เหตุผล |
| --- | --- | --- |
| Feature flags และ config ที่ไม่ใช่ secrets | ข้อมูลหลักของ config ที่ผ่าน validation/versioning | แยกการเผยแพร่และตรวจย้อนหลัง config ออกจากธุรกรรม order |
| Cache/rate-limit policies | แหล่ง published policy; แอปอ่านเป็น local snapshot | ไม่ต้อง query MongoDB ทุก request และไม่พึ่ง Redis เพื่ออ่าน policy ของ Redis เอง |
| Audit/integration events | หลักฐานกิจกรรมและการส่งข้อมูลตามขอบเขตที่เลือก | ค้นตาม event/source/correlation ได้โดยไม่ใช้เป็น financial ledger |
| Transaction copies | Derived projections ที่อาจตามหลัง PostgreSQL | รองรับ operational search โดยไม่เปลี่ยน authority ของ order/payment |

เสนอ collections ได้แก่ `runtime_config_current`, `runtime_config_revisions`, `application_audit_events`, `integration_events` และ `transaction_status_projections` ชื่อเหล่านี้เป็น design candidates ยังไม่มี collection provisioning หรือ migration ในงานนี้

การ publish config ต้องตรวจสิทธิ์จริงจาก PostgreSQL, validate รูปแบบ/ช่วงค่า และตรวจ revision เพื่อไม่เขียนทับงานพร้อมกัน อาจใช้ MongoDB-local transaction รวม current/revision/audit ตามข้อเสนอ แต่ไม่ได้ครอบคลุม PostgreSQL; [MongoDB Transactions](https://www.mongodb.com/docs/manual/core/transactions/) อธิบาย transaction ภายใน MongoDB การเลือก outbox สำหรับข้ามสองระบบเป็นข้อสรุปของแบบนี้ ไม่ใช่คุณสมบัติที่ MongoDB ทำให้อัตโนมัติ

Transaction projections ใช้ stable event ID ป้องกันซ้ำ และ source version ป้องกัน event เก่าทับ snapshot ใหม่ เริ่มจาก status/references และจำกัดผู้อ่านเป็น operational/admin ไม่คัดลอกบัตร รหัสผ่าน token หรือ payload ส่วนตัวทั้งหมด ไม่มี automatic TTL จนกว่าจะอนุมัติ retention/capacity แยกตาม collection ดูรายละเอียดใน [MongoDB design](mongodb-design.md)

### 3.7 Stripe payment provider

Client ยืนยันการชำระผ่าน Stripe.js, backend สร้าง/ใช้ PaymentIntent และเรียก refund ส่วน signed raw-body webhook เป็นหลักฐานให้ backend ประมวลผล payment event ตาม guard ใน SQL การกลับมาหน้า success ของ browser ไม่ทำให้ order paid

เหตุผลคือ browser ถูกปิด เปลี่ยนหน้า หรือส่งข้อมูลปลอมได้ ส่วน provider events อาจซ้ำ/มาช้า จึงต้องตรวจ signature และใช้ idempotency/เงื่อนไขสถานะร่วมกัน Stripe integration ในภาพเป็นข้อกำหนด ยังไม่ใช่ adapter ที่ยืนยันการทำงานจริงใน codebase นี้

### 3.8 Redis public read cache

เสนอ cache เฉพาะ public metadata เช่นชื่อ/คำอธิบาย/labels และ image references ที่อนุญาต ไม่ cache response ทั้งก้อน ราคาปัจจุบัน stock การมองเห็นสินค้า สิทธิ์ cart/order/profile/token ยังคงตรวจจาก PostgreSQL

ใช้ cache-aside: ตรวจ cache, miss แล้วอ่านข้อมูลหลักและเติม cache, เปลี่ยนข้อมูลหลักสำเร็จก่อน invalidate แนวคิดพื้นฐานมีใน [Microsoft Cache-Aside](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside) ส่วนการจำกัด public projection และ generation guards เป็นการออกแบบเฉพาะของโครงการนี้

TTL ที่เสนอคือ product descriptors สุ่ม 48–60 วินาที และ taxonomy labels 240–300 วินาที เพื่อลดการหมดอายุพร้อมกัน ใช้ random generation แยกข้อมูลแต่ละรุ่นและตรวจ generation ก่อน read/fill เพื่อไม่ให้ reader เก่าเติมข้อมูลทับรุ่นใหม่ เริ่มนับอายุจากเวลาเริ่มอ่าน source ไม่ใช่ตอนเขียน cache เสร็จ

ข้อแลกเปลี่ยนคือยังต้อง query SQL สำหรับ live eligibility และ dynamic values จึงไม่ได้ลด SQL ทุกครั้ง ประโยชน์จริงต้องวัด การรับรองความสดมีเงื่อนไข clock/failover ตาม proposal; ป้าย `Hard TTL` ในภาพไม่ใช่คำรับประกัน elapsed time ระหว่างนาฬิกาผิดปกติ เมื่อ cache ใช้ไม่ได้ให้อ่าน SQL พร้อมควบคุม refill concurrency

### 3.9 Redis distributed rate store

เสนอ shared token buckets สำหรับ API หลาย instances โดยหนึ่ง atomic Lua operation คำนวณ refill/admit/deduct/idle TTL ผ่าน Redis server time ตัวตนมาจาก trusted client IP หรือ validated user แล้วแปลงเป็น HMAC ไม่ใช้ email/IP ดิบใน key

ปฏิเสธเพราะ quota หมดเป็น `429` พร้อม `Retry-After` แต่ store timeout/OOM เป็นความขัดข้อง ไม่ใช่หลักฐานว่า quota หมด จึงเสนอ sensitive routes ตอบ `503` ขณะที่ read routes ใช้ local degraded limits ซึ่ง **ไม่รักษา quota รวมทั้ง fleet** รายการ quota/burst ตัวเลขทั้งหมดอยู่ใน [Redis design](redis-design.md) และยังไม่ใช่ production capacity ที่ทดสอบแล้ว

Signed webhooks และ internal expiry ไม่ผ่าน user quota ชุดนี้ แต่ยังต้องมี signature/SQL guards และการคุ้มครอง body/concurrency ที่เหมาะสม การแยกนี้ป้องกัน Redis outage ขวางการรับรู้ผลชำระเงิน โดย host readiness ต้องไม่ผูกกับ Redis ทั้งระบบ

## 4. ความสัมพันธ์ทั้งสิบเอ็ดในภาพ

| จาก → ไป | ป้าย/ความหมาย | เหตุผลที่แสดง |
| --- | --- | --- |
| Client → API host | `HTTP / JSON` | จุดเข้าหลักของ use case |
| API host → Domain | `RULES` | ใช้กฎของ model/value objects |
| API host → Infrastructure | `VIA PORTS` | เรียกความสามารถภายนอกผ่าน interface ที่ DI จัดให้ |
| Infrastructure → Domain | `IMPLEMENTS` | Adapter ทำตาม inner contracts; เป็นความสัมพันธ์เชิง interface ไม่ใช่ HTTP hop |
| Infrastructure → PostgreSQL | `SQL` | อ่าน/เขียน business authority |
| Infrastructure → MongoDB | `DOCS` | Config และ event/projection operations ที่เสนอ; ลูกศรไม่สัญญาว่าทุก operation เป็น synchronous |
| Client → Stripe | `STRIPE.JS` | ข้อมูลบัตรอยู่บน provider path |
| Infrastructure → Stripe | `STRIPE API` | สร้าง/reuse intent และ refund ตาม specification |
| Stripe → API host | `SIGNED EVENT` | แจ้งผลที่ต้องตรวจ signature และ SQL guards |
| Infrastructure → Redis cache | `CACHE` | อ่าน/เติม/invalidate public metadata |
| Infrastructure → Redis rate store | `LIMITS` | ตัดสิน admission ร่วมกันหลาย instances |

ลูกศร runtime ไม่ใช่ `.csproj` references โดยเฉพาะ API เรียก adapter ผ่าน port ได้โดย Application ไม่ต้อง reference Infrastructure ส่วน outbox relay เป็น responsibility ที่อธิบายในกล่องและเอกสาร ยังไม่เลือกรูปแบบ worker host หรือเพิ่ม broker

## 5. เหตุผลที่ Redis แยกเป็นสองบริการ

Cache เป็นข้อมูลสร้างใหม่ได้ จึงเสนอ `allkeys-lfu` ให้ลบ key ที่ใช้น้อยเมื่อ memory เต็ม ส่วน rate counters ถ้าถูก evict จะเหมือนได้ burst ใหม่ จึงเสนอ `noeviction` พร้อมขอบเขต memory แยกกัน การเปลี่ยน prefix หรือ logical database number ไม่ทำให้มี eviction budget อิสระ เหตุผลการแยกนี้อาศัยพฤติกรรม [Redis Key eviction](https://redis.io/docs/latest/develop/reference/eviction/) แล้วนำมาประเมินผลต่อ quota ของโครงการ

ต้นทุนคือมีบริการ/credentials/monitoring เพิ่มขึ้น และ `noeviction` ทำให้ allocation ล้มเหลวเมื่อเต็ม จึงยังต้องกำหนด cardinality/memory budget และ aggregate ingress protection การแยกบริการไม่ใช่หลักฐานว่าทน address churn ได้แล้ว และ failover อาจทำให้ counter updates บางส่วนหายตามข้อจำกัดใน proposal

## 6. ตัวอย่างการทำงานร่วมกัน

### อ่านข้อมูลสินค้า

1. ตรวจ public quota ตามตัวตนที่เชื่อถือได้
2. PostgreSQL เลือกสินค้า/child IDs ที่มองเห็นได้ พร้อมราคาและ stock ปัจจุบัน
3. อ่าน public descriptors จาก Redis ถ้า miss/ผิด generation/clock ผิดปกติ ให้อ่าน SQL และเติมตามกฎ
4. สร้าง response ใหม่ ไม่ reuse authorization headers/request IDs จาก cache

ผลที่ต้องการคือข้อมูลแสดงผลบางส่วนอ่านซ้ำได้เร็วขึ้น โดยไม่เปิดเผยสินค้าที่ถูกปิดหรือใช้ราคาเก่าตัดสินการซื้อ

### บันทึกธุรกรรมและส่งสำเนา

1. ผ่าน authorization/admission แล้วใช้ SQL guards ของ use case
2. Commit ข้อมูลธุรกิจและ outbox intent ใน PostgreSQL transaction เดียวตามข้อเสนอ
3. Invalidate cache ที่เกี่ยวข้องหลัง commit; cache failure ไม่ย้อน business commit
4. Relay อ่าน publication intent และเขียน MongoDB ด้วย stable IDs/source version
5. ถ้า MongoDB ล่ม ให้รอ/retry/reconcile การเผยแพร่ ไม่เรียก charge หรือ stock mutation เดิมใหม่

จึงมีช่วงที่ PostgreSQL ใหม่กว่า MongoDB ได้ หน้าค้นย้อนหลังต้องแสดง source version/time และไม่ใช้ copy อนุมัติการคืนเงิน

### เปลี่ยน config

ผู้ดูแลที่ผ่าน live permission check ส่งค่าที่ผ่าน validation พร้อม expected revision จากนั้น publish current/history/audit ตาม MongoDB-local consistency แอปโหลด validated immutable snapshot และตาม revision ด้วย change-stream hints รวม periodic reconciliation ข้อเสนอให้ poll 30 วินาทีและใช้ last-known-good สูงสุด 5 นาทีระหว่าง outage ยังรออนุมัติ การแก้ banner/TTL ไม่ทำให้ Redis bucket epoch เปลี่ยนอัตโนมัติ

## 7. ความเสี่ยง ข้อแลกเปลี่ยน และสิ่งที่ยังไม่พิสูจน์

| ประเด็น | ผลต่อแบบ | สิ่งที่ต้องตรวจภายหลัง |
| --- | --- | --- |
| Cache เก่า/clock ย้อน/failover | Bypass เมื่อความสดเชื่อถือไม่ได้; ไม่ใช้ cache เป็น money/access authority | Clock/failover และ stale-fill tests |
| Cold cache หรือ Redis outage | SQL load เพิ่มแม้ correctness ยังพึ่ง SQL | Refill concurrency และ load test หลาย instances |
| Rate store เต็ม/ล่ม | Sensitive routes อาจ 503; read fallback เป็น local | Sizing, cardinality, NAT impact และ outage policy |
| MongoDB/projection lag | ประวัติค้นอาจตามหลัง business state | Outbox replay/order/version/reconciliation tests |
| Config เก่า/หาไม่เจอ | ใช้ LKG ตามอายุที่อนุมัติ; protected operations ต้องไม่เลือก policy ที่ผ่อนปรนเอง | Cold start, stale config, revision conflict tests |
| Data services เพิ่มขึ้น | เพิ่มต้นทุนดูแลและ secrets/permissions | Capacity, retention, monitoring และ operational ownership |

เอกสารนี้เป็นคำอธิบายภาพ ไม่เปลี่ยน policy ต้นทาง ไม่มี Redis/MongoDB runtime, failover/load/security tests หรือ backend build ในงานอธิบายนี้ Hosting/replicas/gateway, expiry/7-day completion worker host และ outbox worker host ยังไม่ได้เลือก

## 8. แหล่งหลักฐานและเอกสารที่ต้องอ่านร่วมกัน

- [README ของชุดภาพ](README.md), [semantic source](diagram_content.py) และ [research ของรูปแบบภาพ](research.md) ใช้ตรวจเนื้อหา/การจัดมุมมอง
- [Backend project structure](../repository/project-structure.md), [Program.cs](../repository/src/Ecommerce.Api/Program.cs) และ [Infrastructure DI](../repository/src/Ecommerce.Infrastructure/DependencyInjection.cs) ใช้ยืนยันส่วนที่มีโค้ด
- [Redis design](redis-design.md), [Redis research](redis-research.md) และ [Redis review](redis-review.md) ใช้พิจารณานโยบายและข้อจำกัดของข้อเสนอ
- [MongoDB design](mongodb-design.md) และ [MongoDB research](mongodb-research.md) ใช้ตรวจ config ownership, event projections และ cross-store delivery
- [System Design explanation](system-design.md) เชื่อม runtime decisions กับ order/payment/shipping guards โดยข้อกำหนด API ที่ลิงก์ไว้ยังเป็นต้นทางของรายละเอียดธุรกิจ
