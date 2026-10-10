from typing import Literal

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from app.langgraph_multi_agent.schemas import (
    MultiAgentState,
    create_initial_multi_agent_state,
)


def _is_sales_related_question(question: str) -> bool:
    """判断用户问题是否与销售/购买相关。

    Args:
        question: 用户的问题内容

    Returns:
        bool: 如果问题包含"购买"或"价格"关键词，返回 True；否则返回 False
    """
    return "购买" in question or "价格" in question


def _create_sales_handoff_update(question: str) -> dict:
    """构建转交给销售 Agent 的状态更新字典。

    Args:
        question: 用户的问题内容

    Returns:
        dict: 包含销售转交所需的状态更新字段，包括 agent 信息、日志和追踪记录
    """
    return {
        "current_agent": "support_agent",
        "active_agent": "sales_agent",
        "logs": ["support_agent：发现是购买/价格问题，handoff 给 sales_agent"],
        "agent_trace": [
            {
                "agent_name": "support_agent",
                "input_summary": question,
                "output_summary": "需要销售 Agent 处理",
                "next_agent": "sales_agent",
                "reason": "用户问题和购买价格相关",
            }
        ],
    }


def _create_support_update() -> dict:
    """构建售后支持处理的状态更新字典。

    Returns:
        dict: 包含售后支持处理的状态更新字段，包括报告结果和日志记录
    """
    return {
        "current_agent": "support_agent",
        "active_agent": "answer_agent",
        "report_result": {
            "agent_name": "support_agent",
            "success": True,
            "content": "这是售后支持问题，我可以直接处理。",
            "data": {},
            "confidence": 0.9,
        },
        "logs": ["support_agent：售后问题，直接交给 answer_agent"],
    }


def support_agent(
    state: MultiAgentState,
) -> Command[Literal["sales_agent", "answer_agent"]]:
    question = state["user_question"]

    if _is_sales_related_question(question):
        return Command(
            update=_create_sales_handoff_update(question),
            goto="sales_agent",
        )

    return Command(
        update=_create_support_update(),
        goto="answer_agent",
    )


def sales_agent(state: MultiAgentState) -> dict:
    content = "这是销售问题，我可以介绍套餐价格和购买流程。"

    return {
        "current_agent": "sales_agent",
        "report_result": {
            "agent_name": "sales_agent",
            "success": True,
            "content": content,
            "data": {},
            "confidence": 0.9,
        },
        "logs": ["sales_agent：完成销售回答"],
    }


def answer_agent(state: MultiAgentState) -> dict:
    report = state["report_result"] or {}

    return {
        "current_agent": "answer_agent",
        "final_answer": report.get("content", ""),
        "is_finished": True,
        "logs": ["answer_agent：最终回答完成"],
    }


def build_graph():
    graph = StateGraph(MultiAgentState)

    graph.add_node("support_agent", support_agent)
    graph.add_node("sales_agent", sales_agent)
    graph.add_node("answer_agent", answer_agent)

    graph.add_edge(START, "support_agent")

    graph.add_edge("sales_agent", "answer_agent")
    graph.add_edge("answer_agent", END)

    return graph.compile()


def main():
    app = build_graph()

    questions = [
        "我的订单售后怎么处理？",
        "这个课程价格是多少，怎么买？",
    ]

    for question in questions:
        result = app.invoke(
            create_initial_multi_agent_state(question)
        )

        print("question:", question)
        print("active_agent:", result["active_agent"])
        print("final_answer:", result["final_answer"])
        print("logs:", result["logs"])
        print("=" * 80)


if __name__ == "__main__":
    main()
