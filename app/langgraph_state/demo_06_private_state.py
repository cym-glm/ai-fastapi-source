
from typing import Annotated, TypedDict

from langgraph.graph import MessagesState, END, START, StateGraph



class InputState(TypedDict):
    question: str


class OverallState(TypedDict):
    question: str
    internal_query: str
    raw_docs: list[str]
    answer: str



class OutputState(TypedDict):
    answer: str
    

def rewrite_query_node(state: OverallState) -> dict:
    return {
        "internal_query": f"知识库检索：{state['question']}"
    }


def retrieve_docs_node(state: OverallState) -> dict:
    return {
        "raw_docs": [
            "订单未发货时，用户可以申请取消订单并退款。",
            "订单已发货后，需要收到商品后再申请退货退款。",
        ]
    }

def answer_node(state: OverallState) -> dict:
    docs = "\n".join(state["raw_docs"])
    return {
        "answer": (
            f"根据内部检索到的规则：\n{docs}\n\n"
            f"针对你的问题：{state['question']}，未发货订单通常可以申请取消并退款。"
        )
    }
        

def build_graph():
    graph = StateGraph(
        OverallState,
        input_schema=InputState,
        output_schema=OutputState
    )

    graph.add_node("rewrite_query", rewrite_query_node)
    graph.add_node("retrieve_docs", retrieve_docs_node)
    graph.add_node("answer", answer_node)

    graph.add_edge(START, "rewrite_query")
    graph.add_edge("rewrite_query", "retrieve_docs")
    graph.add_edge("retrieve_docs", "answer")
    graph.add_edge("answer", END)

    return graph.compile()


def main():
    app = build_graph()
    res = app.invoke({
        "question": "我想退款"
    })
    print(res)

if __name__ == "__main__":
    main()