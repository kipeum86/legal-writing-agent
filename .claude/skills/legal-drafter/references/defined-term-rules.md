# Defined Term Management Rules

## 1. Definition Protocol

### Korean
- Pattern: `[전체명칭](이하 "[약칭]"이라 한다)`
- Example: `주식회사 대한테크(이하 "갑"이라 한다)`
- Example: `「자본시장과 금융투자업에 관한 법률」(이하 "자본시장법"이라 한다)`

### English
- Pattern: `[Full Name] (the "[Defined Term]")` or `[Full Name] ("[Abbreviation]")`
- Example: `XYZ Corporation (the "Company")`
- Example: `the Securities Exchange Act of 1934, as amended (the "Exchange Act")`

## 2. Consistency Rules

1. **One concept = one term**: Never use multiple terms for the same concept
2. **One term = one concept**: Never reuse a defined term for a different concept
3. **Exact form**: Once defined, use the exact defined form. Do not vary for style.
   - ✓ "갑은 을에게 통지하여야 한다" (consistent)
   - ✗ "갑은 주식회사 대한테크에게 통지하여야 한다" (inconsistent — use defined term)
4. **Capitalization (English)**: Capitalize defined terms consistently
   - ✓ "the Company shall notify the Director"
   - ✗ "the company shall notify the director" (if defined as "Company" and "Director")

## 3. Term Registry Format

```json
{
  "documentId": "uuid",
  "terms": [
    {
      "definedTerm": "갑",
      "fullForm": "주식회사 대한테크",
      "language": "ko",
      "firstUsedInSection": "s1",
      "definitionText": "주식회사 대한테크(이하 \"갑\"이라 한다)"
    },
    {
      "definedTerm": "the Company",
      "fullForm": "XYZ Corporation",
      "language": "en",
      "firstUsedInSection": "s1",
      "definitionText": "XYZ Corporation (the \"Company\")"
    }
  ]
}
```

## 4. Cross-Document Consistency
When creating related documents in one session:
- Reuse defined terms with the same form
- Do not redefine unless the definition changes
- Inherit from prior document's term registry
