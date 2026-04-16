#!/usr/bin/env bash
# Run after every security-hardening commit to re-prove the leak is closed.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

fail=0

# 1. No individually-named sensitive files in .gitignore
if grep -nE "(ko-legal-opinion|naming-transition|codex-quality-audit|legal-writing-agent-design|source-registry|draft\.md|change-map\.json|outline\.json)" .gitignore; then
    echo "FAIL: sensitive filename detected in .gitignore"
    fail=1
else
    echo "ok: .gitignore carries no individual sensitive filenames"
fi

# 2. Old style-guide path is gone
if rg -n "docs/ko-legal-opinion-style-guide\.md" -g '!docs/plans/*' -g '!docs/_private/*' -g '!tools/security/checks/gitignore-hygiene.sh'; then
    echo "FAIL: legacy style-guide path still referenced"
    fail=1
else
    echo "ok: no residual references to docs/ko-legal-opinion-style-guide.md"
fi

# 3. Required trust-boundary markers are present
for doc in CLAUDE.md \
           docs/security/trust-boundaries.md \
           .claude/skills/ingest/SKILL.md \
           .claude/skills/request-interpreter/SKILL.md \
           .claude/skills/document-reviser/SKILL.md \
           .claude/skills/convention-selector/SKILL.md; do
    if ! grep -q "<untrusted_content" "$doc"; then
        echo "FAIL: $doc missing <untrusted_content marker"
        fail=1
    fi
done
[ $fail -eq 0 ] && echo "ok: all required trust-boundary markers present"

exit $fail
