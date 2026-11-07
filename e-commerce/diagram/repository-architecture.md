---
name: E-commerce Repository Architecture Explanation
description: คำอธิบายภาพ repository-architecture พร้อมหน้าที่แต่ละโปรเจกต์ dependency references เหตุผลการแบ่งชั้น และตำแหน่งส่วน Redis/MongoDB ที่เสนอ ใช้เมื่ออ่านหรือทบทวนโครงสร้าง backend
---

# คำอธิบาย Repository Architecture

เอกสารนี้อ่านคู่กับ [repository-architecture.drawio.png](repository-architecture.drawio.png) เพื่อตอบว่า **แต่ละความรับผิดชอบอยู่ตรงไหน โค้ดอ้างอิงกันทางใด และควรวางส่วนเชื่อมต่อ Redis/MongoDB ไว้ที่ใดตามข้อเสนอปัจจุบัน** ภาพนี้เป็นแผนที่ source code ต่างจาก [Architecture Design](architecture-design.md) ที่อธิบายการทำงานขณะ runtime และ [System Design](system-design.md) ที่อธิบาย order lifecycle

## 1. วิธีอ่านภาพโดยไม่สับสนกับ runtime

ภาพใช้ Tree: root แตกไป `src/`, `tests/` และ solution/build settings; `src/` แตกไป 5 production projects รวม 9 nodes และ 8 containment connectors ลูกศรทุกเส้นหมายถึง “อยู่ภายใต้/เป็นสมาชิกของ” ไม่ใช่ลำดับ request หรือ compile reference

บรรทัด `REF → ...` ภายในแต่ละกล่องต่างหากที่บอก direct `.csproj` references การแยกสองความหมายนี้ทำให้ไม่เข้าใจผิดว่า API ต้องเรียกทุกชั้นเรียงตามตำแหน่งบนหน้า หรือ Infrastructure เป็น directory ลูกของ Application

ไฟล์และความสามารถที่ขึ้นต้น `PROPOSED` เป็นตำแหน่งออกแบบใน [Redis design](redis-design.md)/[MongoDB design](mongodb-design.md) ยังไม่มีการสร้าง middleware/adapters/collections/outbox ในงาน diagram นี้ โค้ดที่พบจริงรองรับ Authen 5 use cases ไม่ใช่ commerce backend ที่ implement ครบแล้ว

## 2. Root และโครงสร้างที่ภาพสื่อ

### 2.1 `e-commerce/repository/`

เป็นตำแหน่ง backend ปัจจุบัน มี production 5 projects และ test 2 projects อยู่ใน `Ecommerce.sln` จัด CQRS ตาม feature เพื่อให้ไฟล์ของ use case เดียวอยู่ใกล้กัน เช่น register มี command, validator, handler และ response ของตนเอง

เหตุผลคือเมื่อแก้พฤติกรรมหนึ่งเรื่อง ผู้พัฒนาตามไฟล์ใน feature นั้นได้ ไม่ต้องเริ่มจากโฟลเดอร์รวม handlers ของทุกเรื่อง แต่ยังคงขอบเขต layer เพื่อไม่ให้ HTTP/DB details ไหลเข้ากฎธุรกิจ ดู [project-structure.md](../repository/project-structure.md)

โครงการนี้ยัง `migration-pending`: code อยู่ตรง `repository/` และยังไม่มี Project manifest ที่ย้ายไป independent Component Repository การเขียนคำอธิบายนี้ไม่ได้ clone, move หรือสร้าง nested Git repository โครงสร้างในภาพจึงอธิบาย checkout ที่ตรวจพบ ไม่ใช่สภาพหลัง migration ที่ยังไม่เกิดขึ้น

### 2.2 `src/`

รวมโค้ด production ที่ประกอบเป็น ASP.NET Core host เดียว การมี 5 `.csproj` แยก logical responsibilities และ compile dependencies ไม่ได้หมายถึง 5 microservices การจะเลือก deployment แยกต้องมีเหตุผล/สัญญาการสื่อสาร/การปฏิบัติการเพิ่มเติม ซึ่งภาพนี้ไม่ได้ตัดสิน

### 2.3 Solution & shared build settings

`Ecommerce.sln` รวม projects ส่วน [Directory.Build.props](../repository/Directory.Build.props) กำหนด `net10.0`, Nullable, ImplicitUsings และ `TreatWarningsAsErrors=true` การรวมค่าที่ใช้ร่วมกันลดโอกาสแต่ละ project ใช้ compiler settings ต่างกันโดยไม่ตั้งใจ

`README.md` และ `project-structure.md` อธิบายวิธีใช้ codebase ส่วน Redis/MongoDB connection secrets ที่กล่าวในภาพเป็นข้อเสนอให้ส่งผ่าน environment/secret management ไม่ใช่ให้ใส่ credential ลง source หรือ MongoDB config ที่ต้องใช้ credential นั้นเพื่อเริ่มเชื่อมต่อ

## 3. หน้าที่ของห้า production projects

### 3.1 `Ecommerce.Api` — HTTP และ composition root

ไฟล์ตัวอย่างจริงคือ [AuthenController.cs](../repository/src/Ecommerce.Api/Controllers/AuthenController.cs), [AuthenRequests.cs](../repository/src/Ecommerce.Api/Contracts/Authen/AuthenRequests.cs), [ResultExtensions.cs](../repository/src/Ecommerce.Api/Extensions/ResultExtensions.cs) และ [Program.cs](../repository/src/Ecommerce.Api/Program.cs)

Api รับ request, สร้าง command/query, เรียก `IDispatcher` และแปลงผลเป็น HTTP response ส่วน `Program.cs` ลงทะเบียน CQRS/Infrastructure และ JWT authentication/authorization เหตุผลที่รวม wiring ที่นี่คือชั้นในต้องรู้เพียง interface ไม่ต้องรู้ว่าจะเลือก adapter ตัวใด

ข้อเสนอ `Middleware/RedisRateLimitMiddleware.cs` อยู่ชั้นนี้เพราะ admission ต้องตัดสินก่อนเข้าการทำงานราคาแพง แต่ quota ที่ใช้ user ID ต้องรอ authentication ยืนยันตัวตนก่อน การเรียง middleware ทั้งหมดและ 429/503 response contract ยังต้องออกแบบ/อนุมัติแยก ไม่ควรแทรกกฎเรื่อง order/stock ลง middleware

### 3.2 `Ecommerce.Application` — use cases และ ports

โครงสร้างจริง `Features/Authen/` มี `Register`, `Login`, `ResetPassword`, `GetCurrentUser` โดย `ResetPassword` ครอบคลุม request link และ confirm รวมเป็น 5 use cases แต่ละ use case มี input, validator, handler และ response; mapping สร้าง response records จาก Domain

Handler ประสานลำดับงาน เช่นตรวจข้อมูลเดิม สร้าง entity เรียก hashing และบันทึกผ่าน transaction port ขณะที่ interfaces ใน `Abstractions/` อธิบายความสามารถที่ต้องใช้ เช่น unit of work, password hashing, token และ email

ข้อเสนอเพิ่ม cache/rate/config snapshots/event-projection ports อยู่ฝั่ง Application เพื่อให้ use cases ระบุความต้องการโดยไม่ import Redis/MongoDB types เหตุผลคือการทดสอบควรแทน port ได้ และการเปลี่ยน SDK ไม่ควรเปลี่ยน signature ของ handler ทั่วระบบ แต่ต้องกำหนด semantic contract ให้ชัด เช่น cache miss ต่างจาก store unavailable อย่างไร

### 3.3 `Ecommerce.Domain` — กฎของ model

มี entities (`User`, `PasswordResetToken`), value objects (`Username`, `EmailAddress`, `PlainPassword` ฯลฯ), common entity/value-object primitives และ repository interfaces ใน [IAuthenRepositories.cs](../repository/src/Ecommerce.Domain/Authen/Repositories/IAuthenRepositories.cs)

Domain ไม่อ้างอิง Infrastructure และในข้อเสนอไม่เพิ่ม Redis/MongoDB SDK ให้ชั้นนี้ เหตุผลคือกฎอย่างรูปแบบ username หรือ token ใช้ได้ครั้งเดียวไม่ควรต้องเปิด connection ฐานข้อมูลเพื่อทดสอบ กฎที่ต้องอ่านข้อมูลภายนอกยังใช้ port และ transaction/constraint รองรับตามลักษณะของกฎนั้น

การมี Domain model ไม่ใช่หลักฐานว่าข้อกำหนด SQL account/session ทั้งหมด implement แล้ว ต้องเทียบ use case และ code จริงแยกกัน

### 3.4 `Ecommerce.Infrastructure` — adapters ที่มีเทคโนโลยีจริง

โครงสร้างจริงมี `Persistence/Authen/{User,Password,Token}Repository.cs`, `DbSession`, `UnitOfWork`, `Pbkdf2PasswordHasher`, `TokenService`, `FieldProtector` และ `LoggingEmailSender` โดย [DependencyInjection.cs](../repository/src/Ecommerce.Infrastructure/DependencyInjection.cs) ลงทะเบียน implementation ของ ports

เหตุผลที่รวม SQL/SDK/serialization/connection handling ที่นี่คือรายละเอียดเหล่านี้เปลี่ยนตามเทคโนโลยี ต่างจากความหมาย use case `LoggingEmailSender` เป็น development stand-in ไม่ใช่ production mail delivery

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

มี CQRS interfaces/dispatcher/registration และ `Result`/`Error` สำหรับส่งผลของ use case ที่คาดหมายได้ [Dispatcher.cs](../repository/src/Ecommerce.Shared/Cqrs/Dispatcher.cs) เรียก validators ก่อน handler ส่วน assembly scanning ลงทะเบียน handler/validator

เหตุผลคือให้แต่ละ feature ใช้ flow ของ validation/result สม่ำเสมอ ข้อเสนอ Redis/MongoDB ไม่ย้าย adapter หรือ business rules มา Shared เพียงเพราะหลาย features ใช้งาน มิฉะนั้น Shared จะกลายเป็นจุดพึ่งพาเทคโนโลยีของทุกชั้น

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
| `Ecommerce.Domain.Tests` | Domain, Shared | Entity/value-object tests |
| `Ecommerce.Application.Tests` | Application, Domain, Shared | Handler/dispatcher tests กับ in-memory fake repositories |
| **รวม** | **5 references** | ไม่ใช่ real database integration suite |

การใช้ fakes ทำให้ตรวจ use case ได้เร็ว แต่ไม่พิสูจน์ SQL locks, isolation, Redis scripts, network failures หรือ MongoDB transactions ส่วน SQL tests อยู่ข้าง code ใน `e-commerce/db/tests/` และต้องไม่สับสนกับสอง C# projects นี้

ในอนาคตต้องเพิ่มหลักฐานตามความเสี่ยงจริงหลัง design approval:

- Redis: concurrent quota หลาย API instances, forged identity/proxy headers, memory pressure, timeout/ambiguous retry, stale-fill race และ clock/failover
- MongoDB config: expected revision conflicts, validation, stream resume/full reload, cold start และหมดอายุ last-known-good
- Delivery: PostgreSQL business/outbox atomicity, duplicate/out-of-order events, newer snapshot guards, retries และ reconciliation เมื่อ MongoDB กลับมา
- End-to-end business: MongoDB/Redis outage ไม่ทำให้ charge หรือคืน stock/budget ซ้ำ และ valid signed webhook ยังถึง SQL path

รายการนี้เป็นเกณฑ์ของงาน implementation ภายหลัง ไม่ได้หมายความว่ามี tests เหล่านี้แล้ว คำสั่ง `dotnet test` ในภาพเป็นวิธีเรียก suites ไม่ใช่ผลทดสอบที่รันในงานเอกสารครั้งนี้

## 6. ตัวอย่างตามรอยหนึ่ง request

กรณี register ตาม code ปัจจุบัน:

1. `AuthenController` รับ HTTP body แล้วสร้าง `RegisterCommand`
2. `IDispatcher` เลือก validator และ handler
3. Validator ใช้ value-object rules หากไม่ผ่าน ไม่เรียก handler
4. Handler ตรวจ duplicate ผ่าน repository port สร้าง user/password และบันทึกผ่าน unit of work
5. Infrastructure ทำ SQL/hash ตาม implementation ที่ลงทะเบียน
6. Application map เป็น response แล้ว Api แปลง `Result` เป็น HTTP

เส้นทางนี้อธิบายเหตุผลของการแบ่งห้า projects โดยไม่ต้องมี network hop ระหว่าง layers หากเพิ่ม Redis admission ตามข้อเสนอ มันอยู่ก่อน handler ไม่ได้แทน account rules หรือ constraints; หากเพิ่ม MongoDB audit copy จะต้องมี publication contract/outbox ที่ออกแบบให้รองรับ failure ไม่ใช่เพิ่ม `InsertOne` แบบ fire-and-forget หลังตอบสำเร็จ

## 7. Analysis artefacts ที่อยู่ข้าง code

| ตำแหน่งจากโครงการ e-commerce | บทบาท | เหตุผลที่แยกจาก implementation |
| --- | --- | --- |
| [doc/api](../doc/api/) | Human-readable API specifications | ระบุ behavior/permission/SQL ก่อนเขียน endpoint |
| [doc/schema](../doc/schema/) | Schema explanations | อธิบายความหมาย field/constraint |
| [db](../db/) | Migrations และ SQL tests | ตรวจ storage behavior โดยตรง |
| [api](../api/) | Machine-readable contract | ใช้กับเครื่องมือ/consumer ตามขอบเขตของ contract |
| [diagram](./) | ภาพและคำอธิบายข้ามมุมมอง | ช่วยอ่านความเชื่อมโยงโดยไม่แทนรายละเอียดทั้งหมด |

ภาพเป็นแผนที่ ไม่ใช่ source of truth ของ payload/SQL ทุกกรณี ถ้า path ของโค้ดเปลี่ยน ต้องแก้ repository view; ถ้า runtime roles เปลี่ยน ต้องตรวจ architecture view; ถ้า business guard เปลี่ยน ต้องตรวจ system view และ specification ที่เกี่ยวข้องร่วมกัน

## 8. เหตุผลที่ไม่แยกเป็น microservices ในภาพนี้

หลักฐานปัจจุบันคือ host เดียวกับห้า code projects ยังไม่มี deployment contracts หรือ independent service ownership ให้ยืนยัน การวาดเป็น microservices จะทำให้ reviewer เข้าใจต้นทุน network/distributed consistency ที่ยังไม่ได้ออกแบบ การเพิ่ม Redis/MongoDB เป็น data services ไม่เปลี่ยน Domain/Application ให้กลายเป็นคนละ service

แบบนี้รักษาความเรียบง่ายในการตาม use case และการทดสอบชั้นใน ขณะยอมรับว่าการ scale แยกบาง feature หรือแยก release อิสระยังไม่ใช่คุณสมบัติที่พิสูจน์แล้ว หากต้องการจะแยกภายหลังต้องมี architecture decision ใหม่ ไม่อนุมานจากจำนวนโฟลเดอร์

## 9. แหล่งหลักฐานและขอบเขตการตรวจ

ตรวจหน้าที่และ references เทียบ [project-structure.md](../repository/project-structure.md), [Api.csproj](../repository/src/Ecommerce.Api/Ecommerce.Api.csproj), [Application.csproj](../repository/src/Ecommerce.Application/Ecommerce.Application.csproj), [Domain.csproj](../repository/src/Ecommerce.Domain/Ecommerce.Domain.csproj), [Infrastructure.csproj](../repository/src/Ecommerce.Infrastructure/Ecommerce.Infrastructure.csproj), [Shared.csproj](../repository/src/Ecommerce.Shared/Ecommerce.Shared.csproj), [Domain.Tests.csproj](../repository/tests/Ecommerce.Domain.Tests/Ecommerce.Domain.Tests.csproj) และ [Application.Tests.csproj](../repository/tests/Ecommerce.Application.Tests/Ecommerce.Application.Tests.csproj)

เอกสารนี้ไม่สร้าง proposed files ไม่เพิ่ม packages ไม่ย้าย repositories และไม่เปลี่ยน dependency direction ส่วน [Redis design](redis-design.md)/[MongoDB design](mongodb-design.md) ยัง `in-review` งานอธิบายนี้ตรวจความสอดคล้องกับภาพและ source ไม่ได้รัน backend build หรือ network/database integration tests
