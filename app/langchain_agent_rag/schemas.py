from typing import Any

from pydantic import BaseModel, Field


class AgentRAGMessageItem(BaseModel):
    type: str = Field(..., description="消息类型")
    content: str = Field(default="", description="消息内容")
    name: str | None = Field(default=None, description="工具名称")
    tool_calls: list[dict[str, Any]] = Field(
        default_factory=list,
        description="工具调用列表",
    )
    tool_call_id: str | None = Field(
        default=None,
        description="工具调用 ID",
    )


class AgentRAGSource(BaseModel):
    document_id: str | None = Field(default=None)
    chunk_id: str | None = Field(default=None)
    source: str | None = Field(default=None)
    content_preview: str = Field(default="")


class AgentRAGRunResponse(BaseModel):
    answer: str = Field(..., description="最终回答")

    used_tools: bool = Field(
        default=False,
        description="是否使用了工具",
    )

    used_rag: bool = Field(
        default=False,
        description="是否使用了知识库检索",
    )

    tool_calls: list[dict[str, Any]] = Field(
        default_factory=list,
        description="工具调用列表",
    )

    messages: list[AgentRAGMessageItem] = Field(
        default_factory=list,
        description="Agent 执行消息",
    )

    sources: list[AgentRAGSource] = Field(
        default_factory=list,
        description="知识库引用来源",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="扩展信息",
    )