# [POST]: v1/shop/product-sku/upsert/batch

| Title       | Description                                                                                                                                                                                                                                                                                                                                                                                      |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Name        | Upsert Shop Product SKU Batch API                                                                                                                                                                                                                                                                                                                                                                |
| Method      | POST                                                                                                                                                                                                                                                                                                                                                                                             |
| Endpoint    | v{version}/shop/product-sku/upsert/batch                                                                                                                                                                                                                                                                                                                                                         |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                                                |
| Description | Insert, update, delete or archive multiple shop product SKUs with their lots at the same time, Each SKU follows the rules of the single upsert, The response is always HTTP 200 for a successful batch including when it deletes (each result is reported in the body with its action), All SKUs are processed in one transaction in the request order, If any SKU fails then nothing is changed |

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

|     | Parameter Name | Data Type                                             | M/O       | Description                                                                   | Example |
| --- | -------------- | ----------------------------------------------------- | --------- | ----------------------------------------------------------------------------- | ------- |
| 1   | skus           | [Array of Shop Product SKU](#shop-product-sku-object) | MANDATORY | Shop product SKUs to insert, update, delete or archive (min 1, max 100 items) |         |

#### Shop Product SKU Object

|     | Parameter Name | Data Type                   | M/O       | Description                                                                                                                                                   | Example                              |
| --- | -------------- | --------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID                | OPTIONAL  | Shop Product SKU Id, Insert when not specified, Update, Delete or Archive when specified, Must not be duplicated in the request                               | ad1e2f3a-4b5c-4d6e-9f7a-8b9c0d1e2f3a |
| 2   | shopId         | String: UUID                | MANDATORY | Shop Id, Cannot be changed                                                                                                                                    | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 3   | productId      | String: UUID                | MANDATORY | Product Id, Cannot be changed                                                                                                                                 | e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c |
| 4   | skuId          | String: UUID                | MANDATORY | Product SKU Id, Must be an ACTIVE SKU of the product, Cannot be changed, The combination of shopId, productId and skuId must not be duplicated in the request | 8c9d0e1f-2a3b-4c4d-8e5f-6a7b8c9d0e1f |
| 5   | code           | String                      | MANDATORY | Shop SKU Code (max 64 characters)                                                                                                                             | MOUSE-BLK                            |
| 6   | name           | String                      | OPTIONAL  | Shop SKU Name (max 128 characters), Defaults to the product SKU name                                                                                          | Wireless Mouse - Black               |
| 7   | description    | String                      | OPTIONAL  | Shop SKU Description (max 256 characters), Defaults to the product SKU description                                                                            | Wireless Mouse - Black               |
| 8   | rowStatus      | String                      | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED (HTTP 204 No Content), Archive when ARCHIVED (HTTP 200)     | ACTIVE                               |
| 9   | lots           | [Array of Lot](#lot-object) | OPTIONAL  | Lots of the shop product SKU, Lots that are not in the list are kept, Not specified: lots are not changed                                                     |                                      |

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

### Lot Rules (same as the single upsert, applied per SKU)

- The system keeps one row per (shopId, productId, skuId) in `shop.t_shop_product_sku`. When `id` is not specified and that combination already exists the request is rejected with 409 (E10003). The shop product (`shop.t_shop_product`, one row per shop and product) is created automatically when it does not exist yet.
- `skuId` must be an ACTIVE SKU of the product (`product.m_product_sku`), and `productId` must be an ACTIVE product, otherwise 404 (E10005).
- A lot cannot be sold below its cost: `sellingPrice` must be greater than or equal to `costPrice` (400, E10001), the database enforces it with the check `ck_t_shop_product_sku_lot_price_not_below_cost`. This keeps the gross profit of an order item from being negative (approved by the product owner).
- Price, cost and stock live on the lot only. A shop product SKU has any number of lots and at most one lot is on sale at a time (`isOnSale`). Customers see and buy at the selling price of the lot that is on sale, an order item takes all of its quantity from that one lot and cannot be larger than the remaining quantity of the lot.
- When `lots` is specified every lot in the list is inserted when `id` is not specified, updated when `id` is specified and deleted or archived by `rowStatus`. Lots that are not in the list are kept, the system never deletes a lot by omission because lots are the cost history of sold items. When `lots` is not specified the lots are not changed.
- More than one lot with `isOnSale = true` in the request is a 400. Setting `isOnSale = true` closes the lot that is on sale now in the same transaction (the shop switches the lot). A lot cannot be put on sale when it is not ACTIVE or its quantity is 0 (400). When the lot on sale runs out of stock the SKU is out of stock until the shop puts another lot on sale, the system never opens the next lot by itself.
- A lot that is on sale cannot be deleted or archived (409, E10006, put another lot on sale or close it first), and a lot that is referenced by order items (`sales.t_order_item.lot_id`) cannot be deleted (409, E10006). Archiving a lot that is not on sale is allowed.
- Deleting a shop product SKU (`rowStatus = DELETED`) soft-deletes all of its lots and is rejected with 409 (E10006) when any of its lots is referenced by order items. Archiving a shop product SKU keeps its lots but none of them can be on sale.
- `gross_margin`, `share_margin` and `platform_margin` of a lot are calculated by the system from the costs, the selling price and the margin rates of the shop, they are not part of the request.
- Permission: the caller (the user of the access token, never a field of the request) must be a member of every shop that appears in the request, an ADMIN or a STAFF in `shop.t_shop_user` that is ACTIVE, or a platform administrator (a user that has the role `PLATFORM_ADMIN`). When one item is not allowed the whole request is rejected with 403 (E10009), the message starts with the position `skus[i]` of the first item that is not allowed, and nothing is written. The rule covers every kind of write of this API. Every shop of the request must be ACTIVE, otherwise 404 (E10005). This permission model (the role PLATFORM_ADMIN, the members of the shop and the code E10009) was approved by the product owner, the choice that STAFF may also manage SKUs and lots is a decision of the lead SA, restrict it to ADMIN if STAFF must not change prices.
- Execution order: validate the request (400) -> existence checks (404) -> permission (403) -> conflict and in-use checks (409) -> write the shop product, the shop product SKU, close the lot on sale when a lot is put on sale, then write the lots. The whole request is one transaction.
- HTTP status of the batch: always 200 Ok. The first failing SKU stops the batch and its error is returned with the position `skus[i]`, nothing is changed. The request based validation (400) of all SKUs runs first in the request order, then the checks that need the database (404, then 409) in the request order, then the writes.

#### Example Body Parameters

```JSON
{
    "skus": [
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
        },
        {
            "id": "ad1e2f3a-4b5c-4d6e-9f7a-8b9c0d1e2f3a",
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
            "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
            "skuId": "8c9d0e1f-2a3b-4c4d-8e5f-6a7b8c9d0e1f",
            "code": "MOUSE-WHT",
            "name": "Wireless Mouse - White",
            "description": "Wireless Mouse - White",
            "rowStatus": "ACTIVE",
            "lots": [
                {
                    "id": "cc33dd44-ee55-4f66-8a77-bb88cc99dd00",
                    "lotNo": "LOT-2026-11-05",
                    "costPrice": 118.0,
                    "sellingPrice": 195.0,
                    "quantity": 30,
                    "isOnSale": true
                }
            ]
        },
        {
            "id": "be2f3a4b-5c6d-4e7f-8a8b-9c0d1e2f3a4b",
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
            "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
            "skuId": "9d0e1f2a-3b4c-4d5e-9f6a-7b8c9d0e1f2a",
            "code": "MOUSE-GRY",
            "rowStatus": "ARCHIVED"
        }
    ]
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/shop/product-sku/upsert/batch HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "skus": [
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
        },
        {
            "id": "ad1e2f3a-4b5c-4d6e-9f7a-8b9c0d1e2f3a",
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
            "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
            "skuId": "8c9d0e1f-2a3b-4c4d-8e5f-6a7b8c9d0e1f",
            "code": "MOUSE-WHT",
            "name": "Wireless Mouse - White",
            "description": "Wireless Mouse - White",
            "rowStatus": "ACTIVE",
            "lots": [
                {
                    "id": "cc33dd44-ee55-4f66-8a77-bb88cc99dd00",
                    "lotNo": "LOT-2026-11-05",
                    "costPrice": 118.0,
                    "sellingPrice": 195.0,
                    "quantity": 30,
                    "isOnSale": true
                }
            ]
        },
        {
            "id": "be2f3a4b-5c6d-4e7f-8a8b-9c0d1e2f3a4b",
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
            "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
            "skuId": "9d0e1f2a-3b4c-4d5e-9f6a-7b8c9d0e1f2a",
            "code": "MOUSE-GRY",
            "rowStatus": "ARCHIVED"
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/shop/product-sku/upsert/batch' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "skus": [
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
        },
        {
            "id": "ad1e2f3a-4b5c-4d6e-9f7a-8b9c0d1e2f3a",
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
            "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
            "skuId": "8c9d0e1f-2a3b-4c4d-8e5f-6a7b8c9d0e1f",
            "code": "MOUSE-WHT",
            "name": "Wireless Mouse - White",
            "description": "Wireless Mouse - White",
            "rowStatus": "ACTIVE",
            "lots": [
                {
                    "id": "cc33dd44-ee55-4f66-8a77-bb88cc99dd00",
                    "lotNo": "LOT-2026-11-05",
                    "costPrice": 118.0,
                    "sellingPrice": 195.0,
                    "quantity": 30,
                    "isOnSale": true
                }
            ]
        },
        {
            "id": "be2f3a4b-5c6d-4e7f-8a8b-9c0d1e2f3a4b",
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
            "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
            "skuId": "9d0e1f2a-3b4c-4d5e-9f6a-7b8c9d0e1f2a",
            "code": "MOUSE-GRY",
            "rowStatus": "ARCHIVED"
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

|     | Parameter Name | Data Type                         | M/O       | Source           | Field     | Description                                                | Example |
| --- | -------------- | --------------------------------- | --------- | ---------------- | --------- | ---------------------------------------------------------- | ------- |
| 1   | skus           | [Array of Result](#result-object) | MANDATORY | Sequence Diagram | data.skus | Result of each shop product SKU, Same order as the request |         |

#### Result Object

|     | Parameter Name   | Data Type                                 | M/O       | Source           | Field                        | Description                                                                                         | Example                              |
| --- | ---------------- | ----------------------------------------- | --------- | ---------------- | ---------------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | index            | Numeric                                   | MANDATORY | Sequence Diagram | data.skus[].index            | Index of the shop product SKU in the request, Starting from 0                                       | 0                                    |
| 2   | shopProductSkuId | String: UUID                              | MANDATORY | Sequence Diagram | data.skus[].shopProductSkuId | Inserted, Updated, Deleted or Archived Shop Product SKU Id                                          | 9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f |
| 3   | action           | String                                    | MANDATORY | Sequence Diagram | data.skus[].action           | Action of the shop product SKU (INSERT, UPDATE, DELETE, ARCHIVE)                                    | INSERT                               |
| 4   | lots             | [Array of Lot Result](#lot-result-object) | MANDATORY | Sequence Diagram | data.skus[].lots             | Lots of the SKU in the request order, Empty array when lots are not specified or the SKU is deleted |                                      |

#### Lot Result Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                       | Description                          | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | --------------------------- | ------------------------------------ | ------------------------------------ |
| 1   | lotId          | String: UUID | MANDATORY | Sequence Diagram | data.skus[].lots[].lotId    | Inserted, Updated or Archived Lot Id | aa11bb22-cc33-4d44-8e55-ff66aa77bb88 |
| 2   | lotNo          | String       | MANDATORY | Sequence Diagram | data.skus[].lots[].lotNo    | Lot Number                           | LOT-2026-11-01                       |
| 3   | isOnSale       | Boolean      | MANDATORY | Sequence Diagram | data.skus[].lots[].isOnSale | The lot is on sale after the request | true                                 |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Batch Upsert Shop Product SKU Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "skus": [
            {
                "index": 0,
                "shopProductSkuId": "9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
                "action": "INSERT",
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
            },
            {
                "index": 1,
                "shopProductSkuId": "ad1e2f3a-4b5c-4d6e-9f7a-8b9c0d1e2f3a",
                "action": "UPDATE",
                "lots": [
                    {
                        "lotId": "cc33dd44-ee55-4f66-8a77-bb88cc99dd00",
                        "lotNo": "LOT-2026-11-05",
                        "isOnSale": true
                    }
                ]
            },
            {
                "index": 2,
                "shopProductSkuId": "be2f3a4b-5c6d-4e7f-8a8b-9c0d1e2f3a4b",
                "action": "ARCHIVE",
                "lots": []
            }
        ]
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
        "bizMessage": "skus[0]: Shop Id, Product Id, SKU Id and Code are required fields.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:40:40.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Item Count

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "SKUs must contain 1 to 100 items.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Duplicate Id

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "skus[2]: Id is duplicated with skus[1].",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:42:54.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Duplicate SKU

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "skus[2]: Shop Id, Product Id and SKU Id are duplicated with skus[0].",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:43:01.123Z",
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
        "bizMessage": "skus[0].lots[0]: Lot Number, Cost Price, Selling Price and Quantity are required fields, Prices and Quantity must be greater than or equal to 0, Selling Price must not be lower than Cost Price.",
        "requestId": "req-440a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:44:08.123Z",
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
        "bizMessage": "skus[0].lots[1]: Only one lot can be on sale, and the lot on sale must be ACTIVE with a quantity greater than 0.",
        "requestId": "req-450a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:45:15.123Z",
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
        "bizMessage": "skus[0].lots[1]: Lot Number is duplicated with skus[0].lots[0].",
        "requestId": "req-460a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:46:22.123Z",
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
        "bizMessage": "skus[1]: Shop product SKU not found.",
        "requestId": "req-470a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:47:29.123Z",
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
        "bizMessage": "skus[0]: Shop, product or product SKU not found.",
        "requestId": "req-480a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:48:36.123Z",
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
        "bizMessage": "skus[1].lots[0]: Lot not found.",
        "requestId": "req-490a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:49:43.123Z",
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
        "bizMessage": "skus[0]: Shop product SKU already exists.",
        "requestId": "req-500a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:00:50.123Z",
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
        "bizMessage": "skus[0].lots[0]: Lot Number already exists.",
        "requestId": "req-510a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:01:57.123Z",
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
        "bizMessage": "skus[1].lots[0]: Lot is on sale or is used by order items.",
        "requestId": "req-520a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:02:04.123Z",
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
        "bizMessage": "skus[1]: You do not have permission to manage this shop.",
        "requestId": "req-403a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:02:30.123Z",
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
WHERE s.id IN ('<sequence.skus.shopIds>')
AND s.row_status = 'ACTIVE'
```

### Table: [shop.t_shop_user](../../../schema/shop/t_shop_user.md)

#### QUERY - Check shop members

```SQL
SELECT
    su.shop_id
FROM shop.t_shop_user su
WHERE su.shop_id IN ('<sequence.skus.shopIds>')
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
WHERE ps.id IN ('<sequence.skus.skuIds>')
AND ps.product_id IN ('<sequence.skus.productIds>')
AND ps.row_status = 'ACTIVE'
```

### Table: [shop.t_shop_product](../../../schema/shop/t_shop_product.md)

#### QUERY - Get shop product

```SQL
SELECT
    sp.id as shop_product_id
FROM shop.t_shop_product sp
WHERE sp.shop_id = '<sequence.skus.shopId>'
AND sp.product_id = '<sequence.skus.productId>'
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
    '<sequence.skus.shopId>',
    '<sequence.skus.productId>'
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
WHERE ssk.id = '<sequence.skus.id>'
```

#### QUERY - Check duplicate shop product SKU

```SQL
SELECT
    ssk.id as shop_product_sku_id
FROM shop.t_shop_product_sku ssk
WHERE ssk.shop_product_id = '<sequence.shopProductId>'
AND ssk.sku_id = '<sequence.skus.skuId>'
AND ssk.id <> '<sequence.skus.id>' -- only when id is specified
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
    '<sequence.skus.rowStatus>',
    '<sequence.shopProductId>',
    '<sequence.skus.skuId>',
    '<sequence.skus.code>',
    '<sequence.skus.name>', -- defaults to product SKU name when not specified
    '<sequence.skus.description>' -- defaults to product SKU description when not specified
)
RETURNING id as shop_product_sku_id
```

#### UPDATE - Update, delete or archive shop product SKU

```SQL
UPDATE shop.t_shop_product_sku
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.skus.rowStatus>',
    code = '<sequence.skus.code>',
    name = '<sequence.skus.name>', -- only when name is specified
    description = '<sequence.skus.description>' -- only when description is specified
WHERE id = '<sequence.skus.id>'
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
WHERE l.id IN ('<sequence.skus.lots.ids>')
AND l.shop_product_sku_id = '<sequence.shopProductSkuId>'
```

#### QUERY - Check duplicate lot number

```SQL
SELECT
    l.id as lot_id
FROM shop.t_shop_product_sku_lot l
WHERE l.shop_product_sku_id = '<sequence.shopProductSkuId>'
AND l.lot_no = '<sequence.skus.lots.lotNo>'
AND l.id <> '<sequence.skus.lots.id>' -- only when id is specified
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
AND id <> '<sequence.skus.lots.id>' -- only when id is specified
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
    '<sequence.skus.lots.rowStatus>',
    '<sequence.shopProductSkuId>',
    '<sequence.skus.lots.lotNo>',
    '<sequence.skus.lots.costPrice>',
    '<sequence.skus.lots.sellingPrice>',
    '<sequence.grossMargin>', -- calculated by the system
    '<sequence.shareMargin>', -- calculated by the system
    '<sequence.platformMargin>', -- calculated by the system
    '<sequence.skus.lots.quantity>',
    '<sequence.skus.lots.isOnSale>' -- TRUE only when the lot is ACTIVE and quantity > 0
)
RETURNING id as lot_id
```

#### UPDATE - Update, delete or archive lot

```SQL
UPDATE shop.t_shop_product_sku_lot
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.skus.lots.rowStatus>',
    lot_no = '<sequence.skus.lots.lotNo>',
    cost_price = '<sequence.skus.lots.costPrice>',
    selling_price = '<sequence.skus.lots.sellingPrice>',
    gross_margin = '<sequence.grossMargin>', -- calculated by the system
    share_margin = '<sequence.shareMargin>', -- calculated by the system
    platform_margin = '<sequence.platformMargin>', -- calculated by the system
    quantity = '<sequence.skus.lots.quantity>',
    is_on_sale = '<sequence.skus.lots.isOnSale>' -- FALSE when the lot is not ACTIVE
WHERE id = '<sequence.skus.lots.id>'
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
WHERE shop_product_sku_id = '<sequence.skus.id>'
AND row_status <> 'DELETED'
```

### Table: [sales.t_order_item](../../../schema/sales/t_order_item.md)

#### QUERY - Check lots in use

```SQL
SELECT
    oi.lot_id
FROM sales.t_order_item oi
WHERE oi.lot_id IN ('<sequence.skus.lots.ids>') -- lots to delete
OR oi.lot_id IN (
    SELECT l.id
    FROM shop.t_shop_product_sku_lot l
    WHERE l.shop_product_sku_id = '<sequence.skus.id>' -- shop product SKU to delete
)
```
