from langchain_core.messages import HumanMessage, SystemMessage

from app.langchain_models.model_factory import LangChainModelFactory
from app.langchain_structured_outputs.schemas import IntentClassificationResult


def main():
    model = LangChainModelFactory.create(
        provider="deepseek",
        model="deepseek-chat",
        temperature=0,
    )

    structured_model = model.with_structured_output(
        IntentClassificationResult,
        method="function_calling",
        include_raw=True,
    )

    result = structured_model.invoke([
        SystemMessage(
            content=(
                "你是一个电商客服意图识别器。\n"
                "请根据用户问题输出结构化分类结果。"
            )
        ),
        HumanMessage(
            content="我的订单怎么还没发货？"
        ),
    ])

    print("result type:", type(result))
    print(result.raw_output)


if __name__ == "__main__":
    main()