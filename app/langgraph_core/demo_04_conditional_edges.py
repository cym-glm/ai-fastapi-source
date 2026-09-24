from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class IntentState(TypedDict):
    user_question: str
    intent: str
    answer: str


def classify_intent_node(state: IntentState) -> dict:
    question = state["user_question"]

    if "退款" in question:
        intent = "refund"
    elif "订单" in question or "物流" in question:
        intent = "order"
    else:
        intent = "general"

    return {
        "intent": intent
    }


def route_by_intent(
    state: IntentState,
) -> Literal["general", "order", "refund"]:
    return state["intent"]  # type: ignore[return-value]


def general_node(state: IntentState) -> dict:
    return {
        "answer": "这是普通问题，走普通聊天。"
    }


def order_node(state: IntentState) -> dict:
    return {
        "answer": "这是订单问题，应该查询订单工具。"
    }


def refund_node(state: IntentState) -> dict:
    return {
        "answer": "这是退款问题，应该查询订单状态和退款规则。"
    }


def build_graph():
    graph = StateGraph(IntentState)

    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("general_node", general_node)
    graph.add_node("order_node", order_node)
    graph.add_node("refund_node", refund_node)

    graph.add_edge(START, "classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "general": "general_node",
            "order": "order_node",
            "refund": "refund_node",
        },
    )

    graph.add_edge("general_node", END)
    graph.add_edge("order_node", END)
    graph.add_edge("refund_node", END)

    return graph.compile()


def main():
    app = build_graph()

    questions = [
        "你好，介绍一下 LangGraph。",
        "帮我查一下订单 10001。",
        "我的订单没发货，可以退款吗？",
    ]

    for question in questions:
        result = app.invoke({
            "user_question": question,
            "intent": "",
            "answer": "",
        })

        print("question:", question)
        print("intent:", result["intent"])
        print("answer:", result["answer"])
        print("=" * 80)


if __name__ == "__main__":
    main()