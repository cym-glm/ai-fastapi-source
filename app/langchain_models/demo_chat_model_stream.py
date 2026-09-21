

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

    full_text = "";

    response = await model.astream(messages)
    # response = model.stream(messages)
    for chunk in response:
        if chunk.content:
            print(chunk.content, end="", flush=True)
            full_text += chunk.content

    # response = model.invoke("请用一句话解释什么是 Langchain ChatModel")

    print('=', *80)
    print('full_text: ')
    print(full_text)


if __name__ == '__main__':
    main()