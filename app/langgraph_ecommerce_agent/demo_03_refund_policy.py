import asyncio

from app.langgraph_ecommerce_agent.graph_factory import build_ecommerce_agent_graph
from app.langgraph_ecommerce_agent.schemas import (
    EcommerceAgentContext,
    create_initial_state,
)


async def main():
    app, _store = build_ecommerce_agent_graph()

    result = await app.ainvoke(
        create_initial_state("我的订单 10002 还没发货，可以退款吗？"),
        config={
            "configurable": {
                "thread_id": "thread_lg38_refund_policy"
            },
            "recursion_limit": 30,
        },
        context=EcommerceAgentContext(
            tenant_id="tenant_001",
            user_id="u_10001",
            conversation_id="conv_refund_policy",
        ),
    )

    print("final_answer:")
    print(result["final_answer"])

    print("=" * 80)
    print("policy_answer:")
    print(result["policy_answer"])

    print("=" * 80)
    print("sources:")
    for source in result["sources"]:
        print(source)

    print("=" * 80)
    print("logs:")
    for log in result["logs"]:
        print("-", log)


if __name__ == "__main__":
    asyncio.run(main())