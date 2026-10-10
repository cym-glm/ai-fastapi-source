from typing import Any

from pydantic import BaseModel, ValidationError

from app.core.logging import get_logger
from app.tools.registry import tool_registry


logger = get_logger(__name__)

class ToolExecutionError(Exception):
    def __init__(
        self,
        message: str,
        tool_name: str,
        detail: str | None = None,
    ):
        self.message = message
        self.tool_name = tool_name
        self.detail = detail

        super().__init__(message)


class ToolExecutor:
    async def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> BaseModel:
        logger.info(
            f"tool_execute_start tool_name={tool_name}"
        )

        try:
            tool = tool_registry.get(tool_name)

        except KeyError as exc:
            raise ToolExecutionError(
                message="工具不存在或未启用",
                tool_name=tool_name,
                detail=str(exc),
            ) from exc

        if tool.require_confirm:
            raise ToolExecutionError(
                message="该工具需要人工确认，不能自动执行",
                tool_name=tool_name,
            )

        try:
            result = await tool.execute(arguments)

        except ValidationError as exc:
            raise ToolExecutionError(
                message="工具参数校验失败",
                tool_name=tool_name,
                detail=str(exc),
            ) from exc

        except Exception as exc:
            logger.exception(
                f"tool_execute_failed tool_name={tool_name}"
            )
            raise ToolExecutionError(
                message="工具执行失败",
                tool_name=tool_name,
                detail=repr(exc),
            ) from exc

        logger.info(
            f"tool_execute_success tool_name={tool_name}"
        )

        return result


tool_executor = ToolExecutor()