#!/usr/bin/env bash
# Orchestrator: extract → map → [subflow A+B ∥ subflow C-prep] → pixel per page → merge.
# Subflows run as parallel OS processes (independent validation paths).
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

# Portable LibreOffice pptx→pdf runner: container skill → PATH → macOS app bundle.
# `timeout` is absent on stock macOS, so it is applied only when available.
soffice_pdf() {
  local T=""; command -v timeout >/dev/null && T="timeout 110"
  if [ -f /mnt/skills/public/pptx/scripts/office/soffice.py ]; then
    $T python3 /mnt/skills/public/pptx/scripts/office/soffice.py --headless --convert-to pdf --outdir out "$1" >/dev/null 2>&1
  elif command -v soffice >/dev/null; then
    $T soffice --headless --convert-to pdf --outdir out "$1" >/dev/null 2>&1
  elif [ -x "/Applications/LibreOffice.app/Contents/MacOS/soffice" ]; then
    $T /Applications/LibreOffice.app/Contents/MacOS/soffice --headless --convert-to pdf --outdir out "$1" >/dev/null 2>&1
  else
    echo "ERROR: LibreOffice not found. macOS: brew install --cask libreoffice" >&2; return 3
  fi
}

echo "── stage 1: extract"
python3 src/extract/weasy_extract.py "$H" "out/$B.ir.json"

echo "── stage 2: map (+normalize)"
node src/map/ir_to_pptx.mjs "out/$B.ir.json" "out/$B.pptx"

echo "── stage 3: parallel validation subflows"
( python3 src/validate/validate_ab.py "$H" "out/$B.pptx" > "out/$B.ab.json" 2> "out/$B.ab.err" || true ) &
P_AB=$!
( python3 -c "from weasyprint import HTML; HTML(filename='$H').write_pdf('out/$B.src.pdf')" \
  && soffice_pdf "out/$B.pptx" \
  && pdftoppm -png -scale-to-x 1280 -scale-to-y 720 "out/$B.src.pdf" "out/${B}_A" \
  && pdftoppm -png -scale-to-x 1280 -scale-to-y 720 "out/$B.pdf" "out/${B}_B" ) &
P_C=$!
wait $P_AB; wait $P_C
echo "  subflow A+B done; subflow C renders done"

echo "── stage 4: pixel diff per slide (chart regions masked)"
for a in out/${B}_A-*.png; do
  n="${a##*-}"; n="${n%.png}"
  node src/validate/pixel_c.mjs "$a" "out/${B}_B-$n.png" "out/${B}_diff-$n.png" "out/$B.masks.json" "$n" || true
done

echo "── stage 5: layout IoU (Layer D)"
python3 src/validate/layout_d.py "out/$B.ir.json" "out/$B.pptx" > "out/$B.d.json" || true
cat "out/$B.d.json"

echo "── report"
cat "out/$B.ab.json"
cat "out/$B.mapreport.json"
