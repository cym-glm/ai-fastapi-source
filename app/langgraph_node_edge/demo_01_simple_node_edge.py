from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class SimpleState(TypedDict):
    user_question: str
    final_answer: str


def answer_node(state: SimpleState) -> dict:
    return {
        "final_answer": f"你问的是：{state['user_question']}"
    }


def build_graph():
    graph = StateGraph(SimpleState)

    graph.add_node("answer", answer_node)

    graph.add_edge(START, "answer")
    graph.add_edge("answer", END)

    return graph.compile()


def main():
    app = build_graph()

    result = app.invoke({
        "user_question": "Node 和 Edge 是什么？",
        "final_answer": "",
    })

    print(result)


if __name__ == "__main__":
    main()