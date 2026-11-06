# [GET]: v1/shop/user

| Title       | Description                                                                                                                                                             |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Shop User API                                                                                                                                                   |
| Method      | GET                                                                                                                                                                     |
| Endpoint    | v{version}/shop/user                                                                                                                                                    |
| Version     | 1                                                                                                                                                                       |
| Description | Inquiry the members of a shop, or the shops of the caller, with paging, search and filters, Inquiry by id returns a list with one item, Deleted shop users are excluded |

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
| 1   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-05T12:42:00.123Z                       |
| 3   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Query Parameters

|     | Parameter Name | Data Type    | M/O      | Description                                                                                                                   | Example                              |
| --- | -------------- | ------------ | -------- | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | shopId         | String: UUID | OPTIONAL | Shop Id, Required unless userId is specified, The caller must be a member of the shop or a platform administrator             | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 2   | id             | String: UUID | OPTIONAL | Shop User Id, Response is a list with one item                                                                                | 2c3d4e5f-0001-4a1b-8c2d-3e4f5a6b7c8d |
| 3   | userId         | String: UUID | OPTIONAL | User Id, The memberships of the user, Only the caller (the shops of the caller) unless the caller is a platform administrator | 3e4f5a6b-7c8d-4e9f-8a0b-1c2d3e4f5a6b |
| 4   | role           | String       | OPTIONAL | Role filter (ADMIN, STAFF)                                                                                                    | ADMIN                                |
| 5   | rowStatus      | String       | OPTIONAL | Row status filter (ACTIVE, INACTIVE, LOCKED, ARCHIVED), All statuses except DELETED when not specified                        | ACTIVE                               |
| 6   | pageIndex      | Numeric      | OPTIONAL | Page index starting from 1, Defaults to 1                                                                                     | 1                                    |
| 7   | pageSize       | Numeric      | OPTIONAL | Number of items per page (max 100), Defaults to 10                                                                            | 10                                   |
| 8   | search         | String       | OPTIONAL | Search by the display name of the user                                                                                        | aof                                  |

### Shop User Inquiry Rules

The rules of this section, including the permission model (the ADMIN of the shop or a platform administrator, 403 E10009), were approved by the product owner.

- `shopId` or `userId` must be specified (400, E10001). With `shopId` the caller must be a member of the shop (see the definition of a member in [the upsert](../11-upsert-shop-user/spec.md#shop-user-rules)) or a platform administrator, otherwise 403 (E10009), also when the shop does not exist.
- A `userId` that is not the caller can be used only by a platform administrator, otherwise 403 (E10009). `userId` of the caller without `shopId` lists the shops of the caller ("my shops"), there is no separate endpoint.
- Shop users with `rowStatus` DELETED and shop users of a shop that is DELETED are never returned. INACTIVE, LOCKED and ARCHIVED rows are returned with their `rowStatus`.
- The user is described by `displayName` and `profilePicturePath` only. The user name and the email address of a user are never returned (they are personal data that is stored encrypted).
- The caller of the examples is the user `3e4f5a6b-7c8d-4e9f-8a0b-1c2d3e4f5a6b`, an ACTIVE ADMIN of the shop `5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d` and an ACTIVE STAFF of the shop `9e0f1a2b-3c4d-4e5f-8a6b-7c8d9e0f1a2c`, and is not a platform administrator.
- The list is ordered by creation time (newest first) and then by `id`.

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/shop/user?shopId=5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d&pageIndex=1&pageSize=10&search=a&role=ADMIN&rowStatus=ACTIVE HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/shop/user?shopId=5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d&pageIndex=1&pageSize=10&search=a&role=ADMIN&rowStatus=ACTIVE' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d'
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

|     | Parameter Name | Data Type                               | M/O       | Source           | Field           | Description                            | Example |
| --- | -------------- | --------------------------------------- | --------- | ---------------- | --------------- | -------------------------------------- | ------- |
| 1   | items          | [Array of Shop User](#shop-user-object) | MANDATORY | Sequence Diagram | data.items      | Shop users, Empty array when not found |         |
| 2   | pageIndex      | Numeric                                 | MANDATORY | Sequence Diagram | data.pageIndex  | Current page index                     | 1       |
| 3   | pageSize       | Numeric                                 | MANDATORY | Sequence Diagram | data.pageSize   | Number of items per page               | 10      |
| 4   | totalItems     | Numeric                                 | MANDATORY | Sequence Diagram | data.totalItems | Total number of items                  | 2       |
| 5   | totalPages     | Numeric                                 | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages                  | 1       |

#### Shop User Object

|     | Parameter Name     | Data Type    | M/O       | Source           | Field                           | Description                                                   | Example                              |
| --- | ------------------ | ------------ | --------- | ---------------- | ------------------------------- | ------------------------------------------------------------- | ------------------------------------ |
| 1   | shopUserId         | String: UUID | MANDATORY | Sequence Diagram | data.items[].shopUserId         | Shop User Id                                                  | 2c3d4e5f-0001-4a1b-8c2d-3e4f5a6b7c8d |
| 2   | shopId             | String: UUID | MANDATORY | Sequence Diagram | data.items[].shopId             | Shop Id                                                       | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 3   | shopName           | String       | MANDATORY | Sequence Diagram | data.items[].shopName           | Shop Name                                                     | Aof Fashion                          |
| 4   | userId             | String: UUID | MANDATORY | Sequence Diagram | data.items[].userId             | User Id                                                       | 3e4f5a6b-7c8d-4e9f-8a0b-1c2d3e4f5a6b |
| 5   | displayName        | String       | OPTIONAL  | Sequence Diagram | data.items[].displayName        | Display name of the user, Null when the user has none         | Aof Sopawan                          |
| 6   | profilePicturePath | String       | OPTIONAL  | Sequence Diagram | data.items[].profilePicturePath | Profile picture path of the user, Null when the user has none | /users/aof/profile.png               |
| 7   | role               | String       | MANDATORY | Sequence Diagram | data.items[].role               | Role in the shop (ADMIN, STAFF)                               | ADMIN                                |
| 8   | rowStatus          | String       | MANDATORY | Sequence Diagram | data.items[].rowStatus          | Row status (ACTIVE, INACTIVE, LOCKED, ARCHIVED)               | ACTIVE                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Shop User Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "shopUserId": "2c3d4e5f-0001-4a1b-8c2d-3e4f5a6b7c8d",
                "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
                "shopName": "Aof Fashion",
                "userId": "3e4f5a6b-7c8d-4e9f-8a0b-1c2d3e4f5a6b",
                "displayName": "Aof Sopawan",
                "profilePicturePath": "/users/aof/profile.png",
                "role": "ADMIN",
                "rowStatus": "ACTIVE"
            },
            {
                "shopUserId": "2c3d4e5f-0002-4a1b-8c2d-3e4f5a6b7c8d",
                "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
                "shopName": "Aof Fashion",
                "userId": "9f1e2d3c-4b5a-4c6d-8e7f-0a1b2c3d4e5f",
                "displayName": "Somchai Jaidee",
                "profilePicturePath": null,
                "role": "STAFF",
                "rowStatus": "ACTIVE"
            }
        ],
        "pageIndex": 1,
        "pageSize": 10,
        "totalItems": 2,
        "totalPages": 1
    }
}
```

#### Success - By Id

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Shop User Success",
        "requestId": "req-8f6a2b4c-5d7e-4f9a-b1c3-4d5e6f7a8b9c",
        "timestamp": "2026-11-05T12:48:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "shopUserId": "2c3d4e5f-0001-4a1b-8c2d-3e4f5a6b7c8d",
                "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
                "shopName": "Aof Fashion",
                "userId": "3e4f5a6b-7c8d-4e9f-8a0b-1c2d3e4f5a6b",
                "displayName": "Aof Sopawan",
                "profilePicturePath": "/users/aof/profile.png",
                "role": "ADMIN",
                "rowStatus": "ACTIVE"
            }
        ],
        "pageIndex": 1,
        "pageSize": 10,
        "totalItems": 1,
        "totalPages": 1
    }
}
```

#### Success - My Shops

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Shop User Success",
        "requestId": "req-8a1b2c3d-5d7e-4f9a-b1c3-4d5e6f7a8b9c",
        "timestamp": "2026-11-05T12:48:30.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "shopUserId": "2c3d4e5f-0001-4a1b-8c2d-3e4f5a6b7c8d",
                "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
                "shopName": "Aof Fashion",
                "userId": "3e4f5a6b-7c8d-4e9f-8a0b-1c2d3e4f5a6b",
                "displayName": "Aof Sopawan",
                "profilePicturePath": "/users/aof/profile.png",
                "role": "ADMIN",
                "rowStatus": "ACTIVE"
            },
            {
                "shopUserId": "2c3d4e5f-0005-4a1b-8c2d-3e4f5a6b7c8d",
                "shopId": "9e0f1a2b-3c4d-4e5f-8a6b-7c8d9e0f1a2c",
                "shopName": "Corner Cafe",
                "userId": "3e4f5a6b-7c8d-4e9f-8a0b-1c2d3e4f5a6b",
                "displayName": "Aof Sopawan",
                "profilePicturePath": "/users/aof/profile.png",
                "role": "STAFF",
                "rowStatus": "ACTIVE"
            }
        ],
        "pageIndex": 1,
        "pageSize": 10,
        "totalItems": 2,
        "totalPages": 1
    }
}
```

#### Success - Not Found

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Shop User Success",
        "requestId": "req-9a7b3c5d-6e8f-4a0b-c2d4-5e6f7a8b9c0d",
        "timestamp": "2026-11-05T12:49:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [],
        "pageIndex": 1,
        "pageSize": 10,
        "totalItems": 0,
        "totalPages": 0
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
        "bizMessage": "Shop Id or User Id is required.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:40.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Paging

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Page Index and Page Size must be greater than 0, Page Size must not be greater than 100.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:47.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Role Or Row Status

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Role must be ADMIN or STAFF, Row status must be one of ACTIVE, INACTIVE, LOCKED, ARCHIVED.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:40:54.123Z",
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
        "bizMessage": "You do not have permission to view the members of this shop.",
        "requestId": "req-403a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:40.123Z",
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

### Table: [shop.t_shop_user](../../../schema/shop/t_shop_user.md)

#### QUERY - Get shop users

```SQL
SELECT
    su.id as shop_user_id,
    su.shop_id,
    s.name as shop_name,
    su.user_id,
    u.display_name,
    u.profile_picture_path,
    su.role,
    su.row_status
FROM shop.t_shop_user su
INNER JOIN shop.m_shop s
    ON s.id = su.shop_id
INNER JOIN authen.m_user u
    ON u.id = su.user_id
WHERE su.row_status <> 'DELETED'
AND s.row_status <> 'DELETED'
AND su.id = '<sequence.id>' -- only when id is specified
AND su.shop_id = '<sequence.shopId>' -- only when shopId is specified
AND su.user_id = '<sequence.userId>' -- only when userId is specified
AND su.role = '<sequence.role>' -- only when role is specified
AND su.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified
AND u.display_name ILIKE '%<sequence.search>%' -- only when search is specified
ORDER BY su.created_at DESC, su.id
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Get total items

```SQL
SELECT
    COUNT(su.id) as total_items
FROM shop.t_shop_user su
INNER JOIN shop.m_shop s
    ON s.id = su.shop_id
INNER JOIN authen.m_user u
    ON u.id = su.user_id
WHERE su.row_status <> 'DELETED'
AND s.row_status <> 'DELETED'
AND su.id = '<sequence.id>' -- only when id is specified
AND su.shop_id = '<sequence.shopId>' -- only when shopId is specified
AND su.user_id = '<sequence.userId>' -- only when userId is specified
AND su.role = '<sequence.role>' -- only when role is specified
AND su.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified
AND u.display_name ILIKE '%<sequence.search>%' -- only when search is specified
```

#### QUERY - Check shop member

```SQL
SELECT
    su.id as shop_user_id
FROM shop.t_shop_user su
WHERE su.shop_id = '<sequence.shopId>' -- only when shopId is specified
AND su.user_id = '<sequence.callerUserId>'
AND su.role IN ('ADMIN', 'STAFF')
AND su.row_status = 'ACTIVE'
```

### Table: [shop.m_shop](../../../schema/shop/m_shop.md)

The shop name and the shop status come from the join of the query above.

### Table: [authen.m_user](../../../schema/authen/m_user.md)

The display name and the profile picture come from the join of the query above, the user name and the email address are not selected.

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
WHERE ur.user_id = '<sequence.callerUserId>'
AND ur.role_id = '<sequence.roleId>'
AND ur.row_status = 'ACTIVE'
```
