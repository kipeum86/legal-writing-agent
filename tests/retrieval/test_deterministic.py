from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.artifacts import schemas
from tools.retrieval.deterministic import apply_retrieval_to_manifest, retrieve_authority_chunks


ROOT = Path(__file__).resolve().parents[2]


def write_source(
    tmp_path: Path,
    *,
    source_id: str,
    grade: str,
    jurisdiction: str,
    title: str,
    topics: list[str],
    provisions: list[str],
    body: str,
) -> dict[str, str]:
    relative = Path("library") / f"grade-{grade.lower()}" / f"{source_id}.md"
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"source_id: \"{source_id}\"\n"
        f"title_kr: \"{title}\"\n"
        f"source_grade: \"{grade}\"\n"
        f"jurisdiction: \"{jurisdiction}\"\n"
        f"topics: {json.dumps(topics, ensure_ascii=False)}\n"
        f"legal_provisions: {json.dumps(provisions, ensure_ascii=False)}\n"
        "applicable_document_types: [\"advisory\", \"regulatory\"]\n"
        "---\n"
        f"{body}\n",
        encoding="utf-8",
    )
    return {
        "source_id": source_id,
        "path": str(relative),
        "title_kr": title,
        "source_grade": grade,
        "jurisdiction": jurisdiction,
        "topics": topics,
        "legal_provisions": provisions,
    }


def write_registry(tmp_path: Path, sources: list[dict[str, object]]) -> Path:
    registry = tmp_path / "library" / "source-registry.json"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(
        json.dumps(
            {
                "last_updated": "2026-04-26T00:00:00+09:00",
                "total_sources": len(sources),
                "by_grade": {},
                "sources": sources,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return registry


def test_retrieval_ranks_by_grade_jurisdiction_provision_and_topic(tmp_path: Path) -> None:
    sources = [
        write_source(
            tmp_path,
            source_id="a-pipa-article-15",
            grade="A",
            jurisdiction="KR",
            title="개인정보 보호법 제15조",
            topics=["privacy", "consent"],
            provisions=["제15조"],
            body="제15조 개인정보 수집 이용 동의에 관한 공식 법령 텍스트입니다.",
        ),
        write_source(
            tmp_path,
            source_id="b-us-privacy-note",
            grade="B",
            jurisdiction="US",
            title="US Privacy Note",
            topics=["privacy"],
            provisions=["Section 5"],
            body="US practice note about privacy.",
        ),
    ]
    registry = write_registry(tmp_path, sources)

    result = retrieve_authority_chunks(
        registry,
        document_type="advisory",
        jurisdiction="korea",
        topics=("privacy",),
        provisions=("제15조",),
    )

    assert result["sufficiency"]["status"] == "sufficient"
    first = result["chunks"][0]
    assert first["source_id"] == "a-pipa-article-15"
    assert first["chunk_id"] == "a-pipa-article-15#c1"
    assert first["grade"] == "A"
    assert first["jurisdiction"] == "korea"
    assert first["provisions"] == ["제15조"]
    assert first["topics"] == ["consent", "privacy"]
    assert first["charStart"] == 0
    assert first["charEnd"] > first["charStart"]
    assert "provision:제15조" in first["matchReasons"]


def test_conditional_without_authority_packet_enters_skeleton_only(tmp_path: Path) -> None:
    registry = write_registry(tmp_path, [])

    result = retrieve_authority_chunks(
        registry,
        document_type="advisory",
        jurisdiction="korea",
        topics=("privacy",),
        support_level="conditional",
    )
    manifest = schemas.MatterManifest(
        documentType="advisory",
        supportLevel="conditional",
        authorityPacketProvided=True,
        skeletonOnly=False,
    )
    updated = apply_retrieval_to_manifest(manifest, result)

    assert result["sufficiency"]["status"] == "insufficient"
    assert updated["authorityPacketProvided"] is False
    assert updated["skeletonOnly"] is True
    assert updated["authorityChunks"] == []


def test_manifest_records_selected_source_and_chunk_ids(tmp_path: Path) -> None:
    source = write_source(
        tmp_path,
        source_id="a-commerce-act",
        grade="A",
        jurisdiction="KR",
        title="상법 제393조",
        topics=["board", "resolution"],
        provisions=["제393조"],
        body="제393조 이사회 권한에 관한 법령 텍스트입니다.",
    )
    registry = write_registry(tmp_path, [source])
    result = retrieve_authority_chunks(
        registry,
        document_type="regulatory",
        jurisdiction="korea",
        topics=("board",),
        provisions=("제393조",),
        support_level="conditional",
    )
    manifest = schemas.MatterManifest(
        documentType="regulatory",
        supportLevel="conditional",
        authorityPacketProvided=False,
        skeletonOnly=True,
    )

    updated = apply_retrieval_to_manifest(manifest, result)

    assert updated["authorityPacketProvided"] is True
    assert updated["skeletonOnly"] is False
    assert updated["authorityChunks"] == [
        {
            "sourceId": "a-commerce-act",
            "chunkId": "a-commerce-act#c1",
            "sourceGrade": "A",
            "title": "상법 제393조",
            "path": "library/grade-a/a-commerce-act.md",
        }
    ]


def test_chunk_and_total_char_caps_are_applied(tmp_path: Path) -> None:
    source = write_source(
        tmp_path,
        source_id="a-long-source",
        grade="A",
        jurisdiction="KR",
        title="긴 법령 자료",
        topics=["privacy"],
        provisions=["제1조"],
        body=("privacy 제1조 " + "가" * 80 + "\n\n") * 10,
    )
    registry = write_registry(tmp_path, [source])

    result = retrieve_authority_chunks(
        registry,
        document_type="advisory",
        jurisdiction="korea",
        topics=("privacy",),
        provisions=("제1조",),
        chunk_char_cap=120,
        total_char_cap=250,
        max_chunks=5,
    )

    assert len(result["chunks"]) <= 5
    assert all(len(chunk["text"]) <= 120 for chunk in result["chunks"])
    assert result["totalSelectedChars"] <= 250


def test_retrieval_cli_emits_json(tmp_path: Path) -> None:
    source = write_source(
        tmp_path,
        source_id="a-cli-source",
        grade="A",
        jurisdiction="KR",
        title="CLI 소스",
        topics=["privacy"],
        provisions=["제2조"],
        body="제2조 privacy 관련 법령 텍스트입니다.",
    )
    registry = write_registry(tmp_path, [source])

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.retrieval.deterministic",
            "--registry",
            str(registry),
            "--document-type",
            "advisory",
            "--jurisdiction",
            "korea",
            "--topic",
            "privacy",
            "--provision",
            "제2조",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["retrievalMode"] == "deterministic-keyword-tag"
    assert payload["selectedChunkIds"] == ["a-cli-source#c1"]

