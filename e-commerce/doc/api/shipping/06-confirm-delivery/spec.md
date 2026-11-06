# [POST]: v1/shipping/confirm

| Title       | Description                                                                                                                                                                            |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Confirm Delivery API                                                                                                                                                                   |
| Method      | POST                                                                                                                                                                                   |
| Endpoint    | v{version}/shipping/confirm                                                                                                                                                            |
| Version     | 1                                                                                                                                                                                      |
| Description | The receiver confirms that a parcel arrived, The shipping becomes DELIVERED, The order becomes COMPLETED when every item is delivered in full, Only the owner of the order can confirm |

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

|     | Parameter Name | Data Type    | M/O       | Description                                                     | Example                              |
| --- | -------------- | ------------ | --------- | --------------------------------------------------------------- | ------------------------------------ |
| 1   | shippingId     | String: UUID | MANDATORY | Shipping Id, the shipping must belong to an order of the caller | f3c4d5e6-7f80-4b92-8cbd-2e3f4a5b6c73 |

### Confirm Delivery Rules

- Only the owner of the order (the user of the access token) can confirm. A shipping of another user's order counts as not found (404, E10004), the same answer as a shipping that does not exist. Members of the shop and platform administrators cannot confirm on behalf of the customer, because the confirmation is the act of the receiver.
- Only a shipping with the status `SHIPPED` can be confirmed, otherwise 409 (E10006) with the current status in the message. A shipping that is already `DELIVERED` answers 409 too, nothing is changed twice.
- The shipping becomes `DELIVERED` and `delivered_at` is set to the time of the request. `DELIVERED` can be set only by this API.
- The order becomes `COMPLETED` when the order is `PROCESSING` and, for every item of the order that is not DELETED, the quantity in shippings with the status `DELIVERED` is equal to the quantity of the item (all goods were shipped and received). Otherwise the order stays `PROCESSING`. `orderStatus` in the response is the status after the request. `COMPLETED` is the status the shop review rule (`shop/15`) reads to know that the caller bought the product.
- There is no automatic completion: an order whose receiver never confirms stays `PROCESSING` (open question of the design, no job is specified).
- Execution order: validate the request (400) -> existence and ownership of the shipping (404) -> status of the shipping (409) -> write the shipping and, when needed, the order in one transaction. The shipping is first read without a lock only to find its order, then the order row is locked (`SELECT ... FOR UPDATE`) before any row of `shipping.*` or `sales.*` is changed, and the update of the shipping repeats the status `SHIPPED` in its `WHERE`.
- This behaviour follows `docs/superpowers/specs/2026-11-06-shipping-design.md`, approved by the product owner on 2026-11-06. The payment columns that the shipping APIs read (`payment.t_payment.shipping_method`) belong to the payment design of WP2 (`docs/superpowers/specs/2026-11-06-payment-design.md`).

#### Example Body Parameters

```JSON
{
    "shippingId": "f3c4d5e6-7f80-4b92-8cbd-2e3f4a5b6c73"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/shipping/confirm HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "shippingId": "f3c4d5e6-7f80-4b92-8cbd-2e3f4a5b6c73"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/shipping/confirm' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "shippingId": "f3c4d5e6-7f80-4b92-8cbd-2e3f4a5b6c73"
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

|     | Parameter Name | Data Type         | M/O       | Source           | Field            | Description                                              | Example                              |
| --- | -------------- | ----------------- | --------- | ---------------- | ---------------- | -------------------------------------------------------- | ------------------------------------ |
| 1   | shippingId     | String: UUID      | MANDATORY | Sequence Diagram | data.shippingId  | Shipping Id                                              | f3c4d5e6-7f80-4b92-8cbd-2e3f4a5b6c73 |
| 2   | orderId        | String: UUID      | MANDATORY | Sequence Diagram | data.orderId     | Order Id                                                 | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 3   | orderCode      | String            | MANDATORY | Sequence Diagram | data.orderCode   | Order code                                               | ORD-20261106-000101                  |
| 4   | orderStatus    | String            | MANDATORY | Sequence Diagram | data.orderStatus | Order status after the request (PROCESSING or COMPLETED) | PROCESSING                           |
| 5   | status         | String            | MANDATORY | Sequence Diagram | data.status      | Shipping status after the request, always DELIVERED      | DELIVERED                            |
| 6   | deliveredAt    | String: TIMESTAMP | MANDATORY | Sequence Diagram | data.deliveredAt | Time the receiver confirmed the parcel (UTC)             | 2026-11-07T14:20:00.123Z             |

### Example Response Parameters

#### Success - Order Still Processing

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Confirm Delivery Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shippingId": "f3c4d5e6-7f80-4b92-8cbd-2e3f4a5b6c73",
        "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
        "orderCode": "ORD-20261106-000101",
        "orderStatus": "PROCESSING",
        "status": "DELIVERED",
        "deliveredAt": "2026-11-07T14:20:00.123Z"
    }
}
```

#### Success - Order Completed

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Confirm Delivery Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shippingId": "f4d5e6f7-8091-4ca3-9dce-3f4a5b6c7d84",
        "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
        "orderCode": "ORD-20261106-000101",
        "orderStatus": "COMPLETED",
        "status": "DELIVERED",
        "deliveredAt": "2026-11-08T10:05:00.123Z"
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
        "bizMessage": "Shipping Id is a required field and must be a valid UUID.",
        "requestId": "req-900a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:40:30.123Z",
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
        "bizMessage": "Shipping not found.",
        "requestId": "req-910a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:37.123Z",
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
        "bizMessage": "Only a shipping that is SHIPPED can be confirmed, The shipping is PENDING.",
        "requestId": "req-920a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:42:44.123Z",
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

### Table: [shipping.t_shipping](../../../schema/shipping/t_shipping.md)

#### QUERY - Get the shipping of the user

```SQL
SELECT
    s.id as shipping_id,
    s.order_id,
    s.status
FROM shipping.t_shipping s
INNER JOIN sales.t_order o
    ON o.id = s.order_id
WHERE s.id = '<sequence.shippingId>'
AND o.user_id = '<sequence.userId>'
AND s.row_status <> 'DELETED' -- a shipping of another user counts as not found
```

#### UPDATE - Confirm the delivery

```SQL
UPDATE shipping.t_shipping
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    status = 'DELIVERED',
    delivered_at = NOW() AT TIME ZONE 'UTC'
WHERE id = '<sequence.shippingId>'
AND status = 'SHIPPED' -- no row changed means the status changed in the meantime, answer 409 (E10006)
RETURNING id as shipping_id, status, delivered_at
```

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

#### UPDATE - Complete the order

```SQL
UPDATE sales.t_order
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    status = 'COMPLETED'
WHERE id = '<sequence.orderId>'
AND status = 'PROCESSING' -- only when every item is delivered in full
RETURNING id as order_id, status
```

### Table: [sales.t_order_item](../../../schema/sales/t_order_item.md)

#### QUERY - Get the delivered quantity of every item

```SQL
SELECT
    oi.id as order_item_id,
    oi.quantity as ordered_quantity,
    COALESCE(SUM(si.quantity), 0) as delivered_quantity -- the order is complete when every row has delivered_quantity = ordered_quantity
FROM sales.t_order_item oi
LEFT JOIN shipping.t_shipping_item si
    ON si.order_item_id = oi.id
    AND si.row_status <> 'DELETED'
    AND si.shipping_id IN (
        SELECT s.id
        FROM shipping.t_shipping s
        WHERE s.order_id = '<sequence.orderId>'
        AND s.row_status <> 'DELETED'
        AND s.status = 'DELIVERED'
    )
WHERE oi.order_id = '<sequence.orderId>'
AND oi.row_status <> 'DELETED'
GROUP BY oi.id, oi.quantity
```
