# ADR 0001: Runtime Constraints for the Pipeline Redesign

Date: 2026-04-25

Status: Accepted for Phase 1-8 planning

## Context

The engineering improvement plan depends on several runtime assumptions:

- whether a single workflow can use cheaper models for routing and stronger models for drafting;
- whether prompt/style references can be lazy-loaded enough to reduce context;
- whether preview length can be measured by tokenizer count;
- whether native Word tracked changes can be supported safely;
- whether generated artifacts should reuse the existing private path resolver.

The repository currently runs as a Claude Code-oriented agent project, with `CLAUDE.md`, `.claude/skills/**`, local Python scripts, and security utilities. There is no executable pipeline controller yet.

## Decisions

### 1. Model Routing

Phase 1-8 will not depend on per-step model swapping.

The router and context builder should be deterministic where possible. If model output is used for classification, it must be treated as schema-bound data and validated before downstream use. Multi-model or subagent orchestration can be revisited after the single-pipeline artifact contract exists.

### 2. Lazy Loading

The redesign will reduce always-loaded policy text first, then split long style content into reference files. It will not assume that Claude Code can perfectly enforce token budgets internally.

Practical implication: `CLAUDE.md` should hold only core policy and routing rules. Large style content should live in selected references loaded by the relevant step.

### 3. Preview Length Measurement

The first implementation will use character-count thresholds by language. Tokenizer-based thresholds are optional and may be added later if a stable tokenizer is available in the runtime.

Initial thresholds:

| Language | Short | Medium | Long |
|---|---:|---:|---:|
| Korean | <= 4,000 chars | 4,001-16,000 chars | > 16,000 chars |
| English | <= 8,000 chars | 8,001-32,000 chars | > 32,000 chars |

### 4. Native Word Tracked Changes

Native Word tracked changes are not part of the Phase 1-8 product promise.

`python-docx` does not provide a stable high-level API for Word tracked changes. Supporting true `w:ins` / `w:del` OOXML would require a separate implementation and compatibility testing. Phase 1-8 will officially support Level B revision artifacts only:

- clean copy;
- redline diff;
- structured change map.

### 5. Artifact Paths

New artifact code must reuse `tools.security.paths` and the existing `LEGAL_AGENT_PRIVATE_DIR` behavior. It must not reimplement path resolution independently.

### 6. Security Boundary

New context and artifact modules must integrate the existing trust-boundary utilities:

- `tools/security/sanitizer.py`
- `tools/security/ingest_gate.py`
- `tools/security/fetch_gate.py`
- `docs/security/trust-boundaries.md`

Artifacts that store untrusted or derived-source content must record sanitizer metadata when available.

## Consequences

- The first execution slice stays small and deterministic.
- Token-efficiency work focuses on reducing and splitting prompt content, not model-tier routing.
- Revision output will be honest about Level B support and will not imply native DOCX tracked changes.
- Artifact storage will remain compatible with existing private work-product handling.

## Revisit Triggers

Revisit this ADR if:

- a stable multi-model pipeline wrapper is added;
- tokenizer access becomes reliable in CI and runtime;
- a tested OOXML tracked-changes implementation is introduced;
- the project moves away from Claude Code conventions to a standalone service runtime.
