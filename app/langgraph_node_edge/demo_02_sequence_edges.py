from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class SequenceState(TypedDict):
    user_question: str
    intent: str
    order_id: str | None
    final_answer: str


def classify_intent_node(state: SequenceState) -> dict:
    question = state["user_question"]

    if "订单" in question:
        intent = "query_order"
    else:
        intent = "general"

    return {
        "intent": intent
    }


def extract_order_id_node(state: SequenceState) -> dict:
    question = state["user_question"]

    if "10001" in question:
        return {"order_id": "10001"}

    return {"order_id": None}


def answer_node(state: SequenceState) -> dict:
    return {
        "final_answer": (
            f"意图：{state['intent']}，"
            f"订单号：{state['order_id']}"
        )
    }


def build_graph():
    graph = StateGraph(SequenceState)

    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("extract_order_id", extract_order_id_node)
    graph.add_node("answer", answer_node)

    graph.add_edge(START, "classify_intent")
    graph.add_edge("classify_intent", "extract_order_id")
    graph.add_edge("extract_order_id", "answer")
    graph.add_edge("answer", END)

    return graph.compile()


def main():
    app = build_graph()

    result = app.invoke({
        "user_question": "帮我查一下订单 10001。",
        "intent": "unknown",
        "order_id": None,
        "final_answer": "",
    })

    print(result)


if __name__ == "__main__":
    main()