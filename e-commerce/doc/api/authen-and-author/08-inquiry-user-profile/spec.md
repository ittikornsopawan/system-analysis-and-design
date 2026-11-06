# [GET]: v1/user/profile

| Title       | Description                                                                                                                  |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry User Profile API                                                                                                     |
| Method      | GET                                                                                                                          |
| Endpoint    | v{version}/user/profile                                                                                                      |
| Version     | 1                                                                                                                            |
| Description | Inquiry the profile of the logged-in user, The user comes from the access token, Sensitive fields are returned as plain text |

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

|     | Parameter Name | Data Type | M/O       | Description                  | Example                                        |
| --- | -------------- | --------- | --------- | ---------------------------- | ---------------------------------------------- |
| 1   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-06T09:00:00.123Z                       |
| 3   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Query Parameters

No query parameters. The profile is the one of the caller.

### User Profile Inquiry Rules

- The profile is the data of the caller: `userId` comes from the access token. There is no `id` parameter and nobody can read another user's profile with this API.
- Sensitive fields (`emailAddress`, `firstName`, `lastName`, `phoneNumber`, `address`) are decrypted by the system and returned as plain text over TLS. `username` and the password are never returned.
- A field that was never set is `null` (all keys are always present). A user without an information row gets `null` for `phoneNumber`, `address`, `dateOfBirth` and `gender`.

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/user/profile HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/user/profile' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d'
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

|     | Parameter Name     | Data Type    | M/O       | Source           | Field                   | Description                                     | Example                              |
| --- | ------------------ | ------------ | --------- | ---------------- | ----------------------- | ----------------------------------------------- | ------------------------------------ |
| 1   | userId             | String: UUID | MANDATORY | Sequence Diagram | data.userId             | User Id (the caller)                            | b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e |
| 2   | emailAddress       | String       | MANDATORY | Sequence Diagram | data.emailAddress       | Email address (read only)                       | john.doe@example.com                 |
| 3   | firstName          | String       | OPTIONAL  | Sequence Diagram | data.firstName          | First name, null when not set                   | John                                 |
| 4   | lastName           | String       | OPTIONAL  | Sequence Diagram | data.lastName           | Last name, null when not set                    | Doe                                  |
| 5   | displayName        | String       | OPTIONAL  | Sequence Diagram | data.displayName        | Display name, null when not set                 | John Doe                             |
| 6   | profilePicturePath | String       | OPTIONAL  | Sequence Diagram | data.profilePicturePath | Profile picture path, null when not set         | /profiles/john-doe.png               |
| 7   | phoneNumber        | String       | OPTIONAL  | Sequence Diagram | data.phoneNumber        | Phone number, null when not set                 | 0812345678                           |
| 8   | address            | String       | OPTIONAL  | Sequence Diagram | data.address            | Address in the profile, null when not set       | 123 Sukhumvit Road                   |
| 9   | dateOfBirth        | Date         | OPTIONAL  | Sequence Diagram | data.dateOfBirth        | Date of birth (YYYY-MM-DD), null when not set   | 1990-01-31                           |
| 10  | gender             | String       | OPTIONAL  | Sequence Diagram | data.gender             | Gender (MALE, FEMALE, OTHER), null when not set | MALE                                 |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry User Profile Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
        "emailAddress": "john.doe@example.com",
        "firstName": "John",
        "lastName": "Doe",
        "displayName": "John Doe",
        "profilePicturePath": "/profiles/john-doe.png",
        "phoneNumber": "0812345678",
        "address": "123 Sukhumvit Road",
        "dateOfBirth": "1990-01-31",
        "gender": "MALE"
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
        "bizMessage": "Invalid or expired access token.",
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

---

## Database Relations

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Get user

```SQL
SELECT
    u.id as user_id,
    u.email_address,
    u.first_name,
    u.last_name,
    u.display_name,
    u.profile_picture_path
FROM authen.m_user u
WHERE u.id = '<sequence.userId>'
AND u.row_status = 'ACTIVE'
```

### Table: [authen.m_user_information](../../../schema/authen/m_user_information.md)

#### QUERY - Get information

```SQL
SELECT
    ui.phone_number,
    ui.address,
    ui.date_of_birth,
    ui.gender
FROM authen.m_user_information ui
WHERE ui.user_id = '<sequence.userId>'
AND ui.row_status <> 'DELETED'
```
