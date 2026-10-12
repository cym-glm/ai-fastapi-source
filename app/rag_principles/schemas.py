from dataclasses import dataclass, field
from typing import Any

@dataclass
class RawDocument:
    document_id: str
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ChunkDocument:
    chunk_id: str
    document_id: str
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EmbeddedChunk:
    chunk: ChunkDocument
    embedding: list[float]


@dataclass
class RetrievedChunk:
    chunk: ChunkDocument
    score: float


@dataclass
class RAGAnswer:
    question: str
    answer: str
    retrieved_chunks: list[RetrievedChunk]
    context: str