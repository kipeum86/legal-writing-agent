#!/usr/bin/env bash
# pdf-generator.sh
# Converts markdown or docx to PDF.
# Usage: ./pdf-generator.sh <input-file> <output.pdf> [--lang ko|en]
#
# Prerequisites: pandoc, wkhtmltopdf (or weasyprint), or libreoffice for .docx

set -euo pipefail

INPUT="$1"
OUTPUT="$2"
LANG="${3:---lang}"
LANG_VAL="${4:-ko}"

if [[ ! -f "$INPUT" ]]; then
  echo "Error: Input file '$INPUT' not found."
  exit 1
fi

EXT="${INPUT##*.}"

case "$EXT" in
  md|txt)
    # Convert markdown/txt to PDF via pandoc
    if command -v pandoc &> /dev/null; then
      PANDOC_ARGS="-V geometry:margin=1in"
      if [[ "$LANG_VAL" == "ko" ]]; then
        PANDOC_ARGS="-V geometry:a4paper -V geometry:top=20mm -V geometry:bottom=15mm -V geometry:left=20mm -V geometry:right=20mm -V mainfont='Noto Serif CJK KR' --pdf-engine=xelatex"
      fi
      pandoc "$INPUT" -o "$OUTPUT" $PANDOC_ARGS
      echo "PDF generated: $OUTPUT"
    else
      echo "Error: pandoc is required for md/txt to PDF conversion."
      exit 1
    fi
    ;;
  docx)
    # Convert docx to PDF via LibreOffice
    if command -v libreoffice &> /dev/null; then
      OUTPUT_DIR=$(dirname "$OUTPUT")
      libreoffice --headless --convert-to pdf --outdir "$OUTPUT_DIR" "$INPUT"
      # Rename if needed
      BASENAME=$(basename "${INPUT%.docx}.pdf")
      if [[ "$OUTPUT_DIR/$BASENAME" != "$OUTPUT" ]]; then
        mv "$OUTPUT_DIR/$BASENAME" "$OUTPUT"
      fi
      echo "PDF generated: $OUTPUT"
    else
      echo "Error: LibreOffice is required for docx to PDF conversion."
      echo "Install: sudo apt install libreoffice-core (Linux) or brew install libreoffice (macOS)"
      exit 1
    fi
    ;;
  *)
    echo "Error: Unsupported input format '.$EXT'. Supported: .md, .txt, .docx"
    exit 1
    ;;
esac
