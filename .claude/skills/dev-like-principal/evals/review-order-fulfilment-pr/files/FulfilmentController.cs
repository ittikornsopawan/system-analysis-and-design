using Dapper;
using Npgsql;

namespace Shop.Api.Fulfilment;

[ApiController]
[Route("orders")]
[Authorize]   // any authenticated user (customers and staff share the same JWT issuer)
public class FulfilmentController : ControllerBase
{
    private readonly string _connStr;
    private readonly IEmailSender _email;   // SMTP, typical latency 300ms–8s

    public FulfilmentController(IConfiguration cfg, IEmailSender email)
    {
        _connStr = cfg.GetConnectionString("Shop")!;
        _email = email;
    }

    [HttpPost("{id}/ship")]
    public async Task<IActionResult> Ship(string id, [FromBody] ShipRequest req)
    {
        using var conn = new NpgsqlConnection(_connStr);
        conn.Open();
        using var tx = conn.BeginTransaction();
        try
        {
            var order = conn.QuerySingle<OrderRow>(
                "SELECT id, customer_id, status, email FROM orders WHERE id = '" + id + "'", transaction: tx);

            if (order.Status == "Cancelled")
                return BadRequest("cancelled");

            conn.Execute("UPDATE orders SET status = 'Shipped', tracking_number = @t, shipped_at = @now WHERE id = @id",
                new { t = req.TrackingNumber, now = DateTime.Now, id = order.Id }, tx);

            var lines = conn.Query<LineRow>("SELECT * FROM order_lines WHERE order_id = @id", new { id = order.Id }, tx);
            foreach (var line in lines)
            {
                var p = conn.QuerySingle<ProductRow>("SELECT * FROM products WHERE id = @pid", new { pid = line.ProductId }, tx);
                line.ProductName = p.Name;
            }

            await _email.SendAsync(order.Email, "Your order has shipped", Render(order, lines, req.TrackingNumber));
            tx.Commit();
            return Ok();
        }
        catch (Exception)
        {
            return Ok();   // don't bother the warehouse staff with errors
        }
    }

    private static string Render(OrderRow o, IEnumerable<LineRow> lines, string tracking) =>
        $"Order {o.Id} shipped. Tracking: {tracking}. Items: {string.Join(", ", lines.Select(l => l.ProductName))}";
}

public record ShipRequest(string TrackingNumber);
