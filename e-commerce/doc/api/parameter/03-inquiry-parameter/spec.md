---
name: "Inquiry Parameter API"
description: "Public inquiry of the parameters (reference data such as countries, provinces, districts, subdistricts and postal codes) with the parent, root, key, status and effective-period filters and paging; only ACTIVE parameters are returned. Read it when you implement, review or test GET v1/parameter."
status: approved
approved_by: Josh (SA Lead, delegated by Ittikorn 2026-11-17)
approved_at: 2026-11-18T07:49:47+07:00
---

# [GET]: v1/parameter

| Title       | Description                                                                                                                                                                                                                    |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Name        | Inquiry Parameter API                                                                                                                                                                                                          |
| Method      | GET                                                                                                                                                                                                                            |
| Endpoint    | v{version}/parameter                                                                                                                                                                                                           |
| Version     | 1                                                                                                                                                                                                                              |
| Description | Inquiry the list of parameters with paging and filters, Inquiry by id returns a list with one item, Public API, no access token, Only ACTIVE parameters that are effective now are returned unless includeNotEffective is true |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- The rules of this section were decided by Josh, SA Lead, delegated by the owner, 2026-11-18 (Q6 and Q7 of the parameter API review).
- This API is public: it needs no access token, because the registration page (authen-and-author/01-register, also public) loads the country, province, district, subdistrict and postal code lists before the user has logged in.
- A public caller sees only ACTIVE parameters: a DELETED, INACTIVE, LOCKED or ARCHIVED parameter is never returned. `rowStatus` stays a filter, but any value other than ACTIVE answers 200 with `items` empty. A parameter is returned on its own status, the status of its parent is not checked.
- By default only the parameters effective now are returned: `effectiveAt` is now or earlier and `expiredAt` is null or later than now (UTC, the server time of the request). `includeNotEffective` true also returns the ACTIVE parameters that are not effective yet or have expired.
- `parentId` returns the children of that parameter. `rootOnly` true returns only the parameters without a parent (for example the countries). `rootOnly` true together with `parentId` is 400 (E10001). Without both, the parameters of every level are returned.
- `key` is an exact match (case-sensitive). `search` matches part of the key or of the text of any language of `value`, ignoring case. It is matched literally: the service escapes `\`, `%` and `_` in `search` before binding it, and the SQL says `ESCAPE '\'`, so `10_00` does not match `10100`.
- The parameters are sorted by `key` ascending, then by `parameterId` ascending, so the pages never repeat or skip a parameter. Nothing found is 200 with `items` empty.
- `value`, `title` and `display` are returned as the whole localized JSON object; the client picks the language. `title`, `display`, `metadata`, `parentId` and `expiredAt` are null when they are not set.
- Rate limit: this API, which needs no access token, answers 429 (E90002) with a `Retry-After` header when a client IP sends more than 60 requests per minute (configurable); the limiter answers before the handler runs, so the 429 is not drawn in the sequence diagram. The rule is in the section Limits and rate limiting of `api-conventions.md`.

---

## Request Parameters

### Header Parameters

|     | Parameter Name | Data Type | M/O       | Description       | Example                                  |
| --- | -------------- | --------- | --------- | ----------------- | ---------------------------------------- |
| 1   | timestamp      | DateTime  | MANDATORY | Request timestamp | 2026-11-18T09:00:00.123Z                 |
| 2   | requestId      | String    | OPTIONAL  | API Request Id    | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d |

### Query Parameters

|     | Parameter Name      | Data Type    | M/O      | Description                                                                                                                      | Example                              |
| --- | ------------------- | ------------ | -------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id                  | String: UUID | OPTIONAL | Parameter Id, Response is a list with one item                                                                                   | 2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e |
| 2   | parentId            | String: UUID | OPTIONAL | Parent Parameter Id, Only the children of this parameter, Not allowed with rootOnly true                                         | 1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d |
| 3   | rootOnly            | Boolean      | OPTIONAL | Only the parameters without a parent when true, Defaults to false                                                                | false                                |
| 4   | key                 | String       | OPTIONAL | Parameter Key, Exact match                                                                                                       | TH-10                                |
| 5   | search              | String       | OPTIONAL | Search by part of the key or of the value in any language, Ignoring case                                                         | bangkok                              |
| 6   | rowStatus           | String       | OPTIONAL | Row status filter (ACTIVE, INACTIVE, LOCKED, ARCHIVED), Only ACTIVE parameters are returned, Another value answers an empty list | ACTIVE                               |
| 7   | includeNotEffective | Boolean      | OPTIONAL | Also the ACTIVE parameters that are not effective yet or have expired when true, Defaults to false                               | false                                |
| 8   | pageIndex           | Numeric      | OPTIONAL | Page index starting from 1, Defaults to 1                                                                                        | 1                                    |
| 9   | pageSize            | Numeric      | OPTIONAL | Number of items per page (max 100), Defaults to 10                                                                               | 10                                   |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/parameter?parentId=1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d&pageIndex=1&pageSize=10 HTTP/1.1
Host: www.domain.com
timestamp: 2026-11-18T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/parameter?parentId=1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d&pageIndex=1&pageSize=10' \
--header 'timestamp: 2026-11-18T09:00:00.123Z' \
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

|     | Parameter Name | Data Type                               | M/O       | Source           | Field           | Description                            | Example |
| --- | -------------- | --------------------------------------- | --------- | ---------------- | --------------- | -------------------------------------- | ------- |
| 1   | items          | [Array of Parameter](#parameter-object) | MANDATORY | Sequence Diagram | data.items      | Parameters, Empty array when not found |         |
| 2   | pageIndex      | Numeric                                 | MANDATORY | Sequence Diagram | data.pageIndex  | Current page index                     | 1       |
| 3   | pageSize       | Numeric                                 | MANDATORY | Sequence Diagram | data.pageSize   | Number of items per page               | 10      |
| 4   | totalItems     | Numeric                                 | MANDATORY | Sequence Diagram | data.totalItems | Total number of items                  | 2       |
| 5   | totalPages     | Numeric                                 | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages                  | 1       |

#### Parameter Object

|     | Parameter Name | Data Type         | M/O       | Source           | Field                    | Description                                                              | Example                              |
| --- | -------------- | ----------------- | --------- | ---------------- | ------------------------ | ------------------------------------------------------------------------ | ------------------------------------ |
| 1   | parameterId    | String: UUID      | MANDATORY | Sequence Diagram | data.items[].parameterId | Parameter Id                                                             | 2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e |
| 2   | parentId       | String: UUID      | MANDATORY | Sequence Diagram | data.items[].parentId    | Parent Parameter Id, null for a root parameter                           | 1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d |
| 3   | key            | String            | MANDATORY | Sequence Diagram | data.items[].key         | Parameter Key                                                            | TH-10                                |
| 4   | value          | Object            | MANDATORY | Sequence Diagram | data.items[].value       | Localized value, An object of language codes and texts                   |                                      |
| 5   | title          | Object            | MANDATORY | Sequence Diagram | data.items[].title       | Localized title, null when not set                                       |                                      |
| 6   | display        | Object            | MANDATORY | Sequence Diagram | data.items[].display     | Localized display text, null when not set                                |                                      |
| 7   | metadata       | Object            | MANDATORY | Sequence Diagram | data.items[].metadata    | Metadata, null when not set                                              |                                      |
| 8   | effectiveAt    | String: TIMESTAMP | MANDATORY | Sequence Diagram | data.items[].effectiveAt | Start of the effective period (UTC)                                      | 2026-11-18T00:00:00.000Z             |
| 9   | expiredAt      | String: TIMESTAMP | MANDATORY | Sequence Diagram | data.items[].expiredAt   | End of the effective period (UTC), null when the parameter never expires | 2030-12-31T23:59:59.000Z             |
| 10  | rowStatus      | String            | MANDATORY | Sequence Diagram | data.items[].rowStatus   | Row status, Always ACTIVE                                                | ACTIVE                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-18T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "parameterId": "2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e",
                "parentId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
                "key": "TH-10",
                "value": {
                    "en": "Bangkok",
                    "th": "กรุงเทพมหานคร"
                },
                "title": {
                    "en": "Province",
                    "th": "จังหวัด"
                },
                "display": {
                    "en": "Bangkok",
                    "th": "กรุงเทพฯ"
                },
                "metadata": {
                    "isoCode": "TH-10"
                },
                "effectiveAt": "2026-11-18T00:00:00.000Z",
                "expiredAt": null,
                "rowStatus": "ACTIVE"
            },
            {
                "parameterId": "3c4d5e6f-7a8b-4c9d-8e0f-2a3b4c5d6e7f",
                "parentId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
                "key": "TH-11",
                "value": {
                    "en": "Samut Prakan",
                    "th": "สมุทรปราการ"
                },
                "title": null,
                "display": null,
                "metadata": null,
                "effectiveAt": "2026-11-18T00:00:00.000Z",
                "expiredAt": "2030-12-31T23:59:59.000Z",
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

#### Fail - Bad Request

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Page size must be between 1 and 100.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-18T09:01:00.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Root Only

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "rootOnly must not be true together with parentId.",
        "requestId": "req-401a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-18T09:01:10.123Z",
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
        "timestamp": "2026-11-18T09:01:20.123Z",
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
        "requestId": "req-500a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-18T09:01:30.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

No transaction: two reads with the same filters. `now` is the server UTC time of the request, bound once for both reads.

### Table: [public.m_parameter](../../../schema/public/m_parameter.md)

#### QUERY - Get parameters

```SQL
SELECT
    p.id as parameter_id,
    p.parent_id,
    p.key,
    p.value,
    p.title,
    p.display,
    p.metadata,
    p.effective_at,
    p.expired_at,
    p.row_status
FROM public.m_parameter p
WHERE p.row_status = 'ACTIVE' -- a public caller sees only ACTIVE parameters
AND p.id = '<sequence.id>' -- only when id is specified
AND p.parent_id = '<sequence.parentId>' -- only when parentId is specified
AND p.parent_id IS NULL -- only when rootOnly is true
AND p.key = '<sequence.key>' -- only when key is specified
AND (p.key ILIKE '%<sequence.search>%' ESCAPE '\' OR EXISTS (SELECT 1 FROM jsonb_each_text(p.value) v WHERE v.value ILIKE '%<sequence.search>%' ESCAPE '\')) -- only when search is specified
AND p.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified
AND p.effective_at <= '<sequence.now>' -- unless includeNotEffective is true
AND (p.expired_at IS NULL OR p.expired_at > '<sequence.now>') -- unless includeNotEffective is true
ORDER BY p.key, p.id
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Get total items

```SQL
SELECT
    COUNT(p.id) as total_items
FROM public.m_parameter p
WHERE p.row_status = 'ACTIVE' -- a public caller sees only ACTIVE parameters
AND p.id = '<sequence.id>' -- only when id is specified
AND p.parent_id = '<sequence.parentId>' -- only when parentId is specified
AND p.parent_id IS NULL -- only when rootOnly is true
AND p.key = '<sequence.key>' -- only when key is specified
AND (p.key ILIKE '%<sequence.search>%' ESCAPE '\' OR EXISTS (SELECT 1 FROM jsonb_each_text(p.value) v WHERE v.value ILIKE '%<sequence.search>%' ESCAPE '\')) -- only when search is specified
AND p.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified
AND p.effective_at <= '<sequence.now>' -- unless includeNotEffective is true
AND (p.expired_at IS NULL OR p.expired_at > '<sequence.now>') -- unless includeNotEffective is true
```
