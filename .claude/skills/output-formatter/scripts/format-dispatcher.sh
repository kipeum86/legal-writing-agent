#!/usr/bin/env bash
# format-dispatcher.sh
# Routes document generation to the appropriate format-specific script.
# Usage: ./format-dispatcher.sh <input.md> <output-format> [--output path] [options]
#
# Supported formats: docx, pdf, md, txt

set -euo pipefail

usage() {
  echo "Usage: $0 <input-file> <output-format> [--output path] [options]"
}

if [[ $# -lt 2 ]]; then
  usage
  exit 2
fi

INPUT="$1"
FORMAT="$2"
shift 2

if [[ ! -f "$INPUT" ]]; then
  echo "Error: Input file '$INPUT' not found."
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
OUTPUT_DIR="$(PYTHONPATH="$REPO_ROOT" python3 -c 'from tools.security.paths import documents_dir; print(documents_dir())')"
mkdir -p "$OUTPUT_DIR"

OUTPUT=""
PASSTHRU=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output)
      if [[ $# -lt 2 ]]; then
        echo "Error: --output requires a path argument."
        exit 2
      fi
      OUTPUT="$2"
      shift 2
      ;;
    *)
      PASSTHRU+=("$1")
      shift
      ;;
  esac
done

if [[ -z "$OUTPUT" ]]; then
  INPUT_NAME="$(basename "${INPUT%.*}")"
  OUTPUT="$OUTPUT_DIR/${INPUT_NAME}.${FORMAT}"
fi

mkdir -p "$(dirname "$OUTPUT")"

case "$FORMAT" in
  md)
    if [[ "$INPUT" != "$OUTPUT" ]]; then
      cp "$INPUT" "$OUTPUT"
    fi
    echo "Output: $OUTPUT"
    ;;
  txt)
    if command -v pandoc &> /dev/null; then
      pandoc "$INPUT" -t plain -o "$OUTPUT"
    else
      sed 's/^#\+\s*//' "$INPUT" | sed 's/\*\*//g' | sed 's/\*//g' > "$OUTPUT"
    fi
    echo "Output: $OUTPUT"
    ;;
  docx)
    python3 "$SCRIPT_DIR/docx-generator.py" "$INPUT" "$OUTPUT" "${PASSTHRU[@]}"
    ;;
  pdf)
    bash "$SCRIPT_DIR/pdf-generator.sh" "$INPUT" "$OUTPUT" "${PASSTHRU[@]}"
    ;;
  *)
    echo "Error: Unsupported format '$FORMAT'. Supported: docx, pdf, md, txt"
    exit 1
    ;;
esac
