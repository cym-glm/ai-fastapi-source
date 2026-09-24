import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class MultiAgentState(TypedDict):
    task: str
    plan: Annotated[list[str], operator.add]
    current_agent: str
    research_result: str | None
    analysis_result: str | None
    review_result: str | None
    final_report: str
    logs: Annotated[list[str], operator.add]


def planner_node(state: MultiAgentState) -> dict:
    return {
        "current_agent": "planner",
        "plan": [
            "检索行业资料",
            "分析核心趋势",
            "生成总结报告",
            "检查报告质量",
        ],
        "logs": ["planner：完成任务拆解"],
    }


def researcher_node(state: MultiAgentState) -> dict:
    return {
        "current_agent": "researcher",
        "research_result": "检索到 3 条与 AI Agent 平台相关的行业趋势。",
        "logs": ["researcher：完成资料检索"],
    }


def analyst_node(state: MultiAgentState) -> dict:
    return {
        "current_agent": "analyst",
        "analysis_result": "核心趋势是企业从单点 Chatbot 转向多 Agent 工作流平台。",
        "logs": ["analyst：完成趋势分析"],
    }


def reviewer_node(state: MultiAgentState) -> dict:
    return {
        "current_agent": "reviewer",
        "review_result": "报告结构完整，可以输出。",
        "logs": ["reviewer：完成质量检查"],
    }


def report_node(state: MultiAgentState) -> dict:
    return {
        "current_agent": "reporter",
        "final_report": (
            f"任务：{state['task']}\n"
            f"研究结果：{state['research_result']}\n"
            f"分析结论：{state['analysis_result']}\n"
            f"审核意见：{state['review_result']}"
        ),
        "logs": ["reporter：完成最终报告"],
    }


def build_graph():
    graph = StateGraph(MultiAgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("reporter", report_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "analyst")
    graph.add_edge("analyst", "reviewer")
    graph.add_edge("reviewer", "reporter")
    graph.add_edge("reporter", END)

    return graph.compile()


def main():
    app = build_graph()

    result = app.invoke({
        "task": "分析 AI Agent 平台趋势",
        "plan": [],
        "current_agent": "",
        "research_result": None,
        "analysis_result": None,
        "review_result": None,
        "final_report": "",
        "logs": [],
    })

    print("final_report:")
    print(result["final_report"])

    print("=" * 80)
    print("plan:")
    for item in result["plan"]:
        print("-", item)

    print("=" * 80)
    print("logs:")
    for log in result["logs"]:
        print("-", log)


if __name__ == "__main__":
    main()