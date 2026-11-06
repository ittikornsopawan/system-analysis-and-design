# [POST]: v1/product-brand/upsert/batch

| Title       | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Product Brand Batch API                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Method      | POST                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Endpoint    | v{version}/product-brand/upsert/batch                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Description | Insert, update or delete multiple product brands at the same time, only a platform administrator can call it, Each product brand is inserted when id is not specified, updated when id is specified, deleted when rowStatus is DELETED, archived when rowStatus is ARCHIVED, The response is always HTTP 200 for a successful batch including when it deletes (each result is reported in the body with its action), All product brands are processed in one transaction in the request order, If any product brand fails then no product brand is changed |

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

|     | Parameter Name | Data Type                                       | M/O       | Description                                                       | Example |
| --- | -------------- | ----------------------------------------------- | --------- | ----------------------------------------------------------------- | ------- |
| 1   | productBrands  | [Array of Product Brand](#product-brand-object) | MANDATORY | Product brands to insert, update or delete (min 1, max 100 items) |         |

#### Product Brand Object

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                                                                                              | Example                              |
| --- | -------------- | ------------ | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Product Brand Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED product brand counts as not found, Must not be duplicated in the request                                                                                      | a3b4c5d6-e7f8-4a9b-8c0d-2e3f4a5b6c7d |
| 2   | name           | String       | MANDATORY | Product Brand Name (max 128 characters), Unique among product brands that are not DELETED                                                                                                                                                                                | Acme                                 |
| 3   | description    | String       | MANDATORY | Product Brand Description (max 256 characters)                                                                                                                                                                                                                           | Home appliances and electronics      |
| 4   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting, Delete or archive is allowed only when the product brand is not used by any product that is not DELETED | ACTIVE                               |

### Product Brand Rules (same as the single upsert, applied per product brand)

- Every product brand follows the rules of [the single upsert](../13-upsert-product-brand/spec.md#product-brand-rules): unique name among product brands that are not DELETED, required `name` and `description`, DELETED is final, delete and archive are rejected while a product that is not DELETED uses the product brand.
- The product brands are processed in the request order in one transaction, so the checks of an item see the changes of the items before it. When any item fails the whole request is rolled back and no product brand is changed.
- `id` must not be duplicated in the request, and `name` must not be duplicated among the items that are not DELETED (400, E10001). The name of a DELETED item is not compared.
- Swapping the names of two product brands in one request is rejected with 409 (E10003) at the first item, because that name is still held by the other product brand when the item is checked. Rename them in two requests.
- An item without `id` and with `rowStatus` DELETED is rejected with 400 (E10001).
- Permission: the same as the single upsert, only a platform administrator can call this API, any other caller gets 403 (E10009). The check is made once for the request, after the existence checks of all items and before the duplicate name and in-use checks, so the 403 message has no item position. Approved by the product owner (answered through the lead SA, 2026-11-06).
- The response is HTTP 200 for every successful batch, including a batch that deletes.

#### Example Body Parameters

```JSON
{
    "productBrands": [
        {
            "name": "Acme",
            "description": "Home appliances and electronics",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "a3b4c5d6-e7f8-4a9b-8c0d-2e3f4a5b6c7d",
            "name": "Northwind",
            "description": "Outdoor and sports equipment",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "b4c5d6e7-f8a9-4b0c-9d1e-3f4a5b6c7d8e",
            "name": "Contoso",
            "description": "Office furniture and supplies",
            "rowStatus": "DELETED"
        }
    ]
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/product-brand/upsert/batch HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "productBrands": [
        {
            "name": "Acme",
            "description": "Home appliances and electronics",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "a3b4c5d6-e7f8-4a9b-8c0d-2e3f4a5b6c7d",
            "name": "Northwind",
            "description": "Outdoor and sports equipment",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "b4c5d6e7-f8a9-4b0c-9d1e-3f4a5b6c7d8e",
            "name": "Contoso",
            "description": "Office furniture and supplies",
            "rowStatus": "DELETED"
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/product-brand/upsert/batch' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "productBrands": [
        {
            "name": "Acme",
            "description": "Home appliances and electronics",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "a3b4c5d6-e7f8-4a9b-8c0d-2e3f4a5b6c7d",
            "name": "Northwind",
            "description": "Outdoor and sports equipment",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "b4c5d6e7-f8a9-4b0c-9d1e-3f4a5b6c7d8e",
            "name": "Contoso",
            "description": "Office furniture and supplies",
            "rowStatus": "DELETED"
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
| 6   | timestamp      | String: TIMESTAMP | MANDATORY | Sequence Diagram | response.status.timestamp  | API Request Timestamp (Without time zone UTC) | 2026-11-05T12:42:00.123Z                 |
| 7   | status         | String            | MANDATORY | Sequence Diagram | response.status.status     | API Request Status (SUCCESS, ERROR)           | SUCCESS                                  |

### Data Object

|     | Parameter Name | Data Type                         | M/O       | Source           | Field              | Description                                             | Example |
| --- | -------------- | --------------------------------- | --------- | ---------------- | ------------------ | ------------------------------------------------------- | ------- |
| 1   | productBrands  | [Array of Result](#result-object) | MANDATORY | Sequence Diagram | data.productBrands | Result of each product brand, Same order as the request |         |

#### Result Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                               | Description                                                   | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ----------------------------------- | ------------------------------------------------------------- | ------------------------------------ |
| 1   | index          | Numeric      | MANDATORY | Sequence Diagram | data.productBrands[].index          | Index of the product brand in the request, Starting from 0    | 0                                    |
| 2   | productBrandId | String: UUID | MANDATORY | Sequence Diagram | data.productBrands[].productBrandId | Inserted, Updated, Deleted or Archived Product Brand Id       | c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f |
| 3   | action         | String       | MANDATORY | Sequence Diagram | data.productBrands[].action         | Action of the product brand (INSERT, UPDATE, DELETE, ARCHIVE) | INSERT                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Batch Upsert Product Brand Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "productBrands": [
            {
                "index": 0,
                "productBrandId": "c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
                "action": "INSERT"
            },
            {
                "index": 1,
                "productBrandId": "a3b4c5d6-e7f8-4a9b-8c0d-2e3f4a5b6c7d",
                "action": "UPDATE"
            },
            {
                "index": 2,
                "productBrandId": "b4c5d6e7-f8a9-4b0c-9d1e-3f4a5b6c7d8e",
                "action": "DELETE"
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
        "bizMessage": "productBrands[0]: Name and Description are required fields.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:40.123Z",
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
        "bizMessage": "Product brands must contain 1 to 100 items.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:47.123Z",
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
        "bizMessage": "productBrands[2]: Id is duplicated with productBrands[1].",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:40:54.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Duplicate Name

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "productBrands[2]: Name is duplicated with productBrands[0].",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:41:01.123Z",
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
        "bizMessage": "productBrands[1]: Row status must not be DELETED when inserting a product brand.",
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
        "bizMessage": "productBrands[1]: Product brand not found.",
        "requestId": "req-450a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:15.123Z",
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
        "bizMessage": "You do not have permission to change product brands.",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
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
        "bizMessage": "productBrands[0]: Product brand name already exists.",
        "requestId": "req-470a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:29.123Z",
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
        "bizMessage": "productBrands[2]: Product brand is used by products.",
        "requestId": "req-480a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:40:36.123Z",
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

### Table: [product.m_product_brand](../../../schema/product/m_product_brand.md)

#### QUERY - Check existing product brand

```SQL
SELECT
    pb.id as product_brand_id
FROM product.m_product_brand pb
WHERE pb.id = '<sequence.productBrands.id>'
AND pb.row_status <> 'DELETED' -- the id of a DELETED product brand counts as not found
```

#### QUERY - Check duplicate name

```SQL
SELECT
    pb.id as product_brand_id
FROM product.m_product_brand pb
WHERE pb.name = '<sequence.productBrands.name>'
AND pb.row_status <> 'DELETED'
AND pb.id <> '<sequence.productBrands.id>' -- only when id is specified
```

#### INSERT - Create product brand

```SQL
INSERT INTO product.m_product_brand (
    created_by,
    row_status,
    name,
    description
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.productBrands.rowStatus>',
    '<sequence.productBrands.name>',
    '<sequence.productBrands.description>'
)
RETURNING id as product_brand_id
```

#### UPDATE - Update or delete product brand

```SQL
UPDATE product.m_product_brand
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.productBrands.rowStatus>',
    name = '<sequence.productBrands.name>',
    description = '<sequence.productBrands.description>'
WHERE id = '<sequence.productBrands.id>'
RETURNING id as product_brand_id
```

### Table: [product.m_product](../../../schema/product/m_product.md)

#### QUERY - Check product in use

```SQL
SELECT
    p.id as product_id
FROM product.m_product p
WHERE p.brand_id = '<sequence.productBrands.id>' -- only when rowStatus is DELETED or ARCHIVED
AND p.row_status <> 'DELETED'
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
