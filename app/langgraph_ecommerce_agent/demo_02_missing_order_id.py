import asyncio

from app.langgraph_ecommerce_agent.graph_factory import build_ecommerce_agent_graph
from app.langgraph_ecommerce_agent.schemas import (
    EcommerceAgentContext,
    append_user_message,
    create_initial_state,
)


async def main():
    app, _store = build_ecommerce_agent_graph()

    config = {
        "configurable": {
            "thread_id": "thread_lg38_missing_order_id"
        },
        "recursion_limit": 30,
    }

    context = EcommerceAgentContext(
        tenant_id="tenant_001",
        user_id="u_10001",
        conversation_id="conv_missing_order_id",
    )

    first = await app.ainvoke(
        create_initial_state("帮我查一下订单。"),
        config=config,
        context=context,
    )

    print("first:")
    print("final_answer:", first["final_answer"])
    print("intent:", first["intent"])
    print("order_id:", first["order_id"])
    print("=" * 80)

    second = await app.ainvoke(
        append_user_message("订单号是 10002。"),
        config=config,
        context=context,
    )

    print("second:")
    print("final_answer:", second["final_answer"])
    print("intent:", second["intent"])
    print("order_id:", second["order_id"])
    print("order_info:", second["order_info"])


if __name__ == "__main__":
    asyncio.run(main())