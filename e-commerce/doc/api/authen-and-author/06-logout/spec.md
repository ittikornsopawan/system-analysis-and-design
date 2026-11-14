---
name: Logout API Specification
description: Defines user-first serialized logout, fresh credential/session checks, atomic session-wide access/refresh revocation, concurrent refresh behavior, complete outcomes and exact SQL for POST v1/auth/logout.
status: in-review
approved_by: null
approved_at: null
---

# [POST]: v1/auth/logout

| Title       | Description                                                                                                                                            |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Name        | Logout API                                                                                                                                             |
| Method      | POST                                                                                                                                                   |
| Endpoint    | v{version}/auth/logout                                                                                                                                 |
| Version     | 1                                                                                                                                                      |
| Description | Log out of the current session, Every access token and refresh token of the same session is closed at once, Other sessions of the user are not changed |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- Governing decisions: owner-confirmed API review Q13 (approved by the product owner).
- No body or target userId/sessionId is accepted.
- Derive userId only from verified JWT sub and accessTokenHash as SHA-256 (32 bytes) of the exact presented JWT.
- Missing/inactive user or missing/revoked/expired/mismatched credential returns the same 401 after ROLLBACK, with no token changes.
- Close **every ACTIVE access token and refresh token that has the same `session_id` as the access token of the request**, including all access tokens issued by earlier refreshes in that session.
- The common user lock serializes logout with refresh, password reset and other conforming credential writers for that user.
- The order of the checks, the locks and every outcome is in the sequence diagram.

---

## Request Parameters

### Header Parameters

|     | Parameter Name | Data Type | M/O       | Description                  | Example                                        |
| --- | -------------- | --------- | --------- | ---------------------------- | ---------------------------------------------- |
| 1   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-06T09:00:00.123Z                       |
| 3   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Body Parameters

No body.

#### Example Body Parameters

No body.

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/auth/logout HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/auth/logout' \
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

No `data`. Only the status object is returned.

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Logout Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
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

#### Fail - Bad Request

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Timestamp must be a valid UTC timestamp and the request body must be empty.",
        "requestId": "req-logout-review",
        "timestamp": "2026-11-07T12:00:00.123Z",
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
        "requestId": "req-logout-review",
        "timestamp": "2026-11-07T12:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

Statements are listed in execution order, all under the common user transaction lock. now is captured after that lock returns. sessionId is the post-lock stored access-token result; affected row counts return from each UPDATE.

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Lock the user

```SQL
SELECT
    u.id as user_id
FROM authen.m_user u
WHERE u.id = '<sequence.userId>'
AND u.row_status = 'ACTIVE'
FOR UPDATE -- every authen API locks the user row first
```

### Table: [authen.t_user_access_token](../../../schema/authen/t_user_access_token.md)

#### QUERY - Get the session of the access token

```SQL
SELECT
    at.session_id
FROM authen.t_user_access_token at
WHERE at.token = '<sequence.accessTokenHash>' -- SHA-256 of the JWT
AND at.user_id = '<sequence.userId>'
AND at.row_status = 'ACTIVE'
AND at.expired_at > '<sequence.now>'
```

### Table: [authen.t_user_access_token](../../../schema/authen/t_user_access_token.md)

#### UPDATE - Close the access tokens of the session

```SQL
UPDATE authen.t_user_access_token
SET
    updated_by = '<sequence.userId>',
    updated_at = '<sequence.now>',
    row_status = 'INACTIVE'
WHERE session_id = '<sequence.sessionId>'
AND user_id = '<sequence.userId>'
AND row_status = 'ACTIVE'
```

### Table: [authen.t_user_refresh_token](../../../schema/authen/t_user_refresh_token.md)

#### UPDATE - Close the refresh tokens of the session

```SQL
UPDATE authen.t_user_refresh_token
SET
    updated_by = '<sequence.userId>',
    updated_at = '<sequence.now>',
    row_status = 'INACTIVE'
WHERE session_id = '<sequence.sessionId>'
AND user_id = '<sequence.userId>'
AND row_status = 'ACTIVE'
```
