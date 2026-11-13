---
name: Refresh Token API Specification
description: Defines refresh rotation, current authorization claims, replay handling, session revocation and exact transactional SQL; read when implementing or reviewing POST v1/auth/refresh-token.
status: in-review
approved_by: null
approved_at: null
---

# [POST]: v1/auth/refresh-token

| Title       | Description                                                                                                                                                                                |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Name        | Refresh Token API                                                                                                                                                                          |
| Method      | POST                                                                                                                                                                                       |
| Endpoint    | v{version}/auth/refresh-token                                                                                                                                                              |
| Version     | 1                                                                                                                                                                                          |
| Description | Exchange one refresh token for fresh access/refresh tokens and current permission-specific claims; preserve the session, reject a recent duplicate, and revoke the session on older replay |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- Governing decisions: owner-confirmed API review Q4/Q7/Q12 (approved by the product owner).
- No `authorization` header is required: the access token may have expired.
- Hash the presented credential once as `presentedRefreshTokenHash` (SHA-256, 32 bytes).
- The post-lock reread must still belong to this user, match the presented hash and be unexpired at `now`.
- **Rotation:** for a freshly ACTIVE row, atomically consume it using ACTIVE/expiry/user/session/hash guards and `RETURNING session_id`.
- **Fresh authorization claims:** after a successful consume, resolve current ACTIVE role/direct assignments, permission masters and the exact assigned scope definitions using login's claim resolution.
- The order of the checks, the locks and every outcome is in the sequence diagram.

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

#### Fail - Internal Server Error

```JSON
{
    "status": {
        "code": 500,
        "message": "Internal Server Error",
        "bizMessage": "An unexpected error occurred.",
        "requestId": "req-500a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

Statements are listed in first source-execution order. Rotation and replay-revocation statements are mutually exclusive branches. Array parameters and claim resolution are identical to login; empty lists are bound as empty UUID arrays. All parameters are bound values, never concatenated SQL.

### Table: [authen.t_user_refresh_token](../../../schema/authen/t_user_refresh_token.md)

#### QUERY - Find the refresh token

```SQL
SELECT
    rt.id as refresh_token_id,
    rt.user_id
FROM authen.t_user_refresh_token rt
WHERE rt.token = '<sequence.presentedRefreshTokenHash>'
AND rt.expired_at > '<sequence.lookupNow>'
```

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Lock the user

```SQL
SELECT
    u.id as user_id,
    u.username,
    u.email_address,
    u.display_name
FROM authen.m_user u
WHERE u.id = '<sequence.userId>'
AND u.row_status = 'ACTIVE'
FOR UPDATE -- every authen API locks the user row first
```

### Table: [authen.t_user_refresh_token](../../../schema/authen/t_user_refresh_token.md)

#### QUERY - Reread the refresh token after user lock

```SQL
SELECT
    rt.id as refresh_token_id,
    rt.user_id,
    rt.session_id,
    rt.row_status,
    rt.updated_at,
    rt.expired_at
FROM authen.t_user_refresh_token rt
WHERE rt.id = '<sequence.refreshTokenId>'
AND rt.user_id = '<sequence.userId>'
AND rt.token = '<sequence.presentedRefreshTokenHash>'
```

### Table: [authen.t_user_refresh_token](../../../schema/authen/t_user_refresh_token.md)

#### UPDATE - Use the refresh token once

```SQL
UPDATE authen.t_user_refresh_token
SET
    updated_by = '<sequence.userId>',
    updated_at = '<sequence.now>',
    row_status = 'INACTIVE'
WHERE id = '<sequence.refreshTokenId>'
AND user_id = '<sequence.userId>'
AND session_id = '<sequence.sessionId>'
AND token = '<sequence.presentedRefreshTokenHash>'
AND row_status = 'ACTIVE'
AND expired_at > '<sequence.now>'
RETURNING session_id -- no row means the answer is 401
```

### Table: [author.t_user_role](../../../schema/author/t_user_role.md)

#### QUERY - Get active role ids

```SQL
SELECT
    ur.role_id
FROM author.t_user_role ur
WHERE ur.user_id = '<sequence.userId>'
AND ur.row_status = 'ACTIVE'
```

### Table: [author.m_role](../../../schema/author/m_role.md)

#### QUERY - Get active roles

```SQL
SELECT
    r.id AS role_id,
    r.name AS role_name
FROM author.m_role r
WHERE r.id = ANY ('<sequence.roleIds>'::UUID[])
AND r.row_status = 'ACTIVE'
```

### Table: [author.t_role_permission](../../../schema/author/t_role_permission.md)

#### QUERY - Get active role permissions

```SQL
SELECT
    rp.id AS role_permission_id,
    rp.permission_id
FROM author.t_role_permission rp
WHERE rp.role_id = ANY ('<sequence.activeRoleIds>'::UUID[])
AND rp.row_status = 'ACTIVE'
```

### Table: [author.t_role_permission_scope](../../../schema/author/t_role_permission_scope.md)

#### QUERY - Get active role permission scopes

```SQL
SELECT
    rps.role_permission_id,
    rps.permission_scope_id
FROM author.t_role_permission_scope rps
WHERE rps.role_permission_id = ANY ('<sequence.rolePermissionIds>'::UUID[])
AND rps.row_status = 'ACTIVE'
```

### Table: [author.t_user_permission](../../../schema/author/t_user_permission.md)

#### QUERY - Get active direct permissions

```SQL
SELECT
    up.permission_id,
    up.permission_scope_id
FROM author.t_user_permission up
WHERE up.user_id = '<sequence.userId>'
AND up.row_status = 'ACTIVE'
```

### Table: [author.t_permission_scope](../../../schema/author/t_permission_scope.md)

#### QUERY - Get permission scope definitions

```SQL
SELECT
    ps.id AS permission_scope_id,
    ps.permission_id,
    ps.scope_id,
    ps.row_status
FROM author.t_permission_scope ps
WHERE ps.permission_id = ANY ('<sequence.permissionIds>'::UUID[])
AND ps.row_status <> 'DELETED'
```

### Table: [author.m_permission](../../../schema/author/m_permission.md)

#### QUERY - Get active permissions

```SQL
SELECT
    p.id AS permission_id,
    p.name AS permission_name
FROM author.m_permission p
WHERE p.id = ANY ('<sequence.permissionIds>'::UUID[])
AND p.row_status = 'ACTIVE'
```

### Table: [author.m_scope](../../../schema/author/m_scope.md)

#### QUERY - Get active scopes

```SQL
SELECT
    s.id AS scope_id,
    s.scope
FROM author.m_scope s
WHERE s.id = ANY ('<sequence.assignedScopeIds>'::UUID[])
AND s.row_status = 'ACTIVE'
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
    '<sequence.sessionId>',
    '<sequence.accessTokenHash>',
    '<sequence.accessExpiredAt>' -- issuedAt plus 15 minutes (configurable)
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
    '<sequence.newRefreshTokenHash>',
    '<sequence.refreshExpiredAt>' -- issuedAt plus 14 days (configurable)
)
```

### Table: [authen.t_user_refresh_token](../../../schema/authen/t_user_refresh_token.md)

#### UPDATE - Close the refresh tokens of the session (reuse)

```SQL
UPDATE authen.t_user_refresh_token
SET
    updated_by = '<sequence.userId>',
    updated_at = '<sequence.now>',
    row_status = 'INACTIVE'
WHERE session_id = '<sequence.sessionId>'
AND user_id = '<sequence.userId>'
AND row_status = 'ACTIVE' -- only on replay outside the 10-second grace window
```

### Table: [authen.t_user_access_token](../../../schema/authen/t_user_access_token.md)

#### UPDATE - Close the access tokens of the session (reuse)

```SQL
UPDATE authen.t_user_access_token
SET
    updated_by = '<sequence.userId>',
    updated_at = '<sequence.now>',
    row_status = 'INACTIVE'
WHERE session_id = '<sequence.sessionId>'
AND user_id = '<sequence.userId>'
AND row_status = 'ACTIVE' -- only on replay outside the 10-second grace window
```
