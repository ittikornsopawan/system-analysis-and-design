---
name: "Inquiry Shop Product SKU API"
description: "Inquiry the list of shop product SKUs with their lots for the shop side, with paging and search. Read it when you implement, review or test GET v1/shop/product-sku."
status: approved
approved_by: Ittikorn
approved_at: 2026-11-16T09:24:57+07:00
---

# [GET]: v1/shop/product-sku

| Title       | Description                                                                                                                                                                                                                                        |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Shop Product SKU API                                                                                                                                                                                                                       |
| Method      | GET                                                                                                                                                                                                                                                |
| Endpoint    | v{version}/shop/product-sku                                                                                                                                                                                                                        |
| Version     | 1                                                                                                                                                                                                                                                  |
| Description | Inquiry the list of shop product SKUs with their lots for the shop side, only for a member of the shop or a platform administrator, with paging and search, Inquiry by id returns a list with one item, Deleted SKUs and deleted lots are excluded |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- The rules of this section, including the permission model (the fixed shop roles OWNER, ADMIN and STAFF or a platform administrator, 403 E10009), were ordered by the product owner on 2026-11-17 (security review F1): the lots carry the cost price, the margins and the remaining quantity, so only the shop side can read them.
- Governing decisions: owner-confirmed API review Q2, Q4, Q10 and Q13 (JWT payload of 2026-11-13).
- `shopId` is mandatory (400, E10001): the call lists the SKUs of one shop. The caller must be an ACTIVE member of that shop (an OWNER, an ADMIN or a STAFF in `shop.t_shop_user`, see the definition of a member in the upsert (shop/11)) or have the exact case-sensitive role `PLATFORM_ADMIN` in the verified `roles` claim (an array of role names, an empty array is valid), otherwise 403 (E10009), also when the shop does not exist, so the answer does not tell whether a shop exists. A platform administrator who asks for a shop that does not exist gets an empty list.
- The platform administrator is read only from the verified `roles` claim: do not query `author.m_role` or `author.t_user_role`, a change of the role assignments does not change a token that was already issued. Membership of a shop is not a token claim and is still read from `shop.t_shop_user`. The JWT is verified and the current credential and user are checked in a read-only transaction (401, E10002), no lock is taken: a read-only transaction cannot lock the caller user.
- The order of the checks is in the sequence diagram.

---

## Request Parameters

### Header Parameters

|     | Parameter Name | Data Type | M/O       | Description                  | Example                                        |
| --- | -------------- | --------- | --------- | ---------------------------- | ---------------------------------------------- |
| 1   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-06T09:00:00.123Z                       |
| 3   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Query Parameters

|     | Parameter Name | Data Type    | M/O       | Description                                           | Example                              |
| --- | -------------- | ------------ | --------- | ----------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Shop Product SKU Id, Response is a list with one item | 9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f |
| 2   | shopId         | String: UUID | MANDATORY | Shop Id, The shop whose SKUs are listed               | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 3   | productId      | String: UUID | OPTIONAL  | Product Id, Filter by product                         | e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c |
| 4   | pageIndex      | Numeric      | OPTIONAL  | Page index starting from 1, Defaults to 1             | 1                                    |
| 5   | pageSize       | Numeric      | OPTIONAL  | Number of items per page (max 100), Defaults to 10    | 10                                   |
| 6   | search         | String       | OPTIONAL  | Search by shop SKU code or shop SKU name              | mouse                                |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/shop/product-sku?shopId=5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d&productId=e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c&pageIndex=1&pageSize=10 HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/shop/product-sku?shopId=5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d&productId=e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c&pageIndex=1&pageSize=10' \
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

|     | Parameter Name | Data Type                                             | M/O       | Source           | Field           | Description                                   | Example |
| --- | -------------- | ----------------------------------------------------- | --------- | ---------------- | --------------- | --------------------------------------------- | ------- |
| 1   | items          | [Array of Shop Product SKU](#shop-product-sku-object) | MANDATORY | Sequence Diagram | data.items      | Shop product SKUs, Empty array when not found |         |
| 2   | pageIndex      | Numeric                                               | MANDATORY | Sequence Diagram | data.pageIndex  | Current page index                            | 1       |
| 3   | pageSize       | Numeric                                               | MANDATORY | Sequence Diagram | data.pageSize   | Number of items per page                      | 10      |
| 4   | totalItems     | Numeric                                               | MANDATORY | Sequence Diagram | data.totalItems | Total number of items                         | 1       |
| 5   | totalPages     | Numeric                                               | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages                         | 1       |

#### Shop Product SKU Object

|     | Parameter Name   | Data Type                   | M/O       | Source           | Field                         | Description                                                                                                 | Example                              |
| --- | ---------------- | --------------------------- | --------- | ---------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | shopProductSkuId | String: UUID                | MANDATORY | Sequence Diagram | data.items[].shopProductSkuId | Shop Product SKU Id                                                                                         | 9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f |
| 2   | shopId           | String: UUID                | MANDATORY | Sequence Diagram | data.items[].shopId           | Shop Id                                                                                                     | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 3   | productId        | String: UUID                | MANDATORY | Sequence Diagram | data.items[].productId        | Product Id                                                                                                  | e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c |
| 4   | skuId            | String: UUID                | MANDATORY | Sequence Diagram | data.items[].skuId            | Product SKU Id                                                                                              | 7b8c9d0e-1f2a-4b3c-9d4e-5f6a7b8c9d0e |
| 5   | code             | String                      | MANDATORY | Sequence Diagram | data.items[].code             | Shop SKU Code                                                                                               | MOUSE-BLK                            |
| 6   | name             | String                      | MANDATORY | Sequence Diagram | data.items[].name             | Shop SKU Name                                                                                               | Wireless Mouse - Black               |
| 7   | description      | String                      | MANDATORY | Sequence Diagram | data.items[].description      | Shop SKU Description                                                                                        | Wireless Mouse - Black               |
| 8   | rowStatus        | String                      | MANDATORY | Sequence Diagram | data.items[].rowStatus        | Row status (ACTIVE, INACTIVE, LOCKED, ARCHIVED)                                                             | ACTIVE                               |
| 9   | lots             | [Array of Lot](#lot-object) | MANDATORY | Sequence Diagram | data.items[].lots             | Lots that are not deleted, The lot on sale first then by creation time, Empty array when the SKU has no lot |                                      |

#### Lot Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                              | Description                                     | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ---------------------------------- | ----------------------------------------------- | ------------------------------------ |
| 1   | lotId          | String: UUID | MANDATORY | Sequence Diagram | data.items[].lots[].lotId          | Lot Id                                          | aa11bb22-cc33-4d44-8e55-ff66aa77bb88 |
| 2   | lotNo          | String       | MANDATORY | Sequence Diagram | data.items[].lots[].lotNo          | Lot Number                                      | LOT-2026-11-01                       |
| 3   | costPrice      | Numeric      | MANDATORY | Sequence Diagram | data.items[].lots[].costPrice      | Cost price of the lot                           | 120.00                               |
| 4   | sellingPrice   | Numeric      | MANDATORY | Sequence Diagram | data.items[].lots[].sellingPrice   | Selling price of the lot                        | 199.00                               |
| 5   | grossMargin    | Numeric      | OPTIONAL  | Sequence Diagram | data.items[].lots[].grossMargin    | Gross margin calculated by the system           | 79.00                                |
| 6   | shareMargin    | Numeric      | OPTIONAL  | Sequence Diagram | data.items[].lots[].shareMargin    | Share margin calculated by the system           | 63.20                                |
| 7   | platformMargin | Numeric      | OPTIONAL  | Sequence Diagram | data.items[].lots[].platformMargin | Platform margin calculated by the system        | 15.80                                |
| 8   | quantity       | Numeric      | MANDATORY | Sequence Diagram | data.items[].lots[].quantity       | Remaining quantity of the lot                   | 80                                   |
| 9   | isOnSale       | Boolean      | MANDATORY | Sequence Diagram | data.items[].lots[].isOnSale       | The lot is on sale now                          | true                                 |
| 10  | rowStatus      | String       | MANDATORY | Sequence Diagram | data.items[].lots[].rowStatus      | Row status (ACTIVE, INACTIVE, LOCKED, ARCHIVED) | ACTIVE                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Shop Product SKU Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "shopProductSkuId": "9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
                "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
                "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
                "skuId": "7b8c9d0e-1f2a-4b3c-9d4e-5f6a7b8c9d0e",
                "code": "MOUSE-BLK",
                "name": "Wireless Mouse - Black",
                "description": "Wireless Mouse - Black",
                "rowStatus": "ACTIVE",
                "lots": [
                    {
                        "lotId": "aa11bb22-cc33-4d44-8e55-ff66aa77bb88",
                        "lotNo": "LOT-2026-11-01",
                        "costPrice": 120.0,
                        "sellingPrice": 199.0,
                        "grossMargin": 79.0,
                        "shareMargin": 63.2,
                        "platformMargin": 15.8,
                        "quantity": 0,
                        "isOnSale": false,
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "lotId": "bb22cc33-dd44-4e55-9f66-aa77bb88cc99",
                        "lotNo": "LOT-2026-12-01",
                        "costPrice": 135.0,
                        "sellingPrice": 219.0,
                        "grossMargin": 84.0,
                        "shareMargin": 67.2,
                        "platformMargin": 16.8,
                        "quantity": 80,
                        "isOnSale": true,
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

#### Success - Not Found

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Shop Product SKU Success",
        "requestId": "req-9a7b3c5d-6e8f-4a0b-c2d4-5e6f7a8b9c0d",
        "timestamp": "2026-11-06T09:05:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [],
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
        "bizMessage": "Shop Id is a required field, Page Index and Page Size must be greater than 0, Page Size must not be greater than 100.",
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
        "bizMessage": "You do not have permission to view the product SKUs of this shop.",
        "requestId": "req-403a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:43:40.123Z",
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

#### Fail - Internal Server Error

```JSON
{
    "status": {
        "code": 500,
        "message": "Internal Server Error",
        "bizMessage": "An unexpected error occurred.",
        "requestId": "req-500a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:46:10.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

One REPEATABLE READ READ ONLY transaction. The caller identity (`callerUserId`, the `sub` of the verified JWT) is used to check the current credential and the membership of the caller; the fresh UTC time is bound.

### Table: [authen.t_user_access_token](../../../schema/authen/t_user_access_token.md)

#### QUERY - Check current credential and user

```SQL
SELECT
    at.id as access_token_id
FROM authen.t_user_access_token at
JOIN authen.m_user u ON u.id = at.user_id
WHERE at.token = '<sequence.accessTokenHash>'
AND at.user_id = '<sequence.callerUserId>'
AND at.row_status = 'ACTIVE'
AND at.expired_at > '<sequence.now>'
AND u.row_status = 'ACTIVE'
```

### Table: [shop.t_shop_user](../../../schema/shop/t_shop_user.md)

#### QUERY - Check shop member

```SQL
SELECT
    su.id as shop_user_id
FROM shop.t_shop_user su
WHERE su.shop_id = '<sequence.shopId>'
AND su.user_id = '<sequence.callerUserId>'
AND su.role IN ('OWNER', 'ADMIN', 'STAFF')
AND su.row_status = 'ACTIVE'
```

### Table: [shop.t_shop_product_sku](../../../schema/shop/t_shop_product_sku.md)

#### QUERY - Get shop product SKUs

```SQL
SELECT
    ssk.id as shop_product_sku_id,
    sp.shop_id,
    sp.product_id,
    ssk.sku_id,
    ssk.code,
    ssk.name,
    ssk.description,
    ssk.row_status
FROM shop.t_shop_product_sku ssk
INNER JOIN shop.t_shop_product sp
    ON sp.id = ssk.shop_product_id
WHERE ssk.row_status <> 'DELETED'
AND ssk.id = '<sequence.id>' -- only when id is specified
AND sp.shop_id = '<sequence.shopId>'
AND sp.product_id = '<sequence.productId>' -- only when productId is specified
AND (ssk.code ILIKE '%<sequence.search>%' OR ssk.name ILIKE '%<sequence.search>%') -- only when search is specified
ORDER BY ssk.created_at DESC
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Get total items

```SQL
SELECT
    COUNT(ssk.id) as total_items
FROM shop.t_shop_product_sku ssk
INNER JOIN shop.t_shop_product sp
    ON sp.id = ssk.shop_product_id
WHERE ssk.row_status <> 'DELETED'
AND ssk.id = '<sequence.id>' -- only when id is specified
AND sp.shop_id = '<sequence.shopId>'
AND sp.product_id = '<sequence.productId>' -- only when productId is specified
AND (ssk.code ILIKE '%<sequence.search>%' OR ssk.name ILIKE '%<sequence.search>%') -- only when search is specified
```

### Table: [shop.t_shop_product_sku_lot](../../../schema/shop/t_shop_product_sku_lot.md)

#### QUERY - Get lots

```SQL
SELECT
    l.id as lot_id,
    l.shop_product_sku_id,
    l.lot_no,
    l.cost_price,
    l.selling_price,
    l.gross_margin,
    l.share_margin,
    l.platform_margin,
    l.quantity,
    l.is_on_sale,
    l.row_status
FROM shop.t_shop_product_sku_lot l
WHERE l.shop_product_sku_id IN ('<sequence.shopProductSkuIds>')
AND l.row_status <> 'DELETED'
ORDER BY l.is_on_sale DESC, l.created_at
```
