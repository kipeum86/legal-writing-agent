#!/usr/bin/env bash
# docx-change-tracker.sh
# Compatibility wrapper that delegates Level B revision artifact generation
# to the canonical implementation in output-formatter/scripts/.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
CANONICAL_SCRIPT="$REPO_ROOT/.claude/skills/output-formatter/scripts/docx-change-tracker.sh"

if [[ ! -x "$CANONICAL_SCRIPT" ]]; then
  chmod +x "$CANONICAL_SCRIPT" 2>/dev/null || true
fi

exec "$CANONICAL_SCRIPT" "$@"
