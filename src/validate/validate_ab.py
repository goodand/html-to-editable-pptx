#!/usr/bin/env python3
"""Layer A: semantic preservation (bag-of-lines, reused from the diff parser).
Layer B: media integrity (MD5 content hashing, reused from the diff parser).
Usage: python3 validate_ab.py fixtures/slide13.html out/slide13.pptx
"""
import sys, re, hashlib, zipfile, os, json, html as html_lib
from collections import Counter
from html.parser import HTMLParser

def norm(s):  # identical normalization to compare_content.py
    return re.sub(r"\s+", " ", s).strip()

class TextGrab(HTMLParser):
    def __init__(self):
        super().__init__(); self.lines, self.skip = [], 0
    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"): self.skip += 1
    def handle_endtag(self, tag):
        if tag in ("style", "script"): self.skip -= 1
    def handle_data(self, d):
        if not self.skip and d.strip(): self.lines.append(norm(d))

def html_lines(path):
    g = TextGrab(); g.feed(open(path, encoding="utf-8").read())
    return Counter(g.lines)

def html_slide_lines(path):
    """Per-slide Counters. Slides delimited by <section ...class=...slide...>; fallback: whole doc.
    <svg> blocks removed — chart content is validated semantically (IR), not as text lines."""
    raw = open(path, encoding="utf-8").read()
    raw = re.sub(r"<svg\b.*?</svg>", "", raw, flags=re.S)
    chunks = re.split(r"<section[^>]*class=[\"'][^\"']*slide[^\"']*[\"'][^>]*>", raw)
    bodies = chunks[1:] if len(chunks) > 1 else [raw]
    out = []
    for b in bodies:
        g = TextGrab(); g.feed(b.split("</section>")[0])
        out.append(Counter(g.lines))
    return out

def pptx_slide_lines(path):
    """Per-slide Counters from PPTX OOXML text runs; no external CLI dependency."""
    z = zipfile.ZipFile(path)
    names = sorted((n for n in z.namelist()
                    if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                   key=lambda n: int(re.search(r"\d+", n).group()))
    slides = []
    for name in names:
        xml = z.read(name).decode("utf-8", "ignore")
        cur = Counter()
        for raw in re.findall(r"<a:t>(.*?)</a:t>", xml, re.S):
            line = norm(html_lib.unescape(raw))
            if line: cur[line] += 1
        slides.append(cur)
    return slides

def jaccard(a, b):
    """Token-set Jaccard |A∩B|/|A∪B| — reused from the diff parser's provenance engine."""
    ta = set(t for line in a for t in line.split())
    tb = set(t for line in b for t in line.split())
    return round(len(ta & tb) / len(ta | tb), 3) if (ta | tb) else 1.0

def layer_a(html_path, pptx_path):
    src_slides = html_slide_lines(html_path)
    dst_slides = pptx_slide_lines(pptx_path)
    per = []
    ok = len(src_slides) == len(dst_slides)
    for i in range(max(len(src_slides), len(dst_slides))):
        src = src_slides[i] if i < len(src_slides) else Counter()
        dst = dst_slides[i] if i < len(dst_slides) else Counter()
        missing = src - dst          # content LOST
        extra = dst - src            # content INVENTED
        if missing: ok = False
        per.append({"slide": i + 1, "sourceLines": sum(src.values()),
                    "missing": sorted(missing), "extra": sorted(extra),
                    "jaccard": jaccard(src, dst)})
    return {"pass": ok, "slides": {"html": len(src_slides), "pptx": len(dst_slides)}, "perSlide": per}

def layer_b(html_dir, pptx_path):
    src_hashes = {}
    for f in os.listdir(html_dir):
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            src_hashes[hashlib.md5(open(os.path.join(html_dir, f), "rb").read()).hexdigest()] = f
    z = zipfile.ZipFile(pptx_path)
    out_hashes = {hashlib.md5(z.read(n)).hexdigest(): n
                  for n in z.namelist() if n.startswith("ppt/media/")}
    missing = {h: f for h, f in src_hashes.items() if h not in out_hashes}
    return {"pass": not missing, "sourceAssets": len(src_hashes),
            "matched": len(src_hashes) - len(missing), "missing": list(missing.values())}

if __name__ == "__main__":
    html_path, pptx_path = sys.argv[1], sys.argv[2]
    rep = {"layerA_semantic": layer_a(html_path, pptx_path),
           "layerB_media": layer_b(os.path.dirname(os.path.abspath(html_path)), pptx_path)}
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    sys.exit(0 if rep["layerA_semantic"]["pass"] and rep["layerB_media"]["pass"] else 1)
