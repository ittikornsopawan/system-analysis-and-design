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

- Public API: no `authorization` header. The caller proves nothing, so the answer never depends on the account.
- **The answer is always 200 with the same message** (`If the email address is registered, a reset link has been sent.`) when the request is valid: the email address does not exist, the user is not ACTIVE, the user asked too often, or the reset token was created. The response time should not depend on the case either (do the same work and send the email after the transaction).
- A reset token is created only for an ACTIVE user. It is 32 random bytes (base64url), only its SHA-256 is stored in `reset_token`, and it expires 30 minutes after the request (`expired_at`, configurable). The token is sent in the link of an email to the registered address (sending is outside this spec).
- A user has at most one ACTIVE reset row. A new request makes the earlier ACTIVE row INACTIVE before it inserts the new one (partial unique index `uq_t_user_reset_password_user_id_active`).
- Throttle: a user can ask at most 3 times per hour (configurable), counted from the rows of `authen.t_user_reset_password` created in the last hour, whatever their status. Over the limit the answer is the same 200 and nothing is created or sent.
- Lock order: lock the `authen.m_user` row of the user first (`FOR UPDATE`), then read and write the reset rows.
- Execution order: validate the request (400) -> find the ACTIVE user by the encrypted email address -> lock the user row -> count the requests of the last hour -> make the old ACTIVE row INACTIVE -> insert the new row -> answer 200. No 401, 403, 404 or 409 exists in this API.

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

---

## Database Relations

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Find the active user by email address

```SQL
SELECT
    u.id as user_id
FROM authen.m_user u
WHERE u.email_address = '<sequence.emailAddressBytes>'
AND u.row_status = 'ACTIVE'
```

#### QUERY - Lock the user

```SQL
SELECT
    u.id as user_id
FROM authen.m_user u
WHERE u.id = '<sequence.userId>'
AND u.row_status = 'ACTIVE'
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

#### UPDATE - Make the old reset token INACTIVE

```SQL
UPDATE authen.t_user_reset_password
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'INACTIVE'
WHERE user_id = '<sequence.userId>'
AND row_status = 'ACTIVE'
```

#### INSERT - Create reset token

```SQL
INSERT INTO authen.t_user_reset_password (
    created_by,
    user_id,
    reset_token,
    expired_at
)
VALUES (
    '<sequence.userId>',
    '<sequence.userId>',
    '<sequence.resetTokenHash>', -- SHA-256 of the token that is sent by email
    '<sequence.expiredAt>' -- now plus 30 minutes (configurable)
)
```
