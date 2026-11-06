# [GET]: v1/payment

| Title       | Description                                                                                                                                                                                            |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Name        | Inquiry Payment API                                                                                                                                                                                    |
| Method      | GET                                                                                                                                                                                                    |
| Endpoint    | v{version}/payment                                                                                                                                                                                     |
| Version     | 1                                                                                                                                                                                                      |
| Description | Inquiry the payments of the logged-in customer, newest first, Filter by id, order, status or order code, The customer sees the status, the amount and the reason of a failure, never the ids of Stripe |

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
| 1   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-06T09:00:00.123Z                       |
| 3   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Query Parameters

|     | Parameter Name | Data Type    | M/O      | Description                                                                                                          | Example                              |
| --- | -------------- | ------------ | -------- | -------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL | Payment Id, Response is a list with one item                                                                         | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 2   | orderId        | String: UUID | OPTIONAL | Order Id filter                                                                                                      | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 3   | status         | String       | OPTIONAL | Payment status filter (PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED, REFUNDED), All statuses when not specified | FAILED                               |
| 4   | pageIndex      | Numeric      | OPTIONAL | Page index starting from 1, Defaults to 1                                                                            | 1                                    |
| 5   | pageSize       | Numeric      | OPTIONAL | Number of items per page (max 100), Defaults to 10                                                                   | 10                                   |
| 6   | search         | String       | OPTIONAL | Search by order code                                                                                                 | ORD-2026                             |

### Payment Inquiry Rules

- Only the payments of the orders of the user of the access token are returned (the request never carries a user id), the payment of another user is not found, `id` of another user answers an empty list. Payments with `rowStatus` DELETED are never returned.
- The payments are ordered by creation time (newest first) then `id`.
- The customer never receives `providerPaymentId`, `providerRefundId`, `transactionCode` or `clientSecret`. `failureCode` and `failureMessage` are filled only when the status is FAILED, `refundedAt` and `refundReason` only when it is REFUNDED, `transactionAt` only when it is COMPLETED or REFUNDED.

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/payment?orderId=d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01&status=FAILED&pageIndex=1&pageSize=10 HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/payment?orderId=d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01&status=FAILED&pageIndex=1&pageSize=10' \
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

|     | Parameter Name | Data Type                           | M/O       | Source           | Field           | Description              | Example |
| --- | -------------- | ----------------------------------- | --------- | ---------------- | --------------- | ------------------------ | ------- |
| 1   | payments       | [Array of Payment](#payment-object) | MANDATORY | Sequence Diagram | data.payments   | Payments of the page     |         |
| 2   | pageIndex      | Numeric                             | MANDATORY | Sequence Diagram | data.pageIndex  | Current page index       | 1       |
| 3   | pageSize       | Numeric                             | MANDATORY | Sequence Diagram | data.pageSize   | Number of items per page | 10      |
| 4   | totalItems     | Numeric                             | MANDATORY | Sequence Diagram | data.totalItems | Total number of payments | 2       |
| 5   | totalPages     | Numeric                             | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages    | 1       |

#### Payment Object

|     | Parameter Name | Data Type         | M/O       | Source           | Field                          | Description                                                  | Example                              |
| --- | -------------- | ----------------- | --------- | ---------------- | ------------------------------ | ------------------------------------------------------------ | ------------------------------------ |
| 1   | paymentId      | String: UUID      | MANDATORY | Sequence Diagram | data.payments[].paymentId      | Payment Id                                                   | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 2   | orderId        | String: UUID      | MANDATORY | Sequence Diagram | data.payments[].orderId        | Order Id                                                     | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 3   | orderCode      | String            | MANDATORY | Sequence Diagram | data.payments[].orderCode      | Order code                                                   | ORD-20261106-000101                  |
| 4   | status         | String            | MANDATORY | Sequence Diagram | data.payments[].status         | Payment status                                               | COMPLETED                            |
| 5   | paymentMethod  | String            | MANDATORY | Sequence Diagram | data.payments[].paymentMethod  | Payment method                                               | CREDIT_CARD                          |
| 6   | paymentName    | String            | OPTIONAL  | Sequence Diagram | data.payments[].paymentName    | Display label of the payment, Null until the payment is paid | Visa 4242                            |
| 7   | amount         | Numeric           | MANDATORY | Sequence Diagram | data.payments[].amount         | Amount of the payment                                        | 657.00                               |
| 8   | currency       | String            | MANDATORY | Sequence Diagram | data.payments[].currency       | Currency code                                                | THB                                  |
| 9   | shippingMethod | String            | MANDATORY | Sequence Diagram | data.payments[].shippingMethod | Shipping method of the payment                               | STANDARD                             |
| 10  | shippingFee    | Numeric           | MANDATORY | Sequence Diagram | data.payments[].shippingFee    | Shipping fee of the payment                                  | 40.00                                |
| 11  | transactionAt  | String: TIMESTAMP | OPTIONAL  | Sequence Diagram | data.payments[].transactionAt  | Time Stripe confirmed the payment (UTC)                      | 2026-11-06T09:12:30.000Z             |
| 12  | failureCode    | String            | OPTIONAL  | Sequence Diagram | data.payments[].failureCode    | Failure code, only when the status is FAILED                 | card_declined                        |
| 13  | failureMessage | String            | OPTIONAL  | Sequence Diagram | data.payments[].failureMessage | Failure message, only when the status is FAILED              | Your card was declined.              |
| 14  | refundedAt     | String: TIMESTAMP | OPTIONAL  | Sequence Diagram | data.payments[].refundedAt     | Time of the refund (UTC), only when the status is REFUNDED   | 2026-11-06T10:05:00.000Z             |
| 15  | refundReason   | String            | OPTIONAL  | Sequence Diagram | data.payments[].refundReason   | Reason of the refund, only when the status is REFUNDED       | Out of stock                         |
| 16  | createdAt      | String: TIMESTAMP | MANDATORY | Sequence Diagram | data.payments[].createdAt      | Time the payment was started (UTC)                           | 2026-11-06T09:00:00.123Z             |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Payment Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "payments": [
            {
                "paymentId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
                "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
                "orderCode": "ORD-20261106-000101",
                "status": "COMPLETED",
                "paymentMethod": "CREDIT_CARD",
                "paymentName": "Visa 4242",
                "amount": 657.0,
                "currency": "THB",
                "shippingMethod": "STANDARD",
                "shippingFee": 40.0,
                "transactionAt": "2026-11-06T09:12:30.000Z",
                "failureCode": null,
                "failureMessage": null,
                "refundedAt": null,
                "refundReason": null,
                "createdAt": "2026-11-06T09:10:00.000Z"
            },
            {
                "paymentId": "a0b1c2d3-e4f5-4a6b-8c7d-9e0f1a2b3c4d",
                "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
                "orderCode": "ORD-20261106-000101",
                "status": "FAILED",
                "paymentMethod": "CREDIT_CARD",
                "paymentName": null,
                "amount": 657.0,
                "currency": "THB",
                "shippingMethod": "STANDARD",
                "shippingFee": 40.0,
                "transactionAt": null,
                "failureCode": "card_declined",
                "failureMessage": "Your card was declined.",
                "refundedAt": null,
                "refundReason": null,
                "createdAt": "2026-11-06T09:00:00.123Z"
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
        "bizMessage": "Inquiry Payment Success",
        "requestId": "req-9a7b3c5d-6e8f-4a0b-c2d4-5e6f7a8b9c0d",
        "timestamp": "2026-11-06T09:05:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "payments": [],
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
        "bizMessage": "Page size must be between 1 and 100, Id and Order Id must be valid UUIDs, Status must be a valid payment status.",
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

### Table: [payment.t_payment](../../../schema/payment/t_payment.md)

#### QUERY - Get the payments of the user

```SQL
SELECT
    p.id as payment_id,
    p.order_id,
    o.code as order_code,
    p.status,
    p.payment_method,
    p.payment_name,
    p.amount,
    p.currency,
    p.shipping_method,
    p.shipping_fee,
    p.transaction_at,
    p.failure_code,
    p.failure_message,
    p.refunded_at,
    p.refund_reason,
    p.created_at
FROM payment.t_payment p
INNER JOIN sales.t_order o
    ON o.id = p.order_id
WHERE o.user_id = '<sequence.userId>'
AND p.row_status <> 'DELETED'
AND p.id = '<sequence.id>' -- only when id is specified
AND p.order_id = '<sequence.orderId>' -- only when orderId is specified
AND p.status = '<sequence.status>' -- only when status is specified
AND o.code ILIKE '%<sequence.search>%' -- only when search is specified
ORDER BY p.created_at DESC, p.id
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Count the payments of the user

```SQL
SELECT
    COUNT(p.id) as total_items
FROM payment.t_payment p
INNER JOIN sales.t_order o
    ON o.id = p.order_id
WHERE o.user_id = '<sequence.userId>'
AND p.row_status <> 'DELETED'
AND p.id = '<sequence.id>' -- only when id is specified
AND p.order_id = '<sequence.orderId>' -- only when orderId is specified
AND p.status = '<sequence.status>' -- only when status is specified
AND o.code ILIKE '%<sequence.search>%' -- only when search is specified
```

### Table: [sales.t_order](../../../schema/sales/t_order.md)

Read together with the payments above (the order gives the owner and the order code).
