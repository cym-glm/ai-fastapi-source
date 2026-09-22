from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.langchain_models.model_factory import LangChainModelFactory
from app.langchain_structured_outputs.schemas import IntentClassificationResult


def build_intent_chain():
    parser = PydanticOutputParser(
        pydantic_object=IntentClassificationResult,
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "你是一个电商客服意图识别器。\n"
                "\n"
                "你需要识别用户问题属于哪一类意图。\n"
                "不要输出 Markdown，不要输出解释性文字。\n"
                "\n"
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

    return prompt | model | parser


def main():
    chain = build_intent_chain()

    questions = [
        "我的订单怎么还没发货？",
        "我想退款，怎么操作？",
        "这个商品有黑色吗？",
        "我要找人工客服。",
        "你好，今天天气不错。",
    ]

    for question in questions:
        result = chain.invoke({
            "user_question": question,
        })

        print("question:", question)
        print(result.model_dump())
        print("=" * 80)


if __name__ == "__main__":
    main()