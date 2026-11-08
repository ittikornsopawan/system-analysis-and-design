---
name: Reset Password Request API Specification
description: Defines public uniform reset-request outcomes, user-first serialized issuance, fresh rolling-hour throttle and timestamps, atomic reset replacement and post-commit email handoff for POST v1/auth/reset-password.
status: in-review
approved_by: null
approved_at: null
---

# [POST]: v1/auth/reset-password

| Title       | Description                                                                                                                                                                                                                                           |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Reset Password API                                                                                                                                                                                                                                    |
| Method      | POST                                                                                                                                                                                                                                                  |
| Endpoint    | v{version}/auth/reset-password                                                                                                                                                                                                                        |
| Version     | 1                                                                                                                                                                                                                                                     |
| Description | Request a password reset, The answer is always the same whether or not the email address is registered, A reset link with a single use token that expires in 30 minutes is sent to a registered and ACTIVE user, At most 3 requests per user per hour |

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

|     | Parameter Name | Data Type | M/O       | Description                                                                                                          | Example              |
| --- | -------------- | --------- | --------- | -------------------------------------------------------------------------------------------------------------------- | -------------------- |
| 1   | emailAddress   | String    | MANDATORY | Email address of the account, Plain text over TLS, The system encrypts it before it is compared (max 254 characters) | john.doe@example.com |

### Reset Password Rules

- Governing behavior: WP4 U11/U12/U23 and [owner-confirmed review](../../../../../docs/superpowers/specs/2026-11-07-api-review-design.md), Q13 credential behavior and Q15 delivery, approved by the product owner. This endpoint revision remains in-review. No backend/email transport, outbox or schema implementation is included.
- Public API: no `authorization` header. Validate mandatory timestamp as UTC and emailAddress as a non-empty, syntactically valid string of at most 254 characters before SQL (400 E10001). Generate requestId if omitted. Accept plaintext only over TLS; Application applies the same deterministic encryption/representation as register/login to produce emailAddressBytes. Do not trim, lowercase or normalize it differently from those APIs. All SQL parameters are typed bound bytes/UUIDs/UTC timestamps; never interpolate input into SQL.
- **The answer is always 200 with the same message** (`If the email address is registered, a reset link has been sent.`) for valid business outcomes: unknown email, non-ACTIVE user, frequency refusal, or committed reset issuance. Same status-only envelope, no data/token/userId/count/refusal reason. No 401, 403, 404, 409 or 429 is added. Operational lookup/transaction timeout is 408 E90001; unexpected failure is generic 500 without bizCode, revealing no account detail. The generic success message does not certify email delivery.
- Before the lookup, perform the same encryption and cryptographic preparation for every syntactically valid request: generate a cryptographically random 32-byte token, encode it as unpadded base64url, hash the exact encoded token with SHA-256 (32 bytes) as resetTokenHash. The database stores only the hash; never log/return the raw token, hash or email plaintext. Discard the unused in-memory secret when no row will be created. Apply the same configured response-latency policy to every 200 business outcome; do not deliberately return sooner for unknown/inactive/throttled accounts. Actual timing privacy needs runtime verification and is not proved by document checks.
- A reset token is created only for an ACTIVE user. Only the registered address matching the encrypted lookup/locked row may receive the link; never accept a target userId or alternate recipient/redirect URL from the request. Build the link from the configured trusted reset-page URL plus the raw token. Sending is outside this spec; the handoff occurs only after the new row COMMIT succeeds. Do not send after rollback, for unknown/inactive users or when throttled. Email transport/retries/durable delivery are not defined or claimed here, as in WP4 U11; their outcome does not expose account existence through this HTTP response.
- Lock order: validate -> prepare encrypted email/token/hash -> autocommit ACTIVE user lookup -> BEGIN READ COMMITTED -> lock the same user FOR UPDATE, rechecking ACTIVE status and email equality -> capture fresh server UTC now after the lock -> count history -> replace ACTIVE reset -> insert -> COMMIT -> post-commit email handoff -> generic 200. Derive userId only from the lookup. A lookup that finds no ACTIVE user returns generic 200 without BEGIN/writes. A user that becomes ineligible before the lock returns the same 200 after closing the read-only transaction, without counting/writing/sending.
- Throttle: a user can ask at most 3 times per hour (configurable), measured by successful reset issuance rows created in the rolling window, whatever their status. Count rows with created_at > windowStart, where windowStart = post-lock now minus 1 hour; equality is outside the window. Consumed/replaced/expired/history rows still count; refused attempts create no row and do not extend the window. Under the user lock, requests >= 3 commits no reset change and sends nothing; requests < 3 may issue once. Concurrent requests must reread the count after acquiring the common user lock.
- Use the same fresh post-lock clock for updated_at, explicit created_at, windowStart and expiredAt = now plus 30 minutes (configurable). Do not rely on transaction-start NOW() or default created_at after a lock wait: a just-issued row must be counted as new. The 30-minute lifetime begins when issued under the lock; it is never derived from the untrusted request timestamp. The database session and bound timestamp values use UTC.
- A user has at most one ACTIVE reset row (partial unique index `uq_t_user_reset_password_user_id_active`). Make all earlier ACTIVE reset rows of that user INACTIVE, then INSERT exactly one fresh row, in one transaction; zero old rows is valid. Preserve prior non-ACTIVE history and every other user. Check the returned new reset_id/count before success; unexpected INSERT failure/constraint failure rolls back the earlier closure and returns generic 500, never a new 409. Do not change password, access/refresh tokens, consent or authorization assignments when merely requesting a reset.
- The common user lock serializes concurrent issuances and create-new-password. Each permitted issuance replaces its predecessor; only the newest remains usable and every issued row counts towards the limit, even if email delivery order differs. If password completion wins first, it consumes its reset before this later request issues a fresh link; if a new issuance wins first, the waiting completion's guarded old-token consumption fails. Do not extend expiry or reactivate a replaced/used row.
- The replacement transaction must COMMIT before email handoff and success. On pre-commit timeout ROLLBACK then 408 E90001; on other pre-commit failure ROLLBACK then generic 500. Pre-BEGIN lookup failures have no transaction to roll back. A lost response after commit does not undo or reuse the new token: a retry is a new issuance request subject to the same throttle. No post-commit email failure may roll back a committed row or turn the generic business outcome into an account-specific response.
- Execution order: validate input -> deterministic encryption and random token/hash -> routing lookup -> BEGIN -> locked ACTIVE user/email recheck -> fresh now/windowStart/expiredAt -> current history count -> throttle branch -> close old ACTIVE reset -> insert new reset with created_at = now -> COMMIT -> email handoff -> generic 200. Each SQL result returns to Application before branching or deriving userId/resetId.

#### Scenario correspondence with sequence.wsd

| Scenario                                  | Sequence behavior                                         | HTTP             | Durable effects                         |
| ----------------------------------------- | --------------------------------------------------------- | ---------------- | --------------------------------------- |
| Invalid timestamp/email                   | No SQL or BEGIN                                           | 400 E10001       | None                                    |
| Lookup timeout / unexpected failure       | No transaction rollback needed                            | 408 E90001 / 500 | None                                    |
| Unknown email / no ACTIVE user            | Generic response, no BEGIN                                | 200 S10000       | No row/email                            |
| User/email becomes ineligible during wait | Locked recheck fails, end read-only transaction           | 200 S10000       | No row/email                            |
| requests >= 3                             | Fresh post-lock count, no write, COMMIT                   | 200 S10000       | No row/email                            |
| requests < 3                              | Close old ACTIVE, insert exactly one, COMMIT before email | 200 S10000       | One new ACTIVE reset; history preserved |
| Concurrent requests                       | Each waits, rereads count, replaces only if below limit   | 200 S10000       | No fourth issuance inside window        |
| Unexpected zero insert result             | ROLLBACK before common success                            | 500              | Old reset remains usable                |
| Pre-commit timeout / other failure        | ROLLBACK both replacement steps                           | 408 E90001 / 500 | None                                    |

#### Example Body Parameters

```JSON
{
    "emailAddress": "john.doe@example.com"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/auth/reset-password HTTP/1.1
Host: www.domain.com
content-type: application/json
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "emailAddress": "john.doe@example.com"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/auth/reset-password' \
--header 'content-type: application/json' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "emailAddress": "john.doe@example.com"
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

No `data`. Only the status object is returned.

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "If the email address is registered, a reset link has been sent.",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
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
        "bizMessage": "Email Address is required and must be a valid email address.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:40:40.123Z",
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
        "requestId": "req-reset-request-review",
        "timestamp": "2026-11-08T00:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

Statements follow execution order. Only the first lookup is autocommit; all remaining SQL uses one READ COMMITTED transaction and the common user lock. The lock rechecks encrypted email ownership. All now/window/expiry values are freshly derived after the lock.

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Find the active user by email address

```SQL
SELECT
    u.id as user_id
FROM authen.m_user u
WHERE u.email_address = '<sequence.emailAddressBytes>'
AND u.row_status = 'ACTIVE'
```

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Lock the user

```SQL
SELECT
    u.id as user_id
FROM authen.m_user u
WHERE u.id = '<sequence.userId>'
AND u.row_status = 'ACTIVE'
AND u.email_address = '<sequence.emailAddressBytes>'
FOR UPDATE -- every authen API locks the user row first
```

### Table: [authen.t_user_reset_password](../../../schema/authen/t_user_reset_password.md)

#### QUERY - Count the requests of the last hour

```SQL
SELECT
    COUNT(rp.id) as requests
FROM authen.t_user_reset_password rp
WHERE rp.user_id = '<sequence.userId>'
AND rp.created_at > '<sequence.windowStart>' -- now minus 1 hour (configurable)
```

### Table: [authen.t_user_reset_password](../../../schema/authen/t_user_reset_password.md)

#### UPDATE - Make the old reset token INACTIVE

```SQL
UPDATE authen.t_user_reset_password
SET
    updated_by = '<sequence.userId>',
    updated_at = '<sequence.now>',
    row_status = 'INACTIVE'
WHERE user_id = '<sequence.userId>'
AND row_status = 'ACTIVE'
```

### Table: [authen.t_user_reset_password](../../../schema/authen/t_user_reset_password.md)

#### INSERT - Create reset token

```SQL
INSERT INTO authen.t_user_reset_password (
    created_by,
    created_at,
    user_id,
    reset_token,
    expired_at
)
VALUES (
    '<sequence.userId>',
    '<sequence.now>',
    '<sequence.userId>',
    '<sequence.resetTokenHash>', -- SHA-256 of the token that is sent by email
    '<sequence.expiredAt>' -- now plus 30 minutes (configurable)
)
RETURNING id as reset_id
```
