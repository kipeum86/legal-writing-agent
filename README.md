# Bilingual Legal Writing Agent

🌐 **Language**: English | [한국어](docs/ko/README.md)

A Claude Code agent that drafts and revises **non-contract legal documents** in Korean and English, applying jurisdiction-appropriate legal writing conventions.

## Best Results: Use the Library

The agent performs best when you actively populate `/library/` with your organization's real materials. Everything in `/library/` is stored locally in this project folder, so you can build up your own reusable writing base over time.

- Add strong sample writing to `/library/precedents/` to guide tone, structure, level of detail, and preferred phrasing
- Add reusable skeletons to `/library/templates/` for document-specific section flow
- Add internal formatting or style preferences to `/library/house-styles/`

High-quality, closely matched samples usually lead to noticeably better outputs. If you want the draft to sound like your team, the most effective way is to give the agent good example writing in the Library and keep that local Library curated with your team's best materials.

## What It Does

- **Drafts** new legal documents from user instructions (D1–D6 pipeline)
- **Revises** existing legal documents with tracked changes (R1–R7 pipeline)
- **Dual-standard writing**: Korean documents follow Korean conventions (쟁점→결론→분석, 「법률명」 인용), English documents follow US/UK/international conventions (IRAC/CRAC, Bluebook/OSCOLA)
- **Reads and writes** `.docx`, `.pdf`, `.md`, `.txt` formats

## What It Does NOT Do

- Contract drafting or review
- Legal advice, risk assessment, or strategy recommendations
- Legal research (searching for statutes, cases, regulations)
- Document review or accuracy auditing
- Citation fabrication — uses `[Citation needed]` placeholders instead

## Supported Document Types

| # | Category | Support Level | Examples |
|---|---|:---:|---|
| 1 | **Advisory** (의견서/메모) | Conditional | 법률의견서, legal memo, due diligence report |
| 2 | **Corporate** (기업문서) | Full | 이사회 결의서, 정관, board resolution, articles |
| 3 | **Litigation** (소송문서) | Conditional | 소장, 답변서, 준비서면, complaint, brief |
| 4 | **Regulatory** (규제문서) | Conditional | 인허가 신청서, compliance report |
| 5 | **General Legal** (기타) | Full | 컴플라이언스 가이드라인, policy document |

- **Full**: Complete draft from instructions alone
- **Conditional**: Requires an authority packet (statutes, case citations, factual basis). Without it, the agent produces a skeleton draft with placeholders.

## Quick Start

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- Python 3.10+ with `python-docx` package:
  ```bash
  pip install python-docx
  ```

### Usage

1. Open this project folder in your terminal
2. Run `claude` to start Claude Code — `CLAUDE.md` loads automatically
3. For better results, place templates, house styles, and sample writing in `/library/` first
4. Give instructions:

**Drafting:**
```
이사회 결의서 작성해줘. 의안은 대표이사 선임의 건이야.
```
```
Draft a legal memorandum analyzing whether the non-compete clause is enforceable under California law.
```

**Revision:**
Place the document in `/input/`, then:
```
input 폴더에 있는 답변서 수정해줘. 피고 주장 부분 보강해야 해.
```
```
Revise the brief in /input/. Strengthen the argument in Section III.
```

## Data Security and Privacy

This project runs locally on your filesystem. Your `/input/`, `/output/`, and `/library/` files stay in this project folder, and `/library/` is gitignored by default so your reusable materials are not committed unless you choose otherwise.

However, drafting and revision still rely on Claude Code / Anthropic model API calls. In practice, that means prompts and document text you provide to the agent may be transmitted to Anthropic in order to generate outputs.

If you plan to use this for real legal work involving confidential, privileged, or personally identifiable information:

- Prefer a commercial Anthropic organization or API setup over a personal consumer account, and review the retention terms that apply to your plan
- If your organization requires tighter controls, evaluate whether an approved Zero Data Retention configuration is available and appropriate for your workflow; Anthropic's current documentation notes important feature and product exceptions
- Check with your organization's security, compliance, and IT teams before processing sensitive matter files through any AI tool

Official Anthropic references:
- [Claude Code data usage](https://docs.anthropic.com/en/docs/claude-code/data-usage)
- [Commercial data retention](https://privacy.anthropic.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data)
- [Zero Data Retention scope and exceptions](https://privacy.anthropic.com/en/articles/8956058-i-have-a-zero-data-retention-agreement-with-anthropic-what-products-does-it-apply-to)

## Project Structure

```
/
├── CLAUDE.md                          # Agent orchestrator
├── /input/                            # Place documents here for revision
├── /output/
│   ├── /documents/                    # Generated documents (auto-versioned)
│   ├── /manifests/                    # Document parameters (JSON)
│   ├── /clause-maps/                  # Section tracking (JSON)
│   ├── /placeholders/                 # Placeholder registry (JSON)
│   └── /term-registries/             # Defined term tracking (JSON)
├── /library/                          # Reusable assets (user-managed)
│   ├── /inbox/                        # Drop source files here for ingest
│   ├── /grade-a/                      # Official primary sources (statutes, guidelines)
│   ├── /grade-b/                      # Secondary sources (case law, law firm materials)
│   ├── /grade-c/                      # Academic/reference sources
│   ├── /house-styles/                 # Org-specific formatting rules
│   ├── /templates/                    # Document structure skeletons
│   └── /precedents/                   # Reference documents
├── /docs/
│   └── formatting-conventions-reference.md
└── /.claude/skills/                   # Agent skills & references
    ├── /request-interpreter/          # D1/R1: Request parsing, classification
    ├── /convention-selector/          # D2/R3: Style guide selection
    ├── /structure-planner/            # D2: Outline generation
    ├── /legal-drafter/                # D3/R4: Core drafting
    ├── /document-reviser/             # R2/R4: Revision scope & tracking
    ├── /consistency-checker/          # D4/R5: Quality checks & validation
    ├── /output-formatter/             # D5/R6: File generation & versioning
    └── /ingest/                       # Source file ingestion & classification
```

## Pipelines

### Drafting Pipeline (D1–D6)

```
D1  Request Interpretation ──► D2  Outline & Convention ──► D3  Drafting
                                                                 │
D6  File Save ◄── D5  Output & Preview ◄── D4  Consistency Check ◄┘
```

### Revision Pipeline (R1–R7)

```
R1  Document Ingestion ──► R2  Scope ──► R3  Convention Check ──► R4  Revision
                                                                       │
R7  File Save ◄── R6  Output (tracked changes) ◄── R5  Consistency Check ◄┘
```

## Skills

| Skill | Pipeline Steps | Purpose |
|---|---|---|
| `request-interpreter` | D1, R1 | Classify request, extract parameters, check scope, parse documents |
| `convention-selector` | D2, R3 | Select style guide by language/jurisdiction, verify conventions |
| `structure-planner` | D2 | Generate outline from templates, initialize clause map |
| `legal-drafter` | D3, R4 | Draft legal prose with correct register and terminology |
| `document-reviser` | R2, R4 | Enforce revision scope, track changes, preserve untouched sections |
| `consistency-checker` | D4, R5 | 8/10-item checklist, self-review, run validation scripts |
| `output-formatter` | D5–D6, R6–R7 | Generate files (.docx/.pdf/.md/.txt), auto-version |
| `ingest` | — | Convert, classify, and catalog source files from inbox |

## Convention System

### 한국어 법률문서 (Korean Legal Writing)

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

### English Legal Writing

| Feature | US | UK | International |
|---|---|---|---|
| Style guide | Bluebook + Garner | OSCOLA | Neutral |
| Page size | US Letter | A4 | A4 |
| Numbering | Art/Sec/(a)/(i) | Clause/1.1/(a) | Art/Sec/Para/(a) |
| Date | Month DD, YYYY | DD Month YYYY | DD Month YYYY |

Key references:
- `style-guide-en-us.md` — Garner's 8 principles, 25+ common errors, detailed Bluebook rules, IRAC/CRAC structure
- `register-guide-en.md` — 25+ legal terms of art, 35+ words to avoid, tone calibration by document type, gender-neutral language

## Validation Scripts

Automated quality checks run during the consistency check step (D4/R5):

| Script | What It Checks |
|---|---|
| `numbering-validator.py` | 조·항·호·목 순서, Article/Section/(a)/(i) hierarchy, orphan detection |
| `cross-reference-checker.py` | Internal cross-references point to existing sections |
| `register-validator.py` | 한국어 문어체 위반 (구어체, 이중피동, 번역투), English formality (contractions, passive voice) |
| `term-consistency-checker.py` | Defined term usage consistency, undefined abbreviations, unused terms |
| `citation-format-checker.py` | 「」 인용 형식, Bluebook, OSCOLA compliance |

```bash
# Run individually
python .claude/skills/consistency-checker/scripts/register-validator.py document.md
python .claude/skills/consistency-checker/scripts/term-consistency-checker.py document.md --generate-registry
python .claude/skills/consistency-checker/scripts/citation-format-checker.py document.md --jurisdiction korea
```

## Library System

The `/library/` folder contains reusable assets and ingested sources. These are **user-managed** and **gitignored by default**, which helps keep them out of version control. They still remain subject to your Claude Code / Anthropic data-handling setup when their contents are sent in prompts.

### House Styles (`/library/house-styles/`)

Organization-specific formatting overrides. Create a folder per style:

```
/library/house-styles/my-firm/
├── style-config.json    # Margins, fonts, numbering preferences
└── signature-block.md   # Standard signature format
```

### Templates (`/library/templates/`)

Document structure skeletons. The agent auto-matches by document type and language. Built-in templates are in `.claude/skills/structure-planner/references/`.

### Precedents (`/library/precedents/`)

Previously completed documents. The agent analyzes their structure and replicates patterns with high fidelity, substituting only specified variables.

### Adding Your Own Sources

1. Drop any file (PDF, DOCX, etc.) into `library/inbox/`
2. Tell the agent: `/ingest` or "파일 넣었어"
3. The agent will automatically:
   - Convert to structured Markdown
   - Classify source grade (A/B/C)
   - Generate metadata (frontmatter)
   - Place in the appropriate `library/grade-{a,b,c}/` folder
   - Update search indexes

> **Note:** Dropping files alone does not trigger processing.
> You must run `/ingest` or tell the agent (e.g. "inbox에 파일 넣었어")
> to start the parsing pipeline.

**Source Grades:**

| Grade | Description | Examples |
|---|---|---|
| A | Official primary sources | Statutes, regulations, government guidelines |
| B | Secondary sources | Case law, law firm newsletters, bar association materials |
| C | Academic/reference | Journal articles, theses, academic papers |

Ingested sources serve as authority packets for Conditional-support documents (Advisory, Litigation, Regulatory).

## File Handling

| Format | Read | Write |
|---|---|---|
| `.docx` | `python-docx` | `python-docx` |
| `.pdf` | Claude Code native | via LibreOffice or pandoc |
| `.md` | Direct | Direct |
| `.txt` | Direct | Direct |

### Versioning

Output files are auto-versioned (`_v1`, `_v2`, `_v3`). Previous versions are never overwritten.

```
output/documents/20260311_advisory_tax-opinion_v1.docx
output/documents/20260311_advisory_tax-opinion_v2.docx    # revision
```

## Key Design Decisions

- **Single-agent architecture**: No sub-agents. Quality review via self-review with configurable intensity (Light/Standard/Thorough).
- **Inference-first**: The agent infers parameters aggressively and proceeds. It states assumptions briefly rather than asking questions.
- **Placeholder over fabrication**: Missing information becomes a bracketed placeholder, never fabricated content.
- **Dual-standard**: Korean and English legal documents follow completely separate convention sets. Mixing is a quality failure.
- **Scope boundaries**: Contracts, legal advice, legal research, and document auditing are explicitly out of scope.

## Configuration

### Review Intensity

| Level | Behavior |
|---|---|
| **Light** (가볍게) | 1 self-review pass, critical issues only |
| **Standard** (표준) | 2 passes, critical + major issues (default) |
| **Thorough** (꼼꼼하게) | 3 passes, all issues |

The agent infers intensity from context ("빨리 초안만" → Light, "최종본이야 꼼꼼하게" → Thorough).

### Bilingual Term Handling

| Situation | Example |
|---|---|
| Korean doc + English concept | 적법절차(due process)의 원칙에 따라... |
| English doc + Korean concept | the Gab/Eul (갑/을) party designation... |

## Part of Jinju Law Firm

This agent is part of the **법무법인 진주 (Jinju Law Firm)** series of specialized legal AI agents:

| Agent | Attorney | Specialty |
|-------|----------|-----------|
| [game-legal-research](https://github.com/kipeum86/game-legal-research) | 심진주 (Sim Jinju) | Game industry law |
| [legal-translation-agent](https://github.com/kipeum86/legal-translation-agent) | 변혁기 (Byeon Hyeok-gi) | Legal translation |
| [general-legal-research](https://github.com/kipeum86/general-legal-research) | 김재식 (Kim Jaesik) | Legal research |
| [PIPA-expert](https://github.com/kipeum86/PIPA-expert) | 정보호 (Jeong Bo-ho) | Data privacy law |
| [contract-review-agent](https://github.com/kipeum86/contract-review-agent) | 고덕수 (Ko Duksoo) | Contract review |
| **[legal-writing-agent](https://github.com/kipeum86/legal-writing-agent)** | **한석봉 (Han Seokbong)** | **Legal writing** |
| [second-review-agent](https://github.com/kipeum86/second-review-agent) | 반성문 (Ban Seong-mun) | Quality review (Partner) |

## License

Licensed under the [Apache License 2.0](LICENSE).
