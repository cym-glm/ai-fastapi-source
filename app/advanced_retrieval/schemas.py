from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.vector_knowledge.schemas import VectorSearchResult


class RetrievalMode(str, Enum):
    VECTOR = "vector"
    KEYWORD = "keyword"
    HYBRID = "hybrid"


@dataclass
class QueryRewriteResult:
    original_query: str
    rewritten_query: str
    intent: str
    keywords: list[str]
    filters: dict[str, Any] = field(default_factory=dict)


@dataclass
class MultiQueryResult:
    original_query: str
    queries: list[str]


@dataclass
class KeywordSearchResult:
    chunk_id: str
    document_id: str
    content: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HybridSearchResult:
    chunk_id: str
    document_id: str
    content: str
    vector_score: float = 0.0
    keyword_score: float = 0.0
    final_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    matched_by: list[str] = field(default_factory=list)


@dataclass
class RetrievalConfig:
    mode: RetrievalMode = RetrievalMode.HYBRID
    top_k: int = 5
    candidate_k: int = 20
    vector_weight: float = 0.7
    keyword_weight: float = 0.3
    use_query_rewrite: bool = True
    use_multi_query: bool = True
    use_mmr: bool = True
    use_rerank: bool = True
    min_score: float = 0.05
    max_context_chars: int = 2000
    metadata_filter: dict[str, Any] | None = None


@dataclass
class AdvancedRetrievalRequest:
    query: str
    config: RetrievalConfig = field(default_factory=RetrievalConfig)


@dataclass
class AdvancedRetrievalResponse:
    original_query: str
    rewritten_query: str
    queries: list[str]
    results: list[HybridSearchResult]
    context: str
    sources: list[dict[str, Any]]
    fallback_reason: str | None = None
    debug: dict[str, Any] = field(default_factory=dict)