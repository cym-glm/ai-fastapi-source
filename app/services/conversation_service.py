import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.conversation_repository import conversation_repository
from app.schemas.chat import ChatRequest, MessageRole,ChatMessage
from app.schemas.conversation import ConversationResponse, ConversationMessagesResponse, ConversationCreateRequest


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
        conversation_id: str) -> ConversationMessagesResponse:
    
    messages = await conversation_repository.get_messages(
        db=db,
        conversation_id =conversation_id)
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
