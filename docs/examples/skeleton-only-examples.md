# Skeleton-Only Output Examples

이 문서는 `docs/policies/drafting-scope.md`에 따른 skeleton-only 출력 예시다. 아래 예시는 권위자료, 변호사 결론, 확신도, 리스크 평가가 부족한 경우에도 문서 구조는 제공하되 실체 법률판단은 생성하지 않는 방식을 고정한다.

---

## Example 1: Advisory Memo Without Authority Packet

**입력 요지:** "개인정보 이전 관련 법률의견서 초안 작성. 사실관계는 별도 제공 예정."

```markdown
# MEMORANDUM

To: [Recipient]
From: [Author / Team]
Date: [Insert date]
Re: 개인정보 이전 관련 검토

## 1. Questions Presented

1. [Argument: 개인정보 이전 구조와 적용 법령을 특정할 쟁점]

## 2. Short Answer / Executive Summary

1. [Counsel conclusion needed: 개인정보 이전의 적법성에 관한 결론]
   [Counsel certainty needed: 개인정보 이전의 적법성에 관한 확신도]

## 3. Facts, Assumptions, and Scope

- Confirmed facts: [Facts needed: 이전 주체, 수령자, 정보 항목, 이전 목적]
- Assumptions: [Assumption: facts to be confirmed]
- Scope limits: 본 초안은 authority packet 및 counsel conclusion 제공 전 skeleton draft입니다.

## 4. Governing Authorities

- [Authority needed: governing statute or leading case]
- [Citation needed: source for proposition]

## 5. Analysis

### A. 개인정보 이전 요건

1. Governing Rule: [Authority needed: 개인정보 이전 요건]
2. Application to Facts: [Argument: confirmed facts needed before application]
3. Counterarguments / Risks / Uncertainties: [Counsel risk assessment needed: 개인정보 이전 관련 주요 리스크]
4. Issue Conclusion: [Counsel conclusion needed: 개인정보 이전 요건 충족 여부]

## 6. Overall Conclusion and Recommendations

[Counsel conclusion needed: overall conclusion]
[Counsel risk assessment needed: recommended risk-mitigation steps]

## 7. Qualifications and Limitations

- 본 문서는 미검토 AI skeleton draft이며 법률 자문이 아닙니다.
- 권위자료, 사실관계, counsel conclusion이 제공되면 본문을 보완해야 합니다.
```

---

## Example 2: Conditional Corporate Bylaws Draft

**입력 요지:** "스타트업 정관 초안 만들어줘. 회사 정보는 아직 미정."

```markdown
# 정관 초안

> 본 문서는 회사 형태, 주식 구조, 기관 설계, 기존 정관, 적용 법령 검토가 제공되기 전의 template-only draft입니다.

## 제1장 총칙

### 제1조(상호)

회사의 상호는 [Company name needed]로 한다.

### 제2조(목적)

회사의 목적은 다음 각 호와 같다.

1. [Business purpose needed]
2. [Business purpose needed]

## 제2장 주식

### 제3조(발행예정주식의 총수)

회사가 발행할 주식의 총수는 [Number needed]주로 한다.

### 제4조(1주의 금액)

회사가 발행하는 주식 1주의 금액은 [Amount needed]원으로 한다.

## 제3장 기관

### 제5조(기관 설계)

[Counsel conclusion needed: 이사회, 감사, 감사위원회 등 기관 설계의 적정성]
[Authority needed: 회사 형태와 규모에 따른 필수 기관 요건]

## 제4장 부칙

### 제6조(시행일)

본 정관은 [Effective date needed]부터 시행한다.

## Drafting Notes

- 정관 조항의 적법성, 필수 기재사항, 기관 설계, 주식 관련 제한은 독립 판단하지 않는다.
- 필요한 자료: 회사 형태, 발행주식 구조, 임원/기관 설계, 투자계약상 정관 반영사항, counsel-provided mandatory clauses.
- 누락된 법률 판단은 `[Counsel conclusion needed: {issue}]` 또는 `[Authority needed: {issue}]`로 남긴다.
```
