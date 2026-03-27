# Korean Document Page Setup

## Scope
Use this file for generic Korean legal-document defaults. If the document is a Korean legal opinion, legal review opinion, or client memorandum, `docs/ko-legal-opinion-style-guide.md` may override these defaults where that guide specifies opinion-specific typography.

## A4 Standard
| Parameter | Value |
|---|---|
| Page size | A4 (210mm × 297mm) |
| Top margin | 20mm |
| Bottom margin | 15mm |
| Left margin | 20mm |
| Right margin | 20mm |
| Header distance | 15mm |
| Footer distance | 10mm |

## Typography
| Element | Font | Size | Weight |
|---|---|---|---|
| Body text | 바탕체 | 12pt | Regular |
| Heading 1 | 맑은 고딕 | 16pt | Bold |
| Heading 2 | 맑은 고딕 | 14pt | Bold |
| Heading 3 | 맑은 고딕 | 12pt | Bold |
| Caption | 바탕체 | 10pt | Regular |
| Footnote | 바탕체 | 9pt | Regular |

## Line Spacing
| Document type | Spacing |
|---|---|
| 법령/규정 style | 160% |
| 의견서/메모 | 180% |
| 소장/준비서면 | 200% (법원 제출용) |
| 각주 | 단일 줄간격 |
| 블록 인용 / 표 내부 | 130%–150% |

## Paragraph Settings
- First-line indent: 10pt (optional, per house style)
- Paragraph spacing after: 6pt
- Alignment: justified (양쪽 정렬)
- Numbered provisions should use hanging indentation so wrapped lines align under the text body rather than the number marker

## Headings and Numbering
- Main titles may be centred if the template requires a document banner
- 조·항·호·목 체계는 번호 부분과 본문 부분이 visually 분리되도록 들여쓰기를 유지
- 장·절·관 구조를 쓰는 규정류 문서는 각 단계별 heading size를 일관되게 유지

## Footnotes, Tables, and Quotations
- 각주는 9pt, 단일 줄간격
- 법령 인용 블록이나 표 내부 텍스트는 10pt 내외까지 축소 가능
- 표 테두리는 보수적으로 사용하고, 과도한 색상 강조는 피한다
- 긴 인용문은 좌우 들여쓰기로 구분하고 본문보다 약간 촘촘하게 배치

## Headers, Footers, and Pagination
- 페이지 번호는 footer 또는 house style 위치에 일관되게 배치
- 헤더/푸터는 장식보다 식별 기능을 우선
- 법원 제출 문서인 경우 사건번호, 당사자명, 문서명을 과도하지 않게 배치

## Signature Blocks
- 서명 블록 전에는 최소 18pt 이상의 여백을 둔다
- 회사/기관 문서에서는 직위 → 성명 → `(인)` 순서를 기본으로 한다
- 법원 제출 문서에서는 대리인 표기와 제출처 표기를 템플릿 구조에 맞춘다

## Override Rule
- Korean legal opinions may use opinion-specific typography from `docs/ko-legal-opinion-style-guide.md`
- House style may override margins, fonts, and header/footer presentation, but should not undermine document readability or numbering clarity
