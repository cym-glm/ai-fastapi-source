import operator
from dataclasses import dataclass
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.graph.message import add_messages


class OrderInfo(TypedDict, total=False):
    order_id: str
    status: str
    status_text: str
    amount: float
    currency: str
    tracking_company: str | None
    tracking_no: str | None
    latest_event: str | None


class SourceInfo(TypedDict, total=False):
    document_id: str
    chunk_id: str
    source: str
    content_preview: str
    score: float


class AgentTraceItem(TypedDict, total=False):
    node_name: str
    input_summary: str
    output_summary: str
    route_to: str | None
    reason: str


class UserMemoryItem(TypedDict, total=False):
    key: str
    type: Literal["preference", "profile", "behavior", "note"]
    content: str
    confidence: float
    source: str


class HumanDecision(TypedDict, total=False):
    type: Literal["approve", "reject", "edit"]
    reviewer_id: str
    reason: str | None
    edited_payload: dict | None


class EcommerceAgentState(TypedDict):
    user_question: str
    messages: Annotated[list[AnyMessage], add_messages]

    intent: Literal[
        "general",
        "query_order",
        "logistics",
        "refund",
        "after_sales",
        "human_service",
        "remember_preference",
        "unknown",
    ]

    order_id: str | None
    order_info: OrderInfo | None

    policy_query: str | None
    policy_answer: str | None
    sources: Annotated[list[SourceInfo], operator.add]
    rag_hit: bool

    risk_level: Literal["low", "medium", "high"]
    need_human_confirm: bool
    pending_action: str | None
    pending_payload: dict | None
    human_decision: HumanDecision | None
    action_result: dict | None

    recalled_memories: Annotated[list[UserMemoryItem], operator.add]
    new_memories: Annotated[list[UserMemoryItem], operator.add]

    draft_answer: str
    final_answer: str
    is_finished: bool

    retry_count: int
    max_retry: int

    agent_trace: Annotated[list[AgentTraceItem], operator.add]
    logs: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]


@dataclass
class EcommerceAgentContext:
    tenant_id: str
    user_id: str
    conversation_id: str


def create_initial_state(
    user_question: str,
) -> EcommerceAgentState:
    return {
        "user_question": user_question,
        "messages": [
            HumanMessage(content=user_question)
        ],

        "intent": "unknown",

        "order_id": None,
        "order_info": None,

        "policy_query": None,
        "policy_answer": None,
        "sources": [],
        "rag_hit": False,

        "risk_level": "low",
        "need_human_confirm": False,
        "pending_action": None,
        "pending_payload": None,
        "human_decision": None,
        "action_result": None,

        "recalled_memories": [],
        "new_memories": [],

        "draft_answer": "",
        "final_answer": "",
        "is_finished": False,

        "retry_count": 0,
        "max_retry": 2,

        "agent_trace": [],
        "logs": [],
        "errors": [],
    }


def append_user_message(
    user_question: str,
) -> dict:
    return {
        "user_question": user_question,
        "messages": [
            HumanMessage(content=user_question)
        ],
    }