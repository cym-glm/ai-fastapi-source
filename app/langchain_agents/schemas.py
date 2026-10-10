from typing import Any
from pydantic import BaseModel, Field

class AgentMessageItem(BaseModel):
    type: str = Field(..., description="消息类型")
    content: str = Field(defalut="", description="消息内容")
    name: str  | None = Field(default=None, description="工具名称或消息名称")
    tool_calls: list[dict[str,Any]] | None = Field(default_factory=list, description="工具调用列表")
    tool_call_id: str | None = Field(default=None, description="工具调用ID")

class AgentRunResponse(BaseModel):
    answer: str = Field(..., description="回答内容")
    messages: list[AgentMessageItem] = Field(default_factory=list, description="agent执行过程中的消息列表")
    used_tools: bool= Field(default= False, description="示范使用了工具")
    tool_calls: list[dict[str,Any]] | None = Field(default_factory=list, description="执行过程中出现的工具调用列表")
    metadata: dict[str, Any] | None = Field(default_factory=dict, description="额外的元数据")


class AgentStreamEvent(BaseModel):
    event: str = Field(..., description="事件类型")
    data: list[str, Any] = Field(default_factory=list, description="事件数据")
