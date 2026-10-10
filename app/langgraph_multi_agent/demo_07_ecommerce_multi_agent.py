from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.langgraph_multi_agent.mock_services import (
    extract_order_id,
    mock_query_order,
    mock_refund_policy,
)
from app.langgraph_multi_agent.schemas import (
    MultiAgentState,
    create_initial_multi_agent_state,
)


def supervisor_agent(state: MultiAgentState) -> dict:
    question = state["user_question"]

    if "退款" in question or "退货" in question:
        next_agent = "order_agent"
        task_type = "ecommerce"
        plan = [
            "查询订单状态",
            "判断退款规则",
            "评估回答风险",
            "生成客服回答",
            "检查回答质量",
        ]
    elif "物流" in question or "订单" in question:
        next_agent = "order_agent"
        task_type = "ecommerce"
        plan = [
            "查询订单状态",
            "生成客服回答",
            "检查回答质量",
        ]
    else:
        next_agent = "answer_agent"
        task_type = "general"
        plan = [
            "直接生成普通回答"
        ]

    return {
        "current_agent": "supervisor_agent",
        "next_agent": next_agent,
        "task_type": task_type,
        "plan": plan,
        "logs": [f"supervisor_agent：next_agent={next_agent}"],
        "agent_trace": [
            {
                "agent_name": "supervisor_agent",
                "input_summary": question,
                "output_summary": f"task_type={task_type}, next_agent={next_agent}",
                "next_agent": next_agent,
                "reason": "根据用户问题判断客服任务类型",
            }
        ],
    }


def route_after_supervisor(
    state: MultiAgentState,
) -> Literal["order_agent", "answer_agent"]:
    if state["next_agent"] == "order_agent":
        return "order_agent"

    return "answer_agent"


def order_agent(state: MultiAgentState) -> dict:
    # 模拟真实的业务
    order_id = extract_order_id(state["user_question"])
    result = mock_query_order(order_id)

    return {
        "current_agent": "order_agent",
        "order_result": {
            "agent_name": "order_agent",
            "success": result["success"],
            "content": result["message"],
            "data": result.get("data") or {},
            "confidence": 0.95,
        },
        "logs": [f"order_agent：{result['message']}"],
        "agent_trace": [
            {
                "agent_name": "order_agent",
                "input_summary": state["user_question"],
                "output_summary": result["message"],
                "next_agent": "refund_agent",
                "reason": "订单结果会决定后续退款或回答逻辑",
            }
        ],
    }


def route_after_order(
    state: MultiAgentState,
) -> Literal["refund_agent", "answer_agent"]:
    if "退款" in state["user_question"] or "退货" in state["user_question"]:
        return "refund_agent"

    return "answer_agent"


def refund_agent(state: MultiAgentState) -> dict:
    order_result = state["order_result"] or {}

    if not order_result.get("success"):
        content = "订单未查询成功，无法判断退款规则。"
        success = False
    else:
        order_data = order_result.get("data") or {}
        # 模拟真实的退款规则判断 (此处仅为示例，实际业务逻辑会更复杂)
        content = mock_refund_policy(order_data.get("status"))
        success = True

    return {
        "current_agent": "refund_agent",
        "refund_result": {
            "agent_name": "refund_agent",
            "success": success,
            "content": content,
            "data": {},
            "confidence": 0.9,
        },
        "logs": ["refund_agent：退款规则判断完成"],
        "agent_trace": [
            {
                "agent_name": "refund_agent",
                "input_summary": str(order_result),
                "output_summary": content,
                "next_agent": "risk_agent",
                "reason": "退款建议需要风险评估",
            }
        ],
    }


def risk_agent(state: MultiAgentState) -> dict:
    order_result = state["order_result"] or {}
    refund_result = state["refund_result"] or {}

    order_data = order_result.get("data") or {}
    status = order_data.get("status")

    if status == "shipped":
        content = "中风险：订单已发货，不能直接承诺立即退款。"
        confidence = 0.9
    elif not refund_result.get("success"):
        content = "高风险：缺少订单信息，不能给确定退款结论。"
        confidence = 0.9
    else:
        content = "低风险：可以按规则给出退款建议。"
        confidence = 0.9

    return {
        "current_agent": "risk_agent",
        "analysis_result": {
            "agent_name": "risk_agent",
            "success": True,
            "content": content,
            "data": {
                "risk_text": content,
            },
            "confidence": confidence,
        },
        "logs": ["risk_agent：风险评估完成"],
    }


def answer_agent(state: MultiAgentState) -> dict:
    order_result = state["order_result"]
    refund_result = state["refund_result"]
    risk_result = state["analysis_result"]

    if not order_result:
        answer = "这是普通问题，可以直接回答。"
    elif not order_result.get("success"):
        answer = "没有查询到订单，请您检查订单号是否正确。"
    else:
        order_data = order_result.get("data") or {}
        answer = f"您的订单状态是：{order_data.get('status_text')}。"

        if refund_result:
            answer += refund_result.get("content", "")

        if risk_result:
            answer += f" 风险提示：{risk_result.get('content')}"

    return {
        "current_agent": "answer_agent",
        "report_result": {
            "agent_name": "answer_agent",
            "success": True,
            "content": answer,
            "data": {},
            "confidence": 0.86,
        },
        "logs": ["answer_agent：客服回答草稿完成"],
    }


def reviewer_agent(state: MultiAgentState) -> dict:
    report = state["report_result"] or {}
    content = report.get("content", "")

    risky_words = ["保证", "一定", "立即到账"]

    has_risky_word = any(word in content for word in risky_words)

    if has_risky_word:
        review_content = "审核不通过：回答里包含过度承诺。"
        passed = False
    else:
        review_content = "审核通过：回答没有明显过度承诺。"
        passed = True

    return {
        "current_agent": "reviewer_agent",
        "review_result": {
            "agent_name": "reviewer_agent",
            "success": passed,
            "content": review_content,
            "data": {
                "passed": passed,
            },
            "confidence": 0.9,
        },
        "logs": [f"reviewer_agent：{review_content}"],
    }


def route_after_reviewer(
    state: MultiAgentState,
) -> Literal["finish", "rewrite"]:
    review = state["review_result"] or {}
    data = review.get("data") or {}

    if data.get("passed"):
        return "finish"

    if state["retry_count"] < state["max_retry"]:
        return "rewrite"

    return "finish"


def rewrite_answer_agent(state: MultiAgentState) -> dict:
    report = state["report_result"] or {}
    content = report.get("content", "")

    rewritten = (
        content
        .replace("保证", "通常")
        .replace("一定", "一般")
        .replace("立即到账", "以实际到账时间为准")
    )

    return {
        "current_agent": "rewrite_answer_agent",
        "retry_count": state["retry_count"] + 1,
        "report_result": {
            "agent_name": "rewrite_answer_agent",
            "success": True,
            "content": rewritten,
            "data": {},
            "confidence": 0.88,
        },
        "logs": ["rewrite_answer_agent：已根据审核意见改写回答"],
    }


def finish_agent(state: MultiAgentState) -> dict:
    report = state["report_result"] or {}

    return {
        "current_agent": "finish_agent",
        "final_answer": report.get("content", ""),
        "is_finished": True,
        "logs": ["finish_agent：输出最终客服回答"],
    }


def build_graph():
    graph = StateGraph(MultiAgentState)

    graph.add_node("supervisor_agent", supervisor_agent)
    graph.add_node("order_agent", order_agent)
    graph.add_node("refund_agent", refund_agent)
    graph.add_node("risk_agent", risk_agent)
    graph.add_node("answer_agent", answer_agent)
    graph.add_node("reviewer_agent", reviewer_agent)
    graph.add_node("rewrite_answer_agent", rewrite_answer_agent)
    graph.add_node("finish_agent", finish_agent)

    graph.add_edge(START, "supervisor_agent")

    graph.add_conditional_edges(
        "supervisor_agent",
        route_after_supervisor,
        {
            "order_agent": "order_agent",
            "answer_agent": "answer_agent",
        },
    )

    graph.add_conditional_edges(
        "order_agent",
        route_after_order,
        {
            "refund_agent": "refund_agent",
            "answer_agent": "answer_agent",
        },
    )

    graph.add_edge("refund_agent", "risk_agent")
    graph.add_edge("risk_agent", "answer_agent")
    graph.add_edge("answer_agent", "reviewer_agent")

    graph.add_conditional_edges(
        "reviewer_agent",
        route_after_reviewer,
        {
            "finish": "finish_agent",
            "rewrite": "rewrite_answer_agent",
        },
    )

    graph.add_edge("rewrite_answer_agent", "reviewer_agent")
    graph.add_edge("finish_agent", END)

    return graph.compile()


def main():
    app = build_graph()

    questions = [
        "我的订单 10002 可以退款吗？",
        "我的订单 10001 可以退款吗？",
        "帮我查一下订单 10002。",
        "你好。",
    ]

    for question in questions:
        result = app.invoke(
            create_initial_multi_agent_state(question),
            config={
                "recursion_limit": 20
            },
        )

        print("question:", question)
        print("final_answer:", result["final_answer"])
        print("logs:")
        for log in result["logs"]:
            print("-", log)
        print("=" * 120)


if __name__ == "__main__":
    main()