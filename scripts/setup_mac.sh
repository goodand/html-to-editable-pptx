#!/usr/bin/env bash
# macOS setup for html-to-editable-pptx parser. Requires Homebrew (https://brew.sh).
set -e
command -v brew >/dev/null || { echo "Homebrew required: https://brew.sh"; exit 1; }

echo "── system deps (poppler: pdftoppm | pango: WeasyPrint backend | LibreOffice: pptx render)"
brew list poppler >/dev/null 2>&1 || brew install poppler
brew list pango   >/dev/null 2>&1 || brew install pango
brew list --cask libreoffice >/dev/null 2>&1 || brew install --cask libreoffice

echo "── python deps"
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip weasyprint

echo "── node deps (uses package-lock.json)"
npm ci

echo
echo "Optional (Korean text fidelity in renders):"
echo "  brew install --cask font-noto-sans-cjk"
echo
echo "Setup done. Smoke test:"
echo "  npm test"
echo "Expect: layerA pass / layerB pass / layerC diffPct<5 per slide / layerD pass worstIoU>0.9"
