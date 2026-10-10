from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies.auth import get_current_user
from app.langgraph_memory.service import langgraph_memory_service
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser


router = APIRouter()


class MemoryChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    conversation_id: str = Field(..., min_length=1)
    tenant_id: str = Field(default="tenant_001")


@router.post(
    "/langgraph/memory/chat",
    response_model=ApiResponse[dict],
)
async def memory_chat(
    request: MemoryChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[dict]:
    result = langgraph_memory_service.chat(
        tenant_id=request.tenant_id,
        user_id=current_user.user_id,
        conversation_id=request.conversation_id,
        question=request.question,
    )

    return ApiResponse[dict](
        data=result
    )


@router.get(
    "/langgraph/memory/list",
    response_model=ApiResponse[list[dict]],
)
async def list_memory(
    tenant_id: str = "tenant_001",
    memory_type: str = "preferences",
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[list[dict]]:
    result = langgraph_memory_service.list_memories(
        tenant_id=tenant_id,
        user_id=current_user.user_id,
        memory_type=memory_type,
    )

    return ApiResponse[list[dict]](
        data=result
    )