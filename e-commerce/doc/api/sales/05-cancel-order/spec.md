# [POST]: v1/order/cancel

| Title       | Description                                                                                                                                                                                                                                                       |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Cancel Order API                                                                                                                                                                                                                                                  |
| Method      | POST                                                                                                                                                                                                                                                              |
| Endpoint    | v{version}/order/cancel                                                                                                                                                                                                                                           |
| Version     | 1                                                                                                                                                                                                                                                                 |
| Description | Cancel an order that is waiting for payment, The quantity of every item goes back to the lot it was taken from, The order owner, a member of the shop of the order or a platform administrator can cancel, Orders that are paid or later cannot be cancelled here |

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

|     | Parameter Name | Data Type    | M/O       | Description | Example                              |
| --- | -------------- | ------------ | --------- | ----------- | ------------------------------------ |
| 1   | orderId        | String: UUID | MANDATORY | Order Id    | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |

### Cancel Rules

- The caller must be the owner of the order (the user of the access token), an ACTIVE member of the shop of the order (ADMIN or STAFF in `shop.t_shop_user`) or a platform administrator (a user that has the role `PLATFORM_ADMIN`). For any other user the order counts as not found (404, E10004), the same answer as an order that does not exist or is DELETED.
- Only an order with the status `WAIT_PAYMENT` can be cancelled, otherwise 409 (E10006) with the current status in the message. An order that has been paid is refunded through the payment API, it is not cancelled here.
- The order becomes `CANCELLED` and the quantity of every item is added back to its lot (`lot_id` of the item) even when that lot is no longer on sale. A lot that was DELETED or ARCHIVED still gets its quantity back because the lot is the stock history. The order and its items stay in the tables as history.
- The system applies the same rule when `expires_at` has passed and the order is still `WAIT_PAYMENT` (the system acts as the caller `system`, this is a scheduled job, not an API).
- The cancel is idempotent in outcome: cancelling an order that is already `CANCELLED` answers 409 (E10006), no quantity is added twice.
- Execution order: validate the request (400) -> existence and ownership checks (404) -> permission of a member of the shop (the owner skips it) -> status check (409) -> write the order and give the quantity back. The whole request is one transaction.

#### Example Body Parameters

```JSON
{
    "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/order/cancel HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/order/cancel' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01"
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

|     | Parameter Name | Data Type                                       | M/O       | Source           | Field              | Description                                      | Example                              |
| --- | -------------- | ----------------------------------------------- | --------- | ---------------- | ------------------ | ------------------------------------------------ | ------------------------------------ |
| 1   | orderId        | String: UUID                                    | MANDATORY | Sequence Diagram | data.orderId       | Cancelled Order Id                               | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 2   | code           | String                                          | MANDATORY | Sequence Diagram | data.code          | Order code                                       | ORD-20261106-000101                  |
| 3   | status         | String                                          | MANDATORY | Sequence Diagram | data.status        | Order status after the request, always CANCELLED | CANCELLED                            |
| 4   | restoredItems  | [Array of Restored Item](#restored-item-object) | MANDATORY | Sequence Diagram | data.restoredItems | Quantity that went back to the lots              |                                      |

#### Restored Item Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                            | Description                        | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | -------------------------------- | ---------------------------------- | ------------------------------------ |
| 1   | orderItemId    | String: UUID | MANDATORY | Sequence Diagram | data.restoredItems[].orderItemId | Order Item Id                      | e1f2a3b4-3c4d-4e5f-9a6b-7c8d9e0f1a21 |
| 2   | lotId          | String: UUID | MANDATORY | Sequence Diagram | data.restoredItems[].lotId       | Lot that got the quantity back     | aa11bb22-cc33-4d44-8e55-ff66aa77bb88 |
| 3   | quantity       | Numeric      | MANDATORY | Sequence Diagram | data.restoredItems[].quantity    | Quantity that was added to the lot | 2                                    |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Cancel Order Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
        "code": "ORD-20261106-000101",
        "status": "CANCELLED",
        "restoredItems": [
            {
                "orderItemId": "e1f2a3b4-3c4d-4e5f-9a6b-7c8d9e0f1a21",
                "lotId": "aa11bb22-cc33-4d44-8e55-ff66aa77bb88",
                "quantity": 2
            },
            {
                "orderItemId": "e2a3b4c5-4d5e-4f60-8b7c-8d9e0f1a2b32",
                "lotId": "bb22cc33-dd44-4e55-9f66-aa77bb88cc99",
                "quantity": 1
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
        "bizMessage": "Order Id is a required field and must be a valid UUID.",
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
        "bizMessage": "Order not found.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict Status

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "Only an order that is waiting for payment can be cancelled, The order is PAYMENT_CONFIRMED.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:42:54.123Z",
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

#### QUERY - Get the order

```SQL
SELECT
    o.id as order_id,
    o.code,
    o.user_id,
    o.shop_id,
    o.status
FROM sales.t_order o
WHERE o.id = '<sequence.orderId>'
AND o.row_status <> 'DELETED' -- an order of a user that is not the owner, a member of the shop or a platform administrator counts as not found
```

#### UPDATE - Cancel the order

```SQL
UPDATE sales.t_order
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    status = 'CANCELLED'
WHERE id = '<sequence.orderId>'
AND status = 'WAIT_PAYMENT' -- no row changed means the status changed in the meantime, answer 409 (E10006)
RETURNING id as order_id, code, status
```

### Table: [sales.t_order_item](../../../schema/sales/t_order_item.md)

#### QUERY - Get the items of the order

```SQL
SELECT
    oi.id as order_item_id,
    oi.lot_id,
    oi.quantity
FROM sales.t_order_item oi
WHERE oi.order_id = '<sequence.orderId>'
AND oi.row_status <> 'DELETED'
```

### Table: [shop.t_shop_product_sku_lot](../../../schema/shop/t_shop_product_sku_lot.md)

#### UPDATE - Give the quantity back to the lot

```SQL
UPDATE shop.t_shop_product_sku_lot
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    quantity = quantity + '<sequence.quantity>' -- the lot may be DELETED or ARCHIVED, it still gets the quantity back
WHERE id = '<sequence.lotId>'
RETURNING id as lot_id, quantity
```

### Table: [shop.t_shop_user](../../../schema/shop/t_shop_user.md)

#### QUERY - Check shop member

```SQL
SELECT
    su.shop_id
FROM shop.t_shop_user su
WHERE su.shop_id = '<sequence.shopId>'
AND su.user_id = '<sequence.userId>'
AND su.role IN ('ADMIN', 'STAFF')
AND su.row_status = 'ACTIVE'
```

### Table: [author.m_role](../../../schema/author/m_role.md)

#### QUERY - Get the platform administrator role

```SQL
SELECT
    r.id as role_id
FROM author.m_role r
WHERE r.name = 'PLATFORM_ADMIN'
AND r.row_status = 'ACTIVE'
```

### Table: [author.t_user_role](../../../schema/author/t_user_role.md)

#### QUERY - Check platform administrator

```SQL
SELECT
    ur.id as user_role_id
FROM author.t_user_role ur
WHERE ur.user_id = '<sequence.userId>'
AND ur.role_id = '<sequence.roleId>'
AND ur.row_status = 'ACTIVE'
```
