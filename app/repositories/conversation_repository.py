import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import ChatMessage, MessageRole
from app.schemas.conversation import ConversationCreateRequest


class ConversationRepository:
    async def create(
        self,
        db: AsyncSession,
        request: ConversationCreateRequest,
        user_id: str | None = None,
    ) -> Conversation:
        conversation = Conversation(
            id=f"c_{uuid.uuid4().hex[:8]}",
            title=request.title,
            user_id=user_id,
        )
        
        # 数据库存储
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

        return conversation

    async def get_messages(
        self,
        db: AsyncSession,
        conversation_id: str,
    ) -> list[ChatMessage]:
        # 查询语句，按创建时间升序排列
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )

        result = await db.execute(stmt)

        messages = result.scalars().all()

        return [
            ChatMessage(
                role=MessageRole(message.role),
                content=message.content,
            )
            for message in messages
        ]

    async def add_message(
        self,
        db: AsyncSession,
        conversation_id: str,
        role: str,
        content: str,
        model: str | None = None,
    ) -> Message:
        message = Message(
            id=f"m_{uuid.uuid4().hex[:8]}",
            conversation_id=conversation_id,
            role=role,
            content=content,
            model=model,
        )

        # 数据库存储 
        db.add(message)
        await db.commit()
        await db.refresh(message)

        return message


conversation_repository = ConversationRepository()