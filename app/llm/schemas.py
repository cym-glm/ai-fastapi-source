

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

class LLMRole(str, Enum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"
    TOOL = "tool"

class LLMMessage(BaseModel):
    role: LLMRole = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")

class LLMCRequest(BaseModel):
    model: str = Field(..., description="模型名称")
    messages: list[LLMMessage] = Field(..., min_length=1, description="消息列表")
    temperature: float = Field(default=0.7, description="温度参数，控制随机性")
    max_tokens: int | None = Field(default=None, description="最大生成token数")
    stream: bool = Field(default=False, description="是否流式返回")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")

class LLMUsage(BaseModel):
    prompt_tokens: int = Field(default=0, description="输入 token")
    completion_tokens: int = Field(default=0,description="输出 token")
    total_tokens: int = Field(default=0,description="总token")

class LLMResponse(BaseModel):
    model: str = Field(..., description="模型名称")
    content: str | None = Field(default=None, description="模型输出的内容")
    usage: LLMUsage = Field(default_factory=LLMUsage, description="token 使用情况")
    raw_response: dict[str, Any] | None = Field(default=None, description="原始返回")