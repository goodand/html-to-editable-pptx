// Layer C: visual fidelity via mapbox/pixelmatch (per third_party manifest).
// Usage: node src/validate/pixel_c.mjs out/render_src.png out/render_out.png out/diff.png
import fs from "node:fs";
import { PNG } from "pngjs";
import pixelmatch from "pixelmatch";

const [, , aPath, bPath, dPath, masksPath, pageIdx] = process.argv;
const A = PNG.sync.read(fs.readFileSync(aPath));
const B = PNG.sync.read(fs.readFileSync(bPath));
if (A.width !== B.width || A.height !== B.height) {
  console.error(`size mismatch ${A.width}x${A.height} vs ${B.width}x${B.height}`); process.exit(2);
}
// mask: zero both buffers inside chart bboxes — those regions pass via semantic Layer A′/IR
let maskedPx = 0;
if (masksPath && fs.existsSync(masksPath)) {
  const rects = (JSON.parse(fs.readFileSync(masksPath, "utf8"))[+pageIdx - 1] || []);
  for (const r of rects) {
    const x0 = Math.max(0, r.x | 0), y0 = Math.max(0, r.y | 0);
    const x1 = Math.min(A.width, Math.ceil(r.x + r.w)), y1 = Math.min(A.height, Math.ceil(r.y + r.h));
    for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) {
      const i = (y * A.width + x) * 4;
      A.data[i] = A.data[i+1] = A.data[i+2] = B.data[i] = B.data[i+1] = B.data[i+2] = 0;
      A.data[i+3] = B.data[i+3] = 255; maskedPx++;
    }
  }
}
const diff = new PNG({ width: A.width, height: A.height });
const bad = pixelmatch(A.data, B.data, diff.data, A.width, A.height, { threshold: 0.1 });
fs.writeFileSync(dPath, PNG.sync.write(diff));
const denom = A.width * A.height - maskedPx;
const pct = +(100 * bad / denom).toFixed(2);
console.log(JSON.stringify({ layerC_visual: { mismatchedPx: bad, comparedPx: denom, maskedPx, diffPct: pct, diffImage: dPath } }));
