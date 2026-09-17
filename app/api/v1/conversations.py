from fastapi import APIRouter, Depends, Path, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db_session
from app.dependencies.redis import get_redis_client
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationListResponse,
    ConversationMessagesResponse,
    ConversationResponse,
)
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser
from app.services.conversation_service import conversation_service


router = APIRouter()


@router.post(
    "/conversations",
    response_model=ApiResponse[ConversationResponse],
)
async def create_conversation(
    request: ConversationCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[ConversationResponse]:
    result = await conversation_service.create_conversation(
        db=db,
        request=request,
        user_id=current_user.user_id,
    )

    return ApiResponse[ConversationResponse](
        data=result
    )


@router.get(
    "/conversations",
    response_model=ApiResponse[ConversationListResponse],
)
async def list_conversations(
    limit: int = Query(default=20, ge=1, le=100, description="返回数量"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[ConversationListResponse]:
    result = await conversation_service.list_conversations(
        db=db,
        user_id=current_user.user_id,
        limit=limit,
    )

    return ApiResponse[ConversationListResponse](
        data=result
    )


@router.get(
    "/conversations/{conversation_id}",
    response_model=ApiResponse[ConversationResponse],
)
async def get_conversation(
    conversation_id: str = Path(..., description="会话 ID"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ApiResponse[ConversationResponse]:
    result = await conversation_service.get_conversation(
        db=db,
        conversation_id=conversation_id,
    )

    return ApiResponse[ConversationResponse](
        data=result
    )


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=ApiResponse[ConversationMessagesResponse],
)
async def get_conversation_messages(
    conversation_id: str = Path(..., description="会话 ID"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
) -> ApiResponse[ConversationMessagesResponse]:
    result = await conversation_service.get_conversation_messages(
        db=db,
        conversation_id=conversation_id,
        redis=redis,
    )

    return ApiResponse[ConversationMessagesResponse](
        data=result
    )