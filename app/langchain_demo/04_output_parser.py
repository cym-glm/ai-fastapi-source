from typing import Literal

from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


# from langchain.chat_models import ChatOpenAI
# from langchain_openai import ChatOpenAI
# from langchain_core.output_parsers import PydanticOutputParser
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.tools import tool


from app.core.config import settings


class IntentResult(BaseModel):
    intent: Literal[
        "query_order",
        "refund",
        "product_question",
        "other",
    ] = Field(..., description="用户意图")

    confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="置信度",
    )

def create_model():
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        temperature=0,
    )


def run_parser_chain():
    parser = PydanticOutputParser(pydantic_object=IntentResult)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "你是一个电商客服意图识别器。\n"
                "你必须按照下面的格式要求输出。\n"
                "{format_instructions}"
            ),
        ),
        (
            "human",
            "用户问题：{question}",
        ),
    ])

    # prompt = prompt.partial(
    #     format_instructions=parser.get_format_instructions()
    # )

    model = create_model()

    chain = prompt | model | parser
    result = chain.invoke({
        "format_instructions": parser.get_format_instructions(),
        "question": "我的订单怎么还没发货？",
    })

    print(type(result))
    print(result.model_dump())


if __name__ == "__main__":
    run_parser_chain()