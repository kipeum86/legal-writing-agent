# Revision Scope Rules

## Core Principle
**Modify what is requested, plus required convention and integrity fixes already brought into scope by the pipeline.** Untouched sections maintain canonical clause identity.

## Scope Classification

### Modify
- Sections explicitly referenced in user's revision instructions
- Content changes: rewording, restructuring, adding, removing
- Full convention compliance applied to modified sections
- Convention issues already identified at R3 when the user did not expressly opt out

### Preserve
- Sections NOT referenced in revision instructions
- Text and structural nesting unchanged
- No "improvements" or "cleanup" without request
- OOXML metadata changes permitted

### Cascade-Only
- Sections affected by changes elsewhere but not directly modified
- Allowed cascading changes:
  - Numbering updates (if sections added/removed)
  - Cross-reference updates (if referenced sections changed)
  - Defined term updates (if terminology changed)
  - Table of contents updates
  - Convention corrections in nearby text when needed to keep the revised document internally consistent with R3 selections
- NOT allowed:
  - Substantive rewording
  - Style improvements outside the revision scope
  - New convention cleanup unrelated to requested changes if the user expressly limited scope to requested edits only

## Scope Boundary Examples

| User instruction | Scope |
|---|---|
| "제3조 수정해줘" | Modify: §3 only. Cascade: renumbering if needed. Preserve: all other sections. |
| "결론 부분 다시 써줘" | Modify: conclusion section. Cascade: cross-refs. Preserve: all other sections. |
| "전체적으로 문어체 통일해줘" | Modify: all sections (register change). This is a global change. |
| "원고 주장 부분 보강해줘" | Modify: plaintiff's argument sections. Cascade: cross-refs. Preserve: facts, other sections. |

## Convention Issues in Original Document
- Detected at R3, presented to user with three options
- Option 1: Fix alongside → convention fixes added to scope
- Option 2: Only requested → convention issues ignored only if the user expressly chooses this narrower scope
- Option 3: Show full list → inform then user decides
- Default behavior if no narrower choice is made: treat convention issues as part of the revision scope and fix them alongside requested changes
