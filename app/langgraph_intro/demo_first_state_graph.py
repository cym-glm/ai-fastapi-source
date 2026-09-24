
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

class SimpleState(TypedDict):
    user_question: str
    answer: str

def answer_node(state:SimpleState ) -> dict:
    question = state["user_question"]

    return {
        "answer":f"你问的是：{question},这是LangGraph的第一个阶段回答" 
    }


def build_graph():
    # 定义State  
    # 定义Node
    # 定义Edge
    # complie编译 ---- invoke
    graph = StateGraph(SimpleState)
    graph.add_node("answer", answer_node)
    graph.add_edge(START, "answer")
    graph.add_edge("answer", END)

    return graph.compile()

def main():
    app = build_graph()

    result = app.invoke({
        "user_question": "为什么需要LangGraph",
        "answer": "",
    })
    print(result)

if __name__ == "__main__":
    main()

