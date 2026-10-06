#!/usr/bin/env bash
# Build THE-HUMAN-CONDITION.pdf from THE-HUMAN-CONDITION.md.
# Needs: python3 with the `markdown` module, Google Chrome, and a venv with pypdf + reportlab
# (create once:  python3 -m venv tools/pdfenv && tools/pdfenv/bin/pip install pypdf reportlab)
set -euo pipefail
cd "$(dirname "$0")/.."
TMP=$(mktemp -d)
python3 -I tools/md2html.py THE-HUMAN-CONDITION.md "$TMP/essay.html"
google-chrome --headless=new --no-sandbox --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$TMP/raw.pdf" "file://$TMP/essay.html" 2>/dev/null
tools/pdfenv/bin/python tools/stamp.py "$TMP/raw.pdf" THE-HUMAN-CONDITION.pdf
rm -rf "$TMP"
