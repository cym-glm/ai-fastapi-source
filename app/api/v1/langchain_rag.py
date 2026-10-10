from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies.auth import get_current_user
from app.langchain_rag.service import RAGAnswer, langchain_rag_service
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser


router = APIRouter()


class RAGAskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题")
    provider: str = Field(default="deepseek", description="模型供应商")
    model: str = Field(default="deepseek-chat", description="模型名称")
    k: int = Field(default=4, ge=1, le=10, description="检索数量")


@router.post(
    "/langchain/rag/rebuild-index",
    response_model=ApiResponse[dict],
)
async def rebuild_rag_index(
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[dict]:
    result = langchain_rag_service.rebuild_index()

    return ApiResponse[dict](
        data=result
    )


@router.post(
    "/langchain/rag/ask",
    response_model=ApiResponse[RAGAnswer],
)
async def rag_ask(
    request: RAGAskRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[RAGAnswer]:
    result = langchain_rag_service.ask(
        question=request.question,
        provider=request.provider,
        model_name=request.model,
        k=request.k,
    )

    return ApiResponse[RAGAnswer](
        data=result
    )