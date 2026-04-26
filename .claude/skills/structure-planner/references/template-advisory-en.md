# Template: Advisory (Memorandum) — English

## Use This Template For
- Legal opinion
- Legal review opinion
- Client memorandum
- Internal memorandum
- Legal brief outside court-filing format
- Due diligence report with analytical legal sections

## Support Profile
- Support level: `Conditional`
- A complete opinion requires an authority packet for the rule statements, authorities, and defensible conclusions
- Apply `docs/policies/drafting-scope.md` before filling conclusions, risk assessments, recommendations, or certainty language
- If authority is missing, keep the outline intact and use canonical placeholders such as `[Authority needed: governing statute or leading case]`, `[Citation needed: source for proposition]`, `[Argument: issue to analyze]`, `[Counsel conclusion needed: issue]`, `[Counsel certainty needed: issue]`, and `[Counsel risk assessment needed: issue]`

## Section Tags
- `[B]` = Boilerplate or administrative material
- `[S]` = Substantive content based on user facts or drafting instructions
- `[AP]` = Authority packet required for a fully supported section

## Core Skeleton — Legal Opinion / Client Memorandum

1. `MEMORANDUM` heading `[B]`
   - Use a centered title if the document is formal
   - For a lighter internal memo, the heading may simply be `Memorandum`

2. Header block `[B]`
   - `To: [Recipient]`
   - `From: [Author / Firm / Team]`
   - `Date: [Insert date]`
   - `Re: [Subject]`

3. `1. Questions Presented` `[S]`
   - State each issue as a precise legal question
   - Use one numbered question per issue
   - If the factual predicate is incomplete, note the assumption directly in the question or in the facts section

4. `2. Short Answer / Executive Summary` `[S/AP]`
   - Give a direct answer only when the user supplied that conclusion or the authority packet supports it
   - If the conclusion is missing, use `[Counsel conclusion needed: issue]` instead of drafting a bottom line
   - If certainty is needed but not supplied, use `[Counsel certainty needed: issue]`

5. `3. Facts, Assumptions, and Scope` `[S]`
   - Present only facts material to the analysis
   - Separate confirmed facts from assumptions
   - Identify any issues outside scope

6. `4. Governing Authorities` `[AP]`
   - List the governing statutes, regulations, cases, and interpretive materials
   - Group authorities by issue if that improves readability
   - Use `[Authority needed: ...]` where support is missing

7. `5. Analysis` `[S/AP]`
   - Repeat the following structure for each issue:
     - `A. Issue 1` `[S]`
     - `1. Governing Rule` `[AP]`
     - `2. Application to the Facts` `[S/AP]`
     - `3. Counterarguments / Risks / Uncertainties` `[AP]`
     - `4. Issue Conclusion` `[S/AP]`
   - Use IRAC or CRAC depending on the style selected at D2
   - Keep the issue heading aligned with the wording in `Questions Presented`

8. `6. Overall Conclusion and Recommendations` `[S/AP]`
   - Synthesize only user-supplied or authority-packet-supported issue-level conclusions
   - If an overall conclusion is missing, use `[Counsel conclusion needed: overall conclusion]`
   - Include risk-mitigation recommendations only when supplied by the user or supported by the authority packet
   - Administrative next steps that do not require legal judgment may be included as drafting logistics

9. `7. Qualifications and Limitations` `[B/S]`
   - State reliance on supplied facts
   - Note missing materials, unresolved factual questions, and jurisdictional assumptions
   - Include any distribution or reliance limitations if appropriate

10. `8. Signature / Attribution` `[B]`
    - Identify the author, team, or firm as appropriate
    - A light internal memo may omit a formal signature block

11. `9. Appendices` `[B/S]`
    - Authority table
    - Chronology
    - Source list
    - Risk matrix or diligence schedule when relevant

## Variant Adjustments

### Legal Review Opinion
- Keep the formal memorandum structure
- Emphasize `Questions Presented`, `Short Answer`, and `Qualifications`
- Include an explicit statement of assumptions and unanswered factual questions

### Internal Memo
- Use shorter headings if speed matters: `Issue`, `Facts`, `Analysis`, `Recommendation`
- A concise internal memo may collapse sections 3 and 4 into a single `Background and Authorities` section
- Retain placeholders instead of guessing at law or fact

### Due Diligence Report
- Replace `Questions Presented` with `Review Scope`
- Replace `Analysis` with topic-by-topic diligence sections:
  - `A. Corporate Status`
  - `B. Licensing / Regulatory`
  - `C. Litigation / Disputes`
  - `D. Material Compliance Risks`
- Add `Findings`, `Risk Rating`, and `Recommended Follow-up` subheadings under each topic

## Boilerplate vs Substantive Guidance
- Boilerplate: heading, header block, attribution, appendix labels
- Substantive: questions, short answers, facts, governing authorities, analysis, conclusions, recommendations
- Conditional support warning: do not write definitive legal conclusions, risk ratings, recommendations, or certainty language in sections `4`, `5`, or `6` without user-supplied instructions or authority-packet support

## Drafting Reminders
- Maintain one-to-one correspondence between each question, its short answer, and its analysis subsection
- Use the citation convention chosen by `convention-selector` rather than embedding jurisdiction-specific citation habits here
- Prefer precise, neutral, and reader-oriented headings over generic labels like `Miscellaneous`
