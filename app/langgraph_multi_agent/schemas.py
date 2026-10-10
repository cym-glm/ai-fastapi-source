import operator
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.graph.message import add_messages


class AgentTraceItem(TypedDict, total=False):
    agent_name: str
    input_summary: str
    output_summary: str
    next_agent: str | None
    reason: str | None


class WorkerResult(TypedDict, total=False):
    agent_name: str
    success: str
    content: str
    data: dict
    confidence: float


class MultiAgentState(TypedDict):
    user_question: str
    messages: Annotated[list[AnyMessage], add_messages]
    task_type: Literal[
        "general",
        "ecommerce",
        "data_analysis",
        "research",
        "unknown",
    ]
    plan: Annotated[list[str], operator.add]
    current_agent: str | None
    next_agent: str | None
    active_agent: str | None

    order_result: WorkerResult | None
    refund_result: WorkerResult | None
    rag_result: WorkerResult | None
    sql_result: WorkerResult | None
    analysis_result: WorkerResult | None
    chart_result: WorkerResult | None
    report_result: WorkerResult | None
    review_result: WorkerResult | None

    final_answer: str
    is_finished: bool

    retry_count: int
    max_retry: int

    agent_trace: Annotated[list[AgentTraceItem], operator.add]
    logs: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]

def create_initial_multi_agent_state(user_question: str) -> MultiAgentState:
    return  {
        "user_question": user_question,
        "messages": [
            HumanMessage(content=user_question)
        ],

        "task_type": "unknown",

        "plan": [],

        "current_agent": None,
        "next_agent": None,
        "active_agent": None,

        "order_result": None,
        "refund_result": None,
        "rag_result": None,
        "sql_result": None,
        "analysis_result": None,
        "chart_result": None,
        "report_result": None,
        "review_result": None,

        "final_answer": "",
        "is_finished": False,

        "retry_count": 0,
        "max_retry": 2,

        "agent_trace": [],
        "logs": [],
        "errors": [],
    }
