---
name: E-commerce Function Book
description: Central list of the e-commerce backend's shared, reusable functions with purpose, parameters and usage. Read before writing any new function in the e-commerce backend; update it in the same change that adds, changes or removes a shared function.
source_component_revision: 648226c7b3b2e69897b58978184ff6ecbaa49252
updated_on: 2026-11-18
---

# E-commerce Function Book

Check this book and the code before writing a new function, as required by `.agents/skills/dev-like-principal/references/code-quality-standards.md`:

- Reuse a listed function when it fits.
- Extend one when it nearly fits, without breaking its current callers.
- Add an entry when you create a shared function.

The book lists only what other code is meant to call. Handlers, controllers and private methods are not listed; `e-commerce/doc/code-structure.md` explains where those live.

Paths are relative to `e-commerce/repository/e-commerce-backend/src/`. The entries were checked against component revision `648226c`. The EF Core switch is in progress, so check the code when an entry concerns persistence.

## Shared — Results and errors

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `Result.Success()` / `Result.Success<T>(T value)` | `Ecommerce.Shared/Results/Result.cs` | Successful outcome of a use case or rule | Optional value → success result | Every handler, policy and factory returns a `Result`; do not throw for expected failures |
| `Result.Failure(Error)` / `Result.Failure(IReadOnlyList<Error>)` / `Result.Failure<T>(Error)` | `Ecommerce.Shared/Results/Result.cs` | Failed outcome carrying one or more errors | Error(s) → failure result | Implicit conversions exist: return an `Error` or a `T` directly from a `Result<T>` method |
| `Error.Of(code, description, type, bizCode)` | `Ecommerce.Shared/Results/Error.cs` | Error with an explicit spec bizCode | Code, text, `ErrorType`, bizCode → `Error` | Use for errors whose bizCode the spec fixes; declare them once in the feature's `*Errors` class |
| `Error.Failure/Validation/NotFound/Conflict/Unauthorized/Forbidden(code, description)` | `Ecommerce.Shared/Results/Error.cs` | Typed errors without a custom bizCode | Code, text → `Error` of that type | The `ErrorType` decides the HTTP status in `ResultExtensions.ToFailure` |
| `CommonErrors.Timeout` | `Ecommerce.Application/Common/CommonErrors.cs` | The shared timeout error (bizCode E90001) | — | Return when `ITransactionRunner` throws `TimeoutException` |
| `ValidationErrors.From(params Result[] results)` | `Ecommerce.Application/Common/ValidationErrors.cs` | Collects the errors of every failed result | Results → all their errors | In validators, to report all problems at once instead of the first only (internal) |

## Shared — Validation messages and formats

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `ValidationMessages.Field(requestField)` | `Ecommerce.Shared/Validation/ValidationMessages.cs` | Turns a JSON field name into display words | `emailAddress` → `Email Address` | Used by the other message builders |
| `ValidationMessages.Required/MaxLength/Uuid/Date/OneOf/Email/JsonType/Duplicated(...)` | same | The 400 E10001 message forms of `api-conventions.md` "Validation messages" | Field name (+ limit/values) → message text | Always use these instead of writing message text by hand; API filters and validators share them |
| `ValidationMessages.At(position, message)` / `Combine(messages)` | same | Prefixes a message with its position; joins messages | Position + message → text; messages → one text | For batch items and multiple failures |
| `EmailAddressFormat.IsValid(string value)` | `Ecommerce.Domain/Common/EmailAddressFormat.cs` | Email format check (today: exactly one `@`, non-empty local part and domain; to become the api-conventions rule) | Text → bool | Validators of register and request-password-reset use it. **Pending change (owner decision 2026-11-18):** the governing rule is now the stricter one in api-conventions "Email address" (plain address, ≤ 254, dot required in the domain). This function still applies the old "non-empty parts" rule until Drake makes it the single shared rule and `EmailAddress.Create` uses it. Do not add a third rule |

## Shared — CQRS

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `services.AddCqrs(params Assembly[] assemblies)` | `Ecommerce.Shared/Cqrs/CqrsServiceCollectionExtensions.cs` | Registers the dispatcher, handlers and validators found in the assemblies | Assemblies → service collection | Composition root only |
| `IDispatcher.SendAsync<TResponse>(IRequest<TResponse>, ct)` | `Ecommerce.Shared/Cqrs/Messaging.cs` | Runs the request's validator, then its handler | Command/query → its `Result` | Controllers send every use case through it; a failed validation never reaches the handler |
| `ICommand`, `ICommand<T>`, `IQuery<T>` + handler interfaces, `IValidator<T>` | same | Contracts for a new use case | — | Implement these for a new use case; do not call handlers directly |

## Domain — Base types and exceptions

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `Entity<TId>` | `Ecommerce.Domain/Common/Entity.cs` | Identity-based equality for entities | — | Base class for entities |
| `ValueObject` | `Ecommerce.Domain/Common/ValueObject.cs` | Value-based equality for value objects | — | Base class for value objects |
| `DuplicateKeyException(constraintName, table)` | `Ecommerce.Domain/DuplicateKeyException.cs` | A unique constraint was violated (PostgreSQL 23505) | Constraint and table names | Thrown by the persistence layer; handlers map the constraint name to the spec's 409 error |
| `MissingReferenceException(constraintName)` | `Ecommerce.Domain/MissingReferenceException.cs` | A foreign key target is missing (23503) | Constraint name | Handlers map it to the spec's not-found error |

## Domain — Authen value objects

Each value object validates and normalises its input in `Create` and returns a failure `Result` for bad input. `Restore` rebuilds an already-stored value without re-validating; use it only when loading from the database.

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `EmailAddress.Create(string? raw)` / `Restore(string)` | `Ecommerce.Domain/Authen/ValueObjects/EmailAddress.cs` | Valid, normalised email address | Raw text → `Result<EmailAddress>` | Not called on `main` yet. Trims and lower-cases, which register and reset do not do: they store and compare the email as sent. Its dot check is anywhere in the value; the decided rule needs the dot in the domain (see above) |
| `Username.Create(string? raw)` / `Restore(string)` | `.../ValueObjects/Username.cs` | Valid username | Raw text → `Result<Username>` | Registration and profile input |
| `LoginIdentifier.Create(string? raw)` | `.../ValueObjects/LoginIdentifier.cs` | Login input that is a username or an email | Raw text → `Result<LoginIdentifier>` | Login only |
| `PersonName.Create(string? first, string? last)` / `Restore(first, last)` | `.../ValueObjects/PersonName.cs` | Valid first and last name | Two texts → `Result<PersonName>` | Registration and profile input |
| `DisplayName.Create(string? raw, PersonName fallback)` / `Restore(string)` | `.../ValueObjects/DisplayName.cs` | Display name, defaulting from the person name | Raw text + fallback → `Result<DisplayName>` | Registration and profile input |
| `PlainPassword.Create(string? raw)` | `.../ValueObjects/PlainPassword.cs` | Password that meets the password rules | Raw text → `Result<PlainPassword>` | Before hashing; never store or log it |
| `UserId.New()` | `.../ValueObjects/UserId.cs` | New time-ordered user id (UUID v7) | — → `UserId` | Creating a user |

## Domain — Authen business operations (Service = Domain)

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `AuthorizationClaims.Resolve(facts, activeScopes)` | `Ecommerce.Domain/Authen/Domain/AuthorizationClaims.cs` | A user's effective grants (spec 02-login claim notes 1-6) | Authorization facts + active scopes → `ResolvedClaims` | Building token claims; a scope definition is never a grant by itself |
| `AuthorizationClaims.AssignedScopeIds(facts)` | same | The scope ids the "Get active scopes" query must read | Facts → scope ids | Before loading active scopes |
| `AuthorizationClaims.ClaimName(permissionName)` | same | Permission name → JWT claim name | `catalog.manage` → `catalog:manage` | Any code that writes or checks permission claims |
| `LoginThrottle.IsRefused(int recentFailures)` | same | Brute-force limit: 5 failed attempts in the window refuse the next | Failure count in the window → bool | Login; the caller counts failures in the window |
| `PasswordResetThrottle.IsRefused(requestsInWindow, maxRequests)` | `.../Domain/PasswordResetThrottle.cs` | Reset-request limit | Count + configured max → bool | Request-password-reset |
| `RegistrationConsentPolicy.Check(...)` | `.../Domain/RegistrationConsentPolicy.cs` | Whether submitted consents may be stored (spec 01-register), in the spec's error order | Submitted and current consents → `Result` | Registration only |

## Application — Ports

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `ITransactionRunner.RunAsync<T>(isolation, work, ct)` | `Ecommerce.Application/Abstractions/ITransactionRunner.cs` | Runs one use case in one transaction at the spec's isolation level. Success commits; failure rolls back; a serialization conflict reruns the work (bounded) | Isolation, work returning `Result<T>` → that result | The EF Core path; the work must read and write only through the transaction. Throws `TimeoutException` → return `CommonErrors.Timeout` |
| `IUnitOfWork.ExecuteInTransactionAsync(work, ct)` | `.../Abstractions/IUnitOfWork.cs` | One transaction: commit on success, roll back on exception | Work → completes | The older Dapper path; prefer `ITransactionRunner` for EF Core slices |
| `IPasswordHasher.Hash(password)` / `Verify(password, credential)` | `.../Abstractions/IPasswordHasher.cs` | Hash and verify passwords (PBKDF2 implementation) | Password → `PasswordCredential`; password + credential → bool | Never compare hashes by hand |
| `ITokenService.IssueAccessToken/IssueRefreshToken/IssuePasswordResetToken`, `Hash(token)` | `.../Abstractions/ITokenService.cs` | Issue tokens; hash an opaque token for storage | Claims → `IssuedToken`; token → SHA-256 bytes | Store only the hash of refresh and reset tokens |
| `IEmailSender` | `.../Abstractions/IEmailSender.cs` | Send email (logging implementation today) | — | Send after the transaction commits, not inside it |

## Infrastructure — Persistence and security helpers

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `query.ForUpdate()` | `Ecommerce.Infrastructure/Persistence/Ef/ForUpdate.cs` | Adds `FOR UPDATE` to a LINQ query | `IQueryable<T>` → same query, locking | Inside a transaction only; not on split queries or aggregates. The only allowed way to lock rows. Never write the SQL |
| `database.AcquireTransactionLockAsync(long key, ct)` | `.../Persistence/Ef/AdvisoryLock.cs` | PostgreSQL transaction advisory lock | Lock key → completes when held | When a rule needs serialisation that no row lock covers; released at transaction end |
| `FieldProtector.Protect(string)` / `Unprotect(byte[])` | `Ecommerce.Infrastructure/Security/FieldProtector.cs` | Deterministic, authenticated encryption of personal data in `bytea` columns | Text ↔ bytes | Unique personal columns (username, email) can still be matched by equality (internal) |

## API — HTTP helpers

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `result.ToFailure(controller)` | `Ecommerce.Api/Extensions/ResultExtensions.cs` | Failed result → the spec's status envelope; the first error decides status and bizCode | Result + controller → `ObjectResult` | Every controller failure path |
| `controller.ToSuccess<T>(httpCode, message, bizMessage, data)` | same | Successful payload → the spec's status envelope (bizCode S10000) | Status, messages, data → `ObjectResult` | Every controller success path |
| `HttpEnvelope.RequestId(http)` / `NowUtc(http)` / `Failure(http, error)` / `WriteFailureAsync(http, error, ct)` | `Ecommerce.Api/Extensions/HttpEnvelope.cs` | Envelope for responses written outside a controller action | HttpContext + error → envelope or written response | Middleware and filters only; `RequestId` generates one if the header is missing |
| `user.TryGetUserId(out Guid userId)` | `Ecommerce.Api/Security/CallerClaims.cs` | The caller's user id from the verified JWT | Principal → bool + id | Every endpoint that acts as the caller |
| `user.IsPlatformAdmin()` | same | Whether the JWT `roles` claim holds `PLATFORM_ADMIN` | Principal → bool | Roles come only from the token, never from the database |
| `InvalidBody.Response(context)` | `Ecommerce.Api/Filters/InvalidBody.cs` | 400 envelope for a body that cannot be bound | Action context → result | Registered once as the invalid-model response |
| `services.AddPublicRateLimits(configuration)` | `Ecommerce.Api/Security/RateLimiting.cs` | Registers the public endpoints' rate limits | Services + config → services | Composition root only |
