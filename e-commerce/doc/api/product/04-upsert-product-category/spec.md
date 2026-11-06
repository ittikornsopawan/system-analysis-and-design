# [POST]: v1/product-category/upsert

| Title       | Description                                                                                                                                                                                                                        |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Product Category API                                                                                                                                                                                                        |
| Method      | POST                                                                                                                                                                                                                               |
| Endpoint    | v{version}/product-category/upsert                                                                                                                                                                                                 |
| Version     | 1                                                                                                                                                                                                                                  |
| Description | Insert, update or delete a product category, Insert when id is not specified, Update when id is specified, Delete when rowStatus is DELETED (HTTP 204 No Content, no response body), Archive when rowStatus is ARCHIVED (HTTP 200) |

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
| 3   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-05T12:42:00.123Z                       |
| 4   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Body Parameters

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                                   | Example                               |
| --- | -------------- | ------------ | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| 1   | id             | String: UUID | OPTIONAL  | Product Category Id, Insert when not specified, Update or Delete when specified                                                                                                                               | b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e  |
| 2   | parentId       | String: UUID | OPTIONAL  | Parent Product Category Id, Root category when not specified, Must be an existing category and must not be the category itself or its sub category                                                            | a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d  |
| 3   | name           | String       | MANDATORY | Product Category Name (max 128 characters), Unique                                                                                                                                                            | Computer Accessories                  |
| 4   | description    | String       | MANDATORY | Product Category Description (max 256 characters)                                                                                                                                                             | Accessories for computers and laptops |
| 5   | slug           | String       | OPTIONAL  | URL friendly name (max 128 characters, a-z, 0-9 and hyphen), Used in the web URL /{id}/{slug}, Generated from name when not specified on insert, Keep the current slug when not specified on update           | computer-accessories                  |
| 6   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, Delete is allowed only when the category is not used by any product or sub category | ACTIVE                                |

### Campaign Rules

- A product category cannot be deleted while it is in a campaign that is not DELETED and has not ended (a live `campaign.t_campaign_product` row of a campaign whose `end_at` is after now), 409 (E10006) with the campaign name in the message. Take it out of the campaign first with the upsert campaign API (a campaign that ended or was deleted does not block). Archiving is always allowed. (`docs/superpowers/specs/2026-11-06-campaign-design.md`, C13, approved by the product owner on 2026-11-06)

#### Example Body Parameters

##### Insert

```JSON
{
    "parentId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
    "name": "Computer Accessories",
    "description": "Accessories for computers and laptops",
    "slug": "computer-accessories",
    "rowStatus": "ACTIVE"
}
```

##### Update

```JSON
{
    "id": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
    "parentId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
    "name": "Computer Peripherals",
    "description": "Accessories for computers and laptops",
    "slug": "computer-peripherals",
    "rowStatus": "ACTIVE"
}
```

##### Delete

```JSON
{
    "id": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
    "parentId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
    "name": "Computer Peripherals",
    "description": "Accessories for computers and laptops",
    "slug": "computer-peripherals",
    "rowStatus": "DELETED"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/product-category/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "parentId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
    "name": "Computer Accessories",
    "description": "Accessories for computers and laptops",
    "slug": "computer-accessories",
    "rowStatus": "ACTIVE"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/product-category/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "parentId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
    "name": "Computer Accessories",
    "description": "Accessories for computers and laptops",
    "slug": "computer-accessories",
    "rowStatus": "ACTIVE"
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
| 6   | timestamp      | String: TIMESTAMP | MANDATORY | Sequence Diagram | response.status.timestamp  | API Request Timestamp (Without time zone UTC) | 2026-11-05T12:42:00.123Z                 |
| 7   | status         | String            | MANDATORY | Sequence Diagram | response.status.status     | API Request Status (SUCCESS, ERROR)           | SUCCESS                                  |

### Data Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field           | Description                                                                             | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | --------------- | --------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | categoryId     | String: UUID | MANDATORY | Sequence Diagram | data.categoryId | Inserted, Updated or Archived Product Category Id, Not returned when deleted (HTTP 204) | b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e |

### Example Response Parameters

#### Success - Insert

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Insert Product Category Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e"
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
        "bizMessage": "Update Product Category Success",
        "requestId": "req-5c3d9e1f-2a4b-4c6d-8e0f-1a2b3c4d5e6f",
        "timestamp": "2026-11-05T12:50:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e"
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
        "bizMessage": "Archive Product Category Success",
        "requestId": "req-7e5f1a3b-4c6d-4e8f-8a2b-3c4d5e6f7a8b",
        "timestamp": "2026-11-05T12:57:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e"
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
        "bizMessage": "Name and Description are required fields.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:40.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Parent

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Parent category must not be the category itself or its sub category.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:47.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Slug

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Slug must contain only a-z, 0-9 and hyphen, and must not be longer than 128 characters.",
        "requestId": "req-460a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:22.123Z",
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
        "requestId": "req-7a2cba3e-1b2d-4caf-8cce-3b1d7b3dcb6d",
        "timestamp": "2026-11-05T12:43:10.456Z",
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
        "bizMessage": "Product category not found.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:40:54.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Parent

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "Parent product category not found.",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:41:01.123Z",
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
        "bizMessage": "Product category name already exists.",
        "requestId": "req-440a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:42:08.123Z",
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
        "bizMessage": "Product category is used by products or sub categories.",
        "requestId": "req-450a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:15.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict Campaign In Use

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "The product category is in a campaign that has not ended (Black Friday 2026) and cannot be deleted.",
        "requestId": "req-510a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:01:57.123Z",
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
        "requestId": "req-408a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:30.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

### Table: [product.m_product_category](../../../schema/product/m_product_category.md)

#### QUERY - Check parent category

```SQL
SELECT
    pc.id as parent_id
FROM product.m_product_category pc
WHERE pc.id = '<sequence.parentId>' -- only when parentId is specified
AND pc.row_status = 'ACTIVE'
```

#### QUERY - Check existing category

```SQL
SELECT
    pc.id as category_id
FROM product.m_product_category pc
WHERE pc.id = '<sequence.id>'
```

#### QUERY - Check duplicate name

```SQL
SELECT
    pc.id as category_id
FROM product.m_product_category pc
WHERE pc.name = '<sequence.name>'
AND pc.id <> '<sequence.id>' -- only when id is specified
```

#### QUERY - Check parent is not the category itself or its sub category

```SQL
WITH RECURSIVE descendants AS (
    SELECT pc.id
    FROM product.m_product_category pc
    WHERE pc.id = '<sequence.id>'
    UNION ALL
    SELECT pc.id
    FROM product.m_product_category pc
    INNER JOIN descendants d
        ON pc.parent_id = d.id
)
SELECT
    d.id as category_id
FROM descendants d
WHERE d.id = '<sequence.parentId>'
```

#### QUERY - Check sub category in use

```SQL
SELECT
    pc.id as category_id
FROM product.m_product_category pc
WHERE pc.parent_id = '<sequence.id>'
AND pc.row_status <> 'DELETED'
```

#### INSERT - Create category

```SQL
INSERT INTO product.m_product_category (
    created_by,
    row_status,
    parent_id,
    name,
    description,
    slug
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.rowStatus>',
    '<sequence.parentId>',
    '<sequence.name>',
    '<sequence.description>',
    '<sequence.slug>'
)
RETURNING id as category_id
```

#### UPDATE - Update or delete category

```SQL
UPDATE product.m_product_category
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.rowStatus>',
    parent_id = '<sequence.parentId>',
    name = '<sequence.name>',
    description = '<sequence.description>',
    slug = '<sequence.slug>' -- only when slug is specified
WHERE id = '<sequence.id>'
RETURNING id as category_id
```

### Table: [product.m_product](../../../schema/product/m_product.md)

#### QUERY - Check product in use

```SQL
SELECT
    p.id as product_id
FROM product.m_product p
WHERE p.category_id = '<sequence.id>'
AND p.row_status <> 'DELETED'
```

### Table: [campaign.t_campaign_product](../../../schema/campaign/t_campaign_product.md)

#### QUERY - Check product category campaigns in use

```SQL
SELECT
    cp.id as campaign_product_id,
    c.name
FROM campaign.t_campaign_product cp
INNER JOIN campaign.m_campaign c
    ON c.id = cp.campaign_id
WHERE cp.product_category_id = '<sequence.id>'
AND cp.row_status <> 'DELETED'
AND c.row_status <> 'DELETED'
AND c.end_at > NOW() AT TIME ZONE 'UTC' -- a campaign that ended or was deleted does not block, answer 409 (E10006) when a row is found
LIMIT 1
```
