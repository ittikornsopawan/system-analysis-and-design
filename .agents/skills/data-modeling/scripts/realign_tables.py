#!/usr/bin/env python3
"""Re-align the markdown tables of the given files so every column has the same width on every row.

The spec checker (check_docs.py) fails on a table whose rows are not padded to the same widths, and a
row added by hand is almost never padded. Run this after editing a table instead of padding by hand.
Tables inside code fences are left alone.

Usage: python3 realign_tables.py <file.md> [<file.md> ...]
"""
import sys


def realign(lines):
    out, i, in_fence = [], 0, False
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            in_fence = not in_fence
        if not in_fence and line.startswith("|"):
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in lines[i:j]]
            n = len(rows[0])
            if any(len(r) != n for r in rows):
                out.extend(lines[i:j])  # ragged table (a cell holds a pipe): leave it, report it
                print("skipped a table with an uneven cell count near line %d" % (i + 1), file=sys.stderr)
            else:
                widths = [max(3, max(len(r[k]) for idx, r in enumerate(rows) if idx != 1)) for k in range(n)]
                for idx, r in enumerate(rows):
                    cells = ("-" * widths[k] if idx == 1 else r[k].ljust(widths[k]) for k in range(n))
                    out.append("| " + " | ".join(cells) + " |")
            i = j
        else:
            out.append(line)
            i += 1
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(realign(text.split("\n"))))
