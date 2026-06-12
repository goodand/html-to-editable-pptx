// IR JSON -> editable .pptx via PptxGenJS.
// Ported from dom-to-pptx: PX_TO_INCH=1/96, render-item type dispatch, paint-order z.
// Usage: node src/map/ir_to_pptx.mjs out/slide13.ir.json out/slide13.pptx
import fs from "node:fs";
import PptxGenJS from "pptxgenjs";
import JSZip from "jszip";
import { DOMParser, XMLSerializer } from "@xmldom/xmldom";
// normalizer (either source) expects browser DOMParser/XMLSerializer; polyfill for Node
globalThis.DOMParser ??= DOMParser;
globalThis.XMLSerializer ??= XMLSerializer;
import { validateIR } from "../ir/validate.js";
import { createRequire } from "node:module";
import path from "node:path";

// ── normalizer resolution per D-2-1 (2026-06-12 final) ──────────────────────
// Default : runtime import of npm `dom-to-pptx` (optionalDependency).
// Fallback: src/output/normalize-zip.js — transplanted copy (MIT attribution).
// Triggers: package absent · normalizePptxZip not exported (true for v1.1.10,
//           which exposes only exportToPptx — verified 2026-06-12) · load
//           error · pptxgenjs version conflict materialized in OUR tree.
const _require = createRequire(import.meta.url);
function pkgJsonOf(spec) {
  let dir = path.dirname(_require.resolve(spec));
  for (let i = 0; i < 6; i++) {
    try { return _require(path.join(dir, "package.json")); }
    catch { dir = path.dirname(dir); }
  }
  throw new Error(`package.json not found for ${spec}`);
}
async function resolveNormalizer() {
  try {
    const ours = pkgJsonOf("pptxgenjs");
    const major = String(ours.version || "").split(".")[0];
    if (major !== "4")
      throw new Error(`pptxgenjs resolved to ${ours.version} (expected 4.x) — conflict materialized`);
    const mod = await import("dom-to-pptx");
    if (typeof mod.normalizePptxZip !== "function")
      throw new Error("dom-to-pptx loaded but does not export normalizePptxZip");
    return { fn: mod.normalizePptxZip, source: "runtime-import" };
  } catch (e) {
    const fb = await import("../output/normalize-zip.js");
    return { fn: fb.normalizePptxZip, source: "transplant-fallback", note: String(e?.message || e) };
  }
}
const { fn: normalizePptxZip, source: normalizerSource, note: normalizerNote } = await resolveNormalizer();
if (normalizerSource === "transplant-fallback")
  console.warn(`[normalizer] fallback active — ${normalizerNote}`);

const PX_TO_INCH = 1 / 96;          // dom-to-pptx src/index.js:36
const PX_TO_PT = 72 / 96;           // CSS px -> typographic pt
const inch = (px) => +(px * PX_TO_INCH).toFixed(3);
const pt = (px) => +(px * PX_TO_PT).toFixed(1);

const [, , irPath, outPath] = process.argv;
const ir = JSON.parse(fs.readFileSync(irPath, "utf8"));

const errs = validateIR(ir);
if (errs.length) { console.error("IR INVALID:\n" + errs.join("\n")); process.exit(1); }

const pptx = new PptxGenJS();
pptx.defineLayout({ name: "PX", width: inch(ir.pagePx.w), height: inch(ir.pagePx.h) });
pptx.layout = "PX";

const stats = { native: 0, fallback: 0, byType: {} };
const count = (t, ok) => { stats.byType[t] = (stats.byType[t] || 0) + 1; ok ? stats.native++ : stats.fallback++; };

const geo = (n) => ({ x: inch(n.bbox.x), y: inch(n.bbox.y), w: inch(n.bbox.w), h: inch(n.bbox.h) });
const transp = (s) => (s.opacity != null ? Math.round((1 - s.opacity) * 100) : undefined);

for (const sl of ir.slides) {
const slide = pptx.addSlide();
if (sl.background) slide.background = { color: sl.background };

for (const n of [...sl.nodes].sort((a, b) => a.zIndex - b.zIndex)) {
  const s = n.style || {};
  if (n.semanticType === "text") {
    slide.addText(n.text, { ...geo(n),
      fontFace: s.fontFamily, fontSize: pt(s.fontSizePx || 16), color: s.color || "000000",
      bold: (s.fontWeight || 400) >= 700, italic: !!s.italic, align: s.align || "left",
      valign: "top", margin: 0, transparency: transp(s) });
    count("text", true);
  } else if (n.semanticType === "shape") {
    slide.addShape(n.shape === "roundRect" ? "roundRect" : "rect", { ...geo(n),
      fill: s.fillColor ? { color: s.fillColor, transparency: transp(s) } : { type: "none" },
      line: s.borderColor ? { color: s.borderColor, width: pt(s.borderWidthPx || 1) } : { type: "none" },
      rectRadius: s.borderRadiusPx ? inch(s.borderRadiusPx) : 0 });
    count("shape", true);
  } else if (n.semanticType === "image") {
    slide.addImage({ path: n.src, ...geo(n) });
    count("image", true);
  } else if (n.semanticType === "table") {
    const NONE = { type: "none" };
    const rows = n.rows.map((r, ri) => r.map((c) => {
      const cs = c.style || {};
      const botPx = cs.borderWidthPx || 0;
      return { text: c.text, options: {
        color: cs.color || "000000", fontSize: pt(cs.fontSizePx || 15),
        bold: (cs.fontWeight || 400) >= 700, align: cs.align || "left",
        fontFace: cs.fontFamily, valign: "middle", margin: 0.04,
        fill: cs.fillColor ? { color: cs.fillColor } : { type: "none" },
        border: [NONE, NONE, botPx ? { pt: pt(botPx), color: cs.borderColor || "000000" } : NONE, NONE],
        ...(c.colspan ? { colspan: c.colspan } : {}),     // I8 — dom-to-pptx pass-through
        ...(c.rowspan ? { rowspan: c.rowspan } : {}),     // I8
      } };
    }));
    slide.addTable(rows, { x: inch(n.bbox.x), y: inch(n.bbox.y), w: inch(n.bbox.w), h: inch(n.bbox.h),
      colW: n.colWidthsPx.map(inch),
      rowH: (n.rowHeightsPx || []).map(inch),
      border: NONE, autoPage: false });
    count("table", true);
  } else if (n.semanticType === "chart") {
    const axisColor = "788CA0";
    slide.addChart(pptx.ChartType.bar, n.series.map((sr) => ({
      name: sr.name, labels: n.categories, values: sr.values,
    })), { ...geo(n), barDir: "col",
      chartColors: n.series.map((sr) => sr.color || "4ECCA3"),
      catAxisLabelColor: axisColor, valAxisLabelColor: axisColor,
      catAxisLineColor: axisColor, valAxisLineColor: axisColor,
      dataLabelColor: "E8E8E8", showLegend: false,
      valGridLine: { color: "2A3B5C", size: 0.5 } });
    count("chart", true);
  } else {
    slide.addImage({ path: n.src || "", ...geo(n) });   // fallbackRegion (logged)
    console.warn(`FALLBACK ${n.sourceRef}: ${n.reason || "unmapped"}`);
    count(n.semanticType, false);
  }
}
}

await pptx.writeFile({ fileName: outPath });

// strip dangling [Content_Types].xml Overrides (normalize-zip.js)
// (PowerPoint refuses files advertising parts that don't exist in the package)
const zip = await JSZip.loadAsync(fs.readFileSync(outPath));
await normalizePptxZip(zip);
fs.writeFileSync(outPath, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
const total = stats.native + stats.fallback;
const report = { out: outPath, nodes: total, editabilityScore: +(stats.native / total).toFixed(3), normalizer: normalizerSource, ...(normalizerNote ? { normalizerNote } : {}), ...stats };
fs.writeFileSync(outPath.replace(/\.pptx$/, ".mapreport.json"), JSON.stringify(report, null, 1));
console.log(JSON.stringify(report));
