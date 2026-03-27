# Document Reviser

> Handles revision scope enforcement, change tracking, and preservation of untouched sections.

## Trigger
- **Revision Pipeline**: Steps R2 (scope determination), R4 (revision execution)

## Required References
- `references/revision-scope-rules.md` — canonical scope-boundary, preserve/cascade rules, and convention-fix handling

## Responsibilities

### 1. Revision Scope Determination (R2)
1. Map user's revision instructions to specific sections in the clause map
2. Classify each section as: **modify**, **preserve**, or **cascade-only**
   - **Modify**: Explicitly requested changes
   - **Preserve**: Untouched; canonical clause identity maintained
   - **Cascade-only**: Not directly modified, but requires cascading fixes (numbering, cross-references, term consistency)
3. Define clear scope boundary
4. If ambiguous, clarify with user (≤3 questions)

### 2. Revision Execution (R4)
Execute revisions within the defined scope:

#### Change Tracking
| Format | Method |
|---|---|
| `.docx` Level A | Native Word tracked changes (when technically validated) |
| `.docx` Level B (fallback) | Redline document + clean copy + `output/change-map.json` |
| `.md` | Inline diff markers: `~~deleted text~~` / `**inserted text**` |
| `.pdf` | Not recommended for revision — suggest converting to `.docx` |

#### Preservation Principle
- **Untouched sections**: Canonical clause identity — text + structural nesting unchanged per clause-map stable IDs
- OOXML metadata changes permitted (they don't affect content)
- Do NOT improve, rephrase, or restructure sections that are not in the revision scope

#### Cascading Changes
For sections marked cascade-only:
- Update numbering if sections were added/removed
- Update cross-references if referenced sections changed
- Update defined terms if terminology changed
- Do NOT make substantive changes
- If R3 identified convention issues, include those fixes by default unless the user expressly limited the revision to requested changes only

### 3. Change Map (Level B)
When using Level B tracking, generate `output/change-map.json`:
```json
{
  "documentId": "uuid",
  "changes": [
    {
      "id": "c1",
      "sectionId": "s3.2",
      "type": "insert|delete|modify",
      "original": "original text",
      "revised": "revised text",
      "reason": "per user instruction: [description]"
    }
  ]
}
```

### 4. Self-Correction
- Max 2 attempts per section
- After 2 attempts: deliver with `[Drafting Gap: {issue}]` flag

## Output
- Revised document with Level A tracked changes when available, otherwise Level B redline outputs
- Updated clause map
- Change map (Level B)
- Updated term registry
