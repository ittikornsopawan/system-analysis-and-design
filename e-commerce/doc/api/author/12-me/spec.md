# [GET]: v1/author/me

| Title       | Description                                                                                                                    |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Name        | Me API                                                                                                                         |
| Method      | GET                                                                                                                            |
| Endpoint    | v{version}/author/me                                                                                                           |
| Version     | 1                                                                                                                              |
| Description | Inquiry the roles of the logged-in user and whether the user is a platform administrator, The user comes from the access token |

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
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-06T09:00:00.123Z                       |
| 3   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Query Parameters

No query parameters. The answer is about the caller.

### Me Rules

- The caller is the user of the access token (never a request field). Any caller with a valid access token can call this API, it shows only the caller's own roles.
- `roles` lists the roles of the caller that are ACTIVE, from ACTIVE `author.t_user_role` rows of ACTIVE roles, sorted by name and then by `roleId`. `isPlatformAdmin` is true when one of them is `PLATFORM_ADMIN`. A user without a role gets `isPlatformAdmin` false and an empty `roles`.
- The permissions and scopes of the user are not returned yet (the assignment of permissions is a later work package); the field will be added when it exists. The roles are read from the database on every call, they are not stored in the access token.
- Execution order: check the access token (401) -> read.

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/author/me HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/author/me' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
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
| 6   | timestamp      | String: TIMESTAMP | MANDATORY | Sequence Diagram | response.status.timestamp  | API Request Timestamp (Without time zone UTC) | 2026-11-06T09:00:00.123Z                 |
| 7   | status         | String            | MANDATORY | Sequence Diagram | response.status.status     | API Request Status (SUCCESS, ERROR)           | SUCCESS                                  |

### Data Object

|     | Parameter Name  | Data Type                     | M/O       | Source           | Field                | Description                                       | Example                              |
| --- | --------------- | ----------------------------- | --------- | ---------------- | -------------------- | ------------------------------------------------- | ------------------------------------ |
| 1   | userId          | String: UUID                  | MANDATORY | Sequence Diagram | data.userId          | User Id (the caller)                              | b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e |
| 2   | isPlatformAdmin | Boolean                       | MANDATORY | Sequence Diagram | data.isPlatformAdmin | TRUE when the caller has the role PLATFORM_ADMIN  | false                                |
| 3   | roles           | [Array of Role](#role-object) | MANDATORY | Sequence Diagram | data.roles           | ACTIVE roles of the caller, Empty array when none |                                      |

#### Role Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field               | Description | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ------------------- | ----------- | ------------------------------------ |
| 1   | roleId         | String: UUID | MANDATORY | Sequence Diagram | data.roles[].roleId | Role Id     | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 2   | name           | String       | MANDATORY | Sequence Diagram | data.roles[].name   | Role Name   | CATALOG_MANAGER                      |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Me Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
        "isPlatformAdmin": false,
        "roles": [
            {
                "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
                "name": "CATALOG_MANAGER"
            },
            {
                "roleId": "d0e1f2a3-b4c5-4d6e-9f7a-8b9c0d1e2f3a",
                "name": "SHOP_SUPPORT"
            }
        ]
    }
}
```

#### Success - Platform Administrator

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Me Success",
        "requestId": "req-8f6a2b4c-5d7e-4f9a-b1c3-4d5e6f7a8b9c",
        "timestamp": "2026-11-06T09:10:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "userId": "c2d3e4f5-a6b7-4c8d-9e0f-1a2b3c4d5e6f",
        "isPlatformAdmin": true,
        "roles": [
            {
                "roleId": "6f7a8b9c-0d1e-4f2a-9b3c-4d5e6f7a8b9c",
                "name": "PLATFORM_ADMIN"
            }
        ]
    }
}
```

#### Success - No Role

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Me Success",
        "requestId": "req-9a7b3c5d-6e8f-4a0b-c2d4-5e6f7a8b9c0d",
        "timestamp": "2026-11-06T09:20:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
        "isPlatformAdmin": false,
        "roles": []
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

### Table: [author.t_user_role](../../../schema/author/t_user_role.md)

#### QUERY - Get the roles of the caller

```SQL
SELECT
    r.id as role_id,
    r.name
FROM author.t_user_role ur
INNER JOIN author.m_role r
    ON r.id = ur.role_id
        AND r.row_status = 'ACTIVE'
WHERE ur.user_id = '<sequence.userId>'
AND ur.row_status = 'ACTIVE'
ORDER BY r.name, r.id
```
