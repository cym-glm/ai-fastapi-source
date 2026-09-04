

from app.schemas.chat import ChatMessage, MessageRole
from app.schemas.conversation import ConversationCreateRequest



class ConversationRepository:
    def __init__(self):
        self._conversations : dict[str, dict] = {}
        self._messages: dict[str, list[ChatMessage]] = {}

    async def create(self, conversation_id: str, request:ConversationCreateRequest) -> dict:
        conversation = {
            "conversation_id": conversation_id,
            "title":request.title
        }
        self._conversations[conversation_id] = conversation
        self._messages[conversation_id] = []
        return conversation

    async def get_messages(self, conversation_id: str) -> list[ChatMessage]:
        if conversation_id not in self._messages:
            return [
                ChatMessage(role=MessageRole.USER, content="什么是AI Agent开发？"),
                ChatMessage(role=MessageRole.ASSISTANT, content="AIAgent是能够自主执行任务的人工智能实体。它能够理解自然语言指令，并根据这些指令完成一系列的任务。例如，它可以用来编写代码、回答问题或者进行数据分析等。")
            ]
        return self._messages[conversation_id]

conversation_repository =  ConversationRepository()