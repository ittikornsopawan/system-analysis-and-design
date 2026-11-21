---
name: Principal Code Quality Standards
description: The owner's mandatory code quality standards (set 2026-11-18) — function reuse through a Function Book, formatting, short single-purpose functions, meaningful comments and class/domain separation — with the before-coding procedure and the before-delivery check. Read before writing or changing any code, in any language, from any skill.
---

# Code quality standards

These are the owner's standards for every line of code in this repository, in every language (C#, SQL, Python, shell). Every skill that writes code loads this file first.

**Core principle:** understand the existing structure before writing anything. Reuse over rewrite. Separation over monolith. Readability over clever code.

## Before writing code

Do these four steps, in order, before the first line:

1. **Read the structure.** Find where the change belongs: the project's code-structure guide (e.g. `e-commerce/doc/code-structure.md`), the neighbouring files, and the conventions they follow.
2. **Check the Function Book.** Open the project's Function Book (e.g. `e-commerce/doc/function-book.md`). Look for a function that already does the job, or most of it.
3. **Check the code.** The book can lag behind. Search the codebase for the behaviour, not just the name, e.g. `grep -rn "IsValid\|Normalize\|ForUpdate" src/`.
4. **Decide, and say so in the handoff.**
   - Found a fit: reuse it as is.
   - Found a near fit: extend it without breaking its current callers.
   - Found nothing: write a new function, then add it to the Function Book in the same change.

If the project has no Function Book yet, create one from `assets/function-book.md.tmpl` when you add its first shared function.

## 1. Function reusability

- One rule, one place. If the same logic appears twice, extract it before adding a third copy.
- Place a shared function by reach. Logic every layer uses goes in the shared layer. Logic used inside one layer goes in the layer that owns its meaning. Logic with one caller stays with that caller.
- Do not create a helper for a caller that does not exist yet. The book records what is shared, not what might be.
- Code you move into a shared function keeps its validation and error handling.

### The Function Book

The Function Book is the project's central list of shared, reusable functions. It lists only what other code is meant to call:

- shared helpers
- value-object factories
- domain policies
- persistence and security helpers
- API extensions

It does not list every handler or private method.

Each entry records five things:

| Field | Content |
| --- | --- |
| Function | The signature, e.g. `Result<EmailAddress> EmailAddress.Create(string? raw)` |
| Location | File path |
| Purpose | What it does and the business rule it carries, in one line |
| Parameters / returns | Meaning of each input; what success and failure look like |
| Use when / notes | When to call it, and when not to; known limits |

Update the book in the same change as the code:

- add new shared functions
- update entries whose signature or behaviour changed
- remove deleted ones

A reviewer rejects a change whose shared functions are missing from the book.

## 2. Code formatting

- Follow the project's formatter and `.editorconfig` (`dotnet format`, the repo's Python style). Never mix reformatting of untouched lines into a behaviour change.
- Use one blank line between logical steps inside a method, so the shape is visible: guard → load → decide → persist → respond.
- Break long expressions at operators or arguments. A LINQ chain puts one operator per line.
- Group a class's members: constants, fields, constructor, public members, private helpers.
- No statement stacking (`if (x) a(); b();` on one line). No line so long it needs horizontal scrolling (aim for ≤ 120 characters).

```csharp
// Hard to read: everything on one line, no steps visible
public async Task<Result> Handle(Cmd c, CancellationToken ct){var u=await _repo.Get(c.Id,ct);if(u==null)return Result.Failure(Errors.NotFound);u.Rename(c.Name);await _uow.Save(ct);return Result.Success();}

// Readable: one step per block
public async Task<Result> Handle(RenameUserCommand command, CancellationToken ct)
{
    var user = await _users.FindAsync(command.UserId, ct);
    if (user is null)
        return Result.Failure(UserErrors.NotFound);

    user.Rename(command.DisplayName);

    await _unitOfWork.SaveAsync(ct);
    return Result.Success();
}
```

## 3. Short and clean functions

- One function, one responsibility. If its name needs "and", split it.
- Keep functions short: aim for 20 lines or fewer. Over 30 lines, split the function, or justify it in the handoff. Count the lines from the opening to the closing brace; do not estimate. A use-case handler is not exempt. Move each block with its own purpose into a named private method, e.g. validation, the duplicate/race recovery, or building the response.
- Flatten nesting with guard clauses and early returns. Two levels of nesting is the usual limit.
- Use arrow syntax (C# expression-bodied members and lambdas, JS/TS arrow functions, Python lambdas) when the body is one clear expression. Use a block body once it needs a statement, a branch or a name for an intermediate value.

```csharp
// Good arrow use: one obvious expression
public static bool IsRefused(int recentFailures) => recentFailures >= MaxFailures;

// Bad arrow use: logic squeezed into one expression to avoid a block
public decimal Total() => Lines.Any() ? Lines.Sum(l => l.Qty * l.Price) - (Coupon?.Kind == Kind.Pct ? Lines.Sum(l => l.Qty * l.Price) * Coupon.Value / 100 : Coupon?.Value ?? 0) : 0;

// Better: named steps, each one obvious
public decimal Total()
{
    var subtotal = Lines.Sum(line => line.Qty * line.Price);
    var discount = Coupon?.DiscountFor(subtotal) ?? 0m;
    return Math.Max(subtotal - discount, 0m);
}
```

## 4. Meaningful comments

Comments are for the next reader: the code owner, a reviewer, or an AI developer arriving with no context. They explain what the code cannot say for itself:

- **Intent and business rule:** why this exists, which spec or rule it enforces (cite the spec ID or section).
- **Design reason:** why this approach and not the obvious one (e.g. why a lock, why an advisory lock instead of a constraint).
- **Constraints and traps:** ordering requirements, concurrency assumptions, things that must not change.
- **Public members:** a one-line XML doc (`/// <summary>`) or docstring on each shared function: what it does and what the result means.

Do not:

- restate the code (`i++ // increment i`)
- leave commented-out code
- describe history ("changed by X", "new version") — git records that
- leave a TODO without the approved ticket or the reason it is acceptable

```csharp
// Restates the code: delete it
// Check if failures >= max
public static bool IsRefused(int recentFailures) => recentFailures >= MaxFailures;

// Explains the rule and its source: keep this kind
/// <summary>Brute-force limit of the login spec: MaxFailures failed attempts inside the failure
/// window refuse the next one. The caller supplies the count for that window.</summary>
public static bool IsRefused(int recentFailures) => recentFailures >= MaxFailures;
```

## 5. Class and domain separation

- **One class, one responsibility within one domain.** An order's validation rules, its payment flow and its transaction handling change for different reasons. They belong in different classes, e.g. `OrderValidation`, `OrderPayment`, `OrderTransaction`, named by the project's conventions.
- Do not put several domains' logic in one class or function (an `OrderService` that also charges cards, sends email and adjusts stock).
- Keep each part separately maintainable, extendable and testable:
  - data and invariants live with the entity or value object
  - reusable business decisions live in the domain's business operations
  - orchestration lives in the use case
  - I/O lives in infrastructure
- Place members deliberately. Properties hold state. Methods change it while protecting invariants. Pure decisions are static functions or policies that do not reach for I/O.
- **Separate by responsibility, not by count.** Split a class when it holds two responsibilities that change for different reasons. Do not create empty classes, interfaces or layers to fill a naming pattern; that is the over-engineering the main skill warns against.
- Follow the project's own layer meanings and naming. In e-commerce this means the layer map in `e-commerce/doc/code-structure.md` and its "Service = Domain" convention.

```text
Order/
  Entities/Order.cs              state + invariants (Cancel, AddLine)
  Domain/OrderValidation.cs      reusable validation rules across use cases
  Domain/OrderPricing.cs         subtotal, discount, total rules
  Payment/OrderPayment.cs        payment orchestration via the gateway port
  Persistence/OrderTransaction   transaction boundary (the project's runner/unit of work)
```

## Before delivery: quality check

Check every item and report the result in the handoff (pass, fixed, or why not applicable). A "pass" names its evidence, e.g. the grep you ran or the line count of each new method. A pass without evidence is a claim, not a check.

| Area | Check |
| --- | --- |
| Reusability | Searched the Function Book and the code first. No logic duplicated from an existing function. New shared functions added to the Function Book; changed ones updated. |
| Formatting | Project formatter or analyzer run (e.g. `dotnet format --verify-no-changes`, `dotnet build` warnings). Logical steps visibly separated. |
| Functions | List each new or changed method with its measured line count. None is over 30 lines without a stated reason. Each has one responsibility, nesting is at most two levels, and arrow syntax is used only for one clear expression. |
| Comments | Business rules, intent and design reasons are explained. No restated code, dead code or history notes. |
| Separation | No class or function mixes domains or layers. Each new class can be tested on its own. |
| Maintainability | A new team member could change this without reading the whole feature. Names come from the domain. |
| Impact on the existing system | Callers of every changed function found (`grep`) and still correct. Public contracts and behaviour preserved unless the approved spec changes them. Existing tests still pass. |
