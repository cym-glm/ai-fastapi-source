import operator
from dataclasses import dataclass
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.graph.message import add_messages


class UserMemoryItem(TypedDict, total=False):
    key: str
    type: Literal["preference", "profile", "behavior", "note"]
    content: str
    confidence: float
    source: str


class MemoryState(TypedDict):
    user_question: str
    messages: Annotated[list[AnyMessage], add_messages]

    short_summary: str | None

    recalled_memories: Annotated[list[UserMemoryItem], operator.add]
    new_memories: Annotated[list[UserMemoryItem], operator.add]

    intent: Literal[
        "general",
        "remember_preference",
        "recall_preference",
        "ecommerce_service",
        "unknown",
    ]

    final_answer: str
    is_finished: bool

    logs: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]


@dataclass
class MemoryContext:
    user_id: str
    tenant_id: str = "tenant_001"


def create_initial_memory_state(
    user_question: str,
) -> MemoryState:
    return {
        "user_question": user_question,
        "messages": [
            HumanMessage(content=user_question)
        ],

        "short_summary": None,

        "recalled_memories": [],
        "new_memories": [],

        "intent": "unknown",

        "final_answer": "",
        "is_finished": False,

        "logs": [],
        "errors": [],
    }