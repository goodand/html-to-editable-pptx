#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    print("Python 3.11+ is required.", file=sys.stderr)
    raise

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "third_party" / "repositories.toml"
MANIFEST_DIR = REPO_ROOT / "third_party" / "manifests"


def load_manifests() -> list[Path]:
    if len(sys.argv) > 1:
        return [Path(p).resolve() for p in sys.argv[1:]]
    manifests = [DEFAULT_MANIFEST]
    if MANIFEST_DIR.exists():
        manifests.extend(sorted(MANIFEST_DIR.glob("*.toml")))
    return [p for p in manifests if p.exists()]


def clone_repo(repo: dict, root: Path, depth: int) -> dict:
    repo_id = repo["id"]
    full_name = repo["full_name"]
    dest = root / repo_id
    url = f"https://github.com/{full_name}.git"

    if (dest / ".git").exists():
        status = "already_cloned"
    else:
        if dest.exists():
            shutil.rmtree(dest)
        cmd = ["git", "clone", "--depth", str(depth), "--single-branch", "--filter=blob:none", url, str(dest)]
        proc = subprocess.run(cmd, text=True, capture_output=True)
        if proc.returncode != 0:
            if dest.exists():
                shutil.rmtree(dest, ignore_errors=True)
            cmd = ["git", "clone", "--depth", str(depth), "--single-branch", url, str(dest)]
            proc = subprocess.run(cmd, text=True, capture_output=True)
        status = "cloned" if proc.returncode == 0 else "failed"

    commit = ""
    if (dest / ".git").exists():
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=dest, text=True).strip()

    print(f"[{status}] {repo_id} {commit[:12]}")
    return {"id": repo_id, "full_name": full_name, "status": status, "commit": commit}


def main() -> None:
    results = []
    for manifest in load_manifests():
        config = tomllib.loads(manifest.read_text(encoding="utf-8"))
        workspace = config.get("workspace", {})
        root = REPO_ROOT / workspace.get("root", "third_party/repos")
        depth = int(workspace.get("clone_depth", 1))
        root.mkdir(parents=True, exist_ok=True)
        print(f"manifest: {manifest.relative_to(REPO_ROOT)}")
        for repo in config.get("repositories", []):
            results.append(clone_repo(repo, root, depth))

    out = REPO_ROOT / "third_party" / "clone_results.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
