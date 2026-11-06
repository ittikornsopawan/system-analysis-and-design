# [POST]: v1/shop/type/upsert

| Title       | Description                                                                                                                                                                                                                                                            |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Shop Type API                                                                                                                                                                                                                                                   |
| Method      | POST                                                                                                                                                                                                                                                                   |
| Endpoint    | v{version}/shop/type/upsert                                                                                                                                                                                                                                            |
| Version     | 1                                                                                                                                                                                                                                                                      |
| Description | Insert, update or delete a shop type, Insert when id is not specified, Update when id is specified, Delete when rowStatus is DELETED (HTTP 204 No Content, no response body), Archive when rowStatus is ARCHIVED (HTTP 200), only a platform administrator can call it |

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

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                                                                                       | Example                                 |
| --- | -------------- | ------------ | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| 1   | id             | String: UUID | OPTIONAL  | Shop Type Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED shop type counts as not found                                                                                                                              | c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f    |
| 2   | name           | String       | MANDATORY | Shop Type Name (max 128 characters), Unique among shop types that are not DELETED                                                                                                                                                                                 | Fashion Store                           |
| 3   | description    | String       | MANDATORY | Shop Type Description (max 256 characters)                                                                                                                                                                                                                        | Shops that sell clothes and accessories |
| 4   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting, Delete or archive is allowed only when the shop type is not used by any shop that is not DELETED | ACTIVE                                  |

### Shop Type Rules

- `name` is unique among shop types that are not DELETED. The comparison is exact (upper and lower case are different names) and a name held by an INACTIVE, LOCKED or ARCHIVED shop type is still taken (409, E10003). The name of a DELETED shop type can be used again.
- `name` and `description` are required in every request, including a delete and an archive.
- DELETED is final: a DELETED shop type is never reopened and its `id` counts as not found (404, E10004). INACTIVE, LOCKED and ARCHIVED are reversible: an update with `rowStatus` ACTIVE opens the shop type again. `rowStatus` DELETED is rejected with 400 (E10001) when the request inserts a shop type.
- A shop type cannot be deleted or archived while any shop that is not DELETED uses it (`shop.m_shop.type_id`), 409 (E10006). INACTIVE and LOCKED are allowed even when shops use the shop type, the shops are not changed. Whether a shop can be created with a shop type that is not ACTIVE is a rule of the shop API.
- Permission: only a platform administrator (a user with an ACTIVE `author.t_user_role` row for the ACTIVE role `PLATFORM_ADMIN`) can call this API, any other caller gets 403 (E10009), after the existence checks and before the duplicate, in-use and other conflict checks and before anything is written. Reading is not changed by this rule. Approved by the product owner (answered through the lead SA, 2026-11-06).
- Execution order: validate the request (400) -> existence check (404) -> permission (403, E10009) -> duplicate name check (409, E10003) -> in-use check (409, E10006, only when `rowStatus` is DELETED or ARCHIVED) -> write.
- HTTP status of the single upsert: Insert 201 Created, Update 200 Ok, Delete 204 No Content (no response body), Archive 200 Ok.

#### Example Body Parameters

##### Insert

```JSON
{
    "name": "Fashion Store",
    "description": "Shops that sell clothes and accessories",
    "rowStatus": "ACTIVE"
}
```

##### Update

```JSON
{
    "id": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f",
    "name": "Fashion and Apparel Store",
    "description": "Shops that sell clothes and accessories",
    "rowStatus": "ACTIVE"
}
```

##### Delete

```JSON
{
    "id": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f",
    "name": "Fashion and Apparel Store",
    "description": "Shops that sell clothes and accessories",
    "rowStatus": "DELETED"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/shop/type/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "name": "Fashion Store",
    "description": "Shops that sell clothes and accessories",
    "rowStatus": "ACTIVE"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/shop/type/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "name": "Fashion Store",
    "description": "Shops that sell clothes and accessories",
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

|     | Parameter Name | Data Type    | M/O       | Source           | Field           | Description                                                                      | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | --------------- | -------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | shopTypeId     | String: UUID | MANDATORY | Sequence Diagram | data.shopTypeId | Inserted, Updated or Archived Shop Type Id, Not returned when deleted (HTTP 204) | c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f |

### Example Response Parameters

#### Success - Insert

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Insert Shop Type Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shopTypeId": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f"
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
        "bizMessage": "Update Shop Type Success",
        "requestId": "req-5c3d9e1f-2a4b-4c6d-8e0f-1a2b3c4d5e6f",
        "timestamp": "2026-11-05T12:50:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shopTypeId": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f"
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
        "bizMessage": "Archive Shop Type Success",
        "requestId": "req-7e5f1a3b-4c6d-4e8f-8a2b-3c4d5e6f7a8b",
        "timestamp": "2026-11-05T12:57:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shopTypeId": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f"
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

#### Fail - Bad Request Row Status

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Row status must not be DELETED when inserting a shop type.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:47.123Z",
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
        "bizMessage": "Shop type not found.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:40:54.123Z",
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
        "bizMessage": "You do not have permission to manage shop types.",
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
        "bizMessage": "Shop type name already exists.",
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
        "bizMessage": "Shop type is used by shops.",
        "requestId": "req-450a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:15.123Z",
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
WHERE st.id = '<sequence.id>'
AND st.row_status <> 'DELETED' -- the id of a DELETED shop type counts as not found
```

#### QUERY - Check duplicate name

```SQL
SELECT
    st.id as shop_type_id
FROM shop.m_shop_type st
WHERE st.name = '<sequence.name>'
AND st.row_status <> 'DELETED'
AND st.id <> '<sequence.id>' -- only when id is specified
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
    '<sequence.rowStatus>',
    '<sequence.name>',
    '<sequence.description>'
)
RETURNING id as shop_type_id
```

#### UPDATE - Update or delete shop type

```SQL
UPDATE shop.m_shop_type
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.rowStatus>',
    name = '<sequence.name>',
    description = '<sequence.description>'
WHERE id = '<sequence.id>'
RETURNING id as shop_type_id
```

### Table: [shop.m_shop](../../../schema/shop/m_shop.md)

#### QUERY - Check shop in use

```SQL
SELECT
    s.id as shop_id
FROM shop.m_shop s
WHERE s.type_id = '<sequence.id>' -- only when rowStatus is DELETED or ARCHIVED
AND s.row_status <> 'DELETED'
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
