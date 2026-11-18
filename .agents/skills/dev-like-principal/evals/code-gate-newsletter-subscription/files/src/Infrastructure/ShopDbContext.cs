using Microsoft.EntityFrameworkCore;
namespace Shop.Infrastructure;

public class ShopDbContext(DbContextOptions<ShopDbContext> options) : DbContext(options)
{
    public DbSet<Shop.Customers.Customer> Customers => Set<Shop.Customers.Customer>();
}
