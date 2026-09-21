
from langchain_core.messages import (
    AIMessage,
    ToolMessage,
    HumanMessage,
    SystemMessage,
)

def main():
    messages = [
        SystemMessage(content="你是一个专业 AI Agent 课程助教。"),
        HumanMessage(content="请用一句话解释 LangChain。"),
        AIMessage(content="LangChain 是一个用于构建 AI Agent 的框架。"),
        ToolMessage(
            content='{"order_id": "10001", "status": "已发货"}',
            tool_call_id="call_query_order_1001"
        )
    ]
    for message in messages:
        print('class: ',message.__class__.__name__ )
        print('type: ',message.type)
        print('content: ',message.content)
        print('model_dump: ',message.model_dump())


if __name__ == '__main__':
    main()

