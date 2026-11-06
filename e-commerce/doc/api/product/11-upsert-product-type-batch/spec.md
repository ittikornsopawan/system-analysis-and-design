# [POST]: v1/product-type/upsert/batch

| Title       | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Product Type Batch API                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Method      | POST                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Endpoint    | v{version}/product-type/upsert/batch                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Description | Insert, update or delete multiple product types at the same time, only a platform administrator can call it, Each product type is inserted when id is not specified, updated when id is specified, deleted when rowStatus is DELETED, archived when rowStatus is ARCHIVED, The response is always HTTP 200 for a successful batch including when it deletes (each result is reported in the body with its action), All product types are processed in one transaction in the request order, If any product type fails then no product type is changed |

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

|     | Parameter Name | Data Type                                     | M/O       | Description                                                      | Example |
| --- | -------------- | --------------------------------------------- | --------- | ---------------------------------------------------------------- | ------- |
| 1   | productTypes   | [Array of Product Type](#product-type-object) | MANDATORY | Product types to insert, update or delete (min 1, max 100 items) |         |

#### Product Type Object

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                                                                                             | Example                                         |
| --- | -------------- | ------------ | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| 1   | id             | String: UUID | OPTIONAL  | Product Type Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED product type counts as not found, Must not be duplicated in the request                                                                                       | e1f2a3b4-c5d6-4e7f-8a9b-0c1d2e3f4a5b            |
| 2   | name           | String       | MANDATORY | Product Type Name (max 128 characters), Unique among product types that are not DELETED                                                                                                                                                                                 | Electronics                                     |
| 3   | description    | String       | MANDATORY | Product Type Description (max 256 characters)                                                                                                                                                                                                                           | Devices and accessories that run on electricity |
| 4   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting, Delete or archive is allowed only when the product type is not used by any product that is not DELETED | ACTIVE                                          |

### Product Type Rules (same as the single upsert, applied per product type)

- Every product type follows the rules of [the single upsert](../10-upsert-product-type/spec.md#product-type-rules): unique name among product types that are not DELETED, required `name` and `description`, DELETED is final, delete and archive are rejected while a product that is not DELETED uses the product type.
- The product types are processed in the request order in one transaction, so the checks of an item see the changes of the items before it. When any item fails the whole request is rolled back and no product type is changed.
- `id` must not be duplicated in the request, and `name` must not be duplicated among the items that are not DELETED (400, E10001). The name of a DELETED item is not compared.
- Swapping the names of two product types in one request is rejected with 409 (E10003) at the first item, because that name is still held by the other product type when the item is checked. Rename them in two requests.
- An item without `id` and with `rowStatus` DELETED is rejected with 400 (E10001).
- Permission: the same as the single upsert, only a platform administrator can call this API, any other caller gets 403 (E10009). The check is made once for the request, after the existence checks of all items and before the duplicate name and in-use checks, so the 403 message has no item position. Approved by the product owner (answered through the lead SA, 2026-11-06).
- The response is HTTP 200 for every successful batch, including a batch that deletes.

#### Example Body Parameters

```JSON
{
    "productTypes": [
        {
            "name": "Electronics",
            "description": "Devices and accessories that run on electricity",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "e1f2a3b4-c5d6-4e7f-8a9b-0c1d2e3f4a5b",
            "name": "Apparel",
            "description": "Clothes, shoes and bags",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "f2a3b4c5-d6e7-4f8a-9b0c-1d2e3f4a5b6c",
            "name": "Grocery",
            "description": "Food and daily goods",
            "rowStatus": "DELETED"
        }
    ]
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/product-type/upsert/batch HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "productTypes": [
        {
            "name": "Electronics",
            "description": "Devices and accessories that run on electricity",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "e1f2a3b4-c5d6-4e7f-8a9b-0c1d2e3f4a5b",
            "name": "Apparel",
            "description": "Clothes, shoes and bags",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "f2a3b4c5-d6e7-4f8a-9b0c-1d2e3f4a5b6c",
            "name": "Grocery",
            "description": "Food and daily goods",
            "rowStatus": "DELETED"
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/product-type/upsert/batch' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "productTypes": [
        {
            "name": "Electronics",
            "description": "Devices and accessories that run on electricity",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "e1f2a3b4-c5d6-4e7f-8a9b-0c1d2e3f4a5b",
            "name": "Apparel",
            "description": "Clothes, shoes and bags",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "f2a3b4c5-d6e7-4f8a-9b0c-1d2e3f4a5b6c",
            "name": "Grocery",
            "description": "Food and daily goods",
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

|     | Parameter Name | Data Type                         | M/O       | Source           | Field             | Description                                            | Example |
| --- | -------------- | --------------------------------- | --------- | ---------------- | ----------------- | ------------------------------------------------------ | ------- |
| 1   | productTypes   | [Array of Result](#result-object) | MANDATORY | Sequence Diagram | data.productTypes | Result of each product type, Same order as the request |         |

#### Result Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                             | Description                                                  | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | --------------------------------- | ------------------------------------------------------------ | ------------------------------------ |
| 1   | index          | Numeric      | MANDATORY | Sequence Diagram | data.productTypes[].index         | Index of the product type in the request, Starting from 0    | 0                                    |
| 2   | productTypeId  | String: UUID | MANDATORY | Sequence Diagram | data.productTypes[].productTypeId | Inserted, Updated, Deleted or Archived Product Type Id       | a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d |
| 3   | action         | String       | MANDATORY | Sequence Diagram | data.productTypes[].action        | Action of the product type (INSERT, UPDATE, DELETE, ARCHIVE) | INSERT                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Batch Upsert Product Type Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "productTypes": [
            {
                "index": 0,
                "productTypeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
                "action": "INSERT"
            },
            {
                "index": 1,
                "productTypeId": "e1f2a3b4-c5d6-4e7f-8a9b-0c1d2e3f4a5b",
                "action": "UPDATE"
            },
            {
                "index": 2,
                "productTypeId": "f2a3b4c5-d6e7-4f8a-9b0c-1d2e3f4a5b6c",
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
        "bizMessage": "productTypes[0]: Name and Description are required fields.",
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
        "bizMessage": "Product types must contain 1 to 100 items.",
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
        "bizMessage": "productTypes[2]: Id is duplicated with productTypes[1].",
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
        "bizMessage": "productTypes[2]: Name is duplicated with productTypes[0].",
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
        "bizMessage": "productTypes[1]: Row status must not be DELETED when inserting a product type.",
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
        "bizMessage": "productTypes[1]: Product type not found.",
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
        "bizMessage": "You do not have permission to change product types.",
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
        "bizMessage": "productTypes[0]: Product type name already exists.",
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
        "bizMessage": "productTypes[2]: Product type is used by products.",
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

### Table: [product.m_product_type](../../../schema/product/m_product_type.md)

#### QUERY - Check existing product type

```SQL
SELECT
    pt.id as product_type_id
FROM product.m_product_type pt
WHERE pt.id = '<sequence.productTypes.id>'
AND pt.row_status <> 'DELETED' -- the id of a DELETED product type counts as not found
```

#### QUERY - Check duplicate name

```SQL
SELECT
    pt.id as product_type_id
FROM product.m_product_type pt
WHERE pt.name = '<sequence.productTypes.name>'
AND pt.row_status <> 'DELETED'
AND pt.id <> '<sequence.productTypes.id>' -- only when id is specified
```

#### INSERT - Create product type

```SQL
INSERT INTO product.m_product_type (
    created_by,
    row_status,
    name,
    description
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.productTypes.rowStatus>',
    '<sequence.productTypes.name>',
    '<sequence.productTypes.description>'
)
RETURNING id as product_type_id
```

#### UPDATE - Update or delete product type

```SQL
UPDATE product.m_product_type
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.productTypes.rowStatus>',
    name = '<sequence.productTypes.name>',
    description = '<sequence.productTypes.description>'
WHERE id = '<sequence.productTypes.id>'
RETURNING id as product_type_id
```

### Table: [product.m_product](../../../schema/product/m_product.md)

#### QUERY - Check product in use

```SQL
SELECT
    p.id as product_id
FROM product.m_product p
WHERE p.type_id = '<sequence.productTypes.id>' -- only when rowStatus is DELETED or ARCHIVED
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
