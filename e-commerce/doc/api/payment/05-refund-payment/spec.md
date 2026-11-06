# [POST]: v1/shop/payment/refund

| Title       | Description                                                                                                                                                                                                                                                                                                         |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Refund Payment API                                                                                                                                                                                                                                                                                                  |
| Method      | POST                                                                                                                                                                                                                                                                                                                |
| Endpoint    | v{version}/shop/payment/refund                                                                                                                                                                                                                                                                                      |
| Version     | 1                                                                                                                                                                                                                                                                                                                   |
| Description | Refund the whole payment of an order that is paid and has not started to ship, The shop members or a platform administrator refund through Stripe, The order becomes REFUNDED and the quantity of every item goes back to its lot, Part of a payment cannot be refunded and a shipped order cannot be refunded here |

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

|     | Parameter Name | Data Type    | M/O       | Description                               | Example                              |
| --- | -------------- | ------------ | --------- | ----------------------------------------- | ------------------------------------ |
| 1   | paymentId      | String: UUID | MANDATORY | Payment Id                                | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 2   | reason         | String       | MANDATORY | Reason of the refund (max 256 characters) | Out of stock                         |

### Refund Rules

- The caller must be an ACTIVE member of the shop of the order (a row of `shop.t_shop_user` with the role ADMIN or STAFF that is ACTIVE) or a platform administrator (a user that has the role `PLATFORM_ADMIN`), otherwise 403 (E10009). The customer cannot refund, the customer asks the shop. A payment that does not exist or is DELETED is not found (404, E10004).
- Only a payment with the status `COMPLETED` can be refunded and only when its order is `PAYMENT_CONFIRMED`, otherwise 409 (E10006) with the current statuses in the message. The first shipment of the order changes the order to `PROCESSING`, so after the shop has started to ship the order cannot be refunded here (a return process is not in this version). When the shop cancels every parcel or every parcel comes back, the shipping API gives the order back to `PAYMENT_CONFIRMED` (shipping design S9, approved by the product owner) and the order can be refunded here again.
- The refund is always the whole `amount` of the payment, shipping fee included. The system asks Stripe for the refund of the PaymentIntent with the `Idempotency-Key` header `refund-` + payment id, so pressing the button twice refunds once. If Stripe does not answer or refuses, nothing is written and the answer is 408 (E90001).
- The payment becomes `REFUNDED` with `provider_refund_id`, `refunded_at` and `refund_reason`, the order becomes `REFUNDED` and the quantity of every item is added back to its lot (`lot_id` of the item) even when that lot is no longer on sale, the same way as a cancel. The Stripe event `charge.refunded` that follows finds the payment already REFUNDED and changes nothing.
- The budget that the order took from a campaign goes back in the same transaction as the stock, when the payment is refunded (`docs/superpowers/specs/2026-11-06-campaign-design.md`, C7 and C9, approved by the product owner on 2026-11-06): every budget that has a ledger row `RESERVE` of the order and no `RELEASE` yet gets its `usage` back (`remaining` grows by that amount) and a ledger row `RELEASE` with the same `usage` is written. An order that took no budget changes nothing. The order of the locks is the order row, the lots by `id`, then the budgets by `id`.
- Execution order: validate the request (400) -> existence of the payment (404) -> permission (403) -> status check (409) -> refund at Stripe and write the payment, the order and the lots. The whole request is one transaction and the order row is locked (`FOR UPDATE`) before the payment is changed, the same lock order as the start payment, the webhook and the shipping APIs.

#### Example Body Parameters

```JSON
{
    "paymentId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "reason": "Out of stock"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/shop/payment/refund HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "paymentId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "reason": "Out of stock"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/shop/payment/refund' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "paymentId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "reason": "Out of stock"
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

|     | Parameter Name | Data Type                                       | M/O       | Source           | Field              | Description                                       | Example                              |
| --- | -------------- | ----------------------------------------------- | --------- | ---------------- | ------------------ | ------------------------------------------------- | ------------------------------------ |
| 1   | paymentId      | String: UUID                                    | MANDATORY | Sequence Diagram | data.paymentId     | Payment Id                                        | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 2   | orderId        | String: UUID                                    | MANDATORY | Sequence Diagram | data.orderId       | Order Id                                          | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 3   | orderStatus    | String                                          | MANDATORY | Sequence Diagram | data.orderStatus   | Order status after the request, always REFUNDED   | REFUNDED                             |
| 4   | status         | String                                          | MANDATORY | Sequence Diagram | data.status        | Payment status after the request, always REFUNDED | REFUNDED                             |
| 5   | amount         | Numeric                                         | MANDATORY | Sequence Diagram | data.amount        | Amount that was refunded                          | 657.00                               |
| 6   | currency       | String                                          | MANDATORY | Sequence Diagram | data.currency      | Currency code                                     | THB                                  |
| 7   | refundedAt     | String: TIMESTAMP                               | MANDATORY | Sequence Diagram | data.refundedAt    | Time of the refund (UTC)                          | 2026-11-06T10:05:00.000Z             |
| 8   | refundReason   | String                                          | MANDATORY | Sequence Diagram | data.refundReason  | Reason of the refund                              | Out of stock                         |
| 9   | restoredItems  | [Array of Restored Item](#restored-item-object) | MANDATORY | Sequence Diagram | data.restoredItems | Quantity that went back to the lots               |                                      |

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
        "bizMessage": "Refund Payment Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "paymentId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
        "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
        "orderStatus": "REFUNDED",
        "status": "REFUNDED",
        "amount": 657.0,
        "currency": "THB",
        "refundedAt": "2026-11-06T10:05:00.000Z",
        "refundReason": "Out of stock",
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
        "bizMessage": "Payment Id is a required field and must be a valid UUID, Reason is a required field and must not be longer than 256 characters.",
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
        "bizMessage": "You do not have permission to refund the payments of this shop.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
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
        "bizMessage": "Payment not found.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:42:54.123Z",
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
        "bizMessage": "Only a completed payment of an order that is PAYMENT_CONFIRMED can be refunded, The order is PROCESSING.",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:43:01.123Z",
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

### Table: [payment.t_payment](../../../schema/payment/t_payment.md)

#### QUERY - Get the payment

```SQL
SELECT
    p.id as payment_id,
    p.order_id,
    p.provider_payment_id,
    p.amount,
    p.status
FROM payment.t_payment p
WHERE p.id = '<sequence.paymentId>'
AND p.row_status <> 'DELETED'
```

#### UPDATE - Refund the payment

```SQL
UPDATE payment.t_payment
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    status = 'REFUNDED',
    provider_refund_id = '<sequence.refundId>', -- id of the refund that Stripe returned
    refunded_at = NOW() AT TIME ZONE 'UTC',
    refund_reason = '<sequence.reason>'
WHERE id = '<sequence.paymentId>'
AND status = 'COMPLETED' -- no row changed means the status changed in the meantime, answer 409 (E10006)
RETURNING id as payment_id, status, amount, currency, refunded_at
```

### Table: [sales.t_order](../../../schema/sales/t_order.md)

#### QUERY - Get the order of the payment and lock it

```SQL
SELECT
    o.id as order_id,
    o.shop_id,
    o.status
FROM sales.t_order o
WHERE o.id = '<sequence.orderId>'
AND o.row_status <> 'DELETED'
FOR UPDATE -- taken before the payment is changed, the shipping API locks the same row when it creates or cancels a shipment
```

#### UPDATE - Refund the order

```SQL
UPDATE sales.t_order
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    status = 'REFUNDED'
WHERE id = '<sequence.orderId>'
AND status = 'PAYMENT_CONFIRMED' -- no row changed means the order has started to ship, answer 409 (E10006)
RETURNING id as order_id, status
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

### Table: [campaign.m_campaign_budget_ledger](../../../schema/campaign/m_campaign_budget_ledger.md)

#### QUERY - Get the budget that the order took

```SQL
SELECT
    l.campaign_budget_id,
    l.campaign_id,
    l.usage,
    l.reference
FROM campaign.m_campaign_budget_ledger l
WHERE l.order_id = '<sequence.orderId>'
AND l.entry_type = 'RESERVE'
AND NOT EXISTS (
    SELECT 1
    FROM campaign.m_campaign_budget_ledger r
    WHERE r.order_id = l.order_id
    AND r.campaign_budget_id = l.campaign_budget_id
    AND r.entry_type = 'RELEASE'
) -- a budget that was already given back is skipped, so nothing goes back twice
ORDER BY l.campaign_budget_id
```

#### INSERT - Write the release in the ledger

```SQL
INSERT INTO campaign.m_campaign_budget_ledger (created_by, campaign_budget_id, campaign_id, order_id, entry_type, reference, usage, remaining)
VALUES ('<sequence.userId>', '<sequence.campaignBudgetId>', '<sequence.campaignId>', '<sequence.orderId>', 'RELEASE', '<sequence.reference>', '<sequence.usage>', '<sequence.remaining>')
RETURNING id as ledger_id
```

### Table: [campaign.m_campaign_budget](../../../schema/campaign/m_campaign_budget.md)

#### UPDATE - Give the budget back

```SQL
UPDATE campaign.m_campaign_budget
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    remaining = remaining + '<sequence.usage>' -- the budget may be INACTIVE, LOCKED or ARCHIVED by now, it still gets the amount back
WHERE id = '<sequence.campaignBudgetId>'
RETURNING id as budget_id, remaining
```
