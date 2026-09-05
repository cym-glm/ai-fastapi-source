from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies.agent_context import AgentContext, get_agent_context
from app.schemas.response import ApiResponse

router = APIRouter()


class AgentRunRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题")
    agent_id: str = Field(default="agent_chat", description="Agent ID")


class AgentRunResponse(BaseModel):
    answer: str = Field(..., description="Agent 回答")
    trace_id: str = Field(..., description="链路追踪 ID")
    debug: bool = Field(default=False, description="是否调试模式")


@router.post("/agents/run", response_model=ApiResponse[AgentRunResponse])
async def run_agent(
    request: AgentRunRequest,
    context: AgentContext = Depends(get_agent_context),
) -> ApiResponse[AgentRunResponse]:
    answer = (
        f"用户 {context.current_user.username} 调用了 {request.agent_id}，"
        f"问题是：{request.question}"
    )

    return ApiResponse[AgentRunResponse](
        data=AgentRunResponse(
            answer=answer,
            trace_id=context.trace_id,
            debug=context.debug,
        )
    )

# run_agent - get_agent_context - get_current_user - verfy_api_key

# http://127.0.0.1:8000/api/v1/agents/run 
# run_agent --- Depends(get_agent_context) --- Depends(get_current_user)- Depends(verfy_api_key)
#  读取 header--x-api-key, x-user-id, x-user-name