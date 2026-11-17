#!/usr/bin/env python3
"""Regenerate e-commerce/api/api-contract.json (OpenAPI 3.1) from the approved API specs.

usage: python3 .agents/skills/api-contract-design/scripts/gen_contract.py

The domains come from API_CONTRACT_DOMAINS in e-commerce/db/tests/check_docs.py; only specs with `status: approved`
are published. Everything is read from the spec: method and path from the title, fields from the parameter tables,
required state from M/O, constraints from explicit description phrases, examples from the JSON blocks. Owner
conventions of 2026-11-17: count fields (COUNT_FIELDS and status.code) are integer; a field is nullable when its
description says null or a spec example shows null. The script then checks every example against its schema and
exits 1 when one does not fit. `check_docs.py api-contract` guards the result in CI.
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
API = ROOT / "e-commerce/doc/api"
CONTRACT = ROOT / "e-commerce/api/api-contract.json"
JSON_BLOCK = re.compile(r"```JSON[ \t]*\n(.*?)```", re.DOTALL)
HEAD = re.compile(r"^(#{2,5}) (.+)$", re.M)
COUNT_FIELDS = {"pageIndex", "pageSize", "totalItems", "totalPages", "expiresIn"}
ERROR_BIZ = {400: ["E10001"], 401: ["E10002"], 403: ["E10009"], 404: ["E10004", "E10005"], 408: ["E90001"],
             409: ["E10003", "E10006", "E10007", "E10008"], 500: None}
COMMON_HEADERS = {"timestamp": ("Timestamp", "MANDATORY"), "requestId": ("RequestId", "OPTIONAL")}
SCALARS = {
    "String": {"type": "string"},
    "String: UUID": {"type": "string", "format": "uuid"},
    "String: TIMESTAMP": {"type": "string", "format": "date-time"},
    "DateTime": {"type": "string", "format": "date-time"},
    "Date": {"type": "string", "format": "date"},
    "Boolean": {"type": "boolean"},
    "Numeric": {"type": "number"},
    "Object": {"type": "object"},
}


def slug(text):
    return re.sub(r"[^a-z0-9 -]", "", text.lower()).strip().replace(" ", "-")


def sections(md):
    """[(level, title, body start, end)]; end is the next heading of the same or a higher level."""
    heads = [(len(m.group(1)), m.group(2).strip(), m.start(), m.end()) for m in HEAD.finditer(md)]
    out = []
    for i, (lvl, title, _, body) in enumerate(heads):
        end = next((s for l2, _, s, _ in heads[i + 1:] if l2 <= lvl), len(md))
        out.append((lvl, title, body, end))
    return out


def own_text(md, start, end):
    """Text of a heading before its first child heading."""
    m = HEAD.search(md, start, end)
    return md[start:m.start() if m else end]


def table(text):
    rows = [line for line in text.splitlines() if line.startswith("|")]
    if len(rows) < 3:
        return []
    cols = [c.strip() for c in rows[0].strip("|").split("|")]
    return [dict(zip(cols, (c.strip() for c in line.strip().strip("|").split("|")))) for line in rows[2:]]


def coerce(value, schema):
    t = schema.get("type")
    if t in ("number", "integer") and re.fullmatch(r"-?\d+(\.\d+)?", value):
        return int(value) if "." not in value else float(value)
    if t == "boolean" and value.lower() in ("true", "false"):
        return value.lower() == "true"
    return value


def constrain(schema, desc):
    t = schema.get("type")
    if t == "string":
        if m := re.search(r"\b(\d+) to (\d+) characters", desc):
            schema["minLength"], schema["maxLength"] = int(m.group(1)), int(m.group(2))
        elif m := re.search(r"\bmax (\d+) characters", desc):
            schema["maxLength"] = int(m.group(1))
        if m := re.search(r"\(([A-Z][A-Z0-9_]*(?:, [A-Z][A-Z0-9_]*)+)\)", desc):
            schema["enum"] = m.group(1).split(", ")
    if t in ("number", "integer") and (m := re.search(r"\(max (\d+)\)", desc)):
        schema["maximum"] = int(m.group(1))
    if m := re.search(r"Defaults to ([^,]+?)(?:,|$)", desc):
        value = m.group(1).strip()
        if t != "string" or re.fullmatch(r"[A-Z][A-Z0-9_]*", value):
            schema["default"] = coerce(value, schema)
    return schema


def nullable(schema):
    if isinstance(schema.get("type"), str):
        schema["type"] = [schema["type"], "null"]
        if "enum" in schema:
            schema["enum"] = schema["enum"] + [None]
    return schema


class Spec:
    def __init__(self, path):
        self.rel = str(path.relative_to(ROOT))
        self.folder = path.parent.name
        self.md = path.read_text(encoding="utf-8")
        self.secs = sections(self.md)
        self.whole = (0, "", 0, len(self.md))
        self.approved = re.search(r"^status: approved$", self.md, re.M) is not None
        m = re.search(r"^# \[(\w+)\]: (\S+)", self.md, re.M)
        self.method, self.path = m.group(1).lower(), "/" + m.group(2)
        meta = {r.get("Title"): r.get("Description") for r in table(own_text(self.md, *self.secs[0][2:4]))}
        self.name, self.desc = meta.get("Name"), meta.get("Description")
        self.errors = []

    def find(self, title, within=None):
        lo, hi = (within[2], within[3]) if within else (0, len(self.md))
        return next((s for s in self.secs if s[1] == title and lo <= s[2] < hi), None)

    def rows(self, title):
        s = self.find(title)
        return table(own_text(self.md, s[2], s[3])) if s else []

    def object_from(self, rows, scope, where):
        props, required = {}, []
        for r in rows:
            name, mo = r["Parameter Name"], r["M/O"]
            props[name] = self.field(name, r["Data Type"], r.get("Description", ""), r.get("Example", ""), scope, f"{where}.{name}")
            if mo == "MANDATORY":
                required.append(name)
            elif mo != "OPTIONAL":
                self.errors.append(f"{where}.{name}: M/O {mo!r}")
        schema = {"type": "object", "properties": props}
        if required:
            schema["required"] = required
        return schema

    def field(self, name, dtype, desc, example, scope, where):
        if m := re.fullmatch(r"\[(Object|Array) of ([^\]]+)\]\(#([^)]+)\)", dtype):
            kind, _, anchor = m.groups()
            target = next((s for s in self.secs if slug(s[1]) == anchor and scope[2] <= s[2] < scope[3]), None)
            if target is None:
                self.errors.append(f"{where}: anchor #{anchor} not found")
                inner = {"type": "object"}
            else:
                inner = self.object_from(table(own_text(self.md, target[2], target[3])), scope, where)
            schema = inner if kind == "Object" else {"type": "array", "items": inner}
        elif m := re.fullmatch(r"Array of (.+)", dtype):
            schema = {"type": "array", "items": dict(SCALARS.get(m.group(1), {}))}
        else:
            if dtype not in SCALARS:
                self.errors.append(f"{where}: unknown type {dtype!r}")
            schema = dict(SCALARS.get(dtype, {}))
            if dtype == "Numeric" and name in COUNT_FIELDS:
                schema["type"] = "integer"
            schema = constrain(schema, desc)
            if example and schema.get("type") in ("string", "number", "integer", "boolean") and "..." not in example:
                schema["examples"] = [coerce(example, schema)]
        if desc:
            schema = {"description": desc, **schema}
        if re.search(r"\bnull\b", desc):
            nullable(schema)
        return schema

    def examples(self, heading):
        """{title: json} for the JSON blocks under a heading and its sub-headings."""
        s = self.find(heading)
        if not s:
            return {}
        out = {}
        for x in [s] + [x for x in self.secs if s[2] <= x[2] < s[3]]:
            for block in JSON_BLOCK.findall(own_text(self.md, x[2], x[3])):
                if block.strip():
                    out["Example" if x is s else x[1]] = json.loads(block)
        return out

    def responses(self):
        s = self.find("Example Response Parameters")
        out = []
        for x in self.secs:
            if x[0] == 4 and s[2] <= x[2] < s[3] and re.match(r"(Success|Fail)", x[1]):
                text = self.md[x[2]:x[3]]
                block = JSON_BLOCK.search(text)
                if "HTTP/1.1 204 No Content" in text:
                    out.append((x[1], 204, None))
                elif block:
                    body = json.loads(block.group(1))
                    out.append((x[1], body["status"]["code"], body))
                else:
                    self.errors.append(f"example {x[1]!r} has no JSON and no 204")
        return out


def components(spec):
    status = spec.object_from(spec.rows("Status Object"), spec.whole, "Status")
    status["properties"]["code"]["type"] = "integer"
    comps = {
        "securitySchemes": {"bearerAuth": {
            "type": "http", "scheme": "bearer", "bearerFormat": "JWT",
            "description": "Access token from POST /v1/auth/login or POST /v1/auth/refresh-token, sent as `authorization: Bearer <token>`."}},
        "parameters": {
            "Timestamp": {"name": "timestamp", "in": "header", "required": True, "description": "Request timestamp",
                          "schema": {"type": "string", "format": "date-time"}, "example": "2026-11-05T12:42:00.123Z"},
            "RequestId": {"name": "requestId", "in": "header", "required": False, "description": "API Request Id",
                          "schema": {"type": "string"}, "example": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"},
        },
        "schemas": {"Status": status},
    }
    for code, biz in ERROR_BIZ.items():
        fixed = {"code": {"const": code}, "status": {"const": "ERROR"}}
        if biz:
            fixed["bizCode"] = {"enum": biz}
        comps["schemas"][f"Error{code}"] = {
            "type": "object", "required": ["status"],
            "description": f"Error response of HTTP {code}" + (f" (bizCode {', '.join(biz)})." if biz else " (no bizCode)."),
            "properties": {"status": {"allOf": [{"$ref": "#/components/schemas/Status"}, {"properties": fixed}]}},
        }
    return comps


def operation(spec, domain):
    words = spec.folder.split("-")[1:]
    op = {"tags": [domain], "operationId": words[0] + "".join(w.capitalize() for w in words[1:]), "summary": spec.name,
          "description": f"{spec.desc}\n\nSource spec: `{spec.rel}`", "x-spec": spec.rel, "parameters": []}
    for r in spec.rows("Header Parameters"):
        name, mo = r["Parameter Name"], r["M/O"]
        if name == "content-type":
            continue
        if name == "authorization":
            op["security"] = [{"bearerAuth": []}] if mo == "MANDATORY" else [{}, {"bearerAuth": []}]
        elif name in COMMON_HEADERS and COMMON_HEADERS[name][1] == mo:
            op["parameters"].append({"$ref": f"#/components/parameters/{COMMON_HEADERS[name][0]}"})
        else:
            schema = spec.field(name, r["Data Type"], "", r.get("Example", ""), spec.whole, f"header.{name}")
            op["parameters"].append({"name": name, "in": "header", "required": mo == "MANDATORY",
                                     "description": r.get("Description", ""), "schema": schema})
    for where in ("path", "query"):
        for r in spec.rows(f"{where.capitalize()} Parameters"):
            name = r["Parameter Name"]
            schema = spec.field(name, r["Data Type"], r.get("Description", ""), r.get("Example", ""), spec.whole, f"{where}.{name}")
            op["parameters"].append({"name": name, "in": where, "required": r["M/O"] == "MANDATORY",
                                     "description": schema.pop("description", ""), "schema": schema})
    if not op["parameters"]:
        del op["parameters"]
    body = spec.find("Body Parameters")
    if body:
        content = {"schema": spec.object_from(spec.rows("Body Parameters"), body, "body")}
        examples = spec.examples("Example Body Parameters") or spec.examples("Example Body Parameters - Display only")
        if examples:
            content["examples"] = {slug(k): {"summary": k, "value": v} for k, v in examples.items()}
        op["requestBody"] = {"required": True, "content": {"application/json": content}}
    data = spec.find("Data Object")
    data_rows = table(own_text(spec.md, data[2], data[3])) if data else []
    responses = {}
    for title, code, body_json in spec.responses():
        if code == 204:
            responses["204"] = {"description": "No Content"}
            continue
        resp = responses.setdefault(str(code), {"description": body_json["status"]["message"], "content": {"application/json": {}}})
        media = resp["content"]["application/json"]
        if "schema" not in media:
            if code < 300:
                props = {"status": {"$ref": "#/components/schemas/Status"}}
                if data_rows:
                    props["data"] = spec.object_from(data_rows, data, "data")
                media["schema"] = {"type": "object", "required": ["status"], "properties": props}
            else:
                if code not in ERROR_BIZ:
                    spec.errors.append(f"HTTP {code} has no shared error schema")
                media["schema"] = {"$ref": f"#/components/schemas/Error{code}"}
            media["examples"] = {}
        media["examples"][slug(title)] = {"summary": title, "value": body_json}
    op["responses"] = dict(sorted(responses.items()))
    return op


# ---------------------------------------------------------------- examples against their schemas
def resolve(contract, schema):
    while "$ref" in schema:
        node = contract
        for part in schema["$ref"][2:].split("/"):
            node = node[part]
        schema = node
    return schema


def kind(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    return {float: "number", str: "string", list: "array", dict: "object"}[type(value)]


def fit(contract, value, schema, where, problems, mark_null):
    """Check a subset of JSON Schema; with mark_null, a null value makes its (inline) schema nullable first."""
    if value is None and mark_null and "$ref" not in schema:
        nullable(schema)
    schema = resolve(contract, schema)
    parts = [schema] + [resolve(contract, p) for p in schema.get("allOf", [])]
    for part in parts[1:]:
        fit(contract, value, part, where, problems, False)
    types = schema.get("type")
    allowed = (types if isinstance(types, list) else [types]) if types else None
    if allowed and kind(value) not in allowed and not (kind(value) == "integer" and "number" in allowed):
        problems.append(f"{where}: {kind(value)} is not {allowed}")
        return
    if "const" in schema and value != schema["const"]:
        problems.append(f"{where}: {value!r} is not {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        problems.append(f"{where}: {value!r} is not in {schema['enum']}")
    if isinstance(value, str) and not schema.get("minLength", 0) <= len(value) <= schema.get("maxLength", len(value)):
        problems.append(f"{where}: length {len(value)} is outside {schema.get('minLength')}..{schema.get('maxLength')}")
    if kind(value) in ("integer", "number") and value > schema.get("maximum", value):
        problems.append(f"{where}: {value} is above {schema['maximum']}")
    if isinstance(value, dict):
        props = {k: v for part in parts for k, v in part.get("properties", {}).items()}
        for name in schema.get("required", []):
            if name not in value:
                problems.append(f"{where}: required {name} is missing")
        for name, item in value.items():
            if name in props:
                fit(contract, item, props[name], f"{where}.{name}", problems, mark_null)
            elif props and schema.get("type") == "object":
                problems.append(f"{where}: {name} is not in the schema")
    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            fit(contract, item, schema["items"], f"{where}[{i}]", problems, mark_null)


def check_examples(contract, mark_null):
    problems = []
    for path, item in contract["paths"].items():
        for method, op in item.items():
            tag = f"{method.upper()} {path}"
            media = op.get("requestBody", {}).get("content", {}).get("application/json", {})
            for name, ex in media.get("examples", {}).items():
                fit(contract, ex["value"], media["schema"], f"{tag} request {name}", problems, mark_null)
            for code, resp in op["responses"].items():
                media = resp.get("content", {}).get("application/json", {})
                for name, ex in media.get("examples", {}).items():
                    fit(contract, ex["value"], media["schema"], f"{tag} {code} {name}", problems, mark_null)
            for p in op.get("parameters", []):
                p = resolve(contract, p)
                for ex in p["schema"].get("examples", []) + ([p["example"]] if "example" in p else []):
                    fit(contract, ex, p["schema"], f"{tag} parameter {p['name']}", problems, False)
    return problems


def main():
    loader = importlib.util.spec_from_file_location("check_docs", ROOT / "e-commerce/db/tests/check_docs.py")
    check_docs = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(check_docs)
    domains = check_docs.API_CONTRACT_DOMAINS
    old = json.loads(CONTRACT.read_text(encoding="utf-8"))
    first = Spec(sorted(API.glob("authen-and-author/*/spec.md"))[0])
    status_rows = [{k: v for k, v in r.items() if k != "Example"} for r in first.rows("Status Object")]
    contract = {
        "openapi": "3.1.0",
        "info": {**old["info"], "description": "Machine-readable contract of the approved e-commerce API specs. The "
                 "human-readable specs under e-commerce/doc/api are the source of behaviour; every operation names its "
                 "spec in x-spec. Regenerate with .agents/skills/api-contract-design/scripts/gen_contract.py."},
        "servers": [{"url": "https://www.domain.com/api-dev", "description": "DEV"},
                    {"url": "https://www.domain.com/api-qa", "description": "QA"},
                    {"url": "https://www.domain.com/api-uat", "description": "UAT"},
                    {"url": "https://www.domain.com/api-pre-prod", "description": "PRE-PRODUCTION"},
                    {"url": "https://www.domain.com/api", "description": "PRODUCTION"}],
        "tags": [{"name": d, "description": f"Approved specs under e-commerce/doc/api/{d}"} for d in sorted(domains)],
        "paths": {},
        "components": components(first),
    }
    errors, skipped = list(first.errors), []
    for domain in domains:
        for path in sorted(API.glob(f"{domain}/*/spec.md")):
            spec = Spec(path)
            if not spec.approved:
                skipped.append(spec.rel)
                continue
            if [{k: v for k, v in r.items() if k != "Example"} for r in spec.rows("Status Object")] != status_rows:
                spec.errors.append("the Status Object differs from the shared one")
            contract["paths"].setdefault(spec.path, {})[spec.method] = operation(spec, domain)
            errors += [f"{spec.rel}: {e}" for e in spec.errors]
    contract["paths"] = {k: dict(sorted(v.items())) for k, v in sorted(contract["paths"].items())}
    check_examples(contract, mark_null=True)
    errors += check_examples(contract, mark_null=False)
    CONTRACT.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    count = sum(len(v) for v in contract["paths"].values())
    print(f"{CONTRACT.relative_to(ROOT)}: {count} operations of {len(domains)} domains")
    for rel in skipped:
        print(f"skipped (not approved): {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
