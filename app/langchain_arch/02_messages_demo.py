

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
)


def main():
    # # 创建一个系统消息
    # system_message = SystemMessage(content="你是一个助手，很高兴为你服务。")

    # # 创建一个人类消息
    # human_message = HumanMessage(content="你好！")

    # # 创建一个AI消息
    # ai_message = AIMessage(content="很高兴见到你！")

    # # 创建一个工具消息
    # tool_message = ToolMessage(
    #     content="这是一个工具的消息",
    #     additional_kwargs={"tool": "tool_name"},
    # )

    # print("系统消息:", system_message.dict())
    # print("人类消息:", human_message.dict())
    # print("AI消息:", ai_message.dict())
    # print("工具消息:", tool_message.dict())
    messages = [
        SystemMessage(content="你是一个助手，很高兴为你服务。"),
        HumanMessage(content="你好！"),
        AIMessage(content="很高兴见到你！"),
        ToolMessage(
            content="这是一个工具的消息",
            tool_call_id="tool_call_1",
        ),
    ]
    for message in messages:
        print("type:", message.type, "content:", message.content)
        print("dict:", message.model_dump())


main()
