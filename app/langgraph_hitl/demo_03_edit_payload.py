from typing import Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class EditPayloadState(TypedDict):
    pending_action: str
    pending_payload: dict
    human_decision: dict | None
    final_payload: dict | None
    final_answer: str


def review_payload_node(state: EditPayloadState) -> dict:
    
    decision = interrupt({
        "type": "review_payload",
        "pending_action": state["pending_action"],
        "pending_payload": state["pending_payload"],
        "options": ["approve", "reject", "edit"],
        "message": "请审核动作参数，可以同意、拒绝或修改。",
    })

    return {
        "human_decision": decision
    }


def route_after_review(
    state: EditPayloadState,
) -> Literal["approved", "edited", "rejected"]:
    decision = state["human_decision"] or {}
    decision_type = decision.get("type")

    if decision_type == "approve":
        return "approved"

    if decision_type == "edit":
        return "edited"

    return "rejected"


def use_original_payload_node(state: EditPayloadState) -> dict:
    return {
        "final_payload": state["pending_payload"],
        "final_answer": f"使用原始参数执行：{state['pending_payload']}",
    }


def use_edited_payload_node(state: EditPayloadState) -> dict:
    decision = state["human_decision"] or {}
    edited_payload = decision.get("edited_payload") or {}

    return {
        "final_payload": edited_payload,
        "final_answer": f"使用人工修改后的参数执行：{edited_payload}",
    }


def reject_node(state: EditPayloadState) -> dict:
    decision = state["human_decision"] or {}

    return {
        "final_payload": None,
        "final_answer": f"人工拒绝执行。原因：{decision.get('reason', '未填写')}",
    }


def build_graph():
    graph = StateGraph(EditPayloadState)

    graph.add_node("review_payload", review_payload_node)
    graph.add_node("use_original_payload", use_original_payload_node)
    graph.add_node("use_edited_payload", use_edited_payload_node)
    graph.add_node("reject", reject_node)

    graph.add_edge(START, "review_payload")

    graph.add_conditional_edges(
        "review_payload",
        route_after_review,
        {
            "approved": "use_original_payload",
            "edited": "use_edited_payload",
            "rejected": "reject",
        },
    )

    graph.add_edge("use_original_payload", END)
    graph.add_edge("use_edited_payload", END)
    graph.add_edge("reject", END)

    checkpointer = InMemorySaver()

    return graph.compile(checkpointer=checkpointer)


def main():
    app = build_graph()

    config = {
        "configurable": {
            "thread_id": "thread_lg35_edit_payload"
        }
    }

    first = app.invoke(
        {
            "pending_action": "refund_order",
            "pending_payload": {
                "order_id": "10002",
                "amount": 199.0,
                "reason": "用户申请未发货退款",
            },
            "human_decision": None,
            "final_payload": None,
            "final_answer": "",
        },
        config=config,
    )

    print("first:")
    print(first)

    print("=" * 80)

    second = app.invoke(
        Command(resume={
            "type": "edit",
            "reviewer_id": "admin_001",
            "reason": "优惠券不可退，只退实付金额",
            "edited_payload": {
                "order_id": "10002",
                "amount": 149.0,
                "reason": "人工修改为仅退实付金额",
            },
        }),
        config=config,
    )

    print("second:")
    print(second)


if __name__ == "__main__":
    main()