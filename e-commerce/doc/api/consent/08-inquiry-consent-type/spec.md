---
name: Consent Type Inquiry API Specification
description: Defines the consent type list and lookup for a caller with a valid access token, with paging, search and SQL; read when reviewing or implementing GET v1/consent/type.
status: in-review
approved_by: null
approved_at: null
---

# [GET]: v1/consent/type

| Title       | Description                                                                                                                              |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Consent Type API                                                                                                                 |
| Method      | GET                                                                                                                                      |
| Endpoint    | v{version}/consent/type                                                                                                                  |
| Version     | 1                                                                                                                                        |
| Description | Inquiry the list of consent types with paging and search, Inquiry by id returns a list with one item, Deleted consent types are excluded |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- Any caller with a valid access token can read consent types, no role is checked (the data is only names and descriptions).
- Consent types with `rowStatus` DELETED are never returned.
- Sorted by `created_at` descending and then by `id`, so that the pages never repeat or skip a row.
- `isRequired` is reference data only.
- The order of the checks, the locks and every outcome is in the sequence diagram.

---

## Request Parameters

### Header Parameters

|     | Parameter Name | Data Type | M/O       | Description                  | Example                                        |
| --- | -------------- | --------- | --------- | ---------------------------- | ---------------------------------------------- |
| 1   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-05T12:42:00.123Z                       |
| 3   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Query Parameters

|     | Parameter Name | Data Type    | M/O      | Description                                                                                            | Example                              |
| --- | -------------- | ------------ | -------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL | Consent Type Id, Response is a list with one item                                                      | a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d |
| 2   | pageIndex      | Numeric      | OPTIONAL | Page index starting from 1, Defaults to 1                                                              | 1                                    |
| 3   | pageSize       | Numeric      | OPTIONAL | Number of items per page (max 100), Defaults to 10                                                     | 10                                   |
| 4   | search         | String       | OPTIONAL | Search by consent type name or consent type description                                                | terms                                |
| 5   | isRequired     | Boolean      | OPTIONAL | Filter by is required (true, false), Not filtered when not specified                                   | true                                 |
| 6   | rowStatus      | String       | OPTIONAL | Row status filter (ACTIVE, INACTIVE, LOCKED, ARCHIVED), All statuses except DELETED when not specified | ACTIVE                               |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/consent/type?pageIndex=1&pageSize=10&rowStatus=ACTIVE HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/consent/type?pageIndex=1&pageSize=10&rowStatus=ACTIVE' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
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
| 6   | timestamp      | String: TIMESTAMP | MANDATORY | Sequence Diagram | response.status.timestamp  | API Request Timestamp (Without time zone UTC) | 2026-11-05T12:42:00.123Z                 |
| 7   | status         | String            | MANDATORY | Sequence Diagram | response.status.status     | API Request Status (SUCCESS, ERROR)           | SUCCESS                                  |

### Data Object

|     | Parameter Name | Data Type                                     | M/O       | Source           | Field           | Description                               | Example |
| --- | -------------- | --------------------------------------------- | --------- | ---------------- | --------------- | ----------------------------------------- | ------- |
| 1   | items          | [Array of Consent Type](#consent-type-object) | MANDATORY | Sequence Diagram | data.items      | Consent types, Empty array when not found |         |
| 2   | pageIndex      | Numeric                                       | MANDATORY | Sequence Diagram | data.pageIndex  | Current page index                        | 1       |
| 3   | pageSize       | Numeric                                       | MANDATORY | Sequence Diagram | data.pageSize   | Number of items per page                  | 10      |
| 4   | totalItems     | Numeric                                       | MANDATORY | Sequence Diagram | data.totalItems | Total number of items                     | 2       |
| 5   | totalPages     | Numeric                                       | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages                     | 1       |

#### Consent Type Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                      | Description                                                          | Example                                               |
| --- | -------------- | ------------ | --------- | ---------------- | -------------------------- | -------------------------------------------------------------------- | ----------------------------------------------------- |
| 1   | consentTypeId  | String: UUID | MANDATORY | Sequence Diagram | data.items[].consentTypeId | Consent Type Id                                                      | a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d                  |
| 2   | name           | String       | MANDATORY | Sequence Diagram | data.items[].name          | Consent Type Name                                                    | Terms and Conditions                                  |
| 3   | description    | String       | OPTIONAL  | Sequence Diagram | data.items[].description   | Consent Type Description, null when not set                          | Terms that every customer accepts to use the platform |
| 4   | isRequired     | Boolean      | MANDATORY | Sequence Diagram | data.items[].isRequired    | Reference data only, the consent decides whether it must be accepted | true                                                  |
| 5   | rowStatus      | String       | MANDATORY | Sequence Diagram | data.items[].rowStatus     | Row status (ACTIVE, INACTIVE, LOCKED, ARCHIVED)                      | ACTIVE                                                |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Consent Type Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "consentTypeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
                "name": "Terms and Conditions",
                "description": "Terms that every customer accepts to use the platform",
                "isRequired": true,
                "rowStatus": "ACTIVE"
            },
            {
                "consentTypeId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
                "name": "Marketing",
                "description": "Permission to send promotions and news",
                "isRequired": false,
                "rowStatus": "ACTIVE"
            }
        ],
        "pageIndex": 1,
        "pageSize": 10,
        "totalItems": 2,
        "totalPages": 1
    }
}
```

#### Success - By Id

Request: `GET v1/consent/type?id=a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d`

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Consent Type Success",
        "requestId": "req-8f6a2b4c-5d7e-4f9a-b1c3-4d5e6f7a8b9c",
        "timestamp": "2026-11-05T12:48:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "consentTypeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
                "name": "Terms and Conditions",
                "description": "Terms that every customer accepts to use the platform",
                "isRequired": true,
                "rowStatus": "ACTIVE"
            }
        ],
        "pageIndex": 1,
        "pageSize": 10,
        "totalItems": 1,
        "totalPages": 1
    }
}
```

#### Success - Not Found

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Consent Type Success",
        "requestId": "req-9a7b3c5d-6e8f-4a0b-c2d4-5e6f7a8b9c0d",
        "timestamp": "2026-11-05T12:49:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [],
        "pageIndex": 1,
        "pageSize": 10,
        "totalItems": 0,
        "totalPages": 0
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
        "bizMessage": "Page Index and Page Size must be greater than 0, Page Size must not be greater than 100.",
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
        "bizMessage": "Row status must be one of ACTIVE, INACTIVE, LOCKED, ARCHIVED.",
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

#### QUERY - Get consent types

```SQL
SELECT
    ct.id as consent_type_id,
    ct.name,
    ct.description,
    ct.is_required,
    ct.row_status
FROM consent.m_consent_type ct
WHERE ct.row_status <> 'DELETED'
AND ct.id = '<sequence.id>' -- only when id is specified
AND (ct.name ILIKE '%<sequence.search>%' OR ct.description ILIKE '%<sequence.search>%') -- only when search is specified
AND ct.is_required = '<sequence.isRequired>' -- only when isRequired is specified
AND ct.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified
ORDER BY ct.created_at DESC, ct.id
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Get total items

```SQL
SELECT
    COUNT(ct.id) as total_items
FROM consent.m_consent_type ct
WHERE ct.row_status <> 'DELETED'
AND ct.id = '<sequence.id>' -- only when id is specified
AND (ct.name ILIKE '%<sequence.search>%' OR ct.description ILIKE '%<sequence.search>%') -- only when search is specified
AND ct.is_required = '<sequence.isRequired>' -- only when isRequired is specified
AND ct.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified
```
