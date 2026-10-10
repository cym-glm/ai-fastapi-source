import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class LogState(TypedDict):
    user_question: str
    logs: Annotated[list[str], operator.add]
    answer: str


def step_one_node(state: LogState) -> dict:
    return {
        "logs": ["step_one：开始分析用户问题。"]
    }


def step_two_node(state: LogState) -> dict:
    return {
        "logs": ["step_two：准备生成最终回答。"]
    }


def answer_node(state: LogState) -> dict:
    return {
        "logs": ["answer：回答生成完成。"],
        "answer": f"你问的是：{state['user_question']}",
    }


def build_graph():
    graph = StateGraph(LogState)

    graph.add_node("step_one", step_one_node)
    graph.add_node("step_two", step_two_node)
    graph.add_node("answer", answer_node)

    graph.add_edge(START, "step_one")
    graph.add_edge("step_one", "step_two")
    graph.add_edge("step_two", "answer")
    graph.add_edge("answer", END)

    return graph.compile()


def main():
    app = build_graph()

    result = app.invoke({
        "user_question": "Reducer 有什么作用？",
        "logs": [],
        "answer": "",
    })

    print("answer:", result["answer"])
    print("logs:")
    for log in result["logs"]:
        print("-", log)


if __name__ == "__main__":
    main()