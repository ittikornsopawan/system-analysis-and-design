# [POST]: v1/payment

| Title       | Description                                                                                                                                                                                                                                                                                                                                                                       |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Start Payment API                                                                                                                                                                                                                                                                                                                                                                 |
| Method      | POST                                                                                                                                                                                                                                                                                                                                                                              |
| Endpoint    | v{version}/payment                                                                                                                                                                                                                                                                                                                                                                |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                                 |
| Description | Start the payment of an order that is waiting for payment through Stripe, The customer chooses the payment method and the shipping method, The system calculates the shipping fee and the amount, sets them on the order and creates the Stripe PaymentIntent, The result carries the client secret for Stripe.js, The payment becomes final only when the Stripe webhook says so |

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

|     | Parameter Name | Data Type    | M/O       | Description                                                        | Example                              |
| --- | -------------- | ------------ | --------- | ------------------------------------------------------------------ | ------------------------------------ |
| 1   | orderId        | String: UUID | MANDATORY | Order Id, Must be an order of the user that is waiting for payment | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 2   | paymentMethod  | String       | MANDATORY | Payment method, one of: CREDIT_CARD, THAI_QR                       | CREDIT_CARD                          |
| 3   | shippingMethod | String       | MANDATORY | Shipping method, one of: STANDARD, EXPRESS, SAME_DAY               | STANDARD                             |

### Payment Rules

- Only the owner of the order (the user of the access token, the request never carries a user id) can pay it. The order of another user, a missing order and an order that is DELETED all answer 404 (E10004).
- The order must be `WAIT_PAYMENT` and `expires_at` must not have passed, otherwise 409 (E10006) with the current status in the message. The order keeps holding the stock while the payment is in progress.
- `paymentMethod` accepts only `CREDIT_CARD` (Stripe card) and `THAI_QR` (Stripe PromptPay). `PAYPAL`, `BANK_TRANSFER` and `CASH_ON_DELIVERY` exist in the table but are not supported yet, they answer 400 (E10001) with the message `Payment method is not supported.` The provider is always `STRIPE`.
- The shipping fee is calculated by the system from `shippingMethod`, the client never sends an amount or a fee. The fee is a flat rate for each order taken from a config (not from the database schema), the values in this spec are STANDARD 40.00, EXPRESS 80.00 and SAME_DAY 150.00 baht, free shipping does not exist yet.
- `amount = totalPrice - totalDiscount + totalTax + shippingFee` (the same formula that the database enforces on the order, `ck_t_order_total_amount_sum`). The system sets `total_shipping` and `total_amount` of the order to the new values in the same transaction, the currency is always THB, and the amount that goes to Stripe is `amount x 100` in satang.
- The amount must be at least 10.00 baht (the Stripe minimum for THB) and, for `THAI_QR`, at most 2,000,000.00 baht, otherwise 409 (E10006) with the limit in the message. Both limits are configs.
- At most one payment of an order is live (PENDING, PROCESSING or COMPLETED, enforced by `uq_t_payment_order_id_live`). When the order already has a live payment: a PENDING payment with the same `paymentMethod` and the same `shippingMethod` is reused, the answer is 200 with a new client secret that the system reads from Stripe and no row is written; a PENDING payment with a different method is cancelled (at Stripe and in the table, status CANCELLED) and a new payment is created (201); a PROCESSING payment answers 409 (E10006) with the message `A payment of the order is in progress.`
- A payment that is FAILED or CANCELLED is history, starting again creates a new row. One row is one Stripe PaymentIntent, it is created with the `Idempotency-Key` header set to the id of the new payment row so a retry never creates two PaymentIntents. The metadata of the PaymentIntent carries `orderId` and `paymentId`.
- The client secret is returned only here and is never stored. The result of the payment is read from the Stripe webhook (`02-stripe-webhook`), not from the browser. Card data never reaches this API, Stripe.js sends it to Stripe.
- If Stripe does not answer or refuses the request nothing is written (the whole request is one transaction) and the answer is 408 (E90001).
- Execution order: validate the request (400) -> existence and ownership of the order (404) -> status, expiry, live payment and amount limits (409) -> create the PaymentIntent and write the order and the payment. The whole request is one transaction and the order row is locked (`FOR UPDATE`) so two requests cannot start two payments.

#### Example Body Parameters

```JSON
{
    "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
    "paymentMethod": "CREDIT_CARD",
    "shippingMethod": "STANDARD"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/payment HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
    "paymentMethod": "CREDIT_CARD",
    "shippingMethod": "STANDARD"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/payment' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
    "paymentMethod": "CREDIT_CARD",
    "shippingMethod": "STANDARD"
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

|     | Parameter Name | Data Type         | M/O       | Source           | Field               | Description                                                           | Example                              |
| --- | -------------- | ----------------- | --------- | ---------------- | ------------------- | --------------------------------------------------------------------- | ------------------------------------ |
| 1   | paymentId      | String: UUID      | MANDATORY | Sequence Diagram | data.paymentId      | Payment Id                                                            | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 2   | orderId        | String: UUID      | MANDATORY | Sequence Diagram | data.orderId        | Order Id                                                              | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 3   | orderCode      | String            | MANDATORY | Sequence Diagram | data.orderCode      | Order code                                                            | ORD-20261106-000101                  |
| 4   | status         | String            | MANDATORY | Sequence Diagram | data.status         | Payment status, PENDING for a new payment                             | PENDING                              |
| 5   | paymentMethod  | String            | MANDATORY | Sequence Diagram | data.paymentMethod  | Payment method                                                        | CREDIT_CARD                          |
| 6   | shippingMethod | String            | MANDATORY | Sequence Diagram | data.shippingMethod | Shipping method                                                       | STANDARD                             |
| 7   | shippingFee    | Numeric           | MANDATORY | Sequence Diagram | data.shippingFee    | Shipping fee calculated by the system                                 | 40.00                                |
| 8   | totalPrice     | Numeric           | MANDATORY | Sequence Diagram | data.totalPrice     | Order total price                                                     | 617.00                               |
| 9   | totalDiscount  | Numeric           | MANDATORY | Sequence Diagram | data.totalDiscount  | Order discount                                                        | 0.00                                 |
| 10  | totalTax       | Numeric           | MANDATORY | Sequence Diagram | data.totalTax       | Order tax                                                             | 0.00                                 |
| 11  | totalShipping  | Numeric           | MANDATORY | Sequence Diagram | data.totalShipping  | Order shipping fee, equals shippingFee                                | 40.00                                |
| 12  | totalAmount    | Numeric           | MANDATORY | Sequence Diagram | data.totalAmount    | Order total amount after the shipping fee                             | 657.00                               |
| 13  | amount         | Numeric           | MANDATORY | Sequence Diagram | data.amount         | Amount of the payment, equals totalAmount                             | 657.00                               |
| 14  | currency       | String            | MANDATORY | Sequence Diagram | data.currency       | Currency code                                                         | THB                                  |
| 15  | clientSecret   | String            | MANDATORY | Sequence Diagram | data.clientSecret   | Client secret of the Stripe PaymentIntent for Stripe.js, Never stored | pi_3QxHk2EXAMPLE0001_secret_EXAMPLE  |
| 16  | orderExpiresAt | String: TIMESTAMP | MANDATORY | Sequence Diagram | data.orderExpiresAt | The order holds the stock until this time (UTC)                       | 2026-11-06T09:30:00.123Z             |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Start Payment Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "paymentId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
        "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
        "orderCode": "ORD-20261106-000101",
        "status": "PENDING",
        "paymentMethod": "CREDIT_CARD",
        "shippingMethod": "STANDARD",
        "shippingFee": 40.0,
        "totalPrice": 617.0,
        "totalDiscount": 0.0,
        "totalTax": 0.0,
        "totalShipping": 40.0,
        "totalAmount": 657.0,
        "amount": 657.0,
        "currency": "THB",
        "clientSecret": "pi_3QxHk2EXAMPLE0001_secret_EXAMPLE",
        "orderExpiresAt": "2026-11-06T09:30:00.123Z"
    }
}
```

#### Success - Reused

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Start Payment Success",
        "requestId": "req-9a7b3c5d-6e8f-4a0b-c2d4-5e6f7a8b9c0d",
        "timestamp": "2026-11-06T09:05:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "paymentId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
        "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
        "orderCode": "ORD-20261106-000101",
        "status": "PENDING",
        "paymentMethod": "CREDIT_CARD",
        "shippingMethod": "STANDARD",
        "shippingFee": 40.0,
        "totalPrice": 617.0,
        "totalDiscount": 0.0,
        "totalTax": 0.0,
        "totalShipping": 40.0,
        "totalAmount": 657.0,
        "amount": 657.0,
        "currency": "THB",
        "clientSecret": "pi_3QxHk2EXAMPLE0001_secret_EXAMPLE",
        "orderExpiresAt": "2026-11-06T09:30:00.123Z"
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
        "bizMessage": "Order Id is a required field and must be a valid UUID, Payment method must be CREDIT_CARD or THAI_QR, Shipping method must be STANDARD, EXPRESS or SAME_DAY.",
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
        "bizMessage": "Only an order that is waiting for payment can be paid, The order is CANCELLED.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:42:54.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict Payment In Progress

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "A payment of the order is in progress.",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:43:01.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict Amount Limit

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "The amount must be at least 10.00 THB.",
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

### Table: [sales.t_order](../../../schema/sales/t_order.md)

#### QUERY - Get the order of the user and lock it

```SQL
SELECT
    o.id as order_id,
    o.code,
    o.status,
    o.total_price,
    o.total_discount,
    o.total_tax,
    o.expires_at
FROM sales.t_order o
WHERE o.id = '<sequence.orderId>'
AND o.user_id = '<sequence.userId>' -- an order of another user counts as not found
AND o.row_status <> 'DELETED'
FOR UPDATE
```

#### UPDATE - Set the shipping fee and the amount of the order

```SQL
UPDATE sales.t_order
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    total_shipping = '<sequence.shippingFee>',
    total_amount = total_price - total_discount + total_tax + '<sequence.shippingFee>'
WHERE id = '<sequence.orderId>'
AND status = 'WAIT_PAYMENT' -- no row changed means the status changed in the meantime, answer 409 (E10006)
RETURNING id as order_id, total_shipping, total_amount
```

### Table: [payment.t_payment](../../../schema/payment/t_payment.md)

#### QUERY - Get the live payment of the order

```SQL
SELECT
    p.id as payment_id,
    p.provider_payment_id,
    p.status,
    p.payment_method,
    p.shipping_method
FROM payment.t_payment p
WHERE p.order_id = '<sequence.orderId>'
AND p.status IN ('PENDING', 'PROCESSING')
AND p.row_status = 'ACTIVE' -- PROCESSING answers 409 (E10006), the same methods are reused without a write
```

#### UPDATE - Cancel the pending payment that is replaced

```SQL
UPDATE payment.t_payment
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    status = 'CANCELLED'
WHERE id = '<sequence.paymentId>'
AND status = 'PENDING' -- no row changed means the payment moved on in the meantime, answer 409 (E10006)
RETURNING id as payment_id, status
```

#### INSERT - Create the payment

```SQL
INSERT INTO payment.t_payment (
    id,
    created_by,
    order_id,
    provider,
    provider_payment_id,
    amount,
    currency,
    shipping_method,
    shipping_fee,
    status,
    payment_method
)
VALUES (
    '<sequence.paymentId>', -- generated before the PaymentIntent is created, it is the Idempotency-Key
    '<sequence.userId>',
    '<sequence.orderId>',
    'STRIPE',
    '<sequence.providerPaymentId>', -- id of the PaymentIntent that Stripe returned
    '<sequence.amount>',
    'THB',
    '<sequence.shippingMethod>',
    '<sequence.shippingFee>',
    'PENDING',
    '<sequence.paymentMethod>'
)
RETURNING id as payment_id, status
```
