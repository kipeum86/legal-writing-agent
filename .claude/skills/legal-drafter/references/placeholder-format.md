# Placeholder Format Reference

## Standard Placeholders

| Category | Korean Format | English Format |
|---|---|---|
| Party name | `[당사자명]` | `[Insert party name]` |
| Date | `[날짜]` | `[Insert date]` |
| Amount | `[금액]` | `[Insert amount]` |
| Address | `[주소]` | `[Insert address]` |
| Citation | `[인용 필요: {설명}]` | `[Citation needed: {description}]` |
| Authority | `[근거 법령 필요: {설명}]` | `[Authority needed: {description}]` |
| Argument | `[주장: {쟁점}]` | `[Argument: {issue}]` |
| Factual basis | `[사실관계 필요]` | `[Factual basis needed]` |
| Convention note | `[관례 참고: {설명}]` | `[Convention Note: {description}]` |
| Drafting gap | `[작성 미비: {사항}]` | `[Drafting Gap: {issue}]` |

## Placeholder Registry Format

```json
{
  "documentId": "uuid",
  "placeholders": [
    {
      "id": "p1",
      "type": "party_name|date|amount|citation|authority|argument|factual_basis|convention_note|drafting_gap",
      "text": "[placeholder text as it appears in document]",
      "section": "s1.2",
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
