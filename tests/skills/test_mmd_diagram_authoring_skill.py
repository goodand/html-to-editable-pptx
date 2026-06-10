from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = (
    REPO_ROOT
    / "skills"
    / "architecture"
    / "mmd-diagram-authoring"
    / "scripts"
    / "check_mmd_files.py"
)


def run_checker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def write_mmd(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_single_valid_file_passes(tmp_path: Path) -> None:
    write_mmd(tmp_path / "single.mmd", "flowchart TD\n    A[Start] --> B[End]\n")
    result = run_checker(str(tmp_path))
    assert result.returncode == 0
    assert "Checked 1 .mmd file(s)" in result.stdout


def test_markdown_fences_fail(tmp_path: Path) -> None:
    write_mmd(tmp_path / "fenced.mmd", "```mermaid\nflowchart TD\nA-->B\n```\n")
    result = run_checker(str(tmp_path))
    assert result.returncode == 1
    assert "must not contain Markdown fences" in result.stderr


def test_tabs_fail(tmp_path: Path) -> None:
    write_mmd(tmp_path / "tabs.mmd", "flowchart TD\n\tA[Start] --> B[End]\n")
    result = run_checker(str(tmp_path))
    assert result.returncode == 1
    assert "use spaces, not tabs" in result.stderr


def test_bad_declaration_fails(tmp_path: Path) -> None:
    write_mmd(tmp_path / "bad.mmd", "flowchat TD\n    A[Start] --> B[End]\n")
    result = run_checker(str(tmp_path))
    assert result.returncode == 1
    assert "unexpected Mermaid declaration" in result.stderr


def test_parity_ok_pair_reports_summary(tmp_path: Path) -> None:
    text_en = "flowchart TD\n    A[One] --> B[Two]\n"
    text_ko = "flowchart TD\n    A[하나] --> B[둘]\n"
    write_mmd(tmp_path / "02_pair.en.mmd", text_en)
    write_mmd(tmp_path / "02_pair.ko.mmd", text_ko)
    result = run_checker(str(tmp_path))
    assert result.returncode == 0
    assert "parity: ok (1 pairs)" in result.stdout


def test_parity_mismatch_fails(tmp_path: Path) -> None:
    text_en = "flowchart TD\n    A[One] --> B[Two]\n"
    text_ko = "flowchart TD\n    A[하나] --> B[둘]\n    B[둘] --> C[셋]\n"
    write_mmd(tmp_path / "02_pair.en.mmd", text_en)
    write_mmd(tmp_path / "02_pair.ko.mmd", text_ko)
    result = run_checker(str(tmp_path))
    assert result.returncode == 1
    assert "parity: mismatch" in result.stdout
    assert "edge parity mismatch" in result.stderr


def test_log_appends_and_no_log_skips(tmp_path: Path) -> None:
    write_mmd(tmp_path / "single.mmd", "flowchart TD\n    A[Start] --> B[End]\n")
    log_path = tmp_path / ".mmd_check_log.jsonl"

    first = run_checker(str(tmp_path))
    second = run_checker(str(tmp_path))
    no_log = run_checker("--no-log", str(tmp_path))

    assert first.returncode == 0
    assert second.returncode == 0
    assert no_log.returncode == 0

    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    records = [json.loads(line) for line in lines]
    assert records[0]["parity"] == "n/a"
    assert records[1]["error_count"] == 0


def test_empty_directory_fails(tmp_path: Path) -> None:
    result = run_checker(str(tmp_path))
    assert result.returncode == 1
    assert "no .mmd files found under" in result.stderr


def test_missing_path_fails_with_usage_error() -> None:
    missing = "/tmp/no_such_dir_zz_test"
    result = run_checker(missing)
    assert result.returncode == 2
    assert "path does not exist" in result.stderr


def test_multiple_directories_do_not_crash_logging(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    write_mmd(first / "a.mmd", "flowchart TD\n    A[One] --> B[Two]\n")
    write_mmd(second / "b.mmd", "flowchart TD\n    A[One] --> B[Two]\n")

    result = run_checker(str(first), str(second))

    assert result.returncode == 0
    assert "Checked 2 .mmd file(s)" in result.stdout

    log_path = first / ".mmd_check_log.jsonl"
    record = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert len(record["files"]) == 2
    assert any(entry == "a.mmd" for entry in record["files"])
    assert any(entry.endswith("second/b.mmd") or entry.endswith("b.mmd") for entry in record["files"])
