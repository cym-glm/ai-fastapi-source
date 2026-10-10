
from typing import Annotated, TypedDict

from langgraph.graph import MessagesState, END, START, StateGraph



def merge_list(
    old: list[str],
    new: list[str],
) -> list[str]: 
    res = list(old)
    for item in new:
        if item not in res:
            res.append(item)
    return res


class SourceState(TypedDict):
    question: str
    sources: Annotated[list[str], merge_list]
    answer: str

def retrieve_answer_node(state: SourceState) -> dict:
    return {
        "sources": ["https://www.baidu.com"]
    }
def retrieve_answer_doc_node(state: SourceState) -> dict:
    return {
        "sources": ["https://www.google.com", "https://www.baidu.com"]
    }

def answer_node(state: SourceState) -> dict:
    return {
        "answer": f"最终引用的来源：{", ".join(state["sources"])}"
    }

def build_graph():
    graph = StateGraph(SourceState)

    graph.add_node("retrieve", retrieve_answer_node)
    graph.add_node("retrieve_doc", retrieve_answer_doc_node)
    graph.add_node("answer", answer_node)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "retrieve_doc")
    graph.add_edge("retrieve_doc", "answer")
    graph.add_edge("retrieve", END)
    return graph.compile()


def main():
    app = build_graph()
    res = app.invoke({"question": "有几个网站", "answer": [], "answer": ""})
    print(res)

if __name__ == "__main__":
    main()

