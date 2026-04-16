# Convention Selector

> Selects the correct legal-writing convention set based on language, jurisdiction, and document type, then applies house style overlay.

## Trigger
- **Drafting Pipeline**: Step D2 (convention selection)
- **Revision Pipeline**: Step R3 (convention verification)

## Required References
- `references/convention-matrix.md` — canonical language/jurisdiction routing matrix
- `references/style-guide-kr.md` — generic Korean legal-writing conventions
- `references/style-guide-en-us.md` — US legal-writing conventions
- `references/style-guide-en-uk.md` — UK legal-writing conventions
- `references/style-guide-en-intl.md` — international English conventions
- `docs/_private/ko-legal-opinion-style-guide.md` — mandatory supplement for Korean legal opinions, legal review opinions, and client memoranda

## Responsibilities

### 1. Convention Set Selection (D2)
Given the parameters from D1, select the complete convention set:

**Step 1 — Base Style Guide**: Language + Jurisdiction → style guide

| Language | Jurisdiction | Style Guide |
|---|---|---|
| Korean | Korea (한국법) | `style-guide-kr` |
| Korean | International | `style-guide-kr` (adapted) |
| English | US | `style-guide-en-us` |
| English | UK | `style-guide-en-uk` |
| English | International | `style-guide-en-intl` |
| Bilingual | Cross-border | Both referenced; primary language's conventions lead |

**Step 2 — Document Template**: Document type + Language → custom override from `/library/templates/` when available; otherwise load built-in template `references/template-{doc-type}-{language}.md`

**Step 3 — House Style Overlay**: If house style loaded at D1, overlay on base style guide. House style takes precedence for formatting (headings, numbering, fonts, margins, signature blocks).

**Step 4 — Mandatory Supplemental Guide**: If the document is a Korean legal opinion / legal review opinion / client memorandum, you MUST load and apply `docs/_private/ko-legal-opinion-style-guide.md`. Where that guide conflicts with generic Korean defaults, the opinion-specific guide controls for structure, numbering, citation, confidence language, and typography.

### 2. Convention Verification (R3)
For revision pipeline, verify the existing document against the applicable convention set:
1. Identify the convention set that should apply
2. Check the original document for convention compliance, including any mandatory supplemental guide
3. If issues found, default behavior is to fix them alongside the requested changes
4. If the convention corrections would be extensive, briefly inform the user what was corrected; only present options when the difference is material to revision scope
5. If options are presented, default if no response: option (1) fix alongside requested changes

### 3. Convention Application Rules

#### Korean (style-guide-kr)
- **Register**: 문어체. Endings: ~한다, ~하여야 한다, ~할 수 있다 (formal); ~합니다 체 permitted for advisory/memo
- **Numbering**: 제1조, 제2조... → 제N항 → 제N호 → 목 (가, 나, 다...)
- **Citation**: 「법률명」 제N조 제N항. 판례: 대법원 YYYY. MM. DD. 선고 YYYY다NNNNN 판결
- **Page**: A4. Margins: 상 20mm, 하 15mm, 좌 20mm, 우 20mm. 바탕체 (body), 맑은 고딕 (headings). 12pt
- **한자 병기**: Optional on first use: 채권(債權), 물권(物權)
- **Date**: YYYY년 MM월 DD일
- **Signature**: Company → Title → Name → (인)
- **Korean legal opinions**: For 법률의견서/법률검토의견/클라이언트 메모, apply `docs/_private/ko-legal-opinion-style-guide.md` as a mandatory supplement

#### English US (style-guide-en-us)
- **Register**: Formal. "Must" for obligations; "may" for permissions. No contractions.
- **Numbering**: Article → Section → (a)(b)(c) → (i)(ii)(iii)
- **Citation**: Bluebook. Statutes: Title, Code, Section. Cases: Party v. Party, Vol Reporter Page (Court Year).
- **Page**: US Letter. 1″ margins. Times New Roman. 12pt.
- **Date**: Month DD, YYYY.

#### English UK (style-guide-en-uk)
- "Clause" not "Section"; A4; OSCOLA citation; DD Month YYYY

#### English International (style-guide-en-intl)
- Neutral register; UNCITRAL/ICC patterns; A4; no jurisdiction-specific idioms

### 4. Bilingual Term Handling
| Situation | Rule |
|---|---|
| Korean doc + English concept | English in parentheses on first use: "적법절차(due process)의 원칙에 따라..." |
| English doc + Korean concept | Romanized + original: "the Gab/Eul (갑/을) party designation..." |
| User instructs in different language than target | Infer target language from context; confirm only if genuinely ambiguous |

## Output
Convention set record for use by downstream skills:
- Selected base style guide
- Mandatory supplemental guides loaded (if any)
- House style overlay (if any)
- Matched template path (custom or built-in)
- Page setup parameters
- Numbering system
- Citation format
- Register requirements
