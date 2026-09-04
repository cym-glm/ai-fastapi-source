from fastapi import APIRouter, Path

from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationMessagesResponse,
    ConversationResponse,
)
from app.schemas.response import ApiResponse
from app.services.conversation_service import (
    create_conversation_mesasge,
    get_conversation_mesage,
)

router = APIRouter()

@router.post(
    "/conversations",
    response_model=ApiResponse[ConversationResponse]
)
async def create_conversation(request: ConversationCreateRequest) -> ApiResponse[ConversationResponse]:
        result = await create_conversation_mesasge(request)
        return ApiResponse[ConversationResponse](data=result)

@router.get(
    "/conversations/{conversation_id}",
    response_model=ApiResponse[ConversationMessagesResponse]
)
async def get_conversation(conversation_id: str = Path(..., description="会话ID")) -> ApiResponse[ConversationMessagesResponse]:
    result = await get_conversation_mesage(conversation_id)
    return ApiResponse[ConversationMessagesResponse](data=result)