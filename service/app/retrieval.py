from __future__ import annotations

import math
import re
from collections import Counter

from .ingestion import Chunk


TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:\.[0-9]+)?")
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does",
    "for", "from", "how", "i", "in", "is", "it", "of", "on", "or", "the",
    "to", "what", "when", "which", "with", "you", "your", "lumendesk",
}


def tokenize(value: str) -> list[str]:
    return [token for token in TOKEN_PATTERN.findall(value.lower()) if token not in STOP_WORDS]


class TfidfRetriever:
    """Small deterministic cosine-similarity retriever with no external ML dependency."""

    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        tokenized = [tokenize(f"{chunk.title} {chunk.text}") for chunk in chunks]
        document_frequency: Counter[str] = Counter()
        for tokens in tokenized:
            document_frequency.update(set(tokens))
        count = max(len(chunks), 1)
        self.idf = {
            token: math.log((1 + count) / (1 + frequency)) + 1
            for token, frequency in document_frequency.items()
        }
        self.vectors = [self._vector(tokens) for tokens in tokenized]

    def _vector(self, tokens: list[str]) -> dict[str, float]:
        frequencies = Counter(tokens)
        weighted = {
            token: frequency * self.idf.get(token, 0.0)
            for token, frequency in frequencies.items()
            if token in self.idf
        }
        norm = math.sqrt(sum(value * value for value in weighted.values())) or 1.0
        return {token: value / norm for token, value in weighted.items()}

    def retrieve(self, question: str, top_k: int = 3) -> list[dict]:
        query_vector = self._vector(tokenize(question))
        scored: list[tuple[float, Chunk]] = []
        for chunk, vector in zip(self.chunks, self.vectors, strict=True):
            score = sum(value * vector.get(token, 0.0) for token, value in query_vector.items())
            scored.append((score, chunk))
        scored.sort(key=lambda item: (-item[0], item[1].chunk_id))
        return [
            {**chunk.to_dict(), "score": round(score, 6)}
            for score, chunk in scored[: max(1, top_k)]
            if score > 0
        ]
