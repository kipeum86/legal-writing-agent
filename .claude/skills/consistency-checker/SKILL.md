# Consistency Checker

> Performs internal consistency checks and self-review against the 8-item (drafting) or 10-item (revision) checklist.

## Trigger
- **Drafting Pipeline**: Step D4
- **Revision Pipeline**: Step R5

## Required References
- `references/consistency-checklist.md` — expanded checklist procedure
- `tools/validation/runner.py` — release-gate wrapper that produces a single validation report artifact
- `scripts/numbering-validator.py`
- `scripts/cross-reference-checker.py`
- `scripts/register-validator.py`
- `scripts/term-consistency-checker.py`
- `scripts/citation-format-checker.py`

## 8-Item Consistency Checklist (Drafting — D4)

| # | Check | Method | Failure Action |
|---|---|---|---|
| 1 | **Term consistency** | Compare all term usages against term registry | Fix inconsistent usages |
| 2 | **Cross-reference integrity** | Verify all internal references point to existing sections | Fix broken references |
| 3 | **Numbering continuity** | Check sequential numbering per convention | Fix gaps/duplicates |
| 4 | **Party designation consistency** | Verify party references match throughout | Standardize |
| 5 | **Register uniformity** | Check all sentences follow register rules | Fix register violations |
| 6 | **Placeholder completeness** | Verify all placeholders are properly formatted and tracked | Format/track missing ones |
| 7 | **Convention compliance** | Check formatting, citation, structure against convention set | Fix deviations |
| 8 | **Section completeness** | Verify all outline sections are present and substantive | Flag missing sections |

## 10-Item Checklist (Revision — R5)

Items 1–8 above, plus:

| # | Check | Method | Failure Action |
|---|---|---|---|
| 9 | **Tracked changes completeness** | All modifications reflected in change tracking | Add missing tracked changes |
| 10 | **Scope compliance** | Compare changes against clause map — no out-of-scope modifications | Revert out-of-scope changes |

## Self-Review Protocol

After checklist, perform a self-review pass:
1. Re-read the draft against the original user instructions
2. Re-read against the convention set
3. Flag issues as `[Drafting Gap: {issue}]`:
   - Missing definitions
   - Ambiguous language
   - Instruction divergence
   - Unresolved placeholders
   - Logical inconsistencies

**Excluded from self-review** (out of scope):
- Independent legal risk assessment
- Strategy recommendations
- Accuracy of user-provided legal content

## Review Intensity Loop

| Level | Passes | Issues Fixed |
|---|---|---|
| **Light** (가볍게) | 1 pass | Critical only |
| **Standard** (표준) | 2 passes | Critical + Major |
| **Thorough** (꼼꼼하게) | 3 passes | All issues |

### Issue Severity
| Severity | Definition | Examples |
|---|---|---|
| **Critical** | Breaks document usability | Missing required sections, wrong document type structure, broken numbering |
| **Major** | Significantly affects quality | Term inconsistency, register violations, missing cross-references |
| **Minor** | Small quality issues | Formatting irregularities, style preferences, optional improvements |

## Automated Validation Scripts

Run deterministic checks through the release-gate runner whenever a manifest exists:

```bash
python -m tools.validation.runner <draft.md> --manifest <manifest.json> --fail-on-blocking
```

The runner emits one `validation_report` JSON containing normalized findings, severity counts, `blocking`, and `renderAllowed`. Rendering must stop when `blocking` is `true`, unless the user explicitly requests an unsafe preview with validation failures disclosed.

The following scripts provide deterministic checks underneath the runner:

| Script | Check | Usage |
|---|---|---|
| `scripts/numbering-validator.py` | Sequential numbering (조·항·호·목, Article/Section/(a)/(i)), orphan detection, 장·절·관 hierarchy | `python numbering-validator.py <file.md> [-v]` |
| `scripts/cross-reference-checker.py` | Internal cross-references point to existing sections | `python cross-reference-checker.py <file.md>` |
| `scripts/register-validator.py` | Register/formality compliance — Korean 문어체 violations, English contractions, informal language, passive voice, sentence length | `python register-validator.py <file.md>` |
| `scripts/term-consistency-checker.py` | Defined term consistency — usage after definition, undefined abbreviations, unused terms, conflicts | `python term-consistency-checker.py <file.md> [--generate-registry]` |
| `scripts/citation-format-checker.py` | Citation format — Korean 「」 brackets, Bluebook, OSCOLA compliance | `python citation-format-checker.py <file.md> [--jurisdiction korea\|us\|uk\|intl]` |

Run all applicable scripts during D4/R5 through `tools.validation.runner`. Integrate findings into the consistency report and save the JSON validation report artifact.

## Output
- Consistency report (issues found and fixed)
- Script validation results (JSON)
- Updated draft with fixes applied
- Any remaining `[Drafting Gap]` flags for issues not auto-fixed
