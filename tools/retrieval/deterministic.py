"""Keyword and metadata based retrieval for authority packets.

This MVP intentionally avoids embeddings. It ranks library sources using the
ingest registry, frontmatter metadata, and deterministic provision/topic
matching, then returns bounded chunks for prompt injection.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable, Sequence

from tools.artifacts import schemas


SCHEMA_VERSION = "1.0"
DEFAULT_MAX_CHUNKS = 5
DEFAULT_CHUNK_CHAR_CAP = 2_500
DEFAULT_TOTAL_CHAR_CAP = 15_000
CONDITIONAL_DOCUMENT_TYPES = {"advisory", "litigation", "regulatory"}
GRADE_WEIGHT = {"A": 30, "B": 20, "C": 10}


def retrieve_authority_chunks(
    registry_path: str | Path,
    *,
    document_type: str,
    jurisdiction: str,
    topics: Sequence[str] = (),
    provisions: Sequence[str] = (),
    support_level: str | None = None,
    max_chunks: int = DEFAULT_MAX_CHUNKS,
    chunk_char_cap: int = DEFAULT_CHUNK_CHAR_CAP,
    total_char_cap: int = DEFAULT_TOTAL_CHAR_CAP,
) -> dict[str, Any]:
    registry_file = Path(registry_path)
    registry = validate_source_registry(_read_json(registry_file))
    query = {
        "documentType": _normalize_document_type(document_type),
        "jurisdiction": _normalize_jurisdiction(jurisdiction),
        "topics": sorted({_normalize_token(item) for item in topics if item}),
        "provisions": sorted({_normalize_token(item) for item in provisions if item}),
        "supportLevel": support_level or _default_support_level(document_type),
    }

    candidates: list[dict[str, Any]] = []
    for source in registry["sources"]:
        source_path = _resolve_source_path(source["path"], registry_file)
        if not source_path.exists():
            continue
        text = source_path.read_text(encoding="utf-8")
        frontmatter, body = _split_frontmatter(text)
        metadata = _source_metadata(source, frontmatter)
        for chunk in _chunk_source(metadata, body, chunk_char_cap=chunk_char_cap):
            score, reasons, relevance_score = _score_chunk(chunk, query)
            if score <= 0:
                continue
            if (query["topics"] or query["provisions"]) and relevance_score <= 0:
                continue
            chunk["score"] = score
            chunk["matchReasons"] = reasons
            candidates.append(chunk)

    candidates.sort(
        key=lambda item: (
            -item["score"],
            -GRADE_WEIGHT.get(item["grade"], 0),
            item["source_id"],
            item["chunk_id"],
        )
    )
    selected = _cap_chunks(candidates, max_chunks=max_chunks, total_char_cap=total_char_cap)
    sufficiency = _sufficiency(query, selected)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "retrievalMode": "deterministic-keyword-tag",
        "query": query,
        "maxChunks": max_chunks,
        "chunkCharCap": chunk_char_cap,
        "totalCharCap": total_char_cap,
        "selectedChunkIds": [chunk["chunk_id"] for chunk in selected],
        "sourceIds": sorted({chunk["source_id"] for chunk in selected}),
        "totalSelectedChars": sum(len(chunk["text"]) for chunk in selected),
        "chunks": selected,
        "sufficiency": sufficiency,
    }


def validate_source_registry(registry: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(registry, dict):
        raise ValueError("source registry must be a JSON object")
    sources = registry.get("sources")
    if not isinstance(sources, list):
        raise ValueError("source registry must contain a sources list")
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            raise ValueError(f"sources[{index}] must be an object")
        for field_name in ("source_id", "path", "source_grade"):
            if not source.get(field_name):
                raise ValueError(f"sources[{index}].{field_name} is required")
        source["source_grade"] = str(source["source_grade"]).upper()
        if source["source_grade"] not in GRADE_WEIGHT:
            raise ValueError(f"sources[{index}].source_grade must be A, B, or C")
    if "total_sources" in registry and registry["total_sources"] != len(sources):
        raise ValueError("source registry total_sources does not match sources length")
    return registry


def apply_retrieval_to_manifest(manifest: Any, retrieval: dict[str, Any]) -> dict[str, Any]:
    payload = schemas.artifact_to_payload(manifest)
    sufficiency = retrieval["sufficiency"]
    payload["authorityPacketProvided"] = bool(sufficiency["authorityPacketProvided"])
    if payload.get("supportLevel") == "conditional":
        payload["skeletonOnly"] = bool(sufficiency["skeletonOnly"])
    payload["authorityChunks"] = [
        {
            "sourceId": chunk["source_id"],
            "chunkId": chunk["chunk_id"],
            "sourceGrade": chunk["grade"],
            "title": chunk["title"],
            "path": chunk["path"],
        }
        for chunk in retrieval.get("chunks", [])
    ]
    return schemas.validate_artifact(payload, expected_type="manifest")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"last_updated": None, "total_sources": 0, "by_grade": {}, "sources": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    try:
        _, raw_frontmatter, body = text.split("---", 2)
    except ValueError:
        return {}, text
    return _parse_frontmatter(raw_frontmatter), body.lstrip("\n")


def _parse_frontmatter(raw: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = _parse_frontmatter_value(value.strip())
    return metadata


def _parse_frontmatter_value(value: str) -> Any:
    if not value:
        return ""
    if value.startswith("[") and value.endswith("]"):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return [item.strip().strip('"').strip("'") for item in value.strip("[]").split(",") if item.strip()]
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    return value


def _source_metadata(source: dict[str, Any], frontmatter: dict[str, Any]) -> dict[str, Any]:
    title = (
        source.get("title_kr")
        or source.get("title_en")
        or frontmatter.get("title_kr")
        or frontmatter.get("title_en")
        or source["source_id"]
    )
    topics = _list_value(source.get("topics") or frontmatter.get("topics"))
    keywords = _list_value(source.get("keywords") or frontmatter.get("keywords"))
    provisions = _list_value(source.get("legal_provisions") or frontmatter.get("legal_provisions"))
    document_types = _list_value(
        source.get("applicable_document_types")
        or frontmatter.get("applicable_document_types")
        or source.get("document_types")
        or frontmatter.get("document_types")
    )
    return {
        "source_id": source["source_id"],
        "path": source["path"],
        "title": str(title),
        "grade": str(source.get("source_grade") or frontmatter.get("source_grade") or "C").upper(),
        "jurisdiction": _normalize_jurisdiction(str(source.get("jurisdiction") or frontmatter.get("jurisdiction") or "")),
        "documentTypes": [_normalize_document_type(item) for item in document_types],
        "topics": sorted({_normalize_token(item) for item in [*topics, *keywords] if item}),
        "provisions": sorted({_normalize_token(item) for item in provisions if item}),
    }


def _chunk_source(metadata: dict[str, Any], body: str, *, chunk_char_cap: int) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    cursor = 0
    index = 1
    while cursor < len(body):
        end = min(len(body), cursor + chunk_char_cap)
        if end < len(body):
            boundary = max(body.rfind("\n\n", cursor, end), body.rfind("\n", cursor, end))
            if boundary > cursor + max(200, chunk_char_cap // 2):
                end = boundary
        raw_chunk = body[cursor:end]
        stripped = raw_chunk.strip()
        if stripped:
            leading_trim = len(raw_chunk) - len(raw_chunk.lstrip())
            chunk_start = cursor + leading_trim
            chunk_end = chunk_start + len(stripped)
            chunks.append(
                {
                    "chunk_id": f"{metadata['source_id']}#c{index}",
                    "source_id": metadata["source_id"],
                    "title": metadata["title"],
                    "grade": metadata["grade"],
                    "jurisdiction": metadata["jurisdiction"],
                    "documentTypes": metadata["documentTypes"],
                    "topics": metadata["topics"],
                    "provisions": metadata["provisions"],
                    "charStart": chunk_start,
                    "charEnd": chunk_end,
                    "path": metadata["path"],
                    "text": stripped[:chunk_char_cap],
                }
            )
            index += 1
        cursor = max(end, cursor + 1)
    return chunks


def _score_chunk(chunk: dict[str, Any], query: dict[str, Any]) -> tuple[int, list[str], int]:
    score = GRADE_WEIGHT.get(chunk["grade"], 0)
    relevance = 0
    reasons = [f"grade:{chunk['grade']}"]
    if chunk["jurisdiction"] and chunk["jurisdiction"] == query["jurisdiction"]:
        score += 25
        relevance += 25
        reasons.append("jurisdiction")
    if query["documentType"] in chunk.get("documentTypes", []):
        score += 10
        relevance += 10
        reasons.append("documentType")

    text_norm = _normalize_token(chunk["text"])
    for provision in query["provisions"]:
        if provision in chunk["provisions"] or provision in text_norm:
            score += 30
            relevance += 30
            reasons.append(f"provision:{provision}")
    for topic in query["topics"]:
        if topic in chunk["topics"] or topic in text_norm or topic in _normalize_token(chunk["title"]):
            score += 20
            relevance += 20
            reasons.append(f"topic:{topic}")
    return score, reasons, relevance


def _cap_chunks(candidates: list[dict[str, Any]], *, max_chunks: int, total_char_cap: int) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    total = 0
    for candidate in candidates:
        length = len(candidate["text"])
        if len(selected) >= max_chunks:
            break
        if total + length > total_char_cap:
            remaining = total_char_cap - total
            if remaining <= 0:
                break
            candidate = dict(candidate)
            candidate["text"] = candidate["text"][:remaining]
            candidate["charEnd"] = candidate["charStart"] + len(candidate["text"])
            length = len(candidate["text"])
        selected.append(candidate)
        total += length
    return selected


def _sufficiency(query: dict[str, Any], chunks: list[dict[str, Any]]) -> dict[str, Any]:
    if query["supportLevel"] != "conditional":
        return {
            "status": "not_required",
            "authorityPacketProvided": bool(chunks),
            "skeletonOnly": False,
            "reason": "support level is not conditional",
        }
    if not chunks:
        return {
            "status": "insufficient",
            "authorityPacketProvided": False,
            "skeletonOnly": True,
            "reason": "no matching authority chunks found",
        }
    if any(chunk["grade"] in {"A", "B"} for chunk in chunks):
        return {
            "status": "sufficient",
            "authorityPacketProvided": True,
            "skeletonOnly": False,
            "reason": "at least one Grade A/B authority chunk matched",
        }
    return {
        "status": "insufficient",
        "authorityPacketProvided": False,
        "skeletonOnly": True,
        "reason": "only Grade C reference chunks matched",
    }


def _resolve_source_path(path_value: str, registry_path: Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    candidates = [
        Path.cwd() / path,
        registry_path.parent / path,
        registry_path.parent.parent / path,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def _list_value(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return [str(value)]


def _normalize_jurisdiction(value: str) -> str:
    lowered = value.strip().lower()
    aliases = {
        "kr": "korea",
        "kor": "korea",
        "korea": "korea",
        "한국": "korea",
        "한국법": "korea",
        "us": "us",
        "usa": "us",
        "united states": "us",
        "uk": "uk",
        "gb": "uk",
        "intl": "international",
        "int": "international",
        "international": "international",
    }
    return aliases.get(lowered, lowered)


def _normalize_document_type(value: str) -> str:
    lowered = value.strip().lower()
    aliases = {
        "memo": "advisory",
        "opinion": "advisory",
        "legal opinion": "advisory",
        "corporation": "corporate",
        "lit": "litigation",
        "reg": "regulatory",
    }
    return aliases.get(lowered, lowered)


def _normalize_token(value: str) -> str:
    return re.sub(r"\s+", "", value.strip().lower())


def _default_support_level(document_type: str) -> str:
    return "conditional" if _normalize_document_type(document_type) in CONDITIONAL_DOCUMENT_TYPES else "full"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tools.retrieval.deterministic",
        description="Retrieve deterministic authority chunks from source-registry metadata.",
    )
    parser.add_argument("--registry", type=Path, required=True, help="library/source-registry.json path")
    parser.add_argument("--document-type", required=True)
    parser.add_argument("--jurisdiction", required=True)
    parser.add_argument("--support-level", choices=("full", "conditional"))
    parser.add_argument("--topic", action="append", default=[])
    parser.add_argument("--provision", action="append", default=[])
    parser.add_argument("--max-chunks", type=int, default=DEFAULT_MAX_CHUNKS)
    parser.add_argument("--chunk-char-cap", type=int, default=DEFAULT_CHUNK_CHAR_CAP)
    parser.add_argument("--total-char-cap", type=int, default=DEFAULT_TOTAL_CHAR_CAP)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = retrieve_authority_chunks(
        args.registry,
        document_type=args.document_type,
        jurisdiction=args.jurisdiction,
        topics=args.topic,
        provisions=args.provision,
        support_level=args.support_level,
        max_chunks=args.max_chunks,
        chunk_char_cap=args.chunk_char_cap,
        total_char_cap=args.total_char_cap,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

