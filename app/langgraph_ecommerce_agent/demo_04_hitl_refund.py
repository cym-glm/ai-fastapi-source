import asyncio

from langgraph.types import Command

from app.langgraph_ecommerce_agent.graph_factory import build_ecommerce_agent_graph
from app.langgraph_ecommerce_agent.schemas import (
    EcommerceAgentContext,
    create_initial_state,
)


async def run_approve_case():
    app, _store = build_ecommerce_agent_graph()

    config = {
        "configurable": {
            "thread_id": "thread_lg38_hitl_approve"
        },
        "recursion_limit": 30,
    }

    context = EcommerceAgentContext(
        tenant_id="tenant_001",
        user_id="u_10001",
        conversation_id="conv_hitl_approve",
    )

    first = await app.ainvoke(
        create_initial_state("我的订单 10003 申请大额退款。"),
        config=config,
        context=context,
    )

    print("第一次执行，应该触发 interrupt：")
    print(first)

    print("=" * 80)
    print("当前 state：")
    snapshot = await app.aget_state(config)
    print(snapshot.values)

    print("=" * 80)
    print("人工 approve 后恢复：")

    second = await app.ainvoke(
        Command(resume={
            "type": "approve",
            "reviewer_id": "admin_001",
            "reason": "大额退款人工审核通过",
        }),
        config=config,
        context=context,
    )

    print("final_answer:")
    print(second["final_answer"])

    print("=" * 80)
    print("action_result:")
    print(second["action_result"])


async def run_edit_case():
    app, _store = build_ecommerce_agent_graph()

    config = {
        "configurable": {
            "thread_id": "thread_lg38_hitl_edit"
        },
        "recursion_limit": 30,
    }

    context = EcommerceAgentContext(
        tenant_id="tenant_001",
        user_id="u_10001",
        conversation_id="conv_hitl_edit",
    )

    await app.ainvoke(
        create_initial_state("我的订单 10003 申请大额退款。"),
        config=config,
        context=context,
    )

    second = await app.ainvoke(
        Command(resume={
            "type": "edit",
            "reviewer_id": "admin_002",
            "reason": "优惠券不可退，只退实付金额",
            "edited_payload": {
                "order_id": "10003",
                "amount": 1099.0,
                "currency": "CNY",
                "reason": "人工修改后的退款金额",
            },
        }),
        config=config,
        context=context,
    )

    print("edit case final_answer:")
    print(second["final_answer"])
    print("pending_payload:")
    print(second["pending_payload"])


async def main():
    await run_approve_case()
    print("=" * 120)
    await run_edit_case()


if __name__ == "__main__":
    asyncio.run(main())