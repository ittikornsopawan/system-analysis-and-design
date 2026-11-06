# [GET]: v1/shop/shipping

| Title       | Description                                                                                                                                                                                                                                                                              |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Shop Shipping API                                                                                                                                                                                                                                                                |
| Method      | GET                                                                                                                                                                                                                                                                                      |
| Endpoint    | v{version}/shop/shipping                                                                                                                                                                                                                                                                 |
| Version     | 1                                                                                                                                                                                                                                                                                        |
| Description | Inquiry the shippings of a shop for the members of the shop with the items, the stops and the copy of the shipping address, Filter by id, order, status, order code or tracking number, Only an ACTIVE member of the shop or a platform administrator can read the shippings of the shop |

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

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                | Example                              |
| --- | -------------- | ------------ | --------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | shopId         | String: UUID | MANDATORY | Shop Id                                                                                                    | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 2   | id             | String: UUID | OPTIONAL  | Shipping Id, Response is a list with one item                                                              | f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51 |
| 3   | orderId        | String: UUID | OPTIONAL  | Order Id filter, All orders of the shop when not specified                                                 | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 4   | status         | String       | OPTIONAL  | Shipping status filter (PENDING, SHIPPED, DELIVERED, CANCELLED, RETURNED), All statuses when not specified | SHIPPED                              |
| 5   | pageIndex      | Numeric      | OPTIONAL  | Page index starting from 1, Defaults to 1                                                                  | 1                                    |
| 6   | pageSize       | Numeric      | OPTIONAL  | Number of items per page (max 100), Defaults to 10                                                         | 10                                   |
| 7   | search         | String       | OPTIONAL  | Search by order code or tracking number                                                                    | TH0123                               |

### Shop Shipping Inquiry Rules

- The caller must be an ACTIVE member of the shop (a row of `shop.t_shop_user` with the role ADMIN or STAFF that is ACTIVE) or a platform administrator (a user that has the role `PLATFORM_ADMIN`), otherwise 403 (E10009). A shop that does not exist or is DELETED is not found (404, E10005). This permission model was approved by the product owner.
- The shippings of the orders of the shop are returned, newest first by creation time, then `id`. Shippings with `rowStatus` DELETED never exist (the API does not delete a shipping). Every shipping carries its items and its stops. The stops are the ones that are not DELETED, in `stopNumber` order, with their `rowStatus`.
- The shop sees what it needs to hand over the parcel: the copy of the shipping address that was stored when the order was created. The customer name and the profit of the items are not part of this response.
- `search` matches the order code or the tracking number (case-insensitive, partial). Nothing found is 200 with an empty list.
- This behaviour follows `docs/superpowers/specs/2026-11-06-shipping-design.md`, approved by the product owner on 2026-11-06. The payment columns that the shipping APIs read (`payment.t_payment.shipping_method`) belong to the payment design of WP2 (`docs/superpowers/specs/2026-11-06-payment-design.md`).

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/shop/shipping?shopId=5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d&status=SHIPPED&search=TH0123&pageIndex=1&pageSize=10 HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/shop/shipping?shopId=5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d&status=SHIPPED&search=TH0123&pageIndex=1&pageSize=10' \
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
| 4   | totalItems     | Numeric                               | MANDATORY | Sequence Diagram | data.totalItems | Total number of shippings | 1       |
| 5   | totalPages     | Numeric                               | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages     | 1       |

#### Shipping Object

|     | Parameter Name  | Data Type                                              | M/O       | Source           | Field                            | Description                                                                            | Example                              |
| --- | --------------- | ------------------------------------------------------ | --------- | ---------------- | -------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | shippingId      | String: UUID                                           | MANDATORY | Sequence Diagram | data.shippings[].shippingId      | Shipping Id                                                                            | f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51 |
| 2   | orderId         | String: UUID                                           | MANDATORY | Sequence Diagram | data.shippings[].orderId         | Order Id                                                                               | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 3   | orderCode       | String                                                 | MANDATORY | Sequence Diagram | data.shippings[].orderCode       | Order code                                                                             | ORD-20261106-000101                  |
| 4   | orderStatus     | String                                                 | MANDATORY | Sequence Diagram | data.shippings[].orderStatus     | Order status                                                                           | PROCESSING                           |
| 5   | shippingMethod  | String                                                 | MANDATORY | Sequence Diagram | data.shippings[].shippingMethod  | Shipping method (STANDARD, EXPRESS, SAME_DAY)                                          | STANDARD                             |
| 6   | status          | String                                                 | MANDATORY | Sequence Diagram | data.shippings[].status          | Shipping status (PENDING, SHIPPED, DELIVERED, CANCELLED, RETURNED)                     | SHIPPED                              |
| 7   | carrierName     | String                                                 | OPTIONAL  | Sequence Diagram | data.shippings[].carrierName     | Carrier, Null until the parcel is shipped                                              | KERRY                                |
| 8   | trackingNumber  | String                                                 | OPTIONAL  | Sequence Diagram | data.shippings[].trackingNumber  | Tracking number, Null until the parcel is shipped                                      | TH0123456789                         |
| 9   | shippedAt       | String: TIMESTAMP                                      | OPTIONAL  | Sequence Diagram | data.shippings[].shippedAt       | Time the parcel was handed to the carrier (UTC)                                        | 2026-11-06T10:00:00.123Z             |
| 10  | deliveredAt     | String: TIMESTAMP                                      | OPTIONAL  | Sequence Diagram | data.shippings[].deliveredAt     | Time the receiver confirmed the parcel (UTC)                                           | 2026-11-07T14:20:00.123Z             |
| 11  | createdAt       | String: TIMESTAMP                                      | MANDATORY | Sequence Diagram | data.shippings[].createdAt       | Time the shipping was created (UTC)                                                    | 2026-11-06T09:05:00.123Z             |
| 12  | shippingAddress | [Object of Shipping Address](#shipping-address-object) | MANDATORY | Sequence Diagram | data.shippings[].shippingAddress | Copy of the shipping address made when the order was created (the label of the parcel) |                                      |
| 13  | items           | [Array of Item](#item-object)                          | MANDATORY | Sequence Diagram | data.shippings[].items           | Order items in the parcel                                                              |                                      |
| 14  | stops           | [Array of Stop](#stop-object)                          | MANDATORY | Sequence Diagram | data.shippings[].stops           | Stops of the parcel in `stopNumber` order, Empty when none is recorded                 |                                      |

#### Shipping Address Object

|     | Parameter Name | Data Type | M/O       | Source           | Field                                       | Description             | Example            |
| --- | -------------- | --------- | --------- | ---------------- | ------------------------------------------- | ----------------------- | ------------------ |
| 1   | title          | String    | MANDATORY | Sequence Diagram | data.shippings[].shippingAddress.title      | Address title           | Home               |
| 2   | address        | String    | MANDATORY | Sequence Diagram | data.shippings[].shippingAddress.address    | Address (decrypted)     | 99/9 Sukhumvit Rd. |
| 3   | city           | String    | MANDATORY | Sequence Diagram | data.shippings[].shippingAddress.city       | City (decrypted)        | Bangkok            |
| 4   | state          | String    | MANDATORY | Sequence Diagram | data.shippings[].shippingAddress.state      | State (decrypted)       | Bangkok            |
| 5   | postalCode     | String    | MANDATORY | Sequence Diagram | data.shippings[].shippingAddress.postalCode | Postal code (decrypted) | 10110              |
| 6   | country        | String    | MANDATORY | Sequence Diagram | data.shippings[].shippingAddress.country    | Country (decrypted)     | TH                 |

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
| 7   | rowStatus        | String            | MANDATORY | Sequence Diagram | data.shippings[].stops[].rowStatus        | Row status of the stop (ACTIVE, INACTIVE, LOCKED, ARCHIVED)    | ACTIVE                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Shop Shipping Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shippings": [
            {
                "shippingId": "f1a2b3c4-5d6e-4f70-8a9b-0c1d2e3f4a51",
                "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
                "orderCode": "ORD-20261106-000101",
                "orderStatus": "PROCESSING",
                "shippingMethod": "STANDARD",
                "status": "SHIPPED",
                "carrierName": "KERRY",
                "trackingNumber": "TH0123456789",
                "shippedAt": "2026-11-06T10:00:00.123Z",
                "deliveredAt": null,
                "createdAt": "2026-11-06T09:05:00.123Z",
                "shippingAddress": {
                    "title": "Home",
                    "address": "99/9 Sukhumvit Rd.",
                    "city": "Bangkok",
                    "state": "Bangkok",
                    "postalCode": "10110",
                    "country": "TH"
                },
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
                        "arrivedAt": "2026-11-06T10:20:00.123Z",
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "stopId": "c2d3e4f5-7a8b-4c91-8d0e-2f3a4b5c6d02",
                        "stopNumber": 2,
                        "stopType": "TRANSIT",
                        "locationName": "Bangkok Sorting Hub",
                        "estimatedArrival": "2026-11-07T08:00:00.123Z",
                        "arrivedAt": null,
                        "rowStatus": "ACTIVE"
                    }
                ]
            }
        ],
        "pageIndex": 1,
        "pageSize": 10,
        "totalItems": 1,
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
        "bizMessage": "Inquiry Shop Shipping Success",
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
        "requestId": "req-700a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:20:10.123Z",
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
        "bizMessage": "Only a member of the shop or a platform administrator can read the shippings of the shop.",
        "requestId": "req-730a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:23:31.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Reference

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "Shop not found.",
        "requestId": "req-720a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:22:24.123Z",
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

#### QUERY - Check shop

```SQL
SELECT
    s.id as shop_id
FROM shop.m_shop s
WHERE s.id = '<sequence.shopId>'
AND s.row_status <> 'DELETED'
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

### Table: [shipping.t_shipping](../../../schema/shipping/t_shipping.md)

#### QUERY - Get the shippings of the shop

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
    o.ship_title,
    o.ship_address,
    o.ship_city,
    o.ship_state,
    o.ship_postal_code,
    o.ship_country
FROM shipping.t_shipping s
INNER JOIN sales.t_order o
    ON o.id = s.order_id
WHERE o.shop_id = '<sequence.shopId>'
AND s.row_status <> 'DELETED'
AND s.id = '<sequence.id>' -- only when id is specified
AND s.order_id = '<sequence.orderId>' -- only when orderId is specified
AND s.status = '<sequence.status>' -- only when status is specified
AND (o.code ILIKE '%<sequence.search>%' OR s.tracking_number ILIKE '%<sequence.search>%') -- only when search is specified
ORDER BY s.created_at DESC, s.id
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Count the shippings of the shop

```SQL
SELECT
    COUNT(s.id) as total_items
FROM shipping.t_shipping s
INNER JOIN sales.t_order o
    ON o.id = s.order_id
WHERE o.shop_id = '<sequence.shopId>'
AND s.row_status <> 'DELETED'
AND s.id = '<sequence.id>' -- only when id is specified
AND s.order_id = '<sequence.orderId>' -- only when orderId is specified
AND s.status = '<sequence.status>' -- only when status is specified
AND (o.code ILIKE '%<sequence.search>%' OR s.tracking_number ILIKE '%<sequence.search>%') -- only when search is specified
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
    ss.arrived_at,
    ss.row_status
FROM shipping.t_shipping_stop ss
WHERE ss.shipping_id IN ('<sequence.shippingIds>')
AND ss.row_status <> 'DELETED'
ORDER BY ss.shipping_id, ss.stop_number, ss.id
```
