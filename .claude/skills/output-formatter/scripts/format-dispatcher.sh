#!/usr/bin/env bash
# format-dispatcher.sh
# Routes document generation to the appropriate format-specific script.
# Usage: ./format-dispatcher.sh <input.md> <output-format> [options]
#
# Supported formats: docx, pdf, md, txt

set -euo pipefail

INPUT="$1"
FORMAT="$2"
shift 2
OPTIONS="$*"

if [[ ! -f "$INPUT" ]]; then
  echo "Error: Input file '$INPUT' not found."
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASENAME="${INPUT%.*}"
OUTPUT="${BASENAME}.${FORMAT}"

case "$FORMAT" in
  md)
    # Markdown: just copy
    cp "$INPUT" "$OUTPUT"
    echo "Output: $OUTPUT"
    ;;
  txt)
    # Plain text: strip markdown formatting
    if command -v pandoc &> /dev/null; then
      pandoc "$INPUT" -t plain -o "$OUTPUT"
    else
      # Fallback: simple sed-based strip
      sed 's/^#\+\s*//' "$INPUT" | sed 's/\*\*//g' | sed 's/\*//g' > "$OUTPUT"
    fi
    echo "Output: $OUTPUT"
    ;;
  docx)
    "$SCRIPT_DIR/docx-generator.js" "$INPUT" "$OUTPUT" $OPTIONS
    ;;
  pdf)
    "$SCRIPT_DIR/pdf-generator.sh" "$INPUT" "$OUTPUT" $OPTIONS
    ;;
  *)
    echo "Error: Unsupported format '$FORMAT'. Supported: docx, pdf, md, txt"
    exit 1
    ;;
esac
