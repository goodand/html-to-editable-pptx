// Runtime validator for IR JSON (enforces schema.ts invariants I1–I9).
export const IR_VERSION = "1.2.0";
const TYPES = new Set(["text", "shape", "table", "image", "chart", "group", "fallbackRegion"]);

export function validateIR(doc) {
  const errs = [];
  const req = (cond, msg) => { if (!cond) errs.push(msg); };

  req(doc.irVersion === IR_VERSION, `irVersion must be ${IR_VERSION}`);
  req(doc.pagePx && doc.pagePx.w > 0 && doc.pagePx.h > 0, "pagePx required");
  req(Array.isArray(doc.slides) && doc.slides.length > 0, "slides[] required (I7)");

  const walk = (n, path) => {
    req(typeof n.sourceRef === "string" && n.sourceRef.length > 0, `${path}: sourceRef (I1)`);
    req(n.bbox && [n.bbox.x, n.bbox.y, n.bbox.w, n.bbox.h].every(Number.isFinite), `${path}: bbox (I2)`);
    req(Number.isInteger(n.zIndex), `${path}: zIndex (I3)`);
    req(TYPES.has(n.semanticType), `${path}: semanticType (I4)`);
    if (n.semanticType === "text")  req(typeof n.text === "string", `${path}: text.text`);
    if (n.semanticType === "image") req(n.src && n.md5, `${path}: image src+md5`);
    if (n.semanticType === "table") {
      req(Array.isArray(n.rows) && n.rows.length > 0, `${path}: table.rows (I5)`);
      req(Array.isArray(n.colWidthsPx) && n.colWidthsPx.every((w) => w > 0), `${path}: colWidthsPx>0`);
      n.rows.flat().forEach((c, ci) => {
        if (c.colspan != null) req(c.colspan >= 2, `${path}.cell[${ci}]: colspan>=2 (I8)`);
        if (c.rowspan != null) req(c.rowspan >= 2, `${path}.cell[${ci}]: rowspan>=2 (I8)`);
      });
    }
    if (n.semanticType === "chart") {
      req(n.chartType === "bar", `${path}: chartType closed set (I9)`);
      req(Array.isArray(n.categories) && n.categories.length > 0, `${path}: chart.categories`);
      req(Array.isArray(n.series) && n.series.every((s) => Array.isArray(s.values) && s.values.length === n.categories.length),
          `${path}: series values must align with categories`);
      req(["attr", "svg-marks"].includes(n.dataSource), `${path}: dataSource provenance (I9)`);
    }
    if (n.semanticType === "fallbackRegion") req(typeof n.reason === "string", `${path}: fallback.reason (I6)`);
    if (n.semanticType === "group") (n.children || []).forEach((c, i) => walk(c, `${path}.children[${i}]`));
  };

  (doc.slides || []).forEach((sl, si) => {
    req(Array.isArray(sl.nodes), `slides[${si}].nodes[] required`);
    (sl.nodes || []).forEach((n, i) => walk(n, `slides[${si}].nodes[${i}]`));
    const sorted = (sl.nodes || []).every((n, i, a) => i === 0 || a[i - 1].zIndex <= n.zIndex);
    req(sorted, `slides[${si}]: nodes must be paint-ordered by zIndex (I3/I7)`);
  });
  return errs;
}
