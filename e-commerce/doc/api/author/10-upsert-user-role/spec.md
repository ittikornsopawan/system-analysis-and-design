---
name: User Role Upsert API Specification
description: Defines verified JWT administration, current credentials, user/role/assignment lock order, last-administrator protection and atomic assignment lifecycle; read when reviewing or implementing user role upsert.
status: in-review
approved_by: null
approved_at: null
---

# [POST]: v1/author/user/role/upsert

| Title       | Description                                                                                                                                                                                                                                                                                                                                                       |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert User Role API                                                                                                                                                                                                                                                                                                                                              |
| Method      | POST                                                                                                                                                                                                                                                                                                                                                              |
| Endpoint    | v{version}/author/user/role/upsert                                                                                                                                                                                                                                                                                                                                |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                 |
| Description | Assign a role to a user, change the status of the assignment or take the role away, only a platform administrator can call it, Insert when id is not specified, Update when id is specified, Delete when rowStatus is DELETED (HTTP 204 No Content, no response body), Archive when rowStatus is ARCHIVED (HTTP 200), The platform always keeps one administrator |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- Governing decisions: owner-confirmed API review Q2/Q4/Q7/Q10/Q13/Q15 (approved by the product owner).
- The caller is the user of the verified access token.
- **The user and the role must be ACTIVE only when the request gives the role**, that is an insert, or an update that sets `rowStatus` ACTIVE on a row that is not ACTIVE, otherwise 404 (E10005).
- A user can have a role once among the rows that are not DELETED (409, E10003).
- **The platform keeps at least one administrator.** After the whole request is applied there must be at least one ACTIVE `t_user_role` row of the ACTIVE role `PLATFORM_ADMIN` whose user is ACTIVE, otherwise 409 (E10006) and the request is ...
- HTTP status of the single upsert: Insert 201 Created, Update 200 Ok, Delete 204 No Content (no response body), Archive 200 Ok.
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

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                                                                                                | Example                              |
| --- | -------------- | ------------ | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | User Role Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED row counts as not found                                                                                                                                             | 5e6f7a8b-9c0d-4e1f-8a2b-3c4d5e6f7a8b |
| 2   | userId         | String: UUID | MANDATORY | User Id, An ACTIVE user when the role is given (not needed to take it away), Cannot be changed by an update                                                                                                                                                                | b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e |
| 3   | roleId         | String: UUID | MANDATORY | Role Id, An ACTIVE role when the role is given (not needed to take it away), Cannot be changed by an update                                                                                                                                                                | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 4   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting, Delete, archive, lock or deactivate is rejected when it would leave the platform without an administrator | ACTIVE                               |

#### Example Body Parameters

##### Insert

```JSON
{
    "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
    "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "rowStatus": "ACTIVE"
}
```

##### Update

```JSON
{
    "id": "5e6f7a8b-9c0d-4e1f-8a2b-3c4d5e6f7a8b",
    "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
    "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "rowStatus": "INACTIVE"
}
```

##### Delete

```JSON
{
    "id": "5e6f7a8b-9c0d-4e1f-8a2b-3c4d5e6f7a8b",
    "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
    "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "rowStatus": "DELETED"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/author/user/role/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
    "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "rowStatus": "ACTIVE"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/author/user/role/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
    "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
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

|     | Parameter Name | Data Type    | M/O       | Source           | Field           | Description                                                                      | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | --------------- | -------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | userRoleId     | String: UUID | MANDATORY | Sequence Diagram | data.userRoleId | Inserted, Updated or Archived User Role Id, Not returned when deleted (HTTP 204) | 5e6f7a8b-9c0d-4e1f-8a2b-3c4d5e6f7a8b |

### Example Response Parameters

#### Success - Insert

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Insert User Role Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "userRoleId": "5e6f7a8b-9c0d-4e1f-8a2b-3c4d5e6f7a8b"
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
        "bizMessage": "Update User Role Success",
        "requestId": "req-5c3d9e1f-2a4b-4c6d-8e0f-1a2b3c4d5e6f",
        "timestamp": "2026-11-06T09:10:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "userRoleId": "5e6f7a8b-9c0d-4e1f-8a2b-3c4d5e6f7a8b"
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
        "bizMessage": "Archive User Role Success",
        "requestId": "req-7e5f1a3b-4c6d-4e8f-8a2b-3c4d5e6f7a8b",
        "timestamp": "2026-11-06T09:20:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "userRoleId": "5e6f7a8b-9c0d-4e1f-8a2b-3c4d5e6f7a8b"
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
        "bizMessage": "User Id and Role Id are required fields.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:40:40.123Z",
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
        "bizMessage": "Row status must not be DELETED when inserting a user role.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request User And Role Changed

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "User Id and Role Id cannot be changed.",
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
        "bizMessage": "You do not have permission to assign roles.",
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
        "bizMessage": "User role not found.",
        "requestId": "req-470a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:47:29.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found User Or Role

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "User or role not found or not ACTIVE.",
        "requestId": "req-480a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:48:36.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Target User

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "User not found.",
        "requestId": "req-485a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:48:50.123Z",
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
        "bizMessage": "The user already has this role.",
        "requestId": "req-490a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:49:43.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict Last Administrator

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "The platform must keep at least one administrator.",
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
        "requestId": "req-user-role-upsert-review",
        "timestamp": "2026-11-12T00:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

One READ COMMITTED transaction. Caller identity (`callerUserId`) is distinct from the target user (`userId`); `userIds` is the bound typed UUID[] of both distinct ids. All values and fresh UTC time are bound. Users are locked first in ascending id order, then the role, then the assignment row.

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Lock the users

```SQL
SELECT
    u.id as user_id,
    u.row_status
FROM authen.m_user u
WHERE u.id = ANY ('<sequence.userIds>'::UUID[]) -- the caller and the target user, distinct
ORDER BY u.id
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

### Table: [author.m_role](../../../schema/author/m_role.md)

#### QUERY - Lock the role

```SQL
SELECT
    r.id as role_id,
    r.name,
    r.row_status
FROM author.m_role r
WHERE r.id = '<sequence.roleId>' -- the PLATFORM_ADMIN role exactly when the request touches the PLATFORM_ADMIN assignment
FOR UPDATE
```

### Table: [author.t_user_role](../../../schema/author/t_user_role.md)

#### QUERY - Lock existing user role

```SQL
SELECT
    ur.id as user_role_id,
    ur.user_id,
    ur.role_id,
    ur.row_status
FROM author.t_user_role ur
WHERE ur.id = '<sequence.id>'
AND ur.row_status <> 'DELETED' -- the id of a DELETED row counts as not found
FOR UPDATE
```

#### QUERY - Check duplicate user role

```SQL
SELECT
    ur.id as user_role_id
FROM author.t_user_role ur
WHERE ur.user_id = '<sequence.userId>'
AND ur.role_id = '<sequence.roleId>'
AND ur.row_status <> 'DELETED'
AND ('<sequence.id>' IS NULL OR ur.id <> '<sequence.id>') -- omitted insert id is typed SQL NULL
```

#### INSERT - Create user role

```SQL
INSERT INTO author.t_user_role (
    created_by,
    created_at,
    row_status,
    user_id,
    role_id
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.now>',
    '<sequence.rowStatus>',
    '<sequence.userId>',
    '<sequence.roleId>'
)
RETURNING id as user_role_id
```

#### UPDATE - Update, archive or delete user role

```SQL
UPDATE author.t_user_role
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = '<sequence.now>',
    row_status = '<sequence.rowStatus>'
WHERE id = '<sequence.id>'
AND row_status <> 'DELETED'
RETURNING id as user_role_id
```

#### QUERY - Count the platform administrators after the write

```SQL
SELECT
    COUNT(ur.id) as administrators
FROM author.t_user_role ur
INNER JOIN author.m_role r
    ON r.id = ur.role_id
        AND r.name = 'PLATFORM_ADMIN'
        AND r.row_status = 'ACTIVE'
INNER JOIN authen.m_user u
    ON u.id = ur.user_id
        AND u.row_status = 'ACTIVE'
WHERE ur.row_status = 'ACTIVE' -- the request is rolled back (409) when the count is 0
```
