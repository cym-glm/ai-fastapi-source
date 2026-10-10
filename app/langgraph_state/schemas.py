import operator
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class OrderInfo(TypedDict, total=False):
    order_id: str
    status: str
    status_text: str
    tracking_company: str | None
    tracking_no: str | None
    latest_event: str | None


class SourceInfo(TypedDict, total=False):
    document_id: str
    chunk_id: str
    source: str
    content_preview: str
    score: float


class ToolCallInfo(TypedDict, total=False):
    name: str
    args: dict
    id: str
    success: bool
    result_preview: str


class EcommerceAgentState(TypedDict):
    # 输入和对话
    user_question: str
    messages: Annotated[list[AnyMessage], add_messages]

    # 意图和槽位
    intent: Literal[
        "general",
        "query_order",
        "logistics",
        "refund",
        "after_sales",
        "human_service",
        "unknown",
    ]
    order_id: str | None
    tracking_no: str | None

    # 业务工具结果
    order_info: OrderInfo | None
    logistics_info: dict | None

    # RAG 结果
    policy_query: str | None
    policy_answer: str | None
    sources: Annotated[list[SourceInfo], operator.add]

    # 风险和人工确认
    risk_level: Literal["low", "medium", "high"]
    need_human_confirm: bool
    pending_action: str | None

    # 执行过程
    tool_calls: Annotated[list[ToolCallInfo], operator.add]
    logs: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]

    # 输出
    final_answer: str
    is_finished: bool