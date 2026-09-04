from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from app.schemas.chat import ChatMessage


class ConversationStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    DELETED = "deleted"
    ARCHIVED = "archived"

class ConversationCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, description="会话标题")


class ConversationResponse(BaseModel):
    conversation_id: str = Field(..., description="会话ID")
    tilte: str = Field(..., description="会话标题")
    status: ConversationStatus = Field(default=ConversationStatus.ACTIVE, description="会话状态")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

class ConversationMessagesResponse(BaseModel):
    conversation_id: str = Field(..., description="会话ID")
    messages: list[ChatMessage] = Field(default_factory=list, description="消息列表")

