# 이중언어 법률문서 작성 에이전트

🌐 **언어**: [English](../../README.md) | 한국어

클로드 코드(Claude Code) 에이전트로, 한국어와 영어로 **비계약 법률문서**를 초안 작성 및 수정하며, 각 법역에 맞는 법률문서 작성 규범을 적용합니다.

## 더 좋은 결과를 위한 핵심: Library 활용

이 에이전트는 `/library/`를 적극적으로 채워둘수록 결과가 더 좋아집니다. `/library/`의 자료는 이 프로젝트 폴더 안에 로컬로 저장되므로, 팀이 쓰는 템플릿과 예시 문서를 계속 축적해둘 수 있습니다.

- `/library/precedents/`에 잘 쓴 샘플 문서를 넣으면 문체, 구조, 디테일 수준, 자주 쓰는 표현을 더 잘 따라갑니다
- `/library/templates/`에 문서 골격을 넣으면 문서 유형별 섹션 흐름을 더 안정적으로 잡습니다
- `/library/house-styles/`에 내부 스타일 규칙을 넣으면 조직 고유의 형식과 톤을 반영하기 쉽습니다

특히 작업하려는 문서와 유사한 샘플 라이팅을 잘 넣어둘수록 결과물이 눈에 띄게 좋아집니다. 팀이 실제로 쓰는 문체와 결과를 맞추고 싶다면, 가장 효과적인 방법은 Library에 좋은 예시 문서를 넣어두고 그 로컬 Library를 팀 기준에 맞게 계속 관리하는 것입니다.

## 주요 기능

- **초안 작성**: 사용자 지시사항에 따른 새 법률문서 작성 (D1~D6 파이프라인)
- **수정**: 기존 법률문서의 변경 추적을 포함한 수정 (R1~R7 파이프라인)
- **이중 규범 적용**: 한국어 문서는 한국 법률문서 작성 규범(쟁점→결론→분석, 「법률명」 인용), 영어 문서는 미국/영국/국제 규범(IRAC/CRAC, Bluebook/OSCOLA) 적용
- **파일 형식**: `.docx`, `.pdf`, `.md`, `.txt` 읽기 및 쓰기

## 지원하지 않는 기능

- 계약서 초안 작성 또는 검토
- 법률 자문, 위험 평가, 전략 권고
- 법률 조사(법령, 판례, 규정 검색)
- 문서 검토 또는 정확성 감사
- 인용 조작 — `[Citation needed]` 자리 표시자 사용

## 지원 문서 유형

| # | 분류 | 지원 수준 | 예시 |
|---|---|:---:|---|
| 1 | **의견서/메모** (Advisory) | 조건부 | 법률의견서, legal memo, due diligence report |
| 2 | **기업문서** (Corporate) | 전면 | 이사회 결의서, 정관, board resolution, articles |
| 3 | **소송문서** (Litigation) | 조건부 | 소장, 답변서, 준비서면, complaint, brief |
| 4 | **규제문서** (Regulatory) | 조건부 | 인허가 신청서, compliance report |
| 5 | **기타 법률문서** (General Legal) | 전면 | 컴플라이언스 가이드라인, policy document |

- **전면 지원**: 지시사항만으로 완전한 초안 작성 가능
- **조건부 지원**: 근거자료 패킷(법령, 판례 인용, 사실관계 등) 필요. 제공되지 않을 경우 자리 표시자를 포함한 골격 초안 작성

## 빠른 시작

### 사전 요구사항

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 설치
- Python 3.10+ 및 `python-docx` 패키지:
  ```bash
  pip install python-docx
  ```

### 사용 방법

1. 터미널에서 이 프로젝트 폴더 열기
2. `claude` 실행 — `CLAUDE.md`가 자동으로 로드됨
3. 더 좋은 결과를 위해 먼저 `/library/`에 템플릿, 스타일 규칙, 샘플 문서를 넣기
4. 지시사항 입력:

**초안 작성:**
```
이사회 결의서 작성해줘. 의안은 대표이사 선임의 건이야.
```
```
Draft a legal memorandum analyzing whether the non-compete clause is enforceable under California law.
```

**수정:**
`/input/` 폴더에 문서를 넣은 후:
```
input 폴더에 있는 답변서 수정해줘. 피고 주장 부분 보강해야 해.
```
```
Revise the brief in /input/. Strengthen the argument in Section III.
```

## 프로젝트 구조

```
/
├── CLAUDE.md                          # 에이전트 오케스트레이터
├── /input/                            # 수정할 문서를 여기에 배치
├── /output/
│   ├── /documents/                    # 생성된 문서 (자동 버전 관리)
│   ├── /manifests/                    # 문서 파라미터 (JSON)
│   ├── /clause-maps/                  # 섹션 추적 (JSON)
│   ├── /placeholders/                 # 자리 표시자 레지스트리 (JSON)
│   └── /term-registries/             # 정의 용어 추적 (JSON)
├── /library/                          # 재사용 가능한 자산 (사용자 관리)
│   ├── /house-styles/                 # 기관별 서식 규칙
│   ├── /templates/                    # 문서 구조 골격
│   └── /precedents/                   # 참조 문서
├── /docs/
│   ├── formatting-conventions-reference.md    # 서식 규범 참조 (영어)
│   └── /ko/
│       ├── README.md                          # 메인 README (한국어)
│       └── formatting-conventions-reference.md  # 서식 규범 참조 (한국어)
└── /.claude/skills/                   # 에이전트 스킬 및 참조자료
    ├── /request-interpreter/          # D1/R1: 요청 해석, 분류
    ├── /convention-selector/          # D2/R3: 스타일 가이드 선택
    ├── /structure-planner/            # D2: 개요 생성
    ├── /legal-drafter/                # D3/R4: 핵심 초안 작성
    ├── /document-reviser/             # R2/R4: 수정 범위 및 변경 추적
    ├── /consistency-checker/          # D4/R5: 품질 검토 및 검증
    └── /output-formatter/             # D5/R6: 파일 생성 및 버전 관리
```

## 파이프라인

### 초안 작성 파이프라인 (D1~D6)

```
D1  요청 해석 ──► D2  개요 및 규범 ──► D3  초안 작성
                                           │
D6  파일 저장 ◄── D5  출력 및 미리보기 ◄── D4  일관성 검토 ◄┘
```

### 수정 파이프라인 (R1~R7)

```
R1  문서 분석 ──► R2  수정 범위 ──► R3  규범 검토 ──► R4  수정 실행
                                                          │
R7  파일 저장 ◄── R6  출력 (변경 추적) ◄── R5  일관성 검토 ◄┘
```

## 스킬

| 스킬 | 파이프라인 단계 | 목적 |
|---|---|---|
| `request-interpreter` | D1, R1 | 요청 분류, 파라미터 추출, 범위 확인, 문서 파싱 |
| `convention-selector` | D2, R3 | 언어/법역별 스타일 가이드 선택, 규범 검증 |
| `structure-planner` | D2 | 템플릿 기반 개요 생성, 조항 맵 초기화 |
| `legal-drafter` | D3, R4 | 올바른 문체 및 용어를 사용한 법률 문장 작성 |
| `document-reviser` | R2, R4 | 수정 범위 적용, 변경 추적, 비수정 섹션 보존 |
| `consistency-checker` | D4, R5 | 8/10개 항목 체크리스트, 자기 검토, 검증 스크립트 실행 |
| `output-formatter` | D5~D6, R6~R7 | 파일 생성(.docx/.pdf/.md/.txt), 자동 버전 관리 |

## 규범 시스템

### 한국어 법률문서

한국어 문서는 다음 규범을 따릅니다:

| 항목 | 규칙 |
|---|---|
| **문체** | 문어체 (~한다, ~하여야 한다, ~할 수 있다). 의견서는 ~합니다 체 허용 |
| **번호체계** | 조·항·호·목 (제1조 → ① → 1. → 가.) |
| **인용** | 「법률명」 제N조. 판례: 대법원 YYYY. MM. DD. 선고 YYYY다NNNNN 판결 |
| **용지** | A4, 바탕체 12pt (본문), 맑은 고딕 (제목) |
| **날짜** | YYYY년 MM월 DD일 |

주요 참고자료:
- `style-guide-kr.md` — 한국 법률문서 작성 규범 (법률용어 정확도, 자주 발생하는 오류, 법원문서 규칙, 문장구조 패턴 포함)
- `register-guide-kr.md` — 문어체 가이드 (문서유형별 문체, 접속사 40+개, 금지표현 50+개, 경어법, 띄어쓰기)
- `template-litigation-kr.md` — 소장/답변서/준비서면 구조
- `template-advisory-kr.md` — 법률의견서 구조 (쟁점→결론→분석)
- `template-corporate-kr.md` — 이사회 결의서, 정관, 주주총회 의사록

### 영어 법률문서

| 항목 | 미국 | 영국 | 국제 |
|---|---|---|---|
| 스타일 가이드 | Bluebook + Garner | OSCOLA | 중립 |
| 용지 크기 | US Letter | A4 | A4 |
| 번호체계 | Art/Sec/(a)/(i) | Clause/1.1/(a) | Art/Sec/Para/(a) |
| 날짜 | Month DD, YYYY | DD Month YYYY | DD Month YYYY |

주요 참고자료:
- `style-guide-en-us.md` — Garner의 8원칙, 25개 이상의 자주 발생하는 오류, 상세 Bluebook 규칙, IRAC/CRAC 구조
- `register-guide-en.md` — 25개 이상의 법률 용어, 35개 이상의 사용 지양 표현, 문서 유형별 어조 설정, 성중립 표현

## 검증 스크립트

일관성 검토 단계(D4/R5)에서 자동 품질 검사가 실행됩니다:

| 스크립트 | 검사 항목 |
|---|---|
| `numbering-validator.py` | 조·항·호·목 순서, Article/Section/(a)/(i) 계층, 고아 항목 감지 |
| `cross-reference-checker.py` | 내부 상호 참조가 존재하는 섹션을 가리키는지 확인 |
| `register-validator.py` | 한국어 문어체 위반 (구어체, 이중피동, 번역투), 영어 격식 (축약형, 수동태) |
| `term-consistency-checker.py` | 정의 용어 사용 일관성, 미정의 약어, 미사용 용어 |
| `citation-format-checker.py` | 「」 인용 형식, Bluebook, OSCOLA 준수 여부 |

```bash
# 개별 실행
python .claude/skills/consistency-checker/scripts/register-validator.py document.md
python .claude/skills/consistency-checker/scripts/term-consistency-checker.py document.md --generate-registry
python .claude/skills/consistency-checker/scripts/citation-format-checker.py document.md --jurisdiction korea
```

## 라이브러리 시스템

`/library/` 폴더에는 세 가지 유형의 재사용 가능한 자산이 포함됩니다. **사용자가 직접 관리**하며 **gitignore** 처리됩니다(기밀 유지).

### 하우스 스타일 (`/library/house-styles/`)

기관별 서식 재정의. 스타일마다 폴더를 생성합니다:

```
/library/house-styles/my-firm/
├── style-config.json    # 여백, 폰트, 번호 설정
└── signature-block.md   # 표준 서명 형식
```

### 템플릿 (`/library/templates/`)

문서 구조 골격. 에이전트가 문서 유형과 언어에 맞는 템플릿을 자동으로 매칭합니다. 기본 제공 템플릿은 `.claude/skills/structure-planner/references/`에 위치합니다.

### 선례 문서 (`/library/precedents/`)

기 작성 완료된 문서. 에이전트가 구조를 분석하고 지정된 변수만 교체하여 높은 충실도로 패턴을 재현합니다.

## 파일 처리

| 형식 | 읽기 | 쓰기 |
|---|---|---|
| `.docx` | `python-docx` | `python-docx` |
| `.pdf` | Claude Code 기본 | LibreOffice 또는 pandoc 경유 |
| `.md` | 직접 | 직접 |
| `.txt` | 직접 | 직접 |

### 버전 관리

출력 파일은 자동으로 버전이 부여됩니다(`_v1`, `_v2`, `_v3`). 이전 버전은 절대 덮어쓰지 않습니다.

```
output/documents/20260311_advisory_tax-opinion_v1.docx
output/documents/20260311_advisory_tax-opinion_v2.docx    # 수정본
```

## 주요 설계 원칙

- **단일 에이전트 아키텍처**: 서브에이전트 없음. 설정 가능한 강도(가볍게/표준/꼼꼼하게)의 자기 검토로 품질 관리.
- **추론 우선**: 에이전트가 파라미터를 적극적으로 추론하고 진행합니다. 가정 사항을 간략히 명시하며 질문을 최소화합니다.
- **자리 표시자 우선**: 누락된 정보는 자리 표시자로 처리되며, 임의 생성하지 않습니다.
- **이중 규범**: 한국어와 영어 법률문서는 완전히 별개의 규범을 따릅니다. 혼용은 품질 오류입니다.
- **범위 경계**: 계약서, 법률 자문, 법률 조사, 문서 감사는 명시적으로 범위 외입니다.

## 설정

### 검토 강도

| 수준 | 동작 |
|---|---|
| **가볍게** (Light) | 자기 검토 1회, 치명적 문제만 수정 |
| **표준** (Standard) | 2회 검토, 치명적·주요 문제 수정 (기본값) |
| **꼼꼼하게** (Thorough) | 3회 검토, 모든 문제 수정 |

에이전트가 문맥에서 강도를 추론합니다 ("빨리 초안만" → 가볍게, "최종본이야 꼼꼼하게" → 꼼꼼하게).

### 이중언어 용어 처리

| 상황 | 예시 |
|---|---|
| 한국어 문서 + 영어 개념 | 적법절차(due process)의 원칙에 따라... |
| 영어 문서 + 한국어 개념 | the Gab/Eul (갑/을) party designation... |

## 라이선스

[Apache License 2.0](../../LICENSE) 라이선스를 따릅니다.
