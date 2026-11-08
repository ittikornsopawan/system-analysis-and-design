---
name: Own User Profile Upsert API Specification
description: Defines user-first current credential verification, own-user partial profile writes, explicit presence/null mapping, separate information insert/update and atomic outcomes for POST v1/user/profile/upsert.
status: in-review
approved_by: null
approved_at: null
---

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

- Governing behavior: WP4 U18/U23 and [owner-confirmed review](../../../../../docs/superpowers/specs/2026-11-07-api-review-design.md), Q13 current credential revocation and Q15 delivery, approved by the product owner. This endpoint revision remains in-review; no backend/schema implementation is included.
- The profile is the data of the caller: userId comes only from verified JWT sub and is never read from the request. No role/administrator permission is required to edit one's own profile. Reject request userId/id, unknown body keys and fixed fields username/emailAddress/password, even when null, with 400 E10001. Username, Email Address and Password cannot be changed here. There is no batch and no delete (there is no API that deletes an account).
- Validate mandatory UTC timestamp, JSON object shape and every supplied non-null field before SQL. firstName/lastName are strings of at most 100 characters; displayName at most 128; profilePicturePath/address strings; phoneNumber matches ^\+?[0-9]{8,15}$; dateOfBirth is a real YYYY-MM-DD date on or before today's UTC date; gender is MALE/FEMALE/OTHER. Null is allowed for all eight optional fields. Do not infer non-empty constraints for optional names/address/path; invalid types are 400. A body {} is valid and returns the same 200 with no profile/audit writes after authentication.
- Sensitive fields (firstName, lastName, phoneNumber, address) are plain text over TLS and encrypted server-side using the same representation as register. displayName stays plain text because shop members/reviews use it. profilePicturePath is stored as supplied, and dateOfBirth/gender remain typed values. Never log plaintext sensitive input, token or encryption material. All SQL placeholders are typed bound UUID/byte/text/date/boolean/UTC timestamp parameters, never interpolated input.
- Preserve omitted fields; explicit null clears them. Derive hasFirstName/hasLastName/hasDisplayName/hasProfilePicturePath/hasPhoneNumber/hasAddress/hasDateOfBirth/hasGender from JSON key presence, never truthiness or non-null value. These flags are server-only parameters, not client fields. For supplied non-null sensitive fields derive encrypted bytes; null stays SQL NULL. On a new information row, omitted nullable fields bind SQL NULL; on an existing row, CASE uses presence flags so omission preserves the old value and null clears it. Do not use COALESCE to implement this distinction.
- Compute userFieldsPresent from the four m_user field-presence flags and informationFieldsPresent from the four m_user_information flags. Skip the m_user UPDATE entirely when userFieldsPresent is false. Skip information lookup/INSERT/UPDATE when informationFieldsPresent is false; do not create an empty information row merely because a name changed. A supplied information field, including explicit null, is an intentional information write and may create its first row. A no-op or skipped table must not change its audit timestamps.
- Verify Bearer JWT signature/issuer/audience/expiry/UUID sub before BEGIN; missing/invalid JWT gets generic 401 E10002 `Invalid or expired access token.`. Derive userId from verified sub and accessTokenHash as SHA-256 of the exact JWT. Lock order: BEGIN READ COMMITTED -> lock ACTIVE authen.m_user FOR UPDATE -> capture fresh server UTC now and recheck JWT expiry -> query the ACTIVE stored access token by hash/userId/expiry > now -> only then profile writes. Missing/inactive user or revoked/expired/mismatched credential, including expiry during lock wait, gets the same 401 after ROLLBACK with no writes.
- The common user lock serializes logout/reset/current-user profile writers. Never authorize a waiter from a pre-lock credential snapshot or transaction-start NOW(). Permission-assignment changes do not replace these current credential checks; this is a self operation under Q13, with no live role lookup or grant change.
- Update only supplied m_user fields with WHERE id = userId AND row_status = ACTIVE RETURNING user_id. Unexpected zero rows after the locked authorization check is an internal consistency failure (500 with rollback). Do not touch username/email/password or other users. Every write's created_by/updated_by is the verified userId, and updated_at is the fresh post-lock now.
- Insert is only the first write of the authen.m_user_information row when no non-DELETED row exists; otherwise update that single non-DELETED row. The partial unique index uq_m_user_information_user_id enforces one current row per user. Preserve existing non-DELETED row_status (including INACTIVE/LOCKED/ARCHIVED), as the existing upsert/inquiry contracts do; never reactivate it implicitly. DELETED information is historical: do not update it; a new row may be inserted. Guard existing UPDATE by informationId, userId and row_status <> DELETED, RETURNING information_id; unexpected zero rows is 500 with rollback. INSERT also returns information_id and must create exactly one row. The user lock serializes first writers, so this endpoint adds no 409 outcome.
- All supplied user/information changes are one transaction. COMMIT must succeed before 200 S10000 `Upsert User Profile Success` with data.userId only, both for first information insert and later update/no-op. On pre-commit timeout ROLLBACK then 408 E90001; on other unexpected failure/constraint error ROLLBACK then generic 500 without bizCode. Never commit one table while the other failed. No 403, 404 or 409 is added; no tokens/passwords/roles/consents are changed.
- Execution order: validate input -> verify JWT -> derive identity/hash/presence flags/typed encrypted values -> BEGIN -> user lock -> fresh now/current token check -> optional m_user UPDATE -> optional information lookup -> exactly one of INSERT or UPDATE -> COMMIT -> data.userId. Every SQL result returns to Application before branching; no success suffix may run after an aborted guarded write.

#### Scenario correspondence with sequence.wsd

| Scenario                                | Sequence behavior                                          | HTTP             | Durable effects                    |
| --------------------------------------- | ---------------------------------------------------------- | ---------------- | ---------------------------------- |
| Invalid input/fixed or unknown field    | No SQL or BEGIN                                            | 400 E10001       | None                               |
| Invalid JWT                             | No SQL or BEGIN                                            | 401 E10002       | None                               |
| Missing/inactive user                   | Locked lookup fails; ROLLBACK                              | 401 E10002       | None                               |
| Credential revoked/expired during wait  | Fresh stored-token/JWT check fails; ROLLBACK               | 401 E10002       | None                               |
| Only user fields supplied               | Update own user; skip information SQL                      | 200 S10000       | Supplied user fields only          |
| Only information fields supplied        | Skip user UPDATE; insert missing row or update current row | 200 S10000       | Supplied information fields only   |
| Both groups supplied                    | User update plus exactly one information write             | 200 S10000       | Both groups atomically             |
| Empty object                            | Authenticate, skip all profile writes, COMMIT              | 200 S10000       | None, including audit timestamps   |
| Explicit null vs omission               | Presence flags clear null; absent flags preserve values    | 200 S10000       | Only intentionally supplied fields |
| Unexpected zero guarded update/insert   | Abort interaction; ROLLBACK before success suffix          | 500              | None                               |
| Timeout / unexpected pre-commit failure | ROLLBACK both groups                                       | 408 E90001 / 500 | None                               |

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
        "bizMessage": "Date of birth must be a real date on or before today's UTC date (YYYY-MM-DD).",
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

#### Fail - Internal Server Error

```JSON
{
    "status": {
        "code": 500,
        "message": "Internal Server Error",
        "bizMessage": "An unexpected error occurred.",
        "requestId": "req-profile-review",
        "timestamp": "2026-11-08T00:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

SQL blocks are listed in orchestration/branch order. now is captured after the common user lock. The token query precedes every profile write. Presence flags are server-derived; optional table operations are skipped when their field group is absent. INSERT and UPDATE information are mutually exclusive.

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

### Table: [authen.t_user_access_token](../../../schema/authen/t_user_access_token.md)

#### QUERY - Check the current access token

```SQL
SELECT
    at.id as access_token_id
FROM authen.t_user_access_token at
WHERE at.token = '<sequence.accessTokenHash>'
AND at.user_id = '<sequence.userId>'
AND at.row_status = 'ACTIVE'
AND at.expired_at > '<sequence.now>'
```

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### UPDATE - Update user

```SQL
UPDATE authen.m_user
SET
    updated_by = '<sequence.userId>',
    updated_at = '<sequence.now>',
    first_name = CASE WHEN '<sequence.hasFirstName>' THEN '<sequence.firstNameBytes>' ELSE first_name END, -- only when firstName is specified (null clears it)
    last_name = CASE WHEN '<sequence.hasLastName>' THEN '<sequence.lastNameBytes>' ELSE last_name END, -- only when lastName is specified (null clears it)
    display_name = CASE WHEN '<sequence.hasDisplayName>' THEN '<sequence.displayName>' ELSE display_name END, -- only when displayName is specified (null clears it)
    profile_picture_path = CASE WHEN '<sequence.hasProfilePicturePath>' THEN '<sequence.profilePicturePath>' ELSE profile_picture_path END -- only when profilePicturePath is specified (null clears it)
WHERE id = '<sequence.userId>'
AND row_status = 'ACTIVE'
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

### Table: [authen.m_user_information](../../../schema/authen/m_user_information.md)

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
RETURNING id as information_id
```

### Table: [authen.m_user_information](../../../schema/authen/m_user_information.md)

#### UPDATE - Update information

```SQL
UPDATE authen.m_user_information
SET
    updated_by = '<sequence.userId>',
    updated_at = '<sequence.now>',
    phone_number = CASE WHEN '<sequence.hasPhoneNumber>' THEN '<sequence.phoneNumberBytes>' ELSE phone_number END, -- only when phoneNumber is specified (null clears it)
    address = CASE WHEN '<sequence.hasAddress>' THEN '<sequence.addressBytes>' ELSE address END, -- only when address is specified (null clears it)
    date_of_birth = CASE WHEN '<sequence.hasDateOfBirth>' THEN '<sequence.dateOfBirth>' ELSE date_of_birth END, -- only when dateOfBirth is specified (null clears it)
    gender = CASE WHEN '<sequence.hasGender>' THEN '<sequence.gender>' ELSE gender END -- only when gender is specified (null clears it)
WHERE id = '<sequence.informationId>'
AND user_id = '<sequence.userId>'
AND row_status <> 'DELETED'
RETURNING id as information_id
```
