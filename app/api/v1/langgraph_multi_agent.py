from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.langgraph_multi_agent.service import langgraph_multi_agent_service
from app.schemas.response import ApiResponse


router = APIRouter()


class MultiAgentChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    graph_type: Literal["ecommerce", "data_analysis"] = "ecommerce"


@router.post(
    "/langgraph/multi-agent/chat",
    response_model=ApiResponse[dict],
)
async def multi_agent_chat(
    request: MultiAgentChatRequest,
) -> ApiResponse[dict]:
    result = langgraph_multi_agent_service.chat(
        question=request.question,
        graph_type=request.graph_type,
    )

    return ApiResponse[dict](
        data=result
    )