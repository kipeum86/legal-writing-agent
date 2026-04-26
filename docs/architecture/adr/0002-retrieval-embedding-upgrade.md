# ADR 0002: Retrieval Embedding Upgrade Evaluation

Date: 2026-04-26

Status: Accepted — do not implement embeddings yet

## Context

Phase 7a added deterministic retrieval using `library/source-registry.json`, Markdown frontmatter, provisions, topics, jurisdiction, document type, and source grade. Phase 7b asks whether embedding retrieval should replace or augment that MVP.

The core product constraint is confidentiality. Library material can include client work product, legal authorities selected for a matter, or internal house knowledge. A remote embedding API would send source text outside the local workspace unless a user explicitly provisions and approves that flow.

## Current Candidate Costs

Official OpenAI pricing, checked on 2026-04-26:

| Candidate | Cost | Batch Cost | Notes |
|---|---:|---:|---|
| `text-embedding-3-small` | USD 0.02 / 1M input tokens | USD 0.01 / 1M input tokens | Lower-cost candidate |
| `text-embedding-3-large` | USD 0.13 / 1M input tokens | USD 0.065 / 1M input tokens | Higher multilingual/search quality candidate |

Sources:

- OpenAI pricing: <https://platform.openai.com/docs/pricing/>
- OpenAI embeddings guide: <https://platform.openai.com/docs/guides/embeddings>

Because prices and model availability can change, these figures are not hard-coded into the product.

## Current Baseline

Deterministic retrieval is the production default for Phase 1-8.

| Metric | Current Deterministic MVP |
|---|---:|
| External API cost | USD 0 |
| External text disclosure | None |
| Local index storage | Not required beyond `library/source-registry.json` |
| Current retrieval test cases | 5/5 passing |
| Authority packet sufficiency behavior | Implemented |
| Manifest source/chunk recording | Implemented |

The current repo has no representative retrieval benchmark large enough to prove an embedding quality gain. Adding embeddings now would increase privacy and maintenance burden without measured product benefit.

## Decision

Do not implement embedding retrieval in Phase 1-8. Keep deterministic retrieval as the default and only revisit embeddings when all of the following are true:

1. A public or synthetic benchmark has at least 30 queries across Korean, US, UK, and international materials.
2. Deterministic retrieval underperforms a target threshold, such as recall@5 below 0.85 or materially poor precision on provision/topic queries.
3. An embedding prototype improves recall@5 by at least 0.10 absolute over deterministic retrieval.
4. Confidentiality mode is explicit:
   - `local`: no external API; local embedding model and local vector index only.
   - `remote`: user-approved external embedding provider, with source redaction or matter-level consent.
5. Index storage uses `LEGAL_AGENT_PRIVATE_DIR` and never writes vectors into the repo.

## Required Design If Revisited

If embeddings are later implemented:

- Store indexes under `$LEGAL_AGENT_PRIVATE_DIR/output/retrieval-index/`.
- Record `embeddingProvider`, `embeddingModel`, `indexVersion`, `sourceId`, `chunkId`, and source hash.
- Keep deterministic metadata filters first: jurisdiction, source grade, document type, and provision.
- Use embeddings only as a reranker or fallback, not as the sole authority selector.
- Add a rebuild command that can delete and regenerate the local index deterministically.
- Add tests proving no vectors or source text are written to tracked repo paths.

## Consequences

- Phase 8 remains executable without network access or external provider configuration.
- Confidentiality remains simple: retrieval reads local Markdown and emits bounded chunks.
- Future embedding work has clear quality, cost, privacy, and storage gates.

