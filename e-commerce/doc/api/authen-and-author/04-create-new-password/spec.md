# [POST]: v1/auth/create-new-password

| Title       | Description                                                                                                                                                                                                                      |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Create New Password API                                                                                                                                                                                                          |
| Method      | POST                                                                                                                                                                                                                             |
| Endpoint    | v{version}/auth/create-new-password                                                                                                                                                                                              |
| Version     | 1                                                                                                                                                                                                                                |
| Description | Set a new password with the reset token from the reset email, The reset token can be used once and expires 30 minutes after the request, All access tokens and refresh tokens of the user are closed, The user must log in again |

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

|     | Parameter Name | Data Type | M/O       | Description                                                                                                                                           | Example                                        |
| --- | -------------- | --------- | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| 1   | resetToken     | String    | MANDATORY | Reset token from the link of the reset email                                                                                                          | k9Vf2Tq8Lm5Zx1Rc7Ya3Pw6Jd0Hs4Gn2Bv8Cx5Mq1Ae... |
| 2   | newPassword    | String    | MANDATORY | New password, Plain text over TLS (8 to 128 characters, an upper-case letter, a lower-case letter and a digit), Must differ from the current password | NewSecret1x                                    |

### Create New Password Rules

- Public API: no `authorization` header. The reset token is the proof. Only the SHA-256 of the token is compared with `reset_token`.
- The new password follows the password policy: 8 to 128 characters with an upper-case letter, a lower-case letter and a digit (400, E10001). The values are configurable.
- **A reset token that does not exist, is INACTIVE (used or replaced), has expired, or belongs to a user that is not ACTIVE gets one answer: 400 (E10001) `Reset token is invalid or expired.`** The answer does not say which case it is.
- The reset token is used once: the row is made INACTIVE by `UPDATE ... WHERE id = <id> AND row_status = 'ACTIVE' AND expired_at > <now> RETURNING id`. When the update returns no row (a second request used it first, or it expired meanwhile) the answer is the same 400 and nothing changes.
- The new password must differ from the current one (400, E10001). The check hashes the new password with the salt of the current password row. A rejected request changes nothing, the reset token stays usable until it expires.
- Password storage: PBKDF2-HMAC-SHA256 with a random 16 byte salt and 600,000 iterations, compared in constant time. The current PASSWORD row becomes INACTIVE (kept as history) and a new ACTIVE PASSWORD row is inserted (partial unique index `uq_m_user_password_user_id_password`).
- All ACTIVE access tokens and refresh tokens of the user (every session) become INACTIVE in the same transaction. The API does not log the user in, the user calls login with the new password.
- Lock order: look up the reset row, lock the `authen.m_user` row of its user (`FOR UPDATE`), then use the reset row, change the password and close the tokens, all in one transaction.
- Execution order: validate the request and the password policy (400) -> find the reset row (400 when none) -> lock the user row -> use the reset row (400 when it returns nothing) -> check the new password differs (400) -> change the password -> close the tokens -> answer 200.

#### Example Body Parameters

```JSON
{
    "resetToken": "k9Vf2Tq8Lm5Zx1Rc7Ya3Pw6Jd0Hs4Gn2Bv8Cx5Mq1Ae...",
    "newPassword": "NewSecret1x"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/auth/create-new-password HTTP/1.1
Host: www.domain.com
content-type: application/json
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "resetToken": "k9Vf2Tq8Lm5Zx1Rc7Ya3Pw6Jd0Hs4Gn2Bv8Cx5Mq1Ae...",
    "newPassword": "NewSecret1x"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/auth/create-new-password' \
--header 'content-type: application/json' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "resetToken": "k9Vf2Tq8Lm5Zx1Rc7Ya3Pw6Jd0Hs4Gn2Bv8Cx5Mq1Ae...",
    "newPassword": "NewSecret1x"
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
        "bizMessage": "Create New Password Success",
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
        "bizMessage": "Reset Token and New Password are required fields.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:40:40.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Password Policy

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Password must be 8 to 128 characters and contain an upper-case letter, a lower-case letter and a digit.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Reset Token

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Reset token is invalid or expired.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:42:54.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Same Password

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "New password must be different from the current password.",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:43:01.123Z",
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

### Table: [authen.t_user_reset_password](../../../schema/authen/t_user_reset_password.md)

#### QUERY - Find the reset token

```SQL
SELECT
    rp.id as reset_id,
    rp.user_id
FROM authen.t_user_reset_password rp
WHERE rp.reset_token = '<sequence.resetTokenHash>' -- SHA-256 of resetToken
AND rp.row_status = 'ACTIVE'
AND rp.expired_at > NOW() AT TIME ZONE 'UTC'
```

#### UPDATE - Use the reset token once

```SQL
UPDATE authen.t_user_reset_password
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'INACTIVE'
WHERE id = '<sequence.resetId>'
AND row_status = 'ACTIVE'
AND expired_at > NOW() AT TIME ZONE 'UTC'
RETURNING id as reset_id -- no row means the answer is 400
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

### Table: [authen.m_user_password](../../../schema/authen/m_user_password.md)

#### QUERY - Get current password

```SQL
SELECT
    up.id as password_id,
    up.password,
    up.password_salt
FROM authen.m_user_password up
WHERE up.user_id = '<sequence.userId>'
AND up.row_type = 'PASSWORD'
AND up.row_status = 'ACTIVE'
```

#### UPDATE - Make the current password INACTIVE

```SQL
UPDATE authen.m_user_password
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'INACTIVE'
WHERE id = '<sequence.passwordId>'
```

#### INSERT - Create password

```SQL
INSERT INTO authen.m_user_password (
    created_by,
    row_type,
    user_id,
    password,
    password_salt
)
VALUES (
    '<sequence.userId>',
    'PASSWORD',
    '<sequence.userId>',
    '<sequence.passwordBytes>', -- PBKDF2-HMAC-SHA256, 600,000 iterations
    '<sequence.passwordSaltBytes>'
)
```

### Table: [authen.t_user_access_token](../../../schema/authen/t_user_access_token.md)

#### UPDATE - Close the access tokens of the user

```SQL
UPDATE authen.t_user_access_token
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'INACTIVE'
WHERE user_id = '<sequence.userId>'
AND row_status = 'ACTIVE'
```

### Table: [authen.t_user_refresh_token](../../../schema/authen/t_user_refresh_token.md)

#### UPDATE - Close the refresh tokens of the user

```SQL
UPDATE authen.t_user_refresh_token
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'INACTIVE'
WHERE user_id = '<sequence.userId>'
AND row_status = 'ACTIVE'
```
