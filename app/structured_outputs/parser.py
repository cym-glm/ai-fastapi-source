# json解析和校验
import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError


T = TypeVar("T", bound=BaseModel)


class StructuredOutputParseError(Exception):
    def __init__(
        self,
        message: str,
        raw_text: str,
        detail: str | None = None,
    ):
        self.message = message
        self.raw_text = raw_text
        self.detail = detail

        super().__init__(message)


def extract_json_text(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        match = re.search(
            r"```(?:json)?\s*(.*?)\s*```",
            text,
            re.DOTALL,
        )

        if match:
            return match.group(1).strip()

    first_brace = text.find("{")
    last_brace = text.rfind("}")

    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return text[first_brace:last_brace + 1]

    return text


def parse_structured_output(
    raw_text: str,
    schema: type[T],
) -> T:
    json_text = extract_json_text(raw_text)

    try:
        return schema.model_validate_json(json_text)

    except ValidationError as exc:
        raise StructuredOutputParseError(
            message="结构化输出字段校验失败",
            raw_text=raw_text,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise StructuredOutputParseError(
            message="结构化输出不是合法 JSON",
            raw_text=raw_text,
            detail=str(exc),
        ) from exc


def safe_json_loads(raw_text: str) -> dict:
    json_text = extract_json_text(raw_text)

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise StructuredOutputParseError(
            message="JSON 解析失败",
            raw_text=raw_text,
            detail=str(exc),
        ) from exc

    if not isinstance(data, dict):
        raise StructuredOutputParseError(
            message="结构化输出必须是 JSON object",
            raw_text=raw_text,
            detail=f"实际类型：{type(data)}",
        )

    return data