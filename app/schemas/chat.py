
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum
from typing import Any
from app.core.config import settings


class GenerateTitleRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="标题内容")

class GenerateTitleResponse(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="生成的标题")


class MessageRole(str, Enum):  # {role: user}
    SYSTEM = "system"  # 系统提示词 用来定义AI的身份和规则
    USER = "user"  # 用户输入
    ASSISTANT = "assistant" # AI的回复
    TOOL = "tool" # 工具调用

#  {"role": "user", "content": "Hello, how are you?"}
class ChatMessage(BaseModel):
    role: MessageRole = Field(..., description="Role of the message")
    content: str = Field(..., min_length=1, max_length=500, description="Content of the message")


class TokenUsage(BaseModel):
    prompt_tokens: int = Field(default=0, ge=0, description="Number of tokens in the prompt")
    completion_tokens: int = Field(default=0, ge=0, description="Number of tokens in the completion")
    total_tokens: int = Field(default=0, ge=0, description="Total number of tokens used")


class SourceDocument(BaseModel):
    document_id: str = Field(..., min_length=1, max_length=500, description="Document ID")
    title: str = Field(..., description="Document title")
    content: str = Field(..., min_length=1, max_length=500, description="Document content")
    score: float = Field(0.0, ge=0, le=1, description="Score of the document")
    metadata: dict[str, Any] = Field({}, description="Metadata of the document")


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    messages: list[ChatMessage] = Field(..., min_length=1, description="对话消息列表")

    model: str = Field("gpt-3.5-turbo", description="Model to use")
    temperature: float = Field(default=0/7, ge=0, le=2, description="Temperature for the model")
    stream: bool = Field(False, description="Stream the response")
    session_id: str | None = Field(None, description="Session ID")
    user_id: str | None = Field(None, description="User ID")
    metadata: dict[str, Any] = Field(default_factory=dict, description="扩展元数据")

    @field_validator("model")
    @classmethod
    def validate_model(cls, v):
        # supported_models = ["gpt-3.5-turbo", "gpt-4", "deepseek-chat", "qwen-72e"]
        if v not in settings.supported_model_list:
            raise ValueError (f"Unsupported model: {v}")
        return v

class ChatResponse(BaseModel):
    answer: str = Field(..., description="Response from the model")
    model: str = Field(..., description="Model used")
    # 前端继续追问的时候要带上之前的对话上下文
    session_id: str | None = Field(None, description="Session ID")
    # 用户消息反馈 点赞 踩菜
    message_id: str | None = Field(None, description="Message ID")
    # 模型调用详情 比如用了多少tokens
    usage: TokenUsage | None = Field(default_factory=TokenUsage, description="Token usage")
    # RAG 引用来源
    sources: list[SourceDocument] = Field(default_factory=list, description="引用来源")
    # 链路追踪ID 日志追踪ID
    trace_id: str | None = Field(None, description="链路追踪Trace ID")
