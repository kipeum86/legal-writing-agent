# Parameter Schema Reference

Scope boundary: `docs/policies/drafting-scope.md` controls legal conclusions, risk assessment, recommendations, certainty language, and safe vs unsafe inference recorded in this schema.

## Matter Manifest Schema

```json
{
  "documentId": "string (UUID v4)",
  "documentType": "enum: advisory | corporate | litigation | regulatory | general",
  "supportLevel": "enum: full | conditional",
  "targetLanguage": "enum: ko | en",
  "jurisdiction": "enum: korea | us | uk | international | string",
  "governingLaw": "string (description of applicable law)",
  "parties": [
    {
      "role": "string (e.g., '갑', '을', 'Plaintiff', 'Defendant')",
      "name": "string",
      "designation": "string (how referred to in document)"
    }
  ],
  "reviewIntensity": "enum: light | standard | thorough",
  "outputFormat": "enum: docx | pdf | md | txt",
  "houseStyle": "string | null",
  "authorityPacketProvided": "boolean",
  "skeletonOnly": "boolean",
  "authorityChunks": [
    {
      "sourceId": "string",
      "chunkId": "string",
      "sourceGrade": "A | B | C",
      "title": "string",
      "path": "string"
    }
  ],
  "safeInference": [
    {
      "field": "string",
      "value": "string",
      "basis": "string (user instruction or non-substantive contextual signal)"
    }
  ],
  "unsafeInference": [
    {
      "issue": "string",
      "resolution": "enum: placeholder | clarification_required",
      "placeholder": "string | null"
    }
  ],
  "pageSize": "enum: a4 | us-letter",
  "createdAt": "string (ISO 8601)",
  "updatedAt": "string (ISO 8601)",
  "step": "string (current pipeline step)",
  "sessionContext": {
    "priorDocumentId": "string | null",
    "inheritedTerms": "boolean",
    "inheritedParties": "boolean"
  }
}
```

## Default Value Policy

### May Default (non-substantive)
| Parameter | Default |
|---|---|
| Page size | A4 (Korean), US Letter (US English), A4 (UK/intl English) |
| Numbering system | Per convention set |
| Heading depth | Per document type template |
| File format | .docx |
| Review intensity | Standard |
| Font | Per style guide |

### Never Default (substantive)
| Parameter | Action if missing |
|---|---|
| Governing law | Infer from context if reasonably clear; ask only if genuinely ambiguous and the answer would materially change the output |
| Claims / defenses | Placeholder |
| Applicable statutes | Placeholder |
| Regulatory requirements | Placeholder |
| Factual basis | Placeholder |
| Legal conclusions | `[Counsel conclusion needed: {issue}]` |
| Risk assessment | `[Counsel risk assessment needed: {issue}]` |
| Certainty level | `[Counsel certainty needed: {issue}]` |
| Strategic recommendations | Placeholder unless user-supplied and within drafting scope |

### Skeleton-Only Rule for Conditional Documents
- If `documentType` is `advisory`, `litigation`, `regulatory`, or a conditional Corporate subtype and `authorityPacketProvided` is `false`, set `skeletonOnly` to `true`
- When deterministic retrieval supplies a sufficient authority packet, set `authorityPacketProvided` to `true`, set `skeletonOnly` to `false`, and record selected source/chunk IDs in `authorityChunks`
- In skeleton-only mode, preserve structure and boilerplate, but use substantive placeholders instead of defaulting legal analysis
- Record non-substantive defaults in `safeInference`
- Record missing legal substance in `unsafeInference`, including the placeholder used or whether a clarification is required

### Corporate Subtype Resolution
- The manifest still stores `supportLevel` as `full` or `conditional`.
- Resolve mixed Corporate documents before writing the manifest.
- Simple board resolutions and simple shareholders meeting minutes resolve to `full`.
- Articles/bylaws, powers of attorney, proxies, internal regulations, company policies, and organizational regulations resolve to `conditional` unless the user supplies enough clause-level instructions to treat the task as template-only drafting.
