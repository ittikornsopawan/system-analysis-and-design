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
- The shipping becomes `DELIVERED` and `delivered_at` is set to the time of the request. `DELIVERED` is set by this API (the customer confirms) and by the automatic completion below (the system confirms after `completion_days`, `updated_by` is `system`), never by the shop.
- The order becomes `COMPLETED` when the order is `PROCESSING` and, for every item of the order that is not DELETED, the quantity in shippings with the status `DELIVERED` is equal to the quantity of the item (all goods were shipped and received). Otherwise the order stays `PROCESSING`. `orderStatus` in the response is the status after the request. `COMPLETED` is the status the shop review rule (`shop/15`) reads to know that the caller bought the product.
- When the customer never confirms, the order completes by itself `completion_days` (7) days after the parcels were shipped, see Automatic Completion Rules below. The order of a partial shipment that cannot be finished does not complete by itself.
- Execution order: validate the request (400) -> existence and ownership of the shipping (404) -> status of the shipping (409) -> write the shipping and, when needed, the order in one transaction. The shipping is first read without a lock only to find its order, then the order row is locked (`SELECT ... FOR UPDATE`) before any row of `shipping.*` or `sales.*` is changed, and the update of the shipping repeats the status `SHIPPED` in its `WHERE`.
- This behaviour follows `docs/superpowers/specs/2026-11-06-shipping-design.md`, approved by the product owner on 2026-11-06. The payment columns that the shipping APIs read (`payment.t_payment.shipping_method`) belong to the payment design of WP2 (`docs/superpowers/specs/2026-11-06-payment-design.md`).

### Automatic Completion Rules

- A job (a scheduled task of the system, not an endpoint, it has no `authorization` header and acts as the caller `system`, the same way as the job that cancels an order whose `expires_at` has passed) completes the orders whose receiver did not confirm. `completion_days` is 7 and is a config, the size of a batch and how often the job runs are configs too, nothing of them is stored in the tables.
- An order qualifies only when all five hold: (1) the order is `PROCESSING` and not DELETED, (2) no shipping of the order is `PENDING`, (3) at least one shipping of the order is `SHIPPED`, (4) every item of the order that is not DELETED has a quantity in shippings that are `SHIPPED` or `DELIVERED` equal to the quantity ordered (`CANCELLED` and `RETURNED` shippings do not count, the same count as the quantity rule of create shipping), (5) every shipping that is `SHIPPED` was shipped at least `completion_days` days ago (`shipped_at` of the newest of them is 7 days old or older, a shipping that is exactly 7 days old qualifies, the shippings that are already `DELIVERED` are not counted).
- The job finds the candidates without a lock: the orders that pass the conditions (1), (2), (4) and (5) above and have a `SHIPPED` shipping at least `completion_days` days old (this is also the condition (3)), at most one batch each time, in `order_id` order. The scan applies every condition and not only the age because an order that can never qualify (a partial shipment that cannot be finished, or a shipping that stays `PENDING`) keeps its old `SHIPPED` shipping for ever: with the age alone it would be a candidate in every run and, in `order_id` order, would fill the batch before an order with a larger id that does qualify, which then would never be selected (the job starves). The scan is only a filter, the conditions are checked again under the lock. The job then works on one order at a time, one transaction for each order: it locks the order row first (`SELECT ... FOR UPDATE`), checks the five conditions again under the lock and skips the order when it does not qualify any more, changes the `SHIPPED` shippings of the order to `DELIVERED` (`updated_by` = `system`, `delivered_at` = the time of the job, the update repeats the status `SHIPPED` in its `WHERE`), and completes the order with the same formula as the confirm API (every item delivered in full, the order is `PROCESSING`). A failure of one order does not stop the others and running the job again changes nothing that is already done.
- No new status and no new column: a shipping that the system confirmed is `DELIVERED` with `updated_by` = `system`, a shipping that the customer confirmed has the user in `updated_by`. The customer and the shop see `deliveredAt` as the time that the customer or the system confirmed the parcel. The budget of a campaign that the order took is not given back when the order completes.
- A partial shipment that cannot be finished (a quantity that is not in any `SHIPPED` or `DELIVERED` shipping, or a shipping that stays `PENDING`) never qualifies and the order stays `PROCESSING`, the shop has to ship the rest or the owner decides a later way to close it (decision S24 of the design).
- Clashes: the order row is locked first by the job, the confirm API, the update shipping status API and the payment APIs, and the one that locks later checks again. A refund needs the order `PAYMENT_CONFIRMED` and a qualifying order is `PROCESSING`, so they do not meet, and when S9 puts the order back to `PAYMENT_CONFIRMED` the job skips it. When the job wins against the customer, confirm answers 409 (E10006) because the shipping is already `DELIVERED`. When the job wins against the shop, a `RETURNED` request answers 409 (E10006) because `DELIVERED` is final, so the shop has to record a returned parcel before the seven days are over.
- This follows the appendix WP3b (S23 to S32) of `docs/superpowers/specs/2026-11-06-shipping-design.md`: the seven days were answered by the product owner and the details were decided by the lead SA on 2026-11-07 (the safe defaults, they can be changed later without a schema change).

### Automatic Completion Example

The job runs on day 10 with `completion_days` 7, so a `SHIPPED` shipping qualifies when it was shipped on day 3 or earlier. The order of every case has one item with the quantity 3. Only the orders with the result COMPLETES are selected by the scan query, the other orders (WAITS, NOT ELIGIBLE, NOT A CANDIDATE) never use a place of the batch, so a dead-end order like case 4 cannot block the orders after it.

| Case | Shippings (status, shipped day, quantity) | Result          | Reason                                                                                                              |
| ---- | ----------------------------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------- |
| 1    | A SHIPPED d1 q2; B SHIPPED d2 q1          | COMPLETES       | All 3 are allocated and the newest SHIPPED shipping is 8 days old: A and B become DELIVERED and the order COMPLETED |
| 2    | A SHIPPED d4 q3                           | WAITS           | The shipping is 6 days old, less than 7                                                                             |
| 3    | A SHIPPED d1 q2; B PENDING q1             | WAITS           | A shipping is still PENDING                                                                                         |
| 4    | A SHIPPED d1 q2                           | NOT ELIGIBLE    | Only 2 of 3 are allocated: the stuck partial shipment stays PROCESSING                                              |
| 5    | A DELIVERED d1 q2; B SHIPPED d2 q1        | COMPLETES       | All 3 are allocated and B is 8 days old: only B becomes DELIVERED, the order COMPLETED                              |
| 6    | A RETURNED d1 q2; B SHIPPED d2 q3         | COMPLETES       | The returned shipping does not count and B holds all 3: B becomes DELIVERED, the order COMPLETED                    |
| 7    | A DELIVERED d1 q3                         | NOT A CANDIDATE | No SHIPPED shipping: the confirm API already completed the order                                                    |

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

|     | Parameter Name | Data Type         | M/O       | Source           | Field            | Description                                                | Example                              |
| --- | -------------- | ----------------- | --------- | ---------------- | ---------------- | ---------------------------------------------------------- | ------------------------------------ |
| 1   | shippingId     | String: UUID      | MANDATORY | Sequence Diagram | data.shippingId  | Shipping Id                                                | f3c4d5e6-7f80-4b92-8cbd-2e3f4a5b6c73 |
| 2   | orderId        | String: UUID      | MANDATORY | Sequence Diagram | data.orderId     | Order Id                                                   | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 3   | orderCode      | String            | MANDATORY | Sequence Diagram | data.orderCode   | Order code                                                 | ORD-20261106-000101                  |
| 4   | orderStatus    | String            | MANDATORY | Sequence Diagram | data.orderStatus | Order status after the request (PROCESSING or COMPLETED)   | PROCESSING                           |
| 5   | status         | String            | MANDATORY | Sequence Diagram | data.status      | Shipping status after the request, always DELIVERED        | DELIVERED                            |
| 6   | deliveredAt    | String: TIMESTAMP | MANDATORY | Sequence Diagram | data.deliveredAt | Time the customer or the system confirmed the parcel (UTC) | 2026-11-07T14:20:00.123Z             |

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


#### QUERY - Get the orders with an old SHIPPED parcel

```SQL
SELECT
    o.id as order_id
FROM sales.t_order o
WHERE o.status = 'PROCESSING'
AND o.row_status <> 'DELETED'
AND EXISTS (
    SELECT 1
    FROM shipping.t_shipping s
    WHERE s.order_id = o.id
    AND s.status = 'SHIPPED'
    AND s.row_status <> 'DELETED'
    AND s.shipped_at <= NOW() AT TIME ZONE 'UTC' - INTERVAL '<sequence.completionDays> days' -- uses the index ix_t_shipping_shipped_at
) -- a SHIPPED shipping is old enough
AND NOT EXISTS (
    SELECT 1
    FROM shipping.t_shipping s
    WHERE s.order_id = o.id
    AND s.row_status <> 'DELETED'
    AND s.status = 'PENDING'
) -- no shipping is still being prepared
AND NOT EXISTS (
    SELECT 1
    FROM shipping.t_shipping s
    WHERE s.order_id = o.id
    AND s.row_status <> 'DELETED'
    AND s.status = 'SHIPPED'
    AND s.shipped_at > NOW() AT TIME ZONE 'UTC' - INTERVAL '<sequence.completionDays> days'
) -- no SHIPPED shipping is younger than completion_days days
AND NOT EXISTS (
    SELECT 1
    FROM sales.t_order_item oi
    WHERE oi.order_id = o.id
    AND oi.row_status <> 'DELETED'
    AND oi.quantity <> (
        SELECT COALESCE(SUM(si.quantity), 0)
        FROM shipping.t_shipping_item si
        INNER JOIN shipping.t_shipping s2
            ON s2.id = si.shipping_id
        WHERE si.order_item_id = oi.id
        AND si.row_status <> 'DELETED'
        AND s2.row_status <> 'DELETED'
        AND s2.status IN ('SHIPPED', 'DELIVERED')
    )
) -- every item is allocated in full, an order that can never qualify must not use a place of the batch
ORDER BY o.id
LIMIT <sequence.batchSize>
```

#### UPDATE - Confirm the delivery as the system

```SQL
UPDATE shipping.t_shipping
SET
    updated_by = 'system',
    updated_at = NOW() AT TIME ZONE 'UTC',
    status = 'DELIVERED',
    delivered_at = NOW() AT TIME ZONE 'UTC'
WHERE order_id = '<sequence.orderId>'
AND row_status <> 'DELETED'
AND status = 'SHIPPED' -- no row changed means the shippings changed in the meantime, skip the order
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

#### QUERY - Check that the order qualifies

```SQL
SELECT
    o.id as order_id
FROM sales.t_order o
WHERE o.id = '<sequence.orderId>'
AND o.status = 'PROCESSING'
AND o.row_status <> 'DELETED'
AND NOT EXISTS (
    SELECT 1
    FROM shipping.t_shipping s
    WHERE s.order_id = o.id
    AND s.row_status <> 'DELETED'
    AND s.status = 'PENDING'
) -- no shipping is still being prepared
AND EXISTS (
    SELECT 1
    FROM shipping.t_shipping s
    WHERE s.order_id = o.id
    AND s.row_status <> 'DELETED'
    AND s.status = 'SHIPPED'
) -- a shipping waits for the confirmation
AND NOT EXISTS (
    SELECT 1
    FROM shipping.t_shipping s
    WHERE s.order_id = o.id
    AND s.row_status <> 'DELETED'
    AND s.status = 'SHIPPED'
    AND s.shipped_at > NOW() AT TIME ZONE 'UTC' - INTERVAL '<sequence.completionDays> days'
) -- every SHIPPED shipping is at least completion_days days old
AND NOT EXISTS (
    SELECT 1
    FROM sales.t_order_item oi
    WHERE oi.order_id = o.id
    AND oi.row_status <> 'DELETED'
    AND oi.quantity <> (
        SELECT COALESCE(SUM(si.quantity), 0)
        FROM shipping.t_shipping_item si
        INNER JOIN shipping.t_shipping s2
            ON s2.id = si.shipping_id
        WHERE si.order_item_id = oi.id
        AND si.row_status <> 'DELETED'
        AND s2.row_status <> 'DELETED'
        AND s2.status IN ('SHIPPED', 'DELIVERED')
    )
) -- every item is allocated in full (CANCELLED and RETURNED shippings do not count)
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
