# [GET]: v1/shipping

| Title       | Description                                                                                                                                                                                                   |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Shipping API                                                                                                                                                                                          |
| Method      | GET                                                                                                                                                                                                           |
| Endpoint    | v{version}/shipping                                                                                                                                                                                           |
| Version     | 1                                                                                                                                                                                                             |
| Description | Inquiry the shippings of the orders of the logged-in customer with the shop, the items, the carrier, the tracking number and the stops, Filter by id, order, status, order code, shop name or tracking number |

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

|     | Parameter Name | Data Type    | M/O      | Description                                                                                                | Example                              |
| --- | -------------- | ------------ | -------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL | Shipping Id, Response is a list with one item                                                              | f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51 |
| 2   | orderId        | String: UUID | OPTIONAL | Order Id filter, All orders of the customer when not specified                                             | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 3   | status         | String       | OPTIONAL | Shipping status filter (PENDING, SHIPPED, DELIVERED, CANCELLED, RETURNED), All statuses when not specified | SHIPPED                              |
| 4   | pageIndex      | Numeric      | OPTIONAL | Page index starting from 1, Defaults to 1                                                                  | 1                                    |
| 5   | pageSize       | Numeric      | OPTIONAL | Number of items per page (max 100), Defaults to 10                                                         | 10                                   |
| 6   | search         | String       | OPTIONAL | Search by order code, shop name or tracking number                                                         | TH0123                               |

### Shipping Inquiry Rules

- Only the shippings of the orders of the user of the access token are returned (the request never carries a user id). The shipping of another user's order is not found, `id` or `orderId` of another user answers an empty list.
- The shippings are returned newest first by creation time, then `id`. Every shipping carries the shop that ships the order, its items and its stops. The customer sees only the stops that are ACTIVE, in `stopNumber` order. The customer does not see the profit of the items.
- `search` matches the order code, the shop name or the tracking number (case-insensitive, partial). Nothing found is 200 with an empty list.
- This behaviour follows `docs/superpowers/specs/2026-11-06-shipping-design.md`, approved by the product owner on 2026-11-06. The payment columns that the shipping APIs read (`payment.t_payment.shipping_method`) belong to the payment design of WP2 (`docs/superpowers/specs/2026-11-06-payment-design.md`).

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/shipping?orderId=d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01&pageIndex=1&pageSize=10 HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/shipping?orderId=d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01&pageIndex=1&pageSize=10' \
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

|     | Parameter Name | Data Type                             | M/O       | Source           | Field           | Description               | Example |
| --- | -------------- | ------------------------------------- | --------- | ---------------- | --------------- | ------------------------- | ------- |
| 1   | shippings      | [Array of Shipping](#shipping-object) | MANDATORY | Sequence Diagram | data.shippings  | Shippings of the page     |         |
| 2   | pageIndex      | Numeric                               | MANDATORY | Sequence Diagram | data.pageIndex  | Page index                | 1       |
| 3   | pageSize       | Numeric                               | MANDATORY | Sequence Diagram | data.pageSize   | Page size                 | 10      |
| 4   | totalItems     | Numeric                               | MANDATORY | Sequence Diagram | data.totalItems | Total number of shippings | 2       |
| 5   | totalPages     | Numeric                               | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages     | 1       |

#### Shipping Object

|     | Parameter Name | Data Type                      | M/O       | Source           | Field                           | Description                                                            | Example                              |
| --- | -------------- | ------------------------------ | --------- | ---------------- | ------------------------------- | ---------------------------------------------------------------------- | ------------------------------------ |
| 1   | shippingId     | String: UUID                   | MANDATORY | Sequence Diagram | data.shippings[].shippingId     | Shipping Id                                                            | f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51 |
| 2   | orderId        | String: UUID                   | MANDATORY | Sequence Diagram | data.shippings[].orderId        | Order Id                                                               | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 3   | orderCode      | String                         | MANDATORY | Sequence Diagram | data.shippings[].orderCode      | Order code                                                             | ORD-20261106-000101                  |
| 4   | orderStatus    | String                         | MANDATORY | Sequence Diagram | data.shippings[].orderStatus    | Order status                                                           | PROCESSING                           |
| 5   | shop           | [Object of Shop](#shop-object) | MANDATORY | Sequence Diagram | data.shippings[].shop           | Shop that ships the order                                              |                                      |
| 6   | shippingMethod | String                         | MANDATORY | Sequence Diagram | data.shippings[].shippingMethod | Shipping method (STANDARD, EXPRESS, SAME_DAY)                          | STANDARD                             |
| 7   | status         | String                         | MANDATORY | Sequence Diagram | data.shippings[].status         | Shipping status (PENDING, SHIPPED, DELIVERED, CANCELLED, RETURNED)     | SHIPPED                              |
| 8   | carrierName    | String                         | OPTIONAL  | Sequence Diagram | data.shippings[].carrierName    | Carrier, Null until the parcel is shipped                              | KERRY                                |
| 9   | trackingNumber | String                         | OPTIONAL  | Sequence Diagram | data.shippings[].trackingNumber | Tracking number, Null until the parcel is shipped                      | TH0123456789                         |
| 10  | shippedAt      | String: TIMESTAMP              | OPTIONAL  | Sequence Diagram | data.shippings[].shippedAt      | Time the parcel was handed to the carrier (UTC)                        | 2026-11-06T10:00:00.123Z             |
| 11  | deliveredAt    | String: TIMESTAMP              | OPTIONAL  | Sequence Diagram | data.shippings[].deliveredAt    | Time the customer or the system confirmed the parcel (UTC)             | 2026-11-07T14:20:00.123Z             |
| 12  | createdAt      | String: TIMESTAMP              | MANDATORY | Sequence Diagram | data.shippings[].createdAt      | Time the shipping was created (UTC)                                    | 2026-11-06T09:05:00.123Z             |
| 13  | items          | [Array of Item](#item-object)  | MANDATORY | Sequence Diagram | data.shippings[].items          | Order items in the parcel                                              |                                      |
| 14  | stops          | [Array of Stop](#stop-object)  | MANDATORY | Sequence Diagram | data.shippings[].stops          | Stops of the parcel in `stopNumber` order, Empty when none is recorded |                                      |

#### Shop Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                        | Description | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ---------------------------- | ----------- | ------------------------------------ |
| 1   | shopId         | String: UUID | MANDATORY | Sequence Diagram | data.shippings[].shop.shopId | Shop Id     | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 2   | name           | String       | MANDATORY | Sequence Diagram | data.shippings[].shop.name   | Shop name   | Coffee Corner                        |

#### Item Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                                | Description            | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ------------------------------------ | ---------------------- | ------------------------------------ |
| 1   | orderItemId    | String: UUID | MANDATORY | Sequence Diagram | data.shippings[].items[].orderItemId | Order Item Id          | e1f2a3b4-3c4d-4e5f-9a6b-7c8d9e0f1a21 |
| 2   | productId      | String: UUID | MANDATORY | Sequence Diagram | data.shippings[].items[].productId   | Product Id             | e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c |
| 3   | productName    | String       | MANDATORY | Sequence Diagram | data.shippings[].items[].productName | Product Name           | Cotton Shirt                         |
| 4   | skuId          | String: UUID | MANDATORY | Sequence Diagram | data.shippings[].items[].skuId       | Product SKU Id         | 7b8c9d0e-1f2a-4b3c-9d4e-5f6a7b8c9d0e |
| 5   | skuName        | String       | MANDATORY | Sequence Diagram | data.shippings[].items[].skuName     | SKU Name               | A / S                                |
| 6   | quantity       | Numeric      | MANDATORY | Sequence Diagram | data.shippings[].items[].quantity    | Quantity in the parcel | 2                                    |

#### Stop Object

|     | Parameter Name   | Data Type         | M/O       | Source           | Field                                     | Description                                                    | Example                              |
| --- | ---------------- | ----------------- | --------- | ---------------- | ----------------------------------------- | -------------------------------------------------------------- | ------------------------------------ |
| 1   | stopId           | String: UUID      | MANDATORY | Sequence Diagram | data.shippings[].stops[].stopId           | Stop Id                                                        | c1c2d3e4-6a7b-4c80-9d0e-1f2a3b4c5d01 |
| 2   | stopNumber       | Numeric           | MANDATORY | Sequence Diagram | data.shippings[].stops[].stopNumber       | Position of the stop on the way                                | 1                                    |
| 3   | stopType         | String            | MANDATORY | Sequence Diagram | data.shippings[].stops[].stopType         | PICKUP, TRANSIT or DROPOFF                                     | PICKUP                               |
| 4   | locationName     | String            | MANDATORY | Sequence Diagram | data.shippings[].stops[].locationName     | Name of the hub or place                                       | Shop warehouse                       |
| 5   | estimatedArrival | String: TIMESTAMP | OPTIONAL  | Sequence Diagram | data.shippings[].stops[].estimatedArrival | Expected arrival (UTC)                                         | 2026-11-06T10:30:00.123Z             |
| 6   | arrivedAt        | String: TIMESTAMP | OPTIONAL  | Sequence Diagram | data.shippings[].stops[].arrivedAt        | Time the parcel reached the stop (UTC), Null = not arrived yet | 2026-11-06T10:20:00.123Z             |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Shipping Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shippings": [
            {
                "shippingId": "f2b3c4d5-6e7f-4a81-9bac-1d2e3f4a5b62",
                "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
                "orderCode": "ORD-20261106-000101",
                "orderStatus": "PROCESSING",
                "shop": {
                    "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
                    "name": "Coffee Corner"
                },
                "shippingMethod": "STANDARD",
                "status": "PENDING",
                "carrierName": null,
                "trackingNumber": null,
                "shippedAt": null,
                "deliveredAt": null,
                "createdAt": "2026-11-06T09:10:00.123Z",
                "items": [
                    {
                        "orderItemId": "e2a3b4c5-4d5e-4f60-8b7c-8d9e0f1a2b32",
                        "productId": "f2b3c4d5-e6f7-4a8b-9c0d-1e2f3a4b5c6d",
                        "productName": "Wireless Mouse",
                        "skuId": "8c9d0e1f-2a3b-4c4d-8e5f-6a7b8c9d0e1f",
                        "skuName": "Wireless Mouse",
                        "quantity": 1
                    }
                ],
                "stops": []
            },
            {
                "shippingId": "f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51",
                "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
                "orderCode": "ORD-20261106-000101",
                "orderStatus": "PROCESSING",
                "shop": {
                    "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
                    "name": "Coffee Corner"
                },
                "shippingMethod": "STANDARD",
                "status": "SHIPPED",
                "carrierName": "KERRY",
                "trackingNumber": "TH0123456789",
                "shippedAt": "2026-11-06T10:00:00.123Z",
                "deliveredAt": null,
                "createdAt": "2026-11-06T09:05:00.123Z",
                "items": [
                    {
                        "orderItemId": "e1f2a3b4-3c4d-4e5f-9a6b-7c8d9e0f1a21",
                        "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
                        "productName": "Cotton Shirt",
                        "skuId": "7b8c9d0e-1f2a-4b3c-9d4e-5f6a7b8c9d0e",
                        "skuName": "A / S",
                        "quantity": 2
                    }
                ],
                "stops": [
                    {
                        "stopId": "c1c2d3e4-6a7b-4c80-9d0e-1f2a3b4c5d01",
                        "stopNumber": 1,
                        "stopType": "PICKUP",
                        "locationName": "Shop warehouse",
                        "estimatedArrival": "2026-11-06T10:30:00.123Z",
                        "arrivedAt": "2026-11-06T10:20:00.123Z"
                    },
                    {
                        "stopId": "c2d3e4f5-7a8b-4c91-8d0e-2f3a4b5c6d02",
                        "stopNumber": 2,
                        "stopType": "TRANSIT",
                        "locationName": "Bangkok Sorting Hub",
                        "estimatedArrival": "2026-11-07T08:00:00.123Z",
                        "arrivedAt": null
                    }
                ]
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
        "bizMessage": "Inquiry Shipping Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shippings": [],
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
        "bizMessage": "Page Size must be a number from 1 to 100.",
        "requestId": "req-800a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:30:20.123Z",
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

### Table: [shipping.t_shipping](../../../schema/shipping/t_shipping.md)

#### QUERY - Get the shippings of the user

```SQL
SELECT
    s.id as shipping_id,
    s.order_id,
    o.code as order_code,
    o.status as order_status,
    s.shipping_method,
    s.status,
    s.carrier_name,
    s.tracking_number,
    s.shipped_at,
    s.delivered_at,
    s.created_at,
    o.shop_id,
    sh.name as shop_name
FROM shipping.t_shipping s
INNER JOIN sales.t_order o
    ON o.id = s.order_id
INNER JOIN shop.m_shop sh
    ON sh.id = o.shop_id
WHERE o.user_id = '<sequence.userId>'
AND o.row_status <> 'DELETED'
AND s.row_status <> 'DELETED'
AND s.id = '<sequence.id>' -- only when id is specified
AND s.order_id = '<sequence.orderId>' -- only when orderId is specified
AND s.status = '<sequence.status>' -- only when status is specified
AND (o.code ILIKE '%<sequence.search>%' OR sh.name ILIKE '%<sequence.search>%' OR s.tracking_number ILIKE '%<sequence.search>%') -- only when search is specified
ORDER BY s.created_at DESC, s.id
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Count the shippings of the user

```SQL
SELECT
    COUNT(s.id) as total_items
FROM shipping.t_shipping s
INNER JOIN sales.t_order o
    ON o.id = s.order_id
INNER JOIN shop.m_shop sh
    ON sh.id = o.shop_id
WHERE o.user_id = '<sequence.userId>'
AND o.row_status <> 'DELETED'
AND s.row_status <> 'DELETED'
AND s.id = '<sequence.id>' -- only when id is specified
AND s.order_id = '<sequence.orderId>' -- only when orderId is specified
AND s.status = '<sequence.status>' -- only when status is specified
AND (o.code ILIKE '%<sequence.search>%' OR sh.name ILIKE '%<sequence.search>%' OR s.tracking_number ILIKE '%<sequence.search>%') -- only when search is specified
```

### Table: [shipping.t_shipping_item](../../../schema/shipping/t_shipping_item.md)

#### QUERY - Get the items of the shippings

```SQL
SELECT
    si.shipping_id,
    si.order_item_id,
    oi.product_id,
    p.name as product_name,
    oi.sku_id,
    ps.name as sku_name,
    si.quantity
FROM shipping.t_shipping_item si
INNER JOIN sales.t_order_item oi
    ON oi.id = si.order_item_id
INNER JOIN product.m_product p
    ON p.id = oi.product_id
INNER JOIN product.m_product_sku ps
    ON ps.id = oi.sku_id
WHERE si.shipping_id IN ('<sequence.shippingIds>')
AND si.row_status <> 'DELETED'
ORDER BY si.created_at, si.id
```

### Table: [shipping.t_shipping_stop](../../../schema/shipping/t_shipping_stop.md)

#### QUERY - Get the stops of the shippings

```SQL
SELECT
    ss.id as stop_id,
    ss.shipping_id,
    ss.stop_number,
    ss.stop_type,
    ss.location_name,
    ss.estimated_arrival,
    ss.arrived_at
FROM shipping.t_shipping_stop ss
WHERE ss.shipping_id IN ('<sequence.shippingIds>')
AND ss.row_status = 'ACTIVE' -- the customer sees only ACTIVE stops
ORDER BY ss.shipping_id, ss.stop_number, ss.id
```
