---
name: Principal Coding Guidelines (C#/.NET focus)
description: Coding philosophy and concrete C#/.NET practices with short good/bad examples for async, EF Core, DI, error handling, validation, idempotency, HTTP clients and testability. Read when writing or changing code, especially in C#/.NET.
---

# Coding guidelines

The owner's mandatory standards (Function Book, formatting, short functions, comments, class/domain separation) are in `code-quality-standards.md`; apply them first. This file adds C#/.NET technical practice.

## Philosophy

1. **Follow the project's existing conventions first.** Layering, naming, data access (EF Core vs Dapper), result/error types, test style. Consistency beats your preference; propose a convention change separately.
2. **Simplicity over abstraction.** Concrete code first. Introduce an interface when there is a second implementation or a test seam you actually use; a pattern when it removes real duplication or complexity.
3. **Readability.** Names from the business domain; small methods that do one thing; no clever one-liners that need decoding.
4. **High cohesion, low coupling, separation of concerns.** HTTP concerns in the API layer, use-case orchestration in the application layer, business rules in the domain, I/O in infrastructure. Do not let a layer do another's job.
5. **Design for testability** through dependency injection of real boundaries (DB, clock, external APIs), not by mocking everything.
6. **Handle errors and edge cases** deliberately: expected business failures as results/ProblemDetails, unexpected faults as exceptions handled once at the edge.
7. **Preserve existing behavior** unless the change is required; a refactor and a behavior change go in separate commits.
8. SOLID and patterns are tools, not goals. Apply them when they make this code easier to change.

## C#/.NET practices with examples

### Async all the way, with cancellation

```csharp
// Bad: blocks a thread-pool thread, risks deadlock, ignores cancellation
var order = _repo.GetAsync(id).Result;

// Good
public async Task<OrderDto?> Handle(GetOrder query, CancellationToken ct)
{
    var order = await _db.Orders.AsNoTracking()
        .Where(o => o.Id == query.OrderId && o.CustomerId == query.CustomerId)
        .Select(o => new OrderDto(o.Id, o.Status, o.Total))
        .SingleOrDefaultAsync(ct);
    return order;
}
```

No `async void` except event handlers. Pass `CancellationToken` through to every I/O call.

### EF Core: query shape matters

```csharp
// Bad: N+1 — one query per order for its lines; loads full entities with tracking
var orders = await _db.Orders.Where(o => o.CustomerId == id).ToListAsync(ct);
foreach (var o in orders) total += o.Lines.Sum(l => l.Price * l.Qty); // lazy load per order

// Good: one query, projected, untracked, bounded
var totals = await _db.Orders.AsNoTracking()
    .Where(o => o.CustomerId == id)
    .OrderByDescending(o => o.CreatedAt)
    .Take(50)
    .Select(o => new { o.Id, Total = o.Lines.Sum(l => l.Price * l.Qty) })
    .ToListAsync(ct);
```

Filter in the database, not after `ToListAsync()`. Use `AsNoTracking()` for reads. Keep transactions short; never call external HTTP inside one.

### Concurrency and idempotency

```csharp
// Idempotent create: a unique index on (CustomerId, IdempotencyKey) is the real guard
try
{
    _db.Payments.Add(new Payment(cmd.CustomerId, cmd.IdempotencyKey, cmd.Amount));
    await _db.SaveChangesAsync(ct);
}
catch (DbUpdateException ex) when (ex.IsUniqueViolation())  // project's helper over the provider error code
{
    return await _db.Payments.SingleAsync(
        p => p.CustomerId == cmd.CustomerId && p.IdempotencyKey == cmd.IdempotencyKey, ct);
}
```

A "check then insert" without a constraint is a race. Use optimistic concurrency (`[Timestamp]`/`xmin` row version) for updates that can collide, and decide what the caller sees on conflict.

### Outbox instead of "save then publish"

```csharp
// Bad: if publish fails after commit, the event is lost; if it succeeds but commit fails, it is a lie
await _db.SaveChangesAsync(ct);
await _bus.PublishAsync(new OrderPlaced(order.Id), ct);

// Good: event row committed atomically with the order; a background worker publishes and marks it sent
_db.Orders.Add(order);
_db.OutboxMessages.Add(OutboxMessage.From(new OrderPlaced(order.Id)));
await _db.SaveChangesAsync(ct);
```

Consumers must be idempotent: the worker delivers at least once.

### HttpClient and resilience

```csharp
// Bad: new HttpClient per call → socket exhaustion; no timeout policy
using var client = new HttpClient();

// Good: typed client via IHttpClientFactory with the standard resilience pipeline
builder.Services.AddHttpClient<PaymentGatewayClient>(c => c.BaseAddress = new(options.BaseUrl))
    .AddStandardResilienceHandler();   // timeout, retry with jitter, circuit breaker
```

Retries only on idempotent calls or with an idempotency key the provider honours.

### Errors and validation

- Validate input at the boundary (FluentValidation or the project's validators); return `400` with `ProblemDetails`. Validate business invariants in the domain.
- Expected failures (not found, conflict, rule violation) → a result type or a mapped status code. Do not use exceptions for control flow.
- Unexpected exceptions → one global handler (`UseExceptionHandler` / `IExceptionHandler`) that logs with the trace ID and returns a generic 500. Never leak stack traces or SQL.
- Never `catch (Exception) { }`. Catch what you can handle.

### Dependency injection and lifetimes

- `DbContext` is scoped; never inject it into a singleton. Background services create a scope per unit of work (`IServiceScopeFactory`).
- Bind configuration with `IOptions<T>` and validate it on start (`ValidateDataAnnotations().ValidateOnStart()`).
- Inject `TimeProvider` (.NET 8+) instead of calling `DateTime.Now`; store UTC.

### Modern C# — use when it helps clarity

Records for immutable DTOs and value objects, `required` members, pattern matching, file-scoped namespaces, primary constructors for simple DI, nullable reference types enabled and warnings treated seriously. Do not rewrite working code just to use new syntax.

### Security in code

Parameterized queries only (EF Core LINQ or Dapper parameters; never string-concatenated SQL). Authorize at the resource level (`order.CustomerId == currentUser.Id`). No secrets in code or logs. Hash passwords with a vetted algorithm (ASP.NET Core Identity's hasher, Argon2/bcrypt) — never a fast hash.

### Clean Architecture and DDD — when

Use layers and aggregates when the domain has real rules and invariants worth protecting. A CRUD admin screen does not need aggregates, domain events and a mediator pipeline. Match the depth of design to the complexity of the domain, and stay consistent with the codebase.

## Tests

- Test behavior through the narrowest boundary that proves the claim: unit tests for domain rules, integration tests (`WebApplicationFactory`, a real database via Testcontainers) for SQL, transactions, constraints, auth and HTTP mapping.
- Mock what you do not own and cannot run (third-party APIs); do not mock the database to "prove" a query.
- A bug fix starts with a test that fails for the bug.
- Name tests after the behavior: `PlaceOrder_WithDuplicateIdempotencyKey_ReturnsExistingOrder`.
