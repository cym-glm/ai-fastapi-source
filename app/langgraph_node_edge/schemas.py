

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


class ToolCallInfo(TypedDict, total=False):
    name: str
    args: dict
    id: str
    success: bool
    result_preview: str


class EcommerceNodeEdgeState(TypedDict):
    user_question: str

    intent: Literal[
        "general",
        "query_order",
        "logistics",
        "refund",
        "human_service",
        "unknown",
    ]

    order_id: str | None
    order_info: OrderInfo | None

    policy_query: str | None
    policy_answer: str | None
    sources: Annotated[list[SourceInfo], operator.add]

    need_human_confirm: bool
    risk_level: Literal["low", "medium", "high"]
    pending_action: str | None

    tool_calls: Annotated[list[ToolCallInfo], operator.add]
    logs: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]

    final_answer: str
    retry_count: int
    is_finished: bool