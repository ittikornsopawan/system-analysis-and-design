# [GET]: v1/campaign

| Title       | Description                                                                                                                                                                                                                                 |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Campaign API                                                                                                                                                                                                                        |
| Method      | GET                                                                                                                                                                                                                                         |
| Endpoint    | v{version}/campaign                                                                                                                                                                                                                         |
| Version     | 1                                                                                                                                                                                                                                           |
| Description | Inquiry the campaigns with their discount, products, and for a platform administrator the budget and the shops, A member of a shop sees the campaigns that apply to the shop and no budget, Filter by id, status, time (activeOnly) or name |

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

|     | Parameter Name | Data Type    | M/O      | Description                                                                                                               | Example                              |
| --- | -------------- | ------------ | -------- | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | shopId         | String: UUID | OPTIONAL | Shop Id, a platform administrator may omit it, any other caller must send the shop that the caller is an ACTIVE member of | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 2   | id             | String: UUID | OPTIONAL | Campaign Id, Response is a list with one item                                                                             | b1c2d3e4-1a2b-4c3d-8e4f-5a6b7c8d9e01 |
| 3   | status         | String       | OPTIONAL | Row status filter (ACTIVE, INACTIVE, LOCKED, ARCHIVED), All statuses that are not DELETED when not specified              | ACTIVE                               |
| 4   | activeOnly     | Boolean      | OPTIONAL | true = only campaigns with row status ACTIVE whose time covers now, Defaults to false                                     | true                                 |
| 5   | pageIndex      | Numeric      | OPTIONAL | Page index starting from 1, Defaults to 1                                                                                 | 1                                    |
| 6   | pageSize       | Numeric      | OPTIONAL | Number of items per page (max 100), Defaults to 10                                                                        | 10                                   |
| 7   | search         | String       | OPTIONAL | Search by campaign name                                                                                                   | Friday                               |

### Campaign Inquiry Rules

- A platform administrator (a user that has the role `PLATFORM_ADMIN`) sees every campaign that is not DELETED with its budget, its remaining amount and its shops. Any other caller must send `shopId` of a shop that the caller is an ACTIVE member of (a row of `shop.t_shop_user` with the role ADMIN or STAFF that is ACTIVE), otherwise 403 (E10009), and sees only the campaigns that apply to that shop: the shop is in a live `t_campaign_shop` row of the campaign, or the campaign has no live shop row (it is for every shop, C2). A shop that does not exist or is DELETED is not found (404, E10005). This permission model was approved by the product owner.
- The members of a shop never see `budget` and the shop list, both are returned as `null` and the keys stay. They see the discount and the products and categories of the campaign. Campaigns with `rowStatus` DELETED are never returned.
- `activeOnly` keeps the campaigns that give discounts right now: `row_status = 'ACTIVE'` and `start_at <= now < end_at` (UTC). Campaigns are ordered by `start_at` (newest first) then `id`. `search` matches the name (case-insensitive, partial). Nothing found is 200 with an empty list.
- Execution order: validate the request (400) -> existence of the shop (404) -> permission (403) -> read.
- This behaviour follows `docs/superpowers/specs/2026-11-06-campaign-design.md`, approved by the product owner on 2026-11-06 (the proposals to the delivered specs in its section 4 are decided by the lead SA).

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/campaign?activeOnly=true&search=Friday&pageIndex=1&pageSize=10 HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/campaign?activeOnly=true&search=Friday&pageIndex=1&pageSize=10' \
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
| 1   | campaigns      | [Array of Campaign](#campaign-object) | MANDATORY | Sequence Diagram | data.campaigns  | Campaigns of the page     |         |
| 2   | pageIndex      | Numeric                               | MANDATORY | Sequence Diagram | data.pageIndex  | Page index                | 1       |
| 3   | pageSize       | Numeric                               | MANDATORY | Sequence Diagram | data.pageSize   | Page size                 | 10      |
| 4   | totalItems     | Numeric                               | MANDATORY | Sequence Diagram | data.totalItems | Total number of campaigns | 1       |
| 5   | totalPages     | Numeric                               | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages     | 1       |

#### Campaign Object

|     | Parameter Name | Data Type                              | M/O       | Source           | Field                        | Description                                                           | Example                                     |
| --- | -------------- | -------------------------------------- | --------- | ---------------- | ---------------------------- | --------------------------------------------------------------------- | ------------------------------------------- |
| 1   | campaignId     | String: UUID                           | MANDATORY | Sequence Diagram | data.campaigns[].campaignId  | Campaign Id                                                           | b1c2d3e4-1a2b-4c3d-8e4f-5a6b7c8d9e01        |
| 2   | name           | String                                 | MANDATORY | Sequence Diagram | data.campaigns[].name        | Campaign name                                                         | Black Friday 2026                           |
| 3   | description    | String                                 | OPTIONAL  | Sequence Diagram | data.campaigns[].description | Description                                                           | Four days of discounts on selected products |
| 4   | startAt        | String: TIMESTAMP                      | MANDATORY | Sequence Diagram | data.campaigns[].startAt     | The campaign gives discounts from this time (UTC)                     | 2026-11-27T00:00:00.000Z                    |
| 5   | endAt          | String: TIMESTAMP                      | MANDATORY | Sequence Diagram | data.campaigns[].endAt       | The campaign gives discounts until this time, not including it (UTC)  | 2026-11-30T23:59:59.000Z                    |
| 6   | rowStatus      | String                                 | MANDATORY | Sequence Diagram | data.campaigns[].rowStatus   | Row status of the campaign                                            | ACTIVE                                      |
| 7   | budget         | [Object of Budget](#budget-object)     | OPTIONAL  | Sequence Diagram | data.campaigns[].budget      | Budget of the campaign, Null for members of a shop                    |                                             |
| 8   | discount       | [Object of Discount](#discount-object) | MANDATORY | Sequence Diagram | data.campaigns[].discount    | The discount of the campaign                                          |                                             |
| 9   | shops          | [Array of Shop](#shop-object)          | OPTIONAL  | Sequence Diagram | data.campaigns[].shops       | Shops of the campaign, Empty = every shop, Null for members of a shop |                                             |
| 10  | products       | [Array of Product](#product-object)    | MANDATORY | Sequence Diagram | data.campaigns[].products    | Products and categories of the campaign, Empty = every product        |                                             |

#### Budget Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                             | Description                                                                    | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | --------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------ |
| 1   | budgetId       | String: UUID | MANDATORY | Sequence Diagram | data.campaigns[].budget.budgetId  | Budget Id                                                                      | d1a2b3c4-5e6f-4a70-8b81-9c0d1e2f3a41 |
| 2   | budget         | Numeric      | MANDATORY | Sequence Diagram | data.campaigns[].budget.budget    | Amount of the budget                                                           | 60000.00                             |
| 3   | remaining      | Numeric      | MANDATORY | Sequence Diagram | data.campaigns[].budget.remaining | Amount that no order has taken                                                 | 59000.00                             |
| 4   | used           | Numeric      | MANDATORY | Sequence Diagram | data.campaigns[].budget.used      | budget - remaining, what the orders took (reservations that were not released) | 1000.00                              |
| 5   | rowStatus      | String       | MANDATORY | Sequence Diagram | data.campaigns[].budget.rowStatus | Row status of the budget                                                       | ACTIVE                               |

#### Discount Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                                   | Description                                    | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | --------------------------------------- | ---------------------------------------------- | ------------------------------------ |
| 1   | discountId     | String: UUID | MANDATORY | Sequence Diagram | data.campaigns[].discount.discountId    | Discount Id                                    | d2b3c4d5-6f70-4b81-9c92-0d1e2f3a4b52 |
| 2   | discountType   | String       | MANDATORY | Sequence Diagram | data.campaigns[].discount.discountType  | PERCENTAGE or FIXED_AMOUNT                     | PERCENTAGE                           |
| 3   | discountValue  | Numeric      | MANDATORY | Sequence Diagram | data.campaigns[].discount.discountValue | Percent (up to 100) or amount in baht per unit | 15.00                                |
| 4   | rowStatus      | String       | MANDATORY | Sequence Diagram | data.campaigns[].discount.rowStatus     | Row status of the discount                     | ACTIVE                               |

#### Shop Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                                   | Description           | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | --------------------------------------- | --------------------- | ------------------------------------ |
| 1   | campaignShopId | String: UUID | MANDATORY | Sequence Diagram | data.campaigns[].shops[].campaignShopId | Campaign shop row Id  | e1a2b3c4-7081-4c92-8da3-1e2f3a4b5c61 |
| 2   | shopId         | String: UUID | MANDATORY | Sequence Diagram | data.campaigns[].shops[].shopId         | Shop Id               | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 3   | rowStatus      | String       | MANDATORY | Sequence Diagram | data.campaigns[].shops[].rowStatus      | Row status of the row | ACTIVE                               |

#### Product Object

|     | Parameter Name    | Data Type    | M/O       | Source           | Field                                         | Description                                                                                          | Example                              |
| --- | ----------------- | ------------ | --------- | ---------------- | --------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | campaignProductId | String: UUID | MANDATORY | Sequence Diagram | data.campaigns[].products[].campaignProductId | Campaign product row Id                                                                              | e2b3c4d5-8192-4da3-9eb4-2f3a4b5c6d72 |
| 2   | productCategoryId | String: UUID | OPTIONAL  | Sequence Diagram | data.campaigns[].products[].productCategoryId | Product category Id (the category itself, not its sub categories), Null when the row names a product | 3c4d5e6f-7a8b-4c9d-8e0f-1a2b3c4d5e6f |
| 3   | productId         | String: UUID | OPTIONAL  | Sequence Diagram | data.campaigns[].products[].productId         | Product Id, Null when the row names a category                                                       | null                                 |
| 4   | rowStatus         | String       | MANDATORY | Sequence Diagram | data.campaigns[].products[].rowStatus         | Row status of the row                                                                                | ACTIVE                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Campaign Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "campaigns": [
            {
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
        ],
        "pageIndex": 1,
        "pageSize": 10,
        "totalItems": 1,
        "totalPages": 1
    }
}
```

#### Success - Shop

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Campaign Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "campaigns": [
            {
                "campaignId": "b1c2d3e4-1a2b-4c3d-8e4f-5a6b7c8d9e01",
                "name": "Black Friday 2026",
                "description": "Four days of discounts on selected products",
                "startAt": "2026-11-27T00:00:00.000Z",
                "endAt": "2026-11-30T23:59:59.000Z",
                "rowStatus": "ACTIVE",
                "budget": null,
                "discount": {
                    "discountId": "d2b3c4d5-6f70-4b81-9c92-0d1e2f3a4b52",
                    "discountType": "PERCENTAGE",
                    "discountValue": 15.0,
                    "rowStatus": "ACTIVE"
                },
                "shops": null,
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
            },
            {
                "campaignId": "b4f5a6b7-4d5e-4f60-9b72-8d9e0f1a2b34",
                "name": "Free Shipping Week",
                "description": null,
                "startAt": "2026-11-20T00:00:00.000Z",
                "endAt": "2026-11-26T23:59:59.000Z",
                "rowStatus": "ACTIVE",
                "budget": null,
                "discount": {
                    "discountId": "d3c4d5e6-7081-4c92-8da3-1e2f3a4b5c63",
                    "discountType": "FIXED_AMOUNT",
                    "discountValue": 20.0,
                    "rowStatus": "ACTIVE"
                },
                "shops": null,
                "products": []
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
        "bizMessage": "Inquiry Campaign Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "campaigns": [],
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
        "requestId": "req-1100a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:10:50.123Z",
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
        "bizMessage": "Only a platform administrator or a member of the shop can read the campaigns.",
        "requestId": "req-1130a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:13:11.123Z",
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
        "requestId": "req-1120a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:12:04.123Z",
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

### Table: [campaign.m_campaign](../../../schema/campaign/m_campaign.md)

#### QUERY - Get the campaigns

```SQL
SELECT
    c.id as campaign_id,
    c.name,
    c.description,
    c.start_at,
    c.end_at,
    c.row_status
FROM campaign.m_campaign c
WHERE c.row_status <> 'DELETED'
AND c.id = '<sequence.id>' -- only when id is specified
AND c.row_status = '<sequence.status>' -- only when status is specified
AND c.row_status = 'ACTIVE' AND c.start_at <= NOW() AT TIME ZONE 'UTC' AND NOW() AT TIME ZONE 'UTC' < c.end_at -- only when activeOnly is true
AND c.name ILIKE '%<sequence.search>%' -- only when search is specified
AND (EXISTS (
        SELECT 1
        FROM campaign.t_campaign_shop cs
        WHERE cs.campaign_id = c.id
        AND cs.shop_id = '<sequence.shopId>'
        AND cs.row_status = 'ACTIVE'
    ) OR NOT EXISTS (
        SELECT 1
        FROM campaign.t_campaign_shop cs
        WHERE cs.campaign_id = c.id
        AND cs.row_status = 'ACTIVE'
    )) -- only when the caller is not a platform administrator
ORDER BY c.start_at DESC, c.id
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Count the campaigns

```SQL
SELECT
    COUNT(c.id) as total_items
FROM campaign.m_campaign c
WHERE c.row_status <> 'DELETED'
AND c.id = '<sequence.id>' -- only when id is specified
AND c.row_status = '<sequence.status>' -- only when status is specified
AND c.row_status = 'ACTIVE' AND c.start_at <= NOW() AT TIME ZONE 'UTC' AND NOW() AT TIME ZONE 'UTC' < c.end_at -- only when activeOnly is true
AND c.name ILIKE '%<sequence.search>%' -- only when search is specified
AND (EXISTS (
        SELECT 1
        FROM campaign.t_campaign_shop cs
        WHERE cs.campaign_id = c.id
        AND cs.shop_id = '<sequence.shopId>'
        AND cs.row_status = 'ACTIVE'
    ) OR NOT EXISTS (
        SELECT 1
        FROM campaign.t_campaign_shop cs
        WHERE cs.campaign_id = c.id
        AND cs.row_status = 'ACTIVE'
    )) -- only when the caller is not a platform administrator
```

### Table: [campaign.m_campaign_budget](../../../schema/campaign/m_campaign_budget.md)

#### QUERY - Get the budgets of the campaigns

```SQL
SELECT
    b.id as budget_id,
    b.campaign_id,
    b.budget,
    b.remaining,
    (b.budget - b.remaining) as used,
    b.row_status -- returned only to a platform administrator
FROM campaign.m_campaign_budget b
WHERE b.campaign_id IN ('<sequence.campaignIds>')
AND b.row_status <> 'DELETED'
```

### Table: [campaign.t_campaign_discount](../../../schema/campaign/t_campaign_discount.md)

#### QUERY - Get the discounts of the campaigns

```SQL
SELECT
    d.id as discount_id,
    d.campaign_id,
    d.discount_type,
    d.discount_value,
    d.row_status
FROM campaign.t_campaign_discount d
WHERE d.campaign_id IN ('<sequence.campaignIds>')
AND d.row_status <> 'DELETED'
```

### Table: [campaign.t_campaign_shop](../../../schema/campaign/t_campaign_shop.md)

#### QUERY - Get the shops of the campaigns

```SQL
SELECT
    cs.id as campaign_shop_id,
    cs.campaign_id,
    cs.shop_id,
    cs.row_status -- returned only to a platform administrator
FROM campaign.t_campaign_shop cs
WHERE cs.campaign_id IN ('<sequence.campaignIds>')
AND cs.row_status <> 'DELETED'
ORDER BY cs.created_at, cs.id
```

### Table: [campaign.t_campaign_product](../../../schema/campaign/t_campaign_product.md)

#### QUERY - Get the products of the campaigns

```SQL
SELECT
    cp.id as campaign_product_id,
    cp.campaign_id,
    cp.product_category_id,
    cp.product_id,
    cp.row_status
FROM campaign.t_campaign_product cp
WHERE cp.campaign_id IN ('<sequence.campaignIds>')
AND cp.row_status <> 'DELETED'
ORDER BY cp.created_at, cp.id
```
