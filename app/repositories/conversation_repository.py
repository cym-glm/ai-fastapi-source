import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.message import Message


class ConversationRepository:
    async def create_conversation(
        self,
        db: AsyncSession,
        title: str,
        user_id: str | None = None,
    ) -> Conversation:
        conversation = Conversation(
            id=f"c_{uuid.uuid4().hex[:8]}",
            title=title,
            user_id=user_id,
            status="active",
        )

        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

        return conversation

    async def list_conversations(
        self,
        db: AsyncSession,
        user_id: str | None = None,
        limit: int = 20,
    ) -> list[Conversation]:
        stmt = (
            select(Conversation)
            .where(Conversation.status == "active")
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )

        if user_id:
            stmt = stmt.where(Conversation.user_id == user_id)

        result = await db.execute(stmt)

        return list(result.scalars().all())

    async def get_conversation(
        self,
        db: AsyncSession,
        conversation_id: str,
    ) -> Conversation | None:
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.status == "active",
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    async def add_message(
        self,
        db: AsyncSession,
        conversation_id: str,
        role: str,
        content: str,
        model: str | None = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
    ) -> Message:
        message = Message(
            id=f"m_{uuid.uuid4().hex[:8]}",
            conversation_id=conversation_id,
            role=role,
            content=content,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

        db.add(message)
        await db.commit()
        await db.refresh(message)

        return message

    async def get_messages(
        self,
        db: AsyncSession,
        conversation_id: str,
        limit: int = 50,
    ) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())

    async def archive_conversation(
        self,
        db: AsyncSession,
        conversation_id: str,
    ) -> bool:
        conversation = await self.get_conversation(
            db=db,
            conversation_id=conversation_id,
        )

        if not conversation:
            return False

        conversation.status = "archived"

        await db.commit()

        return True


conversation_repository = ConversationRepository()