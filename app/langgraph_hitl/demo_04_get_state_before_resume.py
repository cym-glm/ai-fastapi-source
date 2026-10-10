from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from app.langgraph_hitl.demo_03_edit_payload import build_graph


def main():
    app = build_graph()

    config = {
        "configurable": {
            "thread_id": "thread_lg35_get_state_before_resume"
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

    print("first interrupt:")
    print(first)

    print("=" * 80)
    print("人工审核前查看当前 State:")

    snapshot = app.get_state(config)

    print(snapshot.values)

    print("=" * 80)
    print("人工审核通过后恢复:")

    second = app.invoke(
        Command(resume={
            "type": "approve",
            "reviewer_id": "admin_001",
            "reason": "审核通过",
        }),
        config=config,
    )

    print(second)


if __name__ == "__main__":
    main()