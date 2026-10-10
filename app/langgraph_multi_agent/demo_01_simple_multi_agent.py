from langgraph.graph import END, START, StateGraph

from app.langgraph_multi_agent.schemas import (
    MultiAgentState,
    create_initial_multi_agent_state,
)


def planner_agent(state: MultiAgentState) -> dict:
    return {
        "current_agent": "planner_agent",
        "plan": [
            "理解用户问题",
            "生成回答草稿",
            "检查回答质量",
        ],
        "agent_trace": [
            {
                "agent_name": "planner_agent",
                "input_summary": state["user_question"],
                "output_summary": "已生成三步计划",
                "next_agent": "writer_agent",
                "reason": "计划完成后交给写作 Agent",
            }
        ],
        "logs": ["planner_agent：完成任务拆解"],
    }


def writer_agent(state: MultiAgentState) -> dict:
    draft = (
        "LangGraph Multi-Agent 可以理解成多个 Agent "
        "通过共享 State 和路由协作完成复杂任务。"
    )

    return {
        "current_agent": "writer_agent",
        "report_result": {
            "agent_name": "writer_agent",
            "success": True,
            "content": draft,
            "data": {},
            "confidence": 0.8,
        },
        "agent_trace": [
            {
                "agent_name": "writer_agent",
                "input_summary": "根据 planner 计划生成回答",
                "output_summary": draft,
                "next_agent": "reviewer_agent",
                "reason": "回答需要检查质量",
            }
        ],
        "logs": ["writer_agent：完成回答草稿"],
    }


def reviewer_agent(state: MultiAgentState) -> dict:
    content = state["report_result"]["content"]

    return {
        "current_agent": "reviewer_agent",
        "review_result": {
            "agent_name": "reviewer_agent",
            "success": True,
            "content": "审核通过",
            "data": {
                "passed": True,
            },
            "confidence": 0.9,
        },
        "final_answer": content,
        "is_finished": True,
        "agent_trace": [
            {
                "agent_name": "reviewer_agent",
                "input_summary": content,
                "output_summary": "审核通过",
                "next_agent": None,
                "reason": "结果质量达标",
            }
        ],
        "logs": ["reviewer_agent：审核通过"],
    }


def build_graph():
    graph = StateGraph(MultiAgentState)

    graph.add_node("planner_agent", planner_agent)
    graph.add_node("writer_agent", writer_agent)
    graph.add_node("reviewer_agent", reviewer_agent)

    graph.add_edge(START, "planner_agent")
    graph.add_edge("planner_agent", "writer_agent")
    graph.add_edge("writer_agent", "reviewer_agent")
    graph.add_edge("reviewer_agent", END)

    return graph.compile()


def main():
    app = build_graph()

    result = app.invoke(
        create_initial_multi_agent_state(
            "解释一下 LangGraph Multi-Agent。"
        )
    )

    print("final_answer:")
    print(result["final_answer"])

    print("=" * 80)
    print("plan:")
    for item in result["plan"]:
        print("-", item)

    print("=" * 80)
    print("agent_trace:")
    for item in result["agent_trace"]:
        print(item)


if __name__ == "__main__":
    main()