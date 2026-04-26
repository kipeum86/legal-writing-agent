from __future__ import annotations

from pathlib import Path

from tools.retrieval.deterministic import retrieve_authority_chunks


ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "architecture" / "adr" / "0002-retrieval-embedding-upgrade.md"


def test_embedding_upgrade_adr_keeps_deterministic_retrieval_as_default() -> None:
    text = ADR.read_text(encoding="utf-8")

    assert "Status: Accepted — do not implement embeddings yet" in text
    assert "Deterministic retrieval is the production default" in text
    assert "recall@5" in text
    assert "LEGAL_AGENT_PRIVATE_DIR" in text
    assert "remote" in text
    assert "user-approved external embedding provider" in text


def test_retrieval_mvp_reports_deterministic_mode_without_embedding_fields(tmp_path: Path) -> None:
    registry = tmp_path / "source-registry.json"
    registry.write_text(
        '{"last_updated": null, "total_sources": 0, "by_grade": {}, "sources": []}',
        encoding="utf-8",
    )

    result = retrieve_authority_chunks(
        registry,
        document_type="advisory",
        jurisdiction="korea",
        topics=("privacy",),
    )

    assert result["retrievalMode"] == "deterministic-keyword-tag"
    assert "embeddingModel" not in result
    assert "vectorIndexPath" not in result

