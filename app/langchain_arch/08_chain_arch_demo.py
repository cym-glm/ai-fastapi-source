
from langchain_core.output_parsers import StrOutputParser

from langchain_core.prompts import ChatPromptTemplate

from langchain_core.runnables import RunnableLambda

from langchain_openai import ChatOpenAI

from  app.core.config  import  settings


def create_model():
    return ChatOpenAI(
        model_name="deepseek-chat",
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        temperature=0.7,
    )


# 业务逻辑处理，  添加前缀 格式 字体提取
def add_prefix(text: str) ->str:
    return f"【LangChain 架构解释】\n{text}"

def main():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的AIAAgent课程助手，你需要回答用户的问题"),
        ("human", "请用一句话解释 {topic} 的概念"),
    ])

    model = create_model()
    parser = StrOutputParser()
    prefix = RunnableLambda(add_prefix)

    chain = prompt | model | parser | prefix
    
    result = chain.invoke({
        "topic": "LangChain 架构",
    })
    print("result:", result)

if __name__ == "__main__":
    main()
