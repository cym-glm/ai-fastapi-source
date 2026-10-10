from typing import Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class ApproveRejectState(TypedDict):
    action_name: str
    action_payload: dict
    human_decision: dict | None
    final_answer: str


def review_action_node(state: ApproveRejectState) -> dict:

    decision = interrupt({
        "type": "review_action",
        "action_name": state["action_name"],
        "action_payload": state["action_payload"],
        "options": ["approve", "reject"],
    })

    return {
        "human_decision": decision
    }


def route_after_review(
    state: ApproveRejectState,
) -> Literal["approved", "rejected"]:
    decision = state["human_decision"] or {}

    if decision.get("type") == "approve":
        return "approved"

    return "rejected"


def execute_action_node(state: ApproveRejectState) -> dict:
    return {
        "final_answer": (
            f"人工已审批通过，开始执行动作：{state['action_name']}，"
            f"参数：{state['action_payload']}"
        )
    }


def reject_action_node(state: ApproveRejectState) -> dict:
    decision = state["human_decision"] or {}

    return {
        "final_answer": (
            "人工已拒绝执行该动作。"
            f"原因：{decision.get('reason', '未填写')}"
        )
    }


def build_graph():
    graph = StateGraph(ApproveRejectState)

    graph.add_node("review_action", review_action_node)
    graph.add_node("execute_action", execute_action_node)
    graph.add_node("reject_action", reject_action_node)

    graph.add_edge(START, "review_action")

    graph.add_conditional_edges(
        "review_action",
        route_after_review,
        {
            "approved": "execute_action",
            "rejected": "reject_action",
        },
    )

    graph.add_edge("execute_action", END)
    graph.add_edge("reject_action", END)

    checkpointer = InMemorySaver()

    return graph.compile(checkpointer=checkpointer)


def main():
    app = build_graph()

    config = {
        "configurable": {
            "thread_id": "thread_lg35_approve_reject"
        }
    }

    first = app.invoke(
        {
            "action_name": "refund_order",
            "action_payload": {
                "order_id": "10002",
                "amount": 199.0,
            },
            "human_decision": None,
            "final_answer": "",
        },
        config=config,
    )

    print("first:")
    print(first)

    print("=" * 80)

    second = app.invoke(
        Command(resume={
            "type": "reject",
            "reviewer_id": "admin_001",
            "reason": "订单未发货，可以退款",
        }),
        config=config,
    )

    print("second:")
    print(second)


if __name__ == "__main__":
    main()