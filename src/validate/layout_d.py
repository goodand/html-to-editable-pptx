#!/usr/bin/env python3
"""Layer D: layout tolerance — per-object IoU between IR bbox (intent) and
output OOXML xfrm geometry (result). Implements critique #13 (tolerance model)
and #14 (report actionable by source object via sourceRef).
Usage: python3 layout_d.py out/deck.ir.json out/deck.pptx
"""
import sys, json, re, zipfile
from collections import Counter

EMU_PER_PX = 9525  # 914400 EMU/inch ÷ 96 px/inch

def norm(s): return re.sub(r"\s+", " ", s).strip()

def pptx_objects(pptx_path):
    """Per-slide objects with px bboxes from slide XML. Types: text|image|frame(table/chart)."""
    z = zipfile.ZipFile(pptx_path)
    slides = sorted((n for n in z.namelist()
                     if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                    key=lambda n: int(re.search(r"\d+", n).group()))
    out = []
    for name in slides:
        x = z.read(name).decode()
        objs = []
        # shapes with text, pictures, graphic frames — capture xfrm + kind
        for m in re.finditer(
            r"<p:(sp|pic|graphicFrame)\b.*?</p:\1>", x, re.S):
            kind, body = m.group(1), m.group(0)
            off = re.search(r"<a:off x=\"(-?\d+)\" y=\"(-?\d+)\"", body)
            ext = re.search(r"<a:ext cx=\"(\d+)\" cy=\"(\d+)\"", body)
            if not (off and ext): continue
            bb = {"x": int(off.group(1)) / EMU_PER_PX, "y": int(off.group(2)) / EMU_PER_PX,
                  "w": int(ext.group(1)) / EMU_PER_PX, "h": int(ext.group(2)) / EMU_PER_PX}
            text = norm(" ".join(re.findall(r"<a:t>([^<]*)</a:t>", body)))
            objs.append({"kind": {"sp": "text", "pic": "image", "graphicFrame": "frame"}[kind],
                         "text": text, "bbox": bb})
        out.append(objs)
    return out

def iou(a, b):
    x1, y1 = max(a["x"], b["x"]), max(a["y"], b["y"])
    x2 = min(a["x"] + a["w"], b["x"] + b["w"])
    y2 = min(a["y"] + a["h"], b["y"] + b["h"])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    union = a["w"] * a["h"] + b["w"] * b["h"] - inter
    return round(inter / union, 3) if union > 0 else 0.0

def severity(v): return "ok" if v >= 0.90 else ("warn" if v >= 0.50 else "critical")

def run(ir_path, pptx_path):
    ir = json.load(open(ir_path))
    rendered = pptx_objects(pptx_path)
    report, worst = [], 1.0
    for si, sl in enumerate(ir["slides"]):
        objs = rendered[si] if si < len(rendered) else []
        frames = [o for o in objs if o["kind"] == "frame"]
        pics = [o for o in objs if o["kind"] == "image"]
        texts = {o["text"]: o for o in objs if o["kind"] == "text" and o["text"]}
        fi = 0
        for n in sl["nodes"]:
            match = None
            if n["semanticType"] == "text":
                match = texts.get(norm(n["text"]))
            elif n["semanticType"] in ("table", "chart"):
                if fi < len(frames): match = frames[fi]; fi += 1
            elif n["semanticType"] == "image":
                if pics: match = pics.pop(0)
            elif n["semanticType"] == "shape":
                # shapes carry no text; match nearest empty-text sp by IoU
                cands = [o for o in objs if o["kind"] == "text" and not o["text"]]
                match = max(cands, key=lambda o: iou(n["bbox"], o["bbox"]), default=None)
            if match is None:
                report.append({"slide": si + 1, "sourceRef": n["sourceRef"],
                               "type": n["semanticType"], "iou": 0.0, "severity": "critical",
                               "note": "no rendered counterpart"})
                worst = 0.0
                continue
            v = iou(n["bbox"], match["bbox"])
            worst = min(worst, v)
            report.append({"slide": si + 1, "sourceRef": n["sourceRef"],
                           "type": n["semanticType"], "iou": v, "severity": severity(v)})
    sev = Counter(r["severity"] for r in report)
    out = {"layerD_layout": {"pass": sev.get("critical", 0) == 0, "objects": len(report),
                             "bySeverity": dict(sev), "worstIoU": worst,
                             "detail": [r for r in report if r["severity"] != "ok"]}}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0 if out["layerD_layout"]["pass"] else 1

if __name__ == "__main__":
    sys.exit(run(sys.argv[1], sys.argv[2]))
