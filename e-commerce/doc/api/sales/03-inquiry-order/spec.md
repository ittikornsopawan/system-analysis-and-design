# [GET]: v1/order

| Title       | Description                                                                                                                                                                         |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Order API                                                                                                                                                                   |
| Method      | GET                                                                                                                                                                                 |
| Endpoint    | v{version}/order                                                                                                                                                                    |
| Version     | 1                                                                                                                                                                                   |
| Description | Inquiry the orders of the logged-in customer with their items, newest first, Filter by id, status or order code, The customer never sees the cost, the lot or the profit of an item |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- Only the orders of the user of the access token are returned (the request never carries a user id), the order of another user is not found, `id` of another user answers an empty list. Orders with `rowStatus` DELETED are never returned.
- The orders are ordered by creation time (newest first) then `id`. `items` of an order are ordered by creation time then `id`.
- The customer sees the price that was locked when the order was created (`price`, `totalPrice`), never the cost, the lot, the margin or the profit. The shipping address is returned only by its title (`shipTitle`), the full copy is for the shop.
- An order that is `WAIT_PAYMENT` holds the stock until `expiresAt`, after that the system cancels it (status CANCELLED).

---

## Request Parameters

### Header Parameters

|     | Parameter Name | Data Type | M/O       | Description                  | Example                                        |
| --- | -------------- | --------- | --------- | ---------------------------- | ---------------------------------------------- |
| 1   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-06T09:00:00.123Z                       |
| 3   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Query Parameters

|     | Parameter Name | Data Type    | M/O      | Description                                                                                                                                 | Example                              |
| --- | -------------- | ------------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL | Order Id, Response is a list with one item                                                                                                  | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 2   | status         | String       | OPTIONAL | Order status filter (PENDING, PROCESSING, WAIT_PAYMENT, PAYMENT_CONFIRMED, REFUNDED, COMPLETED, CANCELLED), All statuses when not specified | WAIT_PAYMENT                         |
| 3   | pageIndex      | Numeric      | OPTIONAL | Page index starting from 1, Defaults to 1                                                                                                   | 1                                    |
| 4   | pageSize       | Numeric      | OPTIONAL | Number of items per page (max 100), Defaults to 10                                                                                          | 10                                   |
| 5   | search         | String       | OPTIONAL | Search by order code or shop name                                                                                                           | ORD-2026                             |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/order?status=WAIT_PAYMENT&search=ORD-2026&pageIndex=1&pageSize=10 HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/order?status=WAIT_PAYMENT&search=ORD-2026&pageIndex=1&pageSize=10' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d'
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

|     | Parameter Name | Data Type                       | M/O       | Source           | Field           | Description              | Example |
| --- | -------------- | ------------------------------- | --------- | ---------------- | --------------- | ------------------------ | ------- |
| 1   | orders         | [Array of Order](#order-object) | MANDATORY | Sequence Diagram | data.orders     | Orders of the page       |         |
| 2   | pageIndex      | Numeric                         | MANDATORY | Sequence Diagram | data.pageIndex  | Current page index       | 1       |
| 3   | pageSize       | Numeric                         | MANDATORY | Sequence Diagram | data.pageSize   | Number of items per page | 10      |
| 4   | totalItems     | Numeric                         | MANDATORY | Sequence Diagram | data.totalItems | Total number of orders   | 2       |
| 5   | totalPages     | Numeric                         | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages    | 1       |

#### Order Object

|     | Parameter Name | Data Type                     | M/O       | Source           | Field                       | Description                                           | Example                              |
| --- | -------------- | ----------------------------- | --------- | ---------------- | --------------------------- | ----------------------------------------------------- | ------------------------------------ |
| 1   | orderId        | String: UUID                  | MANDATORY | Sequence Diagram | data.orders[].orderId       | Order Id                                              | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 2   | code           | String                        | MANDATORY | Sequence Diagram | data.orders[].code          | Order code                                            | ORD-20261106-000101                  |
| 3   | shopId         | String: UUID                  | MANDATORY | Sequence Diagram | data.orders[].shopId        | Shop Id                                               | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 4   | shopName       | String                        | MANDATORY | Sequence Diagram | data.orders[].shopName      | Shop Name                                             | Acme Store                           |
| 5   | status         | String                        | MANDATORY | Sequence Diagram | data.orders[].status        | Order status                                          | WAIT_PAYMENT                         |
| 6   | shipTitle      | String                        | MANDATORY | Sequence Diagram | data.orders[].shipTitle     | Title of the shipping address copied into the order   | Home                                 |
| 7   | totalPrice     | Numeric                       | MANDATORY | Sequence Diagram | data.orders[].totalPrice    | Sum of the item prices x quantities                   | 617.00                               |
| 8   | totalDiscount  | Numeric                       | MANDATORY | Sequence Diagram | data.orders[].totalDiscount | Discount                                              | 0.00                                 |
| 9   | totalTax       | Numeric                       | MANDATORY | Sequence Diagram | data.orders[].totalTax      | Tax                                                   | 0.00                                 |
| 10  | totalShipping  | Numeric                       | MANDATORY | Sequence Diagram | data.orders[].totalShipping | Shipping fee                                          | 0.00                                 |
| 11  | totalAmount    | Numeric                       | MANDATORY | Sequence Diagram | data.orders[].totalAmount   | totalPrice - totalDiscount + totalTax + totalShipping | 617.00                               |
| 12  | expiresAt      | String: TIMESTAMP             | MANDATORY | Sequence Diagram | data.orders[].expiresAt     | The order holds the stock until this time (UTC)       | 2026-11-06T09:30:00.123Z             |
| 13  | createdAt      | String: TIMESTAMP             | MANDATORY | Sequence Diagram | data.orders[].createdAt     | Time the order was created (UTC)                      | 2026-11-06T09:00:00.123Z             |
| 14  | items          | [Array of Item](#item-object) | MANDATORY | Sequence Diagram | data.orders[].items         | Items of the order                                    |                                      |

#### Item Object

|     | Parameter Name | Data Type                                     | M/O       | Source           | Field                              | Description                                                           | Example                              |
| --- | -------------- | --------------------------------------------- | --------- | ---------------- | ---------------------------------- | --------------------------------------------------------------------- | ------------------------------------ |
| 1   | orderItemId    | String: UUID                                  | MANDATORY | Sequence Diagram | data.orders[].items[].orderItemId  | Order Item Id                                                         | e1f2a3b4-3c4d-4e5f-9a6b-7c8d9e0f1a21 |
| 2   | productId      | String: UUID                                  | MANDATORY | Sequence Diagram | data.orders[].items[].productId    | Product Id                                                            | e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c |
| 3   | productName    | String                                        | MANDATORY | Sequence Diagram | data.orders[].items[].productName  | Product Name                                                          | Cotton Shirt                         |
| 4   | skuId          | String: UUID                                  | MANDATORY | Sequence Diagram | data.orders[].items[].skuId        | Product SKU Id                                                        | 7b8c9d0e-1f2a-4b3c-9d4e-5f6a7b8c9d0e |
| 5   | skuName        | String                                        | MANDATORY | Sequence Diagram | data.orders[].items[].skuName      | SKU Name                                                              | A / S                                |
| 6   | optionValues   | [Array of Option Value](#option-value-object) | MANDATORY | Sequence Diagram | data.orders[].items[].optionValues | Chosen value of every level in level order, Empty for the default SKU |                                      |
| 7   | imagePath      | String                                        | OPTIONAL  | Sequence Diagram | data.orders[].items[].imagePath    | Image of the SKU, Null when there is no image                         | /products/shirt/a.png                |
| 8   | quantity       | Numeric                                       | MANDATORY | Sequence Diagram | data.orders[].items[].quantity     | Quantity                                                              | 2                                    |
| 9   | price          | Numeric                                       | MANDATORY | Sequence Diagram | data.orders[].items[].price        | Unit price locked when the order was created                          | 199.00                               |
| 10  | discount       | Numeric                                       | MANDATORY | Sequence Diagram | data.orders[].items[].discount     | Discount of the item                                                  | 0.00                                 |
| 11  | totalPrice     | Numeric                                       | MANDATORY | Sequence Diagram | data.orders[].items[].totalPrice   | price x quantity                                                      | 398.00                               |

#### Option Value Object

|     | Parameter Name | Data Type | M/O       | Source           | Field                                           | Description  | Example |
| --- | -------------- | --------- | --------- | ---------------- | ----------------------------------------------- | ------------ | ------- |
| 1   | optionName     | String    | MANDATORY | Sequence Diagram | data.orders[].items[].optionValues[].optionName | Level name   | Pattern |
| 2   | value          | String    | MANDATORY | Sequence Diagram | data.orders[].items[].optionValues[].value      | Chosen value | A       |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Order Success",
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
                "totalPrice": 617.0,
                "totalDiscount": 0.0,
                "totalTax": 0.0,
                "totalShipping": 0.0,
                "totalAmount": 617.0,
                "expiresAt": "2026-11-06T09:30:00.123Z",
                "createdAt": "2026-11-06T09:00:00.123Z",
                "items": [
                    {
                        "orderItemId": "e1f2a3b4-3c4d-4e5f-9a6b-7c8d9e0f1a21",
                        "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
                        "productName": "Cotton Shirt",
                        "skuId": "7b8c9d0e-1f2a-4b3c-9d4e-5f6a7b8c9d0e",
                        "skuName": "A / S",
                        "optionValues": [
                            {
                                "optionName": "Pattern",
                                "value": "A"
                            },
                            {
                                "optionName": "Size",
                                "value": "S"
                            }
                        ],
                        "imagePath": "/products/shirt/a.png",
                        "quantity": 2,
                        "price": 199.0,
                        "discount": 0.0,
                        "totalPrice": 398.0
                    },
                    {
                        "orderItemId": "e2a3b4c5-4d5e-4f60-8b7c-8d9e0f1a2b32",
                        "productId": "f2b3c4d5-e6f7-4a8b-9c0d-1e2f3a4b5c6d",
                        "productName": "Wireless Mouse",
                        "skuId": "8c9d0e1f-2a3b-4c4d-8e5f-6a7b8c9d0e1f",
                        "skuName": "Wireless Mouse",
                        "optionValues": [],
                        "imagePath": "/products/wireless-mouse/1.png",
                        "quantity": 1,
                        "price": 219.0,
                        "discount": 0.0,
                        "totalPrice": 219.0
                    }
                ],
                "shipTitle": "Home"
            },
            {
                "orderId": "d2f3a4b5-2c3d-4e4f-8a5b-6c7d8e9f0a12",
                "code": "ORD-20261106-000102",
                "shopId": "6b2c3d4e-5f60-4b7c-9d8e-0f1a2b3c4d5e",
                "shopName": "Beta Shop",
                "status": "CANCELLED",
                "totalPrice": 520.0,
                "totalDiscount": 0.0,
                "totalTax": 0.0,
                "totalShipping": 0.0,
                "totalAmount": 520.0,
                "expiresAt": "2026-11-06T09:30:00.123Z",
                "createdAt": "2026-11-06T09:00:00.123Z",
                "items": [
                    {
                        "orderItemId": "e3b4c5d6-5e6f-4071-9c8d-9e0f1a2b3c43",
                        "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
                        "productName": "Cotton Shirt",
                        "skuId": "9d0e1f2a-3b4c-4d5e-9f6a-7b8c9d0e1f2a",
                        "skuName": "B / M",
                        "optionValues": [
                            {
                                "optionName": "Pattern",
                                "value": "B"
                            },
                            {
                                "optionName": "Size",
                                "value": "M"
                            }
                        ],
                        "imagePath": "/products/shirt/main.png",
                        "quantity": 1,
                        "price": 520.0,
                        "discount": 0.0,
                        "totalPrice": 520.0
                    }
                ],
                "shipTitle": "Home"
            }
        ],
        "pageIndex": 1,
        "pageSize": 10,
        "totalItems": 2,
        "totalPages": 1
    }
}
```

#### Success - Empty

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Order Success",
        "requestId": "req-9a7b3c5d-6e8f-4a0b-c2d4-5e6f7a8b9c0d",
        "timestamp": "2026-11-06T09:05:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "orders": [],
        "pageIndex": 1,
        "pageSize": 10,
        "totalItems": 0,
        "totalPages": 0
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
        "bizMessage": "Page size must be between 1 and 100, Id must be a valid UUID, Status must be a valid order status.",
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

### Table: [sales.t_order](../../../schema/sales/t_order.md)

#### QUERY - Get the orders of the user

```SQL
SELECT
    o.id as order_id,
    o.code,
    o.shop_id,
    s.name as shop_name,
    o.status,
    o.ship_title,
    o.total_price,
    o.total_discount,
    o.total_tax,
    o.total_shipping,
    o.total_amount,
    o.expires_at,
    o.created_at
FROM sales.t_order o
INNER JOIN shop.m_shop s
    ON s.id = o.shop_id
WHERE o.user_id = '<sequence.userId>'
AND o.row_status <> 'DELETED'
AND o.id = '<sequence.id>' -- only when id is specified
AND o.status = '<sequence.status>' -- only when status is specified
AND (o.code ILIKE '%<sequence.search>%' OR s.name ILIKE '%<sequence.search>%') -- only when search is specified
ORDER BY o.created_at DESC, o.id
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Count the orders of the user

```SQL
SELECT
    COUNT(o.id) as total_items
FROM sales.t_order o
INNER JOIN shop.m_shop s
    ON s.id = o.shop_id
WHERE o.user_id = '<sequence.userId>'
AND o.row_status <> 'DELETED'
AND o.id = '<sequence.id>' -- only when id is specified
AND o.status = '<sequence.status>' -- only when status is specified
AND (o.code ILIKE '%<sequence.search>%' OR s.name ILIKE '%<sequence.search>%') -- only when search is specified
```

### Table: [sales.t_order_item](../../../schema/sales/t_order_item.md)

#### QUERY - Get the items of the orders

```SQL
SELECT
    oi.id as order_item_id,
    oi.order_id,
    oi.product_id,
    oi.sku_id,
    oi.quantity,
    oi.price,
    oi.discount,
    oi.total_price
FROM sales.t_order_item oi
WHERE oi.order_id IN ('<sequence.orderIds>')
AND oi.row_status <> 'DELETED'
ORDER BY oi.created_at, oi.id
```

### Table: [product.m_product](../../../schema/product/m_product.md)

#### QUERY - Get the product and SKU names of the items

```SQL
SELECT
    p.id as product_id,
    p.name as product_name,
    ps.id as sku_id,
    ps.name as sku_name
FROM product.m_product p
INNER JOIN product.m_product_sku ps
    ON ps.product_id = p.id
WHERE ps.id IN ('<sequence.skuIds>')
```

### Table: [product.m_product_sku_option_value](../../../schema/product/m_product_sku_option_value.md)

#### QUERY - Get the chosen option values of the SKUs

```SQL
SELECT
    psov.sku_id,
    po.name as option_name,
    pov.value
FROM product.m_product_sku_option_value psov
INNER JOIN product.m_product_option_value pov
    ON pov.id = psov.option_value_id
INNER JOIN product.m_product_option po
    ON po.id = pov.option_id
WHERE psov.sku_id IN ('<sequence.skuIds>')
ORDER BY psov.sku_id, po.level_no
```
