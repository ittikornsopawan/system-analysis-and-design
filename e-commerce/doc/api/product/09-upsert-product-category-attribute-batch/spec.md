# [POST]: v1/product-category-attribute/upsert/batch

| Title       | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Name        | Upsert Product Category Attribute Batch API                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Method      | POST                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Endpoint    | v{version}/product-category-attribute/upsert/batch                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Description | Insert, update or delete multiple product category attributes at the same time, Each attribute is inserted when id is not specified, updated when id is specified, deleted when rowStatus is DELETED, archived when rowStatus is ARCHIVED, The response is always HTTP 200 for a successful batch including when it deletes (each result is reported in the body with its action), All attributes are processed in one transaction in the request order, If any attribute fails then no attribute is changed |

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

|     | Parameter Name | Data Type                               | M/O       | Description                                                                    | Example |
| --- | -------------- | --------------------------------------- | --------- | ------------------------------------------------------------------------------ | ------- |
| 1   | attributes     | [Array of Attribute](#attribute-object) | MANDATORY | Product category attributes to insert, update or delete (min 1, max 100 items) |         |

#### Attribute Object

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                    | Example                              |
| --- | -------------- | ------------ | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Product Category Attribute Id, Insert when not specified, Update or Delete when specified, Must not be duplicated in the request                                                               | 22b3c4d5-0002-4b1c-9d2e-3f4a5b6c7d8e |
| 2   | categoryId     | String: UUID | MANDATORY | Product Category Id, Cannot be changed when the attribute is used by products                                                                                                                  | b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e |
| 3   | name           | String       | MANDATORY | Product Category Attribute Name (max 128 characters), Unique, Must not be duplicated in the request                                                                                            | Color                                |
| 4   | description    | String       | MANDATORY | Product Category Attribute Description (max 256 characters)                                                                                                                                    | Color of the product                 |
| 5   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, Delete is allowed only when the attribute is not used by any product | ACTIVE                               |

#### Example Body Parameters

```JSON
{
    "attributes": [
        {
            "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "name": "Color",
            "description": "Color of the product",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "22b3c4d5-0002-4b1c-9d2e-3f4a5b6c7d8e",
            "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "name": "Connectivity",
            "description": "Connectivity type of the product",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "33c4d5e6-0003-4c2d-8e3f-4a5b6c7d8e9f",
            "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "name": "Weight",
            "description": "Weight of the product",
            "rowStatus": "DELETED"
        }
    ]
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/product-category-attribute/upsert/batch HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "attributes": [
        {
            "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "name": "Color",
            "description": "Color of the product",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "22b3c4d5-0002-4b1c-9d2e-3f4a5b6c7d8e",
            "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "name": "Connectivity",
            "description": "Connectivity type of the product",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "33c4d5e6-0003-4c2d-8e3f-4a5b6c7d8e9f",
            "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "name": "Weight",
            "description": "Weight of the product",
            "rowStatus": "DELETED"
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/product-category-attribute/upsert/batch' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "attributes": [
        {
            "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "name": "Color",
            "description": "Color of the product",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "22b3c4d5-0002-4b1c-9d2e-3f4a5b6c7d8e",
            "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "name": "Connectivity",
            "description": "Connectivity type of the product",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "33c4d5e6-0003-4c2d-8e3f-4a5b6c7d8e9f",
            "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "name": "Weight",
            "description": "Weight of the product",
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

|     | Parameter Name | Data Type                         | M/O       | Source           | Field           | Description                                                          | Example |
| --- | -------------- | --------------------------------- | --------- | ---------------- | --------------- | -------------------------------------------------------------------- | ------- |
| 1   | attributes     | [Array of Result](#result-object) | MANDATORY | Sequence Diagram | data.attributes | Result of each product category attribute, Same order as the request |         |

#### Result Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                         | Description                                                                | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ----------------------------- | -------------------------------------------------------------------------- | ------------------------------------ |
| 1   | index          | Numeric      | MANDATORY | Sequence Diagram | data.attributes[].index       | Index of the product category attribute in the request, Starting from 0    | 0                                    |
| 2   | attributeId    | String: UUID | MANDATORY | Sequence Diagram | data.attributes[].attributeId | Inserted, Updated, Deleted or Archived Product Category Attribute Id       | 11a2b3c4-0001-4a0b-8c1d-2e3f4a5b6c7d |
| 3   | action         | String       | MANDATORY | Sequence Diagram | data.attributes[].action      | Action of the product category attribute (INSERT, UPDATE, DELETE, ARCHIVE) | INSERT                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Batch Upsert Product Category Attribute Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "attributes": [
            {
                "index": 0,
                "attributeId": "11a2b3c4-0001-4a0b-8c1d-2e3f4a5b6c7d",
                "action": "INSERT"
            },
            {
                "index": 1,
                "attributeId": "22b3c4d5-0002-4b1c-9d2e-3f4a5b6c7d8e",
                "action": "UPDATE"
            },
            {
                "index": 2,
                "attributeId": "33c4d5e6-0003-4c2d-8e3f-4a5b6c7d8e9f",
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
        "bizMessage": "attributes[0]: Category Id, Name and Description are required fields.",
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
        "bizMessage": "Attributes must contain 1 to 100 items.",
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
        "bizMessage": "attributes[2]: Id is duplicated with attributes[1].",
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
        "bizMessage": "attributes[2]: Name is duplicated with attributes[0].",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:41:01.123Z",
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
        "bizMessage": "attributes[1]: Product category attribute not found.",
        "requestId": "req-440a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:42:08.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Category

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "attributes[0]: Product category not found.",
        "requestId": "req-450a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:15.123Z",
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
        "bizMessage": "attributes[0]: Product category attribute name already exists.",
        "requestId": "req-460a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:22.123Z",
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
        "bizMessage": "attributes[2]: Product category attribute is used by products.",
        "requestId": "req-470a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:29.123Z",
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

#### QUERY - Check product categories

```SQL
SELECT
    pc.id as category_id
FROM product.m_product_category pc
WHERE pc.id IN ('<sequence.attributes.categoryIds>')
AND pc.row_status = 'ACTIVE'
```

### Table: [product.m_product_category_attribute](../../../schema/product/m_product_category_attribute.md)

#### QUERY - Check existing attributes

```SQL
SELECT
    pca.id as attribute_id,
    pca.category_id
FROM product.m_product_category_attribute pca
WHERE pca.id IN ('<sequence.attributes.ids>')
```

#### QUERY - Check duplicate name

```SQL
SELECT
    pca.id as attribute_id
FROM product.m_product_category_attribute pca
WHERE pca.name = '<sequence.attributes.name>'
AND pca.id <> '<sequence.attributes.id>' -- only when id is specified
```

#### INSERT - Create attribute

```SQL
INSERT INTO product.m_product_category_attribute (
    created_by,
    row_status,
    category_id,
    name,
    description
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.attributes.rowStatus>',
    '<sequence.attributes.categoryId>',
    '<sequence.attributes.name>',
    '<sequence.attributes.description>'
)
RETURNING id as attribute_id
```

#### UPDATE - Update or delete attribute

```SQL
UPDATE product.m_product_category_attribute
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.attributes.rowStatus>',
    category_id = '<sequence.attributes.categoryId>',
    name = '<sequence.attributes.name>',
    description = '<sequence.attributes.description>'
WHERE id = '<sequence.attributes.id>'
RETURNING id as attribute_id
```

### Table: [product.m_product_attribute](../../../schema/product/m_product_attribute.md)

#### QUERY - Check attributes in use

```SQL
SELECT
    pa.id as product_attribute_id
FROM product.m_product_attribute pa
WHERE pa.attribute_id IN ('<sequence.attributes.ids>')
AND pa.row_status <> 'DELETED'
```
