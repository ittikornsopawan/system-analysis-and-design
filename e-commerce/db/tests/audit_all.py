#!/usr/bin/env python3
"""Audit of every table: migrations against schema docs, README, ER diagram and the SQL inside the API specs.

Usage: python3 e-commerce/db/tests/audit_all.py
Prints one line per finding and exits 1 when there is any finding, 0 when everything agrees.
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
E = ROOT / "e-commerce"
FINDINGS = []


def finding(area: str, text: str) -> None:
    FINDINGS.append(f"[{area}] {text}")


def normalize(sql: str) -> str:
    return " ".join(sql.split())


# ------------------------------------------------------------------ migrations
def split_top(body: str) -> list[str]:
    parts, depth, cur = [], 0, ""
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur.strip())
    return parts


def parse_type(definition: str) -> tuple[str, str]:
    m = re.match(r"([A-Za-z]+(?: WITHOUT TIME ZONE)?)\s*(\(([^)]*)\))?", definition)
    base = m.group(1).replace(" WITHOUT TIME ZONE", "").upper()
    length = (m.group(3) or "").replace(" ", "")
    if base == "TIMESTAMP":
        length = ""
    return base, length


def parse_migrations():
    tables = {}
    for path in sorted((E / "db/migrations/up").glob("*.sql")):
        text = path.read_text(encoding="utf-8")
        for m in re.finditer(r"CREATE TABLE\s+IF NOT EXISTS\s+(\w+)\.(\w+)\s*\((.*?)\n    \);", text, re.DOTALL):
            schema, table, body = m.group(1), m.group(2), m.group(3)
            cols, uniques = [], []
            for part in split_top(body):
                if re.match(r"(UNIQUE|CHECK|PRIMARY|CONSTRAINT|FOREIGN)\b", part):
                    uniques.append(part)
                    continue
                name = part.split()[0]
                rest = part[len(name):].strip()
                base, length = parse_type(rest)
                nullable = not re.search(r"NOT NULL|PRIMARY KEY", rest)
                ref = re.search(r"REFERENCES\s+(\w+|\"\w+\")\.(\w+)\s*\((\w+)\)", rest)
                cols.append({"name": name, "type": base, "length": length, "nullable": nullable,
                             "ref": (ref.group(1).strip('"'), ref.group(2)) if ref else None})
            tables[f"{schema}.{table}"] = {"schema": schema, "table": table, "cols": cols, "file": path.name,
                                           "sql": normalize(m.group(0)), "table_constraints": uniques}
    return tables


def indexes_of(tables):
    result = {}
    for path in sorted((E / "db/migrations/up").glob("*.sql")):
        text = path.read_text(encoding="utf-8")
        for stmt in text.split(";"):
            s = normalize(stmt)
            m = re.match(r"CREATE (?:UNIQUE )?INDEX IF NOT EXISTS \S+ ON (\w+\.\w+) ", s)
            if m:
                result.setdefault(m.group(1), []).append(s + ";")
    return result


# ------------------------------------------------------------------ docs
DOC_TYPE_ALIASES = {"TIMESTAMP": "TIMESTAMP"}


def parse_doc_columns(md: str):
    rows = []
    in_cols = False
    for line in md.split("\n"):
        if line.startswith("## Columns"):
            in_cols = True
            continue
        if in_cols and line.startswith("## "):
            break
        if in_cols and line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 8 and cells[2] != "Column Name" and not cells[0].startswith("---"):
                rows.append({"key": cells[0], "ref": cells[1], "name": cells[2], "type": cells[3].upper(),
                             "length": cells[4].replace(" ", ""), "nullable": cells[5].upper() == "TRUE"})
    return rows


def audit_docs(tables, indexes):
    for full, t in tables.items():
        path = E / "doc/schema" / t["schema"] / f"{t['table']}.md"
        if not path.exists():
            finding("doc", f"{full}: missing {path.relative_to(ROOT)}")
            continue
        md = path.read_text(encoding="utf-8")
        body = md.split("\n---\n", 1)[1].lstrip("\n") if md.startswith("---\n") and "\n---\n" in md else md  # skip the frontmatter
        if not body.startswith(f"# Table: {full}\n"):
            finding("doc", f"{path.name}: heading is not '# Table: {full}'")
        rows = parse_doc_columns(md)
        doc_names = [r["name"] for r in rows]
        mig_names = [c["name"] for c in t["cols"]]
        if doc_names != mig_names:
            missing = [n for n in mig_names if n not in doc_names]
            extra = [n for n in doc_names if n not in mig_names]
            finding("doc", f"{full}: Columns table differs from migration (missing {missing}, extra {extra}"
                           + (", different order" if not missing and not extra else "") + ")")
        else:
            for r, c in zip(rows, t["cols"]):
                if r["type"] != c["type"] or r["length"] != c["length"]:
                    finding("doc", f"{full}.{c['name']}: doc type {r['type']}({r['length']}) vs migration {c['type']}({c['length']})")
                if r["nullable"] != c["nullable"]:
                    finding("doc", f"{full}.{c['name']}: doc nullable {r['nullable']} vs migration {c['nullable']}")
                if c["ref"] and not r["key"].startswith("FK"):
                    finding("doc", f"{full}.{c['name']}: references {c['ref'][0]}.{c['ref'][1]} but the Key is '{r['key']}'")
                if not c["ref"] and r["key"].startswith("FK"):
                    finding("doc", f"{full}.{c['name']}: Key is FK but the migration has no REFERENCES")
        # DDL block of the doc equals the migration
        blocks = " ".join(re.findall(r"```SQL[ \t]*\n(.*?)```", md, re.DOTALL))
        doc_sql = normalize(blocks)
        if t["sql"] not in doc_sql:
            finding("doc", f"{full}: SQL block differs from {t['file']}")
        for idx in indexes.get(full, []):
            if idx not in doc_sql:
                finding("doc", f"{full}: index missing in the SQL block: {idx[:70]}")
        # the other direction: every CREATE, ALTER or DROP statement of the doc must be in the migration
        allowed = {t["sql"].rstrip(";").strip()} | {i.rstrip(";").strip() for i in indexes.get(full, [])}
        for statement in blocks.split(";"):
            st = normalize(statement)
            if re.match(r"(CREATE|ALTER|DROP)\b", st) and st not in allowed:
                finding("doc", f"{full}: the SQL block has a statement that is not in the migration: {st[:70]}")
        index_names = {re.search(r"INDEX IF NOT EXISTS (\S+)", i).group(1) for i in indexes.get(full, [])}
        if "UNIQUE" not in t["sql"]:
            constraint_text = md[md.find("## Constain"):] if "## Constain" in md else ""
            for name in re.findall(r"^\| (uq_\w+) +\|", constraint_text, re.MULTILINE):
                if name not in index_names:
                    finding("doc", f"{full}: the constraint table lists {name} but the migration has no such unique")
        # relative links
        for target in re.findall(r"\]\(([^)#]+\.md)\)", md):
            if not (path.parent / target).exists():
                finding("doc", f"{path.name}: broken link {target}")


def audit_readme(tables):
    md = (E / "doc/schema/README.md").read_text(encoding="utf-8")
    m = re.search(r"(\d+) tables in (\d+) schemas", md)
    schemas = {t["schema"] for t in tables.values()}
    if not m or int(m.group(1)) != len(tables) or int(m.group(2)) != len(schemas):
        finding("readme", f"header says '{m.group(0) if m else None}' but there are {len(tables)} tables in {len(schemas)} schemas")
    listed = {}
    current = None
    for line in md.split("\n"):
        h = re.match(r"## (\w+)$", line)
        if h:
            current = h.group(1)
        r = re.match(r"\| \[(\w+)\]\(([^)]+)\) \| (\w+) \| (\d+) \| (\d+) \|", line)
        if r and current:
            listed[f"{current}.{r.group(1)}"] = (r.group(2), r.group(3), int(r.group(4)), int(r.group(5)))
    for full, t in tables.items():
        if full not in listed:
            finding("readme", f"{full} is not listed")
            continue
        link, kind, ncols, nfks = listed[full]
        if ncols != len(t["cols"]):
            finding("readme", f"{full}: README says {ncols} columns, migration has {len(t['cols'])}")
        fks = sum(1 for c in t["cols"] if c["ref"])
        if nfks != fks:
            finding("readme", f"{full}: README says {nfks} FKs, migration has {fks}")
        expected_kind = {"m": "Master", "t": "Transaction", "l": "Log"}[t["table"][0]]
        if kind != expected_kind:
            finding("readme", f"{full}: README type {kind}, name implies {expected_kind}")
        if not (E / "doc/schema" / link).exists():
            finding("readme", f"{full}: broken link {link}")
    for full in listed:
        if full not in tables:
            finding("readme", f"{full} is listed but not in the migrations")


# ------------------------------------------------------------------ ER diagram
def audit_er(tables):
    root = ET.fromstring((E / "db/er-diagram.drawio").read_text(encoding="utf-8"))
    pages = {d.get("name"): d for d in root.iter("diagram")}
    page = pages.get("7 All Tables")
    if page is None:
        finding("er", "page '7 All Tables' is missing")
        return
    cells = list(page.iter("mxCell"))
    by_id = {c.get("id"): c for c in cells}
    swim = {(c.get("value") or "").strip(): c for c in cells if c.get("vertex") == "1" and "swimlane" in (c.get("style") or "")}
    rows_of = {}
    for c in cells:
        if c.get("vertex") == "1" and c.get("parent") in by_id:
            rows_of.setdefault(c.get("parent"), []).append(c)
    title_re = re.compile(r"^\w+\.\w+$")
    diagram_tables = {k for k in swim if title_re.match(k)}
    for full in tables:
        if full not in diagram_tables:
            finding("er", f"{full} is missing on page '7 All Tables'")
    for full in diagram_tables - set(tables):
        finding("er", f"{full} is on the diagram but not in the migrations")
    edge_pairs = set()
    row_table = {}
    for tid, rows in rows_of.items():
        owner = (by_id[tid].get("value") or "").strip()
        for r in rows:
            row_table[r.get("id")] = (owner, r.get("value") or "")
    for c in cells:
        if c.get("edge") == "1" and c.get("source") in row_table and c.get("target") in row_table:
            edge_pairs.add((row_table[c.get("source")][0], row_table[c.get("source")][1].strip(),
                            row_table[c.get("target")][0]))
    for full, t in tables.items():
        if full not in swim:
            continue
        rows = [r.get("value") or "" for r in rows_of.get(swim[full].get("id"), [])]
        cols = {c["name"] for c in t["cols"]}
        for text in rows:
            m = re.match(r"(PK|FK|UK)?\s+(\w+) :", text)
            if m and m.group(2) not in cols:
                finding("er", f"{full}: diagram row '{text.strip()}' is not a column")
            elif not m and not text.startswith("UNIQUE") and text.strip():
                finding("er", f"{full}: unexpected diagram row '{text.strip()}'")
        shown = {re.match(r"(?:PK|FK|UK)?\s+(\w+) :", x).group(1) for x in rows if re.match(r"(?:PK|FK|UK)?\s+(\w+) :", x)}
        for col in t["cols"]:
            if col["name"] in ("created_by", "created_at", "updated_by", "updated_at", "row_status"):
                continue
            if col["name"] not in shown:
                finding("er", f"{full}: column {col['name']} is not drawn")
            if col["ref"]:
                parent = f"{col['ref'][0]}.{col['ref'][1]}"
                if not any(p[0] == full and p[1].split(":")[0].split()[-1] == col["name"] and p[2] == parent for p in edge_pairs):
                    finding("er", f"{full}.{col['name']}: no FK edge to {parent}")


def audit_er_pages(tables):
    """Every table drawn on any page must only show real columns (the audit of page 7 covers the FK edges)."""
    root = ET.fromstring((E / "db/er-diagram.drawio").read_text(encoding="utf-8"))
    for page in root.iter("diagram"):
        cells = list(page.iter("mxCell"))
        by_id = {c.get("id"): c for c in cells}
        for c in cells:
            title = (c.get("value") or "").strip()
            if c.get("vertex") == "1" and "swimlane" in (c.get("style") or "") and title in tables:
                cols = {x["name"] for x in tables[title]["cols"]}
                for r in cells:
                    if r.get("vertex") == "1" and r.get("parent") == c.get("id"):
                        m = re.match(r"(?:PK|FK|UK)?\s+(\w+) :", r.get("value") or "")
                        if m and m.group(1) not in cols:
                            finding("er", f"page '{page.get('name')}': {title} row '{(r.get('value') or '').strip()}' is not a column")


# ------------------------------------------------------------------ SQL inside the specs
def audit_specs(tables):
    cols_of = {full: {c["name"] for c in t["cols"]} for full, t in tables.items()}
    for path in sorted((E / "doc/api").rglob("spec.md")):
        md = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)
        for block in re.findall(r"```SQL[ \t]*\n(.*?)```", md, re.DOTALL):
            sql = re.sub(r"--[^\n]*", "", block)
            aliases = {}
            for m in re.finditer(r'\b(?:FROM|JOIN|UPDATE|INTO)\s+"?(\w+)"?\.(\w+)(?:\s+(?:AS\s+)?(?!ON\b|SET\b|WHERE\b|INNER\b|LEFT\b|JOIN\b|AND\b|VALUES\b)(\w+))?', sql):
                full = f"{m.group(1)}.{m.group(2)}"
                if full not in tables:
                    finding("spec", f"{rel}: unknown table {full}")
                    continue
                aliases[m.group(3) or m.group(2)] = full
                aliases[full] = full
            for m in re.finditer(r"\b(\w+)\.(\w+)\b", sql):
                alias, col = m.group(1), m.group(2)
                if alias in aliases and col not in cols_of[aliases[alias]] and not re.match(r"\w+\.\w+", f"{alias}.{col}") is None:
                    if aliases[alias] == f"{alias}.{col}":
                        continue
                    finding("spec", f"{rel}: {alias}.{col} is not a column of {aliases[alias]}")
            # INSERT INTO schema.table (cols)
            for m in re.finditer(r"INSERT INTO\s+\"?(\w+)\"?\.(\w+)\s*\(([^)]*)\)", sql):
                full = f"{m.group(1)}.{m.group(2)}"
                if full in tables:
                    for col in [c.strip() for c in m.group(3).split(",") if c.strip()]:
                        if col not in cols_of[full]:
                            finding("spec", f"{rel}: INSERT INTO {full} column {col} does not exist")
            # UPDATE schema.table SET col = ...
            for m in re.finditer(r"UPDATE\s+\"?(\w+)\"?\.(\w+)\s+SET\s+(.*?)\bWHERE\b", sql, re.DOTALL):
                full = f"{m.group(1)}.{m.group(2)}"
                if full in tables:
                    for col in re.findall(r"^\s*(\w+)\s*=", m.group(3), re.MULTILINE):
                        if col not in cols_of[full]:
                            finding("spec", f"{rel}: UPDATE {full} SET {col} - not a column")
        for target in re.findall(r"\]\((\.\./[^)#]+)", md):
            if not (path.parent / target).exists():
                finding("spec", f"{rel}: broken link {target}")


def main() -> int:
    tables = parse_migrations()
    indexes = indexes_of(tables)
    audit_docs(tables, indexes)
    audit_readme(tables)
    audit_er(tables)
    audit_er_pages(tables)
    audit_specs(tables)
    for f in FINDINGS:
        print(f)
    print(f"{len(tables)} tables audited, {len(FINDINGS)} findings")
    return 1 if FINDINGS else 0


if __name__ == "__main__":
    sys.exit(main())
