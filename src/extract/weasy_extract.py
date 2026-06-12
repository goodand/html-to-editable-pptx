#!/usr/bin/env python3
"""HTML -> Visual Object IR (JSON) via WeasyPrint box tree. Rule-based only.
Ideas ported from dom-to-pptx (PX_TO_INCH, render-item typing, paint-order z).
Usage: python3 weasy_extract.py fixtures/slide13.html out/slide13.ir.json
"""
import sys, json, hashlib, os, re
from html.parser import HTMLParser
from weasyprint import HTML

IR_VERSION = "1.2.0"

def parse_svg_charts(raw):
    """Document-order chart specs from inline <svg> blocks. Rule-based two-tier:
    tier1 'attr': data-categories/data-values JSON attributes (repo policy: source first);
    tier2 'svg-marks': bar rects + numeric axis ticks -> linear scale (ChartDetective idea,
    simplified to deterministic rules). Returns list of dict|{'error':reason}."""
    import xml.etree.ElementTree as ET
    out = []
    for block in re.findall(r"<svg\b.*?</svg>", raw, re.S):
        try:
            el = ET.fromstring(re.sub(r'\sxmlns(:\w+)?="[^"]*"', "", block))
        except ET.ParseError as e:
            out.append({"error": f"svg parse: {e}"}); continue
        # ── tier 1: source data attributes
        if el.get("data-categories") and el.get("data-values"):
            try:
                out.append({"dataSource": "attr", "chartType": el.get("data-chart", "bar"),
                            "categories": json.loads(el.get("data-categories")),
                            "series": [{"name": el.get("data-name", "Series 1"),
                                        "values": json.loads(el.get("data-values")),
                                        "color": el.get("data-color")}]})
                continue
            except Exception as e:
                out.append({"error": f"attr tier: {e}"}); continue
        # ── tier 2: reverse-engineer marks
        rects = [r for r in el.iter() if r.tag == "rect" and "bar" in (r.get("class") or "")]
        if not rects:
            rects = [r for r in el.iter() if r.tag == "rect"]
        texts = [(float(t.get("x", 0)), float(t.get("y", 0)), "".join(t.itertext()).strip())
                 for t in el.iter() if t.tag == "text"]
        if len(rects) < 2:
            out.append({"error": "svg-marks: <2 bar rects"}); continue
        rects.sort(key=lambda r: float(r.get("x", 0)))
        bar_xs = [float(r.get("x", 0)) for r in rects]
        # numeric ticks left of first bar -> linear value scale from y positions
        ticks = sorted([(y, float(txt.replace(",", ""))) for x, y, txt in texts
                        if x < bar_xs[0] and re.fullmatch(r"-?[\d,.]+", txt)], key=lambda t: t[0])
        def y_to_val(y):
            if len(ticks) >= 2:
                (y1, v1), (y2, v2) = ticks[0], ticks[-1]
                if y2 != y1: return round(v1 + (v2 - v1) * (y - y1) / (y2 - y1), 2)
            return None
        values = []
        for r in rects:
            top = float(r.get("y", 0))
            v = y_to_val(top)
            values.append(v if v is not None else round(float(r.get("height", 0)), 2))
        # category labels: texts below bars, matched to nearest bar center by x
        below = [(x, txt) for x, y, txt in texts
                 if y > max(float(r.get("y", 0)) + float(r.get("height", 0)) for r in rects) - 1]
        cats = []
        for r in rects:
            cx = float(r.get("x", 0)) + float(r.get("width", 0)) / 2
            cats.append(min(below, key=lambda b: abs(b[0] - cx))[1] if below else f"#{len(cats)+1}")
        color = (rects[0].get("fill") or "").lstrip("#") or None
        out.append({"dataSource": "svg-marks", "chartType": "bar", "categories": cats,
                    "series": [{"name": "Series 1", "values": values, "color": color}]})
    return out

class ImgSrcGrab(HTMLParser):
    """Collect <img src> in document order (RasterImage exposes no URL — lesson #7)."""
    def __init__(self):
        super().__init__(); self.srcs = []
    def handle_starttag(self, tag, attrs):
        if tag == "img":
            d = dict(attrs)
            if d.get("src"): self.srcs.append(d["src"])

def intersect(b, clip):
    """Clip bbox b against clip rect (dom-to-pptx isClippedByParent idea, geometric form)."""
    if clip is None: return b
    x1, y1 = max(b["x"], clip["x"]), max(b["y"], clip["y"])
    x2 = min(b["x"] + b["w"], clip["x"] + clip["w"])
    y2 = min(b["y"] + b["h"], clip["y"] + clip["h"])
    if x2 <= x1 or y2 <= y1: return None
    return {"x": round(x1, 1), "y": round(y1, 1), "w": round(x2 - x1, 1), "h": round(y2 - y1, 1)}

def hexc(rgba):
    if rgba is None: return None
    r, g, b, a = rgba
    if a == 0: return None
    return "%02X%02X%02X" % (round(r*255), round(g*255), round(b*255))

def style_of(box, text_box=None):
    s = (text_box or box).style
    st = {}
    fs = s["font_size"]
    if fs: st["fontSizePx"] = round(fs, 1)
    fam = s["font_family"]
    if fam: st["fontFamily"] = fam[0] if isinstance(fam, (list, tuple)) else str(fam)
    fw = s["font_weight"]
    if fw: st["fontWeight"] = int(fw)
    c = hexc(s["color"])
    if c: st["color"] = c
    try:
        ta = s["text_align_all"]
        if ta in ("left", "center", "right"): st["align"] = ta
    except Exception:
        pass
    bg = hexc(s["background_color"])
    if bg: st["fillColor"] = bg
    bw = s["border_top_width"]
    if bw and bw > 0:
        st["borderWidthPx"] = round(bw, 1)
        bc = hexc(s["border_top_color"])
        if bc: st["borderColor"] = bc
    try:
        br = s["border_top_left_radius"]
        rv = br[0][0] if isinstance(br, (list, tuple)) and isinstance(br[0], (list, tuple)) else \
             (br[0] if isinstance(br, (list, tuple)) else br)
        if rv and float(rv) > 0: st["borderRadiusPx"] = round(float(rv), 1)
    except Exception:
        pass
    return st

def bbox_of(box):
    return {"x": round(box.border_box_x(), 1), "y": round(box.border_box_y(), 1),
            "w": round(box.border_width(), 1), "h": round(box.border_height(), 1)}

def texts_under(box):
    out = []
    if type(box).__name__ == "TextBox":
        out.append(box)
    for c in getattr(box, "children", []):
        out.extend(texts_under(c))
    return out

def extract(html_path, out_path):
    base = os.path.dirname(os.path.abspath(html_path))
    raw = open(html_path, encoding="utf-8").read()
    grab = ImgSrcGrab(); grab.feed(raw)
    img_srcs = list(grab.srcs)            # consumed in encounter order
    charts = parse_svg_charts(raw)        # consumed in encounter order (L3)
    doc = HTML(filename=html_path).render()
    page_w, page_h = doc.pages[0].width, doc.pages[0].height
    slides = []

    def do_page(page):
        nodes, z = [], [0]
        background = [None]

        def emit(node, op, clip):
            bb = intersect(node["bbox"], clip)
            if bb is None:
                print(f"  clip-drop {node['sourceRef']}"); return
            node["bbox"] = bb
            if op < 1: node["style"]["opacity"] = round(op, 3)
            node["irVersion"] = IR_VERSION
            node["zIndex"] = z[0]; z[0] += 1
            nodes.append(node)

        def cell_text(cell):
            return " ".join(t.text for t in texts_under(cell)).strip()

        def rows_under(b):
            out = []
            if type(b).__name__ == "TableRowBox": out.append(b)
            for c in getattr(b, "children", []): out.extend(rows_under(c))
            return out

        def cells_of(row):
            return [c for c in row.children if type(c).__name__ == "TableCellBox"]

        def handle_table(box, ref, op, clip):
            rrows = rows_under(box)
            # 1. column count from grid_x + colspan (WeasyPrint cell attrs)
            ncols = 0
            for row in rrows:
                for c in cells_of(row):
                    ncols = max(ncols, (getattr(c, "grid_x", 0) or 0) + (getattr(c, "colspan", 1) or 1))
            # 2. widths from colspan==1 cells at their grid_x
            colw = [0.0] * ncols
            for row in rrows:
                for c in cells_of(row):
                    if (getattr(c, "colspan", 1) or 1) == 1:
                        gx = getattr(c, "grid_x", 0) or 0
                        colw[gx] = max(colw[gx], round(c.border_width(), 1))
            # 3. never-single columns: split merged width (dom-to-pptx extractTableData idea)
            for row in rrows:
                for c in cells_of(row):
                    csp = getattr(c, "colspan", 1) or 1
                    if csp > 1:
                        gx = getattr(c, "grid_x", 0) or 0
                        missing = [i for i in range(gx, gx + csp) if colw[i] == 0]
                        if missing:
                            known = sum(colw[i] for i in range(gx, gx + csp))
                            share = max((round(c.border_width(), 1) - known) / len(missing), 1.0)
                            for i in missing: colw[i] = round(share, 1)
            rows, row_h = [], []
            for row in rrows:
                row_h.append(round(row.border_height(), 1))
                r = []
                for c in cells_of(row):
                    tb = texts_under(c)
                    cs = style_of(c, tb[0] if tb else None)
                    if c.element_tag == "th": cs["fontWeight"] = max(cs.get("fontWeight", 400), 700)
                    cell = {"text": cell_text(c), "style": cs}
                    csp = getattr(c, "colspan", 1) or 1
                    rsp = getattr(c, "rowspan", 1) or 1
                    if csp > 1: cell["colspan"] = csp      # I8
                    if rsp > 1: cell["rowspan"] = rsp      # I8
                    r.append(cell)
                rows.append(r)
            emit({"sourceRef": ref, "semanticType": "table", "bbox": bbox_of(box),
                  "style": style_of(box), "rows": rows,
                  "colWidthsPx": [round(w, 1) for w in colw], "rowHeightsPx": row_h}, op, clip)

        def handle_image(box, ref, op, clip):
            rel = img_srcs.pop(0) if img_srcs else "logo.png"
            src = os.path.join(base, rel)
            md5 = hashlib.md5(open(src, "rb").read()).hexdigest()
            emit({"sourceRef": ref, "semanticType": "image", "bbox": bbox_of(box),
                  "style": style_of(box), "src": src, "md5": md5}, op, clip)

        def is_text_para(box):
            return box.element_tag in ("p", "h1", "h2", "h3", "span", "li") and texts_under(box)

        def handle_text(box, ref, op, clip):
            tbs = texts_under(box)
            txt = " ".join(t.text for t in tbs).strip()
            if not txt: return
            first = tbs[0]
            emit({"sourceRef": ref, "semanticType": "text",
                  "bbox": {"x": round(first.position_x, 1), "y": round(first.position_y, 1),
                           "w": round(box.border_width(), 1), "h": round(box.border_height(), 1)},
                  "style": style_of(box, first), "text": txt}, op, clip)

        def has_visual(box):
            s = box.style
            return hexc(s["background_color"]) or (s["border_top_width"] or 0) > 0

        def get(s, key, default=None):
            try: return s[key]
            except Exception: return default

        def walk(box, path, op, clip):
            box = getattr(box, "_box", box)            # unwrap AbsolutePlaceholder (lesson #1)
            cls = type(box).__name__
            tag = getattr(box, "element_tag", None) or cls
            ref = f"{path}>{tag}"
            s = getattr(box, "style", None)
            if s is not None:
                # opacity product — dom-to-pptx index.js: currentOpacity *= elOpacity
                o = get(s, "opacity")
                if o is not None:
                    op = op * float(o)
                    if op == 0: return                 # dom-to-pptx: skip fully hidden
                # full-page background absorber (body OR section covering the page)
                bg = hexc(get(s, "background_color"))
                if bg and background[0] is None and hasattr(box, "border_width"):
                    if box.border_width() >= 0.95 * page_w and box.border_height() >= 0.95 * page_h:
                        background[0] = bg
                        for c in getattr(box, "children", []): walk(c, ref, op, clip)
                        return
            if cls == "TableBox":
                handle_table(box, ref, op, clip); return
            if tag.endswith("svg"):                      # namespaced: {http://...}svg
                spec = charts.pop(0) if charts else {"error": "no parsed svg left"}
                if "error" in spec:
                    emit({"sourceRef": ref, "semanticType": "fallbackRegion",
                          "bbox": bbox_of(box), "style": style_of(box),
                          "reason": f"chart unrecoverable: {spec['error']}"}, op, clip)   # I6
                else:
                    emit({"sourceRef": ref, "semanticType": "chart", "bbox": bbox_of(box),
                          "style": style_of(box), **spec}, op, clip)
                return
            if tag == "img":
                handle_image(box, ref, op, clip); return
            if is_text_para(box):
                handle_text(box, ref, op, clip); return
            if cls.startswith("Block") and tag not in ("html", "body", "section") \
               and has_visual(box) and not texts_under(box):
                st = style_of(box)
                emit({"sourceRef": ref, "semanticType": "shape", "bbox": bbox_of(box),
                      "style": st, "shape": "roundRect" if st.get("borderRadiusPx") else "rect"}, op, clip)
                # fallthrough intentional: clipped children of a visual box still walk below
            # clip stack — overflow:hidden intersects descendants (dom-to-pptx isClippedByParent)
            if s is not None and get(s, "overflow") == "hidden":
                clip = intersect(bbox_of(box), clip) or {"x": 0, "y": 0, "w": 0, "h": 0}
            for c in getattr(box, "children", []):
                walk(c, ref, op, clip)

        walk(page._page_box, "page", 1.0, None)
        return {"background": background[0], "nodes": nodes}

    for pi, page in enumerate(doc.pages):
        sl = do_page(page)
        if sl["nodes"] or sl["background"]:
            slides.append(sl)

    ir = {"irVersion": IR_VERSION, "pagePx": {"w": page_w, "h": page_h}, "slides": slides}
    json.dump(ir, open(out_path, "w"), ensure_ascii=False, indent=1)
    # masks: chart regions are validated semantically, not pixel-wise (renderer-diff expected)
    masks = [[n["bbox"] for n in sl["nodes"] if n["semanticType"] == "chart"] for sl in slides]
    json.dump(masks, open(out_path.replace(".ir.json", ".masks.json"), "w"))
    for si, sl in enumerate(slides):
        types = {}
        for n in sl["nodes"]: types[n["semanticType"]] = types.get(n["semanticType"], 0) + 1
        print(f"slide {si+1}: bg={sl['background']} nodes={len(sl['nodes'])} {types}")
    print(f"IR written: {out_path} | page {page_w}x{page_h} | slides={len(slides)}")

if __name__ == "__main__":
    extract(sys.argv[1], sys.argv[2])
