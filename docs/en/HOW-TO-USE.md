# How to Use the Legal Writing Agent

[English](./HOW-TO-USE.md) | [한국어](../ko/HOW-TO-USE.md)

> This guide is written for **non-developers**. You don't need to understand Python, Git, or APIs. If you can type instructions, you can use this tool.

---

## What You Need (One-Time Setup)

| What | Why | How to Get It |
|------|-----|---------------|
| **Claude Code** | This is the app that runs the agent | [Get started here](https://docs.anthropic.com/en/docs/claude-code/overview) — available as CLI, desktop app, or VS Code extension |
| **This repository** | Contains the agent and writing conventions | Download from GitHub (see below) |
| **python-docx** | Required for DOCX generation and DOCX-based revision outputs | `pip install python-docx` |
| **pandoc** or **LibreOffice** | Needed if you want PDF output on this machine | Install one of them locally |

That's it. No databases, no servers.

---

## Downloading the Repository

### If you have Git installed

```bash
git clone https://github.com/kipeum86/legal-writing-agent.git
```

### If you don't have Git

1. Go to [github.com/kipeum86/legal-writing-agent](https://github.com/kipeum86/legal-writing-agent)
2. Click the green **"Code"** button
3. Click **"Download ZIP"**
4. Unzip to a folder of your choice

---

## Starting the Agent

### Option A: Desktop App / VS Code

1. Open Claude Code
2. Open the `legal-writing-agent` folder
3. The agent activates automatically as the **Legal Drafting Specialist** for **KP Legal Orchestrator**

### Option B: Terminal (CLI)

```bash
cd legal-writing-agent
claude
```

---

## Drafting a New Document

Tell the agent what you need in natural language. The agent is **bilingual** — it works in Korean and English.

### Simple Drafts (Full Support)

These document types can be drafted from instructions alone:

> "이사회 결의서 작성해줘. 신규 대표이사 선임 건."

> "Draft board resolutions for the appointment of a new CEO."

> "컴플라이언스 가이드라인 초안 써줘. 내부자 거래 관련."

### Conditional Drafts (Authority Packet Needed)

For advisory, litigation, and regulatory documents, the agent needs your **authority packet** — the statutes, case citations, and factual basis:

> "법률의견서 작성해줘. 아래 법령과 판례를 근거로." (then provide your sources)

> "Draft a legal memorandum on data breach notification obligations. Here are the relevant statutes: ..."

Without an authority packet, the agent produces a **skeleton draft** — full structure and boilerplate, but with placeholders like `[Authority needed: ...]` and `[Argument: ...]` where substantive content belongs.

### What Happens Behind the Scenes

The agent runs a 6-step pipeline (D1–D6):

1. **Interprets** your request — document type, language, jurisdiction, conventions
2. **Plans** the structure — selects conventions, generates outline
3. **Drafts** section by section — maintaining term consistency throughout
4. **Self-reviews** — runs an 8-item consistency checklist (terms, numbering, cross-references, register, conventions)
5. **Formats** the final document
6. **Saves** automatically to the resolved documents directory with versioning (`_v1`, `_v2`, ...)

---

## Revising an Existing Document

Place your document in the resolved input directory (`$LEGAL_AGENT_PRIVATE_DIR/input/` when set, otherwise `<repo>/input/`), then tell the agent what to change:

> "input 폴더에 넣은 의견서 수정해줘. 3번 쟁점 부분 논거를 보강하고 결론 다시 써줘."

> "Revise the brief in the input folder. Strengthen the argument in Section III and rewrite the conclusion."

The agent runs a 7-step revision pipeline (R1–R7):

- Reads and analyzes your document structure
- Maps your revision instructions to specific sections
- Executes changes with **revision tracking outputs**:
  - Level B revision artifacts: clean copy, `{name}_redline_v{N}.diff`, and section-level `change-map.json`
  - `.md` inline diff markers when markdown output is used
- Runs a 10-item consistency check
- Saves with `_revised_` suffix and auto-versioning

### Supported File Formats

| Format | Read | Write |
|--------|:----:|:-----:|
| `.docx` | Yes | Yes |
| `.pdf` | Yes | Yes |
| `.md` | Yes | Yes |
| `.txt` | Yes | Yes |

---

## Using the Library for Better Results

The agent performs best when you populate `/library/` with your organization's real materials. Everything in `/library/` stays local, and the ingest source registry is also kept local by default.

### What to Add

| Library Folder | What to Put There | Effect |
|---------------|-------------------|--------|
| `library/precedents/` | Well-written sample documents | Agent matches your tone, structure, and phrasing |
| `library/templates/` | Document skeletons | Agent follows your section flow |
| `library/house-styles/` | Internal style rules | Agent applies your org's formatting preferences |
| `library/grade-a/` | Statutes, official guidelines | Available as authority packet for conditional documents |
| `library/grade-b/` | Case law, practice memos | Secondary reference material |
| `library/grade-c/` | Academic papers, commentary | Background reference only |

### Adding Sources with Ingest

Got statutes, guidelines, case law, or academic papers you want the agent to reference? Use the **ingest** system:

#### Step 1: Drop the file

Place any file (PDF, DOCX, PPTX, XLSX, HTML, MD, TXT) into `library/inbox/`.

> **Note:** `.hwp` files are not directly supported. Convert to PDF or DOCX first.

#### Step 2: Tell the agent

> "inbox에 파일 넣었어, ingest 해줘"

or simply:

> "/ingest"

#### Step 3: Done

The agent will:

1. **Convert** the file to Markdown (using MarkItDown)
2. **Auto-classify** the source by trust level:
   - **Grade A** — Official primary sources: statutes (법률 제XXXXX호), government guidelines, official agency publications
   - **Grade B** — Verified secondary sources: case law (판례), practice updates, bar association materials
   - **Grade C** — Academic/reference: journal articles, theses, academic papers
   - **Grade D** — Rejected: news articles, AI summaries, wiki content (with a warning)
3. **Generate metadata** — title, document type, publisher, date, keywords, related legal provisions
4. **Place** the file in the correct `library/grade-x/` subfolder
5. **Update** the source registry index

Your new source is now available as reference material for future drafts.

#### What Gets Classified Where (Examples)

| You Add | What Happens |
|---------|-------------|
| 개인정보보호법 전문 (PDF) | Grade A, filed under `grade-a/statutes/` |
| 대법원 판결문 | Grade B, filed under `grade-b/court-precedents/` |
| Practice update newsletter | Grade B, filed under `grade-b/practice-materials/` |
| 학술 논문 (법학 저널) | Grade C, filed under `grade-c/academic/` |
| 뉴스 기사 | Grade D — rejected with warning |

---

## Review Intensity

You can control how thoroughly the agent self-reviews:

| Level | What It Does | When to Use |
|-------|-------------|-------------|
| **Light** (가볍게) | 1 review pass, critical issues only | Quick drafts, simple documents |
| **Standard** (표준) | 2 review passes, critical + major issues | Default — most work |
| **Thorough** (꼼꼼하게) | 3 review passes, all issues | High-stakes documents, final submissions |

The agent infers from context:

- "빨리 초안만 줘" → Light
- "최종본이야, 꼼꼼하게 봐줘" → Thorough
- No mention → Standard

---

## Dual-Standard Writing

The agent applies **different conventions depending on the document language**:

### Korean Documents

- Register: 문어체 (~한다, ~하여야 한다)
- Numbering: 조·항·호·목 (제1조 → ① → 1. → 가.)
- Citations: 「법률명」 제N조, 대법원 YYYY. MM. DD. 선고 판결
- Page: A4, 바탕체 12pt (body), 맑은 고딕 (headings)
- Exception: Korean legal opinions / client memoranda may use the opinion-specific profile from `docs/_private/ko-legal-opinion-style-guide.md` (2.54 cm margins, 11pt body text, 1.15 spacing)

### English Documents

- Register: Formal legal prose
- Numbering: Article/Section/(a)/(i) (US), Clause/1.1/(a) (UK)
- Citations: Bluebook (US), OSCOLA (UK), Neutral (International)
- Page: US Letter (US) or A4 (UK/International)

The agent auto-detects which convention set to use based on the document language and jurisdiction. **Mixing conventions is treated as a quality failure.**

---

## Tips for Best Results

### Be Specific About What You Want

| Instead of | Try |
|-----------|-----|
| "의견서 써줘" | "임대차 분쟁에 대한 법률의견서 써줘. 근거 법령은 아래와 같아: ..." |
| "Draft a memo" | "Draft an internal memo on the regulatory implications of the new AI Act for our compliance team" |

### Provide Good Precedents

The single most effective way to get better output is to add high-quality sample documents to `library/precedents/`. The closer the sample matches your target document type, the better the result.

### Use the Library for Repeated Work

If your team drafts the same types of documents regularly, set up:
1. Templates in `library/templates/` for consistent structure
2. House styles in `library/house-styles/` for formatting rules
3. Precedents in `library/precedents/` for tone and phrasing

### Know the Scope

This agent drafts and revises **non-contract** legal documents. It will decline:
- Contract drafting or review ("NDA 만들어줘" → out of scope)
- Legal advice or risk assessment
- Legal research (searching for statutes or case law)
- Document review or accuracy auditing

---

## What This Tool Does NOT Do

- **It does not provide legal advice.** It's a writing assistant that helps you draft and revise legal documents faster. A qualified lawyer must review the output.
- **It does not conduct legal research.** It incorporates references you provide, but does not search for statutes, cases, or regulations on its own.
- **It does not verify citations.** User-provided citations are included verbatim. Missing ones become placeholders.
- **It does not draft contracts.** NDAs, license agreements, and other contracts are out of scope.
- **It does not know your internal policies** — unless you add them via the Library.

---

> **Remember:** This is a power tool, not an autopilot. It makes legal document drafting dramatically faster, but the final judgment always belongs to a qualified human.
