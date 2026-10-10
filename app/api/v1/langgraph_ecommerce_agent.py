from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies.auth import get_current_user
from app.langgraph_ecommerce_agent.service import (
    langgraph_ecommerce_agent_service,
)
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser


router = APIRouter()


class EcommerceAgentChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    conversation_id: str = Field(..., min_length=1)
    tenant_id: str = Field(default="tenant_001")
    is_new_conversation: bool = Field(default=False)


class EcommerceAgentResumeRequest(BaseModel):
    conversation_id: str = Field(..., min_length=1)
    tenant_id: str = Field(default="tenant_001")

    type: Literal["approve", "reject", "edit"]
    reason: str | None = None
    edited_payload: dict | None = None


@router.post(
    "/langgraph/ecommerce-agent/chat",
    response_model=ApiResponse[dict],
)
async def ecommerce_agent_chat(
    request: EcommerceAgentChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[dict]:
    result = await langgraph_ecommerce_agent_service.chat(
        tenant_id=request.tenant_id,
        user_id=current_user.user_id,
        conversation_id=request.conversation_id,
        question=request.question,
        is_new_conversation=request.is_new_conversation,
    )

    return ApiResponse[dict](
        data=result
    )


@router.get(
    "/langgraph/ecommerce-agent/state/{conversation_id}",
    response_model=ApiResponse[dict],
)
async def get_ecommerce_agent_state(
    conversation_id: str,
    tenant_id: str = "tenant_001",
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[dict]:
    result = await langgraph_ecommerce_agent_service.get_state(
        tenant_id=tenant_id,
        user_id=current_user.user_id,
        conversation_id=conversation_id,
    )

    return ApiResponse[dict](
        data=result
    )


@router.post(
    "/langgraph/ecommerce-agent/resume",
    response_model=ApiResponse[dict],
)
async def resume_ecommerce_agent(
    request: EcommerceAgentResumeRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[dict]:
    decision = {
        "type": request.type,
        "reviewer_id": current_user.user_id,
        "reason": request.reason,
    }

    if request.type == "edit":
        decision["edited_payload"] = request.edited_payload

    result = await langgraph_ecommerce_agent_service.resume(
        tenant_id=request.tenant_id,
        user_id=current_user.user_id,
        conversation_id=request.conversation_id,
        decision=decision,
    )

    return ApiResponse[dict](
        data=result
    )


@router.get(
    "/langgraph/ecommerce-agent/memories",
    response_model=ApiResponse[list[dict]],
)
async def list_ecommerce_agent_memories(
    tenant_id: str = "tenant_001",
    memory_type: str = "preferences",
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[list[dict]]:
    result = langgraph_ecommerce_agent_service.list_memories(
        tenant_id=tenant_id,
        user_id=current_user.user_id,
        memory_type=memory_type,
    )

    return ApiResponse[list[dict]](
        data=result
    )