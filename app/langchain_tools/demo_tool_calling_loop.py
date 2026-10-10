import asyncio

from langchain_core.messages import HumanMessage, SystemMessage,ToolMessage

from app.langchain_models.model_factory import LangChainModelFactory
from app.langchain_tools.executor import langchain_tool_executor
from app.langchain_tools.registry import langchain_tool_registry



async def main():
    model = LangChainModelFactory.create(
        provider="deepseek",
        model="deepseek-chat",
        temperature=0.7,
    )

    tools = langchain_tool_registry.get_many(
        names=["query_order", "query_logistics", "transfer_human"]
    )
    model_with_tools = model.bind_tools(tools);

    messages = [
        SystemMessage(
            content=(
                "你是一个跨境电商客服助手。\n"
                "当用户询问订单、物流、发货状态时，必须优先调用工具查询真实信息。\n"
                "工具返回结果后，请用礼貌、简洁的中文回复用户。\n"
                "不要编造订单状态、物流公司或物流单号。"
            )
        ),
        HumanMessage(
            content="帮我查一下订单 10001 到哪了？"
        ),
        # ToolMessage(
        #     content="{'order_status': '已发货', 'logistics_company': '顺丰速运', 'tracking_number': '1234567890'}",
        #     name="query_order",
        #     tool_call_id="call_1",
        # )
    ]
    # AIMesage
    first_response = await model_with_tools.ainvoke(messages)
    print('==========')
    print(first_response.content)

    print('==========')

    print(first_response.tool_calls)

    print('==========')

    if not first_response.tool_calls:
        print("没有工具调用")
        print(first_response.content)
        return 
    # AImessage 提示词
    # 调用业务接口---query_order,---查询数据库--- 真实信息
    #  拼接成 ToolMessage 对象
    tool_messages = await langchain_tool_executor.execute_tool_calls(
        first_response.tool_calls
    )

    print('==========tool_messages')
    print(tool_messages)

    messages.append(first_response)
    messages.extend(tool_messages)

    final_response = await model.ainvoke(messages)

    print('==========final_response')

    print(final_response.content)

if __name__ == '__main__':
    asyncio.run(main())




