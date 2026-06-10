#!/usr/bin/env python3
"""Lightweight checks for repository Mermaid .mmd files."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
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

PAIR_NAME_RE = re.compile(r"^(?P<stem>\d+_[^.]+)\.(?P<lang>en|ko)\.mmd$")
NODE_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*[\[\{\(]", re.MULTILINE)
EDGE_RE = re.compile(
    r"([A-Za-z][A-Za-z0-9_]*)"
    r"(?:\s*[\[\{\(][^\]\}\)]*[\]\}\)])?"
    r"\s*(?:-->|---|-.->|==>)\s*"
    r"([A-Za-z][A-Za-z0-9_]*)"
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


def graph_signature(path: Path) -> tuple[set[str], set[tuple[str, str]]]:
    text = path.read_text(encoding="utf-8")
    node_ids = set(NODE_RE.findall(text))
    edges = {
        (src, dst)
        for src, dst in EDGE_RE.findall(text)
        if src not in {"subgraph", "end"} and dst not in {"subgraph", "end"}
    }
    return node_ids, edges


def check_parity(paths: list[Path]) -> tuple[list[str], str]:
    pairs: dict[str, dict[str, Path]] = {}
    for path in paths:
        match = PAIR_NAME_RE.match(path.name)
        if not match:
            continue
        pairs.setdefault(match.group("stem"), {})[match.group("lang")] = path

    comparable = {
        stem: lang_map
        for stem, lang_map in pairs.items()
        if "en" in lang_map and "ko" in lang_map
    }
    if not comparable:
        return [], "parity: n/a (no pairs)"

    errors: list[str] = []
    for stem, lang_map in sorted(comparable.items()):
        en_nodes, en_edges = graph_signature(lang_map["en"])
        ko_nodes, ko_edges = graph_signature(lang_map["ko"])
        if en_nodes != ko_nodes:
            errors.append(
                f"{stem}: node parity mismatch: "
                f"en={sorted(en_nodes)} ko={sorted(ko_nodes)}"
            )
        if en_edges != ko_edges:
            errors.append(
                f"{stem}: edge parity mismatch: "
                f"en={sorted(en_edges)} ko={sorted(ko_edges)}"
            )

    summary = (
        f"parity: ok ({len(comparable)} pairs)"
        if not errors
        else "parity: mismatch"
    )
    return errors, summary


def write_log(
    target_dir: Path,
    paths: list[Path],
    errors: list[str],
    parity_status: str,
) -> None:
    def render_path(path: Path) -> str:
        try:
            return str(path.relative_to(target_dir))
        except ValueError:
            cwd = Path.cwd().resolve()
            try:
                return os.path.relpath(path.resolve(), start=cwd)
            except ValueError:
                return str(path.resolve())

    log_path = target_dir / ".mmd_check_log.jsonl"
    record = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "files": [render_path(path) for path in paths],
        "error_count": len(errors),
        "errors": errors,
        "parity": parity_status,
    }
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def main(argv: list[str]) -> int:
    if not argv:
        print("Usage: check_mmd_files.py <file-or-directory> [...]", file=sys.stderr)
        return 2

    no_log = False
    if "--no-log" in argv:
        no_log = True
        argv = [arg for arg in argv if arg != "--no-log"]
        if not argv:
            print("Usage: check_mmd_files.py <file-or-directory> [...]", file=sys.stderr)
            return 2

    paths: list[Path] = []
    log_target: Path | None = None
    for arg in argv:
        p = Path(arg)
        if not p.exists():
            print(f"{p}: path does not exist", file=sys.stderr)
            return 2
        if p.is_dir():
            if log_target is None:
                log_target = p
            paths.extend(sorted(p.rglob("*.mmd")))
        else:
            paths.append(p)

    mmd_paths = [p for p in paths if p.suffix == ".mmd"]
    if not mmd_paths:
        print(
            f"no .mmd files found under: {', '.join(argv)}",
            file=sys.stderr,
        )
        return 1

    errors: list[str] = []
    for path in mmd_paths:
        errors.extend(check_file(path))

    parity_errors, parity_summary = check_parity(mmd_paths)
    errors.extend(parity_errors)
    parity_status = (
        "ok" if parity_summary.startswith("parity: ok") else
        "mismatch" if parity_summary.endswith("mismatch") else
        "n/a"
    )

    if log_target is not None and not no_log:
        write_log(log_target, mmd_paths, errors, parity_status)

    print(parity_summary)
    print(f"Checked {len(mmd_paths)} .mmd file(s)")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
