from pydantic import BaseModel, Field

from langgraph.graph import END, START, StateGraph


class PydanticQAState(BaseModel):
    question: str = Field(..., min_length=1, description="问题")
    answer: str = Field(..., description="答案")


def generate_answer_node(state: PydanticQAState) -> dict:
    return {
        "answer": f"{state.question} 的答案是：{state.answer}"
    }


def build_graph():
    graph = StateGraph(PydanticQAState)

    graph.add_node("answer", generate_answer_node)
    graph.add_edge(START, "answer")
    graph.add_edge("answer", END)
    return graph.compile()


def main():
    app = build_graph()
    res = app.invoke({"question": "你是谁", "answer": "我是你的AI助手"})
    print(res)

if __name__ == "__main__":
    main()
