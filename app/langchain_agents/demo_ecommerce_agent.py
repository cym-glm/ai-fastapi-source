
import json
import asyncio

from app.langchain_agents.factory import (
    build_ecommerce_agent,
    parse_agent_result
)


async def main():
    agent = build_ecommerce_agent(
        provider="deepseek",
        model_name="deepseek-chat"
    )

    result = await agent.ainvoke({
        "messages": [
            {
                "role": "user",
                "content": "帮我查一下订单 10001 到哪了？",
            }
        ]
    })
    parsed = parse_agent_result(result)
    # print (result["messages"])
    
    print('===============')
    print (
        json.dumps(
            parsed.model_dump(), 
            ensure_ascii=False, 
            indent=2
        )
    )

if __name__ == "__main__":
    asyncio.run(main())