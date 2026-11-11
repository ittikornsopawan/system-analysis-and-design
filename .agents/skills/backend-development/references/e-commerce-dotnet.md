---
name: E-commerce .NET Backend Conventions
description: Conditional implementation guidance for the e-commerce .NET component, including layer ownership, Business Domain naming and legacy-baseline limits. Read only for that project's .NET work, after inspecting its current manifest and source configuration.
---

# Apply only to the e-commerce .NET component

Read `e-commerce/REPOS.md` and project knowledge to locate the declared component and pinned baseline. Inspect that component's current `project-structure.md`, build/project/package settings, source and tests before coding. Discover framework/language/package versions and commands there; this reference does not freeze them or authorize upgrades. The Showcase owns specs/migrations/contracts; component implementation and its commits belong to the child's remote.

The inspected baseline has five production projects, custom CQRS dispatch, Dapper/Npgsql data access and Domain/Application tests with fakes. It is a legacy baseline, not evidence that newer auth/session/permission specifications are implemented. Recheck current source rather than copying an endpoint as a supposedly approved prototype.

## Responsibility map and complete structural example

Use only the pieces the requested use case needs. The following example is self-contained guidance for placement, not a request to create these classes:

```text
Ecommerce.Api/
  Controllers/<Feature>Controller.cs        HTTP binding, principal and Result-to-HTTP mapping
  Contracts/<Feature>/                     Public request/response contracts
Ecommerce.Application/
  Features/<Feature>/<UseCase>/
    <UseCase>Command.cs or Query.cs          Use-case input, independent of HTTP and SQL
    <UseCase>CommandValidator.cs             Input constraints and value-object validation
    <UseCase>CommandHandler.cs               Orchestration, port calls and transaction intent
    <UseCase>Response.cs                     Caller-facing result when this use case needs one
  Features/<Feature>/Mapping/               Explicit entity/value-to-response mapping
  Abstractions/                            Approved I/O/transaction capabilities
Ecommerce.Domain/
  <Feature>/Entities/                      State, identity and owned invariants
  <Feature>/ValueObjects/                  Value meaning, validation and normalization
  <Feature>/Domain/                        Reusable business operations: Service = Domain
  <Feature>/Repositories/                  Existing inner persistence contracts
Ecommerce.Infrastructure/
  Persistence/<Feature>/                  Parameterized SQL adapters and result mapping
  Persistence/DbSession.cs                Connection/current-transaction lifetime
  Persistence/UnitOfWork.cs                The actual approved transaction mechanism
  Security/, Email/, Options/DI           Technical adapters and composition
Ecommerce.Shared/
  Cqrs/, Results/                         Existing request dispatch and Result/Error mechanisms
```

- Preserve the owner's `Service = Domain` convention and `src/Ecommerce.Domain/<Feature>/Domain/` path. It expresses reusable business operations; entities/value objects still own their invariants. That folder was not implemented in the inspected Authen baseline, so its existence must not be claimed as observed code.
- Application handlers coordinate the use case. Domain business operations consume the required business facts or approved inner abstractions, not concrete SQL connections, HTTP request DTOs or provider clients; SQL commits remain outside business operations. Do not create a service wrapper for every condition or make every query run a state-changing domain operation.
- Domain/Application reference inner contracts rather than Infrastructure. Follow actual project references and DI lifetimes. Preserve the custom dispatcher/validator pattern; do not introduce MediatR, a new mapper or an ORM merely because another stack uses it.
- API binding, Application validation, model invariants and persistence guards prove different things. Trusted caller identity comes from verified security context; permissions/current session state follow the approved contract rather than a caller-supplied id.
- Return mapped response models rather than exposing entity state accidentally. Align exact HTTP statuses, public error bodies and bizCodes with the approved spec/OpenAPI; legacy ProblemDetails/Result mappings may require scoped work rather than blind copying.

## SQL and transaction translation

Translate spec placeholders into named, bound runtime parameters. Preserve predicates, joins, ordering, row-status filters, null semantics, result shapes, lock order and transaction boundaries; never concatenate caller values into SQL. Check zero-row and duplicate/concurrent outcomes where required. The sequence/spec SQL parity rule governs those design artifacts; executable parameter binding requires an explicit semantic mapping, not raw insertion of `<sequence.*>` strings into runtime SQL.

Inspect `IUnitOfWork`, `UnitOfWork` and `DbSession` before adding writes. The inspected implementation commits a normally completed delegate and rolls back an exception; it does not inspect a failure Result. Derive what must survive from each approved branch rather than treating every HTTP error as rollback. If the existing abstraction cannot express a required outcome safely, surface the architecture gap for approval instead of silently redesigning it.

Worked transaction decision example:

| Approved branch intent | Response | Durable outcome to prove |
| --- | --- | --- |
| Successful work | Success | Commit the requested writes |
| Rejected credentials with required attempt audit | 401 | Commit that audit effect if the governing spec requires it |
| Validation failure before transaction | 400 | No transaction/write is started |
| Interrupted transactional work | Specified error/timeout | Roll back the interrupted writes except effects explicitly specified to survive elsewhere |

These are instructional branch shapes, not approval of the current in-review Login spec. Verify the actual branch's required behavior and adapter semantics together.

## Evidence and baseline limits

Inspect test-project references before relying on a passing suite. The inspected Domain/Application tests use in-memory repositories, fake hashing/token generation and a fake UnitOfWork; they do not prove SQL correctness, real rollback, middleware authorization or cross-request token consumption. A model's consume-once guard on one object does not make two DB requests atomic. Add the relevant real database/framework evidence under the generic verification reference.

Read the component's current gap documentation and approved governing spec before reusing auth/reset examples. The baseline's missing session/throttle/claim behavior is a reason to plan a scoped implementation, not to infer new business requirements or to label those legacy patterns secure by default.
