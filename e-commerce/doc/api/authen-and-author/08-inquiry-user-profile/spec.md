---
name: Own User Profile Inquiry API Specification
description: Defines current token and ACTIVE user gating, consistent read-only profile snapshots, exact nullable field mapping and complete outcomes for GET v1/user/profile.
status: in-review
approved_by: null
approved_at: null
---

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

- Governing decisions: owner-confirmed API review Q13, Q15 (approved by the product owner).
- The profile is the data of the caller: userId comes only from verified JWT sub.
- Verify Bearer JWT signature/issuer/audience/expiry/UUID sub before BEGIN.
- BEGIN REPEATABLE READ READ ONLY, capture fresh server UTC now immediately before the first query and recheck JWT expiry.
- Read user and information from the same repeatable-read snapshot, so a concurrent atomic profile writer cannot mix the old name with new phone/address.
- Query information only after the joined user/credential result succeeds.
- The order of the checks, the locks and every outcome is in the sequence diagram.

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
| 3   | firstName          | String       | MANDATORY | Sequence Diagram | data.firstName          | First name, null when not set                   | John                                 |
| 4   | lastName           | String       | MANDATORY | Sequence Diagram | data.lastName           | Last name, null when not set                    | Doe                                  |
| 5   | displayName        | String       | MANDATORY | Sequence Diagram | data.displayName        | Display name, null when not set                 | John Doe                             |
| 6   | profilePicturePath | String       | MANDATORY | Sequence Diagram | data.profilePicturePath | Profile picture path, null when not set         | /profiles/john-doe.png               |
| 7   | phoneNumber        | String       | MANDATORY | Sequence Diagram | data.phoneNumber        | Phone number, null when not set                 | 0812345678                           |
| 8   | address            | String       | MANDATORY | Sequence Diagram | data.address            | Address in the profile, null when not set       | 123 Sukhumvit Road                   |
| 9   | dateOfBirth        | Date         | MANDATORY | Sequence Diagram | data.dateOfBirth        | Date of birth (YYYY-MM-DD), null when not set   | 1990-01-31                           |
| 10  | gender             | String       | MANDATORY | Sequence Diagram | data.gender             | Gender (MALE, FEMALE, OTHER), null when not set | MALE                                 |

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

#### Success - No Information

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
        "phoneNumber": null,
        "address": null,
        "dateOfBirth": null,
        "gender": null
    }
}
```

#### Success - Unset Gender

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
        "gender": null
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
        "bizMessage": "Timestamp must be valid UTC and this endpoint accepts no query parameters or body.",
        "requestId": "req-profile-inquiry-review",
        "timestamp": "2026-11-08T00:00:00.123Z",
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
        "requestId": "req-profile-inquiry-review",
        "timestamp": "2026-11-08T00:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

The first query joins [authen.t_user_access_token](../../../schema/authen/t_user_access_token.md) with the caller profile; both queries share one read-only repeatable-read snapshot. now is captured immediately before the joined credential/user projection, with JWT expiry rechecked. No SQL writes or locks run.

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
JOIN authen.t_user_access_token at ON at.user_id = u.id
WHERE u.id = '<sequence.userId>'
AND u.row_status = 'ACTIVE'
AND at.token = '<sequence.accessTokenHash>'
AND at.user_id = '<sequence.userId>'
AND at.row_status = 'ACTIVE'
AND at.expired_at > '<sequence.now>'
```

### Table: [authen.m_user_information](../../../schema/authen/m_user_information.md)

#### QUERY - Get information

```SQL
SELECT
    ui.phone_number,
    ui.address,
    ui.date_of_birth,
    NULLIF(ui.gender, '') as gender
FROM authen.m_user_information ui
WHERE ui.user_id = '<sequence.userId>'
AND ui.row_status <> 'DELETED'
```
