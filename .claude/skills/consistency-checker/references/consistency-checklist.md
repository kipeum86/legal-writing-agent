# Consistency Checklist Reference

## Detailed Check Procedures

### 1. Term Consistency
- Load term registry
- For each defined term, search entire document for usage
- Check: defined term used consistently (not full form after definition)
- Check: no undefined abbreviations
- Check: no term used for multiple meanings

### 2. Cross-Reference Integrity
- Find all internal references ("제N조", "Section N", "위 제N항", "see supra")
- Verify target section exists
- Verify target section number is correct
- Flag orphaned references

### 3. Numbering Continuity
- Korean: 조·항·호·목 sequential
- English: Article/Section/sub-section sequential
- Check: no gaps (e.g., 제1조 → 제3조 missing 제2조)
- Check: no duplicates
- Check: correct hierarchy (항 inside 조, 호 inside 항)

### 4. Party Designation
- Identify all party references
- Check: consistent designation (always "갑" or always "원고", not mixed)
- Check: party defined before first use

### 5. Register Uniformity
- Korean: check all sentence endings against register-guide-kr
- English: check for contractions, colloquialisms
- Flag any register violations

### 6. Placeholder Completeness
- Find all bracket patterns `[...]` in document
- Check: all are in standard placeholder format
- Check: all are tracked in placeholder registry
- Check: no unformatted gaps

### 7. Convention Compliance
- Page setup: margins, font, size
- Numbering system: correct for language/jurisdiction
- Citation format: correct for language/jurisdiction
- Date format: correct for language
- Signature block: correct format

### 8. Section Completeness
- Compare document sections against approved outline
- Check: all sections present
- Check: no empty sections (unless placeholder)
- Check: section order matches outline

### 9. Level B Artifact Completeness (Revision only)
- All modifications reflected in the clean copy, redline diff, and change map
- No silent modifications outside the section-level change map
- Change-map summary counts match the recorded change objects

### 10. Scope Compliance (Revision only)
- Compare modified sections against revision scope from R2
- Verify: no out-of-scope modifications
- Verify: cascade-only sections have only cascading changes
- Verify: preserved sections unchanged
