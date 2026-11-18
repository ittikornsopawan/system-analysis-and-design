---
name: Shop Function Book
description: Shared, reusable functions of the Shop backend. Check before writing any function; update in the same change.
---

# Shop Function Book

| Function | Location | Purpose | Parameters / returns | Use when / notes |
| --- | --- | --- | --- | --- |
| `ValidationRules.NormalizeEmail(string? raw)` | `src/Shared/ValidationRules.cs` | Trim + lower-case an email | raw → normalised text ("" for null) | Before validating or storing any email |
| `ValidationRules.IsValidEmail(string normalized)` | `src/Shared/ValidationRules.cs` | The project's email rule (one @, non-empty parts, a dot in the domain, ≤ 254) | normalised email → bool | Every email input; never write another regex |
| `ValidationMessages.Required(field)` / `MaxLength(field, max)` / `Email(field)` | `src/Shared/ValidationMessages.cs` | Standard 400 message forms | field name (+ max) → message | All 400 messages |
| `Result` / `Result<T>` / `Error` | `src/Shared/Result.cs` | Expected success/failure without exceptions | — | Return from handlers and rules |
| `ResultHttp.ToHttp(result, successStatus)` | `src/Shared/ResultHttp.cs` | Maps a Result to an HTTP response (Validation→400, Rule→422, NotFound→404) | result + status → IActionResult | Every controller action |
| `IEmailSender.SendAsync(to, subject, body, ct)` | `src/Shared/IEmailSender.cs` | Sends an email | — | After commit only |
