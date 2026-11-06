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
        "52 tables in 11 schemas",
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
    for k, ex in enumerate(order_examples(md, "Success")):
        data, tag = ex["data"], f"01 example {k}"
        count = qty = 0
        total = 0.0
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
            if p["reason"] not in ("QUANTITY_EXCEEDS_STOCK", "OUT_OF_STOCK", "UNAVAILABLE"):
                errors.append(f"{tag}: unknown problem reason {p['reason']}")
            if p["reason"] == "QUANTITY_EXCEEDS_STOCK" and not 0 < p["maxOrderQuantity"] < p["quantity"]:
                errors.append(f"{tag}: QUANTITY_EXCEEDS_STOCK needs 0 < maxOrderQuantity < quantity")
    return errors


def check_order_create(md: str) -> list[str]:
    errors = []
    for ex in order_examples(md, "Success"):
        ids = set()
        for o in ex["data"]["orders"]:
            errors.extend(order_total_errors(f"02 order {o['code']}", o))
            if o["status"] != "WAIT_PAYMENT":
                errors.append(f"02 order {o['code']}: a created order must be WAIT_PAYMENT")
            if o["totalDiscount"] or o["totalTax"] or o["totalShipping"]:
                errors.append(f"02 order {o['code']}: discount, tax and shipping are 0.00 for now")
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
    for key, want in {"01": {"Success": 200, "Success - With Problems": 200}, "02": {"Success": 201}, "03": {"Success": 200, "Success - Empty": 200},
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
