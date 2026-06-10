#!/usr/bin/env python3
"""Lightweight checks for repository Mermaid .mmd files."""

from __future__ import annotations

import sys
from pathlib import Path


VALID_PREFIXES = (
    "flowchart ",
    "graph ",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram",
    "stateDiagram-v2",
    "erDiagram",
    "journey",
    "gantt",
    "pie ",
    "mindmap",
    "timeline",
)


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    stripped = text.lstrip()

    if not stripped:
        return [f"{path}: empty file"]

    if stripped.startswith("```") or "```" in text:
        errors.append(f"{path}: .mmd files must not contain Markdown fences")

    first_line = stripped.splitlines()[0].strip()
    if not first_line.startswith(VALID_PREFIXES):
        errors.append(f"{path}: unexpected Mermaid declaration: {first_line!r}")

    if "\t" in text:
        errors.append(f"{path}: use spaces, not tabs")

    return errors


def main(argv: list[str]) -> int:
    if not argv:
        print("Usage: check_mmd_files.py <file-or-directory> [...]", file=sys.stderr)
        return 2

    paths: list[Path] = []
    for arg in argv:
        p = Path(arg)
        if p.is_dir():
            paths.extend(sorted(p.rglob("*.mmd")))
        else:
            paths.append(p)

    errors: list[str] = []
    for path in paths:
        if path.suffix != ".mmd":
            continue
        errors.extend(check_file(path))

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print(f"Checked {len([p for p in paths if p.suffix == '.mmd'])} .mmd file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
