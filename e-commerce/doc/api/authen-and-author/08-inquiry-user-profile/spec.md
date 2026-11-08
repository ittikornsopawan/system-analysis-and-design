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

- Governing behavior: WP4 U18/U24 and [owner-confirmed review](../../../../../docs/superpowers/specs/2026-11-07-api-review-design.md), Q13 current credential revocation and Q15 delivery, approved by the product owner. This detailed endpoint revision remains in-review; no backend/schema implementation is included.
- The profile is the data of the caller: userId comes only from verified JWT sub. No id/userId/query filters or body are accepted; reject non-empty query/body and invalid mandatory UTC timestamp with 400 E10001 before SQL. Generate requestId when omitted. No administrator role is required and no caller may choose another user's profile.
- Verify Bearer JWT signature/issuer/audience/expiry/UUID sub before BEGIN. Missing/malformed/invalid JWT gets generic 401 E10002 `Invalid or expired access token.` without SQL. Derive accessTokenHash as SHA-256 of the exact presented JWT; never read target identity from the request or trust an unverified token. All SQL parameters are typed bound UUID/bytes/UTC timestamps, never interpolated input.
- BEGIN REPEATABLE READ READ ONLY, capture fresh server UTC now immediately before the first query and recheck JWT expiry. The first SELECT joins the caller's ACTIVE m_user with its matching ACTIVE stored access token, checking exact hash, ownership and expiry > now, and projects only the six user-profile fields. A missing/inactive user or missing/revoked/expired/mismatched token returns the same 401 after ROLLBACK; do not query information or return partial data. Do not authorize from JWT validity alone or transaction-start NOW().
- Read user and information from the same repeatable-read snapshot, so a concurrent atomic profile writer cannot mix the old name with new phone/address. No user/credential lock is taken for this inquiry. Credential/user validation is performed by the first joined read; role-assignment claims do not replace current credential checks and no live role query is needed for this self operation.
- Query information only after the joined user/credential result succeeds. Read the single row with the same userId and row_status <> DELETED, as enforced by uq_m_user_information_user_id. Preserve the existing visibility of non-DELETED information, including INACTIVE/LOCKED/ARCHIVED; DELETED history is excluded. No information row is a normal state, not 404: return null for phoneNumber/address/dateOfBirth/gender.
- Sensitive fields (emailAddress, firstName, lastName, phoneNumber, address) are decrypted server-side and returned as plain text over TLS. Preserve NULL without decrypting it. displayName/profilePicturePath are copied as stored; dateOfBirth is YYYY-MM-DD or null; gender is MALE/FEMALE/OTHER or null. Q20 is approved by the product owner on 2026-11-08: “คืน null สำหรับค่าว่างเดิม (แนะนำ)”. Project legacy empty gender to null with NULLIF(ui.gender, ''); preserve existing NULL and valid values. This is response normalization only: do not update stored history. New writes still accept MALE/FEMALE/OTHER or null under the upsert contract.
- Return all ten data keys every time: userId, emailAddress, firstName, lastName, displayName, profilePicturePath, phoneNumber, address, dateOfBirth, gender. A nullable value is explicit JSON null, never an omitted key. data.userId is the verified caller id; emailAddress is mandatory and read only. Username and the password are never returned, nor token/hash/salt, session, audit/lifecycle fields, role grants or internal informationId. Unexpected mapping/decryption failure is generic 500, not partial 200.
- All SQL is SELECT-only: do not create a missing information row, mark anything read, refresh tokens or update audit fields. COMMIT the read-only transaction only after mapping succeeds, then 200 S10000 `Inquiry User Profile Success`. On timeout before commit ROLLBACK then 408 E90001; on other unexpected failure ROLLBACK then generic 500 without bizCode. The endpoint adds no 403/404/409 and no pagination or write side effect.
- Execution order: validate empty query/body and timestamp -> verify JWT -> derive verified userId/token hash -> BEGIN REPEATABLE READ READ ONLY -> fresh now/JWT expiry recheck -> joined ACTIVE user/current-token projection -> own non-DELETED information -> map all ten keys/decrypt nullable fields -> COMMIT -> 200. Every SQL result returns to Application before branching or mapping.

#### Scenario correspondence with sequence.wsd

| Scenario                                      | Sequence behavior                                            | HTTP             | Data/side effects            |
| --------------------------------------------- | ------------------------------------------------------------ | ---------------- | ---------------------------- |
| Invalid timestamp/query/body                  | No SQL or BEGIN                                              | 400 E10001       | None                         |
| Invalid JWT                                   | No SQL or BEGIN                                              | 401 E10002       | None                         |
| User/current credential invalid               | Joined query returns no row; ROLLBACK; no information query  | 401 E10002       | None                         |
| User and non-DELETED information exist        | Map stored/decrypted values from one snapshot, COMMIT        | 200 S10000       | Ten keys, no writes          |
| Information missing / only DELETED history    | Map four information keys to null, COMMIT                    | 200 S10000       | Ten keys, no row created     |
| Nullable base fields / legacy empty gender    | Explicit nulls; project empty gender to null under owner Q20 | 200 S10000       | No rewriting/history changes |
| Concurrent profile change between reads       | Both SELECTs use the same repeatable-read snapshot           | 200 S10000       | Consistent profile version   |
| Timeout / mapping or other pre-commit failure | ROLLBACK before error                                        | 408 E90001 / 500 | No partial data or writes    |

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
