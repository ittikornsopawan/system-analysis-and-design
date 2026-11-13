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

- Governing decisions: [owner-confirmed API review](../../../../../docs/superpowers/specs/2026-11-07-api-review-design.md), Q4/Q7/Q12 (approved by the product owner). This detailed endpoint revision is in-review and includes no backend implementation.
- No `authorization` header is required: the access token may have expired. `refreshAccessToken` is a mandatory non-empty string, sent over TLS and compared exactly without trimming. Missing, empty or non-string input, malformed JSON or invalid mandatory headers returns 400 (E10001) before any SQL. An unknown or invalid non-empty credential returns 401 (E10002) `Invalid or expired refresh token.` All authentication failures use that same message.
- Hash the presented credential once as `presentedRefreshTokenHash` (SHA-256, 32 bytes). Capture UTC `lookupNow` immediately before the owner lookup. Do not use claims or a user/session id supplied by the request; `userId`, `refreshTokenId` and `sessionId` all come from the stored refresh row. A missing/expired lookup result returns 401 with no transaction or writes.
- Lock order: after finding the owner, BEGIN READ COMMITTED -> lock the ACTIVE `authen.m_user` row (`FOR UPDATE`) -> capture fresh UTC `now` after the lock returns -> reread the presented refresh row under that user lock -> classify the fresh state -> update token rows. For the user check, any other user gets 401 and **nothing has changed**, the refresh token is not made INACTIVE. Do not classify replay from the pre-lock row: another refresh may have consumed it while this request waited.
- The post-lock reread must still belong to this user, match the presented hash and be unexpired at `now`. A missing row, expired row, or status other than ACTIVE/INACTIVE returns 401 after ROLLBACK without issuing or revoking tokens. Reuse classification uses its current `updated_at`; PostgreSQL transaction-start `NOW()` must not substitute for time captured after a lock wait.
- **Rotation:** for a freshly ACTIVE row, atomically consume it using ACTIVE/expiry/user/session/hash guards and `RETURNING session_id`. A zero-row consume returns 401 after ROLLBACK; no replacement is issued. A successful consume, the new access/refresh rows and their common existing `session_id` are one transaction: when any of them fails nothing is saved. COMMIT must succeed before 200 is sent. Existing access tokens remain valid until their own expiry; successful rotation does not revoke them.
- **Fresh authorization claims:** after a successful consume, resolve current ACTIVE role/direct assignments, permission masters and the exact assigned scope definitions using [login's claim resolution](../02-login/spec.md#claim-resolution-and-payload). Use the same eight SQL queries and permission-specific `(permissionId, scopeId)` mapping; do not copy the original access token's claims or expand a direct assignment to all catalogue scopes. A user with no surviving grants still refreshes successfully with empty arrays. `user`, `roles`, `permissions` and `scopes` use the same payload mapping as login (owner-confirmed 2026-11-13): role names, permission names with the last `.` as `:`, `<lower-case scope code>:*` and a fresh `user` snapshot decoded from the locked user row.
- Generate a fresh JWT and 32 random bytes in base64url for a fresh refresh credential. Use distinct `newRefreshTokenHash` and `accessTokenHash`, never the presented hash, for the INSERTs. The new JWT contains `iss`, `sub`, `aud`, `jti`, `iat`, `exp` and the current `user`, `roles`, `permissions` and `scopes` claims; its default lifetime is 15 minutes (`expiresIn` 900), and the new refresh token lasts 14 days. Capture UTC `issuedAt` after claim resolution, derive both expiry values from it, and keep the existing session id. Both tokens are stored as SHA-256 (32 bytes), never as the token itself; only the newly issued raw values appear in the 200 TLS response.
- **Reuse:** a freshly INACTIVE, unexpired row was already consumed or revoked. When the row became INACTIVE less than 10 seconds ago (configurable), return 401 after ROLLBACK with no session revocation or new tokens. At exactly 10 seconds or later, or when `updated_at` is NULL and recency cannot be established, revoke every ACTIVE refresh and access row for that user/session. In particular, when the row was a reuse older than 10 seconds the session is closed and committed first. **The closing of the session is committed although the answer is 401:** it is written in its own transaction that is committed before the answer is sent, not rolled back as an authentication error. No rotation INSERT executes on either reuse path.
- The grace period handles concurrent requests: both may find the owner, but the second waits for the same user lock and then rereads INACTIVE with the first request's fresh `updated_at`. It returns 401 without closing the newly rotated session when within the grace window. A request that waited until the credential expired changes nothing. A concurrent logout/reset holding the same user lock cannot be bypassed by a stale pre-lock refresh snapshot.
- Any timeout before COMMIT rolls back current writes and returns 408 (E90001). An unexpected pre-commit failure rolls back and returns the generic 500 example without a new bizCode. Never send 200 or replay-related 401 before the required COMMIT. A lost response after COMMIT cannot undo durable rotation/revocation. A client that loses the rotated token pair must not assume the old refresh token can recover it.
- Execution order: validate -> hash/find owner -> BEGIN -> lock ACTIVE user -> capture now -> reread fresh token -> ACTIVE: consume once, reload claims, create both fresh tokens, COMMIT, 200; INACTIVE/recent: ROLLBACK, 401; INACTIVE/older: revoke both token tables, COMMIT, 401; other invalid state or failed consume: ROLLBACK, 401. Earlier invalid lookup has no transaction. Successful rotation never runs the replay revocation queries.

#### Scenario correspondence with sequence.wsd

| Scenario                           | Required sequence behavior                                                  | HTTP                | Durable effects                    |
| ---------------------------------- | --------------------------------------------------------------------------- | ------------------- | ---------------------------------- |
| Invalid input                      | No SQL or transaction                                                       | 400 E10001          | None                               |
| Owner lookup missing/expired       | Lookup only; no BEGIN                                                       | 401 E10002          | None                               |
| Inactive/missing user              | Lock returns no ACTIVE user; ROLLBACK                                       | 401 E10002          | None                               |
| Fresh token invalid after waiting  | Post-lock reread fails state/expiry; ROLLBACK                               | 401 E10002          | None                               |
| Conditional consume returns no row | No replacement; ROLLBACK                                                    | 401 E10002          | None                               |
| Recent duplicate                   | Fresh INACTIVE timestamp within grace; ROLLBACK                             | 401 E10002          | No revocation                      |
| Older replay / unknown recency     | Close both token tables; COMMIT before 401                                  | 401 E10002          | Session-wide revocation            |
| Rotation succeeds                  | Consume once; reload current claims; insert fresh tokens; COMMIT before 200 | 200 S10000          | Rotation and both new token hashes |
| Timeout                            | ROLLBACK before response                                                    | 408 E90001          | No uncommitted writes persist      |
| Unexpected failure                 | ROLLBACK before generic response                                            | 500, no new bizCode | No uncommitted writes persist      |

All database results return to Application before branch decisions or later parameters use them. Quoted SQL value lines remain visible in the rendered sequence, and decoded note SQL matches the specification exactly.

#### Acceptance criteria

- Two concurrent uses of one refresh credential produce at most one new pair. The losing request classifies the reread state, not the original snapshot, and cannot silently invalidate the winner inside the grace interval.
- Delayed replay outside the grace period revokes every access/refresh token in the same session and commits this before returning 401; sessions of other users/devices are unaffected.
- Refresh loads current grants using login's exact resolver, including empty grants, direct-scope subsets, inactive definitions/masters and mismatched scope ids. Already issued access-token claims remain effective only until their own expiry as previously agreed.
- Presented and newly generated refresh credentials have different hashes; no response, log or query exposes stored hashes, salts or a previously issued raw token.
- Both token INSERTs roll back with a failed consume/claim load/insert. No invalid, recent-duplicate or replay branch creates any new token.

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
