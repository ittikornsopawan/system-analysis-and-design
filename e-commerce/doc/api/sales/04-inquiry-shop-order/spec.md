---
name: Shop Order Inquiry API Specification
description: Defines the verified-JWT authorization, the current credential check, the shop membership rule and the Allow Scope of the shop order inquiry; read when reviewing or implementing this endpoint.
status: in-review
approved_by: null
approved_at: null
---

# [GET]: v1/shop/order

| Title       | Description                                                                                                                                                                                                                                                                               |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Shop Order API                                                                                                                                                                                                                                                                    |
| Method      | GET                                                                                                                                                                                                                                                                                       |
| Endpoint    | v{version}/shop/order                                                                                                                                                                                                                                                                     |
| Version     | 1                                                                                                                                                                                                                                                                                         |
| Description | Inquiry the orders of a shop for the members of the shop with the customer, the full shipping address, the items, the lot of every item and the profit, Filter by id, status or order code, Only an ACTIVE member of the shop or a platform administrator can read the orders of the shop |

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

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                 | Example                              |
| --- | -------------- | ------------ | --------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | shopId         | String: UUID | MANDATORY | Shop Id                                                                                                                                     | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 2   | id             | String: UUID | OPTIONAL  | Order Id, Response is a list with one item                                                                                                  | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 3   | status         | String       | OPTIONAL  | Order status filter (PENDING, PROCESSING, WAIT_PAYMENT, PAYMENT_CONFIRMED, REFUNDED, COMPLETED, CANCELLED), All statuses when not specified | WAIT_PAYMENT                         |
| 4   | pageIndex      | Numeric      | OPTIONAL  | Page index starting from 1, Defaults to 1                                                                                                   | 1                                    |
| 5   | pageSize       | Numeric      | OPTIONAL  | Number of items per page (max 100), Defaults to 10                                                                                          | 10                                   |
| 6   | search         | String       | OPTIONAL  | Search by order code or the display name of the customer                                                                                    | ORD-2026                             |

### Shop Order Inquiry Rules

- The caller needs a verified JWT (below), then an ACTIVE member row of the shop (a row of `shop.t_shop_user` with the role ADMIN or STAFF that is ACTIVE) or the role `PLATFORM_ADMIN` in the verified `roles` claim, otherwise 403 (E10009). A shop that does not exist or is DELETED is not found (404, E10005). This permission model was approved by the product owner.
- Governing behavior: [owner-confirmed API review](../../../../../docs/superpowers/specs/2026-11-07-api-review-design.md), Q2/Q4/Q10/Q13; this detailed revision remains in-review and includes no backend implementation. Validate the mandatory timestamp as a UTC timestamp before SQL; a missing or malformed timestamp returns 400 E10001. Missing or malformed Bearer credentials or a failed JWT signature/issuer/audience/expiry/UUID sub/roles-claim validation return the same 401 E10002 `Invalid or expired access token.` before SQL.
- Validate the structured `roles` claim defined by [login](../../authen-and-author/02-login/spec.md#claim-resolution-and-payload): `roles` must be an array (an empty array is valid), each object has a UUID `roleId` and a non-empty string `name`, and the `roleId`s are unique; a missing or malformed claim is a 401, never an empty list and never recovered from the database. `userId` comes only from the verified `sub`; `accessTokenHash` is the SHA-256 of the exact presented JWT. Capture the server UTC `now` immediately before the one credential query, recheck the JWT expiry at `now`, then run `QUERY - Check active credential and user`: no row (a missing, revoked or expired stored token, another owner or an inactive user) returns the same 401. The request never carries a user id, a role or a platform administrator flag that controls this lookup.
- The platform administrator is the exact case-sensitive role `PLATFORM_ADMIN` in the verified `roles` claim; do not query `author.m_role` or `author.t_user_role`, and a change of the assignment after the token was issued does not change this token (it may stay usable until its expiry). Membership of a shop is not a token claim and is still read from `shop.t_shop_user`.
- Orders with `rowStatus` DELETED are never returned. The orders are ordered by creation time (newest first) then `id`.
- The shop sees what it needs to prepare the parcel: the customer (display name only, never the user name or the e-mail address), the full copy of the shipping address that was made when the order was created, and the items with the lot they were taken from.
- `grossProfit` and `shopProfit` of an item are returned to the members of the shop. `platformProfit` is returned only to a platform administrator, for the members of the shop it is null and the key is kept (the margin of the platform follows the rule of the shop inquiry). The caller of the examples is a member of the shop and is not a platform administrator.
- Execution order: validate the request and the timestamp (400) -> verify the JWT (401) -> current credential and user (401) -> existence of the shop (404) -> permission (403) -> read. The inquiry has no transaction: every query is one autocommit SELECT, and `platformProfit` is returned only when the verified roles claim has `PLATFORM_ADMIN`.

### Allow Scope

- Rules: `sales:order:read:allow`
- Requested action: `read`
- Data boundary: `SHOP` (ACTIVE ADMIN or STAFF member of the shop) or `ALL` (`PLATFORM_ADMIN` in the verified roles claim)
- Resolution: the checks above decide; a member of the shop reads the orders of the shop, a platform administrator reads every shop and also receives `platformProfit`
- Status: in-review; no explicit deny rule exists yet and the rule does not create a grant by itself
- Reference: [permission-scope.md](../../../permission-scope.md)

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/shop/order?shopId=5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d&status=WAIT_PAYMENT&search=ORD-2026&pageIndex=1&pageSize=10 HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/shop/order?shopId=5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d&status=WAIT_PAYMENT&search=ORD-2026&pageIndex=1&pageSize=10' \
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

|     | Parameter Name | Data Type                       | M/O       | Source           | Field           | Description              | Example |
| --- | -------------- | ------------------------------- | --------- | ---------------- | --------------- | ------------------------ | ------- |
| 1   | orders         | [Array of Order](#order-object) | MANDATORY | Sequence Diagram | data.orders     | Orders of the page       |         |
| 2   | pageIndex      | Numeric                         | MANDATORY | Sequence Diagram | data.pageIndex  | Current page index       | 1       |
| 3   | pageSize       | Numeric                         | MANDATORY | Sequence Diagram | data.pageSize   | Number of items per page | 10      |
| 4   | totalItems     | Numeric                         | MANDATORY | Sequence Diagram | data.totalItems | Total number of orders   | 1       |
| 5   | totalPages     | Numeric                         | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages    | 1       |

#### Order Object

|     | Parameter Name  | Data Type                                              | M/O       | Source           | Field                         | Description                                                  | Example                              |
| --- | --------------- | ------------------------------------------------------ | --------- | ---------------- | ----------------------------- | ------------------------------------------------------------ | ------------------------------------ |
| 1   | orderId         | String: UUID                                           | MANDATORY | Sequence Diagram | data.orders[].orderId         | Order Id                                                     | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 2   | code            | String                                                 | MANDATORY | Sequence Diagram | data.orders[].code            | Order code                                                   | ORD-20261106-000101                  |
| 3   | status          | String                                                 | MANDATORY | Sequence Diagram | data.orders[].status          | Order status                                                 | WAIT_PAYMENT                         |
| 4   | customer        | [Object of Customer](#customer-object)                 | MANDATORY | Sequence Diagram | data.orders[].customer        | Customer who made the order                                  |                                      |
| 5   | shippingAddress | [Object of Shipping Address](#shipping-address-object) | MANDATORY | Sequence Diagram | data.orders[].shippingAddress | Copy of the shipping address made when the order was created |                                      |
| 6   | totalPrice      | Numeric                                                | MANDATORY | Sequence Diagram | data.orders[].totalPrice      | Sum of the item prices x quantities                          | 617.00                               |
| 7   | totalDiscount   | Numeric                                                | MANDATORY | Sequence Diagram | data.orders[].totalDiscount   | Discount                                                     | 0.00                                 |
| 8   | totalTax        | Numeric                                                | MANDATORY | Sequence Diagram | data.orders[].totalTax        | Tax                                                          | 0.00                                 |
| 9   | totalShipping   | Numeric                                                | MANDATORY | Sequence Diagram | data.orders[].totalShipping   | Shipping fee                                                 | 0.00                                 |
| 10  | totalAmount     | Numeric                                                | MANDATORY | Sequence Diagram | data.orders[].totalAmount     | totalPrice - totalDiscount + totalTax + totalShipping        | 617.00                               |
| 11  | expiresAt       | String: TIMESTAMP                                      | MANDATORY | Sequence Diagram | data.orders[].expiresAt       | The order holds the stock until this time (UTC)              | 2026-11-06T09:30:00.123Z             |
| 12  | createdAt       | String: TIMESTAMP                                      | MANDATORY | Sequence Diagram | data.orders[].createdAt       | Time the order was created (UTC)                             | 2026-11-06T09:00:00.123Z             |
| 13  | items           | [Array of Item](#item-object)                          | MANDATORY | Sequence Diagram | data.orders[].items           | Items of the order                                           |                                      |

#### Customer Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                              | Description                  | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ---------------------------------- | ---------------------------- | ------------------------------------ |
| 1   | userId         | String: UUID | MANDATORY | Sequence Diagram | data.orders[].customer.userId      | User Id of the customer      | 5f6a7b8c-9d0e-4f1a-8b2c-3d4e5f6a7b8c |
| 2   | displayName    | String       | MANDATORY | Sequence Diagram | data.orders[].customer.displayName | Display name of the customer | Somchai                              |

#### Shipping Address Object

|     | Parameter Name | Data Type | M/O       | Source           | Field                                    | Description             | Example            |
| --- | -------------- | --------- | --------- | ---------------- | ---------------------------------------- | ----------------------- | ------------------ |
| 1   | title          | String    | MANDATORY | Sequence Diagram | data.orders[].shippingAddress.title      | Address title           | Home               |
| 2   | address        | String    | MANDATORY | Sequence Diagram | data.orders[].shippingAddress.address    | Address (decrypted)     | 99/9 Sukhumvit Rd. |
| 3   | city           | String    | MANDATORY | Sequence Diagram | data.orders[].shippingAddress.city       | City (decrypted)        | Bangkok            |
| 4   | state          | String    | MANDATORY | Sequence Diagram | data.orders[].shippingAddress.state      | State (decrypted)       | Bangkok            |
| 5   | postalCode     | String    | MANDATORY | Sequence Diagram | data.orders[].shippingAddress.postalCode | Postal code (decrypted) | 10110              |
| 6   | country        | String    | MANDATORY | Sequence Diagram | data.orders[].shippingAddress.country    | Country (decrypted)     | TH                 |

#### Item Object

|     | Parameter Name | Data Type                                     | M/O       | Source           | Field                                | Description                                                                              | Example                              |
| --- | -------------- | --------------------------------------------- | --------- | ---------------- | ------------------------------------ | ---------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | orderItemId    | String: UUID                                  | MANDATORY | Sequence Diagram | data.orders[].items[].orderItemId    | Order Item Id                                                                            | e1f2a3b4-3c4d-4e5f-9a6b-7c8d9e0f1a21 |
| 2   | productId      | String: UUID                                  | MANDATORY | Sequence Diagram | data.orders[].items[].productId      | Product Id                                                                               | e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c |
| 3   | productName    | String                                        | MANDATORY | Sequence Diagram | data.orders[].items[].productName    | Product Name                                                                             | Cotton Shirt                         |
| 4   | skuId          | String: UUID                                  | MANDATORY | Sequence Diagram | data.orders[].items[].skuId          | Product SKU Id                                                                           | 7b8c9d0e-1f2a-4b3c-9d4e-5f6a7b8c9d0e |
| 5   | skuName        | String                                        | MANDATORY | Sequence Diagram | data.orders[].items[].skuName        | SKU Name                                                                                 | A / S                                |
| 6   | optionValues   | [Array of Option Value](#option-value-object) | MANDATORY | Sequence Diagram | data.orders[].items[].optionValues   | Chosen value of every level in level order, Empty for the default SKU                    |                                      |
| 7   | imagePath      | String                                        | OPTIONAL  | Sequence Diagram | data.orders[].items[].imagePath      | Image of the SKU, Null when there is no image                                            | /products/shirt/a.png                |
| 8   | quantity       | Numeric                                       | MANDATORY | Sequence Diagram | data.orders[].items[].quantity       | Quantity                                                                                 | 2                                    |
| 9   | price          | Numeric                                       | MANDATORY | Sequence Diagram | data.orders[].items[].price          | Unit price locked when the order was created                                             | 199.00                               |
| 10  | discount       | Numeric                                       | MANDATORY | Sequence Diagram | data.orders[].items[].discount       | Discount of the item                                                                     | 0.00                                 |
| 11  | totalPrice     | Numeric                                       | MANDATORY | Sequence Diagram | data.orders[].items[].totalPrice     | price x quantity                                                                         | 398.00                               |
| 12  | lotId          | String: UUID                                  | MANDATORY | Sequence Diagram | data.orders[].items[].lotId          | Lot the quantity was taken from                                                          | aa11bb22-cc33-4d44-8e55-ff66aa77bb88 |
| 13  | grossProfit    | Numeric                                       | OPTIONAL  | Sequence Diagram | data.orders[].items[].grossProfit    | Gross profit of the item (margin of the lot x quantity), Null when the lot has no margin | 158.00                               |
| 14  | shopProfit     | Numeric                                       | OPTIONAL  | Sequence Diagram | data.orders[].items[].shopProfit     | Profit of the shop, Null when the lot has no margin                                      | 110.60                               |
| 15  | platformProfit | Numeric                                       | OPTIONAL  | Sequence Diagram | data.orders[].items[].platformProfit | Profit of the platform, Null unless the caller is a platform administrator               | 47.40                                |

#### Option Value Object

|     | Parameter Name | Data Type | M/O       | Source           | Field                                           | Description  | Example |
| --- | -------------- | --------- | --------- | ---------------- | ----------------------------------------------- | ------------ | ------- |
| 1   | optionName     | String    | MANDATORY | Sequence Diagram | data.orders[].items[].optionValues[].optionName | Level name   | Pattern |
| 2   | value          | String    | MANDATORY | Sequence Diagram | data.orders[].items[].optionValues[].value      | Chosen value | A       |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Shop Order Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "orders": [
            {
                "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
                "code": "ORD-20261106-000101",
                "status": "WAIT_PAYMENT",
                "totalPrice": 617.0,
                "totalDiscount": 0.0,
                "totalTax": 0.0,
                "totalShipping": 0.0,
                "totalAmount": 617.0,
                "expiresAt": "2026-11-06T09:30:00.123Z",
                "createdAt": "2026-11-06T09:00:00.123Z",
                "items": [
                    {
                        "orderItemId": "e1f2a3b4-3c4d-4e5f-9a6b-7c8d9e0f1a21",
                        "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
                        "productName": "Cotton Shirt",
                        "skuId": "7b8c9d0e-1f2a-4b3c-9d4e-5f6a7b8c9d0e",
                        "skuName": "A / S",
                        "optionValues": [
                            {
                                "optionName": "Pattern",
                                "value": "A"
                            },
                            {
                                "optionName": "Size",
                                "value": "S"
                            }
                        ],
                        "imagePath": "/products/shirt/a.png",
                        "quantity": 2,
                        "price": 199.0,
                        "discount": 0.0,
                        "totalPrice": 398.0,
                        "lotId": "aa11bb22-cc33-4d44-8e55-ff66aa77bb88",
                        "grossProfit": 158.0,
                        "shopProfit": 110.6,
                        "platformProfit": null
                    },
                    {
                        "orderItemId": "e2a3b4c5-4d5e-4f60-8b7c-8d9e0f1a2b32",
                        "productId": "f2b3c4d5-e6f7-4a8b-9c0d-1e2f3a4b5c6d",
                        "productName": "Wireless Mouse",
                        "skuId": "8c9d0e1f-2a3b-4c4d-8e5f-6a7b8c9d0e1f",
                        "skuName": "Wireless Mouse",
                        "optionValues": [],
                        "imagePath": "/products/wireless-mouse/1.png",
                        "quantity": 1,
                        "price": 219.0,
                        "discount": 0.0,
                        "totalPrice": 219.0,
                        "lotId": "bb22cc33-dd44-4e55-9f66-aa77bb88cc99",
                        "grossProfit": 84.0,
                        "shopProfit": 58.8,
                        "platformProfit": null
                    }
                ],
                "customer": {
                    "userId": "5f6a7b8c-9d0e-4f1a-8b2c-3d4e5f6a7b8c",
                    "displayName": "Somchai"
                },
                "shippingAddress": {
                    "title": "Home",
                    "address": "99/9 Sukhumvit Rd.",
                    "city": "Bangkok",
                    "state": "Bangkok",
                    "postalCode": "10110",
                    "country": "TH"
                }
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
        "bizMessage": "Inquiry Shop Order Success",
        "requestId": "req-9a7b3c5d-6e8f-4a0b-c2d4-5e6f7a8b9c0d",
        "timestamp": "2026-11-06T09:05:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "orders": [],
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
        "bizMessage": "Shop Id is a required field, Page size must be between 1 and 100, Status must be a valid order status.",
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
        "bizMessage": "You do not have permission to read the orders of this shop.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
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

### Table: [sales.t_order](../../../schema/sales/t_order.md)

#### QUERY - Get the orders of the shop

```SQL
SELECT
    o.id as order_id,
    o.code,
    o.status,
    o.user_id,
    ui.display_name,
    o.ship_title,
    o.ship_address,
    o.ship_city,
    o.ship_state,
    o.ship_postal_code,
    o.ship_country,
    o.total_price,
    o.total_discount,
    o.total_tax,
    o.total_shipping,
    o.total_amount,
    o.expires_at,
    o.created_at
FROM sales.t_order o
INNER JOIN authen.m_user ui
    ON ui.id = o.user_id
WHERE o.shop_id = '<sequence.shopId>'
AND o.row_status <> 'DELETED'
AND o.id = '<sequence.id>' -- only when id is specified
AND o.status = '<sequence.status>' -- only when status is specified
AND (o.code ILIKE '%<sequence.search>%' OR ui.display_name ILIKE '%<sequence.search>%') -- only when search is specified
ORDER BY o.created_at DESC, o.id
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Count the orders of the shop

```SQL
SELECT
    COUNT(o.id) as total_items
FROM sales.t_order o
INNER JOIN authen.m_user ui
    ON ui.id = o.user_id
WHERE o.shop_id = '<sequence.shopId>'
AND o.row_status <> 'DELETED'
AND o.id = '<sequence.id>' -- only when id is specified
AND o.status = '<sequence.status>' -- only when status is specified
AND (o.code ILIKE '%<sequence.search>%' OR ui.display_name ILIKE '%<sequence.search>%') -- only when search is specified
```

### Table: [sales.t_order_item](../../../schema/sales/t_order_item.md)

#### QUERY - Get the items of the orders

```SQL
SELECT
    oi.id as order_item_id,
    oi.order_id,
    oi.product_id,
    oi.sku_id,
    oi.lot_id,
    oi.quantity,
    oi.price,
    oi.discount,
    oi.total_price,
    oi.gross_profit,
    oi.shop_profit,
    oi.platform_profit -- returned only to a platform administrator, null for the members of the shop
FROM sales.t_order_item oi
WHERE oi.order_id IN ('<sequence.orderIds>')
AND oi.row_status <> 'DELETED'
ORDER BY oi.created_at, oi.id
```

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Get the display name of the customer

```SQL
SELECT
    u.id as user_id,
    u.display_name
FROM authen.m_user u
WHERE u.id IN ('<sequence.userIds>')
```

### Table: [product.m_product_sku_option_value](../../../schema/product/m_product_sku_option_value.md)

#### QUERY - Get the chosen option values of the SKUs

```SQL
SELECT
    psov.sku_id,
    po.name as option_name,
    pov.value
FROM product.m_product_sku_option_value psov
INNER JOIN product.m_product_option_value pov
    ON pov.id = psov.option_value_id
INNER JOIN product.m_product_option po
    ON po.id = pov.option_id
WHERE psov.sku_id IN ('<sequence.skuIds>')
ORDER BY psov.sku_id, po.level_no
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
