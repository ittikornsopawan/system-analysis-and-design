---
name: "Upsert Cart Item Batch API"
description: "Add, update or delete several lines of the cart of the logged-in customer at the same time, for example to move a guest cart into the cart of the user after login. Read it when you implement, review or test POST v1/cart/item/upsert/batch."
status: in-review
approved_by: null
approved_at: null
---

# [POST]: v1/cart/item/upsert/batch

| Title       | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Name        | Upsert Cart Item Batch API                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Method      | POST                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Endpoint    | v{version}/cart/item/upsert/batch                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Description | Add, update or delete several lines of the cart of the logged-in customer at the same time, for example to move a guest cart into the cart of the user after login, Each item follows the rules of the single upsert, The response is always HTTP 200 for a successful batch including when it deletes (each result is reported in the body with its action), All items are processed in one transaction in the request order, If any item fails then nothing is changed |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- The cart belongs to the user of the access token; the request carries no user id and a line of another user is 404 (E10004). A line is one SKU of a shop, with at most one line that is not deleted per user and SKU and at most 100 lines that are not deleted per user (config). The limit is checked after the write in the same transaction: more than 100 lines rolls back with 409 (E10008) (approved by the product owner on 2026-11-08).
- Per item: Add (no `id`) merges into the line of the same SKU (200) or inserts a new line (201) in one statement; Update (`id`) replaces the quantity (200); Delete (`rowStatus = DELETED`) soft-deletes the line (204, no response body).
- The SKU must be on sale: the shop, the product, the shop product, the shop product SKU and the product SKU must be ACTIVE, otherwise the request is rejected with 404 (E10005); the quantity after the request must not be larger than the remaining quantity of the lot on sale, otherwise 409 (E10007). The stock rule is not checked on delete.
- The cart keeps no price and no lot, the inquiry reads them each time the cart is read.
- The transaction starts by locking the ACTIVE row of the user, a user that is missing or not ACTIVE gets 401 (E10002). The order of the checks and the locks is in the sequence diagram.
- Batch: the HTTP status is always HTTP 200; the first failing item stops the batch and its error is returned with the position `items[i]`, nothing is changed. The limit of 100 lines is checked after all items are applied.

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

|     | Parameter Name | Data Type                               | M/O       | Description                                                | Example |
| --- | -------------- | --------------------------------------- | --------- | ---------------------------------------------------------- | ------- |
| 1   | items          | [Array of Cart Item](#cart-item-object) | MANDATORY | Cart lines to add, update or delete (min 1, max 100 items) |         |

#### Cart Item Object

|     | Parameter Name   | Data Type    | M/O       | Description                                                                                                                                                                                                    | Example                              |
| --- | ---------------- | ------------ | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id               | String: UUID | OPTIONAL  | Cart line Id, Add when not specified, Update or Delete when specified, Must not be duplicated in the request                                                                                                   | c2b1c3d4-e5f6-4071-9b82-c3d4e5f60718 |
| 2   | shopProductSkuId | String: UUID | MANDATORY | Shop Product SKU Id from the product page (storefront), The SKU must be on sale, Cannot be changed when the line is updated, Must not be duplicated among the items that have no id                            | ad1e2f3a-4b5c-4d6e-9f7a-8b9c0d1e2f3a |
| 3   | quantity         | Numeric      | OPTIONAL  | Quantity of the line (integer greater than 0), Required unless rowStatus is DELETED, Without id the quantity is added to the existing line of the same SKU, With id the quantity replaces the current quantity | 2                                    |
| 4   | rowStatus        | String       | OPTIONAL  | Row status (ACTIVE, DELETED), Defaults to ACTIVE, Delete when DELETED (HTTP 204 No Content), Other statuses answer 400                                                                                         | ACTIVE                               |

#### Example Body Parameters

```JSON
{
    "items": [
        {
            "shopProductSkuId": "9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
            "quantity": 2
        },
        {
            "id": "c2b1c3d4-e5f6-4071-9b82-c3d4e5f60718",
            "shopProductSkuId": "ad1e2f3a-4b5c-4d6e-9f7a-8b9c0d1e2f3a",
            "quantity": 4
        },
        {
            "id": "c3c2d4e5-f607-4182-8c93-d4e5f6071829",
            "shopProductSkuId": "be2f3a4b-5c6d-4e7f-8a8b-9c0d1e2f3a4b",
            "rowStatus": "DELETED"
        }
    ]
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/cart/item/upsert/batch HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "items": [
        {
            "shopProductSkuId": "9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
            "quantity": 2
        },
        {
            "id": "c2b1c3d4-e5f6-4071-9b82-c3d4e5f60718",
            "shopProductSkuId": "ad1e2f3a-4b5c-4d6e-9f7a-8b9c0d1e2f3a",
            "quantity": 4
        },
        {
            "id": "c3c2d4e5-f607-4182-8c93-d4e5f6071829",
            "shopProductSkuId": "be2f3a4b-5c6d-4e7f-8a8b-9c0d1e2f3a4b",
            "rowStatus": "DELETED"
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/cart/item/upsert/batch' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "items": [
        {
            "shopProductSkuId": "9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
            "quantity": 2
        },
        {
            "id": "c2b1c3d4-e5f6-4071-9b82-c3d4e5f60718",
            "shopProductSkuId": "ad1e2f3a-4b5c-4d6e-9f7a-8b9c0d1e2f3a",
            "quantity": 4
        },
        {
            "id": "c3c2d4e5-f607-4182-8c93-d4e5f6071829",
            "shopProductSkuId": "be2f3a4b-5c6d-4e7f-8a8b-9c0d1e2f3a4b",
            "rowStatus": "DELETED"
        }
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

|     | Parameter Name | Data Type                         | M/O       | Source           | Field      | Description                                    | Example |
| --- | -------------- | --------------------------------- | --------- | ---------------- | ---------- | ---------------------------------------------- | ------- |
| 1   | items          | [Array of Result](#result-object) | MANDATORY | Sequence Diagram | data.items | Result of each item, Same order as the request |         |

#### Result Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                 | Description                                                       | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | --------------------- | ----------------------------------------------------------------- | ------------------------------------ |
| 1   | index          | Numeric      | MANDATORY | Sequence Diagram | data.items[].index    | Index of the item in the request, Starting from 0                 | 0                                    |
| 2   | cartId         | String: UUID | MANDATORY | Sequence Diagram | data.items[].cartId   | Added, Merged, Updated or Deleted Cart line Id                    | c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607 |
| 3   | action         | String       | MANDATORY | Sequence Diagram | data.items[].action   | Action of the item (INSERT, MERGE, UPDATE, DELETE)                | INSERT                               |
| 4   | quantity       | Numeric      | OPTIONAL  | Sequence Diagram | data.items[].quantity | Quantity of the line after the request, Not returned when deleted | 2                                    |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Batch Upsert Cart Item Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "index": 0,
                "cartId": "c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607",
                "action": "INSERT",
                "quantity": 2
            },
            {
                "index": 1,
                "cartId": "c2b1c3d4-e5f6-4071-9b82-c3d4e5f60718",
                "action": "UPDATE",
                "quantity": 4
            },
            {
                "index": 2,
                "cartId": "c3c2d4e5-f607-4182-8c93-d4e5f6071829",
                "action": "DELETE"
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
        "bizMessage": "items[0]: Shop Product SKU Id is a required field, Quantity must be an integer greater than 0, Row status must be ACTIVE or DELETED.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:40:40.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Item Count

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Items must contain 1 to 100 items.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Duplicate Id

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "items[2]: Id is duplicated with items[1].",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:42:54.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Duplicate SKU

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "items[1]: Shop Product SKU Id is duplicated with items[0].",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:43:01.123Z",
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
        "bizMessage": "items[1]: Cart item not found.",
        "requestId": "req-440a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:44:08.123Z",
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
        "bizMessage": "items[0]: Shop product SKU not found.",
        "requestId": "req-450a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:45:15.123Z",
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
        "bizMessage": "items[0]: Quantity exceeds the available stock, The SKU can be bought up to 5.",
        "requestId": "req-460a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:46:22.123Z",
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
        "bizMessage": "items[1]: The SKU is out of stock.",
        "requestId": "req-470a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:47:29.123Z",
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
        "requestId": "req-480a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:48:36.123Z",
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
WHERE ssk.id = '<sequence.items.shopProductSkuId>'
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
WHERE c.id = '<sequence.items.id>'
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
    '<sequence.items.quantity>'
)
ON CONFLICT (user_id, shop_id, product_id, sku_id) WHERE row_status <> 'DELETED' -- the partial unique index uq_t_cart_user_id_shop_id_product_id_sku_id
DO UPDATE SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    quantity = cart.t_cart.quantity + EXCLUDED.quantity
WHERE cart.t_cart.quantity + EXCLUDED.quantity <= '<sequence.items.maxOrderQuantity>' -- the stock rule of a merge, no row is returned when the merged quantity is over the stock
RETURNING id as cart_id, quantity, (xmax = 0) as is_insert -- is_insert is true for a new line and false for a merge
```

#### UPDATE - Update or delete a line

```SQL
UPDATE cart.t_cart
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.items.rowStatus>',
    quantity = '<sequence.newQuantity>' -- quantity when updating, not changed when deleting
WHERE id = '<sequence.cartId>'
AND user_id = '<sequence.userId>'
RETURNING id as cart_id, quantity
```
