from pydantic import BaseModel

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.langchain_models.model_factory import LangChainModelFactory


async def parse_with_repair(
    raw_text: str,
    schema: type[BaseModel],
    provider: str = "deepseek",
    model_name: str = "deepseek-chat",
):
    parser = PydanticOutputParser(
        pydantic_object=schema,
    )

    try:
        return parser.parse(raw_text)

    except Exception as first_error:
        repair_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                (
                    "你是一个 JSON 修复器。\n"
                    "你的任务是把用户提供的内容修复为符合目标 Schema 的合法 JSON。\n"
                    "只能输出 JSON，不要输出 Markdown，不要输出解释。\n"
                    "\n"
                    "{format_instructions}"
                ),
            ),
            (
                "human",
                (
                    "原始输出：\n"
                    "{raw_text}\n"
                    "\n"
                    "解析错误：\n"
                    "{error_message}\n"
                    "\n"
                    "请修复。"
                ),
            ),
        ]).partial(
            format_instructions=parser.get_format_instructions()
        )

        model = LangChainModelFactory.create(
            provider=provider,
            model=model_name,
            temperature=0,
        )

        repair_chain = repair_prompt | model | parser

        return await repair_chain.ainvoke({
            "raw_text": raw_text,
            "error_message": repr(first_error),
        })