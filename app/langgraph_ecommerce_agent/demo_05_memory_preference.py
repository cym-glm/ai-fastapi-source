import asyncio

from app.langgraph_ecommerce_agent.graph_factory import build_ecommerce_agent_graph
from app.langgraph_ecommerce_agent.schemas import (
    EcommerceAgentContext,
    create_initial_state,
)


async def main():
    app, store = build_ecommerce_agent_graph()

    config = {
        "configurable": {
            "thread_id": "thread_lg38_memory_preference"
        },
        "recursion_limit": 30,
    }

    context = EcommerceAgentContext(
        tenant_id="tenant_001",
        user_id="u_10001",
        conversation_id="conv_memory_preference",
    )

    first = await app.ainvoke(
        create_initial_state("记住：以后回答客服问题，先给结论，再给处理步骤。"),
        config=config,
        context=context,
    )

    print("first:")
    print(first["final_answer"])
    print("new_memories:", first["new_memories"])
    print("=" * 80)

    second = await app.ainvoke(
        create_initial_state("你好，介绍一下你能做什么？"),
        config=config,
        context=context,
    )

    print("second:")
    print(second["final_answer"])
    print("recalled_memories:", second["recalled_memories"])
    print("=" * 80)

    namespace = ("tenant_001", "u_10001", "preferences")
    print("store memories:")
    for item in store.search(namespace):
        print(item.key, item.value)


if __name__ == "__main__":
    asyncio.run(main())