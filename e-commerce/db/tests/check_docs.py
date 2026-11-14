#!/usr/bin/env python3
"""Shared checker for the multi-level product SKU docs.

Subcommands (schema, er, spec01, spec02, spec03) are added by later tasks.
Each subcommand returns exit code 0 on pass and prints "FAIL: <reason>" on fail.
"""
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

JSON_BLOCK = re.compile(r"```JSON[ \t]*\n(.*?)```", re.DOTALL)

COMMANDS = {}


def table_lines_aligned(md: str) -> list[str]:
    """Return the tables whose lines do not all have the same length.

    A table is a run of consecutive lines starting with "|". Each result is the
    first line of the offending table (its header row).
    """
    bad = []
    table = []
    for line in md.split("\n") + [""]:
        if line.startswith("|"):
            table.append(line)
            continue
        if table and len({len(row) for row in table}) > 1:
            bad.append(table[0])
        table = []
    return bad


def json_blocks_parse(md: str) -> list[str]:
    """Return the ```JSON blocks that json.loads cannot parse.

    Blocks whose text starts with "curl" are skipped: the existing specs fence
    their cUrl example inside a ```JSON block.
    """
    bad = []
    for match in JSON_BLOCK.finditer(md):
        block = match.group(1)
        if block.strip().startswith("curl"):
            continue
        try:
            json.loads(block)
        except ValueError:
            bad.append(block)
    return bad


def require(md: str, needles: list[str]) -> list[str]:
    """Return the needles that are missing from md."""
    return [needle for needle in needles if needle not in md]


def read(path: str) -> str:
    """Read a repo-relative file as UTF-8 text."""
    return (ROOT / path).read_text(encoding="utf-8")

def missing_apart(spec_md: str, sequence_md: str, needles: list[str], moved: list[str]) -> list[str]:
    """Needles in the spec, except the rules that moved into a note of the sequence diagram, which are searched in the sequence only (one line per wrapped note)."""
    flat = re.sub(r"\n\s+", " ", sequence_md)
    return missing_needles(spec_md, [n for n in needles if n not in moved]) + missing_needles(flat, moved)

def without_frontmatter(md: str) -> str:
    """The Markdown after its YAML frontmatter (the whole text when there is none)."""
    return md.split("\n---\n", 1)[1].lstrip("\n") if md.startswith("---\n") and "\n---\n" in md else md


def fail(reason: str) -> int:
    print(f"FAIL: {reason}")
    return 1

SCHEMA_DIR = "e-commerce/doc/schema/product"
MIGRATION = "e-commerce/db/migrations/up/03-product.schema.up.sql"
NEW_TABLES = ["m_product_option", "m_product_option_value", "m_product_sku_option_value"]
SQL_BLOCK = re.compile(r"```SQL[ \t]*\n(.*?)```", re.DOTALL)


def normalize(sql: str) -> str:
    return " ".join(sql.split())


def table_statements(sql: str, table: str) -> list[str]:
    """Return the normalized CREATE TABLE / CREATE UNIQUE INDEX statements of one table."""
    found = []
    for statement in sql.split(";"):
        text = normalize(statement)
        if re.search(rf"^CREATE TABLE IF NOT EXISTS product\.{table} \(", text) or re.search(
            rf"^CREATE UNIQUE INDEX IF NOT EXISTS \S+ ON product\.{table} \(", text
        ):
            found.append(text)
    return found


def column_row(md: str, column: str) -> bool:
    return re.search(rf"^\|[^\n]*\| {column} +\|", md, re.MULTILINE) is not None


def check_schema() -> int:
    errors = []
    migration = read(MIGRATION)
    for table in NEW_TABLES:
        path = f"{SCHEMA_DIR}/{table}.md"
        try:
            md = read(path)
        except FileNotFoundError:
            errors.append(f"{path} does not exist")
            continue
        if not without_frontmatter(md).startswith(f"# Table: product.{table}\n"):
            errors.append(f"{path} missing heading '# Table: product.{table}'")
    extra = {"m_product_sku": "combination_key", "m_product_image": "option_value_id"}
    for table in NEW_TABLES + list(extra):
        path = f"{SCHEMA_DIR}/{table}.md"
        try:
            md = read(path)
        except FileNotFoundError:
            continue
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        column = extra.get(table)
        blocks = SQL_BLOCK.findall(md)
        if column:
            if not column_row(md, column):
                errors.append(f"{path} Columns table missing {column}")
            if not any(column in block for block in blocks):
                errors.append(f"{path} SQL block missing {column}")
        doc_sql = normalize(" ".join(blocks))
        doc_statements = table_statements(" ".join(blocks), table)
        expected = table_statements(migration, table)
        if not expected:
            errors.append(f"{table} not found in migration")
        elif doc_statements != expected:
            errors.append(f"{path} SQL differs from {MIGRATION}")
        elif doc_sql.count("CREATE ") != len(expected):
            errors.append(f"{path} SQL block has statements not in the migration")
    readme = read("e-commerce/doc/schema/README.md")
    needles = [
        "53 tables in 11 schemas",
        "| [m_product_option](product/m_product_option.md) | Master | 9 | 1 |",
        "| [m_product_option_value](product/m_product_option_value.md) | Master | 9 | 1 |",
        "| [m_product_sku_option_value](product/m_product_sku_option_value.md) | Master | 8 | 2 |",
        "| [m_product_sku](product/m_product_sku.md) | Master | 10 | 1 |",
        "| [m_product_image](product/m_product_image.md) | Master | 9 | 2 |",
    ]
    for missing in require(readme, needles):
        errors.append(f"README.md missing: {missing}")
    if errors:
        return fail("; ".join(errors))
    print("OK: schema")
    return 0


COMMANDS["schema"] = check_schema


def schema_statements(sql: str, schema: str, table: str) -> list[str]:
    """CREATE TABLE / CREATE UNIQUE INDEX statements (normalized) of one table of any schema."""
    found = []
    for statement in sql.split(";"):
        text = normalize(statement)
        if re.search(rf"^CREATE TABLE IF NOT EXISTS {schema}\.{table} \(", text) or re.search(
            rf"^CREATE UNIQUE INDEX IF NOT EXISTS \S+ ON {schema}\.{table} \(", text
        ):
            found.append(text)
    return found


LOT_MOVED_COLUMNS = ["cost_price", "selling_price", "gross_margin", "share_margin", "platform_margin", "quantity"]


def check_shop_schema() -> int:
    """Lots of a shop product SKU: migration 04/06 against the schema docs and README."""
    errors = []
    migrations = {
        "shop": read("e-commerce/db/migrations/up/04-shop.schema.up.sql"),
        "sales": read("e-commerce/db/migrations/up/06-sales.schema.up.sql"),
    }
    docs = [
        ("shop", "t_shop_product_sku_lot", "e-commerce/doc/schema/shop/t_shop_product_sku_lot.md"),
        ("shop", "t_shop_product_sku", "e-commerce/doc/schema/shop/t_shop_product_sku.md"),
        ("sales", "t_order_item", "e-commerce/doc/schema/sales/t_order_item.md"),
    ]
    for schema, table, path in docs:
        try:
            md = read(path)
        except FileNotFoundError:
            errors.append(f"{path} does not exist")
            continue
        if not without_frontmatter(md).startswith(f"# Table: {schema}.{table}\n"):
            errors.append(f"{path} missing heading '# Table: {schema}.{table}'")
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        blocks = " ".join(SQL_BLOCK.findall(md))
        expected = schema_statements(migrations[schema], schema, table)
        if not expected:
            errors.append(f"{schema}.{table} not found in the migration")
        elif schema_statements(blocks, schema, table) != expected:
            errors.append(f"{path} SQL differs from the migration")
        elif normalize(blocks).count("CREATE ") != len(expected):
            errors.append(f"{path} SQL block has statements not in the migration")
        if table == "t_shop_product_sku":
            for column in LOT_MOVED_COLUMNS:
                if column_row(md, column):
                    errors.append(f"{path} still lists moved column {column}")
        if table == "t_order_item" and not column_row(md, "lot_id"):
            errors.append(f"{path} Columns table missing lot_id")
        if table == "t_shop_product_sku_lot":
            for column in ["shop_product_sku_id", "lot_no", "cost_price", "selling_price", "quantity", "is_on_sale"]:
                if not column_row(md, column):
                    errors.append(f"{path} Columns table missing {column}")
    readme = read("e-commerce/doc/schema/README.md")
    needles = [
        "| [t_shop_product_sku](shop/t_shop_product_sku.md) | Transaction | 11 | 2 |",
        "| [t_shop_product_sku_lot](shop/t_shop_product_sku_lot.md) | Transaction | 15 | 1 |",
        "| [t_order_item](sales/t_order_item.md) | Transaction | 18 | 5 |",
    ]
    for missing in require(readme, needles):
        errors.append(f"README.md missing: {missing}")
    if errors:
        return fail("; ".join(errors))
    print("OK: shop-schema")
    return 0


COMMANDS["shop-schema"] = check_shop_schema


DIAGRAM = "e-commerce/db/er-diagram.drawio"
ER_PAGES = ["3 Product", "7 All Tables"]
ER_NEW_TABLES = [
    "product.m_product_option",
    "product.m_product_option_value",
    "product.m_product_sku_option_value",
]
ER_EXTRA_ROWS = {
    "product.m_product_image": "option_value_id : uuid",
    "product.m_product_sku": "combination_key : text",
}
# (child table, parent table) FK edges the new tables need on each page
ER_EDGES = [
    ("product.m_product_option", "product.m_product"),
    ("product.m_product_option_value", "product.m_product_option"),
    ("product.m_product_sku_option_value", "product.m_product_sku"),
    ("product.m_product_sku_option_value", "product.m_product_option_value"),
    ("product.m_product_image", "product.m_product_option_value"),
]
ER_HEADER = 28
ER_ROW = 22


def er_cells(page) -> list:
    return list(page.iter("mxCell"))


def er_rect(cell) -> tuple:
    geo = cell.find("mxGeometry")
    return tuple(float(geo.get(key, 0)) for key in ("x", "y", "width", "height"))


def er_overlaps(a: tuple, b: tuple) -> bool:
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


def check_er_page(page, prefixes=("product.",), new_tables=None, extra_rows=None, edges=None) -> list[str]:
    new_tables = ER_NEW_TABLES if new_tables is None else new_tables
    extra_rows = ER_EXTRA_ROWS if extra_rows is None else extra_rows
    edges = ER_EDGES if edges is None else edges
    name = page.get("name")
    errors = []
    cells = er_cells(page)
    ids = [cell.get("id") for cell in cells]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        errors.append(f"[{name}] duplicate id {dup}")
    by_id = {cell.get("id"): cell for cell in cells}

    swimlanes = [c for c in cells if c.get("vertex") == "1" and "swimlane" in (c.get("style") or "")]
    tables = {}
    for cell in swimlanes:
        title = (cell.get("value") or "").strip()
        if title.startswith(prefixes):
            tables[title] = cell
    rows_of = {}
    for cell in cells:
        if cell.get("vertex") == "1" and cell.get("parent") in {t.get("id") for t in tables.values()}:
            rows_of.setdefault(cell.get("parent"), []).append(cell)

    for title in new_tables:
        if title not in tables:
            errors.append(f"[{name}] missing table {title}")
    for title, needle in extra_rows.items():
        table = tables.get(title)
        values = [r.get("value") or "" for r in rows_of.get(table.get("id") if table is not None else None, [])]
        if not any(needle in value for value in values):
            errors.append(f"[{name}] {title} missing row '{needle}'")

    for title, table in tables.items():
        rows = rows_of.get(table.get("id"), [])
        expected = ER_HEADER + ER_ROW * len(rows)
        if rows and er_rect(table)[3] != expected:
            errors.append(f"[{name}] {title} height {er_rect(table)[3]:g} != {expected}")

    groups = {}
    for cell in swimlanes:
        groups.setdefault(cell.get("parent"), []).append(cell)
    for parent, group in groups.items():
        for i, first in enumerate(group):
            for second in group[i + 1 :]:
                if er_overlaps(er_rect(first), er_rect(second)):
                    errors.append(
                        f"[{name}] overlap: {first.get('value')} / {second.get('value')}"
                    )
        container = by_id.get(parent)
        if container is not None and parent != "1":
            width, height = er_rect(container)[2:]
            for cell in group:
                x, y, w, h = er_rect(cell)
                if x < 0 or y < 0 or x + w > width or y + h > height:
                    errors.append(f"[{name}] {cell.get('value')} sticks out of {container.get('value')}")

    table_of_row = {}
    for table_id, rows in rows_of.items():
        for row in rows:
            table_of_row[row.get("id")] = by_id[table_id].get("value")
    pairs = set()
    for cell in cells:
        if cell.get("edge") != "1":
            continue
        for end in ("source", "target"):
            ref = cell.get(end)
            if ref is not None and ref not in by_id:
                errors.append(f"[{name}] edge {cell.get('id')} {end} {ref} does not exist")
        source, target = cell.get("source"), cell.get("target")
        if source in table_of_row and target in table_of_row:
            if (by_id[source].get("value") or "").startswith("FK"):
                pairs.add((table_of_row[source], table_of_row[target]))
    for child, parent in edges:
        if (child, parent) not in pairs:
            errors.append(f"[{name}] missing FK edge {child} -> {parent}")
    return errors


def check_er() -> int:
    import xml.etree.ElementTree as ET

    try:
        root = ET.fromstring(read(DIAGRAM))
    except ET.ParseError as exc:
        return fail(f"{DIAGRAM} is not well-formed XML: {exc}")
    pages = {d.get("name"): d for d in root.iter("diagram")}
    errors = []
    for name in ER_PAGES:
        if name not in pages:
            errors.append(f"missing page {name}")
            continue
        errors.extend(check_er_page(pages[name]))
    if errors:
        return fail("; ".join(errors))
    print("OK: er")
    return 0


COMMANDS["er"] = check_er


ER_LOT_PAGES = {
    "4 Shop": (["shop.t_shop_product_sku_lot"], {}, [("shop.t_shop_product_sku_lot", "shop.t_shop_product_sku")]),
    "5 Order · Pay · Ship": ([], {"sales.t_order_item": "lot_id : uuid"}, []),
    "7 All Tables": (
        ["shop.t_shop_product_sku_lot"],
        {"sales.t_order_item": "lot_id : uuid"},
        [
            ("shop.t_shop_product_sku_lot", "shop.t_shop_product_sku"),
            ("sales.t_order_item", "shop.t_shop_product_sku_lot"),
        ],
    ),
}
ER_LOT_MOVED = ["cost_price", "selling_price", "gross_margin", "share_margin", "platform_margin", "quantity"]


def check_er_lot() -> int:
    import xml.etree.ElementTree as ET

    try:
        root = ET.fromstring(read(DIAGRAM))
    except ET.ParseError as exc:
        return fail(f"{DIAGRAM} is not well-formed XML: {exc}")
    pages = {d.get("name"): d for d in root.iter("diagram")}
    errors = []
    for name, (new_tables, rows, edges) in ER_LOT_PAGES.items():
        if name not in pages:
            errors.append(f"missing page {name}")
            continue
        errors.extend(check_er_page(pages[name], ("shop.", "sales."), new_tables, rows, edges))
        if name in ("4 Shop", "7 All Tables"):
            cells = list(pages[name].iter("mxCell"))
            sku = [c for c in cells if (c.get("value") or "") == "shop.t_shop_product_sku" and "swimlane" in (c.get("style") or "")]
            if not sku:
                errors.append(f"[{name}] missing shop.t_shop_product_sku")
            else:
                sku_id = sku[0].get("id")
                for cell in cells:
                    if cell.get("parent") == sku_id:
                        for column in ER_LOT_MOVED:
                            if f"{column} :" in (cell.get("value") or ""):
                                errors.append(f"[{name}] shop.t_shop_product_sku still has row {column}")
    if errors:
        return fail("; ".join(errors))
    print("OK: er-lot")
    return 0


COMMANDS["er-lot"] = check_er_lot


SPEC01 = "e-commerce/doc/api/product/01-upsert-product/spec.md"
# Heading needles (start with "#") must match a whole line, text needles are substrings.
SPEC01_NEEDLES = [
    "#### Option Object",
    "#### Value Object",
    "#### Value Image Object",
    "Adding a value or reopening a value generates the SKU combinations that are missing.",
    "Options must not contain more than 3 levels.",
    "SKU count exceeds the maximum of 500.",
    "Product options cannot be changed because SKUs are used.",
    "Product option not found.",
    "Product option value not found.",
    "options[0]: Row status must be ACTIVE or DELETED.",
    "options[0].values[1]: Value is duplicated with options[0].values[0].",
    "#### Fail - Bad Request Option Status",
    "#### Fail - Bad Request Value Duplicate",
    "#### INSERT - Create product option",
    "#### INSERT - Create product SKU",
    "#### INSERT - Create product SKU option value",
    "#### UPDATE - Close product SKUs of closed option values",
    "#### UPDATE - Close product SKUs of deleted option values",
    "#### UPDATE - Delete product options that are not in the list",
    "#### UPDATE - Delete product option values that are not in the list",
    "#### UPDATE - Delete product option values of deleted options",
    "#### UPDATE - Delete product images of deleted option values",
    "#### UPDATE - Set temporary names for renamed product options",
    "#### UPDATE - Set temporary names for renamed product option values",
    "#### UPDATE - Rename product SKUs of renamed option values",
    "#### UPDATE - Rename default product SKU",
    'sales.t_order_item',
]
SPEC01_FORBIDDEN = ["#### QUERY - Count active option values per level"]


def missing_needles(md: str, needles: list[str]) -> list[str]:
    lines = set(md.split("\n"))
    return [n for n in needles if (n not in lines if n.startswith("#") else n not in md)]


def require_absent(md: str, needles: list[str]) -> list[str]:
    """Return the needles that are present in md."""
    return [needle for needle in needles if needle in md]


def section(md: str, start: str, end: str) -> str:
    """Return the text between the start heading and the next end heading."""
    head = md.find(start)
    if head < 0:
        return ""
    tail = md.find(end, head + len(start))
    return md[head : tail if tail >= 0 else len(md)]


def check_spec01() -> int:
    errors = []
    md = read(SPEC01)
    for bad in table_lines_aligned(md):
        errors.append(f"misaligned table: {bad[:40]}")
    for bad in json_blocks_parse(md):
        errors.append(f"invalid JSON block: {bad[:40]!r}")
    for missing in missing_needles(md, SPEC01_NEEDLES):
        errors.append(f"missing: {missing}")
    for present in require_absent(md, SPEC01_FORBIDDEN):
        errors.append(f"must be removed: {present}")
    body = section(md, "### Body Parameters", "#### Example Body Parameters")
    if "sortOrder" in body:
        errors.append("sortOrder must not be in the Body Parameters tables")
    insert = section(md, "##### Insert", "##### Update")
    blocks = JSON_BLOCK.findall(insert)
    for name, end in (("##### Update", "##### Delete"), ("##### Delete", "## Example Request")):
        example = JSON_BLOCK.findall(section(md, name, end))
        if not example:
            errors.append(f"missing {name} example")
            continue
        try:
            data = json.loads(example[0])
        except ValueError:
            continue
        if name == "##### Update" and not any(
            value.get("rowStatus") == "DELETED"
            for option in data.get("options", [])
            for value in option.get("values", [])
        ):
            errors.append("Update example must delete an option value")
        if name == "##### Delete" and (data.get("rowStatus") != "DELETED" or "options" in data):
            errors.append("Delete example must have rowStatus DELETED and no options")
    try:
        options = json.loads(blocks[0])["options"]
        names = [option["name"] for option in options]
        if names != ["ลาย", "ไซส์", "สี"]:
            errors.append(f"Insert example option levels must be ลาย, ไซส์, สี but are {names}")
    except (IndexError, KeyError, ValueError):
        errors.append("Insert example has no parsable options")
    if errors:
        return fail("; ".join(errors))
    print("OK: spec01")
    return 0


COMMANDS["spec01"] = check_spec01


SPEC02 = "e-commerce/doc/api/product/02-inquiry-product/spec.md"
SPEC02_NEEDLES = [
    "#### Option Object",
    "#### Option Value Object",
    "#### Option Value Image Object",
    "#### SKU Object",
    "levelNo",
    "optionValueIds",
    "combinationKey",
    "data.items[].options[].values[].images[].imagePath",
    "data.items[].skus[].optionValueIds",
    "Image shown for a selection is the image of the lowest level selected value that has an image, otherwise the product level images",
    "### Table: [product.m_product_option](../../../schema/product/m_product_option.md)",
    "### Table: [product.m_product_option_value](../../../schema/product/m_product_option_value.md)",
    "### Table: [product.m_product_sku](../../../schema/product/m_product_sku.md)",
    "### Table: [product.m_product_sku_option_value](../../../schema/product/m_product_sku_option_value.md)",
    "#### QUERY - Get product options",
    "#### QUERY - Get product option values",
    "#### QUERY - Get product option value images",
    "#### QUERY - Get product SKUs",
    "#### QUERY - Get product SKU option values",
    "AND po.row_status = 'ACTIVE'",
    "ORDER BY po.level_no",
    "ORDER BY pov.sort_order",
    "AND ps.row_status <> 'DELETED'",
]
# Shop domain data must never be returned by the inquiry (case insensitive).
SPEC02_FORBIDDEN = ["price", "quantity", "sellingprice"]


def check_spec02_examples(md: str) -> list[str]:
    """Check that every example response is consistent with the SKU rules."""
    errors = []
    seen_levels = seen_default = False
    for block in JSON_BLOCK.findall(md):
        if block.strip().startswith("curl"):
            continue
        try:
            data = json.loads(block)
        except ValueError:
            continue
        for item in data.get("data", {}).get("items", []):
            name = item.get("name")
            if "options" not in item or "skus" not in item:
                errors.append(f"{name}: options and skus are required")
                continue
            options, skus = item["options"], item["skus"]
            for key in ("price", "quantity", "sellingPrice"):
                if key in item:
                    errors.append(f"{name}: {key} must not be returned")
            if [o["levelNo"] for o in options] != list(range(1, len(options) + 1)):
                errors.append(f"{name}: levelNo must be 1..n in order")
            if not options:
                seen_default = True
                if len(skus) != 1 or skus[0].get("combinationKey") != "" or skus[0].get("optionValueIds") != []:
                    errors.append(f"{name}: no option product needs 1 default SKU with empty key")
                continue
            seen_levels = seen_levels or [o["name"] for o in options] == ["ลาย", "ไซส์", "สี"]
            value_ids = [[v["valueId"] for v in o["values"]] for o in options]
            expected = 1
            for ids in value_ids:
                expected *= len(ids)
            if len(skus) != expected:
                errors.append(f"{name}: expected {expected} SKUs but found {len(skus)}")
            combos = set()
            for sku in skus:
                ids = sku["optionValueIds"]
                if sku["combinationKey"] != "-".join(ids):
                    errors.append(f"{name}: combinationKey of {sku['skuId']} must join optionValueIds")
                if len(ids) != len(options) or any(i not in value_ids[n] for n, i in enumerate(ids) if n < len(options)):
                    errors.append(f"{name}: optionValueIds of {sku['skuId']} must follow the level order")
                combos.add(tuple(ids))
            if len(combos) != len(skus):
                errors.append(f"{name}: SKU combinations are duplicated")
    if not seen_levels:
        errors.append("an example needs the 3 levels ลาย, ไซส์, สี")
    if not seen_default:
        errors.append("an example needs a product without options")
    return errors


def check_spec02() -> int:
    errors = []
    md = read(SPEC02)
    for bad in table_lines_aligned(md):
        errors.append(f"misaligned table: {bad[:40]}")
    for bad in json_blocks_parse(md):
        errors.append(f"invalid JSON block: {bad[:40]!r}")
    for missing in missing_needles(md, SPEC02_NEEDLES):
        errors.append(f"missing: {missing}")
    for present in require_absent(md.lower(), SPEC02_FORBIDDEN):
        errors.append(f"must not appear: {present}")
    product_images = section(md, "#### QUERY - Get product images", "#### QUERY - Get product option value images")
    if "pi.option_value_id IS NULL" not in product_images:
        errors.append("product image SQL needs pi.option_value_id IS NULL")
    value_images = section(md, "#### QUERY - Get product option value images", "### Table:")
    if "pi.option_value_id IN" not in value_images or "pi.row_status = 'ACTIVE'" not in value_images:
        errors.append("value image SQL needs pi.option_value_id IN and pi.row_status = 'ACTIVE'")
    sku_values = section(md, "#### QUERY - Get product SKU option values", "### Table:")
    if "m_product_option po" not in sku_values or "ORDER BY" not in sku_values or "po.level_no" not in sku_values:
        errors.append("SKU option value SQL must join m_product_option and order by po.level_no")
    errors.extend(check_spec02_examples(md))
    if errors:
        return fail("; ".join(errors))
    print("OK: spec02")
    return 0


COMMANDS["spec02"] = check_spec02


SPEC03 = "e-commerce/doc/api/product/03-upsert-product-batch/spec.md"
SPEC03_NEEDLES = [
    "#### Option Object",
    "#### Value Object",
    "#### Value Image Object",
    "Adding a value or reopening a value generates the SKU combinations that are missing.",
    "[Array of Option](#option-object)",
    "products[0]: Options must not contain more than 3 levels.",
    "products[1]: SKU count exceeds the maximum of 500.",
    "products[1]: Product options cannot be changed because SKUs are used.",
    "products[0].options[0]: Product option not found.",
    "products[0].options[0].values[0]: Product option value not found.",
    "products[0].options[0]: Row status must be ACTIVE or DELETED.",
    "products[0].options[1]: Name is duplicated with products[0].options[0].",
    "products[0].options[0].values[1]: Value is duplicated with products[0].options[0].values[0].",
    "#### Fail - Bad Request Option Status",
    "#### Fail - Bad Request Value Duplicate",
    "#### INSERT - Create product option",
    "#### INSERT - Create product SKU",
    "#### INSERT - Create product SKU option value",
    "#### UPDATE - Close product SKUs of closed option values",
    "#### UPDATE - Close product SKUs of deleted option values",
    "#### UPDATE - Delete product options that are not in the list",
    "#### UPDATE - Delete product option values that are not in the list",
    "#### UPDATE - Delete product option values of deleted options",
    "#### UPDATE - Delete product images of deleted option values",
    "#### UPDATE - Set temporary names for renamed product options",
    "#### UPDATE - Set temporary names for renamed product option values",
    "#### UPDATE - Rename product SKUs of renamed option values",
    "#### UPDATE - Rename default product SKU",
    'sales.t_order_item',
    "sequence.products.options",
    "sequence.products.options.values.images",
    "sequence.products.images",
]
SPEC03_FORBIDDEN = ["#### QUERY - Count active option values per level"]
SPEC03_UNPREFIXED_PLACEHOLDER = re.compile(r"<sequence\.(options|images|attributes|skus)\b")
SPEC03_UNPREFIXED_OK = {"Products must contain 1 to 100 items."}


def spec03_body(md: str):
    """Return the parsed Example Body Parameters JSON, or None."""
    blocks = JSON_BLOCK.findall(section(md, "#### Example Body Parameters", "## Example Request"))
    try:
        return json.loads(blocks[0])
    except (IndexError, ValueError):
        return None


def check_spec03_products(data) -> list[str]:
    """Check the example products: insert 3 levels, complete update, delete."""
    errors = []
    products = data.get("products", [])
    if not 1 <= len(products) <= 100:
        errors.append("example must contain 1 to 100 products")
    ids = [p["id"] for p in products if "id" in p]
    if len(ids) != len(set(ids)):
        errors.append("product ids are duplicated in the example")
    seen_insert = seen_update = seen_delete = False
    for index, product in enumerate(products):
        label = f"products[{index}]"
        options = product.get("options")
        if product.get("rowStatus") == "DELETED":
            seen_delete = True
            if "id" not in product or options is not None:
                errors.append(f"{label}: delete example needs an id and no options")
            continue
        if options is None:
            continue
        if len(options) > 3:
            errors.append(f"{label}: more than 3 levels")
        names = [o.get("name") for o in options]
        if len(names) != len(set(names)):
            errors.append(f"{label}: option names are duplicated")
        for n, option in enumerate(options):
            if not [v for v in option.get("values", []) if v.get("rowStatus") != "DELETED"]:
                errors.append(f"{label}.options[{n}]: needs at least 1 value")
            values = [v.get("value") for v in option.get("values", [])]
            if len(values) != len(set(values)):
                errors.append(f"{label}.options[{n}]: values are duplicated")
        if "id" not in product:
            seen_insert = seen_insert or names == ["ลาย", "ไซส์", "สี"]
            has_id = [o for o in options if "id" in o] + [
                v for o in options for v in o.get("values", []) if "id" in v
            ]
            if has_id:
                errors.append(f"{label}: insert example options and values must not have ids")
        else:
            # R6: update lists the complete definition, every existing item has its id and one value is added
            if any("id" not in o for o in options):
                errors.append(f"{label}: update example must list every existing option with its id")
            new_values = [v for o in options for v in o.get("values", []) if "id" not in v]
            old_values = [v for o in options for v in o.get("values", []) if "id" in v]
            if len(new_values) != 1 or not old_values:
                errors.append(f"{label}: update example must add exactly 1 value and list every existing value")
            seen_update = seen_update or (len(new_values) == 1 and any("id" in o for o in options))
    if not seen_insert:
        errors.append("an insert product needs the 3 levels ลาย, ไซส์, สี")
    if not seen_update:
        errors.append("an update product needs to add a value and list the complete options")
    if not seen_delete:
        errors.append("a delete product (rowStatus DELETED, no options) is required")
    return errors


def check_spec03_requests(md: str, data) -> list[str]:
    """The HTTP and cUrl bodies must equal the Example Body Parameters."""
    errors = []
    http = re.search(r"```HTTP[ \t]*\n(.*?)```", section(md, "### HTTP Request", "### cUrl Request"), re.DOTALL)
    try:
        if json.loads(http.group(1).split("\n\n", 1)[1]) != data:
            errors.append("HTTP request body differs from Example Body Parameters")
    except (AttributeError, IndexError, ValueError):
        errors.append("HTTP request body is missing or not valid JSON")
    curl = re.search(r"--data-raw '(.*)'\n```", section(md, "### cUrl Request", "## Response Parameters"), re.DOTALL)
    try:
        if json.loads(curl.group(1)) != data:
            errors.append("cUrl request body differs from Example Body Parameters")
    except (AttributeError, ValueError):
        errors.append("cUrl request body is missing or not valid JSON")
    return errors


def check_spec03_errors(md: str) -> list[str]:
    """Every error message must name the failing product (position prefix)."""
    errors = []
    for block in JSON_BLOCK.findall(md):
        try:
            status = json.loads(block).get("status", {})
        except (ValueError, AttributeError):
            continue
        message = status.get("bizMessage", "")
        if status.get("code") in (400, 404, 409) and not message.startswith("products[") and message not in SPEC03_UNPREFIXED_OK:
            errors.append(f"error message needs a products[n] prefix: {message[:50]}")
    return errors


def check_spec03() -> int:
    errors = []
    md = read(SPEC03)
    for bad in table_lines_aligned(md):
        errors.append(f"misaligned table: {bad[:40]}")
    for bad in json_blocks_parse(md):
        errors.append(f"invalid JSON block: {bad[:40]!r}")
    for missing in missing_needles(md, SPEC03_NEEDLES):
        errors.append(f"missing: {missing}")
    for present in require_absent(md, SPEC03_FORBIDDEN):
        errors.append(f"must be removed: {present}")
    for match in SPEC03_UNPREFIXED_PLACEHOLDER.finditer(md):
        errors.append(f"placeholder needs the sequence.products prefix: {match.group(0)}")
    body = section(md, "### Body Parameters", "#### Example Body Parameters")
    if "sortOrder" in body:
        errors.append("sortOrder must not be in the Body Parameters tables")
    product_images = section(md, "#### QUERY - Check existing product images", "#### INSERT - Create product image")
    if "pi.option_value_id IS NULL" not in product_images:
        errors.append("product image check needs pi.option_value_id IS NULL")
    image_update = section(md, "#### UPDATE - Update or delete product image", "#### UPDATE - Update or delete product option value image")
    if "option_value_id IS NULL" not in image_update:
        errors.append("product image update needs option_value_id IS NULL")
    errors.extend(check_spec03_errors(md))
    data = spec03_body(md)
    if data is None:
        errors.append("Example Body Parameters has no parsable JSON")
    else:
        errors.extend(check_spec03_products(data))
        errors.extend(check_spec03_requests(md, data))
    if errors:
        return fail("; ".join(errors))
    print("OK: spec03")
    return 0


COMMANDS["spec03"] = check_spec03


# ---------------------------------------------------------------- HTTP status of every upsert spec
SINGLE_UPSERT_SPECS = [
    "e-commerce/doc/api/consent/02-upsert-consent/spec.md",
    "e-commerce/doc/api/product/01-upsert-product/spec.md",
    "e-commerce/doc/api/product/04-upsert-product-category/spec.md",
    "e-commerce/doc/api/product/07-upsert-product-category-attribute/spec.md",
    "e-commerce/doc/api/shop/01-upsert-shop-product-sku/spec.md",
    "e-commerce/doc/api/shop/05-upsert-shop-type/spec.md",
    "e-commerce/doc/api/shop/08-upsert-shop/spec.md",
    "e-commerce/doc/api/shop/11-upsert-shop-user/spec.md",
]
BATCH_UPSERT_SPECS = [
    "e-commerce/doc/api/product/03-upsert-product-batch/spec.md",
    "e-commerce/doc/api/product/06-upsert-product-category-batch/spec.md",
    "e-commerce/doc/api/product/09-upsert-product-category-attribute-batch/spec.md",
    "e-commerce/doc/api/shop/02-upsert-shop-product-sku-batch/spec.md",
    "e-commerce/doc/api/shop/06-upsert-shop-type-batch/spec.md",
    "e-commerce/doc/api/shop/09-upsert-shop-batch/spec.md",
    "e-commerce/doc/api/shop/12-upsert-shop-user-batch/spec.md",
]


def success_codes(md: str) -> dict:
    """Map each '#### Success - X' example title to its HTTP code (None when the example has no JSON)."""
    found = {}
    for match in re.finditer(r"^#### (Success[^\n]*)\n(.*?)(?=^#### |^---|^## |\Z)", md, re.MULTILINE | re.DOTALL):
        title, body = match.group(1), match.group(2)
        code = re.search(r'"code": (\d+)', body)
        if "HTTP/1.1 204 No Content" in body:
            found[title] = 204
        elif code:
            found[title] = int(code.group(1))
        else:
            found[title] = None
    return found


def check_status_codes() -> int:
    errors = []
    expected = {"Success - Insert": 201, "Success - Update": 200, "Success - Delete": 204, "Success - Archive": 200}
    for path in SINGLE_UPSERT_SPECS:
        md = read(path)
        codes = success_codes(md)
        for title, code in expected.items():
            if codes.get(title) != code:
                errors.append(f"{path}: '{title}' must answer {code}, found {codes.get(title)}")
        if "```JSON" in md.split("#### Success - Delete")[1].split("#### Success - Archive")[0]:
            errors.append(f"{path}: the delete example must not have a response body")
        for needle in ["Archive when rowStatus is ARCHIVED", "HTTP 204 No Content"]:
            if needle not in md:
                errors.append(f"{path}: missing '{needle}'")
    for path in BATCH_UPSERT_SPECS:
        md = read(path)
        codes = success_codes(md)
        if set(codes.values()) != {200}:
            errors.append(f"{path}: every success example must answer 200, found {codes}")
        for needle in ["always HTTP 200", "ARCHIVE)"]:
            if needle not in md:
                errors.append(f"{path}: missing '{needle}'")
    if errors:
        return fail("; ".join(errors))
    print("OK: status-codes")
    return 0


COMMANDS["status-codes"] = check_status_codes


# ---------------------------------------------------------------- shop lot and storefront specs
SHOP_SPECS = {
    "01": "e-commerce/doc/api/shop/01-upsert-shop-product-sku/spec.md",
    "02": "e-commerce/doc/api/shop/02-upsert-shop-product-sku-batch/spec.md",
    "03": "e-commerce/doc/api/shop/03-inquiry-shop-product-sku/spec.md",
    "04": "e-commerce/doc/api/shop/04-inquiry-storefront-product/spec.md",
}


def relative_links_exist(path: str, md: str) -> list[str]:
    missing = []
    base = (ROOT / path).parent
    for target in re.findall(r"\]\((\.\./[^)#]+)", md):
        if not (base / target).exists():
            missing.append(target)
    return missing


def check_storefront_example(md: str) -> list[str]:
    errors = []
    match = re.search(r"#### Success\n\n```JSON\n(.*?)```", md, re.DOTALL)
    if not match:
        return ["04: no Success example"]
    data = json.loads(match.group(1))["data"]
    counts = [len(o["values"]) for o in data["options"]]
    expected = 1
    for c in counts:
        expected *= c
    if len(data["skus"]) != expected:
        errors.append(f"04: {len(data['skus'])} SKUs but the levels give {expected}")
    value_ids = {v["valueId"] for o in data["options"] for v in o["values"]}
    in_stock_prices = []
    for sku in data["skus"]:
        if sku["combinationKey"] != "-".join(sku["optionValueIds"]):
            errors.append(f"04: combinationKey of {sku['name']} differs from its option value ids")
        if not set(sku["optionValueIds"]) <= value_ids:
            errors.append(f"04: {sku['name']} uses an unknown option value")
        if sku["stockStatus"] == "IN_STOCK":
            if sku["sellingPrice"] is None or sku["maxOrderQuantity"] <= 0:
                errors.append(f"04: IN_STOCK SKU {sku['name']} needs a price and maxOrderQuantity > 0")
            in_stock_prices.append(sku["sellingPrice"])
        elif sku["sellingPrice"] is not None or sku["maxOrderQuantity"] != 0:
            errors.append(f"04: OUT_OF_STOCK SKU {sku['name']} must have null price and maxOrderQuantity 0")
    for option in data["options"]:
        for value in option["values"]:
            available = any(s["stockStatus"] == "IN_STOCK" and value["valueId"] in s["optionValueIds"] for s in data["skus"])
            if value["isAvailable"] != available:
                errors.append(f"04: isAvailable of value {value['value']} should be {available}")
    if in_stock_prices:
        if data["priceFrom"] != min(in_stock_prices) or data["priceTo"] != max(in_stock_prices):
            errors.append("04: priceFrom/priceTo differ from the IN_STOCK prices")
        if data["stockStatus"] != "IN_STOCK":
            errors.append("04: product stockStatus must be IN_STOCK")
    return errors


def check_shop_spec() -> int:
    errors = []
    mds = {}
    for key, path in SHOP_SPECS.items():
        try:
            mds[key] = read(path)
        except FileNotFoundError:
            errors.append(f"{path} does not exist")
            continue
        md = mds[key]
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        for bad in json_blocks_parse(md):
            errors.append(f"{path} invalid JSON block: {bad[:40]}")
        for link in relative_links_exist(path, md):
            errors.append(f"{path} broken link {link}")
    if errors:
        return fail("; ".join(errors))
    needles = {
        "01": ["#### Lot Object", "- The system keeps one row per (shopId, productId, skuId)", "#### UPDATE - Close the lot that is on sale before another lot is put on sale",
               "#### QUERY - Check lots in use", "sales.t_order_item", "Only one lot can be on sale", "E10006",
               "- Permission:", "E10009", "#### Fail - Forbidden", "#### QUERY - Check shop member",
               "#### QUERY - Check platform administrator", "-> permission (403) ->",
               "must not be lower than costPrice", "ck_t_shop_product_sku_lot_price_not_below_cost"],
        "02": ["#### Shop Product SKU Object", "#### Lot Object", "always 200", "skus[0].lots[1]", "Duplicate SKU",
               "must not be lower than costPrice", "ck_t_shop_product_sku_lot_price_not_below_cost",
               "- Permission:", "E10009", "#### Fail - Forbidden", "#### QUERY - Check shop members",
               "#### QUERY - Check platform administrator", "-> permission (403) ->"],
        "03": ["#### Lot Object", "costPrice", "#### QUERY - Get lots", "ORDER BY l.is_on_sale DESC"],
        "04": ["#### SKU Object", "#### Option Value Object", "- Only a product that is ACTIVE, sold by a shop", "stockStatus", "maxOrderQuantity",
               "#### QUERY - Get the lot that is on sale of each shop product SKU", "pi.option_value_id IS NULL",
               "sold by a shop that is ACTIVE", "AND s.row_status = 'ACTIVE' -- a shop that is not ACTIVE has no page"],
    }
    for key, need in needles.items():
        # rules that moved into a note of the sequence diagram are searched there, one line per wrapped note
        seq = re.sub(r"\n\s+", " ", read(SHOP_SPECS[key].replace("spec.md", "sequence.wsd")))
        for missing in missing_needles(mds[key] + "\n" + seq, need):
            errors.append(f"{SHOP_SPECS[key]} missing: {missing}")
    store = mds["04"]
    for forbidden in ["costPrice", "cost_price", "grossMargin", "gross_margin", "authorization"]:
        # the storefront is public and never returns cost or margins
        if forbidden in store:
            errors.append(f"{SHOP_SPECS['04']} must not contain '{forbidden}'")
    errors.extend(check_storefront_example(store))
    if errors:
        return fail("; ".join(errors))
    print("OK: shop-spec")
    return 0


COMMANDS["shop-spec"] = check_shop_spec


# ---------------------------------------------------------------- cart specs
CART_SPECS = {
    "01": "e-commerce/doc/api/cart/01-upsert-cart-item/spec.md",
    "02": "e-commerce/doc/api/cart/02-upsert-cart-item-batch/spec.md",
    "03": "e-commerce/doc/api/cart/03-inquiry-cart/spec.md",
}


def check_cart_inquiry_example(md: str) -> list[str]:
    errors = []
    match = re.search(r"#### Success\n\n```JSON\n(.*?)```", md, re.DOTALL)
    if not match:
        return ["03: no Success example"]
    data = json.loads(match.group(1))["data"]
    lines = 0
    available = 0
    quantity = 0
    subtotal = 0.0
    for shop in data["shops"]:
        shop_total = 0.0
        for item in shop["items"]:
            lines += 1
            qty, price, mx, kind = item["quantity"], item["sellingPrice"], item["maxOrderQuantity"], item["availability"]
            if kind == "AVAILABLE":
                if price is None or qty > mx or item["lineTotal"] != round(price * qty, 2):
                    errors.append(f"03: AVAILABLE line {item['cartId']} needs price, quantity <= max and lineTotal = price x quantity")
                available += 1
                quantity += qty
                shop_total += item["lineTotal"] or 0
            elif kind == "QUANTITY_EXCEEDS_STOCK":
                if price is None or not 0 < mx < qty or item["lineTotal"] is not None:
                    errors.append(f"03: QUANTITY_EXCEEDS_STOCK line {item['cartId']} needs a price, 0 < max < quantity and lineTotal null")
            elif kind in ("OUT_OF_STOCK", "UNAVAILABLE"):
                if price is not None or mx != 0 or item["lineTotal"] is not None:
                    errors.append(f"03: {kind} line {item['cartId']} needs price null, max 0 and lineTotal null")
            else:
                errors.append(f"03: unknown availability {kind}")
        if round(shop_total, 2) != shop["subtotal"]:
            errors.append(f"03: subtotal of shop {shop['shopName']} should be {round(shop_total, 2)}")
        subtotal += shop_total
    summary = data["summary"]
    expected = {"lineCount": lines, "availableLineCount": available, "totalQuantity": quantity, "subtotal": round(subtotal, 2)}
    for key, value in expected.items():
        if summary[key] != value:
            errors.append(f"03: summary.{key} should be {value}, found {summary[key]}")
    return errors


def check_cart_spec() -> int:
    errors = []
    mds = {}
    for key, path in CART_SPECS.items():
        try:
            mds[key] = read(path)
        except FileNotFoundError:
            errors.append(f"{path} does not exist")
            continue
        md = mds[key]
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        for bad in json_blocks_parse(md):
            errors.append(f"{path} invalid JSON block: {bad[:40]}")
        for link in relative_links_exist(path, md):
            errors.append(f"{path} broken link {link}")
    if errors:
        return fail("; ".join(errors))
    needles = {
        "01": ["- Add (no `id`) merges into the line of the same SKU", "#### Success - Merge", "E10007", "E10008",
               "\nON CONFLICT (user_id, shop_id, product_id, sku_id) WHERE row_status <> 'DELETED' -- the partial unique index uq_t_cart_user_id_shop_id_product_id_sku_id\nDO UPDATE SET",
               "WHERE cart.t_cart.quantity + EXCLUDED.quantity <= '<sequence.maxOrderQuantity>'", "(xmax = 0) as is_insert",
               "#### UPDATE - Update or delete a line", "more than 100 lines",
               "#### QUERY - Lock the user", "AND u.row_status = 'ACTIVE'\nFOR UPDATE -- every authen API locks the user row first",
               "locking the ACTIVE row of the user",
               "#### QUERY - Count the lines of the user", "HTTP/1.1 204 No Content",
               "must be ACTIVE, otherwise the request is rejected with 404 (E10005)"],
        "02": ["#### Cart Item Object", "always HTTP 200", "items[1]: Shop Product SKU Id is duplicated with items[0].", "MERGE",
               "\nON CONFLICT (user_id, shop_id, product_id, sku_id) WHERE row_status <> 'DELETED' -- the partial unique index uq_t_cart_user_id_shop_id_product_id_sku_id\nDO UPDATE SET",
               "WHERE cart.t_cart.quantity + EXCLUDED.quantity <= '<sequence.items.maxOrderQuantity>'", "(xmax = 0) as is_insert",
               "#### UPDATE - Update or delete a line", "more than 100 lines",
               "#### QUERY - Lock the user", "AND u.row_status = 'ACTIVE'\nFOR UPDATE -- every authen API locks the user row first",
               "locking the ACTIVE row of the user",
               "must be ACTIVE, otherwise the request is rejected with 404 (E10005)"],
        "03": ["- AVAILABLE: the SKU is on sale", "QUANTITY_EXCEEDS_STOCK", "#### QUERY - Get the lot that is on sale of each shop product SKU", "no paging"],
    }
    for key, need in needles.items():
        for missing in missing_needles(mds[key], need):
            errors.append(f"{CART_SPECS[key]} missing: {missing}")
    codes = success_codes(mds["01"])
    for title, code in {"Success - Insert": 201, "Success - Merge": 200, "Success - Update": 200, "Success - Delete": 204}.items():
        if codes.get(title) != code:
            errors.append(f"{CART_SPECS['01']}: '{title}' must answer {code}, found {codes.get(title)}")
    if set(success_codes(mds["02"]).values()) != {200}:
        errors.append(f"{CART_SPECS['02']}: every success example must answer 200")
    if set(success_codes(mds["03"]).values()) != {200}:
        errors.append(f"{CART_SPECS['03']}: every success example must answer 200")
    for key in ("01", "02", "03"):
        if "userId" in re.search(r"### Body Parameters.*?(?=\n#### |\n### )", mds[key], re.DOTALL).group(0) if "### Body Parameters" in mds[key] else False:
            errors.append(f"{CART_SPECS[key]}: the request must not carry a user id")
    errors.extend(check_cart_inquiry_example(mds["03"]))
    if errors:
        return fail("; ".join(errors))
    print("OK: cart-spec")
    return 0


COMMANDS["cart-spec"] = check_cart_spec


# ---------------------------------------------------------------- shop type (T1)
SHOP_TYPE_SPECS = {
    "05": "e-commerce/doc/api/shop/05-upsert-shop-type/spec.md",
    "06": "e-commerce/doc/api/shop/06-upsert-shop-type-batch/spec.md",
    "07": "e-commerce/doc/api/shop/07-inquiry-shop-type/spec.md",
}
SHOP_TYPE_INDEX = "CREATE UNIQUE INDEX IF NOT EXISTS uq_m_shop_type_name ON shop.m_shop_type (name) WHERE row_status <> 'DELETED'"


def json_examples(md: str, heading: str):
    """Parsed JSON of the first ```JSON block under '#### <heading>' (None when there is none)."""
    match = re.search(rf"^#### {re.escape(heading)}\n\n```JSON\n(.*?)```", md, re.MULTILINE | re.DOTALL)
    return json.loads(match.group(1)) if match else None


def check_shop_type_upsert_examples(md: str) -> list[str]:
    errors = []
    update = json.loads(re.search(r"##### Update\n\n```JSON\n(.*?)```", md, re.DOTALL).group(1))
    type_id = update["id"]
    for title in ("Success - Insert", "Success - Update", "Success - Archive"):
        body = json_examples(md, title)
        if body is None:
            errors.append(f"05: no JSON in '{title}'")
        elif body["data"]["shopTypeId"] != type_id:
            errors.append(f"05: '{title}' answers a different shopTypeId than the Update example")
    return errors


def check_shop_type_batch_examples(md: str) -> list[str]:
    errors = []
    request = json.loads(re.search(r"#### Example Body Parameters\n\n```JSON\n(.*?)```", md, re.DOTALL).group(1))
    items = request["shopTypes"]
    result = json_examples(md, "Success")["data"]["shopTypes"]
    if len(result) != len(items):
        errors.append(f"06: {len(result)} results for {len(items)} request items")
    ids = [i["id"] for i in items if "id" in i]
    if len(ids) != len(set(ids)):
        errors.append("06: the request example repeats an id")
    names = [i["name"] for i in items if i.get("rowStatus") != "DELETED"]
    if len(names) != len(set(names)):
        errors.append("06: the request example repeats a name among the items that are not DELETED")
    for position, (item, res) in enumerate(zip(items, result)):
        action = {"DELETED": "DELETE", "ARCHIVED": "ARCHIVE"}.get(item.get("rowStatus"), "UPDATE" if "id" in item else "INSERT")
        if "id" not in item and item.get("rowStatus") == "DELETED":
            errors.append(f"06: request item {position} deletes without an id")
        if res["index"] != position or res["action"] != action:
            errors.append(f"06: result {position} should be index {position}, action {action}, found {res['index']}/{res['action']}")
        if "id" in item and res["shopTypeId"] != item["id"]:
            errors.append(f"06: result {position} answers a different shopTypeId than the request item")
    return errors


def check_shop_type_inquiry_examples(md: str) -> list[str]:
    errors = []
    query_id = re.search(r"\?id=([0-9a-f-]{36})", md).group(1)
    for title in ("Success", "Success - By Id", "Success - Not Found"):
        data = json_examples(md, title)["data"]
        if data["totalItems"] != len(data["items"]):
            errors.append(f"07: '{title}' totalItems differs from the number of items")
        if any(item["rowStatus"] == "DELETED" for item in data["items"]):
            errors.append(f"07: '{title}' lists a DELETED shop type")
        if title == "Success - By Id" and [item["shopTypeId"] for item in data["items"]] != [query_id]:
            errors.append("07: the By Id example must list only the id of the request")
        if title == "Success - Not Found" and data["items"]:
            errors.append("07: the Not Found example must have no items")
    return errors


def check_shop_type_spec() -> int:
    errors = []
    mds = {}
    for key, path in SHOP_TYPE_SPECS.items():
        try:
            mds[key] = read(path)
        except FileNotFoundError:
            errors.append(f"{path} does not exist")
            continue
        md = mds[key]
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        for bad in json_blocks_parse(md):
            errors.append(f"{path} invalid JSON block: {bad[:40]}")
        for link in relative_links_exist(path, md):
            errors.append(f"{path} broken link {link}")
        for leftover in re.findall(r"(?i)categor\w*|parent\w*|slug|product(?!ion)(?! owner)\w*", md):
            errors.append(f"{path} still mentions '{leftover}' (copied from the product category spec)")
        if not (ROOT / path).with_name("sequence.wsd").exists():
            errors.append(f"{path} has no sequence.wsd beside it")
    if errors:
        return fail("; ".join(errors))
    needles = {
        "05": ["# [POST]: v1/shop/type/upsert", "- `name` is unique among shop types that are not DELETED", "#### QUERY - Check shop in use", "AND s.row_status <> 'DELETED'",
               "AND st.row_status <> 'DELETED'\nAND st.id <> '<sequence.id>'", "(../../../schema/shop/m_shop_type.md)",
               "(../../../schema/shop/m_shop.md)", "Shop type name already exists.", "Shop type is used by shops.", "Shop type not found.",
               "Row status must not be DELETED when inserting a shop type.", "E10003", "E10004", "E10006", "E90001", "Insert Shop Type Success"],
        "06": ["# [POST]: v1/shop/type/upsert/batch", "- Every shop type follows the rules of the single upsert (shop/05)", "#### QUERY - Check shop in use", "shopTypes[2]: Id is duplicated with shopTypes[1].",
               "shopTypes[2]: Name is duplicated with shopTypes[0].", "Shop types must contain 1 to 100 items.", "Swapping the names",
               "shopTypes[2]: Shop type is used by shops.", "AND st.row_status <> 'DELETED'\nAND st.id <> '<sequence.shopTypes.id>'"],
        "07": ["# [GET]: v1/shop/type", "#### QUERY - Get shop types", "#### QUERY - Get total items", "rowStatus", "ILIKE",
               "Page Index and Page Size must be greater than 0", "Row status must be one of ACTIVE, INACTIVE, LOCKED, ARCHIVED."],
    }
    for key, need in needles.items():
        # rules that moved into a note of the sequence diagram are searched there, one line per wrapped note
        seq = re.sub(r"\n\s+", " ", read(SHOP_TYPE_SPECS[key].replace("spec.md", "sequence.wsd")))
        for missing in missing_needles(mds[key] + "\n" + seq, need):
            errors.append(f"{SHOP_TYPE_SPECS[key]} missing: {missing!r}")
    if errors:
        return fail("; ".join(errors))
    for key in ("05", "06"):
        for forbidden in ("pageSize", "pageIndex"):
            if forbidden in mds[key]:
                errors.append(f"{SHOP_TYPE_SPECS[key]} must not contain '{forbidden}'")
    if "authorization" not in mds["07"]:
        errors.append("07: the inquiry needs the authorization header")
    try:
        errors.extend(check_shop_type_upsert_examples(mds["05"]))
        errors.extend(check_shop_type_batch_examples(mds["06"]))
        errors.extend(check_shop_type_inquiry_examples(mds["07"]))
    except (KeyError, TypeError, AttributeError, ValueError) as exc:
        errors.append(f"an example does not have the expected shape: {exc!r}")
    if errors:
        return fail("; ".join(errors))
    print("OK: shop-type-spec")
    return 0


COMMANDS["shop-type-spec"] = check_shop_type_spec


def er_shop_type_name_rows() -> list[str]:
    """Value of the 'name' row of every shop.m_shop_type table drawn in the ER diagram (one per page that draws it)."""
    import xml.etree.ElementTree as ET

    root = ET.fromstring(read("e-commerce/db/er-diagram.drawio"))
    cells = list(root.iter("mxCell"))
    rows = []
    for cell in cells:
        if cell.get("value") == "shop.m_shop_type":
            for child in cells:
                if child.get("parent") == cell.get("id") and "name :" in (child.get("value") or ""):
                    rows.append(child.get("value"))
    return rows


def check_shop_type_schema() -> int:
    """shop.m_shop_type: the name is unique among rows that are not DELETED (migration, doc, ER diagram, DB test)."""
    errors = []
    sql = read("e-commerce/db/migrations/up/04-shop.schema.up.sql")
    statements = schema_statements(sql, "shop", "m_shop_type")
    create = [s for s in statements if s.startswith("CREATE TABLE")]
    if len(create) != 1 or "UNIQUE" in create[0]:
        errors.append("migration 04: m_shop_type must be created without an inline UNIQUE")
    if SHOP_TYPE_INDEX not in statements:
        errors.append("migration 04: partial unique index uq_m_shop_type_name is missing or different")
    path = "e-commerce/doc/schema/shop/m_shop_type.md"
    md = read(path)
    for bad in table_lines_aligned(md):
        errors.append(f"{path} misaligned table: {bad[:40]}")
    if schema_statements(" ".join(SQL_BLOCK.findall(md)), "shop", "m_shop_type") != statements:
        errors.append(f"{path} SQL differs from the migration")
    if re.search(r"^\| UQ\s+\|.*\| name ", md, re.MULTILINE):
        errors.append(f"{path} still marks name as UQ")
    for needle in ("uq_m_shop_type_name", "Unique among rows where row_status <> 'DELETED'"):
        if needle not in md:
            errors.append(f"{path} missing: {needle}")
    rows = er_shop_type_name_rows()
    if len(rows) < 2:
        errors.append(f"ER diagram: expected m_shop_type on at least 2 pages, found {len(rows)}")
    for row in rows:
        if row.startswith("UK"):
            errors.append("ER diagram: m_shop_type.name still carries the UK marker")
    if not (ROOT / "e-commerce/db/tests/04-shop-type.test.sql").exists():
        errors.append("db/tests/04-shop-type.test.sql does not exist")
    if errors:
        return fail("; ".join(errors))
    print("OK: shop-type-schema")
    return 0


COMMANDS["shop-type-schema"] = check_shop_type_schema


# ---------------------------------------------------------------- shop and shop images (T2)
SHOP_PROFILE_SPECS = {
    "08": "e-commerce/doc/api/shop/08-upsert-shop/spec.md",
    "09": "e-commerce/doc/api/shop/09-upsert-shop-batch/spec.md",
    "10": "e-commerce/doc/api/shop/10-inquiry-shop/spec.md",
}
SHOP_INDEXES = [
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_m_shop_name ON shop.m_shop (name) WHERE row_status <> 'DELETED'",
]
SHOP_IMAGE_INDEXES = [
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_m_shop_image_shop_id_logo ON shop.m_shop_image (shop_id) WHERE type = 'LOGO' AND row_status <> 'DELETED'",
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_m_shop_image_shop_id_wallpaper ON shop.m_shop_image (shop_id) WHERE type = 'WALLPAPER' AND row_status <> 'DELETED'",
]
BANNER_MAX = 10


def json_decimal(text: str):
    from decimal import Decimal

    return json.loads(text, parse_float=Decimal)


def shop_profile_shop_errors(label: str, shop: dict, images_key: str = "images") -> list[str]:
    """Rules of one shop example: margin rates, image ids and the number of images of each type."""
    from decimal import Decimal

    errors = []
    rates = [Decimal(str(shop[k])) for k in ("platformMarginRate", "shopMarginRate") if shop.get(k) is not None]
    for rate in rates:
        if not (Decimal(0) <= rate <= Decimal(100)) or rate.as_tuple().exponent < -2:
            errors.append(f"{label}: margin rate {rate} is outside 0..100 or has more than 2 decimals")
    if sum(rates) > 100:
        errors.append(f"{label}: platform + shop margin rate exceeds 100")
    images = shop.get(images_key, [])
    ids = [i["id"] for i in images if "id" in i]
    if len(ids) != len(set(ids)):
        errors.append(f"{label}: an image id is repeated")
    live = [i for i in images if i.get("rowStatus", "ACTIVE") != "DELETED"]
    for kind, limit in (("LOGO", 1), ("WALLPAPER", 1), ("BANNER", BANNER_MAX)):
        if sum(1 for i in live if i["type"] == kind) > limit:
            errors.append(f"{label}: more than {limit} {kind} images")
    for i in images:
        if i["type"] not in ("LOGO", "BANNER", "WALLPAPER") or not i.get("imagePath", i.get("imagePath", "x")):
            errors.append(f"{label}: an image has a wrong type or no path")
    return errors


def shop_type_names() -> dict:
    """typeId -> name of the shop type examples of spec 07 (the same ids must carry the same names elsewhere)."""
    data = json_examples(read(SHOP_TYPE_SPECS["07"]), "Success")["data"]["items"]
    return {item["shopTypeId"]: item["name"] for item in data}


def check_shop_profile_upsert_examples(md: str) -> list[str]:
    errors = []
    bodies = {}
    for title in ("Insert", "Update", "Delete"):
        bodies[title] = json_decimal(re.search(rf"##### {title}\n\n```JSON\n(.*?)```", md, re.DOTALL).group(1))
        errors.extend(shop_profile_shop_errors(f"08 {title}", bodies[title]))
    shop_id = bodies["Update"]["id"]
    if bodies["Delete"]["id"] != shop_id:
        errors.append("08: the Delete example must use the id of the Update example")
    if "id" in bodies["Insert"]:
        errors.append("08: the Insert example must not have an id")
    for title in ("Success - Insert", "Success - Update", "Success - Archive"):
        body = json_examples(md, title)
        if body is None or body["data"]["shopId"] != shop_id:
            errors.append(f"08: '{title}' must answer the shopId of the Update example")
    for image in bodies["Update"].get("images", []):
        if "id" in image and image["type"] == "LOGO" and "rowStatus" not in image:
            break
    else:
        errors.append("08: the Update example must show the logo being replaced by id")
    return errors


def check_shop_profile_batch_examples(md: str) -> list[str]:
    errors = []
    request = json_decimal(re.search(r"#### Example Body Parameters\n\n```JSON\n(.*?)```", md, re.DOTALL).group(1))
    items = request["shops"]
    result = json_examples(md, "Success")["data"]["shops"]
    if len(result) != len(items):
        errors.append(f"09: {len(result)} results for {len(items)} request items")
    ids = [i["id"] for i in items if "id" in i]
    if len(ids) != len(set(ids)):
        errors.append("09: the request example repeats an id")
    names = [i["name"] for i in items if i.get("rowStatus") != "DELETED"]
    if len(names) != len(set(names)):
        errors.append("09: the request example repeats a name among the items that are not DELETED")
    names_by_type = shop_type_names()
    for position, (item, res) in enumerate(zip(items, result)):
        errors.extend(shop_profile_shop_errors(f"09 shops[{position}]", item))
        action = {"DELETED": "DELETE", "ARCHIVED": "ARCHIVE"}.get(item.get("rowStatus"), "UPDATE" if "id" in item else "INSERT")
        if "id" not in item and item.get("rowStatus") == "DELETED":
            errors.append(f"09: request item {position} deletes without an id")
        if res["index"] != position or res["action"] != action:
            errors.append(f"09: result {position} should be index {position}, action {action}, found {res['index']}/{res['action']}")
        if "id" in item and res["shopId"] != item["id"]:
            errors.append(f"09: result {position} answers a different shopId than the request item")
        if item["typeId"] not in names_by_type:
            errors.append(f"09: shops[{position}].typeId is not a shop type of the examples of spec 07")
    return errors


TYPE_ORDER = {"LOGO": 0, "BANNER": 1, "WALLPAPER": 2}


def check_shop_profile_inquiry_examples(md: str) -> list[str]:
    errors = []
    query_id = re.search(r"\?id=([0-9a-f-]{36})", md).group(1)
    names_by_type = shop_type_names()
    member = re.search(r"The caller of the examples is an ACTIVE member of the shop `([0-9a-f-]{36})` and is not a platform administrator", md)
    member_shop = member.group(1) if member else None
    if member_shop is None:
        errors.append("10: the rules must say which shop the caller of the examples is a member of")
    for title in ("Success", "Success - By Id", "Success - Not Found"):
        data = json_decimal(re.search(rf"^#### {re.escape(title)}\n\n```JSON\n(.*?)```", md, re.MULTILINE | re.DOTALL).group(1))["data"]
        if data["totalItems"] != len(data["items"]):
            errors.append(f"10: '{title}' totalItems differs from the number of items")
        for item in data["items"]:
            label = f"10 '{title}' {item['name']}"
            if item["rowStatus"] == "DELETED":
                errors.append(f"{label}: lists a DELETED shop")
            if names_by_type.get(item["typeId"]) != item["typeName"]:
                errors.append(f"{label}: typeName differs from the shop type example of spec 07")
            errors.extend(shop_profile_shop_errors(label, item))
            hidden = [item.get("platformMarginRate"), item.get("shopMarginRate")]
            if "platformMarginRate" not in item or "shopMarginRate" not in item:
                errors.append(f"{label}: the margin rate keys must stay in the item (null when hidden)")
            elif item["shopId"] == member_shop and None in hidden:
                errors.append(f"{label}: the caller is a member of this shop, its margin rates must be shown")
            elif item["shopId"] != member_shop and hidden != [None, None]:
                errors.append(f"{label}: the caller is not a member of this shop, its margin rates must be null")
            images = item["images"]
            order = [(TYPE_ORDER[i["type"]] if False else i["type"], i["seq"]) for i in images]
            if order != sorted(order):
                errors.append(f"{label}: images are not ordered by type and seq")
            if any(i["rowStatus"] == "DELETED" for i in images):
                errors.append(f"{label}: lists a DELETED image")
        if title == "Success - By Id" and [item["shopId"] for item in data["items"]] != [query_id]:
            errors.append("10: the By Id example must list only the id of the request")
        if title == "Success - Not Found" and data["items"]:
            errors.append("10: the Not Found example must have no items")
    return errors


def check_shop_profile_spec() -> int:
    errors = []
    mds = {}
    for key, path in SHOP_PROFILE_SPECS.items():
        try:
            mds[key] = read(path)
        except FileNotFoundError:
            errors.append(f"{path} does not exist")
            continue
        md = mds[key]
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        for bad in json_blocks_parse(md):
            errors.append(f"{path} invalid JSON block: {bad[:40]}")
        for link in relative_links_exist(path, md):
            errors.append(f"{path} broken link {link}")
        for leftover in re.findall(r"(?i)categor\w*|parent\w*|slug|Shop Type Rules|Pending confirmation|pending confirmation|E10007", md):
            errors.append(f"{path} still mentions '{leftover}'")
        if not (ROOT / path).with_name("sequence.wsd").exists():
            errors.append(f"{path} has no sequence.wsd beside it")
    if errors:
        return fail("; ".join(errors))
    needles = {
        "08": ["# [POST]: v1/shop/upsert", "- `name` is unique among shops that are not DELETED", "#### Image Object", "#### QUERY - Check shop products in use", "#### QUERY - Check shop orders in use",
               "#### INSERT - Add the caller as ADMIN of the new shop", "#### QUERY - Check platform administrator", "#### QUERY - Get next seq of the image type",
               "#### UPDATE - Delete the images of a deleted shop", "AND s.row_status <> 'DELETED'\nAND s.id <> '<sequence.id>'", "(../../../schema/shop/m_shop.md)",
               "(../../../schema/shop/m_shop_image.md)", "(../../../schema/shop/m_shop_type.md)", "(../../../schema/shop/t_shop_user.md)", "(../../../schema/sales/t_order.md)",
               "Shop name already exists.", "Shop is used by products or orders.", "Shop not found.", "Shop image not found.", "Shop type not found.",
               "You do not have permission to manage this shop.", "Only a platform administrator can change the platform margin rate.",
               "The shop already has a LOGO image, update it with its id or delete it in the same request.", "A shop can have at most 10 BANNER images.",
               "Only one LOGO image and one WALLPAPER image are allowed in the request.", "never changes the lots that already exist",
               "approved by the product owner", "This permission model (the role `PLATFORM_ADMIN`, the ADMIN of the shop and the code E10009) was approved by the product owner.", "ck_m_shop_margin_rate_total", "E10003", "E10004", "E10005", "E10006", "E10009", "E90001", "Insert Shop Success"],
        "09": ["# [POST]: v1/shop/upsert/batch", "- Every shop follows the rules of the single upsert (shop/08)", "#### Shop Object", "#### Image Object", "shops[2]: Id is duplicated with shops[1].",
               "shops[2]: Name is duplicated with shops[0].", "Shops must contain 1 to 100 items.", "Swapping the names", "shops[2]: Shop is used by products or orders.",
               "shops[1].images[0]: Shop image not found.", "#### QUERY - Check shop orders in use", "approved by the product owner", "This permission model (the role `PLATFORM_ADMIN`, the ADMIN of the shop and the code E10009) was approved by the product owner.", "never changes the lots that already exist"],
        "10": ["# [GET]: v1/shop", "- Shops with `rowStatus` DELETED and images with `rowStatus` DELETED are never returned", "#### Shop Object", "#### Image Object", "#### QUERY - Get shops", "#### QUERY - Get total items",
               "#### QUERY - Get shop type names", "#### QUERY - Get shop images", "#### QUERY - Check shop members", "#### QUERY - Check platform administrator",
               "(../../../schema/shop/t_shop_user.md)", "(../../../schema/author/t_user_role.md)", "approved by the product owner", "Null when the caller is not an ACTIVE member", "ORDER BY si.type, si.seq, si.created_at, si.id", "then creation time, then `id`",
               "Row status must be one of ACTIVE, INACTIVE, LOCKED, ARCHIVED.", "Page Index and Page Size must be greater than 0", "ILIKE", "typeName"],
    }
    for key, need in needles.items():
        seq = re.sub(r"\n\s+", " ", read(SHOP_PROFILE_SPECS[key].replace("spec.md", "sequence.wsd")))
        for missing in missing_needles(mds[key] + "\n" + seq, need):
            errors.append(f"{SHOP_PROFILE_SPECS[key]} missing: {missing!r}")
    if errors:
        return fail("; ".join(errors))
    if "authorization" not in mds["10"]:
        errors.append("10: the inquiry needs the authorization header")
    for key in ("08", "09"):
        for forbidden in ("pageSize", "pageIndex"):
            if forbidden in mds[key]:
                errors.append(f"{SHOP_PROFILE_SPECS[key]} must not contain '{forbidden}'")
    try:
        errors.extend(check_shop_profile_upsert_examples(mds["08"]))
        errors.extend(check_shop_profile_batch_examples(mds["09"]))
        errors.extend(check_shop_profile_inquiry_examples(mds["10"]))
    except (KeyError, TypeError, AttributeError, ValueError) as exc:
        errors.append(f"an example does not have the expected shape: {exc!r}")
    if errors:
        return fail("; ".join(errors))
    print("OK: shop-profile-spec")
    return 0


COMMANDS["shop-profile-spec"] = check_shop_profile_spec


def er_name_rows(label: str) -> list[str]:
    """Value of the 'name' row of every table with this header drawn in the ER diagram (one per page)."""
    import xml.etree.ElementTree as ET

    root = ET.fromstring(read("e-commerce/db/er-diagram.drawio"))
    cells = list(root.iter("mxCell"))
    rows = []
    for cell in cells:
        if cell.get("value") == label:
            for child in cells:
                if child.get("parent") == cell.get("id") and "name :" in (child.get("value") or ""):
                    rows.append(child.get("value"))
    return rows


def check_shop_profile_schema() -> int:
    """shop.m_shop and shop.m_shop_image: unique name, margin ceiling, RESTRICT on the type, one LOGO and one WALLPAPER."""
    errors = []
    sql = read("e-commerce/db/migrations/up/04-shop.schema.up.sql")
    shop = schema_statements(sql, "shop", "m_shop")
    image = schema_statements(sql, "shop", "m_shop_image")
    create_shop = [s for s in shop if s.startswith("CREATE TABLE")]
    if len(create_shop) != 1:
        errors.append("migration 04: m_shop must have exactly one CREATE TABLE")
    else:
        text = create_shop[0]
        if "UNIQUE" in text:
            errors.append("migration 04: m_shop must be created without an inline UNIQUE")
        if "REFERENCES shop.m_shop_type (id) ON DELETE RESTRICT" not in text:
            errors.append("migration 04: m_shop.type_id must reference m_shop_type with ON DELETE RESTRICT")
        if "CONSTRAINT ck_m_shop_margin_rate_total CHECK (platform_margin_rate + shop_margin_rate <= 100.00)" not in text:
            errors.append("migration 04: ck_m_shop_margin_rate_total is missing or different")
    for index in SHOP_INDEXES:
        if index not in shop:
            errors.append(f"migration 04: missing or different: {index[:75]}")
    for index in SHOP_IMAGE_INDEXES:
        if index not in image:
            errors.append(f"migration 04: missing or different: {index[:75]}")
    docs = [("m_shop", shop, ["uq_m_shop_name", "ck_m_shop_margin_rate_total", "ON DELETE RESTRICT", "Unique among rows where row_status <> 'DELETED'"]),
            ("m_shop_image", image, ["uq_m_shop_image_shop_id_logo", "uq_m_shop_image_shop_id_wallpaper", "one LOGO per shop", "one WALLPAPER per shop"])]
    for table, statements, words in docs:
        path = f"e-commerce/doc/schema/shop/{table}.md"
        md = read(path)
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        if schema_statements(" ".join(SQL_BLOCK.findall(md)), "shop", table) != statements:
            errors.append(f"{path} SQL differs from the migration")
        for word in words:
            if word not in md:
                errors.append(f"{path} missing: {word}")
        if "ON DELETE CASCADE" in md and table == "m_shop" and "m_shop_type(id), ON DELETE CASCADE" in md:
            errors.append(f"{path} still says CASCADE for type_id")
        if re.search(r"^\| UQ\s+\|.*\| name ", md, re.MULTILINE):
            errors.append(f"{path} still marks name as UQ")
    rows = er_name_rows("shop.m_shop")
    if len(rows) < 2:
        errors.append(f"ER diagram: expected m_shop on at least 2 pages, found {len(rows)}")
    for row in rows:
        if row.startswith("UK"):
            errors.append("ER diagram: m_shop.name still carries the UK marker")
    test = ROOT / "e-commerce/db/tests/04-shop-profile.test.sql"
    if not test.exists():
        errors.append("db/tests/04-shop-profile.test.sql does not exist")
    else:
        text = test.read_text(encoding="utf-8")
        for n in range(1, 5):
            if f"PASS test {n}:" not in text:
                errors.append(f"04-shop-profile.test.sql has no test {n}")
    if errors:
        return fail("; ".join(errors))
    print("OK: shop-profile-schema")
    return 0


COMMANDS["shop-profile-schema"] = check_shop_profile_schema


# ---------------------------------------------------------------- one bizCode, one HTTP status across doc/api
def error_status_codes() -> dict:
    """bizCode (E*) -> {HTTP code -> [spec files]} over every JSON example of every spec under doc/api."""
    found = {}
    for path in sorted((ROOT / "e-commerce/doc/api").rglob("spec.md")):
        for match in JSON_BLOCK.finditer(path.read_text(encoding="utf-8")):
            block = match.group(1)
            if block.strip().startswith("curl"):
                continue
            try:
                status = json.loads(block).get("status")
            except (ValueError, AttributeError):
                continue
            if isinstance(status, dict) and str(status.get("bizCode", "")).startswith("E"):
                files = found.setdefault(status["bizCode"], {}).setdefault(status.get("code"), [])
                rel = str(path.relative_to(ROOT))
                if rel not in files:
                    files.append(rel)
    return found


def check_biz_codes() -> int:
    """A bizCode must always come with the same HTTP status, otherwise two specs give it two meanings."""
    errors = []
    for biz, codes in sorted(error_status_codes().items()):
        if len(codes) > 1:
            detail = "; ".join(f"HTTP {code} in {', '.join(f.split('/api/')[1] for f in files[:3])}" for code, files in sorted(codes.items()))
            errors.append(f"{biz} has more than one HTTP status: {detail}")
    if errors:
        return fail(" | ".join(errors))
    print("OK: biz-codes")
    return 0


COMMANDS["biz-codes"] = check_biz_codes


# ---------------------------------------------------------------- order (WP1)
ORDER_SPECS = {
    "01": "e-commerce/doc/api/sales/01-inquiry-checkout/spec.md",
    "02": "e-commerce/doc/api/sales/02-create-order/spec.md",
    "03": "e-commerce/doc/api/sales/03-inquiry-order/spec.md",
    "04": "e-commerce/doc/api/sales/04-inquiry-shop-order/spec.md",
    "05": "e-commerce/doc/api/sales/05-cancel-order/spec.md",
}
ORDER_STATUSES = ["PENDING", "PROCESSING", "WAIT_PAYMENT", "PAYMENT_CONFIRMED", "REFUNDED", "COMPLETED", "CANCELLED"]


def order_total_errors(label: str, order: dict) -> list[str]:
    errors = []
    expected = round(order["totalPrice"] - order["totalDiscount"] + order["totalTax"] + order["totalShipping"], 2)
    if round(order["totalAmount"], 2) != expected:
        errors.append(f"{label}: totalAmount should be {expected}")
    return errors


def order_items_errors(label: str, order: dict) -> list[str]:
    errors = []
    items = order["items"]
    if round(sum(i["totalPrice"] for i in items), 2) != round(order["totalPrice"], 2):
        errors.append(f"{label}: totalPrice should be the sum of the item totals")
    for item in items:
        if round(item["price"] * item["quantity"], 2) != round(item["totalPrice"], 2):
            errors.append(f"{label}: item {item['orderItemId']} totalPrice should be price x quantity")
        if item["quantity"] <= 0:
            errors.append(f"{label}: item {item['orderItemId']} quantity must be greater than 0")
    if order["status"] not in ORDER_STATUSES:
        errors.append(f"{label}: unknown status {order['status']}")
    return errors


def order_examples(md: str, title: str) -> list:
    out = []
    for match in re.finditer(rf"^#### {re.escape(title)}[^\n]*\n\n```JSON\n(.*?)```", md, re.MULTILINE | re.DOTALL):
        out.append(json.loads(match.group(1)))
    return out


def check_order_checkout(md: str) -> list[str]:
    errors = []
    titled = re.findall(r"^#### (Success[^\n]*)\n\n```JSON\n(.*?)```", md, re.MULTILINE | re.DOTALL)
    for k, (ex_title, raw) in enumerate(titled):
        ex = json.loads(raw)
        data, tag = ex["data"], f"01 example {k}"
        count = qty = 0
        total = 0.0
        errors.extend(campaign_example_errors("01", ex_title, data["shops"]))
        for shop in data["shops"]:
            for line in shop["items"]:
                count += 1
                qty += line["quantity"]
                if round(line["sellingPrice"] * line["quantity"], 2) != round(line["lineTotal"], 2):
                    errors.append(f"{tag}: line {line['cartId']} lineTotal should be sellingPrice x quantity")
            if round(sum(i["lineTotal"] for i in shop["items"]), 2) != round(shop["totalPrice"], 2):
                errors.append(f"{tag}: shop {shop['shopName']} totalPrice should be the sum of the lines")
            errors.extend(order_total_errors(f"{tag} shop {shop['shopName']}", shop))
            total += shop["totalAmount"]
        s = data["summary"]
        if (s["shopCount"], s["itemCount"], s["totalQuantity"], round(s["totalAmount"], 2)) != (len(data["shops"]), count, qty, round(total, 2)):
            errors.append(f"{tag}: summary does not match the shops")
        if data["canCheckout"] != (not data["problems"] and bool(data["shops"])):
            errors.append(f"{tag}: canCheckout should be TRUE only when there is no problem and at least one shop")
        for p in data["problems"]:
            if p["reason"] not in ("QUANTITY_EXCEEDS_STOCK", "OUT_OF_STOCK", "UNAVAILABLE", "DISCOUNT_BUDGET_EXHAUSTED"):
                errors.append(f"{tag}: unknown problem reason {p['reason']}")
            if p["reason"] == "QUANTITY_EXCEEDS_STOCK" and not 0 < p["maxOrderQuantity"] < p["quantity"]:
                errors.append(f"{tag}: QUANTITY_EXCEEDS_STOCK needs 0 < maxOrderQuantity < quantity")
    return errors


def campaign_example_errors(tag: str, title: str, shops: list) -> list[str]:
    """The discount of an example: 0.00 unless the example is the one where a campaign applies, and never more than the price."""
    errors = []
    for s in shops:
        if s["totalTax"] or s["totalShipping"]:
            errors.append(f"{tag} {s.get('code') or s.get('shopName')}: tax and shipping are 0.00 here")
        if title in ("Success - With Campaign", "Success - With Capped Discount"):
            if not 0 <= s["totalDiscount"] <= s["totalPrice"] or s["totalDiscount"] != round(s["totalDiscount"], 2):
                errors.append(f"{tag} {s.get('code') or s.get('shopName')}: a discount is between 0 and the price, with 2 decimals")
        elif s["totalDiscount"]:
            errors.append(f"{tag} {s.get('code') or s.get('shopName')}: the discount is 0.00 when no campaign applies")
    if title in ("Success - With Campaign", "Success - With Capped Discount") and not any(s["totalDiscount"] > 0 for s in shops):
        errors.append(f"{tag}: the campaign example needs at least one shop with a discount above 0")
    return errors


def check_order_create(md: str) -> list[str]:
    errors = []
    for title, raw in re.findall(r"^#### (Success[^\n]*)\n\n```JSON\n(.*?)```", md, re.MULTILINE | re.DOTALL):
        ex = json.loads(raw)
        ids = set()
        errors.extend(campaign_example_errors("02", title, ex["data"]["orders"]))
        for o in ex["data"]["orders"]:
            errors.extend(order_total_errors(f"02 order {o['code']}", o))
            if o["status"] != "WAIT_PAYMENT":
                errors.append(f"02 order {o['code']}: a created order must be WAIT_PAYMENT")
            if o["shopId"] in ids:
                errors.append("02: one order for each shop")
            ids.add(o["shopId"])
    return errors


def check_order_inquiry(md: str, key: str) -> list[str]:
    errors = []
    for k, ex in enumerate(order_examples(md, "Success")):
        data = ex["data"]
        if data["totalPages"] != -(-data["totalItems"] // data["pageSize"]):
            errors.append(f"{key} example {k}: totalPages does not match totalItems and pageSize")
        if data["totalPages"] <= 1 and data["totalItems"] != len(data["orders"]):
            errors.append(f"{key} example {k}: one page holds every order, totalItems should be {len(data['orders'])}")
        for o in data["orders"]:
            label = f"{key} order {o['code']}"
            errors.extend(order_total_errors(label, o))
            errors.extend(order_items_errors(label, o))
            for item in o["items"]:
                if key == "03" and any(f in item for f in ("lotId", "grossProfit", "shopProfit", "platformProfit")):
                    errors.append(f"{label}: the customer must not see the lot or the profit")
                if key == "04" and item["platformProfit"] is not None:
                    errors.append(f"{label}: platformProfit is null for the members of the shop")
                if key == "04" and item["grossProfit"] is not None and item["shopProfit"] is not None and item["shopProfit"] > item["grossProfit"]:
                    errors.append(f"{label}: shopProfit cannot be larger than grossProfit")
            if key == "04" and set(o["shippingAddress"]) != {"title", "address", "city", "state", "postalCode", "country"}:
                errors.append(f"{label}: shippingAddress needs title, address, city, state, postalCode and country")
    return errors


def check_order_cancel(md: str) -> list[str]:
    errors = []
    for ex in order_examples(md, "Success"):
        data = ex["data"]
        if data["status"] != "CANCELLED" or not data["restoredItems"]:
            errors.append("05: a cancelled order must be CANCELLED and give items back")
    return errors


def check_order_spec() -> int:
    errors = []
    mds = {}
    for key, path in ORDER_SPECS.items():
        try:
            mds[key] = read(path)
        except FileNotFoundError:
            errors.append(f"{path} does not exist")
            continue
        md = mds[key]
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        for bad in json_blocks_parse(md):
            errors.append(f"{path} invalid JSON block: {bad[:40]}")
        for link in relative_links_exist(path, md):
            errors.append(f"{path} broken link {link}")
    if errors:
        return fail("; ".join(errors))
    needles = {
        "01": ["- Only the logged-in customer previews a checkout", "canCheckout", "#### Problem Object", "QUANTITY_EXCEEDS_STOCK", "#### QUERY - Get the cart lines to order",
               "#### QUERY - Get the SKU of each line with the lot that is on sale", "#### QUERY - Check the address of the user", "E10007"],
        "02": ["- Only the logged-in customer creates orders", "WAIT_PAYMENT", "expires_at", "ck_t_order_total_amount_sum", "ship_address", "#### INSERT - Create the order of a shop",
               "#### INSERT - Create the items of the order", "#### UPDATE - Take the quantity from the lot that is on sale",
               "AND quantity >= '<sequence.quantity>'", "AND is_on_sale = TRUE", "#### UPDATE - Delete the cart lines that were ordered",
               "one transaction", "E10007", "ck_t_shop_product_sku_lot_price_not_below_cost",
               "ORDER BY c.id\nFOR UPDATE -- the lines to order are locked in id order", "the cart lines of the request by `id` (`FOR UPDATE` in `QUERY - Get the cart lines to order`)", "approved by the product owner on 2026-11-08"],
        "03": ["- Only the orders of the user of the access token are returned", "ORDER BY o.created_at DESC, o.id", "o.user_id = '<sequence.userId>'", "#### QUERY - Count the orders of the user", "ILIKE"],
        "04": ["- The caller needs a verified JWT, then an ACTIVE member row of the shop", "E10009", "#### Fail - Forbidden", "#### QUERY - Check shop member", "#### QUERY - Check active credential and user",
               "the role `PLATFORM_ADMIN` in the verified `roles` claim", "do not query `author.m_role` or `author.t_user_role`",
               "approved by the product owner", "platformProfit", "ORDER BY o.created_at DESC, o.id", "INNER JOIN authen.m_user ui"],
        "05": ["- The caller needs a verified JWT, then must be the owner of the order", "#### UPDATE - Cancel the order", "AND status = 'WAIT_PAYMENT'", "#### UPDATE - Give the quantity back to the lot", "E10006",
               "restoredItems", "#### QUERY - Check shop member", "FOR UPDATE -- the order row is locked first", "ORDER BY oi.lot_id",
               "`Idempotency-Key` `cancel-<paymentIntentId>`", "approved by the product owner on 2026-11-08",
               "#### QUERY - Lock the caller user", "#### QUERY - Check current credential and user", "do not query `author.m_role` or `author.t_user_role`"],
    }
    for key, need in needles.items():
        # rules that moved into a note of the sequence diagram are searched there, one line per wrapped note
        seq = re.sub(r"\n\s+", " ", read(ORDER_SPECS[key].replace("spec.md", "sequence.wsd")))
        for missing in missing_needles(mds[key] + "\n" + seq, need):
            errors.append(f"{ORDER_SPECS[key]} missing: {missing}")
    for key, want in {"01": {"Success": 200, "Success - With Campaign": 200, "Success - With Problems": 200},
                      "02": {"Success": 201, "Success - With Campaign": 201, "Success - With Capped Discount": 201}, "03": {"Success": 200, "Success - Empty": 200},
                      "04": {"Success": 200, "Success - Empty": 200}, "05": {"Success": 200}}.items():
        if success_codes(mds[key]) != want:
            errors.append(f"{ORDER_SPECS[key]}: success examples should be {want}, found {success_codes(mds[key])}")
    for key in ("01", "02", "03", "05"):
        params = re.search(r"### (?:Query|Body) Parameters.*?(?=\n### |\n#### Example|\n## )", mds[key], re.DOTALL)
        if params and "userId" in params.group(0):
            errors.append(f"{ORDER_SPECS[key]}: the request must not carry a user id")
    for forbidden in ("email", "username", "costPrice", "cost_price", "lotId"):
        if forbidden in mds["03"]:
            errors.append(f"{ORDER_SPECS['03']} must not contain '{forbidden}'")
    for forbidden in ("email", "username", "email_address"):
        if forbidden in mds["04"]:
            errors.append(f"{ORDER_SPECS['04']} must not contain '{forbidden}'")
    if "E10009" in mds["03"] or "E10009" in mds["01"] or "E10009" in mds["02"]:
        errors.append("01-03: the customer APIs do not use the forbidden code E10009")
    errors.extend(check_order_checkout(mds["01"]))
    errors.extend(check_order_create(mds["02"]))
    errors.extend(check_order_inquiry(mds["03"], "03"))
    errors.extend(check_order_inquiry(mds["04"], "04"))
    errors.extend(check_order_cancel(mds["05"]))
    if errors:
        return fail("; ".join(errors))
    print("OK: order-spec")
    return 0


COMMANDS["order-spec"] = check_order_spec


# ---------------------------------------------------------------- shop users (T3)
SHOP_USER_SPECS = {
    "11": "e-commerce/doc/api/shop/11-upsert-shop-user/spec.md",
    "12": "e-commerce/doc/api/shop/12-upsert-shop-user-batch/spec.md",
    "13": "e-commerce/doc/api/shop/13-inquiry-shop-user/spec.md",
}
SHOP_USER_INDEX = "CREATE UNIQUE INDEX IF NOT EXISTS uq_t_shop_user_shop_id_user_id ON shop.t_shop_user (shop_id, user_id) WHERE row_status <> 'DELETED'"
SHOP_ROLES = ("ADMIN", "STAFF")


def shop_user_item_errors(label: str, item: dict) -> list[str]:
    errors = []
    if item.get("role", "STAFF") not in SHOP_ROLES:
        errors.append(f"{label}: role must be ADMIN or STAFF")
    return errors


def shop_names_from_spec10() -> dict:
    data = json_examples(read(SHOP_PROFILE_SPECS["10"]), "Success")["data"]["items"]
    return {item["shopId"]: item["name"] for item in data}


def check_shop_user_upsert_examples(md: str) -> list[str]:
    errors = []
    bodies = {t: json.loads(re.search(rf"##### {t}\n\n```JSON\n(.*?)```", md, re.DOTALL).group(1)) for t in ("Insert", "Update", "Delete")}
    for title, body in bodies.items():
        errors.extend(shop_user_item_errors(f"11 {title}", body))
    if "id" in bodies["Insert"] or bodies["Insert"].get("rowStatus") == "DELETED":
        errors.append("11: the Insert example must have no id and must not be DELETED")
    update, delete = bodies["Update"], bodies["Delete"]
    if (update["id"], update["shopId"], update["userId"]) != (delete["id"], delete["shopId"], delete["userId"]):
        errors.append("11: the Update and Delete examples must describe the same shop user")
    for title in ("Success - Insert", "Success - Update", "Success - Archive"):
        body = json_examples(md, title)
        if body is None or body["data"]["shopUserId"] != update["id"]:
            errors.append(f"11: '{title}' must answer the shopUserId of the Update example")
    return errors


def check_shop_user_batch_examples(md: str) -> list[str]:
    errors = []
    items = json.loads(re.search(r"#### Example Body Parameters\n\n```JSON\n(.*?)```", md, re.DOTALL).group(1))["shopUsers"]
    result = json_examples(md, "Success")["data"]["shopUsers"]
    if len(result) != len(items):
        errors.append(f"12: {len(result)} results for {len(items)} request items")
    ids = [i["id"] for i in items if "id" in i]
    if len(ids) != len(set(ids)):
        errors.append("12: the request example repeats an id")
    pairs = [(i["shopId"], i["userId"]) for i in items if i.get("rowStatus") != "DELETED"]
    if len(pairs) != len(set(pairs)):
        errors.append("12: the request example repeats a shop and user among the items that are not DELETED")
    for position, (item, res) in enumerate(zip(items, result)):
        errors.extend(shop_user_item_errors(f"12 shopUsers[{position}]", item))
        action = {"DELETED": "DELETE", "ARCHIVED": "ARCHIVE"}.get(item.get("rowStatus"), "UPDATE" if "id" in item else "INSERT")
        if "id" not in item and item.get("rowStatus") == "DELETED":
            errors.append(f"12: request item {position} deletes without an id")
        if res["index"] != position or res["action"] != action:
            errors.append(f"12: result {position} should be index {position}, action {action}, found {res['index']}/{res['action']}")
        if "id" in item and res["shopUserId"] != item["id"]:
            errors.append(f"12: result {position} answers a different shopUserId than the request item")
    return errors


def check_shop_user_inquiry_examples(md: str) -> list[str]:
    errors = []
    query = re.search(r"\?([^ \n']+)", md).group(1)
    shop_id = re.search(r"shopId=([0-9a-f-]{36})", query).group(1)
    caller = re.search(r"The caller of the examples is the user `([0-9a-f-]{36})`", md)
    if caller is None:
        return ["13: the rules must say who the caller of the examples is"]
    caller = caller.group(1)
    shop_names = shop_names_from_spec10()
    by_id_row = re.search(r"^\| \d+ +\| id +\|[^\n]*\| ([0-9a-f-]{36}) +\|", md, re.MULTILINE)
    by_id = by_id_row.group(1) if by_id_row else None
    if re.search(r'"(userName|username|emailAddress|email)"', md):
        errors.append("13: the user name and the email address must not be returned")
    for title in ("Success", "Success - By Id", "Success - My Shops", "Success - Not Found"):
        data = json_examples(md, title)["data"]
        if data["totalItems"] != len(data["items"]):
            errors.append(f"13: '{title}' totalItems differs from the number of items")
        for item in data["items"]:
            label = f"13 '{title}' {item['shopUserId']}"
            errors.extend(shop_user_item_errors(label, item))
            if item["rowStatus"] == "DELETED":
                errors.append(f"{label}: lists a DELETED shop user")
            if item["shopId"] in shop_names and shop_names[item["shopId"]] != item["shopName"]:
                errors.append(f"{label}: shopName differs from the shop example of spec 10")
            if title in ("Success", "Success - By Id") and item["shopId"] != shop_id:
                errors.append(f"{label}: belongs to another shop than the request")
            if title == "Success - My Shops" and item["userId"] != caller:
                errors.append(f"{label}: 'My Shops' lists the shop user of another user")
        if title == "Success - My Shops":
            shops = [item["shopId"] for item in data["items"]]
            if len(shops) != len(set(shops)):
                errors.append("13: 'My Shops' lists a shop twice")
        if title == "Success - By Id" and [item["shopUserId"] for item in data["items"]] != [by_id]:
            errors.append("13: the By Id example must list only the id of the request")
        if title == "Success - Not Found" and data["items"]:
            errors.append("13: the Not Found example must have no items")
        if title == "Success":
            roster = [item for item in data["items"]]
            if not any(i["role"] == "ADMIN" and i["rowStatus"] == "ACTIVE" for i in roster):
                errors.append("13: the roster example of a shop must show an ACTIVE ADMIN")
    return errors


def check_shop_user_spec() -> int:
    errors = []
    mds = {}
    for key, path in SHOP_USER_SPECS.items():
        try:
            mds[key] = read(path)
        except FileNotFoundError:
            errors.append(f"{path} does not exist")
            continue
        md = mds[key]
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        for bad in json_blocks_parse(md):
            errors.append(f"{path} invalid JSON block: {bad[:40]}")
        for link in relative_links_exist(path, md):
            errors.append(f"{path} broken link {link}")
        for leftover in re.findall(r"(?i)categor\w*|parent\w*|slug|Pending confirmation|E10007|decided by the lead SA|pending product owner confirmation", md):
            errors.append(f"{path} still mentions '{leftover}'")
        if not (ROOT / path).with_name("sequence.wsd").exists():
            errors.append(f"{path} has no sequence.wsd beside it")
    if errors:
        return fail("; ".join(errors))
    approval = ("The rules of this section, including the permission model (the ADMIN of the shop or a platform administrator, 403 E10009), "
                "were approved by the product owner.")
    permission = approval
    needles = {
        "11": ["# [POST]: v1/shop/user/upsert", "- A member of a shop is a user that has a row in `shop.t_shop_user`", approval, permission, "#### QUERY - Check shop member", "#### QUERY - Check shop administrator",
               "#### QUERY - Count the ADMIN members of the shop after the write", "#### QUERY - Check duplicate member", "#### QUERY - Check platform administrator",
               "(../../../schema/shop/t_shop_user.md)", "(../../../schema/authen/m_user.md)", "(../../../schema/author/t_user_role.md)",
               "AND su.row_status <> 'DELETED'\nAND su.id <> '<sequence.id>'", "User is already a member of the shop.", "The shop must keep at least one ADMIN.",
               "You do not have permission to manage the members of this shop.", "Shop user not found.", "Shop not found.", "User not found.",
               "Shop Id and User Id cannot be changed.", "Role must be ADMIN or STAFF.", "Row status must not be DELETED when inserting a shop user.",
               "A platform administrator cannot skip this rule", "can only delete or archive their own membership", "it must lock the row of the shop (`shop.m_shop`", "E10003", "E10004", "E10005", "E10006", "E10009", "E90001",
               "Insert Shop User Success"],
        "12": ["# [POST]: v1/shop/user/upsert/batch", "- A member of a shop is a user that has a row in `shop.t_shop_user`", approval, permission, "#### Shop User Object",
               "shopUsers[2]: Id is duplicated with shopUsers[1].", "shopUsers[2]: Shop Id and User Id are duplicated with shopUsers[0].", "Shop users must contain 1 to 100 items.",
               "#### QUERY - Count the ADMIN members of the shop after the write", "except the ADMIN rule that is checked once for each shop after all the items", "it must lock the row of the shop (`shop.m_shop`"],
        "13": ["# [GET]: v1/shop/user", "- `shopId` or `userId` must be specified", approval, permission, "#### Shop User Object", "#### QUERY - Get shop users", "#### QUERY - Get total items",
               "#### QUERY - Check shop member", "#### QUERY - Check platform administrator", "ORDER BY su.created_at DESC, su.id", "(../../../schema/shop/t_shop_user.md)",
               "(../../../schema/authen/m_user.md)", "(../../../schema/author/t_user_role.md)", "Shop Id or User Id is required.",
               "You do not have permission to view the members of this shop.", "The user name and the email address of a user are never returned",
               "list the shops of the caller", "Page Index and Page Size must be greater than 0", "ILIKE", "#### Success - My Shops"],
    }
    needles["13"] = [n if n != "list the shops of the caller" else "lists the shops of the caller" for n in needles["13"]]
    for key, need in needles.items():
        moved = {"11": ["it must lock the row of the shop (`shop.m_shop`"], "12": ["it must lock the row of the shop (`shop.m_shop`"]}.get(key, [])
        for missing in missing_apart(mds[key], read(SHOP_USER_SPECS[key].replace("spec.md", "sequence.wsd")), need, moved):
            errors.append(f"{SHOP_USER_SPECS[key]} missing: {missing!r}")
    if errors:
        return fail("; ".join(errors))
    if "authorization" not in mds["13"]:
        errors.append("13: the inquiry needs the authorization header")
    for key in ("11", "12"):
        for forbidden in ("pageSize", "pageIndex"):
            if forbidden in mds[key]:
                errors.append(f"{SHOP_USER_SPECS[key]} must not contain '{forbidden}'")
    try:
        errors.extend(check_shop_user_upsert_examples(mds["11"]))
        errors.extend(check_shop_user_batch_examples(mds["12"]))
        errors.extend(check_shop_user_inquiry_examples(mds["13"]))
    except (KeyError, TypeError, AttributeError, ValueError) as exc:
        errors.append(f"an example does not have the expected shape: {exc!r}")
    if errors:
        return fail("; ".join(errors))
    print("OK: shop-user-spec")
    return 0


COMMANDS["shop-user-spec"] = check_shop_user_spec


def er_unique_rows(label: str) -> list[str]:
    """The 'UNIQUE (...)' rows of every table with this header in the ER diagram."""
    import xml.etree.ElementTree as ET

    root = ET.fromstring(read("e-commerce/db/er-diagram.drawio"))
    cells = list(root.iter("mxCell"))
    rows = []
    for cell in cells:
        if cell.get("value") == label:
            rows += [c.get("value") for c in cells if c.get("parent") == cell.get("id") and (c.get("value") or "").startswith("UNIQUE")]
    return rows


def check_shop_user_schema() -> int:
    """shop.t_shop_user: one membership per shop and user among rows that are not DELETED."""
    errors = []
    sql = read("e-commerce/db/migrations/up/04-shop.schema.up.sql")
    statements = schema_statements(sql, "shop", "t_shop_user")
    create = [s for s in statements if s.startswith("CREATE TABLE")]
    if len(create) != 1 or "UNIQUE" in create[0]:
        errors.append("migration 04: t_shop_user must be created without an inline UNIQUE")
    if SHOP_USER_INDEX not in statements:
        errors.append("migration 04: partial unique index uq_t_shop_user_shop_id_user_id is missing or different")
    path = "e-commerce/doc/schema/shop/t_shop_user.md"
    md = read(path)
    for bad in table_lines_aligned(md):
        errors.append(f"{path} misaligned table: {bad[:40]}")
    if schema_statements(" ".join(SQL_BLOCK.findall(md)), "shop", "t_shop_user") != statements:
        errors.append(f"{path} SQL differs from the migration")
    for needle in ("uq_t_shop_user_shop_id_user_id", "Unique among rows where row_status <> 'DELETED'"):
        if needle not in md:
            errors.append(f"{path} missing: {needle}")
    if "Unique combination" in md:
        errors.append(f"{path} still says 'Unique combination'")
    for row in er_unique_rows("shop.t_shop_user"):
        errors.append(f"ER diagram: t_shop_user still draws '{row}' (a partial unique index is not drawn)")
    if len(er_name_rows("shop.t_shop_user")) != 0:
        errors.append("ER diagram: t_shop_user must not have a name row")
    test = ROOT / "e-commerce/db/tests/04-shop-user.test.sql"
    if not test.exists():
        errors.append("db/tests/04-shop-user.test.sql does not exist")
    else:
        text = test.read_text(encoding="utf-8")
        for n in range(1, 4):
            if f"PASS test {n}:" not in text:
                errors.append(f"04-shop-user.test.sql has no test {n}")
    if errors:
        return fail("; ".join(errors))
    print("OK: shop-user-schema")
    return 0


COMMANDS["shop-user-schema"] = check_shop_user_schema


# ---------------------------------------------------------------- products of a shop (T4)
SHOP_PRODUCT_SPEC = "e-commerce/doc/api/shop/14-inquiry-storefront-shop-product/spec.md"
SHOP_PRODUCT_INDEX = "CREATE UNIQUE INDEX IF NOT EXISTS uq_t_shop_product_shop_id_product_id ON shop.t_shop_product (shop_id, product_id) WHERE row_status <> 'DELETED'"


def er_child_values(label: str) -> list[str]:
    """Every row of every table with this header in the ER diagram."""
    import xml.etree.ElementTree as ET

    root = ET.fromstring(read("e-commerce/db/er-diagram.drawio"))
    cells = list(root.iter("mxCell"))
    rows = []
    for cell in cells:
        if cell.get("value") == label:
            rows += [c.get("value") or "" for c in cells if c.get("parent") == cell.get("id")]
    return rows


def shop_product_sort_key(item: dict):
    return (item["priceFrom"] is None, item["priceFrom"] if item["priceFrom"] is not None else 0, item["productId"])


def check_shop_product_examples(md: str) -> list[str]:
    errors = []
    titles = ("Success", "Success - Price Ascending", "Success - In Stock Only", "Success - Not Found")
    data = {t: json_decimal(re.search(rf"^#### {re.escape(t)}\n\n```JSON\n(.*?)```", md, re.MULTILINE | re.DOTALL).group(1))["data"] for t in titles}
    shop10 = {i["shopId"]: i for i in json_examples(read(SHOP_PROFILE_SPECS["10"]), "Success")["data"]["items"]}
    page04 = json_examples(read(SHOP_SPECS["04"]), "Success")["data"]
    for title, d in data.items():
        label = f"14 '{title}'"
        shop = d["shop"]
        if d["totalItems"] != len(d["items"]):
            errors.append(f"{label}: totalItems differs from the number of items")
        source = shop10.get(shop["shopId"])
        if source is None:
            errors.append(f"{label}: the shop is not a shop of the examples of spec 10")
        else:
            for key, other in (("name", "name"), ("description", "description"), ("typeName", "typeName")):
                if shop[key] != source[other]:
                    errors.append(f"{label}: shop {key} differs from spec 10")
            expected = [(i["imageId"], i["type"], i["imagePath"]) for i in source["images"] if i["rowStatus"] == "ACTIVE"]
            if [(i["imageId"], i["type"], i["imagePath"]) for i in shop["images"]] != expected:
                errors.append(f"{label}: shop images differ from the ACTIVE images of spec 10")
        order = [(i["type"]) for i in shop["images"]]
        if order != sorted(order):
            errors.append(f"{label}: shop images are not ordered by type")
        ids = [i["productId"] for i in d["items"]]
        if len(ids) != len(set(ids)):
            errors.append(f"{label}: a product is listed twice")
        for item in d["items"]:
            name = f"{label} {item['name']}"
            if item["stockStatus"] == "IN_STOCK":
                if item["priceFrom"] is None or item["priceTo"] is None or item["priceFrom"] > item["priceTo"]:
                    errors.append(f"{name}: IN_STOCK needs priceFrom <= priceTo")
            elif item["stockStatus"] == "OUT_OF_STOCK":
                if item["priceFrom"] is not None or item["priceTo"] is not None:
                    errors.append(f"{name}: OUT_OF_STOCK must have null prices")
            else:
                errors.append(f"{name}: stockStatus must be IN_STOCK or OUT_OF_STOCK")
            if item["imagePath"] is not None and not isinstance(item["imagePath"], str):
                errors.append(f"{name}: imagePath must be text or null")
    everything = {i["productId"]: i for i in data["Success"]["items"]}
    stocks = {i["stockStatus"] for i in data["Success"]["items"]}
    if stocks != {"IN_STOCK", "OUT_OF_STOCK"}:
        errors.append("14: the default example must show a product that is out of stock next to products in stock")
    price = data["Success - Price Ascending"]["items"]
    if sorted(price, key=shop_product_sort_key) != price:
        errors.append("14: 'Price Ascending' must be ordered by priceFrom, products out of stock last, then productId")
    if {i["productId"] for i in price} != set(everything):
        errors.append("14: 'Price Ascending' must list the same products as the default example")
    stock_only = data["Success - In Stock Only"]["items"]
    if any(i["stockStatus"] != "IN_STOCK" for i in stock_only):
        errors.append("14: 'In Stock Only' lists a product that is out of stock")
    if {i["productId"] for i in stock_only} != {k for k, v in everything.items() if v["stockStatus"] == "IN_STOCK"}:
        errors.append("14: 'In Stock Only' must list exactly the products in stock of the default example")
    if data["Success - Not Found"]["items"]:
        errors.append("14: the Not Found example must have no items")
    shirt = everything.get(page04["productId"])
    if shirt is None:
        errors.append("14: the product of the page example (shop/04) must be in the list")
    else:
        first_image = page04["images"][0]["imagePath"] if page04["images"] else None
        same = (shirt["name"], shirt["slug"], shirt["priceFrom"], shirt["priceTo"], shirt["stockStatus"], shirt["imagePath"])
        if same != (page04["name"], page04["slug"], page04["priceFrom"], page04["priceTo"], page04["stockStatus"], first_image):
            errors.append("14: the product of shop/04 differs between the list and its page (name, slug, prices, stock or first image)")
    return errors


def check_shop_product_spec() -> int:
    errors = []
    path = SHOP_PRODUCT_SPEC
    try:
        md = read(path)
    except FileNotFoundError:
        return fail(f"{path} does not exist")
    for bad in table_lines_aligned(md):
        errors.append(f"{path} misaligned table: {bad[:40]}")
    for bad in json_blocks_parse(md):
        errors.append(f"{path} invalid JSON block: {bad[:40]}")
    for link in relative_links_exist(path, md):
        errors.append(f"{path} broken link {link}")
    if not (ROOT / path).with_name("sequence.wsd").exists():
        errors.append(f"{path} has no sequence.wsd beside it")
    for forbidden in ("authorization", "Unauthorized", "costPrice", "cost_price", "grossMargin", "gross_margin", "platformMarginRate", "shopMarginRate",
                      "platform_margin_rate", "shop_margin_rate", "shareMargin", "t_shop_user", "E10007", "E10009"):
        if forbidden in md:
            errors.append(f"{path} is public and must not contain '{forbidden}'")
    for key in ("userId", "quantity"):
        if re.search(rf'"{key}"', md):
            errors.append(f"{path} must not return '{key}'")
    approval = "The rules of this section, including the rule that a shop that is not ACTIVE has no page, were approved by the product owner."
    for old in ("decided by the lead SA", "pending product owner confirmation"):
        if old in md:
            errors.append(f"{path} still says '{old}', the rules are approved by the product owner")
    needles = ["# [GET]: v1/storefront/shop/product", "- This API is public: it needs no access token. It never returns the cost price", approval,
               "#### Shop Object", "#### Shop Image Object", "#### Product Object", "#### QUERY - Get shop", "#### QUERY - Get products of the shop",
               "#### QUERY - Get total items", "#### QUERY - Get the category and its sub categories", "#### QUERY - Get the first image of each product",
               "#### QUERY - Get shop images", "WITH RECURSIVE categories AS", "ORDER BY v.listed_at DESC, p.id", "-- ORDER BY (v.price_from IS NULL), v.price_from, p.id",
               "-- ORDER BY (v.price_from IS NULL), v.price_from DESC, p.id", "-- ORDER BY p.name, p.id", "AND l.quantity > 0", "AND v.price_from IS NOT NULL",
               "ORDER BY pi.product_id, pi.created_at, pi.id", "(../../../schema/shop/t_shop_product.md)", "(../../../schema/shop/m_shop.md)",
               "(../../../schema/product/m_product_category.md)", "(../../../schema/product/m_product_image.md)", "shop/04",
               "Shop Id is a required field.", "Shop not found.", "Sort must be one of NEWEST, PRICE_ASC, PRICE_DESC, NAME_ASC",
               "Page Index and Page Size must be greater than 0", "Every sort ends with `productId` ascending as the tie-break",
               "A shop stops showing a product by closing all the SKUs", "public: it needs no access token", "#### Success - Price Ascending", "#### Success - In Stock Only",
               "E10001", "E10004", "E90001", "Inquiry Storefront Shop Product Success"]
    for missing in missing_needles(md, needles):
        errors.append(f"{path} missing: {missing!r}")
    if errors:
        return fail("; ".join(errors))
    for sql_block in SQL_BLOCK.findall(md):
        if "WITH visible AS (" not in sql_block:
            continue
        cte = sql_block[sql_block.index("WITH visible AS ("): sql_block.index("FROM visible v")]
        defined = set(re.findall(r"\bas (\w+)", cte)) | {"product_id"}
        for column in set(re.findall(r"\bv\.(\w+)", sql_block)):
            if column not in defined:
                errors.append(f"{path}: v.{column} is not a column of the visible query (columns: {sorted(defined)})")
    try:
        errors.extend(check_shop_product_examples(md))
    except (KeyError, TypeError, AttributeError, ValueError, IndexError) as exc:
        errors.append(f"an example does not have the expected shape: {exc!r}")
    if errors:
        return fail("; ".join(errors))
    print("OK: shop-product-spec")
    return 0


COMMANDS["shop-product-spec"] = check_shop_product_spec


def check_shop_product_schema() -> int:
    """shop.t_shop_product: no quantity (the stock is on the lots) and one row per shop and product among rows that are not DELETED."""
    errors = []
    sql = read("e-commerce/db/migrations/up/04-shop.schema.up.sql")
    statements = schema_statements(sql, "shop", "t_shop_product")
    create = [s for s in statements if s.startswith("CREATE TABLE")]
    if len(create) != 1:
        errors.append("migration 04: t_shop_product must have exactly one CREATE TABLE")
    else:
        if "UNIQUE" in create[0]:
            errors.append("migration 04: t_shop_product must be created without an inline UNIQUE")
        if "quantity" in create[0]:
            errors.append("migration 04: t_shop_product must not have a quantity column")
    if SHOP_PRODUCT_INDEX not in statements:
        errors.append("migration 04: partial unique index uq_t_shop_product_shop_id_product_id is missing or different")
    path = "e-commerce/doc/schema/shop/t_shop_product.md"
    md = read(path)
    for bad in table_lines_aligned(md):
        errors.append(f"{path} misaligned table: {bad[:40]}")
    if schema_statements(" ".join(SQL_BLOCK.findall(md)), "shop", "t_shop_product") != statements:
        errors.append(f"{path} SQL differs from the migration")
    if "quantity" in md or "Unique combination" in md:
        errors.append(f"{path} still mentions quantity or 'Unique combination'")
    for needle in ("uq_t_shop_product_shop_id_product_id", "Unique among rows where row_status <> 'DELETED'"):
        if needle not in md:
            errors.append(f"{path} missing: {needle}")
    readme = read("e-commerce/doc/schema/README.md")
    if "| [t_shop_product](shop/t_shop_product.md) | Transaction | 8 | 2 |" not in readme:
        errors.append("README: t_shop_product must have 8 columns and 2 FKs")
    rows = er_child_values("shop.t_shop_product")
    if len(rows) < 2 * 3:
        errors.append(f"ER diagram: t_shop_product must be drawn on at least 2 pages with 3 rows each, found {len(rows)} rows")
    for row in rows:
        if "quantity" in row or row.startswith("UNIQUE"):
            errors.append(f"ER diagram: t_shop_product still draws '{row}'")
    test = ROOT / "e-commerce/db/tests/04-shop-product.test.sql"
    if not test.exists():
        errors.append("db/tests/04-shop-product.test.sql does not exist")
    else:
        text = test.read_text(encoding="utf-8")
        for n in range(1, 4):
            if f"PASS test {n}:" not in text:
                errors.append(f"04-shop-product.test.sql has no test {n}")
    for spec in sorted((ROOT / "e-commerce/doc/api").rglob("spec.md")):
        for match in re.finditer(r"(?:sp|shop_product)\.quantity|shop\.t_shop_product \([^)]*quantity", spec.read_text(encoding="utf-8")):
            errors.append(f"{spec.relative_to(ROOT)} still uses the quantity of the shop product")
    if errors:
        return fail("; ".join(errors))
    print("OK: shop-product-schema")
    return 0


COMMANDS["shop-product-schema"] = check_shop_product_schema


# ---------------------------------------------------------------- reviews of a product (T5)
REVIEW_SPECS = {
    "15": "e-commerce/doc/api/shop/15-upsert-shop-product-review/spec.md",
    "16": "e-commerce/doc/api/shop/16-inquiry-storefront-product-review/spec.md",
}
REVIEW_INDEX = ("CREATE UNIQUE INDEX IF NOT EXISTS uq_t_shop_product_review_shop_product_id_user_id ON shop.t_shop_product_review "
                "(shop_product_id, user_id) WHERE row_status <> 'DELETED'")


def review_summary(reviews: list) -> dict:
    from decimal import Decimal, ROUND_HALF_UP

    count = len(reviews)
    average = None
    if count:
        average = (Decimal(sum(r["rating"] for r in reviews)) / count).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {"averageRating": average, "ratingCount": count,
            "ratingBreakdown": [{"rating": s, "count": sum(1 for r in reviews if r["rating"] == s)} for s in (5, 4, 3, 2, 1)]}


def check_review_upsert_examples(md: str) -> list[str]:
    errors = []
    bodies = {t: json.loads(re.search(rf"##### {t}\n\n```JSON\n(.*?)```", md, re.DOTALL).group(1)) for t in ("Insert", "Update", "Delete")}
    for title, body in bodies.items():
        label = f"15 {title}"
        if "userId" in body:
            errors.append(f"{label}: the caller comes from the access token, the body must not have userId")
        if not isinstance(body["rating"], int) or not 1 <= body["rating"] <= 5:
            errors.append(f"{label}: rating must be a whole number from 1 to 5")
        if len(body.get("comment") or "") > 2000:
            errors.append(f"{label}: comment is longer than 2000 characters")
        if body.get("rowStatus", "ACTIVE") not in ("ACTIVE", "DELETED"):
            errors.append(f"{label}: rowStatus must be ACTIVE or DELETED")
    if "id" in bodies["Insert"] or bodies["Insert"].get("rowStatus") == "DELETED":
        errors.append("15: the Insert example must have no id and must not be DELETED")
    if "id" not in bodies["Update"] or bodies["Delete"].get("rowStatus") != "DELETED" or "id" not in bodies["Delete"]:
        errors.append("15: the Update example needs an id and the Delete example needs an id and rowStatus DELETED")
    codes = success_codes(md)
    if codes != {"Success - Insert": 201, "Success - Update": 200, "Success - Delete": 204}:
        errors.append(f"15: the success examples must be Insert 201, Update 200 and Delete 204 (no Archive), found {codes}")
    update_response = json_examples(md, "Success - Update")
    if update_response is None or update_response["data"]["reviewId"] != bodies["Update"]["id"]:
        errors.append("15: 'Success - Update' must answer the id of the Update example")
    insert_response = json_examples(md, "Success - Insert")
    if insert_response is None or "reviewId" not in insert_response["data"]:
        errors.append("15: 'Success - Insert' must answer a reviewId")
    # the examples must agree with the review list of spec 16
    listing = json_examples(read(REVIEW_SPECS["16"]), "Success")["data"]["items"]
    by_id = {r["reviewId"]: r for r in listing}
    inserted = by_id.get(insert_response["data"]["reviewId"]) if insert_response else None
    if inserted is None or (inserted["rating"], inserted["comment"]) != (bodies["Insert"]["rating"], bodies["Insert"].get("comment")):
        errors.append("15: the inserted review must be in the list of spec 16 with the same rating and comment")
    updated = by_id.get(bodies["Update"].get("id"))
    if updated is None or (updated["rating"], updated["comment"]) != (bodies["Update"]["rating"], bodies["Update"].get("comment")):
        errors.append("15: the updated review must be in the list of spec 16 with the same rating and comment")
    elif updated["updatedAt"] is None:
        errors.append("15: the updated review must show updatedAt in the list of spec 16")
    return errors


def check_review_inquiry_examples(md: str) -> list[str]:
    errors = []
    titles = ("Success", "Success - Highest", "Success - Rating Filter", "Success - Not Found")
    data = {t: json_decimal(re.search(rf"^#### {re.escape(t)}\n\n```JSON\n(.*?)```", md, re.MULTILINE | re.DOTALL).group(1))["data"] for t in titles}
    full = data["Success"]["items"]
    expected = review_summary(full)
    if data["Success"]["totalItems"] != len(full):
        errors.append("16: the default example must list every review on one page (totalItems = number of items)")
    for title in ("Success", "Success - Highest", "Success - Rating Filter"):
        if data[title]["summary"] != expected:
            errors.append(f"16 '{title}': summary differs from the summary calculated from the reviews of the default example ({expected})")
    if data["Success - Not Found"]["summary"] != review_summary([]) or data["Success - Not Found"]["items"]:
        errors.append("16: the Not Found example must have no review, ratingCount 0, averageRating null and every count 0")
    allowed = {"reviewId", "rating", "comment", "displayName", "profilePicturePath", "createdAt", "updatedAt"}
    for title, d in data.items():
        if d["totalItems"] != len(d["items"]) and title != "Success":
            errors.append(f"16 '{title}': totalItems differs from the number of items")
        ids = [i["reviewId"] for i in d["items"]]
        if len(ids) != len(set(ids)):
            errors.append(f"16 '{title}': a review is listed twice")
        for item in d["items"]:
            label = f"16 '{title}' {item.get('reviewId')}"
            if set(item) != allowed:
                errors.append(f"{label}: keys must be exactly {sorted(allowed)}")
                continue
            if not isinstance(item["rating"], int) or not 1 <= item["rating"] <= 5:
                errors.append(f"{label}: rating must be a whole number from 1 to 5")
            if item["updatedAt"] is not None and item["updatedAt"] < item["createdAt"]:
                errors.append(f"{label}: updatedAt is before createdAt")
    newest = sorted(full, key=lambda r: (_neg_text(r["createdAt"]), r["reviewId"]))
    if full != newest:
        errors.append("16: the default example must be ordered by createdAt (newest first) and then reviewId")
    if data["Success - Highest"]["items"] != sorted(full, key=lambda r: (-r["rating"], r["reviewId"])):
        errors.append("16: 'Highest' must be ordered by rating from 5 down to 1 and then reviewId")
    if {i["reviewId"] for i in data["Success - Highest"]["items"]} != {i["reviewId"] for i in full}:
        errors.append("16: 'Highest' must list the same reviews as the default example")
    five = [r for r in full if r["rating"] == 5]
    if data["Success - Rating Filter"]["items"] != five or data["Success - Rating Filter"]["totalItems"] != len(five):
        errors.append("16: 'Rating Filter' must list exactly the reviews with rating 5 of the default example in the default order")
    return errors


def _neg_text(text: str):
    """Sort key that reverses the order of a text (so that a newer ISO timestamp sorts first)."""
    return [-ord(c) for c in text]


def check_review_spec() -> int:
    errors = []
    mds = {}
    for key, path in REVIEW_SPECS.items():
        try:
            mds[key] = read(path)
        except FileNotFoundError:
            errors.append(f"{path} does not exist")
            continue
        md = mds[key]
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        for bad in json_blocks_parse(md):
            errors.append(f"{path} invalid JSON block: {bad[:40]}")
        for link in relative_links_exist(path, md):
            errors.append(f"{path} broken link {link}")
        if not (ROOT / path).with_name("sequence.wsd").exists():
            errors.append(f"{path} has no sequence.wsd beside it")
        for leftover in re.findall(r"(?i)categor\w*|parent\w*|slug|E10007|Pending confirmation|decided by the lead SA|pending product owner confirmation", md):
            errors.append(f"{path} still mentions '{leftover}'")
    if errors:
        return fail("; ".join(errors))
    approval = "The rules of this section were approved by the product owner."
    page = "shop/04"
    needles = {
        "15": ["# [POST]: v1/shop/product-review/upsert", "- The caller is the user of the access token, never a field of the request", approval, "set by the delivery API (work package WP3)", page,
               "#### QUERY - Get the shop product that has a product page", "#### QUERY - Check that the caller has bought the product", "#### QUERY - Check existing review",
               "#### QUERY - Check duplicate review", "o.status = 'COMPLETED'",
               "WHERE r.id = '<sequence.id>'\nAND r.user_id = '<sequence.userId>'\nAND r.row_status = 'ACTIVE'",
               "WHERE r.shop_product_id = '<sequence.shopProductId>'\nAND r.user_id = '<sequence.userId>'\nAND r.row_status <> 'DELETED'",
               "(../../../schema/sales/t_order.md)", "(../../../schema/shop/t_shop_product_review.md)", "(../../../schema/shop/t_shop_product.md)",
               "You can review only a product that you have bought.", "You have already reviewed this product.", "Review not found.", "Product not found.",
               "Rating must be a whole number from 1 to 5.", "Comment must not be longer than 2000 characters.", "Shop Id and Product Id cannot be changed.",
               "Row status must be ACTIVE or DELETED, and must not be DELETED when inserting a review.", "There is no Archive for a customer.",
               "The rule is checked only when a review is inserted", "E10001", "E10002", "E10003", "E10004", "E10005", "E10009", "E90001", "Insert Shop Product Review Success"],
        "16": ["# [GET]: v1/storefront/product-review", "- This API is public: it needs no access token. The reviewer is shown only", approval, page, "#### Summary Object", "#### Breakdown Object", "#### Review Object",
               "#### QUERY - Get the summary of the reviews", "#### QUERY - Get the number of reviews of each rating", "#### QUERY - Get reviews", "#### QUERY - Get total items",
               "ROUND(AVG(r.rating), 2)", "ORDER BY r.created_at DESC, r.id", "-- ORDER BY r.rating DESC, r.id", "-- ORDER BY r.rating, r.id", "(../../../schema/authen/m_user.md)",
               "(../../../schema/shop/t_shop_product_review.md)", "Shop Id and Product Id are required fields.", "Product not found.", "Page Index and Page Size must be greater than 0",
               "Rating must be a whole number from 1 to 5 and Sort must be one of NEWEST, HIGHEST, LOWEST.", "public: it needs no access token",
               "Every sort ends with `reviewId` ascending as the tie-break", "Rounded half up to 2 decimals", "#### Success - Highest", "#### Success - Rating Filter", "E10001", "E10004", "E90001"],
    }
    for key, need in needles.items():
        moved = []
        for missing in missing_apart(mds[key], read(REVIEW_SPECS[key].replace("spec.md", "sequence.wsd")), need, moved):
            errors.append(f"{REVIEW_SPECS[key]} missing: {missing!r}")
    for forbidden in ("authorization", "Unauthorized", "E10002", "E10009"):
        if forbidden in mds["16"]:
            errors.append(f"{REVIEW_SPECS['16']} is public and must not contain '{forbidden}'")
    if re.search(r'"(userId|username|userName|email|emailAddress)"', mds["16"]) or re.search(r"\bu\.(username|email_address)\b", mds["16"]):
        errors.append(f"{REVIEW_SPECS['16']} must not return or select the user id, the user name or the email address of the reviewer")
    if not re.search(r"\| authorization +\| String +\| MANDATORY ", mds["15"]):
        errors.append("15: the upsert needs the authorization header as a MANDATORY header parameter")
    if errors:
        return fail("; ".join(errors))
    try:
        errors.extend(check_review_upsert_examples(mds["15"]))
        errors.extend(check_review_inquiry_examples(mds["16"]))
    except (KeyError, TypeError, AttributeError, ValueError, IndexError) as exc:
        errors.append(f"an example does not have the expected shape: {exc!r}")
    if errors:
        return fail("; ".join(errors))
    print("OK: shop-review-spec")
    return 0


COMMANDS["shop-review-spec"] = check_review_spec


def check_review_schema() -> int:
    """shop.t_shop_product_review: one review per user and shop product among the rows that are not DELETED."""
    errors = []
    sql = read("e-commerce/db/migrations/up/04-shop.schema.up.sql")
    statements = schema_statements(sql, "shop", "t_shop_product_review")
    create = [s for s in statements if s.startswith("CREATE TABLE")]
    if len(create) != 1 or "UNIQUE" in create[0]:
        errors.append("migration 04: t_shop_product_review must be created without an inline UNIQUE")
    elif "rating >= 1 AND rating <= 5" not in create[0]:
        errors.append("migration 04: the rating check 1 to 5 is missing")
    if REVIEW_INDEX not in statements:
        errors.append("migration 04: partial unique index uq_t_shop_product_review_shop_product_id_user_id is missing or different")
    path = "e-commerce/doc/schema/shop/t_shop_product_review.md"
    md = read(path)
    for bad in table_lines_aligned(md):
        errors.append(f"{path} misaligned table: {bad[:40]}")
    if schema_statements(" ".join(SQL_BLOCK.findall(md)), "shop", "t_shop_product_review") != statements:
        errors.append(f"{path} SQL differs from the migration")
    for needle in ("uq_t_shop_product_review_shop_product_id_user_id", "Unique among rows where row_status <> 'DELETED'"):
        if needle not in md:
            errors.append(f"{path} missing: {needle}")
    readme_rows = [line for line in read("e-commerce/doc/schema/README.md").split("\n") if "[t_shop_product_review]" in line]
    if len(readme_rows) != 1 or "| Transaction | 10 | 2 |" not in readme_rows[0]:
        errors.append("README: t_shop_product_review must have 10 columns and 2 FKs")
    test = ROOT / "e-commerce/db/tests/04-shop-review.test.sql"
    if not test.exists():
        errors.append("db/tests/04-shop-review.test.sql does not exist")
    else:
        text = test.read_text(encoding="utf-8")
        for n in range(1, 4):
            if f"PASS test {n}:" not in text:
                errors.append(f"04-shop-review.test.sql has no test {n}")
    if errors:
        return fail("; ".join(errors))
    print("OK: shop-review-schema")
    return 0


COMMANDS["shop-review-schema"] = check_review_schema


PAYMENT_SPECS = {
    "01": "e-commerce/doc/api/payment/01-start-payment/spec.md",
    "02": "e-commerce/doc/api/payment/02-stripe-webhook/spec.md",
    "03": "e-commerce/doc/api/payment/03-inquiry-payment/spec.md",
    "04": "e-commerce/doc/api/payment/04-inquiry-shop-payment/spec.md",
    "05": "e-commerce/doc/api/payment/05-refund-payment/spec.md",
}
PAYMENT_STATUSES = ["PENDING", "PROCESSING", "COMPLETED", "FAILED", "CANCELLED", "REFUNDED"]
SHIPPING_FEES = {"STANDARD": 40.00, "EXPRESS": 80.00, "SAME_DAY": 150.00}
WEBHOOK_ACTIONS = ["PAYMENT_PROCESSING", "PAYMENT_COMPLETED", "PAYMENT_FAILED", "PAYMENT_CANCELLED", "PAYMENT_REFUNDED", "LATE_PAYMENT_REFUNDED", "IGNORED"]
PROVIDER_ID_FIELDS = ("providerPaymentId", "providerRefundId", "transactionCode", "clientSecret")


def check_payment_start(md: str) -> list[str]:
    errors = []
    for k, ex in enumerate(order_examples(md, "Success")):
        d, tag = ex["data"], f"01 example {k}"
        if d["shippingFee"] != SHIPPING_FEES.get(d["shippingMethod"]):
            errors.append(f"{tag}: shippingFee {d['shippingFee']} is not the fee of {d['shippingMethod']}")
        if d["totalShipping"] != d["shippingFee"]:
            errors.append(f"{tag}: totalShipping should equal shippingFee")
        expected = round(d["totalPrice"] - d["totalDiscount"] + d["totalTax"] + d["totalShipping"], 2)
        if round(d["totalAmount"], 2) != expected or round(d["amount"], 2) != expected:
            errors.append(f"{tag}: totalAmount and amount should be {expected}")
        if d["status"] != "PENDING" or d["paymentMethod"] not in ("CREDIT_CARD", "THAI_QR"):
            errors.append(f"{tag}: a started payment is PENDING with CREDIT_CARD or THAI_QR")
        if d["currency"] != "THB" or not d["clientSecret"]:
            errors.append(f"{tag}: currency THB and a client secret are required")
    return errors


def check_payment_webhook(md: str) -> list[str]:
    errors = []
    for title in ("Success", "Success - Ignored", "Success - Late Payment Refunded"):
        for ex in order_examples(md, title):
            d = ex["data"]
            if d["action"] not in WEBHOOK_ACTIONS:
                errors.append(f"02 {title}: unknown action {d['action']}")
            if (d["action"] == "IGNORED") != (d["paymentId"] is None and d["orderId"] is None):
                errors.append(f"02 {title}: IGNORED goes with a null paymentId and orderId, other actions with both")
    body = re.search(r"#### Example Body Parameters\n\n```JSON\n(.*?)```", md, re.DOTALL)
    if not body:
        errors.append("02: no example body")
    else:
        event = json.loads(body.group(1))
        if event["type"] != "payment_intent.succeeded" or not event["data"]["object"]["id"].startswith("pi_"):
            errors.append("02: the example event should be payment_intent.succeeded of a PaymentIntent (pi_)")
    return errors


def check_payment_inquiry(md: str, key: str) -> list[str]:
    errors = []
    for k, ex in enumerate(order_examples(md, "Success")):
        data = ex["data"]
        if data["totalPages"] != -(-data["totalItems"] // data["pageSize"]):
            errors.append(f"{key} example {k}: totalPages does not match totalItems and pageSize")
        if data["totalPages"] <= 1 and data["totalItems"] != len(data["payments"]):
            errors.append(f"{key} example {k}: one page holds every payment, totalItems should be {len(data['payments'])}")
        for p in data["payments"]:
            label = f"{key} payment {p['paymentId']}"
            if p["status"] not in PAYMENT_STATUSES:
                errors.append(f"{label}: unknown status {p['status']}")
            if p["shippingFee"] != SHIPPING_FEES.get(p["shippingMethod"]):
                errors.append(f"{label}: shippingFee is not the fee of {p['shippingMethod']}")
            if (p["failureCode"] is not None) != (p["status"] == "FAILED"):
                errors.append(f"{label}: failureCode goes with FAILED only")
            if (p["refundedAt"] is not None) != (p["status"] == "REFUNDED") or (p["refundReason"] is not None) != (p["status"] == "REFUNDED"):
                errors.append(f"{label}: refundedAt and refundReason go with REFUNDED only")
            if (p["transactionAt"] is not None) != (p["status"] in ("COMPLETED", "REFUNDED")):
                errors.append(f"{label}: transactionAt goes with COMPLETED or REFUNDED only")
            if key == "03" and any(f in p for f in PROVIDER_ID_FIELDS):
                errors.append(f"{label}: the customer must not see the ids of the provider")
            if key == "04":
                for f in ("providerPaymentId", "providerRefundId"):
                    if f not in p:
                        errors.append(f"{label}: {f} must stay as a key")
                    elif p[f] is not None:
                        errors.append(f"{label}: {f} is null for the members of the shop")
    return errors


def check_payment_refund(md: str) -> list[str]:
    errors = []
    for ex in order_examples(md, "Success"):
        d = ex["data"]
        if d["status"] != "REFUNDED" or d["orderStatus"] != "REFUNDED" or not d["restoredItems"]:
            errors.append("05: a refund makes the payment and the order REFUNDED and gives items back")
    return errors


def check_payment_spec() -> int:
    errors = []
    mds = {}
    for key, path in PAYMENT_SPECS.items():
        try:
            mds[key] = read(path)
        except FileNotFoundError:
            errors.append(f"{path} does not exist")
            continue
        md = mds[key]
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        for bad in json_blocks_parse(md):
            errors.append(f"{path} invalid JSON block: {bad[:40]}")
        for link in relative_links_exist(path, md):
            errors.append(f"{path} broken link {link}")
    if errors:
        return fail("; ".join(errors))
    needles = {
        "01": ["- Only the owner of the order can pay it", "CASH_ON_DELIVERY", "uq_t_payment_order_id_live", "payment-<orderId>-<attempt>-<paymentMethod>-<shippingMethod>", "cancel-<paymentIntentId>",
               "#### QUERY - Count the payments of the order", "If the `COMMIT` fails after Stripe answered", "approved by the product owner on 2026-11-08", "clientSecret", "amount x 100", "#### Fail - Conflict Payment In Progress",
               "#### INSERT - Create the payment", "#### UPDATE - Set the shipping fee and the amount of the order", "AND status = 'WAIT_PAYMENT'", "FOR UPDATE", "E10006", "E90001"],
        "02": ["- The endpoint is public", "stripe-signature", "raw body", "5 minutes", "LATE_PAYMENT_REFUNDED", "IGNORED", "payment_intent.succeeded", "charge.refunded",
               "#### UPDATE - Mark the payment as completed", "#### UPDATE - Confirm the order", "AND status = 'WAIT_PAYMENT'", "#### UPDATE - Mark the payment as refunded",
               "#### UPDATE - Give the quantity back to the lot", "idempotent", "E10001",
               "ORDER BY oi.lot_id", "VALUES ('system', '<sequence.campaignBudgetId>'", "has `system` in `created_by` or `updated_by`", "refund-<paymentId>", "also makes the database match when another API called Stripe"],
        "03": ["- Only the payments of the orders of the user", "ORDER BY p.created_at DESC, p.id", "o.user_id = '<sequence.userId>'", "#### QUERY - Count the payments of the user", "ILIKE"],
        "04": ["- A member of the shop (an ACTIVE", "E10009", "#### Fail - Forbidden", "#### QUERY - Check shop member", "#### QUERY - Check active credential and user",
               "the role `PLATFORM_ADMIN` in the verified `roles` claim", "do not query `author.m_role` or `author.t_user_role`",
               "providerPaymentId", "ORDER BY p.created_at DESC, p.id", "#### QUERY - Count the payments of the shop"],
        "05": ["- A member of the shop of the order", "#### UPDATE - Refund the payment", "AND status = 'COMPLETED'", "#### UPDATE - Refund the order", "AND status = 'PAYMENT_CONFIRMED'",
               "#### UPDATE - Give the quantity back to the lot", "refund-", "E10006", "E10009", "restoredItems", "#### QUERY - Check shop member", "FOR UPDATE -- taken before the payment is changed",
               "#### QUERY - Lock the caller user", "#### QUERY - Check current credential and user", "do not query `author.m_role` or `author.t_user_role`",
               "ORDER BY oi.lot_id", "`Idempotency-Key` `refund-<paymentId>`", "If the `COMMIT` fails after Stripe refunded", "approved by the product owner on 2026-11-08"],
    }
    for key, need in needles.items():
        # rules that moved into a note of the sequence diagram are searched there, one line per wrapped note
        seq = re.sub(r"\n\s+", " ", read(PAYMENT_SPECS[key].replace("spec.md", "sequence.wsd")))
        for missing in missing_needles(mds[key] + "\n" + seq, need):
            errors.append(f"{PAYMENT_SPECS[key]} missing: {missing}")
    for key, want in {"01": {"Success": 201, "Success - Reused": 200}, "02": {"Success": 200, "Success - Ignored": 200, "Success - Late Payment Refunded": 200},
                      "03": {"Success": 200, "Success - Empty": 200}, "04": {"Success": 200, "Success - Empty": 200}, "05": {"Success": 200}}.items():
        if success_codes(mds[key]) != want:
            errors.append(f"{PAYMENT_SPECS[key]}: success examples should be {want}, found {success_codes(mds[key])}")
    for key in ("01", "03", "05"):
        params = re.search(r"### (?:Query|Body) Parameters.*?(?=\n### |\n#### Example|\n## )", mds[key], re.DOTALL)
        if params and "userId" in params.group(0):
            errors.append(f"{PAYMENT_SPECS[key]}: the request must not carry a user id")
    body1 = re.search(r"### Body Parameters.*?(?=\n### )", mds["01"], re.DOTALL)
    if body1 and re.search(r"\|\s*(amount|shippingFee|currency)\s*\|", body1.group(0)):
        errors.append(f"{PAYMENT_SPECS['01']}: the client never sends an amount, a fee or a currency")
    if "authorization" in re.search(r"### Header Parameters.*?(?=\n### )", mds["02"], re.DOTALL).group(0):
        errors.append(f"{PAYMENT_SPECS['02']}: the webhook is public, it has no authorization header")
    for key in ("01", "03", "04", "05"):
        for forbidden in ("cardNumber", "card_number", "cvc", "cvv"):
            if forbidden in mds[key]:
                errors.append(f"{PAYMENT_SPECS[key]} must not contain '{forbidden}': card data never reaches the API")
    if "E10009" in mds["01"] or "E10009" in mds["03"] or "E10009" in mds["02"]:
        errors.append("01-03: only the shop APIs use the forbidden code E10009")
    errors.extend(check_payment_start(mds["01"]))
    errors.extend(check_payment_webhook(mds["02"]))
    errors.extend(check_payment_inquiry(mds["03"], "03"))
    errors.extend(check_payment_inquiry(mds["04"], "04"))
    errors.extend(check_payment_refund(mds["05"]))
    if errors:
        return fail("; ".join(errors))
    print("OK: payment-spec")
    return 0


COMMANDS["payment-spec"] = check_payment_spec


PAYMENT_LIVE_INDEX = ("CREATE UNIQUE INDEX IF NOT EXISTS uq_t_payment_order_id_live ON payment.t_payment (order_id) "
                      "WHERE status IN ('PENDING', 'PROCESSING', 'COMPLETED') AND row_status = 'ACTIVE'")
PAYMENT_COLUMNS = ["provider", "provider_payment_id", "currency", "shipping_method", "shipping_fee", "failure_code", "failure_message",
                   "provider_refund_id", "refunded_at", "refund_reason"]
PAYMENT_CONSTRAINTS = ["ck_t_payment_paid_has_transaction_at", "ck_t_payment_refund_details", "ck_t_payment_failure_only_when_failed",
                       "uq_t_payment_order_id_live", "uq_t_payment_provider_payment_id", "uq_t_payment_provider_refund_id",
                       "ck_t_payment_shipping_method", "ck_t_payment_shipping_fee", "ck_t_payment_currency", "ck_t_payment_provider"]


def check_payment_schema() -> int:
    """payment.t_payment: one row is one Stripe PaymentIntent, one live payment per order, refund details, RESTRICT on the order."""
    errors = []
    sql = read("e-commerce/db/migrations/up/07-payment.schema.up.sql")
    statements = schema_statements(sql, "payment", "t_payment")
    create = [s for s in statements if s.startswith("CREATE TABLE")]
    if len(create) != 1:
        errors.append("migration 07: t_payment must have exactly one CREATE TABLE")
    else:
        if "ON DELETE RESTRICT" not in create[0] or "ON DELETE CASCADE" in create[0]:
            errors.append("migration 07: t_payment.order_id must be ON DELETE RESTRICT")
        for column in PAYMENT_COLUMNS:
            if not re.search(rf"\b{column}\b", create[0]):
                errors.append(f"migration 07: column {column} is missing")
        for text in ("provider_payment_id VARCHAR(64) NOT NULL UNIQUE", "provider_refund_id VARCHAR(64) UNIQUE", "shipping_fee NUMERIC(16, 2) NOT NULL DEFAULT 0.00",
                     "shipping_method VARCHAR(32) NOT NULL"):
            if text not in create[0]:
                errors.append(f"migration 07: missing {text}")
    if PAYMENT_LIVE_INDEX not in statements:
        errors.append("migration 07: partial unique index uq_t_payment_order_id_live is missing or different")
    path = "e-commerce/doc/schema/payment/t_payment.md"
    md = read(path)
    for bad in table_lines_aligned(md):
        errors.append(f"{path} misaligned table: {bad[:40]}")
    if schema_statements(" ".join(SQL_BLOCK.findall(md)), "payment", "t_payment") != statements:
        errors.append(f"{path} SQL differs from the migration")
    for name in PAYMENT_CONSTRAINTS + PAYMENT_COLUMNS:
        if f"| {name} " not in md:
            errors.append(f"{path} missing row: {name}")
    if "ON DELETE RESTRICT" not in md:
        errors.append(f"{path} must say ON DELETE RESTRICT")
    readme = read("e-commerce/doc/schema/README.md")
    if "| [t_payment](payment/t_payment.md) | Transaction | 23 | 1 |" not in readme:
        errors.append("README: t_payment should have 23 columns and 1 FK")
    test = ROOT / "e-commerce/db/tests/07-payment.test.sql"
    if not test.exists():
        errors.append("db/tests/07-payment.test.sql does not exist")
    else:
        text = test.read_text(encoding="utf-8")
        for n in range(1, 8):
            if f"PASS test {n}:" not in text:
                errors.append(f"07-payment.test.sql has no test {n}")
    if errors:
        return fail("; ".join(errors))
    print("OK: payment-schema")
    return 0


COMMANDS["payment-schema"] = check_payment_schema


SHIPPING_SCHEMA_DOC = "e-commerce/doc/schema/shipping"
SHIPPING_MIGRATION = "e-commerce/db/migrations/up/08-shipping.schema.up.sql"
SHIPPING_INDEXES = {
    "t_shipping": ("CREATE UNIQUE INDEX IF NOT EXISTS uq_t_shipping_carrier_name_tracking_number ON shipping.t_shipping (carrier_name, tracking_number) "
                   "WHERE tracking_number IS NOT NULL AND row_status <> 'DELETED'"),
    "t_shipping_item": ("CREATE UNIQUE INDEX IF NOT EXISTS uq_t_shipping_item_shipping_id_order_item_id ON shipping.t_shipping_item "
                        "(shipping_id, order_item_id) WHERE row_status <> 'DELETED'"),
    "t_shipping_stop": ("CREATE UNIQUE INDEX IF NOT EXISTS uq_t_shipping_stop_shipping_id_stop_number ON shipping.t_shipping_stop "
                        "(shipping_id, stop_number) WHERE row_status <> 'DELETED'"),
}
# the index that the automatic completion job needs (S26, S31): not unique, partial on the SHIPPED parcels
SHIPPING_SCAN_INDEX = ("CREATE INDEX IF NOT EXISTS ix_t_shipping_shipped_at ON shipping.t_shipping (shipped_at) "
                       "WHERE status = 'SHIPPED' AND row_status <> 'DELETED'")
SHIPPING_TABLE_PARTS = {
    "t_shipping": [
        "order_id UUID NOT NULL REFERENCES sales.t_order (id) ON DELETE RESTRICT",
        "carrier_name VARCHAR(64),",
        "tracking_number VARCHAR(64),",
        "CONSTRAINT ck_t_shipping_shipped_has_tracking CHECK ( status NOT IN ('SHIPPED', 'DELIVERED', 'RETURNED') OR ( carrier_name IS NOT NULL "
        "AND tracking_number IS NOT NULL AND shipped_at IS NOT NULL ) )",
        "CONSTRAINT ck_t_shipping_delivered_at CHECK ( (status = 'DELIVERED') = (delivered_at IS NOT NULL) )",
        "'PENDING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED'",
    ],
    "t_shipping_item": [
        "shipping_id UUID NOT NULL REFERENCES shipping.t_shipping (id) ON DELETE CASCADE",
        "order_item_id UUID NOT NULL REFERENCES sales.t_order_item (id) ON DELETE RESTRICT",
    ],
    "t_shipping_stop": [
        "shipping_id UUID NOT NULL REFERENCES shipping.t_shipping (id) ON DELETE CASCADE",
        "stop_type IN ('PICKUP', 'TRANSIT', 'DROPOFF')",
        "arrived_at TIMESTAMP WITHOUT TIME ZONE",
    ],
}
SHIPPING_DOC_NEEDLES = {
    "t_shipping": ["uq_t_shipping_carrier_name_tracking_number", "ix_t_shipping_shipped_at", "ck_t_shipping_shipped_has_tracking", "ck_t_shipping_delivered_at",
                   "ON DELETE RESTRICT", "carrier_name", "Unique among rows where row_status <> 'DELETED' and tracking_number is not null"],
    "t_shipping_item": ["uq_t_shipping_item_shipping_id_order_item_id", "ON DELETE RESTRICT", "Unique among rows where row_status <> 'DELETED'"],
    "t_shipping_stop": ["uq_t_shipping_stop_shipping_id_stop_number", "TRANSIT", "arrived_at", "Unique among rows where row_status <> 'DELETED'"],
}
SHIPPING_README_ROWS = {
    "t_shipping": "| [t_shipping](shipping/t_shipping.md) | Transaction | 13 | 1 |",
    "t_shipping_item": "| [t_shipping_item](shipping/t_shipping_item.md) | Transaction | 9 | 2 |",
    "t_shipping_stop": "| [t_shipping_stop](shipping/t_shipping_stop.md) | Transaction | 12 | 1 |",
}


def check_shipping_schema() -> int:
    """shipping.*: tracking number per carrier, status checks, one row per item and stop number, history protected."""
    errors = []
    sql = read(SHIPPING_MIGRATION)
    for table, parts in SHIPPING_TABLE_PARTS.items():
        statements = schema_statements(sql, "shipping", table)
        create = [s for s in statements if s.startswith("CREATE TABLE")]
        if len(create) != 1:
            errors.append(f"migration 08: {table} must be created exactly once")
            continue
        if "UNIQUE" in create[0]:
            errors.append(f"migration 08: {table} must be created without an inline UNIQUE (a partial unique index is used)")
        for part in parts:
            if normalize(part) not in create[0]:
                errors.append(f"migration 08: {table} is missing: {part[:70]}")
        if SHIPPING_INDEXES[table] not in statements:
            errors.append(f"migration 08: the partial unique index of {table} is missing or different")
        path = f"{SHIPPING_SCHEMA_DOC}/{table}.md"
        md = read(path)
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        if schema_statements(" ".join(SQL_BLOCK.findall(md)), "shipping", table) != statements:
            errors.append(f"{path} SQL differs from the migration")
        for needle in SHIPPING_DOC_NEEDLES[table]:
            if needle not in md:
                errors.append(f"{path} missing: {needle}")
    migration_statements = [normalize(x) for x in sql.split(";")]
    if SHIPPING_SCAN_INDEX not in migration_statements:
        errors.append("migration 08: the partial index ix_t_shipping_shipped_at on shipped_at is missing or different")
    doc_sql = [normalize(x) for x in " ".join(SQL_BLOCK.findall(read(f"{SHIPPING_SCHEMA_DOC}/t_shipping.md"))).split(";")]
    if SHIPPING_SCAN_INDEX not in doc_sql:
        errors.append("t_shipping.md: the SQL block does not hold ix_t_shipping_shipped_at")
    readme = read("e-commerce/doc/schema/README.md")
    for table, row in SHIPPING_README_ROWS.items():
        if row not in readme:
            errors.append(f"README missing: {row}")
    er = read("e-commerce/db/er-diagram.drawio")
    if "UK    tracking_number" in er:
        errors.append("ER diagram: tracking_number is no longer a plain UNIQUE column")
    for column in ("carrier_name : varchar(64)", "arrived_at : timestamp"):
        if er.count(column) != 2:
            errors.append(f"ER diagram: '{column}' must be drawn on page 6 and on page 8")
    test = ROOT / "e-commerce/db/tests/08-shipping.test.sql"
    if not test.exists():
        errors.append("db/tests/08-shipping.test.sql does not exist")
    else:
        text = test.read_text(encoding="utf-8")
        for n in range(1, 8):
            if f"PASS test {n}:" not in text:
                errors.append(f"08-shipping.test.sql has no test {n}")
    if errors:
        return fail("; ".join(errors))
    print("OK: shipping-schema")
    return 0


COMMANDS["shipping-schema"] = check_shipping_schema


SHIPPING_SPECS = {
    "01": "e-commerce/doc/api/shipping/01-create-shipping/spec.md",
    "02": "e-commerce/doc/api/shipping/02-update-shipping-status/spec.md",
    "03": "e-commerce/doc/api/shipping/03-upsert-shipping-stop/spec.md",
    "04": "e-commerce/doc/api/shipping/04-inquiry-shop-shipping/spec.md",
    "05": "e-commerce/doc/api/shipping/05-inquiry-shipping/spec.md",
    "06": "e-commerce/doc/api/shipping/06-confirm-delivery/spec.md",
}
SHIPPING_SUCCESS_CODES = {
    "01": {"Success - First Shipping": 201, "Success - Second Shipping": 201},
    "02": {"Success - Shipped": 200, "Success - Cancelled": 200, "Success - Returned": 200},
    "03": {"Success - Insert": 201, "Success - Update": 200, "Success - Delete": 204, "Success - Archive": 200},
    "04": {"Success": 200, "Success - Empty": 200},
    "05": {"Success": 200, "Success - Empty": 200},
    "06": {"Success - Order Still Processing": 200, "Success - Order Completed": 200},
}
SHIPPING_NEEDLES = {
    "01": ["- The caller must be an ACTIVE member of the shop of the order", "#### QUERY - Lock the order", "FOR UPDATE", "#### UPDATE - Start processing", "AND status = 'PAYMENT_CONFIRMED'",
           "#### QUERY - Get the quantity already assigned", "AND s.status IN ('PENDING', 'SHIPPED', 'DELIVERED')", "#### QUERY - Get the shipping method of the order",
           "p.status = 'COMPLETED'", "#### INSERT - Create the shipping", "#### INSERT - Add the items to the shipping", "#### Fail - Conflict Quantity",
           "#### Fail - Conflict Order Status", "#### Fail - Not Found Reference", "#### Fail - Forbidden", "E10009", "E10006",
           "validate the request (400) -> existence of the order and of the order items (404) -> permission of the caller (403)",
           "approved by the product owner", "#### QUERY - Check shop member", "#### QUERY - Check platform administrator"],
    "02": ["- The caller must be an ACTIVE member of the shop of the order", "`PENDING` -> `SHIPPED`", "`PENDING` -> `CANCELLED`", "`SHIPPED` -> `RETURNED`", "#### UPDATE - Mark the shipping as shipped",
           "#### UPDATE - Cancel the shipping", "#### UPDATE - Mark the shipping as returned", "AND status = 'PENDING' -- no row changed means the status changed in the meantime",
           "AND status = 'SHIPPED' -- no row changed means the status changed in the meantime", "#### QUERY - Check duplicate tracking number",
           "#### QUERY - Count the shippings that are still active", "#### UPDATE - Give the order back to PAYMENT_CONFIRMED", "AND status = 'PROCESSING'",
           "#### QUERY - Lock the order", "FOR UPDATE", "#### Fail - Conflict Tracking Number", "#### Fail - Conflict Status", "E10003", "E10006", "E10009",
           "approved by the product owner", "#### QUERY - Check shop member", "#### QUERY - Check platform administrator", "#### QUERY - Lock the shipping", "FOR UPDATE -- read again after the order row is locked", "the status step is checked on that second read", "approved by the product owner on 2026-11-08"],
    "03": ["- The caller must be an ACTIVE member of the shop of the order", "#### INSERT - Create the stop", "#### UPDATE - Update, delete or archive the stop", "#### QUERY - Check duplicate stop number",
           "#### QUERY - Lock the order", "FOR UPDATE", "#### Fail - Bad Request Row Status", "#### Fail - Conflict Status", "E10003", "E10006", "E10009",
           "Delete 204 No Content (no response body)", "approved by the product owner", "#### QUERY - Check shop member", "#### Fail - Not Found Shipping", "`Shipping not found.`", "approved by the product owner on 2026-11-08"],
    "04": ["- The caller must be an ACTIVE member of the shop (", "E10009", "#### Fail - Forbidden", "#### Fail - Not Found Reference", "#### QUERY - Check shop member",
           "#### QUERY - Check platform administrator", "#### QUERY - Check shop", "ORDER BY s.created_at DESC, s.id", "o.shop_id = '<sequence.shopId>'",
           "#### QUERY - Count the shippings of the shop", "#### QUERY - Get the stops of the shippings", "o.ship_address", "approved by the product owner"],
    "05": ["- Only the shippings of the orders of the user", "ORDER BY s.created_at DESC, s.id", "o.user_id = '<sequence.userId>'", "#### QUERY - Count the shippings of the user",
           "ss.row_status = 'ACTIVE'", "sh.name ILIKE", "#### QUERY - Get the stops of the shippings", "approved by the product owner"],
    "06": ["- Only the owner of the order (the user of the access token) can confirm", "#### UPDATE - Confirm the delivery", "AND status = 'SHIPPED' -- no row changed means the status changed in the meantime",
           "#### UPDATE - Complete the order", "AND status = 'PROCESSING'", "#### QUERY - Get the delivered quantity of every item", "s.status = 'DELIVERED'",
           "o.user_id = '<sequence.userId>'", "#### QUERY - Lock the order", "FOR UPDATE", "#### Fail - Conflict Status", "E10006",
           "approved by the product owner",
           "- A job (a scheduled task of the system", "**Automatic Completion Example**", "#### QUERY - Get the orders with an old SHIPPED parcel",
           "#### UPDATE - Confirm the delivery as the system", "#### QUERY - Check that the order qualifies", "updated_by = 'system'",
           "AND status = 'SHIPPED' -- no row changed means the shippings changed in the meantime", "`completion_days`",
           "AND s.shipped_at > NOW() AT TIME ZONE 'UTC' - INTERVAL '<sequence.completionDays> days'", "AND s2.status IN ('SHIPPED', 'DELIVERED')",
           "AND s.shipped_at <= NOW() AT TIME ZONE 'UTC' - INTERVAL '<sequence.completionDays> days'", "ix_t_shipping_shipped_at", "never by the shop",
           "so the shop has to record a returned parcel before the seven days are over", "A partial shipment that cannot be finished",
           "locks the order row first (`SELECT ... FOR UPDATE`), checks the five conditions again under the lock",
           "and by the automatic completion below (the system confirms after `completion_days`", "at least `completion_days` days old", "#### QUERY - Lock the shipping", "FOR UPDATE -- read again after the order row is locked", "the status is checked on that second read", "approved by the product owner on 2026-11-08"],
}
# phrases that must appear at least n times (a rule or a guard that two statements share must not lose one copy unnoticed)
SHIPPING_COUNTS = {
    "01": {"approved by the product owner": 2},
    "02": {"AND status = 'PENDING' -- no row changed means the status changed in the meantime": 2,
           "AND status = 'SHIPPED' -- no row changed means the status changed in the meantime": 1, "approved by the product owner": 2},
    "03": {"approved by the product owner": 2},
    "04": {"o.shop_id = '<sequence.shopId>'": 2, "approved by the product owner": 2, "-- only when search is specified": 2},
    "05": {"o.user_id = '<sequence.userId>'": 2, "approved by the product owner": 1, "-- only when search is specified": 2},
    "06": {"approved by the product owner": 1, "AND s.row_status <> 'DELETED'": 6, "AND s.status = 'SHIPPED'": 2, "AND s.status = 'PENDING'": 1},
}
SHIPPING_STATUSES = ("PENDING", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED")
SHIPPING_STOP_TYPES = ("PICKUP", "TRANSIT", "DROPOFF")
# quantities of the order items in the examples (sales/04 and sales/05 use the same ids)
SHIPPING_ORDER_ITEM_QUANTITY = {"e1f2a3b4-3c4d-4e5f-9a6b-7c8d9e0f1a21": 2, "e2a3b4c5-4d5e-4f60-8b7c-8d9e0f1a2b32": 1}


def check_shipping_row(label: str, s: dict, shop_side: bool) -> list[str]:
    """One shipping of an inquiry example: the columns that must go together with the status."""
    errors = []
    status = s.get("status")
    if status not in SHIPPING_STATUSES:
        errors.append(f"{label}: unknown status {status}")
    shipped = status in ("SHIPPED", "DELIVERED", "RETURNED")
    for key in ("carrierName", "trackingNumber", "shippedAt"):
        if (s.get(key) is not None) != shipped:
            errors.append(f"{label}: {key} must be {'set' if shipped else 'null'} when the status is {status}")
    if (s.get("deliveredAt") is not None) != (status == "DELIVERED"):
        errors.append(f"{label}: deliveredAt must be set exactly when the status is DELIVERED")
    stops = s.get("stops", [])
    numbers = [p["stopNumber"] for p in stops]
    if numbers != sorted(set(numbers)):
        errors.append(f"{label}: stops must be in stopNumber order without a duplicate number")
    for p in stops:
        if p["stopType"] not in SHIPPING_STOP_TYPES:
            errors.append(f"{label}: unknown stop type {p['stopType']}")
        if ("rowStatus" in p) != shop_side:
            errors.append(f"{label}: stop rowStatus is returned to the shop only")
        if shop_side and p["rowStatus"] == "DELETED":
            errors.append(f"{label}: a DELETED stop is never returned")
    for item in s.get("items", []):
        if not isinstance(item["quantity"], int) or item["quantity"] < 1:
            errors.append(f"{label}: item quantity must be a positive integer")
        want = SHIPPING_ORDER_ITEM_QUANTITY.get(item["orderItemId"])
        if want is not None and item["quantity"] > want:
            errors.append(f"{label}: item quantity {item['quantity']} is more than the {want} that was ordered")
    if ("shippingAddress" in s) != shop_side:
        errors.append(f"{label}: shippingAddress is returned to the shop only")
    if ("shop" in s) == shop_side:
        errors.append(f"{label}: the shop object is returned to the customer only")
    return errors


def check_shipping_inquiry(md: str, key: str) -> list[str]:
    errors = []
    shop_side = key == "04"
    names = {}
    for title in ("Success", "Success - Empty"):
        body = json_examples(md, title)
        if body is None:
            errors.append(f"{key}: no JSON in '{title}'")
            continue
        data = body["data"]
        rows = data["shippings"]
        if title == "Success - Empty" and (rows or data["totalItems"] != 0 or data["totalPages"] != 0):
            errors.append(f"{key}: the empty example must have no shippings, totalItems 0 and totalPages 0")
        if data["totalItems"] != len(rows) and data["totalPages"] <= 1:
            errors.append(f"{key} '{title}': totalItems {data['totalItems']} is not the number of shippings {len(rows)} on a single page")
        if data["totalPages"] != -(-data["totalItems"] // data["pageSize"]):
            errors.append(f"{key} '{title}': totalPages is not the ceiling of totalItems / pageSize")
        created = [r["createdAt"] for r in rows]
        if created != sorted(created, reverse=True):
            errors.append(f"{key} '{title}': shippings must be newest first")
        for i, r in enumerate(rows):
            errors.extend(check_shipping_row(f"{key} '{title}' shippings[{i}]", r, shop_side))
            for item in r["items"]:
                names.setdefault(item["skuId"], set()).add((item["productName"], item["skuName"]))
    for sku, found in names.items():
        if len(found) > 1:
            errors.append(f"{key}: the SKU {sku} has different names in the examples")
    if shop_side and "shopId" not in md.split("## Example Request")[0]:
        errors.append("04: shopId must be a query parameter")
    if not shop_side:
        params = re.search(r"### Query Parameters.*?(?=\n### )", md, re.DOTALL)
        if params and ("userId" in params.group(0) or "shopId" in params.group(0)):
            errors.append("05: the request must not carry a user id or a shop id")
    return errors


def check_shipping_actions(mds: dict) -> list[str]:
    """Examples of the write APIs: the order status that follows the shipping status, and ids that agree with the request."""
    errors = []
    # 01
    for title, status_before in (("Success - First Shipping", "PAYMENT_CONFIRMED"), ("Success - Second Shipping", "PROCESSING")):
        body = json_examples(mds["01"], title)
        if body is None:
            errors.append(f"01: no JSON in '{title}'")
            continue
        data = body["data"]
        if data["orderStatus"] != "PROCESSING" or data["status"] != "PENDING":
            errors.append(f"01 '{title}': a new shipping is PENDING and the order is PROCESSING after the request")
        if data["shippingMethod"] not in ("STANDARD", "EXPRESS", "SAME_DAY"):
            errors.append(f"01 '{title}': unknown shipping method")
        for item in data["items"]:
            want = SHIPPING_ORDER_ITEM_QUANTITY.get(item["orderItemId"])
            if want is not None and item["quantity"] > want:
                errors.append(f"01 '{title}': quantity {item['quantity']} is more than the {want} that was ordered")
    request = json.loads(re.search(r"### HTTP Request\n\n```HTTP\n.*?\n\n(\{.*?\})\n```", mds["01"], re.DOTALL).group(1))
    request_part = mds["01"].split("## Request Parameters")[1].split("## Example Request")[0]
    if "shippingMethod" in request or "shippingMethod" in request_part:
        errors.append("01: the request must not carry shippingMethod (it is copied from the payment)")
    first = json_examples(mds["01"], "Success - First Shipping")
    if first and first["data"]["orderId"] != request["orderId"]:
        errors.append("01: the first example answers a different orderId than the request")
    # 02
    want = {"Success - Shipped": ("SHIPPED", "PROCESSING", True), "Success - Cancelled": ("CANCELLED", "PROCESSING", False),
            "Success - Returned": ("RETURNED", "PAYMENT_CONFIRMED", True)}
    for title, (status, order_status, has_track) in want.items():
        body = json_examples(mds["02"], title)
        if body is None:
            errors.append(f"02: no JSON in '{title}'")
            continue
        data = body["data"]
        if data["status"] != status:
            errors.append(f"02 '{title}': status must be {status}")
        if data["orderStatus"] != order_status:
            errors.append(f"02 '{title}': orderStatus must be {order_status}")
        for key in ("carrierName", "trackingNumber", "shippedAt"):
            if (data[key] is not None) != has_track:
                errors.append(f"02 '{title}': {key} must be {'set' if has_track else 'null'}")
    bodies = re.findall(r"#### Example Body Parameters\n\n(.*?)\n\n## Example Request", mds["02"], re.DOTALL)
    blocks = [json.loads(b) for b in re.findall(r"```JSON\n(.*?)```", bodies[0], re.DOTALL)] if bodies else []
    if [b["status"] for b in blocks] != ["SHIPPED", "CANCELLED", "RETURNED"]:
        errors.append("02: the example bodies must be SHIPPED, CANCELLED and RETURNED")
    for b in blocks:
        has = "carrierName" in b or "trackingNumber" in b
        if has != (b["status"] == "SHIPPED"):
            errors.append("02: carrierName and trackingNumber belong to the SHIPPED example only")
    # 03
    stop_ids = {}
    bodies = re.search(r"#### Example Body Parameters\n\n(.*?)\n\n## Example Request", mds["03"], re.DOTALL)
    blocks = [json.loads(b) for b in re.findall(r"```JSON\n(.*?)```", bodies.group(1), re.DOTALL)] if bodies else []
    if len(blocks) != 4:
        errors.append("03: expected four example bodies (insert, update, delete, archive)")
    else:
        insert, update, delete, archive = blocks
        if "id" in insert or not all("id" in b for b in (update, delete, archive)):
            errors.append("03: insert has no id, update, delete and archive have one")
        if delete.get("rowStatus") != "DELETED" or archive.get("rowStatus") != "ARCHIVED":
            errors.append("03: the delete and archive examples need rowStatus DELETED and ARCHIVED")
        if len({b["shippingId"] for b in blocks}) != 1:
            errors.append("03: the examples must use one shippingId")
        for title, b in (("Success - Insert", insert), ("Success - Update", update), ("Success - Archive", archive)):
            body = json_examples(mds["03"], title)
            if body is None:
                errors.append(f"03: no JSON in '{title}'")
                continue
            data = body["data"]
            if data["shippingId"] != b["shippingId"] or data["stopNumber"] != b["stopNumber"] or data["stopType"] != b["stopType"]:
                errors.append(f"03 '{title}': the answer does not match the request body")
            if "id" in b and data["stopId"] != b["id"]:
                errors.append(f"03 '{title}': the answer has a different stopId than the request")
        inserted = json_examples(mds["03"], "Success - Insert")
        if inserted and inserted["data"]["stopId"] != update["id"]:
            errors.append("03: the update example must change the stop that the insert example created")
        if json_examples(mds["03"], "Success - Archive")["data"]["rowStatus"] != "ARCHIVED":
            errors.append("03: the archive example must answer rowStatus ARCHIVED")
        if json_examples(mds["03"], "Success - Insert")["data"]["arrivedAt"] is not None:
            errors.append("03: a stop that was just inserted has not arrived yet")
        if {b["stopType"] for b in blocks} - set(SHIPPING_STOP_TYPES):
            errors.append("03: unknown stop type in an example body")
        if update["id"] == delete["id"] or update["id"] == archive["id"] or delete["id"] == archive["id"]:
            errors.append("03: the update, delete and archive examples must use different stops")
        if len({delete["stopNumber"], archive["stopNumber"], update["stopNumber"]}) != 3 or insert["stopNumber"] != update["stopNumber"]:
            errors.append("03: the insert and update examples are the same stop, the delete and archive examples are other stops with other numbers")
    # 06
    for title, order_status in (("Success - Order Still Processing", "PROCESSING"), ("Success - Order Completed", "COMPLETED")):
        body = json_examples(mds["06"], title)
        if body is None:
            errors.append(f"06: no JSON in '{title}'")
            continue
        data = body["data"]
        if data["status"] != "DELIVERED" or data["deliveredAt"] is None:
            errors.append(f"06 '{title}': the shipping is DELIVERED with deliveredAt")
        if data["orderStatus"] != order_status:
            errors.append(f"06 '{title}': orderStatus must be {order_status}")
    request = json.loads(re.search(r"### HTTP Request\n\n```HTTP\n.*?\n\n(\{.*?\})\n```", mds["06"], re.DOTALL).group(1))
    first = json_examples(mds["06"], "Success - Order Still Processing")
    if first and first["data"]["shippingId"] != request["shippingId"]:
        errors.append("06: the first example answers a different shippingId than the request")
    return errors


SHIPPING_JOB_PHRASE = "Time the customer or the system confirmed the parcel (UTC)"


def check_shipping_job_example(md: str) -> list[str]:
    """The Automatic Completion Example of spec 06: every case is judged again with the five conditions and compared with the result that is written."""
    m = re.search(r"\*\*Automatic Completion Example\*\*\n\n(.*?)\n\n((?:\|[^\n]*\n)+)", md, re.DOTALL)
    if not m:
        return ["06: the Automatic Completion Example table is missing"]
    day = re.search(r"runs on day (\d+) with `completion_days` (\d+)", m.group(1))
    quantity = re.search(r"quantity (\d+)", m.group(1))
    if not day or not quantity:
        return ["06: the example must say the day of the job, completion_days and the quantity of the item"]
    now, days, ordered = int(day.group(1)), int(day.group(2)), int(quantity.group(1))
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in m.group(2).strip().split("\n")][2:]
    errors, results = [], set()
    for case, parcels, result, reason in rows:
        items = []
        for part in parcels.split(";"):
            tokens = part.split()
            status = tokens[1]
            shipped = next((int(t[1:]) for t in tokens if re.fullmatch(r"d\d+", t)), None)
            qty = next(int(t[1:]) for t in tokens if re.fullmatch(r"q\d+", t))
            items.append((status, shipped, qty))
        statuses = [x[0] for x in items]
        allocated = sum(q for st, _, q in items if st in ("SHIPPED", "DELIVERED"))
        if "SHIPPED" not in statuses:
            expected = "NOT A CANDIDATE"
        elif "PENDING" in statuses:
            expected = "WAITS"
        elif allocated != ordered:
            expected = "NOT ELIGIBLE"
        elif any(st == "SHIPPED" and now - d < days for st, d, _ in items):
            expected = "WAITS"
        else:
            expected = "COMPLETES"
        results.add(expected)
        if result != expected:
            errors.append(f"06 automatic completion case {case}: the five conditions give {expected}, the example says {result}")
        if expected == "COMPLETES" and "COMPLETED" not in reason:
            errors.append(f"06 automatic completion case {case}: a case that completes must say that the order is COMPLETED")
        if result == "COMPLETES" and any(st == "DELIVERED" for st in statuses) and "only" not in reason.lower():
            errors.append(f"06 automatic completion case {case}: a shipping that is already DELIVERED is not changed, the reason must say that only the SHIPPED ones change")
    if results != {"COMPLETES", "WAITS", "NOT ELIGIBLE", "NOT A CANDIDATE"}:
        errors.append("06: the example must show the four results COMPLETES, WAITS, NOT ELIGIBLE and NOT A CANDIDATE")
    return errors


# the scan query of the job must hold every condition that can be tested without a lock, or an order that can never qualify
# keeps an old SHIPPED parcel, is selected in every run and fills the batch before an order with a larger id (the job starves)
SHIPPING_SCAN_PARTS = {
    "the order must be PROCESSING": "o.status = 'PROCESSING'",
    "the order must not be DELETED": "o.row_status <> 'DELETED'",
    "a SHIPPED shipping at least completion_days old": "AND s.shipped_at <= NOW() AT TIME ZONE 'UTC' - INTERVAL '<sequence.completionDays> days'",
    "no PENDING shipping (condition 2)": "AND NOT EXISTS (\n    SELECT 1\n    FROM shipping.t_shipping s\n    WHERE s.order_id = o.id\n    AND s.row_status <> 'DELETED'\n    AND s.status = 'PENDING'\n)",
    "no SHIPPED shipping younger than completion_days (condition 5)": "AND s.shipped_at > NOW() AT TIME ZONE 'UTC' - INTERVAL '<sequence.completionDays> days'",
    "every item allocated in full (condition 4)": "AND oi.quantity <> (",
    "the allocation counts only SHIPPED and DELIVERED shippings": "AND s2.status IN ('SHIPPED', 'DELIVERED')",
    "a fixed ascending order and one batch": "ORDER BY o.id\nLIMIT <sequence.batchSize>",
}


def check_shipping_scan_query(md: str) -> list[str]:
    m = re.search(r"#### QUERY - Get the orders with an old SHIPPED parcel\n\n```SQL\n(.*?)\n```", md, re.DOTALL)
    if not m:
        return ["06: the scan query 'Get the orders with an old SHIPPED parcel' is missing"]
    sql = m.group(1)
    errors = [f"06 scan query: {why} is missing, an order that never qualifies would fill the batch and starve the others"
              for why, part in SHIPPING_SCAN_PARTS.items() if part not in sql]
    if "s.shipped_at > NOW()" in sql and sql.count("NOT EXISTS") < 3:
        errors.append("06 scan query: the three NOT EXISTS (PENDING, young SHIPPED, item not allocated) must stay NOT EXISTS")
    for needle in ("so a dead-end order like case 4 cannot block the orders after it", "(the job starves)"):
        if needle not in md:
            errors.append(f"06: the reason why the scan applies every condition is missing: {needle}")
    return errors


def check_shipping_spec() -> int:
    errors = []
    mds = {}
    for key, path in SHIPPING_SPECS.items():
        try:
            mds[key] = read(path)
        except FileNotFoundError:
            errors.append(f"{path} does not exist")
            continue
        md = mds[key]
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        for bad in json_blocks_parse(md):
            errors.append(f"{path} invalid JSON block: {bad[:40]}")
        for link in relative_links_exist(path, md):
            errors.append(f"{path} broken link {link}")
    if errors:
        return fail("; ".join(errors))
    # rules that moved into a note of the sequence diagram are searched there, one line per wrapped note
    full = {k: v + "\n" + re.sub(r"\n\s+", " ", read(SHIPPING_SPECS[k].replace("spec.md", "sequence.wsd"))) for k, v in mds.items()}
    for key, need in SHIPPING_NEEDLES.items():
        for missing in missing_needles(full[key], need):
            errors.append(f"{SHIPPING_SPECS[key]} missing: {missing}")
    for key, counts in SHIPPING_COUNTS.items():
        for phrase, n in counts.items():
            if full[key].count(phrase) < n:
                errors.append(f"{SHIPPING_SPECS[key]}: '{phrase[:60]}' must appear at least {n} times, found {full[key].count(phrase)}")
    for key, want in SHIPPING_SUCCESS_CODES.items():
        if success_codes(mds[key]) != want:
            errors.append(f"{SHIPPING_SPECS[key]}: success examples should be {want}, found {success_codes(mds[key])}")
    for key in ("01", "02", "03", "05", "06"):
        params = re.search(r"### (?:Query|Body) Parameters.*?(?=\n### |\n#### Example|\n## )", mds[key], re.DOTALL)
        if params and "userId" in params.group(0):
            errors.append(f"{SHIPPING_SPECS[key]}: the request must not carry a user id")
    for key in ("05", "06"):
        if "E10009" in mds[key]:
            errors.append(f"{SHIPPING_SPECS[key]}: the customer APIs do not use the forbidden code E10009 (another user's row is not found)")
    for key, md in mds.items():
        for forbidden in ("email", "username", "costPrice", "cost_price", "platformProfit", "grossProfit", "shopProfit", "margin"):
            if forbidden in md:
                errors.append(f"{SHIPPING_SPECS[key]} must not contain '{forbidden}'")
    for key in ("01", "02", "03", "06"):
        rules = full[key]
        if "SELECT ... FOR UPDATE" not in rules:
            errors.append(f"{SHIPPING_SPECS[key]}: the rules must say that the order row is locked with SELECT ... FOR UPDATE")
    for key in ("04", "05", "06"):
        if SHIPPING_JOB_PHRASE not in mds[key]:
            errors.append(f"{SHIPPING_SPECS[key]}: deliveredAt must be described as '{SHIPPING_JOB_PHRASE}' (the system can confirm too)")
        if "Time the receiver confirmed the parcel (UTC)" in mds[key]:
            errors.append(f"{SHIPPING_SPECS[key]}: the old deliveredAt wording (only the receiver confirms) must not stay")
    if "There is no automatic completion" in mds["06"]:
        errors.append("06: the sentence that there is no automatic completion must not stay")
    errors.extend(check_shipping_job_example(mds["06"]))
    errors.extend(check_shipping_scan_query(full["06"]))
    errors.extend(check_shipping_inquiry(mds["04"], "04"))
    errors.extend(check_shipping_inquiry(mds["05"], "05"))
    errors.extend(check_shipping_actions(mds))
    # the same SKU has the same name in the shop and the customer inquiry
    names = {}
    for key in ("04", "05"):
        body = json_examples(mds[key], "Success")
        if body:
            for r in body["data"]["shippings"]:
                for item in r["items"]:
                    names.setdefault(item["skuId"], set()).add((item["productName"], item["skuName"]))
    for sku, found in names.items():
        if len(found) > 1:
            errors.append(f"04 and 05: the SKU {sku} has different product or SKU names")
    if errors:
        return fail("; ".join(errors))
    print("OK: shipping-spec")
    return 0


COMMANDS["shipping-spec"] = check_shipping_spec


# ---------------------------------------------------------------- master tables (WP6): product type, product brand, consent type
MASTER_API = "e-commerce/doc/api"
MASTER = {
    "product-type": dict(
        path="product-type", group="product", nums=("10", "11", "12"), folder=("upsert-product-type", "upsert-product-type-batch", "inquiry-product-type"),
        title="Product Type", lower="product type", camel="productType", alias="pt", table="product.m_product_type", doc="product/m_product_type.md",
        use_table="product.m_product", use_alias="p", use_col="type_id", use_doc="product/m_product.md", use_thing="product", use_things="products",
        id="a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d", other_spec=("product/01-upsert-product/spec.md", '"typeId"'), consent=False),
    "product-brand": dict(
        path="product-brand", group="product", nums=("13", "14", "15"), folder=("upsert-product-brand", "upsert-product-brand-batch", "inquiry-product-brand"),
        title="Product Brand", lower="product brand", camel="productBrand", alias="pb", table="product.m_product_brand", doc="product/m_product_brand.md",
        use_table="product.m_product", use_alias="p", use_col="brand_id", use_doc="product/m_product.md", use_thing="product", use_things="products",
        id="c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f", other_spec=("product/01-upsert-product/spec.md", '"brandId"'), consent=False),
    "consent-type": dict(
        path="consent/type", group="consent", nums=("06", "07", "08"), folder=("upsert-consent-type", "upsert-consent-type-batch", "inquiry-consent-type"),
        title="Consent Type", lower="consent type", camel="consentType", alias="ct", table="consent.m_consent_type", doc="consent/m_consent_type.md",
        use_table="consent.t_consent", use_alias="c", use_col="consent_type_id", use_doc="consent/t_consent.md", use_thing="consent", use_things="consents",
        id="a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d", other_spec=("consent/02-upsert-consent/spec.md", '"consentTypeId"'), consent=True),
}
MASTER_GROUPS = {"product-master": ("product-type", "product-brand"), "consent-type": ("consent-type",)}
SINGLE_UPSERT_SPECS.extend(f"{MASTER_API}/{m['group']}/{m['nums'][0]}-{m['folder'][0]}/spec.md" for m in MASTER.values())
BATCH_UPSERT_SPECS.extend(f"{MASTER_API}/{m['group']}/{m['nums'][1]}-{m['folder'][1]}/spec.md" for m in MASTER.values())


def master_path(m: dict, i: int) -> str:
    return f"{MASTER_API}/{m['group']}/{m['nums'][i]}-{m['folder'][i]}/spec.md"


def master_cap(text: str) -> str:
    return text[0].upper() + text[1:]


def master_needles(m: dict) -> list[dict]:
    lower, cap, alias, camel = m["lower"], master_cap(m["lower"]), m["alias"], m["camel"]
    ua, uc = m["use_alias"], m["use_col"]
    admin = ["- Permission:", "E10009", "#### Fail - Forbidden", "#### QUERY - Get the platform administrator role", "#### QUERY - Check platform administrator",
             "(../../../schema/author/m_role.md)", "(../../../schema/author/t_user_role.md)", "WHERE r.name = 'PLATFORM_ADMIN'", "AND r.row_status = 'ACTIVE'",
             "AND ur.role_id = '<sequence.roleId>'", "AND ur.row_status = 'ACTIVE'", f"You do not have permission to change {lower}s.",
             "Approved by the product owner"]
    upsert = [f"# [POST]: v1/{m['path']}/upsert", f"### {m['title']} Rules", "-> permission (403, E10009) -> duplicate name check", f"(../../../schema/{m['doc']})",
              f"(../../../schema/{m['use_doc']})", f"#### QUERY - Check {m['use_thing']} in use", f"WHERE {ua}.{uc} = '<sequence.id>' -- only when rowStatus is DELETED or ARCHIVED",
              f"AND {ua}.row_status <> 'DELETED'", f"AND {alias}.row_status <> 'DELETED'\nAND {alias}.id <> '<sequence.id>'", f"{cap} name already exists.",
              f"{cap} is used by {m['use_things']}.", f"{cap} not found.", f"Row status must not be DELETED when inserting a {lower}.", "E10003", "E10004",
              "E10006", "E90001", f"Insert {m['title']} Success", f"Archive {m['title']} Success", f"AND {alias}.row_status <> 'DELETED' -- the id of a DELETED {lower} counts as not found",
              f"The name of a DELETED {lower} can be used again.", "are allowed even when", "blocks the writes that use it"] + admin
    batch = [f"# [POST]: v1/{m['path']}/upsert/batch", f"### {m['title']} Rules (same as the single upsert, applied per {lower})", f"#### QUERY - Check {m['use_thing']} in use",
             f"{camel}s[2]: Id is duplicated with {camel}s[1].", f"{camel}s[2]: Name is duplicated with {camel}s[0].", f"{cap}s must contain 1 to 100 items.",
             "Swapping the names", f"{camel}s[2]: {cap} is used by {m['use_things']}.", f"AND {alias}.row_status <> 'DELETED'\nAND {alias}.id <> '<sequence.{camel}s.id>'",
             f"WHERE {ua}.{uc} = '<sequence.{camel}s.id>' -- only when rowStatus is DELETED or ARCHIVED", f"{camel}s[0]: {cap} name already exists.",
             f"{camel}s[1]: {cap} not found.", "so the 403 message has no item position", "Batch Upsert " + m["title"] + " Success"] + admin
    inquiry = [f"# [GET]: v1/{m['path']}", f"#### QUERY - Get {lower}s", "#### QUERY - Get total items", "ILIKE", f"### {m['title']} Inquiry Rules", f"ORDER BY {alias}.created_at DESC, {alias}.id",
               "Page Index and Page Size must be greater than 0", "Row status must be one of ACTIVE, INACTIVE, LOCKED, ARCHIVED.", "authorization",
               f"Request: `GET v1/{m['path']}?id={m['id']}`", f"WHERE {alias}.row_status <> 'DELETED'", f"Inquiry {m['title']} Success", "no role is checked"]
    if not m["consent"]:
        # The rules of the order of the checks and the permission are in the note of sequence.wsd (see master_diagram_needles).
        for lst, moved in ((upsert, [f"### {m['title']} Rules", "-> permission (403, E10009) -> duplicate name check", "- Permission:"]),
                           (batch, [f"### {m['title']} Rules (same as the single upsert, applied per {lower})", "so the 403 message has no item position", "- Permission:"]),
                           (inquiry, [f"### {m['title']} Inquiry Rules"])):
            for text in moved:
                lst.remove(text)
    if m["consent"]:
        upsert.extend(["`description` and `isRequired` are optional"])
        for lst in (upsert, batch):
            lst.extend(["Name is a required field.", "is_required", "isRequired", "null clears it"])
        inquiry.extend(["isRequired", "ct.is_required", "AND ct.is_required = '<sequence.isRequired>' -- only when isRequired is specified"])
    return [{"upsert": upsert, "batch": batch, "inquiry": inquiry}]


def master_diagram_needles(m: dict) -> dict:
    """What the note of sequence.wsd must say for the product type and product brand (the consent type keeps these rules in its spec)."""
    if m["consent"]:
        return {"upsert": [], "batch": []}
    admin = "only a platform administrator (a user with an ACTIVE author.t_user_role row for the ACTIVE role PLATFORM_ADMIN)"
    return {"upsert": [f"Permission: {admin}", "-> permission (403, E10009) -> duplicate name check"],
            "batch": ["Permission: the same as the single upsert, only a platform administrator", "so the 403 message has no item position"]}


def master_counted(m: dict) -> dict:
    """Texts that must appear an exact number of times (both inquiry queries carry the same filters)."""
    alias, camel = m["alias"], m["camel"]
    counted = {"inquiry": [(f"AND ({alias}.name ILIKE '%<sequence.search>%' OR {alias}.description ILIKE '%<sequence.search>%') -- only when search is specified", 2),
                           (f"WHERE {alias}.row_status <> 'DELETED'\nAND {alias}.id = '<sequence.id>' -- only when id is specified", 2),
                           (f"AND {alias}.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified", 2)],
               "upsert": [], "batch": []}
    if m["consent"]:
        counted["inquiry"] += [("AND ct.is_required = '<sequence.isRequired>' -- only when isRequired is specified", 2), ("    ct.is_required,\n    ct.row_status", 1)]
        counted["upsert"] += [("    description,\n    is_required\n)", 1), ("    '<sequence.isRequired>'\n)", 1),
                              ("    is_required = '<sequence.isRequired>' -- only when isRequired is specified", 1)]
        counted["batch"] += [("    description,\n    is_required\n)", 1), (f"    '<sequence.{camel}s.isRequired>'\n)", 1),
                             (f"    is_required = '<sequence.{camel}s.isRequired>' -- only when isRequired is specified", 1)]
    return counted


MASTER_FORBIDDEN = {
    "upsert": [], "batch": [], "inquiry": ["Fail - Forbidden", "E10009", "PLATFORM_ADMIN", "t_user_role"],
}


def master_errors_upsert(m: dict, md: str) -> list[str]:
    errors = []
    cid = m["camel"] + "Id"
    update = json.loads(re.search(r"##### Update\n\n```JSON\n(.*?)```", md, re.DOTALL).group(1))
    delete = json.loads(re.search(r"##### Delete\n\n```JSON\n(.*?)```", md, re.DOTALL).group(1))
    insert = json.loads(re.search(r"##### Insert\n\n```JSON\n(.*?)```", md, re.DOTALL).group(1))
    if "id" in insert:
        errors.append("the Insert example must not have an id")
    if update["id"] != m["id"] or delete["id"] != m["id"]:
        errors.append(f"the Update and Delete examples must use the id {m['id']}")
    if update.get("rowStatus") != "ACTIVE" or delete.get("rowStatus") != "DELETED":
        errors.append("Update must be ACTIVE and Delete must be DELETED")
    for label, body in (("Insert", insert), ("Update", update), ("Delete", delete)):
        if not body.get("name"):
            errors.append(f"the {label} example has no name (required in every request)")
        if len(body["name"]) > 128 or len(body.get("description") or "") > (1000 if m["consent"] else 256):
            errors.append(f"the {label} example is longer than the limit")
        if not m["consent"] and not body.get("description"):
            errors.append(f"the {label} example has no description (required)")
        if m["consent"] and not isinstance(body.get("isRequired"), bool):
            errors.append(f"the {label} example needs a boolean isRequired")
    for title in ("Success - Insert", "Success - Update", "Success - Archive"):
        body = json_examples(md, title)
        if body is None:
            errors.append(f"no JSON in '{title}'")
        elif body["data"][cid] != m["id"]:
            errors.append(f"'{title}' answers a different {cid} than the Update example")
    forbidden = json_examples(md, "Fail - Forbidden")
    if not forbidden or forbidden["status"]["code"] != 403 or forbidden["status"]["bizCode"] != "E10009":
        errors.append("the Forbidden example must be 403 E10009")
    for title, code, biz in (("Fail - Bad Request", 400, "E10001"), ("Fail - Not Found", 404, "E10004"), ("Fail - Conflict", 409, "E10003"), ("Fail - Conflict In Use", 409, "E10006"),
                             ("Fail - Unauthorized", 401, "E10002"), ("Fail - Request Timeout", 408, "E90001")):
        body = json_examples(md, title)
        if not body or body["status"]["code"] != code or body["status"]["bizCode"] != biz:
            errors.append(f"'{title}' must be {code} {biz}")
    return errors


def master_errors_batch(m: dict, md: str) -> list[str]:
    errors = []
    key, cid = m["camel"] + "s", m["camel"] + "Id"
    request = json.loads(re.search(r"#### Example Body Parameters\n\n```JSON\n(.*?)```", md, re.DOTALL).group(1))
    items = request[key]
    result = json_examples(md, "Success")["data"][key]
    if len(result) != len(items):
        errors.append(f"{len(result)} results for {len(items)} request items")
    ids = [i["id"] for i in items if "id" in i]
    if len(ids) != len(set(ids)):
        errors.append("the request example repeats an id")
    names = [i["name"] for i in items if i.get("rowStatus") != "DELETED"]
    if len(names) != len(set(names)):
        errors.append("the request example repeats a name among the items that are not DELETED")
    for position, (item, res) in enumerate(zip(items, result)):
        action = {"DELETED": "DELETE", "ARCHIVED": "ARCHIVE"}.get(item.get("rowStatus"), "UPDATE" if "id" in item else "INSERT")
        if "id" not in item and item.get("rowStatus") == "DELETED":
            errors.append(f"request item {position} deletes without an id")
        if res["index"] != position or res["action"] != action:
            errors.append(f"result {position} should be index {position}, action {action}, found {res['index']}/{res['action']}")
        if "id" in item and res[cid] != item["id"]:
            errors.append(f"result {position} answers a different {cid} than the request item")
        if m["consent"] and not isinstance(item.get("isRequired"), bool):
            errors.append(f"request item {position} needs a boolean isRequired")
        if not item.get("name"):
            errors.append(f"request item {position} has no name")
    forbidden = json_examples(md, "Fail - Forbidden")
    if not forbidden or forbidden["status"]["code"] != 403 or forbidden["status"]["bizCode"] != "E10009" or "[" in forbidden["status"]["bizMessage"]:
        errors.append("the Forbidden example must be 403 E10009 without an item position")
    for title in ("Fail - Bad Request", "Fail - Not Found", "Fail - Conflict", "Fail - Conflict In Use", "Fail - Bad Request Duplicate Id", "Fail - Bad Request Duplicate Name", "Fail - Bad Request Row Status"):
        body = json_examples(md, title)
        if not body or f"{key}[" not in body["status"]["bizMessage"]:
            errors.append(f"'{title}' must start its message with the position ({key}[i])")
    return errors


def master_json(md: str, heading: str):
    """Parsed JSON of the first ```JSON block under '#### <heading>', an optional 'Request: ...' line may come first."""
    match = re.search(rf"^#### {re.escape(heading)}\n\n(?:Request: [^\n]*\n\n)?```JSON\n(.*?)```", md, re.MULTILINE | re.DOTALL)
    return json.loads(match.group(1)) if match else None


def master_errors_inquiry(m: dict, md: str) -> list[str]:
    errors = []
    cid = m["camel"] + "Id"
    by_id = re.search(r"Request: `GET v1/[^`]*\?id=([0-9a-f-]{36})`", md).group(1)
    for title in ("Success", "Success - By Id", "Success - Not Found"):
        data = master_json(md, title)["data"]
        if data["totalItems"] != len(data["items"]):
            errors.append(f"'{title}' totalItems differs from the number of items")
        expected_pages = 0 if data["totalItems"] == 0 else -(-data["totalItems"] // data["pageSize"])
        if data["totalPages"] != expected_pages:
            errors.append(f"'{title}' totalPages should be {expected_pages}")
        if any(item["rowStatus"] == "DELETED" for item in data["items"]):
            errors.append(f"'{title}' lists a DELETED {m['lower']}")
        ids = [item[cid] for item in data["items"]]
        if len(ids) != len(set(ids)):
            errors.append(f"'{title}' repeats an id")
        if m["consent"] and any(not isinstance(item.get("isRequired"), bool) for item in data["items"]):
            errors.append(f"'{title}' needs a boolean isRequired on every item")
        if title == "Success - By Id" and ids != [by_id]:
            errors.append("the By Id example must list only the id of its request")
        if title == "Success - Not Found" and data["items"]:
            errors.append("the Not Found example must have no items")
    if by_id != m["id"]:
        errors.append(f"the By Id example must use the id {m['id']}")
    for title, code, biz in (("Fail - Bad Request", 400, "E10001"), ("Fail - Bad Request Row Status", 400, "E10001"), ("Fail - Unauthorized", 401, "E10002"), ("Fail - Request Timeout", 408, "E90001")):
        body = master_json(md, title)
        if not body or body["status"]["code"] != code or body["status"]["bizCode"] != biz:
            errors.append(f"'{title}' must be {code} {biz}")
    return errors


# Needles of a master spec whose sentence now lives in a note of its sequence (moved by the template alignment) and needles whose text is gone by design
MASTER_SEQUENCE_NEEDLES = {
    "consent-type/upsert": ['-> permission (403, E10009) -> duplicate name check',
           'The name of a DELETED consent type can be used again.',
           'are allowed even when',
           'blocks the writes that use it',
           'Approved by the product owner',
           '`description` and `isRequired` are optional'],
    "consent-type/batch": ['so the 403 message has no item position',
           'Approved by the product owner'],
}
MASTER_REMOVED_NEEDLES = {
    "consent-type/upsert": ['### Consent Type Rules'],
    "consent-type/batch": ['### Consent Type Rules (same as the single upsert, applied per consent type)',
           '- Permission:'],
    "consent-type/inquiry": ['### Consent Type Inquiry Rules'],
}


def check_master_spec(names: tuple[str, ...], label: str) -> int:
    errors = []
    for name in names:
        m = MASTER[name]
        mds = {}
        for i, kind in enumerate(("upsert", "batch", "inquiry")):
            path = master_path(m, i)
            try:
                md = read(path)
            except FileNotFoundError:
                errors.append(f"{path} does not exist")
                continue
            mds[kind] = md
            for bad in table_lines_aligned(md):
                errors.append(f"{path} misaligned table: {bad[:40]}")
            for bad in json_blocks_parse(md):
                errors.append(f"{path} invalid JSON block: {bad[:40]}")
            for link in relative_links_exist(path, md):
                errors.append(f"{path} broken link {link}")
            for leftover in re.findall(r"(?i)shop\w*|slug|parent\w*|categor\w*", md):
                errors.append(f"{path} still mentions '{leftover}' (copied from the prototype)")
            if "ALTER TABLE" in md:
                errors.append(f"{path} contains ALTER TABLE")
            if not (ROOT / path).with_name("sequence.wsd").exists():
                errors.append(f"{path} has no sequence.wsd beside it")
            in_sequence = MASTER_SEQUENCE_NEEDLES.get(f"{name}/{kind}", [])
            for missing in missing_needles(md, [x for x in master_needles(m)[0][kind] if x not in in_sequence and x not in MASTER_REMOVED_NEEDLES.get(f"{name}/{kind}", [])]):
                errors.append(f"{path} missing: {missing!r}")
            sequence_note = " ".join((ROOT / path).with_name("sequence.wsd").read_text(encoding="utf-8").split()) if (ROOT / path).with_name("sequence.wsd").exists() else ""
            for missing in missing_needles(sequence_note, in_sequence):
                errors.append(f"{path} sequence note missing: {missing!r}")
            for text, times in master_counted(m)[kind]:
                if md.count(text) != times:
                    errors.append(f"{path}: {text!r} must appear {times} time(s), found {md.count(text)}")
            diagram_path = str(Path(path).with_name("sequence.wsd"))
            if (ROOT / diagram_path).exists():
                for missing in missing_needles(read(diagram_path), master_diagram_needles(m).get(kind, [])):
                    errors.append(f"{diagram_path} missing: {missing!r}")
            for forbidden in MASTER_FORBIDDEN[kind]:
                if forbidden in md:
                    errors.append(f"{path} must not contain {forbidden!r} (the inquiry has no role check)")
        if errors:
            continue
        for kind in ("upsert", "batch"):
            for forbidden in ("pageSize", "pageIndex"):
                if forbidden in mds[kind]:
                    errors.append(f"{master_path(m, 0 if kind == 'upsert' else 1)} must not contain '{forbidden}'")
        try:
            errors.extend(f"{master_path(m, 0)}: {e}" for e in master_errors_upsert(m, mds["upsert"]))
            errors.extend(f"{master_path(m, 1)}: {e}" for e in master_errors_batch(m, mds["batch"]))
            errors.extend(f"{master_path(m, 2)}: {e}" for e in master_errors_inquiry(m, mds["inquiry"]))
        except (KeyError, TypeError, AttributeError, ValueError) as exc:
            errors.append(f"an example of {name} does not have the expected shape: {exc!r}")
        other, key = m["other_spec"]
        other_md = read(f"{MASTER_API}/{other}")
        if f'{key}: "{m["id"]}"' not in other_md:
            errors.append(f"the example id of {name} no longer matches {key} in {other}")
        codes = success_codes(mds["upsert"])
        if codes != {"Success - Insert": 201, "Success - Update": 200, "Success - Delete": 204, "Success - Archive": 200}:
            errors.append(f"{master_path(m, 0)}: wrong success codes {codes}")
        if set(success_codes(mds["batch"]).values()) != {200}:
            errors.append(f"{master_path(m, 1)}: every success example must answer 200")
    if errors:
        return fail("; ".join(errors))
    print(f"OK: {label}")
    return 0


COMMANDS["product-master-spec"] = lambda: check_master_spec(MASTER_GROUPS["product-master"], "product-master-spec")
COMMANDS["consent-type-spec"] = lambda: check_master_spec(MASTER_GROUPS["consent-type"], "consent-type-spec")


def er_name_rows(table: str) -> list[str]:
    """Value of the 'name' row of every <table> drawn in the ER diagram (one per page that draws it)."""
    import xml.etree.ElementTree as ET

    root = ET.fromstring(read("e-commerce/db/er-diagram.drawio"))
    cells = list(root.iter("mxCell"))
    rows = []
    for cell in cells:
        if cell.get("value") == table:
            for child in cells:
                if child.get("parent") == cell.get("id") and re.search(r"\bname :", child.get("value") or ""):
                    rows.append(child.get("value"))
    return rows


def check_master_schema(tables: list[str], migration: str, fk_table: tuple[str, str, str], test: str, label: str) -> int:
    """name is unique among rows that are not DELETED and the foreign keys into the table are RESTRICT (migration, docs, ER, DB test)."""
    errors = []
    sql = read(f"e-commerce/db/migrations/up/{migration}")
    for qualified in tables:
        schema, table = qualified.split(".")
        statements = schema_statements(sql, schema, table)
        create = [s for s in statements if s.startswith("CREATE TABLE")]
        if len(create) != 1 or "UNIQUE" in create[0]:
            errors.append(f"migration {migration}: {table} must be created without an inline UNIQUE")
        index = f"CREATE UNIQUE INDEX IF NOT EXISTS uq_{table} _name ON {qualified} (name) WHERE row_status <> 'DELETED'".replace("uq_" + table + " _name", f"uq_{table}_name")
        if index not in statements:
            errors.append(f"migration {migration}: partial unique index uq_{table}_name is missing or different")
        path = f"e-commerce/doc/schema/{schema}/{table}.md"
        md = read(path)
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        if schema_statements(" ".join(SQL_BLOCK.findall(md)), schema, table) != statements:
            errors.append(f"{path} SQL differs from the migration")
        if re.search(r"^\| UQ\s+\|.*\| name ", md, re.MULTILINE):
            errors.append(f"{path} still marks name as UQ")
        for needle in (f"uq_{table}_name", "Unique among rows where row_status <> 'DELETED'"):
            if needle not in md:
                errors.append(f"{path} missing: {needle}")
        rows = er_name_rows(qualified)
        if len(rows) < 2:
            errors.append(f"ER diagram: expected {table} on at least 2 pages, found {len(rows)}")
        for row in rows:
            if row.startswith("UK"):
                errors.append(f"ER diagram: {table}.name still carries the UK marker")
    child_sql = sql if fk_table[0] == migration else read(f"e-commerce/db/migrations/up/{fk_table[0]}")
    child_doc = read(f"e-commerce/doc/schema/{fk_table[1]}.md")
    for column, parent in fk_table[2]:
        fk = f"{column} UUID NOT NULL REFERENCES {parent} (id) ON DELETE RESTRICT"
        if fk not in child_sql:
            errors.append(f"migration {fk_table[0]}: {column} must be ON DELETE RESTRICT")
        if fk not in child_doc:
            errors.append(f"e-commerce/doc/schema/{fk_table[1]}.md: SQL for {column} must say ON DELETE RESTRICT")
        if f"References {parent}(id), ON DELETE RESTRICT" not in child_doc:
            errors.append(f"e-commerce/doc/schema/{fk_table[1]}.md: the constraint table must say ON DELETE RESTRICT for {column}")
    if not (ROOT / f"e-commerce/db/tests/{test}").exists():
        errors.append(f"db/tests/{test} does not exist")
    if errors:
        return fail("; ".join(errors))
    print(f"OK: {label}")
    return 0


COMMANDS["product-master-schema"] = lambda: check_master_schema(
    ["product.m_product_type", "product.m_product_brand"], "03-product.schema.up.sql",
    ("03-product.schema.up.sql", "product/m_product", [("type_id", "product.m_product_type"), ("brand_id", "product.m_product_brand")]),
    "03-product-master.test.sql", "product-master-schema")
COMMANDS["consent-type-schema"] = lambda: check_master_schema(
    ["consent.m_consent_type"], "00-common.schema.up.sql",
    ("00-common.schema.up.sql", "consent/t_consent", [("consent_type_id", "consent.m_consent_type")]),
    "00-consent-type.test.sql", "consent-type-schema")


# ---------------------------------------------------------------- authen (WP4): tokens, reset password, profile, address
AUTHEN_DIR = "e-commerce/doc/api/authen-and-author"
AUTHEN_SPECS = {
    "01": f"{AUTHEN_DIR}/01-register/spec.md",
    "02": f"{AUTHEN_DIR}/02-login/spec.md",
    "03": f"{AUTHEN_DIR}/03-reset-password/spec.md",
    "04": f"{AUTHEN_DIR}/04-create-new-password/spec.md",
    "05": f"{AUTHEN_DIR}/05-refresh-token/spec.md",
    "06": f"{AUTHEN_DIR}/06-logout/spec.md",
    "07": f"{AUTHEN_DIR}/07-upsert-user-profile/spec.md",
    "08": f"{AUTHEN_DIR}/08-inquiry-user-profile/spec.md",
    "09": f"{AUTHEN_DIR}/09-upsert-user-address/spec.md",
    "10": f"{AUTHEN_DIR}/10-inquiry-user-address/spec.md",
}
AUTHEN_LOCK = "FOR UPDATE -- every authen API locks the user row first"
AUTHEN_POLICY = "Password must be 8 to 128 characters and contain an upper-case letter, a lower-case letter and a digit."
AUTHEN_ADDRESS_ID = "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a"
AUTHEN_NEEDLES = {
    "01": ["#### Fail - Bad Request Password",
           "TRUE, -- the first address of a user is the default address, whatever isDefault says",
           "PBKDF2-HMAC-SHA256",
           "Plain text over TLS",
           AUTHEN_POLICY],
    "02": ["(../../../schema/authen/l_user_login_attempt.md)",
           "#### QUERY - Count failed attempts",
           "#### INSERT - Record attempt",
           "#### INSERT - Create access token",
           "#### INSERT - Create refresh token",
           '"expiresIn": 900',
           "AND la.result = 'FAILED' -- refused attempts are never counted",
           "'<sequence.result>' -- SUCCESS, FAILED or REFUSED",
           "One answer for every failure",
           "Invalid username or password.",
           AUTHEN_LOCK,
           "14 days",
           "'<sequence.sessionId>', -- a new session id for every login",
           "author.t_user_role",
           "author.m_role",
           "author.t_role_permission",
           "author.t_role_permission_scope",
           "author.t_user_permission",
           "author.t_permission_scope",
           "author.m_permission",
           "author.m_scope"],
    "03": ["# [POST]: v1/auth/reset-password",
           "The answer is always 200 with the same message",
           "If the email address is registered, a reset link has been sent.",
           "Throttle:",
           "3 times per hour",
           "#### QUERY - Lock the user",
           AUTHEN_LOCK,
           "#### QUERY - Count the requests of the last hour",
           "#### UPDATE - Make the old reset token INACTIVE",
           "#### INSERT - Create reset token",
           "WHERE u.email_address = '<sequence.emailAddressBytes>'\nAND u.row_status = 'ACTIVE'",
           "'<sequence.resetTokenHash>'",
           "30 minutes",
           "(../../../schema/authen/t_user_reset_password.md)",
           "(../../../schema/authen/m_user.md)",
           "Email Address is required and must be a valid email address.",
           "E10001",
           "E90001",
           "AND rp.created_at > '<sequence.windowStart>'",
           "AND row_status = 'ACTIVE'"],
    "04": ["# [POST]: v1/auth/create-new-password",
           "Reset token is invalid or expired.",
           "New password must be different from the current password.",
           AUTHEN_POLICY,
           "AND row_status = 'ACTIVE'\nAND expired_at > '<sequence.now>'\nRETURNING id as reset_id",
           "#### UPDATE - Close the access tokens of the user",
           "#### UPDATE - Close the refresh tokens of the user",
           "#### UPDATE - Make the current password INACTIVE",
           "#### INSERT - Create password",
           "PBKDF2-HMAC-SHA256",
           "600,000",
           AUTHEN_LOCK,
           "(../../../schema/authen/m_user_password.md)",
           "WHERE user_id = '<sequence.userId>'\nAND row_status = 'ACTIVE'",
           "AND up.row_type = 'PASSWORD'\nAND up.row_status = 'ACTIVE'",
           "E10001",
           "E90001"],
    "05": ["# [POST]: v1/auth/refresh-token",
           "Invalid or expired refresh token.",
           "**Rotation:**",
           "RETURNING session_id -- no row means the answer is 401",
           "#### INSERT - Create refresh token",
           "#### INSERT - Create access token",
           "#### UPDATE - Close the refresh tokens of the session (reuse)",
           "#### UPDATE - Close the access tokens of the session (reuse)",
           AUTHEN_LOCK,
           '"expiresIn": 900',
           "AND row_status = 'ACTIVE'\nAND expired_at > '<sequence.now>'\nRETURNING session_id",
           "WHERE session_id = '<sequence.sessionId>'\nAND user_id = '<sequence.userId>'\nAND row_status = 'ACTIVE'"],
    "06": ["# [POST]: v1/auth/logout",
           "every ACTIVE access token and refresh token that has the same `session_id`",
           "#### UPDATE - Close the access tokens of the session",
           "#### UPDATE - Close the refresh tokens of the session",
           "WHERE session_id = '<sequence.sessionId>'\nAND user_id = '<sequence.userId>'\nAND row_status = 'ACTIVE'",
           "Logout Success",
           AUTHEN_LOCK],
    "07": ["# [POST]: v1/user/profile/upsert",
           "Username, Email Address and Password cannot be changed here.",
           "-- only when firstName is specified (null clears it)",
           "-- only when lastName is specified (null clears it)",
           "-- only when displayName is specified (null clears it)",
           "-- only when profilePicturePath is specified (null clears it)",
           "-- only when phoneNumber is specified (null clears it)",
           "-- only when address is specified (null clears it)",
           "-- only when dateOfBirth is specified (null clears it)",
           "-- only when gender is specified (null clears it)",
           AUTHEN_LOCK,
           "never read from the request"],
    "08": ["# [GET]: v1/user/profile",
           "AND u.row_status = 'ACTIVE'",
           "WHERE u.id = '<sequence.userId>'",
           "WHERE ui.user_id = '<sequence.userId>'"],
    "09": ["# [POST]: v1/user/address/upsert",
           "uq_t_user_address_user_id_default",
           "A user can have at most 10 addresses.",
           "A default address must be ACTIVE.",
           "User address not found.",
           "#### UPDATE - Clear the old default",
           "#### UPDATE - Promote another default address",
           "AND ua.user_id = '<sequence.userId>'",
           AUTHEN_LOCK,
           "AND ua.row_status <> 'DELETED' -- an address of another user or a DELETED address counts as not found",
           "AND is_default\nAND row_status <> 'DELETED'",
           "Row status must not be DELETED when inserting a user address."],
    "10": ["# [GET]: v1/user/address",
           "ORDER BY ua.is_default DESC, ua.created_at DESC, ua.id",
           "Row status must be one of ACTIVE, INACTIVE.",
           "Page Index and Page Size must be greater than 0",
           "Request: `GET v1/user/address?id=%s`" % AUTHEN_ADDRESS_ID],
}
# Sentences that live in a note of the sequence diagram (the rules the template alignment moved out of the spec)
AUTHEN_SEQUENCE_NEEDLES = {
    "02": ['5 `FAILED` attempts in the last 15 minutes',
           '**Only `FAILED` rows are counted.**',
           'recorded as `REFUSED`, which is not counted',
           'The block therefore ends by itself as soon as the 5th most recent failure is older than 15 minutes',
           'The `FAILED` and `REFUSED` rows are committed although the answer is 401',
           'record `REFUSED` and answer 401 when there are 5',
           'record `FAILED` and answer 401 when it does not match or the user is not found',
           'record `SUCCESS`',
           'SHA-256 (32 bytes), never as the token itself',
           'Lock order:',
           '**Authorization claims:**',
           '`roles`, `permissions` and `scopes`',
           'A user with no assigned role or permission can still log in'],
    "03": ['uq_t_user_reset_password_user_id_active',
           'Lock order:'],
    "04": ['Password storage: PBKDF2-HMAC-SHA256 with a random 16 byte salt and 600,000 iterations',
           'uq_m_user_password_user_id_password',
           'Lock order:'],
    "05": ['**Reuse:**',
           'When the row became INACTIVE less than 10 seconds ago (configurable)',
           '**The closing of the session is committed although the answer is 401:**',
           'written in its own transaction that is committed before the answer is sent',
           'any other user gets 401 and **nothing has changed**, the refresh token is not made INACTIVE',
           'when the row was a reuse older than 10 seconds the session is closed and committed first',
           'are one transaction: when any of them fails nothing is saved',
           'Lock order:',
           'SHA-256 (32 bytes), never as the token itself'],
    "06": ['Lock order:',
           'Sessions of other devices are not changed.'],
    "07": ['uq_m_user_information_user_id',
           'Lock order:'],
    "08": ['never returned'],
    "09": ['Lock order:',
           'Delete 204 No Content'],
}
AUTHEN_COUNTED = {
    "10": [("WHERE ua.user_id = '<sequence.userId>'\nAND ua.row_status <> 'DELETED'", 2), ("AND ('<sequence.searchPattern>' IS NULL OR ua.title ILIKE '<sequence.searchPattern>') -- only when search is specified", 2),
           ("AND ('<sequence.rowStatus>' IS NULL OR ua.row_status = '<sequence.rowStatus>') -- only when rowStatus is specified", 2),
           ("AND ('<sequence.id>' IS NULL OR ua.id = '<sequence.id>') -- only when id is specified", 2)],
    "05": [("INSERT INTO authen.t_user_access_token (", 1), ("INSERT INTO authen.t_user_refresh_token (", 1),
           ("AND row_status = 'ACTIVE' -- only on replay outside the 10-second grace window", 2)],
    "06": [("WHERE session_id = '<sequence.sessionId>'\nAND user_id = '<sequence.userId>'\nAND row_status = 'ACTIVE'", 2)],
    "02": [("INSERT INTO authen.t_user_access_token (", 1), ("INSERT INTO authen.t_user_refresh_token (", 1), ("INSERT INTO authen.l_user_login_attempt (", 1)],
    "09": [("ua.user_id = '<sequence.userId>'", 4)],
}
AUTHEN_FORBIDDEN = {
    "01": ["AES256", "Encrypted "], "02": ["AES256", "mobile no", "3600", "7 day", "Encrypted ", "recorded as a failed attempt", "is_success", "isSuccess"],
    "03": ['"code": 401', '"code": 403', '"code": 404', '"code": 409'], "04": ['"code": 401', '"code": 404', '"code": 409'],
    "05": [],
}
AUTHEN_PUBLIC = ("01", "02", "03", "04", "05")
AUTHEN_PRIVATE = ("06", "07", "08", "09", "10")
JWT_FULL = re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")
SECRET_ASSIGNED = re.compile(r"(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token)\b\s*[:=]\s*['\"][^'\"\s<>{}$]{8,}['\"]")


def authen_json(md: str, heading: str):
    """Parsed JSON of the first ```JSON block under '#### <heading>' (an optional 'Request: ...' line may come first)."""
    match = re.search(rf"^#### {re.escape(heading)}\n\n(?:Request: [^\n]*\n\n)?```JSON\n(.*?)```", md, re.MULTILINE | re.DOTALL)
    return json.loads(match.group(1)) if match else None


def authen_status(md: str, title: str, code: int, biz: str, message: str | None = None) -> list[str]:
    body = authen_json(md, title)
    if body is None:
        return [f"no JSON in '{title}'"]
    status = body["status"]
    errors = []
    if status["code"] != code or status["bizCode"] != biz:
        errors.append(f"'{title}' must be {code} {biz}")
    if message is not None and status["bizMessage"] != message:
        errors.append(f"'{title}' must say {message!r}")
    return errors


def authen_example_errors(key: str, md: str) -> list[str]:
    errors = []
    if key == "01":
        if "username" not in md or "john.doe" not in md:
            errors.append("the example must use the plain username john.doe")
    elif key == "02":
        ok = authen_json(md, "Success")
        if ok["data"]["expiresIn"] != 900 or ok["data"]["tokenType"] != "Bearer":
            errors.append("the Success example must have tokenType Bearer and expiresIn 900")
        for token in ("accessToken", "refreshAccessToken"):
            if not ok["data"][token].endswith("..."):
                errors.append(f"the example {token} must end with '...'")
        errors += authen_status(md, "Fail - Unauthorized", 401, "E10002", "Invalid username or password.")
    elif key == "03":
        errors += authen_status(md, "Success", 200, "S10000", "If the email address is registered, a reset link has been sent.")
        errors += authen_status(md, "Fail - Bad Request", 400, "E10001")
        if "data" in authen_json(md, "Success"):
            errors.append("the Success example has no data")
    elif key == "04":
        errors += authen_status(md, "Success", 200, "S10000", "Create New Password Success")
        errors += authen_status(md, "Fail - Bad Request Password Policy", 400, "E10001", AUTHEN_POLICY)
        errors += authen_status(md, "Fail - Bad Request Reset Token", 400, "E10001", "Reset token is invalid or expired.")
        errors += authen_status(md, "Fail - Bad Request Same Password", 400, "E10001", "New password must be different from the current password.")
        request = json.loads(re.search(r"#### Example Body Parameters\n\n```JSON\n(.*?)```", md, re.DOTALL).group(1))
        if set(request) != {"resetToken", "newPassword"} or not request["resetToken"].endswith("..."):
            errors.append("the request example must have resetToken (ending with '...') and newPassword")
    elif key == "05":
        ok = authen_json(md, "Success")
        if set(ok["data"]) != {"tokenType", "accessToken", "refreshAccessToken", "expiresIn"} or ok["data"]["expiresIn"] != 900:
            errors.append("the Success example must have the four token fields and expiresIn 900")
        for token in ("accessToken", "refreshAccessToken"):
            if not ok["data"][token].endswith("..."):
                errors.append(f"the example {token} must end with '...'")
        errors += authen_status(md, "Fail - Unauthorized", 401, "E10002", "Invalid or expired refresh token.")
    elif key == "06":
        errors += authen_status(md, "Success", 200, "S10000", "Logout Success")
        errors += authen_status(md, "Fail - Unauthorized", 401, "E10002", "Invalid or expired access token.")
    elif key == "07":
        request = json.loads(re.search(r"#### Example Body Parameters\n\n```JSON\n(.*?)```", md, re.DOTALL).group(1))
        for fixed in ("username", "emailAddress", "password", "userId", "id"):
            if fixed in request:
                errors.append(f"the request example must not carry {fixed}")
        ok = authen_json(md, "Success")
        if ok["status"]["code"] != 200 or set(ok["data"]) != {"userId"}:
            errors.append("the Success example must be 200 with userId")
        errors += authen_status(md, "Fail - Bad Request Fixed Field", 400, "E10001", "Username, Email Address and Password cannot be changed here.")
    elif key == "08":
        data = authen_json(md, "Success")["data"]
        expected = {"userId", "emailAddress", "firstName", "lastName", "displayName", "profilePicturePath", "phoneNumber", "address", "dateOfBirth", "gender"}
        if set(data) != expected:
            errors.append(f"the Success data keys must be {sorted(expected)}")
        if "username" in data or "password" in data:
            errors.append("the profile must not return username or password")
    elif key == "09":
        bodies = {t: json.loads(re.search(rf"##### {t}\n\n```JSON\n(.*?)```", md, re.DOTALL).group(1)) for t in ("Insert", "Update", "Delete")}
        if "id" in bodies["Insert"]:
            errors.append("the Insert example must not have an id")
        if bodies["Update"].get("id") != AUTHEN_ADDRESS_ID or bodies["Delete"].get("id") != AUTHEN_ADDRESS_ID:
            errors.append("the Update and Delete examples must use the same address id")
        if bodies["Delete"].get("rowStatus") != "DELETED" or bodies["Update"].get("rowStatus") != "ACTIVE":
            errors.append("Update must be ACTIVE and Delete must be DELETED")
        for label, body in bodies.items():
            if body.get("isDefault") and body.get("rowStatus") != "ACTIVE":
                errors.append(f"the {label} example sets a default on a row that is not ACTIVE")
        codes = success_codes(md)
        if codes != {"Success - Insert": 201, "Success - Update": 200, "Success - Delete": 204}:
            errors.append(f"wrong success codes {codes}")
        for title in ("Success - Insert", "Success - Update"):
            if authen_json(md, title)["data"]["userAddressId"] != AUTHEN_ADDRESS_ID:
                errors.append(f"'{title}' answers a different userAddressId")
        for title, code, biz in (("Fail - Bad Request", 400, "E10001"), ("Fail - Bad Request Limit", 400, "E10001"), ("Fail - Not Found", 404, "E10004"), ("Fail - Unauthorized", 401, "E10002")):
            errors += authen_status(md, title, code, biz)
    elif key == "10":
        defaults_seen = 0
        for title in ("Success", "Success - By Id", "Success - Not Found"):
            data = authen_json(md, title)["data"]
            if data["totalItems"] != len(data["items"]):
                errors.append(f"'{title}' totalItems differs from the number of items")
            pages = 0 if data["totalItems"] == 0 else -(-data["totalItems"] // data["pageSize"])
            if data["totalPages"] != pages:
                errors.append(f"'{title}' totalPages should be {pages}")
            if any(item["rowStatus"] == "DELETED" for item in data["items"]):
                errors.append(f"'{title}' lists a DELETED address")
            flags = [item["isDefault"] for item in data["items"]]
            if sum(flags) > 1 or flags != sorted(flags, reverse=True):
                errors.append(f"'{title}' must have at most one default address and list it first")
            defaults_seen += sum(flags)
            if title == "Success - By Id" and [item["userAddressId"] for item in data["items"]] != [AUTHEN_ADDRESS_ID]:
                errors.append("the By Id example must list only its id")
            if title == "Success - Not Found" and data["items"]:
                errors.append("the Not Found example must have no items")
        if defaults_seen == 0:
            errors.append("an example must show the default address")
        for title, code, biz in (("Fail - Bad Request", 400, "E10001"), ("Fail - Unauthorized", 401, "E10002")):
            errors += authen_status(md, title, code, biz)
    if key in ("03", "04", "05", "06", "07", "08", "09", "10"):
        errors += authen_status(md, "Fail - Request Timeout", 408, "E90001")
    if key in ("06", "07", "08", "09", "10"):
        errors += authen_status(md, "Fail - Unauthorized", 401, "E10002", "Invalid or expired access token.")
    return errors


def check_authen_spec() -> int:
    errors = []
    mds = {}
    for key, path in AUTHEN_SPECS.items():
        try:
            mds[key] = read(path)
        except FileNotFoundError:
            errors.append(f"{path} does not exist")
            continue
        md = mds[key]
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        for bad in json_blocks_parse(md):
            errors.append(f"{path} invalid JSON block: {bad[:40]}")
        for link in relative_links_exist(path, md):
            errors.append(f"{path} broken link {link}")
        if "ALTER TABLE" in md:
            errors.append(f"{path} contains ALTER TABLE")
        if JWT_FULL.search(md):
            errors.append(f"{path} contains a full three part JWT (cut the example with '...')")
        for field, value in re.findall(r'"(accessToken|refreshAccessToken|resetToken)": "([^"]+)"', md):
            if not value.endswith("..."):
                errors.append(f"{path}: the example {field} must end with '...'")
        if SECRET_ASSIGNED.search(md):
            errors.append(f"{path} contains a secret-looking assignment")
        if not (ROOT / path).with_name("sequence.wsd").exists():
            errors.append(f"{path} has no sequence.wsd beside it")
        for missing in missing_needles(md, AUTHEN_NEEDLES.get(key, [])):
            errors.append(f"{path} missing: {missing!r}")
        sequence_note = " ".join((ROOT / path).with_name("sequence.wsd").read_text(encoding="utf-8").split()) if (ROOT / path).with_name("sequence.wsd").exists() else ""
        for missing in missing_needles(sequence_note, AUTHEN_SEQUENCE_NEEDLES.get(key, [])):
            errors.append(f"{path} sequence note missing: {missing!r}")
        for text, times in AUTHEN_COUNTED.get(key, []):
            if md.count(text) != times:
                errors.append(f"{path}: {text!r} must appear {times} time(s), found {md.count(text)}")
        for forbidden in AUTHEN_FORBIDDEN.get(key, []):
            if forbidden in md:
                errors.append(f"{path} must not contain {forbidden!r}")
        has_header = bool(re.search(r"^\| \d+ +\| authorization +\|", md, re.MULTILINE))
        if key in AUTHEN_PUBLIC and has_header:
            errors.append(f"{path} is a public API and must not have the authorization header")
        if key in AUTHEN_PRIVATE and not has_header:
            errors.append(f"{path} is a private API and needs the authorization header")
    if errors:
        return fail("; ".join(errors))
    for key in ("01", "02", "03", "04", "05", "06", "07", "08", "09", "10"):
        try:
            errors.extend(f"{AUTHEN_SPECS[key]}: {e}" for e in authen_example_errors(key, mds[key]))
        except (KeyError, TypeError, AttributeError, ValueError, IndexError) as exc:
            errors.append(f"{AUTHEN_SPECS[key]}: an example does not have the expected shape: {exc!r}")
    for key in ("03", "04", "05", "06"):
        if "PBKDF2" in mds[key] and "600,000" not in mds[key]:
            errors.append(f"{AUTHEN_SPECS[key]}: the hash must be PBKDF2 with 600,000 iterations")
    if errors:
        return fail("; ".join(errors))
    print("OK: authen-spec")
    return 0


COMMANDS["authen-spec"] = check_authen_spec

AUTHEN_INDEXES = [
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_t_user_reset_password_user_id_active ON authen.t_user_reset_password (user_id) WHERE row_status = 'ACTIVE'",
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_m_user_password_user_id_password ON authen.m_user_password (user_id) WHERE row_type = 'PASSWORD' AND row_status = 'ACTIVE'",
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_m_user_information_user_id ON authen.m_user_information (user_id) WHERE row_status <> 'DELETED'",
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_t_user_address_user_id_default ON authen.t_user_address (user_id) WHERE is_default AND row_status <> 'DELETED'",
]
AUTHEN_LOG_INDEX = "CREATE INDEX IF NOT EXISTS ix_l_user_login_attempt_identifier_hash_created_at ON authen.l_user_login_attempt (identifier_hash, created_at)"


def authen_statements(sql: str, table: str) -> list[str]:
    found = []
    for statement in sql.split(";"):
        text = normalize(statement)
        if re.search(rf"^CREATE TABLE IF NOT EXISTS authen\.{table} \(", text) or re.search(rf"^CREATE (UNIQUE )?INDEX IF NOT EXISTS \S+ ON authen\.{table} \(", text):
            found.append(text)
    return found


def er_rows(table: str, needle: str) -> list[str]:
    """Rows of every drawn <table> of the ER diagram that contain <needle> (one per page that draws the table)."""
    import xml.etree.ElementTree as ET

    root = ET.fromstring(read("e-commerce/db/er-diagram.drawio"))
    cells = list(root.iter("mxCell"))
    rows = []
    for cell in cells:
        if cell.get("value") == table:
            rows.extend(child.get("value") for child in cells if child.get("parent") == cell.get("id") and needle in (child.get("value") or ""))
    return rows


def check_authen_schema() -> int:
    """WP4: session_id on the token tables, one live row per user, the login attempt log (migration, down, docs, README, ER, test)."""
    errors = []
    sql = read("e-commerce/db/migrations/up/01-authen.schema.up.sql")
    for table in ("t_user_access_token", "t_user_refresh_token"):
        create = [s for s in authen_statements(sql, table) if s.startswith("CREATE TABLE")]
        if len(create) != 1 or "session_id UUID NOT NULL" not in create[0] or "token BYTEA NOT NULL UNIQUE" not in create[0]:
            errors.append(f"migration 01: {table} needs 'session_id UUID NOT NULL' and 'token BYTEA NOT NULL UNIQUE'")
    for index in AUTHEN_INDEXES:
        table = re.search(r"ON authen\.(\w+)", index).group(1)
        if index not in authen_statements(sql, table):
            errors.append(f"migration 01: missing or different: {index[:90]}")
    log = authen_statements(sql, "l_user_login_attempt")
    expected_log = ["identifier_hash BYTEA NOT NULL", "user_id UUID REFERENCES authen.m_user (id) ON DELETE CASCADE", "result VARCHAR(16) NOT NULL CHECK (result IN ('SUCCESS', 'FAILED', 'REFUSED'))"]
    if not log or any(part not in log[0] for part in expected_log):
        errors.append("migration 01: l_user_login_attempt is missing or has different columns")
    if AUTHEN_LOG_INDEX not in log:
        errors.append("migration 01: the index of l_user_login_attempt is missing or different")
    down = read("e-commerce/db/migrations/down/01-authen.schema.down.sql")
    if "DROP TABLE IF EXISTS authen.l_user_login_attempt;" not in down or down.index("authen.l_user_login_attempt") > down.index("authen.m_user;"):
        errors.append("down 01: l_user_login_attempt must be dropped before m_user")
    for table in ("t_user_access_token", "t_user_refresh_token", "t_user_reset_password", "m_user_password", "m_user_information", "t_user_address", "l_user_login_attempt"):
        path = f"e-commerce/doc/schema/authen/{table}.md"
        md = read(path)
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        if authen_statements(" ".join(SQL_BLOCK.findall(md)), table) != authen_statements(sql, table):
            errors.append(f"{path} SQL differs from the migration")
        if table in ("t_user_access_token", "t_user_refresh_token") and not re.search(r"\| session_id +\| UUID +\| +\| FALSE", md):
            errors.append(f"{path} does not list session_id")
        if table in ("t_user_access_token", "t_user_refresh_token", "t_user_reset_password") and "never the token itself" not in md:
            errors.append(f"{path} must say that the token column holds a SHA-256, never the token itself")
    for index in AUTHEN_INDEXES + [AUTHEN_LOG_INDEX]:
        name = re.search(r"INDEX IF NOT EXISTS (\S+) ON authen\.(\w+)", index)
        md = read(f"e-commerce/doc/schema/authen/{name.group(2)}.md")
        if name.group(1) not in md.split("## Constain")[1].split("\n---\n")[0]:
            errors.append(f"e-commerce/doc/schema/authen/{name.group(2)}.md: the constraint table must list {name.group(1)}")
    readme = read("e-commerce/doc/schema/README.md")
    for row in ("| [t_user_access_token](authen/t_user_access_token.md) | Transaction | 10 | 1 |", "| [t_user_refresh_token](authen/t_user_refresh_token.md) | Transaction | 10 | 1 |",
                "| [l_user_login_attempt](authen/l_user_login_attempt.md) | Log | 6 | 1 |"):
        if row not in readme:
            errors.append(f"README missing row: {row}")
    for table in ("authen.t_user_access_token", "authen.t_user_refresh_token"):
        if len(er_rows(table, "session_id : uuid")) < 2:
            errors.append(f"ER diagram: {table} must draw session_id on at least 2 pages")
    if len(er_rows("authen.l_user_login_attempt", "result : varchar(16)")) < 2:
        errors.append("ER diagram: l_user_login_attempt must draw result : varchar(16) on at least 2 pages")
    if "ck_l_user_login_attempt_result" not in read("e-commerce/doc/schema/authen/l_user_login_attempt.md"):
        errors.append("e-commerce/doc/schema/authen/l_user_login_attempt.md: the constraint table must list ck_l_user_login_attempt_result")
    if len(er_rows("authen.l_user_login_attempt", "identifier_hash : bytea")) < 2:
        errors.append("ER diagram: l_user_login_attempt must be drawn on at least 2 pages")
    for table in ("authen.m_user_password", "authen.m_user_information", "authen.t_user_address"):
        if any(row.startswith("UK") and "user_id" in row for row in er_rows(table, "user_id")):
            errors.append(f"ER diagram: {table}.user_id must not carry the UK marker (the unique index is partial)")
    if not (ROOT / "e-commerce/db/tests/01-authen.test.sql").exists():
        errors.append("db/tests/01-authen.test.sql does not exist")
    elif "PASS test 7: refused attempts are not counted" not in read("e-commerce/db/tests/01-authen.test.sql"):
        errors.append("db/tests/01-authen.test.sql must test that refused attempts are not counted")
    login = read(AUTHEN_SPECS["02"])
    count_query = re.search(r"#### QUERY - Count failed attempts\n\n```SQL\n(.*?)```", login, re.DOTALL)
    if not count_query or "AND la.result = 'FAILED'" not in count_query.group(1) or "REFUSED" in count_query.group(1) or "SUCCESS" in count_query.group(1):
        errors.append("02-login: the count query must count only FAILED attempts")
    if errors:
        return fail("; ".join(errors))
    print("OK: authen-schema")
    return 0


COMMANDS["authen-schema"] = check_authen_schema


# ---------------------------------------------------------------- API sequence diagrams: spec SQL parity and table lifecycle
SEQUENCE_API_ROOT = "e-commerce/doc/api"
# Groups whose sequence diagrams are all filled: an empty sequence.wsd in one of them fails the check.
# Every other group may still be empty (pending), but each spec needs a sequence.wsd beside it.
# The owner of the sequence work adds a group here when the group is complete.
REQUIRED_GROUPS = ("authen-and-author", "consent")
# Specs with INSERT, UPDATE or DELETE whose diagram does not follow the login standard yet (BEGIN, COMMIT, ROLLBACK,
# HTTP 400 E10001, 408 E90001 and 500). They wait for a retrofit; an entry is an exact folder, never a wildcard, and the
# check fails when a listed diagram already passes (remove it) or no longer has a write.
LEGACY_SEQUENCES = (
    # authen-and-author: waiting for a retrofit to the login standard
    # consent: waiting for a retrofit to the login standard
    "consent/06-upsert-consent-type",
    "consent/07-upsert-consent-type-batch",
)
# Diagrams written before the access token and timeout answers became part of the check. Each is exempt from the token
# rule (Verify JWT and 401 E10002 when the spec has a mandatory authorization header) and from the 408 E90001 rule, and
# must still fail at least one of them: a file that passes both has to leave this list. Remove an entry in the same
# change that adds the missing answers to the diagram.
LEGACY_TOKEN_SEQUENCES = (
    "consent/06-upsert-consent-type",               # no Verify JWT / 401 step, no 408
    "consent/07-upsert-consent-type-batch",         # no Verify JWT / 401 step, no 408
    "consent/08-inquiry-consent-type",              # no Verify JWT / 401 step, no 408
)


def spec_database_operations(md: str) -> list[tuple[str, str, str]]:
    """Return (qualified table, operation heading, SQL) in specification order."""
    operations = []
    current_table = None
    lines = md.splitlines()
    index = 0
    while index < len(lines):
        table = re.match(r"^### Table: \[([^\]]+)\]", lines[index])
        if table:
            current_table = table.group(1)
            index += 1
            continue
        operation = re.match(r"^#### ((?:QUERY|INSERT|UPDATE|DELETE)[^\n]*)$", lines[index])
        if operation and current_table:
            cursor = index + 1
            while cursor < len(lines) and lines[cursor] != "```SQL":
                if lines[cursor].startswith("#### ") or lines[cursor].startswith("### Table:"):
                    break
                cursor += 1
            if cursor < len(lines) and lines[cursor] == "```SQL":
                cursor += 1
                sql = []
                while cursor < len(lines) and lines[cursor] != "```":
                    sql.append(lines[cursor])
                    cursor += 1
                operations.append((current_table, operation.group(1), "\n".join(sql)))
                index = cursor + 1
                continue
        index += 1
    return operations


def sequence_database_operations(wsd: str) -> tuple[list[tuple[str, str, str]], list[str]]:
    """Return table interactions and lifecycle/indentation errors from one sequence."""
    operations = []
    errors = []
    lines = wsd.splitlines()
    index = 0
    while index < len(lines):
        request = re.match(r"^(\s*)infra -> (\w+): ((?:QUERY|INSERT|UPDATE|DELETE)[^\n]*)$", lines[index])
        if not request:
            index += 1
            continue
        indent, table, heading = len(request.group(1)), request.group(2), request.group(3)
        if index + 2 >= len(lines):
            errors.append(f"line {index + 1}: incomplete interaction for {table}")
            break
        if lines[index + 1] != " " * indent + f"activate {table}":
            errors.append(f"line {index + 1}: {table} must activate immediately after the request")
        if lines[index + 2] != " " * (indent + 4) + f"note right of {table}":
            errors.append(f"line {index + 1}: {table} SQL note must be indented inside its activation")
        cursor = index + 3
        sql = []
        while cursor < len(lines) and lines[cursor].strip() != "end note":
            sql_line = lines[cursor][indent + 8:] if lines[cursor].startswith(" " * (indent + 8)) else lines[cursor].lstrip()
            # A literal leading apostrophe is a PlantUML comment, even inside a note.
            if sql_line.lstrip().startswith("&#39;"):
                sql_line = sql_line.replace("&#39;", "'", 1)
            sql.append(sql_line)
            cursor += 1
        if cursor >= len(lines):
            errors.append(f"line {index + 1}: {table} SQL note is not closed")
            break
        if lines[cursor] != " " * (indent + 4) + "end note":
            errors.append(f"line {cursor + 1}: {table} end note must stay inside its activation")
        if cursor + 1 >= len(lines) or not re.match(rf"^{' ' * (indent + 4)}{re.escape(table)} -> infra: Return ", lines[cursor + 1]):
            errors.append(f"line {cursor + 2}: {table} must return while it is active")
        if cursor + 2 >= len(lines) or lines[cursor + 2] != " " * indent + f"deactivate {table}":
            errors.append(f"line {cursor + 3}: {table} must deactivate after its return")
        operations.append((table, heading, "\n".join(sql)))
        index = cursor + 3
    return operations, errors


SEQUENCE_PARTICIPANT_CHAIN = ('participant "API" as api', 'participant "Application" as app', 'participant "Domain" as domain', 'participant "Infrastructure" as infra')
SEQUENCE_HEAD = ('skinparam defaultFontName "Sarabun"', "hide footbox")
SEQUENCE_USER_HEAD = 'actor "User" as user'
SEQUENCE_USER_BOXES = ["Frontend", "Web API", "Database"]
# a caller that is an external system (the Stripe webhook): box External with its participants instead of actor User and box Frontend
SEQUENCE_EXTERNAL_BOXES = ["External", "Web API", "Database"]
SEQUENCE_BOXES = ('box "Frontend"', 'box "Web API"', 'box "Database"')
SEQUENCE_LOCK = re.compile(r"FOR\s+(?:NO\s+KEY\s+)?UPDATE|FOR\s+(?:KEY\s+)?SHARE|pg_(?:try_)?advisory_(?:xact_)?lock", re.IGNORECASE)
SEQUENCE_LOGIN_STANDARD = ("-> infra: BEGIN", "-> infra: COMMIT", "-> infra: ROLLBACK", "HTTP 400 E10001", "HTTP 408 E90001", "HTTP 500")


def sequence_structure_errors(text: str) -> list[str]:
    """Structure every filled sequence diagram follows (the login diagram is the model)."""
    errors = []
    if not text.startswith("@startuml ") or not text.rstrip().endswith("@enduml"):
        errors.append("must have @startuml and @enduml")
    if not re.search(r"^title .+$", text, re.MULTILINE):
        errors.append("must have a title")
    for needle in SEQUENCE_HEAD:
        if needle not in text:
            errors.append(f"missing {needle!r}")
    boxes = re.findall(r'^box "([^"]+)"', text, re.MULTILINE)
    external = boxes == SEQUENCE_EXTERNAL_BOXES
    if boxes != SEQUENCE_USER_BOXES and not external:
        errors.append(f"boxes must be Frontend, Web API, Database in that order, or External, Web API, Database when the caller is an external system (never Frontend and External together), found {boxes}")
    if external:
        external_box = re.search(r'^box "External".*?^end box$', text, re.MULTILINE | re.DOTALL)
        if not external_box or not re.search(r'^\s*participant "[^"]+" as \w+$', external_box.group(0), re.MULTILINE):
            errors.append("the External box must hold the participant of the external caller")
        if SEQUENCE_USER_HEAD in text:
            errors.append(f"an external caller replaces {SEQUENCE_USER_HEAD!r}: remove the actor")
    elif SEQUENCE_USER_HEAD not in text:
        errors.append(f"missing {SEQUENCE_USER_HEAD!r}")
    if len(re.findall(r"^end box$", text, re.MULTILINE)) != 3:
        errors.append("every box must be closed with end box")
    positions = [text.find(chain) for chain in SEQUENCE_PARTICIPANT_CHAIN]
    if -1 in positions or positions != sorted(positions):
        errors.append("the Web API box must hold the participants API, Application, Domain, Infrastructure in that order")
    if not re.search(r"^\s*api -> app: \[\*\*\w+Handler\*\*\] .+$", text, re.MULTILINE):
        errors.append("missing the handler line 'api -> app: [**XxxHandler**] ...'")
    if "TODO(author)" in text:
        errors.append("still has a TODO(author) marker")
    return errors


def sequence_login_standard_errors(text: str) -> list[str]:
    """Transaction and error standard of the login diagram, for a diagram whose spec writes data."""
    errors = [f"missing {needle!r}" for needle in SEQUENCE_LOGIN_STANDARD if needle not in text]
    if errors:
        return errors
    interactions = [m.start() for m in re.finditer(r"^\s*infra -> \w+: (?:QUERY|INSERT|UPDATE|DELETE)", text, re.MULTILINE)]
    writes = [m.start() for m in re.finditer(r"^\s*infra -> \w+: (?:INSERT|UPDATE|DELETE)", text, re.MULTILINE)]
    # A read that only finds the row to lock (05-refresh-token) may come before BEGIN; every write must come after it.
    lines = text.splitlines()
    begin_line = next(i for i, line in enumerate(lines) if "-> infra: BEGIN" in line)
    # Routing reads can fail before BEGIN: there is no transaction to roll back yet.
    # Every 408/500 after BEGIN still requires its own immediately preceding ROLLBACK.
    for position, line in enumerate(lines):
        failure = re.match(r"^(\s*)app -> api: HTTP (408 E90001|500)\b", line)
        if failure and position > begin_line and (position == 0 or lines[position - 1] != failure.group(1) + "app -> infra: ROLLBACK"):
            errors.append(f"line {position + 1}: HTTP {failure.group(2)} must follow 'app -> infra: ROLLBACK' on the line before")
    for needle in ("HTTP 400 E10001", "HTTP 408 E90001", "HTTP 500"):
        if not re.search(rf"^\s*app -> api: {re.escape(needle)}", text, re.MULTILINE):
            errors.append(f"missing the answer line 'app -> api: {needle}'")
    if "-> infra: BEGIN" in text and "HTTP 400 E10001" in text and text.index("HTTP 400 E10001") > text.index("-> infra: BEGIN"):
        errors.append("the HTTP 400 E10001 answer belongs to the validation step before BEGIN")
    begin = text.index("-> infra: BEGIN")
    if writes and begin > writes[0]:
        errors.append("BEGIN must come before the first INSERT, UPDATE or DELETE")
    # A lock taken outside the transaction is released at once, so every locking statement comes after BEGIN
    # (05-refresh-token reads the row to lock before BEGIN, but that read takes no lock).
    for match in re.finditer(r"^\s*infra -> \w+: (?:QUERY|INSERT|UPDATE|DELETE)", text, re.MULTILINE):
        following = re.search(r"^\s*(?:app|infra) -> ", text[match.end():], re.MULTILINE)
        statement = text[match.start(): match.end() + following.start() if following else len(text)]
        if match.start() < begin and SEQUENCE_LOCK.search(statement):
            errors.append(f"line {text.count(chr(10), 0, match.start()) + 1}: a locking statement (FOR UPDATE / advisory lock) must come after BEGIN")
    # Every error answer inside the transaction ends it first: the closest 'app -> infra:' line that leads to it is
    # ROLLBACK or COMMIT. "Leads to it" follows the nesting by indentation: lines of closed branches (deeper) are skipped
    # and a lower indent moves out to the enclosing block, so the ROLLBACK of a sibling branch does not count.
    offset = 0
    for position, line in enumerate(lines):
        line_start, offset = offset, offset + len(line) + 1
        if not re.match(r"^\s*app -> api: HTTP [45]\d\d\b", line) or line_start < begin:
            continue
        indent = len(line) - len(line.lstrip())
        previous = ""
        for item in reversed(lines[:position]):
            if not item.strip():
                continue
            item_indent = len(item) - len(item.lstrip())
            if item_indent < indent:
                indent = item_indent
            if item_indent == indent and item.lstrip().startswith("app -> infra:"):
                previous = item.strip()
                break
        if previous not in ("app -> infra: ROLLBACK", "app -> infra: COMMIT"):
            errors.append(f"line {position + 1}: {line.strip().split(': ', 1)[1]} inside the transaction must follow 'app -> infra: ROLLBACK' or 'COMMIT' (found {previous!r})")
    if interactions and text.rindex("-> infra: COMMIT") < interactions[-1]:
        errors.append("COMMIT must come after the last SQL interaction")
    return errors


SEQUENCE_AUTH_ROW = re.compile(r"^\|\s*\d+\s*\|\s*authorization\s*\|[^|]*\|\s*MANDATORY\s*\|", re.MULTILINE | re.IGNORECASE)


def spec_needs_token(spec_text: str) -> bool:
    """The spec has a mandatory authorization header, so the caller sends an access token (login and refresh do not)."""
    return bool(SEQUENCE_AUTH_ROW.search(spec_text))


def spec_is_public(spec_text: str) -> bool:
    """The spec has no authorization header and says it is a public API."""
    return not spec_needs_token(spec_text) and bool(re.search(r"public api|api is public", spec_text, re.IGNORECASE))


def sequence_answer_errors(text: str, needs_token: bool, is_public: bool) -> list[str]:
    """Token, public and timeout answers: the 401 comes after the access token is verified and before the first database call."""
    errors = []
    lines = text.splitlines()
    first_infra = next((n for n, line in enumerate(lines) if re.match(r"^\s*app -> infra:", line)), len(lines))
    if needs_token:
        verify = next((n for n, line in enumerate(lines) if re.match(r"^\s*app -> app: Verify\b.*(?:\bJWT\b|access token)", line, re.IGNORECASE)), None)
        answer = next((n for n, line in enumerate(lines) if re.match(r"^\s*app -> api: HTTP 401 E10002\b", line)), None)
        if verify is None:
            errors.append("the spec has a mandatory authorization header: missing 'app -> app: Verify JWT ...' (or 'Verify the access token ...')")
        if answer is None:
            errors.append("the spec has a mandatory authorization header: missing 'app -> api: HTTP 401 E10002'")
        if verify is not None and answer is not None:
            if not verify < answer < first_infra:
                errors.append("the access token is verified and the 401 E10002 is answered before the first 'app -> infra' line")
            elif not any(re.match(r"^\s*alt\b", line) for line in lines[verify + 1:answer]):
                errors.append("the 401 E10002 answer belongs to an alt branch right after the verify step")
    if is_public and any(re.match(r"^\s*app -> api: HTTP 401\b", line) for line in lines):
        errors.append("the spec is a public API (no authorization header): the diagram must not answer 401")
    if not any(re.match(r"^\s*app -> api: HTTP 408 E90001\b", line) for line in lines):
        errors.append("missing 'app -> api: HTTP 408 E90001'")
    return errors


def sequence_quote_errors(text: str) -> list[str]:
    """A note line that starts with a bare quote is drawn by PlantUML as a comment, so the SQL line is missing from the picture."""
    errors = []
    inside = False
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if re.match(r"^note (?:left|right|over)\b[^:]*$", stripped):
            inside = True
        elif stripped == "end note":
            inside = False
        elif inside and stripped.startswith("'"):
            errors.append(f"line {number}: a note line starts with a bare quote (PlantUML draws it as a comment), write it as &#39;")
    return errors


def sequence_heading_errors(text: str) -> list[str]:
    """Each 'app -> infra: <SQL heading>' line is followed at once by 'infra -> <table>: <the same heading>'."""
    errors = []
    lines = text.splitlines()
    for number, line in enumerate(lines):
        request = re.match(r"^\s*app -> infra: ((?:QUERY|INSERT|UPDATE|DELETE) - .*)$", line)
        if not request:
            continue
        following = re.match(r"^\s*infra -> \w+: (.*)$", lines[number + 1]) if number + 1 < len(lines) else None
        if not following or following.group(1) != request.group(1):
            found = following.group(1) if following else (lines[number + 1].strip() if number + 1 < len(lines) else "end of file")
            errors.append(f"line {number + 1}: 'app -> infra: {request.group(1)}' must be followed by 'infra -> <table>: {request.group(1)}', found {found!r}")
    return errors


def sequence_block_errors(spec_operations, sequence_operations, declared_tables) -> list[str]:
    """Blocks of a sequence against the blocks of its spec: every block exactly once or more, in any order.

    A block is its table, its heading and its SQL (normalized). The diagram may put the blocks in the order the work runs
    and repeat a block in several branches; it may not add a block, drop one or change one letter of its SQL. The database
    participants are the tables of the spec, declared in the order of their first use in the diagram.
    """
    errors = []
    spec_blocks = [(table.split(".")[-1], heading, normalize(sql)) for table, heading, sql in spec_operations]
    spec_set = set(spec_blocks)
    used = set()
    for position, (table, heading, sql) in enumerate(sequence_operations, start=1):
        key = (table, heading, normalize(sql))
        if key in spec_set:
            used.add(key)
        elif any(block[:2] == (table, heading) for block in spec_blocks):
            errors.append(f"interaction {position} {table} / {heading}: the SQL is not the SQL of any block of the spec with that table and heading")
        else:
            errors.append(f"interaction {position} {table} / {heading}: no block of the spec has this table and heading")
    for table, heading, sql in dict.fromkeys(spec_blocks):
        if (table, heading, sql) in used:
            continue
        same_name = [block for block in spec_blocks if block[:2] == (table, heading)]
        detail = f" (the one whose SQL starts with {sql.splitlines()[0][:60]!r})" if len(set(same_name)) > 1 else ""
        errors.append(f"the block {table} / {heading} of the spec{detail} is missing from the diagram")
    spec_tables = list(dict.fromkeys(block[0] for block in spec_blocks))
    first_use = list(dict.fromkeys(table for table, _, _ in sequence_operations))
    for table in spec_tables:
        if table not in declared_tables:
            errors.append(f"database participant {table} of the spec is not declared")
    for table in dict.fromkeys(declared_tables):
        if table not in spec_tables:
            errors.append(f"database participant {table} is not a table of the spec")
    if len(set(declared_tables)) != len(declared_tables):
        errors.append(f"database participants {declared_tables} declare a table twice")
    elif set(declared_tables) == set(first_use) and declared_tables != first_use:
        errors.append(f"database participants {declared_tables} must be declared in the order of first use in the diagram {first_use}")
    return errors


def check_api_sequence_spec() -> int:
    errors = []
    api_root = ROOT / SEQUENCE_API_ROOT
    specs = sorted(api_root.glob("*/*/spec.md"))
    groups: dict[str, list[int]] = {}
    legacy_seen = set()
    if not specs:
        errors.append(f"no spec.md found under {SEQUENCE_API_ROOT}")
    for group in REQUIRED_GROUPS:
        if not (api_root / group).is_dir():
            errors.append(f"required group {group} does not exist")
        elif not any(spec.parent.parent.name == group for spec in specs):
            errors.append(f"required group {group} has no spec")
    for entry in LEGACY_SEQUENCES:
        if not (api_root / entry / "spec.md").exists():
            errors.append(f"LEGACY_SEQUENCES lists {entry}, which is not a spec folder")
    for entry in LEGACY_TOKEN_SEQUENCES:
        if not (api_root / entry / "spec.md").exists():
            errors.append(f"LEGACY_TOKEN_SEQUENCES lists {entry}, which is not a spec folder")
    for spec_path in specs:
        group = spec_path.parent.parent.name
        folder = f"{group}/{spec_path.parent.name}"
        counts = groups.setdefault(group, [0, 0])
        counts[1] += 1
        sequence_path = spec_path.with_name("sequence.wsd")
        relative_spec = spec_path.relative_to(ROOT)
        relative_sequence = sequence_path.relative_to(ROOT)
        if not sequence_path.exists():
            errors.append(f"{relative_sequence}: missing (create an empty file while the group is pending)")
            continue
        sequence_text = sequence_path.read_text(encoding="utf-8")
        if not sequence_text.strip():
            if group in REQUIRED_GROUPS:
                errors.append(f"{relative_sequence}: empty, but {group} is a required group")
            continue
        counts[0] += 1
        spec_operations = spec_database_operations(spec_path.read_text(encoding="utf-8"))
        sequence_operations, lifecycle_errors = sequence_database_operations(sequence_text)
        errors.extend(f"{relative_sequence}: {error}" for error in lifecycle_errors)
        errors.extend(f"{relative_sequence}: {error}" for error in sequence_structure_errors(sequence_text))
        has_write = any(heading.split(" - ")[0] in ("INSERT", "UPDATE", "DELETE") for _, heading, _ in spec_operations)
        standard_errors = sequence_login_standard_errors(sequence_text) if has_write else []
        if folder in LEGACY_SEQUENCES:
            legacy_seen.add(folder)
            if not has_write:
                errors.append(f"{relative_sequence}: listed in LEGACY_SEQUENCES but its spec has no INSERT, UPDATE or DELETE")
            elif not standard_errors:
                errors.append(f"{relative_sequence}: already follows the login standard, remove it from LEGACY_SEQUENCES")
        else:
            errors.extend(f"{relative_sequence}: login standard: {error}" for error in standard_errors)
        spec_text = spec_path.read_text(encoding="utf-8")
        errors.extend(f"{relative_sequence}: {error}" for error in sequence_heading_errors(sequence_text))
        errors.extend(f"{relative_sequence}: {error}" for error in sequence_quote_errors(sequence_text))
        answer_errors = sequence_answer_errors(sequence_text, spec_needs_token(spec_text), spec_is_public(spec_text))
        if folder in LEGACY_TOKEN_SEQUENCES:
            if not answer_errors:
                errors.append(f"{relative_sequence}: already has the token and timeout answers, remove it from LEGACY_TOKEN_SEQUENCES")
        else:
            errors.extend(f"{relative_sequence}: {error}" for error in answer_errors)
        declared_tables = re.findall(r'^\s*database "[^"]+" as (\w+)$', sequence_text, re.MULTILINE)
        errors.extend(f"{relative_sequence}: {error}" for error in sequence_block_errors(spec_operations, sequence_operations, declared_tables))
    if errors:
        return fail("; ".join(errors))
    summary = ", ".join(
        f"{group} {filled}/{total}{'' if group in REQUIRED_GROUPS else ' pending' if filled < total else ''}" for group, (filled, total) in sorted(groups.items())
    )
    print(f"OK: api-sequence-spec ({len(specs)} specs; filled/total per group: {summary}; {len(LEGACY_SEQUENCES)} legacy without the login standard; {len(LEGACY_TOKEN_SEQUENCES)} legacy without the token and timeout answers)")
    return 0


COMMANDS["api-sequence-spec"] = check_api_sequence_spec


CAMPAIGN_SCHEMA_DOC = "e-commerce/doc/schema/campaign"
CAMPAIGN_MIGRATION = "e-commerce/db/migrations/up/09-campaign.schema.up.sql"
CAMPAIGN_INDEXES = {
    "m_campaign": ["CREATE UNIQUE INDEX IF NOT EXISTS uq_m_campaign_name ON campaign.m_campaign (name) WHERE row_status <> 'DELETED'"],
    "m_campaign_budget": ["CREATE UNIQUE INDEX IF NOT EXISTS uq_m_campaign_budget_campaign_id ON campaign.m_campaign_budget (campaign_id) "
                          "WHERE row_status <> 'DELETED'"],
    "m_campaign_budget_ledger": [],
    "t_campaign_product": [
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_t_campaign_product_campaign_id_product_id ON campaign.t_campaign_product (campaign_id, product_id) "
        "WHERE product_id IS NOT NULL AND row_status <> 'DELETED'",
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_t_campaign_product_campaign_id_product_category_id ON campaign.t_campaign_product "
        "(campaign_id, product_category_id) WHERE product_category_id IS NOT NULL AND row_status <> 'DELETED'"],
    "t_campaign_shop": ["CREATE UNIQUE INDEX IF NOT EXISTS uq_t_campaign_shop_campaign_id_shop_id ON campaign.t_campaign_shop (campaign_id, shop_id) "
                        "WHERE row_status <> 'DELETED'"],
    "t_campaign_discount": ["CREATE UNIQUE INDEX IF NOT EXISTS uq_t_campaign_discount_campaign_id ON campaign.t_campaign_discount (campaign_id) "
                            "WHERE row_status <> 'DELETED'"],
}
CAMPAIGN_TABLE_PARTS = {
    "m_campaign": ["CONSTRAINT ck_m_campaign_period CHECK (end_at > start_at)"],
    "m_campaign_budget": ["remaining NUMERIC(16, 2) NOT NULL CHECK (remaining >= 0)",
                          "CONSTRAINT ck_m_campaign_budget_remaining_within_budget CHECK (remaining <= budget)"],
    "m_campaign_budget_ledger": ["order_id UUID NOT NULL REFERENCES sales.t_order (id) ON DELETE RESTRICT",
                                 "entry_type VARCHAR(16) NOT NULL CHECK (entry_type IN ('RESERVE', 'RELEASE'))",
                                 "UNIQUE (campaign_budget_id, order_id, entry_type)",
                                 "campaign_budget_id UUID NOT NULL REFERENCES campaign.m_campaign_budget (id) ON DELETE CASCADE"],
    "t_campaign_product": ["CONSTRAINT ck_t_campaign_product_target CHECK ( (product_category_id IS NULL) <> (product_id IS NULL) )"],
    "t_campaign_shop": [],
    "t_campaign_discount": ["discount_value NUMERIC(16, 2) NOT NULL CHECK (discount_value > 0)",
                            "CONSTRAINT ck_t_campaign_discount_percentage CHECK ( discount_type <> 'PERCENTAGE' OR discount_value <= 100 )"],
}
CAMPAIGN_DOC_NEEDLES = {
    "m_campaign": ["ck_m_campaign_period", "uq_m_campaign_name"],
    "m_campaign_budget": ["ck_m_campaign_budget_remaining_within_budget", "uq_m_campaign_budget_campaign_id", "| remaining "],
    "m_campaign_budget_ledger": ["fk_m_campaign_budget_ledger_order_id", "ON DELETE RESTRICT", "ck_m_campaign_budget_ledger_entry_type",
                                 "uq_m_campaign_budget_ledger_campaign_budget_id_order_id_entry_type", "| entry_type ", "| order_id "],
    "t_campaign_product": ["ck_t_campaign_product_target", "uq_t_campaign_product_campaign_id_product_id",
                           "uq_t_campaign_product_campaign_id_product_category_id"],
    "t_campaign_shop": ["uq_t_campaign_shop_campaign_id_shop_id"],
    "t_campaign_discount": ["ck_t_campaign_discount_percentage", "uq_t_campaign_discount_campaign_id", "discount_value > 0"],
}
CAMPAIGN_README_ROWS = {
    "m_campaign": "| [m_campaign](campaign/m_campaign.md) | Master | 10 | 0 |",
    "m_campaign_budget": "| [m_campaign_budget](campaign/m_campaign_budget.md) | Master | 9 | 1 |",
    "m_campaign_budget_ledger": "| [m_campaign_budget_ledger](campaign/m_campaign_budget_ledger.md) | Master | 13 | 3 |",
    "t_campaign_product": "| [t_campaign_product](campaign/t_campaign_product.md) | Transaction | 9 | 3 |",
    "t_campaign_shop": "| [t_campaign_shop](campaign/t_campaign_shop.md) | Transaction | 8 | 2 |",
    "t_campaign_discount": "| [t_campaign_discount](campaign/t_campaign_discount.md) | Transaction | 9 | 1 |",
}


def check_campaign_schema() -> int:
    """campaign.*: period, one live budget with remaining, ledger entry type per order, product target, one live discount."""
    errors = []
    sql = read(CAMPAIGN_MIGRATION)
    for table, parts in CAMPAIGN_TABLE_PARTS.items():
        statements = schema_statements(sql, "campaign", table)
        create = [s for s in statements if s.startswith("CREATE TABLE")]
        if len(create) != 1:
            errors.append(f"migration 09: {table} must be created exactly once")
            continue
        if "UNIQUE" in create[0] and table != "m_campaign_budget_ledger":
            errors.append(f"migration 09: {table} must be created without an inline UNIQUE (a partial unique index is used)")
        for part in parts:
            if normalize(part) not in create[0]:
                errors.append(f"migration 09: {table} is missing: {part[:70]}")
        indexes = [s for s in statements if s.startswith("CREATE UNIQUE INDEX")]
        if indexes != [normalize(i) for i in CAMPAIGN_INDEXES[table]]:
            errors.append(f"migration 09: the partial unique indexes of {table} are missing or different")
        path = f"{CAMPAIGN_SCHEMA_DOC}/{table}.md"
        md = read(path)
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        if schema_statements(" ".join(SQL_BLOCK.findall(md)), "campaign", table) != statements:
            errors.append(f"{path} SQL differs from the migration")
        for needle in CAMPAIGN_DOC_NEEDLES[table]:
            if needle not in md:
                errors.append(f"{path} missing: {needle}")
    readme = read("e-commerce/doc/schema/README.md")
    for table, row in CAMPAIGN_README_ROWS.items():
        if row not in readme:
            errors.append(f"README missing: {row}")
    er = read("e-commerce/db/er-diagram.drawio")
    for text in ("entry_type : varchar(16)", "UNIQUE (campaign_budget_id, order_id, entry_type)", "↗ sales.t_order"):
        if er.count(text) < (1 if text.startswith("↗") else 2):
            errors.append(f"ER diagram: '{text}' is not drawn where it must be (pages 7 and 8; the sales.t_order stub on page 7)")
    test = ROOT / "e-commerce/db/tests/09-campaign.test.sql"
    if not test.exists():
        errors.append("db/tests/09-campaign.test.sql does not exist")
    else:
        text = test.read_text(encoding="utf-8")
        for n in range(1, 12):
            if f"PASS test {n}:" not in text:
                errors.append(f"09-campaign.test.sql has no test {n}")
    if errors:
        return fail("; ".join(errors))
    print("OK: campaign-schema")
    return 0


COMMANDS["campaign-schema"] = check_campaign_schema


CAMPAIGN_SPECS = {
    "01": "e-commerce/doc/api/campaign/01-upsert-campaign/spec.md",
    "02": "e-commerce/doc/api/campaign/02-inquiry-campaign/spec.md",
    "03": "e-commerce/doc/api/campaign/03-inquiry-campaign-ledger/spec.md",
}
CAMPAIGN_SUCCESS_CODES = {
    "01": {"Success - Insert": 201, "Success - Update": 200, "Success - Delete": 204, "Success - Archive": 200},
    "02": {"Success": 200, "Success - Shop": 200, "Success - Empty": 200},
    "03": {"Success": 200, "Success - Empty": 200},
}
CAMPAIGN_NEEDLES = {
    "01": ["- Only a platform administrator (a user that has the role `PLATFORM_ADMIN`) can call this API", "ck_m_campaign_period", "#### QUERY - Check existing campaign", "#### QUERY - Check duplicate campaign name",
           "#### INSERT - Create campaign", "#### UPDATE - Update, delete or archive campaign", "#### QUERY - Check campaign used",
           "#### INSERT - Create budget", "#### UPDATE - Change budget", "AND (budget - remaining) <= '<sequence.budget.budget>'",
           "'<sequence.budget.budget>', '<sequence.budget.budget>'", "#### INSERT - Create discount", "#### INSERT - Create campaign shop",
           "#### INSERT - Create campaign product", "#### QUERY - Check shop", "#### QUERY - Check product", "#### QUERY - Check product category",
           "#### Fail - Conflict In Use", "#### Fail - Conflict Budget Below Used", "#### Fail - Not Found Reference", "#### Fail - Forbidden",
           "#### Fail - Bad Request Row Status", "E10003", "E10005", "E10006", "E10009", "Delete 204 No Content (no response body)",
           "#### QUERY - Get the platform administrator role", "#### QUERY - Check platform administrator",
           "validate the request (400) -> existence of the campaign, the children and the shops, products and categories (404) -> permission (403)", "#### QUERY - Check existing campaign shop", "#### QUERY - Check existing campaign product", "#### UPDATE - Delete the discount of a deleted campaign", "#### UPDATE - Delete the shops of a deleted campaign", "#### UPDATE - Delete the products of a deleted campaign", "one statement for all the rows of the campaign", "approved by the product owner on 2026-11-08"],
    "02": ["- A platform administrator (a user that has the role `PLATFORM_ADMIN`) sees every campaign", "ORDER BY c.start_at DESC, c.id", "NOT EXISTS (", "cs.row_status = 'ACTIVE'", "#### QUERY - Count the campaigns",
           "#### QUERY - Check shop member", "#### QUERY - Check shop", "#### QUERY - Check platform administrator", "#### Fail - Forbidden",
           "#### Fail - Not Found Reference", "activeOnly", "#### QUERY - Get the budgets of the campaigns", "#### QUERY - Get the shops of the campaigns",
           "validate the request (400) -> existence of the shop (404) -> permission (403) -> read"],
    "03": ["- Only a platform administrator (a user that has the role `PLATFORM_ADMIN`) can call this API", "ORDER BY l.created_at DESC, l.id", "#### QUERY - Count the ledger entries", "#### Fail - Forbidden",
           "#### Fail - Not Found", "budget - remaining = sum of RESERVE usage - sum of RELEASE usage", "#### QUERY - Check campaign",
           "#### QUERY - Check platform administrator", "validate the request (400) -> existence of the campaign (404) -> permission (403) -> read"],
}
CAMPAIGN_COUNTS = {
    "01": {"approved by the product owner": 2, "'<sequence.discount.": 8, "E10006": 3},
    "02": {"approved by the product owner": 2, "FROM campaign.t_campaign_shop cs": 3, "OR NOT EXISTS (": 2, "AND cs.row_status = 'ACTIVE'": 4},
    "03": {"approved by the product owner": 2, "-- only when entryType is specified": 2, "-- only when orderId is specified": 2},
}
CAMPAIGN_DISCOUNT_TYPES = ("PERCENTAGE", "FIXED_AMOUNT")


def check_campaign_data(label: str, c: dict, shop_view: bool) -> list[str]:
    """One campaign object of an example: money arithmetic, discount range, and what a shop member may see."""
    errors = []
    if not c["startAt"] < c["endAt"]:
        errors.append(f"{label}: endAt must be after startAt")
    d = c["discount"]
    if d["discountType"] not in CAMPAIGN_DISCOUNT_TYPES or d["discountValue"] <= 0 or (d["discountType"] == "PERCENTAGE" and d["discountValue"] > 100):
        errors.append(f"{label}: the discount is outside its range")
    b = c["budget"]
    if shop_view:
        if b is not None or c["shops"] is not None:
            errors.append(f"{label}: a member of a shop does not see the budget and the shops (null)")
    else:
        if b is None:
            errors.append(f"{label}: a platform administrator sees the budget")
        else:
            if round(b["budget"] - b["remaining"], 2) != b["used"] or not 0 <= b["remaining"] <= b["budget"]:
                errors.append(f"{label}: used must be budget - remaining and remaining must be between 0 and budget")
    for p in c["products"]:
        if (p["productCategoryId"] is None) == (p["productId"] is None):
            errors.append(f"{label}: a campaign product names a product or a category, exactly one")
    if c["shops"] is not None:
        ids = [s["shopId"] for s in c["shops"]]
        if len(ids) != len(set(ids)):
            errors.append(f"{label}: a shop appears twice")
    return errors


def check_campaign_upsert_examples(md: str) -> list[str]:
    errors = []
    bodies = re.search(r"#### Example Body Parameters\n\n(.*?)\n\n## Example Request", md, re.DOTALL)
    blocks = [json.loads(b) for b in re.findall(r"```JSON\n(.*?)```", bodies.group(1), re.DOTALL)] if bodies else []
    if len(blocks) != 4:
        return ["01: expected four example bodies (insert, update, delete, archive)"]
    insert, update, delete, archive = blocks
    if "id" in insert or not all("id" in b for b in (update, delete, archive)):
        errors.append("01: insert has no id, update, delete and archive have one")
    if delete.get("rowStatus") != "DELETED" or archive.get("rowStatus") != "ARCHIVED":
        errors.append("01: the delete and archive examples need rowStatus DELETED and ARCHIVED")
    if len({insert["id"] if "id" in insert else None, update["id"], delete["id"], archive["id"]}) != 4:
        errors.append("01: the update, delete and archive examples are three different campaigns")
    for b in blocks:
        if not b["startAt"] < b["endAt"]:
            errors.append("01: an example body ends before it starts")
        for p in b.get("products", []):
            if ("productId" in p) == ("productCategoryId" in p):
                errors.append("01: an example product row names a product or a category, exactly one")
    ins = json_examples(md, "Success - Insert")
    upd = json_examples(md, "Success - Update")
    arc = json_examples(md, "Success - Archive")
    if not (ins and upd and arc):
        return errors + ["01: a success example has no JSON"]
    ins, upd, arc = ins["data"], upd["data"], arc["data"]
    for label, data in (("Insert", ins), ("Update", upd), ("Archive", arc)):
        errors.extend(check_campaign_data(f"01 {label}", data, False))
    if ins["budget"]["remaining"] != ins["budget"]["budget"] or ins["budget"]["used"] != 0:
        errors.append("01: a campaign that was just inserted has used nothing (remaining = budget)")
    if update["id"] != ins["campaignId"] or upd["campaignId"] != update["id"]:
        errors.append("01: the update example changes the campaign that the insert example created")
    if update["budget"]["id"] != upd["budget"]["budgetId"] or update["budget"]["budget"] != upd["budget"]["budget"]:
        errors.append("01: the update answer must show the budget that the request sent")
    if update["discount"]["discountValue"] != upd["discount"]["discountValue"]:
        errors.append("01: the update answer must show the discount that the request sent")
    if upd["budget"]["used"] <= 0:
        errors.append("01: the update example must show a budget that was already used, to show that remaining keeps it")
    if arc["campaignId"] != archive["id"] or arc["rowStatus"] != "ARCHIVED" or arc["name"] != archive["name"]:
        errors.append("01: the archive answer must match the archive request")
    return errors


def check_campaign_inquiry_examples(md: str) -> list[str]:
    errors = []
    admin = json_examples(md, "Success")
    shop = json_examples(md, "Success - Shop")
    empty = json_examples(md, "Success - Empty")
    if not (admin and shop and empty):
        return ["02: a success example has no JSON"]
    for title, body, shop_view in (("Success", admin, False), ("Success - Shop", shop, True), ("Success - Empty", empty, False)):
        data = body["data"]
        rows = data["campaigns"]
        if data["totalItems"] != len(rows) and data["totalPages"] <= 1:
            errors.append(f"02 '{title}': totalItems is not the number of campaigns on a single page")
        if data["totalPages"] != -(-data["totalItems"] // data["pageSize"]):
            errors.append(f"02 '{title}': totalPages is not the ceiling of totalItems / pageSize")
        starts = [r["startAt"] for r in rows]
        if starts != sorted(starts, reverse=True):
            errors.append(f"02 '{title}': campaigns must be ordered by startAt, newest first")
        for r in rows:
            errors.extend(check_campaign_data(f"02 '{title}' {r['name']}", r, shop_view))
    if empty["data"]["campaigns"] or empty["data"]["totalPages"] != 0:
        errors.append("02: the empty example has no campaigns and totalPages 0")
    return errors


def check_campaign_ledger_examples(md: str) -> list[str]:
    errors = []
    body = json_examples(md, "Success")
    empty = json_examples(md, "Success - Empty")
    if not (body and empty):
        return ["03: a success example has no JSON"]
    data = body["data"]
    rows = data["entries"]
    created = [r["createdAt"] for r in rows]
    if created != sorted(created, reverse=True):
        errors.append("03: entries must be newest first")
    if data["totalItems"] != len(rows) or data["totalPages"] != -(-data["totalItems"] // data["pageSize"]):
        errors.append("03: totalItems and totalPages do not match the entries")
    for r in rows:
        if r["usage"] <= 0 or r["remaining"] < 0:
            errors.append("03: usage is positive and remaining is not negative")
        if round(sum(i["discount"] for i in r["reference"]), 2) != r["usage"]:
            errors.append("03: the discounts in reference must add up to usage")
        if r["entryType"] not in ("RESERVE", "RELEASE"):
            errors.append("03: unknown entry type")
    ordered = sorted(rows, key=lambda r: r["createdAt"])
    for before, after in zip(ordered, ordered[1:]):
        step = -after["usage"] if after["entryType"] == "RESERVE" else after["usage"]
        if round(before["remaining"] + step, 2) != after["remaining"]:
            errors.append("03: remaining after an entry must be the remaining before it minus the usage of a RESERVE or plus the usage of a RELEASE")
    if empty["data"]["entries"] or empty["data"]["totalPages"] != 0:
        errors.append("03: the empty example has no entries and totalPages 0")
    return errors


CAMPAIGN_RELEASE_NEEDLES = ["goes back in the same transaction as the stock", "#### QUERY - Get the budget that the order took",
                            "#### INSERT - Write the release in the ledger", "#### UPDATE - Give the budget back", "AND r.entry_type = 'RELEASE'",
                            "remaining = remaining + '<sequence.usage>'", "[campaign.m_campaign_budget_ledger]"]
CAMPAIGN_IN_USE_NEEDLES = ["cannot be deleted while it is in a campaign that is not DELETED and has not ended", "#### Fail - Conflict Campaign In Use",
                           "AND c.end_at > NOW() AT TIME ZONE 'UTC'", "AND c.row_status <> 'DELETED'", "campaign.m_campaign c"]
CAMPAIGN_DISCOUNT_NEEDLES = ["- Discount rules: a campaign applies to an item only when the campaign is ACTIVE", "- One campaign for each item:",
                             "(selling_price - cost_price) x quantity", "#### QUERY - Get the campaigns that apply to the shop",
                             "#### QUERY - Get the products and categories of the campaigns", "AND NOW() AT TIME ZONE 'UTC' < c.end_at",
                             "OR NOT EXISTS (", "ORDER BY c.id", "DISCOUNT_BUDGET_EXHAUSTED"]
CAMPAIGN_EFFECTS = {
    "e-commerce/doc/api/sales/01-inquiry-checkout/spec.md": CAMPAIGN_DISCOUNT_NEEDLES + ["Nothing is reserved here.", "#### Success - With Campaign"],
    "e-commerce/doc/api/sales/02-create-order/spec.md": [n for n in CAMPAIGN_DISCOUNT_NEEDLES if n != "DISCOUNT_BUDGET_EXHAUSTED"] + [
        "#### UPDATE - Take the budget of the campaign", "AND remaining >= '<sequence.discountTotal>'", "#### INSERT - Write the reservation in the ledger", "'RESERVE'",
        "the lots by `id`, then the budgets by `id`", "gross_profit = gross_margin x quantity - discount", "shop_profit = share_margin x quantity",
        "platform_profit = platform_margin x quantity - discount", "'<sequence.totalDiscount>'", "'<sequence.discount>'", "#### Fail - Conflict Discount Budget",
        "#### Success - With Campaign", "**Discount Example**", "#### Success - With Capped Discount"],
    "e-commerce/doc/api/sales/05-cancel-order/spec.md": CAMPAIGN_RELEASE_NEEDLES + ["also when the system cancels it because `expires_at` has passed"],
    "e-commerce/doc/api/payment/05-refund-payment/spec.md": CAMPAIGN_RELEASE_NEEDLES + ["when the payment is refunded"],
    "e-commerce/doc/api/payment/02-stripe-webhook/spec.md": CAMPAIGN_RELEASE_NEEDLES + ["does not touch the budget"],
    "e-commerce/doc/api/shop/08-upsert-shop/spec.md": CAMPAIGN_IN_USE_NEEDLES + ["#### QUERY - Check shop campaigns in use", "cs.shop_id = '<sequence.id>'"],
    "e-commerce/doc/api/shop/09-upsert-shop-batch/spec.md": CAMPAIGN_IN_USE_NEEDLES + ["#### QUERY - Check shop campaigns in use", "cs.shop_id = '<sequence.id>'"],
    "e-commerce/doc/api/product/01-upsert-product/spec.md": CAMPAIGN_IN_USE_NEEDLES + ["#### QUERY - Check product campaigns in use", "cp.product_id = '<sequence.id>'"],
    "e-commerce/doc/api/product/03-upsert-product-batch/spec.md": CAMPAIGN_IN_USE_NEEDLES + ["#### QUERY - Check product campaigns in use", "cp.product_id = '<sequence.id>'"],
    "e-commerce/doc/api/product/04-upsert-product-category/spec.md": CAMPAIGN_IN_USE_NEEDLES + ["#### QUERY - Check product category campaigns in use", "cp.product_category_id = '<sequence.id>'"],
    "e-commerce/doc/api/product/06-upsert-product-category-batch/spec.md": CAMPAIGN_IN_USE_NEEDLES + ["#### QUERY - Check product category campaigns in use", "cp.product_category_id = '<sequence.id>'"],
}


# cap of an order item of the examples: (selling_price - cost_price) x quantity of its lot (sales/04 shows the same two items)
CAMPAIGN_ITEM_CAP = {"e1f2a3b4-3c4d-4e5f-9a6b-7c8d9e0f1a21": 158.0, "e2a3b4c5-4d5e-4f60-8b7c-8d9e0f1a2b32": 84.0}


def check_discount_example(md: str) -> list[str]:
    """The worked example of sales/02: FIXED_AMOUNT discount, the cap, the profits, and the capped success example that follows from it."""
    errors = []
    m = re.search(r"\*\*Discount Example\*\*\n\n.*?\n\n((?:\|[^\n]*\n)+)", md, re.DOTALL)
    if not m:
        return ["sales/02: the Discount Example table is missing"]
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in m.group(1).strip().split("\n")][2:]
    total_price = total_discount = 0.0
    capped_rows = 0
    for r in rows:
        item, price, cost, qty, campaign, raw, cap, discount, gross_before, shop, gross_profit, platform = r
        price, cost, qty, raw, cap, discount, gross_before, shop, gross_profit, platform = (float(x) for x in (price, cost, qty, raw, cap, discount, gross_before, shop, gross_profit, platform))
        kind, value = campaign.split()
        value = float(value)
        expected_raw = round(price * qty * value / 100, 2) if kind == "PERCENTAGE" else round(value * qty, 2)
        if expected_raw != raw:
            errors.append(f"sales/02 discount example {item}: the discount before the cap should be {expected_raw}")
        if round((price - cost) * qty, 2) != cap:
            errors.append(f"sales/02 discount example {item}: the cap should be (selling price - cost price) x quantity = {round((price - cost) * qty, 2)}")
        if discount != min(raw, cap):
            errors.append(f"sales/02 discount example {item}: the discount should be the smaller of the discount before the cap and the cap")
        if discount > cap:
            errors.append(f"sales/02 discount example {item}: the discount is above the cap")
        if gross_before != cap:
            errors.append(f"sales/02 discount example {item}: gross margin x quantity should equal the cap")
        if round(gross_before - discount, 2) != gross_profit or gross_profit < 0:
            errors.append(f"sales/02 discount example {item}: gross profit should be gross margin - discount and never below 0")
        if round(gross_before - shop - discount, 2) != platform:
            errors.append(f"sales/02 discount example {item}: platform profit should be gross margin - shop profit - discount")
        capped_rows += raw > cap
        total_price += price * qty
        total_discount += discount
    if not capped_rows or capped_rows == len(rows):
        errors.append("sales/02 discount example: one item must be cut by the cap and one must stay under it")
    capped = json_examples(md, "Success - With Capped Discount")
    if capped:
        first = capped["data"]["orders"][0]
        if round(first["totalPrice"], 2) != round(total_price, 2) or round(first["totalDiscount"], 2) != round(total_discount, 2):
            errors.append("sales/02: the capped example must have the totalPrice and the totalDiscount of the discount example table")
    else:
        errors.append("sales/02: the capped discount example has no JSON")
    return errors


def check_campaign_effects() -> list[str]:
    """The proposals E1 to E7 of the campaign design: every delivered spec that the campaign touches still carries its rule, its SQL and its example."""
    errors = []
    for path, needles in CAMPAIGN_EFFECTS.items():
        md = read(path)
        # rules that moved into a note of the sequence diagram are searched there, one line per wrapped note
        seq = re.sub(r"\n\s+", " ", read(path.replace("spec.md", "sequence.wsd")))
        for missing in missing_needles(md + "\n" + seq, needles):
            errors.append(f"{path} missing: {missing}")
        if "Fail - Conflict Campaign In Use" in md:
            example = json_examples(md, "Fail - Conflict Campaign In Use")
            if not example or example["status"]["code"] != 409 or example["status"]["bizCode"] != "E10006":
                errors.append(f"{path}: the campaign in use example must be 409 with E10006")
        if "Fail - Conflict Discount Budget" in md:
            example = json_examples(md, "Fail - Conflict Discount Budget")
            if not example or example["status"]["code"] != 409 or example["status"]["bizCode"] != "E10007":
                errors.append(f"{path}: the discount budget example must be 409 with E10007")
    errors.extend(check_discount_example(read("e-commerce/doc/api/sales/02-create-order/spec.md")))
    ledger_example = json_examples(read(CAMPAIGN_SPECS["03"]), "Success")
    for e in (ledger_example["data"]["entries"] if ledger_example else []):
        for i in e["reference"]:
            cap = CAMPAIGN_ITEM_CAP.get(i["orderItemId"])
            if cap is not None and i["discount"] > cap:
                errors.append(f"campaign ledger example: the discount {i['discount']} of an order item is above its cap {cap}")
    # the order that the ledger example names is the order of the campaign example of the create order spec
    ledger = json_examples(read(CAMPAIGN_SPECS["03"]), "Success")
    created = None
    for title, raw in re.findall(r"^#### (Success - With Campaign)\n\n```JSON\n(.*?)```", read("e-commerce/doc/api/sales/02-create-order/spec.md"), re.MULTILINE | re.DOTALL):
        created = json.loads(raw)
    if ledger and created:
        reserved = [e for e in ledger["data"]["entries"] if e["entryType"] == "RESERVE"]
        orders = {o["orderId"]: o for o in created["data"]["orders"]}
        for e in reserved:
            o = orders.get(e["orderId"])
            if o is None:
                errors.append("campaign ledger example: the RESERVE entry names an order that is not in the create order campaign example")
            elif round(o["totalDiscount"], 2) != e["usage"]:
                errors.append(f"campaign ledger example: usage {e['usage']} is not the totalDiscount {o['totalDiscount']} of the order in sales/02")
    return errors


def check_campaign_spec() -> int:
    errors = []
    mds = {}
    for key, path in CAMPAIGN_SPECS.items():
        try:
            mds[key] = read(path)
        except FileNotFoundError:
            errors.append(f"{path} does not exist")
            continue
        md = mds[key]
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        for bad in json_blocks_parse(md):
            errors.append(f"{path} invalid JSON block: {bad[:40]}")
        for link in relative_links_exist(path, md):
            errors.append(f"{path} broken link {link}")
    if errors:
        return fail("; ".join(errors))
    for key, need in CAMPAIGN_NEEDLES.items():
        # rules that moved into a note of the sequence diagram are searched there, one line per wrapped note
        seq = re.sub(r"\n\s+", " ", read(CAMPAIGN_SPECS[key].replace("spec.md", "sequence.wsd")))
        for missing in missing_needles(mds[key] + "\n" + seq, need):
            errors.append(f"{CAMPAIGN_SPECS[key]} missing: {missing}")
    for key, counts in CAMPAIGN_COUNTS.items():
        for phrase, n in counts.items():
            if mds[key].count(phrase) < n:
                errors.append(f"{CAMPAIGN_SPECS[key]}: '{phrase[:60]}' must appear at least {n} times, found {mds[key].count(phrase)}")
    for key, want in CAMPAIGN_SUCCESS_CODES.items():
        if success_codes(mds[key]) != want:
            errors.append(f"{CAMPAIGN_SPECS[key]}: success examples should be {want}, found {success_codes(mds[key])}")
    for key, md in mds.items():
        params = re.search(r"### (?:Query|Body) Parameters.*?(?=\n### |\n#### Example|\n## )", md, re.DOTALL)
        if params and "userId" in params.group(0):
            errors.append(f"{CAMPAIGN_SPECS[key]}: the request must not carry a user id")
        if "PLATFORM_ADMIN" not in md:
            errors.append(f"{CAMPAIGN_SPECS[key]}: the rules must name the platform administrator")
        for forbidden in ("email", "username", "costPrice", "cost_price"):
            if forbidden in md:
                errors.append(f"{CAMPAIGN_SPECS[key]} must not contain '{forbidden}'")
    for key in ("01", "03"):
        if "QUERY - Check shop member" in mds[key]:
            errors.append(f"{CAMPAIGN_SPECS[key]}: only a platform administrator calls it, there is no shop member check")
    errors.extend(check_campaign_effects())
    errors.extend(check_campaign_upsert_examples(mds["01"]))
    errors.extend(check_campaign_inquiry_examples(mds["02"]))
    errors.extend(check_campaign_ledger_examples(mds["03"]))
    if errors:
        return fail("; ".join(errors))
    print("OK: campaign-spec")
    return 0


COMMANDS["campaign-spec"] = check_campaign_spec



# ---------------------------------------------------------------- author (WP5a): role, permission, scope, user role, me
AUTHOR_DIR = "e-commerce/doc/api/author"
AUTHOR_SPECS = {
    "01": "01-upsert-role", "02": "02-upsert-role-batch", "03": "03-inquiry-role", "04": "04-upsert-permission", "05": "05-upsert-permission-batch",
    "06": "06-inquiry-permission", "07": "07-upsert-scope", "08": "08-upsert-scope-batch", "09": "09-inquiry-scope", "10": "10-upsert-user-role",
    "11": "11-inquiry-user-role", "12": "12-me",
}
AUTHOR_MASTERS = {  # key: (upsert, batch, inquiry, path, Title, lower, camel, alias, unique column, id field, regex of a valid code, in-use message)
    "role": ("01", "02", "03", "role", "Role", "role", "role", "r", "name", "roleId", r"^[A-Z][A-Z0-9_]{0,63}$", "Role is assigned to users or has permissions."),
    "permission": ("04", "05", "06", "permission", "Permission", "permission", "permission", "p", "name", "permissionId", r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$", "Permission is used by roles or users."),
    "scope": ("07", "08", "09", "scope", "Scope", "scope", "scope", "s", "scope", "scopeId", r"^[A-Z][A-Z0-9_]{0,63}$", "Scope is used by permissions."),
}
SINGLE_UPSERT_SPECS.extend(f"{AUTHOR_DIR}/{AUTHOR_SPECS[k]}/spec.md" for k in ("01", "04", "07", "10"))
BATCH_UPSERT_SPECS.extend(f"{AUTHOR_DIR}/{AUTHOR_SPECS[k]}/spec.md" for k in ("02", "05", "08"))
AUTHOR_ADMIN = ["#### QUERY - Get the platform administrator role", "#### QUERY - Check platform administrator", "WHERE r.name = 'PLATFORM_ADMIN'", "AND r.row_status = 'ACTIVE'",
                "AND ur.role_id = '<sequence.roleId>'", "AND ur.row_status = 'ACTIVE'", "(../../../schema/author/m_role.md)", "(../../../schema/author/t_user_role.md)", "Approved by the product owner"]
AUTHOR_USER_ROLE = "5e6f7a8b-9c0d-4e1f-8a2b-3c4d5e6f7a8b"
AUTHOR_FORBIDDEN_TEXT = {"10": ["The user must be ACTIVE and the role must be ACTIVE, otherwise 404", "#### QUERY - Get the platform administrator role", "#### QUERY - Check platform administrator", "NOW()"]}


def author_json(md: str, heading: str):
    match = re.search(rf"^#### {re.escape(heading)}\n\n(?:Request: [^\n]*\n\n)?```JSON\n(.*?)```", md, re.MULTILINE | re.DOTALL)
    return json.loads(match.group(1)) if match else None


def author_status(md: str, title: str, code: int, biz: str, message: str | None = None) -> list[str]:
    body = author_json(md, title)
    if body is None:
        return [f"no JSON in '{title}'"]
    status = body["status"]
    errors = []
    if status["code"] != code or status["bizCode"] != biz:
        errors.append(f"'{title}' must be {code} {biz}")
    if message is not None and status["bizMessage"] != message:
        errors.append(f"'{title}' must say {message!r}")
    return errors


def author_needles(key: str):
    kind = {"01": "upsert", "04": "upsert", "07": "upsert", "02": "batch", "05": "batch", "08": "batch", "03": "inquiry", "06": "inquiry", "09": "inquiry"}[key]
    m = next(v for v in AUTHOR_MASTERS.values() if key in v[:3])
    _, _, _, path, title, lower, camel, alias, ucol, idname, _, use_msg = m
    base = [*AUTHOR_ADMIN, "E10009", "#### Fail - Forbidden", f"You do not have permission to {'read' if kind == 'inquiry' else 'manage'} {lower}s."]
    if key in ("01", "02", "05", "07", "08"):
        base = ["Permission: only a platform administrator from the verified JWT roles claim", "Approved by the product owner", "E10009", "#### Fail - Forbidden", f"You do not have permission to manage {lower}s."]
    if key in ("03", "06", "09"):
        base = ["use exact PLATFORM_ADMIN in verified JWT role claims", "Approved by the product owner", "E10009", "#### Fail - Forbidden", f"You do not have permission to read {lower}s."]
    if key == "04":
        base = ["Permission: only a platform administrator from verified JWT roles", "Approved by the product owner", "E10009", "#### Fail - Forbidden", "You do not have permission to manage permissions."]
    if kind in ("upsert", "batch") and key not in ("01", "02", "04", "05", "07", "08"):
        base.append("Permission: only a platform administrator (a user with an ACTIVE `author.t_user_role` row for the ACTIVE role `PLATFORM_ADMIN`) can call this API")
    if kind == "upsert":
        need = [f"# [POST]: v1/author/{path}/upsert", f"### {title} Rules", "-> permission (403, E10009) ->", f"{title} not found.", use_msg, f"{title} {ucol} already exists.",
                f"Row status must not be DELETED when inserting a {lower}.", f"The value of a DELETED {lower} can be used again.", "Delete 204 No Content", "Archive when rowStatus is ARCHIVED",
                f"AND {alias}.row_status <> 'DELETED' -- the id of a DELETED {lower} counts as not found", f"AND {alias}.row_status <> 'DELETED'\nAND {alias}.id <> '<sequence.id>'",
                "Insert " + title + " Success", "Archive " + title + " Success", "E10003", "E10004", "E10006", "E90001"]
        if lower == "role":
            need += ["is the system role", "#### Fail - Conflict System Role", "#### QUERY - Check system role", f"AND {alias}.name = 'PLATFORM_ADMIN'", "System role cannot be changed."]
        if lower == "permission":
            need += ["#### Scope Object", "#### QUERY - Check scope", "#### QUERY - Check role permission scope in use", "#### QUERY - Check user permission scope in use", "Scope is used by roles or users.",
                     "#### Fail - Not Found Scope", "Scopes that are not listed are kept."]
        if key == "01":
            need = [x.replace("AND r.id <> '<sequence.id>'", "AND ('<sequence.id>' IS NULL OR r.id <> '<sequence.id>')") for x in need]
        if key == "04":
            need = [x.replace("AND p.id <> '<sequence.id>'", "AND ('<sequence.id>' IS NULL OR p.id <> '<sequence.id>')") for x in need]
        if key == "07":
            need = [x.replace("AND s.id <> '<sequence.id>'", "AND ('<sequence.id>' IS NULL OR s.id <> '<sequence.id>')") for x in need]
        return base + need
    if kind == "batch":
        need = [f"# [POST]: v1/author/{path}/upsert/batch", f"### {title} Rules (same as the single upsert, applied per {lower})", f"{camel}s[2]: Id is duplicated with {camel}s[1].", f"{camel}s[2]: {ucol.capitalize()} is duplicated with {camel}s[0].",
                f"{title}s must contain 1 to 100 items.", "The 403 message has no item position", "always HTTP 200", "ARCHIVE)", f"{camel}s[0]: {title} {ucol} already exists.", f"{camel}s[2]: {use_msg}",
                f"{camel}s[1]: {title} not found.", "Batch Upsert " + title + " Success"]
        if lower == "role":
            need += [f"{camel}s[1]: System role cannot be changed.", "#### QUERY - Check system role"]
        if lower == "permission":
            need += ["#### Scope Object", "#### QUERY - Check scope", f"{camel}s[0]: Scope not found."]
        return base + need
    need = [f"# [GET]: v1/author/{path}", f"### {title} Inquiry Rules", f"ORDER BY {alias}.{ucol}, {alias}.id", f"Request: `GET v1/author/{path}?id=", "Row status must be one of ACTIVE, INACTIVE, LOCKED, ARCHIVED.",
            "Page Index and Page Size must be greater than 0", "Only a platform administrator can read", f"Inquiry {title} Success", f"WHERE {alias}.row_status <> 'DELETED'"]
    if lower == "permission":
        need += ["#### Scope Object", "#### QUERY - Get the scopes of the permissions", "#### QUERY - Get scope"]
    return base + need


def author_counted(key: str):
    m = next((v for v in AUTHOR_MASTERS.values() if key in v[:3]), None)
    if key == "03":
        return [("AND ('<sequence.id>' IS NULL OR r.id = '<sequence.id>') -- only when id is specified", 2),
                ("AND ('<sequence.searchPattern>' IS NULL OR r.name ILIKE '<sequence.searchPattern>' OR r.description ILIKE '<sequence.searchPattern>') -- only when search is specified", 2),
                ("AND ('<sequence.rowStatus>' IS NULL OR r.row_status = '<sequence.rowStatus>') -- only when rowStatus is specified", 2)]
    if key == "09":
        return [("AND ('<sequence.id>' IS NULL OR s.id = '<sequence.id>') -- only when id is specified", 2),
                ("AND ('<sequence.searchPattern>' IS NULL OR s.scope ILIKE '<sequence.searchPattern>' OR s.description ILIKE '<sequence.searchPattern>') -- only when search is specified", 2),
                ("AND ('<sequence.rowStatus>' IS NULL OR s.row_status = '<sequence.rowStatus>') -- only when rowStatus is specified", 2)]
    if key == "06":
        return [("AND ('<sequence.id>' IS NULL OR p.id = '<sequence.id>') -- only when id is specified", 2),
                ("AND ('<sequence.searchPattern>' IS NULL OR p.name ILIKE '<sequence.searchPattern>' OR p.description ILIKE '<sequence.searchPattern>') -- only when search is specified", 2),
                ("AND ('<sequence.rowStatus>' IS NULL OR p.row_status = '<sequence.rowStatus>') -- only when rowStatus is specified", 2)]
    if m and key == m[2]:
        alias, ucol = m[7], m[8]
        return [(f"AND ({alias}.{ucol} ILIKE '%<sequence.search>%' OR {alias}.description ILIKE '%<sequence.search>%') -- only when search is specified", 2),
                (f"AND {alias}.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified", 2)]
    if key == "11":
        return [("AND ('<sequence.id>' IS NULL OR ur.id = '<sequence.id>') -- only when id is specified", 2), ("AND ('<sequence.filterUserId>' IS NULL OR ur.user_id = '<sequence.filterUserId>') -- only when userId is specified", 2),
                ("AND ('<sequence.filterRoleId>' IS NULL OR ur.role_id = '<sequence.filterRoleId>') -- only when roleId is specified", 2), ("AND ('<sequence.rowStatus>' IS NULL OR ur.row_status = '<sequence.rowStatus>') -- only when rowStatus is specified", 2)]
    return []


AUTHOR_OTHER_NEEDLES = {
    "10": ["# [POST]: v1/author/user/role/upsert", "### User Role Rules", "### Credential, Lock and Transaction Rules", "**The platform keeps at least one administrator.**",
           "Lock order is users (ascending id) -> the role of the request", "#### QUERY - Lock the users", "#### QUERY - Lock the role", "#### QUERY - Lock existing user role", "ORDER BY u.id\nFOR UPDATE",
           "#### QUERY - Count the platform administrators after the write", "#### Fail - Conflict Last Administrator", "#### Fail - Not Found Target User", "The platform must keep at least one administrator.",
           "The user already has this role.", "User Id and Role Id cannot be changed.", "User not found.", "User or role not found or not ACTIVE.", "You do not have permission to assign roles.",
           "Only a platform administrator from the verified JWT roles claim", "exact case-sensitive role name PLATFORM_ADMIN", "Approved by the product owner", "uq_t_user_role_user_id_role_id",
           "Delete 204 No Content", "Archive when rowStatus is ARCHIVED", "**The user and the role must be ACTIVE only when the request gives the role**",
           "Taking the role away (`rowStatus` DELETED, ARCHIVED, INACTIVE or LOCKED) works whatever the status of the user and of the role is", "The last administrator rule below still applies in full.",
           "a missing target user is 404 (E10005) `User not found.`, also when the request takes the role away"],
    "11": ["# [GET]: v1/author/user/role", "### User Role Inquiry Rules", "ORDER BY r.name, u.display_name, ur.id", f"Request: `GET v1/author/user/role?id={AUTHOR_USER_ROLE}`", "Only a platform administrator can read the roles of users",
           "use exact PLATFORM_ADMIN in verified JWT role claims", "#### Fail - Forbidden", "E10009", "You do not have permission to read user roles.", "Inquiry User Role Success", "The four nullable filters id/userId/roleId/rowStatus"],
    "12": ["# [GET]: v1/author/me", "### Me Rules", "calling token's role snapshot", "Any caller with a valid access token can call this API", "Do not query author.t_user_role or author.m_role", "Success - Platform Administrator", "Success - No Role"],
}


def author_upsert_errors(m, md: str, batch: bool) -> list[str]:
    _, _, _, path, title, lower, camel, alias, ucol, idname, regex, use_msg = m
    errors = []
    if batch:
        request = json.loads(re.search(r"#### Example Body Parameters\n\n```JSON\n(.*?)```", md, re.DOTALL).group(1))
        items = request[f"{camel}s"]
        result = author_json(md, "Success")["data"][f"{camel}s"]
        if len(result) != len(items):
            errors.append(f"{len(result)} results for {len(items)} items")
        ids = [i["id"] for i in items if "id" in i]
        values = [i[ucol] for i in items if i.get("rowStatus") != "DELETED"]
        if len(ids) != len(set(ids)) or len(values) != len(set(values)):
            errors.append("the request repeats an id or a " + ucol)
        for position, (item, res) in enumerate(zip(items, result)):
            action = {"DELETED": "DELETE", "ARCHIVED": "ARCHIVE"}.get(item.get("rowStatus"), "UPDATE" if "id" in item else "INSERT")
            if res["index"] != position or res["action"] != action:
                errors.append(f"result {position} should be index {position} and action {action}")
            if "id" in item and res[idname] != item["id"]:
                errors.append(f"result {position} answers another {idname}")
            if "id" not in item and item.get("rowStatus") == "DELETED":
                errors.append(f"item {position} deletes without an id")
            if not re.match(regex, item[ucol]) or len(item[ucol]) > 64:
                errors.append(f"item {position} has an invalid {ucol} {item[ucol]!r}")
            if item.get(ucol) == "PLATFORM_ADMIN":
                errors.append("an example changes PLATFORM_ADMIN")
        for forbidden in ("Fail - Forbidden", "Fail - Unauthorized", "Fail - Request Timeout", "Fail - Bad Request Item Count"):
            body = author_json(md, forbidden)
            if body and "[" in body["status"]["bizMessage"]:
                errors.append(f"'{forbidden}' must have no item position")
        for t in ("Fail - Bad Request", "Fail - Not Found", "Fail - Conflict", "Fail - Conflict In Use", "Fail - Bad Request Name", "Fail - Bad Request Row Status", "Fail - Bad Request Duplicate Id", "Fail - Bad Request Duplicate Name"):
            body = author_json(md, t)
            if not body or not body["status"]["bizMessage"].startswith(f"{camel}s["):
                errors.append(f"'{t}' must start with the position {camel}s[i]")
    else:
        bodies = {t: json.loads(re.search(rf"##### {t}\n\n```JSON\n(.*?)```", md, re.DOTALL).group(1)) for t in ("Insert", "Update", "Delete")}
        if "id" in bodies["Insert"]:
            errors.append("the Insert example must not have an id")
        rid = bodies["Update"]["id"]
        if bodies["Delete"]["id"] != rid:
            errors.append("the Update and Delete examples must use the same id")
        if bodies["Delete"]["rowStatus"] != "DELETED" or bodies["Insert"]["rowStatus"] == "DELETED":
            errors.append("Delete must be DELETED and Insert must not be")
        for label, body in bodies.items():
            if not re.match(regex, body[ucol]):
                errors.append(f"the {label} example has an invalid {ucol} {body[ucol]!r}")
            if body[ucol] == "PLATFORM_ADMIN":
                errors.append(f"the {label} example changes PLATFORM_ADMIN")
            seen = [s["scopeId"] for s in body.get("scopes", []) if s.get("rowStatus") != "DELETED"]
            if len(seen) != len(set(seen)):
                errors.append(f"the {label} example lists a scope twice")
        for t in ("Success - Insert", "Success - Update", "Success - Archive"):
            body = author_json(md, t)
            if body is None or body["data"][idname] != rid:
                errors.append(f"'{t}' must answer the id of the Update example")
        if success_codes(md) != {"Success - Insert": 201, "Success - Update": 200, "Success - Delete": 204, "Success - Archive": 200}:
            errors.append(f"wrong success codes {success_codes(md)}")
        for t, code, biz in (("Fail - Bad Request", 400, "E10001"), ("Fail - Bad Request Name", 400, "E10001"), ("Fail - Unauthorized", 401, "E10002"), ("Fail - Forbidden", 403, "E10009"),
                             ("Fail - Not Found", 404, "E10004"), ("Fail - Conflict", 409, "E10003"), ("Fail - Conflict In Use", 409, "E10006"), ("Fail - Request Timeout", 408, "E90001")):
            errors += author_status(md, t, code, biz)
    errors += author_status(md, "Fail - Conflict In Use", 409, "E10006")
    if batch and set(success_codes(md).values()) != {200}:
        errors.append("every success example of a batch must answer 200")
    return errors


def author_inquiry_errors(m, md: str) -> list[str]:
    _, _, _, path, title, lower, camel, alias, ucol, idname, regex, _ = m
    errors = []
    by_id = re.search(r"Request: `GET v1/author/[^`]*\?id=([0-9a-f-]{36})`", md).group(1)
    for t in ("Success", "Success - By Id", "Success - Not Found"):
        data = author_json(md, t)["data"]
        if data["totalItems"] != len(data["items"]):
            errors.append(f"'{t}' totalItems differs from the number of items")
        if data["totalPages"] != (0 if data["totalItems"] == 0 else -(-data["totalItems"] // data["pageSize"])):
            errors.append(f"'{t}' has a wrong totalPages")
        ids = [i[idname] for i in data["items"]]
        if len(ids) != len(set(ids)) or any(i["rowStatus"] == "DELETED" for i in data["items"]):
            errors.append(f"'{t}' repeats an id or lists a DELETED row")
        values = [i[ucol] for i in data["items"]]
        if values != sorted(values):
            errors.append(f"'{t}' must be sorted by {ucol}")
        for item in data["items"]:
            if not re.match(regex, item[ucol]):
                errors.append(f"'{t}' has an invalid {ucol} {item[ucol]!r}")
            for scope in item.get("scopes", []):
                if set(scope) != {"permissionScopeId", "scopeId", "scope", "scopeName", "rowStatus"}:
                    errors.append(f"'{t}' has a scope with the wrong keys")
                if scope["rowStatus"] == "DELETED":
                    errors.append(f"'{t}' lists a DELETED scope of a permission")
        if t == "Success - By Id" and ids != [by_id]:
            errors.append("the By Id example must list only its id")
        if t == "Success - Not Found" and data["items"]:
            errors.append("the Not Found example must have no items")
    for t, code, biz in (("Fail - Bad Request", 400, "E10001"), ("Fail - Unauthorized", 401, "E10002"), ("Fail - Forbidden", 403, "E10009"), ("Fail - Request Timeout", 408, "E90001")):
        errors += author_status(md, t, code, biz)
    return errors


# Needles whose sentence now lives in a note of the sequence diagram (moved there by the template alignment) and needles whose text is gone by design
AUTHOR_SEQUENCE_NEEDLES = {
    "01": ['Permission: only a platform administrator from the verified JWT roles claim',
           'Approved by the product owner',
           '-> permission (403, E10009) ->',
           'The value of a DELETED role can be used again.',
           'Delete 204 No Content'],
    "02": ['Approved by the product owner',
           'The 403 message has no item position'],
    "03": ['use exact PLATFORM_ADMIN in verified JWT role claims',
           'Approved by the product owner'],
    "04": ['Permission: only a platform administrator from verified JWT roles',
           'Approved by the product owner',
           '-> permission (403, E10009) ->',
           'The value of a DELETED permission can be used again.',
           'Delete 204 No Content',
           'Scopes that are not listed are kept.'],
    "05": ['Approved by the product owner',
           'The 403 message has no item position'],
    "06": ['use exact PLATFORM_ADMIN in verified JWT role claims',
           'Approved by the product owner'],
    "07": ['Approved by the product owner',
           '-> permission (403, E10009) ->',
           'The value of a DELETED scope can be used again.',
           'Delete 204 No Content'],
    "08": ['Approved by the product owner',
           'The 403 message has no item position'],
    "09": ['use exact PLATFORM_ADMIN in verified JWT role claims',
           'Approved by the product owner'],
    "10": ['Lock order is users (ascending id) -> the role of the request',
           'Only a platform administrator from the verified JWT roles claim',
           'exact case-sensitive role name PLATFORM_ADMIN',
           'Approved by the product owner',
           'uq_t_user_role_user_id_role_id',
           'Taking the role away (`rowStatus` DELETED, ARCHIVED, INACTIVE or LOCKED) works whatever the status of the user and of the role is',
           'The last administrator rule below still applies in full.',
           'a missing target user is 404 (E10005) `User not found.`, also when the request takes the role away'],
    "11": ['use exact PLATFORM_ADMIN in verified JWT role claims'],
    "12": ['Any caller with a valid access token can call this API',
           'Do not query author.t_user_role or author.m_role'],
}
AUTHOR_REMOVED_NEEDLES = {
    "01": ['### Role Rules'],
    "02": ['### Role Rules (same as the single upsert, applied per role)'],
    "03": ['### Role Inquiry Rules'],
    "04": ['### Permission Rules'],
    "05": ['### Permission Rules (same as the single upsert, applied per permission)'],
    "06": ['### Permission Inquiry Rules'],
    "07": ['### Scope Rules'],
    "08": ['### Scope Rules (same as the single upsert, applied per scope)'],
    "09": ['### Scope Inquiry Rules'],
    "10": ['### User Role Rules',
           '### Credential, Lock and Transaction Rules'],
    "11": ['### User Role Inquiry Rules'],
    "12": ['### Me Rules'],
}


def author_example_errors(key: str, md: str) -> list[str]:
    errors = []
    masters = {v[0]: (v, False) for v in AUTHOR_MASTERS.values()}
    masters.update({v[1]: (v, True) for v in AUTHOR_MASTERS.values()})
    inquiry = {v[2]: v for v in AUTHOR_MASTERS.values()}
    if key in masters:
        errors += author_upsert_errors(masters[key][0], md, masters[key][1])
    elif key in inquiry:
        errors += author_inquiry_errors(inquiry[key], md)
    elif key == "10":
        bodies = {t: json.loads(re.search(rf"##### {t}\n\n```JSON\n(.*?)```", md, re.DOTALL).group(1)) for t in ("Insert", "Update", "Delete")}
        if "id" in bodies["Insert"] or bodies["Update"]["id"] != AUTHOR_USER_ROLE or bodies["Delete"]["id"] != AUTHOR_USER_ROLE:
            errors.append("Insert has no id, Update and Delete use the user role id")
        if len({(b["userId"], b["roleId"]) for b in bodies.values()}) != 1:
            errors.append("the three examples must use the same user and role")
        if bodies["Delete"]["rowStatus"] != "DELETED" or bodies["Insert"]["rowStatus"] == "DELETED":
            errors.append("Delete must be DELETED and Insert must not be")
        if success_codes(md) != {"Success - Insert": 201, "Success - Update": 200, "Success - Delete": 204, "Success - Archive": 200}:
            errors.append(f"wrong success codes {success_codes(md)}")
        for t, code, biz in (("Fail - Bad Request", 400, "E10001"), ("Fail - Bad Request User And Role Changed", 400, "E10001"), ("Fail - Unauthorized", 401, "E10002"), ("Fail - Forbidden", 403, "E10009"),
                             ("Fail - Not Found", 404, "E10004"), ("Fail - Not Found User Or Role", 404, "E10005"), ("Fail - Conflict", 409, "E10003"), ("Fail - Conflict Last Administrator", 409, "E10006"), ("Fail - Request Timeout", 408, "E90001")):
            errors += author_status(md, t, code, biz)
        errors += author_status(md, "Fail - Not Found User Or Role", 404, "E10005", "User or role not found or not ACTIVE.")
        if bodies["Update"]["rowStatus"] == "ACTIVE":
            errors.append("the Update example must show taking the role away (a row status that is not ACTIVE)")
    elif key == "11":
        for t in ("Success", "Success - By Id", "Success - Not Found"):
            data = author_json(md, t)["data"]
            if data["totalItems"] != len(data["items"]) or data["totalPages"] != (0 if not data["items"] else 1):
                errors.append(f"'{t}' has wrong totals")
            keys = [(i["roleName"], i["userDisplayName"], i["userRoleId"]) for i in data["items"]]
            if keys != sorted(keys):
                errors.append(f"'{t}' must be sorted by role name, user display name and id")
            if any(i["rowStatus"] == "DELETED" for i in data["items"]):
                errors.append(f"'{t}' lists a DELETED row")
        for t, code, biz in (("Fail - Bad Request", 400, "E10001"), ("Fail - Unauthorized", 401, "E10002"), ("Fail - Forbidden", 403, "E10009"), ("Fail - Request Timeout", 408, "E90001")):
            errors += author_status(md, t, code, biz)
    elif key == "12":
        for t in ("Success", "Success - Platform Administrator", "Success - No Role"):
            data = author_json(md, t)["data"]
            names = list(data["roles"])
            if data["isPlatformAdmin"] != ("PLATFORM_ADMIN" in names):
                errors.append(f"'{t}': isPlatformAdmin must be true exactly when PLATFORM_ADMIN is a role")
            if names != sorted(names):
                errors.append(f"'{t}': roles must be sorted by name")
        if author_json(md, "Success - No Role")["data"]["roles"] != []:
            errors.append("the No Role example must have an empty list")
        for t, code, biz in (("Fail - Unauthorized", 401, "E10002"), ("Fail - Request Timeout", 408, "E90001")):
            errors += author_status(md, t, code, biz)
        if "Fail - Forbidden" in md:
            errors.append("the me API has no 403")
    return errors


def check_author_spec() -> int:
    errors, mds = [], {}
    for key, folder in AUTHOR_SPECS.items():
        path = f"{AUTHOR_DIR}/{folder}/spec.md"
        try:
            mds[key] = read(path)
        except FileNotFoundError:
            errors.append(f"{path} does not exist")
            continue
        md = mds[key]
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        for bad in json_blocks_parse(md):
            errors.append(f"{path} invalid JSON block: {bad[:40]}")
        for link in relative_links_exist(path, md):
            errors.append(f"{path} broken link {link}")
        if "ALTER TABLE" in md:
            errors.append(f"{path} contains ALTER TABLE")
        if not re.search(r"^\| \d+ +\| authorization +\|", md, re.MULTILINE):
            errors.append(f"{path} needs the authorization header (every author API is private)")
        if not (ROOT / path).with_name("sequence.wsd").exists():
            errors.append(f"{path} has no sequence.wsd beside it")
        need = author_needles(key) if key in ("01", "02", "03", "04", "05", "06", "07", "08", "09") else AUTHOR_OTHER_NEEDLES[key]
        in_sequence = AUTHOR_SEQUENCE_NEEDLES.get(key, [])
        for missing in missing_needles(md, [x for x in need if x not in in_sequence and x not in AUTHOR_REMOVED_NEEDLES.get(key, [])]):
            errors.append(f"{path} missing: {missing!r}")
        sequence_note = " ".join((ROOT / path).with_name("sequence.wsd").read_text(encoding="utf-8").split())
        for missing in missing_needles(sequence_note, in_sequence):
            errors.append(f"{path} sequence note missing: {missing!r}")
        for forbidden in AUTHOR_FORBIDDEN_TEXT.get(key, []):
            if forbidden in md:
                errors.append(f"{path} must not contain {forbidden!r}")
        for text, times in author_counted(key):
            if md.count(text) != times:
                errors.append(f"{path}: {text!r} must appear {times} time(s), found {md.count(text)}")
    if errors:
        return fail("; ".join(errors))
    for key, md in mds.items():
        try:
            errors.extend(f"{AUTHOR_SPECS[key]}: {e}" for e in author_example_errors(key, md))
        except (KeyError, TypeError, AttributeError, ValueError, IndexError) as exc:
            errors.append(f"{AUTHOR_SPECS[key]}: an example does not have the expected shape: {exc!r}")
    if errors:
        return fail("; ".join(errors))
    print("OK: author-spec")
    return 0


COMMANDS["author-spec"] = check_author_spec

AUTHOR_NAME_INDEXES = {
    "m_role": "CREATE UNIQUE INDEX IF NOT EXISTS uq_m_role_name ON author.m_role (name) WHERE row_status <> 'DELETED'",
    "m_permission": "CREATE UNIQUE INDEX IF NOT EXISTS uq_m_permission_name ON author.m_permission (name) WHERE row_status <> 'DELETED'",
    "m_scope": "CREATE UNIQUE INDEX IF NOT EXISTS uq_m_scope_scope ON author.m_scope (scope) WHERE row_status <> 'DELETED'",
}
AUTHOR_PAIR_INDEXES = {
    "t_permission_scope": ["CREATE UNIQUE INDEX IF NOT EXISTS uq_t_permission_scope_permission_id_scope_id ON author.t_permission_scope (permission_id, scope_id) WHERE row_status <> 'DELETED'"],
    "t_role_permission": ["CREATE UNIQUE INDEX IF NOT EXISTS uq_t_role_permission_role_id_permission_id ON author.t_role_permission (role_id, permission_id) WHERE row_status <> 'DELETED'"],
    "t_role_permission_scope": ["CREATE UNIQUE INDEX IF NOT EXISTS uq_t_role_permission_scope_role_permission_scope ON author.t_role_permission_scope (role_permission_id, permission_scope_id) WHERE row_status <> 'DELETED'"],
    "t_user_role": ["CREATE UNIQUE INDEX IF NOT EXISTS uq_t_user_role_user_id_role_id ON author.t_user_role (user_id, role_id) WHERE row_status <> 'DELETED'"],
    "t_user_permission": ["CREATE UNIQUE INDEX IF NOT EXISTS uq_t_user_permission_user_id_permission_id ON author.t_user_permission (user_id, permission_id) WHERE permission_scope_id IS NULL AND row_status <> 'DELETED'",
                          "CREATE UNIQUE INDEX IF NOT EXISTS uq_t_user_permission_user_id_permission_scope ON author.t_user_permission (user_id, permission_id, permission_scope_id) WHERE permission_scope_id IS NOT NULL AND row_status <> 'DELETED'"],
}
AUTHOR_FKS = {  # table: [(column, target, action)]
    "t_permission_scope": [("permission_id", "author.m_permission", "RESTRICT"), ("scope_id", "author.m_scope", "RESTRICT")],
    "t_role_permission": [("role_id", "author.m_role", "RESTRICT"), ("permission_id", "author.m_permission", "RESTRICT")],
    "t_role_permission_scope": [("role_permission_id", "author.t_role_permission", "CASCADE"), ("permission_scope_id", "author.t_permission_scope", "RESTRICT")],
    "t_user_role": [("user_id", "authen.m_user", "CASCADE"), ("role_id", "author.m_role", "RESTRICT")],
    "t_user_permission": [("user_id", "authen.m_user", "CASCADE"), ("permission_id", "author.m_permission", "RESTRICT"), ("permission_scope_id", "author.t_permission_scope", "RESTRICT")],
}


def author_er_rows(table: str) -> list[str]:
    import xml.etree.ElementTree as ET

    root = ET.fromstring(read("e-commerce/db/er-diagram.drawio"))
    cells = list(root.iter("mxCell"))
    rows = []
    for cell in cells:
        if cell.get("value") == table:
            rows.extend(child.get("value") or "" for child in cells if child.get("parent") == cell.get("id"))
    return rows


def check_author_schema() -> int:
    """WP5a: partial unique names and pairs, role scope points at the permission scope, user permission scope, seed (migration, docs, README, ER, tests)."""
    errors = []
    sql = read("e-commerce/db/migrations/up/02-author.schema.up.sql")
    for table, index in AUTHOR_NAME_INDEXES.items():
        st = schema_statements(sql, "author", table)
        create = [s for s in st if s.startswith("CREATE TABLE")]
        if len(create) != 1 or "UNIQUE" in create[0]:
            errors.append(f"migration 02: {table} must be created without an inline UNIQUE")
        if index not in st:
            errors.append(f"migration 02: missing or different: {index[:90]}")
    for table, indexes in AUTHOR_PAIR_INDEXES.items():
        st = schema_statements(sql, "author", table)
        create = [s for s in st if s.startswith("CREATE TABLE")]
        if len(create) != 1 or "UNIQUE" in create[0]:
            errors.append(f"migration 02: {table} must be created without UNIQUE (...)")
        for index in indexes:
            if index not in st:
                errors.append(f"migration 02: missing or different: {index[:90]}")
        for column, target, action in AUTHOR_FKS.get(table, []):
            optional = "" if column != "permission_scope_id" or table != "t_user_permission" else ""
            fk = f"{column} UUID {'NOT NULL ' if not (table == 't_user_permission' and column == 'permission_scope_id') else ''}REFERENCES {target} (id) ON DELETE {action}"
            if not create or fk not in create[0]:
                errors.append(f"migration 02: {table} needs '{fk}'")
    docs = list(AUTHOR_NAME_INDEXES) + list(AUTHOR_PAIR_INDEXES)
    for table in docs:
        path = f"e-commerce/doc/schema/author/{table}.md"
        md = read(path)
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        st = schema_statements(sql, "author", table)
        if schema_statements(" ".join(SQL_BLOCK.findall(md)), "author", table) != st:
            errors.append(f"{path} SQL differs from the migration")
        if re.search(r"^\| UQ\s+\|", md, re.MULTILINE):
            errors.append(f"{path} still marks a column as UQ")
        constraint = md.split("## Constain")[1].split("\n---\n")[0]
        for index in [i for i in st if i.startswith("CREATE UNIQUE INDEX")]:
            name = re.search(r"INDEX IF NOT EXISTS (\S+) ON", index).group(1)
            if name not in constraint:
                errors.append(f"{path}: the constraint table must list {name}")
        for column, target, action in AUTHOR_FKS.get(table, []):
            if f"References {target}(id), ON DELETE {action}" not in constraint:
                errors.append(f"{path}: the constraint table must say ON DELETE {action} for {column}")
    if "[author.t_permission_scope.id](t_permission_scope.md)" not in read("e-commerce/doc/schema/author/t_role_permission_scope.md"):
        errors.append("t_role_permission_scope.md must reference author.t_permission_scope")
    if not re.search(r"\| permission_scope_id +\| UUID +\| +\| TRUE", read("e-commerce/doc/schema/author/t_user_permission.md")):
        errors.append("t_user_permission.md must list the nullable permission_scope_id")
    readme = read("e-commerce/doc/schema/README.md")
    if "| [t_user_permission](author/t_user_permission.md) | Transaction | 9 | 3 |" not in readme:
        errors.append("README: t_user_permission must have 9 columns and 3 foreign keys")
    if "[`db/seed/`](../../db/seed/author.seed.sql)" not in readme or "[`grant-platform-admin.sql`](../../db/seed/grant-platform-admin.sql)" not in readme:
        errors.append("README must record the db/seed folder and grant-platform-admin.sql")
    for table in ("m_role", "m_permission", "m_scope"):
        rows = author_er_rows(f"author.{table}")
        if len(rows) == 0 or any(r.startswith("UK") for r in rows):
            errors.append(f"ER diagram: author.{table} must be drawn without the UK marker")
    for table in AUTHOR_PAIR_INDEXES:
        if any(r.startswith("UNIQUE") for r in author_er_rows(f"author.{table}")):
            errors.append(f"ER diagram: author.{table} must not draw UNIQUE (...) (the unique rules are partial)")
    rows = author_er_rows("author.t_user_permission")
    if sum("permission_scope_id : uuid ?" in r for r in rows) < 2 or len(rows) < 8:
        errors.append("ER diagram: author.t_user_permission must draw permission_scope_id : uuid ?")
    for name in ("02-author.test.sql", "02-author-seed.test.sql"):
        if not (ROOT / "e-commerce/db/tests" / name).exists():
            errors.append(f"db/tests/{name} does not exist")
    seed = read("e-commerce/db/seed/author.seed.sql")
    for needle in ("'PLATFORM_ADMIN'", "('system', 'ALL', 'All'"):
        if needle not in seed:
            errors.append(f"seed missing: {needle}")
    for needle, times in (("ON CONFLICT (name)", 2), ("ON CONFLICT (scope)", 1), ("ON CONFLICT (permission_id, scope_id)", 1)):
        if seed.count(needle) != times:
            errors.append(f"seed: {needle!r} must appear {times} time(s), found {seed.count(needle)}")
    if re.search(r"INSERT\s+INTO\s+(authen\.|author\.t_(user|role)_)", seed):
        errors.append("the seed must not create a user or a grant")
    grant = read("e-commerce/db/seed/grant-platform-admin.sql")
    for needle in ("FOR UPDATE", "u.id = :'user_id'", "NOT EXISTS", "holder.row_status = 'ACTIVE'", "u.row_status = 'ACTIVE'", "DO UPDATE", "--single-transaction"):
        if needle not in grant:
            errors.append(f"grant-platform-admin.sql missing: {needle}")
    if errors:
        return fail("; ".join(errors))
    print("OK: author-schema")
    return 0


COMMANDS["author-schema"] = check_author_schema


def login_sequence_paths(wsd: str) -> tuple[list[list[str]], list[str]]:
    """Expand alternatives, prune explicit attempt guards and terminate break paths."""
    root: list = []
    current = root
    stack = []
    errors = []
    in_note = False
    for line in wsd.splitlines():
        text = line.strip()
        if in_note:
            if text == 'end note':
                in_note = False
            continue
        if text.startswith('note ') and ':' not in text:
            in_note = True
            continue
        if text.startswith('alt '):
            branch = [(text[4:], [])]
            current.append(branch)
            stack.append((current, branch))
            current = branch[-1][1]
        elif text.startswith('else'):
            if not stack:
                errors.append('else without alt')
                continue
            branch = stack[-1][1]
            branch.append((text[4:].strip(), []))
            current = branch[-1][1]
        elif text == 'end break':
            # A PlantUML break aborts the whole interaction, including common suffixes.
            current.append('@terminate-interaction')
        elif text in ('end', 'end alt'):
            if not stack:
                errors.append('end without alt')
                continue
            current, _ = stack.pop()
        elif re.match(r'(?:infra -> \w+: (?:QUERY|INSERT|UPDATE)|app -> (?:infra|api|app|domain):)', text):
            # Orchestration requests are distinct from the actual database operations.
            if text.startswith('app -> infra:') and not text.startswith(('app -> infra: BEGIN', 'app -> infra: COMMIT', 'app -> infra: ROLLBACK')):
                continue
            current.append(text)
    if stack or in_note:
        errors.append('unclosed alternative or note')

    def expand(nodes, prefix):
        traces = [prefix]
        for node in nodes:
            finished = [trace for trace in traces if '@terminate-interaction' in trace]
            traces = [trace for trace in traces if '@terminate-interaction' not in trace]
            if isinstance(node, str):
                traces = finished + [trace + [node] for trace in traces]
                continue
            next_traces = []
            for trace in traces:
                values = [re.search(r'result = (SUCCESS|FAILED|REFUSED)$', event).group(1)
                          for event in trace if re.search(r'result = (SUCCESS|FAILED|REFUSED)$', event)]
                result = values[-1] if values else None
                for guard, body in node:
                    if guard == 'result = SUCCESS' and result != 'SUCCESS':
                        continue
                    if guard == 'result = FAILED or REFUSED' and result not in ('FAILED', 'REFUSED'):
                        continue
                    next_traces.extend(expand(body, trace))
            traces = finished + next_traces
        return traces

    return [[event for event in trace if event != '@terminate-interaction'] for trace in expand(root, [])], errors


def check_login_flow() -> int:
    """Check login's security outcomes and query meaning, beyond SQL parity."""
    path = AUTHEN_SPECS['02']
    md = read(path)
    wsd = read(str(Path(path).with_name('sequence.wsd')))
    errors = []
    for needle in ('ambiguous',):
        if needle not in md:
            errors.append(f'login spec missing {needle!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for needle in ('**Only `FAILED` rows are counted.**', 'constant-time', 'permission-specific', 'PBKDF2-HMAC-SHA256 with 600,000 iterations',
            'No role, permission or scope definition creates a grant on its own.'):
        if needle not in seq:
            errors.append(f'login sequence note missing {needle!r}')
    if not md.startswith('---\n'):
        errors.append('login spec requires approval metadata')
    else:
        frontmatter = md.split('---', 2)[1]
        state = re.search(r'^status: (draft|in-review|approved)$', frontmatter, re.MULTILINE)
        if not state:
            errors.append('login spec has invalid approval state')
        for field in ('approved_by', 'approved_at'):
            value = re.search(rf'^{field}: (.+)$', frontmatter, re.MULTILINE)
            if not value or (state and ((state.group(1) == 'approved') == (value.group(1) == 'null'))):
                errors.append(f'login spec has inconsistent {field}')
    operations = spec_database_operations(md)
    sql = {heading: statement for _, heading, statement in operations}
    required = {
        'QUERY - Serialize identifier': ['pg_advisory_xact_lock', '<sequence.identifierLockKey>', '::BIGINT'],
        'QUERY - Count failed attempts': [ "la.result = 'FAILED'", 'la.identifier_hash', 'la.created_at >'],
        'QUERY - Lock the user': ['u.username', 'u.email_address', 'u.display_name', "u.row_status = 'ACTIVE'", 'ORDER BY u.id', 'FOR UPDATE'],
        'QUERY - Get current password': ['up.password AS password_hash', 'up.password_salt', "up.row_type = 'PASSWORD'", "up.row_status = 'ACTIVE'", "up.user_id = '<sequence.userId>'"],
        'QUERY - Get active role ids': ["ur.row_status = 'ACTIVE'", 'ur.user_id'],
        'QUERY - Get active roles': ["r.row_status = 'ACTIVE'", 'r.id', 'r.name'],
        'QUERY - Get active role permissions': ["rp.row_status = 'ACTIVE'", 'rp.role_id', '<sequence.activeRoleIds>', 'rp.permission_id', 'rp.id'],
        'QUERY - Get active role permission scopes': ['rps.role_permission_id', 'rps.permission_scope_id', "rps.row_status = 'ACTIVE'"],
        'QUERY - Get active direct permissions': ['up.permission_id', 'up.permission_scope_id', "up.row_status = 'ACTIVE'", 'up.user_id'],
        'QUERY - Get permission scope definitions': ['ps.id AS permission_scope_id', 'ps.permission_id', 'ps.scope_id', 'ps.row_status', "ps.row_status <> 'DELETED'"],
        'QUERY - Get active permissions': ['p.id', 'p.name', "p.row_status = 'ACTIVE'"],
        'QUERY - Get active scopes': ['s.id', 's.scope', '<sequence.assignedScopeIds>', "s.row_status = 'ACTIVE'"],
        'INSERT - Create access token': ['<sequence.sessionId>', '<sequence.accessTokenHash>', '<sequence.accessExpiredAt>'],
        'INSERT - Create refresh token': ['<sequence.sessionId>', '<sequence.refreshTokenHash>', '<sequence.refreshExpiredAt>'],
        'INSERT - Record attempt': ['created_at', '<sequence.now>', '<sequence.identifierHash>', '<sequence.userId>', '<sequence.result>'],
    }
    for heading, needles in required.items():
        statement = re.sub(r'--[^\n]*', '', sql.get(heading, ''))
        for needle in needles:
            if needle not in statement:
                errors.append(f'{heading}: missing {needle}')
    projections = {
        'QUERY - Get active role permission scopes': ['rps.role_permission_id', 'rps.permission_scope_id'],
        'QUERY - Get active direct permissions': ['up.permission_id', 'up.permission_scope_id'],
        'QUERY - Get permission scope definitions': ['ps.id AS permission_scope_id', 'ps.permission_id', 'ps.scope_id', 'ps.row_status'],
    }
    for heading, fields in projections.items():
        statement = re.sub(r'--[^\n]*', '', sql.get(heading, ''))
        projection = re.search(r'SELECT\s+(.*?)\s+FROM\s', statement, re.DOTALL)
        for field in fields:
            if not projection or field not in projection.group(1):
                errors.append(f'{heading}: must return {field}')
    if re.search(r'\bup\.password\s*=', '\n'.join(sql.values())):
        errors.append('password comparison must be constant-time in the application, not a SQL predicate')
    if 'rps.permission_scope_id AS scope_id' in md:
        errors.append('permission-scope ids are not scope ids')
    try:
        payload = json.loads(re.search(r'#### Example JWT Payload\n\n```JSON\n(.*?)```', md, re.DOTALL).group(1))
        if payload['exp'] - payload['iat'] != 900:
            errors.append('JWT example must have a 900-second lifetime')
        if set(payload) != {'iss', 'sub', 'aud', 'jti', 'iat', 'exp', 'user', 'roles', 'permissions', 'scopes'}:
            errors.append('JWT example must have exactly iss/sub/aud/jti/iat/exp/user/roles/permissions/scopes')
        if set(payload['user']) != {'id', 'username', 'displayName', 'email'} or payload['user']['id'] != payload['sub']:
            errors.append('JWT user must be exactly id/username/displayName/email with id equal to sub')
        for claim, shape in (('roles', r'^[A-Z][A-Z0-9_]*$'), ('permissions', r'^[a-z][a-z0-9_.]*:[a-z0-9_]+$'), ('scopes', r'^[a-z][a-z0-9_]*:\*$')):
            values = payload[claim]
            if values != sorted(set(values)) or any(not isinstance(v, str) or not re.match(shape, v) for v in values):
                errors.append(f'JWT {claim} must be sorted unique strings of the agreed shape')
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        errors.append(f'missing or malformed JWT example: {exc}')
    for guard in ('alt failed_attempts >= 5', 'else failed_attempts < 5', 'alt user_count != 1', 'else user_count = 1'):
        if not re.search(r'^\s*' + re.escape(guard) + r'\s*$', wsd, re.MULTILINE):
            errors.append(f'login sequence missing decision {guard}')
    if 'app -> domain: Verify password with PBKDF2 and constant-time comparison' not in wsd:
        errors.append('password verification must explicitly use PBKDF2 and constant-time comparison')
    for title, code in {'Success': 200, 'Fail - Bad Request': 400, 'Fail - Unauthorized': 401,
                        'Fail - Request Timeout': 408, 'Fail - Internal Server Error': 500}.items():
        try:
            status = authen_json(md, title)['status']
            if status['code'] != code or (code == 500 and 'bizCode' in status):
                errors.append(f'{title}: wrong HTTP status or unexpected internal-error bizCode')
        except (KeyError, TypeError, AttributeError, ValueError):
            errors.append(f'{title}: missing or invalid response example')
    for note in re.finditer(r'(?m)^([ \t]*)note right of \w+\n(.*?)^\1end note$', wsd, re.DOTALL):
        if any(line.lstrip().startswith("'") for line in note.group(2).splitlines()):
            errors.append('leading SQL apostrophe would disappear as a PlantUML comment; use &#39;')
    sequence_lines = wsd.splitlines()
    for index, line in enumerate(sequence_lines):
        exchange = re.match(r'^(\s*)infra -> (\w+): ((?:QUERY|INSERT|UPDATE)[^\n]*)$', line)
        if not exchange:
            continue
        pad, table, heading = exchange.groups()
        if index == 0 or sequence_lines[index - 1].strip() != 'app -> infra: ' + heading:
            errors.append(f'{heading}: Application must request the Infrastructure operation')
        end = next((i for i in range(index + 1, len(sequence_lines)) if sequence_lines[i] == pad + 'deactivate ' + table), None)
        if end is None or end + 1 >= len(sequence_lines) or not sequence_lines[end + 1].startswith(pad + 'infra -> app: Return '):
            errors.append(f'{heading}: Infrastructure must return its result to Application')
    for mapping in ('app -> app: user_count = length(matchedUsers)',
                    'app -> app: activeRoleIds = activeRoles.role_id',
                    'app -> app: rolePermissionIds = rolePermissions.role_permission_id',
                    'app -> app: permissionIds = union of role and direct permission ids',
                    'app -> app: Derive assignedScopeIds by exact assignment/definition and permission match',
                    'domain -> app: user, roles, permissions, scopes',
                    'permissions to names with the last dot as colon, scopes to lower-case code + :*'):
        if mapping not in wsd:
            errors.append(f'missing result-to-parameter mapping: {mapping}')
    if '--rendered-svg' in sys.argv:
        from collections import Counter
        import xml.etree.ElementTree as ET
        try:
            svg_path = Path(sys.argv[sys.argv.index('--rendered-svg') + 1])
            svg = ET.parse(svg_path).getroot()
            expected = Counter(' '.join(line.split()) for _, _, statement in operations
                               for line in statement.splitlines() if line.strip())
            visible = Counter(' '.join(''.join(element.itertext()).split()) for element in svg.iter()
                              if element.tag.endswith('}text'))
            missing = expected - visible
            if missing:
                errors.append(f'rendered SQL is missing {sum(missing.values())}/{sum(expected.values())} lines: {dict(missing)}')
            else:
                print(f'OK: rendered login SQL ({sum(expected.values())}/{sum(expected.values())} visible lines)')
        except (IndexError, OSError, ET.ParseError) as exc:
            errors.append(f'cannot verify rendered SVG: {exc}')
    traces, structure_errors = login_sequence_paths(wsd)
    errors.extend(structure_errors)
    outcomes = []
    for trace in traces:
        response = [event for event in trace if event.startswith('app -> api: HTTP ')]
        if len(response) != 1:
            errors.append('each login trace must have exactly one HTTP outcome')
            continue
        code = int(response[0].split('HTTP ')[1].split()[0])
        outcomes.append(code)
        joined = '\n'.join(trace)
        queries = [e for e in trace if e.startswith('infra -> ')]
        def ordered(*needles):
            positions = [next((i for i, e in enumerate(trace) if n in e), -1) for n in needles]
            return -1 not in positions and positions == sorted(set(positions))
        writes_tokens = any('INSERT - Create access token' in e or 'INSERT - Create refresh token' in e for e in trace)
        if any('QUERY - Get current password' in e for e in trace) and not ordered('QUERY - Serialize identifier', 'QUERY - Count failed attempts', 'QUERY - Lock the user', 'QUERY - Get current password', 'Verify password'):
            errors.append('every password read must follow the failure count and user lock, then verification')
        if code == 401 and 'result = FAILED' in joined and 'QUERY - Get current password' not in joined and 'Perform dummy password verification' not in joined:
            errors.append('unknown/ambiguous users require dummy password work before FAILED')
        if code == 400:
            if queries or any('BEGIN' in e for e in trace):
                errors.append('400 must not open a transaction or execute SQL')
        elif code in (408, 500):
            if not ordered('BEGIN', 'ROLLBACK', f'HTTP {code}') or any(e == 'app -> infra: COMMIT' for e in trace):
                errors.append('pre-commit failure must roll back and never commit')
        elif code in (200, 401):
            if not ordered('BEGIN', 'QUERY - Serialize identifier', 'QUERY - Count failed attempts', 'INSERT - Record attempt', 'app -> infra: COMMIT', f'HTTP {code}'):
                errors.append('normal outcomes must serialize/count, record the attempt, then commit before responding')
            if 'result = REFUSED' in joined and ('Get current password' in joined or 'QUERY - Lock the user' in joined or any(e.startswith('app -> domain:') for e in trace)):
                errors.append('REFUSED must not read users or passwords')
            if code == 401 and writes_tokens:
                errors.append('401 must never issue token rows')
            if code == 401 and 'result = FAILED' not in joined and 'result = REFUSED' not in joined:
                errors.append('401 must record FAILED or REFUSED')
            if code == 200:
                for field in ('tokenType', 'accessToken', 'refreshAccessToken', 'expiresIn'):
                    if not re.search(r'\b' + field + r'\b', response[0]):
                        errors.append(f'success sequence must name response field {field}')
                for heading in required:
                    if heading.startswith('QUERY - Get active') or heading == 'QUERY - Get permission scope definitions':
                        if not ordered(heading, 'Build verified authorization claims'):
                            errors.append('all assignment and master reads must precede claim construction')
                if 'result = SUCCESS' not in joined or not ordered('QUERY - Lock the user', 'QUERY - Get current password', 'Verify password', 'Build verified authorization claims', 'INSERT - Create access token', 'INSERT - Create refresh token', 'INSERT - Record attempt', 'app -> infra: COMMIT', 'HTTP 200'):
                    errors.append('200 must verify under the user lock, resolve claims and atomically commit both tokens and SUCCESS')
    if sorted(outcomes) != [200, 400, 401, 401, 401, 408, 500]:
        errors.append(f'expected success, input error, three authentication failures, timeout and internal failure; got {sorted(outcomes)}')
    if errors:
        return fail('; '.join(errors))
    print('OK: login-flow (7 outcome paths, claim mappings and transaction invariants)')
    return 0


COMMANDS['login-flow'] = check_login_flow


# ---------------------------------------------------------------- WP5c: delivered write APIs are for platform administrators only
ADMIN_WRITE_SPECS = {  # folder: (the thing it manages, batch)
    "shop/05-upsert-shop-type": ("shop types", False),
    "shop/06-upsert-shop-type-batch": ("shop types", True),
    "product/01-upsert-product": ("products", False),
    "product/03-upsert-product-batch": ("products", True),
    "product/04-upsert-product-category": ("product categories", False),
    "product/06-upsert-product-category-batch": ("product categories", True),
    "product/07-upsert-product-category-attribute": ("product category attributes", False),
    "product/09-upsert-product-category-attribute-batch": ("product category attributes", True),
}
ADMIN_WRITE_REFERENCE = "e-commerce/doc/api/shop/05-upsert-shop-type/spec.md"  # sales/05 now reads the administrator from the JWT claims
ADMIN_WRITE_APPROVED = "Approved by the product owner (answered through the lead SA, 2026-11-06)."
# Specs moved to the verified JWT roles claim (API review Q2, Q4, Q10, Q13): the two live role queries are gone, the caller lock and the
# current credential check take their place. Add a folder here in the pull request that migrates it.
ADMIN_WRITE_JWT_CLAIMS = {"product/01-upsert-product"}
# Specs that still use the live role queries but keep their rule and order text in the visible note of the diagram, not in the spec.
_IN_DIAGRAM_SINGLE = ("only a platform administrator (a user with an ACTIVE author.t_user_role row for the ACTIVE role PLATFORM_ADMIN)", "any other caller gets 403 (E10009)",
                      "Order of checks: validate the request (400) -> existence checks (404) -> permission (403, E10009) -> duplicate, in-use and other conflicts (409) -> write")
_IN_DIAGRAM_CAMPAIGN = ("A product category cannot be deleted while it is in a campaign that is not DELETED and has not ended (a live campaign.t_campaign_product row of a campaign "
                        "whose end_at is after now), 409 (E10006) with the campaign name in the message.")
_IN_DIAGRAM_BATCH = _IN_DIAGRAM_SINGLE + ("the same as the single upsert, only a platform administrator", "so the 403 message has no item position")
ADMIN_WRITE_RULE_IN_DIAGRAM = {  # folder: the phrases that the visible note of its diagram must say
    "product/03-upsert-product-batch": ("the same as the single upsert, only a platform administrator", "ACTIVE role PLATFORM_ADMIN", "any other caller gets 403 (E10009)",
                                        "so the 403 message has no item position", "permission check (403, E10009, once for the request) -> in-use check (409)"),
    "product/04-upsert-product-category": _IN_DIAGRAM_SINGLE + (_IN_DIAGRAM_CAMPAIGN,),
    "product/06-upsert-product-category-batch": _IN_DIAGRAM_BATCH + (_IN_DIAGRAM_CAMPAIGN,),
    "product/07-upsert-product-category-attribute": _IN_DIAGRAM_SINGLE,
    "product/09-upsert-product-category-attribute-batch": _IN_DIAGRAM_BATCH,
}
ADMIN_WRITE_CLAIMS_RULE = "the verified JWT `roles` claim (an array of role names, an empty array is valid) must contain the exact case-sensitive role `PLATFORM_ADMIN`"
ADMIN_WRITE_RULE_BATCH = ("Permission: the same as the single upsert, only a platform administrator (a user with an ACTIVE `author.t_user_role` row for the ACTIVE role `PLATFORM_ADMIN`) "
                          "can call this API, any other caller gets 403 (E10009)")
ADMIN_WRITE_RULE = ("Permission: only a platform administrator (a user with an ACTIVE `author.t_user_role` row for the ACTIVE role `PLATFORM_ADMIN`) "
                    "can call this API, any other caller gets 403 (E10009)")


def admin_write_reference_queries() -> list[str]:
    """The two named queries of the reference spec (the text every spec must copy)."""
    md = read(ADMIN_WRITE_REFERENCE)
    found = []
    for title in ("QUERY - Get the platform administrator role", "QUERY - Check platform administrator"):
        match = re.search(rf"#### {re.escape(title)}\n\n```SQL\n(.*?)```", md, re.DOTALL)
        found.append(match.group(1) if match else "")
    return found


def admin_write_claims_flow_errors(wsd: str) -> list[str]:
    """Order of a diagram that authorizes from the verified roles claim: lock, current credential, existence, claims permission, conflicts, writes."""
    errors = []
    marks = [
        ("BEGIN", r"^\s*app -> infra: BEGIN READ COMMITTED"),
        ("caller lock", r"^\s*app -> infra: QUERY - Lock the caller user"),
        ("current credential check", r"^\s*app -> infra: QUERY - Check current credential and user"),
        ("first existence check", r"^\s*app -> infra: QUERY - Check product type\b"),
        ("claims permission", r"^\s*alt The verified roles claim has no PLATFORM_ADMIN"),
        ("first conflict check", r"^\s*app -> infra: QUERY - Check product SKUs in use"),
        ("first write", r"^\s*app -> infra: (?:INSERT|UPDATE) - "),
    ]
    found = []
    for name, pattern in marks:
        match = re.search(pattern, wsd, re.MULTILINE)
        if not match:
            errors.append(f"the diagram has no {name}")
        else:
            found.append((match.start(), name))
    if not errors and [name for _, name in sorted(found)] != [name for name, _ in marks]:
        errors.append("the diagram must run: " + " -> ".join(name for name, _ in marks))
    if not re.search(r"^\s*app -> app: Verify JWT\b.*roles claim", wsd, re.MULTILINE):
        errors.append("the JWT step must verify the roles claim")
    for phrase in ("verify the JWT and its roles claim (401)", "lock the caller user (FOR UPDATE)", "permission from the roles claim (403, E10009)", "the author tables are never queried"):
        if phrase not in wsd:
            errors.append(f"the visible order note of the diagram must say {phrase!r}")
    if re.search(r"infra -> (?:m_role|t_user_role):", wsd):
        errors.append("the diagram must not read author.m_role or author.t_user_role")
    return errors


def check_admin_write_spec() -> int:
    errors = []
    queries = admin_write_reference_queries()
    if not all(queries):
        errors.append(f"{ADMIN_WRITE_REFERENCE} has no platform administrator queries to copy")
    for folder, (thing, batch) in ADMIN_WRITE_SPECS.items():
        path = f"e-commerce/doc/api/{folder}/spec.md"
        try:
            # rules that moved into a note of the sequence diagram are searched there, one line per wrapped note
            md = read(path) + "\n" + re.sub(r"\n\s+", " ", read(path.replace("spec.md", "sequence.wsd")))
        except FileNotFoundError:
            errors.append(f"{path} does not exist")
            continue
        for bad in table_lines_aligned(md):
            errors.append(f"{path} misaligned table: {bad[:40]}")
        for bad in json_blocks_parse(md):
            errors.append(f"{path} invalid JSON block: {bad[:40]}")
        for link in relative_links_exist(path, md):
            errors.append(f"{path} broken link {link}")
        if "ALTER TABLE" in md:
            errors.append(f"{path} contains ALTER TABLE")
        description = next((line for line in md.split("\n") if line.startswith("| Description |")), "")
        if "only a platform administrator can call it" not in description:
            errors.append(f"{path}: the Description row must say that only a platform administrator can call it")
        claims = folder in ADMIN_WRITE_JWT_CLAIMS
        need = [ADMIN_WRITE_RULE_BATCH if batch else ADMIN_WRITE_RULE, ADMIN_WRITE_APPROVED, "permission (403, E10009)", "#### QUERY - Get the platform administrator role", "#### QUERY - Check platform administrator",
                "(../../../schema/author/m_role.md)", "(../../../schema/author/t_user_role.md)", f"You do not have permission to manage {thing}."]
        if claims:
            need = [ADMIN_WRITE_CLAIMS_RULE, "Q2, Q4, Q10 and Q13", "Never query `author.m_role` or `author.t_user_role`", "The order of the checks and the locks is in the sequence diagram",
                    "#### QUERY - Lock the caller user", "WHERE u.id = '<sequence.callerUserId>'\nFOR UPDATE",
                    "#### QUERY - Check current credential and user", "AND at.expired_at > '<sequence.now>'", "(../../../schema/authen/m_user.md)",
                    "(../../../schema/authen/t_user_access_token.md)", f"You do not have permission to manage {thing}."]
            for gone in ("#### QUERY - Get the platform administrator role", "#### QUERY - Check platform administrator", "(../../../schema/author/m_role.md)", "(../../../schema/author/t_user_role.md)"):
                if gone in md:
                    errors.append(f"{path}: the live platform administrator query must be gone, found {gone!r}")
        in_diagram = folder in ADMIN_WRITE_RULE_IN_DIAGRAM
        if in_diagram:
            need = [ADMIN_WRITE_APPROVED, "Only a platform administrator can call this API", "The order of the checks is in the sequence diagram",
                    "#### QUERY - Get the platform administrator role", "#### QUERY - Check platform administrator", "(../../../schema/author/m_role.md)",
                    "(../../../schema/author/t_user_role.md)", f"You do not have permission to manage {thing}."]
            note = read(str(Path(path).with_name("sequence.wsd")))
            if batch:
                need += ["so the 403 message has no item position"]
            if _IN_DIAGRAM_CAMPAIGN in ADMIN_WRITE_RULE_IN_DIAGRAM[folder]:
                need += ["A product category cannot be deleted while it is in a campaign that is not DELETED and has not ended (409, E10006, with the campaign name in the message)"]
            for phrase in ADMIN_WRITE_RULE_IN_DIAGRAM[folder]:
                if phrase not in note:
                    errors.append(f"{path}: the visible note of the diagram must say {phrase!r}")
        if batch and not in_diagram:
            need += ["so the 403 message has no item position", "the same as the single upsert, only a platform administrator"]
        if folder.startswith("product/0") and folder.split("/")[1].startswith(("01", "03")):
            need += []
        elif folder != "shop/05-upsert-shop-type" and not claims and not in_diagram:
            need += ["- Order of checks: validate the request (400) -> existence checks (404) -> permission (403, E10009) -> duplicate, in-use and other conflicts (409) -> write."]
        if folder == "shop/05-upsert-shop-type":
            need += ["existence check (404) -> permission (403, E10009) -> duplicate name check"]
        for missing in missing_needles(md, need):
            errors.append(f"{path} missing: {missing!r}")
        for stale in ("Any caller with a valid access token can call this API", "A role check (for example platform administrators only) is not defined yet"):
            if stale in md:
                errors.append(f"{path} still says {stale!r}")
        for query in ([] if claims else queries):
            if query and md.count(query) != 1:
                errors.append(f"{path}: the platform administrator query must be copied exactly from the reference spec, found {md.count(query)} copies")
        queries_once = ("#### QUERY - Lock the caller user", "#### QUERY - Check current credential and user") if claims else ("#### QUERY - Get the platform administrator role", "#### QUERY - Check platform administrator")
        if md.count("#### Fail - Forbidden") != 1 or any(md.count(q) != 1 for q in queries_once):
            errors.append(f"{path}: Fail - Forbidden and each {'caller lock and credential' if claims else 'platform administrator'} query must appear exactly once")
        match = re.search(r"#### Fail - Forbidden\n\n```JSON\n(.*?)```", md, re.DOTALL)
        if not match:
            errors.append(f"{path}: no JSON in 'Fail - Forbidden'")
        else:
            status = json.loads(match.group(1))["status"]
            if status["code"] != 403 or status["bizCode"] != "E10009" or status["bizMessage"] != f"You do not have permission to manage {thing}.":
                errors.append(f"{path}: the Forbidden example must be 403 E10009 with the message 'You do not have permission to manage {thing}.'")
            if "[" in status["bizMessage"]:
                errors.append(f"{path}: the 403 message must have no item position")
            if md.index("#### Fail - Forbidden") > md.index("#### Fail - Conflict"):
                errors.append(f"{path}: Fail - Forbidden must come before the Conflict examples (after Not Found)")
        if md.index(queries_once[0]) < md.index("## Database Relations"):
            errors.append(f"{path}: the {'caller lock and credential' if claims else 'platform administrator'} queries belong to Database Relations")
        if md.count("E10009") < (2 if claims or in_diagram else 3):
            errors.append(f"{path}: E10009 must appear in the rule, {'' if claims or in_diagram else 'the order of checks, '}and the example")
        if claims:
            errors.extend(f"{path}: {error}" for error in admin_write_claims_flow_errors(read(str(Path(path).with_name("sequence.wsd")))))
    if errors:
        return fail("; ".join(errors))
    print("OK: admin-write-spec (9 specs)")
    return 0


COMMANDS["admin-write-spec"] = check_admin_write_spec


def check_refresh_flow() -> int:
    """Check refresh rotation and replay as distinct committed/rolled-back paths."""
    path = AUTHEN_SPECS['05']
    md = read(path)
    wsd = read(str(Path(path).with_name('sequence.wsd')))
    errors = []
    operations = spec_database_operations(md)
    sql = {heading: statement for _, heading, statement in operations}
    required = {
        'QUERY - Find the refresh token': ['rt.id', 'rt.user_id', '<sequence.presentedRefreshTokenHash>', '<sequence.lookupNow>'],
        'QUERY - Lock the user': ["u.row_status = 'ACTIVE'", 'FOR UPDATE', '<sequence.userId>'],
        'QUERY - Reread the refresh token after user lock': ['rt.row_status', 'rt.updated_at', 'rt.expired_at', 'rt.session_id', '<sequence.refreshTokenId>', '<sequence.userId>', '<sequence.presentedRefreshTokenHash>'],
        'UPDATE - Use the refresh token once': ["row_status = 'INACTIVE'", "updated_at = '<sequence.now>'", "AND row_status = 'ACTIVE'", "AND expired_at > '<sequence.now>'", "AND user_id = '<sequence.userId>'", "AND session_id = '<sequence.sessionId>'", "AND token = '<sequence.presentedRefreshTokenHash>'", 'RETURNING session_id'],
        'INSERT - Create access token': ['<sequence.accessTokenHash>', '<sequence.sessionId>', '<sequence.accessExpiredAt>'],
        'INSERT - Create refresh token': ['<sequence.newRefreshTokenHash>', '<sequence.sessionId>', '<sequence.refreshExpiredAt>'],
        'UPDATE - Close the refresh tokens of the session (reuse)': ["WHERE session_id = '<sequence.sessionId>'", "AND user_id = '<sequence.userId>'", "AND row_status = 'ACTIVE'", "updated_at = '<sequence.now>'"],
        'UPDATE - Close the access tokens of the session (reuse)': ["WHERE session_id = '<sequence.sessionId>'", "AND user_id = '<sequence.userId>'", "AND row_status = 'ACTIVE'", "updated_at = '<sequence.now>'"],
    }
    for heading, needles in required.items():
        statement = re.sub(r'--[^\n]*', '', sql.get(heading, ''))
        for needle in needles:
            if needle not in statement:
                errors.append(f'{heading}: missing {needle}')
    if '<sequence.presentedRefreshTokenHash>' in sql.get('INSERT - Create refresh token', ''):
        errors.append('replacement refresh must not reuse the presented credential hash')
    if 'NOW()' in sql.get('UPDATE - Use the refresh token once', ''):
        errors.append('consume must use post-lock now, not transaction-start NOW()')
    login_claims = [o for o in spec_database_operations(read(AUTHEN_SPECS['02'])) if o[0].startswith('author.')]
    refresh_claims = [o for o in operations if o[0].startswith('author.')]
    if [(t,h,normalize(s)) for t,h,s in login_claims] != [(t,h,normalize(s)) for t,h,s in refresh_claims]:
        errors.append('refresh must resolve current claims using all eight canonical login queries')
    for needle in ('permission-specific', 'updated_at', 'issuedAt'):
        if needle.lower() not in md.lower():
            errors.append(f'refresh spec missing {needle}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for needle in ('at exactly 10 seconds', 'a fresh `user` snapshot', 'the last `.` as `:`'):
        if needle.lower() not in seq.lower():
            errors.append(f'refresh sequence note missing {needle!r}')
    front = re.match(r'---\n(.*?)\n---\n', md, re.DOTALL)
    if not front:
        errors.append('refresh spec needs approval metadata')
    else:
        state = re.search(r'^status: (draft|in-review|approved)$', front.group(1), re.MULTILINE)
        if not state:
            errors.append('refresh spec has invalid status')
        for field in ('approved_by', 'approved_at'):
            value = re.search(rf'^{field}: (.+)$', front.group(1), re.MULTILINE)
            if not value or (state and ((state.group(1) == 'approved') == (value.group(1) == 'null'))):
                errors.append(f'refresh spec has inconsistent {field}')
    guards = ('alt Owner lookup returned no row', 'alt ACTIVE user row returned',
              'alt Fresh row is ACTIVE and expired_at > now',
              'alt Conditional consume returned session_id',
              'else Conditional consume returned no row',
              'else Fresh row is INACTIVE, unexpired, updated_at known and now < updated_at + 10 seconds',
              'else Fresh row is INACTIVE, unexpired and outside grace (or updated_at is NULL)',
              'else Fresh row missing, expired or another status')
    for guard in guards:
        if not re.search(r'^\s*' + re.escape(guard) + r'\s*$', wsd, re.MULTILINE):
            errors.append(f'refresh sequence missing branch {guard}')
    for note in re.finditer(r'(?m)^([ \t]*)note right of \w+\n(.*?)^\1end note$', wsd, re.DOTALL):
        if any(line.lstrip().startswith("'") for line in note.group(2).splitlines()):
            errors.append('leading SQL literal would be hidden by PlantUML')
    lines = wsd.splitlines()
    for i,line in enumerate(lines):
        request = re.match(r'^(\s*)infra -> (\w+): ((?:QUERY|INSERT|UPDATE)[^\n]*)$', line)
        if not request: continue
        pad, table, heading = request.groups()
        if i == 0 or lines[i-1].strip() != 'app -> infra: ' + heading:
            errors.append(f'{heading}: missing Application request')
        end = next((j for j in range(i+1,len(lines)) if lines[j] == pad+'deactivate '+table), None)
        if end is None or end+1 >= len(lines) or not lines[end+1].startswith(pad+'infra -> app: Return '):
            errors.append(f'{heading}: missing result returned to Application')
    if '--rendered-svg' in sys.argv:
        from collections import Counter
        import xml.etree.ElementTree as ET
        try:
            root = ET.parse(sys.argv[sys.argv.index('--rendered-svg')+1]).getroot()
            expected = Counter(' '.join(line.split()) for _,_,statement in operations for line in statement.splitlines() if line.strip())
            visible = Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'))
            missing = expected-visible
            if missing: errors.append(f'rendered refresh SQL missing {sum(missing.values())}/{sum(expected.values())} lines')
            else: print(f'OK: rendered refresh SQL ({sum(expected.values())}/{sum(expected.values())} visible lines)')
        except (IndexError, OSError, ET.ParseError) as exc:
            errors.append(f'cannot verify rendered refresh SVG: {exc}')
    for title,code in {'Success':200,'Fail - Bad Request':400,'Fail - Unauthorized':401,'Fail - Request Timeout':408,'Fail - Internal Server Error':500}.items():
        try:
            status=authen_json(md,title)['status']
            if status['code'] != code or (code==500 and 'bizCode' in status):
                errors.append(f'{title}: incorrect HTTP example or invented internal bizCode')
        except (KeyError,TypeError,AttributeError,ValueError):
            errors.append(f'{title}: missing response example')
    traces, structure = login_sequence_paths(wsd)
    errors.extend(structure)
    outcomes=[]
    for trace in traces:
        response=[e for e in trace if e.startswith('app -> api: HTTP ')]
        if len(response)!=1:
            errors.append('each refresh trace needs exactly one HTTP outcome');continue
        code=int(response[0].split('HTTP ')[1].split()[0]);outcomes.append(code)
        joined='\n'.join(trace)
        def ordered(*needles):
            pos=[next((i for i,e in enumerate(trace) if n in e),-1) for n in needles]
            return -1 not in pos and pos==sorted(set(pos))
        begins=any(e.startswith('app -> infra: BEGIN') for e in trace)
        commits=any(e=='app -> infra: COMMIT' for e in trace)
        rolls_back=any(e=='app -> infra: ROLLBACK' for e in trace)
        inserts=[e for e in trace if e.startswith('infra -> ') and ': INSERT' in e]
        closes=['UPDATE - Close the refresh tokens of the session (reuse)' in joined,
                'UPDATE - Close the access tokens of the session (reuse)' in joined]
        if code==400:
            if begins or any(e.startswith('infra -> ') for e in trace): errors.append('400 must have no SQL or transaction')
        elif code in (408,500):
            if commits or not ordered('BEGIN','ROLLBACK',f'HTTP {code}'): errors.append('pre-commit failure must roll back')
        elif code==200:
            if closes!=[False,False] or rolls_back or not ordered('QUERY - Find the refresh token','BEGIN','QUERY - Lock the user','Capture UTC now','QUERY - Reread the refresh token after user lock','UPDATE - Use the refresh token once','Build verified authorization claims','INSERT - Create access token','INSERT - Create refresh token','app -> infra: COMMIT','HTTP 200'):
                errors.append('rotation must reread/consume under lock, reload claims, issue both tokens and commit without replay revocation')
            for _,heading,_ in login_claims:
                if not ordered('UPDATE - Use the refresh token once',heading,'Build verified authorization claims'):
                    errors.append('current claim queries must follow the successful consume and precede claim construction')
            for field in ('tokenType','accessToken','refreshAccessToken','expiresIn'):
                if not re.search(r'\b'+field+r'\b',response[0]): errors.append(f'success omits {field}')
        elif code==401:
            if inserts: errors.append('401 must not create replacement token rows')
            if any(closes):
                if closes!=[True,True] or rolls_back or not ordered('QUERY - Lock the user','QUERY - Reread the refresh token after user lock','UPDATE - Close the refresh tokens of the session (reuse)','UPDATE - Close the access tokens of the session (reuse)','app -> infra: COMMIT','HTTP 401'):
                    errors.append('older replay must durably close both token tables before 401')
                if 'UPDATE - Use the refresh token once' in joined: errors.append('replay must not execute normal rotation')
            elif begins:
                if commits or not ordered('BEGIN','ROLLBACK','HTTP 401'): errors.append('invalid/recent-duplicate paths must roll back without committing')
            elif not ordered('QUERY - Find the refresh token','HTTP 401'):
                errors.append('missing owner must fail after lookup without a transaction')
        if 'QUERY - Reread the refresh token after user lock' in joined and not ordered('QUERY - Lock the user','Capture UTC now','QUERY - Reread the refresh token after user lock'):
            errors.append('replay classification requires the post-lock reread and timestamp')
    if sorted(outcomes)!=[200,400,401,401,401,401,401,401,408,500]:
        errors.append(f'expected ten refresh paths, got {sorted(outcomes)}')
    if errors: return fail('; '.join(errors))
    print('OK: refresh-flow (10 outcome paths, fresh claims, post-lock reread and replay commit)')
    return 0


COMMANDS['refresh-flow'] = check_refresh_flow


def check_register_flow() -> int:
    """Guard the owner-approved registration policy and atomic execution paths."""
    path = AUTHEN_SPECS['01']
    md = read(path)
    wsd = read(str(Path(path).with_name('sequence.wsd')))
    errors = []
    for needle in ('REPEATABLE READ', 'one optional object, never an array', 'consentVersion'):
        # The prior read timestamp belongs to authenticated submit, but must be explained here too.
        if needle == 'keeps its original read':
            needle = 'repeated reads preserve the first read_at'
        if needle not in md:
            errors.append(f'register rules missing {needle!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for needle in ('first read establishes the transaction snapshot', 'Required means `t_consent.is_required`', 'Reject duplicate consentIds before SQL', 'result=true',
            'every supplied valid consent object represents the displayed version', 'Omitted optional consent creates no row', 'SQLSTATE 23505',
            'rolls back the whole transaction', 'Serialization', '600,000 iterations', 'random 16 byte salt', 'not request input', 'never the string',
            'repeated reads preserve the first read_at'):
        if needle not in seq:
            errors.append(f'register sequence note missing {needle!r}')
    fm = md.split('---', 2)[1] if md.startswith('---\n') else ''
    state = re.search(r'^status: (draft|in-review|approved)$', fm, re.M)
    if not state:
        errors.append('register requires valid approval metadata')
    for field in ('approved_by', 'approved_at'):
        value = re.search(rf'^{field}: (.+)$', fm, re.M)
        if not value or (state and ((state[1] == 'approved') == (value[1] == 'null'))):
            errors.append(f'inconsistent register {field}')
    version_row = re.search(r'^\|[^\n]*\| consentVersion\s*\|[^\n]+$', md, re.M)
    if not version_row or 'MANDATORY' not in version_row[0] or 'never defaulted' not in version_row[0]:
        errors.append('displayed consentVersion must be mandatory, not silently defaulted')
    operations = spec_database_operations(md)
    expected = ('QUERY - Check existing user', 'QUERY - Get effective consents', 'QUERY - Get active consent types',
                'QUERY - Check referrer', 'INSERT - Create user', 'INSERT - Create password',
                'INSERT - Create user information', 'INSERT - Create user address',
                'INSERT - Create user consent', 'INSERT - Create user referral')
    if tuple(h for _, h, _ in operations) != expected:
        errors.append('registration must declare all ten validation/write operations in execution order')
    sql = {h: re.sub(r'--[^\n]*', '', s) for _, h, s in operations}
    required = {
        expected[0]: ["u.username = '<sequence.usernameBytes>' OR u.email_address = '<sequence.emailAddressBytes>'"],
        expected[1]: ['c.id as consent_id', 'c.consent_type_id', 'c.consent_version', 'c.is_required',
                      "c.row_status = 'ACTIVE'", "c.effective_at <= '<sequence.now>'",
                      "c.expired_at IS NULL OR c.expired_at > '<sequence.now>'", 'ORDER BY c.id'],
        expected[2]: ['ct.id as consent_type_id', "ct.id = ANY ('<sequence.consentTypeIds>'::UUID[])", "ct.row_status = 'ACTIVE'"],
        expected[3]: ["u.id = '<sequence.referrerId>'"],
        expected[4]: ['username,', 'email_address,', '<sequence.createdBy>', '<sequence.usernameBytes>', '<sequence.emailAddressBytes>', 'RETURNING id as user_id'],
        expected[5]: ['user_id,', 'password,', 'password_salt', "'PASSWORD'", '<sequence.userId>', '<sequence.passwordBytes>', '<sequence.passwordSaltBytes>'],
        expected[6]: ['user_id,', '<sequence.userId>', '<sequence.phoneNumberBytes>', '<sequence.addressBytes>', '<sequence.dateOfBirth>', '<sequence.gender>'],
        expected[7]: ['is_default,', 'TRUE,', '<sequence.userId>', '<sequence.addresses.title>', '<sequence.addresses.addressBytes>', '<sequence.addresses.cityBytes>', '<sequence.addresses.stateBytes>', '<sequence.addresses.postalCodeBytes>', '<sequence.addresses.countryBytes>'],
        expected[8]: ['consent_id,', 'consent_version,', 'result,', 'is_read,', 'read_at', '<sequence.userId>', '<sequence.consents.consentId>', '<sequence.consents.consentVersion>', '<sequence.consents.result>', 'TRUE,', '<sequence.now>'],
        expected[9]: ['user_id,', 'referrer_id', '<sequence.userId>', '<sequence.referrerId>'],
    }
    for heading, needles in required.items():
        for needle in needles:
            if needle not in sql.get(heading, ''):
                errors.append(f'{heading} missing {needle}')
    if 'row_status' in sql.get(expected[0], ''):
        errors.append('duplicate check must include identifiers in all lifecycle states')
    if any(t.startswith('author.') or '_token' in t for t, _, _ in operations):
        errors.append('registration must not grant privileges or issue tokens')
    actual, lifecycle = sequence_database_operations(wsd)
    errors += lifecycle
    if [(t.split('.')[-1],h,normalize(s)) for t,h,s in operations] != [(t,h,normalize(s)) for t,h,s in actual]:
        errors.append('register spec/sequence SQL and execution order differ')
    for _, heading, _ in operations:
        if f'app -> infra: {heading}' not in wsd:
            errors.append(f'{heading} requires Application request')
        match = re.search(rf'infra -> (\w+): {re.escape(heading)}\n.*?deactivate \1\n([^\n]+)', wsd, re.S)
        if not match or not match[2].strip().startswith('infra -> app: Return '):
            errors.append(f'{heading} requires Infrastructure result to Application')
    for needle in ('consentTypeIds = distinct effectiveConsents.consent_type_id',
                   'applicableConsents = effectiveConsents with typeId in activeTypeIds',
                   'userId = returned user_id', 'result = explicit result or false; isRead = true; readAt = now',
                   'alt addresses object supplied', 'alt Validated consents list is non-empty',
                   'loop Each supplied consent ordered by consentId', 'alt Validated referrerId supplied',
                   'Displayed consentVersion differs from current version',
                   'Required consent missing or result is not explicit true',
                   'Retry whole transaction with new snapshot/now within request timeout'):
        if needle not in wsd:
            errors.append(f'sequence missing mapping/guard {needle!r}')
    traces, structure = login_sequence_paths(wsd)
    errors += structure
    outcomes = []
    retries = 0
    for trace in traces:
        responses = [e for e in trace if e.startswith('app -> api: HTTP ')]
        def ordered(*parts):
            positions = [next((i for i,e in enumerate(trace) if n in e), -1) for n in parts]
            return -1 not in positions and positions == sorted(set(positions))
        writes = [e for e in trace if e.startswith('infra -> ') and ': INSERT' in e]
        if not responses and any('Retry whole transaction' in e for e in trace):
            retries += 1
            if writes or not ordered('BEGIN REPEATABLE READ', 'ROLLBACK', 'Retry whole transaction'):
                errors.append('serialization retry must abandon the whole failed transaction')
            continue
        if len(responses) != 1:
            errors.append('each terminal register trace needs exactly one HTTP outcome')
            continue
        code = int(responses[0].split('HTTP ')[1].split()[0]);outcomes.append(code)
        begun = any('BEGIN' in e for e in trace)
        if code == 201:
            if not ordered('BEGIN REPEATABLE READ', 'Capture UTC now', expected[0], expected[1], expected[2],
                           'applicableConsents =', 'Validate submitted ids/versions', expected[4],
                           'userId = returned user_id', expected[5], expected[6], 'COMMIT', 'HTTP 201'):
                errors.append('success must validate one snapshot, map new user id and atomically commit required children')
            if 'data.userId = userId' not in responses[0]:
                errors.append('success returns the newly created userId')
            if any('ROLLBACK' in e for e in trace):
                errors.append('success cannot roll back')
        elif begun:
            if not ordered('BEGIN REPEATABLE READ', 'ROLLBACK', f'HTTP {code}') or any('COMMIT' in e for e in trace):
                errors.append('transaction failure must rollback before responding, with no commit')
            if writes:
                errors.append('normal validation failure must precede every write')
        elif code != 400 or any(e.startswith('infra -> ') for e in trace):
            errors.append('only malformed input may respond without a transaction; it must execute no SQL')
    from collections import Counter
    if Counter(outcomes) != Counter({201:16,400:5,404:3,409:2,408:1,500:1}) or retries != 1:
        errors.append(f'expected complete terminal/optional paths and one retry; got {dict(Counter(outcomes))}, retry={retries}')
    if '--rendered-svg' in sys.argv:
        import xml.etree.ElementTree as ET
        try:
            root = ET.parse(Path(sys.argv[sys.argv.index('--rendered-svg')+1])).getroot()
            expected_lines = Counter(' '.join(l.split()) for _,_,s in operations for l in s.splitlines() if l.strip())
            visible = Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'))
            missing = expected_lines-visible
            if missing:
                errors.append(f'rendered register SQL missing {sum(missing.values())} lines: {dict(missing)}')
            else:
                print(f'OK: rendered register SQL ({sum(expected_lines.values())}/{sum(expected_lines.values())} visible lines)')
        except (IndexError,OSError,ET.ParseError) as exc:
            errors.append(f'cannot verify rendered register SVG: {exc}')
    if errors:
        return fail('; '.join(errors))
    print(f'OK: register-flow ({len(outcomes)} terminal traces, whole-transaction retry, current consent coverage and atomic writes)')
    return 0


COMMANDS['register-flow'] = check_register_flow


def check_consent_submit_flow() -> int:
    """Check read/answer/no-op transitions, revocation serialization and atomic batch outcomes."""
    path = 'e-commerce/doc/api/consent/04-submit-consent/spec.md'
    md = read(path);wsd = read(str(Path(path).with_name('sequence.wsd')))
    errors = []
    for needle in ('Q16/Q17', 'READ COMMITTED', 'current version', 'mandatory boolean isRead=true'):
        if needle not in md:errors.append(f'submit rule missing {needle!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for needle in ('Duplicate consentIds return 400', 'resultSpecified records presence', 'An existing answer survives a read-only request',
            'performs no UPDATE at all', 'preserve read_at even when NULL', 'newest created_at, then greatest id', 'validate the complete current consent set',
            'including all-no-op batches', 'Return data.consents in original request order', 'A later item/DB failure rolls back earlier item changes'):
        if needle not in seq:
            errors.append(f'submit sequence note missing {needle!r}')
    front = re.match(r'---\n(.*?)\n---\n', md, re.S)
    fm = front[1] if front else ''
    state = re.search(r'^status: (draft|in-review|approved)$', fm, re.M)
    if not state:errors.append('submit needs valid approval metadata')
    for field in ('approved_by','approved_at'):
        value = re.search(rf'^{field}: (.+)$', fm, re.M)
        if not value or (state and ((state[1]=='approved')==(value[1]=='null'))):errors.append(f'inconsistent submit {field}')
    operations = spec_database_operations(md)
    expected = ('QUERY - Lock the user', 'QUERY - Check the active access token', 'QUERY - Get active consents',
                'QUERY - Get existing user consent', 'INSERT - Create user consent', 'UPDATE - Update user consent')
    if tuple(h for _,h,_ in operations)!=expected:errors.append('submit requires all six canonical SQL operations')
    sql={h:re.sub(r'--[^\n]*','',s) for _,h,s in operations}
    required={
        expected[0]: ["u.id = '<sequence.userId>'", "u.row_status = 'ACTIVE'", 'FOR UPDATE'],
        expected[1]: ["at.token = '<sequence.accessTokenHash>'", "at.user_id = '<sequence.userId>'", "at.row_status = 'ACTIVE'", "at.expired_at > '<sequence.now>'"],
        expected[2]: ["c.id = ANY ('<sequence.consentIds>'::UUID[])", "c.row_status = 'ACTIVE'", "c.effective_at <= '<sequence.now>'", "c.expired_at IS NULL OR c.expired_at > '<sequence.now>'", 'AND EXISTS (', 'FROM consent.m_consent_type ct', 'ct.id = c.consent_type_id', "ct.row_status = 'ACTIVE'", 'ORDER BY c.id'],
        expected[3]: ['uc.result,', 'uc.is_read,', 'uc.read_at', "uc.user_id = '<sequence.userId>'", "uc.consent_id = '<sequence.consents.consentId>'", "uc.consent_version = '<sequence.consents.consentVersion>'", "uc.row_status = 'ACTIVE'", 'ORDER BY uc.created_at DESC, uc.id DESC', 'LIMIT 1'],
        expected[4]: ['created_by,', 'user_id,', 'consent_id,', 'consent_version,', 'result,', 'is_read,', 'read_at', '<sequence.userId>', '<sequence.consents.consentId>', '<sequence.consents.consentVersion>', '<sequence.consents.result>', 'TRUE,', '<sequence.now>'],
        expected[5]: ["updated_by = '<sequence.userId>'", "updated_at = '<sequence.now>'", "result = CASE WHEN '<sequence.consents.resultSpecified>'::BOOLEAN THEN '<sequence.consents.result>'::BOOLEAN ELSE result END", "read_at = CASE WHEN is_read THEN read_at ELSE '<sequence.now>'::TIMESTAMP END", 'is_read = TRUE', "WHERE id = '<sequence.userConsentId>'", "AND user_id = '<sequence.userId>'", "AND consent_id = '<sequence.consents.consentId>'", "AND consent_version = '<sequence.consents.consentVersion>'", "AND row_status = 'ACTIVE'", "AND (NOT is_read OR ('<sequence.consents.resultSpecified>'::BOOLEAN AND result IS DISTINCT FROM '<sequence.consents.result>'::BOOLEAN))"],
    }
    for h,needles in required.items():
        for needle in needles:
            if needle not in sql.get(h,''):errors.append(f'{h} missing {needle}')
    for h in expected[-2:]:
        if 'RETURNING id as user_consent_id, consent_id, consent_version, result, is_read, read_at' not in sql.get(h,''):
            errors.append(f'{h} must return actual persisted response values')
    if 'NOW()' in '\n'.join(sql.values()):errors.append('submit must use fresh post-lock now')
    if any(h.startswith('DELETE') or t.startswith('author.') for t,h,_ in operations):errors.append('submit must preserve history and require no role-assignment query')
    actual,lifecycle=sequence_database_operations(wsd);errors+=lifecycle
    if [(t.split('.')[-1],h,normalize(s)) for t,h,s in operations]!=[(t,h,normalize(s)) for t,h,s in actual]:errors.append('submit spec/sequence SQL differs')
    for _,heading,_ in operations:
        if f'app -> infra: {heading}' not in wsd:errors.append(f'{heading} needs Application request')
        match=re.search(rf'infra -> (\w+): {re.escape(heading)}\n.*?deactivate \1\n([^\n]+)',wsd,re.S)
        if not match or not match[2].strip().startswith('infra -> app: Return '):errors.append(f'{heading} must return data to Application')
    for needle in ('userId = verified sub; accessTokenHash = SHA-256 exact JWT', 'Capture fresh UTC now after user lock; recheck JWT exp',
                   'Compare complete eligible id set and all displayed versions before writes',
                   'loop Each consent in ascending consentId order',
                   'resultSpecified = property present; result = explicit boolean or false for insert',
                   'alt No canonical ACTIVE row for user/consent/version',
                   'else Canonical row already read and result omitted or unchanged',
                   'responseItem = existing evidence; no INSERT or UPDATE; preserve result/readAt',
                   'userConsentId = canonical evidence id; preserve first readAt if already read',
                   'Collect responseItem by original request position',
                   'break Abort entire request on internal consistency failure', 'end break'):
        if needle not in wsd:errors.append(f'submit sequence missing guard/mapping {needle!r}')
    traces,structure=login_sequence_paths(wsd);errors+=structure
    from collections import Counter
    outcomes=[];modes=Counter()
    for trace in traces:
        responses=[e for e in trace if e.startswith('app -> api: HTTP ')]
        if len(responses)!=1:errors.append('each submit trace needs exactly one terminal outcome');continue
        code=int(responses[0].split('HTTP ')[1].split()[0]);outcomes.append(code)
        def ordered(*parts):
            pos=[next((i for i,e in enumerate(trace) if part in e),-1) for part in parts]
            return -1 not in pos and pos==sorted(set(pos))
        writes=[e for e in trace if e.startswith('infra -> ') and ': INSERT' in e or e.startswith('infra -> ') and ': UPDATE' in e]
        begun=any('BEGIN' in e for e in trace)
        if code==200:
            if not ordered('Verify Bearer JWT', 'BEGIN READ COMMITTED', expected[0], 'Capture fresh UTC now',expected[1],expected[2], 'Compare complete eligible id set',expected[3], 'Collect responseItem', 'app -> infra: COMMIT','HTTP 200'):
                errors.append('success must serialize, freshly validate token/current policy, resolve evidence and commit before response')
            if any('ROLLBACK' in e for e in trace):errors.append('success must not roll back')
            if len(writes)>1:errors.append('one item cannot both INSERT and UPDATE')
            mode='insert' if any(': INSERT' in e for e in writes) else 'update' if writes else 'noop';modes[mode]+=1
            if mode=='noop' and not any('responseItem = existing evidence' in e for e in trace):errors.append('no-op must return existing evidence unchanged')
            if mode=='update' and not ordered('userConsentId = canonical evidence id', expected[5], 'responseItem = updated evidence'):errors.append('update needs canonical ownership and actual returned values')
            if 'data.consents = original request order' not in responses[0]:errors.append('success must retain original response order')
        elif begun:
            if not ordered('BEGIN','ROLLBACK',f'HTTP {code}') or any(e=='app -> infra: COMMIT' for e in trace):errors.append('failure must rollback and never fall through to common COMMIT')
            if code in (401,404,409) and writes:errors.append('authentication/reference/version failures precede every write')
        elif code not in (400,401) or any(e.startswith('infra -> ') for e in trace):errors.append('early validation/credential failure must execute no SQL')
        if any(expected[1] in e for e in trace) and not ordered(expected[0],'Capture fresh UTC now',expected[1]):errors.append('active-token reread must follow user lock and fresh now')
    if Counter(outcomes)!=Counter({200:3,400:1,401:3,404:1,409:1,408:1,500:2}) or modes!=Counter({'insert':1,'update':1,'noop':1}):errors.append(f'incomplete submit outcome/mode paths: {dict(Counter(outcomes))}, {dict(modes)}')
    for title,code in {'Success':200,'Fail - Bad Request':400,'Fail - Unauthorized':401,'Fail - Not Found':404,'Fail - Conflict':409,'Fail - Request Timeout':408,'Fail - Internal Server Error':500}.items():
        try:
            status=authen_json(md,title)['status']
            if status['code']!=code or code==500 and 'bizCode' in status:errors.append(f'incorrect {title} envelope')
        except (TypeError,KeyError,ValueError):errors.append(f'missing {title} example')
    errors+=json_blocks_parse(md);errors+=table_lines_aligned(md)
    if '--rendered-svg' in sys.argv:
        import xml.etree.ElementTree as ET
        try:
            root=ET.parse(sys.argv[sys.argv.index('--rendered-svg')+1]).getroot()
            expected_lines=Counter(' '.join(l.split()) for _,_,s in operations for l in s.splitlines() if l.strip())
            visible=Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'))
            missing=expected_lines-visible
            if missing:errors.append(f'rendered submit SQL missing {sum(missing.values())} lines')
            else:print(f'OK: rendered submit SQL ({sum(expected_lines.values())}/{sum(expected_lines.values())} visible lines)')
        except (IndexError,OSError,ET.ParseError) as exc:errors.append(f'cannot verify submit SVG: {exc}')
    if errors:return fail('; '.join(errors))
    print('OK: consent-submit-flow (12 terminal traces; insert/update/no-op; first read, revocation and atomic batch)')
    return 0


COMMANDS['consent-submit-flow'] = check_consent_submit_flow


def check_pending_consent_flow() -> int:
    """Guard current canonical evidence, required/optional pending and one read-only response snapshot."""
    path='e-commerce/doc/api/consent/05-inquiry-pending-consent/spec.md'
    md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    for needle in ('Q16/Q17', 'REPEATABLE READ READ ONLY', 'newest created_at, then greatest id'):
        if needle not in md:errors.append(f'pending rule missing {needle!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for needle in ('BOTH is_read=true AND result=true', 'Optional consent is complete once canonical current-version is_read=true', 'No evidence means pending',
            'submittedVersion does not itself prove acceptance', 'This GET never marks a consent read', 'same snapshot', 'effective_at ASC, id ASC',
            'already-authorized in-flight read', 'inactive/locked/archived/deleted type is hidden', 'Required means c.is_required', 'No FOR UPDATE',
            'A new current version is pending'):
        if needle not in seq:
            errors.append(f'pending sequence note missing {needle!r}')
    canonical_rule=re.search(r'^- Select the canonical ACTIVE evidence row[^\n]+',md,re.M)
    if not canonical_rule or 'newest created_at, then greatest id' not in canonical_rule[0]:
        errors.append('canonical current-version evidence must explicitly use newest created_at then greatest id')
    front=re.match(r'---\n(.*?)\n---\n',md,re.S);fm=front[1] if front else ''
    state=re.search(r'^status: (draft|in-review|approved)$',fm,re.M)
    if not state:errors.append('pending spec needs approval metadata')
    for field in ('approved_by','approved_at'):
        value=re.search(rf'^{field}: (.+)$',fm,re.M)
        if not value or (state and ((state[1]=='approved')==(value[1]=='null'))):errors.append(f'inconsistent pending {field}')
    operations=spec_database_operations(md)
    expected=('QUERY - Check active credential and user','QUERY - Get pending consents','QUERY - Get latest submitted version','QUERY - Get consent type')
    if tuple(h for _,h,_ in operations)!=expected:errors.append('pending requires credential, policy, history and type operations')
    sql={h:re.sub(r'--[^\n]*','',s) for _,h,s in operations}
    required={
        expected[0]: ["at.token = '<sequence.accessTokenHash>'", "at.user_id = '<sequence.userId>'", "at.row_status = 'ACTIVE'", "at.expired_at > '<sequence.now>'", 'AND EXISTS (', 'u.id = at.user_id', "u.row_status = 'ACTIVE'"],
        expected[1]: ["c.row_status = 'ACTIVE'", "c.effective_at <= '<sequence.now>'", "c.expired_at IS NULL OR c.expired_at > '<sequence.now>'", 'AND EXISTS (', 'ct.id = c.consent_type_id', "ct.row_status = 'ACTIVE'", 'AND NOT COALESCE((', 'SELECT uc.is_read AND (NOT c.is_required OR uc.result)', "uc.user_id = '<sequence.userId>'", 'uc.consent_id = c.id', 'uc.consent_version = c.consent_version', "uc.row_status = 'ACTIVE'", 'ORDER BY uc.created_at DESC, uc.id DESC', 'LIMIT 1', '), FALSE)', 'ORDER BY c.effective_at, c.id'],
        expected[2]: ['SELECT DISTINCT ON (uc.consent_id)', 'uc.consent_version as submitted_version', "uc.user_id = '<sequence.userId>'", "uc.consent_id = ANY ('<sequence.consentIds>'::UUID[])", "uc.row_status = 'ACTIVE'", 'ORDER BY uc.consent_id, uc.created_at DESC, uc.id DESC'],
        expected[3]: ['ct.id as consent_type_id', 'ct.name as consent_type_name', "ct.id = ANY ('<sequence.consentTypeIds>'::UUID[])", "ct.row_status = 'ACTIVE'"],
    }
    for h,needles in required.items():
        for needle in needles:
            if needle not in sql.get(h,''):errors.append(f'{h} missing {needle}')
    projection=sql.get(expected[1],'').split('FROM consent.t_consent',1)[0]
    for field in ('id as consent_id','code','consent_type_id','consent_version','consent_name','consent_description','effective_at','expired_at','is_required','body'):
        if not re.search(r'^\s*'+re.escape('c.'+field)+r'\s*,?\s*$',projection,re.M):errors.append(f'pending projection missing exact c.{field}')
    for table,heading,statement in operations:
        if not heading.startswith('QUERY') or not statement.startswith('SELECT') or re.search(r'\b(?:INSERT|UPDATE|DELETE|pg_advisory_xact_lock)\b|\bNOW\s*\(',statement,re.I):errors.append('pending must be read-only with explicit now and no locks')
        if table.startswith('author.'):errors.append('self inquiry requires no assignment-table query')
    actual,lifecycle=sequence_database_operations(wsd);errors+=lifecycle
    if [(t.split('.')[-1],h,normalize(s)) for t,h,s in operations]!=[(t,h,normalize(s)) for t,h,s in actual]:errors.append('pending spec/sequence SQL differs')
    for _,heading,_ in operations:
        if f'app -> infra: {heading}' not in wsd:errors.append(f'{heading} needs Application request')
        match=re.search(rf'infra -> (\w+): {re.escape(heading)}\n.*?deactivate \1\n([^\n]+)',wsd,re.S)
        if not match or not match[2].strip().startswith('infra -> app: Return '):errors.append(f'{heading} needs result returned to Application')
    for needle in ('userId = verified sub; accessTokenHash = SHA-256 exact JWT',
                   'Capture UTC now before first query; establish snapshot and recheck JWT exp',
                   'alt pendingConsents is empty', 'data.consents = []; skip history/type lookups',
                   'consentIds = pendingConsents.consent_id; consentTypeIds = distinct pending type ids',
                   'submittedVersion = latest map or null; require every type name',
                   'Return complete data.consents in effective_at ASC, id ASC order',
                   'Mapping failure throws before COMMIT', 'without recording reading'):
        if needle not in wsd:errors.append(f'pending sequence missing mapping/guard {needle!r}')
    traces,structure=login_sequence_paths(wsd);errors+=structure
    from collections import Counter
    outcomes=[];history_modes=[]
    for trace in traces:
        responses=[e for e in trace if e.startswith('app -> api: HTTP ')]
        if len(responses)!=1:errors.append('each pending trace needs one terminal outcome');continue
        code=int(responses[0].split('HTTP ')[1].split()[0]);outcomes.append(code)
        def ordered(*parts):
            pos=[next((i for i,e in enumerate(trace) if part in e),-1) for part in parts]
            return -1 not in pos and pos==sorted(set(pos))
        begun=any(e.startswith('app -> infra: BEGIN') for e in trace)
        if code==200:
            if not ordered('Verify JWT','BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY','Capture UTC now',expected[0],expected[1],'app -> infra: COMMIT','HTTP 200'):errors.append('pending success must authorize/read one snapshot and commit before response')
            if any('ROLLBACK' in e for e in trace):errors.append('pending success must not roll back')
            has_history=any(expected[2] in e for e in trace);history_modes.append(has_history)
            if has_history:
                if not ordered(expected[1],'consentIds = pendingConsents.consent_id',expected[2],expected[3],'Merge twelve response fields','app -> infra: COMMIT'):errors.append('non-empty pending must map current history and type names from derived ids before commit')
            elif any(expected[3] in e for e in trace) or not any('data.consents = []' in e for e in trace):errors.append('empty pending must skip enrichment and return explicit []')
            if 'data.consents' not in responses[0]:errors.append('success must expose pending array')
        elif begun:
            if not ordered('BEGIN','ROLLBACK',f'HTTP {code}') or any(e=='app -> infra: COMMIT' for e in trace):errors.append('pending error must roll back before response with no commit')
            if code==401 and any(expected[1] in e for e in trace):errors.append('invalid credential cannot read policy/history')
        elif code not in (400,401) or any(e.startswith('infra -> ') for e in trace):errors.append('early error must execute no SQL')
        if any(e.startswith('infra -> ') and ': QUERY' not in e for e in trace):errors.append('pending cannot mutate data')
    if Counter(outcomes)!=Counter({200:2,400:1,401:2,408:1,500:1}) or sorted(history_modes)!=[False,True]:errors.append(f'incomplete pending outcome paths: {dict(Counter(outcomes))}, enrich={history_modes}')
    for title,code in {'Success':200,'Success - No Pending Consent':200,'Fail - Bad Request':400,'Fail - Unauthorized':401,'Fail - Request Timeout':408,'Fail - Internal Server Error':500}.items():
        try:
            obj=authen_json(md,title);status=obj['status']
            if status['code']!=code or code==500 and 'bizCode' in status:errors.append(f'incorrect pending {title} envelope')
            if title=='Success - No Pending Consent' and obj['data']['consents']!=[]:errors.append('empty pending success must contain []')
        except (TypeError,KeyError,ValueError):errors.append(f'missing pending {title} example')
    for text in ('| isRead=false, result=true | Pending | Pending |','| isRead=true, result=false (read-only/rejected) | Pending | Complete |','| isRead=true, result=true | Complete | Complete |'):
        if re.sub(r'\s+','',text) not in re.sub(r'\s+','',wsd):errors.append('pending sequence note must carry the truth table that distinguishes read and accepted for both kinds')
    errors+=json_blocks_parse(md);errors+=table_lines_aligned(md)
    if '--rendered-svg' in sys.argv:
        import xml.etree.ElementTree as ET
        try:
            root=ET.parse(sys.argv[sys.argv.index('--rendered-svg')+1]).getroot()
            expected_lines=Counter(' '.join(l.split()) for _,_,s in operations for l in s.splitlines() if l.strip())
            visible=Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'))
            missing=expected_lines-visible
            if missing:errors.append(f'rendered pending SQL missing {sum(missing.values())} lines')
            else:print(f'OK: rendered pending SQL ({sum(expected_lines.values())}/{sum(expected_lines.values())} visible lines)')
        except (IndexError,OSError,ET.ParseError) as exc:errors.append(f'cannot verify pending SVG: {exc}')
    if errors:return fail('; '.join(errors))
    print('OK: pending-consent-flow (7 terminal traces; canonical required/optional truth table; read-only snapshot and complete mapping)')
    return 0


COMMANDS['pending-consent-flow'] = check_pending_consent_flow


def check_active_consent_flow() -> int:
    """Check the public visible-consent contract, complete type names and read-only paths."""
    path='e-commerce/doc/api/consent/01-inquiry-active-consent/spec.md'
    md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    for needle in ('Q3', 'Public endpoint', 'REPEATABLE READ READ ONLY', 'every visible current consent', 'effective_at ASC, id ASC'):
        if needle not in md:errors.append(f'active consent rule missing {needle!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for needle in ('isRequired comes from c.is_required', 'mandatory consentTypeName', 'This GET never records reading', 'skip the type-name lookup',
            'A type deactivated after this snapshot is absent in the next request'):
        if needle not in seq:
            errors.append(f'active consent sequence note missing {needle!r}')
    if 'authorization' in md.lower():errors.append('public active-consent contract must not require a credential header')
    front=re.match(r'---\n(.*?)\n---\n',md,re.S);fm=front[1] if front else ''
    state=re.search(r'^status: (draft|in-review|approved)$',fm,re.M)
    if not state:errors.append('active-consent needs approval metadata')
    for field in ('approved_by','approved_at'):
        value=re.search(rf'^{field}: (.+)$',fm,re.M)
        if not value or (state and ((state[1]=='approved')==(value[1]=='null'))):errors.append(f'inconsistent active consent {field}')
    operations=spec_database_operations(md)
    expected=('QUERY - Get active consents','QUERY - Get consent type')
    if tuple(h for _,h,_ in operations)!=expected:errors.append('active consent must declare exactly definition and type-name queries')
    sql={h:re.sub(r'--[^\n]*','',s) for _,h,s in operations}
    required={expected[0]:["c.row_status = 'ACTIVE'", "c.effective_at <= '<sequence.now>'", "c.expired_at IS NULL OR c.expired_at > '<sequence.now>'", 'AND EXISTS (', 'FROM consent.m_consent_type ct', 'ct.id = c.consent_type_id', "ct.row_status = 'ACTIVE'", 'ORDER BY c.effective_at, c.id'],
              expected[1]:['ct.id as consent_type_id','ct.name as consent_type_name',"ct.id = ANY ('<sequence.consentTypeIds>'::UUID[])","ct.row_status = 'ACTIVE'"]}
    for h,needles in required.items():
        for needle in needles:
            if needle not in sql.get(h,''):errors.append(f'{h} missing {needle}')
    projection=sql.get(expected[0],'').split('FROM consent.t_consent',1)[0]
    for field in ('id as consent_id','code','consent_type_id','consent_version','consent_name','consent_description','effective_at','expired_at','is_required','body'):
        if not re.search(r'^\s*'+re.escape('c.'+field)+r'\s*,?\s*$',projection,re.M):errors.append(f'active projection missing exact c.{field}')
    for table,heading,statement in operations:
        if table not in ('consent.t_consent','consent.m_consent_type') or 'authen.' in statement or 'author.' in statement:errors.append('public inquiry must not read user/credential/assignment data')
        if not heading.startswith('QUERY') or not statement.startswith('SELECT') or re.search(r'\b(?:INSERT|UPDATE|DELETE|pg_advisory_xact_lock)\b|\bNOW\s*\(',statement,re.I):errors.append('active inquiry requires read-only SQL with server now parameter')
    actual,lifecycle=sequence_database_operations(wsd);errors+=lifecycle
    if [(t.split('.')[-1],h,normalize(s)) for t,h,s in operations]!=[(t,h,normalize(s)) for t,h,s in actual]:errors.append('active spec/sequence SQL differs')
    for _,heading,_ in operations:
        if f'app -> infra: {heading}' not in wsd:errors.append(f'{heading} needs Application request')
        match=re.search(rf'infra -> (\w+): {re.escape(heading)}\n.*?deactivate \1\n([^\n]+)',wsd,re.S)
        if not match or not match[2].strip().startswith('infra -> app: Return '):errors.append(f'{heading} needs Application result')
    for needle in ('Capture server UTC now immediately before first query; establish snapshot','alt visibleConsents is empty',
                   'data.consents = []; skip type-name lookup','consentTypeIds = distinct visibleConsents.consent_type_id',
                   'Merge eleven public fields; require every consentTypeName; preserve nulls and current versions',
                   'Return complete data.consents in effective_at ASC, id ASC order','Mapping failure throws before COMMIT',
                   'without creating user evidence'):
        if needle not in wsd:errors.append(f'active sequence missing mapping/guard {needle!r}')
    traces,structure=login_sequence_paths(wsd);errors+=structure
    from collections import Counter
    outcomes=[];enrich=[]
    for trace in traces:
        response=[e for e in trace if e.startswith('app -> api: HTTP ')]
        if len(response)!=1:errors.append('each active-consent path requires one outcome');continue
        code=int(response[0].split('HTTP ')[1].split()[0]);outcomes.append(code)
        def ordered(*parts):
            pos=[next((i for i,e in enumerate(trace) if part in e),-1) for part in parts]
            return -1 not in pos and pos==sorted(set(pos))
        if code==200:
            if not ordered('BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY','Capture server UTC now',expected[0],'app -> infra: COMMIT','HTTP 200'):errors.append('active success must query one snapshot and commit before response')
            if any('ROLLBACK' in e for e in trace):errors.append('active success must not roll back')
            has_type=any(expected[1] in e for e in trace);enrich.append(has_type)
            if has_type:
                if not ordered(expected[0],'consentTypeIds = distinct',expected[1],'Merge eleven public fields','app -> infra: COMMIT'):errors.append('non-empty active response must derive type ids, query names and map before commit')
            elif not any('data.consents = []' in e for e in trace):errors.append('empty active response must expose []')
        elif code==400:
            if any('BEGIN' in e or e.startswith('infra -> ') for e in trace):errors.append('bad timestamp must execute no SQL or transaction')
        elif code in (408,500):
            if not ordered('BEGIN','ROLLBACK',f'HTTP {code}') or any(e=='app -> infra: COMMIT' for e in trace):errors.append('active failure must rollback and never commit')
        if any(e.startswith('infra -> ') and ': QUERY' not in e for e in trace):errors.append('active inquiry cannot write')
    if Counter(outcomes)!=Counter({200:2,400:1,408:1,500:1}) or sorted(enrich)!=[False,True]:errors.append(f'incomplete active outcomes: {dict(Counter(outcomes))}, enrich={enrich}')
    response_fields={'consentId','code','consentTypeId','consentTypeName','consentVersion','consentName','consentDescription','effectiveAt','expiredAt','isRequired','body'}
    for title,code in {'Success':200,'Success - No Active Consent':200,'Fail - Bad Request':400,'Fail - Request Timeout':408,'Fail - Internal Server Error':500}.items():
        try:
            obj=authen_json(md,title);status=obj['status']
            if status['code']!=code or code==500 and 'bizCode' in status:errors.append(f'incorrect active {title} envelope')
            if title=='Success - No Active Consent' and obj['data']['consents']!=[]:errors.append('empty active list must be []')
            if title=='Success' and any(set(row)!=response_fields or not row['consentTypeName'] for row in obj['data']['consents']):errors.append('active response example needs all eleven public fields and a type name')
        except (TypeError,KeyError,ValueError):errors.append(f'missing active {title} example')
    errors+=json_blocks_parse(md);errors+=table_lines_aligned(md)
    if '--rendered-svg' in sys.argv:
        import xml.etree.ElementTree as ET
        try:
            root=ET.parse(sys.argv[sys.argv.index('--rendered-svg')+1]).getroot()
            expected_lines=Counter(' '.join(l.split()) for _,_,s in operations for l in s.splitlines() if l.strip())
            visible=Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'))
            missing=expected_lines-visible
            if missing:errors.append(f'rendered active SQL missing {sum(missing.values())} lines')
            else:print(f'OK: rendered active SQL ({sum(expected_lines.values())}/{sum(expected_lines.values())} visible lines)')
        except (IndexError,OSError,ET.ParseError) as exc:errors.append(f'cannot verify active SVG: {exc}')
    if errors:return fail('; '.join(errors))
    print('OK: active-consent-flow (5 terminal traces; public type visibility, complete mapping and read-only snapshot)')
    return 0


COMMANDS['active-consent-flow'] = check_active_consent_flow


def check_address_inquiry_flow() -> int:
    """Check current-caller address count/page consistency and safe bound filters."""
    path=AUTHEN_SPECS['10'];md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    for needle in ('status: in-review', 'approved_by: null', 'approved_at: null', 'Count and page share the same repeatable-read snapshot'):
        if needle not in md:errors.append(f'address-inquiry spec missing {needle!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for needle in ('exact same userId/non-DELETED/id/searchPattern/rowStatus predicates', 'offset outside nonnegative BIGINT', 'entire pattern as text',
            'existing case-insensitive ILIKE wildcard semantics', "other user's address returns an empty list", 'An id filter is still paginated',
            'skip the list query', 'items=[] while totalItems/totalPages remain positive', 'exactly five data keys', 'Require the returned page row count',
            'COMMIT only after complete decryption/mapping succeeds'):
        if needle not in seq:
            errors.append(f'address-inquiry sequence note missing {needle!r}')
    operations=spec_database_operations(md);expected=('QUERY - Check current credential and user','QUERY - Get total items','QUERY - Get user addresses')
    if tuple(h for _,h,_ in operations)!=expected:errors.append('inquiry needs current credential, identical-filter count and optional page in execution order')
    sql={h:re.sub(r'--[^\n]*','',s) for _,h,s in operations}
    required={expected[0]:['JOIN authen.m_user u ON u.id = at.user_id',"at.token = '<sequence.accessTokenHash>'","at.user_id = '<sequence.userId>'","at.row_status = 'ACTIVE'","at.expired_at > '<sequence.now>'","u.row_status = 'ACTIVE'"]}
    filters=["WHERE ua.user_id = '<sequence.userId>'","AND ua.row_status <> 'DELETED'","AND ('<sequence.id>' IS NULL OR ua.id = '<sequence.id>')","AND ('<sequence.searchPattern>' IS NULL OR ua.title ILIKE '<sequence.searchPattern>')","AND ('<sequence.rowStatus>' IS NULL OR ua.row_status = '<sequence.rowStatus>')"]
    for h in expected[1:]:required[h]=filters
    required[expected[1]]=filters+['COUNT(ua.id) as total_items']
    required[expected[2]]=filters+["LIMIT '<sequence.pageSize>' OFFSET '<sequence.offset>'"]
    for h,needles in required.items():
        for needle in needles:
            if needle not in sql.get(h,''):errors.append(f'{h} missing {needle}')
    def where(h):
        match=re.search(r'\bWHERE\b(.*?)(?:\bORDER BY\b|\bLIMIT\b|$)',sql.get(h,''),re.S)
        return normalize(match[1]) if match else None
    if where(expected[1])!=where(expected[2]):errors.append('count/list WHERE predicates must be identical')
    projection=re.search(r'SELECT\s+(.*?)\s+FROM\s',sql.get(expected[2],''),re.S)
    columns=['ua.id as user_address_id','ua.title','ua.is_default','ua.address','ua.city','ua.state','ua.postal_code','ua.country','ua.row_status']
    if not projection or normalize(projection[1])!=normalize(',\n'.join(columns)):errors.append('page must return only nine address fields, no user/token/audit data')
    if not re.search(r"ORDER BY ua\.is_default DESC, ua\.created_at DESC, ua\.id(?: ASC)?\s+LIMIT",sql.get(expected[2],'')):errors.append('page sort must end with ascending unique id after default/newest')
    if 'NOW()' in '\n'.join(sql.values()) or SEQUENCE_LOCK.search('\n'.join(sql.values())) or any(not s.lstrip().startswith('SELECT') for s in sql.values()):errors.append('inquiry must be SELECT-only without locks and use freshly bound now')
    actual,lifecycle=sequence_database_operations(wsd);errors+=lifecycle
    if [(t.split('.')[-1],h,s) for t,h,s in operations]!=actual:errors.append('address-inquiry spec/sequence SQL differs character-for-character or order')
    for _,heading,_ in operations:
        if f'app -> infra: {heading}' not in wsd:errors.append(f'{heading} needs Application request')
        mapping=re.search(rf'infra -> (\w+): {re.escape(heading)}\n.*?\1 -> infra: Return ([^\n]+)\n.*?deactivate \1\n\s*infra -> app: Return ([^\n]+)',wsd,re.S)
        if not mapping or mapping[2]!=mapping[3]:errors.append(f'{heading} database/Application result mapping differs')
    for needle in ('Verify JWT signature/issuer/audience/expiry/UUID sub','userId = verified sub; accessTokenHash = SHA-256 exact JWT',
                   'checked offset = (pageIndex - 1) * pageSize; reject BIGINT overflow',
                   'Bind omitted id/rowStatus/searchPattern as typed SQL NULL; searchPattern = percent + supplied search + percent, preserve ILIKE wildcards',
                   'Capture fresh server UTC now immediately before credential read; recheck JWT exp',
                   'alt JWT still unexpired at fresh now',
                   'alt totalItems = 0','items = []; skip page query',
                   'Require returned row count = min(pageSize, max(0, totalItems - offset)); mismatch is internal failure',
                   'Map each row to exactly userAddressId/title/isDefault/address/city/state/postalCode/country/rowStatus; decrypt five sensitive fields',
                   'items = []; preserve positive totalItems/totalPages; do not return 404',
                   'data = items/pageIndex/pageSize/totalItems/totalPages; explicit empty array; exclude userId/token/hash/audit'):
        if needle not in wsd:errors.append(f'address inquiry sequence missing {needle!r}')
    traces,structure=login_sequence_paths(wsd);errors+=structure
    from collections import Counter
    outcomes=[];modes=Counter();unauthorized=[]
    for trace in traces:
        response=[e for e in trace if e.startswith('app -> api: HTTP ')]
        if len(response)!=1:errors.append('address inquiry trace needs one terminal outcome');continue
        code=int(response[0].split('HTTP ')[1].split()[0]);outcomes.append(code)
        def ordered(*parts):
            pos=[next((i for i,e in enumerate(trace) if part in e),-1) for part in parts]
            return -1 not in pos and pos==sorted(set(pos))
        queries=[e for e in trace if e.startswith('infra -> ')];begun=any(e.startswith('app -> infra: BEGIN') for e in trace)
        if queries and not ordered('checked offset = (pageIndex - 1) * pageSize','Verify JWT','userId = verified sub','Bind omitted id/rowStatus/searchPattern','BEGIN REPEATABLE READ READ ONLY','Capture fresh server UTC now',expected[0]):errors.append('address read needs verified caller, typed filters and fresh credential snapshot')
        if any(expected[1] in e for e in trace) and not ordered(expected[0],expected[1]):errors.append('count must follow current token/user gate')
        if any(expected[2] in e for e in trace) and not ordered(expected[1],expected[2]):errors.append('page must follow its same-snapshot total count')
        if any(': QUERY' not in e for e in queries):errors.append('address inquiry may never write')
        if code==200:
            if any('items = []; skip page query' in e for e in trace):mode='zero'
            elif any('preserve positive totalItems/totalPages' in e for e in trace):mode='beyond'
            else:mode='rows'
            modes[mode]+=1
            if len(queries)!=(2 if mode=='zero' else 3):errors.append('zero count skips page; positive count must query page')
            if not ordered(expected[1],'data = items/pageIndex','app -> infra: COMMIT','HTTP 200') or any('ROLLBACK' in e for e in trace):errors.append('success requires complete mapping/commit before 200')
            if mode!='zero' and not any('Require returned row count =' in e for e in trace):errors.append('positive count must validate page cardinality')
            if 'all five pagination keys' not in response[0]:errors.append('address list response must have complete metadata')
        elif begun:
            if not ordered('BEGIN','ROLLBACK',f'HTTP {code}') or any(e=='app -> infra: COMMIT' for e in trace):errors.append('read/mapping failure rolls back before error')
            if code==401 and len(queries)>1:errors.append('invalid current credential must not query addresses')
        elif code not in (400,401) or queries:errors.append('invalid input/JWT must execute no SQL')
        if code==401:unauthorized.append(len(queries))
    if Counter(outcomes)!=Counter({200:3,400:1,401:3,408:1,500:1}) or modes!=Counter({'zero':1,'rows':1,'beyond':1}) or sorted(unauthorized)!=[0,0,1]:errors.append(f'incomplete address inquiry paths: {dict(Counter(outcomes))}; modes={dict(modes)}; 401 SQL={unauthorized}')
    item_keys={'userAddressId','title','isDefault','address','city','state','postalCode','country','rowStatus'}
    for title,code in {'Success':200,'Success - By Id':200,'Success - Not Found':200,'Success - Page Beyond Range':200,'Fail - Bad Request':400,'Fail - Unauthorized':401,'Fail - Request Timeout':408,'Fail - Internal Server Error':500}.items():
        try:
            obj=authen_json(md,title);status=obj['status']
            if status['code']!=code or code==500 and 'bizCode' in status:errors.append(f'incorrect address inquiry {title} envelope')
            if code==200:
                data=obj['data']
                if set(data)!={'items','pageIndex','pageSize','totalItems','totalPages'}:errors.append(f'{title} needs exactly five data keys');continue
                if any(type(data[k]) is not int for k in ('pageIndex','pageSize','totalItems','totalPages')) or data['pageIndex']<1 or not 1<=data['pageSize']<=100 or data['totalItems']<0:errors.append(f'{title} pagination must use valid integer bounds');continue
                total=data['totalItems'];size=data['pageSize'];offset=(data['pageIndex']-1)*size
                if data['totalPages']!=(0 if total==0 else (total+size-1)//size) or len(data['items'])!=min(size,max(0,total-offset)):errors.append(f'{title} totals/page cardinality incorrect')
                for item in data['items']:
                    if set(item)!=item_keys or item['rowStatus']=='DELETED':errors.append(f'{title} leaks/misses fields or lists DELETED')
                ids=[x['userAddressId'] for x in data['items']]
                if len(ids)!=len(set(ids)):errors.append(f'{title} duplicates address ids')
                flags=[x['isDefault'] for x in data['items']]
                if any(type(x) is not bool for x in flags) or sum(flags)>1 or flags!=sorted(flags,reverse=True):errors.append(f'{title} default flag/order incorrect')
                if title=='Success - Page Beyond Range' and (data['items'] or total==0 or data['pageIndex']<=data['totalPages']):errors.append('beyond-range example needs empty page with positive totals')
        except (TypeError,KeyError,ValueError):errors.append(f'missing/malformed address inquiry {title} example')
    errors+=json_blocks_parse(md);errors+=table_lines_aligned(md)
    if '--rendered-svg' in sys.argv:
        import xml.etree.ElementTree as ET
        try:
            root=ET.parse(sys.argv[sys.argv.index('--rendered-svg')+1]).getroot()
            expected_lines=Counter(' '.join(l.split()) for _,_,s in operations for l in s.splitlines() if l.strip())
            visible=Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'))
            missing=expected_lines-visible
            if missing:errors.append(f'rendered address-inquiry SQL missing {sum(missing.values())} lines')
            else:print(f'OK: rendered address-inquiry SQL ({sum(expected_lines.values())}/{sum(expected_lines.values())} visible lines)')
        except (IndexError,OSError,ET.ParseError) as exc:errors.append(f'cannot verify address inquiry SVG: {exc}')
    if errors:return fail('; '.join(errors))
    print('OK: address-inquiry-flow (9 terminal traces; exact SQL, current credential gate and consistent filtered pagination)')
    return 0


COMMANDS['address-inquiry-flow'] = check_address_inquiry_flow


def check_profile_inquiry_flow() -> int:
    """Check own-profile live credential projection, read consistency and complete nullable output."""
    path=AUTHEN_SPECS['08'];md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    for needle in ('status: in-review', 'approved_by: null', 'approved_at: null', 'Read user and information from the same repeatable-read snapshot'):
        if needle not in md:errors.append(f'profile-inquiry spec missing {needle!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for needle in ('Q20 is approved by the product owner', 'คืน null สำหรับค่าว่างเดิม (แนะนำ)', 'No id/userId/query filters or body are accepted',
            'all ten data keys every time', 'explicit JSON null, never an omitted key', 'response normalization only',
            'No information row is a normal state, not 404', 'No user/credential lock', 'COMMIT the read-only transaction only after mapping succeeds',
            'Unexpected mapping/decryption failure'):
        if needle not in seq:
            errors.append(f'profile-inquiry sequence note missing {needle!r}')
    operations=spec_database_operations(md);expected=('QUERY - Get user','QUERY - Get information')
    if tuple(h for _,h,_ in operations)!=expected:errors.append('inquiry needs exactly the joined user/credential query then own information query')
    sql={h:re.sub(r'--[^\n]*','',s) for _,h,s in operations}
    required={expected[0]:['JOIN authen.t_user_access_token at ON at.user_id = u.id',"WHERE u.id = '<sequence.userId>'","AND u.row_status = 'ACTIVE'","AND at.token = '<sequence.accessTokenHash>'","AND at.user_id = '<sequence.userId>'","AND at.row_status = 'ACTIVE'","AND at.expired_at > '<sequence.now>'"],
              expected[1]:["WHERE ui.user_id = '<sequence.userId>'","AND ui.row_status <> 'DELETED'"]}
    projections={expected[0]:['u.id as user_id','u.email_address','u.first_name','u.last_name','u.display_name','u.profile_picture_path'],expected[1]:['ui.phone_number','ui.address','ui.date_of_birth',"NULLIF(ui.gender, '') as gender"]}
    for h,needles in required.items():
        for needle in needles:
            if needle not in sql.get(h,''):errors.append(f'{h} missing {needle}')
        match=re.search(r'SELECT\s+(.*?)\s+FROM\s',sql.get(h,''),re.S)
        if not match or normalize(match[1])!=normalize(',\n'.join(projections[h])):errors.append(f'{h} must project only its exact profile fields with Q20 NULLIF')
    if 'NOW()' in '\n'.join(sql.values()) or SEQUENCE_LOCK.search('\n'.join(sql.values())) or any(not s.lstrip().startswith('SELECT') for s in sql.values()):errors.append('inquiry must be SELECT-only without locks and use freshly bound now')
    actual,lifecycle=sequence_database_operations(wsd);errors+=lifecycle
    if [(t.split('.')[-1],h,s) for t,h,s in operations]!=actual:errors.append('profile-inquiry spec/sequence SQL differs character-for-character or order')
    for _,heading,_ in operations:
        if f'app -> infra: {heading}' not in wsd:errors.append(f'{heading} needs Application request')
        mapping=re.search(rf'infra -> (\w+): {re.escape(heading)}\n.*?\1 -> infra: Return ([^\n]+)\n.*?deactivate \1\n\s*infra -> app: Return ([^\n]+)',wsd,re.S)
        if not mapping or mapping[2]!=mapping[3]:errors.append(f'{heading} database/Application result mapping differs')
    for needle in ('Verify JWT signature/issuer/audience/expiry/UUID sub','userId = verified sub; accessTokenHash = SHA-256 exact JWT',
                   'Capture fresh server UTC now immediately before joined read; recheck JWT exp','alt JWT still unexpired at fresh now',
                   'data.userId = verified sub; data.emailAddress = decrypt stored email',
                   'data.firstName/lastName = decrypt non-null stored values; data.displayName/profilePicturePath = stored values or null',
                   'data.phoneNumber/address = decrypt non-null stored values; data.dateOfBirth = YYYY-MM-DD or null; data.gender = SQL normalized gender',
                   'data.phoneNumber/address/dateOfBirth/gender = null; do not create a row',
                   'Emit exactly ten profile keys including explicit nulls; exclude username/password/token/hash/salt/session/audit/roles'):
        if needle not in wsd:errors.append(f'profile inquiry sequence missing {needle!r}')
    traces,structure=login_sequence_paths(wsd);errors+=structure
    from collections import Counter
    outcomes=[];modes=Counter();unauthorized=[]
    for trace in traces:
        response=[e for e in trace if e.startswith('app -> api: HTTP ')]
        if len(response)!=1:errors.append('profile inquiry trace needs one outcome');continue
        code=int(response[0].split('HTTP ')[1].split()[0]);outcomes.append(code)
        def ordered(*parts):
            pos=[next((i for i,e in enumerate(trace) if part in e),-1) for part in parts]
            return -1 not in pos and pos==sorted(set(pos))
        queries=[e for e in trace if e.startswith('infra -> ')];begun=any(e.startswith('app -> infra: BEGIN') for e in trace)
        if queries and not ordered('Verify JWT','userId = verified sub','BEGIN REPEATABLE READ READ ONLY','Capture fresh server UTC now',expected[0]):errors.append('profile read must follow verified identity, read-only snapshot and fresh time')
        if any(expected[1] in e for e in trace) and not ordered(expected[0],expected[1]):errors.append('information query must follow eligible joined profile')
        if any(': QUERY' not in e for e in queries):errors.append('profile inquiry must never write')
        if code==200:
            mode='missing' if any('data.phoneNumber/address/dateOfBirth/gender = null' in e for e in trace) else 'present';modes[mode]+=1
            if len(queries)!=2 or not ordered(expected[0],expected[1],'data.userId = verified sub','Emit exactly ten','app -> infra: COMMIT','HTTP 200') or any('ROLLBACK' in e for e in trace):errors.append('success requires both consistent reads and complete mapping before commit/response')
            if 'all ten data keys' not in response[0]:errors.append('profile success must return complete data')
        elif begun:
            if not ordered('BEGIN','ROLLBACK',f'HTTP {code}') or any(e=='app -> infra: COMMIT' for e in trace):errors.append('read failure must roll back before error without commit')
            if code==401 and len(queries)>1:errors.append('invalid current credential must not read information')
        elif code not in (400,401) or queries:errors.append('invalid input/JWT must execute no SQL')
        if code==401:unauthorized.append(len(queries))
    if Counter(outcomes)!=Counter({200:2,400:1,401:3,408:1,500:1}) or modes!=Counter({'present':1,'missing':1}) or sorted(unauthorized)!=[0,0,1]:errors.append(f'incomplete profile inquiry paths: {dict(Counter(outcomes))}; modes={dict(modes)}; 401 SQL={unauthorized}')
    keys={'userId','emailAddress','firstName','lastName','displayName','profilePicturePath','phoneNumber','address','dateOfBirth','gender'}
    data_table=md.split('### Data Object',1)[-1].split('### Example Response Parameters',1)[0]
    required_keys={cells[2].strip() for line in data_table.splitlines() if line.startswith('|') and len(cells:=line.split('|'))>5 and cells[4].strip()=='MANDATORY'}
    if required_keys!=keys:errors.append('response table must require all ten keys; nullable does not mean omitted')
    for title,code in {'Success':200,'Success - No Information':200,'Success - Unset Gender':200,'Fail - Bad Request':400,'Fail - Unauthorized':401,'Fail - Request Timeout':408,'Fail - Internal Server Error':500}.items():
        try:
            obj=authen_json(md,title);status=obj['status']
            if status['code']!=code or code==500 and 'bizCode' in status:errors.append(f'incorrect inquiry {title} envelope')
            if code==200:
                data=obj['data']
                if set(data)!=keys or data['gender'] not in (None,'MALE','FEMALE','OTHER'):errors.append(f'{title} must have ten keys and normalized gender')
                if title=='Success - No Information' and any(data[k] is not None for k in ('phoneNumber','address','dateOfBirth','gender')):errors.append('missing information example requires four null keys')
                if title=='Success - Unset Gender' and data['gender'] is not None:errors.append('Q20 unset gender example must be null')
        except (TypeError,KeyError,ValueError):errors.append(f'missing profile inquiry {title} example')
    errors+=json_blocks_parse(md);errors+=table_lines_aligned(md)
    if '--rendered-svg' in sys.argv:
        import xml.etree.ElementTree as ET
        try:
            root=ET.parse(sys.argv[sys.argv.index('--rendered-svg')+1]).getroot()
            expected_lines=Counter(' '.join(l.split()) for _,_,s in operations for l in s.splitlines() if l.strip())
            visible=Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'))
            missing=expected_lines-visible
            if missing:errors.append(f'rendered profile-inquiry SQL missing {sum(missing.values())} lines')
            else:print(f'OK: rendered profile-inquiry SQL ({sum(expected_lines.values())}/{sum(expected_lines.values())} visible lines)')
        except (IndexError,OSError,ET.ParseError) as exc:errors.append(f'cannot verify inquiry SVG: {exc}')
    if errors:return fail('; '.join(errors))
    print('OK: profile-inquiry-flow (8 terminal traces; exact SQL, current credential snapshot and Q20 nullable mapping)')
    return 0


COMMANDS['profile-inquiry-flow'] = check_profile_inquiry_flow


def check_author_me_flow() -> int:
    """Check the calling-token role snapshot while preserving live credential/user revocation."""
    path='e-commerce/doc/api/author/12-me/spec.md'
    md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    for needle in ('Q4/Q11/Q13', "calling token's role snapshot", 'one read-only autocommit SELECT'):
        if needle not in md:errors.append(f'me rule missing {needle!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for needle in ('Do not query author.t_user_role or author.m_role', 'duplicate entries', 'roles must be an array of unique non-empty strings, including explicit []',
            'ordinal case-sensitive comparison.', 'isPlatformAdmin is true exactly when one returned role name equals PLATFORM_ADMIN',
            'Do not trust an independent isPlatformAdmin token claim', 'Role/assignment changes after issuance do not change this token',
            'Every refresh resolves latest ACTIVE grants', 'stored token for that hash/userId and an ACTIVE user', 'There is no 403',
            'Permissions and scopes are not returned'):
        if needle not in seq:
            errors.append(f'me sequence note missing {needle!r}')
    front=re.match(r'---\n(.*?)\n---\n',md,re.S);fm=front[1] if front else ''
    state=re.search(r'^status: (draft|in-review|approved)$',fm,re.M)
    if not state:errors.append('me requires approval metadata')
    for field in ('approved_by','approved_at'):
        value=re.search(rf'^{field}: (.+)$',fm,re.M)
        if not value or (state and ((state[1]=='approved')==(value[1]=='null'))):errors.append(f'inconsistent me {field}')
    operations=spec_database_operations(md)
    if len(operations)!=1 or operations[0][:2]!=('authen.t_user_access_token','QUERY - Check active credential and user'):
        errors.append('me must execute only the current credential/user query, never live role queries')
    statement=operations[0][2] if len(operations)==1 else ''
    for needle in ('SELECT\n    at.user_id',"at.token = '<sequence.accessTokenHash>'", "at.user_id = '<sequence.userId>'", "at.row_status = 'ACTIVE'", "at.expired_at > '<sequence.now>'", 'AND EXISTS (','FROM authen.m_user u','u.id = at.user_id',"u.row_status = 'ACTIVE'"):
        if needle not in statement:errors.append(f'me credential SQL missing {needle}')
    if re.search(r'\b(?:INSERT|UPDATE|DELETE)\b|\bNOW\s*\(|\bFOR\s+(?:UPDATE|SHARE)\b',statement,re.I) or 'author.' in statement:
        errors.append('me SQL must not write, lock, use stale NOW() or read authorization assignments')
    actual,lifecycle=sequence_database_operations(wsd);errors+=lifecycle
    if [(t.split('.')[-1],h,normalize(s)) for t,h,s in operations]!=[(t,h,normalize(s)) for t,h,s in actual]:errors.append('me spec/sequence SQL differs')
    for needle in ('app -> infra: QUERY - Check active credential and user',
                   'infra -> app: Return ACTIVE matching token/user or no row',
                   'Verify JWT signature/issuer/audience/exp/UUID sub and roles claim as unique non-empty strings (payload of 2026-11-13)',
                   'userId = verified sub; accessTokenHash = SHA-256 exact JWT',
                   'Capture fresh server UTC now before credential query; recheck JWT exp',
                   'roles = copy the role names from verifiedJwt.roles; sort ordinal',
                   'alt Token roles is empty','data.roles = []; isPlatformAdmin = false',
                   'else Returned token roles contain exact name PLATFORM_ADMIN',
                   'data.roles = sorted token roles; isPlatformAdmin = true',
                   'else Other token roles','data.roles = sorted token roles; isPlatformAdmin = false',
                   'data.userId = verified sub; ignore independent admin flag; no live role-table lookup'):
        if needle not in wsd:errors.append(f'me sequence missing guard/mapping {needle!r}')
    if 'TODO(author)' in wsd or re.search(r'app -> infra: (?:BEGIN|COMMIT|ROLLBACK)',wsd):errors.append('me requires a finished single-read autocommit sequence')
    traces,structure=login_sequence_paths(wsd);errors+=structure
    from collections import Counter
    outcomes=[];modes=Counter()
    for trace in traces:
        responses=[e for e in trace if e.startswith('app -> api: HTTP ')]
        if len(responses)!=1:errors.append('each me trace needs one terminal outcome');continue
        code=int(responses[0].split('HTTP ')[1].split()[0]);outcomes.append(code)
        queries=[e for e in trace if e.startswith('infra -> ')]
        def ordered(*parts):
            pos=[next((i for i,e in enumerate(trace) if part in e),-1) for part in parts]
            return -1 not in pos and pos==sorted(set(pos))
        if queries and not ordered('Verify JWT','userId = verified sub','Capture fresh server UTC now','QUERY - Check active credential and user'):
            errors.append('every credential lookup must follow verified identity and captured current time')
        if code==200:
            if not ordered('Verify JWT','userId = verified sub','Capture fresh server UTC now','QUERY - Check active credential and user','roles = copy the role names','data.userId = verified sub','HTTP 200') or len(queries)!=1:
                errors.append('me success must verify JWT and live credential/user before mapping token roles')
            if any('data.roles = []' in e for e in trace):modes['empty']+=1
            elif any(e.endswith('isPlatformAdmin = true') for e in trace):modes['admin']+=1
            else:modes['other']+=1
            for field in ('data.userId','data.isPlatformAdmin','data.roles'):
                if field not in responses[0]:errors.append(f'me success missing {field}')
        elif code==400 and queries:errors.append('invalid header must execute no SQL')
        elif code==401 and len(queries)>1:errors.append('invalid me credential must not query roles')
        if any(': QUERY' not in e for e in queries):errors.append('me must not write')
    if Counter(outcomes)!=Counter({200:3,400:1,401:2,408:1,500:1}) or modes!=Counter({'empty':1,'admin':1,'other':1}):errors.append(f'incomplete me outcomes/modes: {dict(Counter(outcomes))}, {dict(modes)}')
    for title,code in {'Success':200,'Success - Platform Administrator':200,'Success - No Role':200,'Fail - Bad Request':400,'Fail - Unauthorized':401,'Fail - Request Timeout':408,'Fail - Internal Server Error':500}.items():
        try:
            obj=author_json(md,title);status=obj['status']
            if status['code']!=code or code==500 and 'bizCode' in status:errors.append(f'incorrect me {title} envelope')
            if code==200:
                data=obj['data'];roles=data['roles']
                if set(data)!={'userId','isPlatformAdmin','roles'} or any(type(r) is not str for r in roles):errors.append('me examples must have the three response fields and roles as name strings only')
                if roles!=sorted(roles) or data['isPlatformAdmin']!=('PLATFORM_ADMIN' in roles):errors.append('me example role ordering/admin flag is inconsistent')
        except (TypeError,KeyError,ValueError):errors.append(f'missing me {title} example')
    errors+=json_blocks_parse(md);errors+=table_lines_aligned(md)
    if '--rendered-svg' in sys.argv:
        import xml.etree.ElementTree as ET
        try:
            root=ET.parse(sys.argv[sys.argv.index('--rendered-svg')+1]).getroot()
            expected_lines=Counter(' '.join(l.split()) for _,_,s in operations for l in s.splitlines() if l.strip())
            visible=Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'))
            missing=expected_lines-visible
            if missing:errors.append(f'rendered me SQL missing {sum(missing.values())} lines')
            else:print(f'OK: rendered me SQL ({sum(expected_lines.values())}/{sum(expected_lines.values())} visible lines)')
        except (IndexError,OSError,ET.ParseError) as exc:errors.append(f'cannot verify me SVG: {exc}')
    if errors:return fail('; '.join(errors))
    print('OK: author-me-flow (8 terminal traces; calling-token roles and current credential/user checks)')
    return 0


COMMANDS['author-me-flow'] = check_author_me_flow


def check_permission_upsert_flow() -> int:
    """Check scoped permission parent/link phases, owner Q22/Q23 and atomic rollback."""
    path=f'{AUTHOR_DIR}/{AUTHOR_SPECS["04"]}/spec.md';md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    for n in ('status: in-review', 'approved_by: null', 'approved_at: null'):
        if n not in md:errors.append(f'permission spec missing {n!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for n in ('malformed/missing roles is generic 401', 'exact PLATFORM_ADMIN', 'scopes omitted or [] means no link change', 'duplicate parsed child ids',
            'Lock order: caller user -> existing permission', 'beforeDefinitionCount > 0 and finalDefinitionCount = 0', 'already-unscoped permission',
            'all child reference/duplicate/in-use checks precede any parent/child write', 'Capture beforeDefinitionCount as every non-DELETED definition',
            'After all parent/child writes', 'final whole-request invariant', 'Map exactly data.permissionId', 'uq_m_permission_name',
            'uq_t_permission_scope_permission_id_scope_id', 'ใช่ ปฏิเสธจนถอน grant เดิมครบ', 'ใช่ อนุญาตถอน link ของ scope ที่ปิดแล้ว'):
        if n not in seq:
            errors.append(f'permission sequence note missing {n!r}')
    for n in ('QUERY - Get the platform administrator role','QUERY - Check platform administrator'):
        if n in md or n in wsd:errors.append('permission caller authorization may not reload live grants')
    if 'Q24 approved by the product owner' not in ' '.join(wsd.split()) or 'rowStatus = DELETED and finalDefinitionCount > 0' not in ' '.join(wsd.split()):errors.append('permission sequence note must define owner Q24 final deletion guard')
    q24='alt Parent rowStatus = DELETED and finalDefinitionCount > 0 (Q24)'
    passed='Q24 passed: parent is not DELETED or finalDefinitionCount = 0'
    if q24 not in wsd or passed not in wsd:errors.append('permission sequence must enforce Q24 after final count')
    block=re.search(r'(?m)^( *)'+re.escape(q24)+r'\n(.*?)^\1else Q24 passed\n(.*?)^\1end\n',wsd,re.S)
    if not block or 'app -> infra: ROLLBACK' not in block[2] or 'HTTP 409 E10006 Permission cannot be deleted while scope definitions remain.' not in block[2] or passed not in block[3]:errors.append('Q24 branch must reject with exact 409 E10006 and rollback, otherwise pass explicitly')
    ops=spec_database_operations(md);heads=('QUERY - Lock the caller user','QUERY - Check current credential and user','QUERY - Check existing permission','QUERY - Check scope','QUERY - Check existing permission scope','QUERY - Count permission scope definitions','QUERY - Check duplicate name','QUERY - Check role permission in use','QUERY - Check user permission in use','QUERY - Check duplicate permission scope','QUERY - Check role permission scope in use','QUERY - Check user permission scope in use','INSERT - Create permission','UPDATE - Update or delete permission','INSERT - Create permission scope','UPDATE - Update or delete permission scope')
    if tuple(h for _,h,_ in ops)!=heads:errors.append('permission needs all 16 caller/parent/master/link/count/conflict/write definitions')
    sql={h:re.sub(r'--[^\n]*','',q) for _,h,q in ops};need={
        heads[0]:["WHERE u.id = '<sequence.callerUserId>'",'FOR UPDATE'],heads[1]:['JOIN authen.m_user u ON u.id = at.user_id',"at.token = '<sequence.accessTokenHash>'","at.user_id = '<sequence.callerUserId>'","at.row_status = 'ACTIVE'","at.expired_at > '<sequence.now>'","u.row_status = 'ACTIVE'"],
        heads[2]:["WHERE p.id = '<sequence.id>'","AND p.row_status <> 'DELETED'",'FOR UPDATE'],heads[3]:["WHERE s.id = ANY ('<sequence.activeScopeIds>'::UUID[])","AND s.row_status = 'ACTIVE'",'ORDER BY s.id\nFOR UPDATE'],heads[4]:['ps.scope_id',"WHERE ps.id = ANY ('<sequence.permissionScopeIds>'::UUID[])","AND ps.permission_id = '<sequence.permissionId>'","AND ps.row_status <> 'DELETED'",'ORDER BY ps.id\nFOR UPDATE'],
        heads[5]:['COUNT(ps.id) as definition_count',"WHERE ps.permission_id = '<sequence.permissionId>'","AND ps.row_status <> 'DELETED'"],heads[6]:["WHERE p.name = '<sequence.name>'","AND p.row_status <> 'DELETED'","AND ('<sequence.id>' IS NULL OR p.id <> '<sequence.id>')"],heads[7]:["WHERE rp.permission_id = '<sequence.permissionId>'","AND rp.row_status <> 'DELETED'"],heads[8]:["WHERE up.permission_id = '<sequence.permissionId>'","AND up.row_status <> 'DELETED'"],
        heads[9]:["WHERE ps.permission_id = '<sequence.permissionId>'","AND ps.scope_id = '<sequence.scopes.scopeId>'","AND ps.row_status <> 'DELETED'","AND ('<sequence.scopes.id>' IS NULL OR ps.id <> '<sequence.scopes.id>')"],heads[10]:["WHERE rps.permission_scope_id = '<sequence.scopes.id>'","AND rps.row_status <> 'DELETED'"],heads[11]:["WHERE up.permission_scope_id = '<sequence.scopes.id>'","AND up.row_status <> 'DELETED'"],
        heads[12]:['created_by,\n    created_at,','<sequence.createdBy>','<sequence.now>','<sequence.rowStatus>','<sequence.name>','<sequence.description>','RETURNING id as permission_id'],heads[13]:["updated_by = '<sequence.updatedBy>'","updated_at = '<sequence.now>'","row_status = '<sequence.rowStatus>'","WHERE id = '<sequence.id>'","AND row_status <> 'DELETED'",'RETURNING id as permission_id'],
        heads[14]:['created_by,\n    created_at,','<sequence.now>','<sequence.permissionId>','<sequence.scopes.scopeId>','<sequence.scopes.rowStatus>','RETURNING id as permission_scope_id'],heads[15]:["updated_by = '<sequence.updatedBy>'","updated_at = '<sequence.now>'","row_status = '<sequence.scopes.rowStatus>'","WHERE id = '<sequence.scopes.id>'","AND permission_id = '<sequence.permissionId>'","AND scope_id = '<sequence.scopes.scopeId>'","AND row_status <> 'DELETED'",'RETURNING id as permission_scope_id']}
    for h,ns in need.items():
        for n in ns:
            if n not in sql.get(h,''):errors.append(f'{h} missing {n!r}')
    if 'JOIN' in sql.get(heads[5],'') or "row_status = 'ACTIVE'" in sql.get(heads[5],''):errors.append('definition count must not lose closed definitions/masters')
    if 'NOW()' in '\n'.join(sql.values()) or any('created_at =' in sql.get(h,'') for h in heads[13::2]):errors.append('writes use bound fresh server time and preserve creation audit')
    actual,lifecycle=sequence_database_operations(wsd);errors+=lifecycle
    from collections import Counter
    expected=Counter((t.split('.')[-1],h,q) for t,h,q in ops)
    for t,h,q in ops:
        if h in (heads[5],heads[7],heads[8]):expected[(t.split('.')[-1],h,q)]+=1
    if Counter(actual)!=expected:errors.append('permission SQL differs character-for-character or has missing/excess repeated operations')
    lines=wsd.splitlines()
    for i,l in enumerate(lines):
        req=re.match(r'^( *)infra -> \w+: (?:QUERY|INSERT|UPDATE) - ',l)
        if not req:continue
        pad=' '*(len(req[1])+8);j=i+3
        while j<len(lines) and lines[j].strip()!='end note':
            if lines[j] and not lines[j].startswith(pad):errors.append('permission SQL must preserve exact added note prefix and native whitespace')
            j+=1
    for _,h,_ in ops:
        if wsd.count('app -> infra: '+h+'\n')!=(2 if h in (heads[5],heads[7],heads[8]) else 1):errors.append(f'{h} Application request count incorrect')
    for mat in re.finditer(r'(?m)^( *)infra -> (\w+): ((?:QUERY|INSERT|UPDATE) - [^\n]+)\n',wsd):
        r=re.search(rf'{mat[2]} -> infra: Return ([^\n]+)\n.*?deactivate {mat[2]}\n\s*infra -> app: Return ([^\n]+)',wsd[mat.start():],re.S)
        if not r or r[1]!=r[2]:errors.append('every permission SQL result must map back identically to Application')
    for n in ('Verify JWT signature/issuer/audience/expiry/UUID sub and the roles claim as unique non-empty strings','callerUserId = verified sub; accessTokenHash = SHA-256 exact JWT','Capture fresh server UTC now after caller lock; recheck JWT exp','JWT expired while waiting for caller lock','Current token/user missing/inactive/revoked/expired/mismatched','Authorize only exact case-sensitive PLATFORM_ADMIN in verified JWT roles; never reload live caller grants','activeScopeIds = only requested ACTIVE child scopeIds','permissionScopeIds = supplied child ids','Q23 skip master ACTIVE validation for removing an existing definition','Child absent from owned non-DELETED definition map','Requested scopeId differs from stored immutable scopeId','beforeDefinitionCount = definitionCount','Parent UPDATE returned zero rows','Require exactly one returned parent id equal to request id','permissionId = actual parent RETURNING id; bind this server-derived id for all child writes and final queries','Child UPDATE returned zero rows','Require exactly one returned child id equal to input id','finalDefinitionCount = definitionCount','alt beforeDefinitionCount > 0 and finalDefinitionCount = 0 (Q22 transition)','Either fresh non-DELETED role/direct-user grant survives','Q22 does not prohibit existing unscoped grants','data = exactly permissionId from parent RETURNING; no child ids or audit fields','Suppress body/status/data for 204'):
        if n not in wsd:errors.append(f'permission sequence missing {n!r}')
    phase=['Authorize only exact',heads[3],heads[4],'loop Validate every supplied','beforeDefinitionCount =',heads[6],'loop Precheck every supplied','alt Parent id omitted (INSERT','permissionId = actual parent RETURNING','loop Apply every supplied','finalDefinitionCount =',q24,passed,'alt beforeDefinitionCount > 0']
    positions=[wsd.find(x) for x in phase]
    if -1 in positions or positions!=sorted(set(positions)):errors.append('permission authorization/preflight/count/write/final-guard phases are out of order')
    q23=re.search(r'(?m)^( *)alt Child rowStatus = ACTIVE\n(.*?)^\1else Child rowStatus = DELETED\n(.*?)^\1end\n',wsd,re.S)
    if not q23 or 'Requested master absent from ACTIVE master map' not in q23[2] or 'Q23 skip master ACTIVE' not in q23[3] or 'HTTP 404 E10005' in q23[3]:errors.append('ACTIVE master validation belongs only to ACTIVE link branch; deletion must allow closed masters')
    # Traverse one representative pass through each child phase. Structural paths do not certify concrete multi-item inputs.
    flat=[];stack=[];note=False;loop_ranges=[];loop_starts=[]
    for i,l in enumerate(lines):
        t=l.strip()
        if t.startswith('note ') and ':' not in t:note=True
        if note:
            flat.append(l)
            if t=='end note':note=False
            continue
        if t.startswith('loop '):stack.append('loop');loop_starts.append(i);continue
        if t.startswith('alt '):stack.append('alt')
        elif t in ('end','end alt'):
            if not stack:errors.append('permission loop/alternative unbalanced');continue
            kind=stack.pop()
            if kind=='loop':loop_ranges.append((loop_starts.pop(),i));continue
        flat.append(l)
    if stack or len(loop_ranges)!=3:errors.append('permission needs three complete scope validation/precheck/mutation loops')
    for start,end in loop_ranges:
        if any('app -> infra: COMMIT' in x or 'app -> api: HTTP 20' in x for x in lines[start:end]):errors.append('no scope phase can commit/answer partial success')
    for response in re.finditer(r'(?m)^( *)app -> api: HTTP [^\n]+\n',wsd):
        following=wsd[response.end():].splitlines()[:2]
        if len(following)!=2 or not following[0].strip().startswith('api -> page:') or not following[1].strip().startswith('page -> user:'):errors.append('every permission response must reach frontend/caller')
    traces,structure=login_sequence_paths('\n'.join(flat));errors+=structure;codes=set()
    for tr in traces:
        response=[e for e in tr if e.startswith('app -> api: HTTP ')];joined='\n'.join(tr)
        if len(response)!=1:errors.append('permission structural trace must terminate exactly once');continue
        code=int(response[0].split('HTTP ')[1].split()[0]);codes.add(code);db=[e for e in tr if e.startswith('infra -> ')];begun=any(e.startswith('app -> infra: BEGIN') for e in tr)
        def ordered(*parts):
            pos=[next((i for i,e in enumerate(tr) if p in e),-1) for p in parts]
            return -1 not in pos and pos==sorted(set(pos))
        def hasop(h):return any(e.endswith(': '+h) for e in db)
        if db and not ordered('Verify JWT','callerUserId = verified sub','BEGIN READ COMMITTED',heads[0]):errors.append('permission SQL requires verified caller and user-first transaction')
        if heads[1] in joined and not ordered(heads[0],'Capture fresh server UTC now',heads[1]):errors.append('current credential query must follow caller lock and fresh time')
        if hasop(heads[2]) and not ordered(heads[1],heads[2]):errors.append('parent existence requires current credentials first')
        if 'Authorize only exact' in joined and not ordered(heads[1],*([heads[2]] if hasop(heads[2]) else []),'Authorize only exact'):errors.append('permission claims follow current credential/optional parent existence')
        if heads[3] in joined and not ordered('Authorize only exact',heads[3],heads[4]):errors.append('no scope query before authorization and declared master/link lock order')
        parentwrites=[e for e in db if e.endswith('INSERT - Create permission') or e.endswith('UPDATE - Update or delete permission')];childwrites=[e for e in db if ': INSERT - Create permission scope' in e or ': UPDATE - Update or delete permission scope' in e]
        if parentwrites and not ordered(heads[9],parentwrites[0]):errors.append('all scope duplicate prechecks precede parent mutation')
        if childwrites and not ordered('permissionId = actual parent RETURNING',childwrites[0]):errors.append('scope writes require the real returned parent id')
        if code in (200,201,204):
            if len(parentwrites)!=1 or len(childwrites)!=1 or not ordered('beforeDefinitionCount =',parentwrites[0],childwrites[0],'finalDefinitionCount =',passed,'app -> infra: COMMIT',f'HTTP {code}') or 'ROLLBACK' in joined:errors.append('permission success must complete atomic parent/child/final-count phases then commit')
            if code==204:
                if 'Suppress body/status/data for 204' not in joined or 'data = exactly permissionId' in joined:errors.append('permission delete has no response body')
            elif not ordered('data = exactly permissionId','app -> infra: COMMIT'):errors.append('nondelete success maps only parent permissionId before commit')
        elif begun:
            if not ordered('BEGIN','ROLLBACK',f'HTTP {code}') or 'app -> infra: COMMIT' in joined:errors.append('every post-BEGIN permission rejection rolls back the whole request')
            if code==401 and (hasop(heads[2]) or heads[3] in joined):errors.append('invalid current credentials must not inspect parents/scopes')
            if code==403 and any(h in joined for h in heads[3:]):errors.append('403 must precede every scope/conflict/write phase')
        elif code not in (400,401) or db:errors.append('pre-BEGIN permission rejection is validation/JWT only, no SQL')
        if 'finalDefinitionCount =' in joined and passed in joined and 'Q22 does not prohibit existing unscoped grants' not in joined:
            final=next(i for i,e in enumerate(tr) if 'finalDefinitionCount =' in e);tail='\n'.join(tr[final:])
            if heads[7] not in tail or heads[8] not in tail:errors.append('Q22 must freshly read both role/direct-user grants after the final count')
        if 'HTTP 409 E10006 Permission cannot be deleted while scope definitions remain.' in joined and not ordered('finalDefinitionCount =','ROLLBACK','HTTP 409'):errors.append('Q24 rejection must follow final count and roll back before response')
    if codes!={200,201,204,400,401,403,404,409,408,500}:errors.append(f'permission outcome coverage incomplete: {codes}')
    for title,code in {'Success - Insert':201,'Success - Update':200,'Success - Archive':200,'Fail - Bad Request Scope Changed':400,'Fail - Not Found Permission Scope':404,'Fail - Conflict Scope':409,'Fail - Conflict Last Scope':409,'Fail - Conflict Remaining Scopes':409,'Fail - Internal Server Error':500}.items():
        try:
            obj=author_json(md,title);status=obj['status']
            if status['code']!=code or code==500 and 'bizCode' in status:errors.append(f'{title} permission envelope incorrect')
            if code in (200,201) and set(obj['data'])!={'permissionId'}:errors.append('permission response must not add scope ids/other fields')
            if title=='Fail - Conflict Remaining Scopes' and (status.get('bizCode')!='E10006' or status['bizMessage']!='Permission cannot be deleted while scope definitions remain.'):errors.append('Q24 error must be 409 E10006 with the documented message')
            if title=='Fail - Conflict Last Scope' and (status.get('bizCode')!='E10006' or status['bizMessage']!='Permission cannot become unscoped while assigned to roles or users.'):errors.append('Q22 error must be 409 E10006 with the documented message')
        except (AttributeError,TypeError,KeyError,ValueError):errors.append(f'missing/malformed permission example {title}')
    delete=re.search(r'^##### Delete\n\n```JSON\n(.*?)```',md,re.M|re.S)
    try:
        body=json.loads(delete[1]);assert body.get('rowStatus')=='DELETED' and body.get('scopes') and all(c.get('id') and c.get('rowStatus')=='DELETED' for c in body['scopes'])
    except (AssertionError,TypeError,KeyError,ValueError):errors.append('Q24 Delete example must explicitly withdraw its remaining definitions')
    errors+=json_blocks_parse(md);errors+=table_lines_aligned(md)
    if '--rendered-svg' in sys.argv:
        import xml.etree.ElementTree as ET
        try:
            root=ET.parse(sys.argv[sys.argv.index('--rendered-svg')+1]).getroot();wanted=Counter(' '.join(l.split()) for _,_,q in actual for l in q.splitlines() if l.strip());visible=Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'));missing=wanted-visible
            if missing:errors.append(f'rendered permission-upsert SQL missing {sum(missing.values())} lines')
            else:print(f'OK: rendered permission-upsert SQL ({sum(wanted.values())}/{sum(wanted.values())} visible lines)')
        except (IndexError,OSError,ET.ParseError) as exc:errors.append(f'cannot verify permission SVG: {exc}')
    if errors:return fail('; '.join(dict.fromkeys(errors)))
    print('OK: permission-upsert-flow (16 exact SQL definitions; scope phase/transaction structure and owner Q22/Q23/Q24 guards)')
    return 0


COMMANDS['permission-upsert-flow'] = check_permission_upsert_flow


def check_permission_batch_flow() -> int:
    """Check scoped permission parent/link phases, owner Q22/Q23/Q24 and atomic rollback."""
    path=f'{AUTHOR_DIR}/{AUTHOR_SPECS["05"]}/spec.md';md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    for n in ('status: in-review', 'approved_by: null', 'approved_at: null', 'Q22/Q23 (approved by the product owner)'):
        if n not in md:errors.append(f'permission batch spec missing {n!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for n in ('permissions must be an array of 1..100', 'Reject duplicate parsed canonical parent ids',
            'malformed/missing roles is generic 401', 'Lock order: caller user -> all existing target permissions ordered by id',
            'Check all supplied target ids in original request order before permission', 'Authorize once from exact PLATFORM_ADMIN',
            'activeScopeIds contains only scopeIds requested ACTIVE anywhere', 'Map each returned child id to its stored permission_id and scope_id',
            'optional permissions.id, callerUserId and derived permissionId are distinct', 'scopes omitted or [] means no link change',
            'Every child precheck precedes the current parent', 'Capture beforeDefinitionCount as every non-DELETED definition',
            'beforeDefinitionCount > 0 and finalDefinitionCount = 0',
            "Because parent ids cannot repeat and child ownership is enforced, this post-item state is that permission's final whole-request state; no later item may alter its definitions.",
            'exactly index/permissionId/action', 'one COMMIT after the outer loop', 'Every item-specific 400/404/409 has permissions[i] prefix',
            'uq_m_permission_name', 'uq_t_permission_scope_permission_id_scope_id', 'ใช่ ปฏิเสธจนถอน grant เดิมครบ', 'ใช่ อนุญาตถอน link ของ scope ที่ปิดแล้ว'):
        if n not in seq:
            errors.append(f'permission batch sequence note missing {n!r}')
    for n in ('QUERY - Get the platform administrator role','QUERY - Check platform administrator'):
        if n in md or n in wsd:errors.append('permission caller authorization may not reload live grants')
    if 'Q24 approved by the product owner' not in ' '.join(wsd.split()) or 'rowStatus = DELETED and finalDefinitionCount > 0' not in ' '.join(wsd.split()):errors.append('permission batch sequence note must define owner Q24 final deletion guard')
    q24='alt Current permission rowStatus = DELETED and finalDefinitionCount > 0 (Q24)'
    passed='Q24 passed for permissions[i]: rowStatus is not DELETED or finalDefinitionCount = 0'
    if q24 not in wsd or passed not in wsd:errors.append('permission batch sequence must enforce Q24 after final count')
    block=re.search(r'(?m)^( *)'+re.escape(q24)+r'\n(.*?)^\1else Q24 passed\n(.*?)^\1end\n',wsd,re.S)
    if not block or 'app -> infra: ROLLBACK' not in block[2] or 'HTTP 409 E10006 permissions[i]: Permission cannot be deleted while scope definitions remain.' not in block[2] or passed not in block[3]:errors.append('Q24 batch branch must reject with exact indexed 409 E10006 and full rollback, otherwise pass explicitly')
    ops=spec_database_operations(md);heads=('QUERY - Lock the caller user','QUERY - Check current credential and user','QUERY - Lock existing permissions','QUERY - Check scope','QUERY - Check existing permission scope','QUERY - Count permission scope definitions','QUERY - Check duplicate name','QUERY - Check role permission in use','QUERY - Check user permission in use','QUERY - Check duplicate permission scope','QUERY - Check role permission scope in use','QUERY - Check user permission scope in use','INSERT - Create permission','UPDATE - Update or delete permission','INSERT - Create permission scope','UPDATE - Update or delete permission scope')
    if tuple(h for _,h,_ in ops)!=heads:errors.append('permission needs all 16 caller/parent/master/link/count/conflict/write definitions')
    sql={h:re.sub(r'--[^\n]*','',q) for _,h,q in ops};need={
        heads[0]:["WHERE u.id = '<sequence.callerUserId>'",'FOR UPDATE'],heads[1]:['JOIN authen.m_user u ON u.id = at.user_id',"at.token = '<sequence.accessTokenHash>'","at.user_id = '<sequence.callerUserId>'","at.row_status = 'ACTIVE'","at.expired_at > '<sequence.now>'","u.row_status = 'ACTIVE'"],
        heads[2]:["WHERE p.id = ANY ('<sequence.targetPermissionIds>'::UUID[])","AND p.row_status <> 'DELETED'",'ORDER BY p.id\nFOR UPDATE'],heads[3]:["WHERE s.id = ANY ('<sequence.activeScopeIds>'::UUID[])","AND s.row_status = 'ACTIVE'",'ORDER BY s.id\nFOR UPDATE'],heads[4]:['ps.permission_id','ps.scope_id',"WHERE ps.id = ANY ('<sequence.permissionScopeIds>'::UUID[])","AND ps.permission_id = ANY ('<sequence.targetPermissionIds>'::UUID[])","AND ps.row_status <> 'DELETED'",'ORDER BY ps.id\nFOR UPDATE'],
        heads[5]:['COUNT(ps.id) as definition_count',"WHERE ps.permission_id = '<sequence.permissionId>'","AND ps.row_status <> 'DELETED'"],heads[6]:["WHERE p.name = '<sequence.permissions.name>'","AND p.row_status <> 'DELETED'","AND ('<sequence.permissions.id>' IS NULL OR p.id <> '<sequence.permissions.id>')"],heads[7]:["WHERE rp.permission_id = '<sequence.permissionId>'","AND rp.row_status <> 'DELETED'"],heads[8]:["WHERE up.permission_id = '<sequence.permissionId>'","AND up.row_status <> 'DELETED'"],
        heads[9]:["WHERE ps.permission_id = '<sequence.permissionId>'","AND ps.scope_id = '<sequence.permissions.scopes.scopeId>'","AND ps.row_status <> 'DELETED'","AND ('<sequence.permissions.scopes.id>' IS NULL OR ps.id <> '<sequence.permissions.scopes.id>')"],heads[10]:["WHERE rps.permission_scope_id = '<sequence.permissions.scopes.id>'","AND rps.row_status <> 'DELETED'"],heads[11]:["WHERE up.permission_scope_id = '<sequence.permissions.scopes.id>'","AND up.row_status <> 'DELETED'"],
        heads[12]:['created_by,\n    created_at,','<sequence.createdBy>','<sequence.now>','<sequence.permissions.rowStatus>','<sequence.permissions.name>','<sequence.permissions.description>','RETURNING id as permission_id'],heads[13]:["updated_by = '<sequence.updatedBy>'","updated_at = '<sequence.now>'","row_status = '<sequence.permissions.rowStatus>'","WHERE id = '<sequence.permissions.id>'","AND row_status <> 'DELETED'",'RETURNING id as permission_id'],
        heads[14]:['created_by,\n    created_at,','<sequence.now>','<sequence.permissionId>','<sequence.permissions.scopes.scopeId>','<sequence.permissions.scopes.rowStatus>','RETURNING id as permission_scope_id'],heads[15]:["updated_by = '<sequence.updatedBy>'","updated_at = '<sequence.now>'","row_status = '<sequence.permissions.scopes.rowStatus>'","WHERE id = '<sequence.permissions.scopes.id>'","AND permission_id = '<sequence.permissionId>'","AND scope_id = '<sequence.permissions.scopes.scopeId>'","AND row_status <> 'DELETED'",'RETURNING id as permission_scope_id']}
    for h,ns in need.items():
        for n in ns:
            if n not in sql.get(h,''):errors.append(f'{h} missing {n!r}')
    if 'JOIN' in sql.get(heads[5],'') or "row_status = 'ACTIVE'" in sql.get(heads[5],''):errors.append('definition count must not lose closed definitions/masters')
    if 'NOW()' in '\n'.join(sql.values()) or any('created_at =' in sql.get(h,'') for h in heads[13::2]):errors.append('writes use bound fresh server time and preserve creation audit')
    actual,lifecycle=sequence_database_operations(wsd);errors+=lifecycle
    from collections import Counter
    expected=Counter((t.split('.')[-1],h,q) for t,h,q in ops)
    for t,h,q in ops:
        if h in (heads[5],heads[7],heads[8]):expected[(t.split('.')[-1],h,q)]+=1
    if Counter(actual)!=expected:errors.append('permission SQL differs character-for-character or has missing/excess repeated operations')
    lines=wsd.splitlines()
    for i,l in enumerate(lines):
        req=re.match(r'^( *)infra -> \w+: (?:QUERY|INSERT|UPDATE) - ',l)
        if not req:continue
        pad=' '*(len(req[1])+8);j=i+3
        while j<len(lines) and lines[j].strip()!='end note':
            if lines[j] and not lines[j].startswith(pad):errors.append('permission SQL must preserve exact added note prefix and native whitespace')
            j+=1
    for _,h,_ in ops:
        if wsd.count('app -> infra: '+h+'\n')!=(2 if h in (heads[5],heads[7],heads[8]) else 1):errors.append(f'{h} Application request count incorrect')
    for mat in re.finditer(r'(?m)^( *)infra -> (\w+): ((?:QUERY|INSERT|UPDATE) - [^\n]+)\n',wsd):
        r=re.search(rf'{mat[2]} -> infra: Return ([^\n]+)\n.*?deactivate {mat[2]}\n\s*infra -> app: Return ([^\n]+)',wsd[mat.start():],re.S)
        if not r or r[1]!=r[2]:errors.append('every permission SQL result must map back identically to Application')
    for n in ('Verify JWT signature/issuer/audience/expiry/UUID sub and the roles claim as unique non-empty strings', 'callerUserId = verified sub; accessTokenHash = SHA-256 exact JWT', 'Capture fresh server UTC now after caller lock; recheck JWT exp', 'JWT expired while waiting for caller lock', 'Current token/user missing/inactive/revoked/expired/mismatched', 'Check every supplied parent id in original input order before permission', 'Authorize once using only exact case-sensitive PLATFORM_ADMIN in verified JWT roles; never reload live caller grants', 'activeScopeIds = all requested ACTIVE child scopeIds', 'permissionScopeIds = all supplied child ids', 'Q23 skip master ACTIVE validation for removing an existing definition', 'Child absent from owned non-DELETED definition map', 'Requested scopeId differs from stored immutable scopeId', 'beforeDefinitionCount = definitionCount', 'Parent UPDATE returned zero rows', 'Require exactly one returned parent id equal to request id', 'permissionId = actual parent RETURNING id; bind this server-derived id for all child writes and final queries', 'Child UPDATE returned zero rows', 'Require exactly one returned child id equal to input id', 'finalDefinitionCount = definitionCount', 'alt beforeDefinitionCount > 0 and finalDefinitionCount = 0 (Q22 transition)', 'Either fresh non-DELETED role/direct-user grant survives', 'Q22 does not prohibit existing unscoped grants', 'Process permissions[i] in original request order, not lock order', 'Map exactly index=i, permissionId=actual parent RETURNING id', 'Require result count = input count, indices 0..n-1 in order, unique returned parent UUIDs and exactly index/permissionId/action per item; data = exactly permissions; finish all mapping', 'one final COMMIT'):
        if n not in wsd:errors.append(f'permission batch sequence missing {n!r}')
    phase=[heads[0],heads[1],heads[2],'loop Check every supplied parent id','Authorize once using only exact',heads[3],heads[4],'loop Process permissions[i]','loop Validate every supplied','beforeDefinitionCount =',heads[6],'loop Precheck every supplied','alt Parent id omitted (INSERT','permissionId = actual parent RETURNING','loop Apply every supplied','finalDefinitionCount =',q24,passed,'alt beforeDefinitionCount > 0']
    positions=[wsd.find(x) for x in phase]
    if -1 in positions or positions!=sorted(set(positions)):errors.append('permission authorization/preflight/count/write/final-guard phases are out of order')
    q23=re.search(r'(?m)^( *)alt Child rowStatus = ACTIVE\n(.*?)^\1else Child rowStatus = DELETED\n(.*?)^\1end\n',wsd,re.S)
    if not q23 or 'Requested master absent from ACTIVE master map' not in q23[2] or 'Q23 skip master ACTIVE' not in q23[3] or 'HTTP 404 E10005' in q23[3]:errors.append('ACTIVE master validation belongs only to ACTIVE link branch; deletion must allow closed masters')
    # Traverse one representative pass through each loop (not a concrete multi-item proof). Structural paths do not certify concrete multi-item inputs.
    flat=[];stack=[];note=False;loop_ranges=[];loop_starts=[]
    for i,l in enumerate(lines):
        t=l.strip()
        if t.startswith('note ') and ':' not in t:note=True
        if note:
            flat.append(l)
            if t=='end note':note=False
            continue
        if t.startswith('loop '):stack.append('loop');loop_starts.append(i);continue
        if t.startswith('alt '):stack.append('alt')
        elif t in ('end','end alt'):
            if not stack:errors.append('permission loop/alternative unbalanced');continue
            kind=stack.pop()
            if kind=='loop':loop_ranges.append((loop_starts.pop(),i));continue
        flat.append(l)
    if stack or len(loop_ranges)!=5:errors.append('permission needs five complete target/permission/child loops')
    for start,end in loop_ranges:
        if any('app -> infra: COMMIT' in x or 'app -> api: HTTP 20' in x for x in lines[start:end]):errors.append('no scope phase can commit/answer partial success')
    for response in re.finditer(r'(?m)^( *)app -> api: HTTP [^\n]+\n',wsd):
        following=wsd[response.end():].splitlines()[:2]
        if len(following)!=2 or not following[0].strip().startswith('api -> page:') or not following[1].strip().startswith('page -> user:'):errors.append('every permission response must reach frontend/caller')
    traces,structure=login_sequence_paths('\n'.join(flat));errors+=structure;codes=set()
    for tr in traces:
        response=[e for e in tr if e.startswith('app -> api: HTTP ')];joined='\n'.join(tr)
        if len(response)!=1:errors.append('permission structural trace must terminate exactly once');continue
        code=int(response[0].split('HTTP ')[1].split()[0]);codes.add(code);db=[e for e in tr if e.startswith('infra -> ')];begun=any(e.startswith('app -> infra: BEGIN') for e in tr)
        def ordered(*parts):
            pos=[next((i for i,e in enumerate(tr) if p in e),-1) for p in parts]
            return -1 not in pos and pos==sorted(set(pos))
        def hasop(h):return any(e.endswith(': '+h) for e in db)
        if db and not ordered('Verify JWT','callerUserId = verified sub','BEGIN READ COMMITTED',heads[0]):errors.append('permission SQL requires verified caller and user-first transaction')
        if heads[1] in joined and not ordered(heads[0],'Capture fresh server UTC now',heads[1]):errors.append('current credential query must follow caller lock and fresh time')
        if hasop(heads[2]) and not ordered(heads[1],heads[2]):errors.append('parent existence requires current credentials first')
        if 'Authorize once using only exact' in joined and not ordered(heads[1],*([heads[2]] if hasop(heads[2]) else []),'Authorize once using only exact'):errors.append('permission claims follow current credential/optional parent existence')
        if heads[3] in joined and not ordered('Authorize once using only exact',heads[3],heads[4]):errors.append('no scope query before authorization and declared master/link lock order')
        parentwrites=[e for e in db if e.endswith('INSERT - Create permission') or e.endswith('UPDATE - Update or delete permission')];childwrites=[e for e in db if ': INSERT - Create permission scope' in e or ': UPDATE - Update or delete permission scope' in e]
        if parentwrites and not ordered(heads[9],parentwrites[0]):errors.append('all scope duplicate prechecks precede parent mutation')
        if childwrites and not ordered('permissionId = actual parent RETURNING',childwrites[0]):errors.append('scope writes require the real returned parent id')
        if code==200:
            if len(parentwrites)!=1 or len(childwrites)!=1 or not ordered('beforeDefinitionCount =',parentwrites[0],childwrites[0],'finalDefinitionCount =',passed,'Map exactly index=i','Require result count = input count','app -> infra: COMMIT','HTTP 200') or 'ROLLBACK' in joined:errors.append('batch success must finish all nested writes/final-count/mapping phases before one outer commit')
            if sum('app -> infra: COMMIT' in e for e in tr)!=1:errors.append('batch commits exactly once')
        elif begun:
            if not ordered('BEGIN','ROLLBACK',f'HTTP {code}') or 'app -> infra: COMMIT' in joined:errors.append('every post-BEGIN permission rejection rolls back the whole request')
            if code==401 and (hasop(heads[2]) or heads[3] in joined):errors.append('invalid current credentials must not inspect parents/scopes')
            if code==403 and any(h in joined for h in heads[3:]):errors.append('403 must precede every scope/conflict/write phase')
        elif code not in (400,401) or db:errors.append('pre-BEGIN permission rejection is validation/JWT only, no SQL')
        if 'finalDefinitionCount =' in joined and passed in joined and 'Q22 does not prohibit existing unscoped grants' not in joined:
            final=next(i for i,e in enumerate(tr) if 'finalDefinitionCount =' in e);tail='\n'.join(tr[final:])
            if heads[7] not in tail or heads[8] not in tail:errors.append('Q22 must freshly read both role/direct-user grants after the final count')
        if 'HTTP 409 E10006 permissions[i]: Permission cannot be deleted while scope definitions remain.' in joined and not ordered('finalDefinitionCount =','ROLLBACK','HTTP 409'):errors.append('Q24 rejection must follow final count and roll back before indexed response')
    if codes!={200,400,401,403,404,409,408,500}:errors.append(f'permission outcome coverage incomplete: {codes}')
    for title,code in {'Success':200,'Fail - Forbidden':403,'Fail - Bad Request Scope Changed':400,'Fail - Not Found Permission Scope':404,'Fail - Conflict Scope':409,'Fail - Conflict Last Scope':409,'Fail - Conflict Remaining Scopes':409,'Fail - Internal Server Error':500}.items():
        try:
            obj=author_json(md,title);status=obj['status']
            if status['code']!=code or code==500 and 'bizCode' in status:errors.append(f'{title} permission batch envelope incorrect')
            if code==200:
                results=obj['data']['permissions']
                if set(obj['data'])!={'permissions'} or not results or any(set(r)!={'index','permissionId','action'} or r['index']!=i or r['action'] not in ('INSERT','UPDATE','DELETE','ARCHIVE') for i,r in enumerate(results)):errors.append('batch result must contain ordered index/permissionId/action only')
            elif code in (400,404,409) and not status['bizMessage'].startswith('permissions['):errors.append('item error requires permissions[i] prefix')
            elif code==403 and 'permissions[' in status['bizMessage']:errors.append('caller permission error must not have an item index')
            if title=='Fail - Conflict Remaining Scopes' and (status.get('bizCode')!='E10006' or status['bizMessage']!='permissions[1]: Permission cannot be deleted while scope definitions remain.'):errors.append('Q24 error must be indexed 409 E10006 with documented message')
            if title=='Fail - Conflict Last Scope' and (status.get('bizCode')!='E10006' or status['bizMessage']!='permissions[1]: Permission cannot become unscoped while assigned to roles or users.'):errors.append('Q22 error must be indexed 409 E10006 with documented message')
        except (AttributeError,TypeError,KeyError,ValueError):errors.append(f'missing/malformed permission batch example {title}')
    if wsd.count('app -> infra: COMMIT')!=1 or 'app -> api: HTTP 201' in wsd or 'app -> api: HTTP 204' in wsd:errors.append('batch has one 200 success and one final commit only')
    for line in wsd.splitlines():
        if re.search(r'app -> api: HTTP (404|409) ',line) and 'permissions[i]:' not in line:errors.append('every item not-found/conflict is indexed')
    example=re.search(r'^#### Example Body Parameters\n\n```JSON\n(.*?)```',md,re.M|re.S)
    try:
        body=json.loads(example[1]);deletes=[p for p in body['permissions'] if p.get('rowStatus')=='DELETED']
        assert deletes and all(p.get('id') and p.get('scopes') and all(c.get('id') and c.get('rowStatus')=='DELETED' for c in p['scopes']) for p in deletes)
        # The HTTP and cURL examples must show the same complete withdrawal as the JSON example.
        for p in deletes:
            for c in p['scopes']:
                assert md.count('"id": "'+c['id']+'"')==3
        raw=body['permissions'];http=re.search(r'```HTTP\n.*?\n\n(.*?)```',md,re.S);curl=re.search(r"--data(?:-raw)? '(.*?)'",md,re.S)
        assert http and curl and json.loads(http[1])['permissions']==raw and json.loads(curl[1])['permissions']==raw
    except (AssertionError,TypeError,KeyError,ValueError):errors.append('Q24 batch Delete examples must consistently withdraw remaining definitions in JSON, HTTP and cURL')
    errors+=json_blocks_parse(md);errors+=table_lines_aligned(md)
    if '--rendered-svg' in sys.argv:
        import xml.etree.ElementTree as ET
        try:
            root=ET.parse(sys.argv[sys.argv.index('--rendered-svg')+1]).getroot();wanted=Counter(' '.join(l.split()) for _,_,q in actual for l in q.splitlines() if l.strip());visible=Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'));missing=wanted-visible
            if missing:errors.append(f'rendered permission-batch SQL missing {sum(missing.values())} lines')
            else:print(f'OK: rendered permission-batch SQL ({sum(wanted.values())}/{sum(wanted.values())} visible lines)')
        except (IndexError,OSError,ET.ParseError) as exc:errors.append(f'cannot verify permission SVG: {exc}')
    if errors:return fail('; '.join(dict.fromkeys(errors)))
    print('OK: permission-batch-flow (16 exact SQL definitions; batch lock/order/atomic-result structure and owner Q22/Q23/Q24 guards)')
    return 0

COMMANDS['permission-batch-flow'] = check_permission_batch_flow


def check_permission_inquiry_flow() -> int:
    """Check token-claim administration and consistent filtered current role metadata."""
    path=f'{AUTHOR_DIR}/{AUTHOR_SPECS["06"]}/spec.md';md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    for n in ('status: in-review', 'approved_by: null', 'approved_at: null'):
        if n not in md:errors.append(f'permission-inquiry spec missing {n!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for n in ('2026-11-07-api-review-design.md', 'exact PLATFORM_ADMIN in verified JWT role claims', 'positive signed 64-bit integers', 'nonnegative BIGINT',
            'one bound text searchPattern', 'Missing/malformed roles is generic 401', 'Grant withdrawal after token issuance leaves the old privilege usable',
            'Count first and optionally fetch the page in the same read-only repeatable-read snapshot',
            'identical non-DELETED/id/searchPattern/rowStatus WHERE predicates', 'an offset beyond the range returns items=[] with positive totals/pages',
            'Sort by name then id ascending', 'exactly permissionId/name/description/scopes/rowStatus', 'exactly five data keys', 'integer quotient/remainder',
            'Map the full response before COMMIT', 'distinct UUID[] of that page', 'An empty page skips both definition and master queries',
            'A page with no definitions maps scopes=[]', 'including INACTIVE/LOCKED/ARCHIVED/DELETED masters', 'Metadata is matched by immutable scope_id',
            'exactly permissionScopeId/scopeId/scope/scopeName/rowStatus', "rowStatus is the definition's status", 'derive master rank',
            'Credential/count/page/definition/master SELECTs share the same read-only repeatable-read snapshot', 'No per-permission or per-scope SQL queries'):
        if n not in seq:
            errors.append(f'permission-inquiry sequence note missing {n!r}')
    for n in ('QUERY - Get the platform administrator role','QUERY - Check platform administrator'):
        if n in md or n in wsd:errors.append('permission inquiry authorization must not reload current assignments')
    ops=spec_database_operations(md);heads=('QUERY - Check current credential and user','QUERY - Get total items','QUERY - Get permissions','QUERY - Get the scopes of the permissions','QUERY - Get scope')
    if tuple(h for _,h,_ in ops)!=heads:errors.append('permission inquiry needs credential/count/page in declared order')
    sql={h:re.sub(r'--[^\n]*','',s) for _,h,s in ops};filters=["WHERE p.row_status <> 'DELETED'","AND ('<sequence.id>' IS NULL OR p.id = '<sequence.id>')","AND ('<sequence.searchPattern>' IS NULL OR p.name ILIKE '<sequence.searchPattern>' OR p.description ILIKE '<sequence.searchPattern>')","AND ('<sequence.rowStatus>' IS NULL OR p.row_status = '<sequence.rowStatus>')"]
    required={heads[0]:['JOIN authen.m_user u ON u.id = at.user_id',"at.token = '<sequence.accessTokenHash>'","at.user_id = '<sequence.callerUserId>'","at.row_status = 'ACTIVE'","at.expired_at > '<sequence.now>'","u.row_status = 'ACTIVE'"],heads[1]:filters+['COUNT(p.id) as total_items'],heads[2]:filters+["LIMIT '<sequence.pageSize>' OFFSET '<sequence.offset>'"]}
    required[heads[1]]+=['FROM author.m_permission p']
    required[heads[2]]+=['FROM author.m_permission p']
    required[heads[3]]=['FROM author.t_permission_scope ps',"WHERE ps.permission_id = ANY ('<sequence.permissionIds>'::UUID[])","AND ps.row_status <> 'DELETED'",'ORDER BY ps.permission_id, ps.id']
    required[heads[4]]=['FROM author.m_scope s',"WHERE s.id = ANY ('<sequence.scopeIds>'::UUID[])",'ORDER BY s.scope, s.id']
    for h,ns in required.items():
        for n in ns:
            if n not in sql.get(h,''):errors.append(f'{h} missing {n!r}')
    def where(h):
        r=re.search(r'\bWHERE\b(.*?)(?:\bORDER BY\b|\bLIMIT\b|$)',sql.get(h,''),re.S);return normalize(r[1]) if r else None
    if where(heads[1])!=where(heads[2]):errors.append('permission count/page WHERE predicates must be identical')
    if any(where(h)!=normalize(' '.join(filters).removeprefix('WHERE ')) for h in heads[1:3]):errors.append('permission count/page must use only the four declared lifecycle/nullable predicates')
    projection=re.search(r'SELECT\s+(.*?)\s+FROM\s',sql.get(heads[2],''),re.S)
    if not projection or normalize(projection[1])!=normalize('p.id as permission_id, p.name, p.description, p.row_status'):errors.append('permission page returns exactly four permission fields, no audit/assignment/caller data')
    if not re.search(r"ORDER BY p\.name, p\.id(?: ASC)?\s+LIMIT",sql.get(heads[2],'')):errors.append('permission page requires name then unique ascending id order')
    if SEQUENCE_LOCK.search('\n'.join(sql.values())) or 'NOW()' in '\n'.join(sql.values()) or any(not q.lstrip().startswith('SELECT') for q in sql.values()):errors.append('permission inquiry must use SELECT-only fresh-bound credential time, with no locks')
    for h,expected_where,expected_projection in [(heads[3],"ps.permission_id = ANY ('<sequence.permissionIds>'::UUID[]) AND ps.row_status <> 'DELETED'",'ps.id as permission_scope_id, ps.permission_id, ps.scope_id, ps.row_status'),(heads[4],"s.id = ANY ('<sequence.scopeIds>'::UUID[])",'s.id as scope_id, s.scope, s.name')]:
        if where(h)!=normalize(expected_where):errors.append(f'{h} must use exact page/definition-derived ids without master/grant/status filtering')
        projection=re.search(r'SELECT\s+(.*?)\s+FROM\s',sql.get(h,''),re.S)
        if not projection or normalize(projection[1])!=normalize(expected_projection):errors.append(f'{h} projection must preserve exact parent/definition/master identity')
    actual,lifecycle=sequence_database_operations(wsd);errors+=lifecycle
    if actual!=[(t.split('.')[-1],h,q) for t,h,q in ops]:errors.append('permission inquiry SQL differs character-for-character or execution order')
    lines=wsd.splitlines()
    for i,l in enumerate(lines):
        req=re.match(r'^( *)infra -> \w+: QUERY - ',l)
        if not req:continue
        pad=' '*(len(req[1])+8);j=i+3
        while j<len(lines) and lines[j].strip()!='end note':
            if lines[j] and not lines[j].startswith(pad):errors.append('permission SQL must retain exact added presentation prefix and original SQL indentation')
            j+=1
    for _,h,_ in ops:
        if wsd.count('app -> infra: '+h+'\n')!=1:errors.append(f'{h} needs one Application request')
    for mat in re.finditer(r'(?m)^( *)infra -> (\w+): (QUERY - [^\n]+)\n',wsd):
        r=re.search(rf'{mat[2]} -> infra: Return ([^\n]+)\n.*?deactivate {mat[2]}\n\s*infra -> app: Return ([^\n]+)',wsd[mat.start():],re.S)
        if not r or r[1]!=r[2]:errors.append('role database result must return with the same meaning to Application')
    for n in ('Compute checked offset = (pageIndex - 1) * pageSize; reject numeric/offset overflow beyond nonnegative BIGINT', 'Verify JWT signature/issuer/audience/expiry/UUID sub and the roles claim as unique non-empty strings', 'callerUserId = verified sub; accessTokenHash = SHA-256 exact JWT', 'Bind omitted id/searchPattern/rowStatus as typed SQL NULL; supplied searchPattern = percent + search + percent, preserving ILIKE wildcards', 'Capture fresh server UTC now immediately before joined credential read; recheck JWT exp', 'JWT expired before fresh credential read', 'Missing/invalid JWT or malformed roles', 'Current token/user missing/inactive/revoked/expired/mismatched', 'alt totalItems = 0', 'Authorize once using exact case-sensitive PLATFORM_ADMIN in verified JWT roles; never reload current grants', 'No exact PLATFORM_ADMIN role claim', 'integer quotient plus nonzero remainder', 'items = []; skip page/definition/master queries; totalPages = 0', 'Require page row count = min(pageSize, max(0, totalItems-offset)); unique parent UUIDs and non-null required columns', 'Bind permissionIds as distinct typed UUID[] from returned page permission_id values only', 'Validate definition ids/parent membership/unique scopeId per parent/non-DELETED status', 'Bind scopeIds as distinct typed UUID[] from returned definition scope_id values', 'Require one exact master for every referenced scope_id', 'Build master rank from database scope-code/id order', 'never rebind by reused code', 'Prepare groups by permission_id, ordered by master rank then definition UUID', 'Set all page scopes=[]; skip master query', 'Map exactly permissionId/name/description/scopes/rowStatus', 'Map exactly permissionScopeId/scopeId/scope/scopeName/rowStatus', 'rowStatus comes from definition', 'items = []; retain positive totalItems/totalPages; skip definition/master queries; no 404', 'data = exactly items/pageIndex/pageSize/totalItems/totalPages; echo validated page values; explicit empty arrays; finish full nested mapping'):
        if n not in wsd:errors.append(f'permission inquiry sequence missing {n!r}')
    if wsd.count('Authorize once using exact')!=1:errors.append('permission inquiry checks claims permission exactly once')
    for response in re.finditer(r'(?m)^( *)app -> api: HTTP [^\n]+\n',wsd):
        following=wsd[response.end():].splitlines()[:2]
        if len(following)!=2 or not following[0].strip().startswith('api -> page:') or not following[1].strip().startswith('page -> user:'):errors.append('all permission inquiry responses must reach frontend and caller')
    # Mapping loops perform no SQL and are traversed once for structural checks only.
    flat=[];stack=[];note=False;loops=0
    for line in lines:
        t=line.strip()
        if t.startswith('note ') and ':' not in t:note=True
        if note:
            flat.append(line)
            if t=='end note':note=False
            continue
        if t.startswith('loop '):stack.append(('loop',len(flat)));loops+=1;continue
        if t.startswith('alt '):stack.append(('alt',len(flat)))
        elif t in ('end','end alt'):
            if not stack:errors.append('unbalanced permission mapping loop/branch');continue
            kind,start=stack.pop()
            if kind=='loop':
                if any('app -> infra:' in e or 'app -> api: HTTP' in e for e in flat[start:]):errors.append('mapping loops contain no SQL, commit or response')
                continue
        flat.append(line)
    if stack or loops!=2:errors.append('permission inquiry requires complete parent/definition mapping loops')
    traces,structure=login_sequence_paths('\n'.join(flat));errors+=structure
    from collections import Counter
    outcomes=[];modes=Counter();unauthorized=[]
    for tr in traces:
        response=[e for e in tr if e.startswith('app -> api: HTTP ')];joined='\n'.join(tr)
        if len(response)!=1:errors.append('permission inquiry trace needs one terminal outcome');continue
        code=int(response[0].split('HTTP ')[1].split()[0]);outcomes.append(code);queries=[e for e in tr if e.startswith('infra -> ')];begun=any(e.startswith('app -> infra: BEGIN') for e in tr)
        def ordered(*parts):
            pos=[next((i for i,e in enumerate(tr) if p in e),-1) for p in parts]
            return -1 not in pos and pos==sorted(set(pos))
        if queries and not ordered('Compute checked offset','Verify JWT','callerUserId = verified sub','Bind omitted id/searchPattern','BEGIN REPEATABLE READ READ ONLY','Capture fresh server UTC now',heads[0]):errors.append('permission SQL needs checked pagination, verified caller and fresh read-only credential snapshot')
        if 'Authorize once using exact' in joined and not ordered(heads[0],'Authorize once using exact'):errors.append('claims permission requires valid current credential')
        if heads[1] in joined and not ordered('Authorize once using exact',heads[1]):errors.append('no permission count may precede claims permission')
        if heads[2] in joined and not ordered(heads[1],heads[2]):errors.append('permission page must follow its identical-filter count')
        if heads[3] in joined and not ordered(heads[2],'Bind permissionIds',heads[3]):errors.append('definitions require exact returned page ids after the page query')
        if heads[4] in joined and not ordered(heads[3],'Bind scopeIds',heads[4],'Build master rank'):errors.append('master reads require exact definition ids and retain database rank')
        if any(': QUERY' not in e for e in queries):errors.append('permission inquiry may never write')
        if code==200:
            mode='zero' if 'skip page/definition/master queries' in joined else 'beyond' if 'retain positive totalItems' in joined else 'no_links' if 'Set all page scopes=[]' in joined else 'rows';modes[mode]+=1
            if len(queries)!={'zero':2,'beyond':3,'no_links':4,'rows':5}[mode]:errors.append('zero permission count skips page query; positive count queries page')
            if not ordered(heads[1],'data = exactly items','app -> infra: COMMIT','HTTP 200') or 'ROLLBACK' in joined:errors.append('success needs complete mapped read-only response then commit')
            if mode!='zero' and 'Require page row count' not in joined:errors.append('positive permission count must validate page cardinality')
            if 'all five pagination keys' not in response[0]:errors.append('permission inquiry success must include every pagination key')
        elif begun:
            if not ordered('BEGIN','ROLLBACK',f'HTTP {code}') or 'app -> infra: COMMIT' in joined:errors.append('permission inquiry transaction failures roll back before response')
            if code in (401,403) and len(queries)>1:errors.append('invalid credentials or non-admin must not count/read permissions')
        elif code not in (400,401) or queries:errors.append('pre-BEGIN permission inquiry reject must be no-SQL validation/JWT error')
        if code==401:unauthorized.append(len(queries))
    if Counter(outcomes)!=Counter({400:1,401:3,403:1,200:4,408:1,500:1}) or modes!=Counter({'zero':1,'rows':1,'beyond':1,'no_links':1}) or sorted(unauthorized)!=[0,0,1]:errors.append(f'expected 11 permission inquiry terminal traces, got {dict(Counter(outcomes))}, modes={dict(modes)},401 SQL={unauthorized}')
    for title,code in {'Success':200,'Success - By Id':200,'Success - Not Found':200,'Success - Page Beyond Range':200,'Success - Closed Scope Master':200,'Success - Non-Active Definition':200,'Fail - Bad Request':400,'Fail - Unauthorized':401,'Fail - Forbidden':403,'Fail - Request Timeout':408,'Fail - Internal Server Error':500}.items():
        try:
            obj=author_json(md,title);status=obj['status']
            if status['code']!=code or code==500 and 'bizCode' in status:errors.append(f'{title} permission inquiry envelope incorrect')
            if code==200:
                d=obj['data'];keys={'items','pageIndex','pageSize','totalItems','totalPages'}
                if set(d)!=keys or type(d['items']) is not list:errors.append(f'{title} needs five keys and items array');continue
                if any(type(d[k]) is not int for k in keys-{'items'}) or not 1<=d['pageIndex']<=2**63-1 or not 1<=d['pageSize']<=100 or d['totalItems']<0:errors.append(f'{title} invalid permission page integers');continue
                total=d['totalItems'];size=d['pageSize'];offset=(d['pageIndex']-1)*size;pages=total//size+int(total%size!=0)
                if offset>2**63-1 or d['totalPages']!=pages or len(d['items'])!=min(size,max(0,total-offset)):errors.append(f'{title} page cardinality/totals incorrect')
                ids=[]
                for item in d['items']:
                    if set(item)!={'permissionId','name','description','scopes','rowStatus'} or any(v is None for v in item.values()) or item['rowStatus']=='DELETED':errors.append(f'{title} permission fields missing/null/leaked/DELETED')
                    ids.append(item['permissionId'])
                    scopes=item.get('scopes');seen=set();pairs=set()
                    if type(scopes) is not list:errors.append(f'{title} requires scopes array');continue
                    for child in scopes:
                        if set(child)!={'permissionScopeId','scopeId','scope','scopeName','rowStatus'} or any(v is None for v in child.values()) or child['rowStatus'] not in ('ACTIVE','INACTIVE','LOCKED','ARCHIVED'):errors.append(f'{title} nested scope missing/null/leaked/status')
                        if child['permissionScopeId'] in seen or child['scopeId'] in pairs:errors.append(f'{title} duplicate scope definition/pair')
                        seen.add(child['permissionScopeId']);pairs.add(child['scopeId'])
                    if title=='Success - Closed Scope Master' and (not scopes or scopes[0]['rowStatus']!='ACTIVE'):errors.append('closed master example must preserve definition status')
                    if title=='Success - Non-Active Definition' and (not scopes or scopes[0]['rowStatus']!='INACTIVE'):errors.append('inactive definition example must remain visible')
                if len(ids)!=len(set(ids)):errors.append(f'{title} repeats permission id')
                if title=='Success - Page Beyond Range' and (not total or d['items'] or d['pageIndex']<=pages):errors.append('beyond-range role example must retain positive totals')
        except (AttributeError,TypeError,KeyError,IndexError,ValueError):errors.append(f'{title} permission inquiry example missing/malformed')
    errors+=json_blocks_parse(md);errors+=table_lines_aligned(md)
    if '--rendered-svg' in sys.argv:
        import xml.etree.ElementTree as ET
        try:
            root=ET.parse(sys.argv[sys.argv.index('--rendered-svg')+1]).getroot();wanted=Counter(' '.join(l.split()) for _,_,q in ops for l in q.splitlines() if l.strip());visible=Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'));missing=wanted-visible
            if missing:errors.append(f'rendered permission-inquiry SQL missing {sum(missing.values())} lines')
            else:print(f'OK: rendered permission-inquiry SQL ({sum(wanted.values())}/{sum(wanted.values())} visible lines)')
        except (IndexError,OSError,ET.ParseError) as exc:errors.append(f'cannot verify permission-inquiry SVG: {exc}')
    if errors:return fail('; '.join(errors))
    print('OK: permission-inquiry-flow (11 terminal traces; five exact SQL blocks, claim administration and consistent nested catalog mapping)')
    return 0

COMMANDS['permission-inquiry-flow'] = check_permission_inquiry_flow


def check_scope_upsert_flow() -> int:
    """Check verified-claim scope administration and guarded master/definition lifecycle."""
    path=f'{AUTHOR_DIR}/{AUTHOR_SPECS["07"]}/spec.md';md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    for n in ('status: in-review', 'approved_by: null', 'approved_at: null', 'Permission: only a platform administrator from the verified JWT roles claim',
            'exact case-sensitive role name PLATFORM_ADMIN'):
        if n not in md:errors.append(f'scope-upsert spec missing {n!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for n in ('Malformed/missing roles is generic 401', 'Grant withdrawal alone does not revoke', 'Capture fresh server UTC now after caller lock',
            'lock the non-DELETED scope FOR UPDATE', 'Duplicate scope exclusion is null-safe', 'Existing scope codes, including seed codes, remain editable',
            'Lock order is caller user -> target scope -> usage reads/write', "regardless of its parent permission's lifecycle",
            'No parent/master/grant JOIN or ACTIVE-only filter may hide usage', 'Insert-ARCHIVED is allowed', 'zero returned rows is 404 E10004',
            'exactly data.scopeId from RETURNING', 'SQLSTATE 23505 from uq_m_scope_scope'):
        if n not in seq:
            errors.append(f'scope-upsert sequence note missing {n!r}')
    for n in ('QUERY - Get the platform administrator role','QUERY - Check platform administrator'):
        if n in md or n in wsd:errors.append('scope upsert must not reload live caller grants')
    ops=spec_database_operations(md);heads=('QUERY - Lock the caller user','QUERY - Check current credential and user','QUERY - Check existing scope','QUERY - Check duplicate scope','QUERY - Check permission scope in use','INSERT - Create scope','UPDATE - Update or delete scope')
    if tuple(h for _,h,_ in ops)!=heads:errors.append('scope upsert needs all seven caller/target/conflict/write definitions')
    sql={h:re.sub(r'--[^\n]*','',q) for _,h,q in ops}
    need={heads[0]:['FROM authen.m_user u',"WHERE u.id = '<sequence.callerUserId>'",'FOR UPDATE'],heads[1]:['JOIN authen.m_user u ON u.id = at.user_id',"at.token = '<sequence.accessTokenHash>'","at.user_id = '<sequence.callerUserId>'","at.row_status = 'ACTIVE'","at.expired_at > '<sequence.now>'","u.row_status = 'ACTIVE'"],heads[2]:['FROM author.m_scope s',"WHERE s.id = '<sequence.id>'","AND s.row_status <> 'DELETED'",'FOR UPDATE'],heads[3]:['FROM author.m_scope s',"WHERE s.scope = '<sequence.scope>'","AND s.row_status <> 'DELETED'","AND ('<sequence.id>' IS NULL OR s.id <> '<sequence.id>')"],heads[4]:['FROM author.t_permission_scope ps',"WHERE ps.scope_id = '<sequence.id>'","AND ps.row_status <> 'DELETED'"],heads[5]:['created_by,\n    created_at,','<sequence.createdBy>','<sequence.now>','<sequence.rowStatus>','<sequence.scope>','<sequence.name>','<sequence.description>','RETURNING id as scope_id'],heads[6]:["updated_by = '<sequence.updatedBy>'","updated_at = '<sequence.now>'","row_status = '<sequence.rowStatus>'","scope = '<sequence.scope>'","name = '<sequence.name>'","description = '<sequence.description>'","WHERE id = '<sequence.id>'","AND row_status <> 'DELETED'",'RETURNING id as scope_id']}
    for h,ns in need.items():
        for n in ns:
            if n not in sql.get(h,''):errors.append(f'{h} missing {n!r}')
    usage=sql.get(heads[4],'')
    if 'JOIN' in usage or "row_status = 'ACTIVE'" in usage:errors.append('non-DELETED scope usage must not be hidden by parent/status joins')
    if 'NOW()' in '\n'.join(sql.values()) or 'created_at =' in sql.get(heads[6],''):errors.append('scope writes bind fresh server now and preserve creation audit')
    source=wsd.splitlines()
    for i,l in enumerate(source):
        match=re.match(r'^( *)infra -> \w+: (?:QUERY|INSERT|UPDATE) - ',l)
        if not match:continue
        pad=' '*(len(match[1])+8);j=i+3
        while j<len(source) and source[j].strip()!='end note':
            if source[j] and not source[j].startswith(pad):errors.append('scope SQL must preserve the exact note prefix/native indentation')
            j+=1
    actual,lifecycle=sequence_database_operations(wsd);errors+=lifecycle
    from collections import Counter
    expected=Counter((t.split('.')[-1],h,q) for t,h,q in ops)
    for t,h,q in ops:
        if h in (heads[3],heads[6]):expected[(t.split('.')[-1],h,q)]+=1
    if Counter(actual)!=expected:errors.append('scope-upsert SQL differs character-for-character or repeated occurrences are missing/excess')
    for _,h,_ in ops:
        if wsd.count('app -> infra: '+h+'\n')!=(2 if h in (heads[3],heads[6]) else 1):errors.append(f'{h} Application request count incorrect')
    for match in re.finditer(r'(?m)^( *)infra -> (\w+): ((?:QUERY|INSERT|UPDATE) - [^\n]+)\n',wsd):
        ret=re.search(rf'{match[2]} -> infra: Return ([^\n]+)\n.*?deactivate {match[2]}\n\s*infra -> app: Return ([^\n]+)',wsd[match.start():],re.S)
        if not ret or ret[1]!=ret[2]:errors.append('scope SQL return meaning must propagate intact to Application')
    for n in ('Verify JWT signature/issuer/audience/expiry/UUID sub and the roles claim as unique non-empty strings','callerUserId = verified sub; accessTokenHash = SHA-256 exact JWT; createdBy/updatedBy = caller UUID string; omitted id = typed SQL NULL','Capture fresh server UTC now after caller lock; recheck JWT exp','JWT expired while waiting for caller lock','Current token/user missing/inactive/revoked/expired/mismatched','Authorize only exact case-sensitive PLATFORM_ADMIN in verified JWT roles; never reload live grants','Any non-DELETED definition still references this scope','Guarded UPDATE returned zero rows','Require exactly one returned scope_id equal to requested id','Require exactly one inserted scope_id UUID','SQLSTATE 23505 from uq_m_scope_scope','data = exactly scopeId from RETURNING','Suppress response body/status/data for 204','Keep all definition/grant rows; code/name/description remain editable; old JWT claims stay unchanged'):
        if n not in wsd:errors.append(f'scope upsert sequence missing {n!r}')
    if wsd.count('alt Guarded UPDATE returned zero rows')!=2:errors.append('both existing scope UPDATE branches must handle zero rows')
    for response in re.finditer(r'(?m)^( *)app -> api: HTTP [^\n]+\n',wsd):
        tail=wsd[response.end():].splitlines()[:2]
        if len(tail)!=2 or not tail[0].strip().startswith('api -> page:') or not tail[1].strip().startswith('page -> user:'):errors.append('every scope response must reach frontend and caller')
    traces,structure=login_sequence_paths(wsd);errors+=structure;outcomes=[];unauthorized=[]
    for tr in traces:
        response=[e for e in tr if e.startswith('app -> api: HTTP ')];joined='\n'.join(tr)
        if len(response)!=1:errors.append('each scope structural trace must terminate once');continue
        code=int(response[0].split('HTTP ')[1].split()[0]);outcomes.append(code);db=[e for e in tr if e.startswith('infra -> ')];begun=any(e.startswith('app -> infra: BEGIN') for e in tr);writes=[e for e in db if ': INSERT' in e or ': UPDATE' in e];target=any(e.endswith(': '+heads[2]) for e in db)
        def ordered(*parts):
            pos=[next((i for i,e in enumerate(tr) if p in e),-1) for p in parts];return -1 not in pos and pos==sorted(set(pos))
        if db and not ordered('Verify JWT','callerUserId = verified sub','BEGIN READ COMMITTED',heads[0]):errors.append('scope SQL requires verified caller and caller-first transaction lock')
        if heads[1] in joined and not ordered(heads[0],'Capture fresh server UTC now',heads[1]):errors.append('scope credential check follows caller lock and fresh time')
        if target and not ordered(heads[1],heads[2]):errors.append('target scope existence requires current credentials first')
        if 'Authorize only exact' in joined:
            if not ordered(heads[1],*([heads[2]] if target else []),'Authorize only exact'):errors.append('claims permission follows current credentials and optional target existence')
            if sum('Authorize only exact' in e for e in tr)!=1:errors.append('scope authorizes exactly once per request')
        if heads[3] in joined and not ordered('Authorize only exact',heads[3]):errors.append('scope conflict checks follow caller permission')
        if heads[4] in joined and not ordered(heads[3],heads[4]):errors.append('scope usage follows duplicate check')
        if heads[4] in joined and heads[6] in joined and not ordered(heads[4],heads[6]):errors.append('existing destructive scope usage must be read before its UPDATE')
        if code in (200,201,204):
            if len(writes)!=1 or not ordered(heads[3],writes[0] if writes else 'MISSING','app -> infra: COMMIT',f'HTTP {code}') or 'ROLLBACK' in joined:errors.append('scope success requires one validated write then commit before response')
            if code==201:
                if target or heads[4] in joined or heads[6] in joined or heads[5] not in joined:errors.append('scope insert skips target/usage and only INSERTs')
            elif not target or heads[6] not in joined or heads[5] in joined:errors.append('existing scope success requires locked target and guarded UPDATE')
            if code!=201 and not ordered(heads[6],'Require exactly one returned scope_id equal to requested id','app -> infra: COMMIT'):errors.append('existing scope success must validate returned id')
            destructive=code==204 or 'Archive Scope Success' in response[0]
            if destructive!=(heads[4] in joined):errors.append('only existing delete/archive must check non-DELETED definitions')
            if code==204 and ('no response body' not in response[0] or 'data = exactly scopeId' in joined or 'Suppress response body/status/data for 204' not in joined):errors.append('scope delete must emit no body/status/data')
            if code!=204 and not ordered(heads[5] if code==201 else heads[6],'Require exactly one inserted scope_id UUID' if code==201 else 'Require exactly one returned scope_id equal to requested id','data = exactly scopeId','app -> infra: COMMIT'):errors.append('scope body must map only the validated returned id after its write and before commit')
        elif begun:
            if not ordered('BEGIN','ROLLBACK',f'HTTP {code}') or 'app -> infra: COMMIT' in joined:errors.append('all transactional scope errors roll back before response')
            if code in (401,403,409,408,500) and writes:errors.append('failed visible guard must not continue into a scope write')
            if code==401 and (target or heads[4] in joined):errors.append('bad credentials never inspect target/reference rows')
            if code==403 and any(h in joined for h in heads[3:]):errors.append('403 must precede conflicts and writes')
        elif code not in (400,401) or db:errors.append('scope pre-BEGIN failures are no-SQL validation/JWT only')
        if code==401:unauthorized.append(len(db))
    if Counter(outcomes)!=Counter({400:1,401:4,403:2,404:3,409:4,201:1,200:2,204:1,408:1,500:1}) or sorted(unauthorized)!=[0,1,1,2]:errors.append(f'expected 20 scope terminal traces, got {dict(Counter(outcomes))},401 SQL={unauthorized}')
    for title in ('Success - Insert','Success - Update','Success - Archive'):
        obj=author_json(md,title)
        if not obj or set(obj.get('data',{}))!={'scopeId'}:errors.append(f'{title} scope body must contain scopeId only')
    obj=author_json(md,'Fail - Internal Server Error')
    if not obj or obj['status']['code']!=500 or 'bizCode' in obj['status']:errors.append('scope internal error example is generic 500 without bizCode')
    obj=author_json(md,'Fail - Conflict In Use')
    if not obj or obj['status'].get('bizMessage')!='Scope is used by permissions.':errors.append('scope in-use response must preserve the contract message')
    errors+=json_blocks_parse(md);errors+=table_lines_aligned(md)
    if '--rendered-svg' in sys.argv:
        import xml.etree.ElementTree as ET
        try:
            root=ET.parse(sys.argv[sys.argv.index('--rendered-svg')+1]).getroot();wanted=Counter(' '.join(l.split()) for _,_,q in actual for l in q.splitlines() if l.strip());visible=Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'));missing=wanted-visible
            if missing:errors.append(f'rendered scope-upsert SQL missing {sum(missing.values())} lines')
            else:print(f'OK: rendered scope-upsert SQL ({sum(wanted.values())}/{sum(wanted.values())} visible lines)')
        except (IndexError,OSError,ET.ParseError) as exc:errors.append(f'cannot verify scope SVG: {exc}')
    if errors:return fail('; '.join(dict.fromkeys(errors)))
    print('OK: scope-upsert-flow (20 terminal traces; seven exact SQL definitions, claims/current credentials and guarded lifecycle)')
    return 0

COMMANDS['scope-upsert-flow'] = check_scope_upsert_flow


def check_scope_batch_flow() -> int:
    """Verify whole-batch preflight, sorted target locks before usage checks and ordered atomic scope mutations; unroll one representative item."""
    path=f'{AUTHOR_DIR}/{AUTHOR_SPECS["08"]}/spec.md';md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    for n in ('status: in-review', 'approved_by: null', 'approved_at: null', 'Validate the whole request before SQL', 'Compare parsed canonical UUIDs',
            'exact case-sensitive PLATFORM_ADMIN'):
        if n not in md:errors.append(f'scope-batch spec missing {n!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for n in ('all target existence checks', 'after all target existence checks and before any conflict or write', 'with one SELECT FOR UPDATE',
            'before any in-use check or write', 'any non-DELETED permission-scope definition is 409 E10006',
            'no parent/master/grant JOIN or ACTIVE-only filter may hide usage', 'Withdrawal of a grant alone does not invalidate',
            'first missing/DELETED target in original request order', "Each item's conflict reads see preceding item writes",
            'reversing those items returns duplicate 409', 'does not apply a final-state recode plan', 'exactly one result per input item in the same order',
            'batch never sends per-item 201/204 or partial success', 'SQLSTATE 23505', 'uq_m_scope_scope',
            'lock order is caller user -> target scopes ascending by id -> usage reads/writes'):
        if n not in seq:
            errors.append(f'scope-batch sequence note missing {n!r}')
    for n in ('QUERY - Get the platform administrator role','QUERY - Check platform administrator'):
        if n in md or n in wsd:errors.append('batch caller authorization must not reload live assignments')
    ops=spec_database_operations(md);heads=('QUERY - Lock the caller user','QUERY - Check current credential and user','QUERY - Lock existing scopes','QUERY - Check duplicate scope','QUERY - Check permission scope in use','INSERT - Create scope','UPDATE - Update or delete scope')
    if tuple(h for _,h,_ in ops)!=heads:errors.append('batch needs seven declared caller/credential/sorted-target/conflict/write SQL definitions')
    sql={h:re.sub(r'--[^\n]*','',s) for _,h,s in ops};required={
        heads[0]:["WHERE u.id = '<sequence.callerUserId>'",'FOR UPDATE'],
        heads[1]:['JOIN authen.m_user u ON u.id = at.user_id',"at.token = '<sequence.accessTokenHash>'","at.user_id = '<sequence.callerUserId>'","at.row_status = 'ACTIVE'","at.expired_at > '<sequence.now>'","u.row_status = 'ACTIVE'"],
        heads[2]:['s.id as scope_id',"WHERE s.id = ANY ('<sequence.targetScopeIds>'::UUID[])","AND s.row_status <> 'DELETED'",'ORDER BY s.id\nFOR UPDATE'],
        heads[3]:["WHERE s.scope = '<sequence.scopes.scope>'","AND s.row_status <> 'DELETED'","AND ('<sequence.scopes.id>' IS NULL OR s.id <> '<sequence.scopes.id>')"],
        heads[4]:['FROM author.t_permission_scope ps\n',"WHERE ps.scope_id = '<sequence.scopes.id>'","AND ps.row_status <> 'DELETED'"],
        heads[5]:['created_by,\n    created_at,','<sequence.createdBy>','<sequence.now>','<sequence.scopes.rowStatus>','<sequence.scopes.scope>','<sequence.scopes.name>','<sequence.scopes.description>','RETURNING id as scope_id'],
        heads[6]:["updated_by = '<sequence.updatedBy>'","updated_at = '<sequence.now>'","row_status = '<sequence.scopes.rowStatus>'","scope = '<sequence.scopes.scope>'","name = '<sequence.scopes.name>'","description = '<sequence.scopes.description>'","WHERE id = '<sequence.scopes.id>'","AND row_status <> 'DELETED'",'RETURNING id as scope_id']}
    for h,needles in required.items():
        for n in needles:
            if n not in sql.get(h,''):errors.append(f'{h} missing {n!r}')
    if 'NOW()' in '\n'.join(sql.values()) or 'created_at =' in sql.get(heads[6],'') or 'JOIN' in sql.get(heads[4],'') or "'ACTIVE'" in sql.get(heads[4],'') or SEQUENCE_LOCK.search(''.join(sql.get(h,'') for h in heads[3:5])):errors.append('batch must use bound server now, preserve creation audit on updates and count every non-DELETED definition without joins or extra locks')
    actual,lifecycle=sequence_database_operations(wsd);errors+=lifecycle
    from collections import Counter
    wanted=Counter((t.split('.')[-1],h,s) for t,h,s in ops)
    for t,h,s in ops:
        if h==heads[3]:wanted[(t.split('.')[-1],h,s)]+=1
    if Counter(actual)!=wanted:errors.append('batch SQL differs character-for-character or has missing/excess/repeated blocks')
    lines=wsd.splitlines()
    for i,l in enumerate(lines):
        request=re.match(r'^( *)infra -> \w+: (?:QUERY|INSERT|UPDATE) - ',l)
        if not request:continue
        prefix=' '*(len(request[1])+8);j=i+3
        while j<len(lines) and lines[j].strip()!='end note':
            if lines[j] and not lines[j].startswith(prefix):errors.append('batch SQL must retain exactly added note indentation and original SQL whitespace')
            j+=1
    for _,h,_ in ops:
        if wsd.count('app -> infra: '+h+'\n')!=(2 if h==heads[3] else 1):errors.append(f'{h} needs matching Application request count')
    for mat in re.finditer(r'(?m)^( *)infra -> (\w+): ((?:QUERY|INSERT|UPDATE) - [^\n]+)\n',wsd):
        r=re.search(rf'{mat[2]} -> infra: Return ([^\n]+)\n.*?deactivate {mat[2]}\n\s*infra -> app: Return ([^\n]+)',wsd[mat.start():],re.S)
        if not r or r[1]!=r[2]:errors.append('each database result must return with its meaning to Application')
    for n in ('Validate all items in input order; canonical duplicate ids and exact duplicate non-DELETED scope codes are 400 before SQL','Verify JWT signature/issuer/audience/expiry/UUID sub and the roles claim as unique non-empty strings','callerUserId = verified sub; accessTokenHash = SHA-256 exact JWT; createdBy/updatedBy = caller UUID string','targetScopeIds = typed UUID[] of supplied canonical ids, empty for all inserts; omitted per-item id = typed SQL NULL','Capture fresh server UTC now after caller lock; recheck JWT exp','JWT expired while waiting for caller lock','Map locked scopes by id; check all supplied target ids in original input order; choose first missing index i','Authorize once using only exact case-sensitive PLATFORM_ADMIN in verified JWT roles; never reload live grants','loop For every scopes[i] in original request order; all writes remain provisional','currentIndex = i; bind this item fields and server audit/now; prior item writes are visible','A non-DELETED permission-scope definition exists','Preserve existing permission-scope definitions; no in-use rejection for this status','Guarded UPDATE returned zero rows','Require exactly one returned scope_id equal to this input id','Require exactly one inserted scope_id','action = DELETE for DELETED, ARCHIVE for ARCHIVED, otherwise UPDATE','Append exactly index=i, scopeId from RETURNING and action to ordered results; do not emit per-item HTTP','Require results count equals input count, original index order and unique returned scopeIds; data = exactly scopes array of index/scopeId/action; map all before COMMIT','SQLSTATE 23505 from uq_m_scope_scope at currentIndex'):
        if n not in wsd:errors.append(f'batch sequence missing {n!r}')
    if wsd.count('app -> infra: COMMIT')!=1 or wsd.count('Authorize once using only exact')!=1:errors.append('batch has exactly one permission decision and one final commit')
    # Expand a single representative loop iteration. Real multi-item ordering/rollback is verified by SQL fixtures.
    flattened=[];stack=[];note=False;loop_ranges=[];loop_start=None
    for i,l in enumerate(lines):
        t=l.strip()
        if t.startswith('note ') and ':' not in t:note=True
        if note:
            flattened.append(l)
            if t=='end note':note=False
            continue
        if t.startswith('loop '):stack.append('loop');loop_start=i;continue
        if t.startswith('alt '):stack.append('alt')
        elif t in ('end','end alt'):
            if not stack:errors.append('batch loop/alternative unbalanced');continue
            kind=stack.pop()
            if kind=='loop':loop_ranges.append((loop_start,i));continue
        flattened.append(l)
    if stack or len(loop_ranges)!=1:errors.append('batch requires one balanced request-order item loop')
    elif any('app -> infra: COMMIT' in l or 'app -> api: HTTP 200' in l for l in lines[loop_ranges[0][0]:loop_ranges[0][1]]):errors.append('no success/commit may occur inside the item loop')
    for response in re.finditer(r'(?m)^( *)app -> api: HTTP [^\n]+\n',wsd):
        next_lines=wsd[response.end():].splitlines()[:2]
        if len(next_lines)!=2 or not next_lines[0].strip().startswith('api -> page:') or not next_lines[1].strip().startswith('page -> user:'):errors.append('every batch outcome must reach frontend and caller')
    traces,structure=login_sequence_paths('\n'.join(flattened));errors+=structure;outcomes=[];unauthorized=[]
    for tr in traces:
        responses=[e for e in tr if e.startswith('app -> api: HTTP ')];joined='\n'.join(tr)
        if len(responses)!=1:errors.append('batch representative trace needs one terminal HTTP outcome');continue
        code=int(responses[0].split('HTTP ')[1].split()[0]);outcomes.append(code);db=[e for e in tr if e.startswith('infra -> ')];begun=any(e.startswith('app -> infra: BEGIN') for e in tr);writes=[e for e in db if ': INSERT' in e or ': UPDATE' in e]
        def ordered(*parts):
            pos=[next((i for i,e in enumerate(tr) if p in e),-1) for p in parts]
            return -1 not in pos and pos==sorted(set(pos))
        if db and not ordered('Validate all items','Verify JWT','callerUserId = verified sub','BEGIN READ COMMITTED',heads[0]):errors.append('batch must validate all items/claims before user-first transactional SQL')
        if heads[1] in joined and not ordered(heads[0],'Capture fresh server UTC now',heads[1]):errors.append('batch credential read requires post-user-lock fresh now')
        if heads[2] in joined and not ordered(heads[1],heads[2]):errors.append('target locks require valid current credential')
        if 'Authorize once using only exact' in joined and not ordered(heads[2],'Map locked scopes by id','Authorize once using only exact'):errors.append('whole-target existence must precede one claims permission')
        if heads[3] in joined and not ordered('Authorize once using only exact','currentIndex = i',heads[3]):errors.append('item conflicts require preflight permission and item index')
        if heads[4] in joined and not ordered(heads[2],heads[3],heads[4]):errors.append('usage check requires the locked target and follows the current-item duplicate check')
        if code==200:
            if len(writes)!=1 or not ordered(heads[3],writes[0] if writes else 'missing','Append exactly index=i','Require results count equals input count','app -> infra: COMMIT','HTTP 200') or 'ROLLBACK' in joined:errors.append('representative item must map its returned id/action then one final committed whole-batch 200')
            if heads[5] in joined and (heads[4] in joined or not ordered(heads[5],'Require exactly one inserted scope_id','Append exactly')):errors.append('insert iteration only inserts and validates returned id/action')
            if heads[6] in joined and ((heads[4] in joined)==('Preserve existing permission-scope definitions' in joined) or not ordered(heads[2],*([heads[4]] if heads[4] in joined else []),heads[6],'Require exactly one returned scope_id equal to this input id','action = DELETE','Append exactly')):errors.append('existing iteration must write its locked target after exactly one usage decision and validate update id/action before result mapping')
        elif begun:
            if not ordered('BEGIN','ROLLBACK',f'HTTP {code}') or 'app -> infra: COMMIT' in joined:errors.append('all transactional batch failures roll back before response')
            if code in (401,403,409,408,500) and writes:errors.append('rejected representative item must not continue into a write')
            if code==401 and heads[2] in joined:errors.append('invalid credential must not lock/read target scopes')
            if code==403 and any(h in joined for h in heads[3:]):errors.append('single 403 must precede every item conflict/write')
            if code in (404,409) and 'scopes[i]:' not in responses[0]:errors.append('item 404/409 needs scopes[i] position')
        elif code not in (400,401) or db:errors.append('pre-BEGIN failure must be validation/JWT with no SQL')
        if code==401:unauthorized.append(len(db))
    if Counter(outcomes)!=Counter({400:1,401:4,404:3,403:1,409:4,200:3,408:1,500:1}) or sorted(unauthorized)!=[0,1,1,2]:errors.append(f'expected 18 representative item traces, got {dict(Counter(outcomes))},401 SQL={unauthorized}')
    try:
        body=json.loads(re.search(r'#### Example Body Parameters\n\n```JSON\n(.*?)```',md,re.S)[1]);result=author_json(md,'Success');items=body['scopes'];rows=result['data']['scopes']
        if set(result['data'])!={'scopes'} or len(items)!=len(rows) or len({x['scopeId'] for x in rows})!=len(rows):errors.append('batch example needs one uniquely identified result per input')
        for i,(item,row) in enumerate(zip(items,rows)):
            action='INSERT' if 'id' not in item else {'DELETED':'DELETE','ARCHIVED':'ARCHIVE'}.get(item.get('rowStatus'),'UPDATE')
            if set(row)!={'index','scopeId','action'} or type(row['index']) is not int or row['index']!=i or row['action']!=action or ('id' in item and row['scopeId']!=item['id']):errors.append('batch example result mapping/order/action is incorrect')
        internal=author_json(md,'Fail - Internal Server Error')
        if internal['status']['code']!=500 or 'bizCode' in internal['status']:errors.append('batch internal failure must omit bizCode')
    except (AttributeError,TypeError,KeyError,IndexError,ValueError):errors.append('batch example shape malformed')
    errors+=json_blocks_parse(md);errors+=table_lines_aligned(md)
    if '--rendered-svg' in sys.argv:
        import xml.etree.ElementTree as ET
        try:
            root=ET.parse(sys.argv[sys.argv.index('--rendered-svg')+1]).getroot();wanted=Counter(' '.join(l.split()) for _,_,s in actual for l in s.splitlines() if l.strip());visible=Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'));missing=wanted-visible
            if missing:errors.append(f'rendered scope-batch SQL missing {sum(missing.values())} lines')
            else:print(f'OK: rendered scope-batch SQL ({sum(wanted.values())}/{sum(wanted.values())} visible lines)')
        except (IndexError,OSError,ET.ParseError) as exc:errors.append(f'cannot verify scope-batch SVG: {exc}')
    if errors:return fail('; '.join(errors))
    print('OK: scope-batch-flow (18 representative item traces; seven exact SQL definitions, sorted target locks before usage checks and one final commit)')
    return 0


COMMANDS['scope-batch-flow'] = check_scope_batch_flow


def check_role_upsert_flow() -> int:
    """Verify role upsert claim authorization independently of live business-invariant reads."""
    path=f'{AUTHOR_DIR}/{AUTHOR_SPECS["01"]}/spec.md';md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    for n in ('status: in-review', 'approved_by: null', 'approved_at: null'):
        if n not in md:errors.append(f'role-upsert spec missing {n!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for n in ('Permission: only a platform administrator from the verified JWT roles claim', 'exact case-sensitive role name PLATFORM_ADMIN',
            'Malformed/missing roles is 401', 'Grant withdrawal alone does not invalidate', 'fresh server UTC now after that lock',
            'Lock order is caller user -> target role -> binding checks/write', 'Reference/assignment writers must lock and recheck their target role',
            'must not be presented as certification of an unmigrated cross-API writer', 'Duplicate name exclusion is null-safe',
            'lock the non-DELETED target role FOR UPDATE', 'Insert-ARCHIVED is allowed (201 insert)', 'zero returned rows is 404 E10004',
            'exactly roleId from RETURNING', 'SQLSTATE 23505', 'uq_m_role_name'):
        if n not in seq:
            errors.append(f'role-upsert sequence note missing {n!r}')
    for n in ('QUERY - Get the platform administrator role','QUERY - Check platform administrator'):
        if n in md or n in wsd:errors.append('role-upsert may not reload live caller grants')
    ops=spec_database_operations(md);heads=('QUERY - Lock the caller user','QUERY - Check current credential and user','QUERY - Check existing role','QUERY - Check system role','QUERY - Check duplicate name','QUERY - Check user in use','QUERY - Check role permission in use','INSERT - Create role','UPDATE - Update or delete role')
    if tuple(h for _,h,_ in ops)!=heads:errors.append('role-upsert needs nine operations in declared lock/credential/business/write order')
    sql={h:re.sub(r'--[^\n]*','',s) for _,h,s in ops}
    need={heads[0]:["WHERE u.id = '<sequence.callerUserId>'",'FOR UPDATE'],heads[1]:['JOIN authen.m_user u ON u.id = at.user_id',"at.token = '<sequence.accessTokenHash>'","at.user_id = '<sequence.callerUserId>'","at.row_status = 'ACTIVE'","at.expired_at > '<sequence.now>'","u.row_status = 'ACTIVE'"],
          heads[2]:['r.id as role_id,','r.name',"WHERE r.id = '<sequence.id>'","AND r.row_status <> 'DELETED'",'FOR UPDATE'],heads[3]:["WHERE r.id = '<sequence.id>'","AND r.name = 'PLATFORM_ADMIN'"],
          heads[4]:["WHERE r.name = '<sequence.name>'","AND r.row_status <> 'DELETED'","AND ('<sequence.id>' IS NULL OR r.id <> '<sequence.id>')"],
          heads[5]:["WHERE ur.role_id = '<sequence.id>'","AND ur.row_status <> 'DELETED'"],heads[6]:["WHERE rp.role_id = '<sequence.id>'","AND rp.row_status <> 'DELETED'"],
          heads[7]:['created_by,\n    created_at,','<sequence.createdBy>','<sequence.now>','<sequence.rowStatus>','<sequence.name>','<sequence.description>','RETURNING id as role_id'],
          heads[8]:["updated_by = '<sequence.updatedBy>'","updated_at = '<sequence.now>'","row_status = '<sequence.rowStatus>'","name = '<sequence.name>'","description = '<sequence.description>'","WHERE id = '<sequence.id>'","AND row_status <> 'DELETED'","AND name <> 'PLATFORM_ADMIN'",'RETURNING id as role_id']}
    for h,ns in need.items():
        for n in ns:
            if n not in sql.get(h,''):errors.append(f'{h} missing {n!r}')
    if 'NOW()' in '\n'.join(sql.values()) or 'created_at =' in sql.get(heads[8],''):errors.append('role upsert uses fresh bound now and preserves creation audit on update')
    # Strict presentation decoding removes only the added note prefix, never SQL whitespace.
    source_lines=wsd.splitlines()
    for i,line in enumerate(source_lines):
        request=re.match(r'^( *)infra -> \w+: (?:QUERY|INSERT|UPDATE) - ',line)
        if not request:continue
        prefix=' '*(len(request[1])+8);cursor=i+3
        while cursor<len(source_lines) and source_lines[cursor].strip()!='end note':
            raw=source_lines[cursor]
            if raw and not raw.startswith(prefix):errors.append('every SQL line must retain the exact added presentation prefix')
            cursor+=1
    actual,lifecycle=sequence_database_operations(wsd);errors+=lifecycle
    from collections import Counter
    expected=Counter((t.split('.')[-1],h,s) for t,h,s in ops)
    for t,h,s in ops:
        if h in (heads[4],heads[8]):expected[(t.split('.')[-1],h,s)]+=1
    if Counter(actual)!=expected:errors.append('role-upsert SQL differs character-for-character, has missing/excess or wrong repeated operations')
    for _,h,_ in ops:
        count=2 if h in (heads[4],heads[8]) else 1
        if wsd.count('app -> infra: '+h+'\n')!=count:errors.append(f'{h} Application orchestration count incorrect')
    for match in re.finditer(r'(?m)^( *)infra -> (\w+): ((?:QUERY|INSERT|UPDATE) - [^\n]+)\n',wsd):
        tail=wsd[match.start():];r=re.search(rf'{match[2]} -> infra: Return ([^\n]+)\n.*?deactivate {match[2]}\n\s*infra -> app: Return ([^\n]+)',tail,re.S)
        if not r or r[1]!=r[2]:errors.append('database result must be mapped identically back to Application')
    for n in ('Verify JWT signature/issuer/audience/expiry/UUID sub and the roles claim as unique non-empty strings','callerUserId = verified sub; accessTokenHash = SHA-256 exact JWT; createdBy/updatedBy = caller UUID string; omitted id = typed SQL NULL','Capture fresh server UTC now after caller lock; recheck JWT exp','JWT expired while waiting for caller lock','Authorize only exact case-sensitive PLATFORM_ADMIN in verified JWT roles; never reload live grants','Stored target is PLATFORM_ADMIN','Either non-DELETED binding exists','Guarded UPDATE returned zero rows','Require exactly one returned role_id equal to requested id','Require exactly one inserted role_id; missing or malformed result is internal failure','SQLSTATE 23505 from uq_m_role_name','data = exactly roleId from RETURNING; exclude caller/token/audit/grants','Suppress response body/status/data for 204'):
        if n not in wsd:errors.append(f'role-upsert sequence missing {n!r}')
    if wsd.count('alt Guarded UPDATE returned zero rows')!=2:errors.append('both destructive and reversible UPDATE branches must reject zero returned rows')
    for response in re.finditer(r'(?m)^( *)app -> api: HTTP [^\n]+\n',wsd):
        following=wsd[response.end():].splitlines()[:2]
        if len(following)!=2 or not following[0].strip().startswith('api -> page:') or not following[1].strip().startswith('page -> user:'):errors.append('every HTTP outcome must reach the frontend and caller')
    traces,structure=login_sequence_paths(wsd);errors+=structure;outcomes=[];unauthorized=[]
    for tr in traces:
        responses=[e for e in tr if e.startswith('app -> api: HTTP ')];joined='\n'.join(tr)
        if len(responses)!=1:errors.append('role-upsert trace needs exactly one HTTP outcome');continue
        code=int(responses[0].split('HTTP ')[1].split()[0]);outcomes.append(code)
        def ordered(*parts):
            positions=[next((i for i,e in enumerate(tr) if n in e),-1) for n in parts]
            return -1 not in positions and positions==sorted(set(positions))
        db=[e for e in tr if e.startswith('infra -> ')];begun=any(e.startswith('app -> infra: BEGIN') for e in tr)
        writes=[e for e in db if ': INSERT' in e or ': UPDATE' in e];target=any(heads[2] in e for e in db);permission=any('Authorize only exact' in e for e in tr)
        if db and not ordered('Verify JWT','callerUserId = verified sub','BEGIN READ COMMITTED',heads[0]):errors.append('DB work requires verified caller and user-first transaction lock')
        if any(heads[1] in e for e in db) and not ordered(heads[0],'Capture fresh server UTC now',heads[1]):errors.append('fresh credentials must follow caller lock')
        if target and not ordered(heads[1],heads[2]):errors.append('target existence requires valid current credential first')
        if permission and not ordered(heads[1],*([heads[2]] if target else []),'Authorize only exact'):errors.append('claims permission must follow current credential and optional target existence')
        if any(heads[3] in e for e in db) and not ordered('Authorize only exact',heads[3]):errors.append('system role check must follow caller claims permission')
        if any(heads[4] in e for e in db) and not ordered('Authorize only exact',*([heads[3]] if target else []),heads[4]):errors.append('duplicate check must follow permission and optional system role check')
        if any(heads[5] in e for e in db) and not ordered(heads[4],heads[5],heads[6]):errors.append('in-use checks must follow duplicate check in declared order')
        if code in (200,201,204):
            if len(writes)!=1 or not ordered(heads[4],writes[0] if writes else 'missing','app -> infra: COMMIT',f'HTTP {code}') or 'ROLLBACK' in joined:errors.append('successful role action requires one guarded write then commit before response')
            if code==201:
                if target or any(h in joined for h in (heads[3],heads[5],heads[6],heads[8])) or heads[7] not in joined:errors.append('insert skips target/system/binding reads and only inserts')
            elif not target or heads[8] not in joined or heads[7] in joined:errors.append('existing success requires locked target and guarded update only')
            if code!=201 and not ordered(heads[8],'Require exactly one returned role_id equal to requested id','app -> infra: COMMIT'):errors.append('each existing success must validate returned id after UPDATE and before commit')
            destructive=code==204 or 'Archive Role Success' in responses[0]
            if destructive!=(heads[5] in joined and heads[6] in joined):errors.append('only existing delete/archive must check both binding types')
            if code==204 and ('no response body' not in responses[0] or 'data = exactly roleId' in joined):errors.append('204 must have no mapped response body')
            if code!=204 and not ordered('data = exactly roleId','app -> infra: COMMIT'):errors.append('body must be mapped before commit')
        elif begun:
            if not ordered('BEGIN','ROLLBACK',f'HTTP {code}') or any(e=='app -> infra: COMMIT' for e in tr):errors.append('all rejected transactional role paths roll back before the error')
            if code in (401,403,409,408,500) and writes:errors.append('visible reject path must not proceed past a failed check into a write')
            if code==401 and any(e for e in db if 'm_role:' in e or 't_user_role:' in e or 't_role_permission:' in e):errors.append('invalid current credentials must not inspect target roles/bindings')
            if code==403 and any(h in joined for h in heads[3:]):errors.append('403 must precede system/duplicate/in-use/write')
        elif code not in (400,401) or db:errors.append('pre-transaction reject may only be no-SQL validation or JWT failure')
        if code==401:unauthorized.append(len(db))
    if Counter(outcomes)!=Counter({400:1,401:4,403:2,404:3,409:5,201:1,200:2,204:1,408:1,500:1}) or sorted(unauthorized)!=[0,1,1,2]:errors.append(f'role-upsert terminal paths incorrect: {dict(Counter(outcomes))},401 SQL={unauthorized}')
    for title in ('Success - Insert','Success - Update','Success - Archive'):
        obj=author_json(md,title)
        if not obj or set(obj.get('data',{}))!={'roleId'}:errors.append(f'{title} must return exactly roleId')
    obj=author_json(md,'Fail - Internal Server Error')
    if not obj or obj['status']['code']!=500 or 'bizCode' in obj['status']:errors.append('internal error example must be generic 500 without bizCode')
    errors+=json_blocks_parse(md);errors+=table_lines_aligned(md)
    if '--rendered-svg' in sys.argv:
        import xml.etree.ElementTree as ET
        try:
            root=ET.parse(sys.argv[sys.argv.index('--rendered-svg')+1]).getroot();wanted=Counter(' '.join(l.split()) for _,_,s in actual for l in s.splitlines() if l.strip());visible=Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'));missing=wanted-visible
            if missing:errors.append(f'rendered role-upsert SQL missing {sum(missing.values())} lines')
            else:print(f'OK: rendered role-upsert SQL ({sum(wanted.values())}/{sum(wanted.values())} visible lines)')
        except (IndexError,OSError,ET.ParseError) as exc:errors.append(f'cannot verify role-upsert SVG: {exc}')
    if errors:return fail('; '.join(errors))
    print('OK: role-upsert-flow (21 terminal traces; nine exact SQL definitions, claims and current credential gates)')
    return 0


COMMANDS['role-upsert-flow'] = check_role_upsert_flow


def check_role_batch_flow() -> int:
    """Verify whole-batch preflight and ordered atomic role mutations; unroll one representative item."""
    path=f'{AUTHOR_DIR}/{AUTHOR_SPECS["02"]}/spec.md';md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    for n in ('status: in-review', 'approved_by: null', 'approved_at: null', 'Validate the whole request before SQL', 'exact case-sensitive PLATFORM_ADMIN'):
        if n not in md:errors.append(f'role-batch spec missing {n!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for n in ('Compare parsed canonical UUIDs', 'all target existence checks', 'after all target existence checks and before any conflict or write',
            'with one SELECT FOR UPDATE', 'Withdrawal of a grant alone does not invalidate', 'first missing/DELETED target in original request order',
            "Each item's conflict reads see preceding item writes", 'reversing those items returns duplicate 409', 'does not apply a final-state rename plan',
            'exactly one result per input item in the same order', 'batch never sends per-item 201/204 or partial success', 'SQLSTATE 23505', 'uq_m_role_name',
            'reference/assignment writers must lock and recheck'):
        if n not in seq:
            errors.append(f'role-batch sequence note missing {n!r}')
    for n in ('QUERY - Get the platform administrator role','QUERY - Check platform administrator'):
        if n in md or n in wsd:errors.append('batch caller authorization must not reload live assignments')
    ops=spec_database_operations(md);heads=('QUERY - Lock the caller user','QUERY - Check current credential and user','QUERY - Lock existing roles','QUERY - Check system role','QUERY - Check duplicate name','QUERY - Check user in use','QUERY - Check role permission in use','INSERT - Create role','UPDATE - Update or delete role')
    if tuple(h for _,h,_ in ops)!=heads:errors.append('batch needs nine declared caller/credential/sorted-target/business/write SQL definitions')
    sql={h:re.sub(r'--[^\n]*','',s) for _,h,s in ops};required={
        heads[0]:["WHERE u.id = '<sequence.callerUserId>'",'FOR UPDATE'],
        heads[1]:['JOIN authen.m_user u ON u.id = at.user_id',"at.token = '<sequence.accessTokenHash>'","at.user_id = '<sequence.callerUserId>'","at.row_status = 'ACTIVE'","at.expired_at > '<sequence.now>'","u.row_status = 'ACTIVE'"],
        heads[2]:['r.id as role_id,','r.name',"WHERE r.id = ANY ('<sequence.targetRoleIds>'::UUID[])","AND r.row_status <> 'DELETED'",'ORDER BY r.id\nFOR UPDATE'],
        heads[3]:["WHERE r.id = '<sequence.roles.id>'","AND r.name = 'PLATFORM_ADMIN'"],
        heads[4]:["WHERE r.name = '<sequence.roles.name>'","AND r.row_status <> 'DELETED'","AND ('<sequence.roles.id>' IS NULL OR r.id <> '<sequence.roles.id>')"],
        heads[5]:["WHERE ur.role_id = '<sequence.roles.id>'","AND ur.row_status <> 'DELETED'"],heads[6]:["WHERE rp.role_id = '<sequence.roles.id>'","AND rp.row_status <> 'DELETED'"],
        heads[7]:['created_by,\n    created_at,','<sequence.createdBy>','<sequence.now>','<sequence.roles.rowStatus>','<sequence.roles.name>','<sequence.roles.description>','RETURNING id as role_id'],
        heads[8]:["updated_by = '<sequence.updatedBy>'","updated_at = '<sequence.now>'","row_status = '<sequence.roles.rowStatus>'","name = '<sequence.roles.name>'","description = '<sequence.roles.description>'","WHERE id = '<sequence.roles.id>'","AND row_status <> 'DELETED'","AND name <> 'PLATFORM_ADMIN'",'RETURNING id as role_id']}
    for h,needles in required.items():
        for n in needles:
            if n not in sql.get(h,''):errors.append(f'{h} missing {n!r}')
    if 'NOW()' in '\n'.join(sql.values()) or 'created_at =' in sql.get(heads[8],''):errors.append('batch must use bound server now and preserve creation audit on updates')
    actual,lifecycle=sequence_database_operations(wsd);errors+=lifecycle
    from collections import Counter
    wanted=Counter((t.split('.')[-1],h,s) for t,h,s in ops)
    for t,h,s in ops:
        if h==heads[4]:wanted[(t.split('.')[-1],h,s)]+=1
    if Counter(actual)!=wanted:errors.append('batch SQL differs character-for-character or has missing/excess/repeated blocks')
    lines=wsd.splitlines()
    for i,l in enumerate(lines):
        request=re.match(r'^( *)infra -> \w+: (?:QUERY|INSERT|UPDATE) - ',l)
        if not request:continue
        prefix=' '*(len(request[1])+8);j=i+3
        while j<len(lines) and lines[j].strip()!='end note':
            if lines[j] and not lines[j].startswith(prefix):errors.append('batch SQL must retain exactly added note indentation and original SQL whitespace')
            j+=1
    for _,h,_ in ops:
        if wsd.count('app -> infra: '+h+'\n')!=(2 if h==heads[4] else 1):errors.append(f'{h} needs matching Application request count')
    for mat in re.finditer(r'(?m)^( *)infra -> (\w+): ((?:QUERY|INSERT|UPDATE) - [^\n]+)\n',wsd):
        r=re.search(rf'{mat[2]} -> infra: Return ([^\n]+)\n.*?deactivate {mat[2]}\n\s*infra -> app: Return ([^\n]+)',wsd[mat.start():],re.S)
        if not r or r[1]!=r[2]:errors.append('each database result must return with its meaning to Application')
    for n in ('Validate all items in input order; canonical duplicate ids and exact duplicate non-DELETED names are 400 before SQL','Verify JWT signature/issuer/audience/expiry/UUID sub and the roles claim as unique non-empty strings','callerUserId = verified sub; accessTokenHash = SHA-256 exact JWT; createdBy/updatedBy = caller UUID string','targetRoleIds = typed UUID[] of supplied canonical ids, empty for all inserts; omitted per-item id = typed SQL NULL','Capture fresh server UTC now after caller lock; recheck JWT exp','JWT expired while waiting for caller lock','Map locked roles by id; check all supplied target ids in original input order; choose first missing index i','Authorize once using only exact case-sensitive PLATFORM_ADMIN in verified JWT roles; never reload live grants','loop For every roles[i] in original request order; all writes remain provisional','currentIndex = i; bind this item fields and server audit/now; prior item writes are visible','Stored target is PLATFORM_ADMIN','Either non-DELETED binding exists','Guarded UPDATE returned zero rows','Require exactly one returned role_id equal to this input id','Require exactly one inserted role_id','action = DELETE for DELETED, ARCHIVE for ARCHIVED, otherwise UPDATE','Append exactly index=i, roleId from RETURNING and action to ordered results; do not emit per-item HTTP','Require results count equals input count, original index order and unique returned roleIds; data = exactly roles array of index/roleId/action; map all before COMMIT','SQLSTATE 23505 from uq_m_role_name at currentIndex'):
        if n not in wsd:errors.append(f'batch sequence missing {n!r}')
    if wsd.count('app -> infra: COMMIT')!=1 or wsd.count('Authorize once using only exact')!=1:errors.append('batch has exactly one permission decision and one final commit')
    # Expand a single representative loop iteration. Real multi-item ordering/rollback is verified by SQL fixtures.
    flattened=[];stack=[];note=False;loop_ranges=[];loop_start=None
    for i,l in enumerate(lines):
        t=l.strip()
        if t.startswith('note ') and ':' not in t:note=True
        if note:
            flattened.append(l)
            if t=='end note':note=False
            continue
        if t.startswith('loop '):stack.append('loop');loop_start=i;continue
        if t.startswith('alt '):stack.append('alt')
        elif t in ('end','end alt'):
            if not stack:errors.append('batch loop/alternative unbalanced');continue
            kind=stack.pop()
            if kind=='loop':loop_ranges.append((loop_start,i));continue
        flattened.append(l)
    if stack or len(loop_ranges)!=1:errors.append('batch requires one balanced request-order item loop')
    elif any('app -> infra: COMMIT' in l or 'app -> api: HTTP 200' in l for l in lines[loop_ranges[0][0]:loop_ranges[0][1]]):errors.append('no success/commit may occur inside the item loop')
    for response in re.finditer(r'(?m)^( *)app -> api: HTTP [^\n]+\n',wsd):
        next_lines=wsd[response.end():].splitlines()[:2]
        if len(next_lines)!=2 or not next_lines[0].strip().startswith('api -> page:') or not next_lines[1].strip().startswith('page -> user:'):errors.append('every batch outcome must reach frontend and caller')
    traces,structure=login_sequence_paths('\n'.join(flattened));errors+=structure;outcomes=[];unauthorized=[]
    for tr in traces:
        responses=[e for e in tr if e.startswith('app -> api: HTTP ')];joined='\n'.join(tr)
        if len(responses)!=1:errors.append('batch representative trace needs one terminal HTTP outcome');continue
        code=int(responses[0].split('HTTP ')[1].split()[0]);outcomes.append(code);db=[e for e in tr if e.startswith('infra -> ')];begun=any(e.startswith('app -> infra: BEGIN') for e in tr);writes=[e for e in db if ': INSERT' in e or ': UPDATE' in e]
        def ordered(*parts):
            pos=[next((i for i,e in enumerate(tr) if p in e),-1) for p in parts]
            return -1 not in pos and pos==sorted(set(pos))
        if db and not ordered('Validate all items','Verify JWT','callerUserId = verified sub','BEGIN READ COMMITTED',heads[0]):errors.append('batch must validate all items/claims before user-first transactional SQL')
        if heads[1] in joined and not ordered(heads[0],'Capture fresh server UTC now',heads[1]):errors.append('batch credential read requires post-user-lock fresh now')
        if heads[2] in joined and not ordered(heads[1],heads[2]):errors.append('target locks require valid current credential')
        if 'Authorize once using only exact' in joined and not ordered(heads[2],'Map locked roles by id','Authorize once using only exact'):errors.append('whole-target existence must precede one claims permission')
        if heads[4] in joined and not ordered('Authorize once using only exact','currentIndex = i',*([heads[3]] if heads[3] in joined else []),heads[4]):errors.append('item conflicts require preflight permission, item index and stored system-role check for existing items')
        if heads[5] in joined and not ordered(heads[4],heads[5],heads[6]):errors.append('binding checks follow current-item duplicate in order')
        if code==200:
            if len(writes)!=1 or not ordered(heads[4],writes[0] if writes else 'missing','Append exactly index=i','Require results count equals input count','app -> infra: COMMIT','HTTP 200') or 'ROLLBACK' in joined:errors.append('representative item must map its returned id/action then one final committed whole-batch 200')
            if heads[7] in joined and (heads[3] in joined or heads[5] in joined or not ordered(heads[7],'Require exactly one inserted role_id','Append exactly')):errors.append('insert iteration only inserts and validates returned id/action')
            if heads[8] in joined and not ordered(heads[3],heads[8],'Require exactly one returned role_id equal to this input id','action = DELETE','Append exactly'):errors.append('existing iteration must protect system role and validate update id/action before result mapping')
        elif begun:
            if not ordered('BEGIN','ROLLBACK',f'HTTP {code}') or 'app -> infra: COMMIT' in joined:errors.append('all transactional batch failures roll back before response')
            if code in (401,403,409,408,500) and writes:errors.append('rejected representative item must not continue into a write')
            if code==401 and heads[2] in joined:errors.append('invalid credential must not lock/read target roles')
            if code==403 and any(h in joined for h in heads[3:]):errors.append('single 403 must precede every item conflict/write')
            if code in (404,409) and 'roles[i]:' not in responses[0]:errors.append('item 404/409 needs roles[i] position')
        elif code not in (400,401) or db:errors.append('pre-BEGIN failure must be validation/JWT with no SQL')
        if code==401:unauthorized.append(len(db))
    if Counter(outcomes)!=Counter({400:1,401:4,404:3,403:1,409:5,200:3,408:1,500:1}) or sorted(unauthorized)!=[0,1,1,2]:errors.append(f'expected 19 representative item traces, got {dict(Counter(outcomes))},401 SQL={unauthorized}')
    try:
        body=json.loads(re.search(r'#### Example Body Parameters\n\n```JSON\n(.*?)```',md,re.S)[1]);result=author_json(md,'Success');items=body['roles'];rows=result['data']['roles']
        if set(result['data'])!={'roles'} or len(items)!=len(rows) or len({x['roleId'] for x in rows})!=len(rows):errors.append('batch example needs one uniquely identified result per input')
        for i,(item,row) in enumerate(zip(items,rows)):
            action='INSERT' if 'id' not in item else {'DELETED':'DELETE','ARCHIVED':'ARCHIVE'}.get(item.get('rowStatus'),'UPDATE')
            if set(row)!={'index','roleId','action'} or type(row['index']) is not int or row['index']!=i or row['action']!=action or ('id' in item and row['roleId']!=item['id']):errors.append('batch example result mapping/order/action is incorrect')
        internal=author_json(md,'Fail - Internal Server Error')
        if internal['status']['code']!=500 or 'bizCode' in internal['status']:errors.append('batch internal failure must omit bizCode')
    except (AttributeError,TypeError,KeyError,IndexError,ValueError):errors.append('batch example shape malformed')
    errors+=json_blocks_parse(md);errors+=table_lines_aligned(md)
    if '--rendered-svg' in sys.argv:
        import xml.etree.ElementTree as ET
        try:
            root=ET.parse(sys.argv[sys.argv.index('--rendered-svg')+1]).getroot();wanted=Counter(' '.join(l.split()) for _,_,s in actual for l in s.splitlines() if l.strip());visible=Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'));missing=wanted-visible
            if missing:errors.append(f'rendered role-batch SQL missing {sum(missing.values())} lines')
            else:print(f'OK: rendered role-batch SQL ({sum(wanted.values())}/{sum(wanted.values())} visible lines)')
        except (IndexError,OSError,ET.ParseError) as exc:errors.append(f'cannot verify role-batch SVG: {exc}')
    if errors:return fail('; '.join(errors))
    print('OK: role-batch-flow (19 representative item traces; nine exact SQL definitions, whole-target preflight and one final commit)')
    return 0


COMMANDS['role-batch-flow'] = check_role_batch_flow


def check_role_inquiry_flow() -> int:
    """Check token-claim administration and consistent filtered current role metadata."""
    path=f'{AUTHOR_DIR}/{AUTHOR_SPECS["03"]}/spec.md';md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    for n in ('status: in-review', 'approved_by: null', 'approved_at: null'):
        if n not in md:errors.append(f'role-inquiry spec missing {n!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for n in ('2026-11-07-api-review-design.md', 'exact PLATFORM_ADMIN in verified JWT role claims', 'positive signed 64-bit integers', 'nonnegative BIGINT',
            'one bound text searchPattern', 'Missing/malformed roles is generic 401', 'Grant withdrawal after token issuance leaves the old privilege usable',
            'same read-only repeatable-read snapshot', 'identical non-DELETED/id/searchPattern/rowStatus WHERE predicates',
            'an offset beyond the range returns items=[] with positive totals/pages', 'Sort by name then id ascending',
            'exactly roleId/name/description/rowStatus', 'exactly five data keys', 'integer quotient/remainder', 'Map the full response before COMMIT'):
        if n not in seq:
            errors.append(f'role-inquiry sequence note missing {n!r}')
    for n in ('QUERY - Get the platform administrator role','QUERY - Check platform administrator'):
        if n in md or n in wsd:errors.append('role inquiry authorization must not reload current assignments')
    ops=spec_database_operations(md);heads=('QUERY - Check current credential and user','QUERY - Get total items','QUERY - Get roles')
    if tuple(h for _,h,_ in ops)!=heads:errors.append('role inquiry needs credential/count/page in declared order')
    sql={h:re.sub(r'--[^\n]*','',s) for _,h,s in ops};filters=["WHERE r.row_status <> 'DELETED'","AND ('<sequence.id>' IS NULL OR r.id = '<sequence.id>')","AND ('<sequence.searchPattern>' IS NULL OR r.name ILIKE '<sequence.searchPattern>' OR r.description ILIKE '<sequence.searchPattern>')","AND ('<sequence.rowStatus>' IS NULL OR r.row_status = '<sequence.rowStatus>')"]
    required={heads[0]:['JOIN authen.m_user u ON u.id = at.user_id',"at.token = '<sequence.accessTokenHash>'","at.user_id = '<sequence.callerUserId>'","at.row_status = 'ACTIVE'","at.expired_at > '<sequence.now>'","u.row_status = 'ACTIVE'"],heads[1]:filters+['COUNT(r.id) as total_items'],heads[2]:filters+["LIMIT '<sequence.pageSize>' OFFSET '<sequence.offset>'"]}
    for h,ns in required.items():
        for n in ns:
            if n not in sql.get(h,''):errors.append(f'{h} missing {n!r}')
    def where(h):
        r=re.search(r'\bWHERE\b(.*?)(?:\bORDER BY\b|\bLIMIT\b|$)',sql.get(h,''),re.S);return normalize(r[1]) if r else None
    if where(heads[1])!=where(heads[2]):errors.append('role count/page WHERE predicates must be identical')
    projection=re.search(r'SELECT\s+(.*?)\s+FROM\s',sql.get(heads[2],''),re.S)
    if not projection or normalize(projection[1])!=normalize('r.id as role_id, r.name, r.description, r.row_status'):errors.append('role page returns exactly four role fields, no audit/assignment/caller data')
    if not re.search(r"ORDER BY r\.name, r\.id(?: ASC)?\s+LIMIT",sql.get(heads[2],'')):errors.append('role page requires name then unique ascending id order')
    if SEQUENCE_LOCK.search('\n'.join(sql.values())) or 'NOW()' in '\n'.join(sql.values()) or any(not q.lstrip().startswith('SELECT') for q in sql.values()):errors.append('role inquiry must use SELECT-only fresh-bound credential time, with no locks')
    actual,lifecycle=sequence_database_operations(wsd);errors+=lifecycle
    if actual!=[(t.split('.')[-1],h,q) for t,h,q in ops]:errors.append('role inquiry SQL differs character-for-character or execution order')
    lines=wsd.splitlines()
    for i,l in enumerate(lines):
        req=re.match(r'^( *)infra -> \w+: QUERY - ',l)
        if not req:continue
        pad=' '*(len(req[1])+8);j=i+3
        while j<len(lines) and lines[j].strip()!='end note':
            if lines[j] and not lines[j].startswith(pad):errors.append('role SQL must retain exact added presentation prefix and original SQL indentation')
            j+=1
    for _,h,_ in ops:
        if wsd.count('app -> infra: '+h+'\n')!=1:errors.append(f'{h} needs one Application request')
    for mat in re.finditer(r'(?m)^( *)infra -> (\w+): (QUERY - [^\n]+)\n',wsd):
        r=re.search(rf'{mat[2]} -> infra: Return ([^\n]+)\n.*?deactivate {mat[2]}\n\s*infra -> app: Return ([^\n]+)',wsd[mat.start():],re.S)
        if not r or r[1]!=r[2]:errors.append('role database result must return with the same meaning to Application')
    for n in ('Compute checked offset = (pageIndex - 1) * pageSize; reject numeric/offset overflow beyond nonnegative BIGINT','Verify JWT signature/issuer/audience/expiry/UUID sub and the roles claim as unique non-empty strings','callerUserId = verified sub; accessTokenHash = SHA-256 exact JWT','Bind omitted id/searchPattern/rowStatus as typed SQL NULL; supplied searchPattern = percent + search + percent, preserving ILIKE wildcards','Capture fresh server UTC now immediately before joined credential read; recheck JWT exp','JWT expired before fresh credential read','Missing/invalid JWT or malformed roles','Current token/user missing/inactive/revoked/expired/mismatched','alt totalItems = 0','Authorize once using exact case-sensitive PLATFORM_ADMIN in verified JWT roles; never reload current grants','No exact PLATFORM_ADMIN role claim','integer quotient plus nonzero remainder','items = []; skip page query; totalPages = 0','Require page row count = min(pageSize, max(0, totalItems-offset)); mismatch is internal failure','Map exactly roleId/name/description/rowStatus per row; required values non-null; exclude caller/assignment/token/hash/audit','items = []; retain positive totalItems/totalPages; no 404','data = exactly items/pageIndex/pageSize/totalItems/totalPages; echo validated page values; explicit empty arrays; finish full mapping'):
        if n not in wsd:errors.append(f'role inquiry sequence missing {n!r}')
    if wsd.count('Authorize once using exact')!=1:errors.append('role inquiry checks claims permission exactly once')
    for response in re.finditer(r'(?m)^( *)app -> api: HTTP [^\n]+\n',wsd):
        following=wsd[response.end():].splitlines()[:2]
        if len(following)!=2 or not following[0].strip().startswith('api -> page:') or not following[1].strip().startswith('page -> user:'):errors.append('all role inquiry responses must reach frontend and caller')
    traces,structure=login_sequence_paths(wsd);errors+=structure
    from collections import Counter
    outcomes=[];modes=Counter();unauthorized=[]
    for tr in traces:
        response=[e for e in tr if e.startswith('app -> api: HTTP ')];joined='\n'.join(tr)
        if len(response)!=1:errors.append('role inquiry trace needs one terminal outcome');continue
        code=int(response[0].split('HTTP ')[1].split()[0]);outcomes.append(code);queries=[e for e in tr if e.startswith('infra -> ')];begun=any(e.startswith('app -> infra: BEGIN') for e in tr)
        def ordered(*parts):
            pos=[next((i for i,e in enumerate(tr) if p in e),-1) for p in parts]
            return -1 not in pos and pos==sorted(set(pos))
        if queries and not ordered('Compute checked offset','Verify JWT','callerUserId = verified sub','Bind omitted id/searchPattern','BEGIN REPEATABLE READ READ ONLY','Capture fresh server UTC now',heads[0]):errors.append('role SQL needs checked pagination, verified caller and fresh read-only credential snapshot')
        if 'Authorize once using exact' in joined and not ordered(heads[0],'Authorize once using exact'):errors.append('claims permission requires valid current credential')
        if heads[1] in joined and not ordered('Authorize once using exact',heads[1]):errors.append('no role count may precede claims permission')
        if heads[2] in joined and not ordered(heads[1],heads[2]):errors.append('role page must follow its identical-filter count')
        if any(': QUERY' not in e for e in queries):errors.append('role inquiry may never write')
        if code==200:
            mode='zero' if 'skip page query' in joined else 'beyond' if 'retain positive totalItems' in joined else 'rows';modes[mode]+=1
            if len(queries)!=(2 if mode=='zero' else 3):errors.append('zero role count skips page query; positive count queries page')
            if not ordered(heads[1],'data = exactly items','app -> infra: COMMIT','HTTP 200') or 'ROLLBACK' in joined:errors.append('success needs complete mapped read-only response then commit')
            if mode!='zero' and 'Require page row count' not in joined:errors.append('positive role count must validate page cardinality')
            if 'all five pagination keys' not in response[0]:errors.append('role inquiry success must include every pagination key')
        elif begun:
            if not ordered('BEGIN','ROLLBACK',f'HTTP {code}') or 'app -> infra: COMMIT' in joined:errors.append('role inquiry transaction failures roll back before response')
            if code in (401,403) and len(queries)>1:errors.append('invalid credentials or non-admin must not count/read roles')
        elif code not in (400,401) or queries:errors.append('pre-BEGIN role inquiry reject must be no-SQL validation/JWT error')
        if code==401:unauthorized.append(len(queries))
    if Counter(outcomes)!=Counter({400:1,401:3,403:1,200:3,408:1,500:1}) or modes!=Counter({'zero':1,'rows':1,'beyond':1}) or sorted(unauthorized)!=[0,0,1]:errors.append(f'expected 10 role inquiry terminal traces, got {dict(Counter(outcomes))}, modes={dict(modes)},401 SQL={unauthorized}')
    for title,code in {'Success':200,'Success - By Id':200,'Success - Not Found':200,'Success - Page Beyond Range':200,'Fail - Bad Request':400,'Fail - Unauthorized':401,'Fail - Forbidden':403,'Fail - Request Timeout':408,'Fail - Internal Server Error':500}.items():
        try:
            obj=author_json(md,title);status=obj['status']
            if status['code']!=code or code==500 and 'bizCode' in status:errors.append(f'{title} role inquiry envelope incorrect')
            if code==200:
                d=obj['data'];keys={'items','pageIndex','pageSize','totalItems','totalPages'}
                if set(d)!=keys or type(d['items']) is not list:errors.append(f'{title} needs five keys and items array');continue
                if any(type(d[k]) is not int for k in keys-{'items'}) or not 1<=d['pageIndex']<=2**63-1 or not 1<=d['pageSize']<=100 or d['totalItems']<0:errors.append(f'{title} invalid role page integers');continue
                total=d['totalItems'];size=d['pageSize'];offset=(d['pageIndex']-1)*size;pages=total//size+int(total%size!=0)
                if offset>2**63-1 or d['totalPages']!=pages or len(d['items'])!=min(size,max(0,total-offset)):errors.append(f'{title} page cardinality/totals incorrect')
                ids=[]
                for item in d['items']:
                    if set(item)!={'roleId','name','description','rowStatus'} or any(v is None for v in item.values()) or item['rowStatus']=='DELETED':errors.append(f'{title} role fields missing/null/leaked/DELETED')
                    ids.append(item['roleId'])
                if len(ids)!=len(set(ids)):errors.append(f'{title} repeats role id')
                if title=='Success - Page Beyond Range' and (not total or d['items'] or d['pageIndex']<=pages):errors.append('beyond-range role example must retain positive totals')
        except (AttributeError,TypeError,KeyError,IndexError,ValueError):errors.append(f'{title} role inquiry example missing/malformed')
    errors+=json_blocks_parse(md);errors+=table_lines_aligned(md)
    if '--rendered-svg' in sys.argv:
        import xml.etree.ElementTree as ET
        try:
            root=ET.parse(sys.argv[sys.argv.index('--rendered-svg')+1]).getroot();wanted=Counter(' '.join(l.split()) for _,_,q in ops for l in q.splitlines() if l.strip());visible=Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'));missing=wanted-visible
            if missing:errors.append(f'rendered role-inquiry SQL missing {sum(missing.values())} lines')
            else:print(f'OK: rendered role-inquiry SQL ({sum(wanted.values())}/{sum(wanted.values())} visible lines)')
        except (IndexError,OSError,ET.ParseError) as exc:errors.append(f'cannot verify role-inquiry SVG: {exc}')
    if errors:return fail('; '.join(errors))
    print('OK: role-inquiry-flow (10 terminal traces; exact SQL, claim administration and consistent filtered pagination)')
    return 0


COMMANDS['role-inquiry-flow'] = check_role_inquiry_flow


def author_inquiry_flow(key: str, page_head: str, columns: str, forbidden: str, path: str = '', tail_heads: tuple = ()) -> int:
    """Check only what parity checks cannot: claims-based admin, read-only snapshot, step order, one commit, identical count/page FROM and WHERE."""
    path=path or f'{AUTHOR_DIR}/{AUTHOR_SPECS[key]}/spec.md';md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    if 'QUERY - Get the platform administrator role' in md+wsd or 'QUERY - Check platform administrator' in md+wsd:errors.append('must not reload live grants')
    ops=spec_database_operations(md);heads=[h for _,h,_ in ops]
    if heads!=['QUERY - Check current credential and user','QUERY - Get total items',page_head,*tail_heads]:errors.append('needs credential/count/page SQL in order')
    sql='\n'.join(q for _,_,q in ops)
    if SEQUENCE_LOCK.search(sql) or re.search(r'\b(?:INSERT|UPDATE|DELETE)\b',sql):errors.append('inquiry must be read-only without locks')
    where=lambda h:next((normalize(re.search(r'\bFROM\b(.*?)(?:\bORDER BY\b|\bLIMIT\b|$)',q,re.S)[1]) for _,k,q in ops if k==h),None)
    if where('QUERY - Get total items')!=where(page_head):errors.append('count and page FROM/JOIN/WHERE must be identical')
    order=['BEGIN REPEATABLE READ READ ONLY','app -> infra: QUERY - Check current credential and user','Authorize once using exact','app -> infra: QUERY - Get total items','app -> infra: '+page_head,'app -> infra: COMMIT']
    pos=[wsd.find(x) for x in order]
    if -1 in pos or pos!=sorted(pos):errors.append('steps must run BEGIN read-only, credential, one permission decision, count, page, COMMIT')
    if wsd.count('Authorize once using exact')!=1 or wsd.count('app -> infra: COMMIT')!=1:errors.append('exactly one permission decision and one COMMIT')
    lines=wsd.splitlines();begin=next((i for i,l in enumerate(lines) if 'BEGIN REPEATABLE READ' in l),len(lines))
    for i,l in enumerate(lines):
        if i>begin and re.search(r'app -> api: HTTP (?:401|403|408|500)',l) and 'app -> infra: ROLLBACK' not in lines[i-1]:errors.append(f'post-BEGIN rejection needs ROLLBACK first: {l.strip()}')
    if not md.startswith('---\nname:') or 'status: in-review\napproved_by: null\napproved_at: null' not in md:errors.append('spec stays in-review until approved')
    page=next((q for _,k,q in ops if k==page_head),'');proj=re.search(r'SELECT\s+(.*?)\s+FROM\s',page,re.S)
    if not proj or normalize(proj[1])!=normalize(columns):errors.append('page returns exactly the documented columns')
    errors+=[f'claims wording missing {n!r}' for n in ('verified token roles',) if n not in md]
    errors+=[f'claims wording missing in the sequence note {n!r}' for n in ('verify JWT/roles (401)',) if n not in ' '.join(wsd.split())]
    if forbidden not in wsd or 'skip page query' not in wsd:errors.append('403 text and zero-count page skip must be drawn')
    if errors:return fail('; '.join(errors))
    print(f'OK: {AUTHOR_SPECS[key][3:]}-flow (claims-only admin, read-only snapshot, ordered count/page, one commit)')
    return 0


def check_scope_inquiry_flow() -> int:
    return author_inquiry_flow('09','QUERY - Get scopes','s.id as scope_id, s.scope, s.name, s.description, s.row_status','You do not have permission to read scopes.')


COMMANDS['scope-inquiry-flow'] = check_scope_inquiry_flow


def check_user_role_inquiry_flow() -> int:
    return author_inquiry_flow('11','QUERY - Get user roles','ur.id as user_role_id, ur.user_id, u.display_name, ur.role_id, r.name as role_name, ur.row_status','You do not have permission to read user roles.')


COMMANDS['user-role-inquiry-flow'] = check_user_role_inquiry_flow


def check_consent_inquiry_flow() -> int:
    """Consent management list: the shared inquiry invariants plus the consent type names read after the page, for every type status."""
    path='e-commerce/doc/api/consent/03-inquiry-consent/spec.md'
    if author_inquiry_flow('03','QUERY - Get consents','c.id as consent_id, c.code, c.consent_type_id, c.consent_version, c.consent_name, c.consent_description, c.effective_at, c.expired_at, c.is_required, c.row_status, c.body','You do not have permission to read consents.',path,('QUERY - Get consent type',)):return 1
    md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));sql={h:q for _,h,q in spec_database_operations(md)};errors=[]
    type_sql=sql.get('QUERY - Get consent type','');page_sql=sql.get('QUERY - Get consents','')
    if "ANY ('<sequence.consentTypeIds>'::UUID[])" not in type_sql or 'row_status' in type_sql:errors.append('consent type names are read with a bound typed UUID[] and no status filter (Q19)')
    if 'ORDER BY c.created_at DESC, c.id' not in page_sql or "c.row_status <> 'DELETED'" not in page_sql or 'expired_at' in page_sql.split('WHERE',1)[-1] or 'effective_at' in page_sql.split('WHERE',1)[-1]:errors.append('the page keeps every non-DELETED consent, expired ones included, ordered by created_at descending then id')
    pos=[wsd.find(x) for x in ('app -> infra: QUERY - Get consents','app -> infra: QUERY - Get consent type','app -> infra: COMMIT')]
    if -1 in pos or pos!=sorted(pos):errors.append('the consent type names are read after the page and before COMMIT')
    if errors:return fail('; '.join(errors))
    print('OK: consent-inquiry-flow (administrator-only list of every non-DELETED consent with type names of any status)')
    return 0


COMMANDS['consent-inquiry-flow'] = check_consent_inquiry_flow


def check_author_roles_claim() -> int:
    """The roles claim of the JWT payload of 2026-11-13 is a list of role names; the author 01-11 diagrams must say so and not the old structured form."""
    errors=[]
    for key in ("01","02","03","04","05","06","07","08","09","10","11"):
        path=f'{AUTHOR_DIR}/{AUTHOR_SPECS[key]}/sequence.wsd';text=' '.join(read(path).split())
        for needle in ('Verify JWT signature/issuer/audience/expiry/UUID sub and the roles claim as unique non-empty strings','roles must be an array of unique non-empty role names (JWT payload of 2026-11-13), including []'):
            if needle not in text:errors.append(f'{path} must say {needle!r}')
        for old in ('structured unique roleIds','structured roles','structured unique roles','UUID roleId','roleId/non-empty','role object has UUID'):
            if old in text:errors.append(f'{path} still says the old roles claim form {old!r}')
    if errors:return fail('; '.join(errors))
    print('OK: author-roles-claim (eleven author diagrams say that roles is a list of role names)')
    return 0


COMMANDS['author-roles-claim'] = check_author_roles_claim
def check_consent_upsert_flow() -> int:
    """Check only what parity checks cannot: claims-only admin, caller -> type -> consent lock order, DELETED final, one decision and commit, rollbacks."""
    path='e-commerce/doc/api/consent/02-upsert-consent/spec.md';md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    if 'QUERY - Get the platform administrator role' in md+wsd or 'QUERY - Check platform administrator' in md+wsd or re.search(r'infra -> (?:m_role|t_user_role):',wsd):errors.append('must not read the author tables')
    if not md.startswith('---\nname:') or 'status: in-review\napproved_by: null\napproved_at: null' not in md:errors.append('spec stays in-review until approved')
    ops=spec_database_operations(md);heads=[h for _,h,_ in ops]
    want=['QUERY - Lock the caller user','QUERY - Check current credential and user','QUERY - Lock the consent type','QUERY - Lock existing consent','QUERY - Check duplicate code','INSERT - Create consent','UPDATE - Update or delete consent']
    if heads!=want:errors.append('needs the seven caller/credential/type/consent/duplicate/write SQL definitions in order')
    sql={h:q for _,h,q in ops}
    for h in (want[0],want[2],want[3]):
        if 'FOR UPDATE' not in sql.get(h,''):errors.append(f'{h} must lock with FOR UPDATE')
    if any(SEQUENCE_LOCK.search(sql.get(h,'')) for h in (want[1],want[4],want[5],want[6])) or 'NOW()' in '\n'.join(sql.values()):errors.append('only the three row locks may lock; times are bound')
    for h,needles in {want[3]:["c.row_status <> 'DELETED'",'c.consent_type_id'],want[4]:["('<sequence.id>' IS NULL OR c.id <> '<sequence.id>')"],want[5]:['created_at',"'<sequence.now>'",'RETURNING id as consent_id'],want[6]:["updated_at = '<sequence.now>'","AND row_status <> 'DELETED'",'RETURNING id as consent_id']}.items():
        errors+=[f'{h} missing {n!r}' for n in needles if n not in sql.get(h,'')]
    if 'row_status' in sql.get(want[4],''):errors.append('the duplicate code check counts every status, a DELETED consent keeps its code')
    order=['app -> infra: '+h for h in want[:4]]+['Authorize once','app -> infra: QUERY - Check duplicate code','app -> infra: INSERT - Create consent','app -> infra: COMMIT']
    pos=[wsd.find(x) for x in order]
    if -1 in pos or pos!=sorted(pos):errors.append('steps must run caller lock, credential, type lock, consent lock, one permission decision, duplicate, write, COMMIT')
    if wsd.count('Authorize once')!=1 or wsd.count('app -> infra: COMMIT')!=1:errors.append('exactly one permission decision and one COMMIT')
    lines=wsd.splitlines();begin=next((i for i,l in enumerate(lines) if 'BEGIN READ COMMITTED' in l),len(lines))
    for i,l in enumerate(lines):
        if i>begin and re.search(r'app -> api: HTTP (?:400|401|403|404|408|409|500)',l) and 'app -> infra: ROLLBACK' not in lines[i-1]:errors.append(f'post-BEGIN rejection needs ROLLBACK first: {l.strip()}')
    for n in ('HTTP 404 E10004 Consent not found.','HTTP 404 E10005 Consent type not found or not ACTIVE.','HTTP 403 E10009 You do not have permission to manage consents.','HTTP 409 E10003 Consent code already exists.','expiredAt later than effectiveAt','The request gives the consent when it inserts, or sets ACTIVE on a locked consent that is not ACTIVE, or changes the consent type of an ACTIVE consent','delete, archive, deactivate or lock needs no ACTIVE type','The consent type row is missing, or the request gives the consent and the type is not ACTIVE'):
        if n not in wsd:errors.append(f'sequence missing {n!r}')
    if 'a consent of a type that is not ACTIVE can still be deleted, archived, deactivated or locked' not in md:errors.append('the spec must say that a consent of a closed type can still be deleted or archived (owner answer of 2026-11-14)')
    for title,code in {'Fail - Bad Request Period':400,'Fail - Not Found Consent Type':404,'Fail - Internal Server Error':500}.items():
        try:
            st=authen_json(md,title)['status']
            if st['code']!=code or (code==500)==('bizCode' in st):errors.append(f'{title} example envelope is wrong')
        except (TypeError,KeyError,ValueError):errors.append(f'missing {title} example')
    if errors:return fail('; '.join(errors))
    print('OK: consent-upsert-flow (claims-only admin, caller/type/consent lock order, DELETED final, one decision and commit)')
    return 0


COMMANDS['consent-upsert-flow'] = check_consent_upsert_flow
def check_user_role_upsert_flow() -> int:
    """Check only what parity checks cannot: claims-only admin, user -> role -> assignment lock order, one decision/commit, rollbacks, missing-user 404."""
    path=f'{AUTHOR_DIR}/{AUTHOR_SPECS["10"]}/spec.md';md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    if 'QUERY - Get the platform administrator role' in md+wsd or 'QUERY - Check platform administrator' in md+wsd:errors.append('must not reload live caller grants')
    if not md.startswith('---\nname:') or 'status: in-review\napproved_by: null\napproved_at: null' not in md:errors.append('spec stays in-review until approved')
    ops=spec_database_operations(md);heads=[h for _,h,_ in ops]
    want=['QUERY - Lock the users','QUERY - Check current credential and user','QUERY - Lock the role','QUERY - Lock existing user role','QUERY - Check duplicate user role','INSERT - Create user role','UPDATE - Update, archive or delete user role','QUERY - Count the platform administrators after the write']
    if heads!=want:errors.append('needs the eight caller/user/role/assignment/write/count SQL definitions in order')
    sql={h:q for _,h,q in ops}
    for h in want[:4]:
        if 'FOR UPDATE' not in sql.get(h,'') and h!=want[1]:errors.append(f'{h} must lock with FOR UPDATE')
    if "ANY ('<sequence.userIds>'::UUID[])" not in sql.get(want[0],'') or 'ORDER BY u.id\nFOR UPDATE' not in sql.get(want[0],''):errors.append('users lock must take caller and target in ascending id order')
    for h,needles in {want[3]:["ur.row_status <> 'DELETED'"],want[4]:["('<sequence.id>' IS NULL OR ur.id <> '<sequence.id>')","ur.row_status <> 'DELETED'"],want[5]:['created_at',"'<sequence.now>'",'RETURNING id as user_role_id'],want[6]:["updated_at = '<sequence.now>'","AND row_status <> 'DELETED'",'RETURNING id as user_role_id'],want[7]:["r.name = 'PLATFORM_ADMIN'","r.row_status = 'ACTIVE'","u.row_status = 'ACTIVE'","ur.row_status = 'ACTIVE'"]}.items():
        errors+=[f'{h} missing {n!r}' for n in needles if n not in sql.get(h,'')]
    try:
        if 'bizCode' in author_json(md,'Fail - Internal Server Error')['status']:errors.append('500 example must omit bizCode')
    except (TypeError,KeyError):errors.append('500 example missing')
    if any(SEQUENCE_LOCK.search(sql.get(h,'')) for h in want[1:2]+want[4:]) or 'NOW()' in '\n'.join(sql.values()):errors.append('only the three row locks may lock; times are bound')
    order=['app -> infra: '+h for h in want[:5]]+['app -> infra: '+want[5],'app -> infra: '+want[7],'app -> infra: COMMIT']
    pos=[wsd.find(x) for x in order]
    if -1 in pos or pos!=sorted(pos):errors.append('steps must run users lock, credential, role lock, assignment lock, duplicate, write, administrator count, COMMIT')
    if not (wsd.find('Authorize once')<wsd.find('app -> infra: '+want[4]) and wsd.find('Find the target user')<wsd.find('app -> infra: '+want[2])):errors.append('permission precedes the duplicate check and target-user existence precedes the role lock')
    if wsd.count('Authorize once')!=1 or wsd.count('app -> infra: COMMIT')!=1:errors.append('exactly one permission decision and one COMMIT')
    lines=wsd.splitlines();begin=next((i for i,l in enumerate(lines) if 'BEGIN READ COMMITTED' in l),len(lines))
    for i,l in enumerate(lines):
        if i>begin and re.search(r'app -> api: HTTP (?:400|401|403|404|408|409|500)',l) and 'app -> infra: ROLLBACK' not in lines[i-1]:errors.append(f'post-BEGIN rejection needs ROLLBACK first: {l.strip()}')
    for n in ('HTTP 404 E10005 User not found.','HTTP 404 E10005 User or role not found or not ACTIVE.','HTTP 409 E10006 The platform must keep at least one administrator.','HTTP 403 E10009 You do not have permission to assign roles.'):
        if n not in wsd:errors.append(f'sequence missing {n!r}')
    if errors:return fail('; '.join(errors))
    print('OK: user-role-upsert-flow (claims-only admin, ordered user/role/assignment locks, one decision and commit)')
    return 0


COMMANDS['user-role-upsert-flow'] = check_user_role_upsert_flow


def check_address_upsert_flow() -> int:
    """Check caller-scoped address lifecycle, quota and atomic default transitions."""
    path=AUTHEN_SPECS['09'];md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    for needle in ('status: in-review', 'approved_by: null', 'approved_at: null'):
        if needle not in md:errors.append(f'address-upsert spec missing {needle!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for needle in ('Q21 approved by the product owner', 'ตอบ 400 เมื่อ Delete ส่ง true (แนะนำ)', 'mandatory non-blank strings for insert, update and delete',
            'first ACTIVE, not the first physical/historical row', 'False or omitted preserves an existing ACTIVE',
            'limit is configurable and applies only to insert', 'Count every non-DELETED row regardless of lifecycle', 'fresh server UTC now', 'id = SQL NULL',
            'Compute shouldPromote = wasDefault AND new rowStatus is not ACTIVE', 'Clear-before-write', 'zero rows means 404 with full ROLLBACK',
            'Delete 204 No Content has no response body', 'All target/default changes are one transaction'):
        if needle not in seq:
            errors.append(f'address-upsert sequence note missing {needle!r}')
    operations=spec_database_operations(md)
    expected=('QUERY - Lock the user','QUERY - Check the current access token','QUERY - Check existing address','QUERY - Count addresses','QUERY - Check an ACTIVE address exists','UPDATE - Clear the old default','INSERT - Create user address','UPDATE - Update or delete user address','UPDATE - Promote another default address')
    if tuple(h for _,h,_ in operations)!=expected:errors.append('address contract needs nine SQL definitions in orchestration/branch order')
    sql={h:re.sub(r'--[^\n]*','',s) for _,h,s in operations}
    required={expected[0]:["u.id = '<sequence.userId>'","u.row_status = 'ACTIVE'",'FOR UPDATE'],
              expected[1]:["at.token = '<sequence.accessTokenHash>'","at.user_id = '<sequence.userId>'","at.row_status = 'ACTIVE'","at.expired_at > '<sequence.now>'"],
              expected[2]:['ua.id as user_address_id','ua.is_default',"WHERE ua.id = '<sequence.id>'","AND ua.user_id = '<sequence.userId>'","AND ua.row_status <> 'DELETED'"],
              expected[3]:['COUNT(ua.id) as addresses',"ua.user_id = '<sequence.userId>'","ua.row_status <> 'DELETED'","AND '<sequence.id>' IS NULL"],
              expected[4]:["ua.user_id = '<sequence.userId>'","ua.row_status = 'ACTIVE'","('<sequence.id>' IS NULL OR ua.id <> '<sequence.id>')","AND '<sequence.rowStatus>' = 'ACTIVE'"],
              expected[5]:["WHERE user_id = '<sequence.userId>'",'AND is_default',"AND row_status <> 'DELETED'","('<sequence.id>' IS NULL OR id <> '<sequence.id>')","AND '<sequence.isDefault>'",'is_default = FALSE'],
              expected[6]:['created_by,\n    created_at,\n    row_status,\n    user_id',"'<sequence.userId>',\n    '<sequence.now>',\n    '<sequence.rowStatus>',\n    '<sequence.userId>'",'RETURNING id as user_address_id'],
              expected[7]:["WHERE id = '<sequence.id>'","AND user_id = '<sequence.userId>'","AND row_status <> 'DELETED'",'RETURNING id as user_address_id'],
              expected[8]:['is_default = TRUE',"ua.user_id = '<sequence.userId>'","ua.row_status = 'ACTIVE'",'ORDER BY COALESCE(ua.updated_at, ua.created_at) DESC, ua.id','LIMIT 1',"AND user_id = '<sequence.userId>'","AND row_status = 'ACTIVE'","AND '<sequence.shouldPromote>'",'RETURNING id as user_address_id']}
    for h in (expected[5],expected[7],expected[8]):required[h]+=["updated_by = '<sequence.userId>'","updated_at = '<sequence.now>'"]
    for h in (expected[6],expected[7]):
        required[h]+=["'<sequence.title>'","'<sequence.isDefault>'"]+[f"'<sequence.{v}Bytes>'" for v in ('address','city','state','postalCode','country')]
    for h,needles in required.items():
        for needle in needles:
            if needle not in sql.get(h,''):errors.append(f'{h} missing {needle}')
    if re.search(r"row_status\s*=\s*'ACTIVE'",sql.get(expected[3],'')):errors.append('quota must count every non-DELETED status')
    if 'NOW()' in '\n'.join(sql.values()) or any(t not in ('authen.m_user','authen.t_user_access_token','authen.t_user_address') for t,_,_ in operations):errors.append('address needs fresh bound now and only caller/address credential tables')
    actual,lifecycle=sequence_database_operations(wsd);errors+=lifecycle
    from collections import Counter
    definitions={(t.split('.')[-1],h,s) for t,h,s in operations}
    if set(actual)!=definitions:errors.append('every reused address SQL block must match its spec definition character-for-character')
    expected_reuse=Counter({h:2 if h in expected[7:] else 1 for h in expected})
    if Counter(h for _,h,_ in actual)!=expected_reuse:errors.append('UPDATE/promotion must appear in both existing-id branches; other SQL blocks once')
    errors+=sequence_login_standard_errors(wsd)
    for _,heading,_ in operations:
        requests=list(re.finditer(rf'app -> infra: {re.escape(heading)}\n',wsd));blocks=list(re.finditer(rf'infra -> (\w+): {re.escape(heading)}\n.*?\1 -> infra: Return ([^\n]+)\n.*?deactivate \1\n\s*infra -> app: Return ([^\n]+)',wsd,re.S))
        if len(requests)!=expected_reuse[heading] or len(blocks)!=expected_reuse[heading] or any(x[2]!=x[3] for x in blocks):errors.append(f'{heading} needs matching Application request and database/result mappings on every reuse')
    for needle in ('Q21 reject explicit isDefault=true for INACTIVE or DELETED; reject insert DELETED',
                   'Verify JWT signature/issuer/audience/expiry/UUID sub','userId = verified sub; accessTokenHash = SHA-256 exact JWT',
                   'id = supplied UUID or server SQL NULL for insert; omitted rowStatus = ACTIVE; preserve requestedTrue separately',
                   'Capture fresh server UTC now after user lock; recheck JWT exp',
                   'alt Supplied id and no owned non-DELETED target','wasDefault = returned is_default or false for insert',
                   'alt Insert id absent and addresses >= 10','otherActiveExists = returned rows not empty',
                   'isDefault = rowStatus ACTIVE AND (requestedTrue OR wasDefault OR NOT otherActiveExists)',
                   'shouldPromote = wasDefault AND rowStatus not ACTIVE; flags are server-derived, never caller flags',
                   'alt Insert with id absent','else Delete existing id with rowStatus DELETED','else Update existing id with rowStatus ACTIVE or INACTIVE'):
        if needle not in wsd:errors.append(f'address sequence missing {needle!r}')
    traces,structure=login_sequence_paths(wsd);errors+=structure
    outcomes=[];unauthorized=[]
    for trace in traces:
        response=[e for e in trace if e.startswith('app -> api: HTTP ')]
        if len(response)!=1:errors.append('address trace needs one outcome; abort must not reach success');continue
        code=int(response[0].split('HTTP ')[1].split()[0]);outcomes.append(code)
        def ordered(*parts):
            pos=[next((i for i,e in enumerate(trace) if part in e),-1) for part in parts]
            return -1 not in pos and pos==sorted(set(pos))
        queries=[e for e in trace if e.startswith('infra -> ')];writes=[e for e in queries if ': UPDATE' in e or ': INSERT' in e];begun=any(e.startswith('app -> infra: BEGIN') for e in trace)
        if queries and not ordered('Q21 reject explicit isDefault=true','Verify JWT','userId = verified sub','BEGIN READ COMMITTED',expected[0]):errors.append('address SQL needs verified identity and user-first transaction')
        if any(expected[1] in e for e in trace) and not ordered(expected[0],'Capture fresh server UTC now',expected[1]):errors.append('stored credential read must follow user lock and fresh time')
        if writes and not ordered(expected[1],expected[2],expected[3],expected[4],'isDefault = rowStatus ACTIVE','shouldPromote = wasDefault',expected[5]):errors.append('default/target mutations require fresh credential, owned target, quota and server-computed flags')
        if code in (200,201,204):
            target=expected[6] if code==201 else expected[7]
            need=(expected[5],target) if code==201 else (expected[5],target,expected[8])
            if not ordered(*need,'app -> infra: COMMIT',f'HTTP {code}') or any('ROLLBACK' in e for e in trace):errors.append('success must commit all required target/default changes first')
            if sum(target in e for e in writes)!=1 or (code==201 and len(writes)!=2) or (code!=201 and len(writes)!=3):errors.append('insert/update/delete must run mutually exclusive target SQL and appropriate promotion')
            if code==204 and 'no response body' not in response[0] or code!=204 and 'data.userAddressId only' not in response[0]:errors.append('incorrect address success payload shape')
        elif begun:
            if not ordered('BEGIN','ROLLBACK',f'HTTP {code}') or any(e=='app -> infra: COMMIT' for e in trace):errors.append('address failure must roll back every partial/default mutation before response')
            if code==401 and writes:errors.append('invalid credential must not change any address')
            if code==400 and writes:errors.append('quota rejection must precede clearing defaults')
        elif code not in (400,401) or queries:errors.append('early input/JWT rejection must execute no SQL')
        if code==401:unauthorized.append(len(queries))
    if Counter(outcomes)!=Counter({200:1,201:1,204:1,400:2,401:3,404:3,408:1,500:2}) or sorted(unauthorized)!=[0,1,2]:errors.append(f'incomplete address paths: {dict(Counter(outcomes))}; 401 SQL={unauthorized}')
    for title,code in {'Success - Insert':201,'Success - Update':200,'Fail - Bad Request':400,'Fail - Bad Request Row Status':400,'Fail - Bad Request Limit':400,'Fail - Bad Request Default':400,'Fail - Unauthorized':401,'Fail - Not Found':404,'Fail - Request Timeout':408,'Fail - Internal Server Error':500}.items():
        try:
            obj=authen_json(md,title);status=obj['status']
            if status['code']!=code or code==500 and 'bizCode' in status:errors.append(f'incorrect address {title} envelope')
            if code in (200,201) and set(obj.get('data',{}))!={'userAddressId'}:errors.append('address success returns only target address id')
        except (TypeError,KeyError,ValueError):errors.append(f'missing address {title} example')
    try:
        body=json.loads(re.search(r'##### Delete\n\n```JSON\n(.*?)```',md,re.S)[1])
        if body.get('isDefault') is True:errors.append('Q21 Delete example must not send true')
    except (TypeError,KeyError,ValueError):errors.append('missing Delete request example')
    delete=md.split('#### Success - Delete',1)[-1].split('#### Fail',1)[0]
    if 'HTTP 204, no response body' not in delete or '```JSON' in delete:errors.append('delete must return 204 without JSON body')
    errors+=json_blocks_parse(md);errors+=table_lines_aligned(md)
    if '--rendered-svg' in sys.argv:
        import xml.etree.ElementTree as ET
        try:
            root=ET.parse(sys.argv[sys.argv.index('--rendered-svg')+1]).getroot()
            expected_lines=Counter(' '.join(l.split()) for _,_,s in actual for l in s.splitlines() if l.strip())
            visible=Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'))
            missing=expected_lines-visible
            if missing:errors.append(f'rendered address SQL missing {sum(missing.values())} lines')
            else:print(f'OK: rendered address SQL ({sum(expected_lines.values())}/{sum(expected_lines.values())} visible lines including reused blocks)')
        except (IndexError,OSError,ET.ParseError) as exc:errors.append(f'cannot verify address SVG: {exc}')
    if errors:return fail('; '.join(errors))
    print('OK: address-upsert-flow (14 terminal traces; nine exact SQL definitions, Q21 and atomic quota/default transitions)')
    return 0


COMMANDS['address-upsert-flow'] = check_address_upsert_flow


def check_logout_flow() -> int:
    """Check fresh post-lock authorization and atomic revocation of the complete caller session."""
    path=AUTHEN_SPECS['06'];md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    for needle in ('Q13',):
        if needle not in md:errors.append(f'logout rule missing {needle!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for needle in ('BEGIN READ COMMITTED', 'capture fresh server UTC now after the lock', 'No token UPDATE may run before the user lock',
            'sessionId comes only from the post-lock access-token row', 'Sessions of other devices are not changed.', 'Other users are unaffected',
            'If refresh commits first', 'If logout commits first', 'A second concurrent logout waits', 'Both token-table changes are one transaction',
            'Zero refresh rows is allowed', 'unexpected zero access-row update', 'COMMIT must succeed before 200',
            'A lost response after commit does not undo logout'):
        if needle not in seq:
            errors.append(f'logout sequence note missing {needle!r}')
    fm=md.split('---',2)[1] if md.startswith('---\n') else ''
    state=re.search(r'^status: (draft|in-review|approved)$',fm,re.M)
    if not state:errors.append('logout needs approval metadata')
    for field in ('approved_by','approved_at'):
        value=re.search(rf'^{field}: (.+)$',fm,re.M)
        if not value or (state and ((state[1]=='approved')==(value[1]=='null'))):errors.append(f'inconsistent logout {field}')
    operations=spec_database_operations(md)
    expected=('QUERY - Lock the user','QUERY - Get the session of the access token','UPDATE - Close the access tokens of the session','UPDATE - Close the refresh tokens of the session')
    if tuple(h for _,h,_ in operations)!=expected:errors.append('logout needs user lock, fresh token/session and both closures in execution order')
    sql={h:re.sub(r'--[^\n]*','',s) for _,h,s in operations}
    required={expected[0]:["u.id = '<sequence.userId>'", "u.row_status = 'ACTIVE'", 'FOR UPDATE'],
              expected[1]:['at.session_id', "at.token = '<sequence.accessTokenHash>'", "at.user_id = '<sequence.userId>'", "at.row_status = 'ACTIVE'", "at.expired_at > '<sequence.now>'"]}
    for h in expected[2:]:required[h]=["updated_by = '<sequence.userId>'", "updated_at = '<sequence.now>'", "row_status = 'INACTIVE'", "WHERE session_id = '<sequence.sessionId>'", "AND user_id = '<sequence.userId>'", "AND row_status = 'ACTIVE'"]
    for h,needles in required.items():
        for needle in needles:
            if needle not in sql.get(h,''):errors.append(f'{h} missing {needle}')
    for h in expected[2:]:
        statement=sql.get(h,'')
        if re.search(r'\bexpired_at\b|\btoken\s*=',statement):errors.append('logout closes all ACTIVE session rows, not just unexpired/presented token')
    if 'NOW()' in '\n'.join(sql.values()) or any(t.startswith('author.') or h.startswith('INSERT') for t,h,_ in operations):errors.append('logout must use post-lock now, issue nothing and require no live role lookup')
    actual,lifecycle=sequence_database_operations(wsd);errors+=lifecycle
    if [(t.split('.')[-1],h,normalize(s)) for t,h,s in operations]!=[(t,h,normalize(s)) for t,h,s in actual]:errors.append('logout spec/sequence SQL differs')
    for _,heading,_ in operations:
        if f'app -> infra: {heading}' not in wsd:errors.append(f'{heading} needs Application request')
        match=re.search(rf'infra -> (\w+): {re.escape(heading)}\n.*?deactivate \1\n([^\n]+)',wsd,re.S)
        if not match or not match[2].strip().startswith('infra -> app: Return '):errors.append(f'{heading} needs result returned to Application')
    for needle in ('Verify JWT signature/issuer/audience/expiry/UUID sub',
                   'userId = verified sub; accessTokenHash = SHA-256 exact JWT',
                   'Capture fresh server UTC now after user lock; recheck JWT exp',
                   'sessionId = returned stored session_id; never request/JWT session input',
                   'alt accessClosedCount > 0','else Unexpected accessClosedCount = 0',
                   'refreshClosedCount may be zero; both table changes remain atomic',
                   'else Token missing, revoked, expired, mismatched or JWT expired during wait'):
        if needle not in wsd:errors.append(f'logout sequence missing guard/mapping {needle!r}')
    if 'TODO(author)' in wsd:errors.append('logout sequence must be complete')
    traces,structure=login_sequence_paths(wsd);errors+=structure
    from collections import Counter
    outcomes=[];unauthorized_queries=[]
    for trace in traces:
        response=[e for e in trace if e.startswith('app -> api: HTTP ')]
        if len(response)!=1:errors.append('each logout trace needs one outcome');continue
        code=int(response[0].split('HTTP ')[1].split()[0]);outcomes.append(code)
        def ordered(*parts):
            pos=[next((i for i,e in enumerate(trace) if part in e),-1) for part in parts]
            return -1 not in pos and pos==sorted(set(pos))
        begun=any(e.startswith('app -> infra: BEGIN') for e in trace)
        queries=[e for e in trace if e.startswith('infra -> ')]
        updates=[e for e in queries if ': UPDATE' in e]
        if any(expected[1] in e for e in trace) and not ordered('BEGIN',expected[0],'Capture fresh server UTC now',expected[1]):errors.append('stored session lookup must follow user lock and fresh post-lock time')
        if updates and not ordered(expected[0],expected[1],'sessionId = returned stored session_id',expected[2]):errors.append('every token change must follow locked user and server-derived fresh session')
        if code==200:
            if not ordered('Verify JWT','BEGIN READ COMMITTED',expected[0],'Capture fresh server UTC now',expected[1],'sessionId = returned stored session_id',expected[2],expected[3],'app -> infra: COMMIT','HTTP 200') or len(updates)!=2:errors.append('success must close both complete session token tables atomically before 200')
            if any('ROLLBACK' in e for e in trace) or 'status only, no data' not in response[0]:errors.append('logout success returns status only and must not rollback')
        elif begun:
            if not ordered('BEGIN','ROLLBACK',f'HTTP {code}') or any(e=='app -> infra: COMMIT' for e in trace):errors.append('logout failure must rollback before response and never commit')
            if code==401 and updates:errors.append('invalid logout credential cannot change tokens')
        elif code not in (400,401) or queries:errors.append('early input/JWT failure must execute no SQL')
        if code==401:unauthorized_queries.append(len(queries))
    if Counter(outcomes)!=Counter({200:1,400:1,401:3,408:1,500:2}) or sorted(unauthorized_queries)!=[0,1,2]:errors.append(f'incomplete logout paths: {dict(Counter(outcomes))}, auth-queries={unauthorized_queries}')
    for title,code in {'Success':200,'Fail - Bad Request':400,'Fail - Unauthorized':401,'Fail - Request Timeout':408,'Fail - Internal Server Error':500}.items():
        try:
            obj=authen_json(md,title);status=obj['status']
            if status['code']!=code or code==500 and 'bizCode' in status:errors.append(f'incorrect logout {title} envelope')
            if title=='Success' and 'data' in obj:errors.append('logout success has no data')
        except (TypeError,KeyError,ValueError):errors.append(f'missing logout {title} example')
    errors+=json_blocks_parse(md);errors+=table_lines_aligned(md)
    if '--rendered-svg' in sys.argv:
        import xml.etree.ElementTree as ET
        try:
            root=ET.parse(sys.argv[sys.argv.index('--rendered-svg')+1]).getroot()
            expected_lines=Counter(' '.join(l.split()) for _,_,s in operations for l in s.splitlines() if l.strip())
            visible=Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'))
            missing=expected_lines-visible
            if missing:errors.append(f'rendered logout SQL missing {sum(missing.values())} lines')
            else:print(f'OK: rendered logout SQL ({sum(expected_lines.values())}/{sum(expected_lines.values())} visible lines)')
        except (IndexError,OSError,ET.ParseError) as exc:errors.append(f'cannot verify logout SVG: {exc}')
    if errors:return fail('; '.join(errors))
    print('OK: logout-flow (8 terminal traces; post-lock credential check and atomic full-session revocation)')
    return 0


COMMANDS['logout-flow'] = check_logout_flow
def check_profile_upsert_flow() -> int:
    """Check own-user credential gating, presence/null semantics and mutually exclusive writes."""
    path=AUTHEN_SPECS['07'];md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    for needle in ('status: in-review', 'approved_by: null', 'approved_at: null', 'explicit null clears them', "on or before today's UTC date"):
        if needle not in md:errors.append(f'profile-upsert spec missing {needle!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for needle in ('A body {} is valid', 'JSON key presence, never truthiness', 'Skip the m_user UPDATE entirely', 'Skip information lookup/INSERT/UPDATE',
            'fresh server UTC now', 'expiry during lock wait', 'one transaction', 'COMMIT must succeed before 200', 'Preserve existing non-DELETED row_status',
            'DELETED information is historical'):
        if needle not in seq:
            errors.append(f'profile-upsert sequence note missing {needle!r}')
    operations=spec_database_operations(md)
    expected=('QUERY - Lock the user','QUERY - Check the current access token','UPDATE - Update user','QUERY - Check existing information','INSERT - Create information','UPDATE - Update information')
    if tuple(h for _,h,_ in operations)!=expected:errors.append('profile SQL needs user lock, current token, optional user write and distinct information branches')
    sql={h:re.sub(r'--[^\n]*','',s) for _,h,s in operations}
    required={expected[0]:["u.id = '<sequence.userId>'","u.row_status = 'ACTIVE'",'FOR UPDATE'],
              expected[1]:["at.token = '<sequence.accessTokenHash>'","at.user_id = '<sequence.userId>'","at.row_status = 'ACTIVE'","at.expired_at > '<sequence.now>'"],
              expected[2]:["WHERE id = '<sequence.userId>'","AND row_status = 'ACTIVE'",'RETURNING id as user_id'],
              expected[3]:['ui.id as information_id',"ui.user_id = '<sequence.userId>'","ui.row_status <> 'DELETED'"],
              expected[4]:['INSERT INTO authen.m_user_information',"'<sequence.userId>'",'RETURNING id as information_id'],
              expected[5]:["WHERE id = '<sequence.informationId>'","AND user_id = '<sequence.userId>'","AND row_status <> 'DELETED'",'RETURNING id as information_id']}
    fields=(('first_name','hasFirstName','firstNameBytes'),('last_name','hasLastName','lastNameBytes'),('display_name','hasDisplayName','displayName'),('profile_picture_path','hasProfilePicturePath','profilePicturePath'),('phone_number','hasPhoneNumber','phoneNumberBytes'),('address','hasAddress','addressBytes'),('date_of_birth','hasDateOfBirth','dateOfBirth'),('gender','hasGender','gender'))
    for index,(column,flag,value) in enumerate(fields):required[expected[2] if index<4 else expected[5]].append(f"{column} = CASE WHEN '<sequence.{flag}>' THEN '<sequence.{value}>' ELSE {column} END")
    for h in (expected[2],expected[5]):required[h]+=["updated_by = '<sequence.userId>'","updated_at = '<sequence.now>'"]
    for h,needles in required.items():
        for needle in needles:
            if needle not in sql.get(h,''):errors.append(f'{h} missing {needle}')
    if 'NOW()' in '\n'.join(sql.values()) or re.search(r'\bCOALESCE\s*\(', '\n'.join(sql.values()),re.I):errors.append('profile needs post-lock bound now and CASE presence masks, not non-null fallback')
    for h in (expected[2],expected[4],expected[5]):
        if re.search(r'\b(?:username|email_address|password|row_status)\s*=',sql.get(h,'')) and h!=expected[2]:errors.append('information writes must preserve lifecycle and fixed fields')
    if re.search(r'\b(?:username|email_address|password)\s*=',sql.get(expected[2],'')):errors.append('profile may not update fixed account fields')
    if any(t not in ('authen.m_user','authen.t_user_access_token','authen.m_user_information') for t,_,_ in operations):errors.append('profile must not alter credentials/grants or other domains')
    actual,lifecycle=sequence_database_operations(wsd);errors+=lifecycle
    if [(t.split('.')[-1],h,s) for t,h,s in operations]!=actual:errors.append('profile-upsert spec/sequence SQL differs character-for-character or order')
    errors+=sequence_login_standard_errors(wsd)
    for _,heading,_ in operations:
        if f'app -> infra: {heading}' not in wsd:errors.append(f'{heading} needs Application request')
        mapping=re.search(rf'infra -> (\w+): {re.escape(heading)}\n.*?\1 -> infra: Return ([^\n]+)\n.*?deactivate \1\n\s*infra -> app: Return ([^\n]+)',wsd,re.S)
        if not mapping or mapping[2]!=mapping[3]:errors.append(f'{heading} database/Application result mapping differs')
    for needle in ('Verify JWT signature/issuer/audience/expiry/UUID sub','userId = verified sub; accessTokenHash = SHA-256 exact JWT',
                   'Derive eight hasField flags from JSON key presence; userFieldsPresent/informationFieldsPresent from their groups',
                   'Encrypt supplied non-null sensitive values as register; explicit null = SQL NULL; omit preserves; typed text/date/boolean parameters',
                   'Capture fresh server UTC now after user lock; recheck JWT exp',
                   'alt userFieldsPresent','else No user fields supplied','alt informationFieldsPresent','else No information fields supplied',
                   'alt Exactly one user_id returned','alt Exactly one inserted information_id','alt Exactly one updated information_id',
                   'Bind omitted information columns to SQL NULL on first insert','informationId = returned information_id; preserve row_status',
                   'data.userId = verified sub; response contains no other profile/secret fields'):
        if needle not in wsd:errors.append(f'profile sequence missing {needle!r}')
    traces,structure=login_sequence_paths(wsd);errors+=structure
    from collections import Counter
    outcomes=[];modes=Counter();unauthorized=[]
    for trace in traces:
        response=[e for e in trace if e.startswith('app -> api: HTTP ')]
        if len(response)!=1:errors.append('profile trace needs exactly one outcome; aborted write must terminate common success');continue
        code=int(response[0].split('HTTP ')[1].split()[0]);outcomes.append(code)
        def ordered(*parts):
            pos=[next((i for i,e in enumerate(trace) if part in e),-1) for part in parts]
            return -1 not in pos and pos==sorted(set(pos))
        queries=[e for e in trace if e.startswith('infra -> ')]
        writes=[e for e in queries if ': UPDATE' in e or ': INSERT' in e]
        begun=any(e.startswith('app -> infra: BEGIN') for e in trace)
        if queries and not ordered('Verify JWT','userId = verified sub','Derive eight hasField flags','BEGIN READ COMMITTED',expected[0]):errors.append('profile SQL must follow verified identity and user-first transaction')
        if any(expected[1] in e for e in trace) and not ordered(expected[0],'Capture fresh server UTC now',expected[1]):errors.append('current credential lookup must use fresh post-lock time')
        if writes and not ordered(expected[0],'Capture fresh server UTC now',expected[1],next(h for h in expected if any(h in e for e in writes))):errors.append('all profile writes need locked user and fresh current credential')
        if code==200:
            user_write=any(expected[2] in e for e in writes);insert=any(expected[4] in e for e in writes);update=any(expected[5] in e for e in writes)
            modes[(user_write,'insert' if insert else 'update' if update else 'none')]+=1
            if insert and update:errors.append('information INSERT/UPDATE are mutually exclusive')
            if (insert or update) and not ordered(expected[1],expected[3],expected[4] if insert else expected[5]):errors.append('information write needs current-user lookup before its branch')
            if not ordered(expected[1],'app -> infra: COMMIT','data.userId = verified sub','HTTP 200') or any('ROLLBACK' in e for e in trace) or 'data.userId only' not in response[0]:errors.append('success needs commit before returning verified caller id only')
        elif begun:
            if not ordered('BEGIN','ROLLBACK',f'HTTP {code}') or any(e=='app -> infra: COMMIT' for e in trace):errors.append('profile failure must roll back before response and never reach success commit')
            if code==401 and writes:errors.append('inactive/revoked credential must not change profile')
        elif code not in (400,401) or queries:errors.append('invalid input/JWT must execute no SQL')
        if code==401:unauthorized.append(len(queries))
    expected_modes=Counter({(u,k):1 for u in (False,True) for k in ('none','insert','update')})
    if Counter(outcomes)!=Counter({200:6,400:1,401:3,408:1,500:6}) or modes!=expected_modes or sorted(unauthorized)!=[0,1,2]:errors.append(f'incomplete profile paths: {dict(Counter(outcomes))}; modes={dict(modes)}; 401 SQL={unauthorized}')
    for title,code in {'Success':200,'Fail - Bad Request':400,'Fail - Bad Request Fixed Field':400,'Fail - Unauthorized':401,'Fail - Request Timeout':408,'Fail - Internal Server Error':500}.items():
        try:
            obj=authen_json(md,title);status=obj['status']
            if status['code']!=code or code==500 and 'bizCode' in status:errors.append(f'incorrect profile {title} envelope')
            if title=='Success' and set(obj.get('data',{}))!={'userId'}:errors.append('profile success returns caller userId only')
        except (TypeError,KeyError,ValueError):errors.append(f'missing profile {title} example')
    errors+=json_blocks_parse(md);errors+=table_lines_aligned(md)
    if '--rendered-svg' in sys.argv:
        import xml.etree.ElementTree as ET
        try:
            root=ET.parse(sys.argv[sys.argv.index('--rendered-svg')+1]).getroot()
            expected_lines=Counter(' '.join(l.split()) for _,_,s in operations for l in s.splitlines() if l.strip())
            visible=Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'))
            missing=expected_lines-visible
            if missing:errors.append(f'rendered profile SQL missing {sum(missing.values())} lines')
            else:print(f'OK: rendered profile SQL ({sum(expected_lines.values())}/{sum(expected_lines.values())} visible lines)')
        except (IndexError,OSError,ET.ParseError) as exc:errors.append(f'cannot verify profile SVG: {exc}')
    if errors:return fail('; '.join(errors))
    print('OK: profile-upsert-flow (17 terminal traces; exact SQL, fresh current credential and presence-aware atomic writes)')
    return 0


COMMANDS['profile-upsert-flow'] = check_profile_upsert_flow


def check_create_password_flow() -> int:
    """Check reset single-use serialization, password replacement and all-session revocation."""
    path=AUTHEN_SPECS['04'];md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    for needle in ('status: in-review', 'approved_by: null', 'approved_at: null', 'lookup is only a routing hint'):
        if needle not in md:errors.append(f'create-password spec missing {needle!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for needle in ('fresh server UTC now after the lock', 'No reset/password/token UPDATE may run before the user lock',
            'resetId, userId, resetTokenHash, ACTIVE status', 'constant time', 'random 16 byte salt and 600,000 iterations',
            'reset token stays usable until it expires', 'TEMPORARY_PASSWORD and prior history rows are unchanged', 'every session',
            'Zero access/refresh rows is allowed', 'COMMIT must succeed before 200', 'A lookup timeout/failure before BEGIN',
            'A missing current password is an internal consistency failure', 'A second reset waits', 'A refresh/login that commits first'):
        if needle not in seq:
            errors.append(f'create-password sequence note missing {needle!r}')
    operations=spec_database_operations(md)
    expected=('QUERY - Find the reset token','QUERY - Lock the user','UPDATE - Use the reset token once','QUERY - Get current password','UPDATE - Make the current password INACTIVE','INSERT - Create password','UPDATE - Close the access tokens of the user','UPDATE - Close the refresh tokens of the user')
    if tuple(h for _,h,_ in operations)!=expected:errors.append('reset SQL must follow routing, user lock, consume, password comparison/replacement, both revocations')
    sql={h:re.sub(r'--[^\n]*','',s) for _,h,s in operations}
    required={expected[0]:["rp.reset_token = '<sequence.resetTokenHash>'","rp.row_status = 'ACTIVE'","rp.expired_at > '<sequence.lookupNow>'",'rp.id as reset_id','rp.user_id'],
              expected[1]:["u.id = '<sequence.userId>'","u.row_status = 'ACTIVE'",'FOR UPDATE'],
              expected[2]:["WHERE id = '<sequence.resetId>'","AND user_id = '<sequence.userId>'","AND reset_token = '<sequence.resetTokenHash>'","AND row_status = 'ACTIVE'","AND expired_at > '<sequence.now>'",'RETURNING id as reset_id'],
              expected[3]:['up.id as password_id','up.password,','up.password_salt',"up.user_id = '<sequence.userId>'","up.row_type = 'PASSWORD'","up.row_status = 'ACTIVE'"],
              expected[4]:["WHERE id = '<sequence.passwordId>'","AND user_id = '<sequence.userId>'","AND row_type = 'PASSWORD'","AND row_status = 'ACTIVE'",'RETURNING id as password_id'],
              expected[5]:['INSERT INTO authen.m_user_password','created_by,','row_type,','user_id,','password,','password_salt',"'PASSWORD'","'<sequence.passwordBytes>'","'<sequence.passwordSaltBytes>'"]}
    for h in (expected[2],expected[4],expected[6],expected[7]):
        required.setdefault(h,[]).extend(["updated_by = '<sequence.userId>'","updated_at = '<sequence.now>'","row_status = 'INACTIVE'"])
    for h in expected[6:]:required[h].extend(["WHERE user_id = '<sequence.userId>'","AND row_status = 'ACTIVE'"])
    for h,needles in required.items():
        for needle in needles:
            if needle not in sql.get(h,''):errors.append(f'{h} missing {needle}')
    for h in expected[6:]:
        if re.search(r'\bsession_id\b|\bexpired_at\b|\btoken\s*=',sql.get(h,'')):errors.append('reset must revoke every ACTIVE user session, including expired rows')
    if 'NOW()' in '\n'.join(sql.values()) or any(t.startswith('author.') for t,_,_ in operations):errors.append('reset needs captured post-lock time and no role lookup')
    actual,lifecycle=sequence_database_operations(wsd);errors+=lifecycle
    # Compare every decoded character, including SQL whitespace; only PlantUML note indentation is removed.
    if [(t.split('.')[-1],h,s) for t,h,s in operations]!=actual:errors.append('reset spec/sequence SQL differs character-for-character or order')
    errors+=sequence_login_standard_errors(wsd)
    for _,heading,_ in operations:
        if f'app -> infra: {heading}' not in wsd:errors.append(f'{heading} needs Application request')
        match=re.search(rf'infra -> (\w+): {re.escape(heading)}\n.*?deactivate \1\n([^\n]+)',wsd,re.S)
        if not match or not match[2].strip().startswith('infra -> app: Return '):errors.append(f'{heading} needs Application result')
    for needle in ('resetTokenHash = SHA-256 exact resetToken; capture server UTC lookupNow',
                   'resetId/userId = returned row; never request userId',
                   'Capture fresh server UTC now after user lock; do not reuse lookupNow',
                   'alt Exactly one reset_id returned','alt Exactly one ACTIVE PASSWORD returned',
                   'passwordId = returned password_id; candidate = PBKDF2-HMAC-SHA256(newPassword, stored salt, 600000); constant-time compare',
                   'alt Candidate differs from current password','else Candidate equals current password',
                   'Generate fresh cryptographically random 16-byte passwordSaltBytes; derive passwordBytes with PBKDF2-HMAC-SHA256 600000',
                   'alt Exactly one password_id returned','else Unexpected zero old-password update',
                   'accessClosedCount and refreshClosedCount may be zero; all changes remain atomic'):
        if needle not in wsd:errors.append(f'reset sequence missing {needle!r}')
    traces,structure=login_sequence_paths(wsd);errors+=structure
    from collections import Counter
    outcomes=[];early=[]
    for trace in traces:
        response=[e for e in trace if e.startswith('app -> api: HTTP ')]
        if len(response)!=1:errors.append('reset trace needs exactly one outcome');continue
        code=int(response[0].split('HTTP ')[1].split()[0]);outcomes.append(code)
        def ordered(*parts):
            pos=[next((i for i,e in enumerate(trace) if part in e),-1) for part in parts]
            return -1 not in pos and pos==sorted(set(pos))
        queries=[e for e in trace if e.startswith('infra -> ')]
        writes=[e for e in queries if ': UPDATE' in e or ': INSERT' in e]
        begun=any(e.startswith('app -> infra: BEGIN') for e in trace)
        if queries and not ordered('resetTokenHash = SHA-256',expected[0]):errors.append('lookup must follow hash and lookup clock')
        if any(expected[2] in e for e in trace) and not ordered(expected[0],'resetId/userId = returned row','BEGIN READ COMMITTED',expected[1],'Capture fresh server UTC now',expected[2]):errors.append('reset consumption must follow BEGIN/user lock/fresh clock')
        if any(expected[4] in e for e in trace) and not ordered(expected[2],expected[3],'candidate = PBKDF2','Generate fresh cryptographically random',expected[4]):errors.append('password change must follow consumption, current password comparison and fresh derivation')
        if code==200:
            if not ordered(*expected,'app -> infra: COMMIT','HTTP 200') or len(writes)!=5:errors.append('success must consume once, replace password and revoke both token tables before COMMIT/200')
            if 'status only, no data' not in response[0] or any('ROLLBACK' in e for e in trace):errors.append('reset success must have status only and no rollback')
        elif begun:
            if not ordered('BEGIN','ROLLBACK',f'HTTP {code}') or any(e=='app -> infra: COMMIT' for e in trace):errors.append('every transactional failure must roll back before response')
            if code==400 and len(writes)>1:errors.append('invalid/same-password reset cannot reach password replacement')
        else:
            early.append((code,len(queries)))
            if writes or any('ROLLBACK' in e for e in trace):errors.append('pre-BEGIN failures must not write or roll back a nonexistent transaction')
        if code==400 and any('candidate = PBKDF2' in e for e in trace):
            if len(writes)!=1 or 'New password must be different from the current password.' not in response[0]:errors.append('same-password failure must roll back its single reset consumption')
    if Counter(outcomes)!=Counter({400:5,200:1,408:2,500:4}) or sorted(early)!=[(400,0),(400,1),(408,0),(500,0)]:errors.append(f'incomplete reset outcomes: {dict(Counter(outcomes))}; early={early}')
    for title,code in {'Success':200,'Fail - Bad Request':400,'Fail - Bad Request Password Policy':400,'Fail - Bad Request Reset Token':400,'Fail - Bad Request Same Password':400,'Fail - Request Timeout':408,'Fail - Internal Server Error':500}.items():
        try:
            obj=authen_json(md,title);status=obj['status']
            if status['code']!=code or code==500 and 'bizCode' in status:errors.append(f'incorrect reset {title} envelope')
            if title=='Success' and 'data' in obj:errors.append('reset success has no data')
        except (TypeError,KeyError,ValueError):errors.append(f'missing reset {title} example')
    errors+=json_blocks_parse(md);errors+=table_lines_aligned(md)
    if '--rendered-svg' in sys.argv:
        import xml.etree.ElementTree as ET
        try:
            root=ET.parse(sys.argv[sys.argv.index('--rendered-svg')+1]).getroot()
            expected_lines=Counter(' '.join(l.split()) for _,_,s in operations for l in s.splitlines() if l.strip())
            visible=Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'))
            missing=expected_lines-visible
            if missing:errors.append(f'rendered reset SQL missing {sum(missing.values())} lines')
            else:print(f'OK: rendered reset SQL ({sum(expected_lines.values())}/{sum(expected_lines.values())} visible lines)')
        except (IndexError,OSError,ET.ParseError) as exc:errors.append(f'cannot verify reset SVG: {exc}')
    if errors:return fail('; '.join(errors))
    print('OK: create-password-flow (12 terminal traces; exact SQL, post-lock single use and atomic all-session revocation)')
    return 0


COMMANDS['create-password-flow'] = check_create_password_flow


def check_reset_request_flow() -> int:
    """Check uniform public issuance outcomes, fresh throttling and atomic replacement."""
    path=AUTHEN_SPECS['03'];md=read(path);wsd=read(str(Path(path).with_name('sequence.wsd')));errors=[]
    for needle in ('status: in-review', 'approved_by: null', 'approved_at: null', '32-byte token', 'hash the exact encoded token', 'whatever their status'):
        if needle not in md:errors.append(f'reset-request spec missing {needle!r}')
    seq = ' '.join(wsd.split())  # the note texts of the sequence, one line
    for needle in ('Do not trim, lowercase or normalize', 'same configured response-latency policy', 'equality is outside the window', 'requests >= 3', 'requests < 3',
            'fresh server UTC now after the lock', 'explicit created_at', 'zero old rows is valid', 'one transaction', 'COMMIT before email handoff',
            'Sending is outside this spec', 'No post-commit email failure may roll back', 'Do not change password, access/refresh tokens'):
        if needle not in seq:
            errors.append(f'reset-request sequence note missing {needle!r}')
    operations=spec_database_operations(md)
    expected=('QUERY - Find the active user by email address','QUERY - Lock the user','QUERY - Count the requests of the last hour','UPDATE - Make the old reset token INACTIVE','INSERT - Create reset token')
    if tuple(h for _,h,_ in operations)!=expected:errors.append('reset request SQL must follow routing, user lock, fresh history count, old closure, new insert')
    sql={h:re.sub(r'--[^\n]*','',s) for _,h,s in operations}
    required={expected[0]:['u.id as user_id',"WHERE u.email_address = '<sequence.emailAddressBytes>'","AND u.row_status = 'ACTIVE'"],
              expected[1]:["WHERE u.id = '<sequence.userId>'","AND u.row_status = 'ACTIVE'","AND u.email_address = '<sequence.emailAddressBytes>'",'FOR UPDATE'],
              expected[2]:['COUNT(rp.id) as requests',"WHERE rp.user_id = '<sequence.userId>'","AND rp.created_at > '<sequence.windowStart>'"],
              expected[3]:["updated_by = '<sequence.userId>'","updated_at = '<sequence.now>'","row_status = 'INACTIVE'","WHERE user_id = '<sequence.userId>'","AND row_status = 'ACTIVE'"],
              expected[4]:['created_by,\n    created_at,\n    user_id,\n    reset_token,\n    expired_at',"'<sequence.userId>',\n    '<sequence.now>',\n    '<sequence.userId>',\n    '<sequence.resetTokenHash>'","'<sequence.expiredAt>'",'RETURNING id as reset_id']}
    for h,needles in required.items():
        for needle in needles:
            if needle not in sql.get(h,''):errors.append(f'{h} missing {needle}')
    if re.search(r'\brow_status\b|\bexpired_at\b',sql.get(expected[2],'')):errors.append('throttle must count all lifecycle states, including expired/used/replaced history')
    if 'NOW()' in '\n'.join(sql.values()) or '<sequence.rawResetToken>' in '\n'.join(sql.values()) or any(t not in ('authen.m_user','authen.t_user_reset_password') for t,_,_ in operations):errors.append('reset issuance needs fresh bound time/hash and must not touch password/session/authorization tables')
    actual,lifecycle=sequence_database_operations(wsd);errors+=lifecycle
    if [(t.split('.')[-1],h,s) for t,h,s in operations]!=actual:errors.append('reset request spec/sequence SQL differs character-for-character or order')
    errors+=sequence_login_standard_errors(wsd)
    for _,heading,_ in operations:
        if f'app -> infra: {heading}' not in wsd:errors.append(f'{heading} needs Application request')
        match=re.search(rf'infra -> (\w+): {re.escape(heading)}\n.*?deactivate \1\n([^\n]+)',wsd,re.S)
        if not match or not match[2].strip().startswith('infra -> app: Return '):errors.append(f'{heading} needs Application result')
        mapping=re.search(rf'infra -> (\w+): {re.escape(heading)}\n.*?\1 -> infra: Return ([^\n]+)\n.*?deactivate \1\n\s*infra -> app: Return ([^\n]+)',wsd,re.S)
        if not mapping or mapping[2]!=mapping[3]:errors.append(f'{heading} database/Application result mapping differs')
    for needle in ('emailAddressBytes = same deterministic encryption as register/login; no trimming or case change',
                   'Generate 32 random bytes; rawResetToken = unpadded base64url; resetTokenHash = SHA-256 exact encoded token',
                   'userId = returned user_id; never request target user',
                   'Capture fresh server UTC now after user lock; windowStart = now minus 1 hour; expiredAt = now plus 30 minutes',
                   'alt requests >= 3','else requests < 3','alt Exactly one new reset_id returned',
                   'oldClosedCount; zero is valid','Request email handoff only for committed new reset; registered recipient and configured trusted reset URL'):
        if needle not in wsd:errors.append(f'reset-request sequence missing {needle!r}')
    traces,structure=login_sequence_paths(wsd);errors+=structure
    from collections import Counter
    outcomes=[];success_queries=[]
    for trace in traces:
        response=[e for e in trace if e.startswith('app -> api: HTTP ')]
        if len(response)!=1:errors.append('reset-request trace needs one terminal outcome');continue
        code=int(response[0].split('HTTP ')[1].split()[0]);outcomes.append(code)
        def ordered(*parts):
            pos=[next((i for i,e in enumerate(trace) if part in e),-1) for part in parts]
            return -1 not in pos and pos==sorted(set(pos))
        queries=[e for e in trace if e.startswith('infra -> ')]
        writes=[e for e in queries if ': UPDATE' in e or ': INSERT' in e]
        begun=any(e.startswith('app -> infra: BEGIN') for e in trace)
        if queries and not ordered('emailAddressBytes = same deterministic','Generate 32 random bytes',expected[0]):errors.append('lookup must follow common encrypted identifier/token preparation')
        if any(expected[2] in e for e in trace) and not ordered(expected[0],'userId = returned user_id','BEGIN READ COMMITTED',expected[1],'Capture fresh server UTC now',expected[2]):errors.append('throttle must follow BEGIN, locked ACTIVE same-email user and post-lock time')
        if writes and not ordered(expected[1],'Capture fresh server UTC now',expected[2],expected[3],expected[4]):errors.append('both reset writes must follow fresh locked throttle evaluation')
        handoff=any('Request email handoff only for committed new reset' in e for e in trace)
        if handoff and not ordered(expected[4],'app -> infra: COMMIT','Request email handoff only for committed new reset','HTTP 200'):errors.append('email handoff requires committed new reset before generic success')
        if code==200:
            success_queries.append(len(queries))
            if 'If the email address is registered, a reset link has been sent.; status only, no data' not in response[0]:errors.append('every business outcome needs identical status-only success')
            if not any('common configured response-latency policy' in e for e in trace):errors.append('every business outcome needs common timing policy')
            if begun and not ordered('app -> infra: BEGIN','app -> infra: COMMIT','HTTP 200'):errors.append('open read/write transaction must close before success')
            if writes and (len(writes)!=2 or not handoff):errors.append('issuance must atomically replace reset and hand off email after commit')
            if not writes and handoff:errors.append('unknown/inactive/throttled outcome must never send reset email')
            if any('ROLLBACK' in e for e in trace):errors.append('business success ends its read/write transaction with COMMIT')
        elif begun:
            if not ordered('BEGIN','ROLLBACK',f'HTTP {code}') or any(e=='app -> infra: COMMIT' for e in trace) or handoff:errors.append('transaction failure rolls back before response and must not hand off email')
        elif queries or writes or any('ROLLBACK' in e for e in trace):errors.append('input/early lookup failure has no committed SQL or transaction to roll back')
    if Counter(outcomes)!=Counter({200:4,400:1,408:2,500:3}) or sorted(success_queries)!=[1,2,3,5]:errors.append(f'incomplete reset-request paths: {dict(Counter(outcomes))}; success SQL={success_queries}')
    for title,code in {'Success':200,'Fail - Bad Request':400,'Fail - Request Timeout':408,'Fail - Internal Server Error':500}.items():
        try:
            obj=authen_json(md,title);status=obj['status']
            if status['code']!=code or code==500 and 'bizCode' in status:errors.append(f'incorrect reset request {title} envelope')
            if title=='Success' and 'data' in obj:errors.append('reset-request success has no data')
        except (TypeError,KeyError,ValueError):errors.append(f'missing reset request {title} example')
    errors+=json_blocks_parse(md);errors+=table_lines_aligned(md)
    if '--rendered-svg' in sys.argv:
        import xml.etree.ElementTree as ET
        try:
            root=ET.parse(sys.argv[sys.argv.index('--rendered-svg')+1]).getroot()
            expected_lines=Counter(' '.join(l.split()) for _,_,s in operations for l in s.splitlines() if l.strip())
            visible=Counter(' '.join(''.join(e.itertext()).split()) for e in root.iter() if e.tag.endswith('}text'))
            missing=expected_lines-visible
            if missing:errors.append(f'rendered reset-request SQL missing {sum(missing.values())} lines')
            else:print(f'OK: rendered reset-request SQL ({sum(expected_lines.values())}/{sum(expected_lines.values())} visible lines)')
        except (IndexError,OSError,ET.ParseError) as exc:errors.append(f'cannot verify reset-request SVG: {exc}')
    if errors:return fail('; '.join(errors))
    print('OK: reset-request-flow (10 terminal traces; exact SQL, fresh serialized throttle and atomic reset issuance)')
    return 0


COMMANDS['reset-request-flow'] = check_reset_request_flow


# ---------------------------------------------------------------- integrity of this file: every check is a sub-command and ends with a return
def check_registry() -> int:
    """A merge can cut the end of a checker or its COMMANDS line without a syntax error, and then the check does nothing.

    Every top-level `check_*` function must end with `return` or `raise` and must be registered in COMMANDS (the name may
    be inside a lambda) or be called by another function; a sub-command name may be registered only once, because a second
    registration silently replaces the first.
    """
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith("check_")}
    registered, keys = set(), []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name) and t.value.id == "COMMANDS" for t in node.targets
        ):
            key = next(t.slice for t in node.targets if isinstance(t, ast.Subscript))
            keys.append(key.value if isinstance(key, ast.Constant) else ast.dump(key))
            registered.update(n.id for n in ast.walk(node.value) if isinstance(n, ast.Name))
    called = {
        n.func.id
        for f in ast.walk(tree)
        if isinstance(f, ast.FunctionDef)
        for n in ast.walk(f)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
    }
    errors = []
    for name, node in functions.items():
        if not isinstance(node.body[-1], (ast.Return, ast.Raise)):
            errors.append(f"{name} (line {node.lineno}) does not end with return or raise: its end may have been cut")
        if name not in registered and name not in called:
            errors.append(f"{name} (line {node.lineno}) is neither registered in COMMANDS nor called by another function")
    errors.extend(f"sub-command {key!r} is registered more than once" for key in sorted(set(keys)) if keys.count(key) > 1)
    if errors:
        return fail("; ".join(errors))
    print(f"OK: check-registry ({len(functions)} check functions, {len(set(keys))} sub-commands, every one registered or called and ending with a return)")
    return 0


COMMANDS["check-registry"] = check_registry


# ---------------------------------------------------------------- spec template (owner decision of 2026-11-13)
SPEC_TEMPLATE_SECTIONS = {
    "##": {"Domain", "Request Parameters", "Example Request", "Response Parameters", "Database Relations", "External Services"},
    "###": {"Header Parameters", "Path Parameters", "Query Parameters", "Body Parameters", "HTTP Request", "cUrl Request", "Status Object", "Data Object", "Example Response Parameters"},
}


def spec_template_errors(md: str) -> list[str]:
    """A spec.md has only the ## and ### sections of template.md, and links only to schema docs, external URLs and anchors of its own headings."""
    errors = []
    headings = []
    prose = []
    in_code = False
    for line in md.split("\n"):
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        prose.append(line)
        match = re.match(r"^(#{1,6}) (.+?)\s*$", line)
        if match:
            headings.append((match.group(1), match.group(2)))
    for level, title in headings:
        if level not in ("##", "###"):
            continue
        allowed = title in SPEC_TEMPLATE_SECTIONS[level] or (level == "###" and re.match(r"(?:Table: \[|API: )", title))
        if not allowed:
            errors.append(f"section '{level} {title}' is not a section of template.md (ask the owner before adding one)")
    anchors = {re.sub(r"[^a-z0-9 _-]", "", title.lower()).replace(" ", "-") for _, title in headings}
    for target in re.findall(r"\]\(([^)\s]+)\)", "\n".join(prose)):
        if target.startswith("#"):
            if target[1:] not in anchors:
                errors.append(f"anchor {target} does not match a heading of the file")
        elif target.startswith(("http://", "https://")):
            continue
        elif "/schema/" not in "/" + target.lstrip("./"):
            errors.append(f"link {target} goes to a file that is not a schema doc (only schema docs, external API URLs and anchors are allowed)")
    return errors


# Specs that do not follow the template yet. Each is exempt until its sections and links are fixed; an entry must be a spec folder and
# must still fail, so a spec that passes has to leave the list in the same change. The count is printed in the OK line.
LEGACY_SPEC_TEMPLATE = (
)


def check_spec_template() -> int:
    errors = []
    api_root = ROOT / "e-commerce/doc/api"
    specs = {f"{spec.parent.parent.name}/{spec.parent.name}": spec for spec in sorted(api_root.glob("*/*/spec.md"))}
    if not specs:
        errors.append("no spec.md found under e-commerce/doc/api")
    for entry in LEGACY_SPEC_TEMPLATE:
        if entry not in specs:
            errors.append(f"LEGACY_SPEC_TEMPLATE lists {entry}, which is not a spec folder")
    for name, spec in specs.items():
        found = spec_template_errors(spec.read_text(encoding="utf-8"))
        if name in LEGACY_SPEC_TEMPLATE:
            if not found:
                errors.append(f"{name}/spec.md: already follows the template, remove it from LEGACY_SPEC_TEMPLATE")
        else:
            errors.extend(f"{name}/spec.md: {error}" for error in found)
    if errors:
        return fail("; ".join(errors))
    print(f"OK: spec-template ({len(specs)} specs; {len(LEGACY_SPEC_TEMPLATE)} not following the template yet)")
    return 0


COMMANDS["spec-template"] = check_spec_template


# ---------------------------------------------------------------- Markdown frontmatter (.agents/rules/markdown.md)
# The specs that still have no frontmatter. The owner decided on 2026-11-14 that they get `status: in-review`, `approved_by: null` and
# `approved_at: null`; a file that passes must leave this list (the checker asks for it).
MD_FRONTMATTER_PENDING = ()
MD_STATUSES = ("draft", "in-review", "approved", "superseded")


def markdown_files() -> list[str]:
    """Every tracked human-authored Markdown file (generated, vendor and ignored files such as .workspace and repository/ are not tracked)."""
    result = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("md-frontmatter needs a git checkout: `git ls-files` failed: " + result.stderr.strip())
    return sorted(result.stdout.split())


def is_spec_markdown(path: str) -> bool:
    return bool(re.match(r"e-commerce/doc/api/[^/]+/[^/]+/spec\.md$", path)) or path.startswith("docs/superpowers/specs/")


def frontmatter_errors(path: str, md: str) -> list[str]:
    """name and description for every file, status, approved_by and approved_at for a specification."""
    if not md.startswith("---\n") or "\n---" not in md[4:]:
        return ["does not start with YAML frontmatter"]
    fields = {}
    for line in md[4:].split("\n---", 1)[0].split("\n"):
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip()
    errors = []
    for key in ("name", "description"):
        value = fields.get(key, "")
        if value[:1] == '"':
            try:
                value = json.loads(value)
            except ValueError:
                errors.append(f"frontmatter {key} is not a valid quoted string")
                continue
        if not value:
            errors.append(f"frontmatter has no {key}")
    if is_spec_markdown(path):
        status = fields.get("status")
        if status not in MD_STATUSES:
            errors.append(f"specification status must be one of {', '.join(MD_STATUSES)}")
        for key in ("approved_by", "approved_at"):
            if key not in fields:
                errors.append(f"specification has no {key}")
        if status in ("draft", "in-review") and (fields.get("approved_by") != "null" or fields.get("approved_at") != "null"):
            errors.append("approved_by and approved_at stay null while the specification is not approved")
        if status == "approved" and "null" in (fields.get("approved_by"), fields.get("approved_at")):
            errors.append("an approved specification needs approved_by and approved_at")
    return errors


def check_md_frontmatter() -> int:
    errors = []
    try:
        paths = markdown_files()
    except (OSError, RuntimeError) as error:
        return fail(str(error))
    for entry in MD_FRONTMATTER_PENDING:
        if entry not in paths:
            errors.append(f"MD_FRONTMATTER_PENDING lists {entry}, which is not a tracked Markdown file")
    for path in paths:
        found = frontmatter_errors(path, (ROOT / path).read_text(encoding="utf-8"))
        if path in MD_FRONTMATTER_PENDING:
            if not found:
                errors.append(f"{path}: already has the frontmatter, remove it from MD_FRONTMATTER_PENDING")
        else:
            errors.extend(f"{path}: {error}" for error in found)
    if errors:
        return fail("; ".join(errors))
    print(f"OK: md-frontmatter ({len(paths)} Markdown files; {len(MD_FRONTMATTER_PENDING)} specs without frontmatter yet)")
    return 0


COMMANDS["md-frontmatter"] = check_md_frontmatter


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: check_docs.py <subcommand>")
        print("subcommands: " + (", ".join(sorted(COMMANDS)) or "(none yet)"))
        return 0
    command = COMMANDS.get(argv[1])
    if command is None:
        return fail(f"unknown subcommand: {argv[1]}")
    return command()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
