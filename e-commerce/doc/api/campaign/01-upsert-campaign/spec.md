# [POST]: v1/campaign/upsert

| Title       | Description                                                                                                                                                                                                                           |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Campaign API                                                                                                                                                                                                                   |
| Method      | POST                                                                                                                                                                                                                                  |
| Endpoint    | v{version}/campaign/upsert                                                                                                                                                                                                            |
| Version     | 1                                                                                                                                                                                                                                     |
| Description | Insert, update, delete or archive one campaign with its budget, its discount, its shops and its products, Only a platform administrator can call it, A campaign that used its budget cannot be deleted, Changes reach new orders only |

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

|     | Parameter Name | Data Type                                  | M/O       | Description                                                                                                                  | Example                                     |
| --- | -------------- | ------------------------------------------ | --------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| 1   | id             | String: UUID                               | OPTIONAL  | Campaign Id, Not specified = insert, Specified = update, delete or archive                                                   | b1c2d3e4-1a2b-4c3d-8e4f-5a6b7c8d9e01        |
| 2   | name           | String                                     | MANDATORY | Campaign name up to 128 characters, unique among campaigns that are not DELETED                                              | Black Friday 2026                           |
| 3   | description    | String                                     | OPTIONAL  | Description                                                                                                                  | Four days of discounts on selected products |
| 4   | startAt        | String: TIMESTAMP                          | MANDATORY | The campaign gives discounts from this time (UTC)                                                                            | 2026-11-27T00:00:00.000Z                    |
| 5   | endAt          | String: TIMESTAMP                          | MANDATORY | The campaign gives discounts until this time, not including it (UTC), Must be after startAt                                  | 2026-11-30T23:59:59.000Z                    |
| 6   | rowStatus      | String                                     | OPTIONAL  | ACTIVE, INACTIVE, LOCKED, ARCHIVED or DELETED, Defaults to ACTIVE on insert and keeps the value on update when not specified | ACTIVE                                      |
| 7   | budget         | [Object of Budget](#budget-parameters)     | OPTIONAL  | The budget, required on insert                                                                                               |                                             |
| 8   | discount       | [Object of Discount](#discount-parameters) | OPTIONAL  | The discount, required on insert                                                                                             |                                             |
| 9   | shops          | [Array of Shop](#shop-parameters)          | OPTIONAL  | Shops of the campaign, up to 100, Not specified = rows stay as they are                                                      |                                             |
| 10  | products       | [Array of Product](#product-parameters)    | OPTIONAL  | Products and categories of the campaign, up to 100, Not specified = rows stay as they are                                    |                                             |

#### Budget Parameters

|     | Parameter Name | Data Type    | M/O       | Description                                                                                       | Example                              |
| --- | -------------- | ------------ | --------- | ------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Budget Id, Not specified = insert (only when the campaign has no live budget), Specified = update | d1a2b3c4-5e6f-4a70-8b81-9c0d1e2f3a41 |
| 2   | budget         | Numeric      | MANDATORY | Amount of the budget (at most 2 decimals), 0 or more                                              | 60000.00                             |
| 3   | rowStatus      | String       | OPTIONAL  | ACTIVE, INACTIVE, LOCKED or ARCHIVED (a budget is deleted with its campaign, DELETED is 400)      | ACTIVE                               |

#### Discount Parameters

|     | Parameter Name | Data Type    | M/O       | Description                                                                                           | Example                              |
| --- | -------------- | ------------ | --------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Discount Id, Not specified = insert (only when the campaign has no live discount), Specified = update | d2b3c4d5-6f70-4b81-9c92-0d1e2f3a4b52 |
| 2   | discountType   | String       | MANDATORY | PERCENTAGE or FIXED_AMOUNT                                                                            | PERCENTAGE                           |
| 3   | discountValue  | Numeric      | MANDATORY | Greater than 0, a PERCENTAGE is at most 100 (at most 2 decimals), a FIXED_AMOUNT is baht per unit     | 15.00                                |
| 4   | rowStatus      | String       | OPTIONAL  | ACTIVE, INACTIVE, LOCKED, ARCHIVED or DELETED                                                         | ACTIVE                               |

#### Shop Parameters

|     | Parameter Name | Data Type    | M/O       | Description                                                                | Example                              |
| --- | -------------- | ------------ | --------- | -------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Campaign shop row Id, Not specified = insert, Specified = update or delete | e1a2b3c4-7081-4c92-8da3-1e2f3a4b5c61 |
| 2   | shopId         | String: UUID | MANDATORY | Shop Id, must be sent again on update and a different value is 400         | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 3   | rowStatus      | String       | OPTIONAL  | ACTIVE, INACTIVE, LOCKED, ARCHIVED or DELETED                              | ACTIVE                               |

#### Product Parameters

|     | Parameter Name    | Data Type    | M/O      | Description                                                                   | Example                              |
| --- | ----------------- | ------------ | -------- | ----------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id                | String: UUID | OPTIONAL | Campaign product row Id, Not specified = insert, Specified = update or delete | e2b3c4d5-8192-4da3-9eb4-2f3a4b5c6d72 |
| 2   | productCategoryId | String: UUID | OPTIONAL | Product category Id, exactly one of productCategoryId and productId           | 3c4d5e6f-7a8b-4c9d-8e0f-1a2b3c4d5e6f |
| 3   | productId         | String: UUID | OPTIONAL | Product Id, exactly one of productCategoryId and productId                    | e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c |
| 4   | rowStatus         | String       | OPTIONAL | ACTIVE, INACTIVE, LOCKED, ARCHIVED or DELETED                                 | ACTIVE                               |

### Campaign Rules

- Only a platform administrator (a user that has the role `PLATFORM_ADMIN`) can call this API, any other user gets 403 (E10009). This permission model was approved by the product owner. Shops take part when a platform administrator adds them to the campaign.
- `name`, `startAt` and `endAt` are required in every request, including a delete and an archive. `endAt` must be after `startAt` (400, E10001, the database enforces it with `ck_m_campaign_period`). `name` is unique among campaigns that are not DELETED, the comparison is exact and the name of an INACTIVE, LOCKED or ARCHIVED campaign is still taken (409, E10003). The name of a DELETED campaign can be used again.
- DELETED is final: a DELETED campaign is never reopened and its `id` counts as not found (404, E10004). INACTIVE, LOCKED and ARCHIVED are reversible: an update with `rowStatus` ACTIVE opens the campaign again. `rowStatus` DELETED is rejected with 400 (E10001) when the request inserts a campaign. Only a campaign with `rowStatus` ACTIVE and a time that covers the moment of the order gives discounts, an INACTIVE, LOCKED, ARCHIVED or DELETED campaign gives none and the orders that already took a discount are not changed.
- A campaign that has ledger rows (an order used its budget) cannot be deleted, 409 (E10006), archive it instead. A campaign without ledger rows can be deleted and its budget, discount, shops and products are deleted (soft) with it in the same transaction.
- Budget: one live budget per campaign. Insert needs `budget` and creates the row with `remaining = budget`. A second budget without `id` while a live one exists is 409 (E10003). Update changes `budget` and keeps what the orders took: `used = budget - remaining`, the new `remaining` is the new `budget` minus `used`. A new `budget` below `used` is 409 (E10006) with the used amount in the message. Increasing is always allowed. Editing the budget does not write the ledger (`updated_by` and `updated_at` keep the trace). A budget that has ledger rows cannot be INACTIVE-deleted, it has no delete, `rowStatus` DELETED is 400.
- Discount: one live discount per campaign. `discountType` PERCENTAGE needs `discountValue` above 0 and up to 100, FIXED_AMOUNT needs a value above 0 (400, E10001, the database enforces both). A second discount without `id` while a live one exists is 409 (E10003). The discount can be changed or deleted while the campaign runs, the change reaches new orders only. A campaign without a live discount gives no discount.
- Shops: the list of shops of the campaign, a campaign without any live shop row is for every shop. A row without `id` is inserted, a row with `id` is updated, `rowStatus` DELETED deletes it and rows that are not in the list are kept. `shopId` must be an existing shop that is not DELETED, otherwise 404 (E10005) with the position, `shops[1]: ...`. A shop that is already in the campaign (live row) is 409 (E10003). The same `shopId` or `id` twice in the request is 400 (E10001).
- Products: the same child rules. A row names a product (`productId`) or a product category (`productCategoryId`), exactly one (400, E10001, `ck_t_campaign_product_target`). A category means that category only, its sub categories are not included. A campaign without any live product row is for every product. The product or category must exist and not be DELETED (404, E10005), the same product or category twice in the campaign is 409 (E10003), twice in the request is 400.
- Children (`budget`, `discount`, `shops`, `products`): an `id` that does not belong to the campaign is 404 (E10004), `id` must not be duplicated in the request, up to 100 rows in `shops` and in `products`, and the id of a DELETED row counts as not found. A row of `shops` or `products` is checked with `QUERY - Check existing campaign shop` and `QUERY - Check existing campaign product`, no row answers 404 (E10004) (approved by the product owner on 2026-11-08).
- When a campaign is deleted, its discount, shops and products are soft-deleted with it by `UPDATE - Delete the discount of a deleted campaign`, `UPDATE - Delete the shops of a deleted campaign` and `UPDATE - Delete the products of a deleted campaign`, one statement for all the rows of the campaign, in the same transaction as `UPDATE - Delete the budget of a deleted campaign` (approved by the product owner on 2026-11-08).
- HTTP status of the single upsert: Insert 201 Created, Update 200 Ok, Delete 204 No Content (no response body), Archive 200 Ok.
- Execution order: validate the request (400) -> existence of the campaign, the children and the shops, products and categories (404) -> permission (403) -> duplicate name, duplicate child, budget below used and in-use checks (409) -> write the campaign and its children in one transaction.
- This behaviour follows `docs/superpowers/specs/2026-11-06-campaign-design.md`, approved by the product owner on 2026-11-06 (the proposals to the delivered specs in its section 4 are decided by the lead SA).

#### Example Body Parameters

```JSON
{
    "name": "Black Friday 2026",
    "description": "Four days of discounts on selected products",
    "startAt": "2026-11-27T00:00:00.000Z",
    "endAt": "2026-11-30T23:59:59.000Z",
    "budget": {
        "budget": 50000.0
    },
    "discount": {
        "discountType": "PERCENTAGE",
        "discountValue": 10.0
    },
    "shops": [
        {
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d"
        }
    ],
    "products": [
        {
            "productCategoryId": "3c4d5e6f-7a8b-4c9d-8e0f-1a2b3c4d5e6f"
        },
        {
            "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c"
        }
    ]
}
```

```JSON
{
    "id": "b1c2d3e4-1a2b-4c3d-8e4f-5a6b7c8d9e01",
    "name": "Black Friday 2026",
    "description": "Four days of discounts on selected products",
    "startAt": "2026-11-27T00:00:00.000Z",
    "endAt": "2026-11-30T23:59:59.000Z",
    "budget": {
        "id": "d1a2b3c4-5e6f-4a70-8b81-9c0d1e2f3a41",
        "budget": 60000.0
    },
    "discount": {
        "id": "d2b3c4d5-6f70-4b81-9c92-0d1e2f3a4b52",
        "discountType": "PERCENTAGE",
        "discountValue": 15.0
    },
    "shops": [
        {
            "id": "e1a2b3c4-7081-4c92-8da3-1e2f3a4b5c61",
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d"
        }
    ],
    "products": [
        {
            "id": "e2b3c4d5-8192-4da3-9eb4-2f3a4b5c6d72",
            "productCategoryId": "3c4d5e6f-7a8b-4c9d-8e0f-1a2b3c4d5e6f",
            "rowStatus": "ACTIVE"
        }
    ]
}
```

```JSON
{
    "id": "b2d3e4f5-2b3c-4d4e-9f50-6b7c8d9e0f12",
    "name": "Cyber Monday 2026",
    "startAt": "2026-11-30T00:00:00.000Z",
    "endAt": "2026-12-01T23:59:59.000Z",
    "rowStatus": "DELETED"
}
```

```JSON
{
    "id": "b3e4f5a6-3c4d-4e5f-8a61-7c8d9e0f1a23",
    "name": "Singles Day 2026",
    "startAt": "2026-11-11T00:00:00.000Z",
    "endAt": "2026-11-11T23:59:59.000Z",
    "rowStatus": "ARCHIVED"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/campaign/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "name": "Black Friday 2026",
    "description": "Four days of discounts on selected products",
    "startAt": "2026-11-27T00:00:00.000Z",
    "endAt": "2026-11-30T23:59:59.000Z",
    "budget": {
        "budget": 50000.0
    },
    "discount": {
        "discountType": "PERCENTAGE",
        "discountValue": 10.0
    },
    "shops": [
        {
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d"
        }
    ],
    "products": [
        {
            "productCategoryId": "3c4d5e6f-7a8b-4c9d-8e0f-1a2b3c4d5e6f"
        },
        {
            "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c"
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/campaign/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "name": "Black Friday 2026",
    "description": "Four days of discounts on selected products",
    "startAt": "2026-11-27T00:00:00.000Z",
    "endAt": "2026-11-30T23:59:59.000Z",
    "budget": {
        "budget": 50000.0
    },
    "discount": {
        "discountType": "PERCENTAGE",
        "discountValue": 10.0
    },
    "shops": [
        {
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d"
        }
    ],
    "products": [
        {
            "productCategoryId": "3c4d5e6f-7a8b-4c9d-8e0f-1a2b3c4d5e6f"
        },
        {
            "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c"
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

|     | Parameter Name | Data Type                              | M/O       | Source           | Field            | Description                                                           | Example                                     |
| --- | -------------- | -------------------------------------- | --------- | ---------------- | ---------------- | --------------------------------------------------------------------- | ------------------------------------------- |
| 1   | campaignId     | String: UUID                           | MANDATORY | Sequence Diagram | data.campaignId  | Campaign Id                                                           | b1c2d3e4-1a2b-4c3d-8e4f-5a6b7c8d9e01        |
| 2   | name           | String                                 | MANDATORY | Sequence Diagram | data.name        | Campaign name                                                         | Black Friday 2026                           |
| 3   | description    | String                                 | OPTIONAL  | Sequence Diagram | data.description | Description                                                           | Four days of discounts on selected products |
| 4   | startAt        | String: TIMESTAMP                      | MANDATORY | Sequence Diagram | data.startAt     | The campaign gives discounts from this time (UTC)                     | 2026-11-27T00:00:00.000Z                    |
| 5   | endAt          | String: TIMESTAMP                      | MANDATORY | Sequence Diagram | data.endAt       | The campaign gives discounts until this time, not including it (UTC)  | 2026-11-30T23:59:59.000Z                    |
| 6   | rowStatus      | String                                 | MANDATORY | Sequence Diagram | data.rowStatus   | Row status of the campaign                                            | ACTIVE                                      |
| 7   | budget         | [Object of Budget](#budget-object)     | OPTIONAL  | Sequence Diagram | data.budget      | Budget of the campaign, Null for members of a shop                    |                                             |
| 8   | discount       | [Object of Discount](#discount-object) | MANDATORY | Sequence Diagram | data.discount    | The discount of the campaign                                          |                                             |
| 9   | shops          | [Array of Shop](#shop-object)          | OPTIONAL  | Sequence Diagram | data.shops       | Shops of the campaign, Empty = every shop, Null for members of a shop |                                             |
| 10  | products       | [Array of Product](#product-object)    | MANDATORY | Sequence Diagram | data.products    | Products and categories of the campaign, Empty = every product        |                                             |

#### Budget Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                 | Description                                                                    | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | --------------------- | ------------------------------------------------------------------------------ | ------------------------------------ |
| 1   | budgetId       | String: UUID | MANDATORY | Sequence Diagram | data.budget.budgetId  | Budget Id                                                                      | d1a2b3c4-5e6f-4a70-8b81-9c0d1e2f3a41 |
| 2   | budget         | Numeric      | MANDATORY | Sequence Diagram | data.budget.budget    | Amount of the budget                                                           | 60000.00                             |
| 3   | remaining      | Numeric      | MANDATORY | Sequence Diagram | data.budget.remaining | Amount that no order has taken                                                 | 59000.00                             |
| 4   | used           | Numeric      | MANDATORY | Sequence Diagram | data.budget.used      | budget - remaining, what the orders took (reservations that were not released) | 1000.00                              |
| 5   | rowStatus      | String       | MANDATORY | Sequence Diagram | data.budget.rowStatus | Row status of the budget                                                       | ACTIVE                               |

#### Discount Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                       | Description                                    | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | --------------------------- | ---------------------------------------------- | ------------------------------------ |
| 1   | discountId     | String: UUID | MANDATORY | Sequence Diagram | data.discount.discountId    | Discount Id                                    | d2b3c4d5-6f70-4b81-9c92-0d1e2f3a4b52 |
| 2   | discountType   | String       | MANDATORY | Sequence Diagram | data.discount.discountType  | PERCENTAGE or FIXED_AMOUNT                     | PERCENTAGE                           |
| 3   | discountValue  | Numeric      | MANDATORY | Sequence Diagram | data.discount.discountValue | Percent (up to 100) or amount in baht per unit | 15.00                                |
| 4   | rowStatus      | String       | MANDATORY | Sequence Diagram | data.discount.rowStatus     | Row status of the discount                     | ACTIVE                               |

#### Shop Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                       | Description           | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | --------------------------- | --------------------- | ------------------------------------ |
| 1   | campaignShopId | String: UUID | MANDATORY | Sequence Diagram | data.shops[].campaignShopId | Campaign shop row Id  | e1a2b3c4-7081-4c92-8da3-1e2f3a4b5c61 |
| 2   | shopId         | String: UUID | MANDATORY | Sequence Diagram | data.shops[].shopId         | Shop Id               | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 3   | rowStatus      | String       | MANDATORY | Sequence Diagram | data.shops[].rowStatus      | Row status of the row | ACTIVE                               |

#### Product Object

|     | Parameter Name    | Data Type    | M/O       | Source           | Field                             | Description                                                                                          | Example                              |
| --- | ----------------- | ------------ | --------- | ---------------- | --------------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | campaignProductId | String: UUID | MANDATORY | Sequence Diagram | data.products[].campaignProductId | Campaign product row Id                                                                              | e2b3c4d5-8192-4da3-9eb4-2f3a4b5c6d72 |
| 2   | productCategoryId | String: UUID | OPTIONAL  | Sequence Diagram | data.products[].productCategoryId | Product category Id (the category itself, not its sub categories), Null when the row names a product | 3c4d5e6f-7a8b-4c9d-8e0f-1a2b3c4d5e6f |
| 3   | productId         | String: UUID | OPTIONAL  | Sequence Diagram | data.products[].productId         | Product Id, Null when the row names a category                                                       | null                                 |
| 4   | rowStatus         | String       | MANDATORY | Sequence Diagram | data.products[].rowStatus         | Row status of the row                                                                                | ACTIVE                               |

### Example Response Parameters

#### Success - Insert

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Upsert Campaign Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "campaignId": "b1c2d3e4-1a2b-4c3d-8e4f-5a6b7c8d9e01",
        "name": "Black Friday 2026",
        "description": "Four days of discounts on selected products",
        "startAt": "2026-11-27T00:00:00.000Z",
        "endAt": "2026-11-30T23:59:59.000Z",
        "rowStatus": "ACTIVE",
        "budget": {
            "budgetId": "d1a2b3c4-5e6f-4a70-8b81-9c0d1e2f3a41",
            "budget": 50000.0,
            "remaining": 50000.0,
            "used": 0.0,
            "rowStatus": "ACTIVE"
        },
        "discount": {
            "discountId": "d2b3c4d5-6f70-4b81-9c92-0d1e2f3a4b52",
            "discountType": "PERCENTAGE",
            "discountValue": 10.0,
            "rowStatus": "ACTIVE"
        },
        "shops": [
            {
                "campaignShopId": "e1a2b3c4-7081-4c92-8da3-1e2f3a4b5c61",
                "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
                "rowStatus": "ACTIVE"
            }
        ],
        "products": [
            {
                "campaignProductId": "e2b3c4d5-8192-4da3-9eb4-2f3a4b5c6d72",
                "productCategoryId": "3c4d5e6f-7a8b-4c9d-8e0f-1a2b3c4d5e6f",
                "productId": null,
                "rowStatus": "ACTIVE"
            },
            {
                "campaignProductId": "e3c4d5e6-92a3-4eb4-8fc5-3a4b5c6d7e83",
                "productCategoryId": null,
                "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
                "rowStatus": "ACTIVE"
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
        "bizMessage": "Upsert Campaign Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "campaignId": "b1c2d3e4-1a2b-4c3d-8e4f-5a6b7c8d9e01",
        "name": "Black Friday 2026",
        "description": "Four days of discounts on selected products",
        "startAt": "2026-11-27T00:00:00.000Z",
        "endAt": "2026-11-30T23:59:59.000Z",
        "rowStatus": "ACTIVE",
        "budget": {
            "budgetId": "d1a2b3c4-5e6f-4a70-8b81-9c0d1e2f3a41",
            "budget": 60000.0,
            "remaining": 59000.0,
            "used": 1000.0,
            "rowStatus": "ACTIVE"
        },
        "discount": {
            "discountId": "d2b3c4d5-6f70-4b81-9c92-0d1e2f3a4b52",
            "discountType": "PERCENTAGE",
            "discountValue": 15.0,
            "rowStatus": "ACTIVE"
        },
        "shops": [
            {
                "campaignShopId": "e1a2b3c4-7081-4c92-8da3-1e2f3a4b5c61",
                "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
                "rowStatus": "ACTIVE"
            }
        ],
        "products": [
            {
                "campaignProductId": "e2b3c4d5-8192-4da3-9eb4-2f3a4b5c6d72",
                "productCategoryId": "3c4d5e6f-7a8b-4c9d-8e0f-1a2b3c4d5e6f",
                "productId": null,
                "rowStatus": "ACTIVE"
            },
            {
                "campaignProductId": "e3c4d5e6-92a3-4eb4-8fc5-3a4b5c6d7e83",
                "productCategoryId": null,
                "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
                "rowStatus": "ACTIVE"
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
        "bizMessage": "Upsert Campaign Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "campaignId": "b3e4f5a6-3c4d-4e5f-8a61-7c8d9e0f1a23",
        "name": "Singles Day 2026",
        "description": "Four days of discounts on selected products",
        "startAt": "2026-11-11T00:00:00.000Z",
        "endAt": "2026-11-11T23:59:59.000Z",
        "rowStatus": "ARCHIVED",
        "budget": {
            "budgetId": "d1a2b3c4-5e6f-4a70-8b81-9c0d1e2f3a41",
            "budget": 20000.0,
            "remaining": 20000.0,
            "used": 0.0,
            "rowStatus": "ACTIVE"
        },
        "discount": {
            "discountId": "d2b3c4d5-6f70-4b81-9c92-0d1e2f3a4b52",
            "discountType": "FIXED_AMOUNT",
            "discountValue": 30.0,
            "rowStatus": "ACTIVE"
        },
        "shops": [],
        "products": []
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
        "bizMessage": "End At must be after Start At.",
        "requestId": "req-1000a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:00:40.123Z",
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
        "bizMessage": "Row Status DELETED is not allowed when a campaign is inserted.",
        "requestId": "req-1010a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:01:47.123Z",
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
        "bizMessage": "Only a platform administrator can create or change a campaign.",
        "requestId": "req-1030a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:03:01.123Z",
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
        "bizMessage": "Campaign not found.",
        "requestId": "req-1020a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:02:54.123Z",
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
        "bizMessage": "shops[0]: Shop not found.",
        "requestId": "req-1040a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:04:08.123Z",
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
        "bizMessage": "The campaign name Black Friday 2026 already exists.",
        "requestId": "req-1050a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:05:15.123Z",
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
        "bizMessage": "The campaign already used its budget (1000.00), archive it instead of deleting it.",
        "requestId": "req-1060a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:06:22.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict Budget Below Used

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "The budget cannot be below the amount that the orders took (1000.00).",
        "requestId": "req-1070a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:07:29.123Z",
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

### Table: [campaign.m_campaign](../../../schema/campaign/m_campaign.md)

#### QUERY - Check existing campaign

```SQL
SELECT
    c.id as campaign_id,
    c.row_status
FROM campaign.m_campaign c
WHERE c.id = '<sequence.id>'
AND c.row_status <> 'DELETED' -- a DELETED campaign counts as not found
```

#### QUERY - Check duplicate campaign name

```SQL
SELECT
    c.id as campaign_id
FROM campaign.m_campaign c
WHERE c.name = '<sequence.name>'
AND c.row_status <> 'DELETED'
AND c.id <> '<sequence.id>' -- only when id is specified
```

#### INSERT - Create campaign

```SQL
INSERT INTO campaign.m_campaign (created_by, name, description, start_at, end_at, row_status)
VALUES ('<sequence.userId>', '<sequence.name>', '<sequence.description>', '<sequence.startAt>', '<sequence.endAt>', '<sequence.rowStatus>')
RETURNING id as campaign_id, name, description, start_at, end_at, row_status
```

#### UPDATE - Update, delete or archive campaign

```SQL
UPDATE campaign.m_campaign
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    name = '<sequence.name>',
    description = '<sequence.description>',
    start_at = '<sequence.startAt>',
    end_at = '<sequence.endAt>',
    row_status = '<sequence.rowStatus>' -- a delete sets DELETED, an archive sets ARCHIVED
WHERE id = '<sequence.id>'
RETURNING id as campaign_id, name, description, start_at, end_at, row_status
```

### Table: [campaign.m_campaign_budget](../../../schema/campaign/m_campaign_budget.md)

#### QUERY - Check existing budget

```SQL
SELECT
    b.id as budget_id,
    b.budget,
    b.remaining,
    (b.budget - b.remaining) as used
FROM campaign.m_campaign_budget b
WHERE b.campaign_id = '<sequence.campaignId>'
AND b.row_status <> 'DELETED'
AND b.id = '<sequence.budget.id>' -- only when the budget has an id
```

#### INSERT - Create budget

```SQL
INSERT INTO campaign.m_campaign_budget (created_by, campaign_id, budget, remaining, row_status)
VALUES ('<sequence.userId>', '<sequence.campaignId>', '<sequence.budget.budget>', '<sequence.budget.budget>', '<sequence.budget.rowStatus>') -- remaining starts as the whole budget
RETURNING id as budget_id, budget, remaining, row_status
```

#### UPDATE - Change budget

```SQL
UPDATE campaign.m_campaign_budget
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    remaining = '<sequence.budget.budget>' - (budget - remaining), -- keeps what the orders took
    budget = '<sequence.budget.budget>',
    row_status = '<sequence.budget.rowStatus>'
WHERE id = '<sequence.budget.id>'
AND campaign_id = '<sequence.campaignId>'
AND (budget - remaining) <= '<sequence.budget.budget>' -- no row changed means the budget is below the used amount, answer 409 (E10006)
RETURNING id as budget_id, budget, remaining, (budget - remaining) as used, row_status
```

#### UPDATE - Delete the budget of a deleted campaign

```SQL
UPDATE campaign.m_campaign_budget
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'DELETED'
WHERE campaign_id = '<sequence.campaignId>'
AND row_status <> 'DELETED'
```

### Table: [campaign.m_campaign_budget_ledger](../../../schema/campaign/m_campaign_budget_ledger.md)

#### QUERY - Check campaign used

```SQL
SELECT
    l.id as ledger_id
FROM campaign.m_campaign_budget_ledger l
WHERE l.campaign_id = '<sequence.campaignId>'
LIMIT 1 -- a row means an order used the budget, the campaign cannot be deleted (409, E10006)
```

### Table: [campaign.t_campaign_discount](../../../schema/campaign/t_campaign_discount.md)

#### UPDATE - Delete the discount of a deleted campaign

```SQL
UPDATE campaign.t_campaign_discount
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'DELETED'
WHERE campaign_id = '<sequence.campaignId>'
AND row_status <> 'DELETED'
```

#### QUERY - Check existing discount

```SQL
SELECT
    d.id as discount_id
FROM campaign.t_campaign_discount d
WHERE d.campaign_id = '<sequence.campaignId>'
AND d.row_status <> 'DELETED'
AND d.id = '<sequence.discount.id>' -- only when the discount has an id
```

#### INSERT - Create discount

```SQL
INSERT INTO campaign.t_campaign_discount (created_by, campaign_id, discount_type, discount_value, row_status)
VALUES ('<sequence.userId>', '<sequence.campaignId>', '<sequence.discount.discountType>', '<sequence.discount.discountValue>', '<sequence.discount.rowStatus>')
RETURNING id as discount_id, discount_type, discount_value, row_status
```

#### UPDATE - Update or delete discount

```SQL
UPDATE campaign.t_campaign_discount
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    discount_type = '<sequence.discount.discountType>',
    discount_value = '<sequence.discount.discountValue>',
    row_status = '<sequence.discount.rowStatus>'
WHERE id = '<sequence.discount.id>'
AND campaign_id = '<sequence.campaignId>'
RETURNING id as discount_id, discount_type, discount_value, row_status
```

### Table: [campaign.t_campaign_shop](../../../schema/campaign/t_campaign_shop.md)

#### QUERY - Check existing campaign shop

```SQL
SELECT
    cs.id as campaign_shop_id
FROM campaign.t_campaign_shop cs
WHERE cs.campaign_id = '<sequence.campaignId>'
AND cs.row_status <> 'DELETED'
AND cs.id = '<sequence.shops.id>' -- only when the row has an id, no row means the id is not a live row of the campaign
```

#### UPDATE - Delete the shops of a deleted campaign

```SQL
UPDATE campaign.t_campaign_shop
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'DELETED'
WHERE campaign_id = '<sequence.campaignId>'
AND row_status <> 'DELETED'
```

#### QUERY - Check duplicate campaign shop

```SQL
SELECT
    cs.id as campaign_shop_id
FROM campaign.t_campaign_shop cs
WHERE cs.campaign_id = '<sequence.campaignId>'
AND cs.shop_id = '<sequence.shops.shopId>'
AND cs.row_status <> 'DELETED'
AND cs.id <> '<sequence.shops.id>' -- only when the row has an id
```

#### INSERT - Create campaign shop

```SQL
INSERT INTO campaign.t_campaign_shop (created_by, campaign_id, shop_id, row_status)
VALUES ('<sequence.userId>', '<sequence.campaignId>', '<sequence.shops.shopId>', '<sequence.shops.rowStatus>')
RETURNING id as campaign_shop_id, shop_id, row_status
```

#### UPDATE - Update or delete campaign shop

```SQL
UPDATE campaign.t_campaign_shop
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.shops.rowStatus>'
WHERE id = '<sequence.shops.id>'
AND campaign_id = '<sequence.campaignId>'
RETURNING id as campaign_shop_id, shop_id, row_status
```

### Table: [campaign.t_campaign_product](../../../schema/campaign/t_campaign_product.md)

#### QUERY - Check existing campaign product

```SQL
SELECT
    cp.id as campaign_product_id
FROM campaign.t_campaign_product cp
WHERE cp.campaign_id = '<sequence.campaignId>'
AND cp.row_status <> 'DELETED'
AND cp.id = '<sequence.products.id>' -- only when the row has an id, no row means the id is not a live row of the campaign
```

#### UPDATE - Delete the products of a deleted campaign

```SQL
UPDATE campaign.t_campaign_product
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'DELETED'
WHERE campaign_id = '<sequence.campaignId>'
AND row_status <> 'DELETED'
```

#### QUERY - Check duplicate campaign product

```SQL
SELECT
    cp.id as campaign_product_id
FROM campaign.t_campaign_product cp
WHERE cp.campaign_id = '<sequence.campaignId>'
AND cp.row_status <> 'DELETED'
AND cp.product_id = '<sequence.products.productId>' -- only when the row names a product
AND cp.product_category_id = '<sequence.products.productCategoryId>' -- only when the row names a category
AND cp.id <> '<sequence.products.id>' -- only when the row has an id
```

#### INSERT - Create campaign product

```SQL
INSERT INTO campaign.t_campaign_product (created_by, campaign_id, product_category_id, product_id, row_status)
VALUES ('<sequence.userId>', '<sequence.campaignId>', '<sequence.products.productCategoryId>', '<sequence.products.productId>', '<sequence.products.rowStatus>')
RETURNING id as campaign_product_id, product_category_id, product_id, row_status
```

#### UPDATE - Update or delete campaign product

```SQL
UPDATE campaign.t_campaign_product
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.products.rowStatus>'
WHERE id = '<sequence.products.id>'
AND campaign_id = '<sequence.campaignId>'
RETURNING id as campaign_product_id, product_category_id, product_id, row_status
```

### Table: [shop.m_shop](../../../schema/shop/m_shop.md)

#### QUERY - Check shop

```SQL
SELECT
    s.id as shop_id
FROM shop.m_shop s
WHERE s.id = '<sequence.shops.shopId>'
AND s.row_status <> 'DELETED'
```

### Table: [product.m_product](../../../schema/product/m_product.md)

#### QUERY - Check product

```SQL
SELECT
    p.id as product_id
FROM product.m_product p
WHERE p.id = '<sequence.products.productId>'
AND p.row_status <> 'DELETED'
```

### Table: [product.m_product_category](../../../schema/product/m_product_category.md)

#### QUERY - Check product category

```SQL
SELECT
    pc.id as product_category_id
FROM product.m_product_category pc
WHERE pc.id = '<sequence.products.productCategoryId>'
AND pc.row_status <> 'DELETED'
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
