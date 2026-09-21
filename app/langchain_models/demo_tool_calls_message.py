




from langchain_core.messages import HumanMessage, SystemMessage

from langchain_core.tools import tool

from app.langchain_models.model_factory import LangChainModelFactory

@tool
def query_order(order_id: str) -> str:
    """ 根据订单号查询订单和物流的状态。 """
    if order_id == "10001":
        return "订单 10001 的状态是：已发货。 物流公司是：顺丰快递。 物流单号是：1234567890。"
    return f"未查询到订单 {order_id}。"

def main():
    model = LangChainModelFactory.create(
        provider="deepseek",
        model="deepseek-chat",
        temperature=0.7,
    )
    model_with_tools = model.bind_tools([query_order])

    messages = [
        SystemMessage(
            content=(
                "你是一个电商客服助手。\n"
                "当用户询问订单状态时，优先调用工具查询真实信息。"
            )

        ),
        HumanMessage(content="我有一个订单号是10001，请查询一下物流状态。")
    ]

    response = model_with_tools.invoke(messages)

    print('content: ',response.content)
    print("===================")
    print('tool_calls: ',response.tool_calls)
    print("===================")
    if response.tool_calls:
        first_tool_call = response.tool_calls[0]
        print('tool_call_id: ', first_tool_call['id'])
        print('name: ', first_tool_call['name'])
        print('args: ', first_tool_call['args'])
        print("===================")

main();


# SystemMessage   HumanMessage   AIMessage(tool_calls=[...])   ToolMessage(tool_call_id=...)
# AIMessage(final answer)


#  system  user assistant with tool_calls   tool   assistant

#  AIMessage(tool_calls=[...])  + ToolMessage(tool_call_id=...)