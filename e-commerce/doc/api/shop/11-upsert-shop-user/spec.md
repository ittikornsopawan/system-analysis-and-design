---
name: "Upsert Shop User API"
description: "Insert, update or delete a member of a shop. Read it when you implement, review or test POST v1/shop/user/upsert."
status: in-review
approved_by: null
approved_at: null
---

# [POST]: v1/shop/user/upsert

| Title       | Description                                                                                                                                                                                                                        |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Shop User API                                                                                                                                                                                                               |
| Method      | POST                                                                                                                                                                                                                               |
| Endpoint    | v{version}/shop/user/upsert                                                                                                                                                                                                        |
| Version     | 1                                                                                                                                                                                                                                  |
| Description | Insert, update or delete a member of a shop, Insert when id is not specified, Update when id is specified, Delete when rowStatus is DELETED (HTTP 204 No Content, no response body), Archive when rowStatus is ARCHIVED (HTTP 200) |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- The rules of this section, including the permission model (the ADMIN of the shop or a platform administrator, 403 E10009), were approved by the product owner.
- A member of a shop is a user that has a row in `shop.t_shop_user` with the role ADMIN or STAFF that is ACTIVE, in a shop that is ACTIVE. The queries "Check shop member" and "Check shop members" of the shop product SKU APIs use this definition. INACTIVE, LOCKED, ARCHIVED and DELETED rows are not members. The caller is the user of the access token, never a field of the request.
- Adding a member takes effect at once: the user does not accept an invitation and is not notified.
- A user can be a member of a shop once among the rows that are not DELETED (409, E10003). A row that is INACTIVE, LOCKED or ARCHIVED still holds the place, an update with `rowStatus` ACTIVE opens it again. After a delete the user can be added to the shop again, which creates a new row.
- `shopId` and `userId` are required in every request and cannot be changed by an update: when they differ from the row of `id` the request is rejected with 400 (E10001). The shop must be ACTIVE and the user must be ACTIVE, otherwise 404 (E10005).
- DELETED is final: a DELETED shop user is never reopened and its `id` counts as not found (404, E10004). `rowStatus` DELETED is rejected with 400 (E10001) when the request inserts a shop user. `role` is ADMIN or STAFF (400, E10001).
- Permission: an ADMIN of the shop or a platform administrator (a user that has the role `PLATFORM_ADMIN`) can add members and can change the role or the row status of every member, otherwise 403 (E10009). A caller that is only a STAFF member can only delete or archive their own membership (leave the shop), every other change is 403 (E10009). A platform administrator that is not a member of the shop is not counted in the ADMIN rule below.
- The shop must keep at least one ADMIN that is ACTIVE. A request that leaves the shop without one is rejected with 409 (E10006): this covers deleting or archiving the last ADMIN, changing it to STAFF, setting it to INACTIVE, LOCKED or ARCHIVED, and leaving the shop. A platform administrator cannot skip this rule. The rule is checked on the state after the whole request is applied, so an ADMIN can be replaced in one request, and the whole request is rolled back when it fails.
- HTTP status of the single upsert: Insert 201 Created, Update 200 Ok, Delete 204 No Content (no response body), Archive 200 Ok.

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

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                                           | Example                              |
| --- | -------------- | ------------ | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Shop User Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED shop user counts as not found                                                                                  | 2c3d4e5f-0002-4a1b-8c2d-3e4f5a6b7c8d |
| 2   | shopId         | String: UUID | MANDATORY | Shop Id, Must be an existing ACTIVE shop, Cannot be changed on update (it must be the shop of the shop user)                                                                                                          | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 3   | userId         | String: UUID | MANDATORY | User Id, Must be an existing ACTIVE user, Cannot be changed on update (it must be the user of the shop user)                                                                                                          | 9f1e2d3c-4b5a-4c6d-8e7f-0a1b2c3d4e5f |
| 4   | role           | String       | OPTIONAL  | Role in the shop (ADMIN, STAFF), STAFF when not specified on insert, Keep the current role when not specified on update                                                                                               | STAFF                                |
| 5   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting, The shop must keep at least one ADMIN that is ACTIVE | ACTIVE                               |

#### Example Body Parameters

##### Insert

```JSON
{
    "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
    "userId": "9f1e2d3c-4b5a-4c6d-8e7f-0a1b2c3d4e5f",
    "role": "STAFF",
    "rowStatus": "ACTIVE"
}
```

##### Update

```JSON
{
    "id": "2c3d4e5f-0002-4a1b-8c2d-3e4f5a6b7c8d",
    "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
    "userId": "9f1e2d3c-4b5a-4c6d-8e7f-0a1b2c3d4e5f",
    "role": "ADMIN",
    "rowStatus": "ACTIVE"
}
```

##### Delete

```JSON
{
    "id": "2c3d4e5f-0002-4a1b-8c2d-3e4f5a6b7c8d",
    "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
    "userId": "9f1e2d3c-4b5a-4c6d-8e7f-0a1b2c3d4e5f",
    "role": "ADMIN",
    "rowStatus": "DELETED"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/shop/user/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
    "userId": "9f1e2d3c-4b5a-4c6d-8e7f-0a1b2c3d4e5f",
    "role": "STAFF",
    "rowStatus": "ACTIVE"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/shop/user/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
    "userId": "9f1e2d3c-4b5a-4c6d-8e7f-0a1b2c3d4e5f",
    "role": "STAFF",
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
| 1   | shopUserId     | String: UUID | MANDATORY | Sequence Diagram | data.shopUserId | Inserted, Updated or Archived Shop User Id, Not returned when deleted (HTTP 204) | 2c3d4e5f-0002-4a1b-8c2d-3e4f5a6b7c8d |

### Example Response Parameters

#### Success - Insert

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Insert Shop User Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shopUserId": "2c3d4e5f-0002-4a1b-8c2d-3e4f5a6b7c8d"
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
        "bizMessage": "Update Shop User Success",
        "requestId": "req-5c3d9e1f-2a4b-4c6d-8e0f-1a2b3c4d5e6f",
        "timestamp": "2026-11-05T12:50:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shopUserId": "2c3d4e5f-0002-4a1b-8c2d-3e4f5a6b7c8d"
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
        "bizMessage": "Archive Shop User Success",
        "requestId": "req-7e5f1a3b-4c6d-4e8f-8a2b-3c4d5e6f7a8b",
        "timestamp": "2026-11-05T12:57:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shopUserId": "2c3d4e5f-0002-4a1b-8c2d-3e4f5a6b7c8d"
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
        "bizMessage": "Shop Id and User Id are required fields.",
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
        "bizMessage": "Row status must not be DELETED when inserting a shop user.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:47.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Role

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Role must be ADMIN or STAFF.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:40:54.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Shop And User Changed

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Shop Id and User Id cannot be changed.",
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

#### Fail - Forbidden

```JSON
{
    "status": {
        "code": 403,
        "message": "Forbidden",
        "bizCode": "E10009",
        "bizMessage": "You do not have permission to manage the members of this shop.",
        "requestId": "req-403a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:40.123Z",
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
        "bizMessage": "Shop user not found.",
        "requestId": "req-404a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:40:54.321Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Shop

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "Shop not found.",
        "requestId": "req-414a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:41:01.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found User

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "User not found.",
        "requestId": "req-424a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:41:09.123Z",
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
        "bizMessage": "User is already a member of the shop.",
        "requestId": "req-440b1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:42:08.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict Last Admin

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "The shop must keep at least one ADMIN.",
        "requestId": "req-450b1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
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

### Table: [shop.m_shop](../../../schema/shop/m_shop.md)

#### QUERY - Check shop

```SQL
SELECT
    s.id as shop_id
FROM shop.m_shop s
WHERE s.id = '<sequence.shopId>'
AND s.row_status = 'ACTIVE'
```

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Check user

```SQL
SELECT
    u.id as user_id
FROM authen.m_user u
WHERE u.id = '<sequence.userId>'
AND u.row_status = 'ACTIVE'
```

### Table: [shop.t_shop_user](../../../schema/shop/t_shop_user.md)

#### QUERY - Check existing shop user

```SQL
SELECT
    su.id as shop_user_id,
    su.shop_id,
    su.user_id,
    su.role
FROM shop.t_shop_user su
WHERE su.id = '<sequence.id>'
AND su.row_status <> 'DELETED' -- the id of a DELETED shop user counts as not found
```

#### QUERY - Check duplicate member

```SQL
SELECT
    su.id as shop_user_id
FROM shop.t_shop_user su
WHERE su.shop_id = '<sequence.shopId>'
AND su.user_id = '<sequence.userId>'
AND su.row_status <> 'DELETED'
AND su.id <> '<sequence.id>' -- only when id is specified
```

#### QUERY - Check shop administrator

```SQL
SELECT
    su.id as shop_user_id
FROM shop.t_shop_user su
WHERE su.shop_id = '<sequence.shopId>'
AND su.user_id = '<sequence.userId>'
AND su.role = 'ADMIN'
AND su.row_status = 'ACTIVE'
```

#### QUERY - Check shop member

```SQL
SELECT
    su.id as shop_user_id
FROM shop.t_shop_user su
WHERE su.shop_id = '<sequence.shopId>'
AND su.user_id = '<sequence.userId>'
AND su.role IN ('ADMIN', 'STAFF')
AND su.row_status = 'ACTIVE'
```

#### INSERT - Create shop user

```SQL
INSERT INTO shop.t_shop_user (
    created_by,
    row_status,
    shop_id,
    user_id,
    role
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.rowStatus>',
    '<sequence.shopId>',
    '<sequence.userId>',
    '<sequence.role>' -- STAFF when not specified
)
RETURNING id as shop_user_id
```

#### UPDATE - Update, archive or delete shop user

```SQL
UPDATE shop.t_shop_user
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.rowStatus>',
    role = '<sequence.role>' -- only when role is specified
WHERE id = '<sequence.id>'
AND shop_id = '<sequence.shopId>'
AND user_id = '<sequence.userId>'
RETURNING id as shop_user_id
```

#### QUERY - Count the ADMIN members of the shop after the write

```SQL
SELECT
    COUNT(su.id) as admin_count
FROM shop.t_shop_user su
WHERE su.shop_id = '<sequence.shopId>'
AND su.role = 'ADMIN'
AND su.row_status = 'ACTIVE' -- the request is rolled back when the count is 0
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
