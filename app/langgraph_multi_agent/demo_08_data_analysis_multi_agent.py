from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.langgraph_multi_agent.mock_services import mock_query_sales_data
from app.langgraph_multi_agent.schemas import (
    MultiAgentState,
    create_initial_multi_agent_state,
)


def planner_agent(state: MultiAgentState) -> dict:
    return {
        "current_agent": "planner_agent",
        "plan": [
            "查询最近 30 天销售数据",
            "对比上一周期订单量和销售额",
            "分析下滑原因",
            "生成优化建议",
            "检查报告是否有数据依据",
        ],
        "logs": ["planner_agent：完成数据分析计划"],
    }


def sql_agent(state: MultiAgentState) -> dict:
    # 模拟真实的 SQL 查询
    data = mock_query_sales_data()

    content = (
        f"最近 30 天订单量 {data['total_orders']}，"
        f"销售额 {data['total_amount']}；"
        f"上一周期订单量 {data['last_period_orders']}，"
        f"销售额 {data['last_period_amount']}。"
    )

    return {
        "current_agent": "sql_agent",
        "sql_result": {
            "agent_name": "sql_agent",
            "success": True,
            "content": content,
            "data": data,
            "confidence": 0.98,
        },
        "logs": ["sql_agent：完成销售数据查询"],
    }


def analysis_agent(state: MultiAgentState) -> dict:
    sql_result = state["sql_result"] or {}
    data = sql_result.get("data") or {}

    order_drop = data["last_period_orders"] - data["total_orders"]
    amount_drop = data["last_period_amount"] - data["total_amount"]

    content = (
        f"订单量下降 {order_drop} 单，"
        f"销售额下降 {amount_drop}。"
        f"主要可能来自弱势品类：{data['weak_category']}。"
    )

    return {
        "current_agent": "analysis_agent",
        "analysis_result": {
            "agent_name": "analysis_agent",
            "success": True,
            "content": content,
            "data": {
                "order_drop": order_drop,
                "amount_drop": amount_drop,
            },
            "confidence": 0.86,
        },
        "logs": ["analysis_agent：完成指标分析"],
    }


def chart_agent(state: MultiAgentState) -> dict:
    content = (
        "建议生成两张图："
        "1）最近 30 天销售额 vs 上一周期销售额；"
        "2）不同品类销售贡献对比。"
    )

    return {
        "current_agent": "chart_agent",
        "chart_result": {
            "agent_name": "chart_agent",
            "success": True,
            "content": content,
            "data": {
                "charts": [
                    "period_sales_compare",
                    "category_sales_compare",
                ]
            },
            "confidence": 0.88,
        },
        "logs": ["chart_agent：完成图表建议"],
    }


def report_agent(state: MultiAgentState) -> dict:
    sql_result = state["sql_result"] or {}
    analysis_result = state["analysis_result"] or {}
    chart_result = state["chart_result"] or {}

    report = (
        "【数据分析报告】\n\n"
        "一、核心数据\n"
        f"{sql_result.get('content')}\n\n"
        "二、分析结论\n"
        f"{analysis_result.get('content')}\n\n"
        "三、图表建议\n"
        f"{chart_result.get('content')}\n\n"
        "四、优化建议\n"
        "建议重点优化传统前端课程的转化路径，"
        "同时加强 AI 课程的关联销售。"
    )

    return {
        "current_agent": "report_agent",
        "report_result": {
            "agent_name": "report_agent",
            "success": True,
            "content": report,
            "data": {},
            "confidence": 0.84,
        },
        "logs": ["report_agent：完成报告草稿"],
    }


def reviewer_agent(state: MultiAgentState) -> dict:
    report = state["report_result"] or {}
    content = report.get("content", "")

    has_data = "订单量" in content and "销售额" in content
    has_suggestion = "建议" in content

    passed = has_data and has_suggestion

    if passed:
        review_text = "审核通过：报告包含数据和建议。"
    else:
        review_text = "审核不通过：报告缺少数据依据或建议。"

    return {
        "current_agent": "reviewer_agent",
        "review_result": {
            "agent_name": "reviewer_agent",
            "success": passed,
            "content": review_text,
            "data": {
                "passed": passed,
            },
            "confidence": 0.9,
        },
        "logs": [f"reviewer_agent：{review_text}"],
    }


def route_after_review(
    state: MultiAgentState,
) -> Literal["finish", "rewrite"]:
    review = state["review_result"] or {}
    data = review.get("data") or {}

    if data.get("passed"):
        return "finish"

    if state["retry_count"] < state["max_retry"]:
        return "rewrite"

    return "finish"


def rewrite_report_agent(state: MultiAgentState) -> dict:
    report = state["report_result"] or {}
    old_content = report.get("content", "")

    new_content = (
        old_content
        + "\n\n【补充说明】以上结论基于 mock 销售数据，只能作为分析示例。"
    )

    return {
        "current_agent": "rewrite_report_agent",
        "retry_count": state["retry_count"] + 1,
        "report_result": {
            "agent_name": "rewrite_report_agent",
            "success": True,
            "content": new_content,
            "data": {},
            "confidence": 0.86,
        },
        "logs": ["rewrite_report_agent：根据审核意见补充报告"],
    }


def finish_agent(state: MultiAgentState) -> dict:
    report = state["report_result"] or {}

    return {
        "current_agent": "finish_agent",
        "final_answer": report.get("content", ""),
        "is_finished": True,
        "logs": ["finish_agent：输出最终数据分析报告"],
    }


def build_graph():
    graph = StateGraph(MultiAgentState)

    graph.add_node("planner_agent", planner_agent)
    graph.add_node("sql_agent", sql_agent)
    graph.add_node("analysis_agent", analysis_agent)
    graph.add_node("chart_agent", chart_agent)
    graph.add_node("report_agent", report_agent)
    graph.add_node("reviewer_agent", reviewer_agent)
    graph.add_node("rewrite_report_agent", rewrite_report_agent)
    graph.add_node("finish_agent", finish_agent)

    graph.add_edge(START, "planner_agent")
    graph.add_edge("planner_agent", "sql_agent")
    graph.add_edge("sql_agent", "analysis_agent")
    graph.add_edge("analysis_agent", "chart_agent")
    graph.add_edge("chart_agent", "report_agent")
    graph.add_edge("report_agent", "reviewer_agent")

    graph.add_conditional_edges(
        "reviewer_agent",
        route_after_review,
        {
            "finish": "finish_agent",
            "rewrite": "rewrite_report_agent",
        },
    )

    graph.add_edge("rewrite_report_agent", "reviewer_agent")
    graph.add_edge("finish_agent", END)

    return graph.compile()


def main():
    app = build_graph()

    result = app.invoke(
        create_initial_multi_agent_state(
            "帮我分析最近 30 天销售数据，找出下滑原因。"
        ),
        config={
            "recursion_limit": 20
        },
    )

    print("final_answer:")
    print(result["final_answer"])

    print("=" * 80)
    print("logs:")
    for log in result["logs"]:
        print("-", log)


if __name__ == "__main__":
    main()