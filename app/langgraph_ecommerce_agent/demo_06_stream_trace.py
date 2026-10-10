import asyncio

from app.langgraph_ecommerce_agent.graph_factory import build_ecommerce_agent_graph
from app.langgraph_ecommerce_agent.schemas import (
    EcommerceAgentContext,
    create_initial_state,
)


async def main():
    app, _store = build_ecommerce_agent_graph()

    config = {
        "configurable": {
            "thread_id": "thread_lg38_stream_trace"
        },
        "recursion_limit": 30,
    }

    context = EcommerceAgentContext(
        tenant_id="tenant_001",
        user_id="u_10001",
        conversation_id="conv_stream_trace",
    )

    async for chunk in app.astream(
        create_initial_state("我的订单 10002 还没发货，可以退款吗？"),
        config=config,
        context=context,
        stream_mode="updates",
    ):
        print(chunk)


if __name__ == "__main__":
    asyncio.run(main())