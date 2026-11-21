---
name: Principal Worked Examples
description: Three condensed worked examples in C#/.NET — a feature implementation, an architecture decision and a code review — showing the expected reasoning and output shape. Read when you want to calibrate the depth and format of an answer.
---

# Worked examples

These are condensed to show shape and depth. Real answers cite real files and numbers.

## 1. Feature development — "Add a cancel-order endpoint"

**Context (facts):** ASP.NET Core API with EF Core; `Order` has `Status` (`Pending`, `Paid`, `Shipped`, `Cancelled`); payment refunds go through `IPaymentGateway`. **Assumption:** only the owning customer may cancel, and only before shipping — confirm with the product owner (default used meanwhile).

**Design note:**

- Rule lives in the domain: `order.Cancel(now)` throws/returns a failure unless status is `Pending` or `Paid`.
- Refund is an external call → not inside the DB transaction. Commit `Cancelled` + an outbox row `RefundRequested`; a worker calls the gateway with the order ID as idempotency key.
- Concurrency: a shipping job could ship the order at the same moment → optimistic concurrency token on `Order`; conflict maps to `409`.
- Endpoint: `POST /orders/{id}/cancel` (additive, no contract break). Repeated cancel of an already cancelled order returns `200` with the current state (idempotent).
- Rejected: synchronous refund in the request (couples availability to the gateway, double refunds on retry); a generic "order state machine framework" (one transition today).

```csharp
public Result Cancel(DateTimeOffset now)
{
    if (Status == OrderStatus.Cancelled) return Result.Success();          // idempotent
    if (Status is not (OrderStatus.Pending or OrderStatus.Paid))
        return Result.Failure(OrderErrors.CannotCancel(Status));
    Status = OrderStatus.Cancelled;
    CancelledAt = now;
    return Result.Success();
}
```

**Verification:** unit tests for each status transition; integration tests (real PostgreSQL) for 404 on another customer's order, 409 on concurrent ship, outbox row written in the same transaction; `dotnet build` and `dotnet test` results pasted. **Risk left:** refund worker failure alerting not yet defined.

## 2. Architecture design — "Should we move to microservices with Kafka?"

**Decision:** Not now. Keep the modular monolith, enforce module boundaries, and add a transactional outbox for the integrations that hurt today. Revisit when a module needs an independent release cadence or owning team, or order volume passes ~50/s.

**Context:** Facts — 4 developers, one deployable, PostgreSQL, ~3k orders/day, peak ~2/s; pain points are a slow nightly stock sync and email failures that roll back orders. Assumption — no plan to grow beyond one team this year.

| | Microservices + Kafka | Modular monolith + outbox |
| --- | --- | --- |
| Solves today's pain | Yes, indirectly | Yes, directly |
| New infrastructure | Kafka cluster, N pipelines, service discovery | One outbox table + background worker |
| Ops load for 4 devs | High (distributed tracing, versioned contracts, on-call per service) | Low |
| Consistency | Eventual everywhere, sagas needed | Strong inside one DB, eventual only at integrations |
| Reversibility | One-way door | Two-way; modules can be extracted later |

**Consequences:** single deploy unit remains; module boundaries need an architecture test (e.g. NetArchTest) to stop erosion. **Verification:** email failures no longer roll back orders (integration test); stock sync time measured before/after. **ADR:** written, because the team will ask again.

## 3. Code review — payment controller excerpt

```csharp
[HttpPost("pay")]
public IActionResult Pay(PayRequest req)
{
    var order = _db.Orders.First(o => o.Id == req.OrderId);
    var result = new HttpClient().PostAsJsonAsync(_url, req).Result;
    order.Status = "Paid";
    _db.SaveChanges();
    return Ok();
}
```

- **[Blocker] PaymentsController.cs:4 — no ownership check.** Scenario: any logged-in user pays/marks another user's order. Fix: filter by `CustomerId == User.GetId()`, return 404 otherwise.
- **[Blocker] :5–6 — double charge on retry and status set regardless of result.** Scenario: client times out and retries → charged twice; gateway returns 402 → order still marked Paid. Fix: idempotency key = order ID sent to the gateway; check `IsSuccessStatusCode` and the gateway's result before changing state.
- **[Major] :5 — `new HttpClient()` and `.Result`.** Socket exhaustion under load; thread-pool starvation. Fix: typed client via `IHttpClientFactory` with resilience handler; `async`/`await` with `CancellationToken`.
- **[Major] :4 — `First` throws on unknown ID → 500.** Fix: `SingleOrDefaultAsync` → 404.
- **[Minor] :6 — status as string literal.** Fix: enum, as elsewhere in the codebase.
- **Good:** small surface, single endpoint. **Not checked:** gateway contract, tests (none in PR).
