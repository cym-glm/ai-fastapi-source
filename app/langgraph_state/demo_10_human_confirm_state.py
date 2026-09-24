from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class RefundConfirmState(TypedDict):
    user_question: str
    order_id: str | None
    refund_amount: float
    risk_level: Literal["low", "medium", "high"]
    need_human_confirm: bool
    human_confirm_status: Literal["none", "pending", "approved", "rejected"]
    pending_action: str | None
    human_confirm_payload: dict | None
    final_answer: str


def assess_risk_node(state: RefundConfirmState) -> dict:
    refund_amount = state["refund_amount"]

    if refund_amount >= 500:
        return {
            "risk_level": "high",
            "need_human_confirm": True,
            "human_confirm_status": "pending",
            "pending_action": "refund_order",
            "human_confirm_payload": {
                "order_id": state["order_id"],
                "refund_amount": refund_amount,
                "reason": "大额退款需要人工确认",
            },
        }

    return {
        "risk_level": "low",
        "need_human_confirm": False,
        "human_confirm_status": "none",
    }


def generate_answer_node(state: RefundConfirmState) -> dict:
    if state["need_human_confirm"]:
        return {
            "final_answer": (
                "该退款金额较高，需要人工客服确认后才能继续处理。"
            )
        }

    return {
        "final_answer": "该退款金额较低，可以进入自动退款流程。"
    }


def build_graph():
    graph = StateGraph(RefundConfirmState)

    graph.add_node("assess_risk", assess_risk_node)
    graph.add_node("generate_answer", generate_answer_node)

    graph.add_edge(START, "assess_risk")
    graph.add_edge("assess_risk", "generate_answer")
    graph.add_edge("generate_answer", END)

    return graph.compile()


def main():
    app = build_graph()

    result = app.invoke({
        "user_question": "我要申请退款。",
        "order_id": "10002",
        "refund_amount": 899.0,
        "risk_level": "low",
        "need_human_confirm": False,
        "human_confirm_status": "none",
        "pending_action": None,
        "human_confirm_payload": None,
        "final_answer": "",
    })

    print(result)


if __name__ == "__main__":
    main()