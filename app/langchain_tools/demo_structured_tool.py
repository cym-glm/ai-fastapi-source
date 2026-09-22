import asyncio



from app.langchain_tools.tools import (
    query_order_tool,
    query_logistics_tool,
    transfer_human_tool
)

async def main():
    tools = [
        query_order_tool,
        query_logistics_tool,
        transfer_human_tool
    ]

    for tool in tools:
        print("tool name:", tool.name)

        print("tool description:", tool.description)

        print("tool args:", tool.args)
        print("=========")


    result = await query_order_tool.ainvoke({
        "order_id": "10001",
    })

    print("result:", result)

asyncio.run(main())