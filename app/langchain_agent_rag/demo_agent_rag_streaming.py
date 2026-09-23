import asyncio
from app.langchain_agent_rag.factory import build_ecommerce_agent_with_rag
from app.langchain_agent_rag.index import ensure_rag_index


async def main():
    ensure_rag_index()

    agent = build_ecommerce_agent_with_rag(
        provider="deepseek",
        model_name="deepseek-chat",
    )

    async for chunk in agent.astream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "我的订单 10002 还没发货，这种情况可以退款吗？",
                }
            ]
        },
        stream_mode="updates",
    ):
        print("chunk:")
        print(chunk)
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())