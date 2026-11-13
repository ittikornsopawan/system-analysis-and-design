---
name: Register API Specification
description: Defines atomic registration, required current consent acceptance, displayed-consent read evidence, optional address and referral, validation and exact SQL for POST v1/auth/register.
status: in-review
approved_by: null
approved_at: null
---

# [POST]: v1/auth/register

| Title       | Description                                                                                                                         |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Register API                                                                                                                        |
| Method      | POST                                                                                                                                |
| Endpoint    | v{version}/auth/register                                                                                                            |
| Version     | 1                                                                                                                                   |
| Description | Register a new user with username, email address and password, together with personal information, addresses, consents and referrer |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- Governing decisions: owner-confirmed API review Q3/Q5/Q6/Q8/Q16/Q17 (approved by the product owner).
- Validate mandatory headers, JSON and object shapes before SQL.
- Sensitive fields (`username`, `emailAddress`, `firstName`, `lastName`, `phoneNumber`, `address` and address fields except title) are sent as Plain text over TLS and encrypted on the server before storage.
- `addresses` is one optional object, never an array.
- `consents` may be omitted/empty only when there are no applicable required consents.
- Use one REPEATABLE READ transaction for validation reads and every write.
- The order of the checks, the locks and every outcome is in the sequence diagram.

---

## Request Parameters

### Header Parameters

|     | Parameter Name | Data Type | M/O       | Description                 | Example                                  |
| --- | -------------- | --------- | --------- | --------------------------- | ---------------------------------------- |
| 1   | content-type   | String    | MANDATORY | Content type of the request | application/json                         |
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp           | 2026-11-05T12:42:00.123Z                 |
| 3   | requestId      | String    | OPTIONAL  | API Request Id              | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d |

### Body Parameters

|     | Parameter Name     | Data Type                            | M/O       | Description                                                                                                                                               | Example                              |
| --- | ------------------ | ------------------------------------ | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | username           | String                               | MANDATORY | Username (max 128 characters), Plain text over TLS, The system encrypts it before it is stored, It can be the email address                               | john.doe                             |
| 2   | emailAddress       | String                               | MANDATORY | Email address (max 254 characters), Plain text over TLS, The system encrypts it before it is stored                                                       | john.doe@example.com                 |
| 3   | password           | String                               | MANDATORY | Password, Plain text over TLS, 8 to 128 characters with an upper-case letter, a lower-case letter and a digit, Stored as a salted PBKDF2-HMAC-SHA256 hash | Passw0rd-Example                     |
| 4   | firstName          | String                               | OPTIONAL  | First name (max 100 characters), Plain text over TLS, The system encrypts it before it is stored                                                          | John                                 |
| 5   | lastName           | String                               | OPTIONAL  | Last name (max 100 characters), Plain text over TLS, The system encrypts it before it is stored                                                           | Doe                                  |
| 6   | displayName        | String                               | OPTIONAL  | Display name (max 128 characters)                                                                                                                         | John Doe                             |
| 7   | profilePicturePath | String                               | OPTIONAL  | Profile picture path                                                                                                                                      | /profiles/john-doe.png               |
| 8   | phoneNumber        | String                               | OPTIONAL  | Phone number                                                                                                                                              | 0812345678                           |
| 9   | address            | String                               | OPTIONAL  | Address                                                                                                                                                   | 123 Sukhumvit Road                   |
| 10  | dateOfBirth        | Date                                 | OPTIONAL  | Date of birth (YYYY-MM-DD)                                                                                                                                | 1990-01-31                           |
| 11  | gender             | String                               | OPTIONAL  | Gender (MALE, FEMALE, OTHER)                                                                                                                              | MALE                                 |
| 12  | referrerId         | String: UUID                         | OPTIONAL  | User Id of the referrer                                                                                                                                   | 8d7c6b5a-4f3e-2d1c-0b9a-876543210fed |
| 13  | addresses          | [Object of Address](#address-object) | OPTIONAL  | User address                                                                                                                                              |                                      |
| 14  | consents           | [Array of Consent](#consent-object)  | OPTIONAL  | Displayed consents; required current consents must all be included and accepted                                                                           |                                      |

#### Address Object

|     | Parameter Name | Data Type | M/O       | Description                                                                | Example            |
| --- | -------------- | --------- | --------- | -------------------------------------------------------------------------- | ------------------ |
| 1   | title          | String    | MANDATORY | Address title (max 128 characters)                                         | Home               |
| 2   | isDefault      | Boolean   | OPTIONAL  | Default address, The first address of a user is always the default address | true               |
| 3   | address        | String    | MANDATORY | Address                                                                    | 123 Sukhumvit Road |
| 4   | city           | String    | MANDATORY | City                                                                       | Watthana           |
| 5   | state          | String    | MANDATORY | State                                                                      | Bangkok            |
| 6   | postalCode     | String    | MANDATORY | Postal code                                                                | 10110              |
| 7   | country        | String    | MANDATORY | Country                                                                    | Thailand           |

#### Consent Object

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                            | Example                              |
| --- | -------------- | ------------ | --------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | consentId      | String: UUID | MANDATORY | Consent Id                                                                                                             | c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 2   | consentVersion | String       | MANDATORY | The displayed version (max 8 characters); must match the current version; never defaulted                              | 1.0.0                                |
| 3   | result         | Boolean      | OPTIONAL  | Explicit answer; omission records reading only, stored as false for this new row. Required consent needs explicit true | true                                 |

#### Example Body Parameters

```JSON
{
    "username": "john.doe",
    "emailAddress": "john.doe@example.com",
    "password": "Passw0rd-Example",
    "firstName": "John",
    "lastName": "Doe",
    "displayName": "John Doe",
    "profilePicturePath": "/profiles/john-doe.png",
    "phoneNumber": "0812345678",
    "address": "123 Sukhumvit Road",
    "dateOfBirth": "1990-01-31",
    "gender": "MALE",
    "referrerId": "8d7c6b5a-4f3e-2d1c-0b9a-876543210fed",
    "addresses": {
        "title": "Home",
        "isDefault": true,
        "address": "123 Sukhumvit Road",
        "city": "Watthana",
        "state": "Bangkok",
        "postalCode": "10110",
        "country": "Thailand"
    },
    "consents": [
        {
            "consentId": "c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
            "consentVersion": "1.0.0",
            "result": true
        }
    ]
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/auth/register HTTP/1.1
Host: www.domain.com
content-type: application/json
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "username": "john.doe",
    "emailAddress": "john.doe@example.com",
    "password": "Passw0rd-Example",
    "firstName": "John",
    "lastName": "Doe",
    "displayName": "John Doe",
    "profilePicturePath": "/profiles/john-doe.png",
    "phoneNumber": "0812345678",
    "address": "123 Sukhumvit Road",
    "dateOfBirth": "1990-01-31",
    "gender": "MALE",
    "referrerId": "8d7c6b5a-4f3e-2d1c-0b9a-876543210fed",
    "addresses": {
        "title": "Home",
        "isDefault": true,
        "address": "123 Sukhumvit Road",
        "city": "Watthana",
        "state": "Bangkok",
        "postalCode": "10110",
        "country": "Thailand"
    },
    "consents": [
        {
            "consentId": "c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
            "consentVersion": "1.0.0",
            "result": true
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/auth/register' \
--header 'content-type: application/json' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "username": "john.doe",
    "emailAddress": "john.doe@example.com",
    "password": "Passw0rd-Example",
    "firstName": "John",
    "lastName": "Doe",
    "displayName": "John Doe",
    "profilePicturePath": "/profiles/john-doe.png",
    "phoneNumber": "0812345678",
    "address": "123 Sukhumvit Road",
    "dateOfBirth": "1990-01-31",
    "gender": "MALE",
    "referrerId": "8d7c6b5a-4f3e-2d1c-0b9a-876543210fed",
    "addresses": {
        "title": "Home",
        "isDefault": true,
        "address": "123 Sukhumvit Road",
        "city": "Watthana",
        "state": "Bangkok",
        "postalCode": "10110",
        "country": "Thailand"
    },
    "consents": [
        {
            "consentId": "c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
            "consentVersion": "1.0.0",
            "result": true
        }
    ]
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
| 1   | code           | Numeric           | MANDATORY | Sequence Diagram | response.status.code       | HTTP Status Code                              | 201                                      |
| 2   | message        | String            | MANDATORY | Sequence Diagram | response.status.message    | HTTP Status Message                           | Created                                  |
| 3   | bizCode        | String            | OPTIONAL  | Sequence Diagram | response.status.bizCode    | Business Code Success or Fail                 | S10000                                   |
| 4   | bizMessage     | String            | OPTIONAL  | Sequence Diagram | response.status.bizMessage | Business Message Success or Fail              | Success                                  |
| 5   | requestId      | String            | MANDATORY | Sequence Diagram | response.status.requestId  | API Request Id                                | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d |
| 6   | timestamp      | String: TIMESTAMP | MANDATORY | Sequence Diagram | response.status.timestamp  | API Request Timestamp (Without time zone UTC) | 2026-11-05T12:42:00.123Z                 |
| 7   | status         | String            | MANDATORY | Sequence Diagram | response.status.status     | API Request Status (SUCCESS, ERROR)           | SUCCESS                                  |

### Data Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field       | Description        | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ----------- | ------------------ | ------------------------------------ |
| 1   | userId         | String: UUID | MANDATORY | Sequence Diagram | data.userId | Registered User Id | 3f2b8c1e-5d4a-4e7b-9c6d-1a2b3c4d5e6f |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Register Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "userId": "3f2b8c1e-5d4a-4e7b-9c6d-1a2b3c4d5e6f"
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
        "bizMessage": "Username, Email Address and Password are required fields.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:45.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Password

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Password must be 8 to 128 characters and contain an upper-case letter, a lower-case letter and a digit.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:50.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10003",
        "bizMessage": "Username or email address already exists.",
        "requestId": "req-409a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:20.789Z",
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

#### Fail - Not Found Reference

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "Consent or referrer not found.",
        "requestId": "req-register-review",
        "timestamp": "2026-11-07T12:00:00.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Consent Version

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Consent version is no longer current.",
        "requestId": "req-register-review",
        "timestamp": "2026-11-07T12:00:00.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Required Consent

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "All current required consents must be accepted.",
        "requestId": "req-register-review",
        "timestamp": "2026-11-07T12:00:00.123Z",
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
        "requestId": "req-register-review",
        "timestamp": "2026-11-07T12:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

Statements follow first execution order; optional children run only when present. All policy reads share one REPEATABLE READ snapshot and UTC now. UUID arrays are bound, including an empty array. Inserts use typed parameters and SQL NULL for omitted nullable values.

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Check existing user

```SQL
SELECT
    u.id as user_id
FROM authen.m_user u
WHERE (u.username = '<sequence.usernameBytes>' OR u.email_address = '<sequence.emailAddressBytes>')
```

### Table: [consent.t_consent](../../../schema/consent/t_consent.md)

#### QUERY - Get effective consents

```SQL
SELECT
    c.id as consent_id,
    c.consent_type_id,
    c.consent_version,
    c.is_required
FROM consent.t_consent c
WHERE c.row_status = 'ACTIVE'
AND c.effective_at <= '<sequence.now>'
AND (c.expired_at IS NULL OR c.expired_at > '<sequence.now>')
ORDER BY c.id
```

### Table: [consent.m_consent_type](../../../schema/consent/m_consent_type.md)

#### QUERY - Get active consent types

```SQL
SELECT
    ct.id as consent_type_id
FROM consent.m_consent_type ct
WHERE ct.id = ANY ('<sequence.consentTypeIds>'::UUID[])
AND ct.row_status = 'ACTIVE'
ORDER BY ct.id
```

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Check referrer

```SQL
SELECT
    u.id as referrer_id
FROM authen.m_user u
WHERE u.id = '<sequence.referrerId>' -- only when referrerId is specified
```

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### INSERT - Create user

```SQL
INSERT INTO authen.m_user (
    created_by,
    username,
    email_address,
    first_name,
    last_name,
    display_name,
    profile_picture_path
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.usernameBytes>',
    '<sequence.emailAddressBytes>',
    '<sequence.firstNameBytes>',
    '<sequence.lastNameBytes>',
    '<sequence.displayName>',
    '<sequence.profilePicturePath>'
)
RETURNING id as user_id
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
    '<sequence.createdBy>',
    'PASSWORD',
    '<sequence.userId>',
    '<sequence.passwordBytes>',
    '<sequence.passwordSaltBytes>'
)
```

### Table: [authen.m_user_information](../../../schema/authen/m_user_information.md)

#### INSERT - Create user information

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
    '<sequence.createdBy>',
    '<sequence.userId>',
    '<sequence.phoneNumberBytes>',
    '<sequence.addressBytes>',
    '<sequence.dateOfBirth>',
    '<sequence.gender>'
)
```

### Table: [authen.t_user_address](../../../schema/authen/t_user_address.md)

#### INSERT - Create user address

```SQL
INSERT INTO authen.t_user_address (
    created_by,
    user_id,
    title,
    is_default,
    address,
    city,
    state,
    postal_code,
    country
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.userId>',
    '<sequence.addresses.title>',
    TRUE, -- the first address of a user is the default address, whatever isDefault says
    '<sequence.addresses.addressBytes>',
    '<sequence.addresses.cityBytes>',
    '<sequence.addresses.stateBytes>',
    '<sequence.addresses.postalCodeBytes>',
    '<sequence.addresses.countryBytes>'
)
```

### Table: [authen.t_user_consent](../../../schema/authen/t_user_consent.md)

#### INSERT - Create user consent

```SQL
INSERT INTO authen.t_user_consent (
    created_by,
    user_id,
    consent_id,
    consent_version,
    result,
    is_read,
    read_at
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.userId>',
    '<sequence.consents.consentId>',
    '<sequence.consents.consentVersion>',
    '<sequence.consents.result>', -- explicit result, or false when omitted
    TRUE, -- supplied object records displayed/read version
    '<sequence.now>'
)
```

### Table: [authen.l_user_referral](../../../schema/authen/l_user_referral.md)

#### INSERT - Create user referral

```SQL
INSERT INTO authen.l_user_referral (
    created_by,
    user_id,
    referrer_id
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.userId>',
    '<sequence.referrerId>'
)
```
