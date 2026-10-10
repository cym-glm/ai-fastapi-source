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


def order_agent(state: MultiAgentState) -> dict:
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
        "agent_trace": [
            {
                "agent_name": "order_agent",
                "input_summary": state["user_question"],
                "output_summary": result["message"],
                "next_agent": "refund_agent",
                "reason": "退款问题需要继续判断售后规则",
            }
        ],
        "logs": ["order_agent：订单查询完成"],
    }


def refund_agent(state: MultiAgentState) -> dict:
    order_result = state["order_result"] or {}

    if not order_result.get("success"):
        content = "订单查询失败，无法判断退款规则。"
        success = False
    else:
        order_data = order_result.get("data") or {}
        policy = mock_refund_policy(order_data.get("status"))
        content = policy
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
        "agent_trace": [
            {
                "agent_name": "refund_agent",
                "input_summary": str(order_result),
                "output_summary": content,
                "next_agent": "answer_agent",
                "reason": "退款规则判断完成，交给回答 Agent",
            }
        ],
        "logs": ["refund_agent：退款规则判断完成"],
    }


def answer_agent(state: MultiAgentState) -> dict:
    order_result = state["order_result"] or {}
    refund_result = state["refund_result"] or {}

    if not order_result.get("success"):
        answer = "没有查询到订单，请您检查订单号是否正确。"
    else:
        order_data = order_result.get("data") or {}
        answer = (
            f"您的订单状态是：{order_data.get('status_text')}。"
            f"{refund_result.get('content')}"
        )

    return {
        "current_agent": "answer_agent",
        "final_answer": answer,
        "is_finished": True,
        "agent_trace": [
            {
                "agent_name": "answer_agent",
                "input_summary": "订单结果 + 退款规则",
                "output_summary": answer,
                "next_agent": None,
                "reason": "生成最终用户回答",
            }
        ],
        "logs": ["answer_agent：最终回答完成"],
    }


def build_graph():
    graph = StateGraph(MultiAgentState)

    graph.add_node("order_agent", order_agent)
    graph.add_node("refund_agent", refund_agent)
    graph.add_node("answer_agent", answer_agent)

    graph.add_edge(START, "order_agent")
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
    print("order_result:")
    print(result["order_result"])

    print("=" * 80)
    print("refund_result:")
    print(result["refund_result"])

    print("=" * 80)
    print("agent_trace:")
    for item in result["agent_trace"]:
        print(item)


if __name__ == "__main__":
    main()