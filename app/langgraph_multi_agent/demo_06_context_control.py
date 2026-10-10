from langgraph.graph import END, START, StateGraph

from app.langgraph_multi_agent.schemas import (
    MultiAgentState,
    create_initial_multi_agent_state,
)


def planner_agent(state: MultiAgentState) -> dict:
    plan = [
        "查询订单状态",
        "查询退款规则",
        "生成客服回答",
    ]

    return {
        "current_agent": "planner_agent",
        "plan": plan,
        "logs": ["planner_agent：生成任务计划"],
    }


def order_agent(state: MultiAgentState) -> dict:
    # OrderAgent 只需要用户问题和订单相关计划。
    local_context = {
        "user_question": state["user_question"],
        "plan": [
            item for item in state["plan"]
            if "订单" in item
        ],
    }

    return {
        "current_agent": "order_agent",
        "order_result": {
            "agent_name": "order_agent",
            "success": True,
            "content": "订单 10002 当前为已付款，待发货。",
            "data": {
                "order_id": "10002",
                "status": "paid",
            },
            "confidence": 0.95,
        },
        "agent_trace": [
            {
                "agent_name": "order_agent",
                "input_summary": str(local_context),
                "output_summary": "订单状态查询完成",
                "next_agent": "refund_agent",
                "reason": "订单状态会影响退款规则",
            }
        ],
        "logs": ["order_agent：使用裁剪后的上下文完成订单查询"],
    }


def refund_agent(state: MultiAgentState) -> dict:
    # RefundAgent 不需要全部 messages，只需要订单结果。
    order_result = state["order_result"] or {}
    local_context = {
        "order_result": order_result,
    }

    return {
        "current_agent": "refund_agent",
        "refund_result": {
            "agent_name": "refund_agent",
            "success": True,
            "content": "未发货订单可以取消并退款。",
            "data": {
                "used_context": local_context,
            },
            "confidence": 0.9,
        },
        "logs": ["refund_agent：只基于订单结果判断退款规则"],
    }


def answer_agent(state: MultiAgentState) -> dict:
    order_result = state["order_result"] or {}
    refund_result = state["refund_result"] or {}

    answer = (
        f"{order_result.get('content')}"
        f"{refund_result.get('content')}"
    )

    return {
        "current_agent": "answer_agent",
        "final_answer": answer,
        "is_finished": True,
        "logs": ["answer_agent：完成最终回答"],
    }


def build_graph():
    graph = StateGraph(MultiAgentState)

    graph.add_node("planner_agent", planner_agent)
    graph.add_node("order_agent", order_agent)
    graph.add_node("refund_agent", refund_agent)
    graph.add_node("answer_agent", answer_agent)

    graph.add_edge(START, "planner_agent")
    graph.add_edge("planner_agent", "order_agent")
    graph.add_edge("order_agent", "refund_agent")
    graph.add_edge("refund_agent", "answer_agent")
    graph.add_edge("answer_agent", END)

    return graph.compile()


def main():
    app = build_graph()

    result = app.invoke(
        create_initial_multi_agent_state(
            "我的订单 10002 可以退款吗？"
        )
    )

    print("final_answer:")
    print(result["final_answer"])

    print("=" * 80)
    print("agent_trace:")
    for item in result["agent_trace"]:
        print(item)

    print("=" * 80)
    print("logs:")
    for log in result["logs"]:
        print("-", log)


if __name__ == "__main__":
    main()