from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage ,AIMessage, ToolMessage
from app.core.config import settings



def create_deepseek_chat_model():
    if not settings.deepseek_api_key:
        raise RuntimeError("DeepSeek API key is not set")
    
    return ChatOpenAI(
        model_name="deepseek-chat",
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        temperature=0.7,
    )


def run_chat_with_messages():
    model = create_deepseek_chat_model()
    messages = [
        SystemMessage(content="你是一个专业的AIAAgent课程助手，你需要回答用户的问题"),
        HumanMessage(content="Langchain和直接调用大模型api有什么区别？")
    ]
    response = model.invoke(messages)
    print(response.content)


def run():
    model = create_deepseek_chat_model()
    response = model.invoke("请用一句话解释什么是Langchain")
    print(response.content)
    print("tpye:", type(response))



run_chat_with_messages()