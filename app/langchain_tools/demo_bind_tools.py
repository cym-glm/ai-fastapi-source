
from langchain_core.messages import HumanMessage, SystemMessage


from app.langchain_models.model_factory import  LangChainModelFactory


from app.langchain_tools.registry import langchain_tool_registry

def mian():
    model = LangChainModelFactory.create(
        provider="deepseek",
        model="deepseek-chat",
        temperature=0.7,
    )

    tools = langchain_tool_registry.get_many(
        names=["query_order", "query_logistics", "transfer_human"]
    )
    model_with_tools = model.bind_tools(tools);

    response = model_with_tools.invoke([
        SystemMessage(
            content=(
                "你是一个跨境电商客服助手。\n"
                "当用户询问订单状态时，优先调用工具查询真实信息。\n"
                "不要编造订单状态。"
            )
        ),
        HumanMessage(
            content="帮我查一下订单 10001 到哪了？"
        )

    ])
    print('==========')
    print(response.content)

    print('==========')
    print(response.tool_calls)
    print('==========')
    if response.tool_calls:
        for tool_call in  response.tool_calls:
            print(f"tool call name:{tool_call['name']}")
            print(f"tool call args:{tool_call["args"]}")
            print(f"tool call id:{tool_call["id"]}")


# 按照自己的业务逻辑 --和大模型---  执行 tool_call['name'] 
if __name__ == '__main__':
    mian()

