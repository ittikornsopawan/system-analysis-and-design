# [POST]: v1/shop/shipping

| Title       | Description                                                                                                                                                                                                                                                                                                                      |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Create Shipping API                                                                                                                                                                                                                                                                                                              |
| Method      | POST                                                                                                                                                                                                                                                                                                                             |
| Endpoint    | v{version}/shop/shipping                                                                                                                                                                                                                                                                                                         |
| Version     | 1                                                                                                                                                                                                                                                                                                                                |
| Description | Create a shipping (one parcel) from the items of an order that is paid, The order can be shipped in several parcels, The shipping method comes from the payment of the order, The first shipping moves the order to PROCESSING, Only an ACTIVE member of the shop of the order or a platform administrator can create a shipping |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- The caller must be an ACTIVE member of the shop of the order (a row of `shop.t_shop_user` with the role ADMIN or STAFF that is ACTIVE) or a platform administrator (a user that has the role `PLATFORM_ADMIN`), otherwise 403 (E10009). This permission model was approved by the product owner.
- A shipping can only be created for an order that is `PAYMENT_CONFIRMED` or `PROCESSING` (a later parcel of an order that is already being shipped), otherwise 409 (E10006) with the current status in the message. This API only reads the status of the order, it knows nothing about the payment provider.
- An order can be shipped in several parcels. For every order item the quantity that is already in a shipping with the status `PENDING`, `SHIPPED` or `DELIVERED` counts as assigned (a `CANCELLED` or `RETURNED` parcel frees its quantity). `quantity` plus the assigned quantity must not be more than the quantity of the order item, otherwise 409 (E10006). The check runs while the order row is locked, so two requests at the same time cannot assign the same quantity twice.
- Every `orderItemId` must be an item of the order that is not DELETED, otherwise 404 (E10005) with the position, `items[1]: ...`. The same `orderItemId` twice in the request, an empty `items` list, more than 100 items or a quantity that is not a positive integer is 400 (E10001).
- The new shipping has the status `PENDING`. `shippingMethod` is not a field of the request: it is copied from the payment of the order that has the status `COMPLETED` (`payment.t_payment.shipping_method`, chosen by the customer when the payment started), so every parcel of the order uses the method the customer paid for. The carrier name and the tracking number are given later by the update status API.
- When the order is `PAYMENT_CONFIRMED` it becomes `PROCESSING` in the same transaction. The order row is the only row of the `sales` schema that this API changes (the columns `status`, `updated_by` and `updated_at`).
- The address of the parcel is not copied: the shop reads the shipping address that the order stored when it was created (`sales.t_order.ship_*`).
- This behaviour follows the shipping design, approved by the product owner on 2026-11-06. The payment columns that the shipping APIs read (`payment.t_payment.shipping_method`) belong to the payment design of WP2 (`docs/superpowers/specs/2026-11-06-payment-design.md`).

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

|     | Parameter Name | Data Type                         | M/O       | Description                                                                         | Example                              |
| --- | -------------- | --------------------------------- | --------- | ----------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | orderId        | String: UUID                      | MANDATORY | Order Id, the order must belong to the shop of the caller                           | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 2   | items          | [Array of Item](#item-parameters) | MANDATORY | Order items to put in this parcel, 1 to 100 items, the same order item at most once |                                      |

#### Item Parameters

|     | Parameter Name | Data Type    | M/O       | Description                                                                        | Example                              |
| --- | -------------- | ------------ | --------- | ---------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | orderItemId    | String: UUID | MANDATORY | Order Item Id of the order                                                         | e1f2a3b4-3c4d-4e5f-9a6b-7c8d9e0f1a21 |
| 2   | quantity       | Numeric      | MANDATORY | Quantity in this parcel, an integer from 1 up to the quantity that is left to ship | 2                                    |

#### Example Body Parameters

```JSON
{
    "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
    "items": [
        {
            "orderItemId": "e1f2a3b4-3c4d-4e5f-9a6b-7c8d9e0f1a21",
            "quantity": 2
        }
    ]
}
```

```JSON
{
    "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
    "items": [
        {
            "orderItemId": "e2a3b4c5-4d5e-4f60-8b7c-8d9e0f1a2b32",
            "quantity": 1
        }
    ]
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/shop/shipping HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
    "items": [
        {
            "orderItemId": "e1f2a3b4-3c4d-4e5f-9a6b-7c8d9e0f1a21",
            "quantity": 2
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/shop/shipping' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
    "items": [
        {
            "orderItemId": "e1f2a3b4-3c4d-4e5f-9a6b-7c8d9e0f1a21",
            "quantity": 2
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

|     | Parameter Name | Data Type                     | M/O       | Source           | Field               | Description                                                           | Example                              |
| --- | -------------- | ----------------------------- | --------- | ---------------- | ------------------- | --------------------------------------------------------------------- | ------------------------------------ |
| 1   | shippingId     | String: UUID                  | MANDATORY | Sequence Diagram | data.shippingId     | Created Shipping Id                                                   | f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51 |
| 2   | orderId        | String: UUID                  | MANDATORY | Sequence Diagram | data.orderId        | Order Id                                                              | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 3   | orderCode      | String                        | MANDATORY | Sequence Diagram | data.orderCode      | Order code                                                            | ORD-20261106-000101                  |
| 4   | orderStatus    | String                        | MANDATORY | Sequence Diagram | data.orderStatus    | Order status after the request, PROCESSING                            | PROCESSING                           |
| 5   | shippingMethod | String                        | MANDATORY | Sequence Diagram | data.shippingMethod | Shipping method copied from the payment (STANDARD, EXPRESS, SAME_DAY) | STANDARD                             |
| 6   | status         | String                        | MANDATORY | Sequence Diagram | data.status         | Shipping status, always PENDING                                       | PENDING                              |
| 7   | createdAt      | String: TIMESTAMP             | MANDATORY | Sequence Diagram | data.createdAt      | Time the shipping was created (UTC)                                   | 2026-11-06T09:05:00.123Z             |
| 8   | items          | [Array of Item](#item-object) | MANDATORY | Sequence Diagram | data.items          | Order items in the parcel                                             |                                      |

#### Item Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                    | Description            | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ------------------------ | ---------------------- | ------------------------------------ |
| 1   | orderItemId    | String: UUID | MANDATORY | Sequence Diagram | data.items[].orderItemId | Order Item Id          | e1f2a3b4-3c4d-4e5f-9a6b-7c8d9e0f1a21 |
| 2   | quantity       | Numeric      | MANDATORY | Sequence Diagram | data.items[].quantity    | Quantity in the parcel | 2                                    |

### Example Response Parameters

#### Success - First Shipping

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Create Shipping Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shippingId": "f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51",
        "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
        "orderCode": "ORD-20261106-000101",
        "orderStatus": "PROCESSING",
        "shippingMethod": "STANDARD",
        "status": "PENDING",
        "createdAt": "2026-11-06T09:05:00.123Z",
        "items": [
            {
                "orderItemId": "e1f2a3b4-3c4d-4e5f-9a6b-7c8d9e0f1a21",
                "quantity": 2
            }
        ]
    }
}
```

#### Success - Second Shipping

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Create Shipping Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shippingId": "f2b3c4d5-6e7f-4a81-9bac-1d2e3f4a5b62",
        "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
        "orderCode": "ORD-20261106-000101",
        "orderStatus": "PROCESSING",
        "shippingMethod": "STANDARD",
        "status": "PENDING",
        "createdAt": "2026-11-06T09:10:00.123Z",
        "items": [
            {
                "orderItemId": "e2a3b4c5-4d5e-4f60-8b7c-8d9e0f1a2b32",
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

#### Fail - Forbidden

```JSON
{
    "status": {
        "code": 403,
        "message": "Forbidden",
        "bizCode": "E10009",
        "bizMessage": "Only a member of the shop of the order or a platform administrator can create a shipping.",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:43:01.123Z",
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

#### Fail - Not Found Reference

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "items[0]: Order item not found in the order.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:42:54.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict Order Status

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "A shipping can only be created for an order that is PAYMENT_CONFIRMED or PROCESSING, The order is WAIT_PAYMENT.",
        "requestId": "req-440a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:44:08.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict Quantity

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "items[0]: Quantity 3 is more than the quantity left to ship (2).",
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

### Table: [sales.t_order](../../../schema/sales/t_order.md)

#### QUERY - Lock the order

```SQL
SELECT
    o.id as order_id,
    o.code,
    o.shop_id,
    o.user_id,
    o.status
FROM sales.t_order o
WHERE o.id = '<sequence.orderId>'
AND o.row_status <> 'DELETED'
FOR UPDATE -- the order row is locked first in every write of the shipping and payment APIs, so they never wait for each other in a circle
```

#### UPDATE - Start processing

```SQL
UPDATE sales.t_order
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    status = 'PROCESSING'
WHERE id = '<sequence.orderId>'
AND status = 'PAYMENT_CONFIRMED' -- the first shipping of the order, an order that is already PROCESSING is not changed
RETURNING id as order_id, status
```

### Table: [sales.t_order_item](../../../schema/sales/t_order_item.md)

#### QUERY - Get the order items of the request

```SQL
SELECT
    oi.id as order_item_id,
    oi.quantity
FROM sales.t_order_item oi
WHERE oi.order_id = '<sequence.orderId>'
AND oi.id IN ('<sequence.orderItemIds>')
AND oi.row_status <> 'DELETED' -- an id that is missing from the result is answered 404 (E10005)
```

### Table: [payment.t_payment](../../../schema/payment/t_payment.md)

#### QUERY - Get the shipping method of the order

```SQL
SELECT
    p.shipping_method
FROM payment.t_payment p
WHERE p.order_id = '<sequence.orderId>'
AND p.status = 'COMPLETED' -- an order has at most one COMPLETED payment
AND p.row_status <> 'DELETED'
```

### Table: [shipping.t_shipping_item](../../../schema/shipping/t_shipping_item.md)

#### QUERY - Get the quantity already assigned

```SQL
SELECT
    si.order_item_id,
    COALESCE(SUM(si.quantity), 0) as assigned_quantity
FROM shipping.t_shipping_item si
INNER JOIN shipping.t_shipping s
    ON s.id = si.shipping_id
WHERE si.order_item_id IN ('<sequence.orderItemIds>')
AND si.row_status <> 'DELETED'
AND s.row_status <> 'DELETED'
AND s.status IN ('PENDING', 'SHIPPED', 'DELIVERED') -- a CANCELLED or RETURNED parcel frees its quantity
GROUP BY si.order_item_id
```

#### INSERT - Add the items to the shipping

```SQL
INSERT INTO shipping.t_shipping_item (created_by, shipping_id, order_item_id, quantity)
VALUES ('<sequence.userId>', '<sequence.shippingId>', '<sequence.orderItemId>', '<sequence.quantity>') -- one row per item of the request
RETURNING id as shipping_item_id, order_item_id, quantity
```

### Table: [shipping.t_shipping](../../../schema/shipping/t_shipping.md)

#### INSERT - Create the shipping

```SQL
INSERT INTO shipping.t_shipping (created_by, order_id, shipping_method, status)
VALUES ('<sequence.userId>', '<sequence.orderId>', '<sequence.shippingMethod>', 'PENDING')
RETURNING id as shipping_id, order_id, shipping_method, status, created_at
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
