from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EvaluationCaseDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class EvaluationCategory(str, Enum):
    REFUND = "refund"
    LOGISTICS = "logistics"
    INVOICE = "invoice"
    LEAVE = "leave"
    REIMBURSEMENT = "reimbursement"
    UNKNOWN = "unknown"


@dataclass
class RAGEvaluationCase:
    case_id: str
    question: str
    category: EvaluationCategory
    expected_chunk_ids: list[str]
    expected_document_ids: list[str]
    expected_answer_keywords: list[str]
    expected_source_paths: list[str]
    metadata_filter: dict[str, Any] = field(default_factory=dict)
    difficulty: EvaluationCaseDifficulty = EvaluationCaseDifficulty.EASY
    expected_answer: str | None = None
    notes: str = ""


@dataclass
class RetrievedItemForEval:
    chunk_id: str
    document_id: str
    content: str
    score: float
    source_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratedAnswerForEval:
    answer: str
    sources: list[dict[str, Any]]
    context: str


@dataclass
class RetrievalEvaluationResult:
    case_id: str
    question: str
    retrieved_chunk_ids: list[str]
    expected_chunk_ids: list[str]
    hit_rate: float
    recall_at_k: float
    precision_at_k: float
    mrr: float
    ndcg_at_k: float
    source_accuracy: float


@dataclass
class GenerationEvaluationResult:
    case_id: str
    question: str
    answer: str
    faithfulness: float
    answer_relevance: float
    answer_correctness: float
    context_relevance: float
    citation_accuracy: float
    missing_keywords: list[str] = field(default_factory=list)
    unsupported_claims: list[str] = field(default_factory=list)


@dataclass
class EvaluationReport:
    name: str
    total_cases: int
    retrieval_metrics: dict[str, float]
    generation_metrics: dict[str, float]
    case_results: list[dict[str, Any]]
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyComparisonResult:
    strategy_name: str
    report: EvaluationReport