---
name: ER Diagram Editing
description: How to edit e-commerce/db/er-diagram.drawio safely when a table gains or loses rows, and how to render it to check the result. Read whenever a schema change touches the ER diagram.
---

# Editing and checking the ER diagram

The diagram is a draw.io file with eight pages (page numbers start at 1): 1 Overview, 2 Common · Authen, 3 Author, 4 Product, 5 Shop, 6 Order · Pay · Ship, 7 Campaign, 8 All Tables. A table appears on its schema page and again on page 8. `check_docs.py er` and `audit_all.py` check that every column is drawn and every FK has an edge, but only the rendered picture shows layout problems.

## Editing the XML

- Keep a backup copy before you edit (the scratch directory is fine).
- Each table is a `swimlane` cell; each row is a child cell with `parent="<table id>"` and `y = 28 + 22 × row index`. Row text looks like `FK    shop_id : uuid` (the key tag, spaces, `name : type`, a trailing ` ?` when nullable). Partial unique indexes and checks are not drawn; a plain `UNIQUE (...)` is drawn as the last row.
- Adding a row at the end of a table is the safest change. Give the new row a unique id and the **plain row style** (copy the style of a non-FK row such as `total_price`). Copying the style of an FK row paints the new column blue, which means "foreign key".
- Growing a table by N rows: raise the swimlane `height` by `22 × N`, then move down every table below it (and, on page 8, the group box that holds the tables, by the same amount). Edges that have `mxPoint` waypoints follow row positions; look at them in the render.
- Removing a row: delete the cell, renumber the `y` of the rows below, shrink the swimlane.
- Work on line numbers carefully: after you delete lines, indexes computed earlier are stale (this caused a crash once). Recompute ids from the file each time.
- Move the legend text on the page down when a table grew into it.

## Rendering

The draw.io desktop app is not on the PATH. Use the binary inside the app:

```bash
/Applications/draw.io.app/Contents/MacOS/draw.io -x -f png -p 6 -s 1 -o /tmp/er-p6.png e-commerce/db/er-diagram.drawio
```

`-p` is the 1-based page. Open the PNG (the Read tool shows images) and check: no table overlaps another or the legend, no FK line crosses a table, the added rows are visible and coloured like their kind, and the edge you added leaves from the right row. Render page 8 as well when you touched a table that is on it.
