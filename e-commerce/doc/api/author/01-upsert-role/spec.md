# [POST]: v1/author/role/upsert

| Title       | Description                                                                                                                                                                                                                                                       |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Role API                                                                                                                                                                                                                                                   |
| Method      | POST                                                                                                                                                                                                                                                              |
| Endpoint    | v{version}/author/role/upsert                                                                                                                                                                                                                                     |
| Version     | 1                                                                                                                                                                                                                                                                 |
| Description | Insert, update or delete a role, only a platform administrator can call it, Insert when id is not specified, Update when id is specified, Delete when rowStatus is DELETED (HTTP 204 No Content, no response body), Archive when rowStatus is ARCHIVED (HTTP 200) |

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

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                                                           | Example                              |
| --- | -------------- | ------------ | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Role Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED role counts as not found                                                                                                            | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 2   | name           | String       | MANDATORY | Role Name, Role code (max 64 characters): capital letters, digits and `_`, starting with a letter, Unique among roles that are not DELETED, The role `PLATFORM_ADMIN` cannot be changed                                               | CATALOG_MANAGER                      |
| 3   | description    | String       | MANDATORY | Role Description (max 256 characters)                                                                                                                                                                                                 | Manages the product catalogue        |
| 4   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting, Delete or archive is allowed only when no user or permission uses it | ACTIVE                               |

### Role Rules

- `name` is unique among roles that are not DELETED. The comparison is exact and a value held by an INACTIVE, LOCKED or ARCHIVED role is still taken (409, E10003). The value of a DELETED role can be used again.
- `name` is the role code: capital letters, digits and `_`, starting with a letter (max 64 characters) (400, E10001). Every field that is not optional is required in every request, including a delete and an archive.
- DELETED is final: a DELETED role is never reopened and its `id` counts as not found (404, E10004). INACTIVE, LOCKED and ARCHIVED are reversible: an update with `rowStatus` ACTIVE opens the role again. `rowStatus` DELETED is rejected with 400 (E10001) when the request inserts a role. A role that is not ACTIVE gives no right to anyone.
- A role cannot be deleted or archived while a user (`author.t_user_role`) or a permission (`author.t_role_permission`) that is not DELETED still uses it (409, E10006). INACTIVE and LOCKED are allowed, the rows that use it are not changed.
- **`PLATFORM_ADMIN` is the system role.** It cannot be renamed, changed, deleted, archived, locked or set INACTIVE through this API: any request that names it by `id` is rejected with 409 (E10006) `System role cannot be changed.` Giving another role the name `PLATFORM_ADMIN` is a duplicate name (409, E10003). The role is created by the seed, see `e-commerce/db/seed/author.seed.sql`.
- Permission: only a platform administrator (a user with an ACTIVE `author.t_user_role` row for the ACTIVE role `PLATFORM_ADMIN`) can call this API, any other caller gets 403 (E10009), after the existence check and before the duplicate check. Approved by the product owner (answered through the lead SA, 2026-11-06).
- Execution order: validate the request (400) -> existence check (404) -> permission (403, E10009) -> system role check (409, E10006) -> duplicate check (409, E10003) -> in-use check (409, E10006, only when `rowStatus` is DELETED or ARCHIVED) -> write.
- HTTP status of the single upsert: Insert 201 Created, Update 200 Ok, Delete 204 No Content (no response body), Archive 200 Ok.

#### Example Body Parameters

##### Insert

```JSON
{
    "name": "CATALOG_MANAGER",
    "description": "Manages the product catalogue",
    "rowStatus": "ACTIVE"
}
```

##### Update

```JSON
{
    "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "name": "CATALOG_EDITOR",
    "description": "Manages the product catalogue",
    "rowStatus": "ACTIVE"
}
```

##### Delete

```JSON
{
    "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "name": "CATALOG_EDITOR",
    "description": "Manages the product catalogue",
    "rowStatus": "DELETED"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/author/role/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "name": "CATALOG_MANAGER",
    "description": "Manages the product catalogue",
    "rowStatus": "ACTIVE"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/author/role/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "name": "CATALOG_MANAGER",
    "description": "Manages the product catalogue",
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
| 6   | timestamp      | String: TIMESTAMP | MANDATORY | Sequence Diagram | response.status.timestamp  | API Request Timestamp (Without time zone UTC) | 2026-11-06T09:00:00.123Z                 |
| 7   | status         | String            | MANDATORY | Sequence Diagram | response.status.status     | API Request Status (SUCCESS, ERROR)           | SUCCESS                                  |

### Data Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field       | Description                                                                 | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ----------- | --------------------------------------------------------------------------- | ------------------------------------ |
| 1   | roleId         | String: UUID | MANDATORY | Sequence Diagram | data.roleId | Inserted, Updated or Archived Role Id, Not returned when deleted (HTTP 204) | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |

### Example Response Parameters

#### Success - Insert

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Insert Role Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
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
        "bizMessage": "Update Role Success",
        "requestId": "req-5c3d9e1f-2a4b-4c6d-8e0f-1a2b3c4d5e6f",
        "timestamp": "2026-11-06T09:10:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
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
        "bizMessage": "Archive Role Success",
        "requestId": "req-7e5f1a3b-4c6d-4e8f-8a2b-3c4d5e6f7a8b",
        "timestamp": "2026-11-06T09:20:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
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
        "timestamp": "2026-11-06T09:40:40.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Name

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Role name must be capital letters, digits and _, starting with a letter, at most 64 characters.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
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
        "bizMessage": "Row status must not be DELETED when inserting a role.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:42:54.123Z",
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
        "bizMessage": "You do not have permission to manage roles.",
        "requestId": "req-460a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:46:22.123Z",
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
        "bizMessage": "Role not found.",
        "requestId": "req-470a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:47:29.123Z",
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
        "bizMessage": "Role name already exists.",
        "requestId": "req-490a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:49:43.123Z",
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
        "bizMessage": "Role is assigned to users or has permissions.",
        "requestId": "req-500a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:00:50.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict System Role

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "System role cannot be changed.",
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
        "requestId": "req-80a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:08:56.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

### Table: [author.m_role](../../../schema/author/m_role.md)

#### QUERY - Check existing role

```SQL
SELECT
    r.id as role_id
FROM author.m_role r
WHERE r.id = '<sequence.id>'
AND r.row_status <> 'DELETED' -- the id of a DELETED role counts as not found
```

#### QUERY - Check duplicate name

```SQL
SELECT
    r.id as role_id
FROM author.m_role r
WHERE r.name = '<sequence.name>'
AND r.row_status <> 'DELETED'
AND r.id <> '<sequence.id>' -- only when id is specified
```

#### INSERT - Create role

```SQL
INSERT INTO author.m_role (
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
RETURNING id as role_id
```

#### UPDATE - Update or delete role

```SQL
UPDATE author.m_role
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.rowStatus>',
    name = '<sequence.name>',
    description = '<sequence.description>'
WHERE id = '<sequence.id>'
RETURNING id as role_id
```

#### QUERY - Check system role

```SQL
SELECT
    r.id as role_id
FROM author.m_role r
WHERE r.id = '<sequence.id>'
AND r.name = 'PLATFORM_ADMIN' -- the request is rejected (409) when a row is found, only when id is specified
```

### Table: [author.t_user_role](../../../schema/author/t_user_role.md)

#### QUERY - Check user in use

```SQL
SELECT
    ur.id as user_role_id
FROM author.t_user_role ur
WHERE ur.role_id = '<sequence.id>' -- only when rowStatus is DELETED or ARCHIVED
AND ur.row_status <> 'DELETED'
```

### Table: [author.t_role_permission](../../../schema/author/t_role_permission.md)

#### QUERY - Check role permission in use

```SQL
SELECT
    rp.id as role_permission_id
FROM author.t_role_permission rp
WHERE rp.role_id = '<sequence.id>' -- only when rowStatus is DELETED or ARCHIVED
AND rp.row_status <> 'DELETED'
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
