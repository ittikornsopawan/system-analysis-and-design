---
name: "Stripe Webhook API"
description: "Receive the events of Stripe about a payment. Read it when you implement, review or test POST v1/payment/webhook/stripe."
status: in-review
approved_by: null
approved_at: null
---

# [POST]: v1/payment/webhook/stripe

| Title       | Description                                                                                                                                                                                                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Stripe Webhook API                                                                                                                                                                                                                                                              |
| Method      | POST                                                                                                                                                                                                                                                                            |
| Endpoint    | v{version}/payment/webhook/stripe                                                                                                                                                                                                                                               |
| Version     | 1                                                                                                                                                                                                                                                                               |
| Description | Receive the events of Stripe about a payment, The result of a payment is taken only from here, The request is public and is protected by the Stripe signature, The system updates the payment and the order, The same event can arrive many times and the result stays the same |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- The endpoint is public (no `authorization` header and no user) and is protected by `stripe-signature`, verified against the **raw body**; a missing or wrong signature, a body that is not JSON or a timestamp more than 5 minutes away answers 400 (E10001) and nothing is changed. The system acts as the caller `system`.
- Any other valid event answers 200 with `action` = `IGNORED`, a 408 (E90001) or any other failure makes Stripe send the event again. Every event is applied by the state of the payment, so the same event twice gives the same result (idempotent) and a final payment never moves back.
- `payment_intent.succeeded` completes the payment and confirms the order; `payment_intent.payment_failed` fails the payment (the order stays `WAIT_PAYMENT`); `payment_intent.canceled` cancels it; `charge.refunded` refunds it and gives the stock and the campaign budget back. A late payment (the order is not waiting for payment any more) is refunded at Stripe (`LATE_PAYMENT_REFUNDED`).
- Every row the webhook writes has `system` in `created_by` or `updated_by` (approved by the product owner on 2026-11-08).
- The state table, the late payment, the refund and the budget details are in the sequence diagram.

---

## Request Parameters

### Header Parameters

|     | Parameter Name   | Data Type | M/O       | Description                                                         | Example                         |
| --- | ---------------- | --------- | --------- | ------------------------------------------------------------------- | ------------------------------- |
| 1   | content-type     | String    | MANDATORY | Content type of the request                                         | application/json                |
| 2   | stripe-signature | String    | MANDATORY | Signature of Stripe for the raw body (timestamp t and signature v1) | t=1793869200,v1=5257a869e7ec... |

### Body Parameters

|     | Parameter Name                         | Data Type | M/O       | Description                                                                                                                                              | Example                  |
| --- | -------------------------------------- | --------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------ |
| 1   | id                                     | String    | MANDATORY | Stripe event id                                                                                                                                          | evt_1QxHk3EXAMPLE0001    |
| 2   | type                                   | String    | MANDATORY | Stripe event type, handled: payment_intent.succeeded, payment_intent.processing, payment_intent.payment_failed, payment_intent.canceled, charge.refunded | payment_intent.succeeded |
| 3   | created                                | Numeric   | MANDATORY | Time of the event in epoch seconds (UTC)                                                                                                                 | 1793869950               |
| 4   | data.object.id                         | String    | MANDATORY | Id of the PaymentIntent, for charge.refunded the id of the charge                                                                                        | pi_3QxHk2EXAMPLE0001     |
| 5   | data.object.payment_intent             | String    | OPTIONAL  | Id of the PaymentIntent, only on charge.refunded                                                                                                         | pi_3QxHk2EXAMPLE0001     |
| 6   | data.object.latest_charge              | String    | OPTIONAL  | Id of the charge, on payment_intent.succeeded                                                                                                            | ch_3QxHk2EXAMPLE0001     |
| 7   | data.object.last_payment_error.code    | String    | OPTIONAL  | Failure code, on payment_intent.payment_failed                                                                                                           | card_declined            |
| 8   | data.object.last_payment_error.message | String    | OPTIONAL  | Failure message, on payment_intent.payment_failed                                                                                                        | Your card was declined.  |

#### Example Body Parameters

```JSON
{
    "id": "evt_1QxHk3EXAMPLE0001",
    "object": "event",
    "type": "payment_intent.succeeded",
    "created": 1793869950,
    "data": {
        "object": {
            "id": "pi_3QxHk2EXAMPLE0001",
            "object": "payment_intent",
            "status": "succeeded",
            "latest_charge": "ch_3QxHk2EXAMPLE0001",
            "amount": 65700,
            "currency": "thb",
            "metadata": {
                "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
                "paymentId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
            }
        }
    }
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/payment/webhook/stripe HTTP/1.1
Host: www.domain.com
content-type: application/json
stripe-signature: t=1793869200,v1=5257a869e7ec...

{
    "id": "evt_1QxHk3EXAMPLE0001",
    "object": "event",
    "type": "payment_intent.succeeded",
    "created": 1793869950,
    "data": {
        "object": {
            "id": "pi_3QxHk2EXAMPLE0001",
            "object": "payment_intent",
            "status": "succeeded",
            "latest_charge": "ch_3QxHk2EXAMPLE0001",
            "amount": 65700,
            "currency": "thb",
            "metadata": {
                "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
                "paymentId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
            }
        }
    }
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/payment/webhook/stripe' \
--header 'content-type: application/json' \
--header 'stripe-signature: t=1793869200,v1=5257a869e7ec...' \
--data-raw '{
    "id": "evt_1QxHk3EXAMPLE0001",
    "object": "event",
    "type": "payment_intent.succeeded",
    "created": 1793869950,
    "data": {
        "object": {
            "id": "pi_3QxHk2EXAMPLE0001",
            "object": "payment_intent",
            "status": "succeeded",
            "latest_charge": "ch_3QxHk2EXAMPLE0001",
            "amount": 65700,
            "currency": "thb",
            "metadata": {
                "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
                "paymentId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
            }
        }
    }
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

|     | Parameter Name | Data Type    | M/O       | Source           | Field          | Description                                                                                                                                     | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | eventId        | String       | MANDATORY | Sequence Diagram | data.eventId   | Stripe event id                                                                                                                                 | evt_1QxHk3EXAMPLE0001                |
| 2   | eventType      | String       | MANDATORY | Sequence Diagram | data.eventType | Stripe event type                                                                                                                               | payment_intent.succeeded             |
| 3   | action         | String       | MANDATORY | Sequence Diagram | data.action    | What the system did: PAYMENT_PROCESSING, PAYMENT_COMPLETED, PAYMENT_FAILED, PAYMENT_CANCELLED, PAYMENT_REFUNDED, LATE_PAYMENT_REFUNDED, IGNORED | PAYMENT_COMPLETED                    |
| 4   | paymentId      | String: UUID | OPTIONAL  | Sequence Diagram | data.paymentId | Payment Id, Null when the payment is not found                                                                                                  | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 5   | orderId        | String: UUID | OPTIONAL  | Sequence Diagram | data.orderId   | Order Id, Null when the payment is not found                                                                                                    | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Stripe Event Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "eventId": "evt_1QxHk3EXAMPLE0001",
        "eventType": "payment_intent.succeeded",
        "action": "PAYMENT_COMPLETED",
        "paymentId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
        "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01"
    }
}
```

#### Success - Ignored

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Stripe Event Success",
        "requestId": "req-9a7b3c5d-6e8f-4a0b-c2d4-5e6f7a8b9c0d",
        "timestamp": "2026-11-06T09:05:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "eventId": "evt_1QxHk4EXAMPLE0002",
        "eventType": "payment_intent.created",
        "action": "IGNORED",
        "paymentId": null,
        "orderId": null
    }
}
```

#### Success - Late Payment Refunded

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Stripe Event Success",
        "requestId": "req-9a7b3c5d-6e8f-4a0b-c2d4-5e6f7a8b9c1e",
        "timestamp": "2026-11-06T09:35:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "eventId": "evt_1QxHk5EXAMPLE0003",
        "eventType": "payment_intent.succeeded",
        "action": "LATE_PAYMENT_REFUNDED",
        "paymentId": "a2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
        "orderId": "d2f3a4b5-2c3d-4e4f-8a5b-6c7d8e9f0a12"
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
        "bizMessage": "The signature of the event is missing or does not match the body.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:40:40.123Z",
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

#### QUERY - Get the payment of the event

```SQL
SELECT
    p.id as payment_id,
    p.order_id,
    p.status,
    p.payment_method,
    p.amount
FROM payment.t_payment p
WHERE p.provider_payment_id = '<sequence.providerPaymentId>' -- the PaymentIntent id of the event, no row means the event is IGNORED
AND p.row_status = 'ACTIVE'
```

#### UPDATE - Mark the payment as completed

```SQL
UPDATE payment.t_payment
SET
    updated_by = 'system',
    updated_at = NOW() AT TIME ZONE 'UTC',
    status = 'COMPLETED',
    transaction_code = '<sequence.chargeId>',
    transaction_at = '<sequence.eventAt>', -- the time of the event in UTC
    payment_name = '<sequence.paymentName>'
WHERE id = '<sequence.paymentId>'
AND status IN ('PENDING', 'PROCESSING') -- another status means the event is IGNORED or a late payment
RETURNING id as payment_id, status
```

#### UPDATE - Mark the payment as processing

```SQL
UPDATE payment.t_payment
SET
    updated_by = 'system',
    updated_at = NOW() AT TIME ZONE 'UTC',
    status = 'PROCESSING'
WHERE id = '<sequence.paymentId>'
AND status = 'PENDING'
RETURNING id as payment_id, status
```

#### UPDATE - Mark the payment as failed

```SQL
UPDATE payment.t_payment
SET
    updated_by = 'system',
    updated_at = NOW() AT TIME ZONE 'UTC',
    status = 'FAILED',
    failure_code = '<sequence.failureCode>',
    failure_message = '<sequence.failureMessage>'
WHERE id = '<sequence.paymentId>'
AND status IN ('PENDING', 'PROCESSING')
RETURNING id as payment_id, status
```

#### UPDATE - Mark the payment as cancelled

```SQL
UPDATE payment.t_payment
SET
    updated_by = 'system',
    updated_at = NOW() AT TIME ZONE 'UTC',
    status = 'CANCELLED'
WHERE id = '<sequence.paymentId>'
AND status = 'PENDING'
RETURNING id as payment_id, status
```

#### UPDATE - Mark the payment as refunded

```SQL
UPDATE payment.t_payment
SET
    updated_by = 'system',
    updated_at = NOW() AT TIME ZONE 'UTC',
    status = 'REFUNDED',
    transaction_code = COALESCE(transaction_code, '<sequence.chargeId>'),
    transaction_at = COALESCE(transaction_at, '<sequence.eventAt>'),
    provider_refund_id = '<sequence.refundId>',
    refunded_at = NOW() AT TIME ZONE 'UTC',
    refund_reason = '<sequence.refundReason>' -- 'Late payment: the order is not waiting for payment' for a late payment
WHERE id = '<sequence.paymentId>'
AND status IN ('COMPLETED', 'FAILED', 'CANCELLED') -- COMPLETED for charge.refunded, FAILED and CANCELLED for a late payment
RETURNING id as payment_id, status
```

### Table: [sales.t_order](../../../schema/sales/t_order.md)

#### QUERY - Get the order of the payment and lock it

```SQL
SELECT
    o.id as order_id,
    o.status
FROM sales.t_order o
WHERE o.id = '<sequence.orderId>'
FOR UPDATE -- taken before any update of the payment
```

#### UPDATE - Confirm the order

```SQL
UPDATE sales.t_order
SET
    updated_by = 'system',
    updated_at = NOW() AT TIME ZONE 'UTC',
    status = 'PAYMENT_CONFIRMED'
WHERE id = '<sequence.orderId>'
AND status = 'WAIT_PAYMENT' -- no row changed means a late payment, the money is refunded
RETURNING id as order_id, status
```

#### UPDATE - Refund the order

```SQL
UPDATE sales.t_order
SET
    updated_by = 'system',
    updated_at = NOW() AT TIME ZONE 'UTC',
    status = 'REFUNDED'
WHERE id = '<sequence.orderId>'
AND status = 'PAYMENT_CONFIRMED' -- no row changed means the order has started to ship, only the payment changes
RETURNING id as order_id, status
```

### Table: [sales.t_order_item](../../../schema/sales/t_order_item.md)

#### QUERY - Get the items of the refunded order

```SQL
SELECT
    oi.id as order_item_id,
    oi.lot_id,
    oi.quantity
FROM sales.t_order_item oi
WHERE oi.order_id = '<sequence.orderId>'
AND oi.row_status <> 'DELETED'
ORDER BY oi.lot_id -- the lots are locked in id order, the same as the checkout
```

### Table: [shop.t_shop_product_sku_lot](../../../schema/shop/t_shop_product_sku_lot.md)

#### UPDATE - Give the quantity back to the lot

```SQL
UPDATE shop.t_shop_product_sku_lot
SET
    updated_by = 'system',
    updated_at = NOW() AT TIME ZONE 'UTC',
    quantity = quantity + '<sequence.quantity>' -- the lot may be DELETED or ARCHIVED, it still gets the quantity back
WHERE id = '<sequence.lotId>'
RETURNING id as lot_id, quantity
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
VALUES ('system', '<sequence.campaignBudgetId>', '<sequence.campaignId>', '<sequence.orderId>', 'RELEASE', '<sequence.reference>', '<sequence.usage>', '<sequence.remaining>')
RETURNING id as ledger_id
```

### Table: [campaign.m_campaign_budget](../../../schema/campaign/m_campaign_budget.md)

#### UPDATE - Give the budget back

```SQL
UPDATE campaign.m_campaign_budget
SET
    updated_by = 'system',
    updated_at = NOW() AT TIME ZONE 'UTC',
    remaining = remaining + '<sequence.usage>' -- the budget may be INACTIVE, LOCKED or ARCHIVED by now, it still gets the amount back
WHERE id = '<sequence.campaignBudgetId>'
RETURNING id as budget_id, remaining
```
