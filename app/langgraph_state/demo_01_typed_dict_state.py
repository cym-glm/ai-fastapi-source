from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class QAState(TypedDict):
    question: str
    answer: str


def generate_answer_node(state: QAState) -> dict:

    return {
        "answer": f"{state['question']} 的答案是：{state['answer']}"
    }


def build_graph():
    graph = StateGraph(QAState)

    graph.add_node("answer", generate_answer_node)
    graph.add_edge(START, "answer")
    graph.add_edge("answer", END)
    return graph.compile()



def main():
    graph = build_graph()
    result = graph.invoke({
        "question": "你是谁",
        "answer": "我是你的AI助手，很高兴为你服务。"
    })
    print(result)

if __name__ == "__main__":
    main()