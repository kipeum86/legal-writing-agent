# Placeholder Format Reference

## Standard Placeholders

Canonical rule: placeholder tokens must stay stable across Korean and English workflows so downstream trackers can match them reliably. For Korean documents, only party/date convenience placeholders are localized; substantive drafting placeholders remain canonical.

Scope rule: `docs/policies/drafting-scope.md` controls when counsel placeholders must be used for missing conclusions, certainty, and risk assessment.

| Category | Korean Format | English Format |
|---|---|---|
| Party name | `[당사자명]` | `[Insert party name]` |
| Date | `[날짜]` | `[Insert date]` |
| Amount | `[금액]` | `[Insert amount]` |
| Address | `[주소]` | `[Insert address]` |
| Citation | `[Citation needed: {description}]` | `[Citation needed: {description}]` |
| Authority | `[Authority needed: {description}]` | `[Authority needed: {description}]` |
| Argument | `[Argument: {issue}]` | `[Argument: {issue}]` |
| Factual basis | `[Factual basis needed]` | `[Factual basis needed]` |
| Counsel conclusion | `[Counsel conclusion needed: {issue}]` | `[Counsel conclusion needed: {issue}]` |
| Counsel certainty | `[Counsel certainty needed: {issue}]` | `[Counsel certainty needed: {issue}]` |
| Counsel risk assessment | `[Counsel risk assessment needed: {issue}]` | `[Counsel risk assessment needed: {issue}]` |
| Convention note | `[Convention Note: {description}]` | `[Convention Note: {description}]` |
| Drafting gap | `[Drafting Gap: {issue}]` | `[Drafting Gap: {issue}]` |

## Placeholder Registry Format

```json
{
  "documentId": "uuid",
  "placeholders": [
    {
      "id": "p1",
      "type": "party_name|date|amount|citation|authority|argument|factual_basis|counsel_conclusion|counsel_certainty|counsel_risk_assessment|convention_note|drafting_gap",
      "text": "[placeholder text as it appears in document]",
      "sectionId": "s1.2",
      "description": "Additional context about what is needed",
      "resolved": false
    }
  ]
}
```

## Rules
1. **Never fabricate** — if information is missing, use a placeholder
2. **Be specific** — describe what is needed: `[Citation needed: Supreme Court case on duty of care]` not just `[Citation needed]`
3. **Track all** — every placeholder must be in the registry
4. **Skeleton-only mode** — uses substantive placeholders extensively for Conditional documents without authority packets
5. **Do not localize canonical substantive tokens** — use `[Citation needed: ...]`, `[Authority needed: ...]`, `[Argument: ...]`, `[Factual basis needed]`, `[Counsel conclusion needed: ...]`, `[Counsel certainty needed: ...]`, `[Counsel risk assessment needed: ...]`, `[Convention Note: ...]`, `[Drafting Gap: ...]` in every language
