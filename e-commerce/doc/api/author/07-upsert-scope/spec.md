---
name: Scope Upsert API Specification
description: Defines JWT administration, current credentials and atomic scope lifecycle/usage checks; read when reviewing or implementing scope upsert.
status: in-review
approved_by: null
approved_at: null
---

# [POST]: v1/author/scope/upsert

| Title       | Description                                                                                                                                                                                                                                                        |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Name        | Upsert Scope API                                                                                                                                                                                                                                                   |
| Method      | POST                                                                                                                                                                                                                                                               |
| Endpoint    | v{version}/author/scope/upsert                                                                                                                                                                                                                                     |
| Version     | 1                                                                                                                                                                                                                                                                  |
| Description | Insert, update or delete a scope, only a platform administrator can call it, Insert when id is not specified, Update when id is specified, Delete when rowStatus is DELETED (HTTP 204 No Content, no response body), Archive when rowStatus is ARCHIVED (HTTP 200) |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- Governing decisions: owner-confirmed API review Q2/Q4/Q7/Q10/Q13/Q15 (approved by the product owner).
- `scope` is unique among scopes that are not DELETED.
- `scope` is the scope code: capital letters, digits and `_`, starting with a letter (max 64 characters), for example `ALL`, `SHOP`, `OWN` (400, E10001).
- DELETED is final: a DELETED scope is never reopened and its `id` counts as not found (404, E10004).
- A scope cannot be deleted or archived while a permission (`author.t_permission_scope`) that is not DELETED still uses it (409, E10006).
- Permission: only a platform administrator from the verified JWT roles claim can call this API; require exact case-sensitive role name PLATFORM_ADMIN.
- The order of the checks, the locks and every outcome is in the sequence diagram.

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

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                                                   | Example                              |
| --- | -------------- | ------------ | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Scope Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED scope counts as not found                                                                                                  | a7b8c9d0-e1f2-4a3b-8c4d-5e6f7a8b9c0d |
| 2   | scope          | String       | MANDATORY | Scope Code (max 64 characters): capital letters, digits and `_`, starting with a letter, Unique among scopes that are not DELETED                                                                                             | REGION                               |
| 3   | name           | String       | MANDATORY | Scope Name, label for screens (max 64 characters)                                                                                                                                                                             | Region                               |
| 4   | description    | String       | MANDATORY | Scope Description (max 256 characters)                                                                                                                                                                                        | The shops of one region              |
| 5   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting, Delete or archive is allowed only when no permission uses it | ACTIVE                               |

#### Example Body Parameters

##### Insert

```JSON
{
    "scope": "REGION",
    "name": "Region",
    "description": "The shops of one region",
    "rowStatus": "ACTIVE"
}
```

##### Update

```JSON
{
    "id": "a7b8c9d0-e1f2-4a3b-8c4d-5e6f7a8b9c0d",
    "scope": "REGION",
    "name": "Region",
    "description": "The shops of one region",
    "rowStatus": "ACTIVE"
}
```

##### Delete

```JSON
{
    "id": "a7b8c9d0-e1f2-4a3b-8c4d-5e6f7a8b9c0d",
    "scope": "REGION",
    "name": "Region",
    "description": "The shops of one region",
    "rowStatus": "DELETED"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/author/scope/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "scope": "REGION",
    "name": "Region",
    "description": "The shops of one region",
    "rowStatus": "ACTIVE"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/author/scope/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "scope": "REGION",
    "name": "Region",
    "description": "The shops of one region",
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

|     | Parameter Name | Data Type    | M/O       | Source           | Field        | Description                                                                  | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ------------ | ---------------------------------------------------------------------------- | ------------------------------------ |
| 1   | scopeId        | String: UUID | MANDATORY | Sequence Diagram | data.scopeId | Inserted, Updated or Archived Scope Id, Not returned when deleted (HTTP 204) | a7b8c9d0-e1f2-4a3b-8c4d-5e6f7a8b9c0d |

### Example Response Parameters

#### Success - Insert

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Insert Scope Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "scopeId": "a7b8c9d0-e1f2-4a3b-8c4d-5e6f7a8b9c0d"
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
        "bizMessage": "Update Scope Success",
        "requestId": "req-5c3d9e1f-2a4b-4c6d-8e0f-1a2b3c4d5e6f",
        "timestamp": "2026-11-06T09:10:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "scopeId": "a7b8c9d0-e1f2-4a3b-8c4d-5e6f7a8b9c0d"
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
        "bizMessage": "Archive Scope Success",
        "requestId": "req-7e5f1a3b-4c6d-4e8f-8a2b-3c4d5e6f7a8b",
        "timestamp": "2026-11-06T09:20:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "scopeId": "a7b8c9d0-e1f2-4a3b-8c4d-5e6f7a8b9c0d"
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
        "bizMessage": "Scope, Name and Description are required fields.",
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
        "bizMessage": "Scope code must be capital letters, digits and _, starting with a letter, at most 64 characters.",
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
        "bizMessage": "Row status must not be DELETED when inserting a scope.",
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
        "bizMessage": "You do not have permission to manage scopes.",
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
        "bizMessage": "Scope not found.",
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
        "bizMessage": "Scope scope already exists.",
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
        "bizMessage": "Scope is used by permissions.",
        "requestId": "req-500a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:00:50.123Z",
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

#### Fail - Internal Server Error

```JSON
{
    "status": {
        "code": 500,
        "message": "Internal Server Error",
        "bizMessage": "An unexpected error occurred.",
        "requestId": "req-scope-upsert-review",
        "timestamp": "2026-11-09T00:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

One READ COMMITTED transaction. Caller identity is separate from the optional target id; all values and fresh UTC time are bound. Caller lock precedes current credentials and optional target lock. Usage reads protect master lifecycle only, never caller authorization.

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Lock the caller user

```SQL
SELECT
    u.id as user_id
FROM authen.m_user u
WHERE u.id = '<sequence.callerUserId>'
FOR UPDATE
```

### Table: [authen.t_user_access_token](../../../schema/authen/t_user_access_token.md)

#### QUERY - Check current credential and user

```SQL
SELECT
    at.id as access_token_id
FROM authen.t_user_access_token at
JOIN authen.m_user u ON u.id = at.user_id
WHERE at.token = '<sequence.accessTokenHash>'
AND at.user_id = '<sequence.callerUserId>'
AND at.row_status = 'ACTIVE'
AND at.expired_at > '<sequence.now>'
AND u.row_status = 'ACTIVE'
```

### Table: [author.m_scope](../../../schema/author/m_scope.md)

#### QUERY - Check existing scope

```SQL
SELECT
    s.id as scope_id
FROM author.m_scope s
WHERE s.id = '<sequence.id>'
AND s.row_status <> 'DELETED' -- the id of a DELETED scope counts as not found
FOR UPDATE
```

### Table: [author.m_scope](../../../schema/author/m_scope.md)

#### QUERY - Check duplicate scope

```SQL
SELECT
    s.id as scope_id
FROM author.m_scope s
WHERE s.scope = '<sequence.scope>'
AND s.row_status <> 'DELETED'
AND ('<sequence.id>' IS NULL OR s.id <> '<sequence.id>') -- omitted insert id is typed SQL NULL
```

### Table: [author.t_permission_scope](../../../schema/author/t_permission_scope.md)

#### QUERY - Check permission scope in use

```SQL
SELECT
    ps.id as permission_scope_id
FROM author.t_permission_scope ps
WHERE ps.scope_id = '<sequence.id>' -- only when rowStatus is DELETED or ARCHIVED
AND ps.row_status <> 'DELETED'
```

### Table: [author.m_scope](../../../schema/author/m_scope.md)

#### INSERT - Create scope

```SQL
INSERT INTO author.m_scope (
    created_by,
    created_at,
    row_status,
    scope,
    name,
    description
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.now>',
    '<sequence.rowStatus>',
    '<sequence.scope>',
    '<sequence.name>',
    '<sequence.description>'
)
RETURNING id as scope_id
```

### Table: [author.m_scope](../../../schema/author/m_scope.md)

#### UPDATE - Update or delete scope

```SQL
UPDATE author.m_scope
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = '<sequence.now>',
    row_status = '<sequence.rowStatus>',
    scope = '<sequence.scope>',
    name = '<sequence.name>',
    description = '<sequence.description>'
WHERE id = '<sequence.id>'
AND row_status <> 'DELETED'
RETURNING id as scope_id
```
