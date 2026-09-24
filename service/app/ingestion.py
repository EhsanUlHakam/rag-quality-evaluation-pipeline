from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Document:
    document_id: str
    title: str
    text: str
    path: str


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    title: str
    text: str
    chunk_index: int
    word_start: int
    word_end: int

    def to_dict(self) -> dict:
        return asdict(self)


def normalize_text(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[\t ]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def load_documents(directory: Path) -> list[Document]:
    documents: list[Document] = []
    for path in sorted(directory.glob("*.md")):
        raw = normalize_text(path.read_text(encoding="utf-8"))
        lines = raw.splitlines()
        title = lines[0].removeprefix("#").strip() if lines else path.stem
        body = normalize_text("\n".join(lines[1:]))
        documents.append(
            Document(
                document_id=path.stem,
                title=title,
                text=body,
                path=str(path),
            )
        )
    if not documents:
        raise ValueError(f"No Markdown documents found in {directory}")
    return documents


def chunk_documents(
    documents: list[Document], chunk_size: int = 90, overlap: int = 15
) -> list[Chunk]:
    if chunk_size < 10:
        raise ValueError("chunk_size must be at least 10 words")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")

    chunks: list[Chunk] = []
    step = chunk_size - overlap
    for document in documents:
        words = document.text.split()
        for index, start in enumerate(range(0, len(words), step)):
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            if not chunk_words:
                continue
            chunks.append(
                Chunk(
                    chunk_id=f"{document.document_id}::chunk-{index:03d}",
                    document_id=document.document_id,
                    title=document.title,
                    text=" ".join(chunk_words),
                    chunk_index=index,
                    word_start=start,
                    word_end=end,
                )
            )
            if end == len(words):
                break
    return chunks
