# Convention Selection Matrix

## Quick Reference

| Document Language | Jurisdiction | Style Guide | Numbering | Page Size | Citation | Date Format |
|---|---|---|---|---|---|---|
| Korean | Korea | style-guide-kr | 조·항·호·목 | A4 | 「법률명」 / 대법원 판결 | YYYY년 MM월 DD일 |
| Korean | International | style-guide-kr (adapted) | Adapted Korean | A4 | Korean format | YYYY년 MM월 DD일 |
| English | US | style-guide-en-us | Art/Sec/(a)/(i) | US Letter | Bluebook | Month DD, YYYY |
| English | UK | style-guide-en-uk | Clause/1.1/(a) | A4 | OSCOLA | DD Month YYYY |
| English | International | style-guide-en-intl | Art/Sec/Para/(a) | A4 | Neutral | DD Month YYYY |
| Bilingual | Cross-border | Both | Primary lang's | Primary lang's | Both | Primary lang's |

## Selection Algorithm

```
1. Determine target language (from D1 parameters)
2. Determine jurisdiction (from D1 parameters)
3. Look up style guide from matrix
4. Load matching template from /library/templates/
5. Apply house style overlay (if loaded at D1)
6. Return complete convention set
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
