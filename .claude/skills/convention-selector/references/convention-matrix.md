# Convention Selection Matrix

## Quick Reference

| Document Language | Jurisdiction | Style Guide | Numbering | Page Size | Citation | Date Format |
|---|---|---|---|---|---|---|
| Korean | Korea (한국법) | style-guide-kr | 조·항·호·목 | A4 | 「법률명」 / 대법원 판결 | YYYY년 MM월 DD일 |
| Korean | International | style-guide-kr (adapted) | Adapted Korean conventions | A4 | Korean format | YYYY년 MM월 DD일 |
| English | US | style-guide-en-us | Art/Sec/(a)/(i) | US Letter | Bluebook | Month DD, YYYY |
| English | UK | style-guide-en-uk | Clause/1.1/(a) | A4 | OSCOLA | DD Month YYYY |
| English | International | style-guide-en-intl | Art/Sec/Para/(a) | A4 | Neutral | DD Month YYYY |
| Bilingual (KR+EN) | Cross-border | Both referenced | Primary language's numbering | Primary language's page size | Both as needed | Primary language's date format |

**Mandatory supplement for Korean legal opinions**:
- If the document is a Korean legal opinion, legal review opinion, or client memorandum, load `style-profiles/ko-korea-advisory.md` and load `docs/_private/ko-legal-opinion-style-guide.md` when it exists locally
- The opinion-specific guide controls where it conflicts with the compact Korean advisory profile

## Selection Algorithm

```
1. Determine target language (from D1 parameters)
2. Determine jurisdiction (from D1 parameters)
3. Look up style guide from matrix
4. Load the compact `style-profiles/{language}-{jurisdiction}-{documentType}.md` profile when present; fallback to the smallest base style guide only if no profile exists
5. Load matching template from /library/templates/ when present; otherwise use built-in references/template-{doc-type}-{language}.md
6. Apply house style overlay (if loaded at D1)
7. Load docs/_private/ko-legal-opinion-style-guide.md when the document is a Korean legal opinion family document and the file exists locally
8. Return complete convention set
```

## House Style Override Rules
House style takes precedence over base style guide for:
- Heading formatting (font, size, weight, numbering)
- Page margins and layout
- Signature block format
- Header/footer content
- Logo placement

House style does NOT override:
- Legal citation format (jurisdiction-bound)
- Register/formality level (language-bound)
- Substantive structure (document-type-bound)
- Mandatory Korean legal opinion rules from `docs/_private/ko-legal-opinion-style-guide.md`
