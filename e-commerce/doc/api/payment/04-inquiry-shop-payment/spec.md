---
name: Shop Payment Inquiry API Specification
description: Defines the verified-JWT authorization, the current credential check, the shop membership rule and the Allow Scope of the shop payment inquiry; read when reviewing or implementing this endpoint.
status: in-review
approved_by: null
approved_at: null
---

# [GET]: v1/shop/payment

| Title       | Description                                                                                                                                                                                                                                                                  |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Shop Payment API                                                                                                                                                                                                                                                     |
| Method      | GET                                                                                                                                                                                                                                                                          |
| Endpoint    | v{version}/shop/payment                                                                                                                                                                                                                                                      |
| Version     | 1                                                                                                                                                                                                                                                                            |
| Description | Inquiry the payments of the orders of a shop for the members of the shop, Filter by id, order, status or order code, Only an ACTIVE member of the shop or a platform administrator can read the payments of the shop, The ids of Stripe are for platform administrators only |

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

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                          | Example                              |
| --- | -------------- | ------------ | --------- | -------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | shopId         | String: UUID | MANDATORY | Shop Id                                                                                                              | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 2   | id             | String: UUID | OPTIONAL  | Payment Id, Response is a list with one item                                                                         | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 3   | orderId        | String: UUID | OPTIONAL  | Order Id filter                                                                                                      | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 4   | status         | String       | OPTIONAL  | Payment status filter (PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED, REFUNDED), All statuses when not specified | COMPLETED                            |
| 5   | pageIndex      | Numeric      | OPTIONAL  | Page index starting from 1, Defaults to 1                                                                            | 1                                    |
| 6   | pageSize       | Numeric      | OPTIONAL  | Number of items per page (max 100), Defaults to 10                                                                   | 10                                   |
| 7   | search         | String       | OPTIONAL  | Search by order code                                                                                                 | ORD-2026                             |

### Shop Payment Inquiry Rules

- The caller needs a verified JWT (below), then an ACTIVE member row of the shop (a row of `shop.t_shop_user` with the role ADMIN or STAFF that is ACTIVE) or the role `PLATFORM_ADMIN` in the verified `roles` claim, otherwise 403 (E10009). A shop that does not exist or is DELETED is not found (404, E10005).
- Governing behavior: [owner-confirmed API review](../../../../../docs/superpowers/specs/2026-11-07-api-review-design.md), Q2/Q4/Q10/Q13; this detailed revision remains in-review and includes no backend implementation. Validate the mandatory timestamp as a UTC timestamp before SQL; a missing or malformed timestamp returns 400 E10001. Missing or malformed Bearer credentials or a failed JWT signature/issuer/audience/expiry/UUID sub/roles-claim validation return the same 401 E10002 `Invalid or expired access token.` before SQL.
- Validate the structured `roles` claim defined by [login](../../authen-and-author/02-login/spec.md#claim-resolution-and-payload): `roles` must be an array (an empty array is valid), each object has a UUID `roleId` and a non-empty string `name`, and the `roleId`s are unique; a missing or malformed claim is a 401, never an empty list and never recovered from the database. `userId` comes only from the verified `sub`; `accessTokenHash` is the SHA-256 of the exact presented JWT. Capture the server UTC `now` immediately before the one credential query, recheck the JWT expiry at `now`, then run `QUERY - Check active credential and user`: no row (a missing, revoked or expired stored token, another owner or an inactive user) returns the same 401. The request never carries a user id, a role or a platform administrator flag that controls this lookup.
- The platform administrator is the exact case-sensitive role `PLATFORM_ADMIN` in the verified `roles` claim; do not query `author.m_role` or `author.t_user_role`, and a change of the assignment after the token was issued does not change this token (it may stay usable until its expiry). Membership of a shop is not a token claim and is still read from `shop.t_shop_user`.
- Only the payments of the orders of the shop are returned. Payments with `rowStatus` DELETED are never returned. The payments are ordered by creation time (newest first) then `id`.
- `transactionCode` (the Stripe charge id) is returned to the members of the shop. `providerPaymentId` and `providerRefundId` are returned only to a platform administrator and are `null` (the key stays) for the members of the shop, the same way the margin of the platform is hidden.
- Execution order: validate the request and the timestamp (400) -> verify the JWT (401) -> current credential and user (401) -> existence of the shop (404) -> permission (403) -> read. The inquiry has no transaction: every query is one autocommit SELECT, and the authorization result comes from the verified claims and the shop membership row.

### Allow Scope

- Rules: `payment:payment:read:allow`
- Requested action: `read`
- Data boundary: `SHOP` (ACTIVE ADMIN or STAFF member of the shop) or `ALL` (`PLATFORM_ADMIN` in the verified roles claim)
- Resolution: the checks above decide; a member of the shop reads the payments of the shop, a platform administrator reads every shop and also receives `providerPaymentId` and `providerRefundId`
- Status: in-review; no explicit deny rule exists yet and the rule does not create a grant by itself
- Reference: [permission-scope.md](../../../permission-scope.md)

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/shop/payment?shopId=5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d&status=COMPLETED&search=ORD-2026&pageIndex=1&pageSize=10 HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/shop/payment?shopId=5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d&status=COMPLETED&search=ORD-2026&pageIndex=1&pageSize=10' \
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

|     | Parameter Name    | Data Type         | M/O       | Source           | Field                             | Description                                                                                    | Example                              |
| --- | ----------------- | ----------------- | --------- | ---------------- | --------------------------------- | ---------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | paymentId         | String: UUID      | MANDATORY | Sequence Diagram | data.payments[].paymentId         | Payment Id                                                                                     | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 2   | orderId           | String: UUID      | MANDATORY | Sequence Diagram | data.payments[].orderId           | Order Id                                                                                       | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 3   | orderCode         | String            | MANDATORY | Sequence Diagram | data.payments[].orderCode         | Order code                                                                                     | ORD-20261106-000101                  |
| 4   | status            | String            | MANDATORY | Sequence Diagram | data.payments[].status            | Payment status                                                                                 | COMPLETED                            |
| 5   | paymentMethod     | String            | MANDATORY | Sequence Diagram | data.payments[].paymentMethod     | Payment method                                                                                 | CREDIT_CARD                          |
| 6   | paymentName       | String            | OPTIONAL  | Sequence Diagram | data.payments[].paymentName       | Display label of the payment, Null until the payment is paid                                   | Visa 4242                            |
| 7   | amount            | Numeric           | MANDATORY | Sequence Diagram | data.payments[].amount            | Amount of the payment                                                                          | 657.00                               |
| 8   | currency          | String            | MANDATORY | Sequence Diagram | data.payments[].currency          | Currency code                                                                                  | THB                                  |
| 9   | shippingMethod    | String            | MANDATORY | Sequence Diagram | data.payments[].shippingMethod    | Shipping method of the payment                                                                 | STANDARD                             |
| 10  | shippingFee       | Numeric           | MANDATORY | Sequence Diagram | data.payments[].shippingFee       | Shipping fee of the payment                                                                    | 40.00                                |
| 11  | transactionAt     | String: TIMESTAMP | OPTIONAL  | Sequence Diagram | data.payments[].transactionAt     | Time Stripe confirmed the payment (UTC)                                                        | 2026-11-06T09:12:30.000Z             |
| 12  | failureCode       | String            | OPTIONAL  | Sequence Diagram | data.payments[].failureCode       | Failure code, only when the status is FAILED                                                   | card_declined                        |
| 13  | failureMessage    | String            | OPTIONAL  | Sequence Diagram | data.payments[].failureMessage    | Failure message, only when the status is FAILED                                                | Your card was declined.              |
| 14  | refundedAt        | String: TIMESTAMP | OPTIONAL  | Sequence Diagram | data.payments[].refundedAt        | Time of the refund (UTC), only when the status is REFUNDED                                     | 2026-11-06T10:05:00.000Z             |
| 15  | refundReason      | String            | OPTIONAL  | Sequence Diagram | data.payments[].refundReason      | Reason of the refund, only when the status is REFUNDED                                         | Out of stock                         |
| 16  | createdAt         | String: TIMESTAMP | MANDATORY | Sequence Diagram | data.payments[].createdAt         | Time the payment was started (UTC)                                                             | 2026-11-06T09:00:00.123Z             |
| 17  | transactionCode   | String            | OPTIONAL  | Sequence Diagram | data.payments[].transactionCode   | Id of the Stripe charge, Null until the payment is paid                                        | ch_3QxHk2EXAMPLE0001                 |
| 18  | providerPaymentId | String            | OPTIONAL  | Sequence Diagram | data.payments[].providerPaymentId | Id of the Stripe PaymentIntent, Platform administrators only, Null for the members of the shop | pi_3QxHk2EXAMPLE0001                 |
| 19  | providerRefundId  | String            | OPTIONAL  | Sequence Diagram | data.payments[].providerRefundId  | Id of the Stripe refund, Platform administrators only, Null for the members of the shop        | re_3QxHm4EXAMPLE0001                 |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Shop Payment Success",
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
                "transactionCode": "ch_3QxHk2EXAMPLE0001",
                "providerPaymentId": null,
                "providerRefundId": null,
                "createdAt": "2026-11-06T09:10:00.000Z"
            },
            {
                "paymentId": "a2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
                "orderId": "d2f3a4b5-2c3d-4e4f-8a5b-6c7d8e9f0a12",
                "orderCode": "ORD-20261106-000102",
                "status": "REFUNDED",
                "paymentMethod": "THAI_QR",
                "paymentName": "PromptPay",
                "amount": 600.0,
                "currency": "THB",
                "shippingMethod": "EXPRESS",
                "shippingFee": 80.0,
                "transactionAt": "2026-11-06T09:12:30.000Z",
                "failureCode": null,
                "failureMessage": null,
                "refundedAt": "2026-11-06T10:05:00.000Z",
                "refundReason": "Out of stock",
                "transactionCode": "ch_3QxHn5EXAMPLE0002",
                "providerPaymentId": null,
                "providerRefundId": null,
                "createdAt": "2026-11-06T09:11:00.000Z"
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
        "bizMessage": "Inquiry Shop Payment Success",
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
        "bizMessage": "Shop Id is a required field and must be a valid UUID, Page size must be between 1 and 100, Status must be a valid payment status.",
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
        "bizMessage": "You do not have permission to read the payments of this shop.",
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
        "bizCode": "E10005",
        "bizMessage": "Shop not found.",
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

### Table: [shop.m_shop](../../../schema/shop/m_shop.md)

#### QUERY - Check the shop

```SQL
SELECT
    s.id as shop_id
FROM shop.m_shop s
WHERE s.id = '<sequence.shopId>'
AND s.row_status <> 'DELETED'
```

### Table: [payment.t_payment](../../../schema/payment/t_payment.md)

#### QUERY - Get the payments of the shop

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
    p.transaction_code,
    p.provider_payment_id, -- returned only to a platform administrator, null for the members of the shop
    p.provider_refund_id, -- returned only to a platform administrator, null for the members of the shop
    p.failure_code,
    p.failure_message,
    p.refunded_at,
    p.refund_reason,
    p.created_at
FROM payment.t_payment p
INNER JOIN sales.t_order o
    ON o.id = p.order_id
WHERE o.shop_id = '<sequence.shopId>'
AND p.row_status <> 'DELETED'
AND p.id = '<sequence.id>' -- only when id is specified
AND p.order_id = '<sequence.orderId>' -- only when orderId is specified
AND p.status = '<sequence.status>' -- only when status is specified
AND o.code ILIKE '%<sequence.search>%' -- only when search is specified
ORDER BY p.created_at DESC, p.id
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Count the payments of the shop

```SQL
SELECT
    COUNT(p.id) as total_items
FROM payment.t_payment p
INNER JOIN sales.t_order o
    ON o.id = p.order_id
WHERE o.shop_id = '<sequence.shopId>'
AND p.row_status <> 'DELETED'
AND p.id = '<sequence.id>' -- only when id is specified
AND p.order_id = '<sequence.orderId>' -- only when orderId is specified
AND p.status = '<sequence.status>' -- only when status is specified
AND o.code ILIKE '%<sequence.search>%' -- only when search is specified
```

### Table: [sales.t_order](../../../schema/sales/t_order.md)

Read together with the payments above (the order gives the shop and the order code).

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

### Table: [authen.t_user_access_token](../../../schema/authen/t_user_access_token.md)

#### QUERY - Check active credential and user

```SQL
SELECT
    at.user_id
FROM authen.t_user_access_token at
WHERE at.token = '<sequence.accessTokenHash>'
AND at.user_id = '<sequence.userId>'
AND at.row_status = 'ACTIVE'
AND at.expired_at > '<sequence.now>'
AND EXISTS (
    SELECT 1
    FROM authen.m_user u
    WHERE u.id = at.user_id
    AND u.row_status = 'ACTIVE'
)
```
