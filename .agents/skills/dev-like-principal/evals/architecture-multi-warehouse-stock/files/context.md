Current system (facts from the team):
- One ASP.NET Core 8 monolith + PostgreSQL 16 (single primary, one read replica). Team: 6 backend devs, 1 DevOps.
- Stock today: `products.stock_qty` integer, decremented in the same transaction that creates the order.
- Volume: ~8,000 orders/day; peak ~25 orders/second during monthly 9.9 / 11.11 sales; ~40,000 SKUs.
- Oversell incidents: 14 last 11.11 sale (two orders took the last unit at the same time).
- New requirement: 3 warehouses (Bangkok, Chiang Mai, Hat Yai). Customers see "in stock" per delivery region,
  stock is reserved when the customer reaches the payment page and released if not paid within 15 minutes.
  Warehouse staff adjust stock from a handheld app (~2,000 adjustments/day). The warehouse management system (WMS)
  of the Hat Yai partner sends a full stock snapshot by SFTP CSV every 30 minutes.
- The CTO suggested: "Let's put stock in Redis as the source of truth so it's real-time and fast, and use Kafka
  between services."
