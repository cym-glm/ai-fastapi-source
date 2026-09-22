
import asyncio

from app.langchain_tools.tools import query_order_simple

async def main():
    print("tool name:", query_order_simple.name)

    print("tool description:", query_order_simple.description)


    print("tool args:", query_order_simple.args)


    print("tool name:", query_order_simple.name)

    print("=========")
    result = await query_order_simple.ainvoke({
        "order_id": "10001",
    })

    print("result:", result)

asyncio.run(main())