#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    print("Python 3.11+ is required.", file=sys.stderr)
    raise

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "third_party" / "repositories.toml"
MANIFEST_DIR = REPO_ROOT / "third_party" / "manifests"
RESULTS_DIR = REPO_ROOT / "third_party" / "clone_results"


def load_manifests() -> list[Path]:
    if len(sys.argv) > 1:
        return [Path(p).resolve() for p in sys.argv[1:]]
    manifests = [DEFAULT_MANIFEST]
    if MANIFEST_DIR.exists():
        manifests.extend(sorted(MANIFEST_DIR.glob("*.toml")))
    return [p for p in manifests if p.exists()]


def clone_repo(repo: dict, root: Path, depth: int, manifest: Path) -> dict:
    repo_id = repo["id"]
    full_name = repo["full_name"]
    dest = root / repo_id
    url = f"https://github.com/{full_name}.git"
    first_error = ""
    retry_error = ""

    if (dest / ".git").exists():
        status = "already_cloned"
    else:
        if dest.exists():
            shutil.rmtree(dest)
        cmd = ["git", "clone", "--depth", str(depth), "--single-branch", "--filter=blob:none", url, str(dest)]
        proc = subprocess.run(cmd, text=True, capture_output=True)
        first_error = proc.stderr.strip()
        if proc.returncode != 0:
            if dest.exists():
                shutil.rmtree(dest, ignore_errors=True)
            cmd = ["git", "clone", "--depth", str(depth), "--single-branch", url, str(dest)]
            proc = subprocess.run(cmd, text=True, capture_output=True)
            retry_error = proc.stderr.strip()
        status = "cloned" if proc.returncode == 0 else "failed"

    commit = ""
    if (dest / ".git").exists():
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=dest, text=True).strip()

    print(f"[{status}] {repo_id} {commit[:12]}")
    return {
        "id": repo_id,
        "full_name": full_name,
        "category": repo.get("category", ""),
        "priority": repo.get("priority", None),
        "status": status,
        "commit": commit,
        "path": str(dest.relative_to(REPO_ROOT)),
        "manifest": str(manifest.relative_to(REPO_ROOT)),
        "first_error": first_error if status == "failed" else "",
        "retry_error": retry_error if status == "failed" else "",
    }


def write_results(results: list[dict], manifests: list[Path]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    run_started_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    timestamp = run_started_at.replace(":", "").replace("-", "")

    payload = {
        "run_started_at": run_started_at,
        "repository_count": len(results),
        "manifests": [str(path.relative_to(REPO_ROOT)) for path in manifests],
        "results": results,
    }

    history_file = RESULTS_DIR / f"clone_results_{timestamp}.json"
    latest_file = RESULTS_DIR / "latest.json"
    legacy_file = REPO_ROOT / "third_party" / "clone_results.json"

    text = json.dumps(payload, ensure_ascii=False, indent=2)
    history_file.write_text(text, encoding="utf-8")
    latest_file.write_text(text, encoding="utf-8")

    # Compatibility path for older notes or scripts. This file is overwritten.
    legacy_file.write_text(text, encoding="utf-8")

    print(f"wrote {history_file.relative_to(REPO_ROOT)}")
    print(f"wrote {latest_file.relative_to(REPO_ROOT)}")
    print(f"wrote {legacy_file.relative_to(REPO_ROOT)}")


def main() -> None:
    results = []
    manifests = load_manifests()
    for manifest in manifests:
        config = tomllib.loads(manifest.read_text(encoding="utf-8"))
        workspace = config.get("workspace", {})
        root = REPO_ROOT / workspace.get("root", "third_party/repos")
        depth = int(workspace.get("clone_depth", 1))
        root.mkdir(parents=True, exist_ok=True)
        print(f"manifest: {manifest.relative_to(REPO_ROOT)}")
        for repo in config.get("repositories", []):
            results.append(clone_repo(repo, root, depth, manifest))

    write_results(results, manifests)


if __name__ == "__main__":
    main()
