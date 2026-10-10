

from langchain_core.messages import HumanMessage, SystemMessage

from app.langchain_models.model_factory import LangChainModelFactory



def main():
    model = LangChainModelFactory.create(
        provider="deepseek",
        model="deepseek-chat",
        temperature=0.7,
    )
    messages = [
        SystemMessage(content="我是一个AI助手，很高兴为你服务。"),
        HumanMessage(content="请用一句话解释什么是 Langchain ChatModel")
        
    ]
    response = model.invoke(messages)
    # response = model.invoke("请用一句话解释什么是 Langchain ChatModel")

    print('class: ',response.__class__.__name__ )
    print('type: ',response.type)
    print('content: ',response.content)
    print('response_metadata: ',response.response_metadata)
    print('usage_metadata: ',response.usage_metadata)


if __name__ == '__main__':
    main()