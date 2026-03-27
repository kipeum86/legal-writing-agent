#!/usr/bin/env bash
# docx-change-tracker.sh
# Produces Level B revision artifacts for DOCX/text documents:
#   - clean copy of the revised file
#   - unified diff redline
#   - change-map.json summary
#
# Usage: ./docx-change-tracker.sh <original-file> <revised-file> <output-dir>

set -euo pipefail

usage() {
  echo "Usage: $0 <original-file> <revised-file> <output-dir>"
}

if [[ $# -lt 3 ]]; then
  usage
  exit 2
fi

ORIGINAL="$1"
REVISED="$2"
OUTPUT_DIR="$3"

if [[ ! -f "$ORIGINAL" ]]; then
  echo "Error: Original file '$ORIGINAL' not found."
  exit 1
fi

if [[ ! -f "$REVISED" ]]; then
  echo "Error: Revised file '$REVISED' not found."
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

ORIG_TEXT="$(mktemp)"
REV_TEXT="$(mktemp)"
REDLINE_PATH="$OUTPUT_DIR/redline.diff"
if [[ "$(basename "$OUTPUT_DIR")" == "documents" ]]; then
  CHANGE_MAP_PATH="$(dirname "$OUTPUT_DIR")/change-map.json"
else
  CHANGE_MAP_PATH="$OUTPUT_DIR/change-map.json"
fi
REVISED_BASENAME="$(basename "$REVISED")"
CLEAN_PATH="$OUTPUT_DIR/${REVISED_BASENAME}"

cleanup() {
  rm -f "$ORIG_TEXT" "$REV_TEXT"
}
trap cleanup EXIT

extract_text() {
  local input_file="$1"
  local output_file="$2"
  python3 - "$input_file" "$output_file" <<'PY'
import sys
from pathlib import Path

input_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])

suffix = input_path.suffix.lower()
if suffix == ".docx":
    try:
        from docx import Document
    except ImportError as exc:
        raise SystemExit(f"python-docx is required to read DOCX files: {exc}")
    doc = Document(str(input_path))
    text = "\n".join(p.text for p in doc.paragraphs)
else:
    text = input_path.read_text(encoding="utf-8")

output_path.write_text(text, encoding="utf-8")
PY
}

extract_text "$ORIGINAL" "$ORIG_TEXT"
extract_text "$REVISED" "$REV_TEXT"

diff -u "$ORIG_TEXT" "$REV_TEXT" > "$REDLINE_PATH" || true
cp "$REVISED" "$CLEAN_PATH"

python3 - "$ORIG_TEXT" "$REV_TEXT" "$REDLINE_PATH" "$CHANGE_MAP_PATH" "$ORIGINAL" "$REVISED" "$CLEAN_PATH" <<'PY'
import json
import sys
from pathlib import Path

orig_text = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
rev_text = Path(sys.argv[2]).read_text(encoding="utf-8").splitlines()
redline_path = sys.argv[3]
change_map_path = Path(sys.argv[4])
original_path = sys.argv[5]
revised_path = sys.argv[6]
clean_path = sys.argv[7]

added = 0
removed = 0
modified = 0

max_len = max(len(orig_text), len(rev_text))
for idx in range(max_len):
    left = orig_text[idx] if idx < len(orig_text) else None
    right = rev_text[idx] if idx < len(rev_text) else None
    if left is None and right is not None:
        added += 1
    elif right is None and left is not None:
        removed += 1
    elif left != right:
        modified += 1

report = {
    "status": "pass",
    "mode": "level-b-fallback",
    "nativeTrackedChanges": False,
    "originalFile": original_path,
    "revisedFile": revised_path,
    "cleanOutput": clean_path,
    "redlineOutput": redline_path,
    "summary": {
        "addedLines": added,
        "removedLines": removed,
        "modifiedLines": modified,
    },
}

change_map_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
PY

echo "Clean copy: $CLEAN_PATH"
echo "Redline diff: $REDLINE_PATH"
echo "Change map: $CHANGE_MAP_PATH"
