# Request Interpreter

> Parses user requests, classifies document types, checks scope, resolves parameters, and loads house styles.

## Trigger
- **Drafting Pipeline**: Step D1
- **Revision Pipeline**: Step R1

## Responsibilities

### 1. Scope Check
First, determine if the request is in scope:
- **In scope**: Non-contract legal document drafting or revision
- **Out of scope**: Contract drafting/review, document audit, legal advice, legal research
- If out of scope → respond: *"This is outside my scope. I handle non-contract legal document drafting and revision."*

### 2. Document Type Classification
Classify the request into one of five categories:

| # | Category | Support Level | Authority Packet Required? |
|---|----------|:---:|:---:|
| 1 | **Advisory** (의견서/메모) | Conditional | Yes |
| 2 | **Corporate** (기업문서) | Full | No |
| 3 | **Litigation** (소송문서) | Conditional | Yes |
| 4 | **Regulatory** (규제문서) | Conditional | Yes |
| 5 | **General Legal** (기타 법률문서) | Full | No |

For unlisted document types: identify closest category, inherit support level, confirm with user.

### 3. Parameter Extraction
Extract or infer from user instructions:
- **Document type** and **support level**
- **Target language**: defaults to language of user instructions; for revision, defaults to input document language
- **Governing law / jurisdiction**: Korea, US, UK, international, or other
- **Parties** (if applicable)
- **Review intensity**: Light / Standard (default) / Thorough
- **Output format**: .docx (recommended default), .pdf, .md, .txt
- **House style**: from `/library/house-styles/`

### 4. Support Level Gate
For **Conditional** document types (Advisory, Litigation, Regulatory):
- Check if user provided an **authority packet** (statutes, case citations, regulations, issue lists, factual chronologies, court rules, agency forms)
- If authority packet present → proceed normally
- If missing → offer skeleton-only mode: *"This document type requires an authority packet (applicable laws, case citations, factual basis) for substantive content. Would you like me to generate a skeleton draft with placeholders?"*

### 5. House Style Loading
- Scan `/library/house-styles/`
- If one style exists → auto-apply and inform user
- If multiple → ask user to select
- If none → use base convention defaults

### 6. Clarification Protocol
- **Infer aggressively** — only ask when genuinely ambiguous and the answer would change the output significantly
- Maximum 3 questions total, 1 round preferred
- If enough context exists to make a reasonable judgment → proceed and state your assumptions
- Substantive gaps → placeholder (don't ask, just mark)
- Governing law → infer from document language, parties, and context; only ask if truly ambiguous

### 7. Output
Save resolved parameters to `output/manifests/{document-id}-manifest.json`:
```json
{
  "documentId": "{uuid}",
  "documentType": "advisory|corporate|litigation|regulatory|general",
  "supportLevel": "full|conditional",
  "targetLanguage": "ko|en",
  "jurisdiction": "korea|us|uk|international|{other}",
  "governingLaw": "{description}",
  "parties": [],
  "reviewIntensity": "light|standard|thorough",
  "outputFormat": "docx|pdf|md|txt",
  "houseStyle": "{style-name}|null",
  "authorityPacketProvided": true|false,
  "skeletonOnly": false,
  "createdAt": "{ISO datetime}",
  "step": "D1"
}
```

### 8. For Revision (R1): Document Ingestion
When an existing document is provided for revision:
1. Read the document from `/input/` folder or from a user-specified path
2. Parse by format:
   - `.docx`: Use `python-docx` to extract paragraphs, tables, styles, and structure
   - `.pdf`: Use Claude Code's native PDF reading capability (Read tool)
   - `.md` / `.txt`: Read directly
3. Extract document structure (headings, sections, numbering)
4. Identify document type, language, jurisdiction, and conventions
5. Build term inventory from existing document
6. Extract clause map with stable section IDs
7. Save document profile to manifest

If no document is found in `/input/`, ask the user to place the file there.

## Failure Handling
- `.docx` parsing fails → try `python-docx`; if still fails → ask for `.md` or `.txt`
- `.pdf` complex layout → inform user that `.docx` gives better results
- Document type unclear → infer from content and proceed (inform user of inference)
