---
name: E-commerce Repository Architecture Explanation
description: คำอธิบายภาพ repository-architecture พร้อมหน้าที่แต่ละโปรเจกต์ dependency references เหตุผลการแบ่งชั้น และตำแหน่งส่วน Redis/MongoDB ที่เสนอ ใช้เมื่ออ่านหรือทบทวนโครงสร้าง backend
---

# คำอธิบาย Repository Architecture

เอกสารนี้อ่านคู่กับ [repository-architecture.drawio.png](repository-architecture.drawio.png) เพื่อตอบว่า **แต่ละความรับผิดชอบอยู่ตรงไหน โค้ดอ้างอิงกันทางใด และควรวางส่วนเชื่อมต่อ Redis/MongoDB ไว้ที่ใดตามข้อเสนอปัจจุบัน** ภาพนี้เป็นแผนที่ source code ต่างจาก [Architecture Design](../../main/architecture-design.md) ที่อธิบายการทำงานขณะ runtime และ [System Design](../../main/order-lifecycle.md) ที่อธิบาย order lifecycle

## 1. วิธีอ่านภาพโดยไม่สับสนกับ runtime

ภาพใช้ **Nested package containment**: กรอบนอกคือ Component Repository `e-commerce/repository/e-commerce-backend/` ซึ่งมี remote/Git history ของตนเอง ภายในแยก `src/`, `tests/`, shared build files และ component guides แต่ละ production `.csproj` เป็น native parent ที่ขยับพร้อมกล่องหน้าที่ภายในได้

ภาพมี 11 native containers และ 23 กล่องรายละเอียด ไม่มีลูกศร ใช้ containment เพื่อแสดงเจ้าของ ส่วน `REF: ...` บอก direct `.csproj` references ทั้ง 9 production และ 7 test references ป้าย Api แบ่ง references ไว้สองกล่องภายใน project เดียวกัน โดยรวมเป็น Application, Infrastructure, Shared ไม่ใช่ references ของไฟล์แต่ละไฟล์ Test projects ทั้งสี่เป็นกล่องรายละเอียดภายใน `tests/` แต่ละกล่องระบุ references ของตน

Path header ย่อ outer Showcase/Checkout Directory rings ให้เหลือ Component Repository boundary ขณะ `REPOS.md`, `doc/`, `db/`, `api/` และ `diagram/` ยังเป็นของ Showcase อยู่นอกกรอบ component กล่องด้านขวาล่างจึงเป็น component guides (`README.md`, `project-structure.md`, `code.md`)

กล่อง Command/Query, Validators และ Handlers เป็น native children ภายในกรอบ `Features/Authen/` และรวม **หน้าที่ของไฟล์จากหลาย use cases** ไม่ใช่การอ้างว่ามีโฟลเดอร์กลางสามโฟลเดอร์นี้ โค้ดจริงอยู่ `Features/Authen/<UseCase>/` ส่วนขั้นที่หลาย use cases ใช้ร่วมกันอยู่ `Features/Authen/Common/`

ไฟล์และความสามารถที่ขึ้นต้น `PROPOSED` เป็นตำแหน่งออกแบบใน [Redis design](../../design/redis-design.md)/[MongoDB design](../../design/mongodb-design.md) ยังไม่มี middleware/adapters/collections/outbox ในโค้ด โค้ดที่พบจริงรองรับ Authen 10 use cases (APIs 01–10) ไม่ใช่ commerce backend ที่ implement ครบแล้ว

## 2. Root และโครงสร้างที่ภาพสื่อ

### 2.1 `e-commerce/repository/e-commerce-backend/`

เป็นตำแหน่ง backend มี production 5 projects และ test 4 projects อยู่ใน `Ecommerce.sln` จัด CQRS ตาม feature เพื่อให้ไฟล์ของ use case เดียวอยู่ใกล้กัน เช่น register มี command, validator, handler และ response ของตนเอง ดู [project-structure.md](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/project-structure.md)

ภาพวาดจาก source ที่ `4a8e6808e1887f324aea9e987369e28faf76ec51` (main หลัง authen-and-author APIs 01–10, EF Core และ field transport) [REPOS.md](../../../REPOS.md) ประกาศ Component Repository ชื่อ `e-commerce-backend` และ pin revision นี้ Component มี independent Git history/remote/delivery lifecycle; Showcase เป็นเจ้าของ manifest/specifications/schema/migrations/diagrams ไม่ใช่ backend source

### 2.2 `src/`

รวมโค้ด production ที่ประกอบเป็น ASP.NET Core host เดียว การมี 5 `.csproj` แยก logical responsibilities และ compile dependencies ไม่ได้หมายถึง 5 microservices

### 2.3 Solution & shared build settings

`Ecommerce.sln` รวม projects ส่วน [Directory.Build.props](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/Directory.Build.props) กำหนด `net11.0`, Nullable, ImplicitUsings และ `TreatWarningsAsErrors=true` การรวมค่าที่ใช้ร่วมกันลดโอกาสแต่ละ project ใช้ compiler settings ต่างกันโดยไม่ตั้งใจ

`README.md` และ `project-structure.md` อธิบายวิธีใช้ codebase ส่วน `code.md` อธิบาย request flow, transactions, errors และ tests Redis/MongoDB connection secrets ที่กล่าวในภาพเป็นข้อเสนอให้ส่งผ่าน environment/secret management ไม่ใส่ credential ลง source

## 3. หน้าที่ของห้า production projects

### 3.1 `Ecommerce.Api` — HTTP, filters และ composition root

ไฟล์ตัวอย่างจริงคือ [AuthenController.cs](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/src/Ecommerce.Api/Controllers/AuthenController.cs) (`v1/auth`, specs 01–06), [UserController.cs](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/src/Ecommerce.Api/Controllers/UserController.cs) (`v1/user`, 07–10), `Contracts/Authen/*` กับ `ApiEnvelope`, `Filters/` (`RequiredHeadersFilter`, `InvalidBody`, `EncryptedFieldsFilter`, `EnvelopeExceptionHandler`), `Security/` (`VerifiedCaller`, `CallerClaims`, `RateLimiting`) และ [Program.cs](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/src/Ecommerce.Api/Program.cs)

Api รับ request, สร้าง command/query พร้อม verified caller, เรียก `IDispatcher` และตอบใน spec envelope ส่วน `Program.cs` ลงทะเบียน filters, CQRS, Infrastructure, JWT Bearer และ rate limits เหตุผลที่รวม wiring ที่นี่คือชั้นในต้องรู้เพียง interface

ข้อเสนอ shared quota ด้วย Redis อยู่ชั้นนี้เพราะ admission ต้องตัดสินก่อนงานราคาแพง ปัจจุบัน `RateLimiting.cs` เป็น per-IP limits ใน process ของ public APIs เท่านั้น ไม่ควรแทรกกฎเรื่อง order/stock ลง middleware

### 3.2 `Ecommerce.Application` — use cases และ ports

กล่อง `Command / Query`, `Validators` และ `Handlers` แสดง record input, การตรวจข้อมูล และตัวประสานงานแยกกันภายใน native `Features/Authen/` container โครงสร้างจริงมี 10 use-case folders: `Register`, `Login`, `ResetPassword` (`RequestPasswordReset`), `CreateNewPassword`, `RefreshToken`, `Logout`, `UpsertUserProfile`, `GetUserProfile`, `UpsertUserAddress`, `InquiryUserAddress` รวม 8 commands, 2 queries, 8 validators (`GetUserProfile` และ `Logout` ไม่มี input ที่ต้องตรวจ) และ 10 handlers

Handler รันงานใน `ITransactionRunner` ตาม isolation ของ spec เรียก Business Domain และ repository contracts `Features/Authen/Common/` มี `CallerCredential` (ตรวจ session ปัจจุบันภายใน transaction), `SessionTokens` และ `TokenPairResponse` ส่วน `Abstractions/` มี `ITransactionRunner`, `IFieldTransport`, `IPasswordHasher`, `ITokenService`, `IEmailSender`

ข้อเสนอเพิ่ม cache/rate/config snapshots/event-projection ports อยู่ฝั่ง Application เพื่อให้ use cases ระบุความต้องการโดยไม่ import Redis/MongoDB types แต่ต้องกำหนด semantic contract ให้ชัด เช่น cache miss ต่างจาก store unavailable อย่างไร

### 3.3 `Ecommerce.Domain` — กฎธุรกิจและสัญญาชั้นใน

`Common/` มีกฎที่หลาย feature ใช้ (`EmailAddressFormat`, `ProfileFieldRules`) และ `ValueObject` base; `Authen/AuthenErrors.cs`, `DuplicateKeyException`, `MissingReferenceException` เป็น errors `Authen/ValueObjects/` มี `PlainPassword`, `PasswordCredential` และ records ที่ repositories แลกเปลี่ยน `Authen/Repositories/` มี 11 interfaces ต่อ use case หรือขั้นร่วม เช่น [ILoginRepository.cs](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/src/Ecommerce.Domain/Authen/Repositories/ILoginRepository.cs)

Domain ไม่อ้างอิง Infrastructure และไม่มี EF Core types ไม่มี entities: แถวข้อมูลอ่านเป็น records และการตัดสินใจเป็น pure functions; invariants ข้าม request รักษาด้วยฐานข้อมูล

### `Authen/Domain/` — โค้ดกฎธุรกิจที่ใช้ซ้ำ

```text
e-commerce/repository/e-commerce-backend/src/Ecommerce.Domain/
├── Common/               # กฎที่ใช้ร่วมหลาย feature และ ValueObject base
└── Authen/
    ├── ValueObjects/     # ค่าที่มีกฎของตัวเอง และ records
    ├── Repositories/     # 11 inner contracts สำหรับ data access
    └── Domain/           # reusable Authen business operations (Service = Domain)
```

ชื่อโฟลเดอร์ใช้ **`Domain`** ตาม convention ของเจ้าของงาน (2026-11-08) ปัจจุบันเป็น **CODE**: `AddressDefaultPolicy`, `AuthorizationClaims`, `RefreshTokenReuse`, `PasswordResetThrottle`, `RegistrationConsentPolicy` ขอบเขตนี้อยู่ใน `Ecommerce.Domain` project เดิม จึงไม่เพิ่ม project references

Handler ใน Application เรียก business operation จากส่วนนี้เพื่อให้กฎเดียวกันใช้ได้หลาย use cases โดย Handler ยังรับผิดชอบ orchestration และ transaction กฎของ commerce feature อื่นต้องอยู่ใน feature ที่เป็นเจ้าของกฎนั้น ดู [เหตุผลด้านขอบเขตและการเรียกใช้](../../main/architecture-design.md#business-domain--service--domain)

### 3.4 `Ecommerce.Infrastructure` — adapters ที่มีเทคโนโลยีจริง

โครงสร้างจริงมี `Persistence/Ef/` (`EcommerceDbContext`, `ForUpdate`, `AdvisoryLock`, `UserRecord`), `Persistence/EfTransactionRunner.cs`, `Persistence/Authen/` (11 EF repositories และ `SessionRevocation`), `Security/` (`Pbkdf2PasswordHasher`, `TokenService`, `FieldProtector`, `FieldTransport`), `Email/LoggingEmailSender` และ `Options/` โดย [DependencyInjection.cs](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/src/Ecommerce.Infrastructure/DependencyInjection.cs) ลงทะเบียน implementation ของ ports Provider คือ `Npgsql.EntityFrameworkCore.PostgreSQL`

เหตุผลที่รวม EF Core/SDK/connection handling ที่นี่คือรายละเอียดเหล่านี้เปลี่ยนตามเทคโนโลยี ต่างจากความหมาย use case `LoggingEmailSender` เป็น development stand-in ไม่ใช่ production mail delivery

ข้อเสนอแยกความรับผิดชอบภายใน Infrastructure:

| ตำแหน่งที่เสนอ | หน้าที่ | เหตุผล |
| --- | --- | --- |
| `Caching/RedisCacheStore.cs` | Public projection cache, generation checks และ TTL | แยก cache optimization จาก authority ของข้อมูล |
| `RateLimiting/RedisRateLimitStore.cs` | Atomic shared admission และ store failure results | ไม่ปะปนกับ cache eviction/retry semantics |
| `Configuration/MongoConfigurationProvider.cs` | โหลด/validate/version config snapshots | ไม่ให้แต่ละ handler query config documents เอง |
| `Documents/MongoEventProjectionStore.cs` | Idempotent event/projection writes | บังคับ stable identity/source version ที่ขอบ destination |
| Options/client registration | Connection lifetime และ validated settings | ไม่สร้าง network clients ใหม่ทุก request |

ชื่อไฟล์เป็นข้อเสนอ ไม่ใช่รายการไฟล์ที่มีอยู่แล้ว และ outbox relay hosting ยังไม่ได้เลือก ไม่ควรสรุปว่ามี worker service หรือ broker อยู่ใน solution

### 3.5 `Ecommerce.Shared` — building blocks ร่วม

มี `Cqrs/` (messaging interfaces, dispatcher, registration), `Results/` (`Result`/`Result<T>`/`Error`), `Validation/ValidationMessages`, `Optional` และ `Paging/PageRequest` [Dispatcher.cs](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/src/Ecommerce.Shared/Cqrs/Dispatcher.cs) เรียก validators ก่อน handler ส่วน assembly scanning ลงทะเบียน handler/validator

เหตุผลคือให้แต่ละ feature ใช้ flow ของ validation/result สม่ำเสมอ ข้อเสนอ Redis/MongoDB ไม่ย้าย adapter หรือ business rules มา Shared เพียงเพราะหลาย features ใช้งาน

## 4. Dependency direction ที่ตรวจพบจริง

| Production project | Direct references | จำนวน |
| --- | --- | --- |
| `Ecommerce.Api` | Application, Infrastructure, Shared | 3 |
| `Ecommerce.Application` | Domain, Shared | 2 |
| `Ecommerce.Domain` | Shared | 1 |
| `Ecommerce.Infrastructure` | Application, Domain, Shared | 3 |
| `Ecommerce.Shared` | ไม่มี project reference | 0 |
| **รวม** | ตรวจจาก `.csproj` ของทั้งห้า projects | **9** |

Api reference Infrastructure เพื่อประกอบระบบ แต่ Application/Domain ไม่ reference กลับไป Infrastructure ขณะ runtime handler เรียก interface และ DI ส่ง implementation ให้ได้ จึงต้องแยก **compile dependency** ออกจาก **object call ขณะ runtime** แนวคิด dependency inversion และ logical layering อ่านเพิ่มได้จาก [Microsoft architecture guidance](https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures)

เหตุผลของทิศทางนี้คือชั้นนอกเปลี่ยนได้โดยไม่บังคับให้กฎชั้นในรู้จักเทคโนโลยีใหม่ ต้นทุนคือเพิ่ม interfaces/mapping/registration และต้องรักษาสัญญา consistency ให้ตรงของจริง จึงไม่จำเป็นต้องสร้าง abstraction สำหรับทุกบรรทัด ใช้เฉพาะขอบเขตที่มีความรับผิดชอบชัดเจน

## 5. Tests และสิ่งที่ tests พิสูจน์ได้

| Test project | Direct references | สิ่งที่มีอยู่ |
| --- | --- | --- |
| `Ecommerce.Api.Tests` | Api | ทุก test case ของ `test-cases.md` แต่ละ API ผ่าน HTTP pipeline และฐานข้อมูลจริง |
| `Ecommerce.Application.Tests` | Application, Domain, Shared | Handlers กับ fakes: ลำดับขั้น, isolation, READ ONLY, exception mapping |
| `Ecommerce.Domain.Tests` | Domain, Shared | Business rules และ value objects ไม่มีฐานข้อมูล |
| `Ecommerce.Infrastructure.Tests` | Infrastructure | EF repositories และ transaction runner บน PostgreSQL 17 ชั่วคราวที่โหลดทุก Showcase migration |
| **รวม** | **7 references** | |

Fakes ใน Application tests ไม่พิสูจน์ locks หรือ isolation; ส่วนนี้พิสูจน์ใน Infrastructure และ Api tests ที่ใช้ฐานข้อมูลจริง SQL tests ของ Showcase อยู่ที่ `e-commerce/db/tests/` แยกจาก C# projects เหล่านี้ ยังไม่มี tests ของ Redis scripts หรือ MongoDB

ในอนาคตต้องเพิ่มหลักฐานตามความเสี่ยงจริงหลัง design approval:

- Redis: concurrent quota หลาย API instances, forged identity/proxy headers, memory pressure, timeout/ambiguous retry, stale-fill race และ clock/failover
- MongoDB config: expected revision conflicts, validation, stream resume/full reload, cold start และหมดอายุ last-known-good
- Delivery: PostgreSQL business/outbox atomicity, duplicate/out-of-order events, newer snapshot guards, retries และ reconciliation เมื่อ MongoDB กลับมา
- End-to-end business: MongoDB/Redis outage ไม่ทำให้ charge หรือคืน stock/budget ซ้ำ และ valid signed webhook ยังถึง SQL path

รายการนี้เป็นเกณฑ์ของงาน implementation ภายหลัง ไม่ได้หมายความว่ามี tests เหล่านี้แล้ว คำสั่ง `dotnet test` ในภาพเป็นวิธีเรียก suites ไม่ใช่ผลทดสอบที่รันในงานเอกสารครั้งนี้

## 6. ตัวอย่างตามรอยหนึ่ง request

กรณี register ตาม code ปัจจุบัน:

1. `RequiredHeadersFilter` และ `EncryptedFieldsFilter` ตรวจ headers และถอด field ที่เข้ารหัส จากนั้น `AuthenController` สร้าง `RegisterCommand`
2. `IDispatcher` เรียก `RegisterCommandValidator` หากไม่ผ่านตอบ 400 โดยไม่เรียก handler
3. `RegisterCommandHandler` รันใน `ITransactionRunner` ใช้ `RegistrationConsentPolicy` และ `IRegistrationRepository`
4. Infrastructure บันทึกผ่าน `RegistrationRepository` บน `EcommerceDbContext`; duplicate key ของ `authen.m_user` กลายเป็น `DuplicateKeyException` ที่ handler map เป็น error ของ spec
5. Api แปลง `Result` เป็น spec envelope

เส้นทางนี้อธิบายเหตุผลของการแบ่งห้า production projects โดยไม่ต้องมี network hop ระหว่าง layers หากเพิ่ม Redis admission ตามข้อเสนอ มันอยู่ก่อน handler ไม่ได้แทน account rules หรือ constraints; หากเพิ่ม MongoDB audit copy จะต้องมี publication contract/outbox ที่ออกแบบให้รองรับ failure ไม่ใช่เพิ่ม `InsertOne` แบบ fire-and-forget หลังตอบสำเร็จ

## 7. Analysis artefacts ที่อยู่ข้าง code

| ตำแหน่งจากโครงการ e-commerce | บทบาท | เหตุผลที่แยกจาก implementation |
| --- | --- | --- |
| [doc/api](../../../doc/api/) | Human-readable API specifications | ระบุ behavior/permission/SQL ก่อนเขียน endpoint |
| [doc/schema](../../../doc/schema/) | Schema explanations | อธิบายความหมาย field/constraint |
| [db](../../../db/) | Migrations และ SQL tests | ตรวจ storage behavior โดยตรง |
| [api](../../../api/) | Machine-readable contract | ใช้กับเครื่องมือ/consumer ตามขอบเขตของ contract |
| [diagram](../../) | ภาพและคำอธิบายข้ามมุมมอง | ช่วยอ่านความเชื่อมโยงโดยไม่แทนรายละเอียดทั้งหมด |

ภาพเป็นแผนที่ ไม่ใช่ source of truth ของ payload/SQL ทุกกรณี ถ้า path ของโค้ดเปลี่ยน ต้องแก้ repository view; ถ้า runtime roles เปลี่ยน ต้องตรวจ architecture view; ถ้า business guard เปลี่ยน ต้องตรวจ system view และ specification ที่เกี่ยวข้องร่วมกัน

## 8. เหตุผลที่ไม่แยกเป็น microservices ในภาพนี้

หลักฐานปัจจุบันคือ host เดียวกับห้า code projects ยังไม่มี deployment contracts หรือ independent service ownership ให้ยืนยัน การวาดเป็น microservices จะทำให้ reviewer เข้าใจต้นทุน network/distributed consistency ที่ยังไม่ได้ออกแบบ การเพิ่ม Redis/MongoDB เป็น data services ไม่เปลี่ยน Domain/Application ให้กลายเป็นคนละ service

แบบนี้รักษาความเรียบง่ายในการตาม use case และการทดสอบชั้นใน ขณะยอมรับว่าการ scale แยกบาง feature หรือแยก release อิสระยังไม่ใช่คุณสมบัติที่พิสูจน์แล้ว หากต้องการจะแยกภายหลังต้องมี architecture decision ใหม่ ไม่อนุมานจากจำนวนโฟลเดอร์

## 9. แหล่งหลักฐานและขอบเขตการตรวจ

ตรวจหน้าที่และ references เทียบ [project-structure.md](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/project-structure.md) และ `.csproj` ทั้งเก้าที่ `4a8e680`: production [Api](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/src/Ecommerce.Api/Ecommerce.Api.csproj), [Application](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/src/Ecommerce.Application/Ecommerce.Application.csproj), [Domain](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/src/Ecommerce.Domain/Ecommerce.Domain.csproj), [Infrastructure](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/src/Ecommerce.Infrastructure/Ecommerce.Infrastructure.csproj), [Shared](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/src/Ecommerce.Shared/Ecommerce.Shared.csproj) และ tests [Api.Tests](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/tests/Ecommerce.Api.Tests/Ecommerce.Api.Tests.csproj), [Application.Tests](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/tests/Ecommerce.Application.Tests/Ecommerce.Application.Tests.csproj), [Domain.Tests](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/tests/Ecommerce.Domain.Tests/Ecommerce.Domain.Tests.csproj), [Infrastructure.Tests](https://github.com/ittikornsopawan/e-commerce-backend/blob/4a8e6808e1887f324aea9e987369e28faf76ec51/tests/Ecommerce.Infrastructure.Tests/Ecommerce.Infrastructure.Tests.csproj) ผลคือ source references 3+2+1+3+0 = 9 และ test references 1+3+2+1 = 7 รายชื่อไฟล์ในกล่องตรวจจาก `git ls-tree` ของ revision เดียวกัน

Semantic source ของภาพคือ [layered_core_content.py](../../../scripts/diagrams/layered_core_content.py) ตรวจ source decomposition, text/bounds/containment และ routes ด้วย `generate_layered_diagrams.py`; PNG ส่งออกด้วย draw.io Desktop แล้วตรวจด้วย `verify_diagram.py --require-nested` และตรวจภาพจริง

เอกสารนี้ไม่สร้าง proposed files ไม่เพิ่ม packages และไม่เปลี่ยน dependency direction ไม่ได้รัน backend build หรือ tests ในงานภาพนี้

[กลับสารบัญ diagram](../../README.md)
