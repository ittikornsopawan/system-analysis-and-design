# [POST]: v1/auth/login

| Title       | Description                                                                                                                        |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Login API                                                                                                                          |
| Method      | POST                                                                                                                               |
| Endpoint    | v{version}/auth/login                                                                                                              |
| Version     | 1                                                                                                                                  |
| Description | Authenticate a user by username (mobile no, email address or username) and password, and issue an access token and a refresh token |

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

|     | Parameter Name | Data Type | M/O       | Description                                                                                         | Example                  |
| --- | -------------- | --------- | --------- | --------------------------------------------------------------------------------------------------- | ------------------------ |
| 1   | username       | String    | MANDATORY | Encrypted username in AES256 Key and IV frontend side, It can be mobile no, email address, username | kQ3v8Zx1pL0mN7aR2tYw5g== |
| 2   | password       | String    | MANDATORY | Encrypted password in AES256 Key and IV frontend side                                               | Zr9TqL2vXw8mK5nB1cJd4A== |

#### Example Body Parameters

```JSON
{
    "username": "kQ3v8Zx1pL0mN7aR2tYw5g==",
    "password": "Zr9TqL2vXw8mK5nB1cJd4A=="
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
    "username": "kQ3v8Zx1pL0mN7aR2tYw5g==",
    "password": "Zr9TqL2vXw8mK5nB1cJd4A=="
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/auth/login' \
--header 'content-type: application/json' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "username": "kQ3v8Zx1pL0mN7aR2tYw5g==",
    "password": "Zr9TqL2vXw8mK5nB1cJd4A=="
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

|     | Parameter Name     | Data Type | M/O       | Source           | Field                   | Description                                       | Example                                 |
| --- | ------------------ | --------- | --------- | ---------------- | ----------------------- | ------------------------------------------------- | --------------------------------------- |
| 1   | tokenType          | String    | MANDATORY | Sequence Diagram | data.tokenType          | Access Token Type                                 | Bearer                                  |
| 2   | accessToken        | String    | MANDATORY | Sequence Diagram | data.accessToken        | Access Token                                      | eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 3   | refreshAccessToken | String    | MANDATORY | Sequence Diagram | data.refreshAccessToken | Refresh Token Expiring from expiresIn 7 day after | rF3g7Hk9LpQ1m...                        |
| 4   | expiresIn          | Numeric   | MANDATORY | Sequence Diagram | data.expiresIn          | Access Token Expiring in Second                   | 3600                                    |

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
        "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
        "refreshAccessToken": "rF3g7Hk9LpQ1m8vNxZpQ2w5rT8yU0i1oP3qR5sT7uV9wXyZ",
        "expiresIn": 3600
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
