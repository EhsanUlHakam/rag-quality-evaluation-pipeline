from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .generation import REFUSAL
from .retrieval import STOP_WORDS, tokenize


def load_dataset(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload["cases"]


def normalize_for_match(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def evaluate_case(case: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    answer = response.get("answer") or ""
    normalized_answer = normalize_for_match(answer)
    expected_facts = case.get("expected_answer_facts", [])
    matched_facts = [fact for fact in expected_facts if normalize_for_match(fact) in normalized_answer]
    keyword_coverage = len(matched_facts) / len(expected_facts) if expected_facts else 1.0

    expected_source = case.get("expected_source_id")
    sources = response.get("source_ids") or []
    retrieval_hit = expected_source in sources if case["answerable"] else None
    expected_source_match = retrieval_hit

    refusal = normalize_for_match(REFUSAL) in normalized_answer
    has_error = response.get("error") is not None
    if case["answerable"]:
        answerability_correct = bool(answer) and not refusal and not has_error
    else:
        answerability_correct = refusal and not has_error

    retrieved_chunk_ids = {chunk["chunk_id"] for chunk in response.get("retrieved_chunks", [])}
    retrieved_source_ids = {chunk["document_id"] for chunk in response.get("retrieved_chunks", [])}
    citations = response.get("citations") or []
    citations_are_real = all(
        citation.get("source_id") in retrieved_source_ids
        and citation.get("chunk_id") in retrieved_chunk_ids
        for citation in citations
    )
    citation_validity = (
        len(citations) > 0 and citations_are_real
        if case["answerable"]
        else len(citations) == 0
    )

    context = " ".join(chunk["text"] for chunk in response.get("retrieved_chunks", []))
    context_tokens = set(tokenize(context))
    sentence_support = []
    for sentence in re.split(r"(?<=[.!?])\s+", answer):
        sentence_tokens = {token for token in tokenize(sentence) if token not in STOP_WORDS}
        if sentence_tokens:
            sentence_support.append(len(sentence_tokens & context_tokens) / len(sentence_tokens))
    # The weakest-sentence score is intentionally conservative: a single
    # unsupported claim must not be hidden inside an otherwise extractive answer.
    groundedness = (
        min(sentence_support)
        if sentence_support and case["answerable"]
        else (1.0 if not case["answerable"] and refusal else 0.0)
    )

    required = {
        "retrieval": retrieval_hit is not False,
        "fact_coverage": keyword_coverage >= 0.80,
        "answerability": answerability_correct,
        "citations": citation_validity,
        "groundedness": groundedness >= 0.75,
        "no_error": not has_error,
    }
    maximum_latency = case.get("max_latency_ms")
    if maximum_latency is not None:
        required["latency"] = response.get("latency_ms", 0) <= maximum_latency

    return {
        "case_id": case["id"],
        "retrieval_hit_at_k": retrieval_hit,
        "expected_source_match": expected_source_match,
        "keyword_coverage": round(keyword_coverage, 4),
        "matched_facts": matched_facts,
        "expected_facts": expected_facts,
        "answerability_correct": answerability_correct,
        "citation_validity": citation_validity,
        "groundedness": round(groundedness, 4),
        "error": has_error,
        "latency_ms": response.get("latency_ms", 0),
        "usage": response.get("usage", {}),
        "estimated_cost_usd": response.get("estimated_cost_usd", 0.0),
        "checks": required,
        "case_pass": all(required.values()),
    }
