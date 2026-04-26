# 표 렌더링 기준선

## 1. 구조 보존 확인

아래 표는 향후 DOCX table로 렌더링되어야 한다.

| 항목 | 현재 값 | 목표 값 |
|---|---|---|
| 표 | plain paragraph | DOCX table |
| 인용 | plain paragraph | indented blockquote |
| 목록 | plain paragraph | numbered/bulleted list |

> 이 문장은 향후 blockquote 스타일로 렌더링되어야 한다.

- 첫 번째 항목
- 두 번째 항목

1. 번호 항목
2. 번호 항목

**굵게** 및 *기울임* 표시는 현재 plain text로 남는다.
