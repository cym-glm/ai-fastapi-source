from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.langchain_models.model_factory import LangChainModelFactory
from app.langchain_structured_outputs.schemas import AgentPlanResult


def build_agent_plan_chain():
    parser = PydanticOutputParser(
        pydantic_object=AgentPlanResult,
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "你是一个 AI Agent 任务规划器。\n"
                "\n"
                "你需要根据用户目标、可用工具和约束条件，规划执行步骤。\n"
                "\n"
                "规则：\n"
                "1. 只能使用 available_tools 中列出的工具。\n"
                "2. 不要编造不存在的工具。\n"
                "3. 如果需要高风险操作，need_human_confirm 必须为 true。\n"
                "4. 如果信息不足，要规划 ask_user 步骤。\n"
                "5. 不要输出 Markdown，不要输出额外解释。\n"
                "\n"
                "{format_instructions}\n"
                "\n"
                "可用工具：\n"
                "{available_tools}\n"
                "\n"
                "约束条件：\n"
                "{constraints}"
            ),
        ),
        (
            "human",
            "用户目标：{user_goal}",
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
    chain = build_agent_plan_chain()

    result = chain.invoke({
        "user_goal": "帮用户查询订单 10001 的物流状态，并生成客服回复。",
        "available_tools": (
            "query_order(order_id: string)：根据订单号查询订单和物流状态。\n"
            "transfer_human(reason: string)：转人工客服。"
        ),
        "constraints": "不能编造物流信息；只能调用已提供的工具。",
    })

    print(result.model_dump())


if __name__ == "__main__":
    main()