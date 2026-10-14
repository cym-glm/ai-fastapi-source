from typing import Any, Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.advanced_retrieval.schemas import (
    AdvancedRetrievalRequest,
    RetrievalConfig,
    RetrievalMode,
)
from app.advanced_retrieval.service import advanced_retrieval_service
from app.schemas.response import ApiResponse


router = APIRouter()


class AdvancedRetrievalApiRequest(BaseModel):
    query: str = Field(..., min_length=1)

    mode: Literal["vector", "keyword", "hybrid"] = "hybrid"
    top_k: int = Field(default=5, ge=1, le=20)
    candidate_k: int = Field(default=20, ge=1, le=100)

    vector_weight: float = Field(default=0.7, ge=0, le=1)
    keyword_weight: float = Field(default=0.3, ge=0, le=1)

    use_query_rewrite: bool = True
    use_multi_query: bool = True
    use_mmr: bool = True
    use_rerank: bool = True

    min_score: float = Field(default=0.05, ge=0)
    max_context_chars: int = Field(default=2000, ge=100)

    metadata_filter: dict[str, Any] | None = None


@router.post(
    "/knowledge/advanced-search",
    response_model=ApiResponse[dict],
)
async def advanced_search(
    request: AdvancedRetrievalApiRequest,
) -> ApiResponse[dict]:
    config = RetrievalConfig(
        mode=RetrievalMode(request.mode),
        top_k=request.top_k,
        candidate_k=request.candidate_k,
        vector_weight=request.vector_weight,
        keyword_weight=request.keyword_weight,
        use_query_rewrite=request.use_query_rewrite,
        use_multi_query=request.use_multi_query,
        use_mmr=request.use_mmr,
        use_rerank=request.use_rerank,
        min_score=request.min_score,
        max_context_chars=request.max_context_chars,
        metadata_filter=request.metadata_filter,
    )

    response = advanced_retrieval_service.retrieve(
        AdvancedRetrievalRequest(
            query=request.query,
            config=config,
        )
    )

    return ApiResponse[dict](
        data={
            "original_query": response.original_query,
            "rewritten_query": response.rewritten_query,
            "queries": response.queries,
            "fallback_reason": response.fallback_reason,
            "context": response.context,
            "sources": response.sources,
            "debug": response.debug,
            "results": [
                {
                    "chunk_id": item.chunk_id,
                    "document_id": item.document_id,
                    "content": item.content,
                    "vector_score": item.vector_score,
                    "keyword_score": item.keyword_score,
                    "final_score": item.final_score,
                    "matched_by": item.matched_by,
                    "metadata": item.metadata,
                }
                for item in response.results
            ],
        }
    )