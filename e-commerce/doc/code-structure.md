---
name: E-commerce Layer and Sub-layer Code Structure Guide
description: Explains every backend layer and sub-layer, including responsibilities, inputs/outputs, boundaries, collaboration, source examples and existing diagrams. Use before placing code, developing a use case or reviewing architecture.
status: draft
approved_by: null
approved_at: null
observed_on: 2026-11-08
reviewed_on: 2026-11-09
source_component_revision: d8255183cba54d0c2b218607456b895a70df32f0
source_showcase_revision: f5580ed087c8ffcc6a740b256fcb6aacd36ec5ae
---

# E-commerce Code Structure: Every Layer and Sub-layer

## 1. Meaning and scope

This guide explains the e-commerce backend across **Presentation, Application, Domain, Infrastructure and Shared, including each layer's sub-layers**. It helps readers decide where code belongs, where its inputs come from, what work it owns and where its results go. The diagrams explain runtime collaboration, source ownership and business data concepts as distinct viewpoints.

### 1.1 Terms used across all layers

| Term | Meaning in this guide | Example |
| ------------------ | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Layer | A major responsibility and dependency boundary, currently separated into five production `.csproj` files | API handles HTTP; Domain owns business meaning and rules |
| Sub-layer | A responsibility group inside a layer, represented by folders, files or diagram elements; it does not automatically introduce another project or process | Controllers and Contracts belong to API; DbSession and UnitOfWork belong to Persistence |
| Feature | A business capability grouping related models and use cases | Authen |
| Use case / Handler | A use case is an operation requested by a caller; a handler is the Application class that coordinates its execution | Register, Login, RequestPasswordReset, ResetPassword, GetCurrentUser |
| Contract / DTO | A data shape used across a boundary, separate from a domain entity's state | HTTP requests, Command/Query inputs and response records |
| Port | An inner-layer interface describing a required capability independently of concrete technology | `IUserRepository`, `IUnitOfWork`, `IPasswordHasher` |
| Adapter | A technology-specific implementation of a port | Dapper repositories, `UnitOfWork`, password hasher |

### 1.2 Overview of all five layers

| Layer / project | Question it owns | Inputs and outputs | Sub-layers covered |
| ------------------------------------------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Presentation — `Ecommerce.Api` | How is an HTTP request accepted and its outcome communicated? | HTTP/contracts/principal → Application request → HTTP status/payload | Controllers, Contracts/model binding, HTTP results, Composition/security pipeline |
| Application — `Ecommerce.Application` | Which steps and collaborators complete this use case? | Command/Query → loaded facts, rule/port calls → Result/response DTO | Commands/Queries, Validators, Handlers, Mapping/Responses, Ports/Common |
| Domain — `Ecommerce.Domain` | Which values, states and decisions does the business accept? | Business values/state/facts → business result or state transition through behavior | Entities/Aggregates, ValueObjects, Business Domain, Repository contracts, Common/Errors/Status |
| Infrastructure — `Ecommerce.Infrastructure` | How do databases, cryptography and external systems perform the work? | Port calls and required values → I/O data/outcomes or infrastructure failures | Repositories, DbSession, UnitOfWork, Security, Email, Options/DI and proposed adapters |
| Shared — `Ecommerce.Shared` | Which common mechanisms are shared across features? | Request/result types → handler dispatch and shared success/failure contracts | Messaging contracts, Dispatcher/Registration, Results/Errors |

These layers do not prescribe an API → Application → Domain → Infrastructure → Shared sequence for every request. Shared supplies building blocks referenced by several layers; runtime calls follow interfaces and DI for each use case. Section 2 explains sub-layer responsibilities and boundaries. Section 3 distinguishes project references from runtime calls.

### 1.3 Convention, source baseline and evidence status

Within the Domain layer, this project uses **Service = Domain** to mean reusable business operations, with the owner-selected path `src/Ecommerce.Domain/<Feature>/Domain/`, such as `Authen/Domain/`. Entities and ValueObjects retain their own invariants. Sections 2.3 and 5 explain this convention. Infrastructure services such as `TokenService` retain their technical responsibilities under their respective ports.

**Baseline:** The inspected code is the [e-commerce-backend](https://github.com/ittikornsopawan/e-commerce-backend/tree/d8255183cba54d0c2b218607456b895a70df32f0) Component Repository pinned by [REPOS.md](../REPOS.md). It contains five production projects, two test projects and five Authen use cases. `Authen/Domain/` is an owner-directed design without an implementation at this commit. The domain model diagram describes data concepts rather than an inventory of existing business service classes.

This document covers every layer/sub-layer, its responsibilities, inputs/outputs, collaboration, limitations and observed source examples, distinguishing CODE, SPEC and PROPOSED as the diagrams do. The guide remains a draft. Describing a design does not approve new business behavior; inspect the governing specification and its approval before implementation, following the [SDD workflow](../../.agents/workflows/spec-driven-development.md).


## 2. Architecture: Responsibilities during request execution

![Runtime architecture: Presentation, Application, Domain, Infrastructure and Shared with CODE, SPEC and PROPOSED status](../diagram/main/architecture-design.drawio.png)

[Full-size image](../diagram/main/architecture-design.drawio.png) · [Edit in draw.io](../diagram/main/architecture-design.drawio) · [Diagram companion](../diagram/main/architecture-design.md) · [HTML preview](../diagram/main/architecture-design.html)

This diagram explains logical layers and runtime collaboration within one ASP.NET Core backend application. Nested boxes identify responsibility ownership; arrows show selected calls. They do not represent compile-time project references or require every request to pass through every box.

| Diagram label | Interpretation |
| -------------------------- | --------------------------------------------------------------------------------- |
| `CODE` | Source exists for the indicated element in the pinned backend; behavioral completeness still requires comparison with its specification |
| `SPEC` | A document defines the behavior; inspect its approval status. This label does not establish backend implementation |
| `PROPOSED` | An addition without implementation, such as Redis/MongoDB adapters and an outbox |
| `PROPOSED · OWNER REQUEST` | The owner selected the Business Domain position in the diagram; the pinned source does not yet contain that folder or its classes |

### 2.1 Presentation / API layer — HTTP boundary and system composition

API connects the caller to Application. It owns HTTP semantics, the authenticated principal and construction of the dependency graph. Request handling, business decisions and concrete I/O have separate owners even when one request invokes all three.

| Sub-layer | Responsibilities and owned work | Input → Output / collaboration | Source / status |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| Controllers | Define routes, accept action arguments, construct Command/Query inputs, invoke the dispatcher and select success responses | HTTP action input → Application request → Result → HTTP response | `Controllers/AuthenController.cs` — CODE |
| Contracts / model binding | Define accepted body shapes for ASP.NET Core to bind/deserialize into request records before constructing use-case inputs | JSON/body → `RegisterRequest`, `LoginRequest` and reset request records; use-case validation remains a separate responsibility | `Contracts/Authen/AuthenRequests.cs` — CODE |
| HTTP results / extensions | Translate expected errors into status codes and ProblemDetails, retaining the error list and selecting status from the first ErrorType | `Result`/`Error` → `ObjectResult`/ProblemDetails; controllers map successful outcomes per action | `Extensions/ResultExtensions.cs` — CODE |
| Composition / security pipeline | Register controllers, CQRS, Infrastructure, options and JWT Bearer/authorization; compose exception/authentication/authorization middleware and map controllers | Configuration and service registrations → backend host, resolved adapters and request principal | `Program.cs` — CODE |

**Working example:** The `me` action has `[Authorize]`, reads `sub` from the principal and constructs `GetCurrentUserQuery`. Register accepts `RegisterRequest` and constructs `RegisterCommand`. Controllers therefore know the HTTP boundary and Application inputs; they contain no SQL or password-hashing algorithm.

**Boundary to preserve:** Business formulas belong to Domain/model behavior, use-case steps to handlers, and request serialization/status mapping to API. Enabling JWT authentication does not prove live database token-revocation checks or complete permission resolution. This baseline has no callback checking an ACTIVE token row. Proposed Redis admission middleware still requires placement and failure-contract design.

Source: [AuthenController](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Api/Controllers/AuthenController.cs), [AuthenRequests](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Api/Contracts/Authen/AuthenRequests.cs), [ResultExtensions](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Api/Extensions/ResultExtensions.cs), [Program](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Api/Program.cs)

### 2.2 Application layer — Use cases and orchestration sub-layers

Application accepts caller intent and completes a use case through models and ports. It owns step ordering, transaction boundaries and the outcome returned to the use-case caller, referencing Domain/Shared rather than concrete Infrastructure.

| Sub-layer | Responsibilities and owned work | Input → Output / collaboration | Source / status |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Commands / Queries | Describe operation input and intent; commands change state and queries read data | Request record → handler contract returning `Result` or `Result<T>`; records do not invoke SQL or validators themselves | `Features/Authen/<UseCase>/*Command.cs`, `GetCurrentUserQuery.cs` — CODE |
| Validators | Check use-case input before a handler executes and invoke value-object factories for value rules | Request → error list; Dispatcher combines errors and stops before the handler on failure | Four command validators — CODE; query `/me` has no validator |
| Handlers | Load facts, invoke entity/business behavior and ports, coordinate ordering and transactions, and select expected outcomes | Command/Query → repository/security calls and Result/response; dependencies exclude concrete DB/SDK clients | Five Authen handlers — CODE |
| Mapping / Responses | Select use-case output and translate models into data the caller can consume | `User`/issued tokens → register/login/current-user response records; some commands return Result without a DTO | `Features/Authen/Mapping/AuthenMappings.cs` and response records — CODE |
| Ports / Common | Define required transaction, password, token and email capabilities; collect validation results and identify the assembly for DI scanning | Interface calls → adapters bound by API; validation results → error list | `Abstractions/`, `Common/ValidationErrors.cs`, `AssemblyReference.cs` — CODE |

**Working example:** `RegisterCommandHandler` checks username/email duplication through a repository, creates a `User` and credential, then uses `IUnitOfWork` to persist user/password in one transaction. `LoginCommandHandler` loads user/credential, verifies the password, calls `EnsureCanSignIn()` and persists tokens. Calls into `Authen/Domain/` would be introduced when its designed business operations are implemented.

**Boundary to preserve:** A handler coordinates a feature operation without copying reusable formulas or model invariants across use cases. Current validator contracts are synchronous, so they must not hide database I/O. Authorization and use-case response policy require coordination with relevant identity/business rules; `ICommand` and DI do not supply them automatically.

Source: [Register handler](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Application/Features/Authen/Register/RegisterCommandHandler.cs), [Register validator](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Application/Features/Authen/Register/RegisterCommandValidator.cs), [IUnitOfWork](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Application/Abstractions/IUnitOfWork.cs), [ValidationErrors](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Application/Common/ValidationErrors.cs)

### 2.3 Domain layer — Models, business rules and Business Domain

Domain expresses accepted business meaning: valid values, permitted states/transitions and business-operation outcomes. It separates rule decisions from HTTP and concrete storage. This layer contains several responsibilities beyond business service classes.

| Sub-layer | Responsibilities and owned work | Input → Output / collaboration | Source / status |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| Entities / Aggregates | Hold identity/state and control their own behavior/transitions; an aggregate root marks an invariant boundary that requires explicit design | Typed identity/values and current state → entity or transition success/failure | `Authen/Entities/User.cs`, `PasswordResetToken.cs` — CODE; User has an aggregate-root marker |
| ValueObjects | Define business values, validity, normalization and value equality | Raw values → typed values or validation errors, such as `Username.Create` and `PlainPassword.Create` | `Authen/ValueObjects/` — CODE |
| Business Domain — Service = Domain | Group reusable business operations or operations without a single owning entity, following the project convention | Business facts/values/models/policy → business results consumed by handlers | `Authen/Domain/` — OWNER-DIRECTED DESIGN; no implementation yet |
| Repository contracts | Define model read/write interfaces needed by inner layers without Dapper/Npgsql/SQL syntax | Typed IDs/values/entities → asynchronous results; Application can use these interfaces directly | `Authen/Repositories/IAuthenRepositories.cs` — CODE |
| Common / Errors / Status | Supply entity/value equality, the aggregate-root marker, domain statuses and expected-failure vocabulary | Identity/value components/state → primitives, `UserStatus`, `AuthenErrors`; `DuplicateKeyException` communicates unique-write failures | `Common/`, `AuthenErrors.cs`, `UserStatus.cs`, `DuplicateKeyException.cs` — CODE |

**Working example:** `User.Register()` creates an Active user, `EnsureCanSignIn()` rejects an inactive account, `PasswordResetToken.Consume(now)` changes state when the token is usable, and `PlainPassword.Create()` checks new-password strength. Future Business Domain operations can compose these behaviors while preserving each model's invariant ownership.

**Boundary to preserve:** User has an aggregate-root marker, but password/token operations use separate repositories; this does not establish that the User aggregate controls every credential/session lifecycle. Rules spanning requests need persistence guards too. `Restore()` reconstructs stored models by convention; its public factory does not restrict callers through the compiler. Arrays exposed by `PasswordCredential` also require a separate immutability assessment.

Source: [Entity](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Domain/Common/Entity.cs), [ValueObject](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Domain/Common/ValueObject.cs), [repository contracts](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Domain/Authen/Repositories/IAuthenRepositories.cs), [AuthenErrors](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Domain/Authen/AuthenErrors.cs)

### 2.4 Infrastructure layer — Adapters and technology details

Infrastructure interacts with external systems through ports declared by Domain/Application. It owns persistence mappings, connection lifecycle, SQL/cryptography and provider-specific failures, translating results into types usable by inner layers.

| Sub-layer | Responsibilities and owned work | Input → Output / collaboration | Source / status |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Repository adapters | Execute parameterized SQL, map rows, encrypt/decrypt stored fields and hydrate domain models | Repository calls/typed values → DB commands/rows → User/credential/token or translated failure | `Persistence/Authen/{User,Password,Token}Repository.cs` — CODE |
| DbSession / connection | Share a lazy-opened connection and transaction within a DI scope, pass transaction/cancellation to Dapper and dispose resources | SQL, parameters and cancellation → affected rows/scalars/mapped rows | `Persistence/DbSession.cs` — CODE |
| UnitOfWork / transaction adapter | Implement the transaction port using begin/commit/rollback, reusing an existing transaction | Asynchronous delegate → committed writes or rollback on exception | `Persistence/UnitOfWork.cs` — CODE; handlers select the work boundary |
| Security adapters | Implement password derivation/verification, JWT/opaque-token generation, token hashing and field protection | Credential/plain input/configuration/time → verification flag, hashes, issued tokens or protected values | `Security/Pbkdf2PasswordHasher.cs`, `TokenService.cs`, `FieldProtector.cs` — CODE |
| Email adapter | Implement the email port; currently a development logging stand-in | Reset-email arguments → completed task/logs; no actual email delivery | `Email/LoggingEmailSender.cs` — CODE, development-only |
| Options / DI registration | Read settings, perform implemented startup validation, construct clients and bind interfaces with their lifetimes | Configuration → options and singleton/scoped services consumed by the composition root | `Options/InfrastructureOptions.cs`, `DependencyInjection.cs` — CODE |
| Proposed data adapters | Separate the proposed roles of caching, shared admission, configuration snapshots and event/projection stores | Ports requiring design → Redis/MongoDB operations and failure contracts | Caching/RateLimiting/Configuration/Documents in the diagram — PROPOSED; absent from baseline source |

**Working example:** `UserRepository` encrypts values for lookup/insertion, then decrypts and calls `Restore()` to reconstruct a User. `PasswordRepository.SetAsync()` deactivates the previous password and inserts its replacement. `TokenRepository` persists hashes and revokes rows. `UnitOfWork` uses the same DbSession to enlist repositories in the use-case transaction.

**Boundary to preserve:** The transaction adapter commits when its delegate completes normally and rolls back on an exception; it does not inspect `Result.Failure` to choose rollback. Read-before-write operations still require concurrency and zero-row outcome design. DbSession/repositories are scoped; the data source/security/email services are singleton in current DI. A singleton must not capture a request's scoped connection.

Source: [DbSession](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Infrastructure/Persistence/DbSession.cs), [UnitOfWork](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Infrastructure/Persistence/UnitOfWork.cs), [security options](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Infrastructure/Options/InfrastructureOptions.cs), [LoggingEmailSender](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Infrastructure/Email/LoggingEmailSender.cs)

### 2.5 Shared layer — Common request and result mechanisms

Shared supplies types and mechanisms used across features without project references to other layers. This baseline includes CQRS and Results; handler/validator implementations still belong to Application, and business rules retain their feature owners.

| Sub-layer | Responsibilities and owned work | Input → Output / collaboration | Source / status |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Messaging contracts | Declare request, command/query, handler, validator and dispatcher interfaces, including generic response constraints | Command/Query type → handler/validator contracts resolved by registration and dispatcher | `Cqrs/Messaging.cs` — CODE |
| Dispatcher / registration | Scan Application assemblies to register scoped handlers/validators, cache executors and invoke validators before the handler | Request → validation failure or delegated `HandleAsync()` result | `Cqrs/Dispatcher.cs`, `CqrsServiceCollectionExtensions.cs` — CODE |
| Results / Errors | Supply success/failure, typed values and expected-error vocabulary independently of ASP.NET Core responses | Value/error list → `Result`, `Result<T>`, `Error`; API subsequently maps status | `Results/Result.cs`, `Error.cs` — CODE |

**Working example:** A controller calls `IDispatcher.SendAsync()`. Dispatcher combines validator error lists; a nonempty list uses the response type's failure factory. Otherwise it resolves and awaits the handler. Scanning through `AddCqrs(AssemblyReference.Assembly)` allows use cases to follow conventions without individual handler registration.

**Boundary to preserve:** `Result<T>.Value` is available on success; accessing it on failure throws. Shared does not automatically map HTTP, open transactions, authorize requests or enforce read-only queries. It has a DI abstractions package dependency despite having no project references. Shared additions must preserve this dependency direction.

Source: [Messaging contracts](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Shared/Cqrs/Messaging.cs), [CQRS registration](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Shared/Cqrs/CqrsServiceCollectionExtensions.cs), [Result](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Shared/Results/Result.cs), [Error](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Shared/Results/Error.cs)


### 2.6 Existing request flow

```text
HTTP request
  -> Controller constructs a Command / Query
  -> Dispatcher invokes registered validators
       -> Validation errors: return failure without invoking the Handler
       -> Valid input: invoke the Handler
  -> Handler uses Entity / ValueObject and repository/security ports
  -> Infrastructure performs I/O and SQL
  -> Handler maps the response
  -> Controller returns the HTTP response
```

Four commands have validators; `GetCurrentUserQuery` has none in this baseline. Dispatcher does not automatically open transactions or apply authorization/retry policies.

### 2.7 Business Domain flow under the selected convention

```text
Handler loads facts required by the use case
  -> Invoke a business operation in <Feature>/Domain/
  -> Domain applies rules with Entity / ValueObject and returns a business result
  -> Handler coordinates persistence through ports / transaction boundary
  -> Infrastructure handles SQL / external systems
```

`Handler -> Authen/Domain/` remains an owner-directed design, as its diagram labels and edges indicate; it is not an observed call in the pinned source. Handler remains the Application use case, while Domain supplies reusable business logic within the backend application.

### 2.8 Responsibilities spanning layers

| Concern | Responsibility split across sub-layers | What to verify together |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Validation | API binds/deserializes HTTP contracts; Application validators invoke Domain value factories; Shared dispatcher controls whether the handler runs | HTTP format, use-case constraints and model invariants have distinct owners; baseline validators do not read the database |
| Authentication / authorization | API middleware creates the principal and actions read identity; handlers coordinate use-case permission/credential checks; Domain checks model conditions; Infrastructure verifies hashes/issues JWTs | A valid JWT signature does not establish that user/token rows remain Active or that every business permission is satisfied; inspect actual implementation |
| Transaction / concurrency | Handler selects writes; `IUnitOfWork` is an Application port; Infrastructure UnitOfWork/DbSession executes SQL in a transaction; Domain expresses invariants | Rollback, lock order, conditional updates and zero-row outcomes must agree; a Result failure does not automatically trigger exception-based rollback |
| Expected failure / HTTP | Domain/Application provide reasons; Shared supplies Result/Error; Application selects public use-case outcomes under policy; API maps HTTP | Baseline login exposes AccountNotActive directly; compare this with the specification's generic authentication-failure requirement |
| Dependency composition | API Program invokes DI registrations; Application/Domain use inner contracts; Infrastructure implements ports; Shared supplies common types | A runtime call to an adapter does not create an inner-layer project reference to Infrastructure |

Register connects the sub-layers as follows: HTTP Contracts/Controller → Shared Dispatcher → Application Validator using Domain ValueObjects → Application Handler invoking the User factory and repository/hasher ports → Infrastructure repositories/UnitOfWork → Application Mapping → API success 201. Query `/me` has no command validator or write transaction and therefore does not follow every step of that write flow.

## 3. Repository: Source ownership and allowed project references

![Repository architecture: Source projects, feature packages, tests and the owner-directed Authen/Domain design](../diagram/reference/repository/repository-architecture.drawio.png)

[Full-size image](../diagram/reference/repository/repository-architecture.drawio.png) · [draw.io source](../diagram/reference/repository/repository-architecture.drawio) · [Diagram companion](../diagram/reference/repository/repository-architecture.md) · [HTML preview](../diagram/reference/repository/repository-architecture.html)

This diagram maps source ownership and compile-time dependencies, providing a different viewpoint from runtime architecture. `REF` indicates a `ProjectReference` in a `.csproj`. A runtime call through an interface does not require an inner project to reference concrete Infrastructure.

### 3.1 Two repository boundaries

```text
Showcase: system-analysis-and-design/
└── e-commerce/
    ├── REPOS.md                 # identity / remote / pinned revision
    ├── api/                     # API contract
    ├── db/                      # migrations and database tests
    ├── doc/                     # specifications and this guide
    ├── diagram/                 # diagram bundles
    └── repository/
        ├── .gitkeep
        └── e-commerce-backend/   # independent Git clone; ignored by Showcase
            ├── .git/
            ├── Ecommerce.sln
            ├── Directory.Build.props
            ├── README.md
            ├── project-structure.md
            ├── code.md
            ├── src/
            └── tests/
```

Change backend code and deliver its commits/PRs to the component remote. The manifest, specifications, diagrams and this guide belong to Showcase. To advance the baseline, deliver and verify the component commit on its remote before changing the manifest's `revision`. Never stage child code or its `.git` in Showcase.

### 3.2 Observed project references

| Project | Referenced projects |
| ----------------------------- | ----------------------------------- |
| `Ecommerce.Api`               | Application, Infrastructure, Shared |
| `Ecommerce.Application`       | Domain, Shared                      |
| `Ecommerce.Domain`            | Shared                              |
| `Ecommerce.Infrastructure`    | Application, Domain, Shared         |
| `Ecommerce.Shared` | No project references |
| `Ecommerce.Domain.Tests`      | Domain, Shared                      |
| `Ecommerce.Application.Tests` | Application, Domain, Shared         |

The pinned source contains 9 production references and 5 test references. Domain and Application do not reference Infrastructure. Shared already depends on the DI abstractions package, so having no project references does not imply having no external-package dependencies.

`Authen/Domain/` belongs inside the existing `Ecommerce.Domain.csproj`. Adding this folder alone introduces neither another project nor a dependency-graph change.

## 4. Organizing code by feature and use case

Application groups code under `Features/<Feature>/<UseCase>/`, placing use-case input, validator, handler and output together. The current Authen layout is:

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
    ├── ResetPassword/       # requesting a link and confirming it use separate commands/handlers
    ├── GetCurrentUser/
    └── Mapping/AuthenMappings.cs
```

| Part | Responsibility and example |
| ------------------------ | --------------------------------------------------------------------------------------- |
| Command / Query | Input record expressing operation intent, without ownership of HTTP or SQL |
| Validator | Check request constraints; invoke existing value-object factories for value rules |
| Handler | Coordinate steps, load data, invoke business/model behavior and ports, and define the use-case transaction |
| Response / Mapping | Translate outcomes into caller-facing DTOs rather than returning domain entities directly |
| Application abstractions | Ports for transactions, hashing, token issuing and email, without concrete adapter imports |

Use cases do not all require identical files. `Register` and `Login` return typed responses; reset request/confirmation commands return `Result` without dedicated response DTOs. Query `/me` returns `CurrentUserResponse` without a dedicated validator.

Source: [RegisterCommandHandler](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Application/Features/Authen/Register/RegisterCommandHandler.cs), [LoginCommandHandler](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Application/Features/Authen/Login/LoginCommandHandler.cs), [AuthenMappings](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Application/Features/Authen/Mapping/AuthenMappings.cs)

## 5. Service = Domain: Reusable business operations

Read a Domain feature's layout as follows. The `Domain/` entry is the owner-selected location and does not exist in the source baseline:

```text
Ecommerce.Domain/
├── Common/                  # Entity, ValueObject, IAggregateRoot
└── Authen/
    ├── Entities/            # CODE: User, PasswordResetToken
    ├── ValueObjects/        # CODE: business values and value rules
    ├── Repositories/        # CODE: IUser/IPassword/ITokenRepository
    ├── Domain/              # OWNER CONVENTION: reusable Authen business operations
    │                        # not implemented at the pinned revision
    ├── AuthenErrors.cs
    └── UserStatus.cs
```

### 5.1 What Domain should own

- Apply rules and make business decisions from required facts, such as evaluating a business condition or calculating an outcome from business values/policy.
- Group operations reused across use cases so handlers apply one rule set.
- Collaborate with entities/value objects while preserving explicit invariant ownership.
- Return business results or failures that Application can use in subsequent steps.

The handler loads external facts needed by a rule and passes them to Domain through a designed contract, or Domain uses an approved inner abstraction. Domain does not accept concrete SQL connections, Redis/MongoDB clients or HTTP request DTOs, and does not own SQL commits.

“Tax calculation” illustrates a kind of reusable business operation. It belongs to the feature that actually owns the financial rules. This document introduces no tax class in Authen and defines no rates, formulas or rounding rules.

### 5.2 Dividing work between Handler and Domain

| Question | Primary owner |
| ------------------------------------------------------- | -------------------------------------------------------------------- |
| Which steps and ports complete this request, and what should the caller receive? | Application Handler |
| What do these facts permit, or what business value should be calculated? | Feature `Domain/` under this convention, or behavior on the model owning the rule |
| Does the entity's current state permit this transition? | Entity / Aggregate behavior |
| Is this value valid, and what does it mean? | ValueObject |
| Which rows are read/written, how is hashing performed, or which provider SDK is called? | Infrastructure through ports |
| How is the result translated into an HTTP status/payload? | API boundary under the public contract |

Adding `Domain/` does not require moving every invariant out of entities/value objects. Its purpose is to establish an explicit, reusable owner for business operations according to the owner's convention.

### 5.3 Observed rules and remaining design work

| Rule | Current location | Relationship to Business Domain |
| -------------------------------------------------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| A new user starts Active | `User.Register()` | Existing entity factory behavior |
| Only an Active user can sign in | `User.EnsureCanSignIn()` | Invoked by the handler; reusable operations can compose this behavior |
| A reset token must be unused and unexpired | `PasswordResetToken.Consume(now)` | The model guard exists; persistence must also guarantee concurrency correctness |
| New username/email/password values must be valid | Value-object factories | Validators/handlers share these rules without copying regex/policy across handlers |
| Username/email must be unique | Register handler checks the repository and handles duplicate exceptions | The database must prevent races; SQL remains outside business classes |
| Login throttle, reset-request limit, refresh reuse | Complete flows are absent from the baseline | Design business operations, input facts, persistence guards and failure outcomes under governing specifications before implementation |

Source: [User](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Domain/Authen/Entities/User.cs), [PasswordResetToken](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Domain/Authen/Entities/PasswordResetToken.cs), [PlainPassword](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Domain/Authen/ValueObjects/PlainPassword.cs)

## 6. CQRS and Business Domain calls

Commands own state-changing operations; queries own reads. Each has separate input/handler contracts in Shared. Names and folders alone do not establish correct behavioral separation.

| Side | Current examples | Relationship to Business Domain |
| ------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Command | Register, Login, RequestPasswordReset, ResetPassword | Handlers use existing model behavior and can invoke `Domain/` operations when implemented under their specifications |
| Query | GetCurrentUser | Return the requested data; a state-changing business operation is unnecessary |

Login is a command even though it returns tokens, because it writes token rows. The current query loads `User` through the `IUserRepository` shared with commands and maps it into a DTO. There is no query-specific read port or separate read projection in the source. Introducing those requires evidence from read/write model requirements.

Dispatcher invokes validators before handlers and skips the handler when errors exist. Transactions and business orchestration remain use-case responsibilities; `ICommand` and `IQuery` markers do not provide them automatically.

Source: [Messaging](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Shared/Cqrs/Messaging.cs), [Dispatcher](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Shared/Cqrs/Dispatcher.cs), [GetCurrentUserQueryHandler](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Application/Features/Authen/GetCurrentUser/GetCurrentUserQueryHandler.cs)

## 7. Infrastructure and correctness across requests

Application calls interfaces; Infrastructure implements them with concrete technology:

| Port / responsibility                 | Implementation                                                 |
| ------------------------------------- | -------------------------------------------------------------- |
| User, password and token repositories | Dapper/Npgsql repositories in `Persistence/Authen/` |
| Transaction coordination | Handler invokes `IUnitOfWork`; `UnitOfWork` uses scoped `DbSession` |
| Password hashing                      | `Pbkdf2PasswordHasher`                                         |
| JWT and opaque tokens | `TokenService` |
| Stored personal-field protection      | `FieldProtector`                                               |
| Reset email | `LoggingEmailSender` is a development stub |

Some business rules require both code-level rules and database guards. `Consume()` prevents repeated token use on a loaded object, but two requests can load different objects before either writes. Single use across requests therefore also needs locks/conditional updates and zero-row outcomes that Application can handle.

The baseline reset-consumption SQL uses only `WHERE id = @id` and does not return a business outcome identifying which competing request won. The proposed `Authen/Domain/` design therefore also needs an I/O contract and transaction boundary; its folder alone cannot complete cross-request invariants.

Source: [TokenRepository](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Infrastructure/Persistence/Authen/TokenRepository.cs), [UnitOfWork](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Infrastructure/Persistence/UnitOfWork.cs), [DependencyInjection](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/src/Ecommerce.Infrastructure/DependencyInjection.cs)

## 8. Identity domain model: Data concepts used by business code

![Identity domain model: Schema-derived User, credentials, tokens, consent and authorization concepts](../diagram/domain/domain-identity-model.drawio.png)

[Full-size image](../diagram/domain/domain-identity-model.drawio.png) · [draw.io source](../diagram/domain/domain-identity-model.drawio) · [Explanation and SQL traceability](../diagram/domain/domain-identity-model.md) · [HTML preview](../diagram/domain/domain-identity-model.html)

This diagram is a conceptual interpretation of the schema and remains in review according to its companion document. Its association/cardinality edges have different meanings from the runtime arrows and project references in the previous diagrams.

- User, Credential, Reset request, Profile, Address, Token and Login attempt boxes represent data concepts; they do not establish that all corresponding C# classes exist.
- The `authen` box groups concepts by schema. It does not define one aggregate containing every entity or require all data to load for every operation.
- Role, Permission, Scope and grant associations describe schema-based permissions; they do not prove an implemented JWT claims resolver.
- Session correlation uses `session_id` in token tables. It does not establish a Session table or an `AuthSession` aggregate in code.
- Cardinality includes historical rows. Determine permitted ACTIVE-row counts from the relevant partial constraints as well.

Use this view to understand the facts Business Domain needs. Operation names, aggregate boundaries, transactions and `Authen/Domain/` contracts still require design from the relevant business rules.

## 9. Implemented elements and remaining designs

| Area | Status in the pinned component | How to use the guide and diagrams |
| ----------------------------------------------- | -------------------------------------------------------- | ----------------------------------------------------------- |
| Five production projects / two test projects | Present in source | Reference project layout and dependencies |
| Authen four commands / one query | Present in source | Trace code flow without assuming compliance with every latest specification |
| Entity / ValueObject / repository interfaces | Present in source | Existing model behavior and contracts that Business Domain can reuse |
| `Authen/Domain/` business operations | Owner-selected convention; no implementation yet | Design direction pending complete class/method/specification definitions |
| Product, order, payment and shipping operations | Documented in Showcase; no implementation found in this component | Inspect relevant specifications and approvals before development |
| Redis/MongoDB adapters, outbox/relay | Proposed/in-review according to diagram companions | Keep separate from CODE; do not invent SDKs/workers/transactions in the current flow |

## 10. Tests and checks for business-operation development

Test projects verify production layers; they are not additional runtime layers. Both projects use xUnit and introduce no request-flow steps.

| Test project / sub-layer | Tested behavior and inputs/outputs | Dependencies / limitations |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `Ecommerce.Domain.Tests/Authen/EntityTests.cs` | Create/restore entities and exercise behavior; check identity, Active-user conditions and reset-token expiry/consumption | References Domain/Shared; establishes object behavior rather than database concurrency |
| `Ecommerce.Domain.Tests/Authen/ValueObjectTests.cs` | Pass normal/out-of-range inputs to factories and check typed values/errors, normalization and equality | No HTTP/DB; persistence mappings and request contracts need separate verification |
| `Ecommerce.Application.Tests/Authen/AuthenHandlerTests.cs` | Dispatch commands to real handlers backed by fakes, checking results and side effects | References Application/Domain/Shared; does not use concrete Infrastructure |
| `Ecommerce.Application.Tests/Authen/Fakes.cs` | Replace repositories, hasher, token service, email and unit of work with controlled implementations | `InlineUnitOfWork` performs no real transaction; fake password verification/token revocation does not prove JWT middleware or rollback |

Source: [Domain entity tests](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/tests/Ecommerce.Domain.Tests/Authen/EntityTests.cs), [Domain value tests](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/tests/Ecommerce.Domain.Tests/Authen/ValueObjectTests.cs), [Application handler tests](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/tests/Ecommerce.Application.Tests/Authen/AuthenHandlerTests.cs), [test fakes](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/tests/Ecommerce.Application.Tests/Authen/Fakes.cs)

Neither suite contains integration tests establishing real SQL, transaction rollback, HTTP serialization or JWT middleware behavior. Requirements at those boundaries need additional tests exercising their concrete implementations.

When developing a business operation under an approved specification, check at least:

1. Assign each rule explicitly to `Domain/`, an entity or a value object, using the feature's business language.
2. Keep handlers responsible for use-case coordination and correct use of business results; avoid duplicating rules across handlers.
3. Express Domain inputs/outputs as business values, independent of HTTP and vendor SDKs.
4. Give state-changing operations a transaction/concurrency contract that can be verified with persistence.
5. Ensure read queries have no hidden write side effects.
6. Trace tests to rules and failure boundaries; use database/API tests when the evidence spans processes or connections.
7. Update the code guide, relevant specifications and diagrams to match actual status; mark an element CODE only after implementation exists.

## 11. References and guide verification

- [Diagram index](../diagram/README.md) covers additional views such as order lifecycle, checkout/payment sequences, outbox and operations; this guide embeds the views relevant to code structure.
- [Component project-structure.md](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/project-structure.md) describes baseline file conventions.
- [Component code.md](https://github.com/ittikornsopawan/e-commerce-backend/blob/d8255183cba54d0c2b218607456b895a70df32f0/code.md) details current flows and known gaps; read it alongside the Service = Domain convention clarified here.
- [Manifest](../REPOS.md) and [component-repositories rule](../../.agents/rules/component-repositories.md) define Git ownership and baseline pinning.

The guide embeds three existing diagrams without copying, renaming or generating image files. Their PNGs were inspected at a readable size; editable `.drawio`/PNG metadata parity and native nesting passed for all three bundles. Each image is 2378 × 1682 pixels.

Verification covers frontmatter, references, source/model correspondence and preservation of component/diagram assets. This documentation change modifies no backend, API specification, schema or diagram, and does not rerun builds/runtime tests.

### 11.1 Review verification — 9 November 2026

| Check | Result and scope |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Markdown/frontmatter | YAML parsing passed; the guide remains draft with null approval fields; headings, tables and code fences are valid |
| Source references | Local references resolve, and every component reference identifies an existing pinned commit/blob |
| Illustrations | Three existing PNGs, each 2378 × 1682 pixels, with editable-source and companion-document links |
| Editable model/PNG integrity | Architecture 72 cells, repository 47 cells, identity 99 cells; metadata parity and native nesting passed for all three bundles |
| Diagram preservation | Hashes of all 12 files across three bundles match before/after authoring; no redraw or export |
| Component evidence | Clean component at the pinned SHA; 9 production and 5 test project references; `Authen/Domain/` remains owner-directed design as confirmed by source |
| Visual review | Embedded PNGs were inspected during the preceding guide review; no native-editor box movement or re-export was performed because models were unchanged |

These results verify the guide and its diagram references. They do not replace runtime/database/API integration tests or approve Business Domain implementation.

The expanded-scope review covers all five layer introductions and 24 sub-layer responsibility groups in sections 2.1–2.5. Each explains owned work, inputs/outputs, collaborators, source/status and boundaries. Section 2.8 covers cross-layer validation/security/transactions/errors, and section 10 explains test-project responsibilities. Coverage was checked against actual source; the earlier guide failed this expanded coverage gate.

The English revision also passed a whole-document language check and preserves the original numbered headings, table row/column structure, code fences and all 59 reference targets. The three diagram bundles and pinned component remain unchanged.
