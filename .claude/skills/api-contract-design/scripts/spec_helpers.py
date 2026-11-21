"""Helpers for generating API spec markdown in the project's format (import this from a generator script).

Why generate instead of typing: the spec checker wants tables padded to equal widths, JSON that parses and
examples that agree with each other. A small generator makes the shared sections (headers, status objects,
error examples, request blocks) identical in every spec and lets one change reach every file.

Typical use in a generator kept outside the repo (a scratch directory is fine):

    import sys; sys.path.insert(0, "<.agents/skills/api-contract-design/scripts>")
    from spec_helpers import *
    s = [head("Upsert Thing API", "POST", "v{version}/thing/upsert", "Insert, update, delete or archive a thing"),
         "## Domain", DOMAIN, "---", "## Request Parameters", "### Header Parameters", headers(auth=True, content=True)]
    s.extend(req_block("POST", "/api-dev/v1/thing/upsert", {"name": "x"}))
    open("spec.md", "w", encoding="utf-8").write("\\n\\n".join(s) + "\\n")

Then run realign_tables.py on the output if you wrote tables by hand.
"""
import json

M, O = "MANDATORY", "OPTIONAL"
REQ_ID = "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
TS = "2026-11-06T09:00:00.123Z"
BEARER = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
RESP_HEAD = ["", "Parameter Name", "Data Type", "M/O", "Source", "Field", "Description", "Example"]
REQ_HEAD = ["", "Parameter Name", "Data Type", "M/O", "Description", "Example"]


def table(headers_, rows):
    """A markdown table with every column padded to the widest cell (what the checker expects)."""
    all_rows = [headers_] + rows
    widths = [max(3, max(len(r[k]) for r in all_rows)) for k in range(len(headers_))]
    fmt = lambda r: "| " + " | ".join(r[k].ljust(widths[k]) for k in range(len(headers_))) + " |"
    sep = "| " + " | ".join("-" * w for w in widths) + " |"
    return "\n".join([fmt(headers_), sep] + [fmt(r) for r in rows])


def numbered(rows):
    """Prefix each row with its running number (the first, unnamed column of every parameter table)."""
    return [[str(i + 1)] + r for i, r in enumerate(rows)]


def js(obj):
    return json.dumps(obj, indent=4, ensure_ascii=False)


DOMAIN = table(["Environment", "Url"], [
    ["DEV", "https://www.domain.com/api-dev"],
    ["QA", "https://www.domain.com/api-qa"],
    ["UAT", "https://www.domain.com/api-uat"],
    ["PRE-PRODUCTION", "https://www.domain.com/api-pre-prod"],
    ["PRODUCTION", "https://www.domain.com/api"],
])


def status(code, message, biz_code, biz_message, rid, ts, ok):
    return {"code": code, "message": message, "bizCode": biz_code, "bizMessage": biz_message,
            "requestId": rid, "timestamp": ts, "status": "SUCCESS" if ok else "ERROR"}


def example(title, obj):
    return "#### %s\n\n```JSON\n%s\n```" % (title, js(obj))


def result(title, code, message, biz, ok_text, rid, ts, data):
    """A success example: status object plus data."""
    return example(title, {"status": status(code, message, biz, ok_text, rid, ts, True), "data": data})


def fail(title, code, message, biz_code, biz_message, n):
    """An error example; n only makes the request id and the timestamp differ between examples."""
    return example(title, {"status": status(code, message, biz_code, biz_message,
                                            "req-%d0a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c" % n,
                                            "2026-11-06T09:%02d:%02d.123Z" % (n % 50, (n * 7) % 60), False)})


E_UNAUTH = ("Fail - Unauthorized", 401, "Unauthorized", "E10002", "Invalid or expired access token.", 7)
E_TIMEOUT = ("Fail - Request Timeout", 408, "Request Timeout", "E90001", "The server timed out waiting for the request.", 8)


def errs(entries):
    """entries: (title, http code, message, bizCode, bizMessage, n)."""
    return [fail(t, c, m, b, text, n) for (t, c, m, b, text, n) in entries]


def response_top():
    return table(RESP_HEAD, numbered([
        ["status", "[Object of Status](#status-object)", M, "Sequence Diagram", "response.status", "Response Status", ""],
        ["data", "[Data of Status](#data-object)", O, "Sequence Diagram", "response.data", "Response Data", ""],
    ]))


def status_object():
    return table(RESP_HEAD, numbered([
        ["code", "Numeric", M, "Sequence Diagram", "response.status.code", "HTTP Status Code", "200"],
        ["message", "String", M, "Sequence Diagram", "response.status.message", "HTTP Status Message", "Ok"],
        ["bizCode", "String", O, "Sequence Diagram", "response.status.bizCode", "Business Code Success or Fail", "S10000"],
        ["bizMessage", "String", O, "Sequence Diagram", "response.status.bizMessage", "Business Message Success or Fail", "Success"],
        ["requestId", "String", M, "Sequence Diagram", "response.status.requestId", "API Request Id", REQ_ID],
        ["timestamp", "String: TIMESTAMP", M, "Sequence Diagram", "response.status.timestamp", "API Request Timestamp (Without time zone UTC)", TS],
        ["status", "String", M, "Sequence Diagram", "response.status.status", "API Request Status (SUCCESS, ERROR)", "SUCCESS"],
    ]))


def head(name, method, endpoint, description):
    """Title and the summary table (endpoint keeps the {version} placeholder, the title shows v1)."""
    return "# [%s]: %s" % (method, endpoint.replace("v{version}", "v1")) + "\n\n" + table(["Title", "Description"], [
        ["Name", name], ["Method", method], ["Endpoint", endpoint], ["Version", "1"], ["Description", description]])


def headers(auth=True, content=False):
    """Header parameter table. auth=False for a public (storefront) API."""
    rows = []
    if content:
        rows.append(["content-type", "String", M, "Content type of the request", "application/json"])
    if auth:
        rows.append(["authorization", "String", M, "Access token with token type", BEARER])
    rows += [["timestamp", "DateTime", M, "Request timestamp", TS], ["requestId", "String", O, "API Request Id", REQ_ID]]
    return table(REQ_HEAD, numbered(rows))


def http_req(method, path, body=None, auth=True):
    lines = ["%s %s HTTP/1.1" % (method, path), "Host: www.domain.com"]
    if body is not None:
        lines.append("content-type: application/json")
    if auth:
        lines.append("authorization: %s" % BEARER)
    lines += ["timestamp: %s" % TS, "requestId: %s" % REQ_ID]
    text = "\n".join(lines)
    if body is not None:
        text += "\n\n" + js(body)
    return text


def curl_req(method, path, body=None, auth=True):
    parts = ["curl --location --request %s 'https://www.domain.com%s'" % (method, path)]
    if body is not None:
        parts.append("--header 'content-type: application/json'")
    if auth:
        parts.append("--header 'authorization: %s'" % BEARER)
    parts += ["--header 'timestamp: %s'" % TS, "--header 'requestId: %s'" % REQ_ID]
    text = " \\\n".join(parts)
    if body is not None:
        text += " \\\n--data-raw '%s'" % js(body)
    return text


def req_block(method, path, body=None, auth=True):
    """The 'Example Request' section: HTTP and cUrl."""
    return ["## Example Request", "### HTTP Request", "```HTTP\n%s\n```" % http_req(method, path, body, auth),
            "### cUrl Request", "```JSON\n%s\n```" % curl_req(method, path, body, auth)]
