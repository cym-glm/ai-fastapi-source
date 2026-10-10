import asyncio

from app.langgraph_ecommerce_agent.service import langgraph_ecommerce_agent_service


async def main():
    tenant_id = "tenant_001"
    user_id = "u_10001"
    conversation_id = "conv_lg38_service"

    first = await langgraph_ecommerce_agent_service.chat(
        tenant_id=tenant_id,
        user_id=user_id,
        conversation_id=conversation_id,
        question="帮我查一下订单。",
        is_new_conversation=True,
    )

    print("first:")
    print(first)
    print("=" * 80)

    second = await langgraph_ecommerce_agent_service.chat(
        tenant_id=tenant_id,
        user_id=user_id,
        conversation_id=conversation_id,
        question="订单号是 10002。",
    )

    print("second:")
    print(second)
    print("=" * 80)

    state = await langgraph_ecommerce_agent_service.get_state(
        tenant_id=tenant_id,
        user_id=user_id,
        conversation_id=conversation_id,
    )

    print("state:")
    print(state["values"])


if __name__ == "__main__":
    asyncio.run(main())