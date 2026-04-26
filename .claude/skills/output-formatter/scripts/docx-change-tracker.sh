#!/usr/bin/env bash
# docx-change-tracker.sh
# Produces Level B revision artifacts for DOCX/text documents:
#   - clean copy of the revised file
#   - unified diff redline
#   - section-level change-map.json summary
#
# Usage: ./docx-change-tracker.sh <original-file> <revised-file> <output-dir> [--document-id ID] [--source-instruction TEXT]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

usage() {
  echo "Usage: $0 <original-file> <revised-file> <output-dir> [--document-id ID] [--source-instruction TEXT]"
}

if [[ $# -lt 3 ]]; then
  usage
  exit 2
fi

ORIGINAL="$1"
REVISED="$2"
OUTPUT_DIR="$3"
shift 3

if [[ ! -f "$ORIGINAL" ]]; then
  echo "Error: Original file '$ORIGINAL' not found."
  exit 1
fi

if [[ ! -f "$REVISED" ]]; then
  echo "Error: Revised file '$REVISED' not found."
  exit 1
fi

mkdir -p "$OUTPUT_DIR"
ORIGINAL="$(cd "$(dirname "$ORIGINAL")" && pwd)/$(basename "$ORIGINAL")"
REVISED="$(cd "$(dirname "$REVISED")" && pwd)/$(basename "$REVISED")"
OUTPUT_DIR="$(cd "$OUTPUT_DIR" && pwd)"

cd "$REPO_ROOT"
python3 -m tools.revision.level_b "$ORIGINAL" "$REVISED" "$OUTPUT_DIR" "$@"
