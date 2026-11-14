---
name: Consent Upsert API Specification
description: Defines the consent insert, update, delete and archive for a platform administrator with verified JWT roles, current credential gating, consent type then consent locks, DELETED as final and the consent period check; read when reviewing or implementing POST v1/consent/upsert.
status: in-review
approved_by: null
approved_at: null
---

# [POST]: v1/consent/upsert

| Title       | Description                                                                                                                                                                                                                                                                                                     |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Consent API                                                                                                                                                                                                                                                                                              |
| Method      | POST                                                                                                                                                                                                                                                                                                            |
| Endpoint    | v{version}/consent/upsert                                                                                                                                                                                                                                                                                       |
| Version     | 1                                                                                                                                                                                                                                                                                                               |
| Description | Insert, update or delete a consent, Insert when id is not specified, Update when id is specified, Delete when rowStatus is DELETED (HTTP 204 No Content, no response body), Archive when rowStatus is ARCHIVED (HTTP 200), only a platform administrator can call it, Only a platform administrator can call it |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- Governing decisions: owner-confirmed API review Q2, Q4, Q10, Q13 and the owner answers of 2026-11-13 (approved by the product owner).
- Only a platform administrator can call it: the verified JWT `roles` claim must contain the exact role `PLATFORM_ADMIN`, otherwise 403 (E10009); the author tables are never queried.
- DELETED is final: the id of a DELETED consent is 404 (E10004), while INACTIVE, LOCKED and ARCHIVED can return to ACTIVE; the consent type must exist and be ACTIVE, otherwise 404 (E10005).
- `code` stays plainly UNIQUE, so the code of a DELETED consent cannot be reused (409, E10003); when both are given `expiredAt` must be later than `effectiveAt` (400, E10001).
- Deleting or archiving a consent that has user answers is not blocked; `consentVersion` may change to any different value of at most 8 characters, and the answers of the old version become pending again (Q8) without any user consent row being overwritten.
- The transaction locks the caller user, then the consent type, then the target consent (`FOR UPDATE`); the order of the checks and every outcome is in the sequence diagram.

---

## Request Parameters

### Header Parameters

|     | Parameter Name | Data Type | M/O       | Description                  | Example                                        |
| --- | -------------- | --------- | --------- | ---------------------------- | ---------------------------------------------- |
| 1   | content-type   | String    | MANDATORY | Content type of the request  | application/json                               |
| 2   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 3   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-05T12:42:00.123Z                       |
| 4   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Body Parameters

|     | Parameter Name     | Data Type         | M/O       | Description                                                                                                                      | Example                              |
| --- | ------------------ | ----------------- | --------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id                 | String: UUID      | OPTIONAL  | Consent Id, Insert when not specified, Update or Delete when specified                                                           | c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 2   | code               | String            | MANDATORY | Consent Code (max 64 characters), Unique among all consents including a DELETED one                                              | PRIVACY_POLICY                       |
| 3   | consentTypeId      | String: UUID      | MANDATORY | Consent Type Id                                                                                                                  | a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d |
| 4   | consentVersion     | String            | OPTIONAL  | Consent Version (max 8 characters), Defaults to 1.0.0, Any different value may be set on update                                  | 1.0.0                                |
| 5   | consentName        | String            | MANDATORY | Consent Name (max 128 characters)                                                                                                | Privacy Policy                       |
| 6   | consentDescription | String            | OPTIONAL  | Consent Description                                                                                                              | Privacy policy of the service        |
| 7   | effectiveAt        | String: TIMESTAMP | OPTIONAL  | Consent Effective Timestamp (Without time zone UTC), Defaults to now                                                             | 2026-01-01T00:00:00.000Z             |
| 8   | expiredAt          | String: TIMESTAMP | OPTIONAL  | Consent Expired Timestamp (Without time zone UTC), Later than effectiveAt when both are given                                    | 2027-01-01T00:00:00.000Z             |
| 9   | isRequired         | Boolean           | OPTIONAL  | Consent is required to be accepted, Defaults to FALSE                                                                            | true                                 |
| 10  | rowStatus          | String            | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED (final), Archive when ARCHIVED | ACTIVE                               |
| 11  | body               | Object            | MANDATORY | Consent Body                                                                                                                     |                                      |

#### Example Body Parameters

##### Insert

```JSON
{
    "code": "PRIVACY_POLICY",
    "consentTypeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
    "consentVersion": "1.0.0",
    "consentName": "Privacy Policy",
    "consentDescription": "Privacy policy of the service",
    "effectiveAt": "2026-01-01T00:00:00.000Z",
    "expiredAt": null,
    "isRequired": true,
    "rowStatus": "ACTIVE",
    "body": {
        "title": "Privacy Policy",
        "content": "We collect and use your personal data as follows..."
    }
}
```

##### Update

```JSON
{
    "id": "c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "code": "PRIVACY_POLICY",
    "consentTypeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
    "consentVersion": "1.1.0",
    "consentName": "Privacy Policy",
    "consentDescription": "Privacy policy of the service",
    "effectiveAt": "2026-01-01T00:00:00.000Z",
    "expiredAt": null,
    "isRequired": true,
    "rowStatus": "ACTIVE",
    "body": {
        "title": "Privacy Policy",
        "content": "We collect and use your personal data as follows..."
    }
}
```

##### Delete

```JSON
{
    "id": "c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "code": "PRIVACY_POLICY",
    "consentTypeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
    "consentVersion": "1.1.0",
    "consentName": "Privacy Policy",
    "consentDescription": "Privacy policy of the service",
    "effectiveAt": "2026-01-01T00:00:00.000Z",
    "expiredAt": null,
    "isRequired": true,
    "rowStatus": "DELETED",
    "body": {
        "title": "Privacy Policy",
        "content": "We collect and use your personal data as follows..."
    }
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/consent/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "code": "PRIVACY_POLICY",
    "consentTypeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
    "consentVersion": "1.0.0",
    "consentName": "Privacy Policy",
    "consentDescription": "Privacy policy of the service",
    "effectiveAt": "2026-01-01T00:00:00.000Z",
    "expiredAt": null,
    "isRequired": true,
    "rowStatus": "ACTIVE",
    "body": {
        "title": "Privacy Policy",
        "content": "We collect and use your personal data as follows..."
    }
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/consent/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "code": "PRIVACY_POLICY",
    "consentTypeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
    "consentVersion": "1.0.0",
    "consentName": "Privacy Policy",
    "consentDescription": "Privacy policy of the service",
    "effectiveAt": "2026-01-01T00:00:00.000Z",
    "expiredAt": null,
    "isRequired": true,
    "rowStatus": "ACTIVE",
    "body": {
        "title": "Privacy Policy",
        "content": "We collect and use your personal data as follows..."
    }
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

|     | Parameter Name | Data Type    | M/O       | Source           | Field          | Description                                                                    | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | -------------- | ------------------------------------------------------------------------------ | ------------------------------------ |
| 1   | consentId      | String: UUID | MANDATORY | Sequence Diagram | data.consentId | Inserted, Updated or Archived Consent Id, Not returned when deleted (HTTP 204) | c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |

### Example Response Parameters

#### Success - Insert

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Insert Consent Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "consentId": "c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
    }
}
```

#### Success - Update

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Update Consent Success",
        "requestId": "req-5c3d9e1f-2a4b-4c6d-8e0f-1a2b3c4d5e6f",
        "timestamp": "2026-11-05T12:50:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "consentId": "c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
    }
}
```

#### Success - Delete

HTTP 204, no response body

```HTTP
HTTP/1.1 204 No Content
```

#### Success - Archive

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Archive Consent Success",
        "requestId": "req-7e5f1a3b-4c6d-4e8f-8a2b-3c4d5e6f7a8b",
        "timestamp": "2026-11-05T12:57:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "consentId": "c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
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
        "bizMessage": "Code, Consent Type Id, Consent Name and Body are required fields.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:45.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Period

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Expired timestamp must be later than the effective timestamp.",
        "requestId": "req-415a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:41:20.123Z",
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
        "requestId": "req-7a2cba3e-1b2d-4caf-8cce-3b1d7b3dcb6d",
        "timestamp": "2026-11-05T12:43:10.456Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10004",
        "bizMessage": "Consent not found.",
        "requestId": "req-404a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:05.321Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Consent Type

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "Consent type not found or not ACTIVE.",
        "requestId": "req-475a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:47:30.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Forbidden

```JSON
{
    "status": {
        "code": 403,
        "message": "Forbidden",
        "bizCode": "E10009",
        "bizMessage": "You do not have permission to manage consents.",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
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
        "bizMessage": "Consent code already exists.",
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

#### Fail - Internal Server Error

```JSON
{
    "status": {
        "code": 500,
        "message": "Internal Server Error",
        "bizMessage": "An unexpected error occurred.",
        "requestId": "req-consent-upsert-review",
        "timestamp": "2026-11-14T00:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

One READ COMMITTED transaction. Caller identity (`callerUserId`) is distinct from the consent; all values and the fresh UTC time are bound. Lock order: caller user, consent type, then the target consent.

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Lock the caller user

```SQL
SELECT
    u.id as user_id
FROM authen.m_user u
WHERE u.id = '<sequence.callerUserId>'
FOR UPDATE
```

### Table: [authen.t_user_access_token](../../../schema/authen/t_user_access_token.md)

#### QUERY - Check current credential and user

```SQL
SELECT
    at.id as access_token_id
FROM authen.t_user_access_token at
JOIN authen.m_user u ON u.id = at.user_id
WHERE at.token = '<sequence.accessTokenHash>'
AND at.user_id = '<sequence.callerUserId>'
AND at.row_status = 'ACTIVE'
AND at.expired_at > '<sequence.now>'
AND u.row_status = 'ACTIVE'
```

### Table: [consent.m_consent_type](../../../schema/consent/m_consent_type.md)

#### QUERY - Lock the consent type

```SQL
SELECT
    ct.id as consent_type_id,
    ct.row_status
FROM consent.m_consent_type ct
WHERE ct.id = '<sequence.consentTypeId>'
FOR UPDATE
```

### Table: [consent.t_consent](../../../schema/consent/t_consent.md)

#### QUERY - Lock existing consent

```SQL
SELECT
    c.id as consent_id,
    c.consent_version,
    c.row_status
FROM consent.t_consent c
WHERE c.id = '<sequence.id>'
AND c.row_status <> 'DELETED' -- the id of a DELETED consent counts as not found
FOR UPDATE
```

#### QUERY - Check duplicate code

```SQL
SELECT
    c.id as consent_id
FROM consent.t_consent c
WHERE c.code = '<sequence.code>'
AND ('<sequence.id>' IS NULL OR c.id <> '<sequence.id>') -- every status counts, a DELETED consent keeps its code
```

#### INSERT - Create consent

```SQL
INSERT INTO consent.t_consent (
    created_by,
    created_at,
    row_status,
    code,
    consent_type_id,
    consent_version,
    consent_name,
    consent_description,
    effective_at,
    expired_at,
    is_required,
    body
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.now>',
    '<sequence.rowStatus>',
    '<sequence.code>',
    '<sequence.consentTypeId>',
    '<sequence.consentVersion>',
    '<sequence.consentName>',
    '<sequence.consentDescription>',
    '<sequence.effectiveAt>',
    '<sequence.expiredAt>',
    '<sequence.isRequired>',
    '<sequence.body>'
)
RETURNING id as consent_id
```

#### UPDATE - Update or delete consent

```SQL
UPDATE consent.t_consent
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = '<sequence.now>',
    row_status = '<sequence.rowStatus>',
    code = '<sequence.code>',
    consent_type_id = '<sequence.consentTypeId>',
    consent_version = '<sequence.consentVersion>',
    consent_name = '<sequence.consentName>',
    consent_description = '<sequence.consentDescription>',
    effective_at = '<sequence.effectiveAt>',
    expired_at = '<sequence.expiredAt>',
    is_required = '<sequence.isRequired>',
    body = '<sequence.body>'
WHERE id = '<sequence.id>'
AND row_status <> 'DELETED'
RETURNING id as consent_id
```
