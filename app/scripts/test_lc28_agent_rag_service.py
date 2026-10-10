import asyncio
import json

from app.langchain_agent_rag.service import langchain_agent_rag_service


async def main():
    questions = [
        "订单未发货时可以退款吗？",
        "我的订单 10002 还没发货，这种情况可以退款吗？",
        "第 20 到 28 章属于什么阶段？",
    ]

    for question in questions:
        print("question:", question)
        print("=" * 80)

        result = await langchain_agent_rag_service.run_ecommerce_agent_rag(
            user_question=question,
            provider="deepseek",
            model_name="deepseek-chat",
        )

        print(json.dumps(
            result.model_dump(),
            ensure_ascii=False,
            indent=2,
        ))

        print("=" * 120)


if __name__ == "__main__":
    asyncio.run(main())