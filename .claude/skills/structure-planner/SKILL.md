# Structure Planner

> Generates document outlines from library templates and user instructions; initializes clause maps.

## Trigger
- **Drafting Pipeline**: Step D2 (structure planning, after convention selection)

## Responsibilities

### 1. Template Loading
1. Check `/library/templates/` for a matching template: `{doc-type}-{language}.md`
2. If template exists → use as structural skeleton
3. If no template → generate outline from convention set + user instructions

### 2. Outline Generation
Create a complete document outline with:
- All required sections for the document type
- Section headings in the target language
- Numbering per convention set
- Placeholder markers for substantive content
- Notes on which sections are boilerplate vs. substantive

### 3. Clause Map Initialization
Create `output/clause-maps/{document-id}-clause-map.json`:
```json
{
  "documentId": "{uuid}",
  "sections": [
    {
      "id": "s1",
      "title": "Section title",
      "level": 1,
      "type": "boilerplate|substantive",
      "children": [
        {
          "id": "s1.1",
          "title": "Sub-section title",
          "level": 2,
          "type": "boilerplate|substantive",
          "children": []
        }
      ]
    }
  ]
}
```

### 4. Term Registry Initialization
Create `output/term-registries/{document-id}-terms.json`:
```json
{
  "documentId": "{uuid}",
  "terms": []
}
```

### 5. Present Outline & Proceed
Show the outline briefly, then **immediately proceed to drafting**. No need to wait for explicit approval — user can interrupt if modifications are needed.

Format:
```
## Document Outline — [Document Title]

**Type**: [Document type] | **Language**: [Target language] | **Convention**: [Style guide]

1. [Section 1 title]
   1.1 [Sub-section]
2. [Section 2 title]
   ...

Proceeding to draft. Interrupt if you'd like to modify the outline.
```

### 6. Mid-Draft Outline Revision (D3.5)
When returning from D3.5 for major changes:
1. Present revised outline showing additions/removals
2. Proceed unless user objects
3. Update clause map

## Output
- Document outline (presented to user)
- `output/clause-maps/{document-id}-clause-map.json`
- `output/term-registries/{document-id}-terms.json`
