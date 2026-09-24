from __future__ import annotations

import re
import time
from typing import Any, Protocol

from .retrieval import tokenize


REFUSAL = "I could not find that information in the supplied LumenDesk knowledge base."


class AnswerGenerator(Protocol):
    def generate(self, question: str, retrieved: list[dict], scenario: str = "good") -> dict[str, Any]: ...


def approximate_tokens(value: str) -> int:
    return max(1, round(len(value) / 4)) if value else 0


class ExtractiveAnswerGenerator:
    mode = "deterministic-extractive"

    def generate(self, question: str, retrieved: list[dict], scenario: str = "good") -> dict[str, Any]:
        started = time.perf_counter()
        error: dict[str, str] | None = None

        if scenario == "empty_retrieval":
            retrieved = []
            error = {"code": "EMPTY_RETRIEVAL", "message": "Controlled empty retrieval result."}
        if scenario == "timeout":
            time.sleep(0.25)
            return self._response(
                question, "", [], [], started,
                {"code": "TIMEOUT", "message": "Controlled generation timeout."},
            )
        if scenario == "malformed":
            return self._response(
                question, "{malformed-answer", retrieved, [], started,
                {"code": "MALFORMED_RESPONSE", "message": "Controlled malformed model output."},
            )

        answer, citations = self._extract(question, retrieved)
        if scenario == "hallucination" and answer != REFUSAL:
            answer += " LumenDesk also guarantees unlimited free storage on every subscription."
        if scenario == "missing_citation":
            citations = []

        return self._response(question, answer, retrieved, citations, started, error)

    def _extract(self, question: str, retrieved: list[dict]) -> tuple[str, list[dict]]:
        if not retrieved or retrieved[0]["score"] < 0.08:
            return REFUSAL, []

        query_tokens = set(tokenize(question))
        candidates: list[tuple[float, int, str, dict]] = []
        for rank, chunk in enumerate(retrieved):
            sentences = re.split(r"(?<=[.!?])\s+", chunk["text"])
            for sentence in sentences:
                sentence_tokens = set(tokenize(sentence))
                overlap = len(query_tokens & sentence_tokens)
                numeric_bonus = len(set(re.findall(r"\b\d+(?:\.\d+)?%?\b", question)) & set(re.findall(r"\b\d+(?:\.\d+)?%?\b", sentence)))
                score = overlap + numeric_bonus + float(chunk["score"]) - (rank * 0.02)
                candidates.append((score, -rank, sentence.strip(), chunk))
        candidates.sort(key=lambda item: (-item[0], -item[1], item[2]))
        # Three evidence sentences allow deterministic multi-fact questions to
        # surface facts that live in separate sentences without summarization.
        selected = [item for item in candidates if item[0] > 0][:3]
        if not selected:
            return REFUSAL, []

        answer_parts: list[str] = []
        citations: list[dict] = []
        for _, _, sentence, chunk in selected:
            if sentence and sentence not in answer_parts:
                answer_parts.append(sentence)
            citation = {"source_id": chunk["document_id"], "chunk_id": chunk["chunk_id"]}
            if citation not in citations:
                citations.append(citation)
        return " ".join(answer_parts), citations

    def _response(
        self,
        question: str,
        answer: str,
        retrieved: list[dict],
        citations: list[dict],
        started: float,
        error: dict[str, str] | None,
    ) -> dict[str, Any]:
        context_text = " ".join(chunk["text"] for chunk in retrieved)
        input_tokens = approximate_tokens(question + " " + context_text)
        output_tokens = approximate_tokens(answer)
        return {
            "question": question,
            "answer": answer,
            "retrieved_chunks": retrieved,
            "source_ids": list(dict.fromkeys(chunk["document_id"] for chunk in retrieved)),
            "retrieval_scores": [chunk["score"] for chunk in retrieved],
            "citations": citations,
            "latency_ms": round((time.perf_counter() - started) * 1000, 3),
            "model": self.mode,
            "mode": self.mode,
            "usage": {
                "input_tokens_approx": input_tokens,
                "output_tokens_approx": output_tokens,
                "total_tokens_approx": input_tokens + output_tokens,
            },
            "estimated_cost_usd": 0.0,
            "error": error,
        }


class OllamaAnswerGenerator:
    """Documented adapter seam; intentionally not required by the deterministic MVP."""

    mode = "ollama"

    def generate(self, question: str, retrieved: list[dict], scenario: str = "good") -> dict[str, Any]:
        raise RuntimeError(
            "Ollama mode is optional and disabled in the MVP. Configure an adapter before use."
        )
