---
name: Create New Password API Specification
description: Defines public reset-token verification, user-first serialization, post-lock single-use consumption, password history and atomic all-session revocation for POST v1/auth/create-new-password.
status: in-review
approved_by: null
approved_at: null
---

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

- Governing decisions: owner-confirmed API review Q13 (approved by the product owner).
- Public API: no `authorization` header.
- The new password follows the password policy: 8 to 128 characters with an upper-case letter, a lower-case letter and a digit (400, E10001).
- **A reset token that does not exist, is INACTIVE (used or replaced), has expired, or belongs to a user that is not ACTIVE gets one answer: 400 (E10001) `Reset token is invalid or expired.`** Do not disclose which case occurred.
- The lookup is only a routing hint.
- The new password must differ from the current one (400, E10001).
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

|     | Parameter Name | Data Type | M/O       | Description                                                                                                                                           | Example                                        |
| --- | -------------- | --------- | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| 1   | resetToken     | String    | MANDATORY | Reset token from the link of the reset email                                                                                                          | k9Vf2Tq8Lm5Zx1Rc7Ya3Pw6Jd0Hs4Gn2Bv8Cx5Mq1Ae... |
| 2   | newPassword    | String    | MANDATORY | New password, Plain text over TLS (8 to 128 characters, an upper-case letter, a lower-case letter and a digit), Must differ from the current password | NewSecret1x                                    |

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

#### Fail - Internal Server Error

```JSON
{
    "status": {
        "code": 500,
        "message": "Internal Server Error",
        "bizMessage": "An unexpected error occurred.",
        "requestId": "req-reset-review",
        "timestamp": "2026-11-07T12:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

Statements are listed in execution order. Only the routing lookup is autocommit; all remaining SQL shares the user transaction lock. lookupNow precedes lookup; now is freshly captured after the lock. Returned counts/ids must be checked in Application.

### Table: [authen.t_user_reset_password](../../../schema/authen/t_user_reset_password.md)

#### QUERY - Find the reset token

```SQL
SELECT
    rp.id as reset_id,
    rp.user_id
FROM authen.t_user_reset_password rp
WHERE rp.reset_token = '<sequence.resetTokenHash>' -- SHA-256 of resetToken
AND rp.row_status = 'ACTIVE'
AND rp.expired_at > '<sequence.lookupNow>'
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

### Table: [authen.t_user_reset_password](../../../schema/authen/t_user_reset_password.md)

#### UPDATE - Use the reset token once

```SQL
UPDATE authen.t_user_reset_password
SET
    updated_by = '<sequence.userId>',
    updated_at = '<sequence.now>',
    row_status = 'INACTIVE'
WHERE id = '<sequence.resetId>'
AND user_id = '<sequence.userId>'
AND reset_token = '<sequence.resetTokenHash>'
AND row_status = 'ACTIVE'
AND expired_at > '<sequence.now>'
RETURNING id as reset_id -- no row means the answer is 400
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

### Table: [authen.m_user_password](../../../schema/authen/m_user_password.md)

#### UPDATE - Make the current password INACTIVE

```SQL
UPDATE authen.m_user_password
SET
    updated_by = '<sequence.userId>',
    updated_at = '<sequence.now>',
    row_status = 'INACTIVE'
WHERE id = '<sequence.passwordId>'
AND user_id = '<sequence.userId>'
AND row_type = 'PASSWORD'
AND row_status = 'ACTIVE'
RETURNING id as password_id
```

### Table: [authen.m_user_password](../../../schema/authen/m_user_password.md)

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
    updated_at = '<sequence.now>',
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
    updated_at = '<sequence.now>',
    row_status = 'INACTIVE'
WHERE user_id = '<sequence.userId>'
AND row_status = 'ACTIVE'
```
