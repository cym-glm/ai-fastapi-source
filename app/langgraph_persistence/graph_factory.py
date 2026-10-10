from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from app.langgraph_persistence.schemas import PersistenceState


def classify_intent_node(state: PersistenceState) -> dict:
    question = state["user_question"]

    if "退款" in question or state.get("intent") == "refund":
        intent = "refund"
    elif "订单" in question:
        intent = "query_order"
    elif "人工" in question:
        intent = "human_service"
    else:
        intent = "general"

    return {
        "intent": intent,
        "logs": [f"classify_intent：intent={intent}"],
    }


def extract_order_id_node(state: PersistenceState) -> dict:
    question = state["user_question"]

    if "10001" in question:
        order_id = "10001"
    elif "10002" in question:
        order_id = "10002"
    else:
        order_id = state.get("order_id")

    return {
        "order_id": order_id,
        "logs": [f"extract_order_id：order_id={order_id}"],
    }


def route_after_extract_order_id(
    state: PersistenceState,
) -> Literal["ask_order_id", "query_order"]:
    if not state["order_id"]:
        return "ask_order_id"

    return "query_order"


def ask_order_id_node(state: PersistenceState) -> dict:
    answer = "请您提供订单号，我才能继续处理退款申请。"

    return {
        "need_user_input": True,
        "waiting_for": "order_id",
        "final_answer": answer,
        "is_finished": False,
        "messages": [
            AIMessage(content=answer)
        ],
        "logs": ["ask_order_id：等待用户补充订单号"],
    }


def query_order_node(state: PersistenceState) -> dict:
    order_id = state["order_id"]

    if order_id == "10001":
        order_status = "已发货"
    elif order_id == "10002":
        order_status = "已付款，待发货"
    else:
        order_status = "未查询到订单"

    return {
        "order_status": order_status,
        "need_user_input": False,
        "waiting_for": None,
        "logs": [f"query_order：order_status={order_status}"],
    }


def retrieve_policy_node(state: PersistenceState) -> dict:
    order_status = state["order_status"]

    if order_status == "已付款，待发货":
        policy_answer = "根据售后规则，订单未发货时可以申请取消订单并退款。"
    elif order_status == "已发货":
        policy_answer = "根据售后规则，订单已发货后，需要收到商品后再发起退货退款申请。"
    else:
        policy_answer = "当前订单状态无法确认退款规则，建议联系人工客服。"

    return {
        "policy_answer": policy_answer,
        "logs": ["retrieve_policy：完成售后规则判断"],
    }


def generate_answer_node(state: PersistenceState) -> dict:
    answer = (
        f"您的订单当前状态是：{state['order_status']}。"
        f"{state['policy_answer']}"
    )

    return {
        "final_answer": answer,
        "is_finished": True,
        "messages": [
            AIMessage(content=answer)
        ],
        "logs": ["generate_answer：最终回答完成"],
    }


def build_persistence_graph(
    checkpointer=None,
):
    graph = StateGraph(PersistenceState)

    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("extract_order_id", extract_order_id_node)
    graph.add_node("ask_order_id", ask_order_id_node)
    graph.add_node("query_order", query_order_node)
    graph.add_node("retrieve_policy", retrieve_policy_node)
    graph.add_node("generate_answer", generate_answer_node)

    graph.add_edge(START, "classify_intent")
    graph.add_edge("classify_intent", "extract_order_id")

    graph.add_conditional_edges(
        "extract_order_id",
        route_after_extract_order_id,
        {
            "ask_order_id": "ask_order_id",
            "query_order": "query_order",
        },
    )

    graph.add_edge("query_order", "retrieve_policy")
    graph.add_edge("retrieve_policy", "generate_answer")

    graph.add_edge("ask_order_id", END)
    graph.add_edge("generate_answer", END)

    return graph.compile(checkpointer=checkpointer)


def build_memory_graph():
    checkpointer = InMemorySaver()

    return build_persistence_graph(
        checkpointer=checkpointer,
    )


def add_user_message_to_state(
    user_question: str,
) -> dict:
    return {
        "user_question": user_question,
        "messages": [
            HumanMessage(content=user_question)
        ],
    }