#!/usr/bin/env python3
"""Regenerate e-commerce/api/api-contract.json (OpenAPI 3.1) from the approved API specs.

usage: python3 .agents/skills/api-contract-design/scripts/gen_contract.py [--check | --pretty OUT]

--check writes nothing and exits 1 when the committed contract differs from a fresh generation (a hand edit, or a spec
change that was not regenerated); `check_docs.py api-contract` runs it in CI.
--pretty OUT writes an indented copy to OUT for reading and diffing and leaves the committed contract untouched: the
committed file stays one line because the indented one passes the 1 MB preflight limit. OUT must not be the contract.

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
COUNT_FIELDS = {"pageIndex", "pageSize", "totalItems", "totalPages", "expiresIn", "created"}
ERROR_BIZ = {400: ["E10001"], 401: ["E10002"], 403: ["E10009"], 404: ["E10004", "E10005"], 408: ["E90001"],
             409: ["E10003", "E10006", "E10007", "E10008"], 429: ["E90002"], 500: None}
# The rules of a spec that say who may call it (the lines of ## Domain that name a permission, a role, a member or an
# owner, a public API or the signature), copied word for word into the description of the operation.
ACCESS = re.compile(r"(?i)\bpermission\b|platform administrator|PLATFORM_ADMIN|ACTIVE member|member of the shop|owner of the (order|payment|cart)|"
                    r"can call|may call|API is public|public API|endpoint is public|no access token|no `?authorization|belongs? to the caller|only the (owner|caller)|"
                    r"\bthe caller\b|\b403\b|E10009|signature")
NOT_ACCESS = re.compile(r"^(Rate limit|Governing decisions|The transaction locks the caller user)")  # said once in the contract: 429, the scheme
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


def pascal(text):
    return "".join(w[:1].upper() + w[1:] for w in re.split(r"[^A-Za-z0-9]+", text) if w)


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
        value = coerce(m.group(1).strip(), schema)
        # a conditional default ("FALSE on insert") stays in the description only
        if (t == "string" and re.fullmatch(r"[A-Z][A-Z0-9_]*", value)) or (t != "string" and not isinstance(value, str)):
            schema["default"] = value
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
        self.domain = path.parent.parent.name
        self.md = path.read_text(encoding="utf-8")
        self.secs = sections(self.md)
        self.whole = (0, "", 0, len(self.md))
        self.approved = re.search(r"^status: approved$", self.md, re.M) is not None
        m = re.search(r"^# \[(\w+)\]: (\S+)", self.md, re.M)
        self.method, self.path = m.group(1).lower(), "/" + m.group(2)
        meta = {r.get("Title"): r.get("Description") for r in table(self.md[m.end():self.secs[0][2]])}
        self.name, self.desc = meta.get("Name"), meta.get("Description")
        self.errors = [] if self.name and self.desc else ["no Name or Description in the table under the title"]
        domain = re.search(r"^## Domain\n(.*?)^---", self.md, re.M | re.S)
        front = re.match(r"---\n(.*?)\n---\n", self.md, re.S)
        self.front_rules = re.findall(r"^- (.*)$", front.group(1), re.M) if front else []  # a defect: the rules belong under ## Domain
        rules = re.findall(r"^- (.*(?:\n  .*)*)", domain.group(1), re.M) if domain else []
        self.access = [" ".join(r.split()) for r in rules + self.front_rules if ACCESS.search(r) and not NOT_ACCESS.match(r)]
        self.rate_limit = re.search(r"answers 429 \(E90002\)", self.md) is not None

    def find(self, title, within=None):
        lo, hi = (within[2], within[3]) if within else (0, len(self.md))
        return next((s for s in self.secs if s[1] == title and lo <= s[2] < hi), None)

    def rows(self, title):
        s = self.find(title)
        return table(own_text(self.md, s[2], s[3])) if s else []

    def object_from(self, rows, scope, where):
        """A dotted name (data.object.id) is a field of nested objects: a table of an external payload (the Stripe
        webhook) that lists only the fields the system reads, so those objects accept other fields
        (additionalProperties: true, lead decision of 2026-11-17); a parent is required when a child is MANDATORY."""
        schema = {"type": "object", "properties": {}}
        for r in rows:
            name, mo = r["Parameter Name"], r["M/O"]
            if mo not in ("MANDATORY", "OPTIONAL"):
                self.errors.append(f"{where}.{name}: M/O {mo!r}")
            *parents, leaf = name.split(".")
            node = schema
            if parents:
                schema["additionalProperties"] = True
            for part in parents:
                if mo == "MANDATORY" and part not in node.setdefault("required", []):
                    node["required"].append(part)
                node = node["properties"].setdefault(part, {"type": "object", "additionalProperties": True, "properties": {}})
            node["properties"][leaf] = self.field(leaf, r["Data Type"], r.get("Description", ""), r.get("Example", ""), scope, f"{where}.{name}")
            if mo == "MANDATORY":
                node.setdefault("required", []).append(leaf)
        return schema

    def tag(self, schema, name, role, op=False):
        """Mark an object for Components.register(): its name in the spec, role, origin, and whether the name is already the operation's (removed there)."""
        schema.update({"x-name": name, "x-role": role, "x-domain": self.domain, "x-from": self.rel, "x-op": op})
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
                self.tag(inner, pascal(re.sub(r" Object$", "", target[1])), "Request" if where.startswith("body") else "Response")
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
        if schema.get("type") == "array":
            if m := re.search(r"min (\d+), max (\d+) items", desc):
                schema["minItems"], schema["maxItems"] = int(m.group(1)), int(m.group(2))
            elif m := re.search(r"\(max (\d+)\b", desc):
                schema["maxItems"] = int(m.group(1))
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
            "description": "Access token from POST /v1/auth/login or POST /v1/auth/refresh-token, sent as `authorization: Bearer <token>`. "
                           "A valid signature and expiry are not enough. After them the API also checks that the hash of the exact token matches an ACTIVE stored "
                           "credential and that the user is ACTIVE; a token that was logged out, replaced by a refresh or closed by a password reset is refused with "
                           "401 (E10002). Roles come only from the `roles` claim of the verified token (a platform administrator has the exact, case-sensitive role "
                           "`PLATFORM_ADMIN`), never from the database."}},
        "headers": {"RetryAfter": {"description": "Seconds to wait before the next request (a 429 answer).", "required": True,
                                   "schema": {"type": "integer", "minimum": 0}}},
        "parameters": {
            "Timestamp": {"name": "timestamp", "in": "header", "required": True, "description": "Request timestamp",
                          "schema": {"type": "string", "format": "date-time"}, "example": "2026-11-05T12:42:00.123Z"},
            "RequestId": {"name": "requestId", "in": "header", "required": False, "description": "API Request Id",
                          "schema": {"type": "string"}, "example": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"},
        },
        "schemas": {
            "Status": status,
            "ResponseEnvelope": {"type": "object", "required": ["status"], "description": "Every success response: the status object, and the data of the operation in `data`.",
                                 "properties": {"status": {"$ref": "#/components/schemas/Status"}}},
        },
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
    op_name = pascal(" ".join(words))
    op = {"tags": [domain], "operationId": words[0] + "".join(w.capitalize() for w in words[1:]), "summary": spec.name,
          "description": spec.desc + ("\n\nWho may call, as the spec says:\n" + "\n".join("- " + a for a in spec.access) if spec.access else "")
                         + f"\n\nSource spec: `{spec.rel}`", "x-spec": spec.rel, "security": [], "parameters": []}  # security [] = public, said out loud
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
        content = {"schema": spec.tag(spec.object_from(spec.rows("Body Parameters"), body, "body"), f"{op_name}Request", "Request", op=True)}
        examples = spec.examples("Example Body Parameters") or spec.examples("Example Body Parameters - Display only")
        if examples:
            content["examples"] = {slug(k): {"summary": k, "value": v} for k, v in examples.items()}
        op["requestBody"] = {"required": True, "content": {"application/json": content}}
    data = spec.find("Data Object")
    data_rows = table(own_text(spec.md, data[2], data[3])) if data else []
    responses, payload = {}, None
    for title, code, body_json in spec.responses():
        if code == 204:
            responses["204"] = {"description": "No Content"}
            continue
        resp = responses.setdefault(str(code), {"description": body_json["status"]["message"], "content": {"application/json": {}}})
        media = resp["content"]["application/json"]
        if "schema" not in media:
            if code < 300:
                envelope = {"$ref": "#/components/schemas/ResponseEnvelope"}
                if data_rows:
                    # one payload for every success code, so that a null seen in one example makes the field nullable in all
                    payload = payload or spec.tag(spec.object_from(data_rows, data, "data"), f"{op_name}Data", "Response", op=True)
                    media["schema"] = {"allOf": [envelope, {"type": "object", "properties": {"data": payload}}]}
                else:
                    media["schema"] = envelope
            else:
                if code not in ERROR_BIZ:
                    spec.errors.append(f"HTTP {code} has no shared error schema")
                media["schema"] = {"$ref": f"#/components/schemas/Error{code}"}
            media["examples"] = {}
        media["examples"][slug(title)] = {"summary": title, "value": body_json}
    if "429" not in responses and spec.rate_limit:  # the spec states the limit in its rules, so the contract answers it
        responses["429"] = {"description": "Too Many Requests", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error429"}}}}
    if "429" in responses:
        responses["429"]["headers"] = {"Retry-After": {"$ref": "#/components/headers/RetryAfter"}}
    op["responses"] = dict(sorted(responses.items()))
    return op


# ---------------------------------------------------------------- shared components
PAGE_KEYS = ["pageIndex", "pageSize", "totalItems", "totalPages"]
META = ("x-name", "x-role", "x-domain", "x-from", "x-op")
OPAQUE = {"examples", "example", "x-spec"}


def shape(node):
    """The structure of a schema for comparing: everything but the sample values."""
    if isinstance(node, dict):
        return {k: shape(v) for k, v in node.items() if k != "examples"}
    if isinstance(node, list):
        return [shape(v) for v in node]
    return node


def key(node):
    return json.dumps(shape(node), sort_keys=True, separators=(",", ":"))


NOISE = {"inquiry", "upsert", "batch", "create", "submit", "check", "confirm", "cancel"}  # the action of a spec, never a qualifier
DONE = {"create": "Created", "submit": "Submitted", "confirm": "Confirmed", "cancel": "Cancelled"}  # names the result of an action


def words(text):
    return [w.lower() for w in re.findall(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|\d+", text)]


def repeats(name):
    """A name that says a word twice in a row (ShopShop, ConsentConsent) reads badly in C#."""
    ws = words(name)
    return any(a == b for a, b in zip(ws, ws[1:]))


class Components:
    """Turns every object table of a spec (`#### <Name> Object`, the request body and the data of a response) into a
    component of components/schemas; an identical shape is one component whatever the spec. The names are given in
    finalize(), after every spec has been seen, so that a shape used by several specs gets the plain name."""

    def __init__(self, comps):
        self.schemas = comps["schemas"]
        self.fixed = set(self.schemas)
        self.by_shape = {}   # shape -> id
        self.info = {}       # id -> {"node", "op", "usages": [meta]}
        self.names = {}      # the name in the spec -> {component: [specs]}, filled by finalize()

    def page_info(self, props, required):
        if not (set(PAGE_KEYS) <= set(props) and set(PAGE_KEYS) <= set(required) and all(props[k].get("type") == "integer" for k in PAGE_KEYS)):
            return None
        if "PageInfo" not in self.schemas:
            self.schemas["PageInfo"] = {"type": "object", "required": PAGE_KEYS, "description": "Paging of an inquiry (pageIndex, pageSize, totalItems, totalPages).",
                                        "properties": {k: shape(props[k]) for k in PAGE_KEYS}}
            self.fixed.add("PageInfo")
        return {"$ref": "#/components/schemas/PageInfo"}

    def register(self, node):
        meta = {k: node.pop(k) for k in META}
        desc = node.pop("description", None)
        types = node.get("type")
        null = isinstance(types, list) and "null" in types
        if null:
            node["type"] = "object"
        page = self.page_info(node.get("properties", {}), node.get("required", []))
        if page:
            # a paging field that the spec words differently ("Total number of orders") keeps its own wording
            own = {k: v for k, v in node["properties"].items() if k in PAGE_KEYS and key(v) != key(self.schemas["PageInfo"]["properties"][k])}
            rest = {**{k: v for k, v in node["properties"].items() if k not in PAGE_KEYS}, **own}
            need = [k for k in node.get("required", []) if k not in PAGE_KEYS]
            fragment = {"type": "object", "properties": rest, **({"required": need} if need else {})}
            node = {"allOf": [page, fragment]}
        sid = self.by_shape.setdefault(key(node), len(self.by_shape))
        entry = self.info.setdefault(sid, {"node": node, "op": meta["x-op"], "usages": []})
        entry["usages"].append(meta)
        ref = {"$ref": f"#/components/schemas/@{sid}@"}
        out = {"anyOf": [ref, {"type": "null"}]} if null else ref
        return {**({"description": desc} if desc else {}), **out}

    def walk(self, node):
        if isinstance(node, list):
            return [self.walk(v) for v in node]
        if not isinstance(node, dict):
            return node
        out = {k: (v if k in OPAQUE else self.walk(v)) for k, v in node.items()}
        return self.register(out) if "x-name" in out else out

    @staticmethod
    def about(use):
        """True when the spec is about the object itself (`inquiry-shop` for a Shop), so the plain name suits it."""
        base_words = words(use["x-name"])
        return any(w in base_words for w in use["x-from"].split("/")[-2].split("-")[1:] if w not in NOISE)

    @staticmethod
    def candidates(use, shared, across):
        """The names a shape may take, best first. The words of the spec qualify a name (`ActiveConsent` for the object
        of `inquiry-active-consent`, `PermissionBatchScopeRequest` for the batch of `upsert-permission-batch`); a
        domain prefix comes last, for two domains that clash. A shape shared by several domains takes the plain name."""
        base, role = use["x-name"], use["x-role"]
        whole = use["x-from"].split("/")[-2].split("-")[1:]
        spec_words, base_words = [w for w in whole if w not in NOISE], words(base)
        hit = next((i for i, w in enumerate(spec_words) if w in base_words), None)
        about = hit is not None
        q = pascal(" ".join(w for w in (spec_words[:hit] if about else spec_words) if w not in base_words))
        fq = pascal(" ".join(w for w in whole if w not in base_words))
        domain = pascal(use["x-domain"].split("-")[0])
        done = next((DONE[w] + base for w in whole if w in DONE), "")  # CreatedOrder, rather than OrderResponse
        if role == "Request":  # a request body object never takes the plain name of the read model
            first = [q + base + role] if q else []
            return [c for c in first + ([base + role] if about else []) + [fq + base + role, domain + base + role, base + role] if c]
        if shared:
            first = ([base] if across else []) + [domain + base]
        else:
            first = ([q + base] if q else []) + ([base] if about else [])
        return [c for c in first + [done] + ([base + role] if about else []) + [q and q + base + role, fq + base, fq + base + role, domain + base, domain + base + role, base + role, base] if c]

    def finalize(self):
        """Give every shape its name (the shapes of an operation first, then the shapes the spec is about, the object of
        an inquiry before the result of an action, then the shapes used by most specs) and return the schemas by name."""
        names, taken = {}, set(self.fixed)
        used = lambda i: len({u["x-from"] for u in self.info[i]["usages"]})
        read = lambda i: "inquiry" in self.info[i]["usages"][0]["x-from"].split("/")[-2].split("-")  # the read model takes the plain name
        order = sorted(self.info, key=lambda i: (not self.info[i]["op"], not self.about(self.info[i]["usages"][0]), not read(i), -used(i), i))
        for sid in order:
            entry = self.info[sid]
            first = entry["usages"][0]
            across = len({u["x-domain"] for u in entry["usages"]}) > 1
            cands = [first["x-name"]] if entry["op"] else self.candidates(first, used(sid) > 1, across)
            name = next((c for c in cands if c not in taken and not repeats(c)), None)
            if name is None:
                name = next(f"{cands[-1]}{n}" for n in range(2, 99) if f"{cands[-1]}{n}" not in taken)
            names[sid] = name
            taken.add(name)
        for sid, entry in self.info.items():
            for use in entry["usages"]:
                self.names.setdefault(use["x-name"], {}).setdefault(names[sid], []).append(use["x-from"])
        return {names[sid]: entry["node"] for sid, entry in self.info.items()}, names

    def apply(self, contract):
        """Replace the numbered placeholders by the names, in the paths and in the new components."""
        schemas, names = self.finalize()
        text = json.dumps({"paths": contract["paths"], "schemas": schemas})
        done = json.loads(re.sub(r"#/components/schemas/@(\d+)@", lambda m: "#/components/schemas/" + names[int(m.group(1))], text))
        contract["paths"] = done["paths"]
        contract["components"]["schemas"] = dict(sorted({**self.schemas, **done["schemas"]}.items()))


def objects(node, skip=None):
    """Every inline object with properties (not a $ref) under a schema node, never the examples."""
    if isinstance(node, dict):
        if node.get("type") == "object" and node.get("properties") and node is not skip:
            yield node
        for k, v in node.items():
            if k not in OPAQUE:
                yield from objects(v, skip)
    elif isinstance(node, list):
        for v in node:
            yield from objects(v, skip)


def reuse_report(contract):
    """Components with the same shape under two names, and inline objects that repeat a component."""
    problems, seen = [], {}
    for name, schema in contract["components"]["schemas"].items():
        if repeats(name):
            problems.append(f"component {name} says a word twice in a row")
        if name.startswith("Error") or name in ("Status", "ResponseEnvelope"):
            continue
        k = key(schema)
        if k in seen:
            problems.append(f"components {seen[k]} and {name} have the same shape")
        seen[k] = name
    shapes = {key(v): n for n, v in contract["components"]["schemas"].items()}
    for where, node in [("paths", contract["paths"])] + [(f"component {n}", v) for n, v in contract["components"]["schemas"].items()]:
        for obj in objects(node, skip=contract["components"]["schemas"].get(where.split(" ")[-1])):
            if key(obj) in shapes:
                problems.append(f"an inline object in {where} repeats component {shapes[key(obj)]}")
    return problems


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


def fit(contract, value, schema, where, problems, mark_null, strict=True):
    """Check a subset of JSON Schema; with mark_null, a null value makes its (inline) schema nullable first.
    An allOf part is checked without the undeclared-field rule, which applies to the merged properties instead."""
    if value is None and mark_null and "$ref" not in schema:
        nullable(schema)
    schema = resolve(contract, schema)
    if "anyOf" in schema:
        tries = []
        for branch in schema["anyOf"]:
            tries.append([])
            fit(contract, value, branch, where, tries[-1], False, strict)
            if not tries[-1]:
                break
        else:
            problems.extend(tries[0])
        return
    parts = [schema] + [resolve(contract, p) for p in schema.get("allOf", [])]
    for part in parts[1:]:
        fit(contract, value, part, where, problems, False, strict=False)
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
            elif strict and props and any(p.get("type") == "object" for p in parts) \
                    and not any(p.get("additionalProperties") is True for p in parts):
                problems.append(f"{where}: {name} is not in the schema")
    if isinstance(value, list) and not schema.get("minItems", 0) <= len(value) <= schema.get("maxItems", len(value)):
        problems.append(f"{where}: {len(value)} items are outside {schema.get('minItems')}..{schema.get('maxItems')}")
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


def pretty_target(argv):
    """The OUT path of `--pretty OUT`, or None. Stops before any write when OUT is missing or is the committed contract."""
    if "--pretty" not in argv:
        return None
    at = argv.index("--pretty") + 1
    if at >= len(argv):
        sys.exit("--pretty needs an output path")
    out = Path(argv[at]).resolve()
    if out == CONTRACT.resolve():
        sys.exit("--pretty must not write the committed contract (it is kept on one line, see the 1 MB preflight limit)")
    return out


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
        "security": [{"bearerAuth": []}],  # an operation that forgets its security is protected; a public one says `security: []`
        "paths": {},
        "components": components(first),
    }
    errors, skipped, order, warnings = list(first.errors), [], [], []
    for domain in domains:
        for path in sorted(API.glob(f"{domain}/*/spec.md")):
            spec = Spec(path)
            if not spec.approved:
                skipped.append(spec.rel)
                continue
            if [{k: v for k, v in r.items() if k != "Example"} for r in spec.rows("Status Object")] != status_rows:
                spec.errors.append("the Status Object differs from the shared one")
            contract["paths"].setdefault(spec.path, {})[spec.method] = operation(spec, domain)
            order.append((spec.path, spec.method))
            if spec.front_rules:
                warnings.append(f"{spec.rel}: {len(spec.front_rules)} rules of ## Domain stand in the frontmatter; the spec should move them under ## Domain")
            errors += [f"{spec.rel}: {e}" for e in spec.errors]
    contract["paths"] = {k: dict(sorted(v.items())) for k, v in sorted(contract["paths"].items())}
    check_examples(contract, mark_null=True)
    shared = Components(contract["components"])
    for path, method in order:  # in spec order, so that a new spec does not rename the components of an older one
        contract["paths"][path][method] = shared.walk(contract["paths"][path][method])
    shared.apply(contract)
    errors += check_examples(contract, mark_null=False)
    errors += reuse_report(contract)
    errors += [f"{m.upper()} {p} has no `security` (write `security: []` for a public operation)" for p, item in contract["paths"].items() for m, op in item.items() if "security" not in op]
    # one-line JSON: the indented file passes the 1 MB preflight limit (lead decision 2026-11-17)
    text = json.dumps(contract, separators=(",", ":"), ensure_ascii=False) + "\n"
    count = sum(len(v) for v in contract["paths"].values())
    pretty = pretty_target(sys.argv[1:])
    if pretty:
        pretty.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{pretty}: indented copy of {count} operations (the committed contract is unchanged)")
    elif "--check" in sys.argv[1:]:
        if text != CONTRACT.read_text(encoding="utf-8"):
            errors.append(f"{CONTRACT.relative_to(ROOT)} differs from a fresh generation; run gen_contract.py and commit the result")
        else:
            print(f"{CONTRACT.relative_to(ROOT)}: up to date ({count} operations of {len(domains)} domains)")
    else:
        CONTRACT.write_text(text, encoding="utf-8")
        print(f"{CONTRACT.relative_to(ROOT)}: {count} operations of {len(domains)} domains")
    for rel in skipped:
        print(f"skipped (not approved): {rel}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for base, used in sorted(shared.names.items()):
        if len(used) > 1:  # the same name in the specs, different shapes: for the lead's review
            print(f"collision {base}: " + "; ".join(f"{name} <- {', '.join(sorted({x.split('/api/')[1].rsplit('/', 1)[0] for x in specs}))}" for name, specs in sorted(used.items())))
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
