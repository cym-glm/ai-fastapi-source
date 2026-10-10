import asyncio

from langchain_core.messages import HumanMessage, SystemMessage

from app.langchain_models.model_factory import LangChainModelFactory



async def main():
    model = LangChainModelFactory.create(
        provider="deepseek",
        model="deepseek-chat",
        temperature=0.7,
    )
    messages = [
        SystemMessage(content="我是一个AI助手，很高兴为你服务。"),
        HumanMessage(content="请用一句话解释什么是 Langchain ChatModel")
        
    ]
    response =  await model.ainvoke(messages)
    
    # response = model.invoke("请用一句话解释什么是 Langchain ChatModel")

    print('content: ',response.content)
    print('usage_metadata: ',response.usage_metadata)


if __name__ == '__main__':
    main()