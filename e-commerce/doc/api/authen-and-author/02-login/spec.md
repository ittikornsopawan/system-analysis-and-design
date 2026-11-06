# [POST]: v1/auth/login

| Title       | Description                                                                                                                                                                                                                                   |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Login API                                                                                                                                                                                                                                     |
| Method      | POST                                                                                                                                                                                                                                          |
| Endpoint    | v{version}/auth/login                                                                                                                                                                                                                         |
| Version     | 1                                                                                                                                                                                                                                             |
| Description | Authenticate a user by username or email address and password, record the session and issue an access token and a refresh token, A username that failed 5 times in 15 minutes is refused for a while with the same answer as a wrong password |

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
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp           | 2026-11-05T12:42:00.123Z                 |
| 3   | requestId      | String    | OPTIONAL  | API Request Id              | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d |

### Body Parameters

|     | Parameter Name | Data Type | M/O       | Description                                                                                  | Example          |
| --- | -------------- | --------- | --------- | -------------------------------------------------------------------------------------------- | ---------------- |
| 1   | username       | String    | MANDATORY | Username or email address, Plain text over TLS, The system encrypts it before it is compared | john.doe         |
| 2   | password       | String    | MANDATORY | Password, Plain text over TLS                                                                | Passw0rd-Example |

### Login Rules

- `username` is the username or the email address. It is sent as plain text over TLS and encrypted by the system before it is compared (same deterministic encryption as `01-register`). Login by phone number is not supported.
- Only an ACTIVE user with an ACTIVE PASSWORD row can log in. The password is hashed with PBKDF2-HMAC-SHA256, the salt of the current password row and 600,000 iterations, and compared in constant time. Approved by the product owner (answered through the lead SA, 2026-11-06).
- **One answer for every failure:** an unknown username, a wrong password, a user that is not ACTIVE and a username that is temporarily refused all get 401 (E10002) `Invalid username or password.` The answer never says which one it is.
- **Brute force limit:** every request is written to `authen.l_user_login_attempt` with the SHA-256 of the username (also for names that do not exist) and a `result`: `SUCCESS`, `FAILED` (the password was checked and was wrong, or the user was not found or not ACTIVE) or `REFUSED` (the username was blocked and the password was not checked). **Only `FAILED` rows are counted.** When the username has 5 `FAILED` attempts in the last 15 minutes (configurable) the request is refused without checking the password, answered with the same 401 and recorded as `REFUSED`, which is not counted. The block therefore ends by itself as soon as the 5th most recent failure is older than 15 minutes, however many requests arrive meanwhile. Example: failures at 09:00, 09:01, 09:02, 09:03 and 09:04 block the username from 09:04, the requests from 09:05 to 09:14 are `REFUSED`, and at 09:15:01 the failure of 09:00 is older than 15 minutes, so 4 are counted and the next request checks the password. The `FAILED` and `REFUSED` rows are committed although the answer is 401 (they are written outside the transaction that creates the tokens). The lock is not stored in `authen.m_user` (the `LOCKED` status is kept for administrators). Attempts older than 30 days are deleted by a system job.
- **Session:** a successful login creates a new `session_id` and inserts one access token row and one refresh token row, both with that `session_id`, in one transaction. The tokens are stored as SHA-256 (32 bytes), never as the token itself. The access token is a JWT (HS256) with `sub` (user id), `jti`, `iss`, `aud`, `iat` and `exp`, valid 15 minutes (`expiresIn` 900, configurable). The refresh token is 32 random bytes (base64url), valid 14 days (configurable) and usable once (see `05-refresh-token`).
- Lock order: after the password matches, lock the `authen.m_user` row (`FOR UPDATE`), then write the tokens and the attempt.
- Execution order: validate the request (400) -> count the `FAILED` attempts of the last 15 minutes (record `REFUSED` and answer 401 when there are 5) -> find the ACTIVE user -> get the current password and compare (record `FAILED` and answer 401 when it does not match or the user is not found) -> lock the user row -> insert the access token and the refresh token -> record `SUCCESS` -> answer 200.

#### Example Body Parameters

```JSON
{
    "username": "john.doe",
    "password": "Passw0rd-Example"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/auth/login HTTP/1.1
Host: www.domain.com
content-type: application/json
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "username": "john.doe",
    "password": "Passw0rd-Example"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/auth/login' \
--header 'content-type: application/json' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "username": "john.doe",
    "password": "Passw0rd-Example"
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

|     | Parameter Name     | Data Type | M/O       | Source           | Field                   | Description                                                                                      | Example                                            |
| --- | ------------------ | --------- | --------- | ---------------- | ----------------------- | ------------------------------------------------------------------------------------------------ | -------------------------------------------------- |
| 1   | tokenType          | String    | MANDATORY | Sequence Diagram | data.tokenType          | Access Token Type                                                                                | Bearer                                             |
| 2   | accessToken        | String    | MANDATORY | Sequence Diagram | data.accessToken        | Access Token                                                                                     | eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...            |
| 3   | refreshAccessToken | String    | MANDATORY | Sequence Diagram | data.refreshAccessToken | Refresh Token, Expiring 14 days after it is issued, Can be used once (see the refresh token API) | rF3g7Hk9LpQ1m8vNxZpQ2w5rT8yU0i1oP3qR5sT7uV9wXyZ... |
| 4   | expiresIn          | Numeric   | MANDATORY | Sequence Diagram | data.expiresIn          | Access Token Expiring in Second                                                                  | 900                                                |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Logged-in Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
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
        "bizMessage": "Username and Password are required fields.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:45.123Z",
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
        "bizMessage": "Invalid username or password.",
        "requestId": "req-7a2cba3e-1b2d-4caf-8cce-3b1d7b3dcb6d",
        "timestamp": "2026-11-05T12:43:10.456Z",
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

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY

```SQL
SELECT 
    u.id as user_id
FROM authen.m_user u
WHERE (u.username = '<sequence.usernameBytes>' OR u.email_address = '<sequence.usernameBytes>')
AND u.row_status = 'ACTIVE'
```

### Table: [authen.m_user_password](../../../schema/authen/m_user_password.md)

#### QUERY - Get current password

```SQL
SELECT
    up.user_id,
    up.password_salt
FROM authen.m_user u
INNER JOIN authen.m_user_password up 
    ON u.id = up.user_id 
        AND up.row_type = 'PASSWORD'
        AND up.row_status = 'ACTIVE'
WHERE (u.username = '<sequence.usernameBytes>' OR u.email_address = '<sequence.usernameBytes>')
AND u.row_status = 'ACTIVE'
```

#### QUERY - Get matching user_id and password

```SQL
SELECT
    up.user_id
FROM authen.m_user u
INNER JOIN authen.m_user_password up 
    ON u.id = up.user_id 
WHERE (u.username = '<sequence.usernameBytes>' OR u.email_address = '<sequence.usernameBytes>')
AND u.row_status = 'ACTIVE'
AND up.row_type = 'PASSWORD'
AND up.row_status = 'ACTIVE'
AND up.password = '<sequence.passwordBytes>'
```

### Table: [authen.l_user_login_attempt](../../../schema/authen/l_user_login_attempt.md)

#### QUERY - Count failed attempts

```SQL
SELECT
    COUNT(la.id) as failed_attempts
FROM authen.l_user_login_attempt la
WHERE la.identifier_hash = '<sequence.identifierHash>' -- SHA-256 of the username that was sent
AND la.result = 'FAILED' -- refused attempts are never counted
AND la.created_at > '<sequence.windowStart>' -- now minus 15 minutes (configurable)
```

#### INSERT - Record attempt

```SQL
INSERT INTO authen.l_user_login_attempt (
    created_by,
    identifier_hash,
    user_id,
    result
)
VALUES (
    'system',
    '<sequence.identifierHash>',
    '<sequence.userId>', -- NULL when the username does not exist
    '<sequence.result>' -- SUCCESS, FAILED or REFUSED
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
    '<sequence.sessionId>', -- a new session id for every login
    '<sequence.accessTokenHash>', -- SHA-256 of the JWT
    '<sequence.accessExpiredAt>' -- now plus 15 minutes (configurable)
)
```

### Table: [authen.t_user_refresh_token](../../../schema/authen/t_user_refresh_token.md)

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
    '<sequence.refreshTokenHash>', -- SHA-256 of the refresh token
    '<sequence.refreshExpiredAt>' -- now plus 14 days (configurable)
)
```
