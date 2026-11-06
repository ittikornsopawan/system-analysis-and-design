# [POST]: v1/auth/refresh-token

| Title       | Description                                                                                                                                                                                                |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Refresh Token API                                                                                                                                                                                          |
| Method      | POST                                                                                                                                                                                                       |
| Endpoint    | v{version}/auth/refresh-token                                                                                                                                                                              |
| Version     | 1                                                                                                                                                                                                          |
| Description | Exchange a refresh token for a new access token and a new refresh token, Each refresh token can be used once (rotation), Using a refresh token again closes the whole session, The same session id is kept |

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

|     | Parameter Name | Data Type | M/O       | Description                 | Example                                  |
| --- | -------------- | --------- | --------- | --------------------------- | ---------------------------------------- |
| 1   | content-type   | String    | MANDATORY | Content type of the request | application/json                         |
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp           | 2026-11-06T09:00:00.123Z                 |
| 3   | requestId      | String    | OPTIONAL  | API Request Id              | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d |

### Body Parameters

|     | Parameter Name     | Data Type | M/O       | Description                                       | Example                                            |
| --- | ------------------ | --------- | --------- | ------------------------------------------------- | -------------------------------------------------- |
| 1   | refreshAccessToken | String    | MANDATORY | Refresh token from login or from the last refresh | rF3g7Hk9LpQ1m8vNxZpQ2w5rT8yU0i1oP3qR5sT7uV9wXyZ... |

### Refresh Token Rules

- No `authorization` header: the access token may have expired. The refresh token is the proof, only its SHA-256 is compared with `token` of `authen.t_user_refresh_token`.
- The refresh token must exist, be ACTIVE, not expired and belong to an ACTIVE user. Any other case is 401 (E10002) `Invalid or expired refresh token.`
- **Rotation:** a successful refresh makes the used refresh token INACTIVE and returns a new refresh token (14 days, configurable) and a new access token (15 minutes, configurable) of the same `session_id`. The earlier access tokens of the session stay valid until they expire, so a session can hold several valid access tokens.
- **Reuse:** when the refresh token is INACTIVE and not expired it was already used (or closed). The answer is 401 and every access token and refresh token with the same `session_id` is closed, because the token may have been stolen. **The closing of the session is committed although the answer is 401:** it is written in its own transaction that is committed before the answer is sent, it is not rolled back with the request. When the row became INACTIVE less than 10 seconds ago (configurable) the answer is 401 without closing the session, because two tabs or a double click can send the same token together.
- Lock order: look up the refresh row, lock the `authen.m_user` row of its user (`FOR UPDATE`), then change the token rows. Two refreshes with the same token together: the second one finds the row INACTIVE after the first one and falls in the 10 second case.
- Execution order: validate the request (400) -> find the refresh row (401 when none) -> lock the user row (a row comes back only for an ACTIVE user, any other user gets 401 and **nothing has changed**, the refresh token is not made INACTIVE) -> make the refresh row INACTIVE (`WHERE row_status = 'ACTIVE' AND expired_at > <now> RETURNING session_id`; when it returns nothing the answer is 401, and when the row was a reuse older than 10 seconds the session is closed and committed first) -> insert the new access token and refresh token -> answer 200. The rotation, the new tokens and the answer 200 are one transaction: when any of them fails nothing is saved.
- Both tokens are stored as SHA-256 (32 bytes), never as the token itself.

#### Example Body Parameters

```JSON
{
    "refreshAccessToken": "rF3g7Hk9LpQ1m8vNxZpQ2w5rT8yU0i1oP3qR5sT7uV9wXyZ..."
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/auth/refresh-token HTTP/1.1
Host: www.domain.com
content-type: application/json
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "refreshAccessToken": "rF3g7Hk9LpQ1m8vNxZpQ2w5rT8yU0i1oP3qR5sT7uV9wXyZ..."
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/auth/refresh-token' \
--header 'content-type: application/json' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "refreshAccessToken": "rF3g7Hk9LpQ1m8vNxZpQ2w5rT8yU0i1oP3qR5sT7uV9wXyZ..."
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

|     | Parameter Name     | Data Type | M/O       | Source           | Field                   | Description                                                          | Example                                            |
| --- | ------------------ | --------- | --------- | ---------------- | ----------------------- | -------------------------------------------------------------------- | -------------------------------------------------- |
| 1   | tokenType          | String    | MANDATORY | Sequence Diagram | data.tokenType          | Access Token Type                                                    | Bearer                                             |
| 2   | accessToken        | String    | MANDATORY | Sequence Diagram | data.accessToken        | Access Token (JWT), Valid for expiresIn seconds                      | eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...            |
| 3   | refreshAccessToken | String    | MANDATORY | Sequence Diagram | data.refreshAccessToken | Refresh Token, Expiring 14 days after it is issued, Can be used once | rF3g7Hk9LpQ1m8vNxZpQ2w5rT8yU0i1oP3qR5sT7uV9wXyZ... |
| 4   | expiresIn          | Numeric   | MANDATORY | Sequence Diagram | data.expiresIn          | Access Token Expiring in Second                                      | 900                                                |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Refresh Token Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "tokenType": "Bearer",
        "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refreshAccessToken": "rF3g7Hk9LpQ1m8vNxZpQ2w5rT8yU0i1oP3qR5sT7uV9wXyZ...",
        "expiresIn": 900
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
        "bizMessage": "Refresh Access Token is a required field.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:40:40.123Z",
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
        "bizMessage": "Invalid or expired refresh token.",
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

### Table: [authen.t_user_refresh_token](../../../schema/authen/t_user_refresh_token.md)

#### QUERY - Find the refresh token

```SQL
SELECT
    rt.id as refresh_token_id,
    rt.user_id,
    rt.session_id,
    rt.row_status,
    rt.updated_at
FROM authen.t_user_refresh_token rt
WHERE rt.token = '<sequence.refreshTokenHash>' -- SHA-256 of refreshAccessToken
AND rt.expired_at > NOW() AT TIME ZONE 'UTC'
```

#### UPDATE - Use the refresh token once

```SQL
UPDATE authen.t_user_refresh_token
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'INACTIVE'
WHERE id = '<sequence.refreshTokenId>'
AND row_status = 'ACTIVE'
AND expired_at > NOW() AT TIME ZONE 'UTC'
RETURNING session_id -- no row means the answer is 401
```

#### UPDATE - Close the refresh tokens of the session (reuse)

```SQL
UPDATE authen.t_user_refresh_token
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'INACTIVE'
WHERE session_id = '<sequence.sessionId>'
AND row_status = 'ACTIVE' -- only when the used token became INACTIVE more than 10 seconds ago
```

#### INSERT - Create refresh token

```SQL
INSERT INTO authen.t_user_refresh_token (
    created_by,
    user_id,
    session_id,
    token,
    expired_at
)
VALUES (
    '<sequence.userId>',
    '<sequence.userId>',
    '<sequence.sessionId>',
    '<sequence.refreshTokenHash>',
    '<sequence.refreshExpiredAt>' -- now plus 14 days (configurable)
)
```

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

#### UPDATE - Close the access tokens of the session (reuse)

```SQL
UPDATE authen.t_user_access_token
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'INACTIVE'
WHERE session_id = '<sequence.sessionId>'
AND row_status = 'ACTIVE' -- only when the used token became INACTIVE more than 10 seconds ago
```

#### INSERT - Create access token

```SQL
INSERT INTO authen.t_user_access_token (
    created_by,
    user_id,
    session_id,
    token,
    expired_at
)
VALUES (
    '<sequence.userId>',
    '<sequence.userId>',
    '<sequence.sessionId>',
    '<sequence.accessTokenHash>', -- SHA-256 of the JWT
    '<sequence.accessExpiredAt>' -- now plus 15 minutes (configurable)
)
```
