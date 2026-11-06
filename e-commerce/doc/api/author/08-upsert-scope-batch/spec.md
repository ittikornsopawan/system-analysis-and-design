# [POST]: v1/author/scope/upsert/batch

| Title       | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Name        | Upsert Scope Batch API                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Method      | POST                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Endpoint    | v{version}/author/scope/upsert/batch                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Description | Insert, update or delete multiple scopes at the same time, only a platform administrator can call it, Each scope is inserted when id is not specified, updated when id is specified, deleted when rowStatus is DELETED, archived when rowStatus is ARCHIVED, The response is always HTTP 200 for a successful batch including when it deletes (each result is reported in the body with its action), All scopes are processed in one transaction in the request order, If any scope fails then no scope is changed |

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

|     | Parameter Name | Data Type                       | M/O       | Description                                               | Example |
| --- | -------------- | ------------------------------- | --------- | --------------------------------------------------------- | ------- |
| 1   | scopes         | [Array of Scope](#scope-object) | MANDATORY | Scopes to insert, update or delete (min 1, max 100 items) |         |

#### Scope Object

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                         | Example                              |
| --- | -------------- | ------------ | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Scope Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED scope counts as not found, Must not be duplicated in the request | b8c9d0e1-f2a3-4b4c-9d5e-6f7a8b9c0d1e |
| 2   | scope          | String       | MANDATORY | Scope Code (max 64 characters): capital letters, digits and `_`, starting with a letter, Unique among scopes that are not DELETED                                   | REGION                               |
| 3   | name           | String       | MANDATORY | Scope Name, label for screens (max 64 characters)                                                                                                                   | Region                               |
| 4   | description    | String       | MANDATORY | Scope Description (max 256 characters)                                                                                                                              | The shops of one region              |
| 5   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting     | ACTIVE                               |

### Scope Rules (same as the single upsert, applied per scope)

- Every scope follows the rules of [the single upsert](../07-upsert-scope/spec.md#scope-rules): scope is the scope code: capital letters, DELETED is final, delete and archive are rejected while a permission (`author.t_permission_scope`) that is not DELETED still uses it.
- The scopes are processed in the request order in one transaction, so the checks of an item see the changes of the items before it. When any item fails the whole request is rolled back and no scope is changed. `id` must not be duplicated in the request, and `scope` must not be duplicated among the items that are not DELETED (400, E10001). An item without `id` and with `rowStatus` DELETED is rejected with 400 (E10001). The response is HTTP 200 for every successful batch, including a batch that deletes. The 403 message has no item position (the permission is the caller's, not the item's).
- Permission: only a platform administrator (a user with an ACTIVE `author.t_user_role` row for the ACTIVE role `PLATFORM_ADMIN`) can call this API, any other caller gets 403 (E10009), after the existence check and before the duplicate check. Approved by the product owner (answered through the lead SA, 2026-11-06).

#### Example Body Parameters

```JSON
{
    "scopes": [
        {
            "scope": "REGION",
            "name": "Region",
            "description": "The shops of one region",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "b8c9d0e1-f2a3-4b4c-9d5e-6f7a8b9c0d1e",
            "scope": "TEAM",
            "name": "Team",
            "description": "The members of one team",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "c9d0e1f2-a3b4-4c5d-8e6f-7a8b9c0d1e2f",
            "scope": "BRANCH",
            "name": "Branch",
            "description": "One branch of a shop",
            "rowStatus": "DELETED"
        }
    ]
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/author/scope/upsert/batch HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "scopes": [
        {
            "scope": "REGION",
            "name": "Region",
            "description": "The shops of one region",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "b8c9d0e1-f2a3-4b4c-9d5e-6f7a8b9c0d1e",
            "scope": "TEAM",
            "name": "Team",
            "description": "The members of one team",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "c9d0e1f2-a3b4-4c5d-8e6f-7a8b9c0d1e2f",
            "scope": "BRANCH",
            "name": "Branch",
            "description": "One branch of a shop",
            "rowStatus": "DELETED"
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/author/scope/upsert/batch' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "scopes": [
        {
            "scope": "REGION",
            "name": "Region",
            "description": "The shops of one region",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "b8c9d0e1-f2a3-4b4c-9d5e-6f7a8b9c0d1e",
            "scope": "TEAM",
            "name": "Team",
            "description": "The members of one team",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "c9d0e1f2-a3b4-4c5d-8e6f-7a8b9c0d1e2f",
            "scope": "BRANCH",
            "name": "Branch",
            "description": "One branch of a shop",
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
| 6   | timestamp      | String: TIMESTAMP | MANDATORY | Sequence Diagram | response.status.timestamp  | API Request Timestamp (Without time zone UTC) | 2026-11-06T09:00:00.123Z                 |
| 7   | status         | String            | MANDATORY | Sequence Diagram | response.status.status     | API Request Status (SUCCESS, ERROR)           | SUCCESS                                  |

### Data Object

|     | Parameter Name | Data Type                         | M/O       | Source           | Field       | Description                                     | Example |
| --- | -------------- | --------------------------------- | --------- | ---------------- | ----------- | ----------------------------------------------- | ------- |
| 1   | scopes         | [Array of Result](#result-object) | MANDATORY | Sequence Diagram | data.scopes | Result of each scope, Same order as the request |         |

#### Result Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                 | Description                                           | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | --------------------- | ----------------------------------------------------- | ------------------------------------ |
| 1   | index          | Numeric      | MANDATORY | Sequence Diagram | data.scopes[].index   | Index of the scope in the request, Starting from 0    | 0                                    |
| 2   | scopeId        | String: UUID | MANDATORY | Sequence Diagram | data.scopes[].scopeId | Inserted, Updated, Deleted or Archived Scope Id       | a7b8c9d0-e1f2-4a3b-8c4d-5e6f7a8b9c0d |
| 3   | action         | String       | MANDATORY | Sequence Diagram | data.scopes[].action  | Action of the scope (INSERT, UPDATE, DELETE, ARCHIVE) | INSERT                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Batch Upsert Scope Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "scopes": [
            {
                "index": 0,
                "scopeId": "a7b8c9d0-e1f2-4a3b-8c4d-5e6f7a8b9c0d",
                "action": "INSERT"
            },
            {
                "index": 1,
                "scopeId": "b8c9d0e1-f2a3-4b4c-9d5e-6f7a8b9c0d1e",
                "action": "UPDATE"
            },
            {
                "index": 2,
                "scopeId": "c9d0e1f2-a3b4-4c5d-8e6f-7a8b9c0d1e2f",
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
        "bizMessage": "scopes[0]: Scope, Name and Description are required fields.",
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
        "bizMessage": "scopes[1]: Scope code must be capital letters, digits and _, starting with a letter, at most 64 characters.",
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
        "bizMessage": "scopes[1]: Row status must not be DELETED when inserting a scope.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:42:54.123Z",
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
        "bizMessage": "Scopes must contain 1 to 100 items.",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:43:01.123Z",
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
        "bizMessage": "scopes[2]: Id is duplicated with scopes[1].",
        "requestId": "req-440a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:44:08.123Z",
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
        "bizMessage": "scopes[2]: Scope is duplicated with scopes[0].",
        "requestId": "req-450a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:45:15.123Z",
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
        "bizMessage": "scopes[1]: Scope not found.",
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
        "bizMessage": "scopes[0]: Scope scope already exists.",
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
        "bizMessage": "scopes[2]: Scope is used by permissions.",
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

---

## Database Relations

### Table: [author.m_scope](../../../schema/author/m_scope.md)

#### QUERY - Check existing scope

```SQL
SELECT
    s.id as scope_id
FROM author.m_scope s
WHERE s.id = '<sequence.scopes.id>'
AND s.row_status <> 'DELETED' -- the id of a DELETED scope counts as not found
```

#### QUERY - Check duplicate scope

```SQL
SELECT
    s.id as scope_id
FROM author.m_scope s
WHERE s.scope = '<sequence.scopes.scope>'
AND s.row_status <> 'DELETED'
AND s.id <> '<sequence.scopes.id>' -- only when id is specified
```

#### INSERT - Create scope

```SQL
INSERT INTO author.m_scope (
    created_by,
    row_status,
    scope,
    name,
    description
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.scopes.rowStatus>',
    '<sequence.scopes.scope>',
    '<sequence.scopes.name>',
    '<sequence.scopes.description>'
)
RETURNING id as scope_id
```

#### UPDATE - Update or delete scope

```SQL
UPDATE author.m_scope
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.scopes.rowStatus>',
    scope = '<sequence.scopes.scope>',
    name = '<sequence.scopes.name>',
    description = '<sequence.scopes.description>'
WHERE id = '<sequence.scopes.id>'
RETURNING id as scope_id
```

### Table: [author.t_permission_scope](../../../schema/author/t_permission_scope.md)

#### QUERY - Check permission scope in use

```SQL
SELECT
    ps.id as permission_scope_id
FROM author.t_permission_scope ps
WHERE ps.scope_id = '<sequence.scopes.id>' -- only when rowStatus is DELETED or ARCHIVED
AND ps.row_status <> 'DELETED'
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
