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

- Governing decisions: owner-confirmed API review Q13, Q15 (approved by the product owner).
- Public API: no `authorization` header.
- **The answer is always 200 with the same message** (`If the email address is registered, a reset link has been sent.`) for valid business outcomes: unknown email, non-ACTIVE user, frequency refusal, or committed reset issuance.
- Before the lookup, perform the same encryption and cryptographic preparation for every syntactically valid request: generate a cryptographically random 32-byte token, encode it as unpadded base64url, hash the exact encoded token with ...
- A reset token is created only for an ACTIVE user.
- Throttle: a user can ask at most 3 times per hour (configurable), measured by successful reset issuance rows created in the rolling window, whatever their status.
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

|     | Parameter Name | Data Type | M/O       | Description                                                                                                          | Example              |
| --- | -------------- | --------- | --------- | -------------------------------------------------------------------------------------------------------------------- | -------------------- |
| 1   | emailAddress   | String    | MANDATORY | Email address of the account, Plain text over TLS, The system encrypts it before it is compared (max 254 characters) | john.doe@example.com |

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
