import asyncio


from app.tools.executor import tool_executor

async def main():
    result = await tool_executor.execute(
        tool_name="query_order",
        arguments={
            "order_id": "10001",
        },
    )

    print(result.model_dump())

    result = await tool_executor.execute(
        tool_name="query_logistics",
        arguments={
            "tracking_no": "SF10001",
        },
    )

    print(result.model_dump())


if __name__ == "__main__":
    asyncio.run(main())