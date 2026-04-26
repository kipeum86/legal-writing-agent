# Output Formatter

> Generates final document files, applies formatting, manages versioning.

## Trigger
- **Drafting Pipeline**: Step D5 (output generation), D6 (file save)
- **Revision Pipeline**: Step R6 (output generation), R7 (file save)

## Required References
- `references/page-setup-kr.md` — Korean page and typography defaults
- `references/page-setup-en-us.md` — US English page and typography defaults
- `references/page-setup-en-uk.md` — UK and international English page and typography defaults

## Responsibilities

### 1. Inline Preview & Auto-Save (D5/R6)
- Show the complete document content as inline chat preview
- For revisions: show revision tracking output appropriate to the format
  - `.md`: inline diff markers
  - `.docx` / `.txt`: Level B clean copy, redline diff, and section-level change-map artifacts
- **Auto-save** to the resolved documents directory (`$LEGAL_AGENT_PRIVATE_DIR/output/documents/` when set, otherwise `<repo>/output/documents/`) immediately after preview
- Inform user of saved path (no confirmation needed — previous versions are never overwritten)

### 2. File Generation
Generate the document in the user's chosen format:

| Format | Method |
|---|---|
| `.md` | Direct write — native markdown |
| `.txt` | Direct write — plain text |
| `.docx` | Use `python-docx` to generate formatted .docx (primary method) |
| `.pdf` | Convert from .docx via LibreOffice, or from .md via pandoc |

#### DOCX Read/Write via python-docx
**Reading** (R1 ingestion):
```python
import docx
from tools.security import paths

doc = docx.Document(str(paths.input_dir() / "filename.docx"))
for para in doc.paragraphs:
    # para.style.name, para.text, para.runs
```

**Writing** (D5/R6 output):
```python
from docx import Document
from docx.shared import Pt, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from tools.security import paths

doc = Document()
# Set page size, margins, fonts per convention set
# Add paragraphs with correct styles
doc.save(str(paths.documents_dir() / "filename.docx"))
```

#### PDF Reading
Use Claude Code's native Read tool — supports PDF files directly.

### 3. Formatting Rules

#### Korean Documents
| Parameter | Value |
|---|---|
| Page size | A4 (210mm × 297mm) |
| Margins | Top 20mm, Bottom 15mm, Left 20mm, Right 20mm |
| Body font | 바탕체, 12pt |
| Heading font | 맑은 고딕, 12–16pt |
| Line spacing | 160–200% |

#### English (US) Documents
| Parameter | Value |
|---|---|
| Page size | US Letter (8.5″ × 11″) |
| Margins | 1″ all sides |
| Body font | Times New Roman, 12pt |
| Heading font | Times New Roman or Arial, 12–14pt |
| Line spacing | Double-spaced (briefs), 1.5 (memos) |

#### English (UK/International) Documents
| Parameter | Value |
|---|---|
| Page size | A4 |
| Margins | 2.54cm all sides |
| Body/Heading font | Times New Roman, 12pt |

### 4. File Naming
```
{date}_{type}_{description}_v{N}.{ext}
```
- `date`: YYYYMMDD format
- `type`: advisory, corporate, litigation, regulatory, general
- `description`: brief description in lowercase with hyphens
- `v{N}`: version number, auto-incremented
- `ext`: docx, pdf, md, txt

Examples:
- `20260310_advisory_tax-opinion_v1.docx`
- `20260310_corporate_board-resolution_v2.md`

For revisions:
```
{date}_{type}_{description}_revised_v{N}.{ext}
```
- Revision outputs must include the `_revised_` marker before the version suffix

### 5. Auto-Versioning (D6/R7)
1. Check the resolved documents directory for existing files with same base name
2. Auto-increment version: v1 → v2 → v3
3. **Never overwrite** previous versions
4. Save to the resolved documents directory

### 6. Revision Output (R6)
In addition to the document:
- **Level B only**: Three files:
  - `{name}_clean_v{N}.{ext}` — final clean version
  - `{name}_redline_v{N}.diff` — unified redline diff
  - resolved `change-map.json` under the output base directory — section-level structured change record, auto-versioned if needed
- **Change summary**: Brief list of all changes alongside document

Do not imply that `.docx` native Word tracked changes are supported in Phase 1-8. The `trackingLevel` field in the change map must be `level-b`; it exists for future-proofing.

### 7. Session Checkpoint (D6/R7)
Save session state to the resolved checkpoint path (`$LEGAL_AGENT_PRIVATE_DIR/output/checkpoint.json` when set, otherwise `<repo>/output/checkpoint.json`):
```json
{
  "lastStep": "D6|R7",
  "documentId": "uuid",
  "documentType": "string",
  "manifestPath": "$LEGAL_AGENT_PRIVATE_DIR/output/manifests/{id}-manifest.json",
  "clauseMapPath": "$LEGAL_AGENT_PRIVATE_DIR/output/clause-maps/{id}-clause-map.json",
  "termRegistryPath": "$LEGAL_AGENT_PRIVATE_DIR/output/term-registries/{id}-terms.json",
  "outputPath": "$LEGAL_AGENT_PRIVATE_DIR/output/documents/{filename}",
  "version": 1,
  "timestamp": "ISO 8601"
}
```

## Failure Handling
- Auto-remediate ×1 for formatting issues
- If file generation fails: fall back to .md format and inform user
