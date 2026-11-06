# [POST]: v1/shop/type/upsert/batch

| Title       | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Shop Type Batch API                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Method      | POST                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Endpoint    | v{version}/shop/type/upsert/batch                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Description | Insert, update or delete multiple shop types at the same time, Each shop type is inserted when id is not specified, updated when id is specified, deleted when rowStatus is DELETED, archived when rowStatus is ARCHIVED, The response is always HTTP 200 for a successful batch including when it deletes (each result is reported in the body with its action), All shop types are processed in one transaction in the request order, If any shop type fails then no shop type is changed |

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

|     | Parameter Name | Data Type                               | M/O       | Description                                                   | Example |
| --- | -------------- | --------------------------------------- | --------- | ------------------------------------------------------------- | ------- |
| 1   | shopTypes      | [Array of Shop Type](#shop-type-object) | MANDATORY | Shop types to insert, update or delete (min 1, max 100 items) |         |

#### Shop Type Object

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                                                                                       | Example                                 |
| --- | -------------- | ------------ | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| 1   | id             | String: UUID | OPTIONAL  | Shop Type Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED shop type counts as not found, Must not be duplicated in the request                                                                                       | d2e3f4a5-b6c7-4d8e-9f0a-1b2c3d4e5f6a    |
| 2   | name           | String       | MANDATORY | Shop Type Name (max 128 characters), Unique among shop types that are not DELETED                                                                                                                                                                                 | Fashion Store                           |
| 3   | description    | String       | MANDATORY | Shop Type Description (max 256 characters)                                                                                                                                                                                                                        | Shops that sell clothes and accessories |
| 4   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting, Delete or archive is allowed only when the shop type is not used by any shop that is not DELETED | ACTIVE                                  |

### Shop Type Rules (same as the single upsert, applied per shop type)

- Every shop type follows the rules of [the single upsert](../05-upsert-shop-type/spec.md#shop-type-rules): unique name among shop types that are not DELETED, required `name` and `description`, DELETED is final, delete and archive are rejected while a shop that is not DELETED uses the shop type.
- The shop types are processed in the request order in one transaction, so the checks of an item see the changes of the items before it. When any item fails the whole request is rolled back and no shop type is changed.
- `id` must not be duplicated in the request, and `name` must not be duplicated among the items that are not DELETED (400, E10001). The name of a DELETED item is not compared.
- Swapping the names of two shop types in one request is rejected with 409 (E10003) at the first item, because that name is still held by the other shop type when the item is checked. Rename them in two requests.
- An item without `id` and with `rowStatus` DELETED is rejected with 400 (E10001).
- The response is HTTP 200 for every successful batch, including a batch that deletes.

#### Example Body Parameters

```JSON
{
    "shopTypes": [
        {
            "name": "Fashion Store",
            "description": "Shops that sell clothes and accessories",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "d2e3f4a5-b6c7-4d8e-9f0a-1b2c3d4e5f6a",
            "name": "Electronics Store",
            "description": "Shops that sell electronic devices",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "e3f4a5b6-c7d8-4e9f-8a1b-2c3d4e5f6a7b",
            "name": "Grocery Store",
            "description": "Shops that sell food and daily goods",
            "rowStatus": "DELETED"
        }
    ]
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/shop/type/upsert/batch HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "shopTypes": [
        {
            "name": "Fashion Store",
            "description": "Shops that sell clothes and accessories",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "d2e3f4a5-b6c7-4d8e-9f0a-1b2c3d4e5f6a",
            "name": "Electronics Store",
            "description": "Shops that sell electronic devices",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "e3f4a5b6-c7d8-4e9f-8a1b-2c3d4e5f6a7b",
            "name": "Grocery Store",
            "description": "Shops that sell food and daily goods",
            "rowStatus": "DELETED"
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/shop/type/upsert/batch' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "shopTypes": [
        {
            "name": "Fashion Store",
            "description": "Shops that sell clothes and accessories",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "d2e3f4a5-b6c7-4d8e-9f0a-1b2c3d4e5f6a",
            "name": "Electronics Store",
            "description": "Shops that sell electronic devices",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "e3f4a5b6-c7d8-4e9f-8a1b-2c3d4e5f6a7b",
            "name": "Grocery Store",
            "description": "Shops that sell food and daily goods",
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

|     | Parameter Name | Data Type                         | M/O       | Source           | Field          | Description                                         | Example |
| --- | -------------- | --------------------------------- | --------- | ---------------- | -------------- | --------------------------------------------------- | ------- |
| 1   | shopTypes      | [Array of Result](#result-object) | MANDATORY | Sequence Diagram | data.shopTypes | Result of each shop type, Same order as the request |         |

#### Result Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                       | Description                                               | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | --------------------------- | --------------------------------------------------------- | ------------------------------------ |
| 1   | index          | Numeric      | MANDATORY | Sequence Diagram | data.shopTypes[].index      | Index of the shop type in the request, Starting from 0    | 0                                    |
| 2   | shopTypeId     | String: UUID | MANDATORY | Sequence Diagram | data.shopTypes[].shopTypeId | Inserted, Updated, Deleted or Archived Shop Type Id       | c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f |
| 3   | action         | String       | MANDATORY | Sequence Diagram | data.shopTypes[].action     | Action of the shop type (INSERT, UPDATE, DELETE, ARCHIVE) | INSERT                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Batch Upsert Shop Type Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shopTypes": [
            {
                "index": 0,
                "shopTypeId": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f",
                "action": "INSERT"
            },
            {
                "index": 1,
                "shopTypeId": "d2e3f4a5-b6c7-4d8e-9f0a-1b2c3d4e5f6a",
                "action": "UPDATE"
            },
            {
                "index": 2,
                "shopTypeId": "e3f4a5b6-c7d8-4e9f-8a1b-2c3d4e5f6a7b",
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
        "bizMessage": "shopTypes[0]: Name and Description are required fields.",
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
        "bizMessage": "Shop types must contain 1 to 100 items.",
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
        "bizMessage": "shopTypes[2]: Id is duplicated with shopTypes[1].",
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
        "bizMessage": "shopTypes[2]: Name is duplicated with shopTypes[0].",
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
        "bizMessage": "shopTypes[1]: Row status must not be DELETED when inserting a shop type.",
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
        "bizMessage": "shopTypes[1]: Shop type not found.",
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
        "bizMessage": "shopTypes[0]: Shop type name already exists.",
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
        "bizMessage": "shopTypes[2]: Shop type is used by shops.",
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

### Table: [shop.m_shop_type](../../../schema/shop/m_shop_type.md)

#### QUERY - Check existing shop type

```SQL
SELECT
    st.id as shop_type_id
FROM shop.m_shop_type st
WHERE st.id = '<sequence.shopTypes.id>'
AND st.row_status <> 'DELETED' -- the id of a DELETED shop type counts as not found
```

#### QUERY - Check duplicate name

```SQL
SELECT
    st.id as shop_type_id
FROM shop.m_shop_type st
WHERE st.name = '<sequence.shopTypes.name>'
AND st.row_status <> 'DELETED'
AND st.id <> '<sequence.shopTypes.id>' -- only when id is specified
```

#### INSERT - Create shop type

```SQL
INSERT INTO shop.m_shop_type (
    created_by,
    row_status,
    name,
    description
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.shopTypes.rowStatus>',
    '<sequence.shopTypes.name>',
    '<sequence.shopTypes.description>'
)
RETURNING id as shop_type_id
```

#### UPDATE - Update or delete shop type

```SQL
UPDATE shop.m_shop_type
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.shopTypes.rowStatus>',
    name = '<sequence.shopTypes.name>',
    description = '<sequence.shopTypes.description>'
WHERE id = '<sequence.shopTypes.id>'
RETURNING id as shop_type_id
```

### Table: [shop.m_shop](../../../schema/shop/m_shop.md)

#### QUERY - Check shop in use

```SQL
SELECT
    s.id as shop_id
FROM shop.m_shop s
WHERE s.type_id = '<sequence.shopTypes.id>' -- only when rowStatus is DELETED or ARCHIVED
AND s.row_status <> 'DELETED'
```
