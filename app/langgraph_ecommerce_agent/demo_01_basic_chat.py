import asyncio

from app.langgraph_ecommerce_agent.graph_factory import build_ecommerce_agent_graph
from app.langgraph_ecommerce_agent.schemas import (
    EcommerceAgentContext,
    create_initial_state,
)


async def main():
    app, _store = build_ecommerce_agent_graph()

    result = await app.ainvoke(
        create_initial_state("你好，介绍一下你能做什么？"),
        config={
            "configurable": {
                "thread_id": "thread_lg38_basic_chat"
            },
            "recursion_limit": 30,
        },
        context=EcommerceAgentContext(
            tenant_id="tenant_001",
            user_id="u_10001",
            conversation_id="conv_basic_chat",
        ),
    )

    print("final_answer:")
    print(result["final_answer"])

    print("=" * 80)
    print("logs:")
    for log in result["logs"]:
        print("-", log)


if __name__ == "__main__":
    asyncio.run(main())