import uuid

from app.repositories.conversation_repository import conversation_repository
from app.schemas.chat import ChatRequest, MessageRole,ChatMessage
from app.schemas.conversation import ConversationResponse, ConversationMessagesResponse, ConversationCreateRequest


async def create_conversation_mesasge(request: ConversationCreateRequest) -> ConversationResponse:
    conversation_id=f"c_{uuid.uuid4().hex[:6]}"
    conversation = await conversation_repository.create(conversation_id, request)
    return ConversationResponse(
        conversation_id=conversation["conversation_id"],
        tilte=conversation["title"]
    )


async def get_conversation_mesage(conversation_id: str) -> ConversationMessagesResponse:
    messages = await conversation_repository.get_messages(conversation_id)
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
