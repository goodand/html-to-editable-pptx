#!/usr/bin/env bash
# Orchestrator: extract → map → A/B validation → render → pixel per page → layout.
# LibreOffice is run sequentially; macOS headless rendering can crash from background subflows.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)"; then
  :
else
  ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi
cd "$ROOT"
H="${1:-fixtures/deck.html}"
B="$(basename "${H%.html}")"
ASSET_BASE="$(cd "$(dirname "$H")" && pwd)"
OUT_DIR="${OUT_DIR:-out}"
RUN_RENDER="${RUN_RENDER:-1}"
mkdir -p "$OUT_DIR"

# Portable LibreOffice pptx→pdf runner: container skill → PATH → macOS app bundle.
# `timeout` is absent on stock macOS, so it is applied only when available.
soffice_pdf() {
  local T=""; command -v timeout >/dev/null && T="timeout 110"
  if [ -f /mnt/skills/public/pptx/scripts/office/soffice.py ]; then
    $T python3 /mnt/skills/public/pptx/scripts/office/soffice.py --headless --convert-to pdf --outdir "$OUT_DIR" "$1" >/dev/null 2>&1
  elif command -v soffice >/dev/null; then
    $T soffice --headless --convert-to pdf --outdir "$OUT_DIR" "$1" >/dev/null 2>&1
  elif [ -x "/Applications/LibreOffice.app/Contents/MacOS/soffice" ]; then
    $T /Applications/LibreOffice.app/Contents/MacOS/soffice --headless --convert-to pdf --outdir "$OUT_DIR" "$1" >/dev/null 2>&1
  else
    echo "ERROR: LibreOffice not found. macOS: brew install --cask libreoffice" >&2; return 3
  fi
}

echo "── stage 1: extract"
python3 src/extract/weasy_extract.py "$H" "$OUT_DIR/$B.ir.json"

echo "── stage 2: map (+normalize)"
node src/map/ir_to_pptx.mjs "$OUT_DIR/$B.ir.json" "$OUT_DIR/$B.pptx" --base-dir "$ASSET_BASE"

echo "── stage 3: validation reports"
python3 src/validate/validate_ab.py "$H" "$OUT_DIR/$B.pptx" > "$OUT_DIR/$B.ab.json" 2> "$OUT_DIR/$B.ab.err" || true
echo "  validation A+B done"

if [ "$RUN_RENDER" != "0" ]; then
  echo "── stage 4: pixel diff per slide (chart regions masked)"
  python3 -c "import sys; from weasyprint import HTML; HTML(filename=sys.argv[1]).write_pdf(sys.argv[2])" "$H" "$OUT_DIR/$B.src.pdf"
  soffice_pdf "$OUT_DIR/$B.pptx"
  pdftoppm -png -scale-to-x 1280 -scale-to-y 720 "$OUT_DIR/$B.src.pdf" "$OUT_DIR/${B}_A"
  pdftoppm -png -scale-to-x 1280 -scale-to-y 720 "$OUT_DIR/$B.pdf" "$OUT_DIR/${B}_B"
  shopt -s nullglob
  SRC_PNGS=("$OUT_DIR/${B}_A-"*.png)
  if [ ${#SRC_PNGS[@]} -eq 0 ]; then
    echo "ERROR: no rendered source PNGs found under $OUT_DIR for $B" >&2
    exit 4
  fi
  for a in "${SRC_PNGS[@]}"; do
    n="${a##*-}"; n="${n%.png}"
    test -f "$OUT_DIR/${B}_B-$n.png" || { echo "ERROR: missing rendered PPTX PNG $OUT_DIR/${B}_B-$n.png" >&2; exit 4; }
    node src/validate/pixel_c.mjs "$a" "$OUT_DIR/${B}_B-$n.png" "$OUT_DIR/${B}_diff-$n.png" "$OUT_DIR/$B.masks.json" "$n" || true
  done
else
  echo "── stage 4: skipped render/pixel diff (RUN_RENDER=0)"
fi

echo "── stage 5: layout IoU (Layer D)"
python3 src/validate/layout_d.py "$OUT_DIR/$B.ir.json" "$OUT_DIR/$B.pptx" > "$OUT_DIR/$B.d.json" || true
cat "$OUT_DIR/$B.d.json"

echo "── report"
cat "$OUT_DIR/$B.ab.json"
cat "$OUT_DIR/$B.mapreport.json"
