---
name: E-commerce Runtime Architecture Explanation
description: คำอธิบายภาพ architecture-design อย่างละเอียด พร้อมเหตุผล ข้อแลกเปลี่ยน และแหล่งอ้างอิง ใช้อ่านประกอบการทบทวน runtime architecture และข้อเสนอ Redis/MongoDB
---

# คำอธิบาย Architecture Design

เอกสารนี้อธิบาย [architecture-design.drawio.png](architecture-design.drawio.png) ซึ่งตอบคำถามว่า **ขณะระบบทำงาน ส่วนใดรับผิดชอบอะไร ติดต่อกันอย่างไร และข้อมูลใดเชื่อถือได้จากที่ใด** อ่านต่อเรื่องตำแหน่งโค้ดได้ใน [Repository Architecture](../reference/repository/repository-architecture.md) และเรื่องสถานะคำสั่งซื้อใน [Order lifecycle](order-lifecycle.md)

## 1. ขอบเขตและสถานะของภาพ

CODE baseline อ้างถึง Component Repository [e-commerce-backend](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/code.md) ที่ pin `d8255183cba54d0c2b218607456b895a70df32f0` ตาม [REPOS.md](https://github.com/ittikornsopawan/system-analysis-and-design/blob/90c589a/e-commerce/REPOS.md) ตำแหน่ง checkout คือ `e-commerce/repository/e-commerce-backend/` มี Git history/remote ของตนเองและถูก ignore โดย Showcase ภาพอธิบาย legacy Authen ที่รักษาไว้ ไม่ได้ปิด known gaps กับ API specifications ใหม่

ภาพรวม runtime ของ backend หนึ่งแอปพลิเคชัน ประกอบกับความสามารถ commerce ที่ระบุในเอกสาร และส่วน Redis/MongoDB ที่ผู้ใช้ขอเพิ่ม ไม่ใช่แผน deployment หรือคำยืนยันว่าทุกความสามารถทำงานจริงแล้ว

| ป้ายในภาพ | ความหมาย | หลักฐานและขอบเขต |
| --- | --- | --- |
| `CODE` | มีโค้ดรองรับส่วนที่ระบุ | Backend ปัจจุบันมี Authen 5 use cases; ไม่ได้หมายความว่าทำตามข้อกำหนด Authen ทุกข้อแล้ว |
| `SPEC` | มีข้อกำหนดอธิบายพฤติกรรม | Order, payment, shipping และ expiry ต้องอ่านข้อกำหนดของแต่ละเรื่อง; ภาพไม่ขยายสถานะอนุมัติให้เอกสารต้นทาง |
| `PROPOSED` | ส่วนที่เสนอเพิ่ม | Redis, MongoDB, outbox, adapters และนโยบายยังอยู่ใน [Redis design](../design/redis-design.md) และ [MongoDB design](../design/mongodb-design.md) สถานะ `in-review` |

ผู้ใช้เลือก MongoDB สำหรับ feature flags/config ทั่วไป รวม cache/rate-limit policy ตลอดจน audit/integration events และสำเนาธุรกรรมสำหรับค้นย้อนหลัง PostgreSQL ยังเป็นข้อมูลหลักของธุรกรรม การเลือกบทบาทนี้ไม่ใช่การอนุมัติค่าทางปฏิบัติทั้งหมด เช่น quota, TTL, retention หรือระยะเวลายอมใช้ config เก่า

## 2. วิธีอ่าน logical containment และ runtime calls

กรอบ `One ASP.NET Core backend` มี native child containers สำหรับ Presentation, Application, Domain, Infrastructure และ Shared แต่ละชั้นมีกล่องหน้าที่จริงภายใน ไม่ได้ยุบ HTTP/CQRS ทั้งหมดไว้ใน host card เดียว กล่องแต่ละใบเป็น editable component; ย้าย parent แล้วลูกยังคงอยู่ภายใต้ขอบเขตเดิม

ภาพนี้ใช้ Architecture ที่เน้น layer decomposition บนพื้นที่ 1584 × 1120 และมี 24 กล่องรายละเอียด แบ่งเป็น core responsibilities, client และ data/external services รายละเอียดระดับ faithful ทำให้เห็น Command/Query, Validator และ Handler จริงภายใน Application ส่วน [Repository Architecture](../reference/repository/repository-architecture.md) ตอบคำถามตำแหน่ง source paths และ project references ด้วย containment ตามไฟล์

การซ้อนเป็น logical ownership ไม่ใช่ลำดับที่ทุก request ต้องผ่านทุกกล่อง ชั้น Shared อยู่ข้าง core เพื่อให้เห็นว่าทั้ง dispatcher และ Result/Error ใช้ร่วมกัน การเรียง Infrastructure ไว้ล่างไม่ได้หมายความว่า Domain reference Infrastructure; compile references ทั้งหมดอยู่ในภาพ repository

เส้นทึบแปดเส้นแสดง runtime collaboration ที่เลือก: client → Controller → Dispatcher, Dispatcher → Validator และเมื่อผ่านจึง Dispatcher → Handler, Handler → Domain ย่อย, Handler → Application ports → Persistence adapter → PostgreSQL กล่อง **Handler คือ Application use case** ที่รับผิดชอบ orchestration ส่วน Domain ย่อยเป็น reusable business logic ตาม owner-directed proposal ไม่ใช่ call ที่พบแล้วใน Authen baseline

Controller สร้าง Command/Query แล้วส่งให้ Dispatcher; input record ไม่เรียก Validator/Handler เอง GetCurrentUser ไม่มี validator ตาม baseline การเรียก Domain และ ports เป็นทางแยกของ use case ไม่ใช่ข้อบังคับให้ Domain เรียก I/O หรือให้ทุก handler เรียกทุกกล่อง เส้นจาก port ไป concrete adapter หมายถึงการเรียก implementation ที่ DI bind ไว้ ไม่ใช่ compile reference จาก Application ไป Infrastructure ไม่มีลูกศร `IMPLEMENTS` ปะปนกับ runtime calls ภาพ repository เก็บเป็น reference; ใช้ project-structure.md สำหรับหา source/tests

## 3. การแยกหน้าที่ภายใน backend

### 3.1 Presentation — HTTP และ composition

กล่อง Controllers แสดง `AuthenController` ที่รับ HTTP แล้วสร้าง command/query; Contracts & HTTP results แสดง `AuthenRequests` และ `ResultExtensions` ซึ่งแปลง `Result` เป็น status/ProblemDetails; Composition & security แสดง `Program.cs` ที่เรียก `AddCqrs`, `AddInfrastructure` และตั้ง JWT authentication/authorization

แยกทั้งสามกล่องเพราะ request contract, HTTP mapping และ dependency wiring เป็นคนละหน้าที่ แม้อยู่ project เดียวกัน `Program.cs` เป็น composition root ไม่ใช่ handler หรือที่เก็บกฎ order และ source นี้ยังมี Authen endpoints ห้า use cases เท่านั้น ดู [Program.cs](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Api/Program.cs) และ [AuthenController.cs](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Api/Controllers/AuthenController.cs)

### 3.2 Application — Command/Query, Validator, Handler, Mapping และ ports

| กล่องในภาพ | ส่วนที่ตรวจพบจริง | เหตุผลที่แยก |
| --- | --- | --- |
| Command / Query | `RegisterCommand`, `LoginCommand`, `RequestPasswordResetCommand`, `ResetPasswordCommand`, `GetCurrentUserQuery` | Input records ระบุเจตนา use case โดยไม่ผูก HTTP |
| Validator | Validators ของสี่ commands; query `/me` ไม่มี validator ใน source | ตรวจรูปแบบผ่าน Domain value objects ก่อนทำงานที่มีผลข้างเคียง |
| Handler | Handlers ทั้งห้า use cases | ประสานกฎ model, repository/security ports และ transaction ตาม use case |
| Mapping & responses | `AuthenMappings` และ response records | ไม่ส่ง Domain entity ออกผ่าน public response โดยตรง |
| Application ports | `IUnitOfWork`, `IPasswordHasher`, `ITokenService`, `IEmailSender` | ชั้นในระบุความสามารถที่ต้องการ ขณะ Infrastructure จัด implementation |

[Dispatcher.cs](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Shared/Cqrs/Dispatcher.cs) รวม errors จาก validators ที่ลงทะเบียน เมื่อมี error จะคืน failure โดยไม่เรียก handler เมื่อไม่มี error จึง resolve handler แล้วเรียก `HandleAsync` ลูกศร dispatcher → handler ในภาพต้องอ่านร่วมกับ guard นี้ ไม่ใช่คำกล่าวว่าทุก input ผ่าน validation สำเร็จ

กล่องหน้าที่เป็นการรวมหลาย use cases เพื่อการอ่าน ไม่ใช่โฟลเดอร์กลางที่สร้างใหม่ โค้ดจัดตาม `Features/Authen/<UseCase>/` CQRS ใน source นี้ไม่ตั้ง broker, event sourcing หรือฐานข้อมูล query แยกโดยอัตโนมัติ

Cache/rate/config snapshot และ event/projection contracts เป็น **PROPOSED** ภายในกล่อง ports เท่านั้น ชื่อและ outage/consistency contract ต้องผ่าน review ก่อน implement ไม่ import Redis/MongoDB types เข้าชั้น Domain เพียงเพราะเพิ่ม data services

### 3.3 Domain — entities, value objects, contracts และ reusable business logic

สามกล่องที่เป็น CODE บอกว่า `User`/`PasswordResetToken` ดูแลสถานะและพฤติกรรม, `Username`/`EmailAddress`/`PlainPassword` ดูแลค่าที่ valid และ normalized, ส่วน `IUserRepository`/`IPasswordRepository`/`ITokenRepository` ระบุการเข้าถึงข้อมูลที่ use cases ต้องใช้โดยไม่รู้ SQL

กล่องที่สี่ `Domain` เพิ่มตาม owner convention สำหรับ business logic ที่ใช้ซ้ำ และแสดง `PROPOSED · OWNER REQUEST` แยกจาก CODE อ่านเหตุผลและขอบเขตการเรียกใช้ในหัวข้อ Domain ย่อยด้านล่าง

การแยกนี้ช่วยทดสอบกฎชั้นในโดยไม่เปิด HTTP/connection แต่ interface ไม่ได้ยกเลิกความจำเป็นของ transaction, constraint และ concurrency guards โค้ด Authen ที่มีอยู่ไม่ใช่หลักฐานว่า commerce rules และ SQL account/session ทุกข้อ implement ครบแล้ว ดู [project-structure.md](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/project-structure.md)

### 3.4 Infrastructure — persistence, security, email/payment และ proposed data adapters

Persistence รวม Dapper/Npgsql, scoped `DbSession`, repository implementations และ `UnitOfWork`; Security รวม PBKDF2, JWT/token operations และ `FieldProtector` กล่อง Email/payment ระบุสถานะแยกกัน: `LoggingEmailSender` มี **CODE** และเป็น development stub ส่วน Stripe intent/refund เป็น **SPEC** ยังไม่มี adapter ที่ implement ใน backend นี้

Data adapters เป็นกล่อง **PROPOSED** ต่างหากสำหรับ Redis cache/rate และ MongoDB config/projections ไม่ทำให้เข้าใจว่า SDKs หรือ files เหล่านี้มีอยู่แล้ว [DependencyInjection.cs](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Infrastructure/DependencyInjection.cs) ยืนยันบริการที่ลงทะเบียนจริง ส่วนการเพิ่ม adapter ต้องรักษา lifetime/configuration/error semantics ของแต่ละ role

### 3.5 Shared — dispatch และ expected results

Shared มีสองกล่อง: CQRS dispatcher/messaging/assembly scanning และ `Result`/`Error` Dispatcher เป็น reusable coordination primitive ที่ Application ใช้งาน แต่ validator/handler implementations ยังอยู่ใน Application ความล้มเหลวที่คาดหมายเป็นค่า failure ไม่ใช้ exception เป็น flow control หลัก ภาพจึงไม่ย้าย use-case code ทั้งหมดมาอยู่ Shared

## Domain ย่อย — business logic ที่ใช้ซ้ำ

ตามคำชี้แจงของเจ้าของงานวันที่ 2026-11-08 เพิ่มกล่องชื่อ **`Domain`** ภายใน **Domain Layer** เป็น sibling ของ Entities, Value objects และ Repository contracts กล่องนี้หมายถึงความรับผิดชอบที่มักเรียก domain service แต่ใช้ชื่อ `Domain` ตาม convention ของโครงการ ไม่ได้เพิ่ม process, network service หรือ `.csproj` ใหม่

ใช้สำหรับกฎ/การดำเนินการทางธุรกิจที่หลาย use cases เรียกใช้ หรือไม่เหมาะจะผูกเป็นพฤติกรรมของ entity เดียว เช่นการคำนวณภาษีจากยอดเงินและ policy ที่ส่งเข้ามา ตัวอย่างนี้อธิบายชนิดของงานเท่านั้น ไม่กำหนดสูตร อัตรา หรือกฎการปัดเศษ และไม่อ้างว่ามี tax implementation ใน Authen แล้ว

| ส่วน | หน้าที่และเหตุผล |
| --- | --- |
| Application Handler | โหลดข้อมูล/สิทธิ์ ประสานลำดับ use case เรียก `Domain` แล้วบันทึกผ่าน transaction ports ลดการคัดลอกสูตรระหว่าง handlers |
| Domain ย่อย | รับ business values และ policy ที่จำเป็น คำนวณ/ใช้กฎ และคืนผลที่นำไปใช้ซ้ำได้ ไม่รับ HTTP DTO, SDK client หรือควบคุม SQL commit |
| Entity / Value object | รักษา invariant ของตัวเอง เช่นค่าที่ถูกต้องและ transition ที่อนุญาต ไม่ย้ายกฎเหล่านี้ออกทั้งหมดเพียงเพราะมี `Domain` ย่อย |
| Infrastructure | ติดต่อ PostgreSQL, Redis, MongoDB และ provider ตาม ports; การอ่าน config snapshot/อัตราภายนอกแยกจากการคำนวณใน Domain |

เส้นทางเชิงแนวคิดคือ **Handler → Domain → business result → Handler → persistence** Domain ย่อยเป็นโค้ดภายใน core ใช้ร่วมกับ entities/value objects ได้ แต่ไม่ reference Application หรือ concrete Infrastructure กฎที่ต้องใช้ข้อมูลภายนอกให้ส่งข้อมูลเข้ามาหรือใช้ inner abstraction ที่มี contract ชัดเจน เหตุผลคือทดสอบ business rule ด้วย input เดิมได้โดยไม่ต้องต่อเครือข่าย และไม่ผูกสูตรเข้ากับ endpoint หรือ data-store vendor [Microsoft: Application Core และ domain services](https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures)

ตำแหน่งตัวอย่างที่เจ้าของงานกำหนดคือ `e-commerce/repository/e-commerce-backend/src/Ecommerce.Domain/Authen/Domain/` สำหรับกฎของ Authen ที่ใช้ซ้ำ กฎภาษี/เงินควรอยู่ใต้ feature ที่เป็นเจ้าของกฎนั้น เช่น `<CommerceFeature>/Domain/` ไม่ทำให้ Authen หรือ Shared เป็นที่รวมกฎทุกเรื่อง

สถานะกล่องใหม่คือ `PROPOSED · OWNER REQUEST`: เจ้าของงานกำหนดโครงสร้างสำหรับภาพแล้ว แต่ remote tree ที่ pin `d8255183cba54d0c2b218607456b895a70df32f0` ยังไม่มี `Authen/Domain/` จึงไม่ติดป้าย `CODE` และงานนี้ไม่สร้าง backend folder/class หรือเปลี่ยน business behavior

## 4. Data/external services และสิ่งที่ละจากลูกศร

| กล่อง | Authority / status | ขอบเขตความสอดคล้อง |
| --- | --- | --- |
| PostgreSQL | **CODE adapters + SPEC business authority** | Account/order/payment/refund/stock/budget อาศัย SQL constraints, locks และ transaction |
| MongoDB | **PROPOSED** config source + derived audit/event/status projections | Non-secret configuration มี revision; transaction copies อาจตามหลัง SQL และไม่ใช้ตัดสินเงิน/stock |
| Redis public cache | **PROPOSED** rebuildable public descriptors | Live visibility/price/stock ยังตรวจ SQL; invalidate หลัง commit; isolated `allkeys-lfu` |
| Redis shared admission | **PROPOSED** shared token buckets | แยก `noeviction` memory domain; quota 429 ต่างจาก protected-store outage 503; signed webhook ไม่ผ่าน user quota |
| Stripe | **SPEC** external provider | PaymentIntent/refund, client Stripe.js, signed raw-body webhook; browser completion ไม่ยืนยัน paid |

เส้น SQL เป็น data path ที่มี code รองรับ ส่วน proposed Redis/MongoDB calls และ specified Stripe calls ไม่ขยายเป็น spokes ทุกเส้น เพราะจะเบียด layer decomposition ซึ่งเป็นคำถามหลักของภาพ การไม่มีลูกศรใน view นี้ไม่ได้แปลว่า data service ติดต่อ backend ไม่ได้; semantic contracts อยู่ใน [Redis design](../design/redis-design.md) และ [MongoDB design](../design/mongodb-design.md), Stripe interaction อยู่ [payment/01](../../doc/api/payment/01-start-payment/spec.md) และ [payment/02](../../doc/api/payment/02-stripe-webhook/spec.md)

หมายเหตุใต้ service rail ระบุข้อเสนอ transactional outbox: business mutation และ publication intent commit ใน PostgreSQL transaction เดียว จากนั้น relay ส่ง MongoDB ด้วย stable event ID/source version; MongoDB ล่มไม่สั่ง charge หรือ stock movement ซ้ำ ไม่มี transaction ร่วมระหว่าง PostgreSQL/MongoDB และ worker host ยังไม่ได้เลือก ไม่วาด broker/worker deployment ขึ้นเอง

MongoDB config ไม่เก็บ credentials/signing/encryption keys และไม่เป็น authorization grant; live PostgreSQL permission check ยังใช้ตามข้อกำหนด ค่าตัวเลขเรื่อง TTL, quota, last-known-good age, refresh interval และ retention เป็น proposal ที่ต้องอ่านสถานะ/ข้อจำกัดในเอกสารต้นทาง ไม่มี automatic TTL deletion จนกว่าจะอนุมัติ collection-specific retention

Expiry และ automatic completion หลังเจ็ดวันยังเป็น **SPEC** ที่ใช้ SQL guards การจัดวาง responsibility ไว้ในหมายเหตุแทน worker box ช่วยไม่อ้าง host หรือ scheduler ที่ยังไม่มีการเลือก และไม่เพิ่ม order status ใหม่

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

- [README ของชุดภาพ](../README.md), [semantic source](../scripts/layered_core_content.py) และ [research ของรูปแบบภาพ](../design/research.md) ใช้ตรวจเนื้อหา/การจัดมุมมอง
- [Backend project structure](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/project-structure.md), [Program.cs](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Api/Program.cs) และ [Infrastructure DI](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Infrastructure/DependencyInjection.cs) ใช้ยืนยันส่วนที่มีโค้ด
- [Redis design](../design/redis-design.md), [Redis research](../design/redis-research.md) และ [Redis review](../design/redis-review.md) ใช้พิจารณานโยบายและข้อจำกัดของข้อเสนอ
- [MongoDB design](../design/mongodb-design.md) และ [MongoDB research](../design/mongodb-research.md) ใช้ตรวจ config ownership, event projections และ cross-store delivery
- [Order lifecycle explanation](order-lifecycle.md) เชื่อม runtime decisions กับ order/payment/shipping guards โดยข้อกำหนด API ที่ลิงก์ไว้ยังเป็นต้นทางของรายละเอียดธุรกิจ

[กลับสารบัญ diagram](../README.md)
