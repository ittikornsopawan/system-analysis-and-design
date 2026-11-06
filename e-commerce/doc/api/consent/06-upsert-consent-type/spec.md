# [POST]: v1/consent/type/upsert

| Title       | Description                                                                                                                                                                                                                                                               |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Consent Type API                                                                                                                                                                                                                                                   |
| Method      | POST                                                                                                                                                                                                                                                                      |
| Endpoint    | v{version}/consent/type/upsert                                                                                                                                                                                                                                            |
| Version     | 1                                                                                                                                                                                                                                                                         |
| Description | Insert, update or delete a consent type, only a platform administrator can call it, Insert when id is not specified, Update when id is specified, Delete when rowStatus is DELETED (HTTP 204 No Content, no response body), Archive when rowStatus is ARCHIVED (HTTP 200) |

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
| 3   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-05T12:42:00.123Z                       |
| 4   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Body Parameters

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                                                                                             | Example                                               |
| --- | -------------- | ------------ | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| 1   | id             | String: UUID | OPTIONAL  | Consent Type Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED consent type counts as not found                                                                                                                              | a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d                  |
| 2   | name           | String       | MANDATORY | Consent Type Name (max 128 characters), Unique among consent types that are not DELETED                                                                                                                                                                                 | Terms and Conditions                                  |
| 3   | description    | String       | OPTIONAL  | Consent Type Description (max 1000 characters), Not specified keeps the current description on update, null clears it                                                                                                                                                   | Terms that every customer accepts to use the platform |
| 4   | isRequired     | Boolean      | OPTIONAL  | Reference data only, the consent decides whether it must be accepted, Defaults to FALSE on insert, Not specified keeps the current value on update                                                                                                                      | true                                                  |
| 5   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting, Delete or archive is allowed only when the consent type is not used by any consent that is not DELETED | ACTIVE                                                |

### Consent Type Rules

- `name` is unique among consent types that are not DELETED. The comparison is exact (upper and lower case are different names) and a name held by an INACTIVE, LOCKED or ARCHIVED consent type is still taken (409, E10003). The name of a DELETED consent type can be used again.
- `name` is required in every request, including a delete and an archive. `description` and `isRequired` are optional.
- DELETED is final: a DELETED consent type is never reopened and its `id` counts as not found (404, E10004). INACTIVE, LOCKED and ARCHIVED are reversible: an update with `rowStatus` ACTIVE opens the consent type again. `rowStatus` DELETED is rejected with 400 (E10001) when the request inserts a consent type.
- A consent type cannot be deleted or archived while any consent that is not DELETED uses it (`consent.t_consent.consent_type_id`), 409 (E10006). INACTIVE and LOCKED are allowed even when consents use the consent type, the consents are not changed. A consent type that is not ACTIVE blocks the writes that use it, because a consent is written only with an ACTIVE consent type (404, E10005, see the consent upsert). Nothing is changed in the consents that use it and they can be edited again when this row is ACTIVE.
- Permission: only a platform administrator (a user with an ACTIVE `author.t_user_role` row for the ACTIVE role `PLATFORM_ADMIN`) can change consent types. Any other caller gets 403 (E10009), after the existence check and before the duplicate name check. Reading is open to every caller with a valid access token (see the inquiry). Approved by the product owner (answered through the lead SA, 2026-11-06).
- Execution order: validate the request (400) -> existence check (404) -> permission (403, E10009) -> duplicate name check (409, E10003) -> in-use check (409, E10006, only when `rowStatus` is DELETED or ARCHIVED) -> write.
- HTTP status of the single upsert: Insert 201 Created, Update 200 Ok, Delete 204 No Content (no response body), Archive 200 Ok.

#### Example Body Parameters

##### Insert

```JSON
{
    "name": "Terms and Conditions",
    "description": "Terms that every customer accepts to use the platform",
    "isRequired": true,
    "rowStatus": "ACTIVE"
}
```

##### Update

```JSON
{
    "id": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
    "name": "Terms of Service",
    "description": "Terms that every customer accepts to use the platform",
    "isRequired": true,
    "rowStatus": "ACTIVE"
}
```

##### Delete

```JSON
{
    "id": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
    "name": "Terms of Service",
    "description": "Terms that every customer accepts to use the platform",
    "isRequired": true,
    "rowStatus": "DELETED"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/consent/type/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "name": "Terms and Conditions",
    "description": "Terms that every customer accepts to use the platform",
    "isRequired": true,
    "rowStatus": "ACTIVE"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/consent/type/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "name": "Terms and Conditions",
    "description": "Terms that every customer accepts to use the platform",
    "isRequired": true,
    "rowStatus": "ACTIVE"
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

|     | Parameter Name | Data Type    | M/O       | Source           | Field              | Description                                                                         | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ------------------ | ----------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | consentTypeId  | String: UUID | MANDATORY | Sequence Diagram | data.consentTypeId | Inserted, Updated or Archived Consent Type Id, Not returned when deleted (HTTP 204) | a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d |

### Example Response Parameters

#### Success - Insert

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Insert Consent Type Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "consentTypeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d"
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
        "bizMessage": "Update Consent Type Success",
        "requestId": "req-5c3d9e1f-2a4b-4c6d-8e0f-1a2b3c4d5e6f",
        "timestamp": "2026-11-05T12:50:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "consentTypeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d"
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
        "bizMessage": "Archive Consent Type Success",
        "requestId": "req-7e5f1a3b-4c6d-4e8f-8a2b-3c4d5e6f7a8b",
        "timestamp": "2026-11-05T12:57:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "consentTypeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d"
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
        "bizMessage": "Name is a required field.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:40.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Row Status

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Row status must not be DELETED when inserting a consent type.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:47.123Z",
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
        "bizMessage": "Consent type not found.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:40:54.123Z",
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
        "bizMessage": "You do not have permission to change consent types.",
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
        "bizMessage": "Consent type name already exists.",
        "requestId": "req-440a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:42:08.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict In Use

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "Consent type is used by consents.",
        "requestId": "req-450a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:15.123Z",
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

### Table: [consent.m_consent_type](../../../schema/consent/m_consent_type.md)

#### QUERY - Check existing consent type

```SQL
SELECT
    ct.id as consent_type_id
FROM consent.m_consent_type ct
WHERE ct.id = '<sequence.id>'
AND ct.row_status <> 'DELETED' -- the id of a DELETED consent type counts as not found
```

#### QUERY - Check duplicate name

```SQL
SELECT
    ct.id as consent_type_id
FROM consent.m_consent_type ct
WHERE ct.name = '<sequence.name>'
AND ct.row_status <> 'DELETED'
AND ct.id <> '<sequence.id>' -- only when id is specified
```

#### INSERT - Create consent type

```SQL
INSERT INTO consent.m_consent_type (
    created_by,
    row_status,
    name,
    description,
    is_required
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.rowStatus>',
    '<sequence.name>',
    '<sequence.description>',
    '<sequence.isRequired>'
)
RETURNING id as consent_type_id
```

#### UPDATE - Update or delete consent type

```SQL
UPDATE consent.m_consent_type
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.rowStatus>',
    name = '<sequence.name>',
    description = '<sequence.description>', -- only when description is specified (null clears it)
    is_required = '<sequence.isRequired>' -- only when isRequired is specified
WHERE id = '<sequence.id>'
RETURNING id as consent_type_id
```

### Table: [consent.t_consent](../../../schema/consent/t_consent.md)

#### QUERY - Check consent in use

```SQL
SELECT
    c.id as consent_id
FROM consent.t_consent c
WHERE c.consent_type_id = '<sequence.id>' -- only when rowStatus is DELETED or ARCHIVED
AND c.row_status <> 'DELETED'
```

### Table: [author.m_role](../../../schema/author/m_role.md)

#### QUERY - Get the platform administrator role

```SQL
SELECT
    r.id as role_id
FROM author.m_role r
WHERE r.name = 'PLATFORM_ADMIN'
AND r.row_status = 'ACTIVE'
```

### Table: [author.t_user_role](../../../schema/author/t_user_role.md)

#### QUERY - Check platform administrator

```SQL
SELECT
    ur.id as user_role_id
FROM author.t_user_role ur
WHERE ur.user_id = '<sequence.userId>'
AND ur.role_id = '<sequence.roleId>'
AND ur.row_status = 'ACTIVE'
```
