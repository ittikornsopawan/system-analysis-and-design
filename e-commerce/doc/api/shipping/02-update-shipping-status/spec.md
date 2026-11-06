# [POST]: v1/shop/shipping/status

| Title       | Description                                                                                                                                                                                                                                                                                                                  |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Update Shipping Status API                                                                                                                                                                                                                                                                                                   |
| Method      | POST                                                                                                                                                                                                                                                                                                                         |
| Endpoint    | v{version}/shop/shipping/status                                                                                                                                                                                                                                                                                              |
| Version     | 1                                                                                                                                                                                                                                                                                                                            |
| Description | Hand a parcel to the carrier with the carrier name and the tracking number, cancel a parcel that is not handed over yet or record a parcel that came back, The order goes back to PAYMENT_CONFIRMED when no parcel is left, Only an ACTIVE member of the shop of the order or a platform administrator can change a shipping |

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

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                         | Example                              |
| --- | -------------- | ------------ | --------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | shippingId     | String: UUID | MANDATORY | Shipping Id                                                                                                         | f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51 |
| 2   | status         | String       | MANDATORY | New status of the shipping: SHIPPED, CANCELLED or RETURNED (PENDING and DELIVERED cannot be requested)              | SHIPPED                              |
| 3   | carrierName    | String       | OPTIONAL  | Carrier (shipping company) up to 64 characters, required when status is SHIPPED and not allowed otherwise           | KERRY                                |
| 4   | trackingNumber | String       | OPTIONAL  | Tracking number given by the carrier up to 64 characters, required when status is SHIPPED and not allowed otherwise | TH0123456789                         |

### Update Shipping Status Rules

- The caller must be an ACTIVE member of the shop of the order (a row of `shop.t_shop_user` with the role ADMIN or STAFF that is ACTIVE) or a platform administrator (a user that has the role `PLATFORM_ADMIN`), otherwise 403 (E10009). This permission model was approved by the product owner.
- The status moves only along these steps, any other step is 409 (E10006) with the current status in the message: `PENDING` -> `SHIPPED` (the parcel is handed to the carrier), `PENDING` -> `CANCELLED` (the shop gives up before handing it over), `SHIPPED` -> `RETURNED` (the parcel came back to the shop because it could not be delivered). `DELIVERED` is not set here, only the receiver can set it (confirm delivery API). `DELIVERED`, `CANCELLED` and `RETURNED` are final. A parcel that came back is sent again by creating a new shipping.
- `SHIPPED` needs `carrierName` and `trackingNumber` and sets `shipped_at` to the time of the request. The pair (`carrierName`, `trackingNumber`) is unique among shippings that are not DELETED, a pair that already exists is 409 (E10003). The comparison is exact. `CANCELLED` and `RETURNED` do not accept the two fields (400, E10001) and keep the values the shipping already has.
- A shipping is never deleted by the API: cancelling is the status `CANCELLED`, and `row_status` stays `ACTIVE`. The shipping method never changes.
- The order follows the parcels. After a `CANCELLED` or `RETURNED` change, when the order is `PROCESSING` and none of its shippings is `PENDING`, `SHIPPED` or `DELIVERED` any more, the order becomes `PAYMENT_CONFIRMED` again in the same transaction, so that the payment API can refund an order whose goods never left the shop (a refund is only allowed at `PAYMENT_CONFIRMED`) and the shop can create a new shipping. Otherwise the order stays `PROCESSING`. `SHIPPED` does not change the order. `orderStatus` in the response is the status after the request.
- Execution order: validate the request (400) -> existence of the shipping (404) -> permission of the caller (403) -> status step and duplicate tracking number (409) -> write the shipping and, when needed, the order in one transaction. The shipping is first read without a lock only to find its order, then the order row is locked (`SELECT ... FOR UPDATE`) before any row of `shipping.*` or `sales.*` is changed, and the update of the shipping repeats the current status in its `WHERE`.
- This behaviour follows `docs/superpowers/specs/2026-11-06-shipping-design.md`, approved by the product owner on 2026-11-06. The payment columns that the shipping APIs read (`payment.t_payment.shipping_method`) belong to the payment design of WP2 (`docs/superpowers/specs/2026-11-06-payment-design.md`).

#### Example Body Parameters

```JSON
{
    "shippingId": "f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51",
    "status": "SHIPPED",
    "carrierName": "KERRY",
    "trackingNumber": "TH0123456789"
}
```

```JSON
{
    "shippingId": "f2b3c4d5-6e7f-4a81-9bac-1d2e3f4a5b62",
    "status": "CANCELLED"
}
```

```JSON
{
    "shippingId": "f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51",
    "status": "RETURNED"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/shop/shipping/status HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "shippingId": "f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51",
    "status": "SHIPPED",
    "carrierName": "KERRY",
    "trackingNumber": "TH0123456789"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/shop/shipping/status' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "shippingId": "f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51",
    "status": "SHIPPED",
    "carrierName": "KERRY",
    "trackingNumber": "TH0123456789"
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

|     | Parameter Name | Data Type         | M/O       | Source           | Field               | Description                                                                                | Example                              |
| --- | -------------- | ----------------- | --------- | ---------------- | ------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------ |
| 1   | shippingId     | String: UUID      | MANDATORY | Sequence Diagram | data.shippingId     | Shipping Id                                                                                | f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51 |
| 2   | orderId        | String: UUID      | MANDATORY | Sequence Diagram | data.orderId        | Order Id                                                                                   | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 3   | orderCode      | String            | MANDATORY | Sequence Diagram | data.orderCode      | Order code                                                                                 | ORD-20261106-000101                  |
| 4   | orderStatus    | String            | MANDATORY | Sequence Diagram | data.orderStatus    | Order status after the request (PROCESSING or PAYMENT_CONFIRMED)                           | PROCESSING                           |
| 5   | status         | String            | MANDATORY | Sequence Diagram | data.status         | Shipping status after the request                                                          | SHIPPED                              |
| 6   | carrierName    | String            | OPTIONAL  | Sequence Diagram | data.carrierName    | Carrier, Null while the shipping was never shipped                                         | KERRY                                |
| 7   | trackingNumber | String            | OPTIONAL  | Sequence Diagram | data.trackingNumber | Tracking number, Null while the shipping was never shipped                                 | TH0123456789                         |
| 8   | shippedAt      | String: TIMESTAMP | OPTIONAL  | Sequence Diagram | data.shippedAt      | Time the parcel was handed to the carrier (UTC), Null while the shipping was never shipped | 2026-11-06T10:00:00.123Z             |

### Example Response Parameters

#### Success - Shipped

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Update Shipping Status Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shippingId": "f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51",
        "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
        "orderCode": "ORD-20261106-000101",
        "orderStatus": "PROCESSING",
        "status": "SHIPPED",
        "carrierName": "KERRY",
        "trackingNumber": "TH0123456789",
        "shippedAt": "2026-11-06T10:00:00.123Z"
    }
}
```

#### Success - Cancelled

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Update Shipping Status Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shippingId": "f2b3c4d5-6e7f-4a81-9bac-1d2e3f4a5b62",
        "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
        "orderCode": "ORD-20261106-000101",
        "orderStatus": "PROCESSING",
        "status": "CANCELLED",
        "carrierName": null,
        "trackingNumber": null,
        "shippedAt": null
    }
}
```

#### Success - Returned

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Update Shipping Status Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shippingId": "f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51",
        "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
        "orderCode": "ORD-20261106-000101",
        "orderStatus": "PAYMENT_CONFIRMED",
        "status": "RETURNED",
        "carrierName": "KERRY",
        "trackingNumber": "TH0123456789",
        "shippedAt": "2026-11-06T10:00:00.123Z"
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
        "bizMessage": "Carrier Name and Tracking Number are required when the status is SHIPPED.",
        "requestId": "req-500a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:00:50.123Z",
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
        "bizMessage": "Only a member of the shop of the order or a platform administrator can change a shipping.",
        "requestId": "req-530a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:03:11.123Z",
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
        "requestId": "req-510a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:01:57.123Z",
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
        "bizMessage": "A shipping cannot change from DELIVERED to CANCELLED.",
        "requestId": "req-520a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:02:04.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict Tracking Number

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10003",
        "bizMessage": "The tracking number TH0123456789 already exists for the carrier KERRY.",
        "requestId": "req-540a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:04:18.123Z",
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

#### QUERY - Get the shipping

```SQL
SELECT
    s.id as shipping_id,
    s.order_id,
    s.status,
    s.shipping_method,
    s.carrier_name,
    s.tracking_number,
    s.shipped_at
FROM shipping.t_shipping s
WHERE s.id = '<sequence.shippingId>'
AND s.row_status <> 'DELETED'
```

#### QUERY - Check duplicate tracking number

```SQL
SELECT
    s.id as shipping_id
FROM shipping.t_shipping s
WHERE s.carrier_name = '<sequence.carrierName>'
AND s.tracking_number = '<sequence.trackingNumber>'
AND s.row_status <> 'DELETED'
AND s.id <> '<sequence.shippingId>'
```

#### UPDATE - Mark the shipping as shipped

```SQL
UPDATE shipping.t_shipping
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    status = 'SHIPPED',
    carrier_name = '<sequence.carrierName>',
    tracking_number = '<sequence.trackingNumber>',
    shipped_at = NOW() AT TIME ZONE 'UTC'
WHERE id = '<sequence.shippingId>'
AND status = 'PENDING' -- no row changed means the status changed in the meantime, answer 409 (E10006)
RETURNING id as shipping_id, status, carrier_name, tracking_number, shipped_at
```

#### UPDATE - Cancel the shipping

```SQL
UPDATE shipping.t_shipping
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    status = 'CANCELLED'
WHERE id = '<sequence.shippingId>'
AND status = 'PENDING' -- no row changed means the status changed in the meantime, answer 409 (E10006)
RETURNING id as shipping_id, status, carrier_name, tracking_number, shipped_at
```

#### UPDATE - Mark the shipping as returned

```SQL
UPDATE shipping.t_shipping
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    status = 'RETURNED'
WHERE id = '<sequence.shippingId>'
AND status = 'SHIPPED' -- no row changed means the status changed in the meantime, answer 409 (E10006)
RETURNING id as shipping_id, status, carrier_name, tracking_number, shipped_at
```

#### QUERY - Count the shippings that are still active

```SQL
SELECT
    COUNT(s.id) as active_shippings
FROM shipping.t_shipping s
WHERE s.order_id = '<sequence.orderId>'
AND s.row_status <> 'DELETED'
AND s.status IN ('PENDING', 'SHIPPED', 'DELIVERED') -- read after the update, only after a cancel or a return
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

#### UPDATE - Give the order back to PAYMENT_CONFIRMED

```SQL
UPDATE sales.t_order
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    status = 'PAYMENT_CONFIRMED'
WHERE id = '<sequence.orderId>'
AND status = 'PROCESSING' -- only when no shipping of the order is PENDING, SHIPPED or DELIVERED after a cancel or a return
RETURNING id as order_id, status
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
