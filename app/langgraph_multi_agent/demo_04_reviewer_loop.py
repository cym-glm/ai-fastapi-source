from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.langgraph_multi_agent.schemas import (
    MultiAgentState,
    create_initial_multi_agent_state,
)


def writer_agent(state: MultiAgentState) -> dict:
    retry_count = state["retry_count"]

    if retry_count == 0:
        content = "Multi-Agent 就是多个 Agent 一起干活。"
    else:
        content = (
            "LangGraph Multi-Agent 是把复杂任务拆给多个专职 Agent，"
            "通过共享 State、Node、Edge 和条件路由协作完成。"
            "比如 Planner 负责拆任务，Worker 负责执行，Reviewer 负责检查质量。"
        )

    return {
        "current_agent": "writer_agent",
        "report_result": {
            "agent_name": "writer_agent",
            "success": True,
            "content": content,
            "data": {},
            "confidence": 0.7 if retry_count == 0 else 0.92,
        },
        "logs": [f"writer_agent：生成第 {retry_count + 1} 版回答"],
    }


def reviewer_agent(state: MultiAgentState) -> dict:
    report = state["report_result"] or {}
    content = report.get("content", "")

    if len(content) < 50 and state["retry_count"] < state["max_retry"]:
        return {
            "current_agent": "reviewer_agent",
            "review_result": {
                "agent_name": "reviewer_agent",
                "success": False,
                "content": "回答太短，需要补充定义、机制和例子。",
                "data": {
                    "passed": False,
                },
                "confidence": 0.9,
            },
            "retry_count": state["retry_count"] + 1,
            "logs": ["reviewer_agent：审核不通过，要求重写"],
        }

    return {
        "current_agent": "reviewer_agent",
        "review_result": {
            "agent_name": "reviewer_agent",
            "success": True,
            "content": "审核通过",
            "data": {
                "passed": True,
            },
            "confidence": 0.95,
        },
        "logs": ["reviewer_agent：审核通过"],
    }


def route_after_review(
    state: MultiAgentState,
) -> Literal["rewrite", "finish"]:
    review = state["review_result"] or {}
    data = review.get("data") or {}

    if not data.get("passed") and state["retry_count"] <= state["max_retry"]:
        return "rewrite"

    return "finish"


def finish_agent(state: MultiAgentState) -> dict:
    report = state["report_result"] or {}

    return {
        "current_agent": "finish_agent",
        "final_answer": report.get("content", ""),
        "is_finished": True,
        "logs": ["finish_agent：输出最终结果"],
    }


def build_graph():
    graph = StateGraph(MultiAgentState)

    graph.add_node("writer_agent", writer_agent)
    graph.add_node("reviewer_agent", reviewer_agent)
    graph.add_node("finish_agent", finish_agent)

    graph.add_edge(START, "writer_agent")
    graph.add_edge("writer_agent", "reviewer_agent")

    graph.add_conditional_edges(
        "reviewer_agent",
        route_after_review,
        {
            "rewrite": "writer_agent",
            "finish": "finish_agent",
        },
    )

    graph.add_edge("finish_agent", END)

    return graph.compile()


def main():
    app = build_graph()

    result = app.invoke(
        create_initial_multi_agent_state(
            "解释 LangGraph Multi-Agent。"
        ),
        config={
            "recursion_limit": 10
        },
    )

    print("final_answer:")
    print(result["final_answer"])

    print("=" * 80)
    print("retry_count:", result["retry_count"])

    print("=" * 80)
    print("review_result:")
    print(result["review_result"])

    print("=" * 80)
    print("logs:")
    for log in result["logs"]:
        print("-", log)


if __name__ == "__main__":
    main()