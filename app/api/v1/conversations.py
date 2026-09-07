from fastapi import APIRouter, Path,Depends
from app.dependencies.database import get_db_session, MockDBSession
from app.dependencies.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.dependencies.redis import get_redis_client
from app.dependencies.pagination import PaginationParams

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
from app.schemas.user import CurrentUser

router = APIRouter()

@router.post(
    "/conversations",
    response_model=ApiResponse[ConversationResponse]
)
async def create_conversation(
    request: ConversationCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser= Depends(get_current_user)) -> ApiResponse[ConversationResponse]:
        
        # sql_res = await db.execute("insert into conversations (title) values ('test')")
        # print(sql_res)
        # result = await create_conversation_mesasge(request)
        result = await create_conversation_mesasge(db, request, current_user.user_id)
        return ApiResponse[ConversationResponse](data=result)

@router.get(
    "/conversations/{conversation_id}",
    response_model=ApiResponse[ConversationMessagesResponse]
)
async def get_conversation(
    conversation_id: str = Path(..., description="会话ID"),
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client)) -> ApiResponse[ConversationMessagesResponse]:
    result = await get_conversation_mesage(db, conversation_id, redis)
    return ApiResponse[ConversationMessagesResponse](data=result)


@router.get(
    "/conversations",
    response_model=ApiResponse[dict]
)
async def list_conversations(
    pagination: PaginationParams = Depends(PaginationParams)) -> ApiResponse[dict]:
      return ApiResponse[dict](data={
            "page": pagination.page,
            "page_size": pagination.size,
            "offset": pagination.offset,
            "items": []
    })