
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class LessonState(TypedDict):
    topic: str
    outline: str
    script: str
    summary: str


def generate_outline_node(state: LessonState) -> dict:
    return {
        "outline": f"《{state['topic']}》课程大纲：概念、代码、项目、总结。"
    }


def generate_script_node(state: LessonState) -> dict:
    return {
        "script": f"根据大纲生成口播稿：{state['outline']}"
    }


def generate_summary_node(state: LessonState) -> dict:
    return {
        "summary": f"本节课围绕 {state['topic']}，完成了大纲和口播稿。"
    }


def build_graph():
    graph = StateGraph(LessonState)

    graph.add_node("generate_outline", generate_outline_node)
    graph.add_node("generate_script", generate_script_node)
    graph.add_node("generate_summary", generate_summary_node)

    graph.add_edge(START, "generate_outline")
    graph.add_edge("generate_outline", "generate_script")
    graph.add_edge("generate_script", "generate_summary")
    graph.add_edge("generate_summary", END)

    return graph.compile()


def main():
    app = build_graph()

    result = app.invoke({
        "topic": "LangGraph 核心概念",
        "outline": "",
        "script": "",
        "summary": "",
    })

    print(result)


if __name__ == "__main__":
    main()