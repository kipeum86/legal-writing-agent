#!/usr/bin/env bash
# Run after local-surface changes to re-prove the guardrail still holds.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

fail=0

# 1. No individually named local/private files in .gitignore
if grep -nE "(naming-transition|codex-quality-audit|legal-writing-agent-design|source-registry|draft\.md|change-map\.json|outline\.json)" .gitignore; then
    echo "FAIL: local/private filename detected in .gitignore"
    fail=1
else
    echo "ok: .gitignore carries no individual local/private filenames"
fi

# 2. Configured supplemental references are configured outside committed paths
if rg -n "LEGAL_AGENT_D2_SUPPLEMENTAL_REFERENCE" docs README.md CLAUDE.md .claude tools tests -g '!tools/context/budget.py' -g '!tools/security/checks/gitignore-hygiene.sh' -g '!tests/context/test_budget.py' -g '!tests/policy/test_drafting_scope_policy.py'; then
    echo "FAIL: configured supplemental reference appears in public docs"
    fail=1
else
    echo "ok: configured supplemental references stay out of public docs"
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
