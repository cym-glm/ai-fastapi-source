from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class RouteState(TypedDict):
    user_question: str
    intent: str
    final_answer: str


def classify_intent_node(state: RouteState) -> dict:
    question = state["user_question"]

    if "退款" in question:
        intent = "refund"
    elif "订单" in question:
        intent = "query_order"
    else:
        intent = "general"

    return {
        "intent": intent
    }


def route_by_intent(
    state: RouteState,
) -> Literal["general", "query_order", "refund"]:
    return state["intent"]  # type: ignore[return-value]


def general_answer_node(state: RouteState) -> dict:
    return {
        "final_answer": "这是普通问题，走普通 Chat。"
    }


def query_order_node(state: RouteState) -> dict:
    return {
        "final_answer": "这是订单查询问题，下一步应该调用订单工具。"
    }


def refund_node(state: RouteState) -> dict:
    return {
        "final_answer": "这是退款问题，下一步应该查订单状态和退款规则。"
    }


def build_graph():
    graph = StateGraph(RouteState)

    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("general_answer", general_answer_node)
    graph.add_node("query_order", query_order_node)
    graph.add_node("refund", refund_node)

    graph.add_edge(START, "classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "general": "general_answer",
            "query_order": "query_order",
            "refund": "refund",
        },
    )

    graph.add_edge("general_answer", END)
    graph.add_edge("query_order", END)
    graph.add_edge("refund", END)

    return graph.compile()


def main():
    app = build_graph()

    questions = [
        "你好，介绍一下 LangGraph。",
        "帮我查一下订单 10001。",
        "我的订单还没发货，可以退款吗？",
    ]

    for question in questions:
        result = app.invoke({
            "user_question": question,
            "intent": "unknown",
            "final_answer": "",
        })

        print("question:", question)
        print("intent:", result["intent"])
        print("final_answer:", result["final_answer"])
        print("=" * 80)


if __name__ == "__main__":
    main()