---
name: "Upsert Shipping Stop API"
description: "Insert, update, delete or archive one stop (a hub the parcel passes) of a shipping. Read it when you implement, review or test POST v1/shop/shipping/stop/upsert."
status: in-review
approved_by: null
approved_at: null
---

# [POST]: v1/shop/shipping/stop/upsert

| Title       | Description                                                                                                                                                                                                                                         |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Shipping Stop API                                                                                                                                                                                                                            |
| Method      | POST                                                                                                                                                                                                                                                |
| Endpoint    | v{version}/shop/shipping/stop/upsert                                                                                                                                                                                                                |
| Version     | 1                                                                                                                                                                                                                                                   |
| Description | Insert, update, delete or archive one stop (a hub the parcel passes) of a shipping, The stop can be recorded while the shipping is PENDING or SHIPPED, Only an ACTIVE member of the shop of the order or a platform administrator can record a stop |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- The caller must be an ACTIVE member of the shop of the order (a row of `shop.t_shop_user` with the role ADMIN or STAFF that is ACTIVE) or a platform administrator (a user that has the role `PLATFORM_ADMIN`), otherwise 403 (E10009). This permission model was approved by the product owner. The shop is the shop of the order of the shipping.
- A stop is a checkpoint of the parcel that the customer sees as a timeline (taken from the shop, a hub on the way, arrival at the receiver). The information may come from the carrier, but the system does not call the carrier, the shop records it. A stop is not a driver route.
- A stop can be inserted, updated, deleted or archived only while the shipping is `PENDING` or `SHIPPED`, otherwise 409 (E10006) with the current status in the message. `PICKUP` can be recorded before the parcel is handed over.
- `stopNumber` is unique among the stops of the shipping that are not DELETED, the number held by an INACTIVE, LOCKED or ARCHIVED stop is still taken (409, E10003). The number of a DELETED stop can be used again. The order of the timeline is `stopNumber`.
- `shippingId`, `stopNumber`, `stopType` and `locationName` are required in every request, including a delete and an archive.
- DELETED is final: a DELETED stop is never reopened and its `id` counts as not found (404, E10004). INACTIVE, LOCKED and ARCHIVED are reversible: an update with `rowStatus` ACTIVE shows the stop again. `rowStatus` DELETED is rejected with 400 (E10001) when the request inserts a stop. The customer sees only stops that are ACTIVE.
- This API has no batch version, the shop records one hub at a time, and the stops are read through the inquiry APIs of the shipping (they are returned inside every shipping), so the stop has no inquiry of its own.
- HTTP status of the single upsert: Insert 201 Created, Update 200 Ok, Delete 204 No Content (no response body), Archive 200 Ok.
- A shipping that does not exist, or that is DELETED, answers 404 (E10004) `Shipping not found.` and a stop that does not exist answers 404 (E10004) `Shipping stop not found.` (approved by the product owner on 2026-11-08).
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

|     | Parameter Name   | Data Type         | M/O       | Description                                                                                                                  | Example                              |
| --- | ---------------- | ----------------- | --------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | shippingId       | String: UUID      | MANDATORY | Shipping Id the stop belongs to, must be sent again on update and a different value is 400                                   | f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51 |
| 2   | id               | String: UUID      | OPTIONAL  | Stop Id, Not specified = insert, Specified = update, delete or archive                                                       | c2d3e4f5-7a8b-4c91-8d0e-2f3a4b5c6d02 |
| 3   | stopNumber       | Numeric           | MANDATORY | Position of the stop on the way, an integer from 1, unique in the shipping among stops that are not DELETED                  | 2                                    |
| 4   | stopType         | String            | MANDATORY | PICKUP (parcel taken from the shop), TRANSIT (a hub on the way) or DROPOFF (arrival at the receiver)                         | TRANSIT                              |
| 5   | locationName     | String            | MANDATORY | Name of the hub or place up to 128 characters                                                                                | Bangkok Sorting Hub                  |
| 6   | estimatedArrival | String: TIMESTAMP | OPTIONAL  | Expected arrival (UTC)                                                                                                       | 2026-11-07T08:00:00.123Z             |
| 7   | arrivedAt        | String: TIMESTAMP | OPTIONAL  | Time the parcel reached the stop (UTC), Null or not specified = not arrived yet                                              | 2026-11-07T07:40:00.123Z             |
| 8   | rowStatus        | String            | OPTIONAL  | ACTIVE, INACTIVE, LOCKED, ARCHIVED or DELETED, Defaults to ACTIVE on insert and keeps the value on update when not specified | ACTIVE                               |

#### Example Body Parameters

```JSON
{
    "shippingId": "f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51",
    "stopNumber": 2,
    "stopType": "TRANSIT",
    "locationName": "Bangkok Sorting Hub",
    "estimatedArrival": "2026-11-07T08:00:00.123Z"
}
```

```JSON
{
    "shippingId": "f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51",
    "id": "c2d3e4f5-7a8b-4c91-8d0e-2f3a4b5c6d02",
    "stopNumber": 2,
    "stopType": "TRANSIT",
    "locationName": "Bangkok Sorting Hub",
    "estimatedArrival": "2026-11-07T08:00:00.123Z",
    "arrivedAt": "2026-11-07T07:40:00.123Z"
}
```

```JSON
{
    "shippingId": "f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51",
    "id": "c3d4e5f6-8b9c-4da2-9e1f-3a4b5c6d7e03",
    "stopNumber": 3,
    "stopType": "TRANSIT",
    "locationName": "Nonthaburi Hub",
    "rowStatus": "DELETED"
}
```

```JSON
{
    "shippingId": "f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51",
    "id": "c4e5f6a7-9cad-4eb3-8f2a-4b5c6d7e8f04",
    "stopNumber": 4,
    "stopType": "DROPOFF",
    "locationName": "Receiver address",
    "rowStatus": "ARCHIVED"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/shop/shipping/stop/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "shippingId": "f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51",
    "stopNumber": 2,
    "stopType": "TRANSIT",
    "locationName": "Bangkok Sorting Hub",
    "estimatedArrival": "2026-11-07T08:00:00.123Z"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/shop/shipping/stop/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "shippingId": "f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51",
    "stopNumber": 2,
    "stopType": "TRANSIT",
    "locationName": "Bangkok Sorting Hub",
    "estimatedArrival": "2026-11-07T08:00:00.123Z"
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

|     | Parameter Name   | Data Type         | M/O       | Source           | Field                 | Description                                                    | Example                              |
| --- | ---------------- | ----------------- | --------- | ---------------- | --------------------- | -------------------------------------------------------------- | ------------------------------------ |
| 1   | stopId           | String: UUID      | MANDATORY | Sequence Diagram | data.stopId           | Stop Id                                                        | c2d3e4f5-7a8b-4c91-8d0e-2f3a4b5c6d02 |
| 2   | shippingId       | String: UUID      | MANDATORY | Sequence Diagram | data.shippingId       | Shipping Id                                                    | f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51 |
| 3   | stopNumber       | Numeric           | MANDATORY | Sequence Diagram | data.stopNumber       | Position of the stop                                           | 2                                    |
| 4   | stopType         | String            | MANDATORY | Sequence Diagram | data.stopType         | PICKUP, TRANSIT or DROPOFF                                     | TRANSIT                              |
| 5   | locationName     | String            | MANDATORY | Sequence Diagram | data.locationName     | Name of the hub or place                                       | Bangkok Sorting Hub                  |
| 6   | estimatedArrival | String: TIMESTAMP | OPTIONAL  | Sequence Diagram | data.estimatedArrival | Expected arrival (UTC)                                         | 2026-11-07T08:00:00.123Z             |
| 7   | arrivedAt        | String: TIMESTAMP | OPTIONAL  | Sequence Diagram | data.arrivedAt        | Time the parcel reached the stop (UTC), Null = not arrived yet | 2026-11-07T07:40:00.123Z             |
| 8   | rowStatus        | String            | MANDATORY | Sequence Diagram | data.rowStatus        | Row status after the request                                   | ACTIVE                               |

### Example Response Parameters

#### Success - Insert

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Upsert Shipping Stop Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "stopId": "c2d3e4f5-7a8b-4c91-8d0e-2f3a4b5c6d02",
        "shippingId": "f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51",
        "stopNumber": 2,
        "stopType": "TRANSIT",
        "locationName": "Bangkok Sorting Hub",
        "estimatedArrival": "2026-11-07T08:00:00.123Z",
        "arrivedAt": null,
        "rowStatus": "ACTIVE"
    }
}
```

#### Success - Update

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Upsert Shipping Stop Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "stopId": "c2d3e4f5-7a8b-4c91-8d0e-2f3a4b5c6d02",
        "shippingId": "f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51",
        "stopNumber": 2,
        "stopType": "TRANSIT",
        "locationName": "Bangkok Sorting Hub",
        "estimatedArrival": "2026-11-07T08:00:00.123Z",
        "arrivedAt": "2026-11-07T07:40:00.123Z",
        "rowStatus": "ACTIVE"
    }
}
```

#### Success - Delete

HTTP 204, no response body

```HTTP
HTTP/1.1 204 No Content
```

#### Success - Archive

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Upsert Shipping Stop Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "stopId": "c4e5f6a7-9cad-4eb3-8f2a-4b5c6d7e8f04",
        "shippingId": "f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51",
        "stopNumber": 4,
        "stopType": "DROPOFF",
        "locationName": "Receiver address",
        "estimatedArrival": null,
        "arrivedAt": null,
        "rowStatus": "ARCHIVED"
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
        "bizMessage": "Stop Number is a required field and must be an integer from 1.",
        "requestId": "req-600a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:10:00.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Row Status

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Row Status DELETED is not allowed when a stop is inserted.",
        "requestId": "req-610a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:11:07.123Z",
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
        "bizMessage": "Only a member of the shop of the order or a platform administrator can record a stop.",
        "requestId": "req-630a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:13:21.123Z",
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
        "bizMessage": "Shipping stop not found.",
        "requestId": "req-620a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:12:14.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Shipping

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10004",
        "bizMessage": "Shipping not found.",
        "requestId": "req-630a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:13:21.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10003",
        "bizMessage": "Stop Number 2 already exists in the shipping.",
        "requestId": "req-640a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:14:28.123Z",
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
        "bizMessage": "A stop can only be recorded while the shipping is PENDING or SHIPPED, The shipping is DELIVERED.",
        "requestId": "req-650a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:15:35.123Z",
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
    o.shop_id
FROM shipping.t_shipping s
INNER JOIN sales.t_order o
    ON o.id = s.order_id
WHERE s.id = '<sequence.shippingId>'
AND s.row_status <> 'DELETED'
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

### Table: [shipping.t_shipping_stop](../../../schema/shipping/t_shipping_stop.md)

#### QUERY - Check existing stop

```SQL
SELECT
    ss.id as stop_id,
    ss.shipping_id,
    ss.row_status
FROM shipping.t_shipping_stop ss
WHERE ss.id = '<sequence.id>'
AND ss.shipping_id = '<sequence.shippingId>'
AND ss.row_status <> 'DELETED' -- a DELETED stop counts as not found
```

#### QUERY - Check duplicate stop number

```SQL
SELECT
    ss.id as stop_id
FROM shipping.t_shipping_stop ss
WHERE ss.shipping_id = '<sequence.shippingId>'
AND ss.stop_number = '<sequence.stopNumber>'
AND ss.row_status <> 'DELETED'
AND ss.id <> '<sequence.id>' -- only when id is specified
```

#### INSERT - Create the stop

```SQL
INSERT INTO shipping.t_shipping_stop (created_by, shipping_id, stop_number, stop_type, location_name, estimated_arrival, arrived_at, row_status)
VALUES ('<sequence.userId>', '<sequence.shippingId>', '<sequence.stopNumber>', '<sequence.stopType>', '<sequence.locationName>', '<sequence.estimatedArrival>', '<sequence.arrivedAt>', '<sequence.rowStatus>')
RETURNING id as stop_id, shipping_id, stop_number, stop_type, location_name, estimated_arrival, arrived_at, row_status
```

#### UPDATE - Update, delete or archive the stop

```SQL
UPDATE shipping.t_shipping_stop
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    stop_number = '<sequence.stopNumber>',
    stop_type = '<sequence.stopType>',
    location_name = '<sequence.locationName>',
    estimated_arrival = '<sequence.estimatedArrival>',
    arrived_at = '<sequence.arrivedAt>',
    row_status = '<sequence.rowStatus>' -- a delete sets DELETED, an archive sets ARCHIVED
WHERE id = '<sequence.id>'
AND shipping_id = '<sequence.shippingId>'
RETURNING id as stop_id, shipping_id, stop_number, stop_type, location_name, estimated_arrival, arrived_at, row_status
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
