using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Shop.Infrastructure;
using Shop.Shared;
namespace Shop.Customers;

public class Customer { public Guid Id { get; set; } public string Email { get; set; } = ""; public string FirstName { get; set; } = ""; }
public record RegisterCustomerRequest(string? Email, string? FirstName);

[ApiController]
[Route("customers")]
public class CustomersController(ShopDbContext db) : ControllerBase
{
    [HttpPost]
    public async Task<IActionResult> Register(RegisterCustomerRequest req, CancellationToken ct)
    {
        var email = ValidationRules.NormalizeEmail(req.Email);
        if (!ValidationRules.IsValidEmail(email))
            return ResultHttp.ToHttp(Result<Customer>.Failure(new Error("Customer.Email", ValidationMessages.Email("email"), ErrorType.Validation)), 201);

        var customer = new Customer { Id = Guid.NewGuid(), Email = email, FirstName = req.FirstName ?? "" };
        db.Customers.Add(customer);
        await db.SaveChangesAsync(ct);
        return ResultHttp.ToHttp(Result<Customer>.Success(customer), 201);
    }
}
