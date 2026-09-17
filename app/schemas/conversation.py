from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.chat import ChatMessage


class ConversationStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ConversationCreateRequest(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="会话标题",
    )


class ConversationResponse(BaseModel):
    conversation_id: str = Field(..., description="会话 ID")
    title: str = Field(..., description="会话标题")
    status: ConversationStatus = Field(
        default=ConversationStatus.ACTIVE,
        description="会话状态",
    )
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse] = Field(
        default_factory=list,
        description="会话列表",
    )


class ConversationMessagesResponse(BaseModel):
    conversation_id: str = Field(..., description="会话 ID")
    messages: list[ChatMessage] = Field(
        default_factory=list,
        description="消息列表",
    )