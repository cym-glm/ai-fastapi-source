

from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser, JSONOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.core.config import settings


def create_model():
    return ChatOpenAI(
        model_name="deepseek-chat",
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        temperature=0.7,
    )


def main():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的AIAAgent课程助手，你需要回答用户的问题"),
        ("human", "请用一句话解释 {topic} 的概念"),
    ])
    model = create_model()
    parser = StrOutputParser()
    
    chain = prompt | model | parser
    
    response = chain.invoke({
        "topic": "Langchain",
    })

    print("type:", type(response))

    print(response)

if __name__ == "__main__":
    main()