# Documentation Map

This directory is organized by document purpose:

| Directory | Purpose |
|---|---|
| `en/` | English user-facing docs, including the how-to guide and disclaimer. |
| `ko/` | Korean user-facing docs, including the localized README, how-to guide, and disclaimer. |
| `guides/` | Broad authoring and formatting guides that should be loaded deliberately. |
| `references/` | Optional quick references and mode-specific reference material. |
| `policies/` | Agent policy controls, including context budget and drafting scope. |
| `security/` | Trust boundary and security documentation. |
| `architecture/adr/` | Architecture decision records. |
| `examples/` | Public example outputs and behavior fixtures. |
| `_private/` | Opaque local-only references; filenames other than tracked stubs are intentionally ignored. |

Current guide/reference locations:

- `guides/legal-writing-formatting-guide.md`
- `references/formatting-conventions-reference.md`
- `references/ko/formatting-conventions-reference.md`
- `references/formatting-modes-reference.md`

Quality guardrail:

- Internal Markdown links in tracked public docs are checked by `tests/docs/test_markdown_links.py`.
