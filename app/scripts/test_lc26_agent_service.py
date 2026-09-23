import asyncio
import json

from app.langchain_agents.service import langchain_agent_service


async def main():
    result = await langchain_agent_service.run_ecommerce_agent(
        user_question="帮我查一下订单 10001 到哪了？",
        provider="deepseek",
        model_name="deepseek-chat",
    )

    print(json.dumps(
        result.model_dump(),
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    asyncio.run(main())