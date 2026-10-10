from typing import Literal

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.langchain_models.model_factory import LangChainModelFactory


class IntentResult(BaseModel):
    intent: Literal[
        "query_order",
        "refund",
        "logistics",
        "product_question",
        "human_service",
        "other",
    ] = Field(..., description="用户意图")

    confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="置信度",
    )

    reason: str = Field(..., description="判断原因")


def main():
    
    parser = PydanticOutputParser(
        pydantic_object=IntentResult,
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "你是一个电商客服意图识别器。\n"
                "你必须根据格式要求输出。\n"
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
        # "format_instructions": parser.get_format_instructions(),
        "user_question": "我的订单怎么还没发货？",
    })

    print(result.model_dump())


if __name__ == "__main__":
    main()