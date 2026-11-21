#!/usr/bin/env python3
"""Build the skeleton of an API `sequence.wsd` from its `spec.md`, copying the SQL of the spec letter for letter.

Why generate: every database block of a sequence diagram has to repeat the SQL of the spec exactly, in the spec's
order, in a fixed shape (request, activate, note, return, deactivate) that `check_docs.py api-sequence-spec` reads.
Typing that by hand is where the copy mistakes come from, so the script writes everything that is mechanical and
leaves the decisions to the author as `' TODO(author): ...` comments. The author replaces every TODO with the real
branches (`alt` / `else`) of the spec; a TODO that stays in the file means the diagram is not finished.

Usage:
  python3 sequence_skeleton.py <path to spec.md>                 print the skeleton on stdout
  python3 sequence_skeleton.py <spec.md> [<spec.md> ...] --write  write sequence.wsd next to each spec
  --force                                                        overwrite a sequence.wsd that is not empty

`--write` refuses to overwrite a file that already has content (a hand-written diagram is never lost by accident).

What the skeleton holds:
  - the header of the login diagram (title, style, `hide footbox`), the actor, the page, the four Web API
    participants and one `database` participant per table, in the order the tables first appear in the spec;
  - the handler line `[**<Name>CommandHandler**]` when the spec writes data (INSERT, UPDATE or DELETE) and
    `[**<Name>QueryHandler**]` when it only reads;
  - a write API: `BEGIN READ COMMITTED`, `COMMIT`, `ROLLBACK`, the 400 E10001 branch and the 408 E90001 and 500
    branches around the work; an inquiry has no transaction;
  - one block per SQL of the spec, in the spec's order, with the SQL copied exactly (a line that starts with a
    quote is written as `&#39;` because PlantUML takes a leading quote for a comment, the checker decodes it);
  - TODO(author) comments for what only the author can decide: the order of the checks (400, 404, 403, 409),
    which block runs on which branch, locks, and the response of each outcome. The comments list the execution
    order and the success and failure examples of the spec as hints.
"""
import argparse
import re
import sys
from pathlib import Path

TODO = "' TODO(author):"

HEADER = """@startuml {pascal} Sequence

title {title} API Sequence

' Leading SQL apostrophes use &#39; so PlantUML preserves literals; parity compares decoded SQL.

' Visual style
skinparam defaultFontName "Sarabun"
skinparam defaultFontSize 14
skinparam backgroundColor #FFFFFF
skinparam shadowing false
skinparam roundcorner 10
skinparam sequence {{
    ArrowColor #475569
    ArrowFontColor #334155
    LifeLineBorderColor #CBD5E1
    LifeLineBackgroundColor #F8FAFC
    ParticipantBorderColor #94A3B8
    ParticipantBackgroundColor #F1F5F9
    ParticipantFontColor #0F172A
    GroupBorderColor #94A3B8
    GroupBackgroundColor #F8FAFC
    GroupFontColor #334155
}}

' Do not show participant footers at the bottom of the diagram
hide footbox

actor "User" as user
box "Frontend" #F8FAFC
    participant "{title} Page" as page
end box
box "Web API" #F8FAFC
    participant "API" as api
    participant "Application" as app
    participant "Domain" as domain
    participant "Infrastructure" as infra
end box
"""

RETURN_TEXT = {"QUERY": "query result", "INSERT": "inserted result", "UPDATE": "updated result", "DELETE": "deleted result"}


def folder_title(spec_path: Path, md: str = "") -> str:
    """`02-login` -> `Login`, `07-upsert-consent-type-batch` -> `Upsert Consent Type Batch`.

    The spelling of the `Name` row of the spec wins when it is the same words as the folder (`SKU` and not `Sku`).
    """
    words = re.sub(r"^\d+-", "", spec_path.parent.name).split("-")
    title = " ".join(word.capitalize() for word in words)
    name = re.sub(r" API$", "", spec_field(md, "Name"))
    return name if name.lower() == title.lower() else title


def database_operations(md: str) -> list[tuple[str, str, str]]:
    """(qualified table, operation heading, SQL) in specification order (same reading as check_docs.py)."""
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


def response_examples(md: str, kind: str) -> list[tuple[str, str, str]]:
    """(title, HTTP code, bizCode) of every `#### Success ...` or `#### Fail ...` example of the spec."""
    found = []
    pattern = rf"^#### ({kind}[^\n]*)\n(.*?)(?=^#### |^---|^## |\Z)"
    for match in re.finditer(pattern, md, re.MULTILINE | re.DOTALL):
        title, body = match.group(1), match.group(2)
        code = re.search(r'"code": (\d+)', body)
        biz = re.search(r'"bizCode": "([^"]+)"', body)
        if "HTTP/1.1 204 No Content" in body:
            found.append((title, "204", ""))
        elif code:
            found.append((title, code.group(1), biz.group(1) if biz else ""))
    return found


def spec_field(md: str, field: str) -> str:
    match = re.search(rf"^\| {field}\s+\| (.*?)\s+\|$", md, re.MULTILINE)
    return match.group(1) if match else ""


def endpoint_of(md: str) -> str:
    """`POST v1/auth/login` from the Method, Endpoint and Version rows of the spec header."""
    method = spec_field(md, "Method")
    endpoint = spec_field(md, "Endpoint").replace("{version}", spec_field(md, "Version") or "1")
    return f"{method} {endpoint}".strip()


def note_lines(sql: str, indent: int) -> list[str]:
    """The SQL lines inside the note, `indent + 8` columns in; a leading quote becomes `&#39;`."""
    lines = []
    for line in sql.split("\n"):
        if not line.strip():
            lines.append("")
            continue
        if line.lstrip().startswith("'"):
            line = line.replace("'", "&#39;", 1)
        lines.append(" " * (indent + 8) + line)
    return lines


def rendering_warnings(operations: list[tuple[str, str, str]]) -> list[str]:
    """SQL lines that PlantUML draws struck through: two `--` on one line (the Creole `--text--` markup in a note).

    The text still matches the spec for the checker; only the picture is affected. The script cannot change the
    line without breaking the letter-for-letter copy, so it says so and leaves the choice to the author.
    """
    return [f"{heading}: {line.strip()[:70]}" for _, heading, sql in operations for line in sql.split("\n") if re.search(r"--.*--", line)]


def database_block(table: str, heading: str, sql: str, indent: int) -> list[str]:
    pad = " " * indent
    verb = heading.split(" ", 1)[0]
    description = heading.split(" - ", 1)[-1]
    return [
        f"{pad}app -> infra: {heading}",
        f"{pad}infra -> {table}: {heading}",
        f"{pad}activate {table}",
        f"{pad}    note right of {table}",
        *note_lines(sql, indent),
        f"{pad}    end note",
        f"{pad}    {table} -> infra: Return {RETURN_TEXT[verb]}",
        f"{pad}deactivate {table}",
        f"{pad}infra -> app: Return result of {description}",
    ]


def hints(md: str) -> list[str]:
    """Comment lines that tell the author what the spec says about the order of checks and the responses."""
    lines = []
    execution = re.search(r"^- Execution order: (.*)$", md, re.MULTILINE)
    if execution:
        lines.append(f"'   Execution order in the spec: {execution.group(1)}")
    failures = [f"{title.split(' - ', 1)[-1]} {code} {biz}".strip() for title, code, biz in response_examples(md, "Fail")]
    if failures:
        lines.append("'   Failure examples in the spec: " + "; ".join(failures))
    return lines


def skeleton(spec_path: Path) -> str:
    md = spec_path.read_text(encoding="utf-8")
    title = folder_title(spec_path, md)
    operations = database_operations(md)
    writes = any(not heading.startswith("QUERY") for _, heading, _ in operations)
    tables = list(dict.fromkeys(table.split(".")[-1] for table, _, _ in operations))
    handler = f"{title.replace(' ', '')}{'Command' if writes else 'Query'}Handler"
    successes = response_examples(md, "Success")
    out = HEADER.format(pascal=title.replace(" ", ""), title=title).splitlines()
    if tables:
        out.append('box "Database" #F8FAFC')
        out.extend(f'    database "{table}" as {table}' for table in tables)
        out.append("end box")
    out.append("")

    def success_line() -> str:
        if not successes:
            return "app -> api: HTTP 200 S10000"
        _, code, biz = successes[0]
        return f"app -> api: HTTP {code} {biz}".strip()

    def success_hint() -> str:
        listed = "; ".join(f"{t.split(' - ', 1)[-1]} {c} {b}".strip() for t, c, b in successes)
        return f"'   Success examples in the spec: {listed}" if listed else ""

    blocks: list[str] = []
    for table, heading, sql in operations:
        blocks.extend(database_block(table.split(".")[-1], heading, sql, 20))

    out.append(f"user -> page: {'Submit' if writes else 'Request'} {title}")
    out.append("activate page")
    out.append(f"    page -> api: {endpoint_of(md)}")
    out.append("    activate api")
    out.append(f"        api -> app: [**{handler}**] Process request")
    out.append("        activate app")
    out.append("            app -> app: Create request context; generate requestId when omitted")
    out.append(f"            app -> app: Validate headers and {'body' if writes else 'query parameters'}")
    out.append("            alt Invalid input")
    out.append("                app -> api: HTTP 400 E10001")
    out.append("                api -> page: Bad request")
    out.append("                page -> user: Display validation error")
    out.append("            else Valid input")
    out.append(f"                {TODO} add the checks and branches of the spec (alt / else), replace this comment")
    out.extend(f"                {line}" for line in hints(md))
    if writes:
        out.append("                app -> infra: BEGIN READ COMMITTED")
        out.append("                activate infra")
        out.append("                alt Work completes before commit")
        out.append(f"                    {TODO} put each block on the branch where it runs, mark the lock (FOR UPDATE) and the values that pass between steps")
        out.extend(blocks)
        out.append(f"                    {TODO} one response for each outcome of the spec")
        if success_hint():
            out.append(f"                    {success_hint()}")
        out.append("                    app -> infra: COMMIT")
        out.append(f"                    {success_line()}")
        out.append("                    api -> page: Return committed result")
        out.append("                    page -> user: Display success result")
        out.append("                else Timeout before COMMIT")
        out.append("                    note over app, infra")
        out.append("                        A timeout can interrupt any preceding SQL or domain step.")
        out.append("                        No success response is sent without a successful COMMIT.")
        out.append("                    end note")
        out.append("                    app -> infra: ROLLBACK")
        out.append("                    app -> api: HTTP 408 E90001")
        out.append("                    api -> page: Request timeout")
        out.append("                    page -> user: Retry if needed")
        out.append("                else Unexpected failure before COMMIT")
        out.append("                    app -> infra: ROLLBACK")
        out.append("                    app -> api: HTTP 500 generic error; no new bizCode")
        out.append("                    api -> page: Internal server error")
        out.append("                    page -> user: Display generic failure")
        out.append("                end")
        out.append("                deactivate infra")
    else:
        if blocks:
            out.append("                app -> infra: Execute database operations")
            out.append("                activate infra")
            out.append(f"                    {TODO} put each block on the branch where it runs and the values that pass between steps")
            out.extend(blocks)
            out.append("                deactivate infra")
        out.append("                app -> domain: Apply domain rules and prepare response")
        out.append("                activate domain")
        out.append("                    domain -> app: Return response data")
        out.append("                deactivate domain")
        out.append(f"                {TODO} one response for each outcome of the spec")
        if success_hint():
            out.append(f"                {success_hint()}")
        out.append(f"                {success_line()}")
        out.append("                api -> page: Return success response")
        out.append("                page -> user: Display success result")
    out.append("            end")
    out.append("        deactivate app")
    out.append("    deactivate api")
    out.append("deactivate page")
    out.append("")
    out.append("@enduml")
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Build the skeleton of sequence.wsd from spec.md (SQL copied exactly).")
    parser.add_argument("specs", nargs="+", help="path of a spec.md")
    parser.add_argument("--write", action="store_true", help="write sequence.wsd next to each spec instead of printing")
    parser.add_argument("--force", action="store_true", help="overwrite a sequence.wsd that is not empty")
    args = parser.parse_args(argv)
    if len(args.specs) > 1 and not args.write:
        parser.error("several specs need --write")
    status = 0
    for name in args.specs:
        spec_path = Path(name)
        if spec_path.name != "spec.md" or not spec_path.is_file():
            print(f"{name}: not a spec.md file", file=sys.stderr)
            status = 1
            continue
        text = skeleton(spec_path)
        for warning in rendering_warnings(database_operations(spec_path.read_text(encoding="utf-8"))):
            print(f"warning: {spec_path}: PlantUML draws this SQL line struck through (two --): {warning}", file=sys.stderr)
        if not args.write:
            sys.stdout.write(text)
            continue
        target = spec_path.with_name("sequence.wsd")
        if target.exists() and target.read_text(encoding="utf-8").strip() and not args.force:
            print(f"{target}: not empty, refusing to overwrite (use --force)", file=sys.stderr)
            status = 1
            continue
        target.write_text(text, encoding="utf-8")
        print(f"wrote {target}")
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
