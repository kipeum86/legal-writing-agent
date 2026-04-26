# Legal Drafter

> Core drafting skill: generates human-quality legal prose with correct register, terminology, and conventions.

## Trigger
- **Drafting Pipeline**: Step D3 (section-by-section drafting)
- **Revision Pipeline**: Step R4 (revision execution, prose generation)

## Required References
- `references/defined-term-rules.md` — canonical definition and term-registry rules
- `references/register-guide-kr.md` — Korean register rules and prohibited patterns
- `references/register-guide-en.md` — English register rules and prohibited patterns
- `references/placeholder-format.md` — canonical placeholder tokens and placeholder-registry schema
- `docs/policies/drafting-scope.md` — authoritative boundary for legal conclusions, risk assessment, recommendations, and certainty language

## Quality Bar
**Output must be indistinguishable from a document drafted by a competent human legal drafting specialist.**
- Natural prose flow — not template-fill or AI-sounding language
- Jurisdiction-appropriate legal idiom
- Correct register throughout (문어체 for Korean; formal English for English)
- Consistent terminology via term registry
- Logical coherence between sections

## Drafting Protocol

### 1. Section-by-Section Sequential Drafting
Draft each section from the approved outline in order:
1. Read the section's requirements from the outline and user instructions
2. Apply the convention set (style guide + house style)
3. Draft the section in natural legal prose
4. Register new defined terms in the term registry
5. Check term consistency against existing registry entries
6. Proceed to next section

### 2. Register Enforcement

#### Korean (문어체)
- Apply `references/register-guide-kr.md`
- Sentence endings: ~한다, ~하여야 한다, ~할 수 있다, ~로 한다, ~에 해당한다
- Advisory/memo: ~합니다 체 permitted when contextually appropriate
- NO colloquial endings: ~거든요, ~잖아요, ~인데요
- NO casual speech patterns
- Use formal connectors: 따라서, 그러므로, 이에, 한편, 다만, 또한

#### English (formal)
- Apply `references/register-guide-en.md`
- "Must" / "shall" for obligations; "may" for permissions
- No contractions
- No colloquialisms
- Active voice preferred; passive acceptable for emphasis
- No first person in formal documents (acceptable in memos)

### 3. Terminology Management
- **First use**: Full name with defined abbreviation
  - Korean: "주식회사 OO(이하 "갑"이라 한다)"
  - English: "XYZ Corporation (the 'Company')"
- **Subsequent uses**: Defined term only
- **Consistency rule**: Same concept = same term throughout. Never vary for style.
- Update `output/term-registries/{document-id}-terms.json` with each new term using the canonical entry shape:
  - `definedTerm`
  - `fullForm`
  - `language`
  - `firstUsedInSection`
  - `definitionText`

### 4. Placeholder Insertion
When information is missing, insert bracketed placeholders:
- `[당사자명]`, `[Insert party name]`
- `[날짜]`, `[Insert date]`
- `[Citation needed: {description}]`
- `[Authority needed: {description}]`
- `[Argument: {issue}]`
- `[Factual basis needed]`
- `[Counsel conclusion needed: {issue}]`
- `[Counsel certainty needed: {issue}]`
- `[Counsel risk assessment needed: {issue}]`

Track all placeholders in `output/placeholders/{document-id}-placeholders.json`

### 5. Citation Handling
- User-provided citations: include verbatim, formatted per convention
- Missing citations: `[Citation needed: {description}]`
- NEVER fabricate or hallucinate citations

### 5.5 Conclusions, Risk, Recommendations, and Certainty
- Apply `docs/policies/drafting-scope.md` before drafting any conclusion, risk statement, recommendation, or certainty wording.
- Include legal conclusions only when they are supplied by the user or an authority packet. Missing conclusion → `[Counsel conclusion needed: {issue}]`.
- Include risk assessment only when it is supplied by the user or an authority packet. Missing risk statement → `[Counsel risk assessment needed: {issue}]`.
- Do not assign your own certainty level. Missing certainty → `[Counsel certainty needed: {issue}]`.
- Administrative next steps may be drafted only when they do not require independent legal judgment.

### 6. Precedent Fidelity
When user provided a precedent document:
- Replicate structure and style closely
- Substitute only specified variables (parties, dates, specifics)
- Do NOT deviate from precedent structure without user confirmation
- Flag any proposed structural deviations

### 7. Long Document Strategy (>30 pages)
1. Draft core substantive sections first
2. Then procedural/boilerplate sections
3. Maintain running term registry throughout
4. Checkpoint after major section groups
5. Re-anchor from manifest + term registry if drift detected

### 8. Self-Correction
- Max 2 attempts per section if quality issues detected
- After 2 attempts: deliver with `[Drafting Gap: {issue}]` flag

## Output
- Complete draft, section by section
- Updated `output/term-registries/{document-id}-terms.json`
- Updated `output/placeholders/{document-id}-placeholders.json`
- Draft content prepared for `/output-formatter`
