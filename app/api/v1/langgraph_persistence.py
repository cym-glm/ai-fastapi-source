from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies.auth import get_current_user
from app.langgraph_persistence.service import langgraph_persistence_service
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser


router = APIRouter()


class PersistenceChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    conversation_id: str = Field(..., min_length=1)
    tenant_id: str = Field(default="tenant_001")


@router.post(
    "/langgraph/persistence/chat",
    response_model=ApiResponse[dict],
)
async def persistence_chat(
    request: PersistenceChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[dict]:
    result = langgraph_persistence_service.continue_flow(
        user_question=request.question,
        tenant_id=request.tenant_id,
        user_id=current_user.user_id,
        conversation_id=request.conversation_id,
    )
    print('33333333333333333333-------:')
    print(result)

    return ApiResponse[dict](
        data={
            "answer": result["final_answer"],
            "intent": result["intent"],
            "order_id": result["order_id"],
            "order_status": result.get("order_status") or None,
            "need_user_input": result["need_user_input"],
            "waiting_for": result["waiting_for"],
            "logs": result["logs"],
        }
    )


@router.get(
    "/langgraph/persistence/state/{conversation_id}",
    response_model=ApiResponse[dict],
)
async def get_persistence_state(
    conversation_id: str,
    tenant_id: str = "tenant_001",
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[dict]:
    result = langgraph_persistence_service.get_current_state(
        tenant_id=tenant_id,
        user_id=current_user.user_id,
        conversation_id=conversation_id,
    )

    return ApiResponse[dict](
        data=result
    )

