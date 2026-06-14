#!/usr/bin/env python3
"""Run probe-first regression fixtures from fixtures/matrix/manifest.json."""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None


def fixture_stem(input_path):
    return Path(input_path).stem


def run_cmd(cmd, env=None):
    return subprocess.run(
        cmd,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def parse_layer_c(stdout):
    out = []
    for line in stdout.splitlines():
        if "layerC_visual" not in line:
            continue
        try:
            out.append(json.loads(line)["layerC_visual"])
        except (json.JSONDecodeError, KeyError):
            pass
    return out


def add_check(checks, name, ok, detail):
    checks.append({"name": name, "pass": bool(ok), "detail": detail})


def evaluate(fx, run, out_dir):
    stem = fixture_stem(fx["input"])
    ab = load_json(out_dir / f"{stem}.ab.json")
    d = load_json(out_dir / f"{stem}.d.json")
    report = load_json(out_dir / f"{stem}.mapreport.json")
    layer_c = parse_layer_c(run.stdout)

    checks = []
    gates = fx.get("gates", {})
    render_gate = "maxLayerCDiffPct" in gates or gates.get("renderedPngs")
    if "expectedExitCode" in gates:
        add_check(checks, "exitCode", run.returncode == gates["expectedExitCode"], {
            "actual": run.returncode,
            "expected": gates["expectedExitCode"],
        })
    else:
        add_check(checks, "mustNotCrash", run.returncode == 0, f"exit={run.returncode}")

    if gates.get("layerA"):
        ok = bool(ab and ab.get("layerA_semantic", {}).get("pass") is True)
        add_check(checks, "layerA", ok, ab.get("layerA_semantic") if ab else "missing ab report")
    if gates.get("layerB"):
        ok = bool(ab and ab.get("layerB_media", {}).get("pass") is True)
        add_check(checks, "layerB", ok, ab.get("layerB_media") if ab else "missing ab report")
    if "maxLayerCDiffPct" in gates:
        max_diff = max((x.get("diffPct", 999) for x in layer_c), default=999)
        add_check(checks, "layerC", max_diff <= gates["maxLayerCDiffPct"], {"maxDiffPct": max_diff})
    if "minLayerDWorstIoU" in gates:
        worst = (d or {}).get("layerD_layout", {}).get("worstIoU", 0)
        ok = bool(d and (d.get("layerD_layout", {}).get("pass") is True) and worst >= gates["minLayerDWorstIoU"])
        add_check(checks, "layerD", ok, {"worstIoU": worst})
    if "maxFallback" in gates:
        fallback = (report or {}).get("fallback", 999)
        add_check(checks, "fallbackMax", fallback <= gates["maxFallback"], {"fallback": fallback})
    if gates.get("mustReportFallback"):
        fallback = (report or {}).get("fallback", 0)
        add_check(checks, "fallbackReported", fallback > 0, {"fallback": fallback})
    if gates.get("renderedPngs"):
        src_pngs = sorted(out_dir.glob(f"{stem}_A-*.png"))
        dst_pngs = sorted(out_dir.glob(f"{stem}_B-*.png"))
        add_check(checks, "renderedPngs", bool(src_pngs and dst_pngs), {
            "sourcePngs": len(src_pngs),
            "pptxPngs": len(dst_pngs),
        })

    failed = [c for c in checks if not c["pass"]]
    environment_blocked = bool(render_gate and run.returncode != 0)
    expected = fx["expectedBehavior"]
    if environment_blocked:
        status = "environment_blocked"
    elif failed:
        status = "unexpected_fail"
    else:
        status = expected
    return {
        "id": fx["id"],
        "category": fx["category"],
        "expectedBehavior": expected,
        "primaryGate": fx.get("primaryGate"),
        "status": status,
        "outputDir": str(out_dir),
        "runReturnCode": run.returncode,
        "renderGate": "enabled" if render_gate else "disabled",
        "checks": checks,
        "layerC": layer_c,
        "mapreport": report,
    }


def run_fixture(fx, out_root):
    out_dir = out_root / fx["id"]
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    env = os.environ.copy()
    env["OUT_DIR"] = str(out_dir)
    gates = fx.get("gates", {})
    needs_render = "maxLayerCDiffPct" in gates or gates.get("renderedPngs")
    env["RUN_RENDER"] = "1" if needs_render else "0"

    if fx.get("probeRequired"):
        probe = run_cmd([
            "python3", "scripts/probe_weasy.py", fx["input"],
            "--out", str(out_dir / "probe.json"),
            "--max-depth", "12",
        ], env=env)
        (out_dir / "probe.stdout").write_text(probe.stdout, encoding="utf-8")
        (out_dir / "probe.stderr").write_text(probe.stderr, encoding="utf-8")
        if probe.returncode != 0:
            return {
                "id": fx["id"],
                "category": fx["category"],
                "expectedBehavior": fx["expectedBehavior"],
                "primaryGate": fx.get("primaryGate"),
                "status": "unexpected_fail",
                "outputDir": str(out_dir),
                "probeOutput": str(out_dir / "probe.json"),
                "checks": [{"name": "probe", "pass": False, "detail": f"exit={probe.returncode}"}],
            }

    run = run_cmd(["bash", "scripts/run.sh", fx["input"]], env=env)
    (out_dir / "run.stdout").write_text(run.stdout, encoding="utf-8")
    (out_dir / "run.stderr").write_text(run.stderr, encoding="utf-8")
    return evaluate(fx, run, out_dir)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="fixtures/matrix/manifest.json")
    args = ap.parse_args()

    manifest = load_json(ROOT / args.manifest)
    if not manifest:
        print(f"manifest not found: {args.manifest}", file=sys.stderr)
        return 2

    out_root = ROOT / manifest.get("outRoot", "out/matrix")
    out_root.mkdir(parents=True, exist_ok=True)

    results = []
    for fx in manifest["fixtures"]:
        result = run_fixture(fx, out_root)
        results.append(result)
        marker = "PASS" if result["status"] != "unexpected_fail" else "FAIL"
        print(f"[{marker}] {fx['id']} -> {result['status']} (primary={fx.get('primaryGate')})")
        for check in result.get("checks", []):
            status = "ok" if check["pass"] else "fail"
            print(f"  {check['name']}: {status} {check['detail']}")

    summary = {
        "version": manifest.get("version"),
        "total": len(results),
        "unexpectedFail": sum(1 for r in results if r["status"] == "unexpected_fail"),
        "environmentBlocked": sum(1 for r in results if r["status"] == "environment_blocked"),
        "byStatus": {},
        "results": results,
    }
    for r in results:
        summary["byStatus"][r["status"]] = summary["byStatus"].get(r["status"], 0) + 1

    report_path = ROOT / "out" / "matrix_report.json"
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"matrix report: {report_path}")
    return 1 if summary["unexpectedFail"] or summary["environmentBlocked"] else 0


if __name__ == "__main__":
    sys.exit(main())
