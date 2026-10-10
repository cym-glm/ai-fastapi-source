from langgraph.types import Command

from app.langgraph_hitl.graph_factory import build_memory_hitl_graph
from app.langgraph_hitl.schemas import create_initial_state


def run_low_risk_refund(app):
    config = {
        "configurable": {
            "thread_id": "thread_low_risk_refund"
        }
    }

    result = app.invoke(
        create_initial_state("我的订单 10002 申请退款。"),
        config=config,
    )

    print("低风险退款：")
    print("final_answer:", result["final_answer"])
    print("need_human_confirm:", result["need_human_confirm"])
    print("logs:")
    for log in result["logs"]:
        print("-", log)

    print("=" * 120)


def run_high_risk_refund_with_approve(app):
    config = {
        "configurable": {
            "thread_id": "thread_high_risk_refund_approve"
        }
    }

    first = app.invoke(
        create_initial_state("我的订单 10003 申请退款。"),
        config=config,
    )

    print("高风险退款第一次执行，应该 interrupt：")
    print(first)

    print("=" * 80)

    snapshot = app.get_state(config)
    print("当前 State:")
    print(snapshot.values)

    print("=" * 80)

    second = app.invoke(
        Command(resume={
            "type": "approve",
            "reviewer_id": "admin_001",
            "reason": "大额退款人工审核通过",
        }),
        config=config,
    )

    print("人工 approve 后恢复：")
    print("final_answer:", second["final_answer"])
    print("human_decision:", second["human_decision"])
    print("action_result:", second["action_result"])
    print("logs:")
    for log in second["logs"]:
        print("-", log)

    print("=" * 120)


def run_high_risk_refund_with_reject(app):
    config = {
        "configurable": {
            "thread_id": "thread_high_risk_refund_reject"
        }
    }

    first = app.invoke(
        create_initial_state("我的订单 10003 申请退款。"),
        config=config,
    )

    print("高风险退款第一次执行，应该 interrupt：")
    print(first)

    print("=" * 80)

    second = app.invoke(
        Command(resume={
            "type": "reject",
            "reviewer_id": "admin_002",
            "reason": "金额较大，需要进一步核实用户身份",
        }),
        config=config,
    )

    print("人工 reject 后恢复：")
    print("final_answer:", second["final_answer"])
    print("human_decision:", second["human_decision"])
    print("action_result:", second["action_result"])

    print("=" * 120)


def run_high_risk_refund_with_edit(app):
    config = {
        "configurable": {
            "thread_id": "thread_high_risk_refund_edit"
        }
    }

    first = app.invoke(
        create_initial_state("我的订单 10003 申请退款。"),
        config=config,
    )

    print("高风险退款第一次执行，应该 interrupt：")
    print(first)

    print("=" * 80)

    second = app.invoke(
        Command(resume={
            "type": "edit",
            "reviewer_id": "admin_003",
            "reason": "部分优惠券不可退，人工调整退款金额",
            "edited_payload": {
                "order_id": "10003",
                "amount": 1099.0,
                "currency": "CNY",
                "reason": "人工调整后退款金额",
            },
        }),
        config=config,
    )

    print("人工 edit 后恢复：")
    print("final_answer:", second["final_answer"])
    print("pending_payload:", second["pending_payload"])
    print("action_result:", second["action_result"])

    print("=" * 120)


def main():
    app = build_memory_hitl_graph()

    run_low_risk_refund(app)

    run_high_risk_refund_with_approve(app) 
    run_high_risk_refund_with_reject(app)
    run_high_risk_refund_with_edit(app)


if __name__ == "__main__":
    main()