#!/usr/bin/env bash
# docx-change-tracker.sh
# Generates a redline (Level B) comparison between original and revised .docx files.
# Usage: ./docx-change-tracker.sh <original.docx> <revised.docx> <output-dir>
#
# Prerequisites: pandoc, diff
# This script converts both documents to markdown, diffs them, and generates
# a redline markdown file plus a change-map.json.

set -euo pipefail

ORIGINAL="$1"
REVISED="$2"
OUTPUT_DIR="${3:-output/documents}"

if [[ ! -f "$ORIGINAL" ]] || [[ ! -f "$REVISED" ]]; then
  echo "Error: Both original and revised files must exist."
  echo "Usage: $0 <original.docx> <revised.docx> [output-dir]"
  exit 1
fi

# Check for pandoc
if ! command -v pandoc &> /dev/null; then
  echo "Error: pandoc is required but not installed."
  exit 1
fi

TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

# Convert to markdown for diffing
pandoc "$ORIGINAL" -t markdown -o "$TEMP_DIR/original.md"
pandoc "$REVISED" -t markdown -o "$TEMP_DIR/revised.md"

# Generate unified diff
DIFF_FILE="$TEMP_DIR/changes.diff"
diff -u "$TEMP_DIR/original.md" "$TEMP_DIR/revised.md" > "$DIFF_FILE" || true

# Generate redline markdown
REDLINE_FILE="$OUTPUT_DIR/redline.md"
{
  echo "# Redline Comparison"
  echo ""
  echo "Strikethrough = deleted. **Bold** = inserted."
  echo ""
  echo "---"
  echo ""

  while IFS= read -r line; do
    case "$line" in
      -\ *)  echo "~~${line:2}~~" ;;
      +\ *)  echo "**${line:2}**" ;;
      \ *)   echo "${line:1}" ;;
    esac
  done < <(grep -E '^[-+ ]' "$DIFF_FILE" | tail -n +3)
} > "$REDLINE_FILE"

# Generate change-map.json
CHANGE_MAP="$OUTPUT_DIR/../change-map.json"
CHANGE_COUNT=$(grep -c '^[-+]' "$DIFF_FILE" 2>/dev/null || echo "0")

cat > "$CHANGE_MAP" << EOF
{
  "generatedAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "originalFile": "$ORIGINAL",
  "revisedFile": "$REVISED",
  "totalChanges": $CHANGE_COUNT,
  "redlineFile": "$REDLINE_FILE",
  "changes": []
}
EOF

echo "Redline generated: $REDLINE_FILE"
echo "Change map generated: $CHANGE_MAP"
echo "Total changes detected: $CHANGE_COUNT"
