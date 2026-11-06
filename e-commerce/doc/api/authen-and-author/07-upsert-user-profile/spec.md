# [POST]: v1/user/profile/upsert

| Title       | Description                                                                                                                                                                                                                               |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert User Profile API                                                                                                                                                                                                                   |
| Method      | POST                                                                                                                                                                                                                                      |
| Endpoint    | v{version}/user/profile/upsert                                                                                                                                                                                                            |
| Version     | 1                                                                                                                                                                                                                                         |
| Description | Update the profile of the logged-in user (name, display name, picture, phone number, address, date of birth, gender), The user comes from the access token, Fields that are not specified keep their value, null clears an optional field |

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
| 1   | content-type   | String    | MANDATORY | Content type of the request  | application/json                               |
| 2   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 3   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-06T09:00:00.123Z                       |
| 4   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Body Parameters

|     | Parameter Name     | Data Type | M/O      | Description                                                                                                                                     | Example                |
| --- | ------------------ | --------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| 1   | firstName          | String    | OPTIONAL | First name (max 100 characters), Plain text over TLS, Not specified keeps the current value, null clears it                                     | John                   |
| 2   | lastName           | String    | OPTIONAL | Last name (max 100 characters), Plain text over TLS, Not specified keeps the current value, null clears it                                      | Doe                    |
| 3   | displayName        | String    | OPTIONAL | Display name (max 128 characters), Plain text, Shown on shop members and product reviews, Not specified keeps the current value, null clears it | John Doe               |
| 4   | profilePicturePath | String    | OPTIONAL | Profile picture path, Not specified keeps the current value, null clears it                                                                     | /profiles/john-doe.png |
| 5   | phoneNumber        | String    | OPTIONAL | Phone number (8 to 15 digits, an optional leading +), Plain text over TLS, Not specified keeps the current value, null clears it                | 0812345678             |
| 6   | address            | String    | OPTIONAL | Address in the profile, Plain text over TLS, Not specified keeps the current value, null clears it                                              | 123 Sukhumvit Road     |
| 7   | dateOfBirth        | Date      | OPTIONAL | Date of birth (YYYY-MM-DD, not in the future), Not specified keeps the current value, null clears it                                            | 1990-01-31             |
| 8   | gender             | String    | OPTIONAL | Gender (MALE, FEMALE, OTHER), Not specified keeps the current value, null clears it                                                             | MALE                   |

### User Profile Rules

- The profile is the data of the caller: `userId` comes from the access token and is never read from the request. A user cannot read or change another user's profile. There is no batch and no delete (there is no API that deletes an account).
- Sensitive fields (`firstName`, `lastName`, `phoneNumber`, `address`) are sent as plain text over TLS and encrypted by the system before they are stored, with the same deterministic encryption as `01-register`. `displayName` stays plain text because shop member lists, order lists and product reviews read it.
- `username`, `emailAddress` and `password` cannot be changed here. Sending any of them is 400 (E10001). Changing them, and changing the password while logged in, is not part of this version.
- A field that is not specified keeps its current value. `null` clears a field. Insert is only the first write of the `authen.m_user_information` row when it does not exist (a user has one row, partial unique index `uq_m_user_information_user_id`), the answer is 200 in both cases.
- Validation (400, E10001): `displayName` at most 128 characters, `firstName` and `lastName` at most 100, `phoneNumber` 8 to 15 digits with an optional leading +, `dateOfBirth` a real date that is not in the future, `gender` one of MALE, FEMALE, OTHER.
- Lock order: lock the `authen.m_user` row of the caller first (`FOR UPDATE`), then write the `authen.m_user` and `authen.m_user_information` rows in one transaction.
- Execution order: validate the request (400) -> lock the user row -> update the user -> update or create the information row -> answer 200. There is no 403, 404 or 409.

#### Example Body Parameters

```JSON
{
    "firstName": "John",
    "lastName": "Doe",
    "displayName": "John Doe",
    "profilePicturePath": "/profiles/john-doe.png",
    "phoneNumber": "0812345678",
    "address": "123 Sukhumvit Road",
    "dateOfBirth": "1990-01-31",
    "gender": "MALE"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/user/profile/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "firstName": "John",
    "lastName": "Doe",
    "displayName": "John Doe",
    "profilePicturePath": "/profiles/john-doe.png",
    "phoneNumber": "0812345678",
    "address": "123 Sukhumvit Road",
    "dateOfBirth": "1990-01-31",
    "gender": "MALE"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/user/profile/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "firstName": "John",
    "lastName": "Doe",
    "displayName": "John Doe",
    "profilePicturePath": "/profiles/john-doe.png",
    "phoneNumber": "0812345678",
    "address": "123 Sukhumvit Road",
    "dateOfBirth": "1990-01-31",
    "gender": "MALE"
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

|     | Parameter Name | Data Type    | M/O       | Source           | Field       | Description                                         | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ----------- | --------------------------------------------------- | ------------------------------------ |
| 1   | userId         | String: UUID | MANDATORY | Sequence Diagram | data.userId | Id of the user whose profile was saved (the caller) | b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Upsert User Profile Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e"
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
        "bizMessage": "Date of birth must be a date in the past (YYYY-MM-DD).",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:40:40.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Fixed Field

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Username, Email Address and Password cannot be changed here.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
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

#### QUERY - Lock the user

```SQL
SELECT
    u.id as user_id
FROM authen.m_user u
WHERE u.id = '<sequence.userId>'
AND u.row_status = 'ACTIVE'
FOR UPDATE -- every authen API locks the user row first
```

#### UPDATE - Update user

```SQL
UPDATE authen.m_user
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    first_name = '<sequence.firstNameBytes>', -- only when firstName is specified (null clears it)
    last_name = '<sequence.lastNameBytes>', -- only when lastName is specified (null clears it)
    display_name = '<sequence.displayName>', -- only when displayName is specified (null clears it)
    profile_picture_path = '<sequence.profilePicturePath>' -- only when profilePicturePath is specified (null clears it)
WHERE id = '<sequence.userId>'
RETURNING id as user_id
```

### Table: [authen.m_user_information](../../../schema/authen/m_user_information.md)

#### QUERY - Check existing information

```SQL
SELECT
    ui.id as information_id
FROM authen.m_user_information ui
WHERE ui.user_id = '<sequence.userId>'
AND ui.row_status <> 'DELETED'
```

#### INSERT - Create information

```SQL
INSERT INTO authen.m_user_information (
    created_by,
    user_id,
    phone_number,
    address,
    date_of_birth,
    gender
)
VALUES (
    '<sequence.userId>',
    '<sequence.userId>',
    '<sequence.phoneNumberBytes>',
    '<sequence.addressBytes>',
    '<sequence.dateOfBirth>',
    '<sequence.gender>'
)
```

#### UPDATE - Update information

```SQL
UPDATE authen.m_user_information
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    phone_number = '<sequence.phoneNumberBytes>', -- only when phoneNumber is specified (null clears it)
    address = '<sequence.addressBytes>', -- only when address is specified (null clears it)
    date_of_birth = '<sequence.dateOfBirth>', -- only when dateOfBirth is specified (null clears it)
    gender = '<sequence.gender>' -- only when gender is specified (null clears it)
WHERE id = '<sequence.informationId>'
```
