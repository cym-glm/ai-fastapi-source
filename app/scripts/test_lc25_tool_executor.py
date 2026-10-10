import asyncio

from app.langchain_tools.executor import langchain_tool_executor


async def main():
    tool_call = {
        "name": "query_order",
        "args": {
            "order_id": "10001",
        },
        "id": "call_query_order_001",
        "type": "tool_call",
    }

    tool_message = await langchain_tool_executor.execute_tool_call(
        tool_call
    )

    print("tool message type:", tool_message.type)
    print("tool message content:", tool_message.content)
    print("tool_call_id:", tool_message.tool_call_id)


if __name__ == "__main__":
    asyncio.run(main())