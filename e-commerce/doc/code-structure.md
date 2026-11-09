---
name: E-commerce Layer and Sub-layer Code Structure Guide
description: อธิบายทุก layer และ sub-layer ของ backend พร้อมหน้าที่ input/output ขอบเขต การประสานงาน source examples และ diagram เดิม ใช้ก่อนเลือกตำแหน่งโค้ด พัฒนา use case หรือ review architecture
status: draft
approved_by: null
approved_at: null
observed_on: 2026-11-08
reviewed_on: 2026-11-09
source_component_revision: d8255183cba54d0c2b218607456b895a70df32f0
source_showcase_revision: f5580ed087c8ffcc6a740b256fcb6aacd36ec5ae
---

# โครงสร้างโค้ด E-commerce: ทุก Layer และ Sub-layer

## 1. ความหมายและขอบเขต

คู่มือนี้อธิบายโครงสร้างการเขียนโค้ดของ e-commerce backend **ครบทั้ง Presentation, Application, Domain, Infrastructure และ Shared รวมส่วนย่อยของแต่ละ layer** เพื่อให้ผู้อ่านตัดสินได้ว่าโค้ดหนึ่งส่วนควรอยู่ที่ไหน รับข้อมูลจากใคร ทำหน้าที่ใด และส่งผลให้ส่วนใดต่อ ใช้ภาพประกอบแยก runtime collaboration, source ownership และ business-data concepts ออกจากกัน

### 1.1 คำศัพท์ที่ใช้กับทุก layer

| คำ | ความหมายในคู่มือนี้ | ตัวอย่าง |
| --- | --- | --- |
| Layer | ขอบเขตความรับผิดชอบและ dependency ระดับหลัก ปัจจุบันแยกเป็นห้า production `.csproj` | API รับ HTTP; Domain ถือความหมายและกฎธุรกิจ |
| Sub-layer / ส่วนย่อย | กลุ่มหน้าที่ภายใน layer อาจเป็น folder, กลุ่มไฟล์ หรือองค์ประกอบในภาพ ไม่ได้เพิ่ม project/process ใหม่โดยอัตโนมัติ | Controller กับ Contracts อยู่ใน API; DbSession กับ UnitOfWork อยู่ใน Persistence |
| Feature | กลุ่มความสามารถของธุรกิจที่จัดโมเดลและ use cases ที่เกี่ยวข้องไว้ด้วยกัน | Authen |
| Use case / Handler | Use case คือ operation ที่ caller ต้องการ; Handler คือคลาส Application ที่ประสาน operation นั้นให้สำเร็จ | Register, Login, RequestPasswordReset, ResetPassword, GetCurrentUser |
| Contract / DTO | รูปแบบข้อมูลที่ใช้ข้าม boundary โดยแยกจาก state ของ domain entity | HTTP request, Command/Query input และ response record |
| Port | interface ฝั่งด้านในที่อธิบายความสามารถที่ต้องการ โดยไม่ผูก concrete technology | `IUserRepository`, `IUnitOfWork`, `IPasswordHasher` |
| Adapter | implementation ที่ใช้เทคโนโลยีจริงทำงานตาม port | Dapper repository, `UnitOfWork`, password hasher |

### 1.2 ภาพรวมความหมายของทั้งห้า layers

| Layer / project | คำถามที่เป็นเจ้าของ | รับและคืนอะไร | ส่วนย่อยที่จะอธิบาย |
| --- | --- | --- | --- |
| Presentation — `Ecommerce.Api` | รับคำขอ HTTP และสื่อผลกลับ caller อย่างไร | รับ HTTP/contracts/principal; ส่ง Application request และคืน HTTP status/payload | Controllers, Contracts/model binding, HTTP results, Composition/security pipeline |
| Application — `Ecommerce.Application` | use case นี้ต้องทำขั้นตอนใดและประสานส่วนใดบ้าง | รับ Command/Query; โหลดข้อเท็จจริง เรียกกฎ/ports และคืน Result/response DTO | Commands/Queries, Validators, Handlers, Mapping/Responses, Ports/Common |
| Domain — `Ecommerce.Domain` | ธุรกิจยอมรับค่า สถานะ หรือผลการตัดสินใจแบบใด | รับ business values/state/facts; คืน business result หรือเปลี่ยน state ผ่าน behavior | Entities/Aggregates, ValueObjects, Business Domain, Repository contracts, Common/Errors/Status |
| Infrastructure — `Ecommerce.Infrastructure` | ใช้ database, cryptography และ external systems ทำงานจริงอย่างไร | รับการเรียก port และค่าที่จำเป็น; คืนข้อมูล/ผลของ I/O หรือ infrastructure failure | Repositories, DbSession, UnitOfWork, Security, Email, Options/DI และ proposed adapters |
| Shared — `Ecommerce.Shared` | ส่วนใดเป็นกลไกทั่วไปที่หลาย features ใช้ร่วมกัน | รับ request/result types; dispatch ไป handler และสื่อ success/failure ตาม contract ร่วม | Messaging contracts, Dispatcher/Registration, Results/Errors |

การอ่าน layer ไม่ใช่การบังคับลำดับ API → Application → Domain → Infrastructure → Shared ทุก request: Shared เป็น building blocks ที่หลายชั้นอ้างอิง ส่วน runtime calls เกิดผ่าน interfaces และ DI ตาม use case หัวข้อ 2 อธิบายหน้าที่และ boundary ของแต่ละส่วนย่อย; หัวข้อ 3 แยก project references ออกจาก runtime calls

### 1.3 Convention, source baseline และสถานะของขอบเขต

ใน Domain layer โครงการใช้ **Service = Domain** หมายถึง reusable business operations และเลือก path `src/Ecommerce.Domain/<Feature>/Domain/` เช่น `Authen/Domain/` ตามที่เจ้าของกำหนด ส่วน Entities/ValueObjects ยังคงรักษา invariant ของตัวเอง รายละเอียดอยู่ในหัวข้อ 2.3 และ 5 ชื่อ infrastructure services อย่าง `TokenService` มีหน้าที่ทางเทคนิคตาม port ของตนเอง

**Baseline:** โค้ดที่ตรวจคือ Component Repository [e-commerce-backend](https://github.com/ittikornsopawan/e-commerce-backend/tree/d8255183cba54d0c2b218607456b895a70df32f0) ตาม [REPOS.md](../REPOS.md) มีห้า production projects, สอง test projects และ Authen ห้า use cases ส่วน `Authen/Domain/` เป็น owner-directed design ที่ยังไม่มี implementation ใน commit นี้ ภาพ Domain model เป็นแนวคิดข้อมูล ไม่ใช่รายชื่อ business service classes ที่มีอยู่แล้ว

ขอบเขตงานเอกสารคืออธิบายทุก layer/sub-layer พร้อมหน้าที่ input/output การประสานงาน ข้อจำกัด และตัวอย่าง source ที่ตรวจพบ โดยแยก CODE, SPEC และ PROPOSED ตามภาพ คู่มือนี้ยังเป็น draft การอธิบาย design ไม่ได้อนุมัติ business behavior ใหม่ ต้องอ่าน governing spec และ approval ก่อน implementation ตาม [SDD workflow](../../.agents/workflows/spec-driven-development.md)


## 2. Architecture: ขณะ request ทำงาน แต่ละส่วนรับผิดชอบอะไร

![Runtime architecture: Presentation, Application, Domain, Infrastructure และ Shared พร้อมสถานะ CODE, SPEC และ PROPOSED](../diagram/main/architecture-design.drawio.png)

[เปิดภาพขนาดเต็ม](../diagram/main/architecture-design.drawio.png) · [แก้ไขด้วย draw.io](../diagram/main/architecture-design.drawio) · [คำอธิบายภาพ](../diagram/main/architecture-design.md) · [HTML preview](../diagram/main/architecture-design.html)

ภาพนี้อธิบาย logical layers และ runtime collaboration ภายใน ASP.NET Core backend หนึ่งแอปพลิเคชัน กรอบที่ซ้อนกันบอกเจ้าของความรับผิดชอบ ส่วนลูกศรแสดงการเรียกที่เลือกมาอธิบาย ไม่ใช่ compile-time project references หรือคำสั่งให้ทุก request ผ่านทุกกล่อง

| ป้ายในภาพ                   | วิธีอ่าน                                                                             |
| -------------------------- | --------------------------------------------------------------------------------- |
| `CODE`                     | มี source รองรับส่วนที่ระบุใน pinned backend; ยังต้องตรวจความครบของพฤติกรรมกับ spec         |
| `SPEC`                     | มีเอกสารกำหนด behavior ต้องตรวจ approval ของเอกสารนั้น ไม่ได้แปลว่า backend implement แล้ว |
| `PROPOSED`                 | ส่วนที่เสนอเพิ่ม ยังไม่ใช่ implementation เช่น Redis/MongoDB adapters และ outbox           |
| `PROPOSED · OWNER REQUEST` | เจ้าของกำหนดตำแหน่ง Business Domain ในภาพแล้ว แต่ pinned source ยังไม่มีโฟลเดอร์/คลาสดังกล่าว |

### 2.1 Presentation / API layer — ขอบเขต HTTP และการประกอบระบบ

API เป็นจุดเชื่อม caller กับ Application ดูแลความหมายของ HTTP, authenticated principal และการสร้าง dependency graph ผู้อ่านควรแยกการรับ request ออกจากการตัดสิน business และการทำ I/O จริง แม้ request หนึ่งจะเรียกทั้งสามส่วนต่อเนื่องกัน

| Sub-layer | หน้าที่และงานที่เป็นเจ้าของ | Input → Output / การประสานงาน | Source / สถานะ |
| --- | --- | --- | --- |
| Controllers | กำหนด routes รับ action arguments สร้าง Command/Query เรียก dispatcher และเลือก success response | HTTP action input → Application request → Result → HTTP response | `Controllers/AuthenController.cs` — CODE |
| Contracts / model binding | นิยามรูปร่าง body ที่ API รับ ให้ ASP.NET Core bind/deserialize เป็น request record ก่อนสร้าง use-case input | JSON/body → `RegisterRequest`, `LoginRequest`, reset request records; use-case validation ยังมีหน้าที่ของตนเอง | `Contracts/Authen/AuthenRequests.cs` — CODE |
| HTTP results / extensions | แปลง expected errors เป็น status และ ProblemDetails รวม error list โดยใช้ ErrorType แรกเป็นตัวเลือก status | `Result`/`Error` → `ObjectResult`/ProblemDetails; controller map success ตาม action | `Extensions/ResultExtensions.cs` — CODE |
| Composition / security pipeline | ลงทะเบียน controllers, CQRS, Infrastructure, options และ JWT Bearer/authorization; ต่อ exception/authentication/authorization middleware แล้ว map controllers | configuration + service registrations → backend host, resolved adapters และ request principal | `Program.cs` — CODE |

**ตัวอย่างการทำงาน:** action `me` มี `[Authorize]` อ่าน `sub` จาก principal แล้วสร้าง `GetCurrentUserQuery` ส่วน register รับ `RegisterRequest` แล้วสร้าง `RegisterCommand` Controller จึงรู้จักทั้ง HTTP boundary และ Application input แต่ไม่มี SQL หรือ password-hashing algorithm

**Boundary ที่ต้องรักษา:** สูตรธุรกิจอยู่ที่ Domain/model และขั้นตอน use case อยู่ที่ Handler ส่วนการ serialize request กับการตอบ status อยู่ API การเปิด JWT authentication ไม่ได้พิสูจน์ว่ามี live database token-revocation check หรือ permission resolution ครบแล้ว; baseline นี้ไม่มี callback ที่ตรวจ ACTIVE token row การเสนอ Redis admission middleware ยังเป็น PROPOSED ต้องออกแบบตำแหน่งและ failure contract เพิ่ม

Source: [AuthenController](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Api/Controllers/AuthenController.cs), [AuthenRequests](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Api/Contracts/Authen/AuthenRequests.cs), [ResultExtensions](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Api/Extensions/ResultExtensions.cs), [Program](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Api/Program.cs)

### 2.2 Application layer — use case และส่วนย่อยของการประสานงาน

Application รับเจตนาจาก caller แล้วทำ use case ให้ครบผ่านโมเดลและ ports เป็นเจ้าของลำดับขั้นตอน ขอบเขต transaction และผลที่ caller ของ use case ได้รับ โดยอ้างอิง Domain/Shared แทน concrete Infrastructure

| Sub-layer | หน้าที่และงานที่เป็นเจ้าของ | Input → Output / การประสานงาน | Source / สถานะ |
| --- | --- | --- | --- |
| Commands / Queries | ระบุ input และ intent ของ operation; command เปลี่ยน state ส่วน query อ่านข้อมูล | request record → handler contract ที่คืน `Result` หรือ `Result<T>`; record ไม่เรียก SQL/validator เอง | `Features/Authen/<UseCase>/*Command.cs`, `GetCurrentUserQuery.cs` — CODE |
| Validators | ตรวจ use-case input ก่อนเข้า handler และเรียก value-object factories สำหรับกฎของค่า | request → error list; Dispatcher รวม errors และหยุดก่อน handler เมื่อไม่ผ่าน | สี่ command validators — CODE; query `/me` ไม่มี validator |
| Handlers | โหลดข้อเท็จจริง เรียก entity/business behavior และ ports จัดลำดับและ transaction ของ use case แล้วตัดสิน expected outcome | Command/Query → repository/security calls + Result/response; ไม่รับ concrete DB/SDK clients | Authen ห้า handlers — CODE |
| Mapping / Responses | เลือกข้อมูลที่ use case คืนและแปลงจากโมเดลเป็น output ที่ caller ใช้ | `User`/issued tokens → register/login/current-user response records; บาง commands คืน Result ไม่มี DTO | `Features/Authen/Mapping/AuthenMappings.cs` และ response records — CODE |
| Ports / Common | กำหนดความสามารถด้าน transaction, password, token และ email ที่ use case ต้องใช้; รวม validation results และระบุ assembly สำหรับ DI scan | interface calls → adapter ที่ API bind; validation results → error list | `Abstractions/`, `Common/ValidationErrors.cs`, `AssemblyReference.cs` — CODE |

**ตัวอย่างการทำงาน:** `RegisterCommandHandler` ตรวจชื่อ/email ซ้ำผ่าน repository สร้าง `User` และ credential แล้วเรียก `IUnitOfWork` เพื่อบันทึก user/password ใน transaction เดียว ขณะที่ `LoginCommandHandler` โหลด user/credential, verify, เรียก `EnsureCanSignIn()` และบันทึก tokens การเรียก `Authen/Domain/` เป็นส่วนที่จะมีเมื่อ implement business operations ตาม design

**Boundary ที่ต้องรักษา:** Handler ประสาน operation ของ feature โดยไม่คัดลอก reusable formula หรือ model invariant ไปหลาย use cases Validators ปัจจุบันเป็น synchronous contracts จึงไม่ใช่จุดซ่อน database I/O ส่วน authorization/use-case response policy ต้องประสานกับ identity และ business rules ที่เกี่ยวข้อง ไม่ได้เกิดอัตโนมัติจาก `ICommand` หรือ DI

Source: [Register handler](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Application/Features/Authen/Register/RegisterCommandHandler.cs), [Register validator](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Application/Features/Authen/Register/RegisterCommandValidator.cs), [IUnitOfWork](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Application/Abstractions/IUnitOfWork.cs), [ValidationErrors](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Application/Common/ValidationErrors.cs)

### 2.3 Domain layer — โมเดล กฎธุรกิจ และ Business Domain

Domain แสดงความหมายที่ธุรกิจยอมรับ: ค่าที่ถูกต้อง state/transition ที่อนุญาต และผลของ business operation โดยแยกการตัดสินกฎออกจาก HTTP และ concrete storage ภายใน layer มีหน้าที่หลายแบบ ไม่ใช่ business service class อย่างเดียว

| Sub-layer | หน้าที่และงานที่เป็นเจ้าของ | Input → Output / การประสานงาน | Source / สถานะ |
| --- | --- | --- | --- |
| Entities / Aggregates | ถือ identity และ state; ควบคุม behavior/transition ของตัวเอง; aggregate root เป็นขอบเขต invariant ที่ต้องออกแบบให้ชัด | typed identity/values + current state → entity หรือ success/failure ของ transition | `Authen/Entities/User.cs`, `PasswordResetToken.cs` — CODE; User มี aggregate-root marker |
| ValueObjects | นิยาม business values, validity, normalization และ value equality | raw values → typed value หรือ validation errors เช่น `Username.Create`, `PlainPassword.Create` | `Authen/ValueObjects/` — CODE |
| Business Domain — Service = Domain | รวม business operations ที่ใช้ซ้ำหรือไม่มี entity เดียวเป็นเจ้าของตาม convention ของโครงการ | business facts/values/models/policy → business result ที่ Handler นำไปใช้ต่อ | `Authen/Domain/` — OWNER-DIRECTED DESIGN; ยังไม่มี implementation |
| Repository contracts | กำหนด interface สำหรับอ่าน/บันทึกโมเดลตามความต้องการของชั้นใน โดยไม่รู้ Dapper/Npgsql/SQL syntax | typed ids/values/entities → async result; Application ใช้ interfaces เหล่านี้ได้โดยตรง | `Authen/Repositories/IAuthenRepositories.cs` — CODE |
| Common / Errors / Status | ให้ entity/value equality, aggregate-root marker, domain status และ expected failure vocabulary | identity/value components/state → primitives, `UserStatus`, `AuthenErrors`; unique-write failure สื่อด้วย `DuplicateKeyException` | `Common/`, `AuthenErrors.cs`, `UserStatus.cs`, `DuplicateKeyException.cs` — CODE |

**ตัวอย่างการทำงาน:** `User.Register()` สร้าง Active user, `EnsureCanSignIn()` ปฏิเสธบัญชีที่ไม่ Active, `PasswordResetToken.Consume(now)` เปลี่ยน state เมื่อ token ยังใช้ได้ และ `PlainPassword.Create()` ตรวจความแข็งแรงของรหัสใหม่ Business Domain ที่เพิ่มในอนาคตใช้ behavior เหล่านี้ร่วมกันได้ โดยไม่ต้องย้ายทุก invariant ออกจากโมเดล

**Boundary ที่ต้องรักษา:** User มี marker แต่ password/token ถูกเรียกผ่าน repos แยก จึงยังสรุปไม่ได้ว่า User aggregate ควบคุมทุก credential/session lifecycle แล้ว กฎข้ามหลาย requests ต้องมี persistence guard ร่วมด้วย `Restore()` ใช้สร้าง model กลับจาก storage ตาม convention; public factory นี้ไม่ได้บังคับ caller ด้วย compiler และ `PasswordCredential` ที่เปิดเผย arrays ยังต้องพิจารณา immutability แยก

Source: [Entity](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Domain/Common/Entity.cs), [ValueObject](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Domain/Common/ValueObject.cs), [repository contracts](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Domain/Authen/Repositories/IAuthenRepositories.cs), [AuthenErrors](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Domain/Authen/AuthenErrors.cs)

### 2.4 Infrastructure layer — adapters และรายละเอียดเทคโนโลยี

Infrastructure ทำงานกับโลกภายนอกตาม ports ที่ Domain/Application ประกาศ รับผิดชอบ persistence mappings, connection lifecycle, SQL/cryptography และ provider-specific failures พร้อมแปลงผลกลับเป็นชนิดที่ชั้นในใช้ได้

| Sub-layer | หน้าที่และงานที่เป็นเจ้าของ | Input → Output / การประสานงาน | Source / สถานะ |
| --- | --- | --- | --- |
| Repository adapters | ทำ parameterized SQL, map rows, encrypt/decrypt stored fields และ hydrate domain models | repository calls/typed values → DB commands/rows → User/credential/token หรือ translated failure | `Persistence/Authen/{User,Password,Token}Repository.cs` — CODE |
| DbSession / connection | แชร์ lazy-opened connection และ transaction ใน DI scope ส่ง transaction/cancellation ให้ Dapper และ dispose resources | SQL + parameters + cancellation → affected rows/scalar/mapped rows | `Persistence/DbSession.cs` — CODE |
| UnitOfWork / transaction adapter | implement transaction port โดย begin/commit/rollback และ reuse transaction ที่มีอยู่ | async delegate → committed writes หรือ rollback เมื่อ exception | `Persistence/UnitOfWork.cs` — CODE; Handler เลือกขอบเขตงาน |
| Security adapters | implement password derivation/verification, JWT/opaque-token generation, token hashing และ field protection | credential/plain input/config/time → verified flag, hashes, issued tokens หรือ protected values | `Security/Pbkdf2PasswordHasher.cs`, `TokenService.cs`, `FieldProtector.cs` — CODE |
| Email adapter | ทำงานตาม email port; ปัจจุบันเป็น development logging stand-in | reset-email arguments → completed task/logs; ไม่ได้ส่ง email จริง | `Email/LoggingEmailSender.cs` — CODE, development-only |
| Options / DI registration | อ่าน settings, ทำ startup validation ที่มีใน source, สร้าง clients และจับคู่ interfaces กับ lifetimes | configuration → options + singleton/scoped services ให้ composition root ใช้ | `Options/InfrastructureOptions.cs`, `DependencyInjection.cs` — CODE |
| Proposed data adapters | แยก cache, shared admission, configuration snapshots และ event/projection stores ตามบทบาทที่เสนอ | ports ที่ต้องออกแบบ → Redis/MongoDB operations และ failure contract | Caching/RateLimiting/Configuration/Documents ในภาพ — PROPOSED; ยังไม่มีไฟล์จริงใน baseline |

**ตัวอย่างการทำงาน:** `UserRepository` encrypt ค่าเพื่อค้น/insert แล้ว decrypt และ `Restore()` กลับเป็น User; `PasswordRepository.SetAsync()` ปิด password เดิมแล้ว insert ใหม่; `TokenRepository` บันทึก hashes และ revoke rows ส่วน `UnitOfWork` ใช้ DbSession เดียวกันให้ repositories อยู่ใน transaction ของ use case

**Boundary ที่ต้องรักษา:** transaction adapter commit เมื่อ delegate จบตามปกติและ rollback เมื่อ exception โดยไม่ได้อ่าน `Result.Failure` เพื่อเลือก rollback ให้เอง การอ่านก่อนเขียนจึงยังต้องออกแบบ concurrency/zero-row outcomes ตามกฎจริง DbSession/repositories เป็น scoped ส่วน data source/security/email services ตาม DI ปัจจุบันเป็น singleton; singleton ไม่ควรถือ scoped connection ของ request

Source: [DbSession](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Infrastructure/Persistence/DbSession.cs), [UnitOfWork](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Infrastructure/Persistence/UnitOfWork.cs), [security options](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Infrastructure/Options/InfrastructureOptions.cs), [LoggingEmailSender](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Infrastructure/Email/LoggingEmailSender.cs)

### 2.5 Shared layer — กลไกกลางของ request และผลลัพธ์

Shared ให้ชนิดและกลไกที่ feature code ใช้ร่วมกัน โดยไม่มี project reference ไปยัง layer อื่น ใน baseline มี CQRS และ Results; handler/validator implementations ยังเป็นของ Application และ business rules ยังมีเจ้าของใน feature ของตน

| Sub-layer | หน้าที่และงานที่เป็นเจ้าของ | Input → Output / การประสานงาน | Source / สถานะ |
| --- | --- | --- | --- |
| Messaging contracts | ประกาศ request, command/query, handler, validator และ dispatcher interfaces รวม generic response constraints | Command/Query type → handler/validator contracts ที่ registration และ dispatcher resolve | `Cqrs/Messaging.cs` — CODE |
| Dispatcher / registration | scan Application assemblies เพื่อลงทะเบียน scoped handlers/validators; cache executors และเรียก validators ก่อน handler | request → validation failure หรือ delegated `HandleAsync()` result | `Cqrs/Dispatcher.cs`, `CqrsServiceCollectionExtensions.cs` — CODE |
| Results / Errors | ให้ success/failure, typed value และ expected-error vocabulary โดยไม่ผูก ASP.NET Core response | value/error list → `Result`, `Result<T>`, `Error`; API จึงค่อย map status | `Results/Result.cs`, `Error.cs` — CODE |

**ตัวอย่างการทำงาน:** Controller เรียก `IDispatcher.SendAsync()`; dispatcher รวม error lists ของ validators ถ้าไม่ว่างใช้ failure factory ของ response type ถ้าไม่มี errorจึง resolve handler และ await การทำงาน การ scan ผ่าน `AddCqrs(AssemblyReference.Assembly)` จึงช่วยให้เพิ่ม use case ตาม conventions ได้โดยไม่ลงทะเบียน handler ทีละตัว

**Boundary ที่ต้องรักษา:** `Result<T>.Value` ใช้ได้เมื่อ success; อ่านจาก failure จะ throw Shared ไม่ได้ map HTTP, เปิด transaction, ตรวจสิทธิ์หรือบังคับ query ให้ read-only โดยอัตโนมัติ และยังมี DI abstractions package dependency แม้ไม่มี project references การเพิ่ม code กลางต้องรักษาทิศทาง dependency นี้

Source: [Messaging contracts](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Shared/Cqrs/Messaging.cs), [CQRS registration](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Shared/Cqrs/CqrsServiceCollectionExtensions.cs), [Result](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Shared/Results/Result.cs), [Error](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Shared/Results/Error.cs)


### 2.6 เส้นทางที่มีอยู่แล้ว

```text
HTTP request
  -> Controller สร้าง Command / Query
  -> Dispatcher เรียก validators ที่ลงทะเบียน
       -> มี validation error: คืน failure และไม่เรียก Handler
       -> ผ่าน: เรียก Handler
  -> Handler ใช้ Entity / ValueObject และ repository/security ports
  -> Infrastructure ทำ I/O และ SQL
  -> Handler map เป็น response
  -> Controller คืน HTTP response
```

มี validators ของสี่ commands ส่วน `GetCurrentUserQuery` ไม่มี validator ใน baseline Dispatcher ไม่ได้เปิด transaction หรือเพิ่ม authorization/retry policy ให้อัตโนมัติ

### 2.7 เส้นทาง Business Domain ตาม convention ที่กำหนด

```text
Handler โหลดข้อเท็จจริงที่ use case ต้องใช้
  -> เรียก business operation ใน <Feature>/Domain/
  -> Domain ใช้กฎร่วมกับ Entity / ValueObject และคืน business result
  -> Handler ประสานการบันทึกผ่าน ports / transaction boundary
  -> Infrastructure จัดการ SQL / external systems
```

ส่วน `Handler -> Authen/Domain/` ยังเป็น owner-directed design ตามเส้นและป้ายในภาพ ไม่ใช่ call ที่พบแล้วใน pinned source Handler ยังคงเป็น Application use case ขณะที่ Domain เป็นส่วนทำ business logic ที่นำไปใช้ซ้ำได้ ไม่ใช่ backend service ที่ deploy แยก

### 2.8 ความรับผิดชอบที่พาดหลาย layers

| เรื่อง | การแบ่งหน้าที่ระหว่าง sub-layers | สิ่งที่ต้องตรวจร่วมกัน |
| --- | --- | --- |
| Validation | API bind/deserialize HTTP contract; Application validator ตรวจ input โดยเรียก Domain value factories; Shared dispatcher คุมว่าจะเรียก handler ต่อหรือไม่ | รูปแบบ HTTP, use-case constraints และ model invariant มีเจ้าของต่างกัน; baseline validators ไม่อ่าน DB |
| Authentication / authorization | API middleware สร้าง principal และ action อ่าน identity; Handler ประสาน use-case permission/credential checks; Domain ตรวจ model condition; Infrastructure verify hash/ออก JWT | JWT signature ผ่านไม่ได้หมายถึง user/token row ยัง Active หรือมีสิทธิ์ธุรกิจครบทุกข้อ ต้องดู implementation จริง |
| Transaction / concurrency | Handler เลือกชุด writes; `IUnitOfWork` เป็น Application port; Infrastructure UnitOfWork/DbSession ส่ง SQL ใน transaction; Domain สื่อ invariant | rollback, lock order, conditional update และ zero-row result ต้องสอดคล้องกัน; Result failure ไม่ใช่ exception ที่ rollback เอง |
| Expected failure / HTTP | Domain/Application คืนเหตุผล; Shared จัด Result/Error; Application กำหนด public use-case outcome ตาม policy; API map HTTP | baseline login ส่ง AccountNotActive ออกตรง ๆ จึงต้องเทียบกับ spec เรื่อง generic authentication failure |
| Dependency composition | API Program เรียก DI registrations; Application/Domain ใช้ inner contracts; Infrastructure implement ports; Shared ให้ชนิดร่วม | runtime call ไป adapter ไม่ใช่ project reference จากชั้นในออก Infrastructure |

ตัวอย่าง register เชื่อมส่วนย่อยดังนี้: HTTP Contracts/Controller → Shared Dispatcher → Application Validator ที่ใช้ Domain ValueObjects → Application Handler ที่เรียก User factory และ repository/hasher ports → Infrastructure repositories/UnitOfWork → Application Mapping → API success 201 ส่วน query `/me` ไม่มี command validator และไม่เปิด write transaction จึงไม่ต้องผ่านเส้นทางเดียวกันทุกขั้น

## 3. Repository: โค้ดอยู่ตรงไหน และ project ใดอ้างอิงกันได้

![Repository architecture: source projects, feature packages, tests และ Authen/Domain ที่ยังเป็น owner-directed design](../diagram/reference/repository/repository-architecture.drawio.png)

[เปิดภาพขนาดเต็ม](../diagram/reference/repository/repository-architecture.drawio.png) · [draw.io source](../diagram/reference/repository/repository-architecture.drawio) · [คำอธิบายภาพ](../diagram/reference/repository/repository-architecture.md) · [HTML preview](../diagram/reference/repository/repository-architecture.html)

ภาพนี้เป็นแผนที่ source ownership และ compile-time dependencies ซึ่งเป็นคนละมุมกับ runtime architecture เส้น `REF` แปลว่ามี `ProjectReference` ใน `.csproj` การมี runtime call ผ่าน interface ไม่ได้ทำให้ project ชั้นในต้องอ้างอิง concrete Infrastructure

### 3.1 ขอบเขตสอง repositories

```text
Showcase: system-analysis-and-design/
└── e-commerce/
    ├── REPOS.md                 # identity / remote / pinned revision
    ├── api/                     # API contract
    ├── db/                      # migrations และ database tests
    ├── doc/                     # specifications และคู่มือฉบับนี้
    ├── diagram/                 # diagram bundles
    └── repository/
        ├── .gitkeep
        └── e-commerce-backend/   # independent Git clone; Showcase ignore
            ├── .git/
            ├── Ecommerce.sln
            ├── Directory.Build.props
            ├── README.md
            ├── project-structure.md
            ├── code.md
            ├── src/
            └── tests/
```

แก้ backend code และส่ง commit/PR ที่ remote ของ component ส่วน manifest/specifications/diagrams และเอกสารฉบับนี้เป็นของ Showcase เมื่อจะเลื่อน baseline ให้ส่งมอบและ verify component commit บน remote ก่อนปรับ `revision` ใน manifest ห้าม stage child code หรือ child `.git` เข้าฝั่ง Showcase

### 3.2 Project references ที่พบจริง

| Project                       | อ้างอิง projects                      |
| ----------------------------- | ----------------------------------- |
| `Ecommerce.Api`               | Application, Infrastructure, Shared |
| `Ecommerce.Application`       | Domain, Shared                      |
| `Ecommerce.Domain`            | Shared                              |
| `Ecommerce.Infrastructure`    | Application, Domain, Shared         |
| `Ecommerce.Shared`            | ไม่มี project reference               |
| `Ecommerce.Domain.Tests`      | Domain, Shared                      |
| `Ecommerce.Application.Tests` | Application, Domain, Shared         |

รวม 9 production references และ 5 test references ตาม source ที่ pin Domain และ Application ไม่ reference Infrastructure ส่วน Shared มี DI abstractions package อยู่แล้ว คำว่าไม่มี project reference จึงไม่ได้แปลว่าไม่มี external-package dependency

`Authen/Domain/` อยู่ภายใน `Ecommerce.Domain.csproj` เดิม การใช้โฟลเดอร์นี้จึงไม่ได้เพิ่ม project หรือเปลี่ยน dependency graph ด้วยตัวมันเอง

## 4. การจัดโค้ดตาม feature และ use case

Application จัดกลุ่ม `Features/<Feature>/<UseCase>/` เพื่อให้ input, validator, handler และ output ของ use case อยู่ใกล้กัน ตัวอย่าง Authen ปัจจุบัน:

```text
Ecommerce.Application/
├── Abstractions/
│   ├── IUnitOfWork.cs
│   ├── IPasswordHasher.cs
│   ├── ITokenService.cs
│   └── IEmailSender.cs
└── Features/Authen/
    ├── Register/
    │   ├── RegisterCommand.cs
    │   ├── RegisterCommandValidator.cs
    │   ├── RegisterCommandHandler.cs
    │   └── RegisterResponse.cs
    ├── Login/
    ├── ResetPassword/       # request link และ confirm เป็นคนละ command/handler
    ├── GetCurrentUser/
    └── Mapping/AuthenMappings.cs
```

| ส่วน                      | หน้าที่และตัวอย่าง                                                                           |
| ------------------------ | --------------------------------------------------------------------------------------- |
| Command / Query          | input record ระบุเจตนาของ operation โดยไม่รับผิดชอบ HTTP หรือ SQL                            |
| Validator                | ตรวจ request constraints; เรียก value-object factories สำหรับกฎค่าที่มีอยู่แล้ว                   |
| Handler                  | ประสานขั้นตอน โหลดข้อมูล เรียก business/model behavior และ ports จัด transaction ตาม use case |
| Response / Mapping       | แปลงผลเป็น DTO ที่ caller ใช้ ไม่คืน domain entity ออกตรง ๆ                                   |
| Application abstractions | ports สำหรับ transaction, hashing, token issuing และ email โดยไม่ import concrete adapter  |

ไม่จำเป็นต้องมีไฟล์เหมือนกันทุก use case: `Register` และ `Login` คืน typed response, request/confirm reset คืน `Result` ไม่มี response DTO เฉพาะ ส่วน query `/me` คืน `CurrentUserResponse` และไม่มี validator เฉพาะ

ดู source: [RegisterCommandHandler](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Application/Features/Authen/Register/RegisterCommandHandler.cs), [LoginCommandHandler](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Application/Features/Authen/Login/LoginCommandHandler.cs), [AuthenMappings](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Application/Features/Authen/Mapping/AuthenMappings.cs)

## 5. Service = Domain: ที่เก็บ business operations

โครงสร้างของ feature ใน Domain layer ให้อ่านตามนี้ โดยบรรทัด `Domain/` เป็นตำแหน่งตาม owner convention ที่ยังไม่มีใน source baseline:

```text
Ecommerce.Domain/
├── Common/                  # Entity, ValueObject, IAggregateRoot
└── Authen/
    ├── Entities/            # CODE: User, PasswordResetToken
    ├── ValueObjects/        # CODE: business values และกฎของค่า
    ├── Repositories/        # CODE: IUser/IPassword/ITokenRepository
    ├── Domain/              # OWNER CONVENTION: reusable Authen business operations
    │                        # ยังไม่ implement ที่ pinned revision
    ├── AuthenErrors.cs
    └── UserStatus.cs
```

### 5.1 Domain ควรรับผิดชอบอะไร

- ใช้กฎและตัดสินผลทางธุรกิจจากข้อมูลที่จำเป็น เช่นประเมิน business condition หรือคำนวณผลจาก business values/policy
- รวม operation ที่ต้องใช้ซ้ำระหว่าง use cases เพื่อให้ handlers ใช้กฎชุดเดียวกัน
- ทำงานร่วมกับ entity/value object โดยคงเจ้าของ invariant ที่ชัดเจน
- คืน business result หรือ failure ที่ Application นำไปทำขั้นตอนต่อได้

ข้อมูลภายนอกที่จำเป็นต่อกฎให้ Handler โหลดแล้วส่งเข้า Domain ตาม contract ที่ออกแบบ หรือใช้งานผ่าน inner abstraction ที่อนุมัติไว้ Domain ไม่รับ concrete SQL connection, Redis/MongoDB client หรือ HTTP request DTO และไม่เป็นเจ้าของ SQL commit

ตัวอย่าง “คำนวณภาษี” อธิบายประเภทของ reusable business operation เท่านั้น ต้องอยู่ใน feature ที่เป็นเจ้าของกฎการเงินจริง เอกสารนี้ไม่ได้เพิ่ม tax class ใน Authen หรือกำหนดอัตรา สูตร และการปัดเศษ

### 5.2 Handler และ Domain แบ่งงานอย่างไร

| คำถาม                                                    | เจ้าของหลัก                                                            |
| ------------------------------------------------------- | -------------------------------------------------------------------- |
| request นี้ต้องทำขั้นตอนใด เรียก ports ใด และตอบ caller อย่างไร | Application Handler                                                  |
| กฎธุรกิจจากข้อเท็จจริงเหล่านี้ยอมรับอะไรหรือคำนวณได้เท่าใด           | feature `Domain/` ตาม convention นี้ หรือ behavior ของโมเดลที่เป็นเจ้าของกฎ |
| entity อยู่ในสถานะที่อนุญาตให้เปลี่ยนหรือไม่                      | Entity / Aggregate behavior                                          |
| ค่านี้ valid และมีความหมายอย่างไร                            | ValueObject                                                          |
| อ่าน/เขียนแถวใด hash อย่างไร หรือเรียก provider ด้วย SDK ใด   | Infrastructure ผ่าน ports                                             |
| แปลงผลเป็น status code/HTTP payload อย่างไร               | API boundary ตาม public contract                                     |

การมี `Domain/` ไม่ได้บังคับให้ย้าย invariant ของ entities/value objects ออกทั้งหมด จุดประสงค์คือเพิ่มเจ้าของ business operations ที่ชัดเจนและใช้ซ้ำได้ ตามที่เจ้าของงานต้องการ

### 5.3 กฎที่พบใน source และประเด็นที่จะออกแบบต่อ

| กฎ                                                 | ตำแหน่งปัจจุบัน                                                | การอ่านร่วมกับ Business Domain                                                                                          |
| -------------------------------------------------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| user ใหม่เริ่ม Active                                 | `User.Register()`                                         | เป็น factory behavior ของ entity ที่มีอยู่                                                                                 |
| Active user จึง sign in ได้                          | `User.EnsureCanSignIn()`                                  | Handler เรียกจริง; reusable operation ใช้ behavior นี้ต่อได้                                                                |
| reset token ต้องยังไม่ถูกใช้และไม่หมดอายุ                 | `PasswordResetToken.Consume(now)`                         | model guard มีแล้ว แต่ persistence concurrency ยังต้องรับประกันร่วมกัน                                                        |
| username/email/password ใหม่มีรูปแบบถูกต้อง             | value-object factories                                    | validator/handler เรียกกฎชุดเดียวกัน ไม่ต้องคัดลอก regex/policy ไว้หลาย handlers                                             |
| username/email ต้องไม่ซ้ำ                              | register handler เช็ก repository และรับ duplicate exception | ต้องมีฐานข้อมูลช่วยป้องกัน race; ไม่ย้าย SQL ไปไว้ใน business class                                                            |
| login throttle, reset-request limit, refresh reuse | ยังไม่มี flow ครบใน baseline                                 | ต้องออกแบบ business operation, input facts, persistence guards และ failure outcomes ตาม governing specs ก่อน implement |

Source: [User](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Domain/Authen/Entities/User.cs), [PasswordResetToken](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Domain/Authen/Entities/PasswordResetToken.cs), [PlainPassword](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Domain/Authen/ValueObjects/PlainPassword.cs)

## 6. CQRS และการเรียก Business Domain

Command รับผิดชอบ operation ที่เปลี่ยน state ส่วน Query รับผิดชอบอ่านข้อมูล ทั้งสองแยก input/handler ของตนเองผ่าน contracts ใน Shared การตั้งชื่อหรือสร้างโฟลเดอร์เพียงอย่างเดียวไม่ได้พิสูจน์ว่าการแบ่ง behavior ถูกต้อง

| ฝั่ง      | ตัวอย่างปัจจุบัน                                          | Business Domain เกี่ยวข้องอย่างไร                                                                               |
| ------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Command | Register, Login, RequestPasswordReset, ResetPassword | Handler ใช้ model behavior ปัจจุบัน และสามารถเรียก business operations ใน `Domain/` เมื่อส่วนนี้ถูก implement ตาม spec |
| Query   | GetCurrentUser                                       | คืนข้อมูลที่ต้องการ; ไม่จำเป็นต้องเรียก business operation ที่เปลี่ยน state                                                |

Login เป็น command แม้คืน token เพราะเขียน token rows ในฐานข้อมูล ส่วน query ปัจจุบันโหลด `User` ผ่าน `IUserRepository` ที่ใช้ร่วมกับ commands แล้ว map เป็น DTO ยังไม่มี query-specific read port หรือ read projection แยกใน source การตัดสินใจเพิ่มสิ่งเหล่านั้นต้องดูความต้องการของ read/write models โดยตรง

Dispatcher เรียก validators ก่อน handler เมื่อมี errors จะไม่เรียก handler ส่วน transaction และ business orchestration ยังเป็นความรับผิดชอบของ use case ไม่ได้เกิดจาก marker `ICommand` หรือ `IQuery` โดยอัตโนมัติ

Source: [Messaging](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Shared/Cqrs/Messaging.cs), [Dispatcher](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Shared/Cqrs/Dispatcher.cs), [GetCurrentUserQueryHandler](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Application/Features/Authen/GetCurrentUser/GetCurrentUserQueryHandler.cs)

## 7. Infrastructure และความถูกต้องข้าม requests

Application เรียก interfaces ส่วน Infrastructure implement ด้วยเทคโนโลยีจริง:

| Port / responsibility                 | Implementation                                                 |
| ------------------------------------- | -------------------------------------------------------------- |
| User, password และ token repositories | Dapper/Npgsql repositories ใน `Persistence/Authen/`            |
| Transaction coordination              | Handler เรียก `IUnitOfWork`; `UnitOfWork` ใช้ scoped `DbSession` |
| Password hashing                      | `Pbkdf2PasswordHasher`                                         |
| JWT และ opaque tokens                 | `TokenService`                                                 |
| Stored personal-field protection      | `FieldProtector`                                               |
| Reset email                           | `LoggingEmailSender` เป็น development stub                      |

Business rule บางข้อจำเป็นต้องมีทั้งกฎใน code และ database guard เช่น `Consume()` ป้องกันการใช้ token ซ้ำบน object ที่โหลดมา แต่สอง requests อาจโหลดคนละ object ก่อนเขียน ดังนั้น single-use ระหว่าง requests ยังต้องมี lock/conditional update และผล zero-row write ที่ Application จัดการได้

baseline ปัจจุบันยังใช้ reset consume SQL ที่มีเพียง `WHERE id = @id` และไม่ได้ส่งผลชนะ/แพ้การแข่งขันกลับเป็น business outcome การมี `Authen/Domain/` เพิ่มใน design จึงต้องออกแบบ I/O contract และ transaction boundary ร่วมด้วย ไม่ได้ทำให้ invariant ข้าม requests สมบูรณ์เอง

Source: [TokenRepository](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Infrastructure/Persistence/Authen/TokenRepository.cs), [UnitOfWork](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Infrastructure/Persistence/UnitOfWork.cs), [DependencyInjection](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Infrastructure/DependencyInjection.cs)

## 8. Identity domain model: แนวคิดข้อมูลที่ business code ใช้

![Identity domain model: User, credentials, tokens, consent และ authorization concepts ที่อ้างอิง schema](../diagram/domain/domain-identity-model.drawio.png)

[เปิดภาพขนาดเต็ม](../diagram/domain/domain-identity-model.drawio.png) · [draw.io source](../diagram/domain/domain-identity-model.drawio) · [คำอธิบายและ SQL traceability](../diagram/domain/domain-identity-model.md) · [HTML preview](../diagram/domain/domain-identity-model.html)

ภาพนี้เป็น conceptual interpretation จาก schema และยังอยู่ในสถานะ in-review ตาม companion document ลูกศร runtime และ project references จากสองภาพก่อนหน้าใช้ความหมายต่างจากเส้น association/cardinality ในภาพนี้

- กล่อง User, Credential, Reset request, Profile, Address, Token และ Login attempt สื่อแนวคิดข้อมูล ไม่ได้รับรองว่ามี C# classes ครบทุกกล่อง
- กล่อง `authen` รวมตาม schema ไม่ได้ประกาศว่า entities ทั้งหมดเป็น aggregate เดียว หรือทุก operation ต้องโหลดทุกอย่างพร้อมกัน
- Role, Permission, Scope และ grant associations อธิบายสิทธิ์จาก schema ไม่ใช่หลักฐานว่า JWT claims resolver ใน backend implement แล้ว
- การจับคู่ session ใช้ `session_id` ใน token tables ไม่ควรอนุมานว่ามี Session table หรือ `AuthSession` aggregate ใน code แล้ว
- Cardinality ในภาพพิจารณาทุกแถวรวมประวัติ ไม่ใช่ข้อสรุปว่ามี ACTIVE rows ได้เท่าใด ต้องอ่าน partial constraints ประกอบ

จึงใช้ภาพนี้ทำความเข้าใจข้อมูลที่ Business Domain ต้องใช้ ส่วนชื่อ operation, aggregate boundary, transaction และ contract ของ `Authen/Domain/` ต้องออกแบบจาก business rules ที่เกี่ยวข้องเพิ่มเติม

## 9. สิ่งที่มีแล้วและสิ่งที่ยังเป็น design

| ส่วน                                             | สถานะของ pinned component                                | วิธีใช้เอกสารและภาพ                                            |
| ----------------------------------------------- | -------------------------------------------------------- | ----------------------------------------------------------- |
| Five production projects / two test projects    | มีใน source                                               | ใช้อ้าง project layout และ references                         |
| Authen four commands / one query                | มีใน source                                               | ใช้ไล่ code flow โดยไม่สรุปว่าตรง latest specs ทุกข้อ              |
| Entity / ValueObject / repository interfaces    | มีใน source                                               | เป็น model behavior และ contracts ที่ Business Domain ใช้ร่วมได้  |
| `Authen/Domain/` business operations            | owner-selected convention; ยังไม่มี implementation          | ใช้เป็น design direction ก่อนกำหนด class/method/spec ให้ครบ      |
| Product, order, payment และ shipping operations | มีเอกสารใน Showcase; ยังไม่พบ implementation ใน component นี้ | อ่าน specs และ approval ของแต่ละเรื่องก่อนพัฒนา                   |
| Redis/MongoDB adapters, outbox/relay            | proposed/in-review ตาม diagram companions                | แยกจาก CODE; ไม่เพิ่ม SDK/worker/transaction สมมติใน flow ปัจจุบัน |

## 10. Tests และจุดตรวจเมื่อพัฒนา business operation

Test projects เป็นขอบเขต verification ของ production layers ไม่ใช่ runtime layers เพิ่มเติม ทั้งสอง project ใช้ xUnit และไม่เพิ่มขั้นตอนใน request flow

| Test project / ส่วนย่อย | สิ่งที่ทดสอบและ input/output | Dependency / ข้อจำกัด |
| --- | --- | --- |
| `Ecommerce.Domain.Tests/Authen/EntityTests.cs` | สร้าง/restore entities แล้วเรียก behavior; ตรวจ identity, Active-user condition และ reset-token expiry/consume | อ้าง Domain/Shared; พิสูจน์ model behavior ของ object ไม่ใช่ DB concurrency |
| `Ecommerce.Domain.Tests/Authen/ValueObjectTests.cs` | ส่งค่าปกติ/ค่าผิดขอบเขตเข้า factories แล้วตรวจ typed values/errors, normalization และ equality | ไม่เปิด HTTP/DB; ยังต้องตรวจ persistence mapping และ request contract ที่ชั้นอื่น |
| `Ecommerce.Application.Tests/Authen/AuthenHandlerTests.cs` | ส่ง commands ผ่าน dispatcher ให้ real handlers ทำงานกับ fakes แล้วตรวจผลและ side effects | อ้าง Application/Domain/Shared; ไม่ใช้ concrete Infrastructure |
| `Ecommerce.Application.Tests/Authen/Fakes.cs` | แทน repositories, hasher, token service, email และ unit of work ด้วยค่าที่ควบคุมได้ | `InlineUnitOfWork` ไม่ได้ทำ transaction จริง; fake password verification และ token revocation ไม่พิสูจน์ JWT middleware หรือ rollback |

Source: [Domain entity tests](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/tests/Ecommerce.Domain.Tests/Authen/EntityTests.cs), [Domain value tests](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/tests/Ecommerce.Domain.Tests/Authen/ValueObjectTests.cs), [Application handler tests](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/tests/Ecommerce.Application.Tests/Authen/AuthenHandlerTests.cs), [test fakes](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/tests/Ecommerce.Application.Tests/Authen/Fakes.cs)

สองชุดนี้ไม่มี integration test ที่พิสูจน์ SQL, transaction rollback, HTTP serialization หรือ JWT middleware จริง หาก requirement อยู่ที่ boundary เหล่านั้นต้องเลือก test ระดับที่แตะ implementation จริงเพิ่มเติม

เมื่อพัฒนา business operation ตาม spec ที่อนุมัติ ให้ตรวจอย่างน้อย:

1. Rule มีเจ้าของชัดว่าอยู่ใน `Domain/`, entity หรือ value object และใช้คำธุรกิจของ feature นั้น
2. Handler เป็นผู้ประสาน use case และใช้ business result อย่างถูกต้อง ไม่คัดลอกกฎไปหลาย handlers
3. Input/output ของ Domain ใช้ business values และไม่ผูก HTTP หรือ vendor SDK
4. Operation เปลี่ยน state ต้องมี transaction/concurrency contract ที่พิสูจน์ได้ร่วมกับ persistence
5. Query ที่ใช้ในการอ่านไม่มี write side effects ที่ซ่อนอยู่
6. Tests trace กลับไปยังกฎและ failure boundaries; ใช้ database/API tests เมื่อสิ่งที่ต้องพิสูจน์อยู่ข้าม process/connection
7. Update code guide, relevant specs และ diagrams ตามสถานะจริง โดยไม่เปลี่ยนป้าย PROPOSED เป็น CODE ก่อนมี implementation

## 11. แหล่งอ้างอิงและผลตรวจคู่มือนี้

- [Diagram index](../diagram/README.md) สำหรับภาพอื่น เช่น order lifecycle, checkout/payment sequences, outbox และ operational views ซึ่งไม่ได้ embed ทั้งหมดในคู่มือโครงสร้างโค้ดนี้
- [Component project-structure.md](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/project-structure.md) สำหรับ baseline file conventions
- [Component code.md](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/code.md) สำหรับ flow ปัจจุบันและ known gaps อย่างละเอียด; อ่านคู่กับ Service = Domain convention ที่ชี้แจงในเอกสารฉบับนี้
- [Manifest](../REPOS.md) และ [component-repositories rule](../../.agents/rules/component-repositories.md) สำหรับ Git ownership และ baseline pin

นำภาพเดิมสามภาพมา embed โดยไม่ copy, เปลี่ยนชื่อ หรือสร้างไฟล์ภาพใหม่ ตรวจภาพ PNG ที่ขนาดอ่านได้และตรวจ editable `.drawio`/PNG metadata parity พร้อม native nesting ผ่านทั้งสาม bundle ภาพที่ใช้มีขนาด 2378 × 1682 pixels ทุกภาพ

งานนี้ตรวจ frontmatter, references, source/model correspondence และความคงเดิมของ component/diagram assets ไม่ได้แก้ backend, API specs, schema หรือ diagram และไม่ได้รัน build/runtime tests ใหม่สำหรับงานเอกสารนี้

### 11.1 ผลตรวจสำหรับส่ง review — 9 พฤศจิกายน 2026

| รายการตรวจ                   | ผลและขอบเขต                                                                                                                                          |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Markdown/frontmatter         | YAML parse ผ่าน; คู่มือยังเป็น draft และ approval fields เป็น null; headings, tables และ code fences ถูกต้อง                                                  |
| Source references            | ลิงก์ภายในเปิดไฟล์/โฟลเดอร์ได้ และทุก reference ไป component ตรวจพบ commit/blob ที่ pin ไว้                                                          |
| ภาพประกอบ                    | PNG เดิมสามภาพ ขนาดภาพละ 2378 × 1682 pixels พร้อมลิงก์ไป editable sources และคำอธิบาย                                                                      |
| Editable model/PNG integrity | architecture 72 cells, repository 47 cells, identity 99 cells; metadata parity และ native nesting ผ่านทั้งสาม bundle                                    |
| Diagram preservation         | hashes ของ 12 ไฟล์ในสาม bundles ตรงก่อนและหลังเขียนคู่มือ; ไม่มีการวาดหรือ export ใหม่                                                                          |
| Component evidence           | component อยู่ที่ pinned SHA และ clean; project references รวม production 9 และ tests 5; `Authen/Domain/` ยังติดสถานะ owner-directed design ตาม source จริง |
| Visual review                | เปิดตรวจ PNG ที่นำมา embed แล้ว; ไม่มีการทดลองขยับกล่องหรือ re-export ใน native editor เพราะไม่ได้แก้ model                                                       |

ตารางนี้เป็นหลักฐานการตรวจคู่มือและการอ้างอิงภาพ ไม่ได้ใช้แทน runtime/database/API integration tests หรืออนุมัติ implementation ของ Business Domain

การตรวจรอบขยาย scope ครอบคลุมบทนำของทั้งห้า layers และรายละเอียด 24 กลุ่มหน้าที่ย่อยในหัวข้อ 2.1–2.5 แต่ละส่วนมีหน้าที่ input/output, collaborators, source/status และขอบเขต พร้อมคำอธิบาย validation/security/transaction/error ข้าม layers ในหัวข้อ 2.8 และ test-project responsibilities ในหัวข้อ 10 ตรวจเทียบกับ source จริงและตรวจว่าคู่มือก่อนแก้ยังไม่ผ่าน coverage gate นี้
