# Context Budget Policy

This policy keeps prompt loading deterministic and small. `CLAUDE.md` holds only core routing and safety rules; task-specific style, template, and example material must be loaded through an explicit context plan.

## Loading Rules

| Step | Load | Do Not Load |
|---|---|---|
| D1 routing | core policy, document registry, parameter schema, drafting scope | style guides, templates, long examples |
| D2 style/template | selected style profile, selected template, applicable house style | unrelated language/jurisdiction guides, Mode A-D references unless requested |
| D3 drafting | section outline, term registry, placeholder rules, selected style profile, relevant source chunks | full source corpus, full prior document text |
| D4 validation | validation JSON, relevant draft excerpts, validator references | full style corpus unless a convention failure requires it |
| R1 ingestion | document profile, heading tree, relevant sections | full original document in prompt when parser artifacts suffice |
| Library authority packet | top 5 chunks, about 500 tokens each | whole library files by default |

## Character Budgets

Tokenizers are not assumed to be stable in this runtime. Use character-count budgets until a reliable tokenizer is available.

| Step | Max Injected Characters |
|---|---:|
| D1 | 16,000 |
| D2 | 24,000 |
| D3 | 24,000 |
| D4 | 14,000 |
| R1 | 16,000 |
| R6 | 12,000 |
| library_authority_packet | 15,000 |

## Style Profile Rule

Convention selection must first look for:

```text
.claude/skills/convention-selector/style-profiles/{language}-{jurisdiction}-{documentType}.md
```

If no exact profile exists, fall back to the smallest jurisdiction base guide. Do not load `legal-writing-formatting-guide.md` as a default context payload; it is a broad reference file only.

## Mode Reference Rule

Mode A-D guidance is reference-only. Load `docs/references/formatting-modes-reference.md` only when the user explicitly requests an executive brief, comparative matrix, enforcement/case-law review, or black-letter commentary output.
