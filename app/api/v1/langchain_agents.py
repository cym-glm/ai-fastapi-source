from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies.auth import get_current_user
from app.langchain_agents.schemas import AgentRunResponse
from app.langchain_agents.service import langchain_agent_service
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser


router = APIRouter()


class LangChainAgentChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题")
    provider: str = Field(default="deepseek", description="模型供应商")
    model: str = Field(default="deepseek-chat", description="模型名称")


@router.post(
    "/langchain/agents/ecommerce/chat",
    response_model=ApiResponse[AgentRunResponse],
)
async def ecommerce_agent_chat(
    request: LangChainAgentChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[AgentRunResponse]:
    result = await langchain_agent_service.run_ecommerce_agent(
        user_question=request.question,
        provider=request.provider,
        model_name=request.model,
    )

    return ApiResponse[AgentRunResponse](
        data=result
    )