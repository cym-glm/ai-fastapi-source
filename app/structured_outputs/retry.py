# 失败重试和修复


from pydantic import BaseModel

from app.llm.base import BaseLLMProvider
from app.llm.schemas import LLMMessage, LLMRequest, LLMRole
from app.structured_outputs.parser import (
    StructuredOutputParseError,
    parse_structured_output,
)
from app.structured_outputs.response_format import (
    build_json_object_response_format,
)


async def parse_or_repair_structured_output(
    raw_text: str,
    schema: type[BaseModel],
    model: str,
    llm_provider: BaseLLMProvider,
):
    try:
        return parse_structured_output(
            raw_text=raw_text,
            schema=schema,
        )
    except StructuredOutputParseError as first_error:
        repair_messages = [
            LLMMessage(
                role=LLMRole.SYSTEM,
                content=(
                    "你是一个 JSON 修复器。\n"
                    "你的任务是把输入内容修复为符合目标结构的合法 JSON。\n"
                    "只能输出 JSON，不要输出 Markdown，不要输出解释。"
                ),
            ),
            LLMMessage(
                role=LLMRole.USER,
                content=(
                    "目标 JSON Schema：\n"
                    f"{schema.model_json_schema()}\n"
                    "\n"
                    "上一次输出：\n"
                    f"{raw_text}\n"
                    "\n"
                    "解析错误：\n"
                    f"{first_error.detail}\n"
                    "\n"
                    "请修复为合法 JSON。"
                ),
            ),
        ]

        repair_request = LLMRequest(
            model=model,
            messages=repair_messages,
            temperature=0,
            stream=False,
            response_format=build_json_object_response_format(),
        )

        repair_response = await llm_provider.chat(repair_request)

        return parse_structured_output(
            raw_text=repair_response.content,
            schema=schema,
        )