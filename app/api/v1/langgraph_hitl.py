from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies.auth import get_current_user
from app.langgraph_hitl.service import langgraph_hitl_service
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser


router = APIRouter()


class HITLStartRequest(BaseModel):
    question: str = Field(..., min_length=1)
    conversation_id: str = Field(..., min_length=1)
    tenant_id: str = Field(default="tenant_001")


class HITLDecisionRequest(BaseModel):
    conversation_id: str = Field(..., min_length=1)
    tenant_id: str = Field(default="tenant_001")

    type: Literal["approve", "reject", "edit"]
    reason: str | None = None
    edited_payload: dict | None = None


@router.post(
    "/langgraph/hitl/refund/start",
    response_model=ApiResponse[dict],
)
async def start_hitl_refund(
    request: HITLStartRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[dict]:
    result = langgraph_hitl_service.start(
        user_question=request.question,
        tenant_id=request.tenant_id,
        user_id=current_user.user_id,
        conversation_id=request.conversation_id,
    )

    return ApiResponse[dict](
        data=result
    )


@router.get(
    "/langgraph/hitl/refund/state/{conversation_id}",
    response_model=ApiResponse[dict],
)
async def get_hitl_state(
    conversation_id: str,
    tenant_id: str = "tenant_001",
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[dict]:
    result = langgraph_hitl_service.get_state(
        tenant_id=tenant_id,
        user_id=current_user.user_id,
        conversation_id=conversation_id,
    )

    return ApiResponse[dict](
        data=result
    )


@router.post(
    "/langgraph/hitl/refund/resume",
    response_model=ApiResponse[dict],
)
async def resume_hitl_refund(
    request: HITLDecisionRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[dict]:
    decision = {
        "type": request.type,
        "reviewer_id": current_user.user_id,
        "reason": request.reason,
    }

    if request.type == "edit":
        decision["edited_payload"] = request.edited_payload

    result = langgraph_hitl_service.resume(
        tenant_id=request.tenant_id,
        user_id=current_user.user_id,
        conversation_id=request.conversation_id,
        decision=decision,
    )

    return ApiResponse[dict](
        data=result
    )