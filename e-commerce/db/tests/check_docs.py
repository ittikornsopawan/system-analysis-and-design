#!/usr/bin/env python3
"""Shared checker for the multi-level product SKU docs.

Subcommands (schema, er, spec01, spec02, spec03) are added by later tasks.
Each subcommand returns exit code 0 on pass and prints "FAIL: <reason>" on fail.
"""
import json
import re
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
        if not md.startswith(f"# Table: product.{table}\n"):
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
        if not md.startswith(f"# Table: {schema}.{table}\n"):
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
    "#### Option and SKU Rules",
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
    "#### Option and SKU Rules",
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
        "01": ["#### Lot Object", "### Lot Rules", "#### UPDATE - Close the lot that is on sale before another lot is put on sale",
               "#### QUERY - Check lots in use", "sales.t_order_item", "Only one lot can be on sale", "E10006",
               "- Permission:", "E10009", "#### Fail - Forbidden", "#### QUERY - Check shop member",
               "#### QUERY - Check platform administrator", "-> permission (403) ->",
               "must not be lower than costPrice", "ck_t_shop_product_sku_lot_price_not_below_cost"],
        "02": ["#### Shop Product SKU Object", "#### Lot Object", "always 200", "skus[0].lots[1]", "Duplicate SKU",
               "must not be lower than costPrice", "ck_t_shop_product_sku_lot_price_not_below_cost",
               "- Permission:", "E10009", "#### Fail - Forbidden", "#### QUERY - Check shop members",
               "#### QUERY - Check platform administrator", "-> permission (403) ->"],
        "03": ["#### Lot Object", "costPrice", "#### QUERY - Get lots", "ORDER BY l.is_on_sale DESC"],
        "04": ["#### SKU Object", "#### Option Value Object", "### Page Rules", "stockStatus", "maxOrderQuantity",
               "#### QUERY - Get the lot that is on sale of each shop product SKU", "pi.option_value_id IS NULL",
               "sold by a shop that is ACTIVE", "AND s.row_status = 'ACTIVE' -- a shop that is not ACTIVE has no page"],
    }
    for key, need in needles.items():
        for missing in missing_needles(mds[key], need):
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
        "01": ["### Cart Rules", "#### Success - Merge", "E10007", "E10008", "#### QUERY - Get the line of the same SKU for merging",
               "#### QUERY - Count the lines of the user", "HTTP/1.1 204 No Content",
               "(the shop, the product, the shop product, the shop product SKU and the product SKU are ACTIVE"],
        "02": ["#### Cart Item Object", "always HTTP 200", "items[1]: Shop Product SKU Id is duplicated with items[0].", "MERGE",
               "(the shop, the product, the shop product, the shop product SKU and the product SKU are ACTIVE"],
        "03": ["### Availability Rules", "QUANTITY_EXCEEDS_STOCK", "#### QUERY - Get the lot that is on sale of each shop product SKU", "no paging"],
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
        for leftover in re.findall(r"(?i)categor\w*|parent\w*|slug|product(?!ion)\w*", md):
            errors.append(f"{path} still mentions '{leftover}' (copied from the product category spec)")
        if not (ROOT / path).with_name("sequence.wsd").exists():
            errors.append(f"{path} has no sequence.wsd beside it")
    if errors:
        return fail("; ".join(errors))
    needles = {
        "05": ["# [POST]: v1/shop/type/upsert", "### Shop Type Rules", "#### QUERY - Check shop in use", "AND s.row_status <> 'DELETED'",
               "AND st.row_status <> 'DELETED'\nAND st.id <> '<sequence.id>'", "(../../../schema/shop/m_shop_type.md)",
               "(../../../schema/shop/m_shop.md)", "Shop type name already exists.", "Shop type is used by shops.", "Shop type not found.",
               "Row status must not be DELETED when inserting a shop type.", "E10003", "E10004", "E10006", "E90001", "Insert Shop Type Success"],
        "06": ["# [POST]: v1/shop/type/upsert/batch", "### Shop Type Rules (same as the single upsert, applied per shop type)", "#### QUERY - Check shop in use", "shopTypes[2]: Id is duplicated with shopTypes[1].",
               "shopTypes[2]: Name is duplicated with shopTypes[0].", "Shop types must contain 1 to 100 items.", "Swapping the names",
               "shopTypes[2]: Shop type is used by shops.", "AND st.row_status <> 'DELETED'\nAND st.id <> '<sequence.shopTypes.id>'"],
        "07": ["# [GET]: v1/shop/type", "#### QUERY - Get shop types", "#### QUERY - Get total items", "rowStatus", "ILIKE",
               "Page Index and Page Size must be greater than 0", "Row status must be one of ACTIVE, INACTIVE, LOCKED, ARCHIVED."],
    }
    for key, need in needles.items():
        for missing in missing_needles(mds[key], need):
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
        "08": ["# [POST]: v1/shop/upsert", "### Shop Rules", "#### Image Object", "#### QUERY - Check shop products in use", "#### QUERY - Check shop orders in use",
               "#### INSERT - Add the caller as ADMIN of the new shop", "#### QUERY - Check platform administrator", "#### QUERY - Get next seq of the image type",
               "#### UPDATE - Delete the images of a deleted shop", "AND s.row_status <> 'DELETED'\nAND s.id <> '<sequence.id>'", "(../../../schema/shop/m_shop.md)",
               "(../../../schema/shop/m_shop_image.md)", "(../../../schema/shop/m_shop_type.md)", "(../../../schema/shop/t_shop_user.md)", "(../../../schema/sales/t_order.md)",
               "Shop name already exists.", "Shop is used by products or orders.", "Shop not found.", "Shop image not found.", "Shop type not found.",
               "You do not have permission to manage this shop.", "Only a platform administrator can change the platform margin rate.",
               "The shop already has a LOGO image, update it with its id or delete it in the same request.", "A shop can have at most 10 BANNER images.",
               "Only one LOGO image and one WALLPAPER image are allowed in the request.", "never changes the lots that already exist",
               "approved by the product owner", "This permission model (the role `PLATFORM_ADMIN`, the ADMIN of the shop and the code E10009) was approved by the product owner.", "ck_m_shop_margin_rate_total", "E10003", "E10004", "E10005", "E10006", "E10009", "E90001", "Insert Shop Success"],
        "09": ["# [POST]: v1/shop/upsert/batch", "### Shop Rules (same as the single upsert, applied per shop)", "#### Shop Object", "#### Image Object", "shops[2]: Id is duplicated with shops[1].",
               "shops[2]: Name is duplicated with shops[0].", "Shops must contain 1 to 100 items.", "Swapping the names", "shops[2]: Shop is used by products or orders.",
               "shops[1].images[0]: Shop image not found.", "#### QUERY - Check shop orders in use", "approved by the product owner", "This permission model (the role `PLATFORM_ADMIN`, the ADMIN of the shop and the code E10009) was approved by the product owner.", "never changes the lots that already exist"],
        "10": ["# [GET]: v1/shop", "### Shop Inquiry Rules", "#### Shop Object", "#### Image Object", "#### QUERY - Get shops", "#### QUERY - Get total items",
               "#### QUERY - Get shop type names", "#### QUERY - Get shop images", "#### QUERY - Check shop members", "#### QUERY - Check platform administrator",
               "(../../../schema/shop/t_shop_user.md)", "(../../../schema/author/t_user_role.md)", "approved by the product owner", "Null when the caller is not an ACTIVE member", "ORDER BY si.type, si.seq, si.created_at, si.id", "then creation time, then `id`",
               "Row status must be one of ACTIVE, INACTIVE, LOCKED, ARCHIVED.", "Page Index and Page Size must be greater than 0", "ILIKE", "typeName"],
    }
    for key, need in needles.items():
        for missing in missing_needles(mds[key], need):
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
        "01": ["### Checkout Rules", "canCheckout", "#### Problem Object", "QUANTITY_EXCEEDS_STOCK", "#### QUERY - Get the cart lines to order",
               "#### QUERY - Get the SKU of each line with the lot that is on sale", "#### QUERY - Check the address of the user", "E10007"],
        "02": ["### Order Rules", "WAIT_PAYMENT", "expires_at", "ck_t_order_total_amount_sum", "ship_address", "#### INSERT - Create the order of a shop",
               "#### INSERT - Create the items of the order", "#### UPDATE - Take the quantity from the lot that is on sale",
               "AND quantity >= '<sequence.quantity>'", "AND is_on_sale = TRUE", "#### UPDATE - Delete the cart lines that were ordered",
               "one transaction", "E10007", "ck_t_shop_product_sku_lot_price_not_below_cost"],
        "03": ["### Order Inquiry Rules", "ORDER BY o.created_at DESC, o.id", "o.user_id = '<sequence.userId>'", "#### QUERY - Count the orders of the user", "ILIKE"],
        "04": ["### Shop Order Inquiry Rules", "E10009", "#### Fail - Forbidden", "#### QUERY - Check shop member", "#### QUERY - Check platform administrator",
               "approved by the product owner", "platformProfit", "ORDER BY o.created_at DESC, o.id", "INNER JOIN authen.m_user ui"],
        "05": ["### Cancel Rules", "#### UPDATE - Cancel the order", "AND status = 'WAIT_PAYMENT'", "#### UPDATE - Give the quantity back to the lot", "E10006",
               "restoredItems", "#### QUERY - Check shop member"],
    }
    for key, need in needles.items():
        for missing in missing_needles(mds[key], need):
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
        "11": ["# [POST]: v1/shop/user/upsert", "### Shop User Rules", approval, permission, "#### QUERY - Check shop member", "#### QUERY - Check shop administrator",
               "#### QUERY - Count the ADMIN members of the shop after the write", "#### QUERY - Check duplicate member", "#### QUERY - Check platform administrator",
               "(../../../schema/shop/t_shop_user.md)", "(../../../schema/authen/m_user.md)", "(../../../schema/author/t_user_role.md)",
               "AND su.row_status <> 'DELETED'\nAND su.id <> '<sequence.id>'", "User is already a member of the shop.", "The shop must keep at least one ADMIN.",
               "You do not have permission to manage the members of this shop.", "Shop user not found.", "Shop not found.", "User not found.",
               "Shop Id and User Id cannot be changed.", "Role must be ADMIN or STAFF.", "Row status must not be DELETED when inserting a shop user.",
               "A platform administrator cannot skip this rule", "can only delete or archive their own membership", "it must lock the row of the shop (`shop.m_shop`", "E10003", "E10004", "E10005", "E10006", "E10009", "E90001",
               "Insert Shop User Success"],
        "12": ["# [POST]: v1/shop/user/upsert/batch", "### Shop User Rules (same as the single upsert, applied per shop user)", approval, permission, "#### Shop User Object",
               "shopUsers[2]: Id is duplicated with shopUsers[1].", "shopUsers[2]: Shop Id and User Id are duplicated with shopUsers[0].", "Shop users must contain 1 to 100 items.",
               "#### QUERY - Count the ADMIN members of the shop after the write", "except the ADMIN rule that is checked once for each shop after all the items", "it must lock the row of the shop (`shop.m_shop`"],
        "13": ["# [GET]: v1/shop/user", "### Shop User Inquiry Rules", approval, permission, "#### Shop User Object", "#### QUERY - Get shop users", "#### QUERY - Get total items",
               "#### QUERY - Check shop member", "#### QUERY - Check platform administrator", "ORDER BY su.created_at DESC, su.id", "(../../../schema/shop/t_shop_user.md)",
               "(../../../schema/authen/m_user.md)", "(../../../schema/author/t_user_role.md)", "Shop Id or User Id is required.",
               "You do not have permission to view the members of this shop.", "The user name and the email address of a user are never returned",
               "list the shops of the caller", "Page Index and Page Size must be greater than 0", "ILIKE", "#### Success - My Shops"],
    }
    needles["13"] = [n if n != "list the shops of the caller" else "lists the shops of the caller" for n in needles["13"]]
    for key, need in needles.items():
        for missing in missing_needles(mds[key], need):
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
    needles = ["# [GET]: v1/storefront/shop/product", "### Shop Product List Rules", approval,
               "#### Shop Object", "#### Shop Image Object", "#### Product Object", "#### QUERY - Get shop", "#### QUERY - Get products of the shop",
               "#### QUERY - Get total items", "#### QUERY - Get the category and its sub categories", "#### QUERY - Get the first image of each product",
               "#### QUERY - Get shop images", "WITH RECURSIVE categories AS", "ORDER BY v.listed_at DESC, p.id", "-- ORDER BY (v.price_from IS NULL), v.price_from, p.id",
               "-- ORDER BY (v.price_from IS NULL), v.price_from DESC, p.id", "-- ORDER BY p.name, p.id", "AND l.quantity > 0", "AND v.price_from IS NOT NULL",
               "ORDER BY pi.product_id, pi.created_at, pi.id", "(../../../schema/shop/t_shop_product.md)", "(../../../schema/shop/m_shop.md)",
               "(../../../schema/product/m_product_category.md)", "(../../../schema/product/m_product_image.md)", "(../04-inquiry-storefront-product/spec.md)",
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
    page = "(../04-inquiry-storefront-product/spec.md)"
    needles = {
        "15": ["# [POST]: v1/shop/product-review/upsert", "### Review Rules", approval, "set by the delivery API (work package WP3)", page,
               "#### QUERY - Get the shop product that has a product page", "#### QUERY - Check that the caller has bought the product", "#### QUERY - Check existing review",
               "#### QUERY - Check duplicate review", "o.status = 'COMPLETED'",
               "WHERE r.id = '<sequence.id>'\nAND r.user_id = '<sequence.userId>'\nAND r.row_status = 'ACTIVE'",
               "WHERE r.shop_product_id = '<sequence.shopProductId>'\nAND r.user_id = '<sequence.userId>'\nAND r.row_status <> 'DELETED'",
               "(../../../schema/sales/t_order.md)", "(../../../schema/shop/t_shop_product_review.md)", "(../../../schema/shop/t_shop_product.md)",
               "You can review only a product that you have bought.", "You have already reviewed this product.", "Review not found.", "Product not found.",
               "Rating must be a whole number from 1 to 5.", "Comment must not be longer than 2000 characters.", "Shop Id and Product Id cannot be changed.",
               "Row status must be ACTIVE or DELETED, and must not be DELETED when inserting a review.", "There is no Archive for a customer.",
               "The rule is checked only when a review is inserted", "E10001", "E10002", "E10003", "E10004", "E10005", "E10009", "E90001", "Insert Shop Product Review Success"],
        "16": ["# [GET]: v1/storefront/product-review", "### Review Inquiry Rules", approval, page, "#### Summary Object", "#### Breakdown Object", "#### Review Object",
               "#### QUERY - Get the summary of the reviews", "#### QUERY - Get the number of reviews of each rating", "#### QUERY - Get reviews", "#### QUERY - Get total items",
               "ROUND(AVG(r.rating), 2)", "ORDER BY r.created_at DESC, r.id", "-- ORDER BY r.rating DESC, r.id", "-- ORDER BY r.rating, r.id", "(../../../schema/authen/m_user.md)",
               "(../../../schema/shop/t_shop_product_review.md)", "Shop Id and Product Id are required fields.", "Product not found.", "Page Index and Page Size must be greater than 0",
               "Rating must be a whole number from 1 to 5 and Sort must be one of NEWEST, HIGHEST, LOWEST.", "public: it needs no access token",
               "Every sort ends with `reviewId` ascending as the tie-break", "Rounded half up to 2 decimals", "#### Success - Highest", "#### Success - Rating Filter", "E10001", "E10004", "E90001"],
    }
    for key, need in needles.items():
        for missing in missing_needles(mds[key], need):
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
        "01": ["### Payment Rules", "CASH_ON_DELIVERY", "uq_t_payment_order_id_live", "header set to the id of the new payment row", "clientSecret", "amount x 100", "#### Fail - Conflict Payment In Progress",
               "#### INSERT - Create the payment", "#### UPDATE - Set the shipping fee and the amount of the order", "AND status = 'WAIT_PAYMENT'", "FOR UPDATE", "E10006", "E90001"],
        "02": ["### Webhook Rules", "stripe-signature", "raw body", "5 minutes", "LATE_PAYMENT_REFUNDED", "IGNORED", "payment_intent.succeeded", "charge.refunded",
               "#### UPDATE - Mark the payment as completed", "#### UPDATE - Confirm the order", "AND status = 'WAIT_PAYMENT'", "#### UPDATE - Mark the payment as refunded",
               "#### UPDATE - Give the quantity back to the lot", "idempotent", "E10001"],
        "03": ["### Payment Inquiry Rules", "ORDER BY p.created_at DESC, p.id", "o.user_id = '<sequence.userId>'", "#### QUERY - Count the payments of the user", "ILIKE"],
        "04": ["### Shop Payment Inquiry Rules", "E10009", "#### Fail - Forbidden", "#### QUERY - Check shop member", "#### QUERY - Check platform administrator",
               "providerPaymentId", "ORDER BY p.created_at DESC, p.id", "#### QUERY - Count the payments of the shop"],
        "05": ["### Refund Rules", "#### UPDATE - Refund the payment", "AND status = 'COMPLETED'", "#### UPDATE - Refund the order", "AND status = 'PAYMENT_CONFIRMED'",
               "#### UPDATE - Give the quantity back to the lot", "refund-", "E10006", "E10009", "restoredItems", "#### QUERY - Check shop member", "FOR UPDATE -- taken before the payment is changed"],
    }
    for key, need in needles.items():
        for missing in missing_needles(mds[key], need):
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
    "t_shipping": ["uq_t_shipping_carrier_name_tracking_number", "ck_t_shipping_shipped_has_tracking", "ck_t_shipping_delivered_at",
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
        for n in range(1, 7):
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
    "01": ["### Create Shipping Rules", "#### QUERY - Lock the order", "FOR UPDATE", "#### UPDATE - Start processing", "AND status = 'PAYMENT_CONFIRMED'",
           "#### QUERY - Get the quantity already assigned", "AND s.status IN ('PENDING', 'SHIPPED', 'DELIVERED')", "#### QUERY - Get the shipping method of the order",
           "p.status = 'COMPLETED'", "#### INSERT - Create the shipping", "#### INSERT - Add the items to the shipping", "#### Fail - Conflict Quantity",
           "#### Fail - Conflict Order Status", "#### Fail - Not Found Reference", "#### Fail - Forbidden", "E10009", "E10006",
           "validate the request (400) -> existence of the order and of the order items (404) -> permission of the caller (403)",
           "approved by the product owner", "#### QUERY - Check shop member", "#### QUERY - Check platform administrator"],
    "02": ["### Update Shipping Status Rules", "`PENDING` -> `SHIPPED`", "`PENDING` -> `CANCELLED`", "`SHIPPED` -> `RETURNED`", "#### UPDATE - Mark the shipping as shipped",
           "#### UPDATE - Cancel the shipping", "#### UPDATE - Mark the shipping as returned", "AND status = 'PENDING' -- no row changed means the status changed in the meantime",
           "AND status = 'SHIPPED' -- no row changed means the status changed in the meantime", "#### QUERY - Check duplicate tracking number",
           "#### QUERY - Count the shippings that are still active", "#### UPDATE - Give the order back to PAYMENT_CONFIRMED", "AND status = 'PROCESSING'",
           "#### QUERY - Lock the order", "FOR UPDATE", "#### Fail - Conflict Tracking Number", "#### Fail - Conflict Status", "E10003", "E10006", "E10009",
           "approved by the product owner", "#### QUERY - Check shop member", "#### QUERY - Check platform administrator"],
    "03": ["### Shipping Stop Rules", "#### INSERT - Create the stop", "#### UPDATE - Update, delete or archive the stop", "#### QUERY - Check duplicate stop number",
           "#### QUERY - Lock the order", "FOR UPDATE", "#### Fail - Bad Request Row Status", "#### Fail - Conflict Status", "E10003", "E10006", "E10009",
           "Delete 204 No Content (no response body)", "approved by the product owner", "#### QUERY - Check shop member"],
    "04": ["### Shop Shipping Inquiry Rules", "E10009", "#### Fail - Forbidden", "#### Fail - Not Found Reference", "#### QUERY - Check shop member",
           "#### QUERY - Check platform administrator", "#### QUERY - Check shop", "ORDER BY s.created_at DESC, s.id", "o.shop_id = '<sequence.shopId>'",
           "#### QUERY - Count the shippings of the shop", "#### QUERY - Get the stops of the shippings", "o.ship_address", "approved by the product owner"],
    "05": ["### Shipping Inquiry Rules", "ORDER BY s.created_at DESC, s.id", "o.user_id = '<sequence.userId>'", "#### QUERY - Count the shippings of the user",
           "ss.row_status = 'ACTIVE'", "sh.name ILIKE", "#### QUERY - Get the stops of the shippings", "approved by the product owner"],
    "06": ["### Confirm Delivery Rules", "#### UPDATE - Confirm the delivery", "AND status = 'SHIPPED' -- no row changed means the status changed in the meantime",
           "#### UPDATE - Complete the order", "AND status = 'PROCESSING'", "#### QUERY - Get the delivered quantity of every item", "s.status = 'DELIVERED'",
           "o.user_id = '<sequence.userId>'", "#### QUERY - Lock the order", "FOR UPDATE", "#### Fail - Conflict Status", "E10006",
           "approved by the product owner"],
}
# phrases that must appear at least n times (a rule or a guard that two statements share must not lose one copy unnoticed)
SHIPPING_COUNTS = {
    "01": {"approved by the product owner": 2},
    "02": {"AND status = 'PENDING' -- no row changed means the status changed in the meantime": 2,
           "AND status = 'SHIPPED' -- no row changed means the status changed in the meantime": 1, "approved by the product owner": 2},
    "03": {"approved by the product owner": 2},
    "04": {"o.shop_id = '<sequence.shopId>'": 2, "approved by the product owner": 2, "-- only when search is specified": 2},
    "05": {"o.user_id = '<sequence.userId>'": 2, "approved by the product owner": 1, "-- only when search is specified": 2},
    "06": {"approved by the product owner": 1},
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
    if shop_side and "shopId" not in md.split("### Shop Shipping Inquiry Rules")[0]:
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
    request_part = mds["01"].split("### Create Shipping Rules")[0] + mds["01"].split("#### Example Body Parameters")[1].split("## Example Request")[0]
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
    for key, need in SHIPPING_NEEDLES.items():
        for missing in missing_needles(mds[key], need):
            errors.append(f"{SHIPPING_SPECS[key]} missing: {missing}")
    for key, counts in SHIPPING_COUNTS.items():
        for phrase, n in counts.items():
            if mds[key].count(phrase) < n:
                errors.append(f"{SHIPPING_SPECS[key]}: '{phrase[:60]}' must appear at least {n} times, found {mds[key].count(phrase)}")
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
        rules = mds[key].split("#### Example Body Parameters")[0]
        if "SELECT ... FOR UPDATE" not in rules:
            errors.append(f"{SHIPPING_SPECS[key]}: the rules must say that the order row is locked with SELECT ... FOR UPDATE")
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
    if m["consent"]:
        upsert.extend(["`description` and `isRequired` are optional"])
        for lst in (upsert, batch):
            lst.extend(["Name is a required field.", "is_required", "isRequired", "null clears it"])
        inquiry.extend(["isRequired", "ct.is_required", "AND ct.is_required = '<sequence.isRequired>' -- only when isRequired is specified"])
    return [{"upsert": upsert, "batch": batch, "inquiry": inquiry}]


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
            for missing in missing_needles(md, master_needles(m)[0][kind]):
                errors.append(f"{path} missing: {missing!r}")
            for text, times in master_counted(m)[kind]:
                if md.count(text) != times:
                    errors.append(f"{path}: {text!r} must appear {times} time(s), found {md.count(text)}")
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
    "01": ["### Register Rules", "#### Fail - Bad Request Password", "TRUE, -- the first address of a user is the default address, whatever isDefault says",
           "PBKDF2-HMAC-SHA256", "Plain text over TLS", AUTHEN_POLICY],
    "02": ["### Login Rules", "(../../../schema/authen/l_user_login_attempt.md)", "#### QUERY - Count failed attempts", "#### INSERT - Record attempt",
           "#### INSERT - Create access token", "#### INSERT - Create refresh token", "5 `FAILED` attempts in the last 15 minutes", '"expiresIn": 900', "**Only `FAILED` rows are counted.**", "recorded as `REFUSED`, which is not counted",
           "The block therefore ends by itself as soon as the 5th most recent failure is older than 15 minutes", "The `FAILED` and `REFUSED` rows are committed although the answer is 401",
           "record `REFUSED` and answer 401 when there are 5", "record `FAILED` and answer 401 when it does not match or the user is not found", "record `SUCCESS`",
           "AND la.result = 'FAILED' -- refused attempts are never counted", "'<sequence.result>' -- SUCCESS, FAILED or REFUSED",
           "One answer for every failure", "Invalid username or password.", "SHA-256 (32 bytes), never as the token itself",
           "Lock order:", AUTHEN_LOCK, "14 days", "'<sequence.sessionId>', -- a new session id for every login",
           "**Authorization claims:**", "`roles`, `permissions` and `scopes`", "author.t_user_role", "author.m_role",
           "author.t_role_permission", "author.t_role_permission_scope", "author.t_user_permission", "author.t_permission_scope",
           "author.m_permission", "author.m_scope", "A user with no assigned role or permission can still log in"],
    "03": ["# [POST]: v1/auth/reset-password", "### Reset Password Rules", "The answer is always 200 with the same message",
           "If the email address is registered, a reset link has been sent.", "Throttle:", "3 times per hour", "uq_t_user_reset_password_user_id_active", "Lock order:",
           "#### QUERY - Lock the user", AUTHEN_LOCK, "#### QUERY - Count the requests of the last hour", "#### UPDATE - Make the old reset token INACTIVE",
           "#### INSERT - Create reset token", "WHERE u.email_address = '<sequence.emailAddressBytes>'\nAND u.row_status = 'ACTIVE'", "'<sequence.resetTokenHash>'",
           "30 minutes", "(../../../schema/authen/t_user_reset_password.md)", "(../../../schema/authen/m_user.md)", "Email Address is required and must be a valid email address.",
           "E10001", "E90001", "AND rp.created_at > '<sequence.windowStart>'", "AND row_status = 'ACTIVE'"],
    "04": ["# [POST]: v1/auth/create-new-password", "### Create New Password Rules", "Reset token is invalid or expired.", "New password must be different from the current password.",
           AUTHEN_POLICY, "AND row_status = 'ACTIVE'\nAND expired_at > NOW() AT TIME ZONE 'UTC'\nRETURNING id as reset_id", "#### UPDATE - Close the access tokens of the user",
           "#### UPDATE - Close the refresh tokens of the user", "#### UPDATE - Make the current password INACTIVE", "#### INSERT - Create password", "PBKDF2-HMAC-SHA256",
           "600,000", "Password storage: PBKDF2-HMAC-SHA256 with a random 16 byte salt and 600,000 iterations", "uq_m_user_password_user_id_password", AUTHEN_LOCK, "Lock order:", "(../../../schema/authen/m_user_password.md)",
           "WHERE user_id = '<sequence.userId>'\nAND row_status = 'ACTIVE'", "AND up.row_type = 'PASSWORD'\nAND up.row_status = 'ACTIVE'", "E10001", "E90001"],
    "05": ["# [POST]: v1/auth/refresh-token", "### Refresh Token Rules", "Invalid or expired refresh token.", "**Rotation:**", "**Reuse:**", "When the row became INACTIVE less than 10 seconds ago (configurable)", "**The closing of the session is committed although the answer is 401:**",
           "written in its own transaction that is committed before the answer is sent", "any other user gets 401 and **nothing has changed**, the refresh token is not made INACTIVE",
           "when the row was a reuse older than 10 seconds the session is closed and committed first", "are one transaction: when any of them fails nothing is saved",
           "RETURNING session_id -- no row means the answer is 401", "#### INSERT - Create refresh token", "#### INSERT - Create access token",
           "#### UPDATE - Close the refresh tokens of the session (reuse)", "#### UPDATE - Close the access tokens of the session (reuse)", AUTHEN_LOCK, "Lock order:",
           '"expiresIn": 900', "AND row_status = 'ACTIVE'\nAND expired_at > NOW() AT TIME ZONE 'UTC'\nRETURNING session_id", "SHA-256 (32 bytes), never as the token itself",
           "WHERE session_id = '<sequence.sessionId>'\nAND row_status = 'ACTIVE'"],
    "06": ["# [POST]: v1/auth/logout", "### Logout Rules", "every ACTIVE access token and refresh token that has the same `session_id`", "#### UPDATE - Close the access tokens of the session",
           "#### UPDATE - Close the refresh tokens of the session", "WHERE session_id = '<sequence.sessionId>'\nAND user_id = '<sequence.userId>'\nAND row_status = 'ACTIVE'",
           "Logout Success", AUTHEN_LOCK, "Lock order:", "Sessions of other devices are not changed."],
    "07": ["# [POST]: v1/user/profile/upsert", "### User Profile Rules", "Username, Email Address and Password cannot be changed here.", "-- only when firstName is specified (null clears it)",
           "-- only when lastName is specified (null clears it)", "-- only when displayName is specified (null clears it)", "-- only when profilePicturePath is specified (null clears it)",
           "-- only when phoneNumber is specified (null clears it)", "-- only when address is specified (null clears it)", "-- only when dateOfBirth is specified (null clears it)",
           "-- only when gender is specified (null clears it)", AUTHEN_LOCK, "uq_m_user_information_user_id", "Lock order:", "never read from the request"],
    "08": ["# [GET]: v1/user/profile", "### User Profile Inquiry Rules", "AND u.row_status = 'ACTIVE'", "never returned", "WHERE u.id = '<sequence.userId>'",
           "WHERE ui.user_id = '<sequence.userId>'"],
    "09": ["# [POST]: v1/user/address/upsert", "### User Address Rules", "uq_t_user_address_user_id_default", "A user can have at most 10 addresses.", "A default address must be ACTIVE.",
           "User address not found.", "#### UPDATE - Clear the old default", "#### UPDATE - Promote another default address", "AND ua.user_id = '<sequence.userId>'", "Lock order:", AUTHEN_LOCK,
           "Delete 204 No Content", "AND ua.row_status <> 'DELETED' -- an address of another user or a DELETED address counts as not found",
           "AND is_default\nAND row_status <> 'DELETED'", "Row status must not be DELETED when inserting a user address."],
    "10": ["# [GET]: v1/user/address", "### User Address Inquiry Rules", "ORDER BY ua.is_default DESC, ua.created_at DESC, ua.id",
           "Row status must be one of ACTIVE, INACTIVE.", "Page Index and Page Size must be greater than 0", "Request: `GET v1/user/address?id=%s`" % AUTHEN_ADDRESS_ID],
}
AUTHEN_COUNTED = {
    "10": [("WHERE ua.user_id = '<sequence.userId>'\nAND ua.row_status <> 'DELETED'", 2), ("AND ua.title ILIKE '%<sequence.search>%' -- only when search is specified", 2),
           ("AND ua.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified", 2)],
    "05": [("INSERT INTO authen.t_user_access_token (", 1), ("INSERT INTO authen.t_user_refresh_token (", 1),
           ("AND row_status = 'ACTIVE' -- only when the used token became INACTIVE more than 10 seconds ago", 2)],
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
            if body.get("isDefault") and body.get("rowStatus") != "ACTIVE" and label != "Delete":
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
SEQUENCE_SPEC_DIRS = (
    "e-commerce/doc/api/authen-and-author",
    "e-commerce/doc/api/consent",
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
            sql.append(lines[cursor][indent + 8:] if lines[cursor].startswith(" " * (indent + 8)) else lines[cursor].lstrip())
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


def check_api_sequence_spec() -> int:
    errors = []
    pairs = []
    for directory in SEQUENCE_SPEC_DIRS:
        pairs.extend(sorted((ROOT / directory).glob("*/spec.md")))
    if len(pairs) != 18:
        errors.append(f"expected 18 API specs in authen-and-author and consent, found {len(pairs)}")
    for spec_path in pairs:
        sequence_path = spec_path.with_name("sequence.wsd")
        relative_spec = spec_path.relative_to(ROOT)
        relative_sequence = sequence_path.relative_to(ROOT)
        if not sequence_path.exists() or not sequence_path.read_text(encoding="utf-8").strip():
            errors.append(f"{relative_sequence}: missing or empty")
            continue
        spec_operations = spec_database_operations(spec_path.read_text(encoding="utf-8"))
        sequence_text = sequence_path.read_text(encoding="utf-8")
        sequence_operations, lifecycle_errors = sequence_database_operations(sequence_text)
        errors.extend(f"{relative_sequence}: {error}" for error in lifecycle_errors)
        declared_tables = re.findall(r'^\s*database "[^"]+" as (\w+)$', sequence_text, re.MULTILINE)
        expected_tables = list(dict.fromkeys(table.split(".")[-1] for table, _, _ in spec_operations))
        if declared_tables != expected_tables:
            errors.append(
                f"{relative_sequence}: database participants {declared_tables} differ from spec tables {expected_tables}"
            )
        if not sequence_text.startswith("@startuml ") or not sequence_text.rstrip().endswith("@enduml"):
            errors.append(f"{relative_sequence}: must have @startuml and @enduml")
        if len(spec_operations) != len(sequence_operations):
            errors.append(
                f"{relative_sequence}: has {len(sequence_operations)} table interactions but {relative_spec} has {len(spec_operations)} SQL blocks"
            )
            continue
        for position, (spec_operation, sequence_operation) in enumerate(zip(spec_operations, sequence_operations), start=1):
            table, heading, sql = spec_operation
            sequence_table, sequence_heading, sequence_sql = sequence_operation
            if sequence_table != table.split(".")[-1] or sequence_heading != heading:
                errors.append(
                    f"{relative_sequence}: interaction {position} is {sequence_table} / {sequence_heading}, expected {table} / {heading}"
                )
            if normalize(sequence_sql) != normalize(sql):
                errors.append(f"{relative_sequence}: interaction {position} SQL differs from {relative_spec}")
    if errors:
        return fail("; ".join(errors))
    print("OK: api-sequence-spec (18 specs, SQL parity and table lifecycle)")
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
    "01": ["### Campaign Rules", "ck_m_campaign_period", "#### QUERY - Check existing campaign", "#### QUERY - Check duplicate campaign name",
           "#### INSERT - Create campaign", "#### UPDATE - Update, delete or archive campaign", "#### QUERY - Check campaign used",
           "#### INSERT - Create budget", "#### UPDATE - Change budget", "AND (budget - remaining) <= '<sequence.budget.budget>'",
           "'<sequence.budget.budget>', '<sequence.budget.budget>'", "#### INSERT - Create discount", "#### INSERT - Create campaign shop",
           "#### INSERT - Create campaign product", "#### QUERY - Check shop", "#### QUERY - Check product", "#### QUERY - Check product category",
           "#### Fail - Conflict In Use", "#### Fail - Conflict Budget Below Used", "#### Fail - Not Found Reference", "#### Fail - Forbidden",
           "#### Fail - Bad Request Row Status", "E10003", "E10005", "E10006", "E10009", "Delete 204 No Content (no response body)",
           "#### QUERY - Get the platform administrator role", "#### QUERY - Check platform administrator",
           "validate the request (400) -> existence of the campaign, the children and the shops, products and categories (404) -> permission (403)"],
    "02": ["### Campaign Inquiry Rules", "ORDER BY c.start_at DESC, c.id", "NOT EXISTS (", "cs.row_status = 'ACTIVE'", "#### QUERY - Count the campaigns",
           "#### QUERY - Check shop member", "#### QUERY - Check shop", "#### QUERY - Check platform administrator", "#### Fail - Forbidden",
           "#### Fail - Not Found Reference", "activeOnly", "#### QUERY - Get the budgets of the campaigns", "#### QUERY - Get the shops of the campaigns",
           "validate the request (400) -> existence of the shop (404) -> permission (403) -> read"],
    "03": ["### Campaign Ledger Inquiry Rules", "ORDER BY l.created_at DESC, l.id", "#### QUERY - Count the ledger entries", "#### Fail - Forbidden",
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
        "#### Success - With Campaign", "### Discount Example", "#### Success - With Capped Discount"],
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
    m = re.search(r"### Discount Example\n\n.*?\n\n((?:\|[^\n]*\n)+)", md, re.DOTALL)
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
        for missing in missing_needles(md, needles):
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
        for missing in missing_needles(mds[key], need):
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
AUTHOR_FORBIDDEN_TEXT = {"10": ["The user must be ACTIVE and the role must be ACTIVE, otherwise 404"]}


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
    if kind in ("upsert", "batch"):
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
    if m and key == m[2]:
        alias, ucol = m[7], m[8]
        return [(f"AND ({alias}.{ucol} ILIKE '%<sequence.search>%' OR {alias}.description ILIKE '%<sequence.search>%') -- only when search is specified", 2),
                (f"AND {alias}.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified", 2)]
    if key == "10":
        return [("-- only when the request gives the role (an insert, or opening a row that is not ACTIVE)", 2)]
    if key == "11":
        return [("AND ur.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified", 2), ("AND ur.role_id = '<sequence.filterRoleId>' -- only when roleId is specified", 2)]
    return []


AUTHOR_OTHER_NEEDLES = {
    "10": ["# [POST]: v1/author/user/role/upsert", "### User Role Rules", "**The platform keeps at least one administrator.**", "Lock order:", "FOR UPDATE -- the target users, in ascending id order, before any role row",
           "FOR UPDATE -- only when the request touches the PLATFORM_ADMIN assignment", "#### QUERY - Count the platform administrators after the write", "#### Fail - Conflict Last Administrator",
           "The platform must keep at least one administrator.", "The user already has this role.", "User Id and Role Id cannot be changed.", "-> permission (403, E10009) -> duplicate check (409, E10003) -> write -> last administrator rule",
           "AND ur.row_status = 'ACTIVE' -- the request is rolled back (409) when the count is 0", "        AND u.row_status = 'ACTIVE'\nWHERE ur.role_id = '<sequence.platformAdminRoleId>'", "INNER JOIN authen.m_user u", "Delete 204 No Content", "Archive when rowStatus is ARCHIVED", "User or role not found or not ACTIVE.", *AUTHOR_ADMIN,
           "**The user and the role must be ACTIVE only when the request gives the role**",
           "Taking the role away (`rowStatus` DELETED, ARCHIVED, INACTIVE or LOCKED) works whatever the status of the user and of the role is",
           "The last administrator rule below still applies in full.", "existence checks (404, the row of `id`, and the user and the role only when the request gives the role)"],
    "11": ["# [GET]: v1/author/user/role", "### User Role Inquiry Rules", "ORDER BY r.name, u.display_name, ur.id", f"Request: `GET v1/author/user/role?id={AUTHOR_USER_ROLE}`", "Only a platform administrator can read the roles of users",
           "#### Fail - Forbidden", "E10009", *AUTHOR_ADMIN],
    "12": ["# [GET]: v1/author/me", "### Me Rules", "not stored in the access token", "ORDER BY r.name, r.id", "AND r.row_status = 'ACTIVE'", "AND ur.row_status = 'ACTIVE'", "Any caller with a valid access token can call this API",
           "Success - Platform Administrator", "Success - No Role"],
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
            names = [r["name"] for r in data["roles"]]
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
        for missing in missing_needles(md, need):
            errors.append(f"{path} missing: {missing!r}")
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
