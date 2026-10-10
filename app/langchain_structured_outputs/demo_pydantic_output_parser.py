from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.langchain_models.model_factory import LangChainModelFactory
from app.langchain_structured_outputs.schemas import IntentClassificationResult


def main():
    parser = PydanticOutputParser(
        pydantic_object=IntentClassificationResult,
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "你是一个电商客服意图识别器。\n"
                "你必须根据格式要求输出结构化结果。\n"
                "不要输出 Markdown，不要输出解释。\n"
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

    # 模型输出---PydanticOutputParser --  IntentClassificationResult

    
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
    print(result.model_dump())


if __name__ == "__main__":
    main()