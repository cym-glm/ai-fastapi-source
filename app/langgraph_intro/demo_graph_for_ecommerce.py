
from typing import Literal, TypedDict

from langgraph.graph import StateGraph, END, START


class EcommerceGraphState(TypedDict):
    user_question: str
    intent: str
    order_id: str | None
    order_status: str | None
    policy_answer: str | None
    final_answer: str


def classify_intent_node(state: EcommerceGraphState) -> dict:
    question = state["user_question"]

    if "退款" in question:
        return {"intent": "refund"}

    if "订单" in question or "物流" in question:
        return {"intent": "order"}

    return {"intent": "general"}


def extract_order_id_node(state: EcommerceGraphState) -> dict:
    question = state["user_question"]

    if "10001" in question:
        return {"order_id": "10001"}

    if "10002" in question:
        return {"order_id": "10002"}

    return {"order_id": None}


def route_after_extract_order_id(
    state: EcommerceGraphState,
) -> Literal["ask_order_id", "query_order"]:
    if not state.get("order_id"):
        return "ask_order_id"

    return "query_order"


def query_order_node(state: EcommerceGraphState) -> dict:
    order_id = state["order_id"]

    if order_id == "10001":
        return {"order_status": "已发货"}

    if order_id == "10002":
        return {"order_status": "已付款，待发货"}

    return {"order_status": "未查询到订单"}


def retrieve_policy_node(state: EcommerceGraphState) -> dict:
    order_status = state.get("order_status")

    if order_status == "已付款，待发货":
        return {
            "policy_answer": "根据售后规则，订单未发货时可以申请取消订单并退款。"
        }

    if order_status == "已发货":
        return {
            "policy_answer": "根据售后规则，订单已发货后，需要收到商品后再发起退货退款申请。"
        }

    return {
        "policy_answer": "当前状态无法确认退款规则，建议转人工客服。"
    }


def ask_order_id_node(state: EcommerceGraphState) -> dict:
    return {
        "final_answer": "请您提供订单号，我帮您继续查询和判断。"
    }


def generate_general_answer_node(state: EcommerceGraphState) -> dict:
    return {
        "final_answer": "这是一个普通问题，可以走普通 Chat。"
    }


def generate_order_answer_node(state: EcommerceGraphState) -> dict:
    return {
        "final_answer": f"您的订单当前状态是：{state.get('order_status')}。"
    }


def generate_refund_answer_node(state: EcommerceGraphState) -> dict:
    return {
        "final_answer": (
            f"您的订单当前状态是：{state.get('order_status')}。"
            f"{state.get('policy_answer')}"
        )
    }


def route_by_intent(
    state: EcommerceGraphState,
) -> Literal["general", "order_or_refund"]:
    if state["intent"] == "general":
        return "general"

    return "order_or_refund"


def route_after_query_order(
    state: EcommerceGraphState,
) -> Literal["retrieve_policy", "generate_order_answer"]:
    if state["intent"] == "refund":
        return "retrieve_policy"

    return "generate_order_answer"


def build_graph():
    
    graph = StateGraph(EcommerceGraphState)

    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("extract_order_id", extract_order_id_node)
    graph.add_node("query_order", query_order_node)
    graph.add_node("retrieve_policy", retrieve_policy_node)
    graph.add_node("ask_order_id", ask_order_id_node)
    graph.add_node("generate_general_answer", generate_general_answer_node)
    graph.add_node("generate_order_answer", generate_order_answer_node)
    graph.add_node("generate_refund_answer", generate_refund_answer_node)

    graph.add_edge(START, "classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "general": "generate_general_answer",
            "order_or_refund": "extract_order_id",
        },
    )

    graph.add_conditional_edges(
        "extract_order_id",
        route_after_extract_order_id,
        {
            "ask_order_id": "ask_order_id",
            "query_order": "query_order",
        },
    )

    graph.add_conditional_edges(
        "query_order",
        route_after_query_order,
        {
            "retrieve_policy": "retrieve_policy",
            "generate_order_answer": "generate_order_answer",
        },
    )

    graph.add_edge("retrieve_policy", "generate_refund_answer")

    graph.add_edge("ask_order_id", END)
    graph.add_edge("generate_general_answer", END)
    graph.add_edge("generate_order_answer", END)
    graph.add_edge("generate_refund_answer", END)

    return graph.compile()


def main():
    app = build_graph()

    questions = [
        "你好，介绍一下 LangGraph。",
        "帮我查一下订单 10001。",
        "我的订单 10002 还没发货，可以退款吗？",
        "我要退款，但是忘记订单号了。",
    ]

    for question in questions:
        result = app.invoke({
            "user_question": question,
            "intent": "",
            "order_id": None,
            "order_status": None,
            "policy_answer": None,
            "final_answer": "",
        })

        print("question:", question)
        print("final_answer:", result["final_answer"])
        print("full_state:", result)
        print("=" * 80)


if __name__ == "__main__":
    main()