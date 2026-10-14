from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.advanced_retrieval.schemas import RetrievalMode
from app.rag_evaluation.service import rag_evaluation_service
from app.schemas.response import ApiResponse


router = APIRouter()


class EvaluationRequest(BaseModel):
    mode: Literal["vector", "keyword", "hybrid"] = "hybrid"
    top_k: int = Field(default=3, ge=1, le=20)
    use_query_rewrite: bool = True
    use_multi_query: bool = True
    use_mmr: bool = True
    use_rerank: bool = True


@router.get(
    "/rag-evaluation/cases",
    response_model=ApiResponse[list[dict]],
)
async def list_evaluation_cases() -> ApiResponse[list[dict]]:
    return ApiResponse[list[dict]](
        data=rag_evaluation_service.list_cases()
    )


@router.post(
    "/rag-evaluation/retrieval",
    response_model=ApiResponse[dict],
)
async def evaluate_retrieval(
    request: EvaluationRequest,
) -> ApiResponse[dict]:
    result = rag_evaluation_service.evaluate_retrieval(
        mode=RetrievalMode(request.mode),
        top_k=request.top_k,
        use_query_rewrite=request.use_query_rewrite,
        use_multi_query=request.use_multi_query,
        use_mmr=request.use_mmr,
        use_rerank=request.use_rerank,
    )

    return ApiResponse[dict](
        data=result
    )


@router.post(
    "/rag-evaluation/generation",
    response_model=ApiResponse[dict],
)
async def evaluate_generation(
    request: EvaluationRequest,
) -> ApiResponse[dict]:
    result = rag_evaluation_service.evaluate_generation(
        mode=RetrievalMode(request.mode),
        top_k=request.top_k,
        use_query_rewrite=request.use_query_rewrite,
        use_multi_query=request.use_multi_query,
        use_mmr=request.use_mmr,
        use_rerank=request.use_rerank,
    )

    return ApiResponse[dict](
        data=result
    )


@router.post(
    "/rag-evaluation/full-report",
    response_model=ApiResponse[dict],
)
async def run_full_report() -> ApiResponse[dict]:
    result = rag_evaluation_service.run_full_report()

    return ApiResponse[dict](
        data=result
    )


@router.post(
    "/rag-evaluation/compare-strategies",
    response_model=ApiResponse[list[dict]],
)
async def compare_strategies() -> ApiResponse[list[dict]]:
    result = rag_evaluation_service.compare_strategies()

    return ApiResponse[list[dict]](
        data=result
    )