from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class LoopState(TypedDict):
    user_question: str
    draft: str
    review_result: str
    retry_count: int
    final_answer: str


def generate_draft_node(state: LoopState) -> dict:
    retry_count = state["retry_count"]

    if retry_count == 0:
        draft = "这是一个很粗糙的回答。"
    else:
        draft = "这是一个更完整、更清晰的回答。"

    return {
        "draft": draft
    }


def review_node(state: LoopState) -> dict:
    if "粗糙" in state["draft"] and state["retry_count"] < 1:
        return {
            "review_result": "need_refine",
            "retry_count": state["retry_count"] + 1,
        }

    return {
        "review_result": "pass"
    }


def route_after_review(
    state: LoopState,
) -> Literal["refine", "finish"]:
    if state["review_result"] == "need_refine":
        return "refine"

    return "finish"


def finish_node(state: LoopState) -> dict:
    return {
        "final_answer": state["draft"]
    }


def build_graph():
    graph = StateGraph(LoopState)

    graph.add_node("generate_draft", generate_draft_node)
    graph.add_node("review", review_node)
    graph.add_node("finish", finish_node)

    graph.add_edge(START, "generate_draft")
    graph.add_edge("generate_draft", "review")

    graph.add_conditional_edges(
        "review",
        route_after_review,
        {
            "refine": "generate_draft",
            "finish": "finish",
        },
    )

    graph.add_edge("finish", END)

    return graph.compile()


def main():
    app = build_graph()

    result = app.invoke(
        {
            "user_question": "解释一下 LangGraph Node 与 Edge。",
            "draft": "",
            "review_result": "",
            "retry_count": 0,
            "final_answer": "",
        },
        # "recursion_limit": 10,
        config={
            "recursion_limit": 10
        },
    )

    print(result)


if __name__ == "__main__":
    main()