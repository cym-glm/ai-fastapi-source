from typing import TypedDict, Literal

from langgraph.graph import END, START, StateGraph


class BasicRouteState(TypedDict):
    user_question: str
    answer_type: str
    final_answer: str

def classify_node(state: BasicRouteState) -> dict:
    if "代码" in state["answer_type"]:
        return {"answer_type": "code"}
    else:
        return {"answer_type": "text"}


def route_answer_type(
    state: BasicRouteState,
) -> Literal[Literal["code", "text"]]:
    return state["answer_type"]


def text_answer_node(state: BasicRouteState) -> dict:
    """
    文字回答节点。

    作为 LangGraph 图中的文字类回答处理节点，负责生成文字解释类型的最终回答。
    该节点由条件路由（route_answer_type）在回答类型为 "text" 时被调度执行。

    Args:
        state: 当前图的状态，包含用户问题（user_question）、
            回答类型（answer_type）和最终答案（final_answer）等字段。

    Returns:
        dict: 状态更新字典，键 "final_answer" 对应文字解释类回答内容。
    """
    return {"final_answer": "这个是文字解释回答"}

def code_answer_node(state: BasicRouteState) -> dict:
    return {"final_answer": "这个是代码回答"}



def build_graph():
    graph = StateGraph(BasicRouteState)

    graph.add_node("classify", classify_node)
    graph.add_node("text_answer", text_answer_node)
    graph.add_node("code_answer", code_answer_node)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges("classify", route_answer_type, {
        "code": "code_answer",
        "text": "text_answer",
    })
    graph.add_edge("code_answer", END)
    graph.add_edge("text_answer", END)

    return graph.compile()


def main():
    app = build_graph()  # 编译流程图，得到可执行的应用
    questions = [
        "解释一下 LangGraph。",  # 文字类问题，应路由到 text_answer
        "给我一段 LangGraph 代码。",  # 含“代码”，应路由到 code_answer
    ]

    for question in questions:
        result = app.invoke({
            "user_question": question,
            "answer_type": "",
            "final_answer": "",
        })
        print("question:", question)
        print("answer_type:", result["answer_type"])
        print("final_answer:", result["final_answer"])
        print("=" * 80)

if __name__ == "__main__":
    main()

