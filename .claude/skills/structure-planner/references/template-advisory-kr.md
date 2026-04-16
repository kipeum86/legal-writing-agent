# Template: Advisory (의견서) — Korean

## Use This Template For
- 법률의견서
- 법률검토의견
- 클라이언트 메모
- 내부 메모
- 실사보고서의 법률분석 파트

## Support Profile
- Support level: `Conditional`
- Authority packet required for substantive legal analysis
- If the authority packet is missing, preserve the structure below and fill substantive analysis sections with canonical placeholders such as `[Authority needed: applicable statute or precedent]`, `[Argument: issue to be analyzed]`, and `[Factual basis needed]`
- For Korean legal opinions, `docs/_private/ko-legal-opinion-style-guide.md` controls where it is more specific than this template

## Section Tags
- `[B]` = Boilerplate or administrative content that can usually be drafted without external authority
- `[S]` = Substantive document content that depends on user facts or instructions
- `[AP]` = Authority packet required before the section can be fully completed

## Core Skeleton — Legal Opinion / Legal Review Opinion

1. `MEMORANDUM` or `법률의견서` heading `[B]`
   - Center the document type at the top
   - Use the exact product label requested by the user: `법률의견서`, `법률검토의견`, `클라이언트 메모`, `내부 메모`

2. 정보 블록 `[B]`
   - 수신: `[수신인 / 의뢰인]`
   - 참조: `[참조인]` if applicable
   - 발신: `[작성 주체 / Jinju Legal Orchestrator]`
   - 일자: `[날짜]`
   - 제목: `[검토 제목]`

3. `1. 검토의 배경 및 질의의 요지` `[S]`
   - 사건 또는 거래의 배경 사실을 시간순 또는 논점순으로 정리
   - 의뢰인이 요청한 질의를 번호를 매겨 특정
   - 사실관계가 불완전하면 해당 문단에 `[Factual basis needed]`를 삽입

4. `2. 결론 요약` `[S]`
   - 각 질의별 결론을 먼저 간명하게 제시
   - 확정적 결론이 어려우면 조건부 결론과 리스크를 함께 적시
   - 한국어 의견서 관행상 `~로 판단됩니다`, `~로 사료됩니다` 등의 표현을 사용

5. `3. 검토의 전제 및 범위` `[B/S]`
   - 전제 사실, 미확인 사실, 검토 제외 범위를 명시
   - 필요한 경우 의견의 효력 범위와 작성 목적을 제한
   - 외부 자료 미확인 상태라면 그 한계를 명시

6. `4. 관련 법령 및 판례` `[AP]`
   - 검토에 직접 필요한 법령, 판례, 행정해석만 선별
   - 처음 인용할 때는 완전 인용 형식을 사용
   - 자료가 없으면 `[Citation needed: governing statute or leading authority]`

7. `5. 검토의견` `[S/AP]`
   - 질의별로 동일한 하위 구조를 반복
   - 권장 구조:
     - `가. 쟁점 1` `[S]`
     - `(1) 관련 법령 및 법리` `[AP]`
     - `(2) 사실관계에의 적용` `[S/AP]`
     - `(3) 반대 해석 또는 리스크` `[AP]`
     - `(4) 소결` `[S]`
   - 쟁점이 2개 이상이면 `나.`, `다.` 순으로 확장
   - 한국어 의견서에서는 쟁점명 자체가 결론의 방향을 드러내도록 작성

8. `6. 종합 결론 및 권고사항` `[S]`
   - 검토의견 전체를 다시 묶어 최종 결론을 제시
   - 실무상 권고, 추가 확인 필요 사항, 후속 조치가 있으면 별도 문장으로 분리

9. `7. 면책 및 한계` `[B]`
   - 제공된 사실과 자료를 전제로 한 의견임을 명시
   - 사실 변경, 추가 자료 확인, 법령 변경 가능성에 따른 한계를 적시
   - 필요 시 수신인 제한 또는 제3자 의존 제한 문구를 추가

10. `8. 종결 문구 및 서명 블록` `[B]`
    - 한국 대형 로펌 관행상 `이상입니다.` 또는 `끝.`을 사용 가능
    - 서명 블록 예시:
      - `Jinju Legal Orchestrator`
      - `담당 스페셜리스트 [성명]`
      - `[직인 또는 서명]`

11. `9. 별첨` `[B/S]`
    - 별첨 1. 관련 법령 발췌
    - 별첨 2. 판례 요약
    - 별첨 3. 검토 전제자료 목록

## Variant Adjustments

### Client Memorandum / Internal Memo
- 정보 블록을 `To / From / Date / Re` 또는 `수신 / 발신 / 일자 / 제목` 중심의 간결한 메모 형식으로 축약할 수 있다
- `결론 요약` 뒤에 `실무적 시사점` 또는 `즉시 조치 필요사항` 항목을 추가하는 것이 유용하다
- 대외 배포용이 아니면 서명 블록은 간단한 작성자 표기로 충분하다

### Due Diligence Report
- `검토의 배경 및 질의의 요지`를 `검토 범위`와 `검토 대상 자료`로 나눈다
- `검토의견` 대신 아래 구조를 권장한다:
  - `가. 핵심 발견사항`
  - `나. 위험도 평가`
  - `다. 추가 확인 필요사항`
  - `라. 권고 조치`
- 위험도 평가는 `High / Medium / Low` 또는 사용자 지정 등급을 사용한다

## Boilerplate vs Substantive Guidance
- Boilerplate에 해당하는 부분: 문서 유형 표시, 정보 블록, 면책 문구, 서명 블록, 별첨 제목
- Substantive에 해당하는 부분: 질의 정리, 결론 요약, 관련 법령 및 판례, 쟁점별 분석, 권고사항
- Conditional support 문서이므로 `관련 법령 및 판례`, `검토의견`은 authority packet 없이 완결적으로 쓰지 않는다

## Drafting Reminders
- 질의가 여러 개면 `질의 1 → 결론 1 → 분석 1`의 대응 관계가 문서 전반에서 유지되어야 한다
- 한국어 의견서에서는 결론 선제시가 가능하지만, 결론을 뒷받침하는 법적 근거가 반드시 뒤따라야 한다
- 법령 블록과 판례 인용은 `docs/_private/ko-legal-opinion-style-guide.md`의 형식을 우선 적용한다
