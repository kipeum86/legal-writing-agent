# Legal Opinion Style Guide (EN / KO)

A bilingual style guide for producing formal legal opinion memoranda in English and Korean. The conventions below draw from widely-recognized legal-writing principles.

---

## EN — English Style Conventions

### 1. Document Architecture

A formal opinion letter generally contains the following blocks, in order. Omit or merge blocks only when scope clearly permits (e.g., a one-issue memo may collapse Executive Summary into the Issue Tree).

1. **AI-Generation Notice (top banner)** — prominent notice at the very top stating the document was produced by an AI-assisted workflow and is not legal advice (see §15.1).
2. **Letterhead / Heading Block** — firm or system name, document type label ("MEMORANDUM" / "LEGAL OPINION"), date, addressee ("TO:"), author ("FROM:"), matter reference ("RE:"), and classification marker appropriate to the document's actual status (see §16 — for unreviewed AI drafts, use *Confidential — AI-Generated Draft*, not privilege labels).
3. **Scope & As-Of Date** — one paragraph: (i) the question(s) presented, (ii) the jurisdictions consulted, (iii) the materials reviewed, (iv) the cutoff date for research, and (v) any facts or assumptions expressly taken as given.
4. **Executive Summary / Conclusions** — issue-by-issue conclusions stated in full sentences, calibrated to the certainty scale (§5), placed before the detailed analysis so the reader can stop here if they want only the bottom line.
5. **Issue Tree** — a short, numbered list of questions addressed. Keep as a standalone section; do not embed inside the body analysis.
6. **Detailed Analysis** — one subsection per issue. Default framework: IRAC (Issue / Rule / Application / Conclusion) or CREAC (Conclusion / Rule / Explanation / Application / Conclusion). See §7.
7. **Counter-Analysis / Risk Considerations** — for each key conclusion, state at least one alternative interpretation, adverse authority, or material risk. A conclusion without a counter is incomplete.
8. **Practical Implications / Recommendations** — actionable, enumerated steps tied to each conclusion. Distinguish *must-do* from *advisable*.
9. **Annotated Bibliography** — every cited primary source with (i) full citation, (ii) a one-line reliability note, and (iii) access method (URL or library path) for verification.
10. **Verification Guide** — step-by-step instructions for the reader to independently confirm each primary citation. Separate primary and secondary sources.
11. **Attribution Block** — for unreviewed AI drafts, a single line: *Prepared by: AI-assisted research workflow — [date]*. Do **not** include attorney-style signature fields (bar admission, bar number, "Attorney at Law") by default; these may be added only after a qualified reviewer substantively adopts the document as their own work.
12. **Closing Disclaimer Block** — generic limitation-of-use and no-advice language (see §15.2).

### 2. Pre-Drafting Checklist

Before drafting, confirm in writing (in the Scope paragraph or a cover note):

- [ ] Question(s) presented — captured verbatim from the request
- [ ] Jurisdiction(s) — primary, secondary, conflict-of-laws flags
- [ ] Facts accepted as given vs. facts that would materially alter the conclusion
- [ ] Research cutoff date
- [ ] Deliverable form (memo / letter / bench memo / talking points)
- [ ] Audience (in-house counsel / client principal / court / regulator)
- [ ] Privilege posture (attorney-client, work product, or neither)

If any item is missing, state the assumption explicitly in the Scope block with `[Assumption]` tagging.

### 3. Register, Tone & Voice

- **Register:** formal, third-person, client-facing. Avoid "I", contractions, exclamation marks, and conversational hedges ("kind of", "sort of", "I think").
- **Voice:** active by default; passive only to foreground the object (e.g., "the application *was denied*" when the agency is immaterial).
- **Tone:** considered professional position, not tentative observation. Write as if the conclusion will be read aloud in a partnership meeting or to a regulator.
- **Plain language:** prefer short Anglo-Saxon words over long Latin/French alternatives where meaning is preserved ("use", not "utilize"; "before", not "prior to"; "about", not "with respect to" where "about" suffices).
- **Latin & legal terms of art:** reserve *inter alia*, *mutatis mutandis*, *prima facie*, *a fortiori* for contexts where they genuinely add precision; italicize on first use.
- **No rhetorical padding:** delete "needless to say", "it goes without saying", "obviously", "clearly". If it is obvious, it needs no label; if it is not, the label is misleading.

### 4. Sentence-Level Style

- **Sentence length:** average 20–25 words in analysis, 15–20 in conclusions. Break sentences over 35 words.
- **One idea per sentence.** Compound thoughts get their own sentences or enumerated sub-clauses.
- **Avoid deep nominalization** (turning verbs into nouns). Prefer *decided* over *made a decision*; *considered* over *gave consideration to*.
- **Avoid double negatives** and unintentional ambiguity from modifier placement.
- **Parallelism:** lists must be grammatically parallel ("The statute requires notice, consent, and purpose limitation" — not "notice, consenting, and limiting purpose").
- **Defined terms do the work of hedges:** once "Transaction" is defined, do not also say "the proposed transaction" — pick one and stick.

### 5. Certainty Language Scale

Map every conclusion to exactly one term on this scale. Use the same vocabulary throughout a single document. Avoid undefined hedges ("maybe", "possibly", "could be").

For this agent, this section is a formatting convention only. Do not generate legal conclusions, risk assessments, recommendations, or certainty levels unless they are supplied by the user or supported by an authority packet under `docs/policies/drafting-scope.md`; use the counsel placeholders from that policy when support is missing.

| Label | Meaning | Example wording |
|---|---|---|
| *Will* / *Clear* | Settled law, on-point authority, no material counter-argument | "The Transaction will constitute a 'business transfer' under art. 12(1)." |
| *Should* / *Likely* | Sound argument available; small risk of adverse interpretation | "The disclosure should satisfy the written-notice requirement." |
| *Reasonable basis* | Credible position, but material risk of a different outcome | "There is a reasonable basis to treat the payments as non-taxable." |
| *More likely than not* | > 50% probability of the stated outcome | "It is more likely than not that the contract qualifies for the safe harbor." |
| *Uncertain* / *Material risk* | Significant unresolved issue; decision-maker should be alerted | "The outcome is uncertain; a material risk exists that the regulator will re-characterize the arrangement." |

If you cannot map a conclusion to one of these, the conclusion is not ready to deliver.

### 6. Issue Framing & Executive Summary Patterns

**Issue statement (under-does-when pattern):**

> Under [governing law], does [legal actor] [legal action] when [key facts]?

Example: *Under the Personal Information Protection Act, does a controller breach art. 17 when it transfers pseudonymized data to a processor in a third country without supplementary safeguards?*

**Executive summary — one paragraph per issue, three moves:**

1. **Bottom line.** State the conclusion in one sentence using the §5 scale.
2. **Key rationale.** One sentence naming the governing rule and the decisive fact.
3. **Principal caveat.** One sentence flagging the most important risk, alternative reading, or open factual question.

Avoid opening an executive summary with "this memorandum addresses...". The reader already knows.

### 7. Detailed Analysis Framework (IRAC / CREAC)

For each issue, structure the analysis in this order. Use headings; do not let the analysis flow as a single unbroken paragraph.

- **Issue** — restate the question from §6, one sentence.
- **Rule** — the governing statute, regulation, or case-law rule. Quote the operative language verbatim when construing a statute; paraphrase is insufficient for pinpoint analysis.
- **Explanation** — interpretive guidance: how courts/regulators have read the rule, what elements the rule breaks down into, what the leading commentators say (with transparent attribution).
- **Application** — apply each element to the facts. Address each element separately; do not skip elements because "they are clearly met".
- **Conclusion** — restate the bottom line, on the §5 scale, tied to the specific facts applied.

### 8. Counter-Analysis Patterns

For every key conclusion, append a short block addressing:

- **Alternative interpretation.** The strongest reading that reaches the opposite conclusion.
- **Adverse authority.** Any case, guidance, or commentary that cuts against the position, and why it is distinguishable or less weighty.
- **Factual sensitivity.** Which fact, if different, would change the answer?
- **Regulatory re-characterization risk.** How might an enforcement body recast the conduct?

Flag unresolved conflicts inline with `[Unresolved Conflict]` at the specific finding, not aggregated at the end.

### 9. Recommendations & Action Items

- Apply `docs/policies/drafting-scope.md` before drafting recommendations. Legal risk-mitigation recommendations require user-supplied instructions or authority-packet support; otherwise use the relevant counsel placeholder or limit the section to non-substantive drafting logistics.
- Separate *Must* (legally required), *Should* (strongly advisable to reduce risk), and *Consider* (optional improvements).
- Each item is one sentence, starts with an imperative verb, and names the actor (e.g., "**Must:** Obtain the data subject's explicit consent before transferring pseudonymized records.").
- Sequence items by dependency (do this before that), not alphabetically.
- If an item has a deadline, state it (`by [date]`).

### 10. Citation Format

Primary authority first, then secondary. Within each tier, by reliability grade, then by order of appearance.

- **Statutes / regulations:** statute name, article, paragraph, subparagraph. Include effective or amendment date when the provision was recently amended (e.g., *PIPA art. 15(1), as amended 2023-09-15*). For quoted operative language, use block quotation (§11).
- **Cases:** court, case number, decision date, official reporter if available. Always pinpoint to the paragraph or page (e.g., *Supreme Court 2021Da12345, decided Feb. 10, 2023, at ¶ 17*).
- **Administrative guidance / agency decisions:** issuing body, document title, doc number if any, issuance date, public URL if available.
- **Secondary sources:** identify explicitly as such inline ("according to [treatise author]'s commentary…"); never present secondary analysis as if it were the rule of decision.
- **Unverified:** mark any citation you have not personally retrieved with `[Unverified]`. Do not paraphrase a source you have not read.
- **Cross-references within the memo:** `see §X above` / `see §X below`.

### 11. Quotations & Block Quotes

- Quote statutes verbatim when the exact wording is operative. Use block quotation for passages longer than ~50 words.
- Indent block quotes 1.0 cm left, single-spaced, with an open line above and below. Do not italicize block quotes (italics are reserved for term-of-art emphasis).
- Indicate omissions with "…" (three dots, one space each side) and alterations with square brackets: `[The person] shall…`.
- Place the pinpoint citation after the quote on a new line or in a footnote — not inside the quotation itself.

### 12. Cross-References & Internal Pointers

- Use `§` + section number for internal references: *see §7.2*.
- When referring to a specific conclusion, name the issue: *see Issue 2 above*.
- Do not use "infra" / "supra" in client-facing documents; write "above" / "below".
- Never use "ibid." or "op. cit." for internal references; repeat the short form.

### 13. Abbreviations, Dates, Numbers, Currencies

- **Abbreviations:** define on first use (*Personal Information Protection Act ("PIPA")*); do not abbreviate a term used only once.
- **Dates:** use unambiguous format — *15 March 2026* or *2026-03-15 (ISO)*. Never *03/15/2026* (locale ambiguous).
- **Numbers:** spell out one through nine; use digits for 10 and above. Always use digits when followed by a unit (*5 days*, *3 %*). Use narrow non-breaking space between number and unit.
- **Currencies:** three-letter ISO code before the amount (*KRW 1,500,000,000*, *USD 1.2 million*). Do not mix "₩" with "KRW" in the same document.
- **Large amounts:** write out once for legibility (*KRW 1,500,000,000 (one billion five hundred million Won)*).

### 14. Lists, Enumeration, Numbering, Headings

**Numbering hierarchy (body):**

- Top-level sections: `1.`, `2.`, `3.` …
- Subsections: `1.1`, `1.2`; sub-subsections: `1.1.1`, `1.1.2`.
- Analysis sub-conclusions: `(a)`, `(b)`, `(c)` — reserved for the elements of a legal test.
- Bullets (`-` or `•`) only for non-ordered enumerations where sequence is immaterial.

**Heading typography:**

- H1 (document title): 16 pt, bold, navy/near-black, 24 pt space above/below.
- H2 (main section): 13 pt, bold, navy, 18 pt above / 12 pt below.
- H3 (subsection): 11 pt, bold, 12 pt above / 6 pt below.
- H4 (sub-subsection): 11 pt, bold italic, 6 pt above / 3 pt below.

**List discipline:**

- Do not mix numbered and bulleted lists within a single analytical paragraph.
- Each item starts with a capital letter; ends with a period only if the items are complete sentences. Be consistent within a single list.
- Parallelism is mandatory (§4).

### 15. Disclaimer Blocks

Every memorandum must carry two disclaimers: an **AI-generation notice at the top** and a **closing disclaimer** near the signature block. Adapt only the cutoff date and jurisdiction.

#### 15.1 Top Banner — AI-Generation Notice

Place immediately above or below the letterhead, visually set off (e.g., boxed, grey background, or italicized block):

> **AI-Generated Draft — Not Legal Advice.** This memorandum was produced by an AI-assisted research workflow and has not been reviewed, adopted, or independently verified by licensed counsel. It is provided for informational and drafting reference only. Do not rely on any conclusion herein for legal decisions. Before acting on any point addressed in this document, obtain independent advice from an attorney qualified in the relevant jurisdiction.

#### 15.2 Closing Disclaimer

Place immediately before or after the signature block:

> This memorandum has been prepared for the internal use of the addressee in connection with the matter identified above. It reflects our analysis of applicable law as of **[as-of date]**, based on the facts and assumptions stated herein. This document is legal research product and does not constitute legal advice; no attorney-client relationship is created or implied by its delivery. Recipients should not rely on this memorandum without obtaining independent advice from counsel qualified in the relevant jurisdiction. We undertake no obligation to update this memorandum for subsequent changes in law, facts, or circumstances.

### 16. Signature, Privilege & Classification Markings

**Default classification for AI-generated drafts:** *Confidential — AI-Generated Draft* (or *Confidential — Internal Draft*), small caps, navy or grey, in the header of every page.

**Do NOT apply privilege labels to an unreviewed AI draft.** Labels such as *Attorney Work Product* or *Attorney-Client Communication* are misleading when no licensed attorney has prepared, reviewed, or adopted the document in a professional capacity — they also contradict the AI-Generation Notice in §15.1.

**When privilege labels become appropriate:** only after (i) a qualified attorney has substantively reviewed and adopted the analysis as the attorney's own work, and (ii) the underlying factual conditions for the privilege are met (e.g., the document was prepared in anticipation of litigation, or it is a communication between attorney and client for the purpose of legal advice). At that point, the attorney — not the AI workflow — assumes responsibility, and the classification may be upgraded to:

- *Privileged & Confidential — Attorney Work Product*, or
- *Privileged & Confidential — Attorney-Client Communication*,

as the applicable doctrine dictates. The AI-Generation Notice in §15.1 should then be removed or replaced by a reviewer's certification line.

**Attribution block for unreviewed AI drafts (default):** a single line reading *Prepared by: AI-assisted research workflow — [date]*. Do **not** pre-fill attorney-style fields such as "Attorney at Law", bar admission jurisdiction, bar number, law-firm affiliation, or a signature line formatted for a licensed attorney. Such fields falsely imply that a qualified attorney prepared, reviewed, or adopted the document.

**Reviewer sign-off (optional, post-review only):** once a qualified reviewer has substantively adopted the document, they may add their own signature block — with whatever attributes are actually theirs — directly below or replacing the attribution block. The AI-Generation Notice in §15.1 should be removed or replaced accordingly.

**Version marker:** in footer or cover note — *Draft v0.3 — 2026-04-18*.

### 17. Typography & Page Setup

- **Page:** A4 (210 × 297 mm), 2.5 cm margins all sides.
- **Body text:** 11 pt serif (Times New Roman, Garamond, or equivalent); 1.2 line spacing; full justification or left justification per house preference.
- **Headings:** sans-serif companion (Arial, Helvetica, or equivalent), navy or near-black.
- **Footnotes:** 9 pt, same family as body, 1.0 line spacing.
- **Tables:** 10 pt, thin borders, header row bold with light fill.
- **Page numbers:** footer, centered or outer-aligned, format *Page X of Y*.
- **Orphan/widow control:** enabled.
- **Classification header:** small caps, navy or grey (see §16 for label selection — do not default to privilege labels on AI drafts).

### 18. Pre-Delivery Quality Checklist

Before marking a draft ready for review:

- [ ] Every conclusion maps to one term on the §5 certainty scale.
- [ ] Every key conclusion has a counter-analysis (§8).
- [ ] Every primary citation was personally fetched and pinpoint-verified.
- [ ] No secondary source is presented as if it were primary authority.
- [ ] Defined terms are used consistently; glossary present for memos > 10 pages.
- [ ] AI-Generation Notice is present at the top and Closing Disclaimer near the signature block.
- [ ] Dates, numbers, and currencies follow §13.
- [ ] Classification marker present on every page if privileged.
- [ ] Running header/footer and page numbers correct.
- [ ] Document metadata (author, last-modified) reviewed before sending.

### 19. Mode-Specific Adaptations

Mode A-D guidance is optional reference material and is not part of the default style payload. Load `docs/references/formatting-modes-reference.md` only when the user explicitly requests an executive brief, comparative matrix, enforcement/case-law treatment, or black-letter commentary.

---

## KO — 한국어 스타일 관행

### 1. 문서 구조

공식 법률 의견서는 일반적으로 아래 구성을 따릅니다. 범위가 명백히 제한적인 경우(예: 단일 쟁점 메모)에 한해 블록을 축약·병합합니다.

1. **AI 생성 고지 (상단 배너)** — 문서 최상단에 AI 기반 워크플로우 생성물이며 법률 자문이 아님을 명시합니다 (§15.1 참조).
2. **레터헤드 / 제목부** — 작성 주체(또는 시스템) 명, 문서 종류("메모" / "법률 의견서"), 작성일, 수신인("To:"), 작성자("From:"), 사건·사안 참조("Re:"), 문서의 실제 상태에 부합하는 기밀 등급 표기(§16 참조 — 미검토 AI 초안에는 *Confidential — AI-Generated Draft*를 사용하고 특권 라벨은 사용하지 않습니다).
3. **검토 범위 및 기준일** — (i) 제시된 쟁점, (ii) 검토 관할, (iii) 검토 자료, (iv) 리서치 기준일, (v) 전제 사실·가정을 한 문단으로 명시합니다.
4. **요약 결론** — 각 쟁점별 결론을 §5의 확신도 척도에 맞춰 완결된 문장으로, 상세 분석 앞에 기재합니다. 독자가 결론만 확인하고 멈출 수 있도록 구성합니다.
5. **쟁점 트리** — 다룬 질문을 짧게 번호로 나열합니다(본문에 녹이지 않고 독립 섹션으로 유지).
6. **상세 분석** — 쟁점별 소단원. 기본 구조: IRAC (쟁점 / 법리 / 적용 / 결론) 또는 CREAC (결론 / 법리 / 해설 / 적용 / 결론). §7 참조.
7. **반대 논거 / 리스크 고찰** — 주요 결론마다 최소 하나의 대체 해석, 반대 권위, 또는 중대 리스크를 함께 제시합니다. 반대 논거 없는 결론은 불완전합니다.
8. **실무적 함의 / 권고** — 결론과 연결된 구체적 실행 단계를 항목별로 제시합니다. *필수 조치*와 *권고 조치*를 구분합니다.
9. **주요 참고자료** — 인용한 1차 소스에 (i) 전체 인용, (ii) 한 줄의 신뢰도 코멘트, (iii) 검증을 위한 접근 경로(URL·서지)를 병기합니다.
10. **검증 가이드** — 독자가 1차 인용을 독립적으로 확인할 수 있도록 단계별 안내를 제공하고, 1차·2차 소스를 구분합니다.
11. **작성자 표기** — 미검토 AI 초안에는 *작성: AI 기반 리서치 워크플로우 — [날짜]* 한 줄만 둡니다. "변호사", 변호사 등록 관할·등록번호, "Attorney at Law" 등 **전문 자격을 시사하는 필드는 기본값으로 포함하지 않습니다**. 자격을 갖춘 검토자가 문서를 실질적으로 채택한 이후에만 해당 필드를 추가할 수 있습니다.
12. **마감 면책 문구** — 범용 사용 제한 및 자문 비해당 표기(§15.2 참조).

### 2. 작성 전 확인 목록

초안 작성 전에 범위 문단(또는 별도 커버노트)에 아래 항목을 명시적으로 정리합니다.

- [ ] 제시된 쟁점 — 의뢰 문구 그대로 포착
- [ ] 관할 — 1차·2차 관할, 저촉법 플래그
- [ ] 전제 사실과 결론을 뒤집을 수 있는 사실의 분리
- [ ] 리서치 기준일
- [ ] 결과물 형태 (메모 / 서신 / 법정 메모 / 토킹 포인트)
- [ ] 수신 대상 (사내 법무 / 클라이언트 / 법원 / 규제기관)
- [ ] 특권 여부 (변호사-의뢰인 특권, 업무산출물 특권, 해당 없음)

누락 항목은 범위 블록에 `[가정]` 태그와 함께 명시합니다.

### 3. 어조, 문체, 서술 주체

- **격식체:** 의뢰인 대상 공식 문서로 공손 격식체(`~합니다`, `~습니다`, `~드립니다`, `~입니다`)를 일관 사용합니다. 평서체·구어체·감정 표현은 사용하지 않습니다.
- **주체:** 1인칭 ("본인", "저는")은 피하고, 조직 주어 또는 수동형("본 메모는…") 또는 무주어 구문("검토한 바…")으로 처리합니다.
- **톤:** 잠정 관찰이 아닌 숙고된 전문가 입장. 의사결정자에게 소리 내어 읽혀도 자연스러운 완결성을 확보합니다.
- **평이한 표현 우선:** 한자어 나열보다 의미를 해치지 않는 범위에서 평이한 표현을 선택합니다 ("제공하다" ↔ "공여하다" 중 단순한 쪽).
- **외래어·원어 병기:** 검증 편의가 있을 때만 ( *개인정보 (personal information)* ). 일상적으로 굳어진 용어에는 병기하지 않습니다.
- **불필요한 수식 금지:** "주지하다시피", "당연히", "명백히 알 수 있듯" 등은 지웁니다. 자명하면 불필요하고, 자명하지 않으면 오해를 부릅니다.

### 4. 문장 단위 스타일

- **문장 길이:** 분석부 평균 60–80자, 결론부 40–60자. 100자 초과 문장은 분절합니다.
- **한 문장에 한 아이디어.** 복합 아이디어는 별도 문장 또는 열거된 하위 절로 분리합니다.
- **명사화 과잉 지양:** "검토를 진행하였습니다" → "검토하였습니다", "결정을 하였습니다" → "결정하였습니다".
- **이중 부정·모호한 수식 지양.** 수식어 위치로 인한 오해 여지를 제거합니다.
- **병렬성:** 열거 항목은 품사·어미를 맞춥니다 ("통지, 동의, 목적 제한" — "통지, 동의하기, 목적을 제한함" 금지).
- **정의어는 헤지 대신 사용:** "본건 거래"가 정의되면, 같은 문서 내에서 "위 거래"·"해당 거래"와 섞어 쓰지 않습니다.

### 5. 확신도 표현 기준

결론은 반드시 아래 표 중 하나의 표현에 대응시키며, 한 문서 내에서 용례를 혼용하지 않습니다. 정의되지 않은 헤지 표현("아마도", "어쩌면", "할 수도 있음")은 사용하지 않습니다.

이 에이전트에서 본 절은 표현 형식 기준일 뿐입니다. `docs/policies/drafting-scope.md`에 따라 사용자 또는 authority packet이 제공한 근거가 없는 법률 결론, 리스크 평가, 권고, 확신도는 생성하지 않으며, 근거가 부족한 경우 해당 정책의 counsel placeholder를 사용합니다.

| 표기 | 의미 | 예시 문구 |
|---|---|---|
| *명백히 / 확정적으로* | 확립된 법리, 직접 적용 선례, 중대한 반대 논거 없음 | "본건 거래는 법 제12조 제1항의 '영업양도'에 해당합니다." |
| *유력하게 / 가능성이 높음* | 합리적 논거가 있으나 소수 반대 해석 여지 | "본 고지는 서면 통지 요건을 충족할 가능성이 높습니다." |
| *일응 인정 가능* | 주장 가능한 논거이나 상당한 리스크 존재 | "해당 지급을 비과세로 처리할 일응의 근거가 있습니다." |
| *우세한 것으로 판단* | 50%를 초과하는 확률로 해당 결론 | "본 계약이 면책 조항에 해당할 가능성이 50%를 상회한다고 판단합니다." |
| *불확실 / 중대 리스크* | 미해결 쟁점이 남아 의사결정자에게 환기가 필요 | "결론은 불확실하며, 규제기관이 거래를 재분류할 중대한 리스크가 존재합니다." |

어느 표현에도 매핑할 수 없는 결론은 전달 준비가 된 결론이 아닙니다.

### 6. 쟁점 프레이밍 및 요약 결론 패턴

**쟁점 문장 — "적용법–주체–행위–핵심사실" 패턴:**

> [적용법]에 따를 때, [주체]가 [핵심사실]의 상황에서 [행위]하는 경우 [법적 판단]에 해당합니까?

예: *개인정보 보호법상, 처리자가 보충적 안전조치 없이 가명정보를 제3국 수탁자에게 이전하는 경우 제17조 위반에 해당합니까?*

**요약 결론 — 쟁점별 한 문단, 세 문장:**

1. **결론.** §5 척도에 따라 한 문장으로 기재합니다.
2. **핵심 근거.** 적용 법리와 결정적 사실을 한 문장으로 요약합니다.
3. **주요 유보.** 가장 중요한 리스크, 대체 해석, 또는 미확인 사실을 한 문장으로 명시합니다.

"본 메모는 …을 다룹니다"라는 도입은 지양합니다. 독자는 이미 알고 있습니다.

### 7. 상세 분석 프레임 (IRAC / CREAC)

쟁점별로 아래 순서를 따릅니다. 반드시 소제목을 사용하며, 분석을 한 덩어리 문단으로 풀지 않습니다.

- **쟁점 (Issue)** — §6의 질문을 한 문장으로 재진술합니다.
- **법리 (Rule)** — 지배 법령·규정·판례. 조문 해석 시에는 원문을 그대로 인용합니다. 패러프레이즈만으로는 핀포인트 분석이 불완전합니다.
- **해설 (Explanation)** — 법원·규제기관의 해석례, 법리의 구성 요소 분해, 주요 해설(투명한 출처 표기 포함).
- **적용 (Application)** — 요건별로 사실을 각각 적용합니다. "당연히 충족"이라는 이유로 요건을 건너뛰지 않습니다.
- **결론 (Conclusion)** — §5 척도에 따라 본 사실관계에 한정된 결론을 재진술합니다.

### 8. 반대 논거 작성 패턴

주요 결론마다 짧은 블록으로 아래 항목을 다룹니다.

- **대체 해석.** 반대 결론에 도달하는 가장 강력한 해석.
- **반대 권위.** 입장을 약화시키는 판례·지침·해설, 그리고 이를 구별하거나 경시할 수 있는 근거.
- **사실 민감도.** 어떤 사실이 달라질 때 결론이 바뀌는가?
- **규제 재분류 리스크.** 집행기관이 해당 행위를 어떻게 재구성할 수 있는가?

해소되지 않은 충돌은 해당 지점에 `[Unresolved Conflict]`를 인라인으로 표기하며, 말미에 한데 몰아 적지 않습니다.

### 9. 권고 및 실행 항목

- 권고 작성 전 `docs/policies/drafting-scope.md`를 적용합니다. 법적 리스크 완화 권고는 사용자 제공 지시 또는 authority packet 근거가 있을 때만 작성하고, 근거가 없으면 관련 counsel placeholder를 사용하거나 비실체적 작성 후속 조치로 한정합니다.
- *필수* (법적 의무), *권고* (리스크 완화 목적으로 강력히 권고), *고려* (선택적 개선)로 구분합니다.
- 각 항목은 한 문장, 명령형 동사로 시작하며, 행위자를 명시합니다 ("**필수:** 가명정보 이전 전에 정보주체의 명시적 동의를 확보할 것.").
- 의존 관계를 고려해 순서를 배열합니다 (A를 한 뒤 B). 알파벳 순이 아닙니다.
- 기한이 있으면 표기합니다 (*[날짜]까지*).

### 10. 인용 방식

1차 권위 우선, 이후 2차. 각 계층 내에서는 신뢰도 등급(A → D) 순, 같은 등급에서는 등장 순서.

- **법령·규정:** 법령명, 조, 항, 호 순. 최근 개정 조문은 개정/시행일을 병기합니다 (예: *개인정보 보호법 제15조 제1항, 2023-09-15 개정*). 원문 인용이 필요한 경우 §11 블록 인용 형식을 사용합니다.
- **판례:** 법원, 사건번호, 선고일, 공간 출처. 주장 뒷받침 지점을 반드시 핀포인트 인용합니다 (예: *대법원 2021다12345 판결, 2023. 2. 10. 선고, ¶ 17*).
- **행정 지침·결정:** 발령 기관, 문서명, 문서번호(있는 경우), 발령일, 공개 URL.
- **2차 자료:** 인라인에서 2차임을 명시합니다 ("[해설서]에 따르면…"). 2차 자료를 1차 권위로 제시하지 않습니다.
- **미확인:** 직접 확보하지 않은 자료에는 `[Unverified]`를 표기합니다. 읽지 않은 자료를 단정적으로 인용하지 않습니다.
- **내부 교차 참조:** `§X 참조 (위)` / `§X 참조 (아래)`.

### 11. 인용 및 블록 인용

- 법령 원문이 쟁점인 경우 원문 그대로 인용합니다. 약 100자를 초과하는 경우 블록 인용 형식을 사용합니다.
- 블록 인용은 좌측 1.0cm 들여쓰기, 줄간격 단배, 위아래 한 줄 여백. 이탤릭은 쓰지 않습니다 (이탤릭은 용어 강조 용도).
- 생략은 "…"(점 세 개, 앞뒤 각 한 칸), 변경은 대괄호 처리: `[해당인]은…`.
- 핀포인트 인용은 인용문 내부가 아니라 인용문 다음 줄 또는 각주에 배치합니다.

### 12. 교차 참조 및 내부 포인터

- 내부 참조는 `§` + 번호: *§7.2 참조*.
- 특정 결론을 언급할 때는 쟁점 명을 병기: *쟁점 2 참조 (위)*.
- "infra"·"supra"는 클라이언트 대면 문서에서 사용하지 않고 "위"·"아래"로 표기합니다.
- 내부 참조에서 "ibid."·"op. cit."는 사용하지 않고 단축형을 반복합니다.

### 13. 약어, 날짜, 숫자, 통화

- **약어:** 최초 등장 시 정의합니다 (*개인정보 보호법 (이하 "개인정보법")*). 한 번만 등장하는 용어는 약어화하지 않습니다.
- **날짜:** 모호하지 않은 형식 — *2026년 3월 15일* 또는 *2026-03-15 (ISO)*. *03/15/2026* 같은 로케일 의존 형식은 금지.
- **숫자:** 한 자리 수는 한글 ("하나"·"둘")로, 두 자리 이상은 아라비아 숫자로 표기합니다. 단위가 붙는 경우 항상 아라비아 숫자 (*5일*, *3%*). 숫자와 단위 사이에 좁은 비분리 공백을 둡니다.
- **통화:** ISO 3자리 코드 선행 (*KRW 1,500,000,000*, *USD 1.2 million*). 한 문서에서 "₩"와 "KRW"를 혼용하지 않습니다.
- **큰 금액:** 가독성을 위해 최초 한 번은 풀어 씁니다 (*KRW 1,500,000,000 (15억 원)*).

### 14. 목록, 열거, 번호, 제목

**본문 번호 체계:**

- 대분류: `1.`, `2.`, `3.` …
- 중분류: `1.1`, `1.2` / 소분류: `1.1.1`, `1.1.2`
- 분석 내 하위 결론: `가.`, `나.`, `다.` 또는 `(1)`, `(2)`, `(3)` — 법리 요건별로 한정해 사용합니다.
- 불릿 (`-` 또는 `•`)은 순서가 무의미한 열거에 한정합니다.

**제목 타이포그래피:**

- H1 (문서 제목): 16pt, 굵게, 네이비/다크차콜, 위아래 24pt 여백.
- H2 (주요 섹션): 13pt, 굵게, 네이비, 위 18pt / 아래 12pt.
- H3 (소제목): 11pt, 굵게, 위 12pt / 아래 6pt.
- H4 (세부 소제목): 11pt, 굵은 이탤릭, 위 6pt / 아래 3pt.

**목록 규칙:**

- 한 문단 안에서 번호 목록과 불릿 목록을 혼용하지 않습니다.
- 각 항목은 대문자/한글 정자로 시작하고, 완결된 문장이면 마침표로 끝냅니다. 한 목록 안에서 일관성을 유지합니다.
- 병렬성은 필수 (§4).

### 15. 면책 문구

모든 메모에는 두 개의 면책 문구를 반드시 기재합니다. **상단의 AI 생성 고지**와 **서명란 인근의 마감 면책 문구**입니다. 기준일 및 관할만 상황에 맞춰 조정합니다.

#### 15.1 상단 배너 — AI 생성 고지

레터헤드 바로 위 또는 아래에, 시각적으로 구분되도록 (박스, 음영, 이탤릭 블록 등) 배치합니다:

> **AI 생성 초안 — 법률 자문이 아닙니다.** 본 문서는 AI 기반 리서치 워크플로우에 의해 생성되었으며, 자격을 갖춘 변호사의 검토·채택 또는 독립적 검증을 거치지 않았습니다. 본 문서의 내용은 정보 제공 및 드래프트 참고용에 한하며, 법적 결정의 근거로 의존하여서는 아니 됩니다. 본 문서에서 다룬 사항에 대해 조치하기 전에 관련 관할에 자격을 갖춘 변호사로부터 독립적인 자문을 받으시기 바랍니다.

#### 15.2 마감 면책 문구

서명란 바로 앞 또는 뒤에 배치합니다:

> 본 메모는 상단에 표시된 사안과 관련하여 수신인의 내부 참고를 위해 작성되었습니다. 본 문서는 **[기준일]** 현재의 관련 법령 및 본문에 기재된 사실·전제에 기초한 검토 결과를 반영합니다. 본 문서는 법률 조사 산출물이며 법률 자문에 해당하지 아니하고, 교부 사실만으로 변호사-의뢰인 관계가 성립하지 아니합니다. 수신인은 관련 관할에 자격을 갖춘 변호사의 독립적 조력을 구하기 전에는 본 메모에 의존하여서는 아니 됩니다. 작성자는 추후 법령·사실관계 변경을 이유로 본 메모를 갱신할 의무를 부담하지 아니합니다.

### 16. 서명·특권·기밀 표기

**AI 생성 초안의 기본 기밀 등급:** *Confidential — AI-Generated Draft* (또는 *Confidential — Internal Draft*), 소형 대문자, 네이비 또는 회색으로 모든 페이지 머리말에 표기합니다.

**미검토 AI 초안에 특권 라벨을 사용하지 마십시오.** 자격을 갖춘 변호사가 전문가 자격으로 작성·검토·채택하지 아니한 문서에 *Attorney Work Product*, *Attorney-Client Communication* 등의 라벨을 붙이는 것은 오인 소지가 있으며, §15.1의 AI 생성 고지와도 모순됩니다.

**특권 라벨 사용이 적절해지는 시점:** (i) 자격을 갖춘 변호사가 실질적으로 검토하고 분석을 본인의 업무 산출물로 채택한 경우, 그리고 (ii) 해당 특권의 실체적 요건이 충족된 경우(예: 소송을 염두에 둔 업무산출물, 변호사-의뢰인 간 법률 자문 목적의 통신)에 한합니다. 이 시점에서는 AI 워크플로우가 아닌 **변호사 본인이 책임을 부담**하며, 기밀 등급을 아래와 같이 상향할 수 있습니다:

- *Privileged & Confidential — Attorney Work Product*, 또는
- *Privileged & Confidential — Attorney-Client Communication*

(해당 법리에 따라). 이 경우 §15.1의 AI 생성 고지는 제거하거나 검토자의 확인 문구로 대체합니다.

**미검토 AI 초안의 기본 표기:** *작성: AI 기반 리서치 워크플로우 — [날짜]* 한 줄만 둡니다. "변호사", "Attorney at Law", 변호사 등록 관할·등록번호, 소속 법무법인명, 변호사가 서명할 형식의 서명란 등 **전문 자격을 시사하는 필드를 기본값으로 포함하지 않습니다**. 이런 필드를 두면 변호사가 작성·검토·채택한 문서처럼 오인될 소지가 있습니다.

**검토자 서명 (선택, 사후 검토 시):** 자격을 갖춘 검토자가 문서를 실질적으로 채택한 경우에 한해, 검토자는 작성자 표기란 하단 또는 그 자리에 **본인에게 실제로 해당하는** 속성으로 자신의 서명란을 직접 추가할 수 있습니다. 이 경우 §15.1의 AI 생성 고지는 제거하거나 이에 맞게 대체합니다.

**버전 표기:** 바닥글 또는 커버노트에 — *Draft v0.3 — 2026-04-18*.

### 17. 타이포그래피 및 페이지 설정

- **페이지:** A4 (210 × 297 mm), 상하좌우 여백 2.5 cm.
- **본문:** 11 pt 세리프 (국문 "맑은 고딕" 또는 "바탕", 영문 Times New Roman·Garamond 등). 줄간격 1.2. 양쪽 정렬 또는 왼쪽 정렬 (기관 관행 준수).
- **제목:** 산세리프 (Arial, Helvetica 등), 네이비 또는 다크차콜.
- **각주:** 9 pt, 본문과 동일 계열, 줄간격 단배.
- **표:** 10 pt, 얇은 테두리, 헤더 행 굵게 + 연한 배경.
- **쪽번호:** 바닥글, 중앙 또는 외곽 정렬, 형식 *Page X of Y*.
- **고립 행 방지:** Widow/Orphan 제어 활성화.
- **기밀 등급 머리말:** 소형 대문자, 네이비 또는 회색 (§16 참조 — AI 초안에는 특권 라벨을 기본값으로 사용하지 않습니다).

### 18. 제출 전 품질 체크리스트

초안을 검토자에게 넘기기 전에:

- [ ] 모든 결론이 §5 확신도 척도 중 하나에 대응됩니다.
- [ ] 주요 결론마다 반대 논거가 있습니다 (§8).
- [ ] 모든 1차 인용을 직접 확보하고 핀포인트 검증하였습니다.
- [ ] 2차 자료를 1차 권위로 제시한 부분이 없습니다.
- [ ] 정의어 사용이 일관되며, 10페이지 이상 메모에는 정의어 일람이 있습니다.
- [ ] AI 생성 고지(상단)와 마감 면책 문구(서명란 인근)가 모두 있습니다.
- [ ] 날짜, 숫자, 통화가 §13을 따릅니다.
- [ ] 특권 적용 시 모든 페이지에 기밀 등급 표기가 있습니다.
- [ ] 머리말·바닥말·쪽번호가 정확합니다.
- [ ] 송부 전 문서 메타데이터(작성자, 마지막 수정자)를 확인하였습니다.

### 19. 모드별 적용 지침

Mode A-D 지침은 기본 스타일 payload가 아니라 선택형 reference입니다. 사용자가 집행 요약, 관할 비교 매트릭스, 집행례/판례 중심 정리, 조문별 해설을 명시적으로 요청한 경우에만 `docs/references/formatting-modes-reference.md`를 로드합니다.

---

*End of style guide.*
