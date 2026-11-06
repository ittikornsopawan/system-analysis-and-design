# [POST]: v1/order

| Title       | Description                                                                                                                                                                                                                                                                                                                                                        |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Name        | Create Order API                                                                                                                                                                                                                                                                                                                                                   |
| Method      | POST                                                                                                                                                                                                                                                                                                                                                               |
| Endpoint    | v{version}/order                                                                                                                                                                                                                                                                                                                                                   |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                  |
| Description | Create the orders of the logged-in customer from the cart, one order for each shop, The price and the lot of every item are locked when the order is created and the quantity is taken from the lot, The orders wait for payment until expiresAt and then the system cancels them and the stock goes back to the lot, The cart lines that were ordered are deleted |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

---

## Request Parameters

### Header Parameters

|     | Parameter Name | Data Type | M/O       | Description                  | Example                                        |
| --- | -------------- | --------- | --------- | ---------------------------- | ---------------------------------------------- |
| 1   | content-type   | String    | MANDATORY | Content type of the request  | application/json                               |
| 2   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 3   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-06T09:00:00.123Z                       |
| 4   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Body Parameters

|     | Parameter Name | Data Type             | M/O       | Description                                                                                                         | Example                              |
| --- | -------------- | --------------------- | --------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | addressId      | String: UUID          | MANDATORY | Shipping address of the customer, Must be an ACTIVE address of the user, A copy of the address is kept in the order | a1d2e3f4-0b1c-4d2e-8f3a-4b5c6d7e8f90 |
| 2   | cartIds        | Array of String: UUID | OPTIONAL  | Cart line Ids to order (max 100), Every ACTIVE line of the cart when not specified                                  | c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607 |

### Order Rules

- Only the logged-in customer creates orders. The user comes from the access token and the request never carries a user id. `addressId` must be an ACTIVE address of the user, otherwise 404 (E10005). `cartIds` are lines of the cart of the user, a line of another user or a deleted line is not found (404, E10004), `cartIds` must not be duplicated (400, E10001) and has at most 100 ids. When `cartIds` is not specified every ACTIVE line of the cart is used, an empty selection is rejected with 400 (E10001).
- A line can be ordered only when it is AVAILABLE as the cart defines it: the shop, the product, the shop product, the shop product SKU and the product SKU are ACTIVE, one lot is on sale and the quantity of the line is not larger than the remaining quantity of that lot. One line that is not AVAILABLE rejects the whole request with 409 (E10007), nothing is created, the message names the line (`cartId`) and the reason (QUANTITY_EXCEEDS_STOCK, OUT_OF_STOCK or UNAVAILABLE).
- One order is created for each shop of the selected lines, so a cart with lines of two shops makes two orders. All orders are created in one transaction, either every order is created or none.
- The price of an item is the selling price of the lot that is on sale at the moment of the request and the item keeps that lot (`lot_id`), the price never changes afterwards. The profit of an item is the margin of that lot multiplied by the quantity (`gross_profit`, `shop_profit`, `platform_profit`).
- `totalDiscount`, `totalTax` and `totalShipping` are 0.00 for now (the campaign discount and the tax are not defined yet, and the shipping fee is set by the payment API when the customer starts to pay) and `totalAmount = totalPrice - totalDiscount + totalTax + totalShipping`, the database enforces this formula (`ck_t_order_total_amount_sum`) so the calculation can be added later without changing the tables.

- Each order is inserted with the status `WAIT_PAYMENT` (the status `PENDING` is not used) and `expires_at = now + the payment window` (a config, 30 minutes). The order keeps a copy of the shipping address (`ship_title`, `ship_address`, `ship_city`, `ship_state`, `ship_postal_code`, `ship_country`), so a later change of the user address does not change the order. The order `code` is generated by the system (`ORD-YYYYMMDD-NNNNNN`) and is never a field of the request.
- Stock: the quantity of every item is taken from its lot with one conditional update (`quantity >= n` and the lot is still on sale), when the update changes no row because someone else bought the stock first the request is rejected with 409 (E10007) and the whole transaction is rolled back. A lot that reaches 0 stays on sale with 0 quantity (the SKU shows OUT_OF_STOCK), the system never opens the next lot.
- A lot is never sold below its cost: the lot API and the table (`ck_t_shop_product_sku_lot_price_not_below_cost`) keep `selling_price >= cost_price`, so the gross profit of an item is never negative.
- The cart lines that were ordered are deleted (soft delete) in the same transaction. Lines of the cart that were not selected stay.
- The orders are not paid here. The payment, the refund and the shipping have their own APIs, a customer can cancel an order that is waiting for payment (see the cancel order API).
- Execution order: validate the request (400) -> existence checks (404) -> availability and stock checks (409) -> write the orders and the items, take the stock, delete the cart lines. The whole request is one transaction.

#### Example Body Parameters

```JSON
{
    "addressId": "a1d2e3f4-0b1c-4d2e-8f3a-4b5c6d7e8f90",
    "cartIds": [
        "c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607",
        "c2b1c3d4-e5f6-4071-9b82-c3d4e5f60718",
        "c3c2d4e5-f607-4182-8c93-d4e5f6071829"
    ]
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/order HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "addressId": "a1d2e3f4-0b1c-4d2e-8f3a-4b5c6d7e8f90",
    "cartIds": [
        "c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607",
        "c2b1c3d4-e5f6-4071-9b82-c3d4e5f60718",
        "c3c2d4e5-f607-4182-8c93-d4e5f6071829"
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/order' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "addressId": "a1d2e3f4-0b1c-4d2e-8f3a-4b5c6d7e8f90",
    "cartIds": [
        "c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607",
        "c2b1c3d4-e5f6-4071-9b82-c3d4e5f60718",
        "c3c2d4e5-f607-4182-8c93-d4e5f6071829"
    ]
}'
```

---

## Response Parameters

|     | Parameter Name | Data Type                          | M/O       | Source           | Field           | Description     | Example |
| --- | -------------- | ---------------------------------- | --------- | ---------------- | --------------- | --------------- | ------- |
| 1   | status         | [Object of Status](#status-object) | MANDATORY | Sequence Diagram | response.status | Response Status |         |
| 2   | data           | [Data of Status](#data-object)     | OPTIONAL  | Sequence Diagram | response.data   | Response Data   |         |

### Status Object

|     | Parameter Name | Data Type         | M/O       | Source           | Field                      | Description                                   | Example                                  |
| --- | -------------- | ----------------- | --------- | ---------------- | -------------------------- | --------------------------------------------- | ---------------------------------------- |
| 1   | code           | Numeric           | MANDATORY | Sequence Diagram | response.status.code       | HTTP Status Code                              | 200                                      |
| 2   | message        | String            | MANDATORY | Sequence Diagram | response.status.message    | HTTP Status Message                           | Ok                                       |
| 3   | bizCode        | String            | OPTIONAL  | Sequence Diagram | response.status.bizCode    | Business Code Success or Fail                 | S10000                                   |
| 4   | bizMessage     | String            | OPTIONAL  | Sequence Diagram | response.status.bizMessage | Business Message Success or Fail              | Success                                  |
| 5   | requestId      | String            | MANDATORY | Sequence Diagram | response.status.requestId  | API Request Id                                | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d |
| 6   | timestamp      | String: TIMESTAMP | MANDATORY | Sequence Diagram | response.status.timestamp  | API Request Timestamp (Without time zone UTC) | 2026-11-06T09:00:00.123Z                 |
| 7   | status         | String            | MANDATORY | Sequence Diagram | response.status.status     | API Request Status (SUCCESS, ERROR)           | SUCCESS                                  |

### Data Object

|     | Parameter Name | Data Type                       | M/O       | Source           | Field       | Description                                                      | Example |
| --- | -------------- | ------------------------------- | --------- | ---------------- | ----------- | ---------------------------------------------------------------- | ------- |
| 1   | orders         | [Array of Order](#order-object) | MANDATORY | Sequence Diagram | data.orders | Orders that were created, One for each shop ordered by shop name |         |

#### Order Object

|     | Parameter Name | Data Type         | M/O       | Source           | Field                       | Description                                           | Example                              |
| --- | -------------- | ----------------- | --------- | ---------------- | --------------------------- | ----------------------------------------------------- | ------------------------------------ |
| 1   | orderId        | String: UUID      | MANDATORY | Sequence Diagram | data.orders[].orderId       | Order Id                                              | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 2   | code           | String            | MANDATORY | Sequence Diagram | data.orders[].code          | Order code generated by the system                    | ORD-20261106-000101                  |
| 3   | shopId         | String: UUID      | MANDATORY | Sequence Diagram | data.orders[].shopId        | Shop Id                                               | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 4   | shopName       | String            | MANDATORY | Sequence Diagram | data.orders[].shopName      | Shop Name                                             | Acme Store                           |
| 5   | status         | String            | MANDATORY | Sequence Diagram | data.orders[].status        | Order status, always WAIT_PAYMENT when created        | WAIT_PAYMENT                         |
| 6   | itemCount      | Numeric           | MANDATORY | Sequence Diagram | data.orders[].itemCount     | Number of items of the order                          | 2                                    |
| 7   | totalPrice     | Numeric           | MANDATORY | Sequence Diagram | data.orders[].totalPrice    | Sum of the item prices x quantities                   | 617.00                               |
| 8   | totalDiscount  | Numeric           | MANDATORY | Sequence Diagram | data.orders[].totalDiscount | Discount, 0.00 for now                                | 0.00                                 |
| 9   | totalTax       | Numeric           | MANDATORY | Sequence Diagram | data.orders[].totalTax      | Tax, 0.00 for now                                     | 0.00                                 |
| 10  | totalShipping  | Numeric           | MANDATORY | Sequence Diagram | data.orders[].totalShipping | Shipping fee, 0.00 until the payment starts           | 0.00                                 |
| 11  | totalAmount    | Numeric           | MANDATORY | Sequence Diagram | data.orders[].totalAmount   | totalPrice - totalDiscount + totalTax + totalShipping | 617.00                               |
| 12  | expiresAt      | String: TIMESTAMP | MANDATORY | Sequence Diagram | data.orders[].expiresAt     | The order holds the stock until this time (UTC)       | 2026-11-06T09:30:00.123Z             |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Create Order Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "orders": [
            {
                "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
                "code": "ORD-20261106-000101",
                "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
                "shopName": "Acme Store",
                "status": "WAIT_PAYMENT",
                "itemCount": 2,
                "totalPrice": 617.0,
                "totalDiscount": 0.0,
                "totalTax": 0.0,
                "totalShipping": 0.0,
                "totalAmount": 617.0,
                "expiresAt": "2026-11-06T09:30:00.123Z"
            },
            {
                "orderId": "d2f3a4b5-2c3d-4e4f-8a5b-6c7d8e9f0a12",
                "code": "ORD-20261106-000102",
                "shopId": "6b2c3d4e-5f60-4b7c-9d8e-0f1a2b3c4d5e",
                "shopName": "Beta Shop",
                "status": "WAIT_PAYMENT",
                "itemCount": 1,
                "totalPrice": 520.0,
                "totalDiscount": 0.0,
                "totalTax": 0.0,
                "totalShipping": 0.0,
                "totalAmount": 520.0,
                "expiresAt": "2026-11-06T09:30:00.123Z"
            }
        ]
    }
}
```

#### Fail - Bad Request

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Address Id is a required field, Cart Ids must be valid UUIDs without duplicates, The cart has no item to order.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:40:40.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Unauthorized

```JSON
{
    "status": {
        "code": 401,
        "message": "Unauthorized",
        "bizCode": "E10002",
        "bizMessage": "Invalid or expired access token.",
        "requestId": "req-70a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:07:49.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10004",
        "bizMessage": "Cart item not found.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Reference

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "Address not found.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:42:54.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict Stock

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10007",
        "bizMessage": "Cart item c2b1c3d4-e5f6-4071-9b82-c3d4e5f60718: Quantity exceeds the available stock, The SKU can be bought up to 5.",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:43:01.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict Out Of Stock

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10007",
        "bizMessage": "Cart item c3c2d4e5-f607-4182-8c93-d4e5f6071829: The SKU is out of stock or no longer on sale.",
        "requestId": "req-440a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:44:08.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Request Timeout

```JSON
{
    "status": {
        "code": 408,
        "message": "Request Timeout",
        "bizCode": "E90001",
        "bizMessage": "The server timed out waiting for the request.",
        "requestId": "req-80a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:08:56.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

### Table: [cart.t_cart](../../../schema/cart/t_cart.md)

#### QUERY - Get the cart lines to order

```SQL
SELECT
    c.id as cart_id,
    c.shop_id,
    c.product_id,
    c.sku_id,
    c.quantity
FROM cart.t_cart c
WHERE c.user_id = '<sequence.userId>'
AND c.row_status = 'ACTIVE'
AND c.id IN ('<sequence.cartIds>') -- only when cartIds is specified, otherwise every ACTIVE line of the user
ORDER BY c.created_at
```

### Table: [shop.t_shop_product_sku](../../../schema/shop/t_shop_product_sku.md)

#### QUERY - Get the SKU of each line with the lot that is on sale

```SQL
SELECT
    ssk.id as shop_product_sku_id,
    sp.shop_id,
    sp.product_id,
    ssk.sku_id,
    s.name as shop_name,
    p.name as product_name,
    ps.name as sku_name,
    l.id as lot_id,
    l.selling_price,
    l.cost_price,
    l.gross_margin,
    l.share_margin,
    l.platform_margin,
    l.quantity as max_order_quantity
FROM shop.t_shop_product_sku ssk
INNER JOIN shop.t_shop_product sp
    ON sp.id = ssk.shop_product_id
    AND sp.row_status = 'ACTIVE'
INNER JOIN shop.m_shop s
    ON s.id = sp.shop_id
    AND s.row_status = 'ACTIVE'
INNER JOIN product.m_product p
    ON p.id = sp.product_id
    AND p.row_status = 'ACTIVE'
INNER JOIN product.m_product_sku ps
    ON ps.id = ssk.sku_id
    AND ps.row_status = 'ACTIVE'
LEFT JOIN shop.t_shop_product_sku_lot l
    ON l.shop_product_sku_id = ssk.id
    AND l.is_on_sale = TRUE
    AND l.row_status = 'ACTIVE'
WHERE (sp.shop_id, sp.product_id, ssk.sku_id) IN (<sequence.lineKeys>)
AND ssk.row_status = 'ACTIVE'
```

### Table: [authen.t_user_address](../../../schema/authen/t_user_address.md)

#### QUERY - Check the address of the user

```SQL
SELECT
    ua.id as address_id,
    ua.title,
    ua.address,
    ua.city,
    ua.state,
    ua.postal_code,
    ua.country
FROM authen.t_user_address ua
WHERE ua.id = '<sequence.addressId>'
AND ua.user_id = '<sequence.userId>'
AND ua.row_status = 'ACTIVE'
```

### Table: [sales.t_order](../../../schema/sales/t_order.md)

#### INSERT - Create the order of a shop

```SQL
INSERT INTO sales.t_order (
    created_by,
    row_status,
    user_id,
    shop_id,
    address_id,
    ship_title,
    ship_address,
    ship_city,
    ship_state,
    ship_postal_code,
    ship_country,
    code,
    total_price,
    total_discount,
    total_tax,
    total_shipping,
    total_amount,
    expires_at,
    status
)
VALUES (
    '<sequence.userId>',
    'ACTIVE',
    '<sequence.userId>',
    '<sequence.shopId>',
    '<sequence.addressId>',
    '<sequence.address.title>', -- copy of the user address
    '<sequence.address.address>',
    '<sequence.address.city>',
    '<sequence.address.state>',
    '<sequence.address.postalCode>',
    '<sequence.address.country>',
    '<sequence.code>', -- generated by the system, generate a new code when it is not unique
    '<sequence.totalPrice>',
    0.00,
    0.00,
    0.00,
    '<sequence.totalAmount>',
    NOW() AT TIME ZONE 'UTC' + INTERVAL '<sequence.paymentWindow>',
    'WAIT_PAYMENT'
)
RETURNING id as order_id, code, expires_at
```

### Table: [sales.t_order_item](../../../schema/sales/t_order_item.md)

#### INSERT - Create the items of the order

```SQL
INSERT INTO sales.t_order_item (
    created_by,
    order_id,
    shop_id,
    product_id,
    sku_id,
    lot_id,
    quantity,
    price,
    discount,
    total_price,
    gross_profit,
    shop_profit,
    platform_profit
)
VALUES (
    '<sequence.userId>',
    '<sequence.orderId>',
    '<sequence.shopId>',
    '<sequence.productId>',
    '<sequence.skuId>',
    '<sequence.lotId>', -- the lot that is on sale
    '<sequence.quantity>',
    '<sequence.sellingPrice>', -- selling price of the lot
    0.00,
    '<sequence.sellingPrice * quantity>',
    '<sequence.grossMargin * quantity>', -- margin of the lot
    '<sequence.shareMargin * quantity>',
    '<sequence.platformMargin * quantity>'
)
RETURNING id as order_item_id
```

### Table: [shop.t_shop_product_sku_lot](../../../schema/shop/t_shop_product_sku_lot.md)

#### UPDATE - Take the quantity from the lot that is on sale

```SQL
UPDATE shop.t_shop_product_sku_lot
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    quantity = quantity - '<sequence.quantity>'
WHERE id = '<sequence.lotId>'
AND is_on_sale = TRUE
AND row_status = 'ACTIVE'
AND quantity >= '<sequence.quantity>' -- no row changed means the stock was taken by someone else, answer 409 (E10007) and roll back
RETURNING id as lot_id, quantity
```

### Table: [cart.t_cart](../../../schema/cart/t_cart.md)

#### UPDATE - Delete the cart lines that were ordered

```SQL
UPDATE cart.t_cart
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'DELETED'
WHERE id IN ('<sequence.orderedCartIds>')
AND user_id = '<sequence.userId>'
AND row_status = 'ACTIVE'
```
