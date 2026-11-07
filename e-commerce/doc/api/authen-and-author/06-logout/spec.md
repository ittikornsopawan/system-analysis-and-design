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

### Logout Rules

- Governing behavior: [owner-confirmed review](../../../../../docs/superpowers/specs/2026-11-07-api-review-design.md), Q13, approved by the product owner, and WP4 U9/U23. This detailed endpoint revision remains in-review; no backend implementation is included. No administrator role is required to log out of one's own session.
- No body or target userId/sessionId is accepted. Validate mandatory timestamp as a UTC timestamp and empty body before SQL; invalid input returns 400 E10001. Generate requestId when omitted. Missing/malformed Bearer credentials or failed JWT signature/issuer/audience/expiry/UUID sub validation return the same 401 E10002 `Invalid or expired access token.` before a transaction.
- Derive userId only from verified JWT sub and accessTokenHash as SHA-256 (32 bytes) of the exact presented JWT. Never take userId/sessionId from the request or trust an unverified token payload. JWT role/permission changes do not change this self-session operation; current credential/user checks are still required.
- Lock order: BEGIN READ COMMITTED -> lock the ACTIVE authen.m_user row FOR UPDATE -> capture fresh server UTC now after the lock -> recheck JWT expiry and read the ACTIVE stored access token/session using hash, userId and expiry > now -> close the session's access rows -> close the session's refresh rows -> COMMIT -> 200. Do not use a pre-lock token/session snapshot or transaction-start NOW() to authorize a waiter. No token UPDATE may run before the user lock and fresh credential check.
- Missing/inactive user or missing/revoked/expired/mismatched credential returns the same 401 after ROLLBACK, with no token changes. sessionId comes only from the post-lock access-token row; it is not a JWT flag or caller-selected target. If the JWT expires while waiting, the post-lock expiry check rejects the call even if it passed before the wait.
- Close **every ACTIVE access token and refresh token that has the same `session_id` as the access token of the request**, including all access tokens issued by earlier refreshes in that session. Both UPDATEs also guard user_id. Sessions of other devices are not changed. Other users are unaffected even if legacy data reuses a sessionId. Do not filter revocation to the presented token hash or only unexpired rows: all ACTIVE rows of this user/session become INACTIVE.
- The common user lock serializes logout with refresh, password reset and other conforming credential writers for that user. If refresh commits first, logout reads its still-valid presented access token and closes the newly issued pair too. If logout commits first, a later refresh rereads an INACTIVE credential and cannot issue new tokens. A second concurrent logout waits, then finds its access token INACTIVE and returns 401 without writes. Calling logout again likewise answers 401.
- Both token-table changes are one transaction. Zero refresh rows is allowed when none remains ACTIVE; the access token that authorized the request must be included in access closure. Use returned affected counts for consistency checks; an unexpected zero access-row update after valid authorization is an internal failure that rolls back, not 200. Do not commit only one token table. All parameters are typed bound UUIDs/bytes/timestamps, never interpolated SQL; updatedBy is the verified userId.
- COMMIT must succeed before 200 S10000 `Logout Success` with status only and no data. On timeout before commit, ROLLBACK then 408 E90001; on unexpected pre-commit failure, ROLLBACK then generic 500 without a new bizCode. None of the 400/401/408/500 paths intentionally preserves a token change. A lost response after commit does not undo logout: retry with that token returns 401 because revocation is durable.
- A successful logout does not issue tokens, refresh claims, alter roles/passwords, or affect another session. Each database result returns to Application before branching or deriving sessionId. Return generic credential errors without revealing whether user/token/session exists.

#### Scenario correspondence with sequence.wsd

| Scenario                                         | Required sequence behavior                                       | HTTP             | Durable effects                                 |
| ------------------------------------------------ | ---------------------------------------------------------------- | ---------------- | ----------------------------------------------- |
| Invalid timestamp/body                           | No SQL or BEGIN                                                  | 400 E10001       | None                                            |
| Missing/invalid JWT                              | No SQL or BEGIN                                                  | 401 E10002       | None                                            |
| Missing/inactive user                            | User lock returns no ACTIVE row; ROLLBACK                        | 401 E10002       | None                                            |
| Revoked/expired/mismatched token after lock wait | Fresh token check fails; ROLLBACK                                | 401 E10002       | None                                            |
| Valid current session                            | Close both token tables after lock/check, COMMIT before response | 200 S10000       | All ACTIVE tokens in that user/session INACTIVE |
| Unexpected zero access closure                   | Abort and ROLLBACK before common success                         | 500              | None                                            |
| Concurrent refresh first                         | Close its new pair too under the same user lock                  | 200 S10000       | Session remains fully revoked                   |
| Concurrent logout first / repeated call          | Fresh credential check sees INACTIVE                             | 401 E10002       | No additional writes                            |
| Timeout / other pre-commit failure               | ROLLBACK every token change                                      | 408 E90001 / 500 | None                                            |

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
