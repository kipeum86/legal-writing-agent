#!/usr/bin/env bash
# pdf-generator.sh
# Converts markdown or docx to PDF.
# Usage: ./pdf-generator.sh <input-file> <output.pdf> [--lang ko|en]
#
# Prerequisites: pandoc or LibreOffice / soffice

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  echo "Usage: $0 <input-file> <output.pdf> [--lang ko|en]"
}

if [[ $# -lt 2 ]]; then
  usage
  exit 2
fi

INPUT="$1"
OUTPUT="$2"
shift 2

LANG_VAL="ko"

find_office_bin() {
  if command -v libreoffice &> /dev/null; then
    echo "libreoffice"
    return 0
  fi
  if command -v soffice &> /dev/null; then
    echo "soffice"
    return 0
  fi
  return 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --lang)
      if [[ $# -lt 2 ]]; then
        echo "Error: --lang requires a value."
        exit 2
      fi
      LANG_VAL="$2"
      shift 2
      ;;
    --jurisdiction)
      # Accepted for compatibility with dispatcher passthrough.
      shift 2
      ;;
    *)
      echo "Error: Unsupported option '$1'."
      exit 2
      ;;
  esac
done

if [[ ! -f "$INPUT" ]]; then
  echo "Error: Input file '$INPUT' not found."
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT")"

EXT="${INPUT##*.}"

case "$EXT" in
  md|txt)
    if command -v pandoc &> /dev/null; then
      if [[ "$LANG_VAL" == "ko" ]]; then
        pandoc "$INPUT" -o "$OUTPUT" \
          -V papersize:a4 \
          -V geometry:top=20mm \
          -V geometry:bottom=15mm \
          -V geometry:left=20mm \
          -V geometry:right=20mm \
          -V "mainfont=Noto Serif CJK KR" \
          --pdf-engine=xelatex
      else
        pandoc "$INPUT" -o "$OUTPUT" -V geometry:margin=1in
      fi
      echo "PDF generated: $OUTPUT"
    elif OFFICE_BIN="$(find_office_bin 2>/dev/null)"; then
      TMP_DOCX="$(mktemp).docx"
      python3 "$SCRIPT_DIR/docx-generator.py" "$INPUT" "$TMP_DOCX" --lang "$LANG_VAL"
      "$OFFICE_BIN" --headless --convert-to pdf --outdir "$(dirname "$OUTPUT")" "$TMP_DOCX"
      GENERATED_PATH="$(dirname "$OUTPUT")/$(basename "${TMP_DOCX%.docx}.pdf")"
      if [[ "$GENERATED_PATH" != "$OUTPUT" ]]; then
        mv "$GENERATED_PATH" "$OUTPUT"
      fi
      rm -f "$TMP_DOCX"
      echo "PDF generated: $OUTPUT"
    else
      echo "Error: pandoc or LibreOffice/soffice is required for md/txt to PDF conversion."
      exit 1
    fi
    ;;
  docx)
    if OFFICE_BIN="$(find_office_bin 2>/dev/null)"; then
      OUTPUT_DIR="$(dirname "$OUTPUT")"
      "$OFFICE_BIN" --headless --convert-to pdf --outdir "$OUTPUT_DIR" "$INPUT"
      BASENAME="$(basename "${INPUT%.docx}.pdf")"
      GENERATED_PATH="$OUTPUT_DIR/$BASENAME"
      if [[ "$GENERATED_PATH" != "$OUTPUT" ]]; then
        mv "$GENERATED_PATH" "$OUTPUT"
      fi
      echo "PDF generated: $OUTPUT"
    else
      echo "Error: LibreOffice or soffice is required for docx to PDF conversion."
      echo "Install LibreOffice and ensure 'libreoffice' or 'soffice' is on PATH."
      exit 1
    fi
    ;;
  *)
    echo "Error: Unsupported input format '.$EXT'. Supported: .md, .txt, .docx"
    exit 1
    ;;
esac
