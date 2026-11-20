---
name: E-commerce Function Book
description: Central list of the e-commerce backend's shared, reusable functions with purpose, parameters and usage. Read before writing any new function in the e-commerce backend; update it in the same change that adds, changes or removes a shared function.
source_component_revision: 23fab92ca6936aa905ec3470174f78c179ac6b8a
updated_on: 2026-11-20
---

# E-commerce Function Book

Check this book and the code before writing a new function, as required by `.agents/skills/dev-like-principal/references/code-quality-standards.md`:

- Reuse a listed function when it fits.
- Extend one when it nearly fits, without breaking its current callers.
- Add an entry when you create a shared function.

The book lists only what other code is meant to call. Handlers, controllers and private methods are not listed; `e-commerce/doc/code-structure.md` explains where those live.

Paths are relative to `e-commerce/repository/e-commerce-backend/src/`. The entries were checked against component revision `23fab92` (`main` after #18, #19 and #20). Every API runs on EF Core through `ITransactionRunner`; the Dapper path, the legacy `api/authen/me` endpoint and the unused first-scaffold domain model were removed on 2026-11-20.

## Shared — Results and errors

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `Result.Success()` / `Result.Success<T>(T value)` | `Ecommerce.Shared/Results/Result.cs` | Successful outcome of a use case or rule | Optional value → success result | Every handler, policy and factory returns a `Result`; do not throw for expected failures |
| `Result.Failure(Error)` / `Result.Failure(IReadOnlyList<Error>)` / `Result.Failure<T>(Error)` | `Ecommerce.Shared/Results/Result.cs` | Failed outcome carrying one or more errors | Error(s) → failure result | Implicit conversions exist: return an `Error` or a `T` directly from a `Result<T>` method |
| `Error.Of(code, description, type, bizCode)` | `Ecommerce.Shared/Results/Error.cs` | Error with an explicit spec bizCode | Code, text, `ErrorType`, bizCode → `Error` | Use for errors whose bizCode the spec fixes; declare them once in the feature's `*Errors` class |
| `Error.Failure/Validation/NotFound/Conflict/Unauthorized/Forbidden(code, description)` | `Ecommerce.Shared/Results/Error.cs` | Typed errors without a custom bizCode | Code, text → `Error` of that type | The `ErrorType` decides the HTTP status in `ResultExtensions.ToFailure` |
| `AuthenErrors.*` (for example `AccessTokenInvalid`, `IdentifierTaken`, `AddressNotFound`, `AddressLimit(int max)`) | `Ecommerce.Domain/Authen/AuthenErrors.cs` | The authen specs' errors, each declared once with its spec status, bizCode and text | — / `max` → `Error` | Reuse the declared error; add a new one here, never inline the text in a handler |
| `CommonErrors.Timeout` | `Ecommerce.Application/Common/CommonErrors.cs` | The shared timeout error (bizCode E90001) | — | Return when `ITransactionRunner` throws `TimeoutException` |

## Shared — Validation messages and formats

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `ValidationMessages.Field(requestField)` | `Ecommerce.Shared/Validation/ValidationMessages.cs` | Turns a JSON field name into display words | `emailAddress` → `Email Address` | Used by the other message builders |
| `ValidationMessages.Required/MaxLength/Uuid/Date/OneOf/Email/JsonType/Duplicated/UnknownField(...)` | same | The 400 E10001 message forms of `api-conventions.md` "Validation messages" | Field name (+ limit/values) → message text | Always use these instead of writing message text by hand; API filters and validators share them |
| `ValidationMessages.At(position, message)` / `Combine(messages)` | same | Prefixes a message with its position; joins messages | Position + message → text; messages → one text | For batch items and multiple failures |
| `EmailAddressFormat.IsValid(string value)` | `Ecommerce.Domain/Common/EmailAddressFormat.cs` | The one email rule of api-conventions "Email address" (owner decision 2026-11-18): ≤ 254 characters, exactly one `@` after a non-empty local part, a dot in the domain, a plain address only (no space, display name or angle brackets) | Text → bool | Register and request-password-reset validators. Validity only: callers store and compare the value as sent. Do not add another rule |

## Shared — Optional values and paging

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `Optional<T>` (`IsSet`, `Value`, `Optional<T>.Of(value)`, `default` = unset) | `Ecommerce.Shared/Optional.cs` | Tells an omitted field from an explicit null (specs 07 and 09) | Value → set optional; `default` → unset | Partial updates: omitted keeps the stored value, null clears it. Built by `JsonBody.String` |
| `PageRequest.TryParse(pageIndex, pageSize, maxPageSize, out page)` | `Ecommerce.Shared/Paging/PageRequest.cs` | Checked offset pagination (spec 10): positive 64-bit values, defaults 1/10 only when omitted, offset fits a nonnegative BIGINT | Raw query texts + max → `PageProblem` (`None`, `OutOfRange`, `OffsetOverflow`) and the page | Every paged inquiry; an explicit empty or invalid value is never defaulted |
| `page.Offset` / `TotalPages(totalItems)` / `ExpectedRows(totalItems)` | same | The bound offset; ceiling(total / size) or 0; the row count the page must hold | Count → number | Check the page rows against `ExpectedRows` of the same snapshot; a mismatch is a 500 |
| `Page<T>(Items, PageIndex, PageSize, TotalItems, TotalPages)` | same | The five data keys of a paged inquiry | — | Return it as the handler response; it serializes to the spec's data object |

## Shared — CQRS

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `services.AddCqrs(params Assembly[] assemblies)` | `Ecommerce.Shared/Cqrs/CqrsServiceCollectionExtensions.cs` | Registers the dispatcher, handlers and validators found in the assemblies | Assemblies → service collection | Composition root only |
| `IDispatcher.SendAsync<TResponse>(IRequest<TResponse>, ct)` | `Ecommerce.Shared/Cqrs/Messaging.cs` | Runs the request's validator, then its handler | Command/query → its `Result` | Controllers send every use case through it; a failed validation never reaches the handler |
| `ICommand`, `ICommand<T>`, `IQuery<T>` + handler interfaces, `IValidator<T>` | same | Contracts for a new use case | — | Implement these for a new use case; do not call handlers directly |

## Domain — Base types and exceptions

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `ValueObject` | `Ecommerce.Domain/Common/ValueObject.cs` | Value-based equality for value objects | — | Base class for value objects |
| `DuplicateKeyException(constraintName, table)` | `Ecommerce.Domain/DuplicateKeyException.cs` | A unique constraint was violated (PostgreSQL 23505) | Constraint and table names | Thrown by the persistence layer; handlers map the constraint name to the spec's 409 error |
| `MissingReferenceException(constraintName)` | `Ecommerce.Domain/MissingReferenceException.cs` | A foreign key target is missing (23503) | Constraint name | Handlers map it to the spec's not-found error |

## Domain — Authen value objects

A value object validates its input in `Create` and returns a failure `Result` for bad input.

Only `PlainPassword` and `PasswordCredential` remain: the unused value objects, the `User`/`PasswordResetToken` entities, `Entity` and `ValidationErrors` were removed on 2026-11-20. The validators apply the spec rules with `ValidationMessages`, `EmailAddressFormat` and `ProfileFieldRules`.

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `PlainPassword.Create(string? raw)` | `Ecommerce.Domain/Authen/ValueObjects/PlainPassword.cs` | Password that meets the password rules | Raw text → `Result<PlainPassword>` | Before hashing; never store or log it |

## Domain — Authen business operations (Service = Domain)

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `AuthorizationClaims.Resolve(facts, activeScopes)` | `Ecommerce.Domain/Authen/Domain/AuthorizationClaims.cs` | A user's effective grants (spec 02-login claim notes 1-6) | Authorization facts + active scopes → `ResolvedClaims` | Building token claims; a scope definition is never a grant by itself |
| `AuthorizationClaims.AssignedScopeIds(facts)` | same | The scope ids the "Get active scopes" query must read | Facts → scope ids | Before loading active scopes |
| `AuthorizationClaims.ClaimName(permissionName)` | same | Permission name → JWT claim name | `catalog.manage` → `catalog:manage` | Any code that writes or checks permission claims |
| `LoginThrottle.IsRefused(int recentFailures)` | same | Brute-force limit: 5 failed attempts in the window refuse the next | Failure count in the window → bool | Login; the caller counts failures in the window |
| `PasswordResetThrottle.IsRefused(requestsInWindow, maxRequests)` | `.../Domain/PasswordResetThrottle.cs` | Reset-request limit | Count + configured max → bool | Request-password-reset |
| `RefreshTokenReuse.Classify(row, nowUtc, grace)` | `.../Domain/RefreshTokenReuse.cs` | Spec 05 decision for a reread refresh row: rotate, replay outside the grace window (close the session), or invalid | Row (or null) + fresh now + grace → `RefreshDecision` | Refresh only, after the user lock |
| `AddressDefaultPolicy.Resolve(rowStatus, requestedTrue, wasDefault, otherActiveExists)` | `.../Domain/AddressDefaultPolicy.cs` | Spec 09 default rule: exactly one ACTIVE default; an address leaving ACTIVE hands the default on | Target state → `AddressDefaultDecision(IsDefault, ShouldPromote)` | Address upsert; Q21 (a default must be ACTIVE) is checked earlier by the validator |
| `AddressQuota.IsFull(nonDeletedAddresses, max)` | same | At most `max` non-DELETED addresses per user | Count + max → bool | Address insert, under the user lock |
| `ProfileFieldRules.IsPhoneNumber(value)` / `IsDateOfBirth(value, todayUtc)` / `Genders` | `Ecommerce.Domain/Common/ProfileFieldRules.cs` | Spec 07 value rules: 8 to 15 digits with an optional +; a real date not after today UTC; MALE/FEMALE/OTHER | Text (+ today) → bool | Profile validators; register keeps its own gender list (`RegisterCommandValidator.Genders`) |
| `RegistrationConsentPolicy.Check(...)` | `.../Domain/RegistrationConsentPolicy.cs` | Whether submitted consents may be stored (spec 01-register), in the spec's error order | Submitted and current consents → `Result` | Registration only |

## Application — Shared use-case steps

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `Caller(UserId, AccessToken, TokenExpiresAtUtc)` | `Ecommerce.Application/Features/Authen/Common/Caller.cs` | The verified JWT of a protected call | — | Built by `VerifiedCaller.Of`; null when the JWT did not verify |
| `CallerCredential.VerifyAsync(caller, ct)` | same | Current-credential check for writes (specs 07, 09): lock the ACTIVE user FOR UPDATE, fresh now, JWT expiry recheck, ACTIVE stored access token | Caller (or null) → `Result<DateTime>` with the post-lock now, or 401 | Inside the use case's transaction, before any write; use the returned now for audit columns |
| `CallerCredential.CheckAsync(caller, ct)` | same | Read-only variant (spec 10): no lock; fresh now, expiry recheck, token joined with the ACTIVE user | Caller → `Result<DateTime>` or 401 | Read-only inquiries; answer 401 for a null caller before the transaction (no SQL) |
| `SessionTokens.IssueAsync(user, sessionId, ct)` | `.../Authen/Common/SessionTokens.cs` | Issues and stores an access and refresh token pair for one session (specs 02, 05) | User + session id → `TokenPairResponse` | Login and refresh; only token hashes are stored |

## Application — Ports

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `ITransactionRunner.RunAsync<T>(isolation, work, ct, readOnly = false)` | `Ecommerce.Application/Abstractions/ITransactionRunner.cs` | Runs one use case in one transaction at the spec's isolation level. Success commits; failure rolls back; a serialization conflict reruns the work (bounded); `readOnly` makes it the spec's READ ONLY transaction | Isolation, work returning `Result<T>`, read-only flag → that result | Every handler; pass `readOnly: true` for an inquiry whose spec says READ ONLY (08, 10). The work must read and write only through the transaction. Throws `TimeoutException` → return `CommonErrors.Timeout` |
| `IPasswordHasher.Hash(password)` / `Verify(password, credential)` | `.../Abstractions/IPasswordHasher.cs` | Hash and verify passwords (PBKDF2 implementation) | Password → `PasswordCredential`; password + credential → bool | Never compare hashes by hand |
| `IFieldTransport.Open(keyId, encryptedKey)` / `IFieldTransportSession.Decrypt(path, wireValue)` | `.../Abstractions/IFieldTransport.cs` | Opens the per-request AES key and decrypts one field of the encrypted request fields (api-conventions "Encrypted sensitive fields") | Key id + wrapped key → session or null; JSON path + wire value → plain text or null | The API filter is the caller; null means "cannot decrypt" and is never explained to the client |
| `ITokenService.IssueAccessToken/IssueRefreshToken/IssuePasswordResetToken`, `Hash(token)` | `.../Abstractions/ITokenService.cs` | Issue tokens; hash an opaque token for storage | Claims → `IssuedToken`; token → SHA-256 bytes | Store only the hash of refresh and reset tokens |
| `IEmailSender` | `.../Abstractions/IEmailSender.cs` | Send email (logging implementation today) | — | Send after the transaction commits, not inside it. The same file holds the settings records (`PasswordResetSettings`, `RefreshSettings`, `AddressSettings`) |

## Infrastructure — Persistence and security helpers

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `query.ForUpdate()` | `Ecommerce.Infrastructure/Persistence/Ef/ForUpdate.cs` | Adds `FOR UPDATE` to a LINQ query | `IQueryable<T>` → same query, locking | Inside a transaction only; not on split queries or aggregates. The only allowed way to lock rows. Never write the SQL |
| `database.AcquireTransactionLockAsync(long key, ct)` | `.../Persistence/Ef/AdvisoryLock.cs` | PostgreSQL transaction advisory lock | Lock key → completes when held | When a rule needs serialisation that no row lock covers; released at transaction end |
| `EcommerceDbContext.UtcSession(connectionString)` | `.../Persistence/Ef/EcommerceDbContext.cs` | Adds `Timezone=UTC` so `TIMESTAMP WITHOUT TIME ZONE` columns hold UTC | Connection string → connection string | Every connection: the EF context, the `NpgsqlDataSource` and test fixtures |
| `EcommerceDbContext.Create(connectionString, commandTimeoutSeconds)` / `Configure(builder, connectionString, commandTimeoutSeconds)` | same | A context with the UTC session, snake_case names, the `ForUpdate` interceptor and the command timeout | Connection string (+ timeout) → context or options | `Configure` in DI; `Create` in tests and tools |
| `EfTransactionRunner` (implements `ITransactionRunner`) | `.../Persistence/EfTransactionRunner.cs` | Translates PostgreSQL failures: 23505 → `DuplicateKeyException`, 23503 → `MissingReferenceException`, timeout → `TimeoutException`; reruns 40001 up to 3 attempts, then `TimeoutException` | — | With `readOnly` it runs the constant `SET TRANSACTION READ ONLY` right after BEGIN (a write then fails with 25006). Registered for `ITransactionRunner`; do not open transactions elsewhere (internal) |
| `SessionRevocation.CloseAccessTokensAsync/CloseRefreshTokensAsync(db, sessionId, userId, nowUtc, ct)` | `.../Persistence/Authen/SessionRevocation.cs` | Closes the ACTIVE token rows of one session of one user | Session + user + now → rows changed | Logout and refresh replay; both guard `user_id`, so another user's rows with the same session id are never touched (internal) |
| `FieldProtector.Protect(string)` / `Unprotect(byte[])` | `Ecommerce.Infrastructure/Security/FieldProtector.cs` | Deterministic, authenticated encryption of personal data in `bytea` columns | Text ↔ bytes | Unique personal columns (username, email) can still be matched by equality (internal) |
| `FieldTransport` (implements `IFieldTransport`) | `Ecommerce.Infrastructure/Security/FieldTransport.cs` | RSA-OAEP-SHA-256 unwrap of the request key and AES-256-GCM decrypt of each field, JSON path as AAD | Private keys from `Security:FieldTransport:Keys`; refuses a key under 3072 bits at startup | Different from `FieldProtector`, which protects stored data; this one only reads the wire |

## API — HTTP helpers

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `result.ToFailure(controller)` | `Ecommerce.Api/Extensions/ResultExtensions.cs` | Failed result → the spec's status envelope; the first error decides status and bizCode | Result + controller → `ObjectResult` | Every controller failure path |
| `controller.ToSuccess<T>(httpCode, message, bizMessage, data)` | same | Successful payload → the spec's status envelope (bizCode S10000) | Status, messages, data → `ObjectResult` | Every controller success path |
| `HttpEnvelope.RequestId(http)` / `NowUtc(http)` / `Failure(http, error)` / `WriteFailureAsync(http, error, ct)` | `Ecommerce.Api/Extensions/HttpEnvelope.cs` | Envelope for responses written outside a controller action | HttpContext + error → envelope or written response | Middleware and filters only; `RequestId` generates one if the header is missing |
| `VerifiedCaller.Of(controller)` | `Ecommerce.Api/Security/VerifiedCaller.cs` | The verified JWT of a protected call, read in the action instead of `[Authorize]` so a 400 answers before a 401 | Controller → `Caller?` | Every protected action (specs 06 to 10); pass the result into the command or query |
| `JsonBody.TryRead(body, fields, out read)` + `read.String(field)` / `Boolean(field)` / `Has(field)` | `Ecommerce.Api/Contracts/JsonBody.cs` | Reads a body by key presence: an object, known keys only, allowed JSON kinds | Body + field map (`JsonBody.StringOrNull`, `BooleanOnly`) → shape message or null | Partial-update bodies (specs 07, 09); `String` gives `Optional<string?>` |
| `QueryParameters.TryRead(request, keys, out values)` | `Ecommerce.Api/Contracts/QueryParameters.cs` | Reads a GET query string: known exact-case keys, each once, and no body | Request + key set → shape message or null; absent keys are absent | GET inquiries (spec 10); value rules stay in the Application validator |
| `RequiredHeadersFilter` | `Ecommerce.Api/Filters/RequiredHeadersFilter.cs` | 400 E10001 for a missing or non-UTC `timestamp`, and a non-JSON content-type when a body is sent; on an `[EncryptedFields]` action also a missing `encryptionKeyId` or `encryptedKey` | — | Registered globally; do not repeat the header checks in actions |
| `[EncryptedFields]` / `EncryptedFieldsFilter` | `Ecommerce.Api/Filters/EncryptedFieldsFilter.cs` | Decrypts the encrypted sensitive fields of the bound request before validation; every failure is 400 E10001 "Encrypted fields could not be decrypted." | Action argument implementing `IEncryptedRequest` → its decrypted copy | Put on an action whose spec lists encrypted fields (01–04); the request record lists its fields |
| `IEncryptedRequest.Decrypt(EncryptedFields)` + `EncryptedFields.Field(path, wireValue)` | `Ecommerce.Api/Contracts/EncryptedFields.cs` | A request names its encrypted fields by JSON path; `Field` leaves null as null and decrypts a sent value | Path + wire value → plain text, or `FieldDecryptionException` | Use the field name as the path (`addresses.city` for a nested field) — it is the AAD the frontend used |
| `EnvelopeExceptionHandler` | `Ecommerce.Api/Filters/EnvelopeExceptionHandler.cs` | An unhandled exception → 500 envelope "An unexpected error occurred." without bizCode | — | Registered globally; throw for defects, never return a 500 by hand |
| `ApiEnvelope.Success/Failure(...)` | `Ecommerce.Api/Contracts/ApiEnvelope.cs` | Builds the status envelope; `data` and `bizCode` are omitted when null | — | Used by `ResultExtensions` and `HttpEnvelope`; call those instead |
| `user.TryGetUserId(out Guid userId)` | `Ecommerce.Api/Security/CallerClaims.cs` | The caller's user id from the verified JWT | Principal → bool + id | Used by `VerifiedCaller.Of`; actions take the caller from there |
| `user.TryGetExpiresAt(out DateTime expiresAtUtc)` | same | The verified JWT `exp` in UTC | Principal → bool + time | Used by `VerifiedCaller` for the fresh-now expiry recheck |
| `user.IsPlatformAdmin()` | same | Whether the JWT `roles` claim holds `PLATFORM_ADMIN` | Principal → bool | Roles come only from the token, never from the database. No caller yet |
| `InvalidBody.Response(context)` | `Ecommerce.Api/Filters/InvalidBody.cs` | 400 envelope for a body that cannot be bound | Action context → result | Registered once as the invalid-model response |
| `services.AddPublicRateLimits(configuration)` | `Ecommerce.Api/Security/RateLimiting.cs` | Registers the public endpoints' rate limits: `public-strict` 10/min and `public-standard` 60/min per IP, 429 E90002 with `Retry-After` | Services + config → services | Composition root only; put `[EnableRateLimiting]` with the spec's policy on the action |
