---
name: "Upsert Shop Product SKU API"
description: "Insert, update, delete or archive a SKU of a product sold by a shop together with its lots. Read it when you implement, review or test POST v1/shop/product-sku/upsert."
status: in-review
approved_by: null
approved_at: null
---

# [POST]: v1/shop/product-sku/upsert

| Title       | Description                                                                                                                                                                                                                                                                                                                                                        |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Name        | Upsert Shop Product SKU API                                                                                                                                                                                                                                                                                                                                        |
| Method      | POST                                                                                                                                                                                                                                                                                                                                                               |
| Endpoint    | v{version}/shop/product-sku/upsert                                                                                                                                                                                                                                                                                                                                 |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                  |
| Description | Insert, update, delete or archive a SKU of a product sold by a shop together with its lots, Insert when id is not specified, Update when id is specified, Delete when rowStatus is DELETED (HTTP 204 No Content, no response body), Archive when rowStatus is ARCHIVED, Cost price, selling price and stock are kept on the lots, The shop sells one lot at a time |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- The system keeps one row per (shopId, productId, skuId) in `shop.t_shop_product_sku`. When `id` is not specified and that combination already exists the request is rejected with 409 (E10003). The shop product (`shop.t_shop_product`, one row per shop and product) is created automatically when it does not exist yet.
- `skuId` must be an ACTIVE SKU of the product (`product.m_product_sku`), and `productId` must be an ACTIVE product, otherwise 404 (E10005).
- A lot cannot be sold below its cost: `sellingPrice` must be greater than or equal to `costPrice` (400, E10001), the database enforces it with the check `ck_t_shop_product_sku_lot_price_not_below_cost`. This keeps the gross profit of an order item from being negative (approved by the product owner).
- Price, cost and stock live on the lot only. A shop product SKU has any number of lots and at most one lot is on sale at a time (`isOnSale`). Customers see and buy at the selling price of the lot that is on sale, an order item takes all of its quantity from that one lot and cannot be larger than the remaining quantity of the lot.
- When `lots` is specified every lot in the list is inserted when `id` is not specified, updated when `id` is specified and deleted or archived by `rowStatus`. Lots that are not in the list are kept, the system never deletes a lot by omission because lots are the cost history of sold items. When `lots` is not specified the lots are not changed.
- More than one lot with `isOnSale = true` in the request is a 400. Setting `isOnSale = true` closes the lot that is on sale now in the same transaction (the shop switches the lot). A lot cannot be put on sale when it is not ACTIVE or its quantity is 0 (400). When the lot on sale runs out of stock the SKU is out of stock until the shop puts another lot on sale, the system never opens the next lot by itself.
- A lot that is on sale cannot be deleted or archived (409, E10006, put another lot on sale or close it first), and a lot that is referenced by order items (`sales.t_order_item.lot_id`) cannot be deleted (409, E10006). Archiving a lot that is not on sale is allowed.
- Deleting a shop product SKU (`rowStatus = DELETED`) soft-deletes all of its lots and is rejected with 409 (E10006) when any of its lots is referenced by order items. Archiving a shop product SKU keeps its lots but none of them can be on sale.
- `gross_margin`, `share_margin` and `platform_margin` of a lot are calculated by the system from the costs, the selling price and the margin rates of the shop, they are not part of the request.
- Permission: the caller (the user of the access token, never a field of the request) must be a member of the shop, an ADMIN or a STAFF in `shop.t_shop_user` that is ACTIVE, or a platform administrator (a user that has the role `PLATFORM_ADMIN`), otherwise the request is rejected with 403 (E10009) and nothing is written. The rule covers every kind of write of this API (insert, update, delete, archive and the lots). The shop must be ACTIVE (see "Check shop"), a shop that is INACTIVE, LOCKED, ARCHIVED or DELETED counts as not found (404, E10005). This permission model (the role PLATFORM_ADMIN, the members of the shop and the code E10009) was approved by the product owner, the choice that STAFF may also manage SKUs and lots is a decision of the lead SA, restrict it to ADMIN if STAFF must not change prices.
- HTTP status of the single upsert: Insert 201 Created (a new shop product SKU), Update 200 Ok (including changes of lots only), Delete 204 No Content (no response body), Archive 200 Ok.

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

|     | Parameter Name | Data Type                   | M/O       | Description                                                                                                                                               | Example                              |
| --- | -------------- | --------------------------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID                | OPTIONAL  | Shop Product SKU Id, Insert when not specified, Update, Delete or Archive when specified                                                                  | 9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f |
| 2   | shopId         | String: UUID                | MANDATORY | Shop Id, Cannot be changed                                                                                                                                | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 3   | productId      | String: UUID                | MANDATORY | Product Id, Cannot be changed                                                                                                                             | e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c |
| 4   | skuId          | String: UUID                | MANDATORY | Product SKU Id, Must be an ACTIVE SKU of the product, Cannot be changed                                                                                   | 7b8c9d0e-1f2a-4b3c-9d4e-5f6a7b8c9d0e |
| 5   | code           | String                      | MANDATORY | Shop SKU Code (max 64 characters)                                                                                                                         | MOUSE-BLK                            |
| 6   | name           | String                      | OPTIONAL  | Shop SKU Name (max 128 characters), Defaults to the product SKU name                                                                                      | Wireless Mouse - Black               |
| 7   | description    | String                      | OPTIONAL  | Shop SKU Description (max 256 characters), Defaults to the product SKU description                                                                        | Wireless Mouse - Black               |
| 8   | rowStatus      | String                      | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED (HTTP 204 No Content), Archive when ARCHIVED (HTTP 200) | ACTIVE                               |
| 9   | lots           | [Array of Lot](#lot-object) | OPTIONAL  | Lots of the shop product SKU, Lots that are not in the list are kept, Not specified: lots are not changed                                                 |                                      |

#### Lot Object

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                                | Example                              |
| --- | -------------- | ------------ | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Lot Id, Insert when not specified, Update, Delete or Archive when specified, Must belong to the shop product SKU and must not be duplicated                                                                | aa11bb22-cc33-4d44-8e55-ff66aa77bb88 |
| 2   | lotNo          | String       | MANDATORY | Lot Number (max 64 characters), Unique per shop product SKU among lots that are not deleted                                                                                                                | LOT-2026-11-01                       |
| 3   | costPrice      | Numeric      | MANDATORY | Cost price of the lot (>= 0)                                                                                                                                                                               | 120.00                               |
| 4   | sellingPrice   | Numeric      | MANDATORY | Selling price of the lot (>= 0, must not be lower than costPrice)                                                                                                                                          | 199.00                               |
| 5   | quantity       | Numeric      | MANDATORY | Remaining quantity of the lot (>= 0), Replaces the current remaining quantity when updating                                                                                                                | 50                                   |
| 6   | isOnSale       | Boolean      | OPTIONAL  | The lot that is sold now, Defaults to FALSE, Setting TRUE closes the lot that is on sale now, The lot must be ACTIVE and its quantity must be greater than 0                                               | true                                 |
| 7   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED (HTTP 204 for the SKU only, see rules), Archive when ARCHIVED, A lot that is not ACTIVE is never on sale | ACTIVE                               |

#### Example Body Parameters

##### Insert

```JSON
{
    "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
    "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
    "skuId": "7b8c9d0e-1f2a-4b3c-9d4e-5f6a7b8c9d0e",
    "code": "MOUSE-BLK",
    "name": "Wireless Mouse - Black",
    "description": "Wireless Mouse - Black",
    "rowStatus": "ACTIVE",
    "lots": [
        {
            "lotNo": "LOT-2026-11-01",
            "costPrice": 120.0,
            "sellingPrice": 199.0,
            "quantity": 50,
            "isOnSale": true
        },
        {
            "lotNo": "LOT-2026-12-01",
            "costPrice": 135.0,
            "sellingPrice": 219.0,
            "quantity": 80
        }
    ]
}
```

##### Update

```JSON
{
    "id": "9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
    "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
    "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
    "skuId": "7b8c9d0e-1f2a-4b3c-9d4e-5f6a7b8c9d0e",
    "code": "MOUSE-BLK",
    "name": "Wireless Mouse - Black",
    "description": "Wireless Mouse - Black",
    "rowStatus": "ACTIVE",
    "lots": [
        {
            "id": "aa11bb22-cc33-4d44-8e55-ff66aa77bb88",
            "lotNo": "LOT-2026-11-01",
            "costPrice": 120.0,
            "sellingPrice": 199.0,
            "quantity": 0,
            "isOnSale": false
        },
        {
            "id": "bb22cc33-dd44-4e55-9f66-aa77bb88cc99",
            "lotNo": "LOT-2026-12-01",
            "costPrice": 135.0,
            "sellingPrice": 219.0,
            "quantity": 80,
            "isOnSale": true
        }
    ]
}
```

##### Delete

```JSON
{
    "id": "9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
    "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
    "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
    "skuId": "7b8c9d0e-1f2a-4b3c-9d4e-5f6a7b8c9d0e",
    "code": "MOUSE-BLK",
    "rowStatus": "DELETED"
}
```

##### Archive

```JSON
{
    "id": "9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
    "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
    "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
    "skuId": "7b8c9d0e-1f2a-4b3c-9d4e-5f6a7b8c9d0e",
    "code": "MOUSE-BLK",
    "rowStatus": "ARCHIVED"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/shop/product-sku/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
    "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
    "skuId": "7b8c9d0e-1f2a-4b3c-9d4e-5f6a7b8c9d0e",
    "code": "MOUSE-BLK",
    "name": "Wireless Mouse - Black",
    "description": "Wireless Mouse - Black",
    "rowStatus": "ACTIVE",
    "lots": [
        {
            "lotNo": "LOT-2026-11-01",
            "costPrice": 120.0,
            "sellingPrice": 199.0,
            "quantity": 50,
            "isOnSale": true
        },
        {
            "lotNo": "LOT-2026-12-01",
            "costPrice": 135.0,
            "sellingPrice": 219.0,
            "quantity": 80
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/shop/product-sku/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
    "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
    "skuId": "7b8c9d0e-1f2a-4b3c-9d4e-5f6a7b8c9d0e",
    "code": "MOUSE-BLK",
    "name": "Wireless Mouse - Black",
    "description": "Wireless Mouse - Black",
    "rowStatus": "ACTIVE",
    "lots": [
        {
            "lotNo": "LOT-2026-11-01",
            "costPrice": 120.0,
            "sellingPrice": 199.0,
            "quantity": 50,
            "isOnSale": true
        },
        {
            "lotNo": "LOT-2026-12-01",
            "costPrice": 135.0,
            "sellingPrice": 219.0,
            "quantity": 80
        }
    ]
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

|     | Parameter Name   | Data Type                                 | M/O       | Source           | Field                 | Description                                                                             | Example                              |
| --- | ---------------- | ----------------------------------------- | --------- | ---------------- | --------------------- | --------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | shopProductSkuId | String: UUID                              | MANDATORY | Sequence Diagram | data.shopProductSkuId | Inserted, Updated or Archived Shop Product SKU Id, Not returned when deleted (HTTP 204) | 9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f |
| 2   | lots             | [Array of Lot Result](#lot-result-object) | MANDATORY | Sequence Diagram | data.lots             | Lots of the request in the same order, Empty array when lots are not specified          |                                      |

#### Lot Result Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                | Description                          | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | -------------------- | ------------------------------------ | ------------------------------------ |
| 1   | lotId          | String: UUID | MANDATORY | Sequence Diagram | data.lots[].lotId    | Inserted, Updated or Archived Lot Id | aa11bb22-cc33-4d44-8e55-ff66aa77bb88 |
| 2   | lotNo          | String       | MANDATORY | Sequence Diagram | data.lots[].lotNo    | Lot Number                           | LOT-2026-11-01                       |
| 3   | isOnSale       | Boolean      | MANDATORY | Sequence Diagram | data.lots[].isOnSale | The lot is on sale after the request | true                                 |

### Example Response Parameters

#### Success - Insert

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Insert Shop Product SKU Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shopProductSkuId": "9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
        "lots": [
            {
                "lotId": "aa11bb22-cc33-4d44-8e55-ff66aa77bb88",
                "lotNo": "LOT-2026-11-01",
                "isOnSale": true
            },
            {
                "lotId": "bb22cc33-dd44-4e55-9f66-aa77bb88cc99",
                "lotNo": "LOT-2026-12-01",
                "isOnSale": false
            }
        ]
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
        "bizMessage": "Update Shop Product SKU Success",
        "requestId": "req-5c3d9e1f-2a4b-4c6d-8e0f-1a2b3c4d5e6f",
        "timestamp": "2026-11-06T09:10:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shopProductSkuId": "9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
        "lots": [
            {
                "lotId": "aa11bb22-cc33-4d44-8e55-ff66aa77bb88",
                "lotNo": "LOT-2026-11-01",
                "isOnSale": false
            },
            {
                "lotId": "bb22cc33-dd44-4e55-9f66-aa77bb88cc99",
                "lotNo": "LOT-2026-12-01",
                "isOnSale": true
            }
        ]
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
        "bizMessage": "Archive Shop Product SKU Success",
        "requestId": "req-7e5f1a3b-4c6d-4e8f-8a2b-3c4d5e6f7a8b",
        "timestamp": "2026-11-06T09:20:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shopProductSkuId": "9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
        "lots": []
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
        "bizMessage": "Shop Id, Product Id, SKU Id and Code are required fields.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:40:40.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Lot

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "lots[0]: Lot Number, Cost Price, Selling Price and Quantity are required fields, Prices and Quantity must be greater than or equal to 0, Selling Price must not be lower than Cost Price.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Lot On Sale

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "lots[1]: Only one lot can be on sale, and the lot on sale must be ACTIVE with a quantity greater than 0.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:42:54.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Lot Duplicate

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "lots[1]: Lot Number is duplicated with lots[0].",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:43:01.123Z",
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
        "bizMessage": "Shop product SKU not found.",
        "requestId": "req-440a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:44:08.123Z",
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
        "bizMessage": "Shop, product or product SKU not found.",
        "requestId": "req-450a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:45:15.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Lot

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10004",
        "bizMessage": "lots[0]: Lot not found.",
        "requestId": "req-460a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:46:22.123Z",
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
        "bizMessage": "Shop product SKU already exists.",
        "requestId": "req-470a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:47:29.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict Lot Number

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10003",
        "bizMessage": "lots[0]: Lot Number already exists.",
        "requestId": "req-480a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:48:36.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict In Use

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "lots[0]: Lot is on sale or is used by order items.",
        "requestId": "req-490a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:49:43.123Z",
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
        "bizMessage": "You do not have permission to manage this shop.",
        "requestId": "req-403a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:48:03.123Z",
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
AND s.row_status = 'ACTIVE'
```

### Table: [shop.t_shop_user](../../../schema/shop/t_shop_user.md)

#### QUERY - Check shop member

```SQL
SELECT
    su.id as shop_user_id
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

### Table: [product.m_product_sku](../../../schema/product/m_product_sku.md)

#### QUERY - Check product SKU of the product

```SQL
SELECT
    ps.id as sku_id,
    ps.product_id,
    ps.name,
    ps.description
FROM product.m_product_sku ps
INNER JOIN product.m_product p
    ON p.id = ps.product_id
    AND p.row_status = 'ACTIVE'
WHERE ps.id = '<sequence.skuId>'
AND ps.product_id = '<sequence.productId>'
AND ps.row_status = 'ACTIVE'
```

### Table: [shop.t_shop_product](../../../schema/shop/t_shop_product.md)

#### QUERY - Get shop product

```SQL
SELECT
    sp.id as shop_product_id
FROM shop.t_shop_product sp
WHERE sp.shop_id = '<sequence.shopId>'
AND sp.product_id = '<sequence.productId>'
AND sp.row_status <> 'DELETED' -- a DELETED shop product is never reused, a new one is created
```

#### INSERT - Create shop product when it does not exist

```SQL
INSERT INTO shop.t_shop_product (
    created_by,
    shop_id,
    product_id
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.shopId>',
    '<sequence.productId>'
)
RETURNING id as shop_product_id
```

### Table: [shop.t_shop_product_sku](../../../schema/shop/t_shop_product_sku.md)

#### QUERY - Check existing shop product SKU

```SQL
SELECT
    ssk.id as shop_product_sku_id,
    ssk.shop_product_id,
    ssk.sku_id
FROM shop.t_shop_product_sku ssk
WHERE ssk.id = '<sequence.id>'
```

#### QUERY - Check duplicate shop product SKU

```SQL
SELECT
    ssk.id as shop_product_sku_id
FROM shop.t_shop_product_sku ssk
WHERE ssk.shop_product_id = '<sequence.shopProductId>'
AND ssk.sku_id = '<sequence.skuId>'
AND ssk.id <> '<sequence.id>' -- only when id is specified
```

#### INSERT - Create shop product SKU

```SQL
INSERT INTO shop.t_shop_product_sku (
    created_by,
    row_status,
    shop_product_id,
    sku_id,
    code,
    name,
    description
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.rowStatus>',
    '<sequence.shopProductId>',
    '<sequence.skuId>',
    '<sequence.code>',
    '<sequence.name>', -- defaults to product SKU name when not specified
    '<sequence.description>' -- defaults to product SKU description when not specified
)
RETURNING id as shop_product_sku_id
```

#### UPDATE - Update, delete or archive shop product SKU

```SQL
UPDATE shop.t_shop_product_sku
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.rowStatus>',
    code = '<sequence.code>',
    name = '<sequence.name>', -- only when name is specified
    description = '<sequence.description>' -- only when description is specified
WHERE id = '<sequence.id>'
RETURNING id as shop_product_sku_id
```

### Table: [shop.t_shop_product_sku_lot](../../../schema/shop/t_shop_product_sku_lot.md)

#### QUERY - Check existing lots

```SQL
SELECT
    l.id as lot_id,
    l.is_on_sale,
    l.row_status
FROM shop.t_shop_product_sku_lot l
WHERE l.id IN ('<sequence.lots.ids>')
AND l.shop_product_sku_id = '<sequence.shopProductSkuId>'
```

#### QUERY - Check duplicate lot number

```SQL
SELECT
    l.id as lot_id
FROM shop.t_shop_product_sku_lot l
WHERE l.shop_product_sku_id = '<sequence.shopProductSkuId>'
AND l.lot_no = '<sequence.lots.lotNo>'
AND l.id <> '<sequence.lots.id>' -- only when id is specified
AND l.row_status <> 'DELETED'
```

#### UPDATE - Close the lot that is on sale before another lot is put on sale

```SQL
UPDATE shop.t_shop_product_sku_lot
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    is_on_sale = FALSE
WHERE shop_product_sku_id = '<sequence.shopProductSkuId>'
AND is_on_sale = TRUE
AND id <> '<sequence.lots.id>' -- only when id is specified
```

#### INSERT - Create lot

```SQL
INSERT INTO shop.t_shop_product_sku_lot (
    created_by,
    row_status,
    shop_product_sku_id,
    lot_no,
    cost_price,
    selling_price,
    gross_margin,
    share_margin,
    platform_margin,
    quantity,
    is_on_sale
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.lots.rowStatus>',
    '<sequence.shopProductSkuId>',
    '<sequence.lots.lotNo>',
    '<sequence.lots.costPrice>',
    '<sequence.lots.sellingPrice>',
    '<sequence.grossMargin>', -- calculated by the system
    '<sequence.shareMargin>', -- calculated by the system
    '<sequence.platformMargin>', -- calculated by the system
    '<sequence.lots.quantity>',
    '<sequence.lots.isOnSale>' -- TRUE only when the lot is ACTIVE and quantity > 0
)
RETURNING id as lot_id
```

#### UPDATE - Update, delete or archive lot

```SQL
UPDATE shop.t_shop_product_sku_lot
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.lots.rowStatus>',
    lot_no = '<sequence.lots.lotNo>',
    cost_price = '<sequence.lots.costPrice>',
    selling_price = '<sequence.lots.sellingPrice>',
    gross_margin = '<sequence.grossMargin>', -- calculated by the system
    share_margin = '<sequence.shareMargin>', -- calculated by the system
    platform_margin = '<sequence.platformMargin>', -- calculated by the system
    quantity = '<sequence.lots.quantity>',
    is_on_sale = '<sequence.lots.isOnSale>' -- FALSE when the lot is not ACTIVE
WHERE id = '<sequence.lots.id>'
AND shop_product_sku_id = '<sequence.shopProductSkuId>'
RETURNING id as lot_id
```

#### UPDATE - Delete the lots of a deleted shop product SKU

```SQL
UPDATE shop.t_shop_product_sku_lot
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'DELETED',
    is_on_sale = FALSE
WHERE shop_product_sku_id = '<sequence.id>'
AND row_status <> 'DELETED'
```

### Table: [sales.t_order_item](../../../schema/sales/t_order_item.md)

#### QUERY - Check lots in use

```SQL
SELECT
    oi.lot_id
FROM sales.t_order_item oi
WHERE oi.lot_id IN ('<sequence.lots.ids>') -- lots to delete
OR oi.lot_id IN (
    SELECT l.id
    FROM shop.t_shop_product_sku_lot l
    WHERE l.shop_product_sku_id = '<sequence.id>' -- shop product SKU to delete
)
```
