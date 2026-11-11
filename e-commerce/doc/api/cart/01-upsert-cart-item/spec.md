# [POST]: v1/cart/item/upsert

| Title       | Description                                                                                                                                                                                                                                                                                                                   |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Cart Item API                                                                                                                                                                                                                                                                                                          |
| Method      | POST                                                                                                                                                                                                                                                                                                                          |
| Endpoint    | v{version}/cart/item/upsert                                                                                                                                                                                                                                                                                                   |
| Version     | 1                                                                                                                                                                                                                                                                                                                             |
| Description | Add, update or delete a line of the cart of the logged-in customer, Add when id is not specified (the quantity is added when the SKU is already in the cart), Update when id is specified, Delete when rowStatus is DELETED (HTTP 204 No Content, no response body), The stock of the lot that is on sale limits the quantity |

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

|     | Parameter Name   | Data Type    | M/O       | Description                                                                                                                                                                                                    | Example                              |
| --- | ---------------- | ------------ | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id               | String: UUID | OPTIONAL  | Cart line Id, Add when not specified, Update or Delete when specified                                                                                                                                          | c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607 |
| 2   | shopProductSkuId | String: UUID | MANDATORY | Shop Product SKU Id from the product page (storefront), The SKU must be on sale, Cannot be changed when the line is updated                                                                                    | 9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f |
| 3   | quantity         | Numeric      | OPTIONAL  | Quantity of the line (integer greater than 0), Required unless rowStatus is DELETED, Without id the quantity is added to the existing line of the same SKU, With id the quantity replaces the current quantity | 2                                    |
| 4   | rowStatus        | String       | OPTIONAL  | Row status (ACTIVE, DELETED), Defaults to ACTIVE, Delete when DELETED (HTTP 204 No Content), Other statuses answer 400                                                                                         | ACTIVE                               |

### Cart Rules

- The cart belongs to the user of the access token (customer). The request never carries a user id and a line of another user is treated as not found (404, E10004). A user has one cart that holds lines of any number of shops, the lines are grouped by shop only when the cart is read.
- A line is one SKU of a shop. `shop_id`, `product_id` and `sku_id` of the line come from `shopProductSkuId`. There is at most one line that is not deleted per user and SKU, and at most 100 lines that are not deleted per user (the limit is a config). The limit is checked after the line is written, in the same transaction: when the cart then has more than 100 lines the transaction is rolled back and the request answers 409 (E10008) (approved by the product owner on 2026-11-08).
- Add (no `id`): when the user already has a line of the same SKU the quantity is added to that line (merge, HTTP 200), otherwise a new line is inserted (HTTP 201). An add is one statement, `INSERT ... ON CONFLICT (user_id, shop_id, product_id, sku_id) WHERE row_status <> 'DELETED' DO UPDATE`, that uses the partial unique index `uq_t_cart_user_id_shop_id_product_id_sku_id` (it covers the lines that are not DELETED): two requests at the same time can never create two lines of the same SKU, the merge is limited by the stock in the same statement, and a line that was deleted is outside the index, so adding the SKU again inserts a new line (approved by the product owner on 2026-11-08). Update (`id`): the quantity of the line is replaced (HTTP 200). Delete (`rowStatus = DELETED`): the line is soft-deleted (HTTP 204, no response body). The cart has no archive.
- Stock rule: the SKU must be on sale: the shop, the product, the shop product, the shop product SKU and the product SKU must be ACTIVE, otherwise the request is rejected with 404 (E10005) and the cart is not changed. One lot must be on sale and the quantity of the line after the request must not be larger than the remaining quantity of that lot, otherwise the request is rejected with 409 (E10007) and the cart is not changed. The rule is checked on add, merge and update, not on delete (approved by the product owner on 2026-11-08).
- The cart keeps no price and no lot. The price, the stock status and the total are read from the lot that is on sale each time the cart is read, so they always follow the shop (see the inquiry). A line can later become larger than the stock or no longer on sale, the cart still holds it and the inquiry reports it.
- Lock: the transaction starts by locking the ACTIVE row of the user (`authen.m_user`, `FOR UPDATE`, the first statement after BEGIN, as every authen API does), so that two requests of the same user are applied one after the other: the merge, the stock rule and the limit of 100 lines are then exact, because no other request of the user can write a line between the write and the count. A user that is missing or not ACTIVE gets 401 (E10002) and nothing is written (a technical decision of the lead SA that does not change the business rules approved by the product owner on 2026-11-08).
- Execution order: validate the request (400) -> verify the access token (401) -> BEGIN and lock the user (401 when the user is missing or not ACTIVE) -> existence checks (404, the line of the user and the shop, product and SKU that must be ACTIVE) -> stock checks (409, E10007) -> write the line (an add is the one `INSERT ... ON CONFLICT` that merges) -> line limit check (409, E10008, the transaction is rolled back). The whole request is one transaction.

#### Example Body Parameters

##### Add

```JSON
{
    "shopProductSkuId": "9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
    "quantity": 2
}
```

##### Add the same SKU again (merge)

```JSON
{
    "shopProductSkuId": "9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
    "quantity": 1
}
```

##### Update

```JSON
{
    "id": "c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607",
    "shopProductSkuId": "9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
    "quantity": 5
}
```

##### Delete

```JSON
{
    "id": "c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607",
    "shopProductSkuId": "9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
    "rowStatus": "DELETED"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/cart/item/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "shopProductSkuId": "9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
    "quantity": 2
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/cart/item/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "shopProductSkuId": "9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
    "quantity": 2
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

|     | Parameter Name | Data Type    | M/O       | Source           | Field         | Description                                                                 | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ------------- | --------------------------------------------------------------------------- | ------------------------------------ |
| 1   | cartId         | String: UUID | MANDATORY | Sequence Diagram | data.cartId   | Added, Merged or Updated Cart line Id, Not returned when deleted (HTTP 204) | c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607 |
| 2   | quantity       | Numeric      | MANDATORY | Sequence Diagram | data.quantity | Quantity of the line after the request                                      | 2                                    |

### Example Response Parameters

#### Success - Insert

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Add Cart Item Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "cartId": "c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607",
        "quantity": 2
    }
}
```

#### Success - Merge

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Merge Cart Item Success",
        "requestId": "req-5c3d9e1f-2a4b-4c6d-8e0f-1a2b3c4d5e6f",
        "timestamp": "2026-11-06T09:10:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "cartId": "c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607",
        "quantity": 3
    }
}
```

#### Success - Update

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Update Cart Item Success",
        "requestId": "req-6d4e0f2a-3b5c-4d7e-9f1a-2b3c4d5e6f7a",
        "timestamp": "2026-11-06T09:20:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "cartId": "c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607",
        "quantity": 5
    }
}
```

#### Success - Delete

HTTP 204, no response body

```HTTP
HTTP/1.1 204 No Content
```

#### Fail - Bad Request

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Shop Product SKU Id is a required field, Quantity must be an integer greater than 0, Row status must be ACTIVE or DELETED.",
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
        "bizMessage": "Shop product SKU not found.",
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
        "bizMessage": "Quantity exceeds the available stock, The SKU can be bought up to 5.",
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
        "bizMessage": "The SKU is out of stock.",
        "requestId": "req-440a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:44:08.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict Cart Full

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10008",
        "bizMessage": "The cart can hold at most 100 items.",
        "requestId": "req-450a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:45:15.123Z",
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

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Lock the user

```SQL
SELECT
    u.id as user_id
FROM authen.m_user u
WHERE u.id = '<sequence.userId>'
AND u.row_status = 'ACTIVE'
FOR UPDATE -- every authen API locks the user row first
```

### Table: [shop.t_shop_product_sku](../../../schema/shop/t_shop_product_sku.md)

#### QUERY - Get the SKU that is on sale

```SQL
SELECT
    ssk.id as shop_product_sku_id,
    sp.shop_id,
    sp.product_id,
    ssk.sku_id,
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
WHERE ssk.id = '<sequence.shopProductSkuId>'
AND ssk.row_status = 'ACTIVE'
```

### Table: [cart.t_cart](../../../schema/cart/t_cart.md)

#### QUERY - Check the line of the user

```SQL
SELECT
    c.id as cart_id,
    c.sku_id,
    c.quantity
FROM cart.t_cart c
WHERE c.id = '<sequence.id>'
AND c.user_id = '<sequence.userId>'
AND c.row_status = 'ACTIVE'
```

#### QUERY - Count the lines of the user

```SQL
SELECT
    COUNT(c.id) as line_count
FROM cart.t_cart c
WHERE c.user_id = '<sequence.userId>'
AND c.row_status = 'ACTIVE'
```

#### INSERT - Add a line

```SQL
INSERT INTO cart.t_cart (
    created_by,
    user_id,
    shop_id,
    product_id,
    sku_id,
    quantity
)
VALUES (
    '<sequence.userId>',
    '<sequence.userId>',
    '<sequence.shopId>',
    '<sequence.productId>',
    '<sequence.skuId>',
    '<sequence.quantity>'
)
ON CONFLICT (user_id, shop_id, product_id, sku_id) WHERE row_status <> 'DELETED' -- the partial unique index uq_t_cart_user_id_shop_id_product_id_sku_id
DO UPDATE SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    quantity = cart.t_cart.quantity + EXCLUDED.quantity
WHERE cart.t_cart.quantity + EXCLUDED.quantity <= '<sequence.maxOrderQuantity>' -- the stock rule of a merge, no row is returned when the merged quantity is over the stock
RETURNING id as cart_id, quantity, (xmax = 0) as is_insert -- is_insert is true for a new line and false for a merge
```

#### UPDATE - Update or delete a line

```SQL
UPDATE cart.t_cart
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.rowStatus>',
    quantity = '<sequence.newQuantity>' -- quantity when updating, not changed when deleting
WHERE id = '<sequence.cartId>'
AND user_id = '<sequence.userId>'
RETURNING id as cart_id, quantity
```
