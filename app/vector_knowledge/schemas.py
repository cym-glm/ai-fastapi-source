from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.document_chunking.schemas import ChunkDocument


class EmbeddingProvider(str, Enum):
    HASH = "hash"
    OPENAI = "openai"
    QWEN = "qwen"
    BGE = "bge"
    JINA = "jina"


class VectorStoreProvider(str, Enum):
    IN_MEMORY = "in_memory"
    CHROMA = "chroma"
    PGVECTOR = "pgvector"
    QDRANT = "qdrant"
    MILVUS = "milvus"
    ELASTICSEARCH = "elasticsearch"


@dataclass
class EmbeddingConfig:
    provider: EmbeddingProvider = EmbeddingProvider.HASH
    model_name: str = "deterministic-hash-embedding"
    dimension: int = 128
    normalize: bool = True


@dataclass
class EmbeddedChunk:
    chunk_id: str
    document_id: str
    content: str
    embedding: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorSearchResult:
    chunk_id: str
    document_id: str
    content: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorSearchRequest:
    query: str
    top_k: int = 5
    metadata_filter: dict[str, Any] | None = None


@dataclass
class VectorSearchResponse:
    query: str
    top_k: int
    results: list[VectorSearchResult]


@dataclass
class IndexBuildResult:
    total_chunks: int
    embedded_chunks: int
    provider: EmbeddingProvider
    vector_store: VectorStoreProvider
    warnings: list[str] = field(default_factory=list)


@dataclass
class ChunkEmbeddingRequest:
    chunk: ChunkDocument
    config: EmbeddingConfig