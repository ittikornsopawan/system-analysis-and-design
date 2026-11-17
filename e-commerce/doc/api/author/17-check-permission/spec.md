---
name: Check Permission API Specification
description: Defines how a caller checks one permission, and optionally one scope, of their own from the verified access-token claims, the current credential/user validation, and the outcomes of GET v1/author/check; read when reviewing or implementing the permission check.
status: in-review
approved_by: null
approved_at: null
---

# [GET]: v1/author/check

| Title       | Description                                                                                                                                                                                                         |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Check Permission API                                                                                                                                                                                                |
| Method      | GET                                                                                                                                                                                                                 |
| Endpoint    | v{version}/author/check                                                                                                                                                                                             |
| Version     | 1                                                                                                                                                                                                                   |
| Description | Check whether the access token of the caller holds a permission, and optionally a scope, The answer comes from the verified token claims, Any caller with a valid access token can call it for their own token only |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- Governing decisions: WP5 author design A12 (5b restarted by the owner on 2026-11-17), owner answers of 2026-11-17 (Q1–Q6, relayed by Josh) and owner-confirmed API review Q2/Q4/Q12/Q13. The owner answers supersede the implicit permissions of A2: a platform administrator holds only granted permissions.
- **Claim source:** the answer comes only from the `permissions` and `scopes` claims of the verified access token; no grant table is read (Q1).
- **Permission and scope are checked separately.** `allowed` is true when `permission` is in the `permissions` claim and, when `scope` is given, `scope` is in the `scopes` claim. The claims are flat, so `allowed` does not prove that the scope was granted with that permission (Q2, Q12).
- `PLATFORM_ADMIN` gives no implicit permission: a platform administrator is allowed only what the token holds (Q3).
- Always HTTP 200 with `allowed` true or false; a permission the token does not hold is not a 403.
- No query or body parameter names another user; the answer is about the caller.
- The order of the checks and every outcome is in the sequence diagram.

---

## Request Parameters

### Header Parameters

|     | Parameter Name | Data Type | M/O       | Description                  | Example                                        |
| --- | -------------- | --------- | --------- | ---------------------------- | ---------------------------------------------- |
| 1   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-17T09:00:00.123Z                       |
| 3   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Query Parameters

|     | Parameter Name | Data Type | M/O       | Description                                                                                                                                                                                          | Example        |
| --- | -------------- | --------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- |
| 1   | permission     | String    | MANDATORY | Permission claim to check (max 64 characters): the permission name with its last `.` replaced by `:`, lower-case letters, digits, `_` and `.`, for example `catalog:manage` or `shop.product:manage` | catalog:manage |
| 2   | scope          | String    | OPTIONAL  | Scope claim to check (max 64 characters): `<lower-case scope code>:*`, for example `all:*` or `shop:*`, Not checked when not specified                                                               | all:*          |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/author/check?permission=catalog:manage&scope=all:* HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-17T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/author/check?permission=catalog:manage&scope=all:*' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-17T09:00:00.123Z' \
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
| 6   | timestamp      | String: TIMESTAMP | MANDATORY | Sequence Diagram | response.status.timestamp  | API Request Timestamp (Without time zone UTC) | 2026-11-17T09:00:00.123Z                 |
| 7   | status         | String            | MANDATORY | Sequence Diagram | response.status.status     | API Request Status (SUCCESS, ERROR)           | SUCCESS                                  |

### Data Object

|     | Parameter Name | Data Type | M/O       | Source           | Field           | Description                                                                                  | Example        |
| --- | -------------- | --------- | --------- | ---------------- | --------------- | -------------------------------------------------------------------------------------------- | -------------- |
| 1   | permission     | String    | MANDATORY | Sequence Diagram | data.permission | The permission claim that was checked, as requested                                          | catalog:manage |
| 2   | scope          | String    | OPTIONAL  | Sequence Diagram | data.scope      | The scope claim that was checked, as requested, null when not specified                      | all:*          |
| 3   | allowed        | Boolean   | MANDATORY | Sequence Diagram | data.allowed    | TRUE when the token holds the permission and, when specified, the scope (checked separately) | true           |

### Example Response Parameters

#### Success - Allowed

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Check Permission Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-17T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "permission": "catalog:manage",
        "scope": "all:*",
        "allowed": true
    }
}
```

#### Success - Not Allowed

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Check Permission Success",
        "requestId": "req-5c3d9e1f-2a4b-4c6d-8e0f-1a2b3c4d5e6f",
        "timestamp": "2026-11-17T09:10:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "permission": "payment:refund",
        "scope": "shop:*",
        "allowed": false
    }
}
```

#### Success - Without Scope

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Check Permission Success",
        "requestId": "req-7e5f1a3b-4c6d-4e8f-8a2b-3c4d5e6f7a8b",
        "timestamp": "2026-11-17T09:20:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "permission": "catalog:manage",
        "scope": null,
        "allowed": true
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
        "bizMessage": "Permission is required and must be a permission claim such as catalog:manage.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:40:40.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Scope

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Scope must be a scope claim such as shop:*.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:41:47.123Z",
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
        "timestamp": "2026-11-17T09:07:49.123Z",
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
        "timestamp": "2026-11-17T09:08:56.123Z",
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
        "requestId": "req-check-permission-review",
        "timestamp": "2026-11-17T00:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

One typed, bound, read-only SELECT validates the stored credential and user. The permission and scope answer comes from the already-verified JWT claims, not from a grant lookup. No explicit transaction or mutation is needed.

### Table: [authen.t_user_access_token](../../../schema/authen/t_user_access_token.md)

#### QUERY - Check active credential and user

```SQL
SELECT
    at.user_id
FROM authen.t_user_access_token at
WHERE at.token = '<sequence.accessTokenHash>'
AND at.user_id = '<sequence.userId>'
AND at.row_status = 'ACTIVE'
AND at.expired_at > '<sequence.now>'
AND EXISTS (
    SELECT 1
    FROM authen.m_user u
    WHERE u.id = at.user_id
    AND u.row_status = 'ACTIVE'
)
```
