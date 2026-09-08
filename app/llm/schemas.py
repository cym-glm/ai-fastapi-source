from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class LLMProviderName(str, Enum):
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    KIMI = "kimi"


class LLMRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class LLMMessage(BaseModel):
    role: LLMRole = Field(..., description="消息角色")
    content: str = Field(..., min_length=1, description="消息内容")


class LLMRequest(BaseModel):
    model: str = Field(..., description="模型名称")
    messages: list[LLMMessage] = Field(..., min_length=1, description="消息列表")
    temperature: float = Field(default=0.7, ge=0, le=2, description="温度")
    max_tokens: int | None = Field(default=None, ge=1, description="最大输出 token")
    stream: bool = Field(default=False, description="是否流式输出")
    metadata: dict[str, Any] = Field(default_factory=dict, description="扩展信息")


class LLMUsage(BaseModel):
    prompt_tokens: int = Field(default=0, ge=0, description="输入 token")
    completion_tokens: int = Field(default=0, ge=0, description="输出 token")
    total_tokens: int = Field(default=0, ge=0, description="总 token")


class LLMResponse(BaseModel):
    provider: LLMProviderName = Field(..., description="模型供应商")
    model: str = Field(..., description="模型名称")
    content: str = Field(..., description="模型输出内容")
    usage: LLMUsage = Field(default_factory=LLMUsage, description="Token 用量")
    raw_response: dict[str, Any] = Field(default_factory=dict, description="原始响应")


class LLMStreamChunk(BaseModel):
    provider: LLMProviderName = Field(..., description="模型供应商")
    model: str = Field(..., description="模型名称")
    content: str = Field(default="", description="当前增量内容")
    finish_reason: str | None = Field(default=None, description="结束原因")
    usage: LLMUsage | None = Field(default=None, description="Token 用量")
    raw_chunk: dict[str, Any] = Field(default_factory=dict, description="原始 chunk")