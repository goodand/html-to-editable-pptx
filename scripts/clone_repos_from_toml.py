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

manifest = Path(sys.argv[1] if len(sys.argv) > 1 else "third_party/repositories.toml").resolve()
base = manifest.parent.parent if manifest.parent.name == "third_party" else manifest.parent
config = tomllib.loads(manifest.read_text(encoding="utf-8"))
root = base / config.get("workspace", {}).get("root", "third_party/repos")
root.mkdir(parents=True, exist_ok=True)

depth = int(config.get("workspace", {}).get("clone_depth", 1))
results = []

for repo in config.get("repositories", []):
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

    results.append({"id": repo_id, "full_name": full_name, "status": status, "commit": commit})
    print(f"[{status}] {repo_id} {commit[:12]}")

out = base / "third_party" / "clone_results.json"
out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {out}")
