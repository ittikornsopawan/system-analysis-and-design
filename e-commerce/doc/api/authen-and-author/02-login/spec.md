---
name: Login API Specification
description: Defines the login request, authentication controls, authorization claims, token session, responses, and database operations for POST v1/auth/login.
status: in-review
approved_by: null
approved_at: null
---

# [POST]: v1/auth/login

| Title       | Description                                                                                                                                                                                                                                                                              |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Login API                                                                                                                                                                                                                                                                                |
| Method      | POST                                                                                                                                                                                                                                                                                     |
| Endpoint    | v{version}/auth/login                                                                                                                                                                                                                                                                    |
| Version     | 1                                                                                                                                                                                                                                                                                        |
| Description | Authenticate a user by username or email address and password, load active roles, permissions and scopes, record the session and issue an access token and a refresh token, A username that failed 5 times in 15 minutes is refused for a while with the same answer as a wrong password |

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

- Governing behavior is [the owner-confirmed API review](../../../../../docs/superpowers/specs/2026-11-07-api-review-design.md) (Q2, Q4, Q7, Q12–Q14, approved by the product owner directly in this task on 2026-11-07). This detailed endpoint revision is in-review; no backend implementation is included.
- Validate headers and the JSON body before opening a transaction. `username` is a non-empty string of at most 254 characters and `password` is a non-empty string of at most 128 characters; malformed or missing values answer 400 (E10001). Do not apply the registration password-complexity rule to a login attempt. `timestamp` is a valid UTC timestamp; generate `requestId` when it is omitted.
- `username` is the username or the email address. It is sent as plain text over TLS and encrypted by the system before it is compared (same deterministic encryption as `01-register`). Compare the supplied identifier exactly, without silently changing case or trimming it. Login by phone number is not supported. If it matches two ACTIVE accounts across username/email, the identifier is **ambiguous**: record `FAILED`, do not choose an account, and answer the same 401 (Q14). An unknown or ambiguous identifier has NULL `user_id` in the attempt log.
- Only an ACTIVE user with an ACTIVE PASSWORD row can log in. Lock the matching user rows in ascending `id` order before reading the current password; proceed only when exactly one ACTIVE user matches. Read the stored salted hash and salt once, derive PBKDF2-HMAC-SHA256 with 600,000 iterations in the application, and compare hashes using a **constant-time** comparison. The password is never compared with a SQL `=` predicate. Perform a dummy hash/constant-time comparison for an unknown or ambiguous user or a missing password row; no token is issued. Never log passwords, hashes, salts or raw tokens.
- **One answer for every failure:** an unknown or ambiguous username, a wrong password, a missing ACTIVE PASSWORD row, a user that is not ACTIVE and a username that is temporarily refused all get 401 (E10002) `Invalid username or password.` The answer never says which one it is.
- **Brute force limit:** every syntactically valid login attempt is written to `authen.l_user_login_attempt` with the SHA-256 of the exact supplied username and a `result`: `SUCCESS`, `FAILED` or `REFUSED`. **Only `FAILED` rows are counted.** When the username has 5 `FAILED` attempts in the last 15 minutes (configurable), refuse without looking up the user or checking a password; it is recorded as `REFUSED`, which is not counted. The block therefore ends by itself as soon as the 5th most recent failure is older than 15 minutes, however many requests arrive meanwhile. A missing/malformed request (400) is not an authentication attempt and is not stored.
- **Concurrent attempts:** begin a READ COMMITTED transaction and acquire `pg_advisory_xact_lock` for the identifier before counting failures. `identifierLockKey` is the signed 64-bit, big-endian interpretation of the first eight bytes of `identifierHash`; it only serializes attempts (the full 32-byte hash still selects the log rows). Capture `now` and `windowStart` after acquiring the lock. Hold this transaction-scoped lock through the attempt insert and COMMIT/ROLLBACK, so concurrent requests for the same identifier cannot all pass a stale count. Username and email are distinct supplied identifiers; the counter is per supplied identifier, as in WP4.
- The `FAILED` and `REFUSED` rows are committed although the answer is 401. Those branches perform no token writes. `SUCCESS`, the two token rows and their common session are committed atomically. A failed attempt does not change `authen.m_user.row_status`; the `LOCKED` status remains an administrative state. Attempts older than 30 days are deleted by a system job.
- **Authorization claims:** after password verification, load ACTIVE user-role assignments and ACTIVE roles, then role/direct permission assignments and the permission-scope definitions they reference. Resolve ACTIVE permission and scope masters. Preserve the `(permissionId, scopeId)` association; scope definitions are a catalogue, not grants. In particular, `t_role_permission_scope.permission_scope_id` references `t_permission_scope.id`, not `m_scope.id`, and a direct assignment uses its own `t_user_permission.permission_scope_id`, not every scope defined for that permission. See the resolution rules below. A user with no assigned role or permission can still log in with empty claim arrays.
- **JWT authorization:** `roles`, `permissions` and `scopes` are the effective authorization snapshot for this access token. Assignment or role/permission/scope-status changes may leave former privileges usable until that token expires (15 minutes by configuration). Every new access token at login or refresh resolves current assignments; refresh must not copy the old claims. Keep signature, issuer, audience, expiry, ACTIVE token-row and ACTIVE user checks on protected calls so logout/password reset still revoke credentials immediately. `author/me` will display this same token snapshot. Dependent endpoints are migrated in separate PRs; this login PR does not claim they are already synchronized.
- **Session:** successful login creates a new `session_id` and inserts one access token and one refresh token with that session id. The access token is a JWT (HS256) with `iss`, `sub`, `aud`, `jti`, `iat`, `exp`, `user`, `roles`, `permissions` and `scopes`; default `exp - iat` and `expiresIn` are 900 seconds. The refresh token is 32 random bytes in base64url, valid 14 days, and usable once (`05-refresh-token`). Both database tokens are stored as SHA-256 (32 bytes), never as the token itself. Issuer, audience, lifetimes and signing key are server configuration, never request values.
- Lock order: identifier advisory lock -> matching `authen.m_user` rows by `id` (`FOR UPDATE`) -> current password read -> authorization reads -> token and attempt inserts. A reset that changes the password must hold the same user-row lock, so login cannot verify an old password and then issue tokens after that reset commits.
- Execution order: validate (400) -> BEGIN and serialize/count -> record `REFUSED` and answer 401 when there are 5 (after committing the attempt, without a password read) -> lock/find the user -> read and verify the current password -> record `FAILED` and answer 401 when it does not match or the user is not found (also when ambiguous, after committing the attempt) -> resolve claims -> create both tokens -> record `SUCCESS` -> COMMIT -> answer 200.
- Any timeout before COMMIT rolls the transaction back, including token and attempt inserts, and answers 408 (E90001). An unexpected failure before COMMIT also rolls back and answers 500 with the generic example below and no new bizCode. Never send 200 or 401 before a successful COMMIT. A lost response after COMMIT cannot undo the durable transaction; login is not idempotent, and a retry creates a different session.

#### Claim resolution and payload

No role, permission or scope definition creates a grant on its own. Empty UUID lists are bound as empty `UUID[]` parameters (`{}`); each `ANY` query then returns zero rows. Placeholder text below denotes bound parameters, never string concatenation.

1. Resolve `activeRoleIds` from the intersection of ACTIVE `t_user_role` rows and ACTIVE `m_role` rows. Only those role ids feed the role-permission query.
2. Candidate permissions come only from ACTIVE `t_role_permission` rows of these active roles, or ACTIVE `t_user_permission` rows of this user. Remove candidates whose `m_permission` row is not ACTIVE.
3. Read the non-DELETED `t_permission_scope` definitions of candidate permissions to determine whether a permission is scoped. For a scoped role grant, join an ACTIVE `t_role_permission_scope` row back to its `role_permission_id`, then to its exact ACTIVE definition by `permission_scope_id`; the definition's `permission_id` must equal that role permission's `permission_id`. For a scoped direct grant, the exact ACTIVE definition must match both the direct assignment's `permission_scope_id` and `permission_id`. A missing, inactive or mismatched definition grants nothing.
4. Derive `assignedScopeIds` only from those matched assignment-definition pairs and retain only ACTIVE `m_scope` rows. Never infer a grant from the catalogue alone. A scoped permission with no surviving assigned scope is omitted. A NULL direct scope, or a role grant with no ACTIVE scope link, grants an unscoped permission only when that permission has no non-DELETED scope definition; it is not a wildcard for a scoped permission. An ACTIVE role-scope link that fails resolution must not be reinterpreted as an unscoped role grant.
5. Merge role and direct grants by `permissionId`. Deduplicate roles by `roleId`, permissions by `permissionId`, and scope grants by `(permissionId, scopeId)`. Sort roles by `(name, roleId)`, permissions by `(name, permissionId)`, and scope grants by `(permissionId, scope, scopeId)`. A consumer checks scopes for the requested permission id, never the union of every permission's scopes.

6. Map the resolved grants to the payload claims (owner-confirmed 2026-11-13, see the [JWT payload decision](../../../../../docs/superpowers/specs/2026-11-07-api-review-design.md)): `roles` is the sorted unique list of the ACTIVE role names; `permissions` is the sorted unique list of the effective permission names with the last `.` replaced by `:` (`catalog.manage` becomes `catalog:manage`, `shop.product.manage` becomes `shop.product:manage`; the stored name never changes); `scopes` is the sorted unique list of `<lower-case scope code>:*` of the surviving assigned scopes (`OWN` becomes `own:*`), meaning every instance of that type. Q12 still governs the permission-specific resolution above, but the payload no longer shows which permission a scope belongs to: a consumer must not treat a scope as granted to every permission, and an API still checks membership or ownership of the data itself (Q10). `user` is `{id, username, displayName, email}` decoded from the locked user row (`username` and `email` are decrypted by the Application, `displayName` is null when not set); it is a snapshot for display and never an authorization input. A permission without a scope definition contributes no scope. `sub` equals `user.id`; the payload never includes credentials or other profile fields.

#### Example JWT Payload

```JSON
{
    "iss": "https://www.domain.com",
    "sub": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
    "aud": "ecommerce",
    "jti": "8bf3ef1e-cddc-4ad7-b627-5ed8093675ca",
    "iat": 1793882520,
    "exp": 1793883420,
    "user": {
        "id": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
        "username": "johndoe",
        "displayName": "John Doe",
        "email": "john.doe@example.com"
    },
    "roles": [
        "CATALOG_MANAGER"
    ],
    "permissions": [
        "catalog:manage",
        "order:view"
    ],
    "scopes": [
        "all:*",
        "own:*"
    ]
}
```

The example is a decoded illustrative payload, not a usable signed token. The payload is flat: `own:*` and `all:*` do not say which permission they belong to. The HTTP response still contains the same four token fields as before.

#### Acceptance criteria

- 400 opens no transaction. REFUSED reads no user/password and does not extend the failure window. Unknown, ambiguous and incorrect credentials return the same 401; each 401 requires its attempt insert to commit.
- Concurrent attempts for one identifier serialize the count and log; only FAILED contributes to the 5-in-15-minute threshold. Password lookup/verification occurs under the user lock.
- The payload has exactly `iss`, `sub`, `aud`, `jti`, `iat`, `exp`, `user`, `roles`, `permissions` and `scopes`; the three claim lists are sorted unique strings and may be empty.
- Role/direct scope resolution cannot grant a different permission's scope, all catalogue scopes, inactive masters/assignments, or a scoped permission with no valid assigned scope. A user with no grants still receives valid tokens and empty claim arrays.
- Success commits both token hashes and SUCCESS together; pre-commit failure rolls back all of them. No secret is logged or returned except the newly issued raw tokens in the successful TLS response.
- The sequence contains the same SQL as this spec and shows every validation, failed/refused, success, timeout and internal-error path explicitly.

#### Scenario correspondence with sequence.wsd

Read this table alongside [sequence.wsd](sequence.wsd). These are seven control-flow paths; empty grants and invalid scope bindings are additional data cases inside the successful path. SQL parity, branch checks and rendered-text checks provide separate evidence.

| Scenario                                  | Required sequence branch and data handoff                                                                                     | HTTP                | Durable effects                                  |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ------------------- | ------------------------------------------------ |
| Malformed headers/body                    | Invalid input; no BEGIN or SQL                                                                                                | 400 E10001          | None                                             |
| Failure limit reached                     | failed_attempts >= 5; no user/password lookup; result REFUSED                                                                 | 401 E10002          | Attempt commits; no token rows                   |
| Unknown, inactive or ambiguous identifier | user_count != 1 after matchedUsers return; dummy verification; result FAILED                                                  | 401 E10002          | Attempt commits with NULL user_id; no token rows |
| Missing password or mismatch              | user_count = 1; passwordRow return; password verification; result FAILED                                                      | 401 E10002          | Attempt commits; no token rows                   |
| Valid credentials                         | Password matches; all role/direct/scope results return to Application; claims built before both token inserts; result SUCCESS | 200 S10000          | Both token hashes and attempt commit together    |
| Timeout before commit                     | Timeout alternative; ROLLBACK before response                                                                                 | 408 E90001          | No uncommitted token/attempt writes persist      |
| Unexpected failure before commit          | Failure alternative; ROLLBACK before generic response                                                                         | 500, no new bizCode | No uncommitted token/attempt writes persist      |

Every SQL interaction has an Application request, Infrastructure/database execution, database return while active, and an Infrastructure result returned to Application before that result is used. The role/permission-id arrays are derived explicitly. Success names all four response data fields in the sequence.

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

#### Fail - Internal Server Error

```JSON
{
    "status": {
        "code": 500,
        "message": "Internal Server Error",
        "bizMessage": "An unexpected error occurred.",
        "requestId": "req-500a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:30.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

SQL blocks are listed in first-execution order. The final attempt insert is shared by the three mutually exclusive result branches. All statements belong to the same explicit transaction; only the successful branch writes token rows.

### Table: [authen.l_user_login_attempt](../../../schema/authen/l_user_login_attempt.md)

#### QUERY - Serialize identifier

```SQL
SELECT pg_advisory_xact_lock('<sequence.identifierLockKey>'::BIGINT)
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

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Lock the user

```SQL
SELECT
    u.id as user_id,
    u.username,
    u.email_address,
    u.display_name
FROM authen.m_user u
WHERE (u.username = '<sequence.usernameBytes>' OR u.email_address = '<sequence.usernameBytes>')
AND u.row_status = 'ACTIVE'
ORDER BY u.id
FOR UPDATE -- every authen API locks the user row first
```

### Table: [authen.m_user_password](../../../schema/authen/m_user_password.md)

#### QUERY - Get current password

```SQL
SELECT
    up.user_id,
    up.password AS password_hash,
    up.password_salt
FROM authen.m_user_password up
WHERE up.user_id = '<sequence.userId>'
AND up.row_type = 'PASSWORD'
AND up.row_status = 'ACTIVE'
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

### Table: [authen.l_user_login_attempt](../../../schema/authen/l_user_login_attempt.md)

#### INSERT - Record attempt

```SQL
INSERT INTO authen.l_user_login_attempt (
    created_by,
    created_at,
    identifier_hash,
    user_id,
    result
)
VALUES (
    'system',
    '<sequence.now>', -- UTC time captured after the identifier lock
    '<sequence.identifierHash>',
    '<sequence.userId>', -- NULL when the username is unknown, ambiguous or REFUSED
    '<sequence.result>' -- SUCCESS, FAILED or REFUSED
)
```
