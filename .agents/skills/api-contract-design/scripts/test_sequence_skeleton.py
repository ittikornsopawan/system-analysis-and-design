#!/usr/bin/env python3
"""Tests of sequence_skeleton.py against every API spec of the repository.

Run from anywhere: python3 .agents/skills/api-contract-design/scripts/test_sequence_skeleton.py

  1. Every spec.md (all groups): the skeleton is read back with the parser of `check_docs.py` (loaded with importlib;
     its structure check may only complain about the TODO(author) markers and its login standard must be met) and must hold the same table interactions as the spec, in order, with the SQL equal line for line, the same
     `database` participants, a clean lifecycle (activate, note, return, deactivate), balanced alt / else / end and
     activate / deactivate, the header of the login diagram, a handler line and TODO(author) markers.
  2. The hand-written diagrams (a sequence.wsd that is not empty): the database blocks and the participants that
     the script builds must equal the ones written by hand.
  3. The command line: print, `--write` into an empty file, refusal to overwrite a non-empty file, `--force`.

A failure of (2) means that the script is wrong or that the hand-written diagram is wrong, and the message says
which block differs.
"""
import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SCRIPT = HERE / "sequence_skeleton.py"
API_DIR = ROOT / "e-commerce" / "doc" / "api"
LOGIN = API_DIR / "authen-and-author" / "02-login"

sys.dont_write_bytecode = True  # importing the script must not leave a __pycache__ folder in the skill
sys.path.insert(0, str(HERE))
import sequence_skeleton  # noqa: E402


def load_checker():
    spec = importlib.util.spec_from_file_location("check_docs", ROOT / "e-commerce" / "db" / "tests" / "check_docs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECK = load_checker()
SPECS = sorted(API_DIR.glob("*/*/spec.md"))


def decoded_sql_lines(sql: str) -> list[str]:
    """SQL lines of a note with the &#39; of a leading quote decoded, trailing blanks removed."""
    return [line.rstrip() for line in sql.split("\n")]


def balance_errors(text: str) -> list[str]:
    """Structure PlantUML needs: alt / end, note / end note, box / end box, activate / deactivate per participant."""
    errors = []
    stack = []
    active = {}
    in_note = False
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if in_note:
            if line == "end note":
                in_note = False
            continue
        if re.match(r"^note (right of|over|left of)\b", line):
            in_note = True
        elif line.startswith("alt "):
            stack.append(("alt", number))
        elif line == "else" or line.startswith("else "):
            if not stack or stack[-1][0] != "alt":
                errors.append(f"line {number}: else without alt")
        elif line == "end":
            if not stack:
                errors.append(f"line {number}: end without alt")
            else:
                stack.pop()
        elif line.startswith("box "):
            stack.append(("box", number))
        elif line == "end box":
            if not stack or stack[-1][0] != "box":
                errors.append(f"line {number}: end box without box")
            else:
                stack.pop()
        elif line.startswith("activate "):
            name = line.split()[1]
            active[name] = active.get(name, 0) + 1
        elif line.startswith("deactivate "):
            name = line.split()[1]
            active[name] = active.get(name, 0) - 1
            if active[name] < 0:
                errors.append(f"line {number}: deactivate {name} without activate")
    if in_note:
        errors.append("a note is not closed")
    errors.extend(f"line {n}: {kind} is not closed" for kind, n in stack)
    errors.extend(f"{name} is still active at the end" for name, depth in active.items() if depth > 0)
    return errors


def header_of(text: str) -> list[str]:
    """Lines from the style comment to `hide footbox`, plus the Web API box (the part that is the same in every diagram)."""
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("' Leading SQL apostrophes"))
    stop = next(i for i, line in enumerate(lines) if line == "hide footbox")
    web = next(i for i, line in enumerate(lines) if line == 'box "Web API" #F8FAFC')
    return lines[start:stop + 1] + lines[web:web + 6]


class SkeletonOfEverySpec(unittest.TestCase):
    def test_specs_were_found(self):
        self.assertEqual(len(SPECS), 83, "the repository has 83 API specs")

    def test_every_skeleton_matches_its_spec(self):
        login_header = header_of((LOGIN / "sequence.wsd").read_text(encoding="utf-8"))
        problems = []
        for spec_path in SPECS:
            name = f"{spec_path.parent.parent.name}/{spec_path.parent.name}"
            md = spec_path.read_text(encoding="utf-8")
            text = sequence_skeleton.skeleton(spec_path)
            spec_ops = CHECK.spec_database_operations(md)
            seq_ops, lifecycle = CHECK.sequence_database_operations(text)
            problems.extend(f"{name}: {error}" for error in lifecycle)
            if len(seq_ops) != len(spec_ops):
                problems.append(f"{name}: {len(seq_ops)} table interactions, the spec has {len(spec_ops)}")
                continue
            for position, ((table, heading, sql), (s_table, s_heading, s_sql)) in enumerate(zip(spec_ops, seq_ops), start=1):
                if s_table != table.split(".")[-1] or s_heading != heading:
                    problems.append(f"{name}: interaction {position} is {s_table} / {s_heading}, expected {table} / {heading}")
                if decoded_sql_lines(s_sql) != decoded_sql_lines(sql):
                    problems.append(f"{name}: interaction {position} SQL is not copied letter for letter")
                if CHECK.normalize(s_sql) != CHECK.normalize(sql):
                    problems.append(f"{name}: interaction {position} SQL differs for the checker")
            declared = re.findall(r'^\s*database "[^"]+" as (\w+)$', text, re.MULTILINE)
            expected = list(dict.fromkeys(table.split(".")[-1] for table, _, _ in spec_ops))
            if declared != expected:
                problems.append(f"{name}: participants {declared}, expected {expected}")
            problems.extend(f"{name}: {error}" for error in balance_errors(text))
            if not text.startswith("@startuml ") or not text.rstrip().endswith("@enduml"):
                problems.append(f"{name}: needs @startuml and @enduml")
            if header_of(text) != login_header:
                problems.append(f"{name}: the header differs from the login diagram")
            writes = any(not heading.startswith("QUERY") for _, heading, _ in spec_ops)
            handler = re.search(r"\[\*\*(\w+)Handler\*\*\]", text)
            if not handler or not handler.group(1).endswith("Command" if writes else "Query"):
                problems.append(f"{name}: handler line is missing or has the wrong kind (writes={writes})")
            transaction = {"BEGIN READ COMMITTED", "COMMIT", "ROLLBACK"}
            lines = {line.strip().split(": ", 1)[-1] for line in text.splitlines() if " -> infra: " in line}
            if writes and not transaction <= lines:
                problems.append(f"{name}: a write API needs BEGIN READ COMMITTED, COMMIT and ROLLBACK")
            if not writes and transaction & lines:
                problems.append(f"{name}: an inquiry has no transaction")
            if writes and (text.count("BEGIN READ COMMITTED") != 1 or text.count("app -> infra: COMMIT") != 1 or text.count("app -> infra: ROLLBACK") != 2):
                problems.append(f"{name}: a write API needs one BEGIN, one COMMIT and two ROLLBACK (timeout and failure)")
            if writes and not all(code in text for code in ("HTTP 400 E10001", "HTTP 408 E90001", "HTTP 500")):
                problems.append(f"{name}: a write API needs the 400, 408 and 500 branches")
            method = re.search(r"^\| Method\s+\| (\w+)", md, re.MULTILINE).group(1)
            endpoint = re.search(r"^\| Endpoint\s+\| (\S+)", md, re.MULTILINE).group(1).replace("{version}", "1")
            if f"    page -> api: {method} {endpoint}" not in text.splitlines():
                problems.append(f"{name}: the page must call {method} {endpoint}")
            words = re.sub(r"^\d+-", "", spec_path.parent.name).replace("-", " ")
            title = re.search(r"^title (.*) API Sequence$", text, re.MULTILINE)
            page = re.search(r'participant "(.*) Page" as page', text)
            if not title or not page or title.group(1).lower() != words or page.group(1).lower() != words:
                problems.append(f"{name}: the title and the page must be named after the folder ({words})")
            if CHECK.sequence_structure_errors(text) != ["still has a TODO(author) marker"]:
                problems.append(f"{name}: the checker finds {CHECK.sequence_structure_errors(text)}, only the TODO marker is expected")
            if writes and CHECK.sequence_login_standard_errors(text):
                problems.append(f"{name}: the login standard of the checker is not met: {CHECK.sequence_login_standard_errors(text)}")
            if text.count("' TODO(author):") < 2:
                problems.append(f"{name}: the TODO(author) markers are missing")
            if re.search(r"[ \t]+$", text, re.MULTILINE):
                problems.append(f"{name}: trailing whitespace in the skeleton")
        self.assertEqual(problems, [], "\n".join(problems[:40]))

    def test_leading_quote_is_escaped(self):
        sql = "VALUES (\n    '<sequence.id>',\n    NOW()\n)"
        lines = sequence_skeleton.note_lines(sql, 20)
        self.assertEqual(lines[1], " " * 28 + "    &#39;<sequence.id>',")
        self.assertEqual(lines[2], " " * 28 + "    NOW()")


    def test_every_operation_kind_is_read_from_the_spec(self):
        md = "\n".join(["### Table: [s.t](x.md)", ""] + [f"#### {kind} - do it\n\n```SQL\n{kind} 1\n```\n" for kind in ("QUERY", "INSERT", "UPDATE", "DELETE")])
        self.assertEqual([h for _, h, _ in sequence_skeleton.database_operations(md)], [f"{k} - do it" for k in ("QUERY", "INSERT", "UPDATE", "DELETE")])
        block = sequence_skeleton.database_block("t", "DELETE - do it", "DELETE 1", 20)
        self.assertIn(" " * 24 + "t -> infra: Return deleted result", block)

    def test_blank_sql_line_stays_empty(self):
        lines = sequence_skeleton.note_lines("SELECT 1\n\nFROM t", 20)
        self.assertEqual(lines[1], "")

    def test_title_keeps_the_spelling_of_the_spec(self):
        text = sequence_skeleton.skeleton(API_DIR / "shop" / "01-upsert-shop-product-sku" / "spec.md")
        self.assertIn('participant "Upsert Shop Product SKU Page" as page', text)
        self.assertIn("title Upsert Shop Product SKU API Sequence", text)
        self.assertIn("[**UpsertShopProductSKUCommandHandler**]", text)

    def test_double_dash_line_is_reported(self):
        operations = [("t", "QUERY - x", "SELECT 1\n-- ORDER BY a -- sort A\nWHERE x = 1 -- one comment")]
        warnings = sequence_skeleton.rendering_warnings(operations)
        self.assertEqual(len(warnings), 1)
        self.assertIn("sort A", warnings[0])


class HandWrittenDiagrams(unittest.TestCase):
    def test_database_blocks_and_participants_equal_the_hand_written_ones(self):
        problems = []
        written = sorted(p for p in API_DIR.glob("*/*/sequence.wsd") if p.read_text(encoding="utf-8").strip())
        self.assertGreaterEqual(len(written), 1)
        for wsd_path in written:
            name = f"{wsd_path.parent.parent.name}/{wsd_path.parent.name}"
            hand = wsd_path.read_text(encoding="utf-8")
            generated = sequence_skeleton.skeleton(wsd_path.with_name("spec.md"))
            hand_ops, _ = CHECK.sequence_database_operations(hand)
            gen_ops, _ = CHECK.sequence_database_operations(generated)
            if [(t, h, CHECK.normalize(s)) for t, h, s in hand_ops] != [(t, h, CHECK.normalize(s)) for t, h, s in gen_ops]:
                problems.append(f"{name}: the database blocks differ")
            hand_tables = re.findall(r'^\s*database "[^"]+" as (\w+)$', hand, re.MULTILINE)
            gen_tables = re.findall(r'^\s*database "[^"]+" as (\w+)$', generated, re.MULTILINE)
            if hand_tables != gen_tables:
                problems.append(f"{name}: participants {hand_tables} (hand) and {gen_tables} (script) differ")
        self.assertEqual(problems, [], "\n".join(problems))


class CommandLine(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)

    def make_spec(self, directory: Path) -> Path:
        folder = directory / "02-login"
        folder.mkdir(parents=True)
        spec = folder / "spec.md"
        spec.write_text((LOGIN / "spec.md").read_text(encoding="utf-8"), encoding="utf-8")
        return spec

    def test_print_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = self.make_spec(Path(tmp))
            result = self.run_script(str(spec))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(result.stdout.startswith("@startuml Login Sequence"))
            self.assertFalse(spec.with_name("sequence.wsd").exists())

    def test_write_refuses_a_file_with_content_unless_forced(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = self.make_spec(Path(tmp))
            target = spec.with_name("sequence.wsd")
            target.write_text("", encoding="utf-8")
            self.assertEqual(self.run_script(str(spec), "--write").returncode, 0)
            first = target.read_text(encoding="utf-8")
            self.assertTrue(first.startswith("@startuml"))
            target.write_text("hand written\n", encoding="utf-8")
            refused = self.run_script(str(spec), "--write")
            self.assertEqual(refused.returncode, 1)
            self.assertEqual(target.read_text(encoding="utf-8"), "hand written\n")
            self.assertEqual(self.run_script(str(spec), "--write", "--force").returncode, 0)
            self.assertEqual(target.read_text(encoding="utf-8"), first)

    def test_several_specs_need_write_and_a_wrong_path_fails(self):
        self.assertNotEqual(self.run_script(str(LOGIN / "spec.md"), str(LOGIN / "spec.md")).returncode, 0)
        self.assertEqual(self.run_script(str(LOGIN / "sequence.wsd")).returncode, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
