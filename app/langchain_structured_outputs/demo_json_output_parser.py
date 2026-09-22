from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.langchain_models.model_factory import LangChainModelFactory


def main():
    
    parser = JsonOutputParser()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "你是一个电商客服意图识别器。\n"
                "你必须只输出 JSON，不要输出 Markdown，不要解释。\n"
                "{format_instructions}"
            ),
        ),
        (
            "human",
            "用户问题：{user_question}",
        ),
    ]).partial(
        format_instructions=parser.get_format_instructions()
    )

    model = LangChainModelFactory.create(
        provider="deepseek",
        model="deepseek-chat",
        temperature=0,
    )

    chain = prompt | model | parser

    result = chain.invoke({
        "user_question": "我的订单怎么还没发货？",
    })

    print("result type:", type(result))
    print(result)


if __name__ == "__main__":
    main()