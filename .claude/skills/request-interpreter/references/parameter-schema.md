# Parameter Schema Reference

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
| Legal conclusions | Placeholder |

### Skeleton-Only Rule for Conditional Documents
- If `documentType` is `advisory`, `litigation`, or `regulatory` and `authorityPacketProvided` is `false`, set `skeletonOnly` to `true`
- In skeleton-only mode, preserve structure and boilerplate, but use substantive placeholders instead of defaulting legal analysis
