import asyncio

from app.llm.factory import LLMProviderFactory
from app.services.structured_output_service import structured_output_service


async def main():
    provider = LLMProviderFactory.create("deepseek")

    questions = [
        "我的订单怎么还没发货？",
        "我想退款，怎么操作？",
        "这款衣服有黑色吗？",
        "我要找人工客服。",
    ]

    for question in questions:
        result = await structured_output_service.classify_intent(
            user_question=question,
            model="deepseek-chat",
            llm_provider=provider,
        )

        print("question:", question)
        print(result.model_dump())
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())


    #  问题 -- llm---> 意图分类 ---> 意图--> json --业务代码-- 解析json ---> 执行（tool 业务接口）  数据--  结果