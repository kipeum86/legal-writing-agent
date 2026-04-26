# ADR 0003: Phase 0.5 Runtime Measurements and Pipeline Decisions

Date: 2026-04-26

Status: Accepted

## Context

Phase 0.5 required measurement of implementation constraints before treating the redesign plan as executable. The relevant questions were:

- whether Claude Code lazy loading and this repository's skill layout can keep context small;
- whether `CLAUDE.md` and skill `SKILL.md` files are small and scoped enough for auto-load behavior;
- whether pipeline steps can rely on cheaper models or subagents;
- whether preview length can use a tokenizer;
- whether native Word tracked changes can be supported with the current DOCX stack;
- whether the existing `ko-korea-opinion` profile produces acceptable baseline output.

ADR 0001 set the planning direction. This ADR records the Phase 0.5 measurements that confirm or constrain that direction.

## Measurements

### Lazy-Load and Context Budget

Measured with `python3 -m tools.context.budget` on 2026-04-26:

| Plan | Estimated Characters | Budget | Result |
|---|---:|---:|---|
| D1 Korean advisory | 15,128 | 16,000 | Within budget |
| D2 Korean advisory | 22,781 | 24,000 | Within budget |
| D3 Korean advisory | 18,141 | 24,000 | Within budget |

Selected character counts from local files:

| File | Characters |
|---|---:|
| `CLAUDE.md` | 24,100 |
| `legal-writing-formatting-guide.md` | 29,304 |
| `docs/_private/ko-legal-opinion-style-guide.md` | 15,199 |
| `.claude/skills/convention-selector/style-profiles/ko-korea-advisory.md` | 1,292 |
| `.claude/skills/structure-planner/references/template-advisory-kr.md` | 4,203 |

`CLAUDE.md` remains substantial, so lazy loading cannot rely on runtime convention alone. The enforceable mechanism is the deterministic context plan in `tools.context.budget`, plus tests that selected plans do not include broad references such as `legal-writing-formatting-guide.md` by default.

`.claude/settings.json` permits access to selected skill reference directories, but it does not by itself prove that all references are auto-loaded. Skill `SKILL.md` files must therefore continue to say exactly when to run `tools.context.budget` and which returned references to load.

### Model Swap and Subagent Feasibility

The current executable path is a local single-process CLI:

- `python -m tools.pipeline draft --request request.json`
- `python -m tools.pipeline revise --input input.docx --instructions instructions.md`

There is no provider abstraction, model routing configuration, step-level model parameter, or external orchestration wrapper in the repository. The router, context builder, validation runner, renderer, retrieval, and revision artifact writer are deterministic Python modules.

Subagent orchestration would add a second state boundary on top of the artifact boundary. With the current codebase, it would not reduce token use unless a separate orchestration runtime can assign different models and pass only typed artifacts between agents.

### Tokenizer Availability

Checked with `importlib.util.find_spec` on 2026-04-26:

| Package | Available |
|---|:---:|
| `tiktoken` | No |
| `tokenizers` | No |

Character-count thresholds are therefore the only dependency-free preview measurement available in the current runtime.

### DOCX Tracked Changes

Checked on 2026-04-26:

| Component | Result |
|---|---|
| `python-docx` | Available, version 1.2.0 |
| `lxml` | Available |
| `python-docx` document revision/tracking API | Not present |
| Paragraph-level insert/delete/tracked-change API | Not present |

`lxml` can edit OOXML, but native Word tracked changes require manual `w:ins`, `w:del`, author/date metadata, relationships, and round-trip compatibility tests in Word/LibreOffice. That is a separate feature, not an incremental change to the current renderer.

### `ko-korea-opinion` Baseline

The current renderer selects `ko-korea-opinion` for Korean advisory documents. A generated DOCX from `tests/fixtures/public/ko_advisory_no_authority/input.md` confirmed:

- config key: `ko-korea-opinion`;
- heading styles are applied to the title and numbered headings;
- classification header is rendered when supplied;
- page footer contains a `PAGE` field;
- skeleton placeholders are preserved.

Current limitation: this verifies formatting and skeleton safety, not substantive output quality. The style profile is compact and useful for routing, but high-quality Korean advisory prose still depends on selected template content, the optional private style supplement, and authority-packet availability.

## Decisions

### 1. Router Architecture

Use a deterministic single-pipeline router for Phase 1-8. Do not introduce subagents or step-level model routing until there is a dedicated orchestration wrapper with typed artifact handoff and measurable token/cost benefit.

Implementation consequence: keep request classification, support-level resolution, retrieval selection, and context planning in deterministic code where possible. Any model-generated classification must be schema-bound and validated before downstream use.

### 2. Preview Length Measurement

Use character-count thresholds, not tokenizer counts.

Implementation consequence: `docs/policies/context-budget.md` remains authoritative for character budgets. A tokenizer may be added only if the dependency is pinned, available in CI/runtime, and covered by tests.

### 3. Revision Tracking Promise

Keep Level A native Word tracked changes outside the Phase 1-8 product promise.

Implementation consequence: official revision output remains Level B only: clean copy, redline diff, and section-level `change-map.json`. Native tracked changes may be revisited only with a dedicated OOXML implementation and round-trip compatibility tests.

### 4. Lazy-Load Strategy

Lazy loading is useful only when enforced through explicit context plans. Do not assume Claude Code auto-load behavior is sufficient to control token cost.

Implementation consequence: skills must keep large references out of `SKILL.md`, call `tools.context.budget` before loading style/template content, and keep tests that fail if broad guides or unrelated style packs are included by default.

## Follow-Up Gates

Revisit these decisions only if one of the following happens:

- a model-provider wrapper is added with per-step model selection and cost logging;
- a subagent runtime can pass typed artifacts without re-injecting full prompt state;
- `tiktoken` or another tokenizer is pinned and available in CI;
- a native tracked-changes OOXML prototype passes Word/LibreOffice round-trip tests;
- Korean advisory output receives a larger public/synthetic quality benchmark beyond the current rendering baseline.
