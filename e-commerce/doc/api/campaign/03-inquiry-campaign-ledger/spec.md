# [GET]: v1/campaign/ledger

| Title       | Description                                                                                                                                                         |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Campaign Ledger API                                                                                                                                         |
| Method      | GET                                                                                                                                                                 |
| Endpoint    | v{version}/campaign/ledger                                                                                                                                          |
| Version     | 1                                                                                                                                                                   |
| Description | Inquiry the budget ledger of a campaign (the reservations and the releases with the order and the discount of each item), Only a platform administrator can call it |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- Only a platform administrator (a user that has the role `PLATFORM_ADMIN`) can call this API, any other user gets 403 (E10009). This permission model was approved by the product owner.
- The ledger of the budget of the campaign: every time an order takes the budget there is a `RESERVE` row, and every time the budget goes back (the order was cancelled or expired, or the payment was refunded) a `RELEASE` row. `usage` is the amount of the entry, always positive, the direction is `entryType`. `remaining` is the remaining amount of the budget after that entry. `reference` lists the order items and the discount each of them got. The system writes the rows, this API only reads them.
- The invariant `budget - remaining = sum of RESERVE usage - sum of RELEASE usage` holds for the budget at any time, the entry with the newest `createdAt` shows the current `remaining` of the budget. Entries are ordered by `created_at` (newest first) then `id`. A campaign that does not exist or is DELETED is not found (404, E10004). Nothing found is 200 with an empty list.
- This behaviour follows the campaign design, approved by the product owner on 2026-11-06 (the proposals to the delivered specs in its section 4 are decided by the lead SA).

---

## Request Parameters

### Header Parameters

|     | Parameter Name | Data Type | M/O       | Description                  | Example                                        |
| --- | -------------- | --------- | --------- | ---------------------------- | ---------------------------------------------- |
| 1   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-06T09:00:00.123Z                       |
| 3   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Query Parameters

|     | Parameter Name | Data Type    | M/O       | Description                                        | Example                              |
| --- | -------------- | ------------ | --------- | -------------------------------------------------- | ------------------------------------ |
| 1   | campaignId     | String: UUID | MANDATORY | Campaign Id                                        | b1c2d3e4-1a2b-4c3d-8e4f-5a6b7c8d9e01 |
| 2   | entryType      | String       | OPTIONAL  | RESERVE or RELEASE, Both when not specified        | RESERVE                              |
| 3   | orderId        | String: UUID | OPTIONAL  | Order Id                                           | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 4   | pageIndex      | Numeric      | OPTIONAL  | Page index starting from 1, Defaults to 1          | 1                                    |
| 5   | pageSize       | Numeric      | OPTIONAL  | Number of items per page (max 100), Defaults to 10 | 10                                   |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/campaign/ledger?campaignId=b1c2d3e4-1a2b-4c3d-8e4f-5a6b7c8d9e01&orderId=d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01&pageIndex=1&pageSize=10 HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/campaign/ledger?campaignId=b1c2d3e4-1a2b-4c3d-8e4f-5a6b7c8d9e01&orderId=d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01&pageIndex=1&pageSize=10' \
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

|     | Parameter Name | Data Type                       | M/O       | Source           | Field           | Description                | Example |
| --- | -------------- | ------------------------------- | --------- | ---------------- | --------------- | -------------------------- | ------- |
| 1   | entries        | [Array of Entry](#entry-object) | MANDATORY | Sequence Diagram | data.entries    | Ledger entries of the page |         |
| 2   | pageIndex      | Numeric                         | MANDATORY | Sequence Diagram | data.pageIndex  | Page index                 | 1       |
| 3   | pageSize       | Numeric                         | MANDATORY | Sequence Diagram | data.pageSize   | Page size                  | 10      |
| 4   | totalItems     | Numeric                         | MANDATORY | Sequence Diagram | data.totalItems | Total number of entries    | 2       |
| 5   | totalPages     | Numeric                         | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages      | 1       |

#### Entry Object

|     | Parameter Name   | Data Type                               | M/O       | Source           | Field                           | Description                                    | Example                              |
| --- | ---------------- | --------------------------------------- | --------- | ---------------- | ------------------------------- | ---------------------------------------------- | ------------------------------------ |
| 1   | ledgerId         | String: UUID                            | MANDATORY | Sequence Diagram | data.entries[].ledgerId         | Ledger entry Id                                | f1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e51 |
| 2   | campaignBudgetId | String: UUID                            | MANDATORY | Sequence Diagram | data.entries[].campaignBudgetId | Budget Id                                      | d1a2b3c4-5e6f-4a70-8b81-9c0d1e2f3a41 |
| 3   | campaignId       | String: UUID                            | MANDATORY | Sequence Diagram | data.entries[].campaignId       | Campaign Id                                    | b1c2d3e4-1a2b-4c3d-8e4f-5a6b7c8d9e01 |
| 4   | orderId          | String: UUID                            | MANDATORY | Sequence Diagram | data.entries[].orderId          | Order Id that took or gave back the budget     | d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01 |
| 5   | entryType        | String                                  | MANDATORY | Sequence Diagram | data.entries[].entryType        | RESERVE or RELEASE                             | RESERVE                              |
| 6   | usage            | Numeric                                 | MANDATORY | Sequence Diagram | data.entries[].usage            | Amount of the entry, always positive           | 61.70                                |
| 7   | remaining        | Numeric                                 | MANDATORY | Sequence Diagram | data.entries[].remaining        | Remaining amount of the budget after the entry | 58938.30                             |
| 8   | reference        | [Array of Reference](#reference-object) | MANDATORY | Sequence Diagram | data.entries[].reference        | Order items and the discount of each           |                                      |
| 9   | createdAt        | String: TIMESTAMP                       | MANDATORY | Sequence Diagram | data.entries[].createdAt        | Time of the entry (UTC)                        | 2026-11-28T09:00:00.123Z             |

#### Reference Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                                  | Description                                | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | -------------------------------------- | ------------------------------------------ | ------------------------------------ |
| 1   | orderItemId    | String: UUID | MANDATORY | Sequence Diagram | data.entries[].reference[].orderItemId | Order Item Id                              | e1f2a3b4-3c4d-4e5f-9a6b-7c8d9e0f1a21 |
| 2   | discount       | Numeric      | MANDATORY | Sequence Diagram | data.entries[].reference[].discount    | Discount of the item taken from the budget | 39.80                                |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Campaign Ledger Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "entries": [
            {
                "ledgerId": "f2e3f4a5-b6c7-4d8e-9fa0-1b2c3d4e5f62",
                "campaignBudgetId": "d1a2b3c4-5e6f-4a70-8b81-9c0d1e2f3a41",
                "campaignId": "b1c2d3e4-1a2b-4c3d-8e4f-5a6b7c8d9e01",
                "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
                "entryType": "RELEASE",
                "usage": 61.7,
                "remaining": 59000.0,
                "reference": [
                    {
                        "orderItemId": "e1f2a3b4-3c4d-4e5f-9a6b-7c8d9e0f1a21",
                        "discount": 39.8
                    },
                    {
                        "orderItemId": "e2a3b4c5-4d5e-4f60-8b7c-8d9e0f1a2b32",
                        "discount": 21.9
                    }
                ],
                "createdAt": "2026-11-28T09:30:00.123Z"
            },
            {
                "ledgerId": "f1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e51",
                "campaignBudgetId": "d1a2b3c4-5e6f-4a70-8b81-9c0d1e2f3a41",
                "campaignId": "b1c2d3e4-1a2b-4c3d-8e4f-5a6b7c8d9e01",
                "orderId": "d1e2f3a4-1b2c-4d3e-9f4a-5b6c7d8e9f01",
                "entryType": "RESERVE",
                "usage": 61.7,
                "remaining": 58938.3,
                "reference": [
                    {
                        "orderItemId": "e1f2a3b4-3c4d-4e5f-9a6b-7c8d9e0f1a21",
                        "discount": 39.8
                    },
                    {
                        "orderItemId": "e2a3b4c5-4d5e-4f60-8b7c-8d9e0f1a2b32",
                        "discount": 21.9
                    }
                ],
                "createdAt": "2026-11-28T09:00:00.123Z"
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
        "bizMessage": "Inquiry Campaign Ledger Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "entries": [],
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
        "bizMessage": "Campaign Id is a required field and must be a valid UUID.",
        "requestId": "req-1200a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:20:00.123Z",
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
        "bizMessage": "Only a platform administrator can read the ledger of a campaign.",
        "requestId": "req-1230a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:23:21.123Z",
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
        "requestId": "req-1220a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:22:14.123Z",
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

#### QUERY - Check campaign

```SQL
SELECT
    c.id as campaign_id
FROM campaign.m_campaign c
WHERE c.id = '<sequence.campaignId>'
AND c.row_status <> 'DELETED'
```

### Table: [campaign.m_campaign_budget_ledger](../../../schema/campaign/m_campaign_budget_ledger.md)

#### QUERY - Get the ledger entries

```SQL
SELECT
    l.id as ledger_id,
    l.campaign_budget_id,
    l.campaign_id,
    l.order_id,
    l.entry_type,
    l.usage,
    l.remaining,
    l.reference,
    l.created_at
FROM campaign.m_campaign_budget_ledger l
WHERE l.campaign_id = '<sequence.campaignId>'
AND l.entry_type = '<sequence.entryType>' -- only when entryType is specified
AND l.order_id = '<sequence.orderId>' -- only when orderId is specified
ORDER BY l.created_at DESC, l.id
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Count the ledger entries

```SQL
SELECT
    COUNT(l.id) as total_items
FROM campaign.m_campaign_budget_ledger l
WHERE l.campaign_id = '<sequence.campaignId>'
AND l.entry_type = '<sequence.entryType>' -- only when entryType is specified
AND l.order_id = '<sequence.orderId>' -- only when orderId is specified
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
