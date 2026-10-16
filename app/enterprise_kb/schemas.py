

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class KnowledgeDocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    PARSED = "parsed"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXED = "indexed"
    FAILED = "failed"



class FeedbackRating(str, Enum):
    GOOD = "good"
    BAD = "bad"
    UNKNOWN = "unknown"


@dataclass
class KnowledgeDocumentRecord:
    document_id: str
    tenant_id: str
    title: str
    file_name: str
    file_path: str
    file_type: str
    status: KnowledgeDocumentStatus
    chunk_count: int = 0
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class KnowledgeSource:
    chunk_id: str
    document_id: str
    source_path: str | None
    heading: str | None
    page_number: int | None
    score: float
    matched_by: list[str] = field(default_factory=list)


@dataclass
class KnowledgeChatRequest:
    question: str
    tenant_id: str = "tenant_001"
    user_id: str = "anonymous"
    top_k: int = 3
    metadata_filter: dict[str, Any] | None = None


@dataclass
class KnowledgeChatResponse:
    query_id: str
    question: str
    answer: str
    sources: list[KnowledgeSource]
    context: str
    fallback_reason: str | None = None
    debug: dict[str, Any] = field(default_factory=dict)



@dataclass
class KnowledgeQueryLog:
    query_id: str
    tenant_id: str
    user_id: str
    question: str
    answer: str
    retrieved_chunk_ids: list[str]
    retrieved_scores: list[float]
    sources: list[dict[str, Any]]
    fallback_reason: str | None
    metadata_filter: dict[str, Any] | None = None


@dataclass
class KnowledgeFeedback:
    feedback_id: str
    query_id: str
    tenant_id: str
    user_id: str
    rating: FeedbackRating
    comment: str = ""


@dataclass
class IndexFileResult:
    document: KnowledgeDocumentRecord
    chunk_count: int
    message: str


@dataclass
class KnowledgeBaseStats:
    document_count: int
    indexed_document_count: int
    query_count: int
    feedback_count: int