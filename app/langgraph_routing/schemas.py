import operator
from typing import Annotated, Literal, TypedDict


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


class RoutingToolCall(TypedDict, total=False):
    name: str
    args: dict
    success: bool
    result_preview: str


class RoutingState(TypedDict):
    user_question: str

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
    order_info: OrderInfo | None
    # RAG 
    need_policy: bool
    policy_query: str | None
    policy_answer: str | None
    sources: Annotated[list[SourceInfo], operator.add]

    tool_success: bool
    tool_calls: Annotated[list[RoutingToolCall], operator.add]
    # human in the loop
    rag_hit: bool
    need_human_confirm: bool
    risk_level: Literal["low", "medium", "high"]
    pending_action: str | None

    retry_count: int
    max_retry: int

    final_answer: str
    is_finished: bool

    logs: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]