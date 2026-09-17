import asyncio

from app.llm.factory import LLMProviderFactory
from app.services.structured_output_service import structured_output_service


async def main():
    provider = LLMProviderFactory.create("deepseek")

    result = await structured_output_service.plan_agent_task(
        user_goal="帮用户查询订单 10001 的物流状态，并生成客服回复。",
        available_tools="query_order(order_id: string)：根据订单号查询订单和物流状态。",
        constraints="不能编造物流信息；只能调用已提供的工具。",
        model="deepseek-chat",
        llm_provider=provider,
    )

    print(result.model_dump())


if __name__ == "__main__":
    asyncio.run(main())