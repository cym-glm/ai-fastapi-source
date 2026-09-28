from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.langgraph_routing.mock_services import create_initial_state
from app.langgraph_routing.schemas import RoutingState


def classify_intent_node(state: RoutingState) -> dict:
    question = state["user_question"]

    if "人工" in question:
        intent = "human_service"
    elif "退款" in question or "退货" in question:
        intent = "refund"
    elif "物流" in question:
        intent = "logistics"
    elif "订单" in question:
        intent = "query_order"
    else:
        intent = "general"

    return {
        "intent": intent,
        "logs": [f"classify_intent：识别到 intent={intent}"],
    }


def route_by_intent(
    state: RoutingState,
) -> Literal["general", "human", "need_order"]:
    intent = state["intent"]

    if intent == "general":
        return "general"

    if intent == "human_service":
        return "human"

    return "need_order"


def general_answer_node(state: RoutingState) -> dict:
    return {
        "final_answer": "这是普通问题，可以走普通 Chat。",
        "is_finished": True,
        "logs": ["general_answer：完成普通回答"],
    }


def transfer_human_node(state: RoutingState) -> dict:
    return {
        "final_answer": "我已经为您转接人工客服，请稍等。",
        "is_finished": True,
        "logs": ["transfer_human：完成转人工"],
    }


def need_order_node(state: RoutingState) -> dict:
    return {
        "final_answer": "这个问题需要订单号，后续会进入订单号提取流程。",
        "logs": ["need_order：进入订单相关流程"],
    }


def build_graph():
    graph = StateGraph(RoutingState)

    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("general_answer", general_answer_node)
    graph.add_node("transfer_human", transfer_human_node)
    graph.add_node("need_order", need_order_node)

    graph.add_edge(START, "classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "general": "general_answer",
            "human": "transfer_human",
            "need_order": "need_order",
        },
    )

    graph.add_edge("general_answer", END)
    graph.add_edge("transfer_human", END)
    graph.add_edge("need_order", END)

    return graph.compile()


def main():
    app = build_graph()

    questions = [
        "你好，介绍一下 LangGraph。",
        "我要找人工客服。",
        "帮我查一下订单 10001。",
        "我的订单还没发货，可以退款吗？",
    ]

    for question in questions:
        result = app.invoke(create_initial_state(question))

        print("question:", question)
        print("intent:", result["intent"])
        print("final_answer:", result["final_answer"])
        print("logs:", result["logs"])
        print("=" * 80)


if __name__ == "__main__":
    main()