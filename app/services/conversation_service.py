import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.repositories.conversation_repository import conversation_repository
from app.schemas.chat import ChatRequest, MessageRole,ChatMessage
from app.schemas.conversation import ConversationResponse, ConversationMessagesResponse, ConversationCreateRequest
from app.redis.cache import (
    cache_recent_messages,
    get_cached_recent_messages)


async def create_conversation_mesasge(
        db: AsyncSession, 
        request: ConversationCreateRequest,
        user_id: str | None=None) -> ConversationResponse:

    conversation = await conversation_repository.create(db, request, user_id)
    # conversation_id=f"c_{uuid.uuid4().hex[:6]}"
    # conversation = await conversation_repository.create(conversation_id, request)

    return ConversationResponse(
        conversation_id=conversation.id,
        title=conversation.title,   
        status=conversation.status,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    )


async def get_conversation_mesage(
        db: AsyncSession, 
        conversation_id: str,
        redis: Redis| None = None) -> ConversationMessagesResponse:
    if redis:
        cached_messages = await get_cached_recent_messages(redis, conversation_id)
        if cached_messages is not None:
            return ConversationMessagesResponse(
                conversation_id=conversation_id,
                messages=cached_messages
            )
    
    messages = await conversation_repository.get_messages(
        db=db,
        conversation_id =conversation_id)
    if redis:
        await cache_recent_messages(
            redis=redis,
            conversation_id=conversation_id,
            messages=messages[-10:]) # 只缓存最近的10条消息
        
    return ConversationMessagesResponse(
        conversation_id=conversation_id,
        messages=messages
        # messages=[
        #     ChatMessage(
        #         role=MessageRole.USER,
        #         content="什么是 AI Agent"
        #     ),
        #     ChatMessage(
        #         role=MessageRole.ASSISTANT,
        #         content="AI Agent 是指能够与人类进行自然语言交互的智能体，它可以执行各种任务。"
        #     )
        # ]
    )
