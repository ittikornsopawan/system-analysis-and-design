---
name: E-commerce Runtime Architecture Explanation
description: คำอธิบายภาพ architecture-design อย่างละเอียด พร้อมเหตุผล ข้อแลกเปลี่ยน และแหล่งอ้างอิง ใช้อ่านประกอบการทบทวน runtime architecture และข้อเสนอ Redis/MongoDB
---

# คำอธิบาย Architecture Design

เอกสารนี้อธิบาย [architecture-design.drawio.png](architecture-design.drawio.png) ซึ่งตอบคำถามว่า **ขณะระบบทำงาน ส่วนใดรับผิดชอบอะไร ติดต่อกันอย่างไร และข้อมูลใดเชื่อถือได้จากที่ใด** อ่านต่อเรื่องตำแหน่งโค้ดได้ใน [Repository Architecture](../reference/repository/repository-architecture.md) และเรื่องสถานะคำสั่งซื้อใน [Order lifecycle](order-lifecycle.md)

## 1. ขอบเขตและสถานะของภาพ

CODE baseline คือ Component Repository [e-commerce-backend ที่ `4a8e680`](https://github.com/ittikornsopawan/e-commerce-backend/tree/4a8e6808e1887f324aea9e987369e28faf76ec51) (main หลัง authen-and-author APIs 01–10, EF Core และ field transport) ตำแหน่ง checkout คือ `e-commerce/repository/e-commerce-backend/` มี Git history/remote ของตนเองและถูก ignore โดย Showcase และเป็น revision ที่ [REPOS.md](../../REPOS.md) pin ไว้ ภาพวาดใหม่ทั้งชุดจาก source ที่ revision นี้และตารางของ [code-structure.md](../../doc/code-structure.md) ไม่มีป้ายจาก first scaffold เหลืออยู่

ภาพรวม runtime ของ backend หนึ่งแอปพลิเคชัน ประกอบกับความสามารถ commerce ที่ระบุในเอกสาร และส่วน Redis/MongoDB ที่ผู้ใช้ขอเพิ่ม ไม่ใช่แผน deployment หรือคำยืนยันว่าทุกความสามารถทำงานจริงแล้ว

| ป้ายในภาพ | ความหมาย | หลักฐานและขอบเขต |
| --- | --- | --- |
| `CODE` | มีโค้ดรองรับส่วนที่ระบุ | Backend มี Authen 10 use cases (APIs 01–10) ทุก test case ของแต่ละ spec มี automated test; spec ยังเป็น authority |
| `SPEC` | มีข้อกำหนดอธิบายพฤติกรรม | Order, payment, shipping และ expiry ต้องอ่านข้อกำหนดของแต่ละเรื่อง; ภาพไม่ขยายสถานะอนุมัติให้เอกสารต้นทาง |
| `PROPOSED` | ส่วนที่เสนอเพิ่ม | Redis, MongoDB, outbox, adapters และนโยบายยังอยู่ใน [Redis design](../design/redis-design.md) และ [MongoDB design](../design/mongodb-design.md) ยังไม่มี implementation |

ผู้ใช้เลือก MongoDB สำหรับ feature flags/config ทั่วไป รวม cache/rate-limit policy ตลอดจน audit/integration events และสำเนาธุรกรรมสำหรับค้นย้อนหลัง PostgreSQL ยังเป็นข้อมูลหลักของธุรกรรม การเลือกบทบาทนี้ไม่ใช่การอนุมัติค่าทางปฏิบัติทั้งหมด เช่น quota, TTL, retention หรือระยะเวลายอมใช้ config เก่า

## 2. วิธีอ่าน logical containment และ runtime calls

กรอบ `One ASP.NET Core backend` มี native child containers สำหรับ Presentation, Application, Domain, Infrastructure และ Shared แต่ละชั้นมีกล่องหน้าที่จริงภายใน กล่องแต่ละใบเป็น editable component; ย้าย parent แล้วลูกยังคงอยู่ภายใต้ขอบเขตเดิม

ภาพนี้ใช้ Architecture ที่เน้น layer decomposition บนพื้นที่ 1584 × 1120 และมี 24 กล่องรายละเอียด แบ่งเป็น core responsibilities, client และ data/external services ส่วน [Repository Architecture](../reference/repository/repository-architecture.md) ตอบคำถามตำแหน่ง source paths และ project references

การซ้อนเป็น logical ownership ไม่ใช่ลำดับที่ทุก request ต้องผ่านทุกกล่อง ชั้น Shared อยู่ข้าง core เพราะ dispatcher, `Result`/`Error`, `Optional`, `PageRequest` และ `ValidationMessages` ใช้ร่วมกันหลายชั้น การเรียง Infrastructure ไว้ล่างไม่ได้หมายความว่า Domain reference Infrastructure; compile references อยู่ในภาพ repository

เส้นทึบแปดเส้นแสดง runtime collaboration ที่เลือก: client → Controller → Dispatcher, Dispatcher → Validator และเมื่อผ่านจึง Dispatcher → Handler, Handler → Business Domain, Handler → Application ports → Persistence adapter → PostgreSQL กล่อง **Handler คือ Application use case** ที่รับผิดชอบ orchestration และ transaction ส่วน Business Domain เป็นกฎธุรกิจที่ใช้ซ้ำ (Service = Domain)

Filters ทำงานรอบ controller ไม่ใช่ขั้นของ use case จึงไม่มีลูกศรแยก เส้นจาก port ไป concrete adapter หมายถึงการเรียก implementation ที่ DI bind ไว้ ไม่ใช่ compile reference จาก Application ไป Infrastructure

## 3. การแยกหน้าที่ภายใน backend

### 3.1 Presentation — HTTP, filters และ composition

| กล่องในภาพ | ส่วนที่ตรวจพบจริง | เหตุผลที่แยก |
| --- | --- | --- |
| Controllers | `AuthenController` (`v1/auth`, specs 01–06) และ `UserController` (`v1/user`, 07–10) | อ่าน request, ส่ง `VerifiedCaller` เข้า Command/Query, dispatch แล้วเลือก success status; ไม่มี SQL หรือกฎธุรกิจ |
| Filters & envelope | `RequiredHeadersFilter` (400 E10001), `InvalidBody` (body ที่ bind ไม่ได้), `EncryptedFieldsFilter` (ถอด field ที่เข้ารหัสผ่าน `IFieldTransport`), `EnvelopeExceptionHandler` (500 ไม่มี bizCode) | ทุก API ตอบใน spec envelope เดียวกันก่อนและหลัง controller |
| Composition & security | `Program.cs`: `AddCqrs`, `AddInfrastructure`, JWT Bearer, `VerifiedCaller`, per-IP rate limits ของ public APIs | Composition root ไม่ใช่ที่เก็บกฎ; ลำดับ rate limiter → authentication → controllers |

ดู [Program.cs](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/src/Ecommerce.Api/Program.cs), [AuthenController.cs](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/src/Ecommerce.Api/Controllers/AuthenController.cs) และ [UserController.cs](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/src/Ecommerce.Api/Controllers/UserController.cs)

### 3.2 Application — Command/Query, Validator, Handler, shared steps และ ports

| กล่องในภาพ | ส่วนที่ตรวจพบจริง | เหตุผลที่แยก |
| --- | --- | --- |
| Command / Query | 8 commands (Register, Login, RequestPasswordReset, CreateNewPassword, RefreshToken, Logout, UpsertUserProfile, UpsertUserAddress) และ 2 queries (GetUserProfile, InquiryUserAddress) | Input records ระบุเจตนา use case; raw strings และ `Optional<T>` แยก "ไม่ส่ง" ออกจาก null/invalid |
| Validator | 8 validators (ทุก use case ที่มี input) ใช้รูปข้อความจาก `ValidationMessages` | ทุก 400 ของ spec ตอบก่อน SQL และก่อน 401 |
| Handler | 10 handlers | รันงานใน `ITransactionRunner` ตาม isolation/READ ONLY ของ spec เรียก Business Domain และ repositories |
| Shared use-case steps | `CallerCredential` (ตรวจ session ปัจจุบันภายใน transaction), `SessionTokens`, `TokenPairResponse` ใน `Features/Authen/Common/` | ขั้นที่หลาย use cases ใช้ร่วมกันโดยไม่คัดลอก |
| Application ports | `ITransactionRunner`, `IFieldTransport`, `IPasswordHasher`, `ITokenService`, `IEmailSender`; cache/rate/config/event ports เป็น PROPOSED | ชั้นในระบุความสามารถที่ต้องการ ขณะ Infrastructure จัด implementation |

[Dispatcher.cs](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/src/Ecommerce.Shared/Cqrs/Dispatcher.cs) รวม errors จาก validators ที่ลงทะเบียน เมื่อมี error จะคืน failure โดยไม่เรียก handler ลูกศร dispatcher → handler ต้องอ่านร่วมกับ guard นี้

กล่องหน้าที่เป็นการรวมหลาย use cases เพื่อการอ่าน โค้ดจริงจัดตาม `Features/Authen/<UseCase>/` CQRS ใน source นี้ไม่มี broker, event sourcing หรือฐานข้อมูล query แยก

### 3.3 Domain — common rules, value objects, repository contracts และ Business Domain

| กล่องในภาพ | ส่วนที่ตรวจพบจริง | เหตุผลที่แยก |
| --- | --- | --- |
| Common / errors | `AuthenErrors`, `EmailAddressFormat`, `ProfileFieldRules`, `ValueObject`, `DuplicateKeyException`, `MissingReferenceException` | กฎที่หลาย feature ใช้ และ error ที่มี status/bizCode ของ spec |
| Value objects | `PlainPassword`, `PasswordCredential` และ records ที่ repositories แลกเปลี่ยน (registration, login, profile, address, refresh row) | ค่าที่มีกฎของตัวเอง; records ถือข้อมูลอย่างเดียว |
| Repository contracts | 11 interfaces ต่อ use case หรือขั้นร่วม ใน `Authen/Repositories/` | ไม่มี EF Core types ข้ามเข้า Domain |
| Business Domain | `AddressDefaultPolicy`, `AuthorizationClaims`, `RefreshTokenReuse` และ throttles/consent policy ใน `Authen/Domain/` | การตัดสินใจทางธุรกิจที่ใช้ซ้ำ เป็น pure functions ทดสอบได้โดยไม่มีฐานข้อมูล |

ไม่มี entities: แถวข้อมูลถูกอ่านเป็น records และการตัดสินใจเป็น pure functions; invariants ข้าม request รักษาด้วยฐานข้อมูล (locks, guarded updates, unique indexes)

### 3.4 Infrastructure — persistence, security, email/payment และ proposed data adapters

Persistence ใช้ EF Core: `EcommerceDbContext`, `ForUpdate()` สำหรับ row lock, `AdvisoryLock`, `EfTransactionRunner` (retry 40001) และ repositories ต่อ use case ใน `Persistence/Authen/` Security รวม `Pbkdf2PasswordHasher`, `TokenService`, `FieldProtector` และ `FieldTransport` กล่อง Email/payment ระบุสถานะแยกกัน: `LoggingEmailSender` เป็น **CODE** แบบ development stub ส่วน Stripe intent/refund เป็น **SPEC** ยังไม่มี adapter

Data adapters เป็นกล่อง **PROPOSED** สำหรับ Redis cache/rate และ MongoDB config/projections [DependencyInjection.cs](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/src/Ecommerce.Infrastructure/DependencyInjection.cs) ยืนยันบริการที่ลงทะเบียนจริง

### 3.5 Shared — dispatch และ primitives

Shared มีสองกล่อง: CQRS dispatcher/messaging/assembly scanning และ shared primitives (`Result`/`Error`, `Optional`, `PageRequest`, `ValidationMessages`) ความล้มเหลวที่คาดหมายเป็นค่า failure ไม่ใช้ exception เป็น flow control หลัก

## Business Domain — Service = Domain

ตามคำชี้แจงของเจ้าของงานวันที่ 2026-11-08 กฎธุรกิจที่ใช้ซ้ำอยู่ใน `src/Ecommerce.Domain/<Feature>/Domain/` ไม่ได้เพิ่ม process, network service หรือ `.csproj` ใหม่ ปัจจุบันเป็น **CODE** ที่ `Authen/Domain/` แล้ว (ก่อนหน้านี้ภาพแสดงเป็น `PROPOSED · OWNER REQUEST`)

| ส่วน | หน้าที่และเหตุผล |
| --- | --- |
| Application Handler | โหลดข้อเท็จจริงผ่าน repositories ประสานลำดับ use case เรียก Business Domain แล้วบันทึกภายใน transaction เดียว |
| Business Domain | รับ business values คำนวณ/ใช้กฎ และคืนผล ไม่รับ HTTP DTO, EF Core type หรือควบคุม commit |
| Infrastructure | ติดต่อ PostgreSQL และ providers ตาม ports; การอ่านข้อมูลแยกจากการตัดสินใจใน Domain |

เส้นทางคือ **Handler → Domain → business result → Handler → persistence** เช่น `AddressDefaultPolicy.Resolve(...)` ตัดสินว่า address เป็น default หรือไม่และต้องย้าย default หรือไม่ handler ส่งข้อเท็จจริงเข้าไปและนำผลไปบันทึก กฎของ commerce feature อื่นควรอยู่ใต้ feature ที่เป็นเจ้าของ เช่น `<CommerceFeature>/Domain/` [Microsoft: Application Core และ domain services](https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures)

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

เอกสารนี้เป็นคำอธิบายภาพ ไม่เปลี่ยน policy ต้นทาง ไม่มี Redis/MongoDB runtime หรือ failover/load/security tests ในงานอธิบายนี้ Hosting/replicas/gateway, expiry/7-day completion worker host และ outbox worker host ยังไม่ได้เลือก

## 8. แหล่งหลักฐานและเอกสารที่ต้องอ่านร่วมกัน

- [README ของชุดภาพ](../README.md), [semantic source](../../scripts/diagrams/layered_core_content.py) และ [research ของรูปแบบภาพ](../design/research.md) ใช้ตรวจเนื้อหา/การจัดมุมมอง
- [Backend project structure](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/project-structure.md), [Program.cs](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/src/Ecommerce.Api/Program.cs) และ [Infrastructure DI](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/src/Ecommerce.Infrastructure/DependencyInjection.cs) ใช้ยืนยันส่วนที่มีโค้ด
- [Redis design](../design/redis-design.md), [Redis research](../design/redis-research.md) และ [Redis review](../design/redis-review.md) ใช้พิจารณานโยบายและข้อจำกัดของข้อเสนอ
- [MongoDB design](../design/mongodb-design.md) และ [MongoDB research](../design/mongodb-research.md) ใช้ตรวจ config ownership, event projections และ cross-store delivery
- [Order lifecycle explanation](order-lifecycle.md) เชื่อม runtime decisions กับ order/payment/shipping guards โดยข้อกำหนด API ที่ลิงก์ไว้ยังเป็นต้นทางของรายละเอียดธุรกิจ

[กลับสารบัญ diagram](../README.md)
