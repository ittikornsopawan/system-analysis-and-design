SHOP-412 (from Product Owner)

1. We are expanding to Malaysia next quarter. Change the order response so `total` becomes
   `{ "amount": 1250.00, "currency": "THB" }` instead of a plain number.
2. Add coupon support to POST /orders: request gets an optional `couponCode`.
   Coupons are either a fixed amount (THB) or a percentage, have an expiry date,
   and each coupon has a max number of uses (marketing usually sets 1000 uses for a campaign;
   flash campaigns get ~3000 redemptions in the first minute).
Please ship both this sprint.
