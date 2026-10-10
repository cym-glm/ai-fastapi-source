from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.langgraph_multi_agent.schemas import (
    MultiAgentState,
    create_initial_multi_agent_state,
)


def supervisor_agent(state: MultiAgentState) -> dict:
    question = state["user_question"]

    if "订单" in question or "退款" in question or "物流" in question:
        task_type = "ecommerce"
        next_agent = "ecommerce_agent"
    elif "数据" in question or "销售" in question or "分析" in question:
        task_type = "data_analysis"
        next_agent = "data_agent"
    elif "调研" in question or "趋势" in question:
        task_type = "research"
        next_agent = "research_agent"
    else:
        task_type = "general"
        next_agent = "general_agent"

    return {
        "current_agent": "supervisor_agent",
        "task_type": task_type,
        "next_agent": next_agent,
        "agent_trace": [
            {
                "agent_name": "supervisor_agent",
                "input_summary": question,
                "output_summary": f"task_type={task_type}",
                "next_agent": next_agent,
                "reason": "根据用户问题选择合适的 Worker Agent",
            }
        ],
        "logs": [f"supervisor_agent：路由到 {next_agent}"],
    }


def route_by_supervisor(
    state: MultiAgentState,
) -> Literal[
    "ecommerce_agent",
    "data_agent",
    "research_agent",
    "general_agent",
]:
    return state["next_agent"]  # type: ignore[return-value]


def ecommerce_agent(state: MultiAgentState) -> dict:
    answer = "这是电商客服问题，应该交给订单、退款或物流 Agent 继续处理。"

    return {
        "final_answer": answer,
        "is_finished": True,
        "logs": ["ecommerce_agent：处理完成"],
    }


def data_agent(state: MultiAgentState) -> dict:
    answer = "这是数据分析问题，应该交给 SQL、Analysis、Report Agent 继续处理。"

    return {
        "final_answer": answer,
        "is_finished": True,
        "logs": ["data_agent：处理完成"],
    }


def research_agent(state: MultiAgentState) -> dict:
    answer = "这是研究调研问题，应该交给 Researcher 和 Writer Agent。"

    return {
        "final_answer": answer,
        "is_finished": True,
        "logs": ["research_agent：处理完成"],
    }


def general_agent(state: MultiAgentState) -> dict:
    answer = "这是普通问题，可以直接回答。"

    return {
        "final_answer": answer,
        "is_finished": True,
        "logs": ["general_agent：处理完成"],
    }


def build_graph():
    graph = StateGraph(MultiAgentState)

    graph.add_node("supervisor_agent", supervisor_agent)
    graph.add_node("ecommerce_agent", ecommerce_agent)
    graph.add_node("data_agent", data_agent)
    graph.add_node("research_agent", research_agent)
    graph.add_node("general_agent", general_agent)

    graph.add_edge(START, "supervisor_agent")

    graph.add_conditional_edges(
        "supervisor_agent",
        route_by_supervisor,
        {
            "ecommerce_agent": "ecommerce_agent",
            "data_agent": "data_agent",
            "research_agent": "research_agent",
            "general_agent": "general_agent",
        },
    )

    graph.add_edge("ecommerce_agent", END)
    graph.add_edge("data_agent", END)
    graph.add_edge("research_agent", END)
    graph.add_edge("general_agent", END)

    return graph.compile()


def main():
    app = build_graph()

    questions = [
        "我的订单 10002 可以退款吗？",
        "帮我分析最近 30 天销售数据。",
        "调研一下 AI Agent 平台趋势。",
        "你好，介绍一下 LangGraph。",
    ]

    for question in questions:
        result = app.invoke(
            create_initial_multi_agent_state(question)
        )

        print("question:", question)
        print("task_type:", result["task_type"])
        print("next_agent:", result["next_agent"])
        print("final_answer:", result["final_answer"])
        print("=" * 80)


if __name__ == "__main__":
    main()