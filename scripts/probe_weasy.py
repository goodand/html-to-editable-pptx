#!/usr/bin/env python3
"""Probe WeasyPrint's box tree before adding parser fixtures.

This is intentionally observational: it records library-internal structure so
fixture authors can see wrappers, implicit table groups, namespaced tags, and
cell span attributes before changing extraction code.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

from weasyprint import HTML


def unwrap(box):
    inner = getattr(box, "_box", box)
    wrapper = type(box).__name__
    inner_type = type(inner).__name__
    return inner, (wrapper if wrapper != inner_type else None)


def bbox(box):
    return {
        "x": round(getattr(box, "position_x", 0), 2),
        "y": round(getattr(box, "position_y", 0), 2),
        "w": round(getattr(box, "width", 0), 2),
        "h": round(getattr(box, "height", 0), 2),
    }


def node_info(box, depth, max_depth):
    inner, wrapper = unwrap(box)
    info = {
        "type": type(inner).__name__,
        "depth": depth,
        "tag": str(getattr(inner, "element_tag", "") or ""),
        "bbox": bbox(inner),
    }
    if wrapper:
        info["wrapper"] = wrapper
    for attr in ("grid_x", "colspan", "rowspan"):
        if hasattr(inner, attr):
            info[attr] = getattr(inner, attr)
    if type(inner).__name__ == "TextBox":
        info["text"] = getattr(inner, "text", "")
    if depth < max_depth:
        children = getattr(inner, "children", [])
        info["children"] = [node_info(c, depth + 1, max_depth) for c in children]
    return info


def walk_types(box, counts, wrappers):
    inner, wrapper = unwrap(box)
    counts[type(inner).__name__] += 1
    if wrapper:
        wrappers[f"{wrapper}->{type(inner).__name__}"] += 1
    for child in getattr(inner, "children", []):
        walk_types(child, counts, wrappers)


def rows_under(table):
    rows = []
    nested_tables = 0

    def rec(box, root=False):
        nonlocal nested_tables
        inner, _ = unwrap(box)
        if type(inner).__name__ == "TableBox" and not root:
            nested_tables += 1
            return
        if type(inner).__name__ == "TableRowBox":
            rows.append(inner)
        for child in getattr(inner, "children", []):
            rec(child)

    rec(table, root=True)
    return rows, nested_tables


def table_summary(box):
    inner, _ = unwrap(box)
    rows, nested = rows_under(inner)
    out = {
        "bbox": bbox(inner),
        "directChildren": [type(unwrap(c)[0]).__name__ for c in getattr(inner, "children", [])],
        "recursiveRowsStoppingNestedTables": len(rows),
        "nestedTablesSkipped": nested,
        "rows": [],
    }
    for row in rows:
        cells = []
        for child in getattr(row, "children", []):
            cell, _ = unwrap(child)
            if type(cell).__name__ == "TableCellBox":
                cells.append({
                    "grid_x": getattr(cell, "grid_x", None),
                    "colspan": getattr(cell, "colspan", None),
                    "rowspan": getattr(cell, "rowspan", None),
                    "bbox": bbox(cell),
                })
        out["rows"].append(cells)
    return out


def collect_tables(box, tables):
    inner, _ = unwrap(box)
    if type(inner).__name__ == "TableBox":
        tables.append(table_summary(inner))
    for child in getattr(inner, "children", []):
        collect_tables(child, tables)


def probe(html_path, max_depth):
    doc = HTML(filename=html_path).render()
    counts, wrappers, tables = Counter(), Counter(), []
    pages = []
    for page in doc.pages:
        root = page._page_box
        walk_types(root, counts, wrappers)
        collect_tables(root, tables)
        pages.append(node_info(root, 0, max_depth))
    return {
        "input": html_path,
        "pages": len(doc.pages),
        "boxTypeCounts": dict(sorted(counts.items())),
        "wrappers": dict(sorted(wrappers.items())),
        "tables": tables,
        "tree": pages,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--out")
    ap.add_argument("--max-depth", type=int, default=8)
    args = ap.parse_args()
    report = probe(args.html, args.max_depth)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
