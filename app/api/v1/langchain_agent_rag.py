from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies.auth import get_current_user
from app.langchain_agent_rag.schemas import AgentRAGRunResponse
from app.langchain_agent_rag.service import langchain_agent_rag_service
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser


router = APIRouter()


class AgentRAGChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题")
    provider: str = Field(default="deepseek", description="模型供应商")
    model: str = Field(default="deepseek-chat", description="模型名称")


@router.post(
    "/langchain/agent-rag/ecommerce/chat",
    response_model=ApiResponse[AgentRAGRunResponse],
)
async def ecommerce_agent_rag_chat(
    request: AgentRAGChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[AgentRAGRunResponse]:
    result = await langchain_agent_rag_service.run_ecommerce_agent_rag(
        user_question=request.question,
        provider=request.provider,
        model_name=request.model,
    )

    return ApiResponse[AgentRAGRunResponse](
        data=result
    )