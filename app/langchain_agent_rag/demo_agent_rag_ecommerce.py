import json
import asyncio
from app.langchain_agent_rag.factory import (
    build_ecommerce_agent_with_rag,
    parse_agent_rag_result,
)
from app.langchain_agent_rag.index import ensure_rag_index


async def main():
    ensure_rag_index()

    agent = build_ecommerce_agent_with_rag(
        provider="deepseek",
        model_name="deepseek-chat",
    )

    result = await agent.ainvoke({
        "messages": [
            {
                "role": "user",
                "content": "我的订单 10002 还没发货，这种情况可以退款吗？",
            }
        ]
    })

    parsed = parse_agent_rag_result(result)

    print(json.dumps(
        parsed.model_dump(),
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    asyncio.run(main())