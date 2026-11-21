// Shop.Api — ASP.NET Core 8, EF Core 8 (PostgreSQL). Consumed by the web app and by the
// Android/iOS apps (mobile releases go through store review; ~40% of users are on app versions older than 3 months).
namespace Shop.Api.Orders;

public class Order
{
    public Guid Id { get; set; }
    public Guid CustomerId { get; set; }
    public decimal Total { get; set; }            // THB only today
    public string Status { get; set; } = "Pending";
    public DateTime CreatedAt { get; set; }
    public List<OrderLine> Lines { get; set; } = new();
}

public class OrderLine
{
    public Guid Id { get; set; }
    public Guid ProductId { get; set; }
    public int Qty { get; set; }
    public decimal UnitPrice { get; set; }
}

public record PlaceOrderRequest(List<PlaceOrderLine> Lines);
public record PlaceOrderLine(Guid ProductId, int Qty);
public record OrderResponse(Guid Id, decimal Total, string Status, DateTime CreatedAt);

[ApiController]
[Route("orders")]
[Authorize]
public class OrdersController(ShopDbContext db) : ControllerBase
{
    [HttpPost]
    public async Task<ActionResult<OrderResponse>> Place(PlaceOrderRequest req, CancellationToken ct)
    {
        var customerId = User.GetCustomerId();
        var productIds = req.Lines.Select(l => l.ProductId).ToList();
        var prices = await db.Products.Where(p => productIds.Contains(p.Id))
            .ToDictionaryAsync(p => p.Id, p => p.Price, ct);

        var order = new Order
        {
            Id = Guid.NewGuid(),
            CustomerId = customerId,
            CreatedAt = DateTime.UtcNow,
            Lines = req.Lines.Select(l => new OrderLine
                { Id = Guid.NewGuid(), ProductId = l.ProductId, Qty = l.Qty, UnitPrice = prices[l.ProductId] }).ToList()
        };
        order.Total = order.Lines.Sum(l => l.UnitPrice * l.Qty);
        db.Orders.Add(order);
        await db.SaveChangesAsync(ct);
        return new OrderResponse(order.Id, order.Total, order.Status, order.CreatedAt);
    }

    [HttpGet("{id:guid}")]
    public async Task<ActionResult<OrderResponse>> Get(Guid id, CancellationToken ct)
    {
        var o = await db.Orders.AsNoTracking()
            .SingleOrDefaultAsync(x => x.Id == id && x.CustomerId == User.GetCustomerId(), ct);
        return o is null ? NotFound() : new OrderResponse(o.Id, o.Total, o.Status, o.CreatedAt);
    }
}
