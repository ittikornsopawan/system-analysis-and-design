---
name: "Upsert Shop User Batch API"
description: "Insert, update or delete multiple members of shops at the same time, for an ADMIN of the shop or a platform administrator from the verified JWT roles claim after the caller lock and the current credential check. Read it when you implement, review or test POST v1/shop/user/upsert/batch."
status: approved
approved_by: Ittikorn
approved_at: 2026-11-16T09:24:57+07:00
---

# [POST]: v1/shop/user/upsert/batch

| Title       | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Shop User Batch API                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Method      | POST                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Endpoint    | v{version}/shop/user/upsert/batch                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Description | Insert, update or delete multiple members of shops at the same time, Each shop user is inserted when id is not specified, updated when id is specified, deleted when rowStatus is DELETED, archived when rowStatus is ARCHIVED, The response is always HTTP 200 for a successful batch including when it deletes (each result is reported in the body with its action), All shop users are processed in one transaction in the request order, If any shop user fails then no shop user is changed |

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
- Governing decisions: owner-confirmed API review Q2, Q4, Q10 and Q13 (JWT payload of 2026-11-13).
- Permission: an ADMIN of the shop or a caller with the exact case-sensitive role `PLATFORM_ADMIN` in the verified `roles` claim (an array of role names, an empty array is valid) can add members and can change the role or the row status of every member, otherwise 403 (E10009). A caller that is only a STAFF member can only delete or archive their own membership (leave the shop), every other change is 403 (E10009). A platform administrator that is not a member of the shop is not counted in the ADMIN rule below. The platform administrator is read only from the verified `roles` claim: do not query `author.m_role` or `author.t_user_role`, a change of the role assignments does not change a token that was already issued. Membership of a shop is not a token claim and is still read from `shop.t_shop_user`.
- The transaction locks the caller user first and checks the current credential, a missing user or credential is 401 (E10002); the rows of the shops are locked after it. The order of the checks and the locks is in the sequence diagram.
- The shop must keep at least one ADMIN that is ACTIVE. A request that leaves the shop without one is rejected with 409 (E10006): this covers deleting or archiving the last ADMIN, changing it to STAFF, setting it to INACTIVE, LOCKED or ARCHIVED, and leaving the shop. A platform administrator cannot skip this rule. The rule is checked on the state after the whole request is applied, so an ADMIN can be replaced in one request, and the whole request is rolled back when it fails.
- The shop users are processed in the request order in one transaction, so the checks of an item see the changes of the items before it, except the ADMIN rule that is checked once for each shop after all the items. When any item fails the whole request is rolled back and no shop user is changed.
- `id` must not be duplicated in the request, and the pair `shopId` and `userId` must not be duplicated among the items that are not DELETED (400, E10001). An item without `id` and with `rowStatus` DELETED is rejected with 400 (E10001).
- Every shop user follows the rules of the single upsert (shop/11).
- The response is HTTP 200 for every successful batch, including a batch that deletes.

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
| 1   | shopUsers      | [Array of Shop User](#shop-user-object) | MANDATORY | Shop users to insert, update or delete (min 1, max 100 items) |         |

#### Shop User Object

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                                           | Example                              |
| --- | -------------- | ------------ | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Shop User Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED shop user counts as not found, Must not be duplicated in the request                                           | 2c3d4e5f-0002-4a1b-8c2d-3e4f5a6b7c8d |
| 2   | shopId         | String: UUID | MANDATORY | Shop Id, Must be an existing ACTIVE shop, Cannot be changed on update (it must be the shop of the shop user)                                                                                                          | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 3   | userId         | String: UUID | MANDATORY | User Id, Must be an existing ACTIVE user, Cannot be changed on update (it must be the user of the shop user)                                                                                                          | 9f1e2d3c-4b5a-4c6d-8e7f-0a1b2c3d4e5f |
| 4   | role           | String       | OPTIONAL  | Role in the shop (ADMIN, STAFF), STAFF when not specified on insert, Keep the current role when not specified on update                                                                                               | STAFF                                |
| 5   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting, The shop must keep at least one ADMIN that is ACTIVE | ACTIVE                               |

#### Example Body Parameters

```JSON
{
    "shopUsers": [
        {
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
            "userId": "9f1e2d3c-4b5a-4c6d-8e7f-0a1b2c3d4e5f",
            "role": "STAFF",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "2c3d4e5f-0003-4a1b-8c2d-3e4f5a6b7c8d",
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
            "userId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
            "role": "ADMIN",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "2c3d4e5f-0004-4a1b-8c2d-3e4f5a6b7c8d",
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
            "userId": "4b5c6d7e-8f9a-4b0c-8d1e-2f3a4b5c6d7e",
            "role": "STAFF",
            "rowStatus": "DELETED"
        }
    ]
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/shop/user/upsert/batch HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "shopUsers": [
        {
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
            "userId": "9f1e2d3c-4b5a-4c6d-8e7f-0a1b2c3d4e5f",
            "role": "STAFF",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "2c3d4e5f-0003-4a1b-8c2d-3e4f5a6b7c8d",
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
            "userId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
            "role": "ADMIN",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "2c3d4e5f-0004-4a1b-8c2d-3e4f5a6b7c8d",
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
            "userId": "4b5c6d7e-8f9a-4b0c-8d1e-2f3a4b5c6d7e",
            "role": "STAFF",
            "rowStatus": "DELETED"
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/shop/user/upsert/batch' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "shopUsers": [
        {
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
            "userId": "9f1e2d3c-4b5a-4c6d-8e7f-0a1b2c3d4e5f",
            "role": "STAFF",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "2c3d4e5f-0003-4a1b-8c2d-3e4f5a6b7c8d",
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
            "userId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
            "role": "ADMIN",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "2c3d4e5f-0004-4a1b-8c2d-3e4f5a6b7c8d",
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
            "userId": "4b5c6d7e-8f9a-4b0c-8d1e-2f3a4b5c6d7e",
            "role": "STAFF",
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
| 1   | shopUsers      | [Array of Result](#result-object) | MANDATORY | Sequence Diagram | data.shopUsers | Result of each shop user, Same order as the request |         |

#### Result Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                       | Description                                               | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | --------------------------- | --------------------------------------------------------- | ------------------------------------ |
| 1   | index          | Numeric      | MANDATORY | Sequence Diagram | data.shopUsers[].index      | Index of the shop user in the request, Starting from 0    | 0                                    |
| 2   | shopUserId     | String: UUID | MANDATORY | Sequence Diagram | data.shopUsers[].shopUserId | Inserted, Updated, Deleted or Archived Shop User Id       | 2c3d4e5f-0002-4a1b-8c2d-3e4f5a6b7c8d |
| 3   | action         | String       | MANDATORY | Sequence Diagram | data.shopUsers[].action     | Action of the shop user (INSERT, UPDATE, DELETE, ARCHIVE) | INSERT                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Batch Upsert Shop User Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shopUsers": [
            {
                "index": 0,
                "shopUserId": "2c3d4e5f-0002-4a1b-8c2d-3e4f5a6b7c8d",
                "action": "INSERT"
            },
            {
                "index": 1,
                "shopUserId": "2c3d4e5f-0003-4a1b-8c2d-3e4f5a6b7c8d",
                "action": "UPDATE"
            },
            {
                "index": 2,
                "shopUserId": "2c3d4e5f-0004-4a1b-8c2d-3e4f5a6b7c8d",
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
        "bizMessage": "shopUsers[1]: Shop Id and User Id are required fields.",
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
        "bizMessage": "Shop users must contain 1 to 100 items.",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:12.123Z",
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
        "bizMessage": "shopUsers[2]: Id is duplicated with shopUsers[1].",
        "requestId": "req-440a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:20.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Duplicate Member

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "shopUsers[2]: Shop Id and User Id are duplicated with shopUsers[0].",
        "requestId": "req-450a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:25.123Z",
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
        "bizMessage": "shopUsers[1]: Row status must not be DELETED when inserting a shop user.",
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
        "bizMessage": "shopUsers[1]: Role must be ADMIN or STAFF.",
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
        "bizMessage": "shopUsers[1]: Shop Id and User Id cannot be changed.",
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
        "bizMessage": "shopUsers[1]: You do not have permission to manage the members of this shop.",
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
        "bizMessage": "shopUsers[1]: Shop user not found.",
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
        "bizMessage": "shopUsers[1]: Shop not found.",
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
        "bizMessage": "shopUsers[1]: User not found.",
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
        "bizMessage": "shopUsers[0]: User is already a member of the shop.",
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

#### Fail - Internal Server Error

```JSON
{
    "status": {
        "code": 500,
        "message": "Internal Server Error",
        "bizMessage": "An unexpected error occurred.",
        "requestId": "req-500a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:46:10.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

One READ COMMITTED transaction. The caller identity (`callerUserId`, the `sub` of the verified JWT, the same user as `userId` of the member checks) is distinct from the member rows that are written; the fresh UTC time is bound. The caller user is locked first, then the current credential is checked.

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

### Table: [shop.m_shop](../../../schema/shop/m_shop.md)

#### QUERY - Check shop

```SQL
SELECT
    s.id as shop_id
FROM shop.m_shop s
WHERE s.id = '<sequence.shopUsers.shopId>'
AND s.row_status = 'ACTIVE'
```

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Check user

```SQL
SELECT
    u.id as user_id
FROM authen.m_user u
WHERE u.id = '<sequence.shopUsers.userId>'
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
WHERE su.id = '<sequence.shopUsers.id>'
AND su.row_status <> 'DELETED' -- the id of a DELETED shop user counts as not found
FOR UPDATE
```

#### QUERY - Check duplicate member

```SQL
SELECT
    su.id as shop_user_id
FROM shop.t_shop_user su
WHERE su.shop_id = '<sequence.shopUsers.shopId>'
AND su.user_id = '<sequence.shopUsers.userId>'
AND su.row_status <> 'DELETED'
AND su.id <> '<sequence.shopUsers.id>' -- only when id is specified
```

#### QUERY - Check shop administrator

```SQL
SELECT
    su.id as shop_user_id
FROM shop.t_shop_user su
WHERE su.shop_id = '<sequence.shopUsers.shopId>'
AND su.user_id = '<sequence.userId>'
AND su.role = 'ADMIN'
AND su.row_status = 'ACTIVE'
```

#### QUERY - Check shop member

```SQL
SELECT
    su.id as shop_user_id
FROM shop.t_shop_user su
WHERE su.shop_id = '<sequence.shopUsers.shopId>'
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
    '<sequence.shopUsers.rowStatus>',
    '<sequence.shopUsers.shopId>',
    '<sequence.shopUsers.userId>',
    '<sequence.shopUsers.role>' -- STAFF when not specified
)
RETURNING id as shop_user_id
```

#### UPDATE - Update, archive or delete shop user

```SQL
UPDATE shop.t_shop_user
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.shopUsers.rowStatus>',
    role = '<sequence.shopUsers.role>' -- only when role is specified
WHERE id = '<sequence.shopUsers.id>'
AND shop_id = '<sequence.shopUsers.shopId>'
AND user_id = '<sequence.shopUsers.userId>'
RETURNING id as shop_user_id
```

#### QUERY - Count the ADMIN members of the shop after the write

```SQL
SELECT
    COUNT(su.id) as admin_count
FROM shop.t_shop_user su
WHERE su.shop_id = '<sequence.shopUsers.shopId>'
AND su.role = 'ADMIN'
AND su.row_status = 'ACTIVE' -- the request is rolled back when the count is 0
```
